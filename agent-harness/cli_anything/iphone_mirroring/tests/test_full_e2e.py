"""Host integration tests, not connected-iPhone acceptance tests."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


def _resolve_cli(name):
    path = shutil.which(name)
    if path:
        return [path]
    if os.environ.get('CLI_ANYTHING_FORCE_INSTALLED') == '1':
        raise RuntimeError(f'{name} is not installed')
    return [sys.executable, '-m', 'cli_anything.iphone_mirroring']


CLI = _resolve_cli('cli-anything-iphone-mirroring')
ARTIFACTS = Path(__file__).resolve().parents[4] / 'artifacts'


def execute(*args):
    return subprocess.run(CLI + list(args), capture_output=True, text=True, timeout=20)


def test_installed_help():
    result = execute('--help')
    assert result.returncode == 0
    assert 'app-switcher' in result.stdout and 'inspect' in result.stdout


def test_real_apple_app_diagnostics():
    result = execute('--json', 'doctor')
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['installed'] is True
    assert data['bundle_id'] == 'com.apple.ScreenContinuity'
    assert data['app_version'] != 'unknown'
    assert data['permission_prompted'] is False
    ARTIFACTS.mkdir(exist_ok=True)
    destination = ARTIFACTS / 'doctor.json'
    destination.write_text(result.stdout, encoding='utf-8')
    print(f'\nActual helper diagnostic: {destination}')


def test_real_accessibility_observation_or_explicit_blocker():
    result = execute('--json', 'inspect')
    data = json.loads(result.stdout)
    if data['ok']:
        assert result.returncode == 0
        assert isinstance(data['windows'], list)
        assert isinstance(data['accessibility'], list)
        for window in data['accessibility']:
            assert window['nodes'] and window['nodes'][0]['role']
    else:
        assert result.returncode == 1
        assert data['error']['code'] in {'ACCESSIBILITY_REQUIRED', 'APP_NOT_RUNNING'}
        print(f'\nHOST OBSERVATION BLOCKED: {data["error"]["code"]}; not a device-test pass.')
    ARTIFACTS.mkdir(exist_ok=True)
    (ARTIFACTS / 'inspect.json').write_text(result.stdout, encoding='utf-8')


def test_installed_invalid_coordinates_are_json():
    result = execute('--json', 'click', 'nan', '100')
    assert result.returncode == 2
    assert json.loads(result.stdout)['error']['code'] == 'INVALID_ARGUMENT'


def test_native_unknown_operation_fails_without_permissions():
    from cli_anything.iphone_mirroring.utils.backend import HELPER
    result = subprocess.run([str(HELPER)], input='{"operation":"shell"}',
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 1
    assert json.loads(result.stdout)['error']['code'] == 'INVALID_ARGUMENT'


@pytest.mark.parametrize('payload', ['not json', '[]', '{}'])
def test_native_rejects_invalid_requests(payload):
    from cli_anything.iphone_mirroring.utils.backend import HELPER
    result = subprocess.run([str(HELPER)], input=payload, capture_output=True,
                            text=True, timeout=15)
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data['ok'] is False
    assert data['error']['code'] in {'INVALID_ARGUMENT', 'INVALID_REQUEST'}


def test_real_dry_run_launch_does_not_start_app():
    before = json.loads(execute('doctor').stdout)['running']
    result = execute('--dry-run', 'launch')
    assert result.returncode == 0
    assert json.loads(result.stdout)['dry_run'] is True
    after = json.loads(execute('doctor').stdout)['running']
    assert before == after
