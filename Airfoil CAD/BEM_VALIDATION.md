# Steady BEM analysis in Mahras Airfoil-CAD

## Purpose

This module adds a steady blade-element/momentum (BEM) calculation to the existing rotor-design screen. The existing CAD and rotor-preview workflow remains in place. The solver accepts an airfoil polar exported from QBlade or another documented source; it does not copy or embed QBlade source code.

## Importing a polar

In the Rotor tab, build the rotor preview and choose **Steady BEM analysis**. The importer accepts QBlade `.plr` files, headed CSV files, and whitespace-delimited polar text containing angle of attack and lift/drag coefficients. QBlade `.plr` Reynolds metadata is read when present. For generic text files, use headers such as `AOA`, `Alpha`, `Cl`, and `Cd`; angle of attack is in degrees and CL/CD are dimensionless. Select multiple polar files to build a Reynolds-dependent polar family; enter Reynolds numbers for files that do not contain metadata. The solver interpolates CL and CD in logarithmic Reynolds space and stops if the local Reynolds number falls outside the imported range. With one polar, the same data is reused at all Reynolds numbers and a warning is emitted.

Use polars matching the intended airfoil, Reynolds number, Mach number, and surface condition. If the polar does not cover an operating angle, the solver stops rather than silently inventing stall data.

## Model scope and assumptions

- Steady, axial-flow, horizontal-axis rotor.
- Blade-element/momentum formulation with Prandtl hub/tip loss correction and a high-induction branch.
- Spanwise chord is estimated from CAD-mesh cross-sections.
- Spanwise twist is currently assumed to be zero by the integrated UI; therefore results are provisional for blades whose twist distribution is not represented in the mesh workflow.
- The imported 2-D polar is currently reused at all radial stations. Multiple Reynolds polars can be supplied and interpolated by local Reynolds number, but the current implementation still uses the same airfoil polar family at all span stations. Dynamic stall, yawed inflow, shear, tower interaction, elastic deformation, free-vortex wake, controller dynamics, and IEC load cases are not implemented by this feature.
- A result is not a certification result and must not be presented as such.

## Validation procedure before engineering use

1. Use a documented QBlade example rotor and its exact blade geometry, blade count, hub/tip radii, pitch, rotor speed, air density, wind speed, and matching polar.
2. Confirm that both tools use the same sign conventions, radius convention, units, loss corrections, and operating point.
3. Compare sectional angle of attack, induction factors, thrust, torque, power, (C_P), and (C_T), not only the final power value.
4. Repeat across low, rated, and high tip-speed ratios and include a case close to the onset of high induction.
5. Record the QBlade version, polar source, settings, exported reference data, numerical differences, and any excluded cases in a version-controlled benchmark dataset.
6. Set acceptance tolerances only after reviewing the benchmark data. Do not label the solver validated until the tests pass and an independent reviewer has checked the comparison.

## Automated tests

Run from the repository root in an environment with NumPy and pytest installed:

```bash
python -m pytest "Airfoil CAD/tests/test_bem_solver.py" -q
```

The included tests cover polar validation, strict refusal to extrapolate, geometry validation, and finite integrated results. They are software checks, not validation against QBlade or wind-tunnel measurements.

## QBlade licensing note

The QBlade Community Edition uses the Academic Public License and is intended for non-commercial use and evaluation. Mahras should obtain written licensing guidance from QBlade before including or depending on its engine in a commercial product. Exported user-provided data and independently implemented published methods are separate from copying QBlade source, but the applicable license and data provenance should still be reviewed before release.


## Comparing against a QBlade reference case

The repository includes a QBlade `.plr` importer and comparison utility, but no reference results are fabricated or bundled. Export a reference case from QBlade after matching the blade geometry, polar(s), air density, kinematic viscosity, pitch, wind speed, rotor speed, blade count, and loss-correction settings. Record the QBlade version and exact setup alongside the CSV.

Create a CSV with these required columns:

```csv
metric,reference_value,relative_tolerance,absolute_tolerance,unit
power_w,REPLACE_WITH_QBLADE_VALUE,0.05,0,W
thrust_n,REPLACE_WITH_QBLADE_VALUE,0.05,0,N
torque_nm,REPLACE_WITH_QBLADE_VALUE,0.05,0,N*m
cp,REPLACE_WITH_QBLADE_VALUE,0.05,0,-
ct,REPLACE_WITH_QBLADE_VALUE,0.05,0,-
sections[0].cl,REPLACE_WITH_QBLADE_SECTION_VALUE,0.05,0,-
```

Replace every placeholder with values exported from the same operating point; the placeholder file is a schema example, not runnable benchmark data. Summary metrics and section values such as `sections[0].cl`, `sections[0].angle_of_attack_deg`, and `sections[0].axial_induction` are supported.

Run the comparison:

```bash
python "Airfoil CAD/validation/compare_qblade_reference.py" bem_results.json qblade_reference.csv
```

The tool exits with code 0 only when all comparisons pass. Tolerances must be justified from the benchmark plan; the default 5% is only a convenient starting point, not a certification criterion. Compare sectional values and integrated loads, not only power.

Official QBlade example models and test datasets are available at https://qblade.org/downloads/ . Choose a model whose geometry, airfoil polars, and operating point can be reproduced in Mahras. QBlade's documentation describes steady BEM as a low-cost preliminary performance method and distinguishes it from its higher-fidelity free-vortex-wake and unsteady models.
