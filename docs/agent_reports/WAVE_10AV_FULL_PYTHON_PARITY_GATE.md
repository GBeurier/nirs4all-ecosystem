# Wave 10AV - Full Python parity gate

Date: 2026-07-09

## Scope

Final post-batch verification of the Python reference parity gate after the V1
refactoring/release batch.

## Inputs

- Reference/oracle repo: `nirs4all`
- Commit tested: `d3863ee2 test(parity): harden prediction and parquet skip guards`
- Cockpit snapshot head checked: `0d8788e chore(collect): refresh data/current.json`
- Ecosystem head before this report: `a187c1a docs(agent): record cockpit provenance e2e audit`
- GitHub CLI check: local `gh` is `2.96.0`, matching latest `cli/cli` release `v2.96.0`

## Commands

```bash
cd /home/delete/nirs4all/nirs4all
.venv/bin/python -m pytest -q tests/integration/parity
```

## Result

```text
799 passed, 1857 warnings in 2134.73s (0:35:34)
```

There were no skipped tests, no xfailed tests, and no failures in this full
parity run. This replaces the older ambiguous `810 passed / 30 skipped / 11
xfailed` snapshot for the current parity gate.

## Review notes

- The run covers the Python reference parity suite only: compatibility ledger,
  dual engine conformance, DAG-ML bridge/CLI/dataplane/native result paths,
  generator conformance, baseline parity, compile parity, and parity smoke.
- Warnings are dominated by existing dependency/runtime warnings:
  Polars string-cache deprecation, Pandas 4 dtype warning, sklearn split/linear
  algebra warnings, expected branch fallback warning, and visualization warnings.
- No test was relaxed, xfailed, or skipped to obtain the green result.

## Remaining external/manual gates

- `nirs4all-core` CRAN aggregate publication remains a manual CRAN web
  submission. Local WSL does not have `R`, so `R CMD check` cannot be rerun in
  this environment.
- `n4m`, `pls4all`, `nirs4allio`, and `nirs4alldatasets` CRAN submissions remain
  manual CRAN web actions in cockpit.
- `nirs4all-studio` Windows RC installer smoke-test remains manual on Windows.
- Python `nirs4all` production and Studio production remain intentionally held.

## Files modified

- `nirs4all-ecosystem/docs/agent_reports/WAVE_10AV_FULL_PYTHON_PARITY_GATE.md`

