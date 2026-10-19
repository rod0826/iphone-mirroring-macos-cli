#!/bin/bash
set -euo pipefail
base_dir="$(cd -- "$(dirname -- "$0")" && pwd -P)"
install_dir="$HOME/Applications/IPhone-Mirroring-CLI-0.1.0"
if [ "$(uname -m)" != "arm64" ]; then
  echo '이 패키지는 Apple Silicon Mac용입니다.'
  exit 1
fi
if [ -e "$install_dir" ] || [ -L "$install_dir" ]; then
  echo "설치 위치가 이미 있습니다: $install_dir"
  echo '기존 폴더를 보관하거나 이름을 바꾼 뒤 다시 실행하세요. 자동으로 덮어쓰지 않습니다.'
  exit 1
fi
mkdir -p "$HOME/Applications"
/usr/bin/ditto "$base_dir" "$install_dir"
echo "설치 완료: $install_dir"
echo '폴더 안의 먼저읽기.md에서 최초 연결과 손쉬운 사용 권한 설정을 확인하세요.'
/usr/bin/open "$install_dir"
