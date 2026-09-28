# Ownership handoff

Use this section when a change crosses lane ownership, touches a consulted lane,
or changes a contract, schema, or golden. Replace every placeholder; the JSON
can be checked with `python3 scripts/n4a_ownership_ledger.py validate-handoff
--handoff HANDOFF.json`.

```json
{
  "schema_version": "n4a.ownership-handoff/v1",
  "source_lane": "REPLACE_WITH_LANE_A_TO_H",
  "target_lane": "REPLACE_WITH_DIFFERENT_LANE_A_TO_H",
  "repositories": ["REPLACE_WITH_REPOSITORY_KEY"],
  "from_sha": "REPLACE_WITH_40_HEX_SOURCE_SHA",
  "to_sha": "REPLACE_WITH_40_HEX_TARGET_SHA",
  "tests": ["REPLACE_WITH_EXACT_COMMAND_AND_RESULT"],
  "rollback": "REPLACE_WITH_AN_EXPLICIT_REVERSIBLE_ROLLBACK",
  "artifact_classes": [],
  "arbitration_ids": [],
  "notes": "REPLACE_WITH_CONTEXT_OR_REMOVE_THIS_FIELD"
}
```

- [ ] Repository primary owner approved.
- [ ] Every touched consulted lane acknowledged the handoff.
- [ ] Contract/schema/golden owner approved when applicable.
- [ ] SHAs, tests, and rollback are concrete rather than placeholders.
