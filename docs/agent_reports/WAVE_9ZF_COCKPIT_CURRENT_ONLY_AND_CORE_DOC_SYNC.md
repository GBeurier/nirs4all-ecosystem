# Wave 9ZF - cockpit current-only cleanup and core doc sync

Date: 2026-07-10T00:48:02Z

## Scope

- `nirs4all-cockpit`: removed held-release wording from public target reasons for
  protected Python `nirs4all` and `nirs4all-studio`; kept statuses and release
  workflows unchanged.
- `nirs4all-cockpit`: added a snapshot guard so `Release bundles`,
  `production held`, `held outside`, and `production app release remains held`
  do not re-enter the public generated payload.
- `nirs4all-lite`: retired maintenance docs that still described a final PyPI
  compatibility/alias release as pending.
- `nirs4all-core`: clarified a historical changelog entry as "then-named lite".
- `nirs4all-ecosystem`: refreshed strategy docs after the `nirs4all-lite` to
  `nirs4all-core` cutover and fixed npm/WASM aggregate naming to `nirs4all`.

## Commits

- `nirs4all-cockpit` `ebf4672` - `fix(dashboard): remove held release wording from snapshot`
- `nirs4all-cockpit` `7a87327` - `chore(collect): refresh data/current.json`
- `nirs4all-lite` `83f7373` - `docs(core): retire lite alias release checklist`
- `nirs4all-core` `b25b9de` - `docs(changelog): clarify lite-era version entry`

## Tests and checks

- `cd nirs4all-cockpit && pytest -q` -> 142 passed.
- `cd nirs4all-cockpit && n4a-cockpit validate-targets ops/targets.yaml` -> OK, 23 packages, 103 targets.
- `cd nirs4all-cockpit && n4a-cockpit collect --offline --out /tmp/n4a-cockpit-current-check.json` -> OK scratch snapshot.
- GitHub Actions on `nirs4all-cockpit`:
  - `ci` on `ebf4672` -> success.
  - `version-guard` on `ebf4672` -> success.
  - `collect` run `29060646616` -> success.
  - `pages` on `7a87327` -> success.
- Public checks:
  - `https://cockpit.nirs4all.org/` exposes `manual-actions-block` and no
    `Release bundles`/`production held` UI strings.
  - `https://cockpit.nirs4all.org/data/current.json` has no
    `Release bundles`/`production held`/`held outside`/`production app release
    remains held` strings.

## Agent review inputs

- Core/topology reviewer found no active `nirs4all-lite` publication surface and
  reported only historical-doc drift. The drift was corrected or marked
  historical in this wave.
- Public surface reviewer confirmed the cockpit UI had already removed the
  `Release bundles` block and channel capsules; this wave also cleaned the
  generated public JSON wording.
- UI reviewer identified broader `nirs4all-ui` asset/adoption debt. No
  `nirs4all-ui` files or quality-used components were changed in this wave.

## Risks

- This is a docs/status cleanup and dashboard wording change; no runtime,
  package, prediction, converter or parity logic changed.
- `nirs4all` Python and `nirs4all-studio` remain protected production lines.
- R-universe remains externally gated until its rebuild/update can be completed.
