# W16 - Web Runtime Fallback Smoke Gate

Status: salvaged after max-turns, verified, and committed.

## Scope

W16 covered B-018 for `nirs4all-web/studio-lite`: prove runtime fallback
diagnostics are typed, survive the worker boundary, and are covered by a reliable
WSL smoke runner.

## Changes

- Added `npm run smoke` via `studio-lite/scripts/run-smokes.mjs`.
- The smoke runner starts `vite preview`, polls real readiness, runs matching
  `tests/*smoke.mjs`, pins Chrome, and always tears the preview process group
  down.
- Added engine-layer forced-failure coverage for scheduler and variant-planning
  degrade paths.
- Added worker-boundary tests proving a typed `RtErrorException` is rebuilt from
  worker messages and ordinary worker errors stay plain `Error`s.

## Verification

From `_worktrees/W16-web-rt-smoke/studio-lite` with WSL Node:

```bash
export PATH="$HOME/.nvm/versions/node/v22.21.1/bin:$HOME/.cargo/bin:$PATH"
export CHROME=/usr/bin/google-chrome
npm run typecheck
npm run test
npm run build
npm run smoke -- rt-fallback smoke
```

Results:

- TypeScript typecheck passed.
- Vitest: `16 passed`, `115 passed`.
- Vite production build passed.
- Browser smokes: `23/23` passed.
- Preview teardown verified: `port4345 closed`.

## Commit

`1a1bdba test(web): add reliable runtime fallback smoke gate`
