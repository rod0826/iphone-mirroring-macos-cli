# iPhone Mirroring CLI for macOS — 실험용 PoC

**비공식 실험용 프로젝트입니다. Apple의 검토·승인·인증을 받지 않았으며, Apple이 제공하거나 지원하는 제품이 아닙니다.**

Unofficial experimental project. Not affiliated with, endorsed by, or supported by Apple.

이 저장소는 소스·문서 공개용입니다. 회사 Mac에서 시험할 설치 ZIP은 별도로 전달하며,
실행 앱·설치 ZIP을 GitHub Releases에 게시하지 않습니다. GitHub의 자동 생성 소스 ZIP은
설치 파일이 아닙니다. 0.1.1 전달 ZIP에는 `검증.command`와 `SHA256SUMS`가 포함돼
ZIP 하나만으로 압축 해제 파일의 무결성을 확인할 수 있습니다. [회사 Mac 시험 안내](docs/company-mac-test.md)와
[별도 전달 ZIP 설치 안내](docs/zip-install.md)를 참고하세요.

설치된 Apple iPhone 미러링 앱을 감싸는 실험용 CLI입니다. Apple 앱이 연결·인증·
화면 전송을 담당하고 이 도구는 Mac 쪽 UI를 관찰하거나 입력 이벤트를 전달합니다.
비공개 프레임워크 호출, entitlement 복제, 자체 iPhone 원격 제어 서버는 없습니다.

## 설치

프로젝트 폴더에서 macOS의 Command Line Tools와 Python 3.10 이상으로 실행합니다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install 'click>=8.1,<9' 'prompt_toolkit>=3,<4' setuptools wheel pytest
.venv/bin/python scripts/build.py
.venv/bin/python -m pip install --no-build-isolation -e ./agent-harness
source .venv/bin/activate
cli-anything-iphone-mirroring --json doctor
```

설치 후 `source .venv/bin/activate`로 가상 환경을 활성화하거나 `.venv/bin/`의
실행 파일을 직접 실행하세요. 이동하거나 다른 Mac에서 쓸 때는 다시 빌드하세요.
위 명령은 개발자용 소스 빌드이며, Python과 Command Line Tools가 필요합니다.
검증 환경은 macOS 26.6.2 / Apple iPhone Mirroring 1.6 / Apple Silicon입니다.
네이티브 빌드 타깃은 macOS 15 이상이지만 다른 OS·기기 조합의 호환성을 보증하지 않습니다.

## 처음 사용할 때

1. Apple iPhone 미러링 앱에서 사용자 본인이 최초 설정·기기 인증을 완료합니다.
2. `doctor`에서 `accessibility_trusted`를 확인합니다. false라면 시스템 설정 →
   개인정보 보호 및 보안 → 손쉬운 사용에서 doctor가 표시한 `helper_bundle`, 즉
   `IPhoneMirroringCLI.app`을 추가하고 켭니다. 내부 실행 파일이나 Codex/터미널
   전체에 권한을 주는 방식 대신 이 전용 앱 번들을 사용합니다.
   도구는 권한 프롬프트를 띄우거나 인증 설정을 바꾸지 않습니다.
   보조 실행 파일을 재빌드하면 해시 기반 서명이 바뀌므로 기존 권한 항목을
   제거한 뒤 같은 파일을 다시 추가해야 할 수 있습니다. 권한 설정은 빌드 후에 하세요.
3. `launch`, `inspect`로 실제 화면과 창 정보를 확인합니다.
4. 먼저 `--dry-run home`, 이후 `home`을 실행하고 iPhone 화면 변화를 확인합니다.

최초 설정이나 권한이 없어도 `doctor`는 사용할 수 있습니다. 권한 부여 후에도
접근성 읽기가 실패하면 재실행하고 `inspect`의 오류를 확인하세요. 접근성 권한은
Mac UI 제어를 허용하는 권한이며 iPhone 내부 API 접근 권한을 뜻하지 않습니다.

## 명령

모든 일반 응답과 오류는 JSON입니다. `--json`, `--dry-run`은 명령 **앞에** 둡니다.
`--help`와 사람용 REPL 안내는 텍스트입니다.

```bash
cli-anything-iphone-mirroring --json doctor
cli-anything-iphone-mirroring launch
cli-anything-iphone-mirroring status
cli-anything-iphone-mirroring inspect
cli-anything-iphone-mirroring inspect --output /tmp/iphone-ax.json
cli-anything-iphone-mirroring --dry-run home
cli-anything-iphone-mirroring home
cli-anything-iphone-mirroring app-switcher
cli-anything-iphone-mirroring search '날씨'
cli-anything-iphone-mirroring type '한글 입력 시험'
cli-anything-iphone-mirroring click 150 240
cli-anything-iphone-mirroring scroll down --pixels 300
cli-anything-iphone-mirroring key escape
cli-anything-iphone-mirroring
```

- `doctor`: 설치 버전·실행 여부·접근성 권한 조회. 앱 실행이나 권한 요청 없음.
- `status`: PID, 활성 여부, 창 제목·식별자·위치·크기. 미실행이면 명시적 오류.
- `inspect`: 최대 깊이 8, 노드 300개까지 실제 접근성 트리 조회. iPhone 내부 요소
  요소는 현재 검증 환경에서 노출되지 않았습니다. `--output`은 기존 파일을 덮어쓰지 않습니다.
- `launch`: 앱 실행. 연결 성공을 의미하지 않습니다.
- `home` / `app-switcher`: Apple 앱의 실제 접근성 홈·앱 전환 버튼 호출.
  버튼이 숨겨져 있으면 포인터를 창 상단으로 옮겨 호버로 드러낸 뒤 최대 0.75초 재조회합니다.
  포인터를 복원하지 않으며 창·포커스가 바뀌면 중단합니다. `search`의 홈 이동도 같습니다.
  `inspect`와 `--dry-run`은 포인터를 이동하지 않습니다.
- `search`: 홈으로 이동하고 전환을 기다린 뒤 보기 → Spotlight 메뉴를 열어 문자열을
  입력합니다. 검색 중 다시 호출해도 동작하도록 홈에서 시작합니다. 메뉴 제목은
  현재 한국어·영어 환경을 지원합니다. 검색 결과를 선택하거나 실행하지 않습니다.
- `type`: 포커스된 필드에 Unicode 이벤트 전달. 최대 1,000자이며 아주 긴 결합문자는
  거부합니다. 한글은 실기기에서 확인했으며 모든 이모지·입력기 조합은 검증하지 않았습니다.
- `key`: return, escape, tab, backspace, up, down, left, right.
  return이나 클릭은 해당 앱에서 전송·제출을 유발할 수 있으니 대상을 확인하세요.
- `click`: 창 좌상단 기준 **포인트** 좌표. 상단 40pt·하단 20pt를 제외합니다.
  레티나 스크린샷의 픽셀 좌표와 다릅니다. 콘텐츠 영역이 바뀌면 좌표를 재확인하세요.
- `scroll`: 창 중앙에서 픽셀 단위 스크롤 이벤트. 1–10,000.
- 인자 없는 실행: REPL. `help`, `quit` 지원. 명령·입력 문자열 이력을 디스크에 저장하지 않습니다.

## 동작 계약과 한계

- 입력은 접근성 권한, 정확히 하나의 사용 가능한 `iphone-mirroring-main` 창, 초기 설정·모달 부재가
  전제입니다. 앱을 활성화하고 창·포커스를 재확인합니다. 탐색은 접근성 동작,
  한글은 대상 PID의 Unicode 이벤트, 클릭·스크롤·일반 키는 macOS 입력 이벤트로 보냅니다.
  실제 관찰된 작은 시스템 공유 표시 창은 제목·자식 버튼·크기가 일치할 때만 제외합니다.
  검사와 전달은 원자적이지 않으므로 실행 도중 사용자의 조작은 피하세요.
- `delivery: requested` 또는 `posted`, `verified: false`는 **Mac UI 동작을 요청하거나
  이벤트를 보냈다는 뜻**입니다.
  Apple 앱의 수용, iPhone 동작, 연결 성공을 보장하지 않습니다.
- `connection`은 항상 `unknown`입니다. 일반 창 존재만으로 연결을 추정하지 않습니다.
  초기 화면·설정·시트는 차단하지만 모든 연결 오류 화면을 식별하는 분류기는 없습니다.
- `--dry-run`은 입력 전제조건을 읽으며 앱 활성화·키 입력·파일 출력을 하지 않습니다.
- CLI와 보조 앱은 권한 0700의 임시 디렉터리 안에서 JSON으로 통신합니다. 요청은
  12초 후 만료되고 요청·응답 파일은 명령 완료 또는 타임아웃 후 삭제됩니다.
  macOS LaunchServices로 앱을 실행하여 권한 귀속을 실행 부모와 분리합니다. 다만
  CLI 인자 자체는 셸 히스토리·프로세스 목록에 보일 수 있으므로 비밀번호는 입력하지 마세요.
- `inspect`에는 개인 화면 텍스트가 포함될 수 있습니다. 명시적으로 저장할 때만
  파일을 만들며 자동 수집·업로드하지 않습니다.
- CLI-Anything의 패키징·REPL·JSON·실앱 테스트 구조를 적용한 **GUI 어댑터 확장**입니다.
  소스 분석 기반 백엔드 하네스와 동일하지 않습니다. 스크린샷 스크래핑 preview,
  프로젝트 파일, 원격 동작 undo/redo, 세션 복원은 제공하지 않습니다.
- Apple iPhone 미러링과 로그인된 Mac 데스크톱이 필요합니다. 헤드리스 서버용이 아닙니다.

현재 Mac과 연결된 iPhone에서 홈·앱 전환·한글 검색 및 입력·클릭·세로 스크롤·
backspace를 화면으로 검증했습니다. iPhone 내부 앱의 버튼·텍스트는 접근성 트리에
노출되지 않았으므로 결과 검증에는 별도 화면 관찰이 필요합니다. 반환값의
`verified: false`는 자동 관찰 기능이 없다는 의미이며 수동 검증 결과와 구분됩니다.

## 검증

```bash
PATH="$PWD/.venv/bin:$PATH" CLI_ANYTHING_FORCE_INSTALLED=1 \
  .venv/bin/python -m pytest agent-harness/cli_anything/iphone_mirroring/tests -v -s
.venv/bin/python scripts/test-native.py
```

단위 테스트, 실제 앱 진단, 실기기 입력 검증은 따로 기록합니다.
실기기 미연결이나 접근성 권한 부재를 입력 성공으로 집계하지 않습니다.
0.1.1 회귀 검증은 `docs/verification-0.1.1.md`를 참고하세요.
초기 PoC의 구체적인 결과는 `VERIFICATION.md`와 `agent-harness/cli_anything/iphone_mirroring/tests/TEST.md`를 보세요.

## 라이선스와 출처

프로젝트 자체 코드는 [Apache-2.0](LICENSE)입니다. `repl_skin.py`는
[HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything)에서 가져와 적용했습니다.
[NOTICE](NOTICE)와 [상위 프로젝트 라이선스](THIRD_PARTY_LICENSES/CLI-Anything-APACHE.txt)를 함께 제공합니다.
Apple 앱 바이너리는 포함하지 않습니다. iPhone·macOS 및 관련 상표는 각 권리자에게 귀속됩니다.

## 회사 테스트 ZIP 빌드

Apple Silicon macOS에서 PyInstaller 6.22.3, Python 3.12.14와 런타임 라이선스 자료를 준비합니다.
CLI 런타임은 Click 8.5.0, prompt_toolkit 3.0.53, wcwidth 0.9.2, Pygments 2.21.0을 사용했습니다.
먼저 scripts/build.py로 보조 앱을 빌드하거나 같은 소스의 검증된 보조 앱을 사용합니다.

```sh
python scripts/package-company.py \
  --helper agent-harness/cli_anything/iphone_mirroring/bin/IPhoneMirroringCLI.app \
  --notices /path/to/audited-runtime-licenses
```

빌드 스크립트는 release/에 ZIP과 SHA-256 파일을 만들며 업로드하지 않습니다.
런타임의 Python·동적 라이브러리·의존성 라이선스 자료를 --notices로 전달해야 합니다.
배포 전 압축 해제·이동 후 실행, 앱 서명, helper 원본 일치, 문서와 라이선스를 확인하세요.
