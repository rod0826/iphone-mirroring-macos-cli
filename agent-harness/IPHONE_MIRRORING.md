# Backend mapping

Apple app: `/System/Applications/iPhone Mirroring.app`, `com.apple.ScreenContinuity`.
The app is a hard dependency. This PoC is a GUI-adapter extension to CLI-Anything;
source/backend-engine analysis, native project formats, undo and screen-scraped
preview bundles are not applicable or claimed.

| Command | Real backend action |
| --- | --- |
| doctor | Bundle metadata, NSRunningApplication, AXIsProcessTrusted |
| launch | NSWorkspace.openApplication |
| status / inspect | AXUIElementCopyAttributeValue on the real Apple process |
| home / app-switcher | AXPress on app.grid.3x3 / iphone.app.switcher |
| search | Home AXPress, remote transition wait, visible View → Spotlight AXPress, Unicode input |
| type | CGEvent Unicode keyboard events addressed to app PID |
| key / click / scroll | CGEvent HID keyboard / mouse / pixel-scroll events after focus and window checks |

All mutation input goes over private expiring JSON IPC files, never a shell.
LaunchServices starts the signed local .app, separating TCC attribution from
the parent terminal/agent. Window/focus checks precede input.
The helper does not request Accessibility permission. Quartz posting is
asynchronous, so the short-lived helper stays alive briefly after posting.
Responses acknowledge requests, not iPhone-side completion. Device observations
and remaining validation limits are documented separately in VERIFICATION.md.
