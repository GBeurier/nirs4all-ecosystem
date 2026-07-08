#!/usr/bin/env python3
"""Run the nirs4all-quality client-side WASM smoke and write E2E evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "n4a.e2e.quality_custom_host_smoke.v1"
SCENARIO_ID = "e2e-core-ui-custom-app-host"


def _default_workspace_root() -> Path:
    env_root = os.environ.get("N4A_WORKSPACE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[3]


def _node_path() -> str:
    candidates = [
        Path.home() / ".nvm/versions/node/v24.16.0/bin",
        Path.home() / ".nvm/versions/node/v22.21.1/bin",
    ]
    current = os.environ.get("PATH", "")
    prefix = [str(path) for path in candidates if path.exists()]
    return os.pathsep.join(prefix + [current])


def _run(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def _find_port() -> int:
    for port in range(4399, 4420):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError("no free local preview port found in 4399..4419")


def _wait_for_preview(url: str, *, timeout: int = 45) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except Exception as exc:  # noqa: BLE001 - surfaced after timeout
            last_error = exc
        time.sleep(0.5)
    raise RuntimeError(f"preview did not become ready at {url}: {last_error}")


def _terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=8)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _dist_summary(app_dir: Path) -> dict[str, Any]:
    dist = app_dir / "dist"
    files = [path for path in dist.rglob("*") if path.is_file()] if dist.exists() else []
    return {
        "dist_index_exists": (dist / "index.html").is_file(),
        "dist_asset_count": len(files),
        "wasm_asset_count": sum(1 for path in files if path.suffix == ".wasm"),
    }


def run_quality_smoke(workspace_root: Path, artifacts_dir: Path, *, install: bool) -> dict[str, Any]:
    quality_root = workspace_root / "nirs4all-quality"
    app_dir = quality_root / "app"
    if not app_dir.is_dir():
        raise RuntimeError(f"missing nirs4all-quality app directory: {app_dir}")

    env = os.environ.copy()
    env["PATH"] = _node_path()
    npm = shutil.which("npm", path=env["PATH"])
    if npm is None:
        raise RuntimeError("npm not found; install Node 22/24 or set PATH")

    install_result: subprocess.CompletedProcess[str] | None = None
    if install and not (app_dir / "node_modules").is_dir():
        install_result = _run([npm, "ci"], cwd=app_dir, env=env, timeout=240)
        if install_result.returncode != 0:
            raise RuntimeError(f"npm ci failed:\n{install_result.stdout}")

    build = _run([npm, "run", "build"], cwd=app_dir, env=env, timeout=180)
    if build.returncode != 0:
        raise RuntimeError(f"quality build failed:\n{build.stdout}")

    port = _find_port()
    url = f"http://127.0.0.1:{port}/"
    preview = subprocess.Popen(
        [npm, "run", "preview", "--", "--host", "127.0.0.1", "--port", str(port), "--strictPort"],
        cwd=app_dir,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        _wait_for_preview(url)
        smoke_env = env.copy()
        smoke_env["SMOKE_URL"] = url
        smoke_env.setdefault("CHROME", "/usr/bin/google-chrome")
        smoke = _run([npm, "run", "smoke"], cwd=app_dir, env=smoke_env, timeout=120)
    finally:
        _terminate(preview)

    stdout = smoke.stdout
    engine_match = re.search(r"engine label:\s*([A-Za-z0-9_-]+)", stdout)
    engine_label = engine_match.group(1) if engine_match else ""
    console_error_count = len(re.findall(r"\[error\]", stdout, flags=re.IGNORECASE))
    passed = smoke.returncode == 0
    real_wasm = "nirs4all-core-wasm" in stdout
    rmsep = "model report with RMSEP rendered" in stdout

    theme_css = _read_text(app_dir / "src/styles/index.css")
    package_json = json.loads(_read_text(app_dir / "package.json"))
    brand_dir = app_dir / "public/brand"
    required_brand_assets = ["icon.svg", "horizontal.svg", "horizontal-dark.svg", "og.png"]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "scenario_id": SCENARIO_ID,
        "status": "passed" if passed and real_wasm and rmsep else "failed",
        "repo": "nirs4all-quality",
        "app_name": package_json.get("name"),
        "app_version": package_json.get("version"),
        "client_side_only": True,
        "static_preview": True,
        "no_python_backend": True,
        "preview_url": url,
        "install_ran": install_result is not None,
        "build": _dist_summary(app_dir),
        "nirs4all_ui": {
            "theme_import": "nirs4all-ui/assets/theme.css" in theme_css,
            "lab_source_declared": "nirs4all-ui/src/lab" in theme_css,
            "brand_assets_present": all((brand_dir / name).is_file() for name in required_brand_assets),
        },
        "wasm_smoke": {
            "executed": passed,
            "engine_label": engine_label,
            "nirs4all_core_wasm": real_wasm,
            "rmsep_rendered": rmsep,
            "console_error_count": console_error_count,
        },
    }
    if payload["status"] != "passed":
        payload["smoke_output_tail"] = stdout[-4000:]
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", type=Path, default=_default_workspace_root())
    parser.add_argument("--artifacts-dir", type=Path, required=True)
    parser.add_argument("--no-install", action="store_true")
    args = parser.parse_args(argv)

    output = args.artifacts_dir / "custom-app-host" / "custom-host-quality-smoke.json"
    try:
        payload = run_quality_smoke(
            args.workspace_root.expanduser().resolve(),
            args.artifacts_dir.expanduser().resolve(),
            install=not args.no_install,
        )
    except Exception as exc:  # noqa: BLE001 - preserve failure evidence
        payload = {
            "schema_version": SCHEMA_VERSION,
            "scenario_id": SCENARIO_ID,
            "status": "failed",
            "repo": "nirs4all-quality",
            "error": str(exc),
        }
        _write_json(output, payload)
        print(f"wrote failed evidence to {output}", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1
    _write_json(output, payload)
    print(f"wrote {output}")
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
