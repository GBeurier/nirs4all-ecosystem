#!/usr/bin/env python3
"""Export a catalog/provider dataset into the CSV shape used by Web repository smokes."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_DATASET_ID = "web_repository_provider_fixture"


def _descriptor_payload(descriptor: Any) -> dict[str, Any]:
    if hasattr(descriptor, "model_dump"):
        return descriptor.model_dump(mode="json", exclude_none=True)
    return descriptor.dict(exclude_none=True)


def _sha256(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"file": path.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"cannot serialize {type(value).__name__}")


def _write_matrix(path: Path, wavelengths: np.ndarray, x: np.ndarray) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([f"{float(value):.12g}" for value in wavelengths])
        for row in x:
            writer.writerow([f"{float(value):.12g}" for value in row])


def _write_target(path: Path, target_name: str, values: list[float]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([target_name])
        for value in values:
            writer.writerow([f"{float(value):.12g}"])


def _write_metadata(path: Path, *, dataset_id: str, source: str, sample_ids: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sample_id", "dataset_id", "source_id", "source_row"])
        writer.writeheader()
        for index, sample_id in enumerate(sample_ids):
            writer.writerow(
                {
                    "sample_id": sample_id,
                    "dataset_id": dataset_id,
                    "source_id": source,
                    "source_row": index,
                }
            )


def _deterministic_spectra(rows: int, cols: int) -> tuple[np.ndarray, np.ndarray, list[float]]:
    wavelengths = np.arange(350, 350 + cols, dtype=np.float64)
    x = np.empty((rows, cols), dtype=np.float64)
    y: list[float] = []
    for row_index in range(rows):
        phase = row_index / 7.0
        target = 0.0
        for col_index, wavelength in enumerate(wavelengths):
            value = (
                0.35 * math.sin(phase + col_index / 19.0)
                + 0.22 * math.cos(row_index / 9.0 - col_index / 31.0)
                + 0.0007 * wavelength
                + ((row_index % 5) - 2.0) * 0.018
                + 0.015 * math.sin(((row_index + 3) * (col_index + 5)) / 41.0)
            )
            x[row_index, col_index] = value
            target += value * (0.003 if col_index < cols / 2 else -0.0018)
        y.append(70.0 + target + 0.12 * math.sin(row_index / 4.0) + row_index * 0.045)
    return wavelengths, x, y


def _write_synthetic_leaf(leaf: Path, *, dataset_id: str, rows: int, cols: int, target: str) -> None:
    wavelengths, x, y = _deterministic_spectra(rows, cols)
    sample_ids = [f"s{index + 1:03d}" for index in range(rows)]
    observation_ids = [f"o{index + 1:03d}" for index in range(rows)]
    leaf.mkdir(parents=True, exist_ok=True)
    with (leaf / "X.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["observation_id", *[f"{float(value):.12g}" for value in wavelengths]])
        for observation_id, row in zip(observation_ids, x, strict=True):
            writer.writerow([observation_id, *[f"{float(value):.12g}" for value in row]])
    with (leaf / "Y.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["observation_id", target])
        for observation_id, value in zip(observation_ids, y, strict=True):
            writer.writerow([observation_id, f"{float(value):.12g}"])
    with (leaf / "M.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["dataset_id", "observation_id", "sample_id", "split_original", "cultivar"])
        for index, (observation_id, sample_id) in enumerate(zip(observation_ids, sample_ids, strict=True)):
            writer.writerow([dataset_id, observation_id, sample_id, "calibration" if index % 4 else "validation", f"synthetic_{index % 3}"])
    card = {
        "dataset_id": dataset_id,
        "dataset_name": "Web Repository Provider Fixture",
        "spectral_organization": {
            "organization_type": "single_block",
            "alignment_level": "sample",
            "n_blocks": 1,
        },
        "spectral_blocks": [
            {
                "block_id": "X",
                "x_file": "X.csv",
                "instrument_name": "synthetic_nir",
                "axis_unit": "nm",
                "axis_min": f"{float(wavelengths[0]):.12g}",
                "axis_max": f"{float(wavelengths[-1]):.12g}",
                "n_rows": rows,
                "n_spectral_variables": cols,
            }
        ],
        "target_summary": {
            "target_variables": [target],
            "target_types": {target: "regression"},
        },
        "metadata_fields_summary": {
            "m_fields": ["dataset_id", "observation_id", "sample_id", "split_original", "cultivar"],
        },
        "split_summary": {
            "original_split_available": True,
            "split_should_be_preserved_not_applied": True,
        },
        "license_summary": {
            "public_release_allowed": True,
            "rights_notes": "deterministic synthetic E2E fixture generated by nirs4all-datasets",
            "license_name": "CC-BY-4.0",
        },
        "source_summary": {
            "source_name": "NIRS4ALL deterministic E2E fixture",
            "source_url": "https://github.com/GBeurier/nirs4all-ecosystem",
        },
        "detected_sources": [{"url": "https://github.com/GBeurier/nirs4all-ecosystem"}],
        "associated_publications": [],
    }
    (leaf / "dataset_card.json").write_text(json.dumps(card, ensure_ascii=True, sort_keys=True), encoding="utf-8")


def _build_synthetic_catalog_root(out_dir: Path, *, dataset_id: str, rows: int, cols: int, target: str) -> Path:
    import yaml
    from nirs4all_datasets.bootstrap import build_descriptor_from_card
    from nirs4all_datasets.organize import organize

    catalog_root = out_dir / "_catalog_root"
    leaf = out_dir / "_source_v2" / dataset_id
    _write_synthetic_leaf(leaf, dataset_id=dataset_id, rows=rows, cols=cols, target=target)
    descriptor, _warnings = build_descriptor_from_card(leaf)
    organize(leaf, descriptor, catalog_root / "datasets")
    descriptor_dir = catalog_root / "catalog" / "datasets"
    descriptor_dir.mkdir(parents=True, exist_ok=True)
    (descriptor_dir / f"{descriptor.id}.yaml").write_text(
        yaml.safe_dump(_descriptor_payload(descriptor), sort_keys=True),
        encoding="utf-8",
    )
    return catalog_root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", type=Path, default=Path.cwd(), help="Ecosystem workspace root.")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output directory for repository_*.csv files.")
    parser.add_argument("--dataset-id", default=DEFAULT_DATASET_ID, help="nirs4all-datasets catalog id.")
    parser.add_argument("--source", default=None, help="Source id to export; defaults to the dataset's first source.")
    parser.add_argument("--target", default="LMA", help="Numeric target column to export.")
    parser.add_argument("--build-synthetic-catalog-fixture", action="store_true", help="Build a temporary local catalog root before resolving through DatasetProvider.")
    parser.add_argument("--rows", type=int, default=48, help="Rows for the temporary synthetic catalog fixture.")
    parser.add_argument("--cols", type=int, default=2151, help="Spectral columns for the temporary synthetic catalog fixture.")
    args = parser.parse_args()

    workspace_root = args.workspace_root.resolve()
    sys.path.insert(0, str(workspace_root / "nirs4all-providers" / "src"))
    sys.path.insert(0, str(workspace_root / "nirs4all-datasets" / "src"))

    from nirs4all_providers import DatasetProvider

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    catalog_root = (
        _build_synthetic_catalog_root(
            out_dir,
            dataset_id=args.dataset_id,
            rows=args.rows,
            cols=args.cols,
            target=args.target,
        )
        if args.build_synthetic_catalog_fixture
        else workspace_root / "nirs4all-datasets"
    )
    provider = DatasetProvider(root=str(catalog_root))
    dataset = provider.get_dataset(args.dataset_id)
    source = args.source or dataset.sources()[0]
    x = np.asarray(dataset.x(source), dtype=np.float64)
    wavelengths = np.asarray(dataset.wavelengths(source), dtype=np.float64)
    y_frame = dataset.y(args.target)
    if y_frame is None or args.target not in y_frame.columns:
        raise SystemExit(f"target {args.target!r} is not available in {args.dataset_id!r}")
    y_by_sample = {str(row["sample_id"]): float(row[args.target]) for _, row in y_frame.iterrows()}
    sample_ids = [str(value) for value in dataset.sample_ids(source)]
    y_values = [y_by_sample[sample_id] for sample_id in sample_ids]
    if x.shape[0] != len(sample_ids) or x.shape[0] != len(y_values):
        raise SystemExit(f"row mismatch: X={x.shape} sample_ids={len(sample_ids)} y={len(y_values)}")
    if x.shape[1] != wavelengths.shape[0]:
        raise SystemExit(f"axis mismatch: X columns={x.shape[1]} wavelengths={wavelengths.shape[0]}")
    if not np.isfinite(x).all() or not np.isfinite(wavelengths).all() or not all(math.isfinite(value) for value in y_values):
        raise SystemExit("dataset export contains non-finite numeric values")

    x_path = out_dir / "repository_X_train.csv"
    y_path = out_dir / "repository_y_train.csv"
    metadata_path = out_dir / "repository_metadata.csv"
    manifest_path = out_dir / "repository_dataset_manifest.json"
    _write_matrix(x_path, wavelengths, x)
    _write_target(y_path, args.target, y_values)
    _write_metadata(metadata_path, dataset_id=args.dataset_id, source=source, sample_ids=sample_ids)
    file_hashes = [_sha256(path) for path in (x_path, y_path, metadata_path)]
    files_sha256 = hashlib.sha256(
        json.dumps([[item["file"], item["bytes"], item["sha256"]] for item in file_hashes], separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
    manifest = {
        "schema_version": "n4a.web.repository_dataset_fixture/v1",
        "provider": {
            "id": "datasets",
            "package": "nirs4all-providers",
            "portability": provider.capabilities().portability,
        },
        "dataset": {
            "id": dataset.id,
            "tier": dataset.tier.value,
            "catalog_root": str(catalog_root),
            "synthetic_catalog_fixture": bool(args.build_synthetic_catalog_fixture),
            "source": source,
            "target": args.target,
            "rows": int(x.shape[0]),
            "cols": int(x.shape[1]),
            "sample_ids_sha256": hashlib.sha256(json.dumps(sample_ids, separators=(",", ":")).encode("utf-8")).hexdigest(),
        },
        "expected_badge": f"{x.shape[0]} samples \u00d7 {x.shape[1]} wavelengths",
        "files": file_hashes,
        "files_sha256": files_sha256,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=_json_default) + "\n", encoding="utf-8")
    print(json.dumps({"out_dir": str(out_dir), **manifest}, sort_keys=True, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
