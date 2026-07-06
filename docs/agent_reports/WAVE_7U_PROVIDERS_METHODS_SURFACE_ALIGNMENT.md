# Wave 7U - Providers And Methods Surface Alignment

Date: 2026-07-07

## Scope

Integrated two non-UI lanes while protecting concurrent `nirs4all-ui` / `nirs4all-quality` work:

- `nirs4all-providers`: keep only neutral-contract-backed public facets.
- `nirs4all-methods`: align JS/WASM and MATLAB/Octave public binding names with the V1 surface.
- `nirs4all-ecosystem`: synchronize the canonical provider descriptor contract.

No files were modified in `nirs4all-ui`, `nirs4all-quality`, `nirs4all-drafts`, or `nirs4all-lab`.

## Agents / Reviews

- Codex worker `Anscombe`: implemented the providers trim in `nirs4all-providers`.
- Codex worker `Pascal`: implemented the methods JS/MATLAB naming patch in `nirs4all-methods`.
- Codex main lane: reviewed both diffs, fixed providers/site/security and methods distribution-doc consistency, synchronized the canonical ecosystem provider contract, ran gates, committed and pushed.

## Repos / Commits

- `nirs4all-providers`
  - Commit pushed: `6dc8a16` (`refactor(providers): keep only neutral contract facets`).
  - Public registry/API now exposes `datasets` and `repository` only.
  - Removed public `BenchmarkProvider` and `PaperExportProvider` facets and their dedicated tests.
  - Release gates, local release harness, publish workflow, extras, README/site/security/CITATION now describe providers as dataset/repository clients.
- `nirs4all-methods`
  - Commit pushed: `599582e9` (`refactor(bindings): align methods JS and MATLAB names`).
  - JS/WASM npm package renamed from `@nirs4all/methods-wasm` to `@nirs4all/methods`; CMake target renamed from `pls4all_wasm` to `n4m_wasm`; JS error type renamed from `Pls4allError` to `N4mError`.
  - MATLAB/Octave gained a V1 `+n4m` namespace that delegates to the existing `+pls4all` implementation; `+pls4all` remains compatibility, and numerics remain behind the shared `libn4m`/MEX layer.
  - Added `bindings/matlab/test/test_n4m_alias.m` and wired it into Octave/MATLAB gates.
- `nirs4all-ecosystem`
  - Canonical `provider_descriptor.v1` now reflects the public provider read slice as `datasets` / `repository`.
  - `capabilities.writes` is now restricted to `none`, `local-cache`, or future-reserved `gated`; benchmark local stores and paper local outputs remain in their owning repos, not in the provider descriptor.

## Validation

- `nirs4all-providers`
  - `.venv/bin/python scripts/ci_gate.py` -> PASS.
  - Covered version-sync, Ruff, mypy, pytest, conformance, and neutral-contract byte identity against `nirs4all-ecosystem`.
- `nirs4all-methods`
  - `git diff --check` -> PASS.
  - `scripts/bump_version.sh --check` -> PASS (`project=1.0.5`, `ABI=2.0.0`).
  - `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH make test-js-wasm` -> PASS.
  - JS/WASM smoke/parity tests passed and `npm pack --dry-run` produced package `@nirs4all/methods@1.0.5`.
  - Octave/MATLAB alias test was not run locally because neither `octave` nor `matlab` is available in this WSL session; it is wired into CI/release gates.
- `nirs4all-ecosystem`
  - `python3 scripts/n4a_e2e_scenarios.py validate` -> OK, 11 scenarios.
  - `python3 -m pytest -q tests/test_e2e_scenarios.py` -> 87 passed.
- `nirs4all-core`
  - Commit `e29ee1b` CI completed successfully, including `version-guard`, `python`, `npm`, `rust`, `r`, `matlab-octave`, and `strict-parity`.

## Decisions

- Providers are neutral clients only where a neutral schema exists today: `datasets` and `repository`.
- Benchmarks and papers remain first-class ecosystem repos, but not public facets of `nirs4all-providers`.
- MATLAB/Octave V1 surface is `+n4m` with `+pls4all` compatibility rather than copying numerical logic.
- JS/WASM V1 surface is `@nirs4all/methods`; no legacy JS alias was kept for `@nirs4all/methods-wasm` or `Pls4allError`.

## Risks / Follow-Up

- The JS rename is intentionally breaking for consumers importing `@nirs4all/methods-wasm` or `Pls4allError`.
- `nirs4all-methods` CI must confirm `test_n4m_alias.m` under Octave, because this local WSL environment lacks Octave.
- Ecosystem documents that still describe historical provider plans may mention benchmarks/papers as old provider candidates; the canonical contract and current release gate now override that.
