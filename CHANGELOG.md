# Changes

## 0.1.1 — 2026-10-27

- Fixed #1: reveal hidden Home/App Switcher controls with hover and bounded AX retries; abort on changed window/focus. Search uses the same Home path.
- Fixed #2 distribution: one ZIP now contains SHA256SUMS and 검증.command. Installation stops before copying if verification fails; the optional external ZIP checksum is still generated.
- Documented exit 137 diagnosis and an explicit, installation-folder-only quarantine removal option after trust/integrity checks. No automatic permission or quarantine changes.
- Bumped helper and install directory to 0.1.1; grant Accessibility to the new helper bundle on each test Mac.

## 0.1.0 — 2026-10-19

- Added an experimental CLI around the installed Apple iPhone Mirroring app.
- Added diagnostics, bounded AX inspection, basic input commands, JSON errors,
  dry-run checks and a REPL with no persistent input history.
- Real-device input acceptance remains dependent on user permissions and setup.

### 배포 보완
- Apple Silicon 회사 테스트용 오프라인 ZIP 빌드와 사용자 폴더 설치 명령, 설치 안내 추가.
- 실행 파일은 GitHub에 게시하지 않고 별도 전달.
