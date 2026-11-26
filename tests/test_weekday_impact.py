import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from n4a_artifact_graph import DEFAULT_GRAPH, load_graph, plan
from n4a_weekday_changes import classify, comparison_paths, load_rules, repositories

ARTIFACTS, ORDER = load_graph(DEFAULT_GRAPH)
RULES = load_rules(ARTIFACTS)


def test_every_inventoried_repository_can_be_classified():
    reviewed = json.loads(DEFAULT_GRAPH.read_text())["reviewed_sources"]
    assert set(repositories()) | {"nirs4all-server"} == reviewed.keys()
    for repo in reviewed:
        roots, scope = classify(ARTIFACTS, RULES, repo, ["new-package/Cargo.toml"])
        assert roots == {key for key, value in ARTIFACTS.items() if value["repository"] == repo}
        assert scope == "repository"


def test_domains_receives_preflight_but_papers_content_stays_local():
    roots, scope = classify(ARTIFACTS, RULES, "nirs4all-preflight", ["crates/nirs4all-preflight-core/src/lib.rs"])
    assert scope == "paths"
    result = plan(ARTIFACTS, ORDER, roots, set(), full=False)
    assert "domains.wasm" in {r["artifact"] for r in result["builds"]}
    roots, _ = classify(ARTIFACTS, RULES, "nirs4all-papers", ["papers/new-paper/data/table.csv"])
    result = plan(ARTIFACTS, ORDER, roots, set(), full=False)
    assert [r["artifact"] for r in result["builds"]] == ["papers.document-site"]


def test_shared_binding_and_unknown_input():
    paths = ["bindings/wasm/src/lib.rs"]
    assert classify(ARTIFACTS, RULES, "nirs4all-io", paths)[0] == {"io.node-wasm", "io.browser"}
    assert classify(ARTIFACTS, RULES, "nirs4all-io", paths + ["build.rs"])[1] == "repository"


def test_compare_handles_rename_and_ambiguous_history():
    entry = {"filename": "after", "previous_filename": "before"}
    assert comparison_paths({"status": "ahead", "files": [entry]}) == ["after", "before"]
    assert comparison_paths({"status": "ahead", "files": [entry] * 300}) is None
    assert comparison_paths({"status": "diverged", "files": [entry]}) is None


def test_local_diff_uses_both_sides_of_a_move(tmp_path):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=tmp_path, text=True).strip()
    git("init", "--quiet")
    git("config", "user.email", "fixture@example.invalid")
    git("config", "user.name", "fixture")
    f = tmp_path / "crates/nirs4all-io-core/src/fixture.rs"
    f.parent.mkdir(parents=True)
    f.write_text("fixture")
    git("add", ".")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD")
    target = tmp_path / "bindings/wasm/src/fixture.rs"
    target.parent.mkdir(parents=True)
    f.rename(target)
    git("add", "-A")
    git("commit", "-qm", "move")
    out = tmp_path / "impact.json"
    subprocess.run([sys.executable, ROOT / "scripts/n4a_weekday_changes.py", "--checkout", tmp_path,
                    "--repository", "nirs4all-io", "--base", base, "--head", git("rev-parse", "HEAD"),
                    "--output", out], check=True)
    assert set(json.loads(out.read_text())["plan"]["roots"]) == {"io.core-crate", "io.browser", "io.node-wasm"}


def test_crate_graph_crosses_repository_with_workspace_and_renamed_target_dependency():
    from n4a_crate_impact import affected_crates

    origins = {"owner": "Org/owner", "app": "Org/app"}
    inventory = {
        "owner": {
            "Cargo.toml": {"workspace": {}},
            "crates/core/Cargo.toml": {"package": {"name": "owner-core"}},
            "crates/facade/Cargo.toml": {"package": {"name": "owner-facade"},
                                         "dependencies": {"engine": {"package": "owner-core", "path": "../core"}}},
            "crates/cli/Cargo.toml": {"package": {"name": "owner-cli"}},
        },
        "app": {
            "Cargo.toml": {"workspace": {"dependencies": {"bridge": {"package": "owner-facade", "version": "0.3"}}}},
            "native/Cargo.toml": {"package": {"name": "app-native"}, "target": {
                "cfg(windows)": {"build-dependencies": {"bridge": {"workspace": True}}}}},
            "other/Cargo.toml": {"package": {"name": "app-other"}, "dependencies": {
                "owner-core": {"git": "https://github.com/SomeoneElse/owner"}}},
        },
    }
    result = affected_crates(inventory, origins, {"owner": (["crates/core/src/lib.rs"], "repository")})
    assert [v["name"] for v in result["crates"].values()] == ["app-native", "owner-core", "owner-facade"]
    assert result["roots"] == ["owner/crates/core/Cargo.toml"]
    result = affected_crates(inventory, origins, {"owner": (["Cargo.toml"], "repository")})
    assert len(result["roots"]) == 3


def test_cli_source_selects_only_the_product_that_ships_it():
    for repo, crate, artifact in [
        ("nirs4all-io", "nirs4all-io-cli", "io.native-cli"),
        ("dag-ml", "dag-ml-cli", "dag.native-cli"),
        ("nirs4all-domains", "nirs4all-domains-cli", "domains.native-cli"),
    ]:
        roots, scope = classify(ARTIFACTS, RULES, repo, [f"crates/{crate}/src/main.rs"])
        result = plan(ARTIFACTS, ORDER, roots, set(), full=False)
        assert scope == "paths"
        assert [row["artifact"] for row in result["builds"]] == [artifact]
