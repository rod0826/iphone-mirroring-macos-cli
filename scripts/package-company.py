"""Build an offline, per-user company-test ZIP; never uploads artifacts."""
import argparse
import hashlib
import json
import importlib.metadata as metadata
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NAME = 'IPhone-Mirroring-CLI-0.1.0-company-test-arm64'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--helper', type=Path, required=True, help='Previously built, signed helper .app')
    parser.add_argument('--notices', type=Path, required=True, help='License directory for the frozen runtime')
    args = parser.parse_args()
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        parser.error('This test package targets Apple Silicon macOS only.')
    helper = args.helper.resolve()
    if not (helper/'Contents/MacOS/IPhoneMirroringCLI').is_file():
        parser.error('Missing helper app; build it with scripts/build.py first.')
    if not args.notices.is_dir():
        parser.error('Runtime license directory is required.')
    subprocess.run(['codesign', '--verify', '--strict', str(helper)], check=True)
    destination = ROOT/'release'/NAME
    if destination.exists() or Path(str(destination) + '.zip').exists():
        parser.error('Output already exists; preserve or remove the previous build explicitly.')
    env = {**os.environ, 'PYINSTALLER_CONFIG_DIR': str(ROOT/'build/pyinstaller-cache')}
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir',
        '--name', 'cli-anything-iphone-mirroring', '--distpath', str(ROOT/'build/frozen'),
        '--workpath', str(ROOT/'build/pyinstaller'), '--specpath', str(ROOT/'build'),
        '--paths', str(ROOT/'agent-harness'),
        '--hidden-import', 'cli_anything.iphone_mirroring.utils.repl_skin',
        '--add-data', str(ROOT/'skills/cli-anything-iphone-mirroring/SKILL.md') + ':cli_anything/iphone_mirroring/skills',
        str(ROOT/'scripts/frozen-entry.py')], env=env, check=True)
    destination.mkdir(parents=True)
    shutil.copytree(ROOT/'build/frozen/cli-anything-iphone-mirroring', destination/'cli')
    target = destination/'cli/_internal/cli_anything/iphone_mirroring/bin/IPhoneMirroringCLI.app'
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(helper, target)
    subprocess.run(['codesign', '--verify', '--strict', str(target)], check=True)
    for name in ['LICENSE', 'NOTICE', 'VERIFICATION.md']:
        shutil.copy2(ROOT/name, destination/name)
    shutil.copytree(args.notices, destination/'THIRD_PARTY_LICENSES')
    for dependency in ['click', 'prompt_toolkit', 'wcwidth', 'Pygments']:
        distribution = metadata.distribution(dependency)
        for member in distribution.files or []:
            if member.name.upper().startswith(('LICENSE', 'COPYING', 'AUTHORS')):
                license_target = destination/'THIRD_PARTY_LICENSES'/dependency/str(member)
                license_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(distribution.locate_file(member), license_target)
    shutil.copytree(ROOT/'skills', destination/'skills')
    shutil.copy2(ROOT/'docs/zip-install.md', destination/'먼저읽기.md')
    shutil.copy2(ROOT/'scripts/install.command', destination/'설치.command')
    shutil.copy2(ROOT/'scripts/start.command', destination/'시작.command')
    for item in ['설치.command', '시작.command']:
        (destination/item).chmod(0o755)
    manifest = {'version': '0.1.0', 'architecture': 'arm64',
                'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                'python': sys.version.split()[0], 'helper_sha256': hashlib.sha256((target/'Contents/MacOS/IPhoneMirroringCLI').read_bytes()).hexdigest()}
    (destination/'BUILD.json').write_text(json.dumps(manifest, indent=2)+'\n')
    archive = Path(str(destination) + '.zip')
    subprocess.run(['/usr/bin/ditto', '-c', '-k', '--keepParent', str(destination), str(archive)], check=True)
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    archive.with_suffix('.zip.sha256').write_text(checksum+'  '+archive.name+'\n')
    print(archive)


if __name__ == '__main__':
    main()
