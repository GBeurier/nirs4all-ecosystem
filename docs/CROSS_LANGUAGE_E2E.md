# Cross-language V1 E2E scenarios

The canonical scenario contract lives at
`docs/contracts/e2e/cross-language-scenarios.n4a.json`.

The suite deliberately separates planning from execution:

- `python3 scripts/n4a_e2e_scenarios.py validate` validates the manifest.
- `python3 scripts/n4a_e2e_scenarios.py list` lists the ten scenarios.
- `python3 scripts/n4a_e2e_scenarios.py plan --json` renders tool/env blockers
  without running long tests.
- `python3 scripts/n4a_e2e_scenarios.py run <scenario-id>` is a dry run.
- `python3 scripts/n4a_e2e_scenarios.py run <scenario-id> --execute` runs the
  commands and fails with exit code 2 if required tools or env vars are missing.

The runner reports missing toolchains as `blocked`; it does not xfail or silently
skip. Full parity scenarios are meant to run after large integration batches or
on selected release heads, not on every small commit.
