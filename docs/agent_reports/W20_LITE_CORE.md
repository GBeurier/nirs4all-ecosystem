# W20 - Lite/Core Naming Facades

Status: completed by agent and committed.

## Scope

W20 handled the first safe naming/governance slice for the aggregate/lite
bindings: expose additive import facades without renaming the distribution yet.

## Changes

- Added `n4a` Python import facade over the existing `nirs4all_lite` surface.
- Added `nirs4all_core` forward-compatible alias.
- Packaged both facades with `py.typed`.
- Added facade tests for parity, passthrough, legacy import, and no shadowing of
  the full Python `nirs4all` library.
- Added `docs/NAMING.md` and linked it from binding/index docs.
- Cleaned contradictory license metadata by keeping the SPDX expression as the
  authoritative license record.

## Verification

Agent-reported gates:

- 23 Python unittests passed, 1 skipped due missing methods bindings.
- Ruff clean.
- Wheel and sdist build.
- Built wheel metadata license check.
- Built-wheel import checks for facade parity.

## Commit

`2f379ef feat(python): additive n4a / nirs4all_core aggregate facades (LOCK-GOV slice)`
