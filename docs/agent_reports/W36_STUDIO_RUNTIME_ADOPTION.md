# W36 report - Studio runtime adoption

Summary:
W36 moved Studio spectral stats toward the core/runtime surface. `/spectra/{dataset_id}/stats` now prefers `nirs4all.core.metrics.compute_spectral_statistics`, while preserving the existing route schema and keeping a fallback for older runtimes.

Code changed:
- Added lazy import support for the core spectral statistics helper.
- Routed metrics computation through the helper when available.
- Updated performance/route tests for the preserved wire shape.

Files touched:
- `api/lazy_imports.py`
- `api/shared/metrics_computer.py`
- `tests/test_spectra_perf.py`

Commits:
- `nirs4all-studio/refactor/W36-runtime-adoption` `f5094c2`
- Integrated into `nirs4all-studio/refactor/integration-studio` as `64b43c7`

Tests run:
- `PYTHONPATH=. .venv/bin/python -m pytest tests/test_spectra_perf.py -q` -> `10 passed`.
- Targeted `compileall` -> passed.
- Targeted Ruff -> passed.

Impact:
Advances `B-017` by reducing Studio-local compute duplication without changing the route contract.

Next action:
Continue pushing analysis/dataset/preprocessing/chart computations out of Studio backend into shared runtime/core helpers.

Sync doc updated: yes
