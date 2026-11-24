# Mahras Validation

**Engineering evidence for the Mahras renewable-energy software**

This repository is the public record of selected verification and validation work carried out for Mahras. It brings together the reports, source datasets, comparison tables, test snapshots and figures that help a reviewer understand what has been checked, how it was checked, and what remains open.

The intention is not to present every passing test as proof of engineering accuracy. Each result is kept with its scope, reference source, assumptions and limitations so that the evidence can be assessed on its own merits.

> **Current evidence boundary:** the material includes software regression tests and numerical comparisons against independent software/reference datasets. It does not establish field validation, product certification, or guaranteed performance at a real project site.

## What is included

| Area | Evidence in this repository | Current interpretation |
|---|---|---|
| Solar resource and PV modelling | Hourly and monthly comparisons, PVGIS reference outputs, POA component tables, time-alignment checks and SVG figures | Numerical agreement is assessed by model layer. Differences between complete annual-yield estimates remain documented rather than hidden. |
| Airfoil-CAD and rotor engineering | Backend acceptance tests, BEM and composite-model notes, reference-data plan, sample comparison data and a test-summary figure | A recorded 51-test software regression snapshot is available. It is not an experimental benchmark or certification result. |
| Weather-station import | Small valid and edge-case CSV fixtures with test instructions | Synthetic test fixtures for parsing and quality-control behaviour; not measured weather observations. |
| Site and financial analysis | Khalkhal site report and rooftop financial reconciliation data | Project-specific analytical evidence; assumptions and data provenance must be read with each report. |

## Start here

1. [Results catalogue](docs/RESULTS_CATALOG.md) — a reviewer-oriented guide to the evidence.
2. [Validation methodology](docs/METHODOLOGY.md) — how comparisons, tolerances and evidence classes are treated.
3. [Products and model scope](docs/PRODUCTS.md) — which Mahras components are covered.
4. [Validation policy](docs/VALIDATION_POLICY.md) — rules for claims, acceptance and reporting.
5. [Limitations and open work](LIMITATIONS.md) — what the current evidence does not prove.
6. [Evidence log](EVIDENCE_LOG.md) — dated snapshots and their recorded status.
7. [Source provenance](SOURCE_PROVENANCE.md) — source repository, commit and file-level traceability.

## Repository map

- `reports/` — curated report packages already maintained in this repository.
- `validations/` — solar validation runners, archived outputs, tables and figures transferred from the Mahras project.
- `Airfoil CAD/validation/` — Airfoil-CAD acceptance and reference-comparison material.
- `Airfoil CAD/BEM_VALIDATION.md` and `Airfoil CAD/COMPOSITE_FAILURE_VALIDATION.md` — model scope and engineering caveats.
- `validation/weather/` — weather-station test fixtures and instructions.
- `docs/` — methodology, product scope, reproducibility, reporting and policy.

## Reading a result correctly

A result should always be read together with its input data, model boundary, reference source, units, time convention and acceptance criterion. In particular:

- A unit test verifies specified software behaviour; it does not prove that a physical model matches nature.
- Agreement with another software package is a cross-model comparison, not automatically an independent measurement.
- Reanalysis and satellite-derived datasets are not substitutes for calibrated instruments at the project site.
- A yearly total can agree while hourly or monthly errors remain material. The detailed time-series and residual plots matter.
- A missing comparison is not a pass. Where source data or material properties are incomplete, the status is explicitly left open.

## Reproducing the work

Some validation runners use modules from the Mahras application repository and are therefore intended to be run alongside a matching Mahras source checkout. This repository preserves the validation material and its provenance; it is not a complete copy of the application. Each package describes its required environment and execution path.

For a new run, use a new dated output directory. Do not overwrite a historical result. Record the Mahras commit, dependency versions, input-file hashes, reference dataset version, command, run date and generated artifacts.

## Language

The repository uses English for the top-level review structure and retains original Persian reports and project notes where they are part of the source record. Original wording and historical results are preserved unless a correction is clearly identified.

---

**Mahras — engineering evidence, not marketing claims.**


## Live validation of the private source

The public workflow can run the current private Mahras test suites without copying
application code or tests into this repository. Configure the read-only
`MAHRAS_READ_TOKEN` repository secret, then run
[Private Mahras validation](.github/workflows/private-mahras-validation.yml).
See [private-source execution instructions](docs/PRIVATE_SOURCE_EXECUTION.md).
