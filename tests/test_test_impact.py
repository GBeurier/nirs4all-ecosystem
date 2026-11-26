import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from n4a_test_impact import environment, selection


def test_measured_change_selects_tests_and_unknown_changes_run_the_suite(tmp_path):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=tmp_path, text=True).strip()

    git("init", "-q")
    git("config", "user.name", "fixture")
    git("config", "user.email", "fixture@example.invalid")
    src = tmp_path / "src"
    src.mkdir()
    code = src / "engine.py"
    code.write_text("def result():\n    return 3\n")
    git("add", ".")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD")
    graph = {"schema": "n4a.pytest-impact/v2", "source": "src", "commit": base,
             "environment": environment(), "groups": [["tests/test_engine.py::test_result"]], "files": {"src/engine.py": {"2": 0}}}
    code.write_text("def result():\n    return 4\n")
    git("commit", "-qam", "change")
    assert selection(tmp_path, base, graph, "src")["tests"] == ["tests/test_engine.py::test_result"]
    assert selection(tmp_path, base, {**graph, "commit": "stale"}, "src")["scope"] == "suite"
    graph["files"]["src/engine.py"].clear()
    assert selection(tmp_path, base, graph, "src")["scope"] == "suite"
    (tmp_path / "config.toml").write_text("test = true")
    git("add", ".")
    git("commit", "-qm", "config")
    assert selection(tmp_path, base, graph, "src")["scope"] == "suite"


def test_full_suite_routes_keep_uninstrumented_owners_visible(tmp_path):
    path = tmp_path / "routes.json"
    subprocess.run([sys.executable, ROOT / "scripts/n4a_weekday_changes.py", "--all-test-routes",
                    "--output", path], check=True)
    routes = json.loads(path.read_text())
    assert "papers.readers-check" in routes["nirs4all-papers"]["owner-gates"]
    assert routes["nirs4all-tools"]["pytest:tools"] == ["tools.python-wheel"]
    assert routes["nirs4all-io"]["cargo:nirs4all-io-cli"] == ["io.native-cli"]
    assert len(routes) == 27
