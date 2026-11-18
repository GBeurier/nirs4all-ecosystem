# Cross-repository version constraints

Status: maintainer decision, 18 November 2026 (versioning rule revised the same
day). Applies to every nirs4all repository that releases a package or declares a
dependency on a package released from another nirs4all repository.

## Why

Repositories used to pin each other exactly (Rust `=0.3.5`, Python `==`, npm
exact). Every patch release of a lower layer then forced a release of every
consumer only to move a pin (IO 0.3.5 forced Core, which forced Studio), and a
candidate-cohort build could not `[patch]` an unreleased crate whose version did
not match an exact requirement. Ranges that stop at the next major (`^1.3.0`,
Cargo `"1.3"`, `>=1.3,<2`) have the opposite defect: they accept untested
compatibility breaks. Exact versions belong in lockfiles; manifests accept the
patches of one tested series.

## Version numbers

Versions are `X.Y.Z`.

| Part | Bumped for | Examples |
|---|---|---|
| `Z` (patch) | No compatibility change: fixes and purely additive, backward-compatible features. Existing outputs, wire formats, schemas and ABI symbols stay unchanged. | bug fix; new catalog method; new optional export |
| `Y` (minor) | Any compatibility break. | changed or removed API signature; native ABI break or ABI version change; wire, byte, schema or shared fixture/golden change; renamed ids; changed numerical results of an existing operation |
| `X` | General/product version. | |

The package that bumps is responsible for classifying its change correctly
(`Z` or `Y`). A fix that changes the numerical result of an existing operation
is a `Y`, even when the previous result was wrong.

## Dependency ranges

A cross-repository dependency (a package from repository A depending on a
package from repository B) accepts every patch of **one tested `Y` series**:
`>=X.Y[.Z],<X.(Y+1)`.

- The floor is `X.Y`. A patch floor (for example `>=1.4.1,<1.5`) is allowed
  when the consumer requires a feature or fix from that patch.
- The upper bound is the next minor. Moving to a new `Y` series is an explicit,
  tested decision of the consumer.
- For packages at 1.x or above, never use the caret defaults that mean `<2`:
  npm `^1.4.0` and Cargo `"1.4"` both accept 1.5 and later.

| Ecosystem | 1.x or above | 0.x |
|---|---|---|
| Rust (Cargo) | `">=1.4, <1.5"`, `">=1.4.1, <1.5"` | `"0.4"`, `"0.4.1"` (caret, stops at 0.5) |
| Python (PEP 440) | `>=1.4,<1.5`, `>=1.4.1,<1.5` | `>=0.4,<0.5`, `>=0.4.1,<0.5` |
| npm | `~1.4.0`, `~1.4.1` (or `>=1.4.1 <1.5.0`) | `^0.4.0`, `^0.4.1` (caret, stops at 0.5) |
| R (`DESCRIPTION`) | `pkg (>= 1.4.1)` and a documented series | `pkg (>= 0.4.0)` and a documented series |

- R expresses an upper bound only by repeating a package entry; R packages
  declare a lower bound and document the tested series instead.
- A constraint that is absent or wider (`*`, an unversioned extra) may stay,
  but new constraints use the forms above.
- Existing ranges that predate this rule (for example 1.x caret ranges or
  `>=1.3,<2`) are aligned at each package's next normal release. No release is
  made only to align a range.

## What stays exact

Exact pins live only in lockfiles, hash-locked wheel locks and product install
lists:

- `Cargo.lock` (and binding lockfiles), `package-lock.json`, uv/pip locks and
  install constraint files (for example `nirs4all/docker/native-constraints.txt`);
- Studio's `install` versions in `recommended-config.json`, its hash-locked
  wheel locks (`build/constraints/python-wheels-*.json`) and
  `build/runtime-cohort.json`; Web's vendored packages;
- source trains and parity references that select sibling checkouts or commits
  (for example `nirs4all-datasets/release/train-v1.toml`,
  `nirs4all-core/compat/upstreams.toml`, workflow commit pins);
- vendored artifacts (`file:` tarballs, git commit references, staged WASM
  packages with provenance) and frozen scientific oracles (for example
  `dag-ml/tools/*-core-oracle`);
- this repository's submodule gitlinks.

A product's environment-admission range (the version below which the product
updates a user's environment) follows the range rule and may carry a patch
floor; Studio's `recommended-config.json` `nirs4all` range `>=1.4.18,<1.5` is
such a range.

## Intra-repository lockstep

Packages released together from one repository (for example
`nirs4all-io-core`/`nirs4all-io`, `dag-ml-core`/`dag-ml`, `nirs4all-methods`/
`pls4all`/R `n4m`, `nirs4all-preflight-core`/`nirs4all-preflight`) may keep
their exact lockstep pins, enforced by each repository's version tooling. They
never block cross-repository propagation.

## Native ABI (Methods)

Native libraries are accepted by the runtime ABI check
(`n4m_check_abi_compatibility(header_major, header_minor)`, exposed in Rust as
`n4m::runtime_abi_version`), never by package version. That check stays the
authority. Methods 1.x carries ABI major 2. An ABI version change, additive or
not, is a `Y`: it ships in a Methods minor and in an `n4m` crate minor.
Releases up to 1.3.18 shipped additive ABI minors in project patches
(1.3.11–1.3.14: ABI 2.20; 1.3.15–1.3.17: 2.22; 1.3.18: 2.23); Methods 1.4.0
carries ABI 2.24. The published `n4m` crate 0.4.2 requires ABI 2.22, so the
next crate publication is 0.5.0.

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
| Core | `bindings/python/tests/test_release_topology.py` (owner requirements are minor-level ranges); CI resolves `n4m` from `Cargo.lock` |
| SDK, Studio | dependency tests assert the declared ranges (`test_publish_workflow.py`/`test_rt_goldens.py`; `test_nirs4all_release_pin.py`) |
| Repository | `tests/test_train_compatibility.py` checks the `nirs4all` extra bounds |

Guards written for the previous minor-only form (Core, Datasets, dag-ml) are
updated with each owner's next release to accept a patch floor and to require
the `<X.(Y+1)` upper bound for 1.x dependencies.

Follow-up, not automated yet: a guard in each owner that fails when a contract
file, golden, the native ABI or a numerical reference result changes without a
minor bump (Methods: ABI version change without a project/crate minor).
