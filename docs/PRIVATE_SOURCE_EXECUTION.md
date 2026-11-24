# Running validation against the private Mahras source

This repository is public, but the application source and its test suite remain in
`Japharzadeh/Mahras`. The workflow in
`.github/workflows/private-mahras-validation.yml` checks out that private repository
at run time, executes selected native test suites there, and publishes only a
sanitized summary.

## One-time setup

1. In the GitHub account, create a fine-grained personal access token restricted to
   the `Japharzadeh/Mahras` repository.
2. Grant **Contents: Read-only** permission only. Do not grant write, administration,
   workflow, or organization permissions.
3. In **Mahras-Validation → Settings → Secrets and variables → Actions**, add the
   repository secret named `MAHRAS_READ_TOKEN`.
4. Run **Actions → Private Mahras validation → Run workflow**.

The token is used only by the checkout action to read the private source. It is not
written to disk by the workflow, printed, or passed to the test process as an
environment variable.

## What runs

The workflow currently groups existing tests from the private source into:

- Solar shadow geometry, terrain integration, solar position and 3D shading.
- PV layout, system design, yield and hourly/component validation.
- Weather-station data, directional wind, Weibull, soiling, historical weather,
  aerodynamic CFD backend and wake cancellation.
- Airfoil BEM, composite failure, progressive damage and turbulence/Reynolds tests.

The workflow uses the tests in the private checkout directly. It does not copy
application modules, test files, fixtures, or private reports into this repository.

## What becomes public

Only `public-summary.json` is uploaded as a GitHub Actions artifact. It contains:

- the private source commit SHA;
- run timestamp and workflow run identifier;
- suite-level status and aggregate test/failure/error/skip counts;
- an explicit statement that source code, test names, traces and raw logs were not
  published.

JUnit XML and raw test logs stay in the ephemeral runner and are not uploaded.
The workflow does not commit source files or test output into the public branch.

## Trigger and cadence

- Manual: Actions → Private Mahras validation.
- Scheduled: daily at 02:23 UTC.
- The scheduled run always checks out the current `main` of the private source.

A public-repository workflow cannot receive private-repository push events by itself.
If immediate validation on every private push is required, add a small dispatch
step in the private repository later; that step should trigger this workflow without
sending source code or test artifacts.

## Scope and limitations

- This is software regression verification, not field validation or certification.
- A failed suite is reported as failed; missing JUnit output is not treated as a pass.
- The runner environment is Ubuntu/Python 3.12. Platform-specific desktop rendering,
  live external-data availability, OpenFOAM execution, and hardware acceleration
  are not claimed as validated by these suites.
- Review the test groups when the private suite layout changes.
