#!/usr/bin/env bash
# Run dev/shot.sh inside the pinned Plasma 6.8 image (built on first use).
# Needs /dev/dri on this machine.
# Usage: dev/shot-docker.sh <out.png> [--install] [app...]
# The output path must be inside the repo; it is mounted at /repo.
set -euo pipefail

repo=$(cd "$(dirname "$0")/.." && pwd)
image=golden-delicious-shot:6.8
docker image inspect "$image" >/dev/null 2>&1 || docker build -t "$image" "$repo/dev/docker"

out=$(realpath -m "$1"); shift
rel=${out#"$repo"/}
[[ $rel != "$out" ]] || { echo "output must be inside $repo" >&2; exit 1; }

docker run --rm --shm-size=512m --device /dev/dri -v "$repo:/repo" -e SHOT_W -e SHOT_H -e SHOT_WAIT \
  "$image" dev/shot.sh "/repo/$rel" "$@"
