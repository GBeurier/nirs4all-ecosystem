from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load_runner() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "scripts" / "n4a_cutover_gates.py"
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
