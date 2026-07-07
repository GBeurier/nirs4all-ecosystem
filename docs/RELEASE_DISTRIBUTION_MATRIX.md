# Release Distribution Matrix

The canonical distribution inventory for the current refactoring wave is:

`/home/delete/nirs4all/RELEASE_DISTRIBUTION_INVENTORY.md`

The bounded, machine-readable W2P public V1 surface matrix is:

`docs/contracts/release/public-v1-surface-matrix.n4a.json`

The latest head-selection and publication-state audit for this matrix and the
aggregation lock is:

`docs/agent_reports/WAVE_8Q_CORE_PROVIDERS_FALLBACK_ASSETS.md`

When live RC worktrees diverge from the selected release members, the
aggregation lock validated from an isolated `checkout-members` workspace is the
authority, not the live `_worktrees` checkout state.

Validate it with:

```bash
python3 scripts/n4a_release_surface_matrix.py validate
```

This pointer exists because some orchestration prompts and control boards refer
to `nirs4all-ecosystem/docs/RELEASE_DISTRIBUTION_MATRIX.md`. Do not duplicate the
full inventory here until the release topology is finalized; update the
inventory first, keep the public surface matrix in sync, then regenerate or
replace this pointer with a generated matrix.
