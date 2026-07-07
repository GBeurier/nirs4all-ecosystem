# Wave 8J - Cockpit Manual Blockers And Audits

Date: 2026-07-07

## Scope

- `nirs4all-cockpit`: public dashboard now surfaces non-secret manual release
  blockers from `ops/manual-actions.yaml` and `data/current.json`.
- `nirs4all-cockpit`: collect workflow now publishes
  `data/manual-actions.json` for GitHub Pages.
- `nirs4all-ecosystem`: submodule pointer updated for `nirs4all-cockpit`.
- Read-only audits coordinated for PyPI, CRAN/R-universe, and the protected
  `nirs4all-ui` paths consumed by `nirs4all-quality`.

## Decisions

- Manual release blockers are public facts, but secrets are not. The dashboard
  payload intentionally strips `secret_updates` while retaining action ids,
  affected packages, check notes, and manual URLs.
- `runiverse-core-rebuild` and `runiverse-io-rebuild` are marked done because
  current auto-checks resolve `nirs4all` 0.2.13 and `nirs4allio` 0.1.9 as green.
- CRAN actions for `n4m` and `pls4all` now reference the current 1.0.6 release
  tarballs instead of the stale 0.99.0 text.
- `nirs4alldatasets` is tracked as a CRAN resubmission to replace the stale or
  archived 0.2.0 publication with 0.3.5, not as a first submission.
- `nirs4all-ui` remains protected for active `nirs4all-quality` work: no edits
  under `src/lab`, `assets/theme.css`, `assets/brand/nirs4all`, or
  `assets/brand/quali`.

## Files Modified

- `nirs4all-cockpit`
  - `.github/workflows/collect.yml`
  - `README.md`
  - `cockpit/cli.py`
  - `cockpit/manual_actions.py`
  - `ops/manual-actions.yaml`
  - `tests/test_cli.py`
  - `tests/test_targets_topology.py`
  - `web/app.js`
  - `web/index.html`
  - `web/style.css`
  - `data/manual-actions.json`
- `nirs4all-ecosystem`
  - `docs/RELEASE_DISTRIBUTION_MATRIX.md`
  - `docs/agent_reports/WAVE_8J_COCKPIT_MANUAL_BLOCKERS_AND_AUDITS.md`
  - submodule: `nirs4all-cockpit`

## Tests

- `nirs4all-cockpit`: `python3.11 -m pytest -q` -> 119 passed.
- `nirs4all-cockpit`: `python3.11 -m cockpit.cli validate-targets
  ops/targets.yaml`.
- `nirs4all-cockpit`: `python3.11 -m cockpit.cli summarize
  data/current.json`.
- `nirs4all-cockpit`: `node --check web/app.js`.
- `nirs4all-cockpit`: headless Chrome DOM smoke on `web/index.html`, verifying
  `Manual blockers`, `pypi-publisher-core`, `nirs4all-core status=missing`, and
  `cran-resubmit-n4m-pls4all`.
- `nirs4all-cockpit`: JSON smoke confirms no `secret_updates` in
  `data/manual-actions.json`.

## Audit Results

- PyPI blockers remain external Trusted Publisher setup for
  `nirs4all-core`, `nirs4all-providers`, `nirs4all-tools`, `dag-ml`,
  `dag-ml-data`, `nirs4all-benchmarks`, and `nirs4all-repository`.
- R-universe stale cells are rebuild/snapshot issues for formats and
  `dagmldata`; `nirs4allio` and core are already green in current checks.
- CRAN remains manual/human-reviewed: `n4m`, `pls4all`, `nirs4allio`, and the
  core aggregate are pending; `nirs4alldatasets` needs a 0.3.5 resubmission.
- Safe future `nirs4all-ui` asset work should be add-only in paths such as
  `assets/defaults/**`, `assets/page-assets/**`, `assets/brand/<new-kit>/**`,
  `scripts/<new-generator>.mjs`, or `site/**`.

## Risks

- The cockpit is now clearer, but the seven PyPI missing targets cannot become
  green until PyPI Trusted Publishers are created or token-based uploads are
  deliberately used.
- CRAN acceptance remains outside automation and should not be represented as a
  completed release gate until live registry checks are green.
- `nirs4all-quality` consumes `nirs4all-ui` directly from sibling source aliases;
  UI asset/style work must avoid the protected paths listed above.
