<#
Launch the first 10 nirs4all refactoring agents from Windows PowerShell.

Run from Windows, not from inside WSL:

  $script = (wsl.exe wslpath -w /home/delete/nirs4all/nirs4all-ecosystem/scripts/launch_refactor_agents.ps1).Trim()
  powershell.exe -ExecutionPolicy Bypass -File $script

Dry run:

  $script = (wsl.exe wslpath -w /home/delete/nirs4all/nirs4all-ecosystem/scripts/launch_refactor_agents.ps1).Trim()
  powershell.exe -ExecutionPolicy Bypass -File $script -DryRun -StaggerSeconds 0

The project is expected to live in WSL at /home/delete/nirs4all.
WSL windows start in /home/delete, load the user shell environment, then cd to
the project root for the agent.
Each agent opens in its own Windows PowerShell window and runs inside WSL.
#>

[CmdletBinding()]
param(
    [string]$WslRoot = "/home/delete/nirs4all",
    [string]$WslHome = "/home/delete",
    [string]$Distro = "",
    [string]$ClaudeModel = "opus",
    [string]$ClaudeEffort = "max",
    [string]$CodexModel = "gpt-5-codex",
    [int]$StaggerSeconds = 2,
    [switch]$PrepareOnly,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$promptFile = "$WslRoot/nirs4all-ecosystem/docs/PARALLEL_AGENT_PROMPT_PROGRAM.md"
$reportsDir = "$WslRoot/nirs4all-ecosystem/docs/agent_reports"
$launchersDir = "$WslRoot/nirs4all-ecosystem/docs/agent_launchers"

$agents = @(
    @{
        Id = "A0"
        Title = "A0-coordination"
        Backend = "claude"
        Start = "^## Prompt A0 "
        Stop = "^## Prompt A1 "
        Mode = "coordinator"
    },
    @{
        Id = "A2"
        Title = "A2-pyref"
        Backend = "claude"
        Start = "^## Prompt A2 "
        Stop = "^## Prompt A3 "
        Mode = "report"
    },
    @{
        Id = "A4"
        Title = "A4-controllers"
        Backend = "claude"
        Start = "^## Prompt A4 "
        Stop = "^## Prompt A5 "
        Mode = "report"
    },
    @{
        Id = "A6"
        Title = "A6-studio-ui"
        Backend = "claude"
        Start = "^## Prompt A6 "
        Stop = "^## Prompt A7 "
        Mode = "report"
    },
    @{
        Id = "A9"
        Title = "A9-lockstep"
        Backend = "claude"
        Start = "^## Prompt A9 "
        Stop = "^## Prompt A10 "
        Mode = "report"
    },
    @{
        Id = "A1"
        Title = "A1-preflight"
        Backend = "codex"
        Start = "^## Prompt A1 "
        Stop = "^## Prompt A2 "
        Mode = "report"
    },
    @{
        Id = "A3"
        Title = "A3-dagml"
        Backend = "codex"
        Start = "^## Prompt A3 "
        Stop = "^## Prompt A4 "
        Mode = "report"
    },
    @{
        Id = "A5"
        Title = "A5-methods"
        Backend = "codex"
        Start = "^## Prompt A5 "
        Stop = "^## Prompt A6 "
        Mode = "report"
    },
    @{
        Id = "A8"
        Title = "A8-migration"
        Backend = "codex"
        Start = "^## Prompt A8 "
        Stop = "^## Prompt A9 "
        Mode = "report"
    },
    @{
        Id = "A13"
        Title = "A13-core-release"
        Backend = "codex"
        Start = "^## Prompt A13 "
        Stop = "^## Prompt A14 "
        Mode = "report"
    }
)

function Quote-WslSingle {
    param([Parameter(Mandatory = $true)][string]$Value)
    return "'" + ($Value -replace "'", "'\''") + "'"
}

function Get-WslPrefixArgs {
    if ([string]::IsNullOrWhiteSpace($Distro)) {
        return @()
    }
    return @("-d", $Distro)
}

function Invoke-Wsl {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    & wsl.exe @((Get-WslPrefixArgs) + $Arguments)
}

function Convert-WslPathToWindows {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Invoke-Wsl -Arguments @("wslpath", "-w", $Path)).Trim()
}

function Write-WslTextFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content,
        [switch]$Executable
    )

    $normalizedPath = $Path.Replace("\", "/")
    $lastSlash = $normalizedPath.LastIndexOf("/")
    if ($lastSlash -lt 1) {
        throw "Cannot determine parent directory for WSL path: $Path"
    }
    $parent = $normalizedPath.Substring(0, $lastSlash)
    Invoke-Wsl -Arguments @("mkdir", "-p", $parent) | Out-Null
    $windowsPath = Convert-WslPathToWindows -Path $Path
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($windowsPath, ($Content -replace "`r`n", "`n"), $utf8NoBom)

    if ($Executable) {
        Invoke-Wsl -Arguments @("chmod", "+x", $Path) | Out-Null
    }
}

function New-BashCommand {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Agent
    )

    $agentId = $Agent.Id
    $agentTitle = $Agent.Title
    $backend = $Agent.Backend
    $startPattern = $Agent.Start
    $stopPattern = $Agent.Stop
    $mode = $Agent.Mode
    $reportFile = "$reportsDir/$agentId`_$agentTitle.md"
    $logFile = "$reportsDir/$agentId`_$agentTitle.log"
    $promptInputFile = "$reportsDir/$agentId`_$agentTitle.prompt.txt"

    $modeInstructions = if ($mode -eq "coordinator") {
@"
SESSION MODE:
- You are A0, the only agent allowed to edit PARALLEL_REFACTORING_SYNC.md during this multi-CLI run.
- Integrate other agents' reports from docs/agent_reports/ when they appear.
- Keep edits scoped to coordination docs unless the maintainer explicitly asks for implementation.
"@
    } else {
@"
SESSION MODE:
- Multi-CLI report mode. Do not edit PARALLEL_REFACTORING_SYNC.md and do not modify implementation code.
- Work read-only unless a dedicated report file is needed.
- Write your final report to $reportFile if practical, or print a handoff that A0 can integrate.
- If you find a blocker, record it in the report instead of changing shared contracts.
"@
    }

    $launcher = if ($backend -eq "claude" -and $mode -eq "coordinator") {
@"
claude --model $(Quote-WslSingle $ClaudeModel) --effort $(Quote-WslSingle $ClaudeEffort) --ax-screen-reader --name $(Quote-WslSingle $agentTitle) --allowedTools Bash Read Write Edit Glob Grep Task --add-dir $(Quote-WslSingle $WslRoot) < "`$PROMPT_INPUT_FILE"
"@
    } elseif ($backend -eq "claude") {
@"
set +e
claude -p --model $(Quote-WslSingle $ClaudeModel) --effort $(Quote-WslSingle $ClaudeEffort) --allowedTools Bash Read Glob Grep Task --add-dir $(Quote-WslSingle $WslRoot) < "`$PROMPT_INPUT_FILE" 2>&1 | tee $(Quote-WslSingle $logFile)
status=`${PIPESTATUS[0]}
cp $(Quote-WslSingle $logFile) $(Quote-WslSingle $reportFile) 2>/dev/null || true
exit `$status
"@
    } else {
@"
set +e
codex exec -C $(Quote-WslSingle $WslRoot) --skip-git-repo-check -m $(Quote-WslSingle $CodexModel) -s danger-full-access - < "`$PROMPT_INPUT_FILE" 2>&1 | tee $(Quote-WslSingle $logFile)
status=`${PIPESTATUS[0]}
cp $(Quote-WslSingle $logFile) $(Quote-WslSingle $reportFile) 2>/dev/null || true
exit `$status
"@
    }

@"
#!/usr/bin/env bash
set -euo pipefail

debug_shell() {
  cd $(Quote-WslSingle $WslHome) 2>/dev/null || cd "`$HOME" 2>/dev/null || true
  exec bash -l
}

cd $(Quote-WslSingle $WslHome) 2>/dev/null || cd "`$HOME"

# Load the user shell environment first. This is needed on this workstation
# because the Claude/Codex CLIs live in the user's home-level environment.
set +e +u
for profile in "`$HOME/.profile" "`$HOME/.bash_profile" "`$HOME/.bashrc"; do
  if [ -f "`$profile" ]; then
    # shellcheck disable=SC1090
    . "`$profile" >/dev/null 2>&1
  fi
done
set -euo pipefail

cd $(Quote-WslSingle $WslRoot)
mkdir -p $(Quote-WslSingle $reportsDir)

# Prefer WSL-local CLIs over Windows npm shims inherited through PATH.
export PATH="`$HOME/.local/bin:`$HOME/bin:`$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin:`$PATH"
hash -r

PROMPT_FILE=$(Quote-WslSingle $promptFile)
REPORT_FILE=$(Quote-WslSingle $reportFile)
LOG_FILE=$(Quote-WslSingle $logFile)
PROMPT_INPUT_FILE=$(Quote-WslSingle $promptInputFile)

if [ ! -f "`$PROMPT_FILE" ]; then
  echo "Prompt file not found: `$PROMPT_FILE" >&2
  debug_shell
fi

if ! command -v $backend >/dev/null 2>&1; then
  echo "$backend CLI not found in WSL PATH." >&2
  echo "PATH=`$PATH" >&2
  echo "Install/configure $backend inside WSL, then rerun this window command." >&2
  debug_shell
fi

BACKEND_PATH="`$(command -v $backend)"
if [[ "`$BACKEND_PATH" == /mnt/c/* ]]; then
  echo "Refusing to use Windows $backend shim from WSL: `$BACKEND_PATH" >&2
  echo "Install/use the WSL-local $backend CLI, or add it before /mnt/c paths in PATH." >&2
  echo "Current PATH=`$PATH" >&2
  debug_shell
fi

COMMON_RULES="`$(awk '
  /^## Regles communes/ {p=1}
  p && /^## Ordre de lancement rapide/ {exit}
  p {print}
' "`$PROMPT_FILE")"

AGENT_PROMPT="`$(awk -v start=$(Quote-WslSingle $startPattern) -v stop=$(Quote-WslSingle $stopPattern) '
  `$0 ~ start {p=1}
  p && `$0 ~ stop {exit}
  p {print}
' "`$PROMPT_FILE")"

if [ -z "`$AGENT_PROMPT" ]; then
  echo "Could not extract prompt for $agentId from `$PROMPT_FILE" >&2
  debug_shell
fi

read -r -d '' SESSION_MODE <<'EOF_SESSION_MODE' || true
$modeInstructions
EOF_SESSION_MODE

PROMPT="`$SESSION_MODE

`$COMMON_RULES

`$AGENT_PROMPT"

printf '%s\n' "`$PROMPT" > "`$PROMPT_INPUT_FILE"

echo "============================================================"
echo "Launching $agentId ($agentTitle) with $backend"
echo "WSL root: $WslRoot"
echo "Prompt file: `$PROMPT_FILE"
echo "Runtime prompt: `$PROMPT_INPUT_FILE"
echo "Report file: `$REPORT_FILE"
echo "Log file: `$LOG_FILE"
echo "============================================================"
echo

$launcher
"@
}

function Get-AgentLauncherPath {
    param([Parameter(Mandatory = $true)][hashtable]$Agent)
    return "$launchersDir/$($Agent.Id)-$($Agent.Title).sh"
}

function Prepare-AgentLauncher {
    param([Parameter(Mandatory = $true)][hashtable]$Agent)
    $launcherPath = Get-AgentLauncherPath -Agent $Agent
    $bashCommand = New-BashCommand -Agent $Agent
    Write-WslTextFile -Path $launcherPath -Content $bashCommand -Executable
    return $launcherPath
}

function Start-AgentWindow {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Agent
    )

    $title = "n4a-$($Agent.Title)"
    $launcherPath = if ($DryRun) {
        Get-AgentLauncherPath -Agent $Agent
    } else {
        Prepare-AgentLauncher -Agent $Agent
    }

    $distroArgs = if ([string]::IsNullOrWhiteSpace($Distro)) {
        ""
    } else {
        "-d `"$Distro`" "
    }

    $inner = @"
`$Host.UI.RawUI.WindowTitle = "$title"
Write-Host "Starting $title inside WSL..."
Write-Host "Launcher: $launcherPath"
& wsl.exe $distroArgs--cd "$WslHome" -- bash -lc "cd $(Quote-WslSingle $WslHome); bash $(Quote-WslSingle $launcherPath); status=`$?; echo; echo '$($Agent.Id) exited with status' `$status; echo 'Press Enter to close this WSL session...'; read -r _; exit `$status"
Write-Host "wsl.exe exited with code `$LASTEXITCODE"
"@

    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($inner))
    $args = @("-NoExit", "-EncodedCommand", $encoded)

    if ($DryRun) {
        Write-Host "Would launch $title ($($Agent.Backend)) via $launcherPath"
        return
    }

    Start-Process -FilePath "powershell.exe" -ArgumentList $args
}

Write-Host "Launching $($agents.Count) nirs4all refactoring agents."
Write-Host "WSL root: $WslRoot"
Write-Host "WSL home: $WslHome"
if (-not [string]::IsNullOrWhiteSpace($Distro)) {
    Write-Host "WSL distro: $Distro"
}
Write-Host

foreach ($agent in $agents) {
    if ($PrepareOnly) {
        $launcherPath = Prepare-AgentLauncher -Agent $agent
        Write-Host "Prepared $($agent.Id) at $launcherPath"
    } else {
        Start-AgentWindow -Agent $agent
    }
    if ($StaggerSeconds -gt 0) {
        Start-Sleep -Seconds $StaggerSeconds
    }
}

Write-Host
Write-Host "Done. A0 is the sync-board owner; other agents should report into docs/agent_reports/."
