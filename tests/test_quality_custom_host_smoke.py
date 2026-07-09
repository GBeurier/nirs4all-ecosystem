from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/e2e/run_quality_custom_host_smoke.py"
SPEC = importlib.util.spec_from_file_location("run_quality_custom_host_smoke", SCRIPT)
assert SPEC is not None
assert SPEC.loader is not None
smoke = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(smoke)


def test_ensure_local_ui_build_deps_runs_before_quality_install(
    tmp_path: Path,
    monkeypatch,
) -> None:
    workspace = tmp_path / "workspace"
    ui_root = workspace / "nirs4all-ui"
    ui_root.mkdir(parents=True)
    (ui_root / "package.json").write_text('{"scripts":{"build":"tsc"}}\n', encoding="utf-8")
    calls: list[tuple[list[str], Path]] = []

    def fake_run(cmd, *, cwd, env, timeout):
        calls.append((cmd, cwd))
        return subprocess.CompletedProcess(cmd, 0, stdout="ok")

    monkeypatch.setattr(smoke, "_run", fake_run)

    result = smoke._ensure_local_ui_build_deps(workspace, npm="/usr/bin/npm", env={}, install=True)

    assert result is not None
    assert calls == [(["/usr/bin/npm", "ci"], ui_root)]


def test_ensure_local_ui_build_deps_skips_when_tsc_exists(
    tmp_path: Path,
    monkeypatch,
) -> None:
    workspace = tmp_path / "workspace"
    ui_root = workspace / "nirs4all-ui"
    (ui_root / "node_modules/.bin").mkdir(parents=True)
    (ui_root / "package.json").write_text("{}\n", encoding="utf-8")
    (ui_root / "node_modules/.bin/tsc").write_text("#!/bin/sh\n", encoding="utf-8")

    def fail_run(*args, **kwargs):
        raise AssertionError("npm ci should not run when local tsc exists")

    monkeypatch.setattr(smoke, "_run", fail_run)

    assert smoke._ensure_local_ui_build_deps(workspace, npm="/usr/bin/npm", env={}, install=True) is None
