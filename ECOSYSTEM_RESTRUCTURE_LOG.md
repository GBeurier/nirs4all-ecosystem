# nirs4all Ecosystem Restructure Log

Started: 2026-06-11

## Target Model

- `nirs4all-drafts`: private working area for active manuscripts, reviews, journal scouting, and lab-to-paper drafting material.
- `nirs4all-papers`: public repository for deposited papers, PDFs, and reproducible public code bundles once a draft and its lab work are accepted for publication/release.
- `nirs4all-web`: standalone browser client built from the WASM stack. This is the role currently implemented by the existing `nirs4all-lite` checkout.
- `nirs4all-lite`: canonical low-level aggregate distribution of `dag-ml`, `dag-ml-data`, `nirs4all-formats`, `nirs4all-io`, `nirs4all-datasets`, and `nirs4all-methods`, with native/idiomatic bindings for Rust, Python (`nirs4all-lite` package name), R, MATLAB/Octave, and JavaScript/WASM (`nirs4all` package name outside Python).
- `nirs4all-org`: static website repository for `nirs4all.org`, replacing the ambiguous `nirs4all-webpage` name.

## Visibility Policy

Working assumption for this migration:

- private: `nirs4all-drafts`
- public: `nirs4all-papers`, once it contains only deposited/reproducible material

Note: the initial request also said "`nirs4all-drafts` and `nirs4all-papers` are the only private repositories", but the surrounding paper workflow says deposited papers and reproducibility kits should be public and permanent. Do not publish sensitive draft material into the new public `nirs4all-papers`.

## Initial State Observed

- `GBeurier/nirs4all-drafts` does not currently exist on GitHub.
- Local `nirs4all-drafts/` is not a git repository and only contains `.codegraph/`.
- `GBeurier/nirs4all-papers` exists and is private; local checkout has active uncommitted draft work.
- `GBeurier/nirs4all-lite` exists and is public; local checkout contains the browser app under `studio-lite/`.
- `GBeurier/nirs4all-web` does not exist.
- `GBeurier/nirs4all-webpage` exists and is public; it serves `nirs4all.org`.
- `GBeurier/nirs4all-org` and `GBeurier/nirs4all.org` do not exist.
- `GBeurier/nirs4all-cluster`, `GBeurier/nirs4all-dist`, and `GBeurier/nirs4all-lab` are currently private.

## Remote State After 2026-06-11 Execution

- `GBeurier/nirs4all-papers` was renamed to `GBeurier/nirs4all-drafts` and remains private.
- `GBeurier/nirs4all-lite` was renamed to `GBeurier/nirs4all-web` and remains public.
- `GBeurier/nirs4all-webpage` was renamed to `GBeurier/nirs4all-org` and remains public.
- New public `GBeurier/nirs4all-papers` was created and seeded from local `nirs4all-papers/`.
- New public `GBeurier/nirs4all-lite` was created and seeded from local `nirs4all-lite/`.
- New public `GBeurier/GBeurier.github.io` was created as a minimal redirect from `https://gbeurier.github.io/` to `https://nirs4all.org/`.
- `GBeurier/nirs4all-org` Pages is configured with `CNAME=nirs4all.org`, source `main:/`, HTTPS enforced, and status `built`.

## Local State After Split

- Local checkout `nirs4all-web/` now contains the former `nirs4all-lite` browser/WASM app.
- Local checkout `nirs4all-org/` now contains the former `nirs4all-webpage` static site.
- Local checkout `nirs4all-drafts/` now contains the former private `nirs4all-papers` draft/manuscript repository.
- Local checkout `nirs4all-lite/` is a new git repository scaffold with Rust, Python, R, MATLAB/Octave, and JS/WASM binding surfaces.
- Local checkout `nirs4all-papers/` is a new git repository scaffold for public deposited papers and reproducibility kits.
- The old non-git `.codegraph` stub that occupied `nirs4all-drafts/` was moved to `nirs4all-drafts.codegraph-stub-20260611/`.

## Task Log

| Status | Task | Notes |
| --- | --- | --- |
| done | Inventory local repos and GitHub metadata | Used `git status` and `gh repo view --json isPrivate`. |
| done | Plan safe GitHub rename sequence | Keep remote operations separate because repo visibility changes can expose private material. |
| done | Move current `nirs4all-lite` role to `nirs4all-web` locally | Existing app remains browser/WASM client; package/workflow text now says `nirs4all-web`. |
| done | Recreate `nirs4all-lite` as canonical aggregate distribution | Added testable Rust/Python/JS registries, R/MATLAB skeletons, binding docs, parity plan, and CI placeholder. |
| done | Rename `nirs4all-webpage` to `nirs4all-org` locally | Prefer `nirs4all-org` over `nirs4all.org` for tooling compatibility; keep CNAME as `nirs4all.org`. |
| done | Re-home current private `nirs4all-papers` as `nirs4all-drafts` locally | Preserved active draft history and uncommitted work; did not make public. |
| done | Initialize new public `nirs4all-papers` locally | README, safety rules, and reproducibility kit template added; AOM public repro can migrate later. |
| in-progress | Update `nirs4all-ecosystem` submodules/docs | README reflects target model. `.gitmodules` still needs a controlled update after remote renames/create. |
| done | Update `nirs4all.org` content | Replaced "lite demo" language with `nirs4all-web`; added `nirs4all-lite` and `nirs4all-papers` links. Deployed to Pages successfully. |
| done | Restore `https://gbeurier.github.io/` | Created `GBeurier.github.io` redirect page to `https://nirs4all.org/`; Pages status is `built`. |
| done | Push `nirs4all-web` rename commit | Pages deploy succeeded and `https://gbeurier.github.io/nirs4all-web/` now serves `nirs4all-web` title/OG metadata. |
| done | Push `nirs4all-lite` seed | Remote `main` exists; CI scaffold passed. |
| done | Push `nirs4all-papers` seed | Remote `main` exists; content check passed. |
| pending | Audit private non-paper repos before visibility flips | `nirs4all-lab`, `nirs4all-cluster`, and `nirs4all-dist` are still private on GitHub; do not make public without content audit. |

## GitHub Commands Executed

Actual `gh` CLI syntax used `--confirm`, not `--yes`:

```bash
gh repo rename nirs4all-drafts --repo GBeurier/nirs4all-papers --confirm
gh repo rename nirs4all-web --repo GBeurier/nirs4all-lite --confirm
gh repo rename nirs4all-org --repo GBeurier/nirs4all-webpage --confirm

gh repo create GBeurier/nirs4all-papers --public --description "Deposited nirs4all papers and reproducible public code bundles"
gh repo create GBeurier/nirs4all-lite --public --description "Canonical low-level nirs4all aggregate distribution with Rust, Python, R, MATLAB/Octave, and WASM bindings"
gh repo create GBeurier/GBeurier.github.io --public --description "GitHub Pages user-site redirect to nirs4all.org"
```

Local `origin` URLs updated:

```bash
git -C ../nirs4all-drafts remote set-url origin https://github.com/GBeurier/nirs4all-drafts.git
git -C ../nirs4all-web remote set-url origin https://github.com/GBeurier/nirs4all-web.git
git -C ../nirs4all-org remote set-url origin https://github.com/GBeurier/nirs4all-org.git
```

New local seed repositories pushed:

```bash
git -C ../nirs4all-papers remote add origin https://github.com/GBeurier/nirs4all-papers.git
git -C ../nirs4all-papers push -u origin main
git -C ../nirs4all-lite remote add origin https://github.com/GBeurier/nirs4all-lite.git
git -C ../nirs4all-lite push -u origin main
```

Finally update `nirs4all-ecosystem/.gitmodules`, sync submodules, and commit the new submodule pointers.

## Remaining Controlled Work

- Update `nirs4all-ecosystem/.gitmodules` and submodule gitlinks now that all target remotes exist.
- Decide whether to keep or remove the pre-existing local `single-page-WASM/` deletion in `nirs4all-web`; it was not included in the `nirs4all-web` rename commit.
- Audit `nirs4all-lab`, `nirs4all-cluster`, and `nirs4all-dist` before any visibility change.
- Migrate AOM public reproduction material into `nirs4all-papers` only after draft/private content is separated.
