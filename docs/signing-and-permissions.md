# 서명·권한 유지 검토 — 이슈 #4

0.1.2는 버전 없는 사용자 설치 경로를 도입하지만 보조 앱은 기존과 같은 ad-hoc 서명입니다. 빌드 Mac의 `security find-identity -v -p codesigning` 결과 사용 가능한 코드 서명 인증서가 0개였습니다. 인증서·키체인 신뢰·TCC 설정을 새로 만들거나 바꾸지 않았습니다.

같은 인증서와 코드 식별 요구사항을 유지하는 서명 체계는 업데이트 식별에 도움이 되지만, 자체 서명 인증서로 이 도구의 TCC 허용이 유지되는지는 아직 검증하지 않았습니다. 고정 경로만으로 권한 유지가 보장되지는 않습니다. 자체 서명과 Apple Developer ID·공증도 구분해야 합니다.

따라서 #4 중 고정 경로·설치 편의는 구현하고, 서명에 의한 권한 유지와 반복 격리 처리 해소는 후속 검증 과제로 남깁니다. 현재 설치·검증 명령은 격리 속성을 자동 삭제하거나 보안 기능을 전역 해제하지 않습니다.

후속 검증에는 같은 서명 신원으로 만든 서로 다른 두 빌드의 designated requirement 비교, 동일 경로 교체 후 TCC 상태 확인, 다운로드 격리 상태의 새 Mac 실행, Developer ID 공증 경로 확인이 필요합니다. 현장 성공 전에는 유지된다고 안내하지 않습니다.

- [Apple: 코드 서명 요구사항과 업데이트 식별](https://developer.apple.com/documentation/technotes/tn3127-inside-code-signing-requirements)
- [Apple: 자체 서명과 코드 서명](https://developer.apple.com/library/archive/technotes/tn2206/)
- [Apple: Developer ID와 공증](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution)
