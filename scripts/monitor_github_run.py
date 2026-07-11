#!/usr/bin/env python3
"""Patient GitHub Actions run monitor for long NIRS4ALL validation jobs.

The monitor deliberately gives parity/e2e/release jobs a large wall-clock budget.
It never cancels GitHub runs. It exits early only when GitHub reports a terminal
run, a terminal failed job, or a clearly stale in-progress run.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


DEFAULT_POLL_SECONDS = 120
DEFAULT_MAX_WAIT_SECONDS = 6 * 60 * 60
DEFAULT_STALE_SECONDS = 2 * 60 * 60
TERMINAL_STATUSES = {"completed"}
FAILED_CONCLUSIONS = {
    "action_required",
    "cancelled",
    "failure",
    "skipped",
    "startup_failure",
    "timed_out",
}
SUCCESS_CONCLUSIONS = {"success", "neutral"}


class MonitorError(RuntimeError):
    """Configuration or execution error while monitoring a GitHub run."""


@dataclass(frozen=True)
class Decision:
    state: str
    exit_code: int
    reason: str


def parse_github_time(raw: str | None) -> float | None:
    if not raw:
        return None
    text = raw.strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        return datetime.fromisoformat(text).timestamp()
    except ValueError:
        return None


def failed_job_names(run: dict[str, Any]) -> list[str]:
    jobs = run.get("jobs") or []
    names: list[str] = []
    for job in jobs:
        if not isinstance(job, dict):
            continue
        conclusion = job.get("conclusion")
        status = job.get("status")
        if status in TERMINAL_STATUSES and conclusion in FAILED_CONCLUSIONS:
            names.append(str(job.get("name") or job.get("databaseId") or "unknown-job"))
    return names


def decide(run: dict[str, Any], *, now: float, started: float, max_wait: int, stale_after: int) -> Decision:
    status = str(run.get("status") or "").lower()
    conclusion = str(run.get("conclusion") or "").lower()
    url = str(run.get("url") or run.get("htmlUrl") or "")

    if status in TERMINAL_STATUSES:
        if conclusion in SUCCESS_CONCLUSIONS:
            return Decision("success", 0, f"run completed with conclusion={conclusion or 'success'} {url}".strip())
        return Decision("failed", 1, f"run completed with conclusion={conclusion or 'unknown'} {url}".strip())

    failed_jobs = failed_job_names(run)
    if failed_jobs:
        return Decision("failed", 1, f"terminal failed job(s): {', '.join(failed_jobs)} {url}".strip())

    if now - started > max_wait:
        return Decision("timeout", 124, f"monitor budget exceeded after {max_wait}s {url}".strip())

    updated = parse_github_time(run.get("updatedAt") or run.get("updated_at"))
    if updated is not None and now - updated > stale_after:
        stale_for = int(now - updated)
        return Decision("stale", 124, f"no GitHub run update for {stale_for}s (threshold {stale_after}s) {url}".strip())

    return Decision("running", 0, f"status={status or 'unknown'} conclusion={conclusion or '-'}")


def gh_run_view(repo: str, run_id: str) -> dict[str, Any]:
    cmd = [
        "gh",
        "run",
        "view",
        run_id,
        "--repo",
        repo,
        "--json",
        "conclusion,createdAt,databaseId,displayTitle,event,headBranch,headSha,jobs,name,status,updatedAt,url,workflowName",
    ]
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise MonitorError(proc.stderr.strip() or f"`{' '.join(cmd)}` failed with {proc.returncode}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise MonitorError(f"invalid gh JSON: {exc}") from exc


def monitor(repo: str, run_id: str, *, poll: int, max_wait: int, stale_after: int, once: bool) -> int:
    started = time.time()
    last_summary = ""
    while True:
        run = gh_run_view(repo, run_id)
        now = time.time()
        decision = decide(run, now=now, started=started, max_wait=max_wait, stale_after=stale_after)
        summary = (
            f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} "
            f"repo={repo} run={run_id} {decision.reason}"
        )
        if summary != last_summary:
            print(summary, flush=True)
            last_summary = summary
        if decision.state != "running" or once:
            return decision.exit_code
        time.sleep(poll)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="GitHub repo slug, e.g. GBeurier/nirs4all")
    parser.add_argument("--run-id", required=True, help="GitHub Actions run id/database id")
    parser.add_argument("--poll", type=positive_int, default=DEFAULT_POLL_SECONDS, help="Poll interval in seconds.")
    parser.add_argument(
        "--max-wait",
        type=positive_int,
        default=DEFAULT_MAX_WAIT_SECONDS,
        help="Maximum local wait time in seconds; the GitHub run is not cancelled.",
    )
    parser.add_argument(
        "--stale-after",
        type=positive_int,
        default=DEFAULT_STALE_SECONDS,
        help="Fail only when an in-progress run has no GitHub updatedAt movement for this many seconds.",
    )
    parser.add_argument("--once", action="store_true", help="Inspect once and exit without sleeping.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return monitor(
            args.repo,
            args.run_id,
            poll=args.poll,
            max_wait=args.max_wait,
            stale_after=args.stale_after,
            once=args.once,
        )
    except MonitorError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
