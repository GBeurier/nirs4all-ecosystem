# Wave 4AP - Studio Skip Hardening

Date: 2026-07-03

Scope:

- `nirs4all-studio` selected RC worktree: `_worktrees/RC-v1-studio`
- Branch: `rc/v1-full-refactor`
- New head: `0eb8596`
- Tag refreshed: `n4a-v1-rc1-2026.07-refactor`

Files changed:

- `tests/integration/test_run_errors.py`
- `tests/test_operators_manifests.py`

Decision:

- Convert product and contract precondition skips into hard test failures.
- Keep the endpoint degradation tests that deliberately mock a missing
  `nirs4all.runtime` accessor, because those verify the product's old-runtime
  UX path rather than release-gate availability.
- Make Studio fail when quick-run or experiment creation fails in run-error
  tests; those failures are the subject under test and must not disappear as
  skipped tests.
- Make Studio fail when completed-run preconditions do not hold for stop/retry
  tests or when the slow-run precondition for delete-while-running does not
  hold.
- Make the manifest contract test require the real
  `nirs4all.runtime.list_controller_manifests()` accessor, the dag-ml
  `controller_manifest.schema.json`, and `jsonschema`.
- Resolve the dag-ml schema in both local multi-repo layouts and GitHub Actions
  layouts instead of reintroducing a skip.

Local gates:

- `rtk pytest tests/test_operators_manifests.py tests/integration/test_run_errors.py -q`
  -> `29 passed`.
- `rtk ruff check tests/integration/test_run_errors.py tests/test_operators_manifests.py`
  -> passed.
- Static skip scan over the two hardened files:
  `rg -n "pytest\\.skip\\(|importorskip|xfail|skipif" ...` -> no matches.
- `git diff --check` -> passed.

Review:

- Codex worker `019f26fe-020c-73f0-9b64-7fb7ce859046` implemented the
  hardening and reported the same targeted pytest/Ruff results.
- Coordinator review adjusted the dag-ml schema resolver to cover both
  `/home/delete/nirs4all/dag-ml` style local checkouts and GitHub Actions'
  `path: dag-ml` checkout under the Studio workspace.

Risks:

- Environments that run the hardened Studio gate without the RC Python runtime,
  dag-ml checkout, or `jsonschema` will now fail. That is intentional for RC
  release gates.
- This does not rerun the full Studio backend/frontend suites; those remain
  covered by the existing broader Studio CI and the final cutover batch.
- Studio all-in-one archive and Docker release jobs still need a real run after
  the Wave 4AO pin fix and this Wave 4AP test hardening.
