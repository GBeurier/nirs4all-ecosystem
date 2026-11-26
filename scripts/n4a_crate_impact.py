"""Compute reverse Cargo manifest dependencies at exact public repository revisions."""

import base64
from concurrent.futures import ThreadPoolExecutor
from pathlib import PurePosixPath
import posixpath
import tomllib


def fetch_manifests(api, origin, sha):
    tree = api(f"repos/{origin}/git/trees/{sha}?recursive=1")
    if tree["truncated"]:
        raise ValueError(f"incomplete manifest inventory: {origin}@{sha}")
    files = [f for f in tree["tree"] if PurePosixPath(f["path"]).name == "Cargo.toml" and f["type"] == "blob"]

    def read(entry):
        blob = api(f"repos/{origin}/git/blobs/{entry['sha']}")
        if blob["encoding"] != "base64":
            raise ValueError(f"unsupported manifest encoding: {origin}/{entry['path']}")
        manifest = tomllib.loads(base64.b64decode(blob["content"]).decode())
        return entry["path"], manifest

    with ThreadPoolExecutor(max_workers=4) as pool:
        return dict(pool.map(read, files))


def dependencies(manifest):
    for table in [manifest, *manifest.get("target", {}).values()]:
        for key in ("dependencies", "build-dependencies", "dev-dependencies"):
            yield from table.get(key, {}).items()


def nearest_workspace(path, manifest, manifests):
    folder = PurePosixPath(path).parent
    explicit = manifest["package"].get("workspace")
    if explicit:
        return posixpath.normpath(str(folder / explicit / "Cargo.toml"))
    for parent in (folder, *folder.parents):
        ref = str(parent / "Cargo.toml")
        if "workspace" in manifests.get(ref, {}):
            return ref
    return None


def affected_crates(inventory, origins, changes):
    """Include optional, development and target edges. Actual Cargo resolution gates each profile."""
    packages, registry = {}, {}
    for repo, manifests in inventory.items():
        for path, manifest in manifests.items():
            package = manifest.get("package")
            if not package:
                continue
            key = f"{repo}/{path}"
            workspace = nearest_workspace(path, manifest, manifests)
            packages[key] = (repo, path, manifest, workspace)
            if package.get("publish") is not False and package.get("publish") != []:
                registry.setdefault(package["name"], []).append(key)

    reverse = {}
    for consumer, (repo, path, manifest, workspace) in packages.items():
        for alias, spec in dependencies(manifest):
            folder = PurePosixPath(path).parent
            if isinstance(spec, dict) and spec.get("workspace"):
                if workspace is None:
                    raise ValueError(f"missing workspace for {consumer}: {alias}")
                spec = inventory[repo][workspace]["workspace"]["dependencies"][alias]
                folder = PurePosixPath(workspace).parent
            detail = spec if isinstance(spec, dict) else {"version": spec}
            name = detail.get("package", alias)
            if "path" in detail:
                dependency = posixpath.normpath(f"{repo}/{folder}/{detail['path']}/Cargo.toml")
                providers = [dependency] if dependency in packages else []
            elif "registry" in detail:
                providers = []
            elif "git" in detail:
                url = detail["git"].removesuffix("/").removesuffix(".git")
                providers = [key for key, (owner, _, candidate, _) in packages.items()
                             if url == f"https://github.com/{origins[owner]}" and candidate["package"]["name"] == name]
            else:
                providers = registry.get(name, [])
            for provider in providers:
                reverse.setdefault(provider, set()).add(consumer)

    roots = set()
    for repo, (paths, scope) in changes.items():
        owned = [key for key in packages if packages[key][0] == repo]
        if paths is None:
            roots.update(owned)
            continue
        for path in paths:
            dirs = [key for key in owned if PurePosixPath(path).is_relative_to(PurePosixPath(packages[key][1]).parent)]
            if dirs:
                closest = max(dirs, key=lambda k: len(PurePosixPath(k).parts))
                relative = PurePosixPath(path).relative_to(PurePosixPath(packages[closest][1]).parent)
                if relative.parts and relative.parts[0] in {"src", "tests", "benches", "examples", "build.rs"}:
                    roots.add(closest)
                    continue
            if scope == "repository":
                # A workspace edit, a deleted package or a shared native input
                # can affect more than the nearest manifest.
                roots.update(owned)
                break
    impacted = set(roots)
    pending = list(roots)
    while pending:
        for consumer in reverse.get(pending.pop(), set()) - impacted:
            impacted.add(consumer)
            pending.append(consumer)
    return {
        "scope": "declared-cargo-dependencies-all-targets-and-features",
        "roots": sorted(roots),
        "crates": {k: {"name": packages[k][2]["package"]["name"], "consumers": sorted(reverse.get(k, set()))}
                   for k in sorted(impacted)},
    }
