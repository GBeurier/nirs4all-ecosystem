# Wave 10B — Formats/IO/Methods WASM strict parity

Date: 2026-07-08

## Scope

- Lane G/F overlap: `nirs4all-io` reference dataset assembly plus `nirs4all-methods` Python/R/native/WASM binding parity.
- No runtime repositories were edited.

## Files Modified

- `docs/contracts/e2e/cross-language-scenarios.n4a.json`
- `docs/CROSS_LANGUAGE_E2E.md`
- `tests/test_e2e_scenarios.py`

## Evidence Run

```bash
rm -rf /tmp/n4a-e2e-formats-io-methods
python3.11 scripts/n4a_e2e_scenarios.py \
  --artifacts-dir /tmp/n4a-e2e-formats-io-methods \
  run --execute e2e-formats-io-datasets-methods-language-bindings
python3.11 scripts/n4a_e2e_scenarios.py \
  --artifacts-dir /tmp/n4a-e2e-formats-io-methods \
  evidence --scenario e2e-formats-io-datasets-methods-language-bindings
```

Result: scenario passed and evidence verified with 3 artifacts:

- `formats-io-methods/assembled-datasets.json`
- `formats-io-methods/binding-parity.json`
- `formats-io-methods/predictions-by-language.json`

WASM strict evidence from `binding-parity.json`:

- `wasm.ok=true`
- `metrics_max_rmse_rel=2.837e-16`
- tolerance `1e-12`

## Decision

The scenario remains `hybrid` because WASM is still fixture-scoped and Rust is intentionally archived as non-release-target evidence. The WASM parity check itself is now strict because the produced JSON artifacts contain finite numeric deltas under tolerance.

## Tests

```bash
python3.11 scripts/n4a_e2e_scenarios.py validate
python3.11 scripts/n4a_e2e_scenarios.py coverage --json
python3.11 -m pytest tests/test_e2e_scenarios.py -q
```

## Risks / Remaining Gaps

- No broad full-parity sweep was run in this batch.
- The remaining formats lane gap is real: WASM proof is deterministic-fixture parity, not external/catalog runtime coverage; Rust remains archived and is not a V1 release target here.
