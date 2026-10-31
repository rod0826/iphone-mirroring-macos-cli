"""LaunchServices app boundary, preserving the helper's own TCC identity."""
import json
from pathlib import Path
import subprocess
import tempfile
import time

APP = Path(__file__).resolve().parents[1] / 'bin' / 'IPhoneMirroringCLI.app'
HELPER = APP / 'Contents/MacOS/IPhoneMirroringCLI'


class BackendError(RuntimeError):
    def __init__(self, code, message):
        self.code, self.message = code, message
        super().__init__(f'{code}: {message}')


def reveal_helper():
    if not APP.is_dir():
        raise BackendError('HELPER_MISSING', 'Build or install the helper app first.')
    try:
        result = subprocess.run(['/usr/bin/open', '-R', str(APP)], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BackendError('FINDER_REVEAL_FAILED', 'Finder did not open; locate helper_bundle from doctor manually.') from exc
    if result.returncode:
        raise BackendError('FINDER_REVEAL_FAILED', 'Could not select the helper in Finder.')


def _execute(payload):
    # LaunchServices avoids inheriting the terminal/agent's Accessibility identity.
    # Each invocation gets private, expiring IPC files removed on exit or timeout.
    if not APP.is_dir():
        raise BackendError('HELPER_MISSING', 'Run python scripts/build.py first.')
    with tempfile.TemporaryDirectory(prefix='iphone-mirroring-cli-') as directory:
        root = Path(directory)
        request = root / 'request.json'
        request.write_text(json.dumps({**payload, 'expires_at': time.time() + 12}), encoding='utf-8')
        request.chmod(0o600)
        result = subprocess.run(
            ['/usr/bin/open', '-W', '-n', '-g', str(APP), '--args', '--ipc', str(root)],
            text=True, capture_output=True, timeout=15, check=False,
        )
        response = root / 'response.json'
        if not response.is_file():
            raise BackendError('APP_HELPER_FAILED',
                               'Helper app produced no response. Build first and run on a logged-in Mac desktop.')
        return subprocess.CompletedProcess(result.args, 0, response.read_text(encoding='utf-8'), '')


def call(payload):
    try:
        result = _execute(payload)
    except FileNotFoundError as exc:
        raise BackendError('HELPER_MISSING', 'Run python scripts/build.py first.') from exc
    except subprocess.TimeoutExpired as exc:
        raise BackendError('BACKEND_TIMEOUT',
                           'Helper timed out. Inspect the app before retrying input.') from exc
    try:
        data = json.loads(result.stdout)
        if not isinstance(data, dict) or not isinstance(data.get('ok'), bool):
            raise ValueError('Expected response object with ok boolean')
        if not data['ok']:
            error = data['error']
            raise BackendError(error['code'], error['message'])
        if result.returncode:
            raise ValueError('Helper returned success with nonzero exit')
        return data
    except (ValueError, KeyError, TypeError) as exc:
        raise BackendError('BACKEND_PROTOCOL', 'Invalid helper response; rebuild helper.') from exc
