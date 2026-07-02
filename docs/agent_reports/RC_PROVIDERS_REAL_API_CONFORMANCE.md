# RC Providers Real-API Conformance

Date: 2026-07-02

Coordinator follow-up after RC-M provider/plugin lane.

## Change

`nirs4all-providers` now prefers the first-party
`nirs4all_papers.provider` facade for `citation()` and `bibtex()` when the
facade exists, matching the already-facade-first behavior for list/load/inspect
and local export helpers.

Commit:

- `nirs4all-providers`: `3de0042 fix(papers): prefer first-party facade helpers`

## Validation

With RC worktrees visible:

```bash
PYTHONPATH=/tmp/rc_v1_bench_jsonschema:/home/delete/nirs4all/_worktrees/RC-v1-providers/src:/home/delete/nirs4all/_worktrees/RC-v1-datasets/src:/home/delete/nirs4all/_worktrees/RC-v1-repository/src:/home/delete/nirs4all/_worktrees/RC-v1-benchmarks/src:/home/delete/nirs4all/_worktrees/RC-v1-papers/src:/home/delete/nirs4all/_worktrees/RC-v1-io/src python3.11 -m pytest -q -ra
```

Result: all providers tests passed (`94 passed`), with one dependency warning
from `pytz`.

Supporting focused checks:

- `tests/test_papers_provider.py tests/test_conformance.py`: `20 passed`.
- `ruff check src/nirs4all_providers/papers.py tests/test_papers_provider.py tests/test_conformance.py`: passed.
- `mypy src/nirs4all_providers/papers.py`: passed.

The only special environment piece is `/tmp/rc_v1_bench_jsonschema`, used to
provide `jsonschema>=4` because the base shell has `jsonschema 3.2.0` and
`nirs4all-benchmarks` requires `Draft202012Validator`.
