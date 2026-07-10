#!/usr/bin/env python3
"""Verify the public nirs4all-core MATLAB/Octave release parity gate."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "n4a.e2e.matlab_octave_release_gate.v1"
SCENARIO_ID = "e2e-formats-io-datasets-methods-language-bindings"
REPO = "GBeurier/nirs4all-core"
WORKFLOW = "release-matlab.yml"
TAG = "v0.3.11"
CORE_VERSION = "0.3.11"
ASSET_NAME = f"nirs4all-matlab-octave-{CORE_VERSION}.zip"


def _default_workspace_root() -> Path:
    env_root = os.environ.get("N4A_WORKSPACE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[3]


def _github_json(url: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "nirs4all-ecosystem-e2e",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {exc.code} for {url}: {body}") from exc


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _release() -> dict[str, Any]:
    return _github_json(f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}")


def _workflow_run() -> dict[str, Any]:
    data = _github_json(
        f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}/runs"
        f"?branch={TAG}&event=push&per_page=10"
    )
    runs = [
        run
        for run in data.get("workflow_runs", [])
        if run.get("head_branch") == TAG and run.get("event") == "push"
    ]
    if not runs:
        raise RuntimeError(f"no {WORKFLOW} push run found for {TAG}")
    successful = [run for run in runs if run.get("conclusion") == "success"]
    return successful[0] if successful else runs[0]


def verify(workspace_root: Path) -> dict[str, Any]:
    core_root = workspace_root / "nirs4all-core"
    workflow_path = core_root / ".github" / "workflows" / WORKFLOW
    makefile_path = core_root / "Makefile"
    workflow_text = _read(workflow_path)
    makefile_text = _read(makefile_path)

    release = _release()
    assets = release.get("assets") or []
    asset = next((item for item in assets if item.get("name") == ASSET_NAME), None)
    run = _workflow_run()

    local_workflow = {
        "strict_matlab_parity_job_declared": "strict-matlab-parity" in workflow_text,
        "octave_mex_build_declared": 'octave --quiet --eval "cd bindings/matlab; build_mex"' in workflow_text,
        "test_matlab_parity_declared": "make test-matlab-parity" in workflow_text,
        "release_asset_upload_declared": "nirs4all-matlab-octave-" in workflow_text,
        "no_continue_on_error": "continue-on-error" not in workflow_text,
    }
    core_makefile = {
        "test_matlab_parity_target_declared": re.search(r"^test-matlab-parity:", makefile_text, re.MULTILINE)
        is not None,
        "octave_invocation_declared": 'octave --quiet --eval "addpath(' in makefile_text,
        "python_oracle_env_declared": "NIRS4ALL_CORE_PARITY_ORACLE" in makefile_text,
        "methods_parity_env_declared": "NIRS4ALL_CORE_REQUIRE_METHODS_PARITY" in makefile_text,
    }
    status = (
        "passed"
        if release.get("tag_name") == TAG
        and asset is not None
        and run.get("conclusion") == "success"
        and all(local_workflow.values())
        and all(core_makefile.values())
        else "failed"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "scenario_id": SCENARIO_ID,
        "status": status,
        "release": {
            "repo": REPO,
            "tag": release.get("tag_name"),
            "url": release.get("html_url"),
            "asset_name": ASSET_NAME,
            "asset_present": asset is not None,
            "asset_digest": (asset or {}).get("digest"),
            "asset_size": (asset or {}).get("size"),
        },
        "workflow_run": {
            "workflow": WORKFLOW,
            "run_id": run.get("id"),
            "event": run.get("event"),
            "head_branch": run.get("head_branch"),
            "head_sha": run.get("head_sha"),
            "conclusion": run.get("conclusion"),
            "url": run.get("html_url"),
        },
        "local_workflow": local_workflow,
        "core_makefile": core_makefile,
        "parity_gate": {
            "runtime": "matlab_octave",
            "oracle": "python nirs4all portable parity fixtures",
            "workflow_declares_octave_build": local_workflow["octave_mex_build_declared"],
            "workflow_declares_strict_parity": local_workflow["test_matlab_parity_declared"],
            "release_asset_uploaded_after_gate": asset is not None and run.get("conclusion") == "success",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", type=Path, default=_default_workspace_root())
    parser.add_argument("--artifacts-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    output = args.artifacts_dir / "matlab-octave-release-gate.json"
    try:
        payload = verify(args.workspace_root.expanduser().resolve())
    except Exception as exc:  # noqa: BLE001 - write explicit failed evidence.
        payload = {
            "schema_version": SCHEMA_VERSION,
            "scenario_id": SCENARIO_ID,
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote failed MATLAB/Octave release-gate evidence to {output}", file=sys.stderr)
        raise

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {output}")
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
