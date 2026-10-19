# 검증 요약 — 2026-10-19

원본 PoC에서 Python 단위 18개와 설치된 CLI/실제 앱 호스트 통합 9개가 통과했습니다.
추가로 Swift 창 분류 정책 5사례가 통과했습니다. 실제 입력의 화면 관찰 결과와
미검증 범위는 루트 VERIFICATION.md에 기록합니다.

개인 로컬 경로와 화면 정보가 들어갈 수 있는 원시 로그는 공개하지 않습니다.
호스트 통합 테스트는 macOS, 빌드된 보조 앱, 설치된 CLI, 실행 중인 Apple 앱과
적절한 접근성 권한이 필요합니다. 단위 테스트만으로 실기기 입력 성공을 주장하지 않습니다.

단위 테스트:

```sh
python -m pytest agent-harness/cli_anything/iphone_mirroring/tests/test_core.py -q
python scripts/test-native.py
```

설치된 CLI와 호스트 테스트는 README의 검증 명령을 사용하세요.
