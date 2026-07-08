# Wave 8B - No Legacy Lite Alias

Date: 2026-07-08

## Summary

Aligned active roadmap/design wording with the decision that `nirs4all-core` is
the canonical public aggregate name and that no public `nirs4all-lite`
compatibility alias should be maintained.

## Files Modified

- `docs/MULTIMODAL_ECOSYSTEM_DESIGN_SCHEMAS.md`
- `docs/NIRS4ALL-ECOSYSTEM_VISION.md`
- `../nirs4all-studio/docs/STUDIO_PRISTINE_AUDIT.md`

## Decisions

- Historical mentions of `nirs4all-lite` are allowed only when explaining the
  pre-rename origin.
- Active packaging, roadmap and risk wording must say `nirs4all-core` and
  explicitly avoid public legacy aliases.
- Test-only guards that reject `nirs4all-lite` backend ids remain valid.

## Tests Run

- `rg` checks for remaining active `nirs4all-lite` alias language in the touched
  ecosystem docs.

## Risks

- Two ignored README files under generated Web WASM package directories still
  exist locally and are not publishable through `nirs4all-web` without changing
  ignore policy.
