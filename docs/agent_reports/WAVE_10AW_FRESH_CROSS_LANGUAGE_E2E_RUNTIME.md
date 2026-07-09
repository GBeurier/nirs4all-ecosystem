# Wave 10AW - Fresh cross-language E2E runtime evidence

Date: 2026-07-09

## Scope

Refresh the runtime evidence for the V1 cross-language E2E suite after the
post-batch Python parity gate. This run targets the user-requested complex
cross-language scenarios rather than only manifest/static validation.

## Commands

```bash
cd /home/delete/nirs4all/nirs4all-ecosystem
python3 scripts/n4a_e2e_scenarios.py run-ready --execute
python3 scripts/n4a_e2e_scenarios.py evidence --ready-only --max-age-seconds 14400 --json
python3 scripts/n4a_e2e_scenarios.py evidence-ledger --check --out docs/contracts/e2e/latest-runtime-evidence-ledger.n4a.json
```

## Result

- Ready scenarios executed: 11/11
- Verified fresh artifacts: 70/70
- Evidence failures: 0
- Freshness policy checked: every expected artifact is younger than 14400 seconds
- Ledger check: 11/11 scenarios verified, 70 artifacts, 0 failures

## Scenario coverage refreshed

- `e2e-r-dataset-io-pipeline-save`
- `e2e-python-reopen-paper-repository-refit`
- `e2e-wasm-open-repo-pipeline-alt-dataset`
- `e2e-multimodal-python-r-wasm-roundtrip`
- `e2e-multisource-branching-stacking-replay`
- `e2e-converter-legacy-save-predictions-web`
- `e2e-dataset-provider-repository-roundtrip`
- `e2e-pipeline-generation-performance-compare`
- `e2e-cluster-dag-rights-client-core`
- `e2e-formats-io-datasets-methods-language-bindings`
- `e2e-core-ui-custom-app-host`

## Notable runtime checks observed

- R package install/parity ran through the conda R toolchain and native `n4m`
  binding.
- Web/WASM repository import and prediction smokes passed with no JS console
  errors.
- Legacy save conversion lowered predictions and rendered them in Web.
- Performance comparison reported Python legacy/dag-ml parity with a faster
  dag-ml path and Web WASM prediction evidence.
- Custom app host passed against the published packages:
  `nirs4all@0.3.7` and `nirs4all-ui@0.1.9`.

## Files modified

- `nirs4all-ecosystem/docs/agent_reports/WAVE_10AW_FRESH_CROSS_LANGUAGE_E2E_RUNTIME.md`

## Notes

`.n4a-e2e-artifacts/` remains intentionally untracked; this report records the
fresh runtime execution while `latest-runtime-evidence-ledger.n4a.json` keeps the
portable normalized ledger.

