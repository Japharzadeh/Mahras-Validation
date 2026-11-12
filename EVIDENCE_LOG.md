# Evidence log

This log records the status of evidence packages included in the repository. Dates refer to the source snapshot or recorded test run, not necessarily the date on which this repository was updated.

## Solar PV model comparison — 2026-10-25

**Package:** `validations/results/component_yield_2026-10-25/`

- Includes an acceptance matrix, model-comparison CSV files, a JSON summary, a written report and SVG figures for monthly component bias, plane-of-array irradiance, transposition and time alignment.
- The report records comparisons against PVGIS and Open-Meteo-derived quantities, with the time convention and model boundary discussed in the package.
- The report also records a material difference between annual production estimates from the complete internal and PVGIS workflows. That difference remains visible in the evidence; it is not converted into a pass by comparing only annual totals.
- The source report identifies unresolved monthly POA discrepancies requiring investigation.
- No calibrated on-site irradiance or power measurements were supplied for this package. It is not field validation.

**Status:** numerical cross-check with open discrepancies; no field-validation claim.

## Solar PV transfer-angle comparison — 2026-10-25

**Package:** `validations/results/component_yield_2026-10-25_tilt32/`

- Preserves the separate 32° / 190° transfer-angle report and monthly PVGIS transposition-bias data.
- This package should be read separately from the roof-orientation case; the two geometries are not interchangeable.

**Status:** retained as a distinct comparison case.

## Earlier solar POA comparison — 2026-10-17

**Package:** `validations/results/run_2026-10-17/`

- Preserves the earlier monthly comparison, summary JSON, acceptance matrix and source CSVs.
- This is a historical run preceding later time-alignment and component-yield work.
- It must not be substituted for the later report when describing the current state of the solar validation work.

**Status:** historical evidence; useful for traceability, not the latest result.

## Airfoil-CAD backend regression snapshot — 2026-10-27

**Package:** `Airfoil CAD/validation/airfoilcad_acceptance/`

- The source status document records 51 passed, 0 failed and 0 skipped automated checks.
- The test summary is a snapshot of software regression coverage.
- The package includes test code, a runner, comparison utilities and a reference-data plan.
- Passing regression checks do not establish agreement with wind-tunnel measurements, QBlade results or a certified engineering design.

**Status:** recorded software regression pass; independent experimental validation remains incomplete.

## Composite reference data

**Package:** `Airfoil CAD/validation/airfoilcad_acceptance/composite_experimental_reference.csv`

- Contains literature-derived specimen metadata and measured peak-force values.
- The source record explicitly marks predicted failure-force comparison as pending because the required material strengths and raw workbook are not yet available.

**Status:** reference data catalogued; comparison not completed.

## Weather-station import fixtures

**Package:** `validation/weather/`

- Contains a 24-row synthetic valid sample and a separate edge-case fixture.
- The fixtures are intended to exercise timestamp parsing, unit handling and quality-control logic.
- They are not observations from a meteorological station and do not validate the accuracy of a weather sensor or forecast model.

**Status:** software input fixtures only.

## What is not yet evidenced here

At this snapshot, the repository does not contain a complete independent field-validation package for a deployed solar site, a complete measured wake/CFD benchmark for a wind farm, or a certification assessment. Absence of evidence is not a pass.
