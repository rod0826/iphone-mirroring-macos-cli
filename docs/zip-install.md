# iPhone Mirroring CLI 0.1.2 — 회사 Mac 테스트 ZIP

비공식 실험용 PoC입니다. Apple의 검토·승인·인증을 받지 않았습니다.
Apple Silicon Mac용이며 Python 런타임이 포함돼 있습니다. 별도 Python·Homebrew·Xcode 설치 없이 사용합니다.
Apple iPhone 미러링 앱과 사용자 본인이 완료한 최초 연결·인증이 필요합니다.
검증 환경은 macOS 26.6.2 / Apple iPhone 미러링 1.6입니다. 빌드 하한 macOS 15와 다른 조합의 호환성을 보증하지 않습니다.

## 1. ZIP 하나로 설치

1. ZIP을 압축 해제합니다.
2. `검증.command`를 실행해 SHA256SUMS 검사를 통과하는지 확인합니다.
3. 실행 중인 이전 CLI·REPL·보조 앱을 종료한 후 `설치.command`를 실행합니다.

0.1.2부터 설치 경로는 버전 없는 아래 위치로 고정됩니다.

```text
~/Applications/IPhone-Mirroring-CLI
```

다음 버전도 이 경로를 사용합니다. 설치기는 임시 폴더에 복사·검증을 마친 뒤, 같은 제품의 기존 설치본만 보관하고 교체합니다. 기존본은 같은 상위 폴더의 숨김 `.IPhone-Mirroring-CLI.backup.XXXXXX`에 남습니다. 알 수 없는 폴더·심볼릭 링크는 교체하지 않습니다.
0.1.0·0.1.1의 버전별 폴더는 자동 변경·삭제하지 않습니다. 새 버전 작동 확인 후 옛 폴더와 옛 접근성 항목만 수동 정리하세요.

체크섬은 압축 해제된 파일의 손상·변경 확인용이며 출처 인증을 대신하지 않습니다. 외부 `.zip.sha256` 파일도 받았다면 ZIP 자체를 추가로 확인할 수 있지만 전달에 필수는 아닙니다. 관리자 암호나 전역 PATH·보안 설정을 설치기가 바꾸지 않습니다.

## 2. 버전과 권한 확인

터미널에서 실행합니다.

```sh
iphone_cli="$HOME/Applications/IPhone-Mirroring-CLI/cli/cli-anything-iphone-mirroring"
"$iphone_cli" --version
"$iphone_cli" doctor --reveal-helper
```

`--version`은 보조 앱 실행 없이 CLI 버전을 표시합니다. doctor는 cli_version과 helper_version을 구분해 표시합니다. `--reveal-helper`는 Finder에서 실제 보조 앱을 선택해 보여 줍니다. Finder의 선택된 앱을 시스템 설정 → 개인정보 보호 및 보안 → 손쉬운 사용 목록으로 드래그해 등록하고 켭니다. 권한은 자동 부여하지 않습니다.

보조 앱의 고정 설치 경로:

```text
~/Applications/IPhone-Mirroring-CLI/cli/_internal/cli_anything/iphone_mirroring/bin/IPhoneMirroringCLI.app
```

같은 이름의 항목이 여러 개면 우클릭 → Finder에서 보기로 경로를 확인하고, 지금 설치한 앱의 항목만 사용합니다. 보조 앱을 더블클릭하면 CLI 보조 앱이라는 안내 창이 뜨도록 변경했습니다. 실제 명령은 `시작.command`의 REPL 또는 CLI로 실행합니다.

**고정 경로여도 이번 임시 서명은 업데이트 후 접근성 재등록이 필요할 수 있습니다.** 켜져 있는데 doctor가 false이면 해당 앱 항목만 제거·재추가하세요. 0.1.1의 허용 기록이 0.1.2에 이어진다고 보장하지 않습니다.

## 3. 실행 차단·종료 코드 137

이번 패키지도 Developer ID 서명·공증을 받지 않았습니다. 회사 정책을 먼저 확인하고 신뢰할 수 있는 전달본만 사용하세요. 출력 없이 Killed: 9 / exit 137로 종료되는 원인 중 하나는 다운로드 격리 속성이지만, 이 코드만으로 원인을 확정할 수 없습니다.

먼저 내부 파일을 검증합니다. 스크립트가 더블클릭으로 열리지 않으면 터미널에서 아래처럼 실행할 수 있습니다.

```sh
/bin/bash "$HOME/Applications/IPhone-Mirroring-CLI/검증.command"
xattr -l "$HOME/Applications/IPhone-Mirroring-CLI/cli/cli-anything-iphone-mirroring"
codesign --verify --strict "$HOME/Applications/IPhone-Mirroring-CLI/cli/_internal/cli_anything/iphone_mirroring/bin/IPhoneMirroringCLI.app"
```

설치 전이라면 압축을 푼 폴더의 검증.command를 사용합니다. Apple의 [개별 앱 열기 안내](https://support.apple.com/102445)를 참고하세요.
**무결성 검증을 통과했고 회사 정책상 허용되며 사용자가 이 전달본 실행을 선택한 경우에만**, 설치 폴더 한정으로 다음 수동 명령을 사용할 수 있습니다.

```sh
xattr -dr com.apple.quarantine "$HOME/Applications/IPhone-Mirroring-CLI"
```

이는 해당 파일의 최초 실행 검사를 생략하게 합니다. sudo나 전역 Gatekeeper 해제는 필요하지 않습니다. Downloads·Applications 전체에는 적용하지 마세요. 설치기와 검증기는 이 속성을 자동 제거하지 않으며, 재설치한 파일에는 다시 붙을 수 있습니다.

자체 서명 인증서만으로 Developer ID 공증을 대신할 수는 없습니다. 안정적인 배포 서명과 권한 유지의 검증은 추후 작업이며, 이번 버전에서 해결됐다고 주장하지 않습니다.

## 4. 회사 Mac 재검증

Apple iPhone 미러링을 연결하고 창을 **현재 데스크톱(Space)**에 둡니다.

```sh
"$iphone_cli" inspect
"$iphone_cli" --dry-run home
"$iphone_cli" home
"$iphone_cli" search '날씨'
"$iphone_cli" key backspace
"$iphone_cli" app-switcher
"$iphone_cli" home
```

명령마다 실제 화면을 확인합니다. `home`은 기본적으로 간격을 두고 2회 요청합니다. 앱 전환 화면 아래의 Spotlight를 닫기 위한 보완이며 자동으로 화면 도착을 검증하지는 않습니다. 원래 한 번 동작은 다음과 같습니다.

```sh
"$iphone_cli" home --presses 1
```

search도 먼저 홈 2회 요청 후 Spotlight를 열고 입력합니다. 2회로도 화면이 기대와 다르면 중단하고 상태를 확인하세요. verified는 false, connection은 unknown을 유지합니다.
한글 backspace는 입력기 상태에 따라 자모 단위로 삭제됩니다. 회사 관찰 예시는 `날씨 → 날ㅆ → 날`이며, 한 번에 완성형 한 글자를 지운다고 가정하지 않습니다.

버튼이 숨겨져 있으면 탐색 명령이 포인터를 창 상단으로 이동해 150ms 간격 최대 5회 재조회합니다. 포인터는 복원하지 않습니다. inspect와 dry-run은 포인터를 움직이지 않습니다.
실행 중인데 AX 창이 0개면 이제 `NO_ACCESSIBLE_WINDOWS` 오류가 나옵니다. 다른 Space·숨겨진 창 등일 수 있으며 연결 끊김으로 단정하지 않습니다. 창을 현재 Space로 옮긴 뒤 재조회하세요. 도구가 Space를 자동 전환하지 않습니다.

## 5. 제거와 검증 한계

CLI와 REPL을 종료하고 해당 보조 앱의 손쉬운 사용 항목을 제거한 뒤 고정 설치 폴더를 휴지통으로 이동합니다. Apple iPhone 미러링 앱은 제거하지 않습니다.
이전 설치본 보관 폴더는 필요 없을 때 수동 정리합니다. `PACKAGE-VERIFICATION.md`에 이번 검사 결과와 미검증 범위를, VERIFICATION.md에 초기 PoC 결과를 구분해 기록합니다.
