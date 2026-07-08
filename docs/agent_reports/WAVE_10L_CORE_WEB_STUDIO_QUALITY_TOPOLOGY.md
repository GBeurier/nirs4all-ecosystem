# Wave 10L - Core/Web/Studio/Quality topology sync

## Scope

- Repinned public ecosystem gitlinks for `nirs4all-core`, `nirs4all-web`,
  `nirs4all-cockpit`, and `nirs4all-studio` to their current pushed heads.
- Added `nirs4all-quality` as a public ecosystem submodule because the cockpit
  now tracks it as an RC browser/WASM surface.
- Added `nirs4all-quality` to the public V1 surface matrix as an optional
  client-side custom-host product surface outside the aggregation lock.
- Kept `nirs4all` Python and production `nirs4all-studio` releases held; the
  Studio change is a CI guard and manual Windows RC blocker only.
- Replaced the release distribution matrix pointer to tracked contracts instead
  of workspace-local scratch files.

## Files Modified

- `nirs4all-quality`: public URL metadata and version guard.
- `nirs4all-studio`: version guard.
- `nirs4all-cockpit`: RC metadata for Studio/Web/UI, Studio Windows manual
  blocker, generated manual-action payload, and targeted snapshot refresh for
  Studio/Web/Quality/UI after the full local collect timed out.
- `nirs4all-web`: documentation/comment cleanup for retired `lite` wording.
- `nirs4all-ecosystem`: `.gitmodules`, gitlinks, README topology, public surface
  matrix, release matrix pointer, topology tests, and this report.

## Tests Run

- `nirs4all-quality`: `npm run typecheck`, `npm run build`, local version-guard
  check, `git diff --check`.
- `nirs4all-studio`: local version-guard check, `git diff --check`.
- `nirs4all-cockpit`: `n4a-cockpit validate-targets`, `pytest -q`,
  `python3 scripts/smoke_dashboard_dom.py`, targeted
  `cockpit.cli collect --only nirs4all-studio,nirs4all-web,nirs4all-quality,nirs4all-ui`,
  `git diff --check`.
- `nirs4all-web`: documentation/comment-only cleanup; `git diff --check`.
- `nirs4all-ecosystem`: release surface matrix, release-lock selected-root
  validation, gitmodule topology, and targeted release tests before commit.

## Decisions

- `nirs4all-quality` is now a public topology member rather than a cockpit-only
  surface.
- `nirs4all-studio` remains production-held. The Windows installer RC is tracked
  as a manual blocker instead of being released automatically.
- The `studio-lite/` path remains a technical app directory for now; public
  wording is aligned with `nirs4all-web` / `nirs4all-core`.
- The full local cockpit collect timed out after 300 seconds; only the four
  desynchronized package entries were refreshed and the global target-status
  counts were recomputed.

## Risks

- Studio/Web adoption of `nirs4all-ui` is still partial: contracts and package
  imports exist, but not every shared component/style/asset is used in product
  screens yet.
- A full Python-reference parity run has not been re-run in this wave; keep it
  after the next large integration batch.
