# WAVE 10O - Runtime E2E and Release-Lock Audit

Date: 2026-07-08

## Scope

After the `nirs4all-ui@0.1.9` web/custom-host propagation and cockpit refresh,
run the executable cross-language E2E gate and prove the aggregation lock from
an isolated selected-member checkout.

## Files Modified

- `docs/RELEASE_DISTRIBUTION_MATRIX.md`
- `docs/agent_reports/WAVE_10O_RUNTIME_E2E_LOCK_AUDIT.md`

## Tests And Gates

- `python3.11 scripts/n4a_e2e_scenarios.py run-ready --execute`
  - result: `11/11` ready scenarios executed successfully;
  - covered R/Python/WASM/Web, datasets/io, multimodal, multisource,
    repository, papers, converter, predictions, cluster, formats, methods,
    performance comparison, and custom core+UI hosts.
- `python3.11 scripts/n4a_e2e_scenarios.py evidence`
  - result: `11/11 scenarios verified; artifacts=70 failures=0`.
- `python3.11 scripts/n4a_e2e_scenarios.py coverage`
  - result: `ready=11`, `blocked=0`, `full_strict_ready=true`,
    `strictness_gaps=0`, `python_parity strict=11`.
- `python3.11 scripts/n4a_release_lock.py checkout-members --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json --output /tmp/n4a-release-lock-selected`
- `python3.11 scripts/n4a_release_lock.py --workspace-root /tmp/n4a-release-lock-selected validate --manifest docs/contracts/release/aggregation-manifest.n4a.json --lock docs/contracts/release/aggregation-lock.n4a.lock.json`
  - result: selected lock validated against isolated checkouts at the pinned
    commits.
- GitHub Actions:
  - `nirs4all-web@4539f31`: `web-ci`, `version-guard`, and Pages succeeded.
  - `nirs4all-cockpit@d8b26c0`: `ci`, `version-guard`, and Pages succeeded.
  - `nirs4all-ecosystem@61804c1`: `version-guard` and Cross-language E2E
    scenarios succeeded.

## Decisions

- Keep the aggregation lock authority tied to the selected lock checkout, not
  to live submodule gitlinks that may contain newer non-selected product heads.
- Treat the executed `run-ready --execute` result as the current ecosystem
  runtime proof for core/UI/custom-host/cross-language scenarios, separate from
  the still-held Python production cutover.

## Risks / Follow-Up

- `nirs4all` Python production remains held back: current Python defaults and
  fallback inventory still require the strict cutover gates before switching
  production to dag-ml/native by default.
- `nirs4all-quality` still consumes sibling `nirs4all-ui` source aliases rather
  than the public `nirs4all-ui/lab` and `nirs4all-ui/assets/*` exports.
- Studio/Web shared-component convergence is not complete; Web proves the
  custom-host package surface, but many Studio/Web feature components remain
  local to their apps.
