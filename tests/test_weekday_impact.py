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
