# Source provenance and transfer record

## Source snapshot

The material added in this consolidation was read from the default branch of the private application repository:

- Source repository: [Japharzadeh/Mahras](https://github.com/Japharzadeh/Mahras)
- Source branch: `main`
- Source commit: `df33091843481ff9dc1dc04855fa642229266ddb`
- Source commit date: 2026-11-12
- Destination repository: [Japharzadeh/Mahras-Validation](https://github.com/Japharzadeh/Mahras-Validation)
- Destination branch: `main`

The source repository was private at the time of transfer. The destination repository is public. The owner should review the licensing and disclosure implications of publishing any transferred material before using this repository as an external submission package.

## Material transferred

The consolidation includes the following source areas:

- `validations/`: solar validation scripts, reports, JSON summaries, CSV comparison tables, archived run outputs, Persian methodology and site reports.
- `validation/weather/`: weather-station test instructions and synthetic CSV fixtures.
- `Airfoil CAD/validation/`: Airfoil-CAD acceptance tests, comparison utilities, reference dataset notes, sample data and the existing SVG test summary.
- `Airfoil CAD/BEM_VALIDATION.md` and `Airfoil CAD/COMPOSITE_FAILURE_VALIDATION.md`: engineering scope, assumptions and limitations.

The existing destination reports and documentation were retained. Where a source artifact had a newer version than an existing destination copy, the source snapshot was used for the consolidated evidence package.

## Git object identity

Git blob IDs are content-addressed identifiers. The transferred files retain their original blob IDs where GitHub returned the same content, which provides a useful integrity check. The source commit above is the authoritative snapshot reference; file paths alone should not be treated as sufficient provenance.

Selected solar artifacts:

| Source path | Blob SHA |
|---|---|
| `validations/results/component_yield_2026-10-25/report.md` | `f889f57bba6f85bfd4d635407c326a49fa795c83` |
| `validations/results/component_yield_2026-10-25/component_yield_summary.json` | `b6455494774938b072ba9d64923c1cdca83fc64e` |
| `validations/results/component_yield_2026-10-25/acceptance_matrix.csv` | `c78a326c870763bfa9c5e9085dbe4295aa69cb92` |
| `validations/results/component_yield_2026-10-25/monthly_component_bias.svg` | `36393fb34833244ef0287a8c27d6002156fb8be8` |
| `validations/results/component_yield_2026-10-25/monthly_poa_bias.svg` | `0fac29dcccd2dcd6773c7495f2c5add64e3fb7d3` |
| `validations/results/component_yield_2026-10-25/time_alignment_mae.svg` | `85c6aff3936488b364d30dcba97fa71d77551d59` |
| `validations/results/component_yield_2026-10-25/poa_model_comparison.csv` | `45709e053a0f2edd73fa95f86528551ac006b86d` |
| `validations/results/component_yield_2026-10-25/annual_yield_model_comparison.csv` | `e835fa8099115f7187a0c39fe95c0fe1125d3e32` |
| `validations/results/component_yield_2026-10-25_tilt32/report.md` | `3358218b6af6b8eefc9409b4c399032b93da0d75` |

Selected Airfoil-CAD artifacts:

| Source path | Blob SHA |
|---|---|
| `Airfoil CAD/validation/airfoilcad_acceptance/VALIDATION_STATUS.md` | `9fc3ea862933d6ef5e9fd71946617be0b2371034` |
| `Airfoil CAD/validation/airfoilcad_acceptance/test_backend_acceptance.py` | `c21deaacdc84115c7102fd2121e6b579b583f95c` |
| `Airfoil CAD/validation/airfoilcad_acceptance/validation_summary.svg` | `6d9ea4c9b56c341bba4688716a1b1706a9e3bc76` |

## Preservation rules

- Historical reports are retained as dated snapshots; they are not silently rewritten to reflect later code.
- New runs should be added under a new date or run identifier.
- Corrections to an existing report must be explained in its change history.
- Synthetic fixtures must remain labelled synthetic.
- External reference datasets must retain their original citation, license and usage conditions.
- A copied script is not automatically reproducible in this repository if it imports application modules that are not included here.

## Known source-link caveat

Some historical CI references in the source documents point to the legacy `WindFarm` repository. They are retained as historical provenance, not represented as current public CI runs for this repository.
