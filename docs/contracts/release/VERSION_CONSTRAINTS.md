# Cross-repository version constraints

Status: maintainer decision, 18 November 2026. Applies to every nirs4all
repository that declares a dependency on a package released from another
nirs4all repository.

## Why

Repositories used to pin each other exactly (Rust `=0.3.5`, Python `==`, npm
exact). Every patch release of a lower layer then forced a release of every
consumer only to move a pin (IO 0.3.5 forced Core, which forced Studio), and a
candidate-cohort build could not `[patch]` an unreleased crate whose version did
not match an exact requirement. Exact versions belong in lockfiles, not in
manifests.

## Rule

A cross-repository constraint (a package from repository A depending on a
package from repository B) is expressed at **minor** granularity, never more
precisely. Each ecosystem uses its caret-equivalent form:

| Ecosystem | 0.x dependency | 1.x dependency | Meaning |
|---|---|---|---|
| Rust (Cargo) | `"0.3"` | `"1.3"` | caret: `>=0.3.0, <0.4.0`; `>=1.3.0, <2.0.0` |
| Python (PEP 440) | `>=0.3,<0.4` | `>=1.3,<2` | same bounds |
| npm | `^0.3.0` | `^1.3.0` | same bounds |
| R (`DESCRIPTION`) | `pkg (>= 0.3.0)` | `pkg (>= 1.3.0)` | lower bound only (see below) |

- The floor is a minor (`X.Y`), never a patch. A floor that predates this
  contract and is older than the current release line may be kept at its minor
  with an upper bound at the next breaking boundary (for example
  `nirs4all>=0.10,<2`); it is not raised just to follow the rule.
- An existing deliberate pre-release bound that is not more precise than a minor
  (for example `nirs4all>=0.10,<2.0.0.dev0`) may stay.
- A constraint that is absent or wider (`*`, an unversioned extra) is not more
  precise than a minor and may stay, but new constraints use the form above.
- R expresses an upper bound only by repeating a package entry. The packages do
  not rely on it and declare lower bounds only.
- A consumer that needs a fix that exists only from a given patch does **not**
  encode it as a patch floor. Its lockfile and the release order deliver the
  patch; runtime checks (for example the Methods ABI check) refuse what cannot
  work.

## What stays exact

Exact, reproducible versions live in lockfiles and install cohorts, never in
dependency declarations:

- `Cargo.lock` (and binding lockfiles), `package-lock.json`, uv/pip locks and
  install constraint files (for example `nirs4all/docker/native-constraints.txt`);
- Studio's `install` versions in `recommended-config.json`, its hash-locked
  wheel locks (`build/constraints/python-wheels-*.json`) and
  `build/runtime-cohort.json`;
- source trains and parity references that select sibling checkouts or commits
  (for example `nirs4all-datasets/release/train-v1.toml`,
  `nirs4all-core/compat/upstreams.toml`, workflow commit pins);
- vendored artifacts (`file:` tarballs, git commit references, staged WASM
  packages with provenance) and frozen scientific oracles (for example
  `dag-ml/tools/*-core-oracle`);
- this repository's submodule gitlinks.

## Intra-repository lockstep

Packages released together from one repository (for example
`nirs4all-io-core`/`nirs4all-io`, `dag-ml-core`/`dag-ml`, `nirs4all-methods`/
`pls4all`/R `n4m`, `nirs4all-preflight-core`/`nirs4all-preflight`) keep their
exact lockstep pins, enforced by each repository's version tooling. They never
block cross-repository propagation.

## What a release promises

- A **patch** release is backward compatible and changes no wire format, byte
  contract, persisted schema, `.n4a` container or payload semantics, native ABI
  or shared fixture/golden.
- Any such change requires at least a **minor** release. For 0.x every minor is
  breaking, so consumers raise their range explicitly.
- For 1.x a minor may add to these surfaces backward-compatibly; removing or
  changing them requires a major release.

## Native ABI (Methods)

Native libraries are accepted by the runtime ABI check
(`n4m_check_abi_compatibility(header_major, header_minor)`, exposed in Rust as
`n4m::runtime_abi_version`), never by package version. That check stays the
authority. Methods 1.x carries ABI major 2. Releases up to 1.3.18 shipped
additive ABI minors in project patches (1.3.11–1.3.14: ABI 2.20; 1.3.15–1.3.17:
2.22; 1.3.18: 2.23). From now on an ABI minor ships in a Methods minor (the next
one is 1.4.0) and in an `n4m` crate minor. The crate on `main` already requires
ABI 2.23 while the published `n4m` 0.4.2 requires 2.22, so the next crate
publication is 0.5.0.

## RustSec advisories

`cargo audit` gates fail on vulnerabilities and unsound advisories (`cargo audit --deny unsound`), never on informational ones.
Unmaintained, notice and yanked advisories are printed as warnings in the job log and kept out of per-advisory ignore lists.

## Enforcement

| Repository | Existing enforcement |
|---|---|
| Methods | `scripts/bump_version.sh --check` (lockstep, ABI-constant drift), ABI symbol snapshots + `docs/abi/changes_log.md`, `scripts/check_n4m_crate_release.py` |
| Formats | `scripts/bump_version.sh --check`, `version-sync`/`version-guard`, conformance goldens, record-schema version |
| IO | contract-constant tests (`versions.rs`, `test_versions.py`), append-only goldens, `abi-check`, version sync |
| dag-ml-data | ADR-02 version bumps/refusals, ABI snapshot, `dag-ml/scripts/validate_contracts.py` |
| dag-ml | `validate_contracts.py`, conformance packs, `scripts/validate_release_metadata.py` (requires a `MAJOR.MINOR` `n4m` range with the locked crate inside it), ADR-29 |
| Datasets | `scripts/check_release_train.py` (manifest ranges equal the minor of the exact train; locks resolve the train) |
| Core | `bindings/python/tests/test_release_topology.py` refuses owner requirements more precise than a minor; CI resolves `n4m` from `Cargo.lock` |
| SDK, Studio | dependency tests assert the declared ranges (`test_publish_workflow.py`/`test_rt_goldens.py`; `test_nirs4all_release_pin.py`) |
| Repository | `tests/test_train_compatibility.py` checks the `nirs4all` extra bounds |

Follow-up, not automated yet: a guard in each owner that fails when a contract
file, golden or the native ABI changes without a minor bump (Methods: ABI change
without a project/crate minor).
