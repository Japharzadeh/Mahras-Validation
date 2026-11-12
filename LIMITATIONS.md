# Limitations and open validation work

This document is intended to make the boundary of the current evidence easy to see. It should be updated whenever a new validation package is added.

## Solar modelling

- The available reports compare model outputs with PVGIS and Open-Meteo-derived data. These are useful independent software/data cross-checks, but they are not calibrated measurements collected at the project site.
- Annual-energy agreement can conceal hourly and monthly errors. The monthly bias, hourly residuals, time alignment and component-level comparisons must be considered together.
- The source reports record unresolved monthly plane-of-array discrepancies and differences between complete annual-yield workflows. These remain open engineering questions.
- A comparison is only meaningful when weather period, orientation, module assumptions, losses, temperature model, DC/AC boundary and time convention are aligned or explicitly accounted for.
- No site-specific measured irradiance and inverter/power time series are included here. Therefore field validation and guaranteed yield are not established.

## Airfoil-CAD, rotor and structural calculations

- The recorded 51-test result is a software regression snapshot. It verifies selected code paths and analytical invariants, not all physical behaviour.
- The available QBlade comparison utility is a mechanism for comparing supplied result files; the presence of the utility does not mean a complete QBlade benchmark has been performed.
- The external airfoil and rotor reference-data plan identifies candidate datasets. Dataset-specific geometry, Reynolds number, Mach number, turbulence, transition, roughness and operating conditions still need to be matched before comparison.
- The BEM documentation describes model assumptions and omissions. Results should not be interpreted beyond those assumptions.
- Composite reference rows are not yet fully compared. The source record identifies missing material-strength provenance and raw source data.
- No certification, design approval or structural safety assessment is implied.

## Weather data

- The station CSV files are synthetic fixtures created for software tests.
- They can test parsing and validation rules but cannot establish sensor accuracy, station representativeness, forecast quality or climatological suitability.

## Reproducibility

- Some runners import modules from the Mahras application repository. This evidence repository does not include the complete application source or a frozen runtime image.
- Public API-backed runs may change as upstream datasets and API versions change. Preserve raw inputs, request parameters, timestamps, package versions and hashes for every new run.
- Historical CI links may point to the legacy private `WindFarm` repository and may not be accessible to an external reviewer.

## Minimum work before stronger claims

1. Run each benchmark from a pinned Mahras commit and archive the exact input files, environment and complete outputs.
2. Complete paired hourly comparisons with traceable measured site data for solar irradiance and electrical power.
3. Complete at least one matched airfoil/rotor benchmark against an accessible experimental dataset, with geometry and operating conditions documented.
4. Complete the composite comparison only after material properties and the original experimental data are available.
5. Publish uncertainty, acceptance thresholds and failed cases alongside passing results.
6. Have an independent reviewer check the methodology and reproduce a representative run.

Until then, describe the work as software verification and model-to-model/reference-data comparison, not field validation or certification.
