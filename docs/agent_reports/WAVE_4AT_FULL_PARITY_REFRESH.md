# Wave 4AT Full Parity Refresh

Date: 2026-07-03

## Scope

Refresh the full Python-reference parity proof after the Wave 4AR batch moved the
selected Python RC head to `bf242e48`, `dag-ml-data` to `616f3e5`, and Studio
runtime pins to those immutable heads.

## Environment

- Worktree: `/home/delete/nirs4all/_worktrees/RC-v1-nirs4all-python`
- Python head: `bf242e4854693ccb048b7f0ffc5f3fdd2380315a`
- `dag-ml` Python path: `/home/delete/nirs4all/_worktrees/RC-v1-dagml/crates/dag-ml-py/python`
- `dag-ml-data` Python path: `/home/delete/nirs4all/_worktrees/RC-v1-dmd/crates/dag-ml-data-py/python`
- `dag-ml-cli`: `/home/delete/nirs4all/_worktrees/RC-v1-dagml/target/debug/dag-ml-cli`
- Python executable: `/home/delete/nirs4all/nirs4all/.venv/bin/python`
- `NIRS4ALL_REQUIRE_N4M=1`
- `PYTHONDONTWRITEBYTECODE=1`

Import preflight confirmed `nirs4all` loaded from the Python RC worktree,
`dag_ml` from `RC-v1-dagml`, `dag_ml_data` from `RC-v1-dmd`, and `shap` was
installed in the oracle venv.

## Commands

Non-slow split:

```bash
env "PYTHONDONTWRITEBYTECODE=1" "NIRS4ALL_REQUIRE_N4M=1" "PYTHONPATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/RC-v1-dmd/crates/dag-ml-data-py/python:." "PATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/target/debug:$PATH" /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity -m "not slow" -q --tb=short -p no:cacheprovider
```

Slow split:

```bash
env "PYTHONDONTWRITEBYTECODE=1" "NIRS4ALL_REQUIRE_N4M=1" "PYTHONPATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/crates/dag-ml-py/python:/home/delete/nirs4all/_worktrees/RC-v1-dmd/crates/dag-ml-data-py/python:." "PATH=/home/delete/nirs4all/_worktrees/RC-v1-dagml/target/debug:$PATH" /home/delete/nirs4all/nirs4all/.venv/bin/python -m pytest tests/integration/parity -m "slow" -q --tb=short -p no:cacheprovider
```

Logs:

- `/tmp/n4a_full_parity_bf242e48_non_slow_20260703.log`
- `/tmp/n4a_full_parity_bf242e48_slow_20260703.log`

## Results

- Non-slow split: `444 passed`, `443 deselected`, `507 warnings` in `538.77s`.
- Slow split: `443 passed`, `444 deselected`, `1292 warnings` in `1876.58s`.
- Combined interpretation: `887 passed`, `0 skipped`, `0 xfailed`, `0 failed`.

`deselected` is the opposite marker split, not skipped test debt.

## Decisions

- The Python-reference parity proof is current for selected Python head
  `bf242e48`.
- New parity skips, xfails, or native/data runtime movement remain release
  blockers until this gate is rerun.

## Risks

- This proof covers the Python oracle parity suite. It does not replace the
  remaining non-Python release-environment proofs for R, MATLAB/Octave, Studio
  all-in-one/Docker release jobs, or final dataset hosting routes.
