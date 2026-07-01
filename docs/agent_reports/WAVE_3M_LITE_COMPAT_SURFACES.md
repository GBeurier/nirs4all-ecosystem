# Wave 3M - Lite Compat Surface Registry

Date: 2026-07-01

## Scope

Lane E/A tranche focused on `nirs4all-lite` release-topology metadata for the public aggregate surfaces. No behavior change, no release-lock pin change, and no full parity run.

This tranche directly reinforces the roadmap requirement that public `nirs4all` accounting includes:

- Python `nirs4all` as the existing oracle package reserved outside the lite aggregate;
- R `nirs4all` as the lite aggregate R package;
- browser/WASM `nirs4all` as the lite aggregate npm package.

## Commit

- `nirs4all-lite` `1824421` - `test(release): align compat upstream package surfaces`

## Files Modified

`nirs4all-lite`:

- `compat/upstreams.toml`
- `bindings/python/tests/test_release_topology.py`

## Agents

| Agent | Ownership | Status | Output |
| --- | --- | --- | --- |
| Planck | Read-only Lane E audit of `nirs4all-lite` | done | Found the same narrow patch: align `compat/upstreams.toml` with existing release topology for R/WASM upstream package declarations. |
| Nietzsche | Initial review of the two-file diff | GO | Confirmed `methods.ref` was unchanged and no release-lock files changed; noted the test did not assert `bindings` flags. |
| Darwin | Final review after strengthening the test | GO | Confirmed `dag_ml` WASM and `datasets` R binding flags now match package declarations; no blockers. |

## Decisions

- Keep this as contract/topology hardening only.
- Add `r` and `r_packages = ["nirs4alldatasets"]` to the `datasets` compat row, matching existing R `Suggests`, release workflow comments, and `release_topology_manifest()`.
- Add `wasm` to the `dag_ml` compat row because it already declares `wasm_packages = ["dag-ml-wasm"]`.
- Add a release-topology test comparing `compat/upstreams.toml` to `release_topology_manifest()["upstream_components"]` for repo, role, Python imports, R packages, WASM packages, and required `r`/`wasm` binding flags.
- Do not change `methods.ref` (`00ca846705bc6ca30ec34ad9e8452e241dda6945`).
- Do not regenerate or repin aggregation lock files from the current sibling workspace.

## Tests Run

`nirs4all-lite`:

- `PYTHONPATH=bindings/python/src python3 -m unittest bindings/python/tests/test_release_topology.py -v` -> 12 passed.
- `PYTHONPATH=bindings/python/src python3 -m unittest bindings/python/tests/test_facade.py bindings/python/tests/test_upstreams.py -v` -> 18 passed.
- `make test-python` -> 38 passed, 1 skipped.
- `python3.11` TOML parse of `compat/upstreams.toml` -> passed.
- `git diff --check` -> passed.

## Risks / Follow-Ups

- This does not prove `nirs4alldatasets` installability or runtime parity; it only prevents topology metadata drift.
- The new test is scoped to Python/R/WASM package-declaration consistency, not a full schema validator for every binding kind.
- R CMD check, npm tests, and full parity remain deferred to larger integrated gates or CI/toolchain environments.
