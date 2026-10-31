# 0.1.2 검증 — 2026-10-31

## 회사 Mac 관찰을 반영한 변경

이슈 #3은 앱 전환 화면 → 직전 Spotlight → 홈으로 이어지는 iOS 동작을 보여 줬습니다. 홈을 기본 2회로 요청하고 한 번 요청은 home --presses 1로 제공합니다. search도 같은 2회 기준을 사용합니다. 한글 Backspace는 입력기 상태에 따라 자모 단위 삭제가 가능함을 문서화했습니다. 0.1.1 자동 호버는 회사 재검증에서 성공한 것으로 보고됐습니다.

이슈 #4의 빈 AX 창 조회는 NO_ACCESSIBLE_WINDOWS 오류로 바꾸고, 다른 Space·숨겨진 창 등 가능한 원인을 안내합니다. 원인을 다른 Space로 단정하거나 자동 Space 전환을 하지 않습니다. --version, doctor의 cli_version/helper_version, --reveal-helper, 보조 앱 직접 실행 안내를 추가했습니다.

설치 경로를 ~/Applications/IPhone-Mirroring-CLI로 고정하고, 검증된 임시 복사본으로 같은 제품만 교체하며 기존본을 보관합니다. 버전별 옛 경로는 건드리지 않습니다. 서명과 격리 속성 자동 처리는 구현하지 않았습니다.

## 자동 검증

- Python 단위·배포 회귀 34 passed (0.57초).
- Swift: 공유 표시 창 분류 5 + 빈/정상 관찰 창 2 + 호버 정책 5 + 앱 전환 아래 Spotlight를 포함한 Home 시퀀스 3 = 15사례 통과.
- RED 단계에서 한 번 Home만 요청하는 기존 동작은 Spotlight에 머물러 테스트가 실패했고, 수정 후 홈 상태에 도달했습니다. 창 변경 시 두 번째 입력을 중단하는 경우도 검사했습니다.
- 고정 설치 경로의 교체·백업, 알 수 없는 폴더 및 심볼릭 링크 거부, 복사 후 quarantine 속성 존속, Finder reveal의 dry-run 무동작·정확한 경로·시간 초과 JSON 오류를 검사했습니다.
- Swift 보조 앱 빌드와 코드 서명 검사 통과. 시스템에 유효한 코드 서명 신원이 0개임을 읽기 전용으로 확인했습니다.

## 아직 검증하지 않은 부분

Home 2회 정책은 회사 관찰과 상태 모델 회귀에 기반합니다. 실제 기기에서 0.1.2의 앱 전환 → Home, 반복 검색, 자모 삭제 조합을 이번 Mac에서 검증하지 않았습니다. verified=false, connection=unknown을 유지합니다.
보조 앱을 직접 실행할 때의 안내 창은 구현했으나 Computer Use 호출이 시간 초과되어 화면 확인을 완료하지 못했습니다. 다른 Space에서의 실제 AX 0개 조건도 현장 재확인이 필요합니다.
서명 인증서가 없어 자체 서명의 TCC 연속성과 Developer ID 공증·격리 없는 회사 배포는 미검증이며 해결됐다고 표시하지 않습니다. [서명 검토](signing-and-permissions.md) 참고.

전체 호스트 실행: Python 43 passed, 0 skipped (1.49초). doctor는 CLI·보조 앱 버전 0.1.2와 접근성 권한 false를 확인했습니다. inspect는 APP_NOT_RUNNING을 반환했습니다. 실행 환경의 차단 상태를 입력 성공으로 세지 않습니다.

## 독립 ZIP 최종 검사

독립 배포 CLI를 CLI_ANYTHING_FORCE_INSTALLED=1로 선택한 전체 테스트도 43 passed, 0 skipped (6.74초)였습니다. 실제 ZIP을 새 임시 경로에 압축 해제해 검증한 뒤 고정 경로 신규 설치 및 재설치·기존본 보관을 확인했습니다. 설치된 CLI의 --version, doctor/home의 --help와 helper 서명 검사도 통과했습니다. 외부 Python·Homebrew가 없는 PATH=/usr/bin:/bin 조건에서 검사했습니다. 실기기 입력과 GUI 화면 확인을 의미하지 않습니다.
