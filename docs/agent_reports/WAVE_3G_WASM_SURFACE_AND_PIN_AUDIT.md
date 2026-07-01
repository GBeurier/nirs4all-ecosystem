# Wave 3G - WASM Surface And Pin Audit

Date: 2026-07-01T19:09:42+02:00

## Scope

Lane E/A/G follow-up after W3E/W3F:

- harden the published npm/WASM `nirs4all` surface with optional peer
  declarations and a consumer TypeScript typecheck gate;
- audit whether release-lock pins and `nirs4all-methods` strict-parity pins are
  remote-fetchable;
- audit the `nirs4all-io` sibling/worktree drift found during W3F.

No full parity run in this batch.

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Beauvoir | Read-only remote/pin audit | done | Found `nirs4all-methods` pin `00ca8467` is not fetchable from GitHub; release workflows will fail until a remote ref/tag exists or the pin is changed. |
| Hypatia | Read-only WASM type-surface audit | done | Recommended optional `peerDependencies`, top-level `types`, `typescript` typecheck script, and a consumer import smoke. |
| Russell | Read-only IO drift audit | done | Confirmed `nirs4all-io` sibling `e52eecd` is an ancestor of locked integration `eae8263`; do not repin IO to the sibling. |
| Herschel | W3G reviewer | done | Approved the WASM type-surface patch. Noted the consumer test is a type-surface smoke, not a runtime ABI proof. |

## Decisions

- Add real optional npm peer edges for the six WASM upstream packages while
  keeping lazy loading and no hard runtime dependency.
- Make `npm test --prefix bindings/wasm` include `tsc --project
  tsconfig.typecheck.json`, so existing CI/release callers pick up the new gate.
- Add a TypeScript consumer file importing from package name `nirs4all` to
  prove published type resolution.
- Keep the release-lock pin on `nirs4all-io@eae8263`; the raw sibling checkout
  remains a non-release lane state.
- Do not weaken release workflows to use remote default branches. The current
  pin reachability blocker requires publishing immutable refs/tags or an
  explicit release-root publication step.

## Files Changed

`nirs4all-lite`:

- `.github/workflows/release-npm.yml`
- `bindings/python/tests/test_release_topology.py`
- `bindings/wasm/package.json`
- `bindings/wasm/package-lock.json`
- `bindings/wasm/tsconfig.typecheck.json`
- `bindings/wasm/tests/types/consumer.ts`

`nirs4all-ecosystem`:

- `docs/agent_reports/WAVE_3G_WASM_SURFACE_AND_PIN_AUDIT.md`

## Gates

- `PYTHONPATH=bindings/python/src python3 -m unittest bindings/python/tests/test_release_topology.py -v` - 11 passed.
- `make test-python` - 37 tests passed, 1 skipped.
- `python3 -m json.tool bindings/wasm/package.json` - passed.
- `python3 -m json.tool bindings/wasm/package-lock.json` - passed.
- `python3 -m json.tool bindings/wasm/tsconfig.typecheck.json` - passed.
- `npm install --package-lock-only --ignore-scripts --dry-run --prefix bindings/wasm` - passed.
- `npm ci --dry-run --ignore-scripts --prefix bindings/wasm` - passed.
- `git diff --check` - passed.

## Risks

- `npm test` / `npm run typecheck` were not run locally because Linux `node` is
  absent and local `npm` resolves to Windows npm from WSL. CI `setup-node` is
  expected to run the real gate.
- The TypeScript consumer validates public type resolution and signatures, not
  the runtime ABI of `@nirs4all/methods-wasm`.
- Current release-lock member commits, including `nirs4all-methods@00ca8467`,
  are not remote-fetchable from GitHub in this workspace state. Release
  workflows that rely on GitHub checkout by pin need immutable published refs
  before they can pass.
