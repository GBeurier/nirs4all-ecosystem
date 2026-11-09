# Ecosystem repository instructions

- This public repository coordinates independent projects through submodules and cross-repository contracts; it is not a monorepo or the implementation owner of its members.
- Use the tracked [README](README.md) and [contracts](docs/contracts/) as entrypoints. The [developer guide](DEVELOPER_GUIDE.md) is optional navigation context; no operative rule below depends on it.
- Working sibling checkouts and submodule copies can differ. Read the target checkout's local AGENTS.md/CLAUDE.md; local instructions govern local conventions under current user scope and safety limits.

## Hierarchy and boundaries

- Data flows from Formats decoding through IO materialization and DMD identity/data contracts, then DAG execution with Methods, into Core and language/product hosts; this states ownership, not complete implemented support.
- Core aggregates Methods, DAG-ML, DMD, Formats, IO and Datasets. Python adds controllers/extras to that skeleton; R supplies a host API/controllers over these owners.
- Formats owns vendor decoding; IO owns roles, axes, masks, identities, targets, declared partitions and task inference; DMD owns generic data/identity contracts, not ML phases.
- Methods owns numerics, preprocessing, filters, augmentation, splitters and fitted state; DAG owns execution, variant generation, folds, OOF/leakage, search/selection, metric definitions and scoring context.
- Keep the specifically accepted generic identity-aligned conformal exception in DAG. Methods remains the default numerical owner; shared metric fixtures qualify named profiles, not universal metric equivalence.
- `.n4a` is directed cross-platform/language exchange for recipes, data, results, scores and fitted state. Core owns its byte container/inventory; payload owners keep semantics and serializers.
- Container, owner-schema, ABI/wire, recipe-language and package-release versions are independent. Route by declared schema/owner, never suffix; SDK Python-host bundles use Core V1 containers through `BundleLoader`; active V2/V3 execution profiles remain separate, and readability does not imply portability.
- UI owns reusable presentation/interactions; hosts own routing, persistence and execution. Repository owns presets/requirements; adapters retain complete recipes or explicitly refuse.
- Cluster's `packages/nirs4all-access/` is the nested stdlib-only Access leaf, independent of Cluster; Cluster requires it. Datasets/Repository service extras are optional; Arena authentication remains future work and needs no upload.
- Preserve declared identity, masks, axes, training-only fit and forward contracts. Remove obsolete alternatives only after callers migrate and parity is established; preserve identified scientific/frozen references.
- The maintainer authorizes shared-UI adoption across existing WASM demonstrators and web apps; hosts retain loading, storage and execution. Frontend pins/generated assets needed by those coherent batches are included; no hosting, publication or upload is authorized. Studio backend/owner integration, including necessary non-visual transport/contract types, may be updated autonomously; Studio GUI migration/refactoring remains last and joint with the maintainer. Preflight takeover covers its existing engine/backend, UI and instruction work; preserve all prior/concurrent work; no release, deployment or upload is authorized.

## Navigation and delivery

- Use CodeGraph FIRST only with the target checkout's own `.codegraph/`; never auto-index or silently use another index. Direct source and checks are final authority; unindexed code uses ordinary navigation.
- Preserve dirty work. Use declared owner contracts and consult affected owners for handoffs within the authorized batch; report executed checks, skips, refusals and limits separately. Do not delegate policy to an untracked guide.
- Do not change gitlinks, locks, tags or publication state as a documentation side effect. Integration/publication requires maintainer authorization; a parent pin does not merge child changes.
- Project content is English; preserve identifiers/provenance and owner licensing/data restrictions. Never commit credentials, private data, generated workspaces or build outputs.
