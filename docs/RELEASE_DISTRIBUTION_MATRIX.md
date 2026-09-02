# Release Distribution Matrix

The bounded, machine-readable public V1 surface matrix is the canonical tracked
distribution inventory for this refactoring wave:

`docs/contracts/release/public-v1-surface-matrix.n4a.json`

The matrix is explicitly **not exhaustive**: it records the known surfaces
needed by the reviewed V1 train without turning omission into a capability
decision. `required_for_nirs4all_v1: true` means that a surface is inside the
V1 program and needs evidence before R4 promotion; it does not mean that its
gate passed, that it was published, or that it is an aggregation-lock member.
Studio, UI, Web, Tools, Providers, Cockpit and Org are therefore required V1
scope even though they remain outside the current seven-member aggregate lock.
Studio is still explicitly held until its product gates close.

The execution inventory that binds all 66 reviewed Phase-0/R1/R2/R3/R4 lots,
plus separately justified implementation slices, is:

`docs/contracts/release/migration-work-ledger.yaml`

Roadmap coverage is only an inventory assertion. Missing lots added to the
ledger remain `pending`; coverage never means completion or release readiness.

The aggregate release-member intent and exact selected lock are tracked in:

- `docs/contracts/release/aggregation-manifest.n4a.json`
- `docs/contracts/release/aggregation-lock.n4a.lock.json`

The latest head-selection and publication-state audit for this matrix and the
aggregation lock is:

`docs/agent_reports/WAVE_10O_RUNTIME_E2E_LOCK_AUDIT.md`

The latest operational follow-up for Studio RC packaging, cockpit manual
blocker ordering, and the cluster GitGuardian audit is:

`docs/agent_reports/WAVE_10P_STUDIO_RC_COCKPIT_CLUSTER_AUDIT.md`

When live RC worktrees diverge from the selected release members, the
aggregation lock validated from an isolated `checkout-members` workspace is the
authority, not the live `_worktrees` checkout state.

Validate it with:

```bash
python3 scripts/n4a_release_surface_matrix.py validate
python3 scripts/n4a_migration_work_ledger.py validate
```

This pointer exists because some orchestration prompts and control boards refer
to `nirs4all-ecosystem/docs/RELEASE_DISTRIBUTION_MATRIX.md`. Do not point it at
workspace-local scratch files. Update the tracked public surface matrix and
release contracts first, then replace this pointer with a generated matrix when
the topology is finalized.
