# Airfoil-CAD backend validation status

**Latest completed backend CI run:** https://github.com/Japharzadeh/WindFarm/actions/runs/40499210783  
**Tested commit:** f953794b8c5c3fb319f9ee62952892e196892797  
**Result:** **51 passed, 0 failed, 0 skipped**  
**BEM workflow:** https://github.com/Japharzadeh/WindFarm/actions/runs/40499210790 (passed)

## Test coverage

| Backend area | Verification | Result |
|---|---|---|
| BEM solver and polar import | Solver invariants, polar parsing, Reynolds interpolation, invalid input | PASS |
| Airfoil coordinates | Normalization/scaling, surface detection, zero-chord and nonfinite rejection | PASS |
| Blade-root profiles | Polygon analytical checks, centroidal moments, section moduli, dovetail/T-root/fir-tree geometry | PASS |
| Hollow-section buckling | Weak-axis Euler load against analytical calculation | PASS |
| Bolt and contact calculations | Thread-adjusted tensile capacity and Hertzian peak pressure | PASS |
| Material and laminate analysis | Material property sanity, mixed-material density, laminate stiffness and unassessed failure semantics | PASS |
| Thermal analysis | Free, uniaxial, biaxial restraint and equivalent-stress checks | PASS |
| Structural fatigue | Turning points, Goodman correction, invalid histories, zero-amplitude life | PASS |
| Turbulence | Reynolds number, closure outputs, nonphysical-input rejection | PASS |
| Blade mesh and geometry | Preset station endpoints and finite mesh coordinates | PASS |
| Reference-comparison metrics | Bias, MAE, RMSE and invalid-pair handling | PASS |
| **Total** | **51 automated tests** | **PASS** |

## Defects found and corrected

1. Airfoil upper/lower surface classification could depend on point order; geometric branch detection now swaps the branches when needed.
2. Airfoil normalization/scaling could silently continue with zero chord or invalid target lengths; invalid and nonfinite inputs are now rejected.
3. Polygon centroid used unsigned area in a signed formula, yielding incorrect centroids for clockwise polygons. The implementation now uses signed area.
4. Polygon second moments were taken about the origin but used as centroidal moments. They now use the parallel-axis theorem to shift to centroidal axes.
5. Section modulus assumed the centroid lay halfway through the bounding dimensions; it now uses the farthest extreme-fiber distance.
6. Fir-tree profile generation could exceed its requested width due to inconsistent step increments; the outline is now symmetric and bounded.
7. Hollow-section Euler buckling used only one bending axis; critical load now uses the weaker centroidal axis.
8. Hertz contact peak stress was set equal to average pressure. Peak line-contact pressure is now calculated separately and used in the simplified safety check.
9. Mixed-material laminate density used the first ply's density for every ply; it now uses each ply's material and thickness.
10. Laminate failure index was calculated from reciprocal strengths without applied stresses. It now reports an unassessed state rather than a dimensionally invalid safety claim.
11. Thermal stress did not specify restraint assumptions and treated the scalar stress as a signed divisor. Free/uniaxial/biaxial restraint options are now explicit, biaxial coupling is included, and safety uses equivalent plane-stress von Mises stress.
12. Turbulence methods masked invalid viscosity with a numerical floor; they now reject nonfinite and nonphysical inputs.
13. Fatigue input validation now checks finite, equal-length histories and strictly increasing time. Zero stress amplitude now maps to infinite S-N life.
14. A CSV comparison tool now calculates bias, MAE, RMSE, maximum absolute error, MAPE where defined, and per-condition metrics.

## External experimental validation

Official dataset sources and comparison procedure are documented in [REFERENCE_DATASETS.md](REFERENCE_DATASETS.md). Candidate sources include NLR's Ohio State wind-tunnel airfoil measurements, NREL/NASA Ames Phase VI turbine data, and the TU Delft IEA 15 MW PIV dataset. Their access conditions, licenses, geometries, units, and operating conditions must be checked before use.

**No raw experimental dataset has yet been imported and numerically compared against Airfoil-CAD output.** Therefore, the 51 passing tests establish software regression and analytical-invariant checks only; they do not establish agreement with laboratory measurements, full physical accuracy, or certification.

## Remaining engineering limitations

- The steady BEM solver does not replace free-vortex wake, dynamic stall, aeroelastic, or certification tools.
- Bolt-joint, Hertz-contact, thermal, and some material models remain simplified screening models and need independent engineering review.
- External comparison requires matched geometry and operating conditions, source/uncertainty metadata, and documented unit conversions.
