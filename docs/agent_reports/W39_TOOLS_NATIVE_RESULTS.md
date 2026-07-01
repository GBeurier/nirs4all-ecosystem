# W39 report - tools native results preservation

Summary:
W39 extended `nirs4all-tools` migration to preserve native result artifacts without adding legacy readers to the V1 runtime. `.n4a`, `.n4a.py`, and native-results-v1 inputs are copied into a checksummed `preserved/` area with a workspace-v2 `store.sqlite` shell and strict-mode refusal before output creation when opaque preservation would be required.

Code changed:
- Added detection and preservation path for native result artifacts.
- Added checksummed preserved artifact records and verification behavior.
- Added tests and CLI smokes for best-effort and strict migration modes.

Files touched:
- `src/nirs4all_tools/commands.py`
- `src/nirs4all_tools/workspace_v2.py`
- `tests/test_cli.py`
- `tests/test_commands.py`
- related fixtures/contracts in `nirs4all-tools`

Commits:
- `nirs4all-tools/refactor/W39-native-results` `ce8ed47`
- Integrated into `nirs4all-tools/main` as merge `b76458d`

Tests run:
- `PYTHONPATH=src /home/delete/.local/bin/pytest tests -q` -> `69 passed`.
- `python3 -m compileall -q src tests` -> passed.
- Ruff -> passed.
- CLI smoke: native-results migrate exit `10`, verify exit `0`.

Tests not run and why:
- `mypy` was not run because no `mypy` binary was available in the shell used for this repo.

Impact:
Advances `LOCK-MIG`: old native artifacts are not lost, but runtime V1 remains free of legacy reader code.

Next action:
Implement full runtime-readable native results conversion once the final native result schema is frozen.

Sync doc updated: yes
