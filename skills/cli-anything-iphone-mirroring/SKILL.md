---
name: cli-anything-iphone-mirroring
description: Operate the installed Apple iPhone Mirroring app through its local experimental CLI, including diagnostics, accessibility observation, and basic GUI input. Use for the existing Apple app rather than an independent mirroring implementation.
---

# iPhone Mirroring CLI PoC

Use `cli-anything-iphone-mirroring` from the project's activated `.venv` or its
absolute executable path. macOS, Apple iPhone Mirroring, and a logged-in desktop
are required. Build the Swift helper with `python scripts/build.py`; install with
`python -m pip install --no-build-isolation -e ./agent-harness` after installing
Click, prompt_toolkit, setuptools and wheel in a Python 3.10+ virtual environment.

## Inspect before input

```bash
cli-anything-iphone-mirroring --json doctor
cli-anything-iphone-mirroring launch
cli-anything-iphone-mirroring --json inspect
cli-anything-iphone-mirroring --dry-run home
```

`doctor` never prompts for permissions. If Accessibility is missing, report the
`helper_bundle` path from doctor and ask the user to grant that .app access manually.
The CLI starts the helper via LaunchServices to avoid inheriting the agent's TCC
identity; adding only the bare executable is insufficient in this environment.
Initial pairing
and authentication also require the user. Do not alter authentication settings.
`launch` opens the Apple app; it does not prove an iPhone connection.

## Command surface

- `doctor`: app version, installation, running status, Accessibility trust.
- `status`: process and window metadata.
- `inspect [--output PATH]`: bounded actual AX state, optionally saved to a new JSON file.
- `launch`: open the installed Apple app.
- `home`, `app-switcher`: invoke the actual Apple navigation buttons via AXPress.
  If hidden, hover the pointer over the verified window toolbar and retry at most
  five times with 150ms waits. The pointer stays there. `search` uses this same Home step. Read-only
  inspect/status and dry-run never move the pointer. Focus/window changes abort.
- `search TEXT`: Home, wait for transition, View → Spotlight, then query input;
  no result selection. Menu lookup supports Korean and English.
- `type TEXT`: Unicode text into the focused field, without pressing Return.
- `click X Y`: window-relative points, excluding top 40pt and bottom 20pt.
- `scroll up|down|left|right [--pixels 300]`: scroll over window center.
- `key return|escape|tab|backspace|up|down|left|right`: one key.
- No command enters the REPL; `help` and `quit` are available.

Options `--json` and `--dry-run` precede the subcommand. Normal responses and
errors are JSON even without `--json`; help and REPL banners are human-readable.
Exit codes: 0 acknowledged, 1 backend/environment failure, 2 invalid arguments.
Command history is not saved to disk. Type/search text is not echoed in success
responses, but command arguments can appear in shell history and process lists.

## Interpret results honestly

`delivery: requested` or `posted`, with `verified: false`, only acknowledges a
Mac UI action or event posting.
The connection is deliberately `unknown`. Verify the actual screen after input;
AX may not expose iPhone app controls, so fall back to an available authorized
Computer Use observation or report that verification is unavailable. Do not
blindly retry input after a timeout: it might have partially executed.

The helper rejects missing Accessibility, setup, modal dialogs, minimized or
ambiguous windows and changed focus. It does not classify every possible
connection/error screen. Return or a click can submit in the focused iPhone app;
only use actions within the user's requested task.

This is a GUI-adapter PoC using CLI-Anything packaging and REPL conventions.
There is no iPhone data API, private-framework backend, undo/redo, persistent
remote session restoration, screenshot preview protocol, or headless support.
Host integration tests are not proof of connected-device input success.
