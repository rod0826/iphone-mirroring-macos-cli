#!/bin/bash
set -euo pipefail
base_dir="$(cd -- "$(dirname -- "$0")" && pwd -P)"
exec "$base_dir/cli/cli-anything-iphone-mirroring" "$@"
