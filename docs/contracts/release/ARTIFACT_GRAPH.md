# Ecosystem artifact release graph

Plan, build and qualify a change from the package or deliverable it affects. Package versions advance independently under [VERSION_CONSTRAINTS.md](VERSION_CONSTRAINTS.md). Build and qualification can consume a candidate before its registry version exists. Published tags identify public versions. A clean weekly or manual run qualifies an explicitly selected ecosystem baseline and can propose a coherent publication batch when needed.

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

Candidate builds wait for their candidate material inputs. Qualification separately resolves the affected runtime closure. Optional integrations have named qualification gates. For example, SDK and Tools can be installed and tested together for workspace migration after each required artifact exists.

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

The current workflow executes the planning stage in read-only mode. `--full` emits the full plan. Candidate acquisition, actual build fan-out, publication, the periodic full runner and cross-channel timing measurements require the rollout above. The Studio Linux artifact rehearsal remains release-independent evidence of reuse after a late failure.
