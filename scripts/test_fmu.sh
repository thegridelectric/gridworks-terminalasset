#!/usr/bin/env bash
#
# Run the fmu tests in a Linux container of the host's processor, the one
# place the FMUs in build/ load: fmpy loads an FMU's binary, which the
# OpenModelica build makes for Linux. The repo is copied into the container
# read-only and synced there from the lock file. A test marked both fmu and
# live reaches the dev broker on localhost:5672: through the broker
# container's own network when a container named gw-dev-rabbit is running
# (a laptop), else through the host's (CI, where the broker is a service
# container with its port on the runner).
#
# Usage: scripts/test_fmu.sh   (after scripts/build_fmu.sh)
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE=ghcr.io/astral-sh/uv:python3.12-bookworm
if docker inspect gw-dev-rabbit >/dev/null 2>&1; then
  NETWORK=container:gw-dev-rabbit
else
  NETWORK=host
fi

docker run --rm --network "$NETWORK" -v "$REPO":/w:ro "$IMAGE" sh -c '
  cp -r /w /tmp/w && cd /tmp/w && rm -rf .venv &&
  uv sync --all-groups --locked -q &&
  uv run pytest -q -p no:cacheprovider -o addopts="" -m fmu'
