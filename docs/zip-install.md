# iPhone Mirroring CLI — 회사 Mac 테스트 ZIP

비공식 실험용 PoC입니다. Apple의 검토·승인·인증을 받지 않았습니다.
설치 ZIP은 별도 전달하며 GitHub Releases에는 게시하지 않습니다.

## 대상과 포함 파일

- Apple Silicon(M1 이상) Mac용 arm64 패키지입니다. Intel Mac에서는 실행할 수 없습니다.
- macOS 15 이상을 빌드 하한으로 삼았으나 실기기 검증 환경은 macOS 26.6.2 / Apple iPhone Mirroring 1.6입니다. 다른 버전 호환성은 미검증입니다.
- Apple iPhone 미러링을 사용할 수 있는 Mac·iPhone 및 완료된 최초 연결·인증이 필요합니다.
- Python 런타임·CLI·전용 보조 앱·스킬·라이선스가 포함돼 있습니다. Python, Homebrew, Xcode를 별도로 설치하지 않습니다.
- Apple 앱과 iPhone 앱은 포함하지 않습니다. macOS에 설치된 Apple iPhone 미러링 앱을 사용합니다.
- Developer ID 서명·공증을 받지 않은 개발용 패키지입니다. 회사 정책과 Gatekeeper가 실행을 막을 수 있습니다. 이 경우 회사 IT 담당자에게 확인하세요. 보안 기능을 일괄 해제하지 마세요.

## 1. ZIP 하나로 확인하고 설치하기

**0.1.1부터 ZIP 하나만 전달하면 됩니다.** 압축을 풀면 `검증.command`와 파일별
체크섬 `SHA256SUMS`가 함께 들어 있습니다. `검증.command`를 실행한 뒤
`설치.command`를 실행하세요. 설치 명령도 복사 전에 같은 검증을 자동 수행하며,
파일이 누락되거나 변경되면 중단합니다. 검증은 macOS 기본 도구로 수행하므로
포함된 CLI 바이너리를 먼저 실행할 필요가 없습니다.

별도로 받은 `.zip.sha256` 파일도 있다면 ZIP 자체를 먼저 확인할 수 있습니다.

```sh
cd "$HOME/Downloads"
shasum -a 256 -c IPhone-Mirroring-CLI-0.1.1-company-test-arm64.zip.sha256
```

외부 체크섬 파일이 없다면 이 명령은 건너뛰고 ZIP 내부 검증을 사용합니다.
ZIP 안에 그 ZIP 자신의 해시를 넣을 수는 없으므로, 내부 체크섬은 압축 해제된
파일을 검사합니다. 체크섬은변조 방지 서명이나 출처 인증을 대신하지 않습니다.

폴더 안의 **설치.command**를 실행하면 다음 위치에 복사합니다.

```text
~/Applications/IPhone-Mirroring-CLI-0.1.1
```

관리자 암호, 전역 PATH 변경, 백그라운드 서비스 설치는 없습니다. 기존 대상 폴더가 있으면 덮어쓰지 않고 중단합니다.
실행 제한이 있으면 아래의 해당 설치 폴더 확인 절차를 참고하고 회사 정책을 따르세요.

### 출력 없이 종료되거나 `Killed: 9` / 종료 코드 137이 나오는 경우

브라우저·메신저로 받은 파일에는 `com.apple.quarantine` 격리 속성이 붙을 수 있습니다.
개발용 임시 서명 바이너리는 이 상태에서 macOS에 의해 종료될 수 있으며,
`ditto`로 설치해도 속성이 유지됩니다. 다만 종료 코드 137만으로 원인을 확정할 수는 없습니다.

먼저 내부 검증을 통과하고 신뢰할 수 있는 전달본인지 확인합니다. Apple의
[확인되지 않은 앱 열기 안내](https://support.apple.com/102445)에 따라 시스템 설정의
개별 앱 허용 절차가 제공되는지 확인하세요. 아래 명령은 설치된 CLI의 속성과 보조 앱 서명을 읽기만 합니다.

```sh
xattr -l "$HOME/Applications/IPhone-Mirroring-CLI-0.1.1/cli/cli-anything-iphone-mirroring"
codesign --verify --strict "$HOME/Applications/IPhone-Mirroring-CLI-0.1.1/cli/_internal/cli_anything/iphone_mirroring/bin/IPhoneMirroringCLI.app"
```

**회사 정책상 허용되고 사용자가 이 전달본 실행을 선택한 경우에만**, 설치 폴더
안의 `검증.command`를 다시 실행한 후 다음 명령으로 **이 버전 설치 폴더에 한해서**
격리 속성을 제거할 수 있습니다. 이는 해당 파일들의 최초 실행 검사를 생략하게
하므로 전달 경로와 무결성을 확인한 테스트 패키지에만 적용합니다.

```sh
/bin/bash "$HOME/Applications/IPhone-Mirroring-CLI-0.1.1/검증.command"
```

위 검증이 성공한 경우에만 별도로 실행합니다.

```sh
xattr -dr com.apple.quarantine "$HOME/Applications/IPhone-Mirroring-CLI-0.1.1"
"$HOME/Applications/IPhone-Mirroring-CLI-0.1.1/cli/cli-anything-iphone-mirroring" --help
```

`sudo`나 전역 Gatekeeper 해제는 필요하지 않습니다. Downloads·Applications 전체나
회사 보안 설정에 이 명령을 적용하지 마세요. 설치기·검증기는 격리 속성을 자동으로 제거하지 않습니다.
여전히 종료되거나 속성이 없으면 서명 오류·회사 보안 제품·시스템 종료 로그를 확인합니다.

## 2. iPhone 연결과 권한 등록

1. Mac의 Apple iPhone 미러링 앱을 열어 사용자 본인이 최초 연결과 인증을 완료합니다.
2. 터미널에서 아래 진단 명령을 실행합니다.

```sh
"$HOME/Applications/IPhone-Mirroring-CLI-0.1.1/cli/cli-anything-iphone-mirroring" --json doctor
```

3. accessibility_trusted가 false이면 시스템 설정 → 개인정보 보호 및 보안 → 손쉬운 사용에서 다음 **앱 번들**을 추가하고 켭니다. Finder의 이동 → 폴더로 이동(Command+Shift+G)에 아래 경로를 붙여 넣으면 찾기 쉽습니다.

```text
~/Applications/IPhone-Mirroring-CLI-0.1.1/cli/_internal/cli_anything/iphone_mirroring/bin/IPhoneMirroringCLI.app
```

내부의 확장자 없는 실행 파일이 아니라 IPhoneMirroringCLI.app을 등록합니다. 이 보조 앱을 직접 더블클릭해 쓰는 방식은 아닙니다. Mac마다 권한을 별도로 등록해야 합니다. 0.1.1은 설치 경로와 보조 앱 서명이 바뀌었으므로
0.1.0에 부여한 권한만으로는 동작하지 않을 수 있습니다. 새 경로의 앱을 등록하세요. CLI 자체는 권한을 부여하거나 기존 권한 기록을 초기화하지 않습니다.

## 3. 최소 확인

아래 CLI 경로를 변수에 저장하고 진단·조회부터 실행합니다.

```sh
iphone_cli="$HOME/Applications/IPhone-Mirroring-CLI-0.1.1/cli/cli-anything-iphone-mirroring"
"$iphone_cli" --json doctor
"$iphone_cli" inspect
"$iphone_cli" --dry-run home
"$iphone_cli" home
```

0.1.1은 홈·앱 전환 버튼이 숨겨져 있으면 포인터를 미러링 창 상단으로 옮기고
150ms 간격으로 최대 5회 다시 조회합니다. 이동만 하며 클릭하지 않습니다. 포인터는 복원하지 않습니다.
창·포커스가 바뀌면 중단합니다. 버튼이 계속 없으면 iPhone 연결을 확인하고 포인터를
툴바 위에 둔 뒤 inspect로 확인하세요. inspect와 dry-run은 포인터를 옮기지 않습니다.

home 실행 후 실제 iPhone 미러링 화면에서 홈 화면으로 이동했는지 확인합니다. 연결을 조회하는 자동 판정은 없으므로 connection은 unknown, 입력 성공의 자동 판정은 없으므로 verified는 false입니다.

```sh
"$iphone_cli" search '날씨'
"$iphone_cli" key backspace
"$iphone_cli" home
```

메시지·결제·설정 변경 화면에서 좌표 클릭이나 Return을 시험하지 마세요.
폴더의 시작.command는 대화형 REPL을 엽니다. help로 명령을 보고 quit으로 종료합니다.
Codex에서 사용할 때는 설치된 CLI의 전체 경로와 skills/cli-anything-iphone-mirroring/SKILL.md를 알려주세요. 스킬 자동 등록은 하지 않습니다.

## 제거와 알려진 한계

실행 중인 CLI를 종료하고 시스템 설정의 해당 보조 앱 권한 항목을 제거한 다음, 설치한 IPhone-Mirroring-CLI-0.1.1 폴더를 휴지통으로 이동합니다. Apple iPhone 미러링 앱은 제거하지 않습니다.

화면 속 iPhone 버튼·문구를 읽는 API, 자동 결과 검증, 화면 녹화, headless 실행은 제공하지 않습니다. 이전 PoC의 실기기 결과는 VERIFICATION.md, 이 ZIP의 검사 결과는 PACKAGE-VERIFICATION.md를 참고하세요. 회사 Mac에서의 최초 설치와 실기기 입력은 현장 확인이 필요합니다.
