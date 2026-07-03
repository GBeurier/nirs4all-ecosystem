# Wave 4AH - Methods Python Sdist Gate

Date: 2026-07-03

Scope:

- `nirs4all-methods` selected RC worktree: `_worktrees/RC-v1-methods`
- Branch: `rc/v1-full-refactor`
- Head: `115077ae`
- Tag: `n4a-v1-rc1-2026.07-refactor`

Files changed:

- `.github/workflows/ci.yml`
- `Makefile`
- `bindings/python/scripts/make_python_package.py`
- `bindings/python/scripts/smoke_installed_nirs4all_methods.py`
- `bindings/python/tests/test_installed_nirs4all_methods_smoke.py`

Decision:

- The full Python distribution `nirs4all-methods` now has a local and CI smoke
  for both wheel and sdist installability.
- The generated package now writes `setup.cfg` in addition to `pyproject.toml`,
  avoiding the observed sdist fallback to `UNKNOWN-0.0.0`.
- The sdist smoke inspects the tarball and requires the bundled `libn4m` payload
  before installing into a clean venv and importing `n4m`.

Local gates:

- `python3 -m pytest bindings/python/tests/test_installed_nirs4all_methods_smoke.py -q`
  -> `6 passed`.
- `python3 bindings/python/scripts/smoke_installed_nirs4all_methods.py --help`
  -> passed.
- `make help`
  -> passed.
- `make test-python-install`
  -> installed wheel, imported `n4m`, loaded bundled `libn4m`, ran SNV/PLS smoke,
  returned `INSTALLED_N4M_OK`.
- `make test-python-sdist-install`
  -> inspected `nirs4all_methods-1.0.1.tar.gz` (`115` members, bundled
  `src/n4m/lib/libn4m.so.2.0.0`), installed from sdist, returned
  `INSTALLED_N4M_OK`.
- `make test-abi-freshness PRESET=dev-release`
  -> ABI snapshot/loadability/linkage OK.
- `scripts/bump_version.sh --check`
  -> manifests in sync with `1.0.1`.
- `git diff --check`
  -> passed.

GitHub status:

- Branch and RC tag were pushed to `115077ae`.
- Remote GitHub Actions are green on `115077ae`: `CI`, `Parity gate`,
  `Cross-binding parity`, `Coverage`, `Sanitizers`, `ABI Surface`,
  `version-sync`, and `version-guard`.

Risks:

- This is a host-local sdist smoke for the bundled library model. It does not
  claim a portable from-source native rebuild on every platform.
- The full release wheel matrix still remains owned by `release-wheels.yml`.
