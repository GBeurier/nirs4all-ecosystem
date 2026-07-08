# WAVE 10U - Cockpit Stable Ledger Repin

Date: 2026-07-09

## Scope

Repin the ecosystem cockpit submodule after the public cockpit snapshot was
refreshed for the WAVE 10T stable runtime evidence ledger.

## Files Modified

- `nirs4all-cockpit`
- `docs/agent_reports/WAVE_10U_COCKPIT_STABLE_LEDGER_REPIN.md`

## Upstream Evidence

- `nirs4all-ecosystem` stable ledger commit: `5d16053`
- `nirs4all-cockpit` snapshot commit: `1575bc7`
- Cockpit workflows on `1575bc7`: `ci`, `pages`, and `version-guard` passed.

## Decision

Keep the release/topology lock aligned with the public cockpit snapshot while
accepting the normal one-commit repin cycle: the cockpit snapshot records the
functional ecosystem ledger head, and this ecosystem commit records the refreshed
cockpit snapshot.
