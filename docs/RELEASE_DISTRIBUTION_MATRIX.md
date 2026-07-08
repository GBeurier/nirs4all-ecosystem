# Release Distribution Matrix

The bounded, machine-readable public V1 surface matrix is the canonical tracked
distribution inventory for this refactoring wave:

`docs/contracts/release/public-v1-surface-matrix.n4a.json`

The aggregate release-member intent and exact selected lock are tracked in:

- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`

The latest head-selection and publication-state audit for this matrix and the
aggregation lock is:

`docs/agent_reports/WAVE_10O_RUNTIME_E2E_LOCK_AUDIT.md`

When live RC worktrees diverge from the selected release members, the
aggregation lock validated from an isolated `checkout-members` workspace is the
authority, not the live `_worktrees` checkout state.

Validate it with:

```bash
python3 scripts/n4a_release_surface_matrix.py validate
```

This pointer exists because some orchestration prompts and control boards refer
to `nirs4all-ecosystem/docs/RELEASE_DISTRIBUTION_MATRIX.md`. Do not point it at
workspace-local scratch files. Update the tracked public surface matrix and
release contracts first, then replace this pointer with a generated matrix when
the topology is finalized.
