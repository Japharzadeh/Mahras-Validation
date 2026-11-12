# Composite failure model: independent engineering review

## Implemented scope

`composite_failure.py` adds a separate classical-laminate-theory (CLT) stress recovery and ply-failure assessment path. It does not silently change the existing UI's laminate calculations.

- Builds the laminate ABD matrix from each ply's thickness, angle, and orthotropic elastic constants.
- Solves membrane and bending strains from the six force/moment resultants `(Nx, Ny, Nxy, Mx, My, Mxy)`.
- Recovers local 1-2 ply stresses at both surfaces of each ply.
- Calculates 2-D Hashin fiber/matrix initiation indices and a Tsai-Wu index.
- Requires explicit positive values for `Xt, Xc, Yt, Yc, S` in SI Pa; no strength is inferred from generic isotropic ultimate strength.
- Reports the governing ply, surface, mode, and index. An index >= 1 means predicted initiation according to the selected criterion.

## Independent code-review findings

- The legacy laminate path previously derived its reported in-plane engineering constants from the bending stiffness matrix `D`. That is not generally valid for arbitrary layups. It now derives extensional engineering constants from `A^-1`, with an analytical isotropic regression test.
- The legacy `create_ply` helper still provides convenience fields derived from generic material ultimate strength (including a transverse strength estimated as half that value). Those fields are **not accepted as validated composite strengths** by the new failure solver.
- The legacy `analyze_laminate` deliberately returns `failure_index=None`, `failure_assessed=False`, and `is_safe=False` because it does not receive applied resultants or local ply stresses.
- The new CLT/Hashin/Tsai-Wu path is a separate backend API; it has not been connected to the existing GUI or material database, to avoid implying a user-facing safety assessment before strength provenance and benchmark checks are complete.

## Corrections applied to damage mechanics prototypes

- Progressive damage now reports a load step as converged only when every ply's initiation index is below 1. If damage reaches its cap while failure indices remain >= 1 and the state can no longer change, the step terminates as **nonconverged**. This prevents a false equilibrium/convergence claim.
- Progressive-damage input validation now rejects missing, non-finite, or non-positive ply properties used by the solver.
- The cohesive law now includes elastic work accumulated before damage onset in its work balance. The previous implementation omitted that contribution and could under-report dissipated energy before complete separation.
- Added regression checks for damage-cap nonconvergence, invalid ply properties, cohesive energy continuity at onset, and fracture-energy recovery at complete separation.
- The cohesive response still only represents a monotonic proportional separation path. `previous_damage` preserves irreversible damage, but without previous separation and mode-mix history the function does **not** calculate general unloading/reloading dissipation. This is explicitly documented and remains a limitation rather than being presented as a fully history-dependent constitutive model.

## Engineering assumptions and limitations

- Small-strain, linear elastic classical laminate theory; perfect bonding; plane stress per ply; no interlaminar stresses.
- Hashin is a ply-level initiation criterion, not a progressive-damage, delamination, open-hole stress-concentration, or fracture-mechanics model.
- Tsai-Wu uses the conventional interaction assumption `F12 = -0.5*sqrt(F11*F22)`; measured biaxial interaction data should replace this assumption where available.
- Strengths and moduli must be measured for the same fiber/matrix system, cure, layup, temperature, moisture, loading rate, and statistical basis. Manufacturer nominal values need traceable source metadata.
- This module is not a certification tool and does not establish structural safety by itself.

## Analytical verification

The tests compare uniaxial 0-degree response and failure index with closed-form results, test tension/compression/shear branches, check symmetric laminate coupling, and reject missing or nonphysical material inputs. These are implementation/analytical checks, not experimental validation.

## Experimental benchmark selected

Ma et al., *Experimental data on fracture of open-hole composite laminates subjected to tension loading*, Data in Brief 35 (2021), DOI: 10.1016/j.dib.2021.106876; dataset DOI: 10.17632/bxrwgtynp6.1. The dataset describes three CFRP layups tested to failure, with load-displacement, strain-gauge, and DIC measurements. The Mendeley record states CC BY 4.0:
https://data.mendeley.com/datasets/bxrwgtynp6/1

## Published experimental baseline (not a model comparison)

The paper reports measured peak forces of 43.96 kN for `[0]8`, 31.53 kN for `[0/90]2s`, and 24.81 kN for `[0/90/45/-45]s`. Its specimen dimensions are 160 mm width, 100 mm hole diameter, and 1.2 mm thickness. Using the nominal net section area `(160 - 100) * 1.2 = 72 mm²`, the corresponding measured nominal stresses are 610.56, 437.92, and 344.58 MPa. These are arithmetic transformations of reported experimental peak loads, **not model predictions** and not local stresses around the hole. The values are recorded in `validation/airfoilcad_acceptance/composite_experimental_reference.csv`.

## Required numerical validation protocol

Do not compare the local Hashin index directly with a specimen's global failure load. Open-hole failure is a structural problem with stress concentrations and possible damage progression. For a defensible comparison:
1. Retrieve and preserve the original workbook unchanged; record its checksum, source version, license, and sheet/column mapping.
2. Obtain the exact tested layup, ply thickness, coupon geometry, fiber/resin identity, and measured (X_t, X_c, Y_t, Y_c, S), plus uncertainty.
3. Use a matching structural stress field (validated finite-element/open-hole model or a suitable analytical solution) to recover local ply stresses around the hole.
4. Compare predicted initiation/failure load and failure mode against each experimental replicate, not only a single average.
5. Report bias, MAE/RMSE, relative error, scatter, uncertainty, and any exclusions. Separate calibration specimens from held-out validation specimens.

## Current status

The raw workbook is identified but is not available in this repository workspace or accessible through the connected GitHub file interface, so it has not been imported. No experimental error metrics or model-versus-experiment comparison are claimed. The measured peak loads above are reference observations only.

The progressive-damage and cohesive-interface routines are research backends, not yet calibrated to the selected test series, and the cohesive law is not coupled to a spatial stress/damage solver. Accordingly:
- Raw-data numerical comparison: **pending** workbook retrieval, sheet/column mapping, material property provenance, and an open-hole stress model.
- Progressive failure: **prototype implemented; experimentally unvalidated**.
- Delamination: **cohesive material-point law implemented; spatial delamination analysis not implemented**.
- Engineering accuracy and structural safety: **not certified or confirmed**.

Do not use these routines for safety-critical sizing or certification. A defensible closure requires matching material allowables, a validated open-hole stress field, multiple experimental replicates, uncertainty/error metrics, and independent engineering review.


## Running the current model prototypes

From the `Airfoil CAD` directory, install the project's existing NumPy and pytest dependencies in the active environment, then run:

```bash
python composite_damage_runner.py --output validation/composite_damage_demo.json
python -m pytest -q tests/test_composite_failure.py tests/test_progressive_damage.py tests/test_composite_damage_runner.py
```

The runner executes the CLT/Hashin baseline, the incremental ply-degradation prototype, and a 21-point monotonic cohesive material-point sweep. Its JSON output includes the input assumptions, per-step damage and convergence flags, and cohesive response samples. A nonconverged progressive-damage step is reported as such; the runner does not reinterpret it as equilibrium.

The included layup, strengths, loads, and cohesive parameters are synthetic demonstration values, not a material card for a real component. The runner is a reproducible smoke-test and inspection path, not experimental validation. It does not solve the open-hole coupon geometry, spatial stress redistribution, mesh-dependent damage localization, or delamination-front propagation.

## Next steps for a physically coupled model

A spatially resolved progressive-damage/delamination implementation still requires a structural solver or a validated finite-element coupling layer. Before adding one, choose and document the target solver and supported element formulation; define fracture-energy-regularized intralaminar damage, cohesive interface state/history, mesh objectivity, load control and equilibrium strategy; and verify against analytical cases before calibrating to raw experimental data. Do not describe the current pointwise law as a complete delamination solver.
