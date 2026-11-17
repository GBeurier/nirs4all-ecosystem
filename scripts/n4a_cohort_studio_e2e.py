#!/usr/bin/env python3
"""Drive one real Studio run on a candidate cohort: import a multi-target dataset with
missing values and train one target to completion.

The sidecar is the cohort-built binary, the scientific host is the cohort Python
environment, the document adapters are staged from the Studio source with
Studio's own script, and libn4m is the cohort native library. The requests are
the renderer's own calls (as in Studio's ``scripts/smoke-archive-standalone.cjs``).
Only names, counts and statuses are printed, never data values.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

TARGETS = ("protein", "moisture", "grade")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class Sidecar:
    def __init__(self, base: str) -> None:
        self.base = base

    def call(self, route: str, body: object | None = None, timeout: float = 120) -> tuple[int, object]:
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(self.base + "/api" + route, data=data, method="GET" if body is None else "POST",
                                         headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status, json.loads(response.read() or b"null")
        except urllib.error.HTTPError as error:
            text = error.read().decode("utf-8", "replace")
            try:
                return error.code, json.loads(text)
            except ValueError:
                return error.code, text

    def ok(self, route: str, body: object | None = None) -> dict:
        status, payload = self.call(route, body)
        if status not in (200, 202) or not isinstance(payload, dict):
            raise SystemExit(f"FAIL {route}: HTTP {status}: {json.dumps(payload)[:1500]}")
        return payload


def write_dataset(directory: Path) -> dict[str, int]:
    """Synthetic spectra with three targets; two of them have missing values."""
    directory.mkdir(parents=True)
    wavelengths = [1000 + 10 * i for i in range(60)]
    spectra, targets = [";".join(map(str, wavelengths))], [";".join(TARGETS)]
    missing = {name: 0 for name in TARGETS}
    for index in range(48):
        a, b = index / 11.0, math.sin(index / 3.0)
        row = [a * math.exp(-((w - 1200) / 120.0) ** 2) + b * math.exp(-((w - 1450) / 90.0) ** 2) + 0.01 * ((index * 7 + j) % 5)
               for j, w in enumerate(wavelengths)]
        spectra.append(";".join(f"{v:.6f}" for v in row))
        values = {"protein": f"{2.0 * a + 0.5 * b:.5f}", "moisture": f"{1.0 - a + b:.5f}", "grade": f"{a * b:.5f}"}
        if index % 9 == 4:
            values["protein"] = ""
        if index % 7 == 2:
            values["moisture"] = "NA"
        for name in TARGETS:
            missing[name] += values[name] in ("", "NA")
        targets.append(";".join(values[name] for name in TARGETS))
    (directory / "Xtrain.csv").write_text("\n".join(spectra) + "\n", encoding="utf-8")
    (directory / "Ytrain.csv").write_text("\n".join(targets) + "\n", encoding="utf-8")
    return missing


RESULT_COUNTS = """
import glob, json, sys
import polars as pl
runs = sorted(glob.glob(sys.argv[1] + "/native_results/*/predictions.parquet"))
frame = pl.read_parquet(runs[-1])
out = {}
for row in frame.iter_rows(named=True):
    ids = row["sample_ids"] or row["sample_indices"] or []
    out[f"{row['partition']}:{row['fold_id']}"] = len(ids)
print(json.dumps({"runs": len(runs), "rows": out}))
"""


def check_results(python: str, workspace: Path, samples: int, missing: int) -> None:
    """The run's sample accounting: train on the samples with a value, predict the others."""
    proc = subprocess.run([python, "-c", RESULT_COUNTS, str(workspace)], check=True, capture_output=True, text=True)
    counts = json.loads(proc.stdout)["rows"]
    print(f"result sample counts: {counts}")
    expected = {"train:final": samples - missing, "prediction:final": missing}
    wrong = {key: counts.get(key) for key, value in expected.items() if counts.get(key) != value}
    folds = sum(n for key, n in counts.items() if key.startswith("val:") and key.split(":")[1].isdigit())
    if wrong or folds != samples - missing:
        raise SystemExit(f"FAIL result accounting: expected {expected} and {samples - missing} validation samples over folds, got {counts}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--sidecar", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--studio-src", required=True)
    parser.add_argument("--libn4m", required=True)
    parser.add_argument("--node", required=True)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--target", default="protein", help="the target column to train")
    parser.add_argument("--timeout", type=float, default=900)
    args = parser.parse_args()

    work = Path(args.work_dir)
    studio = Path(args.studio_src)
    sidecar_bin = Path(args.sidecar)
    if not sidecar_bin.is_file():
        raise SystemExit(f"FAIL sidecar binary missing: {sidecar_bin}")
    adapters = work / "adapters"
    subprocess.run([args.node, "scripts/studio-document-adapters.cjs", "--install", str(adapters)], cwd=studio, check=True)
    print(f"adapters staged: {sorted(p.name for p in adapters.iterdir())}")

    profile = work / "profile"
    for name in ("config", "portable", "home"):
        (profile / name).mkdir(parents=True, exist_ok=True)
    site = subprocess.run([args.python, "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
                          check=True, capture_output=True, text=True).stdout.strip()
    version = json.loads((studio / "package.json").read_text(encoding="utf-8"))["version"]
    port = free_port()
    # Studio selects libn4m for Rust only; its Python host keeps the Methods wheels' own library.
    env = {k: v for k, v in os.environ.items() if k not in ("NIRS4ALL_STUDIO_SESSION_TOKEN", "N4M_LIB_PATH", "N4M_EXPECTED_LIBRARY_SHA256")}
    env.update({
        "HOME": str(profile / "home"),
        "NIRS4ALL_CONFIG": str(profile / "config"),
        "NIRS4ALL_PORTABLE_ROOT": str(profile / "portable"),
        "NIRS4ALL_PYTHON_PLUGIN_HOST": args.python,
        "NIRS4ALL_PYTHON_PLUGIN_SITE_PACKAGES": site,
        "NIRS4ALL_STUDIO_ADAPTERS_DIR": str(adapters),
        "NIRS4ALL_SCIENTIFIC_EXECUTOR": "cpython-stdio-v1",
        "NIRS4ALL_APP_VERSION": version,
        "N4M_LIBRARY_PATH": args.libn4m,
        "SENTRY_DSN": "",
    })
    log_path = work / "sidecar.log"
    with log_path.open("wb") as log:
        process = subprocess.Popen([str(sidecar_bin), "--host", "127.0.0.1", "--port", str(port)], env=env,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        return drive(Sidecar(f"http://127.0.0.1:{port}"), work, args, process, log_path)
    finally:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=20)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            os.killpg(process.pid, signal.SIGKILL)


def drive(api: Sidecar, work: Path, args: argparse.Namespace, process: subprocess.Popen, log_path: Path) -> int:
    deadline = time.time() + 240
    readiness: object = None
    while time.time() < deadline:
        if process.poll() is not None:
            raise SystemExit(f"FAIL sidecar exited ({process.returncode}); log tail:\n{log_path.read_text(errors='replace')[-3000:]}")
        try:
            status, readiness = api.call("/system/readiness", timeout=5)
            if status == 200 and isinstance(readiness, dict) and readiness.get("ml_ready") is True:
                break
        except OSError:
            pass
        time.sleep(1)
    else:
        raise SystemExit(f"FAIL scientific host not ready: {json.dumps(readiness)[:1500]}\n{log_path.read_text(errors='replace')[-3000:]}")
    print("sidecar ready: ml_ready=true")

    workspace = work / "workspace"
    api.ok("/workspace/create", {"path": str(workspace), "name": "Cohort e2e", "create_dir": True})
    api.ok("/workspace/select", {"path": str(workspace)})
    data = work / "data"
    missing = write_dataset(data)
    # The wizard's own declaration: every target column, the default one and its task.
    targets = [{"column": name, "type": "regression", "is_default": name == TARGETS[0]} for name in TARGETS]
    linked = api.ok("/datasets/link", {"path": str(data), "config": {
        "name": "Cohort multi-target NA", "delimiter": ";", "decimal_separator": ".", "has_header": True, "na_policy": "auto",
        "files": [{"path": "Xtrain.csv", "type": "X", "split": "train"}, {"path": "Ytrain.csv", "type": "Y", "split": "train"}],
        "targets": targets, "default_target": TARGETS[0], "task_type": "regression",
        "target_selection": {"selected_targets": list(TARGETS), "default_target": TARGETS[0],
                             "task_by_target": {name: "regression" for name in TARGETS}},
    }})
    dataset = linked.get("dataset") or {}
    reported = {t.get("column"): t.get("missing_count") for t in dataset.get("targets") or []}
    print(f"dataset linked: samples={dataset.get('num_samples')} targets={sorted(reported)} missing={reported}")
    if linked.get("success") is not True or set(reported) != set(TARGETS):
        raise SystemExit(f"FAIL dataset import: {json.dumps(linked)[:2000]}")
    if any(reported[name] != missing[name] for name in TARGETS):
        raise SystemExit(f"FAIL missing-value counts differ: expected {missing}, Studio reports {reported}")

    imported = api.ok("/pipelines/import", {"payload": {"name": "Cohort PLS", "pipeline": [
        {"class": "sklearn.preprocessing.StandardScaler"},
        {"class": "sklearn.model_selection.KFold", "params": {"n_splits": 3}},
        {"class": "sklearn.cross_decomposition.PLSRegression", "params": {"n_components": 3}},
    ]}})
    dataset_id, pipeline = dataset["id"], imported["pipeline"]["id"]
    pair, name = f"{dataset_id}::{pipeline}", "Cohort e2e"
    submitted = api.ok("/runs/run-groups", {
        "legacyConfig": {"name": name, "dataset_ids": [dataset_id], "pipeline_ids": [pipeline], "execution_backend": "local-python",
                         "engine": "dag-ml", "allow_fallback": False, "missing_target_policy": "predict",
                         "target_by_dataset": {dataset_id: args.target}},
        "manifest": {"version": "studio.native-launch-payload.v1", "legacyExperimentName": name, "legacyDatasetCount": 1,
                     "legacyPipelineCount": 1, "strictCampaignCount": 1, "skippedRunCount": 0, "sourceRunIds": [pair], "skippedRunIds": []},
        "strictCampaignSpecs": {"splitSpecs": [{"id": f"single-pair:{pair}", "sourceRunId": pair, "sourceDatasetId": dataset_id,
            "sourcePipelineId": pipeline, "campaign": {"name": name, "mode": "paired_by_index", "executionBackend": "local-python",
                "datasets": [{"id": dataset_id, "name": name, "splitGroupBy": None}],
                "pipelines": [{"id": pipeline, "name": "Cohort PLS", "source": "saved"}],
                "runMatrix": [{"id": pair, "datasetId": dataset_id, "pipelineId": pipeline, "datasetIndex": 0, "pipelineIndex": 0,
                               "splitGroupBy": None}]}}],
            "skippedRunIds": []},
    })
    job_id = submitted.get("job_id") or submitted.get("run_id")
    print(f"run submitted: target={args.target} job={job_id}")
    deadline = time.time() + args.timeout
    job: dict = {}
    while time.time() < deadline:
        job = api.ok(f"/training/{job_id}")
        if job.get("status") in ("completed", "failed", "error", "cancelled"):
            break
        time.sleep(1)
    status = job.get("status")
    print(f"run finished: status={status} progress={job.get('progress')}")
    if status != "completed":
        raise SystemExit(f"FAIL run did not complete: {json.dumps(job)[:4000]}")
    check_results(args.python, work / "workspace", samples=dataset["num_samples"], missing=missing[args.target])
    print("PASS Studio imported a multi-target dataset with missing values and trained one target to completion")
    return 0


if __name__ == "__main__":
    sys.exit(main())
