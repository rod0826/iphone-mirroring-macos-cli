import json
import subprocess
from unittest.mock import patch
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli_anything.iphone_mirroring.iphone_mirroring_cli import cli
from cli_anything.iphone_mirroring.core.service import request
from cli_anything.iphone_mirroring.utils.backend import BackendError, call


@pytest.mark.parametrize('args', [
    ['click', '-1', '10'], ['click', 'nan', '10'],
    ['click', 'inf', '10'], ['scroll', 'down', '--pixels', '0'],
    ['scroll', 'up', '--pixels', '10001'], ['type', 'a\x00b'],
    ['type', 'a' * 1001], ['key', 'cmd+q'],
])
def test_invalid_input_never_calls_backend(args):
    with patch('cli_anything.iphone_mirroring.core.service.call') as backend:
        result = CliRunner().invoke(cli, ['--json', *args])
    assert result.exit_code != 0
    assert json.loads(result.output)['ok'] is False
    backend.assert_not_called()


def test_dry_run_only_probes_preconditions():
    with patch('cli_anything.iphone_mirroring.core.service.call', return_value={
        'ok': True, 'dry_run': True, 'operation': 'home'
    }) as backend:
        result = CliRunner().invoke(cli, ['--json', '--dry-run', 'home'])
    assert result.exit_code == 0
    assert backend.call_args.args[0] == {'operation': 'home', 'dry_run': True, 'home_presses': 2}


def test_text_not_echoed_in_response():
    with patch('cli_anything.iphone_mirroring.core.service.call', return_value={
        'ok': True, 'delivery': 'posted', 'verified': False
    }):
        result = CliRunner().invoke(cli, ['--json', 'type', 'private 한국어'])
    assert result.exit_code == 0
    assert 'private 한국어' not in result.output


def test_backend_error_is_json_and_nonzero():
    with patch('cli_anything.iphone_mirroring.core.service.call', side_effect=
               BackendError('ACCESSIBILITY_REQUIRED', 'Permission required')):
        result = CliRunner().invoke(cli, ['--json', 'status'])
    assert result.exit_code == 1
    assert json.loads(result.output)['error']['code'] == 'ACCESSIBILITY_REQUIRED'


def test_timeout_is_actionable():
    with patch('cli_anything.iphone_mirroring.utils.backend._execute',
               side_effect=subprocess.TimeoutExpired('helper', 15)):
        with pytest.raises(BackendError, match='BACKEND_TIMEOUT'):
            call({'operation': 'doctor'})


@pytest.mark.parametrize('output', ['oops', '[]', '{"ok":true} trailing'])
def test_malformed_helper_output(output):
    with patch('cli_anything.iphone_mirroring.utils.backend._execute',
               return_value=subprocess.CompletedProcess([], 0, output, '')):
        with pytest.raises(BackendError, match='BACKEND_PROTOCOL'):
            call({'operation': 'doctor'})


def test_repl_handles_eof_without_saving_history():
    result = CliRunner().invoke(cli, [], input='quit\n')
    assert result.exit_code == 0


def test_service_rejects_unknown_operations():
    with pytest.raises(ValueError):
        request('shell', command='anything')


def test_app_ipc_uses_private_expiring_request_and_cleans_up(tmp_path):
    from cli_anything.iphone_mirroring.utils.backend import _execute
    directory = None

    def opened(args, **kwargs):
        nonlocal directory
        assert args[:4] == ['/usr/bin/open', '-W', '-n', '-g']
        directory = Path(args[-1])
        assert directory.stat().st_mode & 0o777 == 0o700
        payload = json.loads((directory / 'request.json').read_text())
        assert payload['operation'] == 'doctor'
        assert isinstance(payload['expires_at'], float)
        (directory / 'response.json').write_text('{"ok":true}')
        return subprocess.CompletedProcess(args, 0, '', '')

    fake_app = tmp_path / 'IPhoneMirroringCLI.app'
    fake_app.mkdir()
    with patch('cli_anything.iphone_mirroring.utils.backend.APP', fake_app), \
            patch('cli_anything.iphone_mirroring.utils.backend.subprocess.run', side_effect=opened):
        result = _execute({'operation': 'doctor'})
    assert json.loads(result.stdout)['ok'] is True
    assert not directory.exists()
