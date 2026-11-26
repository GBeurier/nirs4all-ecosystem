import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLANNER = ROOT / "scripts/n4a_artifact_graph.py"
GRAPH = ROOT / "docs/contracts/release/artifact-graph.n4a.json"


def run(*args):
    return subprocess.run(
        [sys.executable, str(PLANNER), *args], check=False, text=True, capture_output=True
    )


def plan(*args):
    result = run(*args)
    result.check_returncode()
    return json.loads(result.stdout)


def index(result, phase):
    return {row["artifact"]: row for row in result[phase]}


def test_io_browser_change_reassembles_browser_consumers_only():
    result = plan("--artifact", "io.browser")
    builds = index(result, "builds")
    assert set(builds) == {
        "io.browser", "io.demo", "preflight.site", "quali.site", "web.site", "web.offline-app"
    }
    assert builds["web.site"]["candidate_inputs"] == ["io.browser"]
    assert {"core.npm", "io.node-wasm", "methods.wasm"} <= set(builds["web.site"]["baseline_inputs"])
    assert not result["admission_review"]
    assert index(result, "refresh_after_promotion")["cockpit.site"]["if_promoted"] == [
        "preflight.site", "quali.site", "web.site"
    ]


def test_io_core_change_rebuilds_embedded_code_and_requalifies_runtime_consumers():
    result = plan("--artifact", "io.core-crate")
    builds = index(result, "builds")
    checks = index(result, "qualification")
    assert {"core.python-wheel", "core.native-wasm", "core.npm", "studio.sidecar",
            "studio.docker-image", "web.site", "quali.site", "datasets.wasm"} <= builds.keys()
    assert {"sdk.python-wheel", "papers.readers-check", "domains.python-bridge"} <= checks.keys()
    assert "papers.document-site" not in checks
    assert {"sdk.python-wheel", "papers.python-wheel", "papers.document-site", "domains.site",
            "dag.python-wheel", "methods.wasm", "studio.frontend"}.isdisjoint(builds)
    assert {"core.python-wheel", "io.python-wheel"} <= set(checks["sdk.python-wheel"]["candidate_inputs"])
    assert "sdk.python-wheel" in builds["studio.linux-installer"]["baseline_inputs"]
    assert {"io.browser", "core.npm"} <= set(builds["web.site"]["candidate_inputs"])
    assert {"candidate": "io.node-wasm", "consumer": "domains.site"} in result["admission_review"]
    seen = set()
    for entry in result["builds"]:
        assert set(entry["candidate_inputs"]) <= seen
        seen.add(entry["artifact"])


def test_preflight_rust_change_consumes_candidate_crate_in_domains():
    result = plan("--artifact", "preflight.rust-crates")
    builds = index(result, "builds")
    assert set(builds) == {
        "preflight.rust-crates", "preflight.python-wheel", "preflight.wasm", "preflight.site",
        "domains.rust", "domains.wasm", "domains.site"
    }
    assert builds["domains.wasm"]["candidate_inputs"] == ["preflight.rust-crates"]
    assert builds["domains.site"]["candidate_inputs"] == ["domains.wasm"]


def test_sdk_wheel_change_uses_existing_native_sidecar_and_retests_papers_reader():
    result = plan("--artifact", "sdk.python-wheel")
    builds = index(result, "builds")
    checks = index(result, "qualification")
    assert set(builds) == {
        "sdk.python-wheel", "studio.linux-installer", "studio.windows-installer", "studio.docker-image"
    }
    assert {"studio.macos-installer", "papers.readers-check", "tools.target-check"} <= checks.keys()
    assert "sdk.python-wheel" in checks["tools.target-check"]["candidate_inputs"]
    assert "studio.sidecar" in builds["studio.linux-installer"]["baseline_inputs"]


def test_full_qualification_covers_every_declared_repository():
    result = plan("--full")
    graph = json.loads(GRAPH.read_text())
    builds = index(result, "builds")
    checks = index(result, "qualification")
    assert set(result["roots"]) == graph["artifacts"].keys()
    assert all(not row["baseline_inputs"] for row in builds.values())
    assert graph["artifacts"].keys() == checks.keys() | {"cockpit.site"}
    assert "dag.shared-contract-check" in checks.keys() - builds.keys()


def test_repository_selection_runs_all_its_declared_outputs():
    result = plan("--repository", "nirs4all-papers")
    assert result["roots"] == ["papers.document-site", "papers.python-wheel", "papers.readers-check"]
    assert "papers.document-site" in index(result, "builds")


def test_declared_qualification_gate_can_run_on_baseline():
    result = plan("--artifact", "dag.shared-contract-check")
    assert not result["builds"]
    assert result["qualification"] == [{
        "artifact": "dag.shared-contract-check",
        "candidate_inputs": [],
        "baseline_inputs": ["dag.rust-crates", "dmd.rust-crates"],
    }]


@pytest.mark.parametrize("selection", ["--artifact", "--repository"])
def test_unknown_selection_is_refused(selection):
    result = run(selection, "typo")
    assert result.returncode == 2
    assert "unknown artifact or repository: typo" in result.stderr


def test_material_cycles_are_refused(tmp_path):
    graph = json.loads(GRAPH.read_text())
    graph["artifacts"]["io.core-crate"]["inputs"]["io.browser"] = "compile"
    path = tmp_path / "cycle.json"
    path.write_text(json.dumps(graph))
    result = run("--graph", str(path), "--full")
    assert result.returncode == 2
    assert "nodes are in a cycle" in result.stderr
