from __future__ import annotations

import configparser
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_SUBMODULES = {
    "dag-ml",
    "dag-ml-data",
    "nirs4all",
    "nirs4all-aom",
    "nirs4all-benchmarks",
    "nirs4all-cluster",
    "nirs4all-cockpit",
    "nirs4all-core",
    "nirs4all-datasets",
    "nirs4all-formats",
    "nirs4all-io",
    "nirs4all-methods",
    "nirs4all-org",
    "nirs4all-papers",
    "nirs4all-providers",
    "nirs4all-quality",
    "nirs4all-repository",
    "nirs4all-studio",
    "nirs4all-tools",
    "nirs4all-ui",
    "nirs4all-web",
}
OUT_OF_SCOPE_SUBMODULES = {"nirs4all-drafts", "nirs4all-lab", "nirs4all-lite"}


def _gitmodules() -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    parser.read(ROOT / ".gitmodules", encoding="utf-8")
    return parser


def _submodule_paths(parser: configparser.ConfigParser) -> dict[str, str]:
    paths: dict[str, str] = {}
    for section in parser.sections():
        if not section.startswith("submodule "):
            continue
        name = section.split('"', 2)[1]
        paths[name] = parser[section]["path"]
    return paths


def test_gitmodules_tracks_public_refactor_topology_only() -> None:
    parser = _gitmodules()
    paths = _submodule_paths(parser)

    assert set(paths) == PUBLIC_SUBMODULES
    assert OUT_OF_SCOPE_SUBMODULES.isdisjoint(paths)
    for name in PUBLIC_SUBMODULES:
        section = f'submodule "{name}"'
        assert parser[section]["path"] == name
        assert parser[section]["url"] == f"https://github.com/GBeurier/{name}.git"
        assert parser[section]["branch"] == "main"


def test_public_submodule_gitlinks_match_gitmodules() -> None:
    parser = _gitmodules()
    paths = set(_submodule_paths(parser).values())
    listed = subprocess.run(
        ["git", "ls-files", "-s"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    gitlinks = {
        line.split("\t", 1)[1]
        for line in listed.stdout.splitlines()
        if line.startswith("160000 ")
    }

    assert gitlinks == paths
