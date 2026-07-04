# Wave 4BB - Active Goal Operating Constraints

Date: 2026-07-04

This report records the additional operating constraints added to the active
NIRS4ALL V1 refactor goal after the latest workspace reset/context handoff.
It is a coordination note only; it does not supersede the release locks,
aggregation manifests, or repo-local `AGENTS.md` / `CLAUDE.md` files.

## Added constraints

- Root workspace scope is `/home/delete/nirs4all`.
- Repo-local `AGENTS.md` / `CLAUDE.md` files remain mandatory before editing a
  child repository.
- `nirs4all-drafts` and `nirs4all-lab` remain private and out of scope.
- In repositories with a `.codegraph/` directory, CodeGraph must be used before
  grep/direct reads when locating or understanding indexed code. Direct reads
  and repo test gates still remain authoritative for final decisions.
- Claude Code may be used again for parallel review/implementation, but every
  Claude Code MCP call must pass `allowedTools` explicitly:
  `["Bash", "Read", "Write", "Edit", "Glob", "Grep", "Task"]`.
- Add `WebFetch` / `WebSearch` to Claude Code only when the specific task needs
  network access.
- Claude Code sessions must be polled to completion with their `sessionId` and
  cursor; permission requests should be answered `allow_for_session` when they
  appear.
- Full parity runs remain deferred until large integrated batches, because they
  are long. Targeted gates should be run per lane before integration.

## Active goal interpretation

The active goal still targets release-candidate readiness across the ecosystem:
core/lite naming closure, UI/package surfaces, cockpit/site correctness,
publications for non-prod-critical repos, and roughly ten executable
cross-language ecosystem e2e scenarios. The two prod-sensitive projects remain
held back from final production release:

- `nirs4all` Python package.
- `nirs4all-studio`, except for a Windows RC installer intended for local
  manual testing.

## Current immediate lane

The current implementation lane is the ecosystem e2e suite. The first concrete
target is to turn at least one blocked cross-repo scenario into an executable,
honest partial gate without hiding remaining blockers.
