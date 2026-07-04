# Wave 4CL - Cockpit/Core Release Sync

Generated: 2026-07-04T04:14:18Z

## Scope

- `nirs4all-cockpit`: expose target `channel`/`reason` in snapshots and UI tooltips; regenerate live snapshot.
- `nirs4all-org`: align public copy with V1 RC topology, core/providers/UI surfaces, and `lite` compatibility alias.
- `nirs4all-ui`: sync GitHub Pages showcase brand assets with package assets.
- `nirs4all-core`: align WASM optional upstream package names with scoped npm packages; wire E2E entrypoint checks; make multimodal R loader portable across Linux/macOS/Windows.
- `nirs4all-providers`: clarify `[all]` optional backing count and current benchmark dependency version.
- `nirs4all-benchmarks`: audited local divergent `main`; local commits were patch-equivalent to `origin/main`, old head preserved as `backup/codex-benchmarks-pre-origin-sync-20260704`, workspace realigned to `origin/main`.

## Agents / Review

- Codex release audit (`Kierkegaard the 4th`) found blockers around core PyPI trusted publishing, scoped wasm package naming, and benchmarks/provider dependency alignment.
- Codex cockpit/org audit (`Russell the 4th`) found stale public fallback copy and missing non-production reason visibility.
- Codex core/ui/providers audit (`Cicero the 4th`) found unwired E2E entrypoint checks, R loader portability gaps, and UI Pages asset drift.
- Main integrator reviewed diffs and kept `nirs4all` Python and `nirs4all-studio` production releases out of this wave.

## Tests Run

- `nirs4all-cockpit`: `git diff --check`; `node --check web/app.js`; `python3.11 -m cockpit.cli validate-targets ops/targets.yaml`; `python3.11 -m cockpit.cli summarize data/current.json`; `python3.11 -m pytest -q` -> 92 passed.
- `nirs4all-ui`: `git diff --check`; `npm run ci`; `npm run site:build`.
- `nirs4all-core`: `git diff --check`; `make test-e2e-entrypoints PYTHON=python3.11`; `PYTHONPATH=bindings/python/src python3.11 -m unittest -v bindings/python/tests/test_release_topology.py bindings/python/tests/test_cross_language_surface.py` -> 18 passed; `npm run test:v1-surface --prefix bindings/wasm` -> 14 passed.
- `nirs4all-providers`: `git diff --check`; `PYTHONPATH=src python3.11 -m pytest tests/test_registry.py tests/test_benchmarks_provider.py tests/test_local_release_gate.py -q` -> 22 passed; `python3.11 -m build` -> sdist/wheel built.
- `nirs4all-benchmarks`: `git cherry -v origin/main main`; targeted tests after realignment -> 32 passed; `python3.11 -m build` -> sdist/wheel built.

## Decisions

- Do not publish `nirs4all-core` as PyPI `nirs4all-core` until Trusted Publisher / release target is configured; cockpit now marks this as RC/pending rather than green.
- Treat `nirs4all-lite` as a compatibility alias while `nirs4all-core` is the V1 aggregate repo/package surface.
- Use scoped npm upstream names `@nirs4all/formats-wasm` and `@nirs4all/io-wasm` everywhere in core.
- Keep providers as a thin Python registry/contract facade for optional ecosystem providers, not as a numerical/runtime implementation.

## Risks / Follow-ups

- Providers build emits setuptools license metadata deprecation warnings; non-blocking for current RC but should be cleaned before the 2027 cutoff.
- Cockpit snapshot remains a live point-in-time status; non-production `reason` fields are now visible to avoid interpreting planned RC targets as failed production.
- Full parity gates remain intentionally deferred until the next large integration batch because they are long-running.
