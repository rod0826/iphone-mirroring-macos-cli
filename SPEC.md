# iPhone Mirroring CLI PoC

Wrap the installed Apple iPhone Mirroring app, without replacing its transport,
authentication, or iPhone services. Target observed: 1.6 on macOS 26.6.2.

## Scope

- Python/Click one-shot commands and default REPL; JSON success and error output.
- Swift helper using public AppKit, Accessibility and CoreGraphics APIs.
- LaunchServices .app identity and private expiring file IPC avoid inheriting
  the agent/terminal's TCC identity. Temporary IPC is deleted after each request.
- doctor, launch, status, inspect, home, app-switcher, search, type, key, click, scroll.
- No automatic setup, permission grants, authentication, sending messages, or submission.
- Input requires Accessibility permission, one verified main window (excluding
  only the observed small system sharing indicator), no setup/sheet,
  and confirmed foreground focus. Coordinates are window-relative points.
- dry-run validates arguments and reads preconditions but never launches/focuses/inputs.
- Input acknowledgement means events posted, never proof of iPhone-side completion.
- No project/session undo: remote operations cannot truthfully be undone.
- No screen-scraping preview bundle; inspect exports actual AX state as JSON.

## Acceptance

1. Installed console command works outside the project directory.
2. doctor reports app version and permission without prompting or launching.
3. Real helper reads app AX state, or returns an explicit permission error.
4. Setup and ambiguous targets reject input rather than guessing.
5. Tests cover malformed coordinates, safe errors, dry-run, text handling and packaging.
6. Connected-device input tests are reported separately; never implied by unit tests.

## Evidence

Prior REA report identifies private ScreenSharingKit/UniversalHID dependencies;
these are not linked by this wrapper. Public interfaces:
- https://developer.apple.com/documentation/applicationservices/1460720-axisprocesstrusted
- https://developer.apple.com/documentation/coregraphics/cgevent
- https://support.apple.com/en-us/120421
