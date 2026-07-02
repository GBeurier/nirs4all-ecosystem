# Wave 3AL - Providers Papers Facade

Date: 2026-07-02

## Scope

Lane J follow-up after `nirs4all-papers` gained its first-party provider/export
facade. The goal was to make `nirs4all-providers` consume that public facade
instead of continuing to depend on lower-level papers internals.

Boundaries preserved:

- `nirs4all-papers` remains the reproducible archive/export implementation.
- `nirs4all-providers` exposes a provider adapter over that public facade.
- No execution, upload, ecosystem writeback, runtime, prediction, or converter
  behavior changed.
- `nirs4all-drafts` and `nirs4all-lab` were not touched.

## Agent Board

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Nietzsche the 2nd | `nirs4all-providers` papers adapter implementation | integrated | Commits `0142ac2` and `ad7ac5d`. |
| Popper the 2nd | `nirs4all-providers` review and re-review | GO | Confirmed lazy facade delegation, fallback compatibility, and release-gate coverage. |

## Integrated Changes

### `nirs4all-providers`

- Updated `PaperExportProvider` to lazy-import and delegate to
  `nirs4all_papers.provider` when available.
- Preserved compatibility fallback for older `nirs4all-papers` checkouts.
- Added public adapter methods:
  - `load_paper_bundle()`;
  - `export_sidecars(paper_dir, out)`.
- Kept `load_paper()` as the compatibility alias.
- Made `export_sidecars()` require the first-party papers facade instead of
  reimplementing private sidecar writes in providers.
- Updated capabilities mapping for the real facade payload:
  - handles facade `verbs`;
  - maps `writes="local_output"`;
  - unions adapter compatibility services such as `load_paper`, `citation`, and
    `bibtex`.
- Updated provider documentation, release-gate expectations, conformance tests,
  and papers provider tests.

## Files Modified

- `README.md`
- `src/nirs4all_providers/papers.py`
- `src/nirs4all_providers/release_gate.py`
- `tests/test_conformance.py`
- `tests/test_papers_provider.py`

## Validation

Post-integration validation in `nirs4all-providers`:

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3.11 -m pytest tests/test_papers_provider.py tests/test_release_gate.py tests/test_conformance.py -q -p no:cacheprovider` -> 20 passed, 4 skipped.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3.11 -m pytest -q -p no:cacheprovider` -> 69 passed, 4 skipped.
- `PYTHONPATH=src ruff check src tests` -> passed.
- `PYTHONPATH=src mypy src/nirs4all_providers` -> passed.
- Real facade smoke with both local packages on `PYTHONPATH` confirmed the
  adapter sees `list_papers`, `inspect_bundle`, `load_paper`,
  `load_paper_bundle`, `build_methods_section`, `citation`, `bibtex`,
  `build_repro_page`, and `export_sidecars`.
- `git diff --check HEAD~2..HEAD` -> passed.

## Gate Policy

- Full Python-reference parity was intentionally not run for this small Lane J
  adapter batch, per the batching policy for long parity suites.
- No runtime, prediction, save/load, converter, native method, WASM, R, or Python
  aggregate behavior changed.
- The release surface matrix remains the explicit accounting gate for the
  required `nirs4all` Python, R, and browser/WASM surfaces.

## Risks

- `PaperExportProvider.capabilities()` still trusts a facade-provided
  `executes` value. The release gate catches a bad execution claim, but the
  adapter does not clamp it by itself.
- If the real facade omits `portability`, the adapter reports
  `portability=None` instead of substituting fallback explanatory text.
- The adapter depends on `nirs4all_papers.provider.export_sidecars()` for local
  export writes; older papers checkouts without that facade cannot use
  `export_sidecars()` through providers.
