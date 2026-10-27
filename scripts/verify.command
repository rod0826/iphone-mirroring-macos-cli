#!/bin/bash
set -euo pipefail
base_dir="$(cd -- "$(dirname -- "$0")" && pwd -P)"
cd "$base_dir"
if [ ! -f SHA256SUMS ]; then
  echo 'SHA256SUMS is missing; installation stopped.' >&2
  exit 1
fi
if ! /usr/bin/shasum -a 256 --check --quiet SHA256SUMS; then
  echo 'SHA-256 mismatch; installation stopped. Obtain a fresh ZIP.' >&2
  exit 1
fi
echo 'SHA-256 verification passed (extracted files).'
