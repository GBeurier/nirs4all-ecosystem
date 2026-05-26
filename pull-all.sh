#!/usr/bin/env bash
set -euo pipefail

# Met à jour le dépôt parent puis (re)synchronise tous les submodules.
git pull --ff-only
git submodule update --init --recursive
git submodule update --remote --merge
