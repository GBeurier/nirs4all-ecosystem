# Wave 6S - UI Convergence Audit

Date: 2026-07-06

## Scope

- Repos: `nirs4all-ui`, `nirs4all-studio`, `nirs4all-web`
- Mode: read-only audit

## Finding

`nirs4all-ui` is not yet a shared Studio/Web application base. It is currently a small shared
library for score formatting, runtime diagnostics, runtime badges, and a few presentational
components.

## Current Reuse

- Studio depends on `nirs4all-ui` via `file:../nirs4all-ui` and aliases the sibling source in Vite
  and TypeScript.
- Web depends on a vendored `nirs4all-ui` shim under `studio-lite/vendor/nirs4all-ui`.
- Studio uses shared runtime components through local wrappers.
- Web uses `RuntimeEngineBadge`, runtime helpers, and score formatting helpers.

## Still Duplicated

- Shadcn/Radix primitives exist as separate local copies in Studio and Web.
- Dataset/explore surfaces are separate.
- Pipeline editors are separate.
- Results and prediction views are separate.
- Navigation/workbench shell is separate.
- Web still reconstructs some runtime error text locally although `nirs4all-ui` exposes a formatter.

## Decision

Do not claim that Web and Studio are already quasi-identical through `nirs4all-ui`. The convergence
has started at the runtime/score/badge layer only. The next implementation wave should extract
host-agnostic contracts and components for dataset summary, pipeline DSL display, run/result
presentation, prediction display, and workbench navigation while leaving host adapters local.
