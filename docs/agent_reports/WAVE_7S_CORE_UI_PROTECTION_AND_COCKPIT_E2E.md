# Wave 7S - Core/UI Protection, Cockpit RC11, And E2E Custom Host

Date: 2026-07-07

## Scope

Continued the V1 refactor without touching `nirs4all-ui` or `nirs4all-quality`, because another agent is actively using those repos for the `nirs4all-quality` project.

## Agents / Reviews

- Codex main lane: reviewed and integrated finished worker output, ran validation, committed reports.
- Codex worker `Cicero`: implemented the missing cross-language E2E doc guard in `nirs4all-ecosystem`.
- Codex worker `Pauli`: aligned `nirs4all-cockpit` RC11 prose, HTTPS Pages evidence, and manual actions.
- Codex explorer `Tesla`: read-only GitGuardian audit for `nirs4all-cluster`.
- Claude Code read-only audit: launched for a second opinion on core/providers/methods naming and packaging. It used read-only tools only and did not modify files.

## Repos / Files Changed

- `nirs4all-ecosystem`
  - `docs/CROSS_LANGUAGE_E2E.md`
  - `tests/test_e2e_scenarios.py`
  - Commit pushed: `a5a3d45` (`test(e2e): guard cross-language scenario documentation`).
- `nirs4all-cockpit`
  - `ops/targets.yaml`
  - `ops/manual-actions.yaml`
  - `cockpit/reconcile.py`
  - `data/current.json`
  - `ROADMAP.md`
  - `tests/test_reconcile.py`
  - `tests/test_targets_topology.py`
  - Commit pushed: `574de20` (`chore(cockpit): align rc11 release status`).

No files were modified in `nirs4all-ui`, `nirs4all-quality`, `nirs4all-drafts`, or `nirs4all-lab`.

## Validation

- `nirs4all-ecosystem`
  - `python3 scripts/n4a_e2e_scenarios.py validate` -> OK, 11 scenarios.
  - `python3 -m pytest -q tests/test_e2e_scenarios.py` -> 87 passed.
  - GitHub Actions on `a5a3d45`: `Cross-language E2E scenarios` success, `version-guard` success.
- `nirs4all-cockpit`
  - `./.venv/bin/n4a-cockpit validate-targets ops/targets.yaml` -> OK, 21 packages, 100 targets.
  - `./.venv/bin/pytest -q` -> 111 passed.
  - `./.venv/bin/ruff check .` -> OK.
  - `python3 -m json.tool data/current.json` -> OK.
  - GitHub Actions on `574de20`: `pages` success, `version-guard` success.
- `nirs4all-core`
  - `PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH make test-v1-surfaces` -> Rust/Python/WASM passed.
  - Rust: `cargo fmt --all --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace` -> 9 passed.
  - Python V1 surfaces -> 59 passed.
  - WASM V1 surfaces -> 15 passed + TypeScript typecheck.
  - R and Octave were not available in this WSL environment, so those optional gates reported `SKIP/RISK`.
- `nirs4all-providers`
  - `PYTHONPATH=src python3.11 scripts/validate_contracts.py --canonical ../nirs4all-ecosystem/docs/contracts/providers` -> PASS.
  - `PYTHONPATH=src:../nirs4all-datasets/src:../nirs4all-repository/src:../nirs4all-benchmarks/src:../nirs4all-papers/src:../nirs4all-io/src python3.11 -m pytest -q -rs` -> all tests passed with no skips.

## Cockpit Snapshot

Current committed snapshot remains honest:

- `green=86`
- `stale=2`
- `pending=4`
- `missing=7`
- `broken=0`
- `unknown=0`
- `excluded=1`

Remaining non-green targets are real external blockers:

- Missing PyPI: `nirs4all-providers`, `nirs4all-tools`, `nirs4all-core`, `dag-ml`, `dag-ml-data`, `nirs4all-benchmarks`, `nirs4all-repository`.
- Pending CRAN: `n4m`, `pls4all`, `nirs4allio`, `nirs4all`.
- Stale CRAN/PyPI legacy: `nirs4alldatasets`, `nirs4all-lite`.

## Architecture / Naming Notes

- `nirs4all-core` exists and is the canonical portable aggregate repo.
- The Python aggregate distribution intentionally remains `nirs4all-core`, with imports `nirs4all_lite`, `nirs4all_core`, and `n4a`, because the full Python `nirs4all` package still owns the `nirs4all` import/distribution line until the production cutover.
- Non-Python core bindings already use the bare `nirs4all` name where appropriate:
  - Rust crate `nirs4all`.
  - npm package `nirs4all`.
  - R package `nirs4all`.
  - MATLAB/Octave namespace `+nirs4all`.
- `nirs4all-providers` is an optional Python client over neutral provider contracts. It is not a runtime controller layer, and R/WASM/Rust dataset access should consume the neutral schemas/artifacts directly rather than depending on Python.

## Security Audit

The `nirs4all-cluster` GitGuardian alert was audited read-only:

- `HEAD`, `origin/main`, and `origin/rc/v1-full-refactor` are clean.
- The finding is historical example CLI credential-shaped text around `2026-07-02 09:19:53 UTC`, already cleaned from current heads.
- No secret value was printed or copied into this report.
- If the examples were never real credentials, mark the alert as false-positive/mitigated in GitGuardian. If any value was reused as a real token, rotate it.

## Decisions / Risks

- Full Python parity was not rerun in this batch by request; only targeted V1 surface and contract gates were run.
- `nirs4all-ui` asset consolidation remains intentionally unmodified in this wave because another agent owns concurrent work there.
- PyPI Trusted Publisher and CRAN actions remain external blockers; cockpit now states them explicitly instead of marking them green.
