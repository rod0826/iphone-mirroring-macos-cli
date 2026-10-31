#!/bin/bash
set -euo pipefail
base_dir="$(cd -- "$(dirname -- "$0")" && pwd -P)"
/bin/bash "$base_dir/검증.command"
install_root="${IPHONE_MIRRORING_INSTALL_ROOT:-$HOME/Applications}"
install_dir="$install_root/IPhone-Mirroring-CLI"
if [ "$(uname -m)" != "arm64" ]; then
  echo '이 패키지는 Apple Silicon Mac용입니다.' >&2
  exit 1
fi
if [ -L "$install_dir" ]; then
  echo '설치 대상이 심볼릭 링크입니다. 자동 교체하지 않습니다.' >&2
  exit 1
fi
if [ -e "$install_dir" ]; then
  product="$(/usr/bin/plutil -extract product raw -o - "$install_dir/BUILD.json" 2>/dev/null || true)"
  if [ "$product" != "iphone-mirroring-macos-cli" ] || [ ! -f "$install_dir/cli/cli-anything-iphone-mirroring" ]; then
    echo "알 수 없는 기존 폴더입니다. 자동 교체하지 않습니다: $install_dir" >&2
    exit 1
  fi
fi
mkdir -p "$install_root"
stage_dir="$(mktemp -d "$install_root/.IPhone-Mirroring-CLI.stage.XXXXXX")"
trap 'if [ -n "$stage_dir" ] && [ -d "$stage_dir" ]; then /bin/rm -rf -- "$stage_dir"; fi' EXIT
/usr/bin/ditto "$base_dir" "$stage_dir"
/bin/bash "$stage_dir/검증.command"
backup_dir=""
if [ -e "$install_dir" ]; then
  backup_dir="$(mktemp -d "$install_root/.IPhone-Mirroring-CLI.backup.XXXXXX")"
  /bin/rmdir "$backup_dir"
  /bin/mv "$install_dir" "$backup_dir"
fi
if ! /bin/mv "$stage_dir" "$install_dir"; then
  if [ -n "$backup_dir" ]; then /bin/mv "$backup_dir" "$install_dir"; fi
  exit 1
fi
stage_dir=""
echo "설치 완료: $install_dir"
if [ -n "$backup_dir" ]; then echo "기존 버전 보관: $backup_dir"; fi
echo '시작.command 또는 CLI doctor --reveal-helper로 시작하세요. 새 서명은 권한 재등록이 필요할 수 있습니다.'
if [ "${IPHONE_MIRRORING_NO_OPEN:-0}" != "1" ]; then /usr/bin/open "$install_dir"; fi
