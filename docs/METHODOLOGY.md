# Validation methodology

## 1. Purpose

The purpose of this repository is to preserve evidence that can be reviewed and, where the required software and source data are available, reproduced. It separates three questions that are often confused:

1. Does the software behave as specified?
2. Does a numerical model agree with an independent implementation or published reference under matched conditions?
3. Does the model agree with measurements from the physical system it is intended to represent?

A positive answer to the first question does not answer the second or third.

## 2. Evidence classes

### A. Software verification

Examples include unit tests, input validation, numerical invariants, regression tests and deterministic edge cases. Report the tested commit, test command, environment, counts and failures.

### B. Numerical cross-validation

Compare Mahras outputs with a second implementation or an external reference dataset. Use identical inputs and aligned definitions wherever possible. Record the reference software/version or dataset DOI, all relevant parameters, units, timestamps and transformations.

### C. Experimental or field validation

Compare model predictions with measured physical quantities. Preserve instrument details, calibration status, measurement uncertainty, site configuration, operating conditions and data-quality decisions. Do not label reanalysis or satellite-derived products as site measurements.

### D. Certification or standards assessment

This requires a defined standard, scope, competent independent assessment and the evidence required by that standard. Nothing in this repository should be read as certification unless a separate formal assessment is added.

## 3. Comparison procedure

For every comparison:

1. Define the engineering question and model boundary before selecting metrics.
2. Freeze the Mahras commit and the reference dataset/version.
3. Match geometry, orientation, operating conditions, time interval, units and sign conventions.
4. Preserve the original reference data; do not overwrite or silently clean it.
5. Document exclusions, missing values, interpolation and time alignment.
6. Calculate suitable metrics, including bias, MAE and RMSE where appropriate. Add normalized metrics only when the denominator is meaningful and non-zero.
7. Examine time-series, monthly/condition-wise residuals and outliers. A single aggregate score is not sufficient.
8. Apply a pre-declared acceptance threshold and explain its engineering basis.
9. Archive machine-readable inputs and outputs, figures, environment details and a readable report.
10. Record failed checks and unresolved discrepancies with the same visibility as passing checks.

## 4. Solar-specific considerations

Solar comparisons should distinguish irradiance on the horizontal plane, direct and diffuse components, plane-of-array irradiance, cell temperature, DC energy, inverter conversion and AC energy. A POA comparison is not a PV power validation. A yield comparison is only interpretable when weather periods, orientation, module/inverter definitions, losses and output boundaries are comparable.

Hourly comparisons require explicit timestamp semantics: UTC/local time, interval start or centre, daylight-saving treatment and missing-hour policy. Monthly or annual sums should never replace hourly residual analysis.

## 5. Wind and airfoil-specific considerations

Airfoil and rotor comparisons require matching airfoil geometry, Reynolds and Mach numbers, turbulence intensity, transition/roughness assumptions, rotor geometry, pitch, rotational speed, inflow and measurement definition. For wake or CFD comparisons, document mesh and domain sensitivity, boundary conditions, turbulence closure, convergence criteria and the experimental measurement plane.

An analytical invariant or a passing software test is useful verification evidence, but is not a substitute for a matched wind-tunnel or field benchmark.

## 6. Uncertainty and acceptance

Acceptance thresholds must be chosen before reviewing the final result and justified by intended use, reference uncertainty and model scope. Report both absolute and relative errors where meaningful. Avoid percentage errors near zero. Include sample count and excluded-pair count.

Where uncertainty is not quantified, state that explicitly. Do not convert a tolerance selected for a software regression test into a claim of physical accuracy.

## 7. Reporting and versioning

Each report should identify:

- Mahras repository and commit;
- date, environment and dependency versions;
- command and configuration;
- input and reference dataset identifiers, licenses and hashes;
- units, time basis and geometry;
- metrics, acceptance criteria and results;
- plots and machine-readable outputs;
- limitations, failed checks and next actions.

Store each run in a new dated directory. Preserve historical reports and explain any corrections in the evidence log.
