# nirs4all developer quick guide (nirs4all-ecosystem repository)

For developers and coding agents. Read once, then load only the instructions,
contracts and tests for the repositories your task touches. This guide is optional
navigation, not operative policy or a runtime support certificate. Current owner
contracts and executed checks determine support for each profile and operation.

## Start here

- **Independent repositories, coordinated ecosystem.** This parent pins Git
  submodules; each project owns its code, issues, CI and releases. Sibling and
  submodule checkouts can differ: verify repository root, branch, commit and
  working-tree changes before editing. Preserve concurrent work.
- Read applicable workspace/repository `AGENTS.md`, `CLAUDE.md` and
  `CONTRIBUTING.md`. Current maintainer instructions supersede older plans.
  Normative contracts and executable tests establish behavior; README versions
  and review receipts may describe historical states.
- The coordination workspace's `_backlogs/BACKLOG_CONSOLIDE.md` is the open-work
  entry point (not shipped in this parent). Archived plans are provenance;
  do not revive them as work queues or create a competing backlog.
- Use CodeGraph first when the target checkout has `.codegraph/`. Inspect the
  owner implementation and callers before adding any helper or dependency.

## Responsibility map

Names are repositories except the nested Access package; `.gitmodules` defines
this parent's submodules. Additional projects may live in sibling checkouts.
Ownership below does not establish implementation, publication or portability:
some callers await migration.

| Repository | Owns / where work belongs |
| --- | --- |
| `nirs4all-methods` (`n4m`) | C++17 numerical kernels, preprocessing, filters, augmentation, splitters, models, metrics/statistical primitives; `n4m_*` C ABI, method catalog and native model serialization. Bindings translate objects and call the ABI. |
| `nirs4all-formats` | Rust file sniffing, reader registry, vendor decoding and spectral records. Add readers here; bindings never reparse bytes. |
| `nirs4all-io` | Resolve → infer → configure → materialize datasets: X/Y/metadata roles, declared partitions, joins, multisource and task/signal inference. Uses Formats; emits data-provider contracts. Rust is production; retain Python's parity oracle and align load-bearing changes. |
| `dag-ml-data` | Generic sources, axes, representations, views, sample relations, alignment/collation, provider interfaces and fingerprints. Declares fit scope; no ML scheduling or leakage enforcement. |
| `dag-ml` | Generic graphs, phases, variant generation, folds, OOF/leakage safety, selection/HPO coordination, aggregation, metric definitions/scoring, prediction/score persistence, lineage and replay. Retains the accepted generic identity-aligned conformal score/quantile/application exception (ADR-20); Methods remains the default numerical owner. Control-plane features/host objects are opaque handles; feature-gated Methods execution controllers may own buffers. |
| `nirs4all-core` | Portable aggregate/facades over the upstream owners and Datasets; shared `.n4a` container storage/inventory. No second parser, loader, numerical engine or coordinator. |
| `nirs4all` | Python product API, Python controllers/operators/integrations, analysis/explanation and workspace workflows. Existing reference paths are scientific oracles, not templates for duplicate runtime logic. |
| `nirs4all-r` | R product package `nirs4all`, controllers and integrations. Composes upstream APIs; local fit/predict alone does not establish DAG parity. |
| `nirs4all-ui` | Shared React components/capsules, display contracts, pure TypeScript view-models, visualizations, styles and brand assets. Hosts supply results and execution callbacks. |
| `nirs4all-studio` | Desktop/web product and Electron shell. Rust sidecar owns routes, jobs, WebSockets, product state/adapters; CPython is a bounded library/plugin host. FastAPI is explicit development/diagnostics, not product fallback. |
| `nirs4all-web` | Client-side browser/WASM app: state, routing, local storage and adapters consuming Core/UI. |
| `nirs4all-quality`, `nirs4all-device` | Lab-quality workflow app; phone/tablet acquisition and spectrometer adapters, respectively. Reuse scientific owners/UI. |
| `nirs4all-preflight` | Dataset qualification protocols and input/report contracts; reuses Methods kernels, DAG nested validation, IO/Formats/UI. |
| `nirs4all-domains` | Dataset structure, population support and evaluation-limit protocols; reuses Methods/Preflight. Python is transport/batch glue. |
| `nirs4all-datasets` | Curated catalog, dataset identity/metadata, acquisition, checksums and cache; delegates reading/assembly. |
| `nirs4all-repository` | Versioned pipeline recipes/bundles, provenance, verification and publication/catalog contracts. |
| `nirs4all-providers` | Optional Python Datasets/Repository clients; mirrors neutral provider contracts. Never a dependency of Core/IO/DAG runtimes. |
| `nirs4all-cluster` | Distributed campaigns, submission, scheduling, workers, transport and operational persistence; delegates scientific execution. |
| `nirs4all-access` (nested at `nirs4all-cluster/packages/nirs4all-access/`) | Independent stdlib-only project-token verification leaf; no Cluster dependency. Cluster requires Access; Datasets/Repository service extras are optional and need no Cluster. |
| `nirs4all-tools` | Explicit migration/conversion utilities, outside production runtime paths. |
| `nirs4all-benchmarks` | Benchmark ingestion, score ledgers, comparisons and residuals; no fitted-model store or replacement scientific engine. |
| `nirs4all-aom`, `nirs4all-papers` | Paper companion/reference implementations; public manuscripts and reproducibility kits, respectively. |
| `nirs4all-org`, `nirs4all-cockpit` | Public website; release/health reporting, respectively. Neither defines runtime capability. |
| `nirs4all-ecosystem` | Cross-repository contracts, ownership, integration/release qualification, aggregate locks and submodule references. |

Package names: Python `nirs4all` is the full SDK; Python `nirs4all-core` imports
as `nirs4all_core` (also `n4a`); Core's npm package and Rust crate are `nirs4all`;
the R product lives in `nirs4all-r`. `nirs4all-lite` is retired/audit-only, never
a dependency or alias. Private `nirs4all-lab` and `nirs4all-drafts` are out of scope.

## Rules that prevent duplication and contract drift

1. **Fix the owner, propagate to consumers.** Trace implementation → ABI/schema
   → binding → aggregate/controller → application. Extend owner APIs instead
   of copying kernels, parsers, CV/scoring orchestration or joins into consumers.
   Methods supplies kernels; DAG owns metric meaning, context, joins, reductions
   and selection; UI presents results.
   Derive method/capability menus from owner registries, not per-binding lists.
2. **Keep boundaries.** DAG/Data stay NIRS-agnostic. UI owns presentation and
   interaction; hosts own routing, persistence, fetching and scientific execution.
   Studio orchestrates owner APIs. Missing functionality belongs upstream,
   not in a fallback engine. Preserve optional dependencies/standalone builds.
3. **Preserve identity and fit scope.** Join/split by declared sample, target,
   group, repetition and origin identities, not accidental row order. Preserve
   axes, units, precision and missingness. Fit only within the declared training
   scope; selection uses designated validation/OOF, never the retained test set.
4. **Change contracts coherently.** Update owner types, schemas, C headers/ABI
   metadata, serializers, registries and affected bindings together. Regenerate
   mirrors/fixtures from their source; run drift validators. Byte-identical
   mirrors stay byte-identical. Document/test deliberate route differences;
   never silently coerce invalid inputs.
5. **Separate storage, semantics and execution.** Core validates storage/inventory
   for the `.n4a` containers it reads; payload owners validate contents and admit
   operations. Route by declared schema/owner/profile/operation, never suffix.
   Current SDK Python-host source uses Core V1 storage through `BundleLoader`;
   trusted joblib payloads remain nonportable. Native Package V2/V3 profiles also
   use Core V1 storage but keep separate execution contracts. Container,
   owner-schema, ABI/wire, recipe-language and package-release versions are
   independent.
   These source contracts do not establish publication or universal portability.
   Readable archives, recipes, schemas or capability metadata alone grant no
   execution permission. Report unsupported/unavailable paths. Recipe portability,
   trained-state interchange and numerical parity each need actual-path evidence.
6. **Keep the V1 path clean.** Migrate active callers before removing old
   implementations in the same authorized batch. No new compatibility aliases
   or silent fallback runtimes; remove pre-V1 readers with their caller migrations.
   Keep independent scientific oracles/frozen references as provenance outside
   live execution. Version numbers alone do not make current writer output obsolete.

## Work and PR workflow

1. **Scope and branch.** Reproduce the defect or state expected behavior; identify
   owners, boundaries and callers. Preserve dirty work. Create a branch/worktree
   from the agreed base in each affected repo; submodules may have detached HEAD.
2. **Plan interfaces.** Write a short contract delta and consumer/check plan.
   Follow [ownership/arbitration](docs/contracts/governance/ownership-ledger.v1.json)
   and `CODEOWNERS`; use the [handoff template](.github/PULL_REQUEST_TEMPLATE/ownership-handoff.md)
   for lane changes, consulted-lane paths or contracts/schemas/goldens: source/target
   SHAs, tests and rollback. For repos absent from the ledger, state owner/handoff in
   the PR; its validator accepts only declared repository keys.
3. **Implement and verify.** Change the owner, then authorized consumers. Add a
   regression and failure cases. Run each touched repo's documented gate plus
   actual binding/consumer integration; workspace tests may exclude bindings.
   Rebuild native/WASM artifacts used by probes and identify their source.
   Compare independent references with declared tolerances. Report skips,
   unavailable runtimes and untested paths; never bless goldens merely to pass.
4. **Prepare PRs.** Commit inside each changed repo with scoped imperative
   subjects (`fix(io): ...`). Prepare one focused PR per affected repository for
   the coherent batch; cross-link them and state integration order. Use local
   templates: behavior/root cause, issue, contract/ABI impact, exact checks,
   limits and fixture/license provenance. Critical reviews seek counterexamples
   and execute targeted production-path probes.
5. **Review and integrate.** Obtain declared-owner review and maintainer
   authorization for remote publication/merge. Verify GitHub identity `GBeurier`
   before writes; use the workspace credential without exposing it. Workspace
   commits use `GBeurier <95907737+GBeurier@users.noreply.github.com>`.
   Coordinate owner/consumer merges as a batch; no PR chains.
6. **Pin/release last.** Update only intended parent gitlinks and applicable
   release contracts after integration. A parent PR pins commits; it does not
   merge child changes. Aggregate selection uses the
   [reviewed manifest and batch lock](docs/RELEASE_DISTRIBUTION_MATRIX.md),
   validated from an isolated `checkout-members` workspace, not live sibling
   heads/gitlinks. Check its release train: the tracked lock can lag the public
   cohort. The lock is narrower than the public surface matrix.
   Version bumps, tags, publication and deployment are coordinated
   maintainer actions after local qualification; refresh Cockpit at batch end.

**Migration scope:** consult current maintainer instructions and the target
owner's instructions before acting; this guide grants no authorization. The
workspace's standing scope covers owner/backend work and shared-UI adoption in
existing demonstrators/web apps, including their necessary adapters, pins and
assets. Studio backend/owner integration is authorized; Studio GUI migration
and refactoring remain last and joint with the maintainer. Preflight takeover
includes its existing engine/backend, UI and instruction work. Preserve concurrent
work and follow the current task's narrower limits. Hosting, deployment and
experiment/data uploads require separate authorization.

Write code, comments, documentation, commits and PRs in **English**. Follow each
repo's toolchain/license rules. Never commit credentials, private data, generated
workspaces, caches or incidental build outputs.
