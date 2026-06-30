# RV7 — review of the `nirs4all-tools` scaffold (IMP-L18)

**Reviewer:** RV7 (read-only). **Lane:** L18 tools / legacy migration. **Lock:** `LOCK-MIG` / `DEC-MIG-001`.
**Under review:** staged tree of the new sibling repo `/home/delete/nirs4all/nirs4all-tools` (branch `main`,
22 files, all `A`/added, nothing committed) + `docs/agent_reports/IMP_L18_TOOLS_SCAFFOLD.md`.
**Contract of record:** `docs/agent_reports/SW4_MIG_CONVERTER_spec.md` (the signed `LOCK-MIG` spec).
**Mode:** direct `Read` + `git diff --cached` + focused validation runs. CodeGraph not relied on.
**Date:** 2026-07-01.

---

## 0. Disposition (TL;DR)

**APPROVE the scaffold to commit.** The four implemented surfaces — `inspect`, `migrate --dry-run`,
`migrate --copy-only`, and `verify` — plus the no-in-place policy core are correct, internally
consistent, and well covered. The green gate reproduces clean (ruff / 57 pytest / mypy). The
no-in-place guarantee holds end-to-end in my own out-of-tree smoke (source byte+mtime identical
pre/post). Every runtime fact the code hard-codes (table order, schema versions, table names) was
re-verified against live `nirs4all` source and matches.

**Not yet releasable as a package**, and three Medium items should be tracked before the converter
is treated as beyond-scaffold:

- **M1** — `--verify` (and `--strict`, `--trusted-load-joblib`) are accepted but inert; `--verify`
  on `--copy-only` exits `0` while performing **no** verification (`verification_summary.ran=False`).
- **M2** — emitted `input_inventory` / `output_inventory` entry shapes diverge from the frozen
  `legacy_migration_manifest.v1` field set (§7) under an unchanged `$id` + `schema_version: 1`.
- **M3** — `manifest.source.fingerprint` is always `null`; the spec makes it the byte-level
  no-in-place + `--resume` anchor, so today that guarantee rests only on `(size, mtime_ns)` stats.

None of these block the *scaffold* commit — the schema-transform engine is explicitly deferred — but
they are contract-level and should not silently persist into the first real engine slice or a release.

---

## 1. Validation evidence (reproduced read-only)

Run from `/home/delete/nirs4all/nirs4all-tools` with
`VENV=/home/delete/nirs4all/nirs4all/.venv/bin/python` (Python 3.11.15), `PYTHONPATH=src`,
`PYTHONDONTWRITEBYTECODE=1`, and `--no-cache`/`-p no:cacheprovider`/`--cache-dir=/dev/null` so no
caches are written into the staged tree:

| Check | Command | Result |
|---|---|---|
| Lint | `ruff check --no-cache .` | **All checks passed** |
| Tests | `pytest -q -p no:cacheprovider` | **57 passed** |
| Types | `mypy --no-incremental --cache-dir=/dev/null src/nirs4all_tools` | **Success, 11 files** |
| Staged hygiene | `git diff --cached --check` | clean; exactly the 22 intended files staged, no caches |
| Metadata | `tomllib` parse + AST `__version__` resolve | name/dynamic/scripts OK; `__version__=0.0.1` |
| `target` extra | `importlib.metadata.version('nirs4all')` | **0.10.3** → `nirs4all>=0.10.0` satisfiable |

**No-in-place smoke (my own, in `/tmp`, synthetic SQLite v2 ws + `notes.txt`):**

- `migrate --copy-only --verify` → exit `0`; source pre/post snapshot **byte+mtime identical**
  (`notes.txt 5 …487675265`, `store.sqlite 12288 …483675153` unchanged).
- Manifest spot-check: `$id = …legacy_migration_manifest.v1.json`; `target.kind = "copy-only"`;
  `checksums` present and **`sha256:`-prefixed** for `payload/notes.txt` + `payload/store.sqlite`.
- CLI `verify` clean → exit `0`; after tampering a payload byte → exit **`30`** (confirms the
  `VerificationFailed → 30` CLI mapping, which the unit tests exercise only at the exception layer).
- **Evidence for M1/M3:** the `--copy-only --verify` migrate report carried
  `verification_summary = {ran: False, passed: None, …}` and `source.fingerprint = None`.

**Runtime anchors re-verified against `nirs4all` working tree (all match the scaffold constants):**

| Scaffold constant | Source of truth | Verified |
|---|---|---|
| `FK_SAFE_TABLE_ORDER` (contracts.py:35) | `migration.py:493` `_MIGRATION_TABLES` | `projects,runs,pipelines,chains,predictions,artifacts,logs` ✓ |
| `WORKSPACE_V2_USER_VERSION=2`, `SUPPORTED_SQLITE_USER_VERSION=2` | `store_schema.py:28` `SCHEMA_VERSION=2` | ✓ |
| `SUPPORTED_NATIVE_MANIFEST_VERSION=2` | `native_results.py:58` `MANIFEST_SCHEMA_VERSION=2` | ✓ |
| `SUPPORTED_BUNDLE_FORMAT_VERSION=(1,0)` | `generator.py:54` `BUNDLE_FORMAT_VERSION="1.0"` | ✓ |
| legacy-arrays probe `"prediction_arrays"` | `migration.py:188,230,…` table name | ✓ |

---

## 2. Findings (severity-ordered)

### MEDIUM

**M1 — Inert migrate flags; `--verify` silently performs no verification.**
`cli.py:96` advertises `--verify` as *"migrate, then fully verify the output"*, and the CLI threads
`verify`, `strict`, `trusted_load_joblib` into `commands.migrate(...)` (`commands.py:183-187`). None of
the three is ever read in the function body (grep confirms the only other `verify` token is the
unrelated `def verify` at `commands.py:346`). `--best-effort` is not even forwarded from the CLI
(`cli.py:99-101` define it; `_cmd_migrate` reads only `args.strict`). Net effect, confirmed by smoke:
`migrate --copy-only --verify` exits `0` with `verification_summary.ran=False` — a user who explicitly
asked for verification gets none, with no signal. **Recommendation:** for the scaffold, either wire
`--verify` into the `--copy-only` path (run `verify()` on the produced output) or *reject* the inert
flags with an explicit `unsupported_capability` "not implemented in this scaffold" error, rather than
accepting-and-ignoring. (`ruff`/`mypy` will not catch unused function parameters, so this is invisible
to the gate.)

**M2 — Manifest inventory entry shapes diverge from the frozen `legacy_migration_manifest.v1` (§7).**
`_inventory_entry` (`commands.py:50-59`) emits
`{path, source_kind, detected_version, supported, forward_version, note, details}`, and the copy-only
`output_inventory` entry (`commands.py:166-169`) emits
`{path, tables, row_counts, generated_manifests, file_count}`. The spec's frozen §7 entry fields are
`{path, source_kind, tables, row_counts, discovered_manifests, discovered_bundles}` (input) and
`{path, tables, row_counts, generated_manifests}` (output). The top-level skeleton from
`contracts.build_manifest` is faithful, but the *per-entry* shape is an undocumented departure emitted
under the same `$id` and `schema_version: 1`. Because `--copy-only` manifests are durable artifacts a
user may keep, two different "v1" shapes can reach the wild once the real engine emits the spec shape.
**Recommendation:** align the entry field names now (carry the spec keys, even if empty/`null` in the
scaffold), or annotate the divergence and bump/namespace the schema before the manifest is consumed.

**M3 — `source.fingerprint` is always `null`; the no-in-place / `--resume` byte anchor is absent.**
`migrate` passes `source_fingerprint=None` (`commands.py:253`) into `build_manifest`
(`contracts.py:108` records it verbatim). Spec §7/§3.3/§3.5 designate `source.fingerprint`
(`"sha256:…"` tree fingerprint) as the byte-level no-in-place anchor and the `--resume` precondition.
Consequences: (a) the durable manifest cannot attest byte-for-byte source identity — only the
in-process `source_guard` `(size, mtime_ns)` snapshot does, and that cannot detect a same-size,
mtime-restored in-place edit; (b) `--resume` has nothing to validate against (see L1). The snapshot
machinery already walks the whole tree, so deriving a content fingerprint is incremental work.
**Recommendation:** populate `source.fingerprint` (SHA-256 over the canonical file set) before the
manifest is treated as a contract of record. This gap is **not** listed in the IMP report's residual
risks.

### LOW

**L1 — `--resume` does not enforce its spec §3.3 precondition.**
`assert_output_available(output, resume=resume)` (`policy.py:100-120`) merely *permits* a non-empty
output when `resume=True`; it never validates a prior tool-written manifest (same `source_fingerprint`,
same `tool_schema_version`) as §3.3 requires. With `--copy-only --resume` this lets payload files
interleave into an arbitrary non-empty tree, which `verify` would later flag as orphans (exit `30`).
Blocked on M3 (no fingerprint to validate). Acceptable for the scaffold; track with M3.

**L2 — Contract sidecars are excluded from checksums/orphan-scan by hard-coded names, not recorded.**
`verify` (`commands.py:376-384`) builds `exclude` from the three default contract filenames +
`manifest_path.name` (+ `report_path.name` if given) and never checksums the report/id-map. So:
(a) tampering with `migration-report.json` / `migration-id-map.json` is undetectable; and (b) a
`migrate` that wrote **custom-named** `--report`/`--id-map` into the output, later checked with
`verify` *without* `--report` (there is no `--id-map` on `verify`), would mis-flag those sidecars as
orphans → false exit `30`. This also technically violates §7's "every output file has a checksums
entry." Low because default-named runs are self-consistent (smoke confirmed). **Recommendation:** have
the manifest enumerate its own generated sidecars (or checksum report+id-map) instead of name-matching.

**L3 — `old_to_new_ids` is inlined, not `$ref`-ed (§7).**
`build_manifest` embeds the full empty id-map (`contracts.py:116` via `empty_id_map`), and copy-only
also writes the standalone `migration-id-map.json` (`commands.py:328-329`). Spec §7 shows
`"old_to_new_ids": {"$ref": "legacy_id_map.v1"}`. Inlining is arguably more self-contained but is a
shape deviation; reconcile the intended representation.

**L4 — `migrate` runs detection *outside* `source_guard`; `inspect` runs it *inside*.**
In `migrate`, `detect_sources(input_path)` executes at `commands.py:228`, before the guard is entered
at `commands.py:267`; `inspect` wraps detection in the guard (`commands.py:92-93`). Detection is
read-only (immutable RO SQLite URI, ZIP/JSON peeks), so there is no current impact, but the
defense-in-depth asymmetry means a future detector regression that touched the source would be caught
by `inspect` but not `migrate`. Cheap to make symmetric.

**L5 — Copy-only silently drops stat-failing files and empty directories.**
`_copy_only` (`commands.py:157-165`) skips snapshot entries with `size < 0`, which covers both
directory markers (`-1`) and unreadable/stat-failing files (`-2`, set in `policy.py:165`), and only
copies files — empty source directories are not recreated. A "faithful" copy can therefore omit an
unreadable file or an empty dir with no warning and no manifest record (so `verify` cannot notice).
Edge case; consider logging dropped/empty entries.

**L6 — Partial copy-only output into a pre-existing (empty) dir is not rolled back.**
`_run_copy_only` rolls back only when it created the output dir this run
(`commands.py:315,330-332`). If the output pre-existed and was empty (it passes
`assert_output_available`), a mid-copy failure leaves partial payload files behind. This honors §12
("never delete a pre-existing directory") but leaves inconsistent output; the user must clean up.

**L7 — Symlink handling in the integrity snapshot.**
`snapshot_tree` uses `os.walk(..., followlinks=False)` (`policy.py:149`) and `Path.stat()` (follows
symlinks). A file symlink whose *external* target changes mid-run trips a false
`SourceIntegrityError` (exit `70`); conversely, changes inside a symlinked *directory* target are not
walked and go undetected. Edge case for symlinked sources; document the assumption.

### TEST COVERAGE (Low)

**T1 — Detection branches with zero tests.** `test_detect.py` covers sqlite v2 / legacy-arrays /
forward sqlite / duckdb presence / `.n4a` (+ forward) / `.n4a.py` / loose-predictions / unknown /
missing. It does **not** exercise `native-results-v1` (`_detect_native_dir`, `commands`/`detect.py:168`),
`fs-runs-v2`, `fs-runs-legacy` (`detect.py:216-221`), or a forward-version native manifest — all live
code paths in the staged scaffold.

**T2 — Id-map file emission untested.** No test asserts `migration-id-map.json` is written by
copy-only or checks its `$id`/`entities` structure (`test_commands.py:159-164` checks manifest +
report + payload only). I confirmed emission manually.

**T3 — CLI exit-code coverage holes.** No end-to-end CLI test for exit `30` (verification_failed) or
`70` (source-integrity); I validated `30` manually and `70` is the same `ToolError → int(exit_code)`
mechanism. Exit `10` (`MIGRATED_WITH_WARNINGS`) and `STATUS_MIGRATED_WITH_WARNINGS` are **never
emitted** by any path in the scaffold (best-effort preserve-opaque lives in the deferred engine) — fine,
but worth noting they are currently unreachable.

**T4 — No assertion on real-output manifest content.** Tests check sidecar *existence* but not that a
produced manifest's `checksums` are `sha256:`-prefixed / `$id` / `target.kind` are correct
(`contracts` builders are unit-tested in isolation instead). I validated the produced content manually.

### PACKAGE METADATA (Low / Trivial)

**P1 — LICENSE is a placeholder summary.** `LICENSE:18-21` self-notes that the full canonical
CeCILL-2.1 + AGPL-3.0 texts must be dropped in "before the first public release." Fine for a scaffold;
a blocker for releasing the package. The IMP report's residual-risk list omits this.

**P2 — Deprecated `license` table form + license classifier.** `pyproject.toml:17` uses
`license = { text = "CeCILL-2.1 OR AGPL-3.0-or-later" }` together with the AGPL **License classifier**
(`:23`). Under newer setuptools / PEP 639 the SPDX-string form (`license = "…"`) is preferred and
license *classifiers* are deprecated; this can emit build warnings later. Harmless at the declared
`setuptools>=61` floor. (Also note there is no SPDX/classifier signal for CeCILL — expected, none exists.)

**P3 — Cosmetic metadata mismatches.** Author email `beurier@cirad.fr` vs maintainer
`gregory.beurier@cirad.fr` (`pyproject.toml:11,14`); README/LICENSE contact `nirs4all-admin@cirad.fr`;
`[project.urls]` point at `github.com/GBeurier/nirs4all-tools`, which does not exist yet (IMP report
acknowledges "no remote"). Reconcile before publishing.

---

## 3. What is solid (recorded so it is not re-litigated)

- **No-in-place policy** (`policy.py`) is the strongest part: RO-immutable SQLite URI
  (`mode=ro&immutable=1`, so no `-wal`/`-shm`, no locks), disjoint/alias/nesting refusal with correct
  sibling-prefix handling, `realpath` that tolerates a not-yet-created output, whole-tree
  `(size, mtime_ns)` guard that runs on the `finally` path and **outranks** an in-flight body
  exception (`policy.py:181-203`). All thoroughly unit-tested (`test_policy.py`, 16 cases).
- **Exit-code / error model** is clean and stable: `ExitCode` IntEnum `{0,10,20,30,40,70}`,
  one-to-one `ToolError` subclasses, structured JSON error on stderr (`cli.py:125-135`), argparse
  usage problems kept distinct at `2`.
- **Detection** is stat-first and never constructs a `WorkspaceStore`; forward-version refusal is wired
  for SQLite (`user_version>2`), `.n4a` (`bundle_format_version>1.0`), and native (`schema_version>2`);
  malformed sources degrade to `unknown` instead of raising (`detect.py:110-128,245-275`).
- **Contracts** (`contracts.py`) single-source the runtime facts correctly (verified in §1) and the
  report skeleton matches §8 field-for-field; `cause` vocab references CAP-004/RT-003 rather than
  reinventing it (`vocab.py`).
- **Packaging** basics are right: PEP 561 `py.typed` shipped via `package-data` + `Typing :: Typed`
  classifier, single-sourced dynamic version, `requires-python>=3.11` consistent with `datetime.UTC`
  usage, std-lib-only core with format readers behind extras, `target` extra satisfiable.

---

## 4. Residual risks

1. **Contract drift (M2/M3/L3):** durable `--copy-only` manifests are being emitted *now* with a
   non-spec entry shape, a `null` source fingerprint, and an inlined id-map. If users archive them
   before the contract is reconciled, the first real-engine release inherits two "v1" shapes.
2. **Misleading inert flags (M1):** `--verify`/`--strict`/`--trusted-load-joblib` accepted but
   ignored is a footgun for anyone scripting against the scaffold expecting verification/strictness.
3. **Verification is checksum-only (acknowledged):** `sqlite_integrity_check` and
   `array_checksum_coverage` are `"skipped (scaffold)"` (`commands.py:391-392`); the §13/G4
   shape-aware full-coverage guarantees are not yet real. Correctly scoped out, but G3–G5 cannot be
   claimed until the engine lands.
4. **`--resume` is effectively unvalidated (L1)** until M3 provides a fingerprint to check.
5. **Release blockers (P1, P3):** no remote, placeholder LICENSE text, aspirational URLs — must be
   resolved before this is treated as a publishable package (the IMP report flags the remote but not
   the LICENSE text).
6. **Symlink/edge-case fidelity (L5/L7):** faithful-copy and integrity-guard semantics around
   symlinks, empty dirs, and stat-failing files are untested and lightly handled.

---

## 5. Final disposition

**Approve for scaffold commit** in the `nirs4all-tools` repo as-is — the implemented surface is
correct, gate-green, and the no-in-place contract holds under direct test. **Do not tag/publish a
release** until P1/P3 and, ideally, M1–M3 are resolved. Recommended tracked follow-ups before the
first real transform slice:

1. Make inert flags explicit — wire `--verify` into copy-only or reject them with
   `unsupported_capability` (M1).
2. Populate `manifest.source.fingerprint` and align `input_inventory`/`output_inventory` entry shapes
   (or version) to the frozen contract (M2, M3); then implement the §3.3 `--resume` validation (L1).
3. Add detection tests for `native-results-v1` / `fs-runs-v2` / `fs-runs-legacy` / forward native
   manifest, plus an id-map-file emission test and a real-output manifest-content assertion (T1, T2,
   T4).
4. Drop in the full CeCILL-2.1 + AGPL-3.0 license texts and reconcile contact/URL metadata before
   publishing (P1, P3).

No source files were edited; nothing was staged, unstaged, or committed.
