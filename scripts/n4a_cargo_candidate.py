#!/usr/bin/env python3
"""Test a locked Rust consumer with exact candidate sources in disposable checkouts."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tomllib


def locked_packages(lock):
    return tomllib.loads(lock.read_text())["package"]


def run(producer, consumer, manifests, package, tests):
    producer = producer.resolve()
    consumer = consumer.resolve()
    for checkout in [producer, consumer]:
        if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=normal"], cwd=checkout):
            raise ValueError(f"dirty source checkout: {checkout}")
    lock = consumer / "Cargo.lock"
    before = locked_packages(lock)
    patches = {}
    config = []
    for manifest in manifests:
        path = (producer / manifest).resolve()
        if not path.is_relative_to(producer) or path.name != "Cargo.toml":
            raise ValueError(f"invalid candidate manifest: {manifest}")
        name = tomllib.loads(path.read_text())["package"]["name"]
        matches = [p for p in before if p["name"] == name]
        if len(matches) != 1 or matches[0].get("source") != "registry+https://github.com/rust-lang/crates.io-index":
            raise ValueError(f"expected one crates.io lock entry for {name}")
        if name in patches:
            raise ValueError(f"duplicate candidate: {name}")
        patches[name] = path
        config.extend(["--config", f'patch.crates-io.{json.dumps(name)}.path={json.dumps(path.parent.as_posix())}'])

    def cargo(*args):
        return subprocess.check_output(["cargo", *config, *args], cwd=consumer)

    host = next(line.split(": ", 1)[1] for line in subprocess.check_output(
        ["rustc", "-vV"], text=True).splitlines() if line.startswith("host: "))
    data = json.loads(cargo("metadata", "--format-version", "1", "--no-default-features", "--filter-platform", host))
    after = locked_packages(lock)
    if [p for p in before if p["name"] not in patches] != [p for p in after if p["name"] not in patches]:
        raise ValueError("unrelated dependency resolution changed; the consumer needs a reviewed lock")
    package_by_id = {p["id"]: p for p in data["packages"]}
    ids = [i for i in data["workspace_members"] if package_by_id[i]["name"] == package]
    if len(ids) != 1:
        raise ValueError(f"expected one consumer workspace package: {package}")
    deps = {n["id"]: [d["pkg"] for d in n["deps"]] for n in data["resolve"]["nodes"]}
    pending = list(ids)
    reachable = set()
    while pending:
        item = pending.pop()
        if item not in reachable:
            reachable.add(item)
            pending.extend(deps[item])
    for name, path in patches.items():
        active = [package_by_id[i] for i in reachable if package_by_id[i]["name"] == name]
        rows = [p for p in after if p["name"] == name]
        if (len(active) != 1 or Path(active[0]["manifest_path"]).resolve() != path or
                len(rows) != 1 or "source" in rows[0]):
            raise ValueError(f"consumer did not resolve the exact candidate {name}")
    # Keep Cargo's exit status and owner test output visible in the job.
    command = ["cargo", *config, "test", "--locked", "--no-default-features", "-p", package]
    for test in tests:
        command.extend(["--test", test])
    subprocess.run(command, cwd=consumer, check=True)
    return {
        "producer_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=producer, text=True).strip(),
        "consumer_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=consumer, text=True).strip(),
        "package": package, "tests": tests, "host": host,
        "candidate_manifests": manifests,
        "consumer_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer", type=Path, required=True)
    parser.add_argument("--consumer", type=Path, required=True)
    parser.add_argument("--manifest", action="append", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--test", action="append", default=[])
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = run(args.producer, args.consumer, args.manifest, args.package, args.test)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
