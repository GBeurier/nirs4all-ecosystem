# Wave 3S - Methods Binding Parity Audit

Date: 2026-07-01

## Scope

Lane F read-only audit of `nirs4all-methods` after the W3N JS/WASM smoke wiring. No files were changed and no full registry parity sweep was run.

## Repository State

- `nirs4all-methods` clean.
- Local `main` is ahead 4 and behind `origin/main` by one docs/metadata commit: `90fe5517 fix(docs): add canonical SEO metadata`.
- No remote merge, fetch, push, or release-lock update was performed.

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Peirce the 2nd | Lane F read-only audit | done | Confirmed ABI/catalog checks are not the current blocker and identified the remaining cross-binding parity documentation gap. |

## Findings

- ABI/catalog checks are coherent: Linux/macOS/Windows snapshots are covered by CI, and catalog validation reports 209 methods with expected ABI references.
- Python, R, JS/WASM, MATLAB/Octave surfaces are active. Rust is archived only, not an active binding.
- The current cross-binding parity gate covers Python/R/Octave for `pls`/`pcr`; JS/WASM is covered separately by `bindings/js` npm tests, not by the cross-binding orchestrator.
- Full binding parity remains open by design; W3S did not run the full registry sweep.

## Read-Only Checks Run

`nirs4all-methods`:

- `scripts/bump_version.sh --check` -> passed.
- `python3 catalog/scripts/validate.py --strict-abi --check-references` -> passed.
- `python3 catalog/scripts/split_legacy_methods.py --check` -> passed.
- `python3 catalog/scripts/selftest.py` -> passed.

## Recommended Next Tranche

Contract hygiene only, after deciding whether to patch despite the behind-origin docs delta:

- Clarify in `benchmarks/cross_binding/ci_parity_gate.py` that JS/WASM is not wired into that harness and is instead covered by the `js-wasm` job.
- Clean remaining stale `p4a.{js,wasm}` comments/examples.
- Add a static test to keep this contract explicit.

## Risks / Follow-Ups

- Full methods binding parity, ABI release gates on built libraries, and cross-binding registry sweeps remain deferred to a larger batch.
- Do not present W3N/W3S smoke coverage as full numerical parity.
