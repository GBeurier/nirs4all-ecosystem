# W106 - Full parity and runtime evidence batch

Date: 2026-07-10

## Scope

Fresh full-parity batch after the Python/Studio transition work:

- Python `nirs4all` reference parity oracle, including legacy vs `dag-ml`
  dual-engine conformance, committed legacy baselines, native results, export,
  dataplane, generation, multi-source, repetition, and public API smokes.
- Native `dag-ml` gate for the selected workspace head.
- Cross-language ecosystem runtime evidence for the 11 strict scenarios.
- Studio lint, unit/backend tests, and Playwright web runtime smoke.

## Evidence

`nirs4all`:

- Command: `.venv/bin/python -m pytest -ra tests/integration/parity/ -v`
- Result: `799 passed`, `0 skipped`, `0 xfailed`, `0 failed`.
- Duration: `2278.06s` (`0:37:58`).
- Log: `/tmp/n4a-full-parity-nirs4all-20260710-181851.log`.

`dag-ml`:

- Commands:
  - `cargo fmt --all --check`
  - `cargo clippy --workspace --all-targets -- -D warnings`
  - `cargo test --workspace`
  - `cargo run -p dag-ml-cli -- validate-graph examples/minimal_graph.json`
  - `python3 scripts/validate_contracts.py`
  - `python3 scripts/check_so_freshness.py`
- Result: green. The workspace tests reported `575` executed Rust/C/CLI tests
  plus `2` ignored perf probes; contract validation and extension freshness
  passed.
- Log: `/tmp/n4a-full-parity-dag-ml-20260710-181851.log`.

`nirs4all-ecosystem`:

- Commands:
  - `python3.11 scripts/n4a_e2e_scenarios.py validate`
  - `python3.11 -m pytest -q tests/test_e2e_scenarios.py`
  - `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-full-parity-e2e-artifacts-20260710-181851 run-ready --execute`
  - targeted reruns for the external GitHub-auth release gate and the custom
    app host scenario
  - `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-full-parity-e2e-artifacts-20260710-181851 evidence --ready-only --max-age-seconds 14400`
  - `python3.11 scripts/n4a_e2e_scenarios.py --artifacts-dir /tmp/n4a-full-parity-e2e-artifacts-20260710-181851 evidence-ledger --max-age-seconds 14400 --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
  - `python3.11 scripts/n4a_e2e_scenarios.py coverage --require-full-strict`
- Result: `11/11` scenarios verified, `70` artifacts, `0` failures,
  `full_strict_ready=true`, `strictness_gaps=0`.
- Updated: `docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json`
  now records `max_age_seconds: 14400` for the fresh runtime evidence batch.
- Logs:
  - `/tmp/n4a-full-parity-ecosystem-20260710-181851.log`
  - `/tmp/n4a-full-parity-ecosystem-formats-gh-rerun-20260710-182554.log`
  - `/tmp/n4a-full-parity-ecosystem-custom-host-20260710-182650.log`

`nirs4all-studio`:

- Commands:
  - `npm run lint:parallel`
  - `npm run test:parallel`
  - `PATH=/home/delete/nirs4all/nirs4all-studio/.venv/bin:$PATH CI=1 npx playwright test --project=web-chromium`
- Result:
  - lint passed.
  - backend/frontend test batch: `2237 passed`, `59 skipped`, `0 failed`.
  - Playwright: `63 passed`.
- Logs:
  - `/tmp/n4a-full-parity-studio-20260710-181851.log`
  - `/tmp/n4a-full-parity-studio-e2e-rerun-20260710-182058.log`

## Superseded Transient Failures

- The first Studio Playwright attempt used the local non-CI Playwright command,
  whose web server command resolves `../nirs4all/.venv/bin/python`; that Python
  did not have `uvicorn`. The rerun forced Studio's `.venv` through `PATH` with
  `CI=1` and passed.
- The first ecosystem MATLAB/Octave release-gate check hit unauthenticated
  GitHub API rate limits. The token stored in `/home/delete/nirs4all/github_token`
  returned `401`, so the gate was rerun with the active `gh auth token` and
  passed.
- The first rerun of the formats scenario proved that scenario but correctly
  reported missing custom-host artifacts in the shared artifact directory. The
  custom-host scenario was executed explicitly; final evidence verification then
  passed for all 11 scenarios.

## Decisions

- The Python parity gate is now strict and has no skip/xfail debt in this run.
- Studio's 59 skipped tests are not part of the Python/dag-ml parity oracle.
  They remain visible as Studio-suite debt to audit separately before claiming a
  zero-skip Studio release gate.
- The local runtime evidence ledger is fresh for the artifact batch under
  `/tmp/n4a-full-parity-e2e-artifacts-20260710-181851`; future checks should
  either reuse that directory while it remains available or execute a new batch.

## Risks / Follow-up

- Studio Windows RC smoke remains a Windows-side manual gate.
- CRAN submissions remain manual.
- A strict production cutover gate still depends on the prepared RC workspace
  topology selected for the final Python `nirs4all` and `nirs4all-studio`
  transition release.
