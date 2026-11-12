# External reference and experimental validation plan

This file distinguishes repeatable software tests from engineering validation against measurements.

## Recommended public reference sources

1. **NREL/NASA Ames Unsteady Aerodynamics Experiment (UAE) Phase VI**  
   Wind Data Hub sequences contain blade pressure and operating-condition data. Some downloads require the portal's sign-in/access workflow. Sequence I is an upwind, rigid rotor at 72 RPM with pitch 0 degrees and winds spanning the experiment's stated operating range. Use the exact sequence metadata and omit sentinel values such as \`-99999.99\` rather than treating them as measurements.  
   Source: https://wdh.energy.gov/data/uae6/uae6.z08.00  
   Test-program description: https://doi.org/10.2172/15000240

2. **IEA 15 MW model-turbine PIV benchmark (TU Delft / 4TU.ResearchData)**  
   Contains wind-tunnel flow fields, blade-level aerodynamic quantities, model geometry, and operating conditions for comparison with numerical models.  
   DOI: https://doi.org/10.4121/164890AB-39D7-4AF8-8B3C-9E21F789B80A

3. **Wind AI Bench (NLR)**  
   A collection of wind-energy datasets with dataset-specific metadata, access instructions, and licensing. Select a dataset only after checking that its quantities and conditions match the Airfoil-CAD model being evaluated.  
   Documentation: https://github.com/NREL/windAI_bench  
   Registry: https://registry.opendata.aws/nrel-pds-windai/

4. **NLR / Ohio State University wind-tunnel airfoil data**  
   The official archive lists experimental reports and data files for S809 and other wind-turbine airfoils. The source notes that test conditions and raw data are reported to support comparisons; some airfoil geometry is proprietary. Read the data disclaimer and each report's Reynolds number, transition/roughness setup, and units before using a polar.  
   Source: https://www.nlr.gov/wind/nwtc/airfoils-osu-data

## How to run a comparison

Prepare a CSV with paired measurements and model predictions for the *same* condition. Keep the source data unchanged in a separate, traceable input file. Include metadata in the accompanying record: source DOI/URL, source file name, license/access terms, units, geometry, wind speed, rotor speed, pitch, yaw, air density, Reynolds number, sensor uncertainty, and any excluded rows.

Example command:

    python "Airfoil CAD/validation/airfoilcad_acceptance/compare_reference_data.py" comparison.csv --reference measured_power_w --predicted mahras_power_w --group-by wind_speed_m_s --output reports/power_comparison.json

The script reports bias, MAE, RMSE, maximum absolute error, MAPE where reference values are nonzero, pair count, and per-condition metrics. It does not infer missing values or normalize units automatically.

## Dataset admission rules

- Do not compare unlike quantities or mismatched geometry/operating conditions.
- Convert units explicitly before comparison and record the conversion.
- Keep raw measured data and sentinel/missing-value handling auditable.
- Report measurement uncertainty and repeatability where available.
- Do not call an agreement result a certification. A BEM model is not expected to reproduce every 3-D, unsteady, aeroelastic, or stall phenomenon.
- No experimental measurements or benchmark results are fabricated or bundled in this repository. Until a verified reference file is imported and compared, experimental validation remains pending.
