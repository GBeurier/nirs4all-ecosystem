# Wave 2T Release Gate Completion

Date: 2026-07-01T15:56:47+02:00

## Scope

Follow-up after W2S. Claude is not used. `nirs4all-drafts` and
`nirs4all-lab` remain out of scope.

W2T promotes recent reviewed proof work into first-class release evidence
without changing runtime numerical behavior:

- W2R/W2S installed-`n4m` proof should become a visible non-full release gate.
- W2S providers local sibling gate should become visible release evidence with
  explicit real dependency paths.
- The public V1 `nirs4all` surfaces for Python, R, and WASM/browser must remain
  explicitly gated through the aggregate/lite topology, not only documented.
- Old worktrees/branches from interrupted runs must not be merged without audit.

Full Python-reference parity remains deferred for a larger runtime/numerical
batch. W2T must not run `pyref_oracle_full` unless the coordinator explicitly
changes this scope.

## Starting State

- W2S integrated:
  - `nirs4all-ecosystem` `dd90b02`
  - `_worktrees/INT-nirs4all` `7ab1ec1e`
  - `_worktrees/INT-providers` `314c8681`
- W2S non-full cutover passed with `pyref_oracle_full` skipped.
- W2N already integrated lite V1 surface gates for Python, R, and WASM/browser
  in `nirs4all-lite` through `8fa133b`.

## Agents

| Lane | Agent | Write Scope | Task |
| --- | --- | --- | --- |
| A/C/F/J/G/E | pending | `nirs4all-ecosystem` docs/scripts/tests only | Add or tighten cutover/release gates for installed `n4m`, providers local sibling release, and lite Python/R/WASM V1 surfaces. Do not run full parity. |
| E | pending | `nirs4all-lite` only | Audit the existing V1 Python/R/WASM aggregate gates and patch only if a real gap remains; otherwise report no-change with exact commands. |
| K | pending | read-only across non-private repos and `_worktrees` | Audit superseded/preexisting worktrees and current integration heads; identify anything still relevant without merging it. Do not code. |

## Review Criteria

- Agents must read local `AGENTS.md` / `CLAUDE.md` before editing a repo.
- No old worktree or branch merges without fresh audit.
- No private repos touched.
- No strict gate weakening, xfail, or silent fallback.
- New gates must be bounded, reproducible on this machine, and allowed to skip
  R only through the existing explicit availability-aware R policy.
- Any dependency resolver change must be explicit and local; do not assume PyPI
  contains unreleased ecosystem packages.

## Expected Gates

- Ecosystem manifest/readiness tests and cutover self-check.
- Installed-`n4m` proof default/local-deps evidence remains green.
- Providers local sibling gate passes with real local dependency paths and keeps
  bare missing-dependency failures honest.
- Lite `make test-v1-surfaces` runs Python and WASM, and skips R only if R is not
  installed locally.
- Non-full cutover gate after integration.

## Integration Log

### 2026-07-01T16:02:29+02:00

Lane A/C/F/J/G/E completed in `nirs4all-ecosystem` only.

- Added required non-full release gates to
  `docs/contracts/cutover/drop-gates.n4a.json`:
  - `installed_n4m_proof`, bounded by `timeout 1800`, running
    `python3.11 scripts/prove_installed_n4m.py --install-deps` in
    `_worktrees/INT-nirs4all` with explicit local `dag-ml` and `dag-ml-data`
    paths.
  - `providers_local_sibling_release`, bounded by `timeout 900`, running
    `nirs4all_providers.local_release_gate` in `_worktrees/INT-providers` with
    explicit dependency venv paths for `nirs4all-datasets` and
    `nirs4all-repository`.
  - `lite_v1_surfaces`, bounded by `timeout 1800`, running
    `make test-v1-surfaces` in `nirs4all-lite` with the selected Node path and
    `PYTHONPATH=bindings/python/src`.
- Promoted the corresponding readiness rows:
  - new `W2S-INSTALLED-N4M-001`;
  - promoted `PROV-READ-001` from advisory/readiness command to required
    `providers_local_sibling_release`;
  - new `LITE-V1-SURFACE-001`.
- Added ecosystem tests asserting the new required gates, command shapes, and
  readiness links.

Validation:

- `python3 -m json.tool docs/contracts/cutover/drop-gates.n4a.json`
- `python3 -m json.tool docs/contracts/cutover/readiness-matrix.n4a.json`
- `python3 scripts/n4a_cutover_gates.py validate --workspace-root /home/delete/nirs4all`
- `python3 -m pytest tests/test_cutover_state_gate.py -q` (`4 passed`)
- `python3 scripts/n4a_cutover_gates.py run --workspace-root /home/delete/nirs4all --gate installed_n4m_proof --gate providers_local_sibling_release --gate lite_v1_surfaces --skip pyref_oracle_full --timeout 2400 --json` passed.
  - `installed_n4m_proof` reported `NIRS4ALL_INSTALLED_N4M_OK`.
  - `providers_local_sibling_release` reported `ok: true`.
  - `lite_v1_surfaces` ran Python and WASM; R skipped only through the existing
    `test-r-if-available` policy because `R` is not installed locally.
- `python3 -m pytest tests -q` (`13 passed`)
- `python3 scripts/n4a_release_surface_matrix.py validate`
- `python3 scripts/n4a_release_surface_matrix.py report`
- `python3 scripts/n4a_cutover_gates.py readiness --workspace-root /home/delete/nirs4all --gate installed_n4m_proof --gate providers_local_sibling_release --gate lite_v1_surfaces --json`
- `git diff --check`

`pyref_oracle_full` was not run.
