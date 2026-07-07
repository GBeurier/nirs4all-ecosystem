from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]


def _load_runner() -> ModuleType:
    path = ROOT / "scripts" / "n4a_cutover_gates.py"
    spec = importlib.util.spec_from_file_location("n4a_cutover_gates", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_minimal_nirs4all(root: Path, *, default_engine: str = "dag-ml", fallback_count: int = 0) -> None:
    (root / "nirs4all" / "pipeline").mkdir(parents=True)
    (root / "nirs4all" / "api").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "nirs4all" / "pipeline" / "engine.py").write_text(
        f'DEFAULT_ENGINE = "{default_engine}"\n',
        encoding="utf-8",
    )
    (root / "nirs4all" / "api" / "run.py").write_text(
        """
def run(*, allow_fallback=False):
    def _run_legacy():
        return "legacy"

    def _fallback(exc):
        if not allow_fallback:
            raise exc
        return _run_legacy()

    return "dag-ml"
""",
        encoding="utf-8",
    )
    (root / "nirs4all" / "api" / "result.py").write_text(
        '''
_DAGML_LEGACY_REFIT_COMPATIBILITY = "legacy-refit"

class RunResult:
    def _dagml_export_delegate(self):
        return None

    def export(self, output_path, *, compatibility=None):
        legacy_refit_compatibility = compatibility == _DAGML_LEGACY_REFIT_COMPATIBILITY
        if legacy_refit_compatibility:
            return self._dagml_export_delegate().export(output_path)
        raise RuntimeError("native artifacts required")

    def export_model(self, output_path, *, compatibility=None):
        legacy_refit_compatibility = compatibility == _DAGML_LEGACY_REFIT_COMPATIBILITY
        if legacy_refit_compatibility:
            return self._dagml_export_delegate().export_model(output_path)
        raise RuntimeError("native artifacts required")
''',
        encoding="utf-8",
    )
    (root / "docs" / "compatibility.json").write_text(
        f'{{"coverage_meter": {{"fallback": {fallback_count}, "expected_fallback_target": 0}}, "expected_fallback": []}}\n',
        encoding="utf-8",
    )


def test_nirs4all_cutover_state_accepts_post_w2j_contract(tmp_path: Path) -> None:
    runner = _load_runner()
    _write_minimal_nirs4all(tmp_path)

    checks = runner._check_nirs4all_cutover_state(tmp_path)

    assert {check["status"] for check in checks} == {"passed"}


def test_nirs4all_cutover_state_rejects_stale_default_and_fallback(tmp_path: Path) -> None:
    runner = _load_runner()
    _write_minimal_nirs4all(tmp_path, default_engine="legacy", fallback_count=1)

    checks = runner._check_nirs4all_cutover_state(tmp_path)
    failures = {check["id"] for check in checks if check["status"] == "failed"}

    assert "nirs4all.default_engine" in failures
    assert "nirs4all.coverage_meter.fallback_zero" in failures


def test_release_non_full_gates_promote_w2s_and_core_evidence() -> None:
    manifest = json.loads((ROOT / "docs" / "contracts" / "cutover" / "drop-gates.n4a.json").read_text(encoding="utf-8"))
    gates = {gate["id"]: gate for gate in manifest["gates"]}

    assert gates["installed_n4m_proof"]["required"] is True
    assert gates["installed_n4m_proof"]["cwd"] == "_worktrees/RC-v1-nirs4all-python"
    installed_command = " ".join(gates["installed_n4m_proof"]["command"])
    assert "timeout 1800 python3.11 scripts/prove_installed_n4m.py --install-deps" in installed_command
    assert "--dag-ml-path {workspace_root}/_worktrees/RC-v1-dagml" in installed_command
    assert "--dag-ml-data-path {workspace_root}/_worktrees/RC-v1-dmd" in installed_command

    assert gates["providers_local_sibling_release"]["required"] is True
    assert gates["providers_local_sibling_release"]["cwd"] == "_worktrees/RC-v1-providers"
    providers_command = " ".join(gates["providers_local_sibling_release"]["command"])
    assert "nirs4all_providers.local_release_gate" in providers_command
    assert "ln -s {workspace_root}/_worktrees/RC-v1-datasets" in providers_command
    assert "ln -s {workspace_root}/_worktrees/RC-v1-repository" in providers_command
    assert "--dependency-path {workspace_root}/_worktrees/RC-v1-io/src" in providers_command

    assert gates["core_v1_surfaces"]["required"] is True
    assert gates["core_v1_surfaces"]["cwd"] == "_worktrees/RC-v1-nirs4all-core"
    core_command = " ".join(gates["core_v1_surfaces"]["command"])
    assert "PATH=/home/delete/.nvm/versions/node/v22.21.1/bin:$PATH" in core_command
    assert "PYTHONPATH=bindings/python/src" in core_command
    assert "make test-v1-surfaces" in core_command


def test_cutover_gates_target_selected_rc_worktrees() -> None:
    manifest = json.loads((ROOT / "docs" / "contracts" / "cutover" / "drop-gates.n4a.json").read_text(encoding="utf-8"))
    serialized = json.dumps(manifest, sort_keys=True)

    assert "_worktrees/INT-" not in serialized
    assert "{workspace_root}/dag-ml" not in serialized
    assert "{workspace_root}/dag-ml-data" not in serialized
    assert '"cwd": "nirs4all-ecosystem"' not in serialized
    assert '"cwd": "nirs4all-tools"' not in serialized
    assert '"cwd": "nirs4all-lite"' not in serialized
    for expected in (
        "_worktrees/RC-v1-nirs4all-python",
        "_worktrees/RC-v1-studio",
        "_worktrees/RC-v1-web",
        "_worktrees/RC-v1-tools",
        "_worktrees/RC-v1-cluster",
        "_worktrees/RC-v1-providers",
        "_worktrees/RC-v1-dagml",
        "_worktrees/RC-v1-dmd",
        "_worktrees/RC-v1-nirs4all-core",
        "_worktrees/RC-v1-ecosystem",
    ):
        assert expected in serialized


def test_readiness_matrix_requires_promoted_release_gates() -> None:
    matrix = json.loads((ROOT / "docs" / "contracts" / "cutover" / "readiness-matrix.n4a.json").read_text(encoding="utf-8"))
    blockers = {blocker["id"]: blocker for blocker in matrix["blockers"]}

    expected = {
        "W2S-INSTALLED-N4M-001": "installed_n4m_proof",
        "PROV-READ-001": "providers_local_sibling_release",
        "CORE-V1-SURFACE-001": "core_v1_surfaces",
    }
    for blocker_id, gate_id in expected.items():
        blocker = blockers[blocker_id]
        assert blocker["required_for_cutover"] is True
        assert blocker["primary_gate_id"] == gate_id
        assert gate_id in blocker["gate_ids"]
