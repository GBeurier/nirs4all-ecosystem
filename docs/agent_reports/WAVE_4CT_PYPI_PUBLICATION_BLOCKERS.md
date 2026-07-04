# Wave 4CT — PyPI Publication Blockers

Date: 2026-07-04

## Scope

- Lane A / release cockpit publication audit.
- Repos reviewed: `nirs4all-core`, `nirs4all-providers`, `nirs4all-tools`, `nirs4all-cockpit`, `nirs4all-ecosystem`.
- Production hold respected: no release action on `nirs4all` Python or `nirs4all-studio`.

## Changes Integrated

- `nirs4all-cockpit@757e737`
  - `ops/targets.yaml`: `nirs4all-tools` PyPI reason now records the real failure:
    `invalid-publisher on v0.0.1 release`.
  - `ops/manual-actions.yaml`: providers/tools manual actions now name the failed tag.
  - `tests/test_targets_topology.py`: guard added so core/providers/tools blockers must keep exact PyPI OIDC evidence.
- `nirs4all-ecosystem`
  - Gitlink moved to `nirs4all-cockpit@757e737`.

## Publication Status

The PyPI publication failures are external Trusted Publisher configuration blockers, not package build failures:

- `nirs4all-core`: `release-python.yml@refs/tags/v0.2.3` failed with PyPI `invalid-publisher`.
- `nirs4all-providers`: `publish.yml@refs/tags/v0.2.1` failed with PyPI `invalid-publisher`.
- `nirs4all-tools`: `publish.yml@refs/tags/v0.0.1` failed with PyPI `invalid-publisher`.

Required manual action:

- Create PyPI Trusted Publishers with environment `pypi` for the three projects above, then rerun the failed tag workflow or dispatch the publish workflow where supported.

## Verification

From `nirs4all-cockpit`:

- `python3.11 -m pytest -q` — 93 passed.
- `python3.11 -m cockpit.cli validate-targets ops/targets.yaml` — OK, 21 packages / 98 targets.
- `python3.11 -m cockpit.cli collect --offline --out /tmp/n4a-cockpit-offline-current.json` — OK.
- `python3.11 -m ruff check .` — OK.

## Risks / Decisions

- Do not hide these blockers by rewording them as pending publication.
- Do not attempt token-based PyPI publishing from local token files; the current workflows are OIDC Trusted Publisher based.
- Full parity remains deferred until the next large integration batch, per user instruction.
