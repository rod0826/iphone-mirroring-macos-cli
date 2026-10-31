import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from cli_anything.iphone_mirroring.iphone_mirroring_cli import cli
from cli_anything.iphone_mirroring.core.service import request


def test_version_requires_no_native_helper():
    result = CliRunner().invoke(cli, ['--version'])
    assert result.exit_code == 0 and '0.1.2' in result.output


@pytest.mark.parametrize('args,presses', [(['home'], 2), (['home','--presses','1'], 1)])
def test_home_has_bounded_press_contract(args, presses):
    with patch('cli_anything.iphone_mirroring.core.service.call', return_value={'ok':True}) as backend:
        result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0
    assert backend.call_args.args[0]['home_presses'] == presses


@pytest.mark.parametrize('presses', [0, 3, True, '2'])
def test_home_rejects_invalid_press_counts_without_input(presses):
    with patch('cli_anything.iphone_mirroring.core.service.call') as backend:
        with pytest.raises(ValueError):
            request('home', home_presses=presses)
    backend.assert_not_called()


def test_doctor_reports_cli_version():
    with patch('cli_anything.iphone_mirroring.core.service.call', return_value={'ok':True}):
        result = CliRunner().invoke(cli, ['doctor'])
    assert result.exit_code == 0
    assert json.loads(result.output)['cli_version'] == '0.1.2'


def test_reveal_is_explicit_and_dry_run_does_not_open_finder():
    with patch('cli_anything.iphone_mirroring.core.service.call', return_value={'ok':True}), \
         patch('cli_anything.iphone_mirroring.iphone_mirroring_cli.reveal_helper') as reveal:
        result = CliRunner().invoke(cli, ['--dry-run','doctor','--reveal-helper'])
    assert result.exit_code == 0
    assert json.loads(result.output)['helper_revealed'] is False
    reveal.assert_not_called()


def test_explicit_reveal_opens_helper_only():
    with patch('cli_anything.iphone_mirroring.core.service.call', return_value={'ok':True}), \
         patch('cli_anything.iphone_mirroring.iphone_mirroring_cli.reveal_helper') as reveal:
        result = CliRunner().invoke(cli, ['doctor','--reveal-helper'])
    assert result.exit_code == 0
    assert json.loads(result.output)['helper_revealed'] is True
    reveal.assert_called_once_with()


def test_finder_reveal_uses_exact_bundle_and_timeout_is_json(tmp_path):
    import subprocess
    from cli_anything.iphone_mirroring.utils import backend
    app = tmp_path / 'helper.app'
    app.mkdir()
    with patch.object(backend, 'APP', app), patch.object(backend.subprocess, 'run', return_value=subprocess.CompletedProcess([],0,'')) as opened:
        backend.reveal_helper()
    assert opened.call_args.args[0] == ['/usr/bin/open', '-R', str(app)]
    with patch('cli_anything.iphone_mirroring.core.service.call', return_value={'ok':True}), \
         patch.object(backend, 'APP', app), patch.object(backend.subprocess, 'run', side_effect=subprocess.TimeoutExpired('open',10)):
        result = CliRunner().invoke(cli, ['doctor','--reveal-helper'])
    assert result.exit_code == 1
    assert json.loads(result.output)['error']['code'] == 'FINDER_REVEAL_FAILED'
