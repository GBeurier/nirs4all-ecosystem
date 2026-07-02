# Wave 4I - Security and performance refresh

Date: 2026-07-02  
Coordinator: Codex

## Scope

Follow-up to the user-reported GitGuardian alert and the pending RC performance
evidence request. Full Python parity was not rerun in this wave.

## Security

`GBeurier/nirs4all-cluster` now exposes only:

- `main` -> `97b2b38`
- `rc/v1-full-refactor` -> `e843073`
- `n4a-v1-rc1-2026.07-refactor` -> tag `60c1b5a`, peeled commit `e843073`

The latest cleanup removes token-shaped CLI examples from help text and comments
after the earlier targeted history rewrite. Strict scan over the published refs
for concrete `N4CLUSTER_TOKEN=...`, `Authorization/Bearer ...`,
`--token VALUE`, and old `example-token` patterns returned no matches.

Cluster gates:

- `nirs4all-cluster` main: `uv run --extra dev pytest -q` ->
  `142 passed, 1 skipped, 1 deselected, 3 warnings`.
- `RC-v1-cluster`: `uv run --extra dev pytest -q` ->
  `145 passed, 1 skipped, 1 deselected, 3 warnings`.

## Performance

Command:

```bash
PYTHONPATH=src /home/delete/nirs4all/nirs4all-benchmarks/.venv/bin/n4a-benchmarks perf-compare \
  --repeats 3 \
  --warmups 0 \
  --assert-max-ratio python_run=1.0 \
  --assert-max-ratio studio_run=1.0 \
  --json-out /tmp/n4a_perf_compare_rc_gate_20260702.json \
  --markdown-out /tmp/n4a_perf_compare_rc_gate_20260702.md
```

Environment:

- child Python: `/home/delete/nirs4all/nirs4all-studio/.venv/bin/python`
- Python oracle/root: `/home/delete/nirs4all/_worktrees/RC-v1-nirs4all-python`
- thread env pinned to one thread for BLAS/OpenMP families.

Result:

| suite | legacy run median | dag-ml run median | dag-ml/legacy run ratio | dag-ml/legacy total ratio |
| --- | ---: | ---: | ---: | ---: |
| `nirs4all.run() direct` | `2.1533s` | `1.6411s` | `0.762x` | `0.806x` |
| `Studio training worker` | `1.4784s` | `1.0377s` | `0.702x` | `0.753x` |

Decision: this satisfies the requested local RC performance comparison for the
current selected heads. It is still a small deterministic benchmark, not a
substitute for broader dataset/model production profiling.
