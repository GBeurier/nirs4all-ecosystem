#!/usr/bin/env python3
"""Assemble a candidate cohort of ecosystem members from source and test it end to end.

A candidate cohort names, per chain member, the source to test: a commit, a
branch, a local working tree, or the published release. The tool snapshots each
source member into one build root, builds every consumer against the cohort's
crates (a generated ``[patch.crates-io]`` in the build root's ``.cargo``), the
cohort's Python wheels (one ``uv`` environment, cohort members never resolved
from PyPI) and the Methods native library, then runs the members' gates from
cheap to expensive and prints which layer broke first.

Nothing is published and nothing is written into the member repositories:
sources are read with ``git ls-tree``/``git cat-file`` (or from a working tree)
and copied into the build root. ``release-plan`` turns a green report into the
ordered, tested-SHA-only release sequence.

Subcommands: ``init``, ``run``, ``summary``, ``release-plan``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]

sys.path.insert(0, str(Path(__file__).resolve().parent))
import n4a_release_lock as release_lock  # noqa: E402  (shared version-source readers)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_SCHEMA = "n4a.candidate-cohort/v1"
MEMBERS_SCHEMA = "n4a.cohort-members/v1"
REPORT_SCHEMA = "n4a.candidate-cohort-report/v1"
DEFAULT_MEMBERS = ROOT / "docs/contracts/release/cohort/members.n4a.json"
COMMIT_RE = re.compile(r"[0-9a-f]{40}")
DEP_TABLES = ("dependencies", "dev-dependencies", "build-dependencies")
MIN_FREE_GB = float(os.environ.get("N4A_COHORT_MIN_FREE_GB", "15"))  # stop large builds below this
USER_AGENT = "n4a-cohort (nirs4all ecosystem release tooling)"


class CohortError(RuntimeError):
    """Invalid cohort input or a failed assembly step."""


# --------------------------------------------------------------------------- utils


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_of(value: Any) -> str:
    return sha256_hex(release_lock.canonical_json(value))


def log(message: str) -> None:
    print(f"[cohort] {message}", flush=True)


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None, check: bool = True,
        capture: bool = True, input_bytes: bytes | None = None) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, cwd=cwd, env=env, input=input_bytes,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE if capture else None)
    if check and proc.returncode != 0:
        detail = (proc.stderr or b"").decode("utf-8", "replace").strip()[-4000:] if capture else ""
        raise CohortError(f"command failed ({proc.returncode}) in {cwd}: {' '.join(cmd)}\n{detail}")
    return proc


def git(repo: Path | str, *args: str, check: bool = True) -> str:
    proc = run(["git", "-C", str(repo), *args], check=check)
    return proc.stdout.decode("utf-8", "replace").strip() if proc.returncode == 0 else ""


def free_gb(path: Path) -> float:
    probe = path
    while not probe.exists():
        probe = probe.parent
    usage = shutil.disk_usage(probe)
    return usage.free / 1e9


def require_disk(path: Path, label: str) -> None:
    available = free_gb(path)
    if available < MIN_FREE_GB:
        raise CohortError(f"only {available:.1f} GB free under {path}; {label} needs at least {MIN_FREE_GB} GB")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


# --------------------------------------------------------------------- semver/cargo


def _parse_version(text: str) -> tuple[int, int, int, str]:
    core, _, pre = text.strip().partition("-")
    core = core.split("+", 1)[0]
    parts = [int(p) for p in core.split(".")]
    while len(parts) < 3:
        parts.append(0)
    return parts[0], parts[1], parts[2], pre


def _comparator(op: str, req: str, version: tuple[int, int, int, str]) -> bool:
    req = req.strip()
    pieces = req.split(".")
    wild = [p in ("*", "x", "X") for p in pieces]
    if any(wild):
        pieces = pieces[: wild.index(True)]
        op = op or "="
        if not pieces:
            return True
    n = len(pieces)
    nums = [int(p.split("-")[0]) for p in pieces]
    full = nums + [0] * (3 - n)
    v = version[:3]
    low = tuple(full)
    if op in ("", "^"):
        if n == 1 or nums[0] > 0:
            high = (nums[0] + 1, 0, 0)
        elif n == 2 or nums[1] > 0:
            high = (0, nums[1] + 1, 0)
        else:
            high = (0, 0, nums[2] + 1)
        return low <= v < high
    if op == "~":
        high = (nums[0] + 1, 0, 0) if n == 1 else (nums[0], nums[1] + 1, 0)
        return low <= v < high
    if op == "=":
        if n == 3:
            return v == low
        high = (nums[0] + 1, 0, 0) if n == 1 else (nums[0], nums[1] + 1, 0)
        return low <= v < high
    if op == ">=":
        return v >= low
    if op == ">":
        return v > low if n == 3 else v >= ((nums[0] + 1, 0, 0) if n == 1 else (nums[0], nums[1] + 1, 0))
    if op == "<":
        return v < low
    if op == "<=":
        return v <= low if n == 3 else v < ((nums[0] + 1, 0, 0) if n == 1 else (nums[0], nums[1] + 1, 0))
    raise CohortError(f"unsupported cargo comparator {op!r}")


def cargo_req_matches(requirement: str, version: str) -> bool:
    """Return whether a Cargo version requirement admits ``version`` (pre-releases ignored)."""
    parsed = _parse_version(version)
    for clause in requirement.split(","):
        clause = clause.strip()
        if not clause or clause == "*":
            continue
        match = re.fullmatch(r"(>=|<=|=|>|<|\^|~)?\s*(.+)", clause)
        if not match:
            raise CohortError(f"unparseable cargo requirement {requirement!r}")
        if not _comparator(match.group(1) or "", match.group(2), parsed):
            return False
    return True


# ------------------------------------------------------------------------ recipes


@dataclass
class Recipe:
    key: str
    data: dict[str, Any]
    order: int

    @property
    def repo(self) -> str:
        return self.data["repo"]

    @property
    def sibling(self) -> str:
        return self.data["sibling"]

    @property
    def python(self) -> dict[str, Any]:
        return self.data.get("python", {})

    @property
    def rust_excludes(self) -> list[str]:
        return list(self.data.get("rust", {}).get("exclude_paths", []))


def load_recipes(path: Path) -> tuple[dict[str, Recipe], dict[str, Any]]:
    data = read_json(path)
    if data.get("schema_version") != MEMBERS_SCHEMA:
        raise CohortError(f"{path}: schema_version must be {MEMBERS_SCHEMA}")
    aggregation = read_json(ROOT / data["aggregation_manifest"])
    components = {c["key"]: c for c in aggregation["components"]}
    recipes: dict[str, Recipe] = {}
    for index, entry in enumerate(data["members"]):
        entry = dict(entry)
        component = entry.get("aggregation_component")
        if component:
            if component not in components:
                raise CohortError(f"recipe {entry['key']}: unknown aggregation component {component}")
            entry.setdefault("version_sources", components[component]["version_sources"])
        recipes[entry["key"]] = Recipe(entry["key"], entry, index)
    return recipes, data


# ----------------------------------------------------------------------- manifest


# "published" installs the release a source consumer ships (its exact ``install`` pin); "published:latest" opts
# into the newest release within that consumer's declared range.
PUBLISHED_REFS = ("published", "published:latest")


@dataclass
class MemberSpec:
    key: str
    ref: str
    source: str | None = None
    native_ref: str | None = None
    python: str | None = None
    version: str | None = None
    note: str | None = None

    @property
    def published(self) -> bool:
        return self.ref in PUBLISHED_REFS

    @property
    def latest(self) -> bool:
        """Whether a consumer's newest admitted release is wanted instead of its exact ``install`` pin."""
        return self.ref == "published:latest"

    @property
    def is_path(self) -> bool:
        return self.ref.startswith("path:")


def parse_member_value(key: str, value: Any, base: Path) -> MemberSpec:
    if isinstance(value, str):
        value = {"ref": value}
    if not isinstance(value, dict) or not isinstance(value.get("ref"), str) or not value["ref"]:
        raise CohortError(f"member {key}: an object with a non-empty 'ref' is required")
    allowed = {"ref", "source", "native_ref", "python", "version", "note"}
    unknown = set(value) - allowed
    if unknown:
        raise CohortError(f"member {key}: unknown fields {sorted(unknown)}")
    ref = value["ref"]
    if ref.startswith("path:"):
        target = Path(ref[5:]).expanduser()
        ref = "path:" + str((base / target).resolve() if not target.is_absolute() else target)
    if value.get("python") not in (None, "published"):
        raise CohortError(f"member {key}: python may only be 'published'")
    if ref == "published:latest" and value.get("version"):
        raise CohortError(f"member {key}: 'published:latest' and an explicit version are exclusive")
    return MemberSpec(key=key, ref=ref, source=value.get("source"), native_ref=value.get("native_ref"),
                      python=value.get("python"), version=value.get("version"), note=value.get("note"))


def load_manifest(path: Path | None, overrides: list[str], recipes: dict[str, Recipe]) -> dict[str, Any]:
    if path:
        data = read_json(path)
        base = path.resolve().parent
    else:
        data = {"schema_version": MANIFEST_SCHEMA, "cohort_id": "adhoc", "members": {}}
        base = Path.cwd()
    if data.get("schema_version") != MANIFEST_SCHEMA:
        raise CohortError(f"manifest schema_version must be {MANIFEST_SCHEMA}")
    if data.get("pin_alignment", "refuse") not in ("refuse", "align"):
        raise CohortError("pin_alignment must be 'refuse' or 'align'")
    members_raw = dict(data.get("members", {}))
    for item in overrides:
        key, sep, value = item.partition("=")
        if not sep:
            raise CohortError(f"--set expects key=ref, got {item!r}")
        members_raw[key] = value
        base_for_set = Path.cwd()
        if value.startswith("path:") and not Path(value[5:]).is_absolute():
            members_raw[key] = "path:" + str((base_for_set / value[5:]).resolve())
    unknown = set(members_raw) - set(recipes)
    if unknown:
        raise CohortError(f"unknown cohort members {sorted(unknown)}; known: {sorted(recipes)}")
    specs = {key: parse_member_value(key, members_raw.get(key, "published"), base) for key in recipes}
    return {
        "cohort_id": data.get("cohort_id", "adhoc"),
        "description": data.get("description", ""),
        "python": data.get("python", "3.11"),
        "pin_alignment": data.get("pin_alignment", "refuse"),
        "tier": data.get("tier", "fast"),
        "members": specs,
        "raw": data,
    }


# ------------------------------------------------------------------------ sources


@dataclass
class Snapshot:
    key: str
    kind: str  # "commit" | "path"
    root: Path
    commit: str | None
    branch: str | None
    dirty: bool
    digest: str
    files: dict[str, str]
    source: str
    changed: int = 0
    notes: list[str] = field(default_factory=list)
    repo: Path | None = None

    def original_text(self, rel: str) -> str:
        """Source bytes of a file, before any build-root pin alignment."""
        if self.kind == "path":
            return (Path(self.source) / rel).read_text(encoding="utf-8")
        return run(["git", "-C", str(self.repo), "cat-file", "blob", self.files[rel]]).stdout.decode("utf-8")


class SourceManager:
    """Copy member sources into the build root, writing only changed files."""

    def __init__(self, build: Path, workspace: Path) -> None:
        self.build = build
        self.workspace = workspace
        (build / "src").mkdir(parents=True, exist_ok=True)
        # Snapshots are laid out like the workspace (src/<sibling>), with this runner as
        # src/nirs4all-ecosystem, so member tooling that looks for sibling checkouts finds
        # the cohort's sources, never unrelated working trees above the build root.
        link = build / "src" / "nirs4all-ecosystem"
        if not link.is_symlink() or link.resolve() != ROOT:
            if link.is_symlink():
                link.unlink()
            link.symlink_to(ROOT, target_is_directory=True)

    def directory(self, recipe: Recipe) -> Path:
        return self.build / "src" / recipe.sibling

    def default_source(self, recipe: Recipe) -> str:
        sibling = self.workspace / recipe.sibling
        if (sibling / ".git").exists():
            return str(sibling)
        return f"https://github.com/{recipe.repo}.git"

    def _mirror(self, recipe: Recipe) -> Path:
        mirror = self.build / "git" / f"{recipe.key}.git"
        if not mirror.exists():
            mirror.parent.mkdir(parents=True, exist_ok=True)
            run(["git", "init", "--bare", "-q", str(mirror)])
        return mirror

    def resolve_commit(self, recipe: Recipe, spec: MemberSpec, ref: str) -> tuple[Path, str]:
        source = spec.source or self.default_source(recipe)
        if not re.match(r"^(https://|ssh://|git@|file://)", source):
            repo = Path(source)
            commit = git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", check=False)
            if commit:
                return repo, commit
            source = f"https://github.com/{recipe.repo}.git"
        mirror = self._mirror(recipe)
        commit = git(mirror, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", check=False)
        if not commit:
            log(f"{recipe.key}: fetching {ref} from {source}")
            run(["git", "-C", str(mirror), "fetch", "-q", "--no-tags", source, f"{ref}"], check=True)
            commit = git(mirror, "rev-parse", "--verify", "FETCH_HEAD^{commit}")
            if COMMIT_RE.fullmatch(ref) and commit != ref:
                raise CohortError(f"{recipe.key}: fetched {commit}, expected {ref}")
            git(mirror, "update-ref", f"refs/cohort/{commit}", commit)
        return mirror, commit

    def _stamp_path(self, key: str) -> Path:
        return self.build / "src" / f"{key}.stamp.json"

    def _sync(self, key: str, root: Path, desired: dict[str, tuple[str, str, Any]], reader) -> int:
        """desired: path -> (identity, mode, handle). Write changed files, delete stale ones."""
        stamp_path = self._stamp_path(key)
        previous = read_json(stamp_path)["files"] if stamp_path.exists() else {}
        root.mkdir(parents=True, exist_ok=True)
        to_write = [p for p, (ident, mode, _) in desired.items()
                    if previous.get(p) != [ident, mode] or not (root / p).exists() and not (root / p).is_symlink()]
        for rel in sorted(set(previous) - set(desired)):
            target = root / rel
            if target.is_symlink() or target.is_file():
                target.unlink()
        contents = reader([desired[p][2] for p in to_write]) if to_write else []
        for rel, body in zip(to_write, contents, strict=True):
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            mode = desired[rel][1]
            if target.is_symlink() or target.exists():
                if target.is_dir() and not target.is_symlink():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            if mode == "120000":
                os.symlink(body.decode("utf-8"), target)
                continue
            target.write_bytes(body)
            target.chmod(0o755 if mode == "100755" else 0o644)
        write_json(stamp_path, {"files": {p: [ident, mode] for p, (ident, mode, _) in desired.items()}})
        return len(to_write)

    def snapshot_commit(self, recipe: Recipe, spec: MemberSpec, ref: str) -> Snapshot:
        repo, commit = self.resolve_commit(recipe, spec, ref)
        listing = run(["git", "-C", str(repo), "ls-tree", "-r", "-z", "--full-tree", commit]).stdout
        desired: dict[str, tuple[str, str, Any]] = {}
        notes = []
        for entry in listing.split(b"\0"):
            if not entry:
                continue
            meta, _, path = entry.partition(b"\t")
            mode, kind, obj = meta.decode().split()
            rel = path.decode("utf-8")
            if kind != "blob":
                notes.append(f"submodule {rel} not materialized")
                continue
            desired[rel] = (obj, mode, obj)

        def reader(objects: list[str]) -> list[bytes]:
            proc = run(["git", "-C", str(repo), "cat-file", "--batch"], input_bytes=("\n".join(objects) + "\n").encode())
            out, pos, bodies = proc.stdout, 0, []
            for _ in objects:
                header_end = out.index(b"\n", pos)
                size = int(out[pos:header_end].split()[2])
                bodies.append(out[header_end + 1: header_end + 1 + size])
                pos = header_end + 1 + size + 1
            return bodies

        changed = self._sync(recipe.key, self.directory(recipe), desired, reader)
        tree = git(repo, "rev-parse", f"{commit}^{{tree}}")
        branch = None if COMMIT_RE.fullmatch(ref) else ref
        return Snapshot(recipe.key, "commit", self.directory(recipe), commit, branch, False,
                        digest=f"tree:{tree}", files={p: v[0] for p, v in desired.items()},
                        source=str(spec.source or self.default_source(recipe)), changed=changed, notes=notes, repo=repo)

    def snapshot_path(self, recipe: Recipe, spec: MemberSpec) -> Snapshot:
        tree_root = Path(spec.ref[5:])
        if not (tree_root / ".git").exists():
            raise CohortError(f"{recipe.key}: {tree_root} is not a git working tree")
        names = run(["git", "-C", str(tree_root), "ls-files", "-z", "-co", "--exclude-standard"]).stdout
        stamp_path = self._stamp_path(recipe.key)
        previous = read_json(stamp_path).get("stat", {}) if stamp_path.exists() else {}
        desired: dict[str, tuple[str, str, Any]] = {}
        stats: dict[str, list[Any]] = {}
        for raw in names.split(b"\0"):
            if not raw:
                continue
            rel = raw.decode("utf-8")
            path = tree_root / rel
            if not path.is_symlink() and not path.is_file():
                continue  # deleted but still tracked, or a submodule directory
            info = path.lstat()
            mode = "120000" if path.is_symlink() else ("100755" if info.st_mode & 0o111 else "100644")
            key = [info.st_size, info.st_mtime_ns, mode]
            prior = previous.get(rel)
            if prior and prior[0] == key:
                ident = prior[1]
            else:
                body = os.readlink(path).encode() if mode == "120000" else path.read_bytes()
                ident = "sha256:" + sha256_hex(body)
            stats[rel] = [key, ident]
            desired[rel] = (ident, mode, path)

        def reader(paths: list[Path]) -> list[bytes]:
            return [os.readlink(p).encode() if p.is_symlink() else p.read_bytes() for p in paths]

        changed = self._sync(recipe.key, self.directory(recipe), desired, reader)
        stamp = read_json(stamp_path)
        stamp["stat"] = stats
        write_json(stamp_path, stamp)
        head = git(tree_root, "rev-parse", "HEAD")
        dirty = bool(git(tree_root, "status", "--porcelain"))
        branch = git(tree_root, "branch", "--show-current") or None
        digest = "files:" + digest_of(sorted((p, v[0]) for p, v in desired.items()))
        return Snapshot(recipe.key, "path", self.directory(recipe), head, branch, dirty, digest,
                        {p: v[0] for p, v in desired.items()}, str(tree_root), changed)


# ------------------------------------------------------------------- rust analysis


def _cargo_files(snapshot: Snapshot, excludes: list[str]) -> list[str]:
    return sorted(p for p in snapshot.files if p.endswith("Cargo.toml") and not any(p.startswith(e) for e in excludes))


def discover_crates(snapshot: Snapshot, excludes: list[str]) -> dict[str, dict[str, str]]:
    crates: dict[str, dict[str, str]] = {}
    for rel in _cargo_files(snapshot, excludes):
        data = tomllib.loads((snapshot.root / rel).read_text(encoding="utf-8"))
        package = data.get("package")
        if not package or package.get("publish") is False:
            continue
        version = package.get("version")
        if isinstance(version, dict) and version.get("workspace"):
            version = _workspace_value(snapshot.root, rel, ("package", "version"))
        if not isinstance(version, str):
            continue
        crate_dir = str(Path(rel).parent)
        crates[package["name"]] = {"path": str(snapshot.root / crate_dir), "version": version, "manifest": rel}
    return crates


def _workspace_value(root: Path, rel: str, keys: tuple[str, ...]) -> Any:
    """Resolve an inherited ``*.workspace = true`` value from the nearest enclosing workspace."""
    current = (root / rel).parent
    while True:
        candidate = current / "Cargo.toml"
        if candidate.exists():
            data = tomllib.loads(candidate.read_text(encoding="utf-8"))
            if "workspace" in data:
                value: Any = data["workspace"]
                for key in keys:
                    value = value.get(key, {}) if isinstance(value, dict) else {}
                return value or None
        if current == root:
            return None
        current = current.parent


def iter_dependencies(data: dict[str, Any]):
    """Yield (table_path, dep_key, crate_name, requirement) for every registry-style dependency."""
    tables: list[tuple[str, dict[str, Any]]] = []
    for name in DEP_TABLES:
        if isinstance(data.get(name), dict):
            tables.append((name, data[name]))
    for target, body in (data.get("target") or {}).items():
        for name in DEP_TABLES:
            if isinstance(body.get(name), dict):
                tables.append((f"target.{target}.{name}", body[name]))
    workspace = data.get("workspace") or {}
    if isinstance(workspace.get("dependencies"), dict):
        tables.append(("workspace.dependencies", workspace["dependencies"]))
    for table, deps in tables:
        for dep_key, spec in deps.items():
            if isinstance(spec, str):
                yield table, dep_key, dep_key, spec, False
            elif isinstance(spec, dict):
                if spec.get("workspace"):
                    continue
                yield table, dep_key, spec.get("package", dep_key), spec.get("version"), "path" in spec


def rewrite_requirement(text: str, table: str, dep_key: str, new_req: str) -> str:
    """Replace one dependency's version requirement in Cargo.toml text, keeping layout."""
    lines = text.splitlines(keepends=True)
    current = None
    dotted = f"{table}.{dep_key}"
    for index, line in enumerate(lines):
        header = re.match(r"\s*\[([^\[\]]+)\]\s*(#.*)?$", line)
        if header:
            current = header.group(1).strip().replace('"', "").replace("'", "")
            continue
        if current == table and re.match(rf"\s*\"?{re.escape(dep_key)}\"?\s*=", line):
            if re.match(rf"\s*\"?{re.escape(dep_key)}\"?\s*=\s*\"", line):
                lines[index] = re.sub(r'=\s*"[^"]*"', f'= "{new_req}"', line, count=1)
            else:
                replaced = re.sub(r'(version\s*=\s*)"[^"]*"', rf'\g<1>"{new_req}"', line, count=1)
                if replaced == line:
                    raise CohortError(f"cannot rewrite {dep_key} in [{table}]: multi-line declaration")
                lines[index] = replaced
            return "".join(lines)
        if current == dotted and re.match(r"\s*version\s*=", line):
            lines[index] = re.sub(r'(version\s*=\s*)"[^"]*"', rf'\g<1>"{new_req}"', line, count=1)
            return "".join(lines)
    raise CohortError(f"dependency {dep_key} not found in [{table}]")


# --------------------------------------------------------------------- assembly


@dataclass
class Step:
    layer: str
    name: str
    status: str  # passed | failed | blocked | skipped | cached
    seconds: float = 0.0
    detail: str = ""
    log: str | None = None
    signals: list[str] = field(default_factory=list)


class Cohort:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.recipes, _ = load_recipes(Path(args.members))
        self.manifest = load_manifest(Path(args.manifest) if args.manifest else None, args.set or [], self.recipes)
        self.workspace = Path(args.workspace_root).resolve()
        self.build = Path(args.build_root).resolve()
        self.build.mkdir(parents=True, exist_ok=True)
        import fcntl

        self._lock = (self.build / ".lock").open("w")
        try:
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise CohortError(f"another cohort run holds {self.build}; use another --build-root") from None
        self.cargo_target = self.build / "target"
        self.uv = shutil.which("uv") or str(Path.home() / ".local/bin/uv")
        self.state_path = self.build / "state.json"
        self.state = read_json(self.state_path) if self.state_path.exists() else {}
        self.run_id = time.strftime("%Y%m%dT%H%M%S")
        self.run_dir = self.build / "runs" / self.run_id
        (self.run_dir / "logs").mkdir(parents=True, exist_ok=True)
        self.steps: list[Step] = []
        self.snapshots: dict[str, Snapshot] = {}
        self.crates: dict[str, dict[str, str]] = {}
        self.crate_owner: dict[str, str] = {}
        self.requirements: list[dict[str, Any]] = []
        self.alignments: list[dict[str, Any]] = []
        self.edges: dict[str, set[str]] = {k: set() for k in self.recipes}
        self.libn4m: Path | None = None
        self.native: dict[str, Any] = {}
        self.wheels: dict[str, Path] = {}
        self.rebuilt_wheels: set[str] = set()
        self.env_python: Path | None = None
        self.env_digest = ""
        self.installed: dict[str, str] = {}
        self.timings: dict[str, float] = {}

    # ------------------------------------------------------------- environment
    def base_env(self) -> dict[str, str]:
        env = dict(os.environ)
        env["CARGO_TARGET_DIR"] = str(self.cargo_target)
        # Line tables keep panic locations while cutting the shared target directory several-fold.
        env.setdefault("CARGO_PROFILE_DEV_DEBUG", "line-tables-only")
        env.setdefault("CARGO_PROFILE_TEST_DEBUG", "line-tables-only")
        env.setdefault("CARGO_INCREMENTAL", "0")  # incremental caches double the target size for little gain here
        env["UV_CACHE_DIR"] = str(self.build / "uv-cache")
        env["UV_PYTHON_INSTALL_DIR"] = str(self.build / "uv-python")
        env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
        env.pop("VIRTUAL_ENV", None)
        return env

    def source_members(self) -> list[str]:
        return [k for k, s in self.manifest["members"].items() if not s.published]

    def ordered(self, keys) -> list[str]:
        return sorted(keys, key=lambda k: self.recipes[k].order)

    def record(self, step: Step) -> Step:
        self.steps.append(step)
        mark = {"passed": "PASS", "failed": "FAIL", "blocked": "BLOCK", "skipped": "SKIP", "cached": "CACHED"}[step.status]
        log(f"{mark:6} {step.layer:12} {step.name} ({step.seconds:.0f}s){' - ' + step.detail if step.detail else ''}")
        return step

    # ------------------------------------------------------------------ sources
    def materialize(self) -> None:
        manager = SourceManager(self.build, self.workspace)
        keys = [k for k in self.ordered(self.recipes) if not self.manifest["members"][k].published]
        methods = self.manifest["members"]["methods"]
        if methods.published and self.needs_native():
            keys.append("methods")  # the published release's source, for the native library only
        for key in keys:
            spec = self.manifest["members"][key]
            recipe = self.recipes[key]
            ref = spec.ref
            if spec.published:
                ref = spec.native_ref or self.default_methods_runtime_ref() or ""
                if not COMMIT_RE.fullmatch(ref):
                    raise CohortError("methods is published but needs a native_ref commit (none declared, and no cohort Core declares one)")
            if recipe.data.get("unsupported"):
                raise CohortError(f"{key}: {recipe.data['unsupported']}")
            started = time.time()
            snap = manager.snapshot_path(recipe, spec) if ref.startswith("path:") else manager.snapshot_commit(recipe, spec, ref)
            if spec.published:
                snap.notes.append("published release: its source is used only to build the native library")
            self.snapshots[key] = snap
            self.record(Step(key, "source", "passed", time.time() - started,
                             f"{snap.kind} {snap.commit[:12] if snap.commit else '?'}{' dirty' if snap.dirty else ''}"
                             f"{' (' + snap.branch + ')' if snap.branch else ''}, {snap.changed} file(s) written"))

    def default_methods_runtime_ref(self) -> str | None:
        core = self.snapshots.get("core")
        upstreams = core.root / "compat/upstreams.toml" if core else None
        if upstreams and upstreams.exists():
            for entry in tomllib.loads(upstreams.read_text())["upstream"]:
                if entry["key"] == "methods":
                    return entry["ref"]
        return None

    def needs_native(self) -> bool:
        return any("libn4m" in g.get("needs", []) for k in self.source_members() for g in self.recipes[k].data.get("gates", []))

    def is_source(self, key: str) -> bool:
        return key in self.snapshots and not self.manifest["members"][key].published

    # ----------------------------------------------------------------- rust pins
    def analyse_rust(self) -> None:
        started = time.time()
        for key in self.ordered(self.snapshots):
            if not self.is_source(key):
                continue  # native-only snapshot of a published release: never patched
            for name, info in discover_crates(self.snapshots[key], self.recipes[key].rust_excludes).items():
                if name in self.crates:
                    raise CohortError(f"crate {name} is provided by both {self.crate_owner[name]} and {key}")
                self.crates[name] = info
                self.crate_owner[name] = key
        policy = self.manifest["pin_alignment"]
        refusals = []
        for key in self.ordered(self.snapshots):
            if not self.is_source(key):
                continue
            snap = self.snapshots[key]
            for rel in _cargo_files(snap, self.recipes[key].rust_excludes):
                path = snap.root / rel
                text = snap.original_text(rel)
                data = tomllib.loads(text)
                new_text = text
                for table, dep_key, crate, req, _has_path in iter_dependencies(data):
                    owner = self.crate_owner.get(crate)
                    if owner is None or owner == key or req is None:
                        continue
                    self.edges[key].add(owner)
                    version = self.crates[crate]["version"]
                    ok = cargo_req_matches(req, version)
                    record = {"consumer": key, "manifest": rel, "table": table, "crate": crate, "requirement": req,
                              "cohort_version": version, "provider": owner, "admits": ok}
                    self.requirements.append(record)
                    if ok:
                        continue
                    if policy == "align":
                        new_text = rewrite_requirement(new_text, table, dep_key, f"={version}")
                        self.alignments.append(record)
                    else:
                        refusals.append(record)
                if path.read_text(encoding="utf-8") != new_text:
                    path.write_text(new_text, encoding="utf-8")
        for key, recipe in self.recipes.items():
            if recipe.data.get("consumes_environment") and self.is_source(key):
                self.edges[key].update(k for k in self.snapshots if k != key and self.recipes[k].order < recipe.order)
        self.write_cargo_config()
        detail = f"{len(self.crates)} cohort crate(s) patched; {len(self.alignments)} requirement(s) aligned"
        for record in self.alignments:
            log(f"  ALIGNED {record['consumer']}:{record['manifest']} {record['crate']} {record['requirement']} -> ={record['cohort_version']}")
        if refusals:
            lines = [f"{r['consumer']}:{r['manifest']} requires {r['crate']} {r['requirement']}, cohort has {r['cohort_version']}"
                     for r in refusals]
            self.record(Step("pins", "cargo patch", "failed", time.time() - started,
                             "[patch] would be ignored (requirement too strict): " + "; ".join(lines)))
            raise CohortError("cohort requirements refuse the cohort crate versions:\n  " + "\n  ".join(lines) +
                              "\nUse minor-level ranges in the consumers, or set \"pin_alignment\": \"align\" to test the pin updates.")
        self.record(Step("pins", "cargo patch", "passed", time.time() - started, detail))

    def write_cargo_config(self) -> None:
        lines = ["# Generated by nirs4all-ecosystem scripts/n4a_cohort.py; build-root only, never commit.",
                 f"# cohort: {self.manifest['cohort_id']}", "", "[patch.crates-io]"]
        for name in sorted(self.crates):
            lines.append(f'{json.dumps(name)} = {{ path = {json.dumps(self.crates[name]["path"])} }}')
        lines += ["", "[build]", f"target-dir = {json.dumps(str(self.cargo_target))}", ""]
        config = self.build / ".cargo" / "config.toml"
        config.parent.mkdir(parents=True, exist_ok=True)
        text = "\n".join(lines)
        if not config.exists() or config.read_text() != text:
            config.write_text(text)
        self.cargo_config_digest = sha256_hex(text.encode())

    def lock_check(self, key: str, lock: Path) -> list[str]:
        """Report cohort crates that also resolved from the registry in a consumer lockfile."""
        if not lock.exists():
            return []
        data = tomllib.loads(lock.read_text(encoding="utf-8"))
        problems = []
        for package in data.get("package", []):
            name, source = package.get("name"), package.get("source", "")
            if name in self.crates and source.startswith("registry+"):
                problems.append(f"{name} {package.get('version')} still resolved from crates.io (cohort {self.crates[name]['version']}); "
                                f"a requirement in the graph refuses the cohort version and the patch is ignored for it")
        return problems

    # ----------------------------------------------------------------- native
    def build_native(self) -> None:
        if "methods" not in self.snapshots:
            return
        recipe = self.recipes["methods"]
        native = recipe.data["native"]
        snap = self.snapshots["methods"]
        started = time.time()
        stamp = self.state.get("native", {})
        library = snap.root / native["library"]
        if stamp.get("digest") == snap.digest and library.exists():
            self.libn4m = library.resolve()
        else:
            require_disk(self.build, "the Methods native build")
            env = self.base_env()
            logfile = self.run_dir / "logs" / "methods-native.log"
            with logfile.open("wb") as handle:
                for cmd in (["cmake", "--preset", native["preset"]],
                            ["cmake", "--build", "--preset", native["preset"], "--target", native["target"], "--parallel"]):
                    handle.write(f"$ {' '.join(cmd)}\n".encode())
                    handle.flush()
                    proc = subprocess.run(cmd, cwd=snap.root, env=env, stdout=handle, stderr=subprocess.STDOUT)
                    if proc.returncode != 0:
                        self.record(Step("methods", "native libn4m", "failed", time.time() - started,
                                         f"{' '.join(cmd)} exited {proc.returncode}", str(logfile)))
                        return
            self.libn4m = library.resolve()
            self.state["native"] = {"digest": snap.digest}
        header = release_lock.parse_c_header_macros(snap.root / native["header"])
        major, minor, _ = (int(x) for x in header["abi_version"].split("."))
        self.native = {"library": str(self.libn4m), "sha256": sha256_hex(self.libn4m.read_bytes()),
                       "abi": header["abi_version"], "project_version": header["project_version"],
                       "commit": snap.commit}
        problems, checks = self.abi_checks(major, minor)
        detail = f"ABI {header['abi_version']} (Methods {header['project_version']}); " + "; ".join(checks)
        self.record(Step("methods", "native libn4m + ABI", "failed" if problems else "passed", time.time() - started,
                         detail + ("; " + "; ".join(problems) if problems else "")))

    def abi_checks(self, major: int, minor: int) -> tuple[list[str], list[str]]:
        problems, checks = [], []
        n4m = self.crates.get("n4m")
        candidates = [Path(n4m["path"]) / "src/lib.rs"] if n4m else []
        if not n4m:
            registry = Path(os.environ.get("CARGO_HOME", Path.home() / ".cargo")) / "registry/src"
            for req in self.requirements_on("n4m"):
                version = req.lstrip("=")
                candidates += sorted(registry.glob(f"*/n4m-{version}/src/lib.rs"))
        for lib in candidates[:1]:
            text = lib.read_text(encoding="utf-8")
            want_major = int(re.search(r"const ABI_MAJOR: u32 = (\d+);", text).group(1))
            want_minor = int(re.search(r"const ABI_MINOR: u32 = (\d+);", text).group(1))
            ok = want_major == major and minor >= want_minor
            (checks if ok else problems).append(f"n4m crate needs ABI {want_major}.>={want_minor}")
        for key in self.ordered(k for k in self.snapshots if self.is_source(k)):
            for expect in self.recipes[key].data.get("abi_expectations", []):
                text = (self.snapshots[key].root / expect["path"]).read_text(encoding="utf-8")
                want = [int(re.search(rf"\b{expect[name]}\s*=\s*(\d+)", text).group(1)) for name in ("major", "minor")]
                ok = want[0] == major and (minor == want[1] if expect.get("exact") else minor >= want[1])
                (checks if ok else problems).append(f"{key} expects ABI {want[0]}.{want[1]}{' exactly' if expect.get('exact') else ''}")
        return problems, checks

    def requirements_on(self, crate: str) -> list[str]:
        found = []
        for key, snap in self.snapshots.items():
            if not self.is_source(key):
                continue
            for rel in _cargo_files(snap, self.recipes[key].rust_excludes):
                data = tomllib.loads((snap.root / rel).read_text(encoding="utf-8"))
                found += [req for _, _, name, req, _ in iter_dependencies(data) if name == crate and req]
        return found

    # ----------------------------------------------------------------- python
    def python_digest(self, key: str) -> str:
        """Inputs of a member's wheels: its sources, its upstream cohort members and the cargo patch set."""
        upstream = sorted(self.transitive_upstream(key))
        return digest_of([self.snapshots[key].digest, [self.snapshots[u].digest for u in upstream], self.cargo_config_digest])

    def transitive_upstream(self, key: str) -> set[str]:
        seen: set[str] = set()
        stack = list(self.edges.get(key, ()))
        while stack:
            item = stack.pop()
            if item in seen:
                continue
            seen.add(item)
            stack.extend(self.edges.get(item, ()))
        return seen & set(self.snapshots)

    def build_wheels(self) -> bool:
        ok = True
        python = self.manifest["python"]
        for key in self.ordered(self.snapshots):
            recipe = self.recipes[key]
            spec = self.manifest["members"][key]
            if spec.published:
                continue
            if recipe.python.get("source_build_refusal") and spec.python != "published":
                raise CohortError(f"{key}: {recipe.python['source_build_refusal']}")
            for project in recipe.python.get("projects", []):
                dist = project["distribution"]
                out = self.build / "wheels" / key / dist.replace("-", "_")
                digest = self.python_digest(key)
                stamp = self.state.get("wheels", {}).get(dist, {})
                existing = sorted(out.glob("*.whl")) if out.exists() else []
                started = time.time()
                if stamp.get("digest") == digest and len(existing) == 1:
                    self.wheels[dist] = existing[0]
                    self.record(Step(key, f"wheel {dist}", "cached", 0, existing[0].name))
                    continue
                require_disk(self.build, f"the {dist} wheel build")
                if out.exists():
                    shutil.rmtree(out)
                out.mkdir(parents=True)
                logfile = self.run_dir / "logs" / f"wheel-{dist}.log"
                cmd = [self.uv, "build", "--wheel", "--python", python, "--out-dir", str(out), str(self.snapshots[key].root / project["path"])]
                with logfile.open("wb") as handle:
                    proc = subprocess.run(cmd, cwd=self.snapshots[key].root / project["path"], env=self.base_env(),
                                          stdout=handle, stderr=subprocess.STDOUT)
                built = sorted(out.glob("*.whl"))
                if proc.returncode != 0 or len(built) != 1:
                    ok = False
                    self.record(Step(key, f"wheel {dist}", "failed", time.time() - started, f"uv build exited {proc.returncode}", str(logfile)))
                    continue
                project_dir = self.snapshots[key].root / project["path"]
                lock = next((d / "Cargo.lock" for d in [project_dir, *project_dir.parents]
                             if (d / "Cargo.lock").exists() and self.snapshots[key].root in [d, *d.parents]), None)
                ignored = self.lock_check(key, lock) if lock else []
                if ignored:
                    ok = False
                    self.record(Step(key, f"wheel {dist}", "failed", time.time() - started, "built against a registry copy of a cohort crate",
                                     str(logfile), [f"PATCH IGNORED: {line}" for line in ignored]))
                    continue
                self.wheels[dist] = built[0]
                self.rebuilt_wheels.add(dist)
                self.state.setdefault("wheels", {})[dist] = {"digest": digest}
                self.record(Step(key, f"wheel {dist}", "passed", time.time() - started, built[0].name, str(logfile)))
        return ok

    def python_overrides(self) -> list[str]:
        lines = []
        for dist, wheel in sorted(self.wheels.items()):
            lines.append(f"{dist} @ {wheel.resolve().as_uri()}")
        for key, spec in self.manifest["members"].items():
            if spec.published and spec.version:
                for dist in self.recipes[key].python.get("distributions", [])[:1]:
                    lines.append(f"{dist}=={spec.version}")
        return lines

    def consumer_requirements(self) -> list[str]:
        """Chain packages that source consumers of the environment declare and the cohort does not build.

        Cohort wheels are installed by direct-file override, so they are left out. Every other declared
        distribution comes from PyPI at the manifest's ``version`` when its member pins one, otherwise at the
        consumer's exact ``install`` version, so the environment reproduces what the consumer ships. A member
        whose ref is ``published:latest`` takes the newest release within the consumer's declared range instead.
        """
        owners = {dist: key for key, recipe in self.recipes.items() for dist in recipe.python.get("distributions", [])}
        requirements = []
        for key in self.ordered(self.snapshots):
            declared = self.recipes[key].data.get("environment_requirements")
            if not declared or not self.is_source(key):
                continue
            entries = read_json(self.snapshots[key].root / declared["path"]).get(declared["field"])
            if not isinstance(entries, list) or not entries:
                raise CohortError(f"{key}: {declared['path']} declares no '{declared['field']}' Python requirements")
            for entry in entries:
                name = entry["name"]
                if name in self.wheels:
                    continue
                spec = self.manifest["members"].get(owners.get(name, ""))
                if spec and spec.version:
                    requirements.append(f"{name}=={spec.version}")
                elif spec and spec.latest:
                    requirements.append(name + (entry.get("range") or ""))
                elif entry.get("install"):
                    requirements.append(f"{name}=={entry['install']}")
                else:
                    raise CohortError(f"{key}: {declared['path']} declares no exact 'install' version for {name}")
        return requirements

    def build_env(self) -> None:
        started = time.time()
        env_dir = self.build / "env"
        python = env_dir / "bin" / "python"
        env = self.base_env()
        logfile = self.run_dir / "logs" / "python-env.log"
        requirements: list[str] = []
        torch_spec = None
        sdk = self.snapshots.get("sdk")
        sdk_recipe = self.recipes["sdk"].python
        if sdk is not None:
            test_reqs = (sdk.root / sdk_recipe["test_requirements"]).read_text(encoding="utf-8").splitlines()
            requirements = [line for line in test_reqs if line.strip() and not line.lstrip().startswith("#")
                            and not re.match(r"\s*torch\b", line)]
            action = (sdk.root / sdk_recipe["torch_cpu_from"]).read_text(encoding="utf-8")
            match = re.search(r"'(torch==[^']+\+cpu)'", action)
            if not match:
                raise CohortError(f"sdk: no CPU torch pin found in {sdk_recipe['torch_cpu_from']}")
            torch_spec = match.group(1)
        requirements += self.consumer_requirements()
        if not requirements and not self.wheels:
            raise CohortError("the Python environment has nothing to install: no cohort wheel and no declared consumer requirement")
        overrides = self.python_overrides()
        wanted = {"python": self.manifest["python"], "requirements": requirements, "torch": torch_spec,
                  "overrides": overrides, "wheels": {d: sha256_hex(w.read_bytes()) for d, w in sorted(self.wheels.items())}}
        wanted_digest = digest_of(wanted)
        if self.state.get("env", {}).get("digest") == wanted_digest and python.exists():
            self.env_python = python
            self.env_digest = wanted_digest
            self.installed = self.state["env"]["installed"]
            self.record(Step("env", "python environment", "cached", 0, self.env_summary()))
            return
        require_disk(self.build, "the Python environment")
        override_file = self.run_dir / "overrides.txt"
        override_file.write_text("\n".join(overrides) + "\n")
        req_file = self.run_dir / "requirements.txt"
        roots = [str(w) for w in self.wheels.values()]
        req_file.write_text("\n".join(requirements + roots) + "\n")
        commands = []
        if not python.exists():
            commands.append([self.uv, "venv", "--seed", "--python", self.manifest["python"], str(env_dir)])
        if torch_spec:
            commands.append([self.uv, "pip", "install", "--python", str(python), "--index-url", "https://download.pytorch.org/whl/cpu", torch_spec])
        install = [self.uv, "pip", "install", "--python", str(python), "--override", str(override_file), "-r", str(req_file)]
        for dist in sorted(self.rebuilt_wheels):
            install += ["--reinstall-package", dist]
        commands.append(install)
        if torch_spec:
            commands.append([self.uv, "pip", "uninstall", "--python", str(python), "triton"])
        with logfile.open("wb") as handle:
            for cmd in commands:
                handle.write(f"$ {' '.join(cmd)}\n".encode())
                handle.flush()
                proc = subprocess.run(cmd, env=env, stdout=handle, stderr=subprocess.STDOUT)
                if proc.returncode != 0 and "uninstall" not in cmd:
                    self.record(Step("env", "python environment", "failed", time.time() - started, f"{cmd[1]} {cmd[2]} exited {proc.returncode}", str(logfile)))
                    raise CohortError("Python environment assembly failed; see " + str(logfile))
        self.env_python = python
        self.installed = self.query_installed()
        self.env_digest = wanted_digest
        self.state["env"] = {"digest": wanted_digest, "installed": self.installed}
        self.record(Step("env", "python environment", "passed", time.time() - started, self.env_summary(), str(logfile)))
        self.check_python_requirements()

    def chain_distributions(self) -> list[str]:
        names = []
        for recipe in sorted(self.recipes.values(), key=lambda r: r.order):
            names += recipe.python.get("distributions", [])
        return names

    def query_installed(self) -> dict[str, str]:
        script = ("import json,sys\nfrom importlib.metadata import version, PackageNotFoundError\nout={}\n"
                  "for n in sys.argv[1:]:\n    try: out[n]=version(n)\n    except PackageNotFoundError: pass\nprint(json.dumps(out))")
        proc = run([str(self.env_python), "-c", script, *self.chain_distributions()])
        return json.loads(proc.stdout)

    def env_summary(self) -> str:
        parts = []
        for dist, version in self.installed.items():
            origin = "cohort" if dist in self.wheels else "PyPI"
            parts.append(f"{dist} {version} ({origin})")
        return ", ".join(parts)

    def check_python_requirements(self) -> None:
        script = (
            "import json,sys\nfrom importlib.metadata import distribution\nfrom packaging.requirements import Requirement\n"
            "chain=set(json.loads(sys.argv[1])); cohort=json.loads(sys.argv[2]); out=[]\n"
            "for consumer in chain:\n"
            "    try: dist=distribution(consumer)\n    except Exception: continue\n"
            "    for raw in dist.requires or []:\n"
            "        req=Requirement(raw)\n"
            "        if req.marker and not req.marker.evaluate({'extra': ''}): continue\n"
            "        name=req.name.lower().replace('_','-')\n"
            "        if name in cohort and not req.specifier.contains(cohort[name], prereleases=True):\n"
            "            out.append(f'{consumer} requires {raw}, cohort installs {name} {cohort[name]}')\n"
            "print(json.dumps(out))")
        cohort_versions = {d: self.installed[d] for d in self.wheels if d in self.installed}
        proc = run([str(self.env_python), "-c", script, json.dumps(self.chain_distributions()), json.dumps(cohort_versions)])
        mismatches = json.loads(proc.stdout)
        self.python_mismatches = mismatches
        if mismatches:
            self.record(Step("env", "python requirements", "failed", 0,
                             "cohort wheels installed by override against declared requirements: " + "; ".join(mismatches)))

    # ------------------------------------------------------------------- gates
    def node(self) -> str | None:
        candidates = [os.environ.get("N4A_NODE")] + sorted((Path.home() / ".nvm/versions/node").glob("v24*/bin/node"), reverse=True) + [shutil.which("node")]
        for candidate in candidates:
            if not candidate:
                continue
            proc = run([str(candidate), "--version"], check=False)
            if proc.returncode == 0 and int(proc.stdout.decode().strip().lstrip("v").split(".")[0]) >= 20:
                return str(candidate)
        return None

    def gate_list(self) -> list[tuple[str, dict[str, Any]]]:
        tiers = {"fast": {"fast"}, "full": {"fast", "full"}}[self.args.tier or self.manifest["tier"]]
        gates = []
        for key in self.ordered(self.snapshots):
            if self.manifest["members"][key].published:
                continue
            for gate in self.recipes[key].data.get("gates", []):
                if gate.get("tier", "fast") not in tiers:
                    continue
                if self.args.only and gate["id"] not in self.args.only:
                    continue
                if self.args.skip and gate["id"] in self.args.skip:
                    continue
                gates.append((key, gate))
        return gates

    def gate_digest(self, key: str, gate: dict[str, Any]) -> str:
        needs = gate.get("needs", [])
        tools = [sha256_hex((ROOT / part.split("{ecosystem}/", 1)[1]).read_bytes()) for part in gate["cmd"] if "{ecosystem}/" in part]
        parts = [gate, tools, self.snapshots[key].digest, sorted(self.snapshots[u].digest for u in self.transitive_upstream(key)),
                 self.cargo_config_digest]
        if "env" in needs:
            parts.append(self.env_digest)
        if "libn4m" in needs:
            parts.append(self.native.get("sha256"))
        return digest_of(parts)

    def run_gates(self) -> None:
        failed_ids: set[str] = set()
        node = self.node()
        cache = self.state.setdefault("gates", {})
        for key, gate in self.gate_list():
            needs = gate.get("needs", [])
            name = gate["id"]
            missing = []
            if "env" in needs and self.env_python is None:
                missing.append("Python environment")
            if "libn4m" in needs and self.libn4m is None:
                missing.append("libn4m")
            if "node" in needs and node is None:
                missing.append("Node >= 20 (set N4A_NODE)")
            missing += [f"gate {dep}" for dep in gate.get("after", []) if dep in failed_ids]
            missing += [f"{member} as a source member" for member in gate.get("requires_source", []) if not self.is_source(member)]
            if any(s.layer == key and s.status == "failed" and s.name.startswith("wheel") for s in self.steps) and "env" in needs:
                missing.append(f"{key} wheel")
            if missing:
                failed_ids.add(name)
                self.record(Step(key, name, "blocked", 0, "needs " + ", ".join(missing)))
                continue
            digest = self.gate_digest(key, gate)
            if not self.args.no_cache and cache.get(name) == digest:
                self.record(Step(key, name, "cached", 0, "inputs unchanged since its last pass"))
                continue
            self.run_gate(key, gate, node)
            if self.steps[-1].status == "passed":
                cache[name] = digest
            else:
                cache.pop(name, None)
                failed_ids.add(name)
            self.save_state()

    def run_gate(self, key: str, gate: dict[str, Any], node: str | None) -> None:
        snap = self.snapshots[key]
        work = self.build / "work" / gate["id"]
        if work.exists():
            shutil.rmtree(work)
        work.mkdir(parents=True)
        values = {"python": str(self.env_python or ""), "libn4m": str(self.libn4m or ""), "src": str(snap.root),
                  "cargo_target": str(self.cargo_target), "ecosystem": str(ROOT), "tool_python": sys.executable,
                  "node": node or "", "work": str(work), "build": str(self.build),
                  "site_packages": str(next((self.build / "env" / "lib").glob("python3*/site-packages"), ""))}
        for dist, wheel in self.wheels.items():
            values[f"wheel:{dist}"] = str(wheel)

        def expand(text: str) -> str:
            return re.sub(r"\{([a-z0-9_]+(?::[A-Za-z0-9_.-]+)?)\}", lambda m: values[m.group(1)], text)

        cmd = [expand(part) for part in gate["cmd"]]
        env = self.base_env()
        env.update({k: expand(v) for k, v in gate.get("env", {}).items()})
        if self.env_python:
            env["PATH"] = f"{self.env_python.parent}{os.pathsep}{env['PATH']}"
        if self.libn4m and "libn4m" in gate.get("needs", []):
            # Rust consumers select libn4m explicitly; Core's attested-runtime tests also check its digest.
            env["N4M_LIBRARY_PATH"] = str(self.libn4m)
            env["N4M_LIB_PATH"] = str(self.libn4m)
            env["N4M_EXPECTED_LIBRARY_SHA256"] = self.native["sha256"]
            env["NIRS4ALL_METHODS_LIB"] = str(self.libn4m)
            env["LD_LIBRARY_PATH"] = f"{self.libn4m.parent}{os.pathsep}{env.get('LD_LIBRARY_PATH', '')}"
        if node:
            env["PATH"] = f"{Path(node).parent}{os.pathsep}{env['PATH']}"
        logfile = self.run_dir / "logs" / f"{gate['id']}.log"
        started = time.time()
        if gate["cmd"][0] == "cargo" and free_gb(self.build) < MIN_FREE_GB:
            self.record(Step(key, gate["id"], "blocked", 0, f"only {free_gb(self.build):.1f} GB free (floor {MIN_FREE_GB:g} GB)"))
            return
        with logfile.open("wb") as handle:
            handle.write(f"$ {' '.join(cmd)}\n".encode())
            handle.flush()
            try:
                proc = subprocess.run(cmd, cwd=snap.root / gate.get("cwd", ""), env=env, stdout=handle,
                                      stderr=subprocess.STDOUT, timeout=gate.get("timeout", 3600))
                code = proc.returncode
            except subprocess.TimeoutExpired:
                code = "timeout"
        text = logfile.read_text(encoding="utf-8", errors="replace")
        signals = sorted(set(re.findall(r"^\[XPASS\(strict\)\][^\n]*|^XPASS[^\n]*|^FAILED [^\n]*", text, re.M)))[:40]
        signals += [f"FAILED {name}" for name in re.findall(r"^_{3,} (\S.*?) _{3,}$", text, re.M)
                    if not any(name in s for s in signals)][:40]
        summary = ""
        for pattern in (r"^((?:PASS|FAIL) .*)$", r"^=+ (.*(?:passed|failed|error)[^=]*) =+$", r"^((?:\d+ (?:passed|failed|errors?|skipped|xfailed|xpassed)[, ]*)+.* in [\d.]+s.*)$", r"^test result: (FAILED[^\n]*)$", r"^(error(?:\[E\d+\])?: [^\n]*)$"):
            found = re.findall(pattern, text, re.M)
            if found:
                summary = found[-1].strip()
                break
        cargo_runs = re.findall(r"^test result: \w+\. (\d+) passed; (\d+) failed; (\d+) ignored", text, re.M)
        if not summary and cargo_runs:
            totals = [sum(int(run[i]) for run in cargo_runs) for i in range(3)]
            summary = f"cargo: {totals[0]} passed, {totals[1]} failed, {totals[2]} ignored in {len(cargo_runs)} test binaries"
        if gate["cmd"][0] == "cargo":
            lock_dir = snap.root / (gate["cmd"][gate["cmd"].index("--manifest-path") + 1] if "--manifest-path" in gate["cmd"] else "Cargo.toml")
            lock = lock_dir.parent / "Cargo.lock"
            resolved = code == 0 or (lock.exists() and lock.stat().st_mtime >= started)
            ignored = self.lock_check(key, lock) if resolved else []
            if ignored:
                signals += [f"PATCH IGNORED: {line}" for line in ignored]
                code = code or "patch-ignored"
        if gate["cmd"][:2] == ["cargo", "test"]:
            self.prune_test_executables(started)
        status = "passed" if code == 0 else "failed"
        detail = summary or (f"exit {code}" if code else "")
        if code == "patch-ignored":
            detail = "built against a registry copy of a cohort crate; " + detail
        self.record(Step(key, gate["id"], status, time.time() - started, detail, str(logfile), signals))

    def prune_test_executables(self, since: float) -> None:
        """Delete the test binaries a gate linked (each embeds its whole graph); libraries stay for reuse."""
        deps = self.cargo_target / "debug" / "deps"
        for path in deps.glob("*") if deps.exists() else []:
            if "." not in path.name and path.is_file() and os.access(path, os.X_OK) and path.stat().st_mtime >= since - 1:
                path.unlink()

    def save_state(self) -> None:
        write_json(self.state_path, self.state)

    # ------------------------------------------------------------------- report
    def report(self) -> dict[str, Any]:
        members = {}
        for key in self.ordered(self.recipes):
            spec = self.manifest["members"][key]
            snap = self.snapshots.get(key)
            entry: dict[str, Any] = {"ref": spec.ref, "published": spec.published}
            if snap:
                entry.update({"kind": snap.kind, "commit": snap.commit, "branch": snap.branch, "dirty": snap.dirty,
                              "digest": snap.digest, "source": snap.source, "notes": snap.notes})
                if not spec.published:
                    entry["versions"] = self.member_versions(key)
            members[key] = entry
        statuses = [s.status for s in self.steps]
        first = next((s for s in sorted(self.steps, key=lambda s: self.layer_order(s.layer)) if s.status == "failed"), None)
        return {
            "schema_version": REPORT_SCHEMA,
            "cohort_id": self.manifest["cohort_id"],
            "build_root": str(self.build),
            "manifest_digest": digest_of(self.manifest["raw"]),
            "run_id": self.run_id,
            "tier": self.args.tier or self.manifest["tier"],
            "pin_alignment": self.manifest["pin_alignment"],
            "members": members,
            "crates": {name: {"member": self.crate_owner[name], "version": info["version"]} for name, info in sorted(self.crates.items())},
            "requirements": self.requirements,
            "alignments": self.alignments,
            "python_requirement_mismatches": getattr(self, "python_mismatches", []),
            "native": self.native,
            "python_environment": {"installed": self.installed, "cohort_wheels": sorted(self.wheels)},
            "steps": [s.__dict__ for s in self.steps],
            "result": "failed" if "failed" in statuses else ("blocked" if "blocked" in statuses else "passed"),
            "first_failure": first.__dict__ if first else None,
            "timings": self.timings,
            "layer_order": {layer: self.layer_order(layer) for layer in {s.layer for s in self.steps}},
            "disk_usage_bytes": dir_size(self.build),
        }

    def layer_order(self, layer: str) -> float:
        if layer in self.recipes:
            return self.recipes[layer].order
        return {"pins": -1, "env": self.recipes["sdk"].order - 0.5}.get(layer, 99)

    def member_versions(self, key: str) -> dict[str, Any]:
        component = {"key": key, "version_sources": [dict(s, allow_untracked=True) for s in self.recipes[key].data.get("version_sources", [])]}
        versions = release_lock.collect_versions(self.snapshots[key].root, component)
        crates = {name: info["version"] for name, info in self.crates.items() if self.crate_owner[name] == key}
        return {"sources": {k: (v.get("value") if isinstance(v, dict) else v) for k, v in versions.items()}, "crates": crates}

    def execute(self) -> int:
        started = time.time()
        stop = self.args.stop_after
        try:
            self.materialize()
            self.timings["sources"] = time.time() - started
            mark = time.time()
            self.analyse_rust()
            if stop != "pins":
                self.build_native()
            self.timings["native"] = time.time() - mark
            mark = time.time()
            wheels_ok = stop in (None, "wheels", "env") and self.build_wheels()
            self.timings["wheels"] = time.time() - mark
            mark = time.time()
            if wheels_ok and stop in (None, "env") and any("env" in g.get("needs", []) for _, g in self.gate_list()):
                self.build_env()
            self.timings["environment"] = time.time() - mark
            self.save_state()
            mark = time.time()
            if stop is None:
                self.run_gates()
            self.timings["gates"] = time.time() - mark
        except CohortError as exc:
            self.record(Step("cohort", "assembly", "failed", 0, str(exc).splitlines()[0]))
            log(str(exc))
        finally:
            self.save_state()
        self.timings["total"] = time.time() - started
        report = self.report()
        write_json(self.run_dir / "report.json", report)
        write_json(self.build / "latest-report.json", report)
        print_summary(report)
        return 0 if report["result"] == "passed" else 1


def dir_size(path: Path) -> int:
    total = 0
    for root, _, files in os.walk(path):
        for name in files:
            try:
                total += os.lstat(os.path.join(root, name)).st_size
            except OSError:
                pass
    return total


def print_summary(report: dict[str, Any]) -> None:
    print()
    print(f"Candidate cohort {report['cohort_id']} - run {report['run_id']} ({report['tier']} tier, pin alignment: {report['pin_alignment']})")
    print(f"{'layer':12} {'source':44} {'step':32} {'result':7} {'time':>6}  detail")
    by_layer: dict[str, list[dict[str, Any]]] = {}
    for step in report["steps"]:
        by_layer.setdefault(step["layer"], []).append(step)
    rank = report.get("layer_order", {})
    for layer, steps in sorted(by_layer.items(), key=lambda item: rank.get(item[0], 99)):
        member = report["members"].get(layer, {})
        if member.get("commit"):
            source = f"{member['commit'][:12]}{'+dirty' if member.get('dirty') else ''} {member.get('branch') or ''}".strip()
        elif member.get("published"):
            source = member.get("ref") or "published"
        else:
            source = ""
        for index, step in enumerate(steps):
            print(f"{layer if index == 0 else '':12} {source[:44] if index == 0 else '':44} {step['name'][:32]:32} "
                  f"{step['status'].upper():7} {step['seconds']:6.0f}  {step['detail'][:160]}")
            for signal in step.get("signals", [])[:8]:
                print(f"{'':12} {'':44}   > {signal[:200]}")
    published = [k for k, m in report["members"].items() if m.get("published") and not m.get("commit")]
    if published:
        print(f"Published members (registry artifacts): {', '.join(published)}")
    if report["alignments"]:
        print("Pin alignment applied in the build root (these consumer pins must change before release):")
        for record in report["alignments"]:
            print(f"  {record['consumer']}:{record['manifest']} {record['crate']} {record['requirement']} -> ={record['cohort_version']}")
    first = report.get("first_failure")
    print()
    if first:
        print(f"FIRST BROKEN LAYER: {first['layer']} - {first['name']}: {first['detail'][:300]}")
        if first.get("log"):
            print(f"  log: {first['log']}")
    else:
        print(f"RESULT: {report['result'].upper()}")
    total = report.get("timings", {}).get("total")
    if total is not None:
        print(f"Wall clock: {total / 60:.1f} min; build root size: {report.get('disk_usage_bytes', 0) / 1e9:.1f} GB")


# ------------------------------------------------------------------ release plan


def registry_has(kind: str, name: str, version: str) -> bool | None:
    urls = {
        "crates": f"https://crates.io/api/v1/crates/{name}/{version}",
        "pypi": f"https://pypi.org/pypi/{name}/{version}/json",
        "npm": f"https://registry.npmjs.org/{urllib.parse.quote(name, safe='@')}/{version}",
    }
    request = urllib.request.Request(urls[kind], headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status == 200
    except urllib.error.HTTPError as error:
        return False if error.code == 404 else None
    except OSError:
        return None


def workflow_triggers(repo: Path, commit: str) -> tuple[list[str], list[str]]:
    """Workflows of the tested commit that a tag push or a published GitHub release starts."""
    import yaml  # PyYAML: declared by the ecosystem CI environment

    tag_workflows, release_workflows = [], []
    names = git(repo, "ls-tree", "--name-only", f"{commit}:.github/workflows", check=False).splitlines()
    for name in sorted(n for n in names if n.endswith((".yml", ".yaml"))):
        doc = yaml.safe_load(git(repo, "show", f"{commit}:.github/workflows/{name}")) or {}
        on = doc.get("on", doc.get(True)) or {}
        if isinstance(on, dict):
            push = on.get("push") or {}
            if isinstance(push, dict) and push.get("tags"):
                tag_workflows.append(f"{name} (tags {', '.join(map(str, push['tags']))})")
            if "release" in on:
                release_workflows.append(name)
    return tag_workflows, release_workflows


def inspect_commit(build: Path, recipe: Recipe, commit: str, sibling: Path, offline: bool) -> tuple[Path | None, bool | None, str]:
    """Find a repository holding the tested commit and whether the default branch contains it."""
    has = lambda repo: repo.exists() and run(["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"], check=False).returncode == 0
    mirror = build / "git" / f"{recipe.key}.git"
    if offline:
        repo = sibling if has(sibling) else (mirror if has(mirror) else None)
        if repo is None:
            return None, None, "origin/main"
        default = git(repo, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD", check=False) or "origin/main"
        known = run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", default], check=False).returncode == 0
        if not known:
            return repo, None, default
        return repo, run(["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, default], check=False).returncode == 0, default
    if not mirror.exists():
        mirror.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "--bare", "-q", str(mirror)])
    if not has(mirror):
        source = str(sibling) if has(sibling) else f"https://github.com/{recipe.repo}.git"
        run(["git", "-C", str(mirror), "fetch", "-q", "--no-tags", source, commit], check=False)
    if not has(mirror):
        return None, None, "the default branch"
    url = f"https://github.com/{recipe.repo}.git"
    head = run(["git", "ls-remote", "--symref", url, "HEAD"]).stdout.decode()
    match = re.search(r"ref: refs/heads/(\S+)\s+HEAD", head)
    default = match.group(1) if match else "main"
    run(["git", "-C", str(mirror), "fetch", "-q", "--no-tags", url, f"+refs/heads/{default}:refs/remotes/origin/{default}"])
    contained = run(["git", "-C", str(mirror), "merge-base", "--is-ancestor", commit, f"refs/remotes/origin/{default}"], check=False).returncode == 0
    return mirror, contained, f"origin/{default}"


def remote_tag_commit(repo_slug: str, tag: str) -> str | None:
    """Commit a public tag points at (peeled), or None when the tag does not exist."""
    out = run(["git", "ls-remote", "--tags", f"https://github.com/{repo_slug}.git", f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"]).stdout.decode()
    refs = dict(reversed(line.split("\t")) for line in out.splitlines() if "\t" in line)
    return refs.get(f"refs/tags/{tag}^{{}}") or refs.get(f"refs/tags/{tag}")


def release_plan(args: argparse.Namespace) -> int:
    report = read_json(Path(args.report))
    recipes, _ = load_recipes(Path(args.members))
    if report.get("schema_version") != REPORT_SCHEMA:
        raise CohortError("not a candidate-cohort report")
    blockers: list[str] = []
    if report["result"] != "passed":
        blockers.append(f"the cohort run {report['run_id']} is {report['result']}, not passed (first failure: "
                        f"{(report.get('first_failure') or {}).get('layer')}/{(report.get('first_failure') or {}).get('name')})")
    if report["tier"] not in ("fast", "full"):
        blockers.append("unknown tier")
    if report["alignments"]:
        blockers.append("pins were aligned in the build root; commit the consumer pin updates listed under 'Consumer pin updates' and re-run the cohort")
    if report.get("python_requirement_mismatches"):
        blockers.append("cohort wheels were installed against refusing Python requirements: " + "; ".join(report["python_requirement_mismatches"]))
    plan = []
    order = sorted((k for k, m in report["members"].items() if not m["published"]), key=lambda k: recipes[k].order)
    released_versions: dict[str, str] = {}
    for key in order:
        member, recipe = report["members"][key], recipes[key]
        release = recipe.data.get("release", {})
        item: dict[str, Any] = {"member": key, "repo": recipe.repo, "commit": member.get("commit"), "blockers": [], "steps": []}
        plan.append(item)
        if release.get("excluded"):
            item["excluded"] = release["excluded"]
            continue
        if member.get("dirty"):
            item["blockers"].append("tested from a dirty working tree; commit and re-run the cohort")
        if member.get("kind") == "path" and not member.get("dirty"):
            item["steps"].append("tested from a clean working tree at its HEAD commit")
        versions = member.get("versions", {})
        sources = versions.get("sources", {})
        version = sources.get(recipe.data.get("release_version_key"))
        if isinstance(version, dict):
            version = version.get("project_version")
        distinct = {v if not isinstance(v, dict) else v.get("project_version") for v in sources.values() if v}
        if len(distinct) > 1 and key not in ("methods",):
            item["blockers"].append(f"version sources disagree: {sources}")
        item["version"] = version
        item["tags"] = [t.format(version=version) for t in release.get("tags", [])]
        publishes = recipe.data.get("publishes", {})
        crate_versions = versions.get("crates", {})
        registry = []
        for kind in ("crates", "pypi", "npm"):
            for name in publishes.get(kind, []):
                v = crate_versions.get(name, version) if kind == "crates" else version
                state = registry_has(kind, name, v) if not args.offline else None
                registry.append({"registry": kind, "name": name, "version": v, "published": state})
                if state:
                    item["blockers"].append(f"{kind} {name} {v} is already published: bump the version and re-run the cohort")
        for crate, tag in release.get("crate_tags", {}).items():
            if crate in crate_versions:
                item["tags"].append(tag.format(crate_version=crate_versions[crate]))
        item["registry"] = registry
        sibling = Path(args.workspace_root) / recipe.sibling
        if not args.offline:
            for tag in item["tags"]:
                existing = remote_tag_commit(recipe.repo, tag)
                if existing and existing != member["commit"]:
                    item["blockers"].append(f"tag {tag} already exists at {existing[:12]}, not the tested {member['commit'][:12]}")
                elif existing:
                    item["steps"].append(f"tag {tag} already points at the tested commit")
        repo, on_default, default = inspect_commit(Path(report.get("build_root", "")), recipe, member["commit"], sibling, args.offline)
        if repo is None:
            item["blockers"].append(f"tested commit {member['commit'][:12]} is not available locally or on GitHub")
        else:
            tags, releases = workflow_triggers(repo, member["commit"])
            item["workflows"] = tags + ([f"{r} (GitHub release published)" for r in releases] if release.get("github_release") else [])
            item["on_default_branch"] = on_default
            if on_default is False:
                item["blockers"].append(f"tested commit is not on {default}: merge it so that {default} contains exactly this commit "
                                        "(fast-forward, or a merge commit whose parent is the tested commit), then tag the tested commit")
            elif on_default is None:
                item["blockers"].append(f"could not verify that the tested commit is on {default}")
        action = "create GitHub release" if release.get("github_release") else "push tag"
        item["steps"].append(f"{action} {', '.join(item['tags'])} at {member['commit']}")
        item["steps"].append("wait until " + ", ".join(f"{r['registry']}:{r['name']}=={r['version']}" for r in registry) + " are available")
        released_versions.update({r["name"]: r["version"] for r in registry})
    follow_ups = []
    for record in report["requirements"]:
        if record in report["alignments"]:
            continue  # listed below as a prerequisite
        if record["crate"] in released_versions and record["requirement"].startswith("=") and record["requirement"][1:] != record["cohort_version"]:
            follow_ups.append(f"{record['consumer']}:{record['manifest']} pins {record['crate']} {record['requirement']}; "
                              f"update to {record['cohort_version']} (or a minor range) after release")
    for record in report["alignments"]:
        follow_ups.append(f"{record['consumer']}:{record['manifest']} must require {record['crate']} {record['cohort_version']} "
                          f"(currently {record['requirement']}) before its commit can be tested and released")
    blocked = blockers + [f"{p['member']}: {b}" for p in plan for b in p["blockers"]]
    output = {"cohort_id": report["cohort_id"], "run_id": report["run_id"], "manifest_digest": report["manifest_digest"],
              "blockers": blocked, "plan": plan, "consumer_pin_updates": follow_ups}
    print_release_plan(output)
    if args.json_out:
        write_json(Path(args.json_out), output)
    if not args.execute:
        return 0 if not blocked else 2
    if blocked:
        log("refusing to execute: the plan has blockers")
        return 2
    if args.confirm != report["manifest_digest"][:16]:
        log(f"refusing to execute: pass --confirm {report['manifest_digest'][:16]} to release exactly this tested cohort")
        return 2
    return execute_plan(output, recipes, args)


def print_release_plan(plan: dict[str, Any]) -> None:
    print(f"Release plan for cohort {plan['cohort_id']} (run {plan['run_id']})")
    for index, item in enumerate(plan["plan"], 1):
        print(f"{index}. {item['member']} ({item['repo']}) @ {item.get('commit')}")
        if item.get("excluded"):
            print(f"   not released here: {item['excluded']}")
            continue
        print(f"   version {item.get('version')}; tags: {', '.join(item.get('tags', []))}; on default branch: {item.get('on_default_branch')}")
        for wf in item.get("workflows", []):
            print(f"   fires: {wf}")
        for reg in item.get("registry", []):
            state = {True: "ALREADY PUBLISHED", False: "not yet published", None: "unknown"}[reg["published"]]
            print(f"   {reg['registry']}: {reg['name']} {reg['version']} ({state})")
        for step in item["steps"]:
            print(f"   - {step}")
        for blocker in item["blockers"]:
            print(f"   BLOCKER: {blocker}")
    if plan["consumer_pin_updates"]:
        print("Consumer pin updates:")
        for line in plan["consumer_pin_updates"]:
            print(f"  - {line}")
    print("BLOCKED:" if plan["blockers"] else "READY: no blockers.")
    for blocker in plan["blockers"]:
        print(f"  - {blocker}")


def execute_plan(plan: dict[str, Any], recipes: dict[str, Recipe], args: argparse.Namespace) -> int:
    """Tag the tested commits in order and wait for each registry before the next member."""
    if not os.environ.get("GH_TOKEN"):
        raise CohortError("GH_TOKEN is required to create tags or releases")
    login = run(["gh", "api", "user", "-q", ".login"]).stdout.decode().strip()
    if login != args.expected_login:
        raise CohortError(f"authenticated as {login!r}, expected {args.expected_login!r}")
    for item in plan["plan"]:
        if item.get("excluded"):
            continue
        recipe = recipes[item["member"]]
        commit = item["commit"]
        for tag in item["tags"]:
            remote = run(["gh", "api", f"repos/{recipe.repo}/git/ref/tags/{tag}", "-q", ".object.sha"], check=False)
            if remote.returncode == 0:
                existing = remote.stdout.decode().strip()
                if existing != commit:
                    tag_object = run(["gh", "api", f"repos/{recipe.repo}/git/tags/{existing}", "-q", ".object.sha"], check=False)
                    if tag_object.stdout.decode().strip() != commit:
                        raise CohortError(f"{recipe.repo} tag {tag} exists and does not point at the tested {commit}")
                log(f"{recipe.repo}: {tag} already at the tested commit")
                continue
            if recipe.data.get("release", {}).get("github_release"):
                run(["gh", "release", "create", tag, "--repo", recipe.repo, "--target", commit, "--title", tag, "--generate-notes"])
            else:
                tag_sha = run(["gh", "api", f"repos/{recipe.repo}/git/tags", "-f", f"tag={tag}", "-f", f"message={tag}",
                               "-f", f"object={commit}", "-f", "type=commit", "-q", ".sha"]).stdout.decode().strip()
                run(["gh", "api", f"repos/{recipe.repo}/git/refs", "-f", f"ref=refs/tags/{tag}", "-f", f"sha={tag_sha}"])
            log(f"{recipe.repo}: created {tag} at {commit}")
        deadline = time.time() + args.wait_minutes * 60
        pending = list(item["registry"])
        while pending:
            pending = [r for r in pending if not registry_has(r["registry"], r["name"], r["version"])]
            if not pending:
                break
            if time.time() > deadline:
                raise CohortError(f"{item['member']}: still waiting for {pending}; resume release-plan --execute later (completed tags are skipped)")
            log(f"{item['member']}: waiting for {', '.join(r['name'] for r in pending)}")
            time.sleep(60)
    return 0


# --------------------------------------------------------------------------- init


def init_manifest(args: argparse.Namespace) -> int:
    recipes, _ = load_recipes(Path(args.members))
    workspace = Path(args.workspace_root).resolve()
    members: dict[str, Any] = {}
    for key, recipe in sorted(recipes.items(), key=lambda kv: kv[1].order):
        members[key] = {"ref": "published"}
        if args.from_siblings and key in args.from_siblings:
            sibling = workspace / recipe.sibling
            branch = git(sibling, "branch", "--show-current", check=False)
            head = git(sibling, "rev-parse", "HEAD", check=False)
            dirty = bool(git(sibling, "status", "--porcelain", check=False))
            members[key] = {"ref": f"path:{sibling}", "note": f"{branch or 'detached'} at {head[:12]}{' (dirty)' if dirty else ''}"}
    for item in args.set or []:
        key, _, value = item.partition("=")
        members[key] = {"ref": value}
    manifest = {"schema_version": MANIFEST_SCHEMA, "cohort_id": args.cohort_id, "description": "",
                "python": "3.11", "tier": "fast", "pin_alignment": "refuse", "members": members}
    write_json(Path(args.out), manifest)
    log(f"wrote {args.out}")
    return 0


# ---------------------------------------------------------------------------- cli


def default_workspace() -> Path:
    env = os.environ.get("N4A_WORKSPACE_ROOT")
    if env:
        return Path(env)
    root = ROOT.parent
    return root.parent if root.name == "_worktrees" else root


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--members", default=str(DEFAULT_MEMBERS), help="member recipes (n4a.cohort-members/v1)")
    parser.add_argument("--workspace-root", default=str(default_workspace()), help="directory holding the sibling checkouts")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="write a cohort manifest (published members unless told otherwise)")
    init.add_argument("--out", required=True)
    init.add_argument("--cohort-id", default="local")
    init.add_argument("--from-siblings", nargs="*", default=[], help="members to take from their sibling working trees")
    init.add_argument("--set", action="append", help="key=ref (commit, branch, path:<dir>, published or published:latest)")

    run_p = sub.add_parser("run", help="assemble the cohort from source and run its gates")
    run_p.add_argument("--manifest", help="cohort manifest (n4a.candidate-cohort/v1); members default to published")
    run_p.add_argument("--set", action="append", help="override one member: key=ref")
    run_p.add_argument("--build-root", default=os.environ.get("N4A_COHORT_BUILD_ROOT") or str(default_workspace() / "_cohort-build"))
    run_p.add_argument("--tier", choices=["fast", "full"], help="gate tier (default: the manifest's, else fast)")
    run_p.add_argument("--only", nargs="*", help="run only these gate ids")
    run_p.add_argument("--skip", nargs="*", help="skip these gate ids")
    run_p.add_argument("--no-cache", action="store_true", help="re-run gates whose inputs did not change")
    run_p.add_argument("--stop-after", choices=["pins", "native", "wheels", "env"], help="assemble up to this stage, run no gate")

    summary = sub.add_parser("summary", help="print the summary of the latest (or a given) report")
    summary.add_argument("--report", default=None)
    summary.add_argument("--build-root", default=os.environ.get("N4A_COHORT_BUILD_ROOT") or str(default_workspace() / "_cohort-build"))

    plan = sub.add_parser("release-plan", help="print (or execute) the ordered release of a green cohort's tested commits")
    plan.add_argument("--report", required=True)
    plan.add_argument("--json-out")
    plan.add_argument("--offline", action="store_true", help="do not query the registries")
    plan.add_argument("--execute", action="store_true", help="create the tags/releases (maintainer only)")
    plan.add_argument("--confirm", default="", help="first 16 hex digits of the tested manifest digest")
    plan.add_argument("--expected-login", default="GBeurier")
    plan.add_argument("--wait-minutes", type=int, default=120)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.command == "init":
            return init_manifest(args)
        if args.command == "run":
            return Cohort(args).execute()
        if args.command == "summary":
            path = Path(args.report) if args.report else Path(args.build_root) / "latest-report.json"
            report = read_json(path)
            print_summary(report)
            return 0 if report["result"] == "passed" else 1
        if args.command == "release-plan":
            return release_plan(args)
    except CohortError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
