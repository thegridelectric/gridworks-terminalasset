#!/usr/bin/env bash
#
# The gate for this repo: the GitHub workflow runs this script and nothing
# else, so a local pass is a CI pass. Run it before committing.
#
# The live tests need the dev broker on localhost:5672 (gridworks-base
# arm.sh / x86.sh; CI runs the same baked image as a service container).
# The fmu tests need the plants' FMUs, which this script generates with
# docker, and the FMUs load on Linux only, so those tests run in a Linux
# container (scripts/test_fmu.sh) and the host runs the rest.
#
# Usage: ./ci.sh
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

step() { printf '\n=== %s ===\n' "$1"; shift; "$@"; }

step "uv sync (locked)" uv sync --all-groups --locked
step "ruff check" uv run ruff check --no-fix --no-cache .
step "ruff format --check" uv run ruff format --check --no-cache .
step "pyright" uv run pyright
step "sema snapshot staging check" uv run python -P \
  src/gwta/sema/check_staging.py src/gwta/sema_seed_request.yaml --deploy-branch main

if ! nc -z localhost 5672 2>/dev/null; then
  echo "ERROR: no broker on localhost:5672 — start the dev rabbit (gridworks-base arm.sh or x86.sh)." >&2
  exit 1
fi
step "generate the FMUs" scripts/build_fmu.sh
# -o addopts="" lifts pyproject's default `-m 'not live and not fmu'` so the
# live tests run too; the fmu tests run in the container.
step "tests (offline + live)" uv run pytest -q -o addopts="" -m "not fmu"
step "tests (fmu, in a Linux container)" scripts/test_fmu.sh

printf '\nAll checks passed.\n'
