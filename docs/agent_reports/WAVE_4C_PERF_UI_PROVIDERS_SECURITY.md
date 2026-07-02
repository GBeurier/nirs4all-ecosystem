# Wave 4C - perf gate, UI/providers audits, cluster security follow-up

Date: 2026-07-02  
Coordinator: Codex

## Scope

Post full-parity-closeout batch. No changes in `nirs4all-drafts` or
`nirs4all-lab`. Full parity was not rerun in this batch; per coordinator policy
it is reserved for a larger integration batch.

## Published code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all` | `rc/v1-full-refactor-python` | `3d568abe504f` / `n4a-v1-rc1-2026.07-refactor` | `scripts/bench_engine_perf.py`, `tests/unit/test_bench_engine_perf.py` |

Change summary:

- `scripts/bench_engine_perf.py` now acts as a CI-usable legacy vs dag-ml
  perf gate: strict `engine=...`, `allow_fallback=False`, explicit
  `--max-wall-ratio`, `--max-rss-ratio`, `--max-score-delta`, stable JSON
  payload with `ratios`, strict `allow_nan=False`, and automatic prediction
  count delta check when both engines are compared.
- The benchmark child now closes `RunResult` explicitly before process exit to
  avoid shutdown-time import/cleanup noise.
- Unit coverage added for ratio computation, unavailable comparison handling,
  gate failure messages, and strict JSON serialization.

## Tests and smokes

In `_worktrees/RC-v1-nirs4all-python`:

- `PYTHONPATH=... /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/unit/test_bench_engine_perf.py -q -ra --tb=short` -> `3 passed`.
- `/home/delete/nirs4all/nirs4all/.venv/bin/ruff check scripts/bench_engine_perf.py tests/unit/test_bench_engine_perf.py` -> clean.
- `python scripts/bench_engine_perf.py --cases pls_small --repeats 1 --json /tmp/n4a_py_engine_perf_gate.json --max-wall-ratio 10 --max-rss-ratio 10` -> pass; observed `wall=0.233x`, `rss=0.957x`, prediction count delta `0`.
- Negative gate smoke: `--max-wall-ratio 0.01` -> fails as expected.
- Mono-engine diagnostic smoke: `--engines legacy --cases pls_small --repeats 1` -> pass.

In `_worktrees/RC-v1-benchmarks` before this code commit:

- `PYTHONPATH=src /home/delete/nirs4all/nirs4all-benchmarks/.venv/bin/python -m pytest tests/test_performance_compare.py -q -ra --tb=short` -> `1 passed`.
- `nirs4all_benchmarks.performance_compare --suite python_run --repeats 1` -> direct `nirs4all.run()` dag-ml/legacy run ratio about `0.547x`.
- `nirs4all_benchmarks.performance_compare --suite studio_run --repeats 1` -> Studio training worker dag-ml/legacy run ratio about `0.713x`.

These are smoke measurements on seeded synthetic cases, not final production
performance claims.

## Agent reviews

| Lane | Agent | Scope | Outcome |
| --- | --- | --- | --- |
| A | Codex release/naming reviewer | `nirs4all-lite`, `RC-v1-nirs4all-core`, ecosystem release contracts, cockpit, org | `nirs4all-core` is an RC/local future aggregate, not a published production surface. Public production still points at `nirs4all-lite`. Release lock validation is stale against the living workspace. Matrix covers Python/R/WASM products, but `nirs4all-ui` is not yet treated as a separately published public package. |
| H | Codex UI/Web/Studio reviewer | `nirs4all-ui`, Studio, Web | `nirs4all-ui` exists and is consumed by Studio/Web. Web uses shared React components; Studio currently consumes shared `score`/`runtime` helpers but keeps a local badge component. RC Web has a client-side-only test and sibling UI checkout action; main Web lacks those proofs. |
| H | Claude UI/Web/Studio reviewer | Same, read-only | Confirmed Web production is static GitHub Pages and Node is build/test only. Flagged hybrid `nirs4all-ui` distribution, missing UI repo CI, Studio component adoption gap, and need to extend client-only tests to remote `<link>`/font resources. |
| G/E | Codex providers/datasets reviewer | `nirs4all-providers`, datasets, IO, R bindings | `nirs4all-providers` Python is an optional facade, not the source of truth. Portable provider contract should be JSON/catalog/checksum + native bindings. R can resolve/fetch/verify datasets, but `nirs4allio` R still lacks materialization/load surface equivalent to Python. |
| J/K | Codex perf reviewer | Python perf script, Studio runtime tests, benchmarks | Identified lack of threshold gates in Python `bench_engine_perf.py`; this batch implements the wall/RSS/score gate and JSON contract. Studio perf comparison remains covered by `nirs4all-benchmarks perf-compare`, not by Studio itself. |

## GitGuardian / cluster follow-up

User reported a GitGuardian "Generic CLI Option Secret" alert for
`GBeurier/nirs4all-cluster`, pushed on 2026-07-02 at 09:41:03 UTC.

Current published refs checked:

- `main` -> `911c0edd1849`
- `rc/v1-full-refactor` -> `7c4621b52ca7`
- `n4a-v1-rc1-2026.07-refactor^{}` -> `7c4621b52ca7`

Checks run locally on `nirs4all-cluster`:

- `rg` secret-pattern scan over the working tree excluding `.git`, virtualenvs,
  caches, and `node_modules` -> no match.
- `git grep` secret-pattern scan on published `main` and
  `rc/v1-full-refactor` -> no match.
- No local `gitleaks`, `trufflehog`, or `ggshield` binary was installed, so
  this is not a substitute for the GitGuardian server-side finding. The alert
  should still be resolved in GitGuardian after confirming the exact historical
  secret fingerprint; if it represented a real credential, it should be revoked
  even though the published refs are now clean.

Local cluster branches previously identified as contaminated/superseded remain
local-only and must not be merged without audit.

## Decisions

- Keep production-facing install docs on `nirs4all-lite` until the
  `nirs4all-core` package/repo/registry migration is actually published and
  verified. `nirs4all-core` is RC/cutover preparation, not current prod.
- Treat `nirs4all-ui` as real shared code, but not yet as a fully published
  release package until distribution mode and CI are settled.
- Keep `nirs4all-providers` Python as an idiomatic optional facade. Portable
  provider semantics must live in neutral contracts and native bindings, not in
  hidden Python behavior.
- Do not relaunch full Python parity after this small perf-gate batch. Relaunch
  after the next substantial integration batch.

## Remaining gaps

- Release lock/manifest needs a refresh once the final selected RC heads are
  fixed; current release/naming review found stale lock validation.
- Studio should either adopt `nirs4all-ui/components` for the runtime badge or
  document that React components are Web-only for now.
- Web client-only test should cover remote `<link>` and font/preconnect
  resources in addition to script/API/network bans.
- R provider/dataset story needs a small high-level provider/card API and IO
  materialization/load binding before it matches Python ergonomics without a
  Python shim.
