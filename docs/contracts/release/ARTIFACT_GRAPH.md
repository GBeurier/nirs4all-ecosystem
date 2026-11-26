# Ecosystem artifact release graph

The planner starts from the affected package or deliverable. The target delivery flow builds and qualifies candidates before their registry versions exist. Package versions advance independently under [VERSION_CONSTRAINTS.md](VERSION_CONSTRAINTS.md). Published tags identify public versions. The rollout adds a weekly or manual clean qualification of an explicitly selected ecosystem baseline.

## Select the affected artifacts

```sh
python scripts/n4a_artifact_graph.py --artifact io.browser
python scripts/n4a_artifact_graph.py --artifact io.core-crate
python scripts/n4a_artifact_graph.py --artifact preflight.rust-crates
python scripts/n4a_artifact_graph.py --repository nirs4all-quality
python scripts/n4a_artifact_graph.py --full
```

The **Ecosystem artifact graph** workflow uploads the plan. Use repository scope when a change has not been classified at package level. The [inventory](artifact-graph.n4a.json) covers the ecosystem's tracked member repositories plus Server and Ecosystem itself. Each node identifies owner source files at a reviewed commit. These commits establish the inventory's provenance. The executor will separately resolve the selected candidate sources and qualified baseline.

| Relationship | Planned work |
| --- | --- |
| Compile | Rebuild the binary with the candidate crate/source inputs. A Rust crate consumed by Cargo can be staged as exact source before crates.io publication. |
| Bundle | Reassemble the output using the staged bytes of its changed inputs. Preserve unchanged dependencies from the baseline. |
| Runtime | Reuse the consumer's bytes and qualify the selected install or execution profile with the changed runtime inputs. |
| Review | Resolve an admission constraint, such as an incompatible version series or a separately maintained lock, before substitution. |
| Observe | Refresh Cockpit after applicable publications have been verified through the public channel. |

Candidate builds wait for their candidate material inputs. Qualification separately resolves the affected runtime closure. A packed site or installer declares the dependencies it actually embeds. The planner will not substitute a runtime dependency inside already assembled bytes. Optional integrations have named qualification gates. For example, SDK and Tools can be installed and tested together for workspace migration after each required artifact exists.

| Starting change | Selected outcomes |
| --- | --- |
| IO browser delivery only | Reassemble Web's site and offline app, QualiNIRS, the Preflight demo and the IO demo. Reuse the native IO and Core outputs and the independent IO npm Node delivery. |
| IO common Rust crate | Recompile IO bindings and the Core/Studio outputs which embed IO. Reassemble consumers taking those binaries. Requalify the retained SDK wheel and Papers' optional readers. Domains' IO loader requires admission because it pins Node WASM 0.2.14. |
| Preflight engine crate | Rebuild the Preflight wheel and WASM and the Domains native and WASM outputs. Reassemble their affected sites. |
| SDK wheel | Reassemble the Linux/Windows Studio installers and Docker image with the candidate wheel. Qualify the macOS registry-install profile and optional readers, including Papers. Reuse the existing Studio sidecar. |
| Deposited Papers content | Reassemble the document site. Select `papers.document-site` for this change. Deposited source, data and reproductions retain their own provenance. |

## Rollout

1. Run the read-only planner with explicit affected artifacts. Validate named paths with owner manifests, release workflows and staged inputs. Treat unlisted bindings, delivery variants and capability profiles as outside the automated impact decision until their inputs are declared and verified.
2. Connect owner builders to stage exact candidate bytes. A reusable result records the source commit, selected dependency digests, platform, toolchain and relevant build options, plus the output SHA-256. Reuse a result only when those inputs match. Browser artifacts include the matched JS loader, WASM, declarations and companion modules. Preserve Web/QualiNIRS pin verification when substituting candidate inputs.
3. Wire installed and delivered-product tests to those bytes. Start with IO browser → Web and QualiNIRS, IO native → Core/SDK, and Preflight → Domains. Connect independently runnable builders and tests in parallel once their inputs are ready. Retain the existing source/contract, numerical and platform gates for the affected profiles.
4. Promote the qualified bytes from each owner channel. Verify the served or installed bytes, then refresh Cockpit. Retry failed promotion from the same qualified artifact. Keep channel rules, trust configuration and Studio release authorization with their current owners.
5. Run the full qualification on a clean, pinned baseline weekly or manually. Use its evidence to check the declared graph against the actual dependency resolution and detect missing paths. Publish only when an owner version or delivery needs promotion.

The read-only planner emits the complete affected or full plan. The workflows below execute selected paths from that plan. The remaining builders, owner promotion and cross-channel timing measurements are tracked by the rollout above.

## Public release observations

The [artifact release targets](artifact-release-targets.n4a.json) associate a graph node with exact public Cockpit targets by package ID, registry and target name. The mapping contains no release versions. Consumers join it with the current public `data/current.json` whenever their snapshot refreshes. An artifact can have several observations, such as a source package tracked by both R-universe and CRAN.

A missing target leaves the artifact visible without a release observation. Separate browser packages, individual Studio installers and other outputs need their own target evidence before they can inherit any observation. A Pages health result can have an unavailable version. These public observations describe the published channel and do not qualify a candidate build.

## Executable qualification

**Graph qualification - IO browser and Web** admits candidate changes limited to the
Rust source of the IO browser binding. It builds the binding once from the exact
commit, verifies and transfers its bytes to Web, and assembles Web's served and
offline products using the retained WASM and companion files. Both products are
smoked before the run archives them. Its retained mode exercises the same Web
checks with the committed artifact cohort and skips the Rust browser build.
The candidate workflow covers the Web branch of the IO plan. Other IO consumers
require their own adapters.

**Weekly retained artifact qualification** runs Saturday at 02:15 in
`Europe/Paris` (Friday night), and can be dispatched manually. It runs the
[historical tagged source cohort](../../CANDIDATE_COHORT.md#friday-tagged-source-cohort)
at the full Linux tier alongside the retained Web checks, the SDK quickstart and
replay through Studio's pinned Linux wheel set, the Domains browser-profile Rust
tests against locked Preflight crates, and aggregation lock and capability checks. It posts a coverage and
failure summary in GitHub Actions for Monday triage. The attached full plan
includes all declared artifacts. A green run applies to the listed checks only.
Publication stays with the owner workflows, and the scheduled run uses read-only
permissions.

## Default-branch changes and source candidates

The **Weekday ecosystem impact** workflow compares the default branch of each
public member in `.gitmodules`, plus Ecosystem itself. It runs every 15 minutes
and supports manual dispatch. Each scan records the exact previous and current
commits and combines concurrent changes into a single affected plan. Scheduling
and runner queues can add latency. Server uses local admission. Compare an
exact range in any inventoried sibling, including Server, with this command:

```sh
python scripts/n4a_weekday_changes.py --repository nirs4all-io --checkout ../nirs4all-io \
  --base "$BASE_SHA" --head "$HEAD_SHA" --output impact.json
```

Reviewed source-directory rules select roots for an individual change. For
example, IO's shared WASM binding feeds both the browser and Node packages.
A change to a workspace manifest, an unmapped file, a rewritten branch or a
truncated compare selects the repository's declared outputs. Both paths of a
rename count. Some source nodes, notably DAG and Preflight, still group several
crates. The report distinguishes path selection from repository fallback.

The cached cursor records **observed** revisions after the impact report is archived
and the selected candidate job passes. An expired cursor starts from the inventory's reviewed commits. Re-run
a failed qualification on its original run and inspect the source SHAs in the
receipt. The cursor does not establish a qualified or published version.

The attached plan lists all affected declared surfaces. The Preflight → Domains
job exercises two named consumer test suites against both candidate crates in
disposable checkouts. It verifies Cargo selected the exact source paths in the
consumer's reachable dependency graph and retained all unrelated lock entries.
The ordinary consumer version constraints remain active. Admission of a changed
lock or incompatible version requires a reviewed consumer update. A manual run
also exercises this handoff with the current public revisions. Passing this job
qualifies only those suites. Other owner releases still follow their existing
publication workflows.

The `cargo` section expands individual crates at the observed commits. It reads
tracked Cargo manifests, including inherited workspace dependencies, renamed
packages and target-specific dependencies. It follows reverse dependencies from
each changed source directory. The graph includes possible consumers across
features and targets. Per-profile Cargo resolution still determines which
candidate enters a given binary. The accompanying artifact plan describes the
language bindings, runtime tests and products that Cargo cannot discover.

Changes under the source directory of a standalone CLI select its own binary.
The weekday job builds and tests that package in the release profile on Windows
when all material inputs can come from the owner's locked checkout. Each
retained binary carries its SHA-256, source revision, Cargo lock digest and
compiler identity. A change that also needs candidate material from upstream
remains in the impact plan for an adapter that can stage those inputs.

**Weekly Windows CLI qualification** rebuilds the DAG, DMD, Datasets, Domains,
Formats, IO and Preflight CLIs on clean Windows runners at the seven source
commits pinned by Ecosystem's gitlinks. It runs alongside the retained Friday
workflow at 02:15 Saturday in Europe/Paris. The source list, package tests and
Windows binaries are available from the run. These package checks supplement
the product qualification documented above.
