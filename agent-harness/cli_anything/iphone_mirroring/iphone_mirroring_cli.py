"""Small, stateless CLI: operating-system state remains the source of truth."""
import json
from pathlib import Path
import shlex
import sys

import click

from .core.service import KEYS, request
from .utils.backend import BackendError, reveal_helper
from . import __version__


def emit(data):
    click.echo(json.dumps(data, ensure_ascii=False, indent=2))


class JsonGroup(click.Group):
    def main(self, *args, standalone_mode=True, **kwargs):
        code = 0
        try:
            super().main(*args, standalone_mode=False, **kwargs)
        except BackendError as exc:
            emit({'ok': False, 'error': {'code': exc.code, 'message': exc.message}})
            code = 1
        except (click.ClickException, ValueError, OSError) as exc:
            emit({'ok': False, 'error': {'code': 'INVALID_ARGUMENT', 'message': str(exc)}})
            code = 2
        if standalone_mode:
            raise SystemExit(code)
        return code


def invoke(ctx, operation, **arguments):
    data = request(operation, dry_run=ctx.obj['dry_run'], **arguments)
    emit(data)


@click.group(cls=JsonGroup, invoke_without_command=True)
@click.version_option(__version__, prog_name='cli-anything-iphone-mirroring')
@click.option('--json', 'as_json', is_flag=True, help='Machine-readable output (also the default).')
@click.option('--dry-run', is_flag=True, help='Check preconditions without launching or posting input.')
@click.pass_context
def cli(ctx, as_json, dry_run):
    """Operate the installed Apple iPhone Mirroring app. Experimental GUI adapter."""
    ctx.obj = {'dry_run': dry_run}
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


for name in ('status', 'launch', 'app-switcher'):
    def register(name):
        @cli.command(name)
        @click.pass_context
        def command(ctx):
            invoke(ctx, name)
    register(name)


@cli.command()
@click.option('--reveal-helper', 'reveal', is_flag=True, help='Select the helper .app in Finder; never grants permissions.')
@click.pass_context
def doctor(ctx, reveal):
    data = request('doctor', dry_run=ctx.obj['dry_run'])
    data['cli_version'] = __version__
    if reveal:
        if not ctx.obj['dry_run']:
            reveal_helper()
        data['helper_revealed'] = not ctx.obj['dry_run']
    emit(data)


@cli.command()
@click.option('--presses', type=click.IntRange(1, 2), default=2, show_default=True,
              help='Spaced Home actions; two dismiss an underlying Spotlight after App Switcher.')
@click.pass_context
def home(ctx, presses):
    invoke(ctx, 'home', home_presses=presses)


@cli.command()
@click.option('--output', type=click.Path(dir_okay=False, path_type=Path),
              help='Save actual accessibility state as JSON (may contain private screen text).')
@click.pass_context
def inspect(ctx, output):
    """Read bounded accessibility state; does not prove iPhone connectivity."""
    data = request('inspect', dry_run=ctx.obj['dry_run'])
    if output and not ctx.obj['dry_run']:
        with output.open('x', encoding='utf-8') as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
    emit(data)


@cli.command()
@click.argument('text')
@click.pass_context
def search(ctx, text):
    """Open iPhone Spotlight and enter a query; does not select a result."""
    invoke(ctx, 'search', text=text)


@cli.command('type')
@click.argument('text')
@click.pass_context
def type_text(ctx, text):
    """Send Unicode text to the focused field; never presses Return."""
    invoke(ctx, 'type', text=text)


@cli.command()
@click.argument('name', type=click.Choice(KEYS))
@click.pass_context
def key(ctx, name):
    """Send one supported key; Return may submit in the focused app."""
    invoke(ctx, 'key', name=name)


@cli.command('click')
@click.argument('x', type=float)
@click.argument('y', type=float)
@click.pass_context
def click_point(ctx, x, y):
    """Click at window-relative points; excludes window chrome."""
    invoke(ctx, 'click', x=x, y=y)


@cli.command()
@click.argument('direction', type=click.Choice(['up', 'down', 'left', 'right']))
@click.option('--pixels', type=click.IntRange(1, 10000), default=300, show_default=True)
@click.pass_context
def scroll(ctx, direction, pixels):
    """Scroll over the center of the target window."""
    invoke(ctx, 'scroll', direction=direction, pixels=pixels)


@cli.command()
@click.pass_context
def repl(ctx):
    """Interactive mode, with in-memory history only."""
    from .utils.repl_skin import ReplSkin
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory

    skin = ReplSkin('iphone_mirroring', version='0.1.2', history_file='/dev/null')
    skin.skill_install_cmd = 'Use the project .venv; installation is documented in README.md'
    session = PromptSession(history=InMemoryHistory()) if sys.stdin.isatty() else None
    skin.print_banner()
    while True:
        try:
            line = (skin.get_input(session) if session else input('iphone> ')).strip()
            if line in {'quit', 'exit'}:
                break
            if line in {'help', '?'}:
                click.echo(cli.get_help(ctx.parent or ctx))
            elif line:
                prefix = ['--dry-run'] if ctx.obj['dry_run'] else []
                run(prefix + shlex.split(line))
        except (EOFError, KeyboardInterrupt):
            break
        except ValueError as exc:
            emit({'ok': False, 'error': {'code': 'INVALID_ARGUMENT', 'message': str(exc)}})
    skin.print_goodbye()


def run(args=None):
    return cli.main(args=args, standalone_mode=False)


def main():
    raise SystemExit(run())
