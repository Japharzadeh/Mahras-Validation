# Airfoil-CAD backend acceptance and regression checks

This directory contains repeatable engineering-oriented checks for numerical backends. It is separate from the UI and does not claim certification.

## Run locally

From the repository root:

    python -m pip install numpy scipy pytest
    python "Airfoil CAD/validation/airfoilcad_acceptance/run_validation.py"

The runner writes CSV/JSON, Markdown, and SVG reports into reports/. GitHub Actions uploads these as a workflow artifact even when a test fails.

## Evidence policy

- Analytical invariants are not substitutes for experimental validation.
- No synthetic values are labeled as manufacturer or QBlade reference data.
- External dataset comparisons must record source, license, units, geometry, and operating conditions.
- Passing software tests do not establish suitability for real turbine design or certification.

## Defect found and corrected

The bolt-joint calculation used total_stiffness multiplied by clamp_length as a critical load, making the result depend on elastic modulus rather than bolt yield capacity. It now uses a thread-adjusted tensile area and a simplified remaining-yield-capacity estimate after preload. This remains a screening calculation: joint separation, prying, load sharing, fatigue, thread engagement, and applicable design standards are not modeled.
