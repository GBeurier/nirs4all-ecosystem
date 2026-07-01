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

Pending.
