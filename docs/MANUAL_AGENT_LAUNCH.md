# Manual bypass launch for the first 10 agents

This file replaces the broken multi-window launcher.

Open WSL terminals manually. In each terminal, run the shared setup, then run
one agent command. All commands below use bypass / no-approval mode.

Important:

- A0 is the coordinator.
- Non-A0 agents should write reports under `docs/agent_reports/`.
- Do not let several agents edit `PARALLEL_REFACTORING_SYNC.md` at the same
  time. A0 integrates reports.
- Prompts are passed through files/stdin, not as long command-line arguments.

## Shared setup for every WSL terminal

Paste this at the top of every terminal:

```bash
cd /home/delete
source ~/.bashrc
cd /home/delete/nirs4all
mkdir -p nirs4all-ecosystem/docs/agent_reports
export PATH="$HOME/.local/bin:$HOME/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
hash -r
echo "claude=$(command -v claude || true)"
echo "codex=$(command -v codex || true)"
```

Expected output:

```text
claude=/home/delete/.local/bin/claude
codex=/home/delete/.local/bin/codex
```

If either path is under `/mnt/c/...`, stop and fix your WSL PATH.

## Prompt helper

Paste this function once in every terminal after the shared setup:

```bash
agent_prompt() {
  local agent="$1"
  local next="$2"
  local out="$3"
  local prompt_file="/home/delete/nirs4all/nirs4all-ecosystem/docs/PARALLEL_AGENT_PROMPT_PROGRAM.md"

  {
    cat <<'EOF'
MANUAL BYPASS MODE:
- You are launched manually in bypass/no-approval mode.
- A0 is the only agent allowed to edit PARALLEL_REFACTORING_SYNC.md.
- Non-A0 agents must not edit PARALLEL_REFACTORING_SYNC.md.
- Non-A0 agents should write findings under nirs4all-ecosystem/docs/agent_reports/.
- Work read-only unless this prompt explicitly asks for a report file.
- Do not modify implementation code unless a relevant DEC/LOCK is accepted.
- Use CodeGraph when useful, but verify directly with rg/sed/git.

EOF
    awk '
      /^## Regles communes/ {p=1}
      p && /^## Ordre de lancement rapide/ {exit}
      p {print}
    ' "$prompt_file"
    echo
    awk -v start="^## Prompt ${agent} " -v stop="^## Prompt ${next} " '
      $0 ~ start {p=1}
      p && $0 ~ stop {exit}
      p {print}
    ' "$prompt_file"
  } > "$out"

  test -s "$out" || {
    echo "Failed to create prompt: $out" >&2
    return 1
  }
  echo "Wrote $out"
}
```

## Recommended first wave

Launch these 10 agents:

Claude Code Opus max:

- `A0` coordination
- `A2` PYREF/oracle
- `A4` controllers/bindings
- `A6` Studio/UI extraction
- `A9` dag-ml/dag-ml-data lockstep

Codex:

- `A1` preflight/evidence
- `A3` dag-ml runtime/native coverage
- `A5` methods/n4m
- `A8` migration/tools
- `A13` core/release topology

## Terminal 1 - A0 Claude coordinator

```bash
agent_prompt A0 A1 nirs4all-ecosystem/docs/agent_reports/A0.prompt.txt
claude --model opus --effort max \
  --dangerously-skip-permissions \
  --ax-screen-reader \
  --name A0-coordination \
  --allowedTools Bash Read Write Edit Glob Grep Task \
  --add-dir /home/delete/nirs4all \
  < nirs4all-ecosystem/docs/agent_reports/A0.prompt.txt \
  2>&1 | tee nirs4all-ecosystem/docs/agent_reports/A0_coordination.md
```

## Terminal 2 - A2 Claude PYREF

```bash
agent_prompt A2 A3 nirs4all-ecosystem/docs/agent_reports/A2.prompt.txt
claude -p --model opus --effort max \
  --dangerously-skip-permissions \
  --allowedTools Bash Read Write Edit Glob Grep Task \
  --add-dir /home/delete/nirs4all \
  < nirs4all-ecosystem/docs/agent_reports/A2.prompt.txt \
  2>&1 | tee nirs4all-ecosystem/docs/agent_reports/A2_pyref.md
```

## Terminal 3 - A4 Claude controllers

```bash
agent_prompt A4 A5 nirs4all-ecosystem/docs/agent_reports/A4.prompt.txt
claude -p --model opus --effort max \
  --dangerously-skip-permissions \
  --allowedTools Bash Read Write Edit Glob Grep Task \
  --add-dir /home/delete/nirs4all \
  < nirs4all-ecosystem/docs/agent_reports/A4.prompt.txt \
  2>&1 | tee nirs4all-ecosystem/docs/agent_reports/A4_controllers.md
```

## Terminal 4 - A6 Claude Studio/UI

```bash
agent_prompt A6 A7 nirs4all-ecosystem/docs/agent_reports/A6.prompt.txt
claude -p --model opus --effort max \
  --dangerously-skip-permissions \
  --allowedTools Bash Read Write Edit Glob Grep Task \
  --add-dir /home/delete/nirs4all \
  < nirs4all-ecosystem/docs/agent_reports/A6.prompt.txt \
  2>&1 | tee nirs4all-ecosystem/docs/agent_reports/A6_studio_ui.md
```

## Terminal 5 - A9 Claude lockstep

```bash
agent_prompt A9 A10 nirs4all-ecosystem/docs/agent_reports/A9.prompt.txt
claude -p --model opus --effort max \
  --dangerously-skip-permissions \
  --allowedTools Bash Read Write Edit Glob Grep Task \
  --add-dir /home/delete/nirs4all \
  < nirs4all-ecosystem/docs/agent_reports/A9.prompt.txt \
  2>&1 | tee nirs4all-ecosystem/docs/agent_reports/A9_lockstep.md
```

## Terminal 6 - A1 Codex preflight

```bash
agent_prompt A1 A2 nirs4all-ecosystem/docs/agent_reports/A1.prompt.txt
codex exec -C /home/delete/nirs4all \
  --skip-git-repo-check \
  -m gpt-5-codex \
  --dangerously-bypass-approvals-and-sandbox \
  - < nirs4all-ecosystem/docs/agent_reports/A1.prompt.txt \
  2>&1 | tee nirs4all-ecosystem/docs/agent_reports/A1_preflight.md
```

## Terminal 7 - A3 Codex dag-ml runtime

```bash
agent_prompt A3 A4 nirs4all-ecosystem/docs/agent_reports/A3.prompt.txt
codex exec -C /home/delete/nirs4all \
  --skip-git-repo-check \
  -m gpt-5-codex \
  --dangerously-bypass-approvals-and-sandbox \
  - < nirs4all-ecosystem/docs/agent_reports/A3.prompt.txt \
  2>&1 | tee nirs4all-ecosystem/docs/agent_reports/A3_dagml.md
```

## Terminal 8 - A5 Codex methods/n4m

```bash
agent_prompt A5 A6 nirs4all-ecosystem/docs/agent_reports/A5.prompt.txt
codex exec -C /home/delete/nirs4all \
  --skip-git-repo-check \
  -m gpt-5-codex \
  --dangerously-bypass-approvals-and-sandbox \
  - < nirs4all-ecosystem/docs/agent_reports/A5.prompt.txt \
  2>&1 | tee nirs4all-ecosystem/docs/agent_reports/A5_methods.md
```

## Terminal 9 - A8 Codex migration/tools

```bash
agent_prompt A8 A9 nirs4all-ecosystem/docs/agent_reports/A8.prompt.txt
codex exec -C /home/delete/nirs4all \
  --skip-git-repo-check \
  -m gpt-5-codex \
  --dangerously-bypass-approvals-and-sandbox \
  - < nirs4all-ecosystem/docs/agent_reports/A8.prompt.txt \
  2>&1 | tee nirs4all-ecosystem/docs/agent_reports/A8_migration.md
```

## Terminal 10 - A13 Codex core/release

```bash
agent_prompt A13 A14 nirs4all-ecosystem/docs/agent_reports/A13.prompt.txt
codex exec -C /home/delete/nirs4all \
  --skip-git-repo-check \
  -m gpt-5-codex \
  --dangerously-bypass-approvals-and-sandbox \
  - < nirs4all-ecosystem/docs/agent_reports/A13.prompt.txt \
  2>&1 | tee nirs4all-ecosystem/docs/agent_reports/A13_core_release.md
```

## Monitor reports

```bash
watch -n 5 'ls -lh /home/delete/nirs4all/nirs4all-ecosystem/docs/agent_reports/*.md 2>/dev/null'
```

## After the first wave

Let A0 integrate the reports into:

```text
nirs4all-ecosystem/docs/PARALLEL_REFACTORING_SYNC.md
```

Then answer the P0 arbitrations in:

```text
nirs4all-ecosystem/docs/REFACTORING_DECISIONS_TO_ARBITRATE.md
```

Minimum P0 list:

- `ARB-001` default engine / legacy-DROP scope
- `ARB-002` PYREF 3-tier oracle
- `ARB-003` n4m in V1 or post-V1
- `ARB-004` ControllerManifest canonical surface
- `ARB-005` core vs runtime responsibility
- `ARB-006` nirs4all-tools migration
- `ARB-007` UI extraction strategy
- `ARB-008` dag-ml/dag-ml-data lockstep
- `ARB-009` branch/worktree strategy
