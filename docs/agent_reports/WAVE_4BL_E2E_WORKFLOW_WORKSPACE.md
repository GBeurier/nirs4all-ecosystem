# Wave 4BL - Cross-Repo E2E Workflow Workspace

## Scope

- Hardened the `nirs4all-ecosystem` cross-language E2E workflow so GitHub Actions checks out the sibling repositories declared by the scenario manifest.
- Kept `nirs4all-drafts` and `nirs4all-lab` out of scope.
- Preserved the default lightweight behavior: validate and plan all scenarios; execute only a selected scenario through `workflow_dispatch`.

## Files changed

- `.github/workflows/cross-language-e2e.yml`
- `tests/test_e2e_scenarios.py`

## Decisions

- `N4A_WORKSPACE_ROOT` is set to `${{ github.workspace }}` so scenario commands resolve sibling repositories consistently in CI.
- The workflow installs the tool shims used by the planner (`python3`, Node/npm, Rscript, Rust cargo, CMake, Ninja) before planning.
- The workflow checks out production-sensitive repositories (`nirs4all`, `nirs4all-studio`) for read/plan coverage only; this does not publish or release them.

## Tests

- `python3.11 scripts/n4a_e2e_scenarios.py validate`
- `PYTHONDONTWRITEBYTECODE=1 python3.11 -m pytest -q -p no:cacheprovider tests/test_e2e_scenarios.py`
- YAML parse check for `.github/workflows/cross-language-e2e.yml`
- `python3.11 scripts/n4a_e2e_scenarios.py plan --json` summary: 5 ready, 5 blocked.

## Risks

- GitHub checkout access must be valid for every declared repository. If a repository is private or renamed, the workflow will fail early instead of producing a misleading plan.
- Execute mode still depends on the selected scenario's repo-specific dependencies; this change only guarantees the workspace topology and planning prerequisites.
