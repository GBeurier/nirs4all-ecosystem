from __future__ import annotations

from scripts.monitor_github_run import decide, failed_job_names, parse_github_time


def test_decide_allows_long_running_active_run() -> None:
    run = {
        "status": "in_progress",
        "conclusion": None,
        "updatedAt": "2026-07-11T10:00:00Z",
        "jobs": [{"name": "full parity", "status": "in_progress", "conclusion": None}],
    }

    now = parse_github_time("2026-07-11T10:30:00Z") or 0
    decision = decide(run, now=now, started=now - 1_800, max_wait=21_600, stale_after=7_200)

    assert decision.state == "running"
    assert decision.exit_code == 0


def test_decide_fails_on_terminal_failed_job_without_waiting_for_whole_run() -> None:
    run = {
        "status": "in_progress",
        "conclusion": None,
        "updatedAt": "2026-07-11T10:00:00Z",
        "jobs": [
            {"name": "linux", "status": "completed", "conclusion": "success"},
            {"name": "windows", "status": "completed", "conclusion": "failure"},
        ],
    }

    now = parse_github_time("2026-07-11T10:01:00Z") or 0
    decision = decide(run, now=now, started=now - 120, max_wait=21_600, stale_after=7_200)

    assert decision.state == "failed"
    assert decision.exit_code == 1
    assert failed_job_names(run) == ["windows"]


def test_decide_marks_stale_only_after_large_quiet_window() -> None:
    run = {
        "status": "queued",
        "conclusion": None,
        "updatedAt": "2026-07-11T08:00:00Z",
        "jobs": [],
    }

    active_now = parse_github_time("2026-07-11T09:00:00Z") or 0
    stale_now = parse_github_time("2026-07-11T10:01:00Z") or 0
    active = decide(
        run,
        now=active_now,
        started=active_now - 600,
        max_wait=21_600,
        stale_after=7_200,
    )
    stale = decide(
        run,
        now=stale_now,
        started=stale_now - 600,
        max_wait=21_600,
        stale_after=7_200,
    )

    assert active.state == "running"
    assert stale.state == "stale"
    assert stale.exit_code == 124


def test_decide_reports_terminal_success_and_failure() -> None:
    success = decide(
        {"status": "completed", "conclusion": "success", "updatedAt": "2026-07-11T08:00:00Z"},
        now=1,
        started=0,
        max_wait=21_600,
        stale_after=7_200,
    )
    failure = decide(
        {"status": "completed", "conclusion": "timed_out", "updatedAt": "2026-07-11T08:00:00Z"},
        now=1,
        started=0,
        max_wait=21_600,
        stale_after=7_200,
    )

    assert success.state == "success"
    assert success.exit_code == 0
    assert failure.state == "failed"
    assert failure.exit_code == 1
