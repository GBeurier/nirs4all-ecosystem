# Wave 4G - Public topology, Cockpit surfaces, and GitGuardian refresh

Date: 2026-07-02  
Coordinator: Codex

## Scope

Follow-up to Waves 4E/4F after reviewer feedback and the user-reported
GitGuardian alert on `GBeurier/nirs4all-cluster`.

Full Python parity was not rerun in this wave. The next large gate should run
full parity on the selected RC heads because the Python/dag-ml runtime changed
after the last full result.

## Published code

| Repo | Branch | Head / tag | Files changed |
| --- | --- | --- | --- |
| `nirs4all-org` | `rc/v1-full-refactor` | `9417073` / `n4a-v1-rc1-2026.07-refactor` | static site topology docs |
| `nirs4all-cockpit` | `rc/v1-full-refactor` | `7da47eb` / `n4a-v1-rc1-2026.07-refactor` | `ops/targets.yaml`, `data/current.json`, README/ROADMAP/tests |
| `nirs4all-cluster` | `main` | `727480c` | rewritten secret-clean history |
| `nirs4all-cluster` | `rc/v1-full-refactor` | `c4df557` / `n4a-v1-rc1-2026.07-refactor` | rewritten secret-clean history |
| `nirs4all-ecosystem` | `rc/v1-full-refactor` | this report commit | security/control reports and this report |

## Changes

- `nirs4all-org` now describes the public V1 topology without overclaiming:
  Python `nirs4all` remains the oracle, Studio is the desktop product,
  `web.nirs4all.org` is client-side-only/WASM, `nirs4all-lite` remains the
  current portable aggregate lineage, and `nirs4all-core` is the V1 target
  aggregate naming.
- `nirs4all-cockpit` now tracks `nirs4all-providers` and `nirs4all-tools` as
  explicit RC planned PyPI surfaces. They stay outside `nirs4all-core`:
  providers is an optional Python facade over neutral contracts, and tools is
  the migration/converter toolkit.
- Cockpit topology tests now lock the `nirs4all-core`/legacy-lite split,
  Python oracle, client-side Web, shared UI package, providers, and tools.
- The GitGuardian follow-up was upgraded to a targeted history rewrite for
  `nirs4all-cluster`. Published refs now expose rewritten history and local
  scanner-style checks report no remaining candidate.

## Parallel reviews

| Reviewer | Mode | Key result |
| --- | --- | --- |
| Codex reviewer | read-only | Confirmed that Cockpit/Org/UI/Web evidence must not be treated as full release proof; requested full Python parity and web/UI CI hardening before final RC sign-off. |
| Claude Code reviewer | read-only | Confirmed the RC topology is coherent but not release-clean; highlighted stale parity narratives, UI CI gaps, and Cockpit omission of providers/tools. |

## Tests and gates

Cockpit:

- `python3.11 -m cockpit.cli validate-targets ops/targets.yaml` ->
  `21 packages, 89 targets`.
- `python3.11 -m json.tool data/current.json` -> OK.
- `python3.11 -m ruff check .` -> clean.
- `python3.11 -m pytest -q` -> `84 passed`.
- `python3.11 -m cockpit.cli collect --offline --only nirs4all-providers,nirs4all-tools --out /tmp/n4a-rc-extra-surfaces-current.json` -> `missing=2`.
- `python3.11 -m cockpit.cli summarize data/current.json` ->
  `green=75 stale=2 pending=5 missing=7 broken=0 unknown=0 excluded=0`.

Org:

- `git diff --check` -> clean.
- JSON-LD extraction parse -> OK.
- `sitemap.xml` XML parse -> OK.
- Inline JavaScript extracted and checked with `node --check` -> OK.
- `tidy` was not installed, so no HTML validator ran.

Cluster security:

- History scan over rewritten local refs for `N4CLUSTER_TOKEN`,
  `Authorization/Bearer`, and CLI-option-secret-like patterns ->
  `sensitive_candidate_count 0`.
- `git ls-remote` confirms published refs:
  `main=727480c`, `rc/v1-full-refactor=c4df557`,
  `n4a-v1-rc1-2026.07-refactor=e0784fa`.
- `uv run --extra dev pytest -q` in `nirs4all-cluster` ->
  `142 passed, 1 skipped, 1 deselected, 3 warnings`.

## Risks and decisions

- The GitGuardian finding looks like a placeholder/documentation-token alert
  from local evidence. If GitGuardian shows a value that was ever a real
  deployed credential, it must still be revoked; the history rewrite cannot
  make a leaked credential safe.
- Cockpit full live collect was intentionally not committed in this wave. A
  network collect can churn many public registry cells; the committed snapshot
  is a topology-aligned RC snapshot, not a fresh full registry scrape.
- `nirs4all-providers`, `nirs4all-tools`, `nirs4all-ui`, and `nirs4all-core`
  target package names are still planned/missing on their target registries.
- Web client-only and UI package checks are stronger than before, but CI still
  needs explicit gates before final release sign-off.
- Full Python-reference parity, dag-ml/native parity, migration golden tests,
  Studio/Web runtime contract tests, and methods binding parity remain final
  gates before production cutover.
