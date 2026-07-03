# Wave 4AI - Cluster GitGuardian Audit

Date: 2026-07-03

Scope:

- `nirs4all-cluster`
- Alert source: GitGuardian Generic CLI Option Secret on
  `GBeurier/nirs4all-cluster`, pushed 2026-07-02 09:41:03 UTC.
- Audit mode: read-only Codex subagent plus coordinator review.

Agent report:

- Local `CLAUDE.md` was read; no local `AGENTS.md` was found.
- No files were modified; `git status` stayed clean.

Findings:

- Primary scanner candidate was a CLI documentation/example value for
  `--principal` in the shape `name:token:roles`, previously present in
  `docs/cli-reference.md` and `nirs4all_cluster/cli.py`.
- Candidate appeared near the alert window on commit `1027e64` on main and on
  variant `8cb30d2` on RC.
- Earlier introductions were `6b200f4` and `6275b3c`; active refs were later
  neutralized by `16b4a2a` / `19384e2`, then `8bb991b` / `fb64314`, and finally
  by `eaf79a0` on main plus `ffeaf4b` on RC/tag.
- Secondary scanner candidate was an example-like `N4CLUSTER_TOKEN` value in
  `docs/operations.md`, removed by `e87d4a4` / `5715bf7`.

Current active-ref status:

- `HEAD`, `main`, `origin/main`, `rc/v1-full-refactor`,
  `origin/rc/v1-full-refactor`, and tag `n4a-v1-rc1-2026.07-refactor` no
  longer contain the suspicious literal example values.
- Active published heads remain:
  - main: `eaf79a0`
  - RC branch/tag: `ffeaf4b`
- Remaining appearances are on older local historical/refactor branches or old
  GitHub history/PR refs, not on the selected active heads.

Decision:

- Treat the alert as remediated placeholder/example exposure unless GitGuardian
  reveals a non-placeholder value.
- If any real deployment reused one of the exposed example values, rotate it
  out of band immediately.
- History purge/GitHub support is only necessary if a real credential was
  exposed or if the team wants to suppress residual alerts on historical/hidden
  PR refs.

Risks:

- The coordinator cannot prove from the scanner alert alone whether a user ever
  copied the placeholder into a real deployment.
- Hidden GitHub PR refs may keep stale examples even after active branch/tag
  cleanup.
