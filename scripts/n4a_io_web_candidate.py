#!/usr/bin/env python3
"""Transfer an IO browser-only candidate to Web's existing package verifier."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

SCHEMA = "n4a.io-browser-candidate/v1"
PACKAGE = "nirs4all-io-wasm"
FILES = {
    "package.json",
    "nirs4all_io_wasm.js",
    "nirs4all_io_wasm.d.ts",
    "nirs4all_io_wasm_bg.wasm",
    "nirs4all_io_wasm_bg.wasm.d.ts",
}


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def facts(path: Path) -> dict:
    data = path.read_bytes()
    return {"size": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def emit(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def check_source(io: Path, baseline: str) -> None:
    if git(io, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Candidate source must match the selected commit")
    paths = subprocess.check_output(
        ["git", "-C", str(io), "diff", "--name-only", "-z", baseline, "HEAD"], text=True,
    ).split("\0")
    outside = [path for path in paths if path and not path.startswith("bindings/wasm/src/")]
    if outside:
        raise ValueError(f"Browser-only runner cannot qualify these source changes: {outside}")


def pack(io: Path, baseline: str, output: Path) -> None:
    check_source(io, baseline)
    generated = io / "bindings/wasm/pkg"
    if (generated / "snippets").exists():
        raise ValueError("Unexpected wasm-bindgen snippets. The Web projection needs review.")
    output.mkdir()
    files = {}
    for name in sorted(FILES):
        shutil.copyfile(generated / name, output / name)
        files[name] = facts(output / name)
    emit(output / "receipt.json", {
        "schema": SCHEMA,
        "source_commit": git(io, "rev-parse", "HEAD"),
        "source_tree": git(io, "rev-parse", "HEAD^{tree}"),
        "baseline_tree": git(io, "rev-parse", f"{baseline}^{{tree}}"),
        "cargo_lock_sha256": facts(io / "bindings/wasm/Cargo.lock")["sha256"],
        "files": files,
    })


def stage(web: Path, payload: Path, expected_sha: str) -> None:
    manifest = web / "scripts/public-packages.v1.json"
    pins = json.loads(manifest.read_text())
    pin = pins["io"]
    receipt = json.loads((payload / "receipt.json").read_text())
    if receipt["schema"] != SCHEMA or receipt["source_commit"] != expected_sha:
        raise ValueError("Unexpected IO candidate identity")
    if (pin["source"]["tree"] != receipt["baseline_tree"] or
            pin["browser_deployment"]["build"]["lock_sha256"] != receipt["cargo_lock_sha256"]):
        raise ValueError("The candidate baseline differs from Web's locked IO browser cohort")
    if set(receipt["files"]) != FILES or set(pin["browser_files"]) != FILES:
        raise ValueError("Unexpected IO browser file inventory")
    metadata = json.loads((payload / "package.json").read_text())
    if metadata["name"] != PACKAGE or metadata["version"] != pin["version"]:
        raise ValueError("Candidate changes the IO browser package identity")

    retained = web / pin["destination"]
    staged = {}
    for name, baseline in pin["files"].items():
        if name in FILES:
            source = payload / name
            expected = receipt["files"][name]
        else:
            source = retained / name
            expected = baseline
        if facts(source) != expected:
            raise ValueError(f"Unexpected staged bytes: {name}")
        if name not in FILES:
            # Web's normal staging removes the previous projection before install.
            # Keep baseline inputs in a stable side directory outside that projection.
            copy = payload / "retained" / name
            copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, copy)
            source = copy
        staged[name] = {"source": str(source.resolve()), **expected}

    for key in ("registry", "browser_deployment", "browser_files", "projection", "source_files", "package_type_normalization"):
        pin.pop(key, None)
    pin["source"] = {
        "kind": "io-browser-candidate",
        "repository": "https://github.com/GBeurier/nirs4all-io",
        "commit": receipt["source_commit"],
        "tree": receipt["source_tree"],
    }
    pin["files"] = {name: {k: v for k, v in entry.items() if k != "source"} for name, entry in staged.items()}
    pin["local"] = {
        "kind": "local-unpublished",
        "note": "Exact IO browser candidate and retained Web companions from the locked cohort",
        "files": staged,
    }
    emit(manifest, pins)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check-source")
    check_parser.add_argument("io", type=Path)
    check_parser.add_argument("baseline")
    pack_parser = sub.add_parser("pack")
    pack_parser.add_argument("io", type=Path)
    pack_parser.add_argument("baseline")
    pack_parser.add_argument("output", type=Path)
    stage_parser = sub.add_parser("stage")
    stage_parser.add_argument("web", type=Path)
    stage_parser.add_argument("payload", type=Path)
    stage_parser.add_argument("expected_sha")
    args = parser.parse_args()
    if args.command == "check-source":
        check_source(args.io, args.baseline)
    elif args.command == "pack":
        pack(args.io, args.baseline, args.output)
    else:
        stage(args.web, args.payload, args.expected_sha)


if __name__ == "__main__":
    main()
