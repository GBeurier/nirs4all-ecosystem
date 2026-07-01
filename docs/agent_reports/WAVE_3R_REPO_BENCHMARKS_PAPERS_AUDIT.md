# Wave 3R - Repository, Benchmarks, Papers Audit

Date: 2026-07-01

## Scope

Lane J read-only audit of provider/plugin/export boundaries for `nirs4all-repository`, `nirs4all-benchmarks`, and `nirs4all-papers`. No code was changed and no remote branch was merged.

## Commits

- No commits in this wave.

## Repositories Audited

| Repo | Local State | Remote Delta |
| --- | --- | --- |
| `nirs4all-repository` | clean `main` | behind `origin/main` by `b6ddaff fix(site): add canonical SEO metadata` |
| `nirs4all-benchmarks` | clean `main` | behind `origin/main` by `3607862 fix(site): add crawl discovery metadata` |
| `nirs4all-papers` | clean `main` | behind `origin/main` by `d780535 fix(site): advertise sitemap metadata` |

Ignored local outputs observed: `nirs4all-benchmarks/arena-store`, `nirs4all-papers/site`, and `nirs4all-repository/docs/_build`.

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Dirac the 2nd | Lane J read-only audit | done | Recommended no patch before refreshing/auditing the one-commit remote deltas. Identified a safe future `nirs4all-benchmarks` recipe consumer from `nirs4all-repository`. |

## Findings

- `nirs4all-repository` is the correct owner for presets/pipelines via `pipelines/<id>`, `descriptor.yaml`, `manifest.json`, `ro-crate-metadata.json`, and `catalog/index.json`.
- Current repository pipelines are still draft/unvalidated, so they are presets, not official benchmark/release evidence.
- `nirs4all-benchmarks` consumes `.n4a`, workspace, dag-ml bundle, and manifest exports, but does not yet resolve a pipeline recipe directly from `nirs4all-repository` by name.
- `nirs4all-papers` remains a public archive/export surface. Its publisher path is coherent, but libn4m WASM replay and richer dag-ml provenance fusion are future work.

## Recommended Next Tranche

After separately reviewing/rebasing the one-commit remote deltas, add an optional `nirs4all-benchmarks` consumer that resolves a pipeline recipe from `nirs4all-repository` and feeds `register_pipeline` / `planned_runs` without executing anything and without writing into the repository.

## Tests Run

None. This was a read-only audit.

## Risks / Follow-Ups

- Do not patch the three audited repos until the remote metadata deltas are reviewed.
- Benchmarks must remain a consumer/tester and must not write into the ecosystem.
- Papers must remain public/reproducible material only; no private drafts or lab artifacts.
