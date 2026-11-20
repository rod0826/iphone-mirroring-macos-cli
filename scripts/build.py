"""Build the native helper; no signing entitlements or private frameworks."""
from pathlib import Path
import platform
import plistlib
import runpy
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'agent-harness/cli_anything/iphone_mirroring'
VERSION = runpy.run_path(str(PACKAGE / '__init__.py'))['__version__']
BIN = PACKAGE / 'bin'
APP = BIN / 'IPhoneMirroringCLI.app'
TARGET = APP / 'Contents/MacOS/IPhoneMirroringCLI'
TARGET.parent.mkdir(parents=True, exist_ok=True)
CACHE = ROOT / 'build/swift-module-cache'
CACHE.mkdir(parents=True, exist_ok=True)
subprocess.run(['xcrun', 'swiftc', '-O', '-module-cache-path', str(CACHE),
                '-target', f'{platform.machine()}-apple-macosx15.0',
                str(ROOT / 'native/Errors.swift'), str(ROOT / 'native/WindowPolicy.swift'), str(ROOT / 'native/NavigationPolicy.swift'),
                str(ROOT / 'native/main.swift'),
                '-o', str(TARGET)], check=True)
resources = APP / 'Contents/Resources'
resources.mkdir(parents=True, exist_ok=True)
shutil.copy2(ROOT / 'assets/AppIcon.icns', resources / 'AppIcon.icns')
with (APP / 'Contents/Info.plist').open('wb') as stream:
    plistlib.dump({
        'CFBundleIdentifier': 'local.cli-anything.iphone-mirroring',
        'CFBundleName': 'iPhone Mirroring CLI',
        'CFBundleExecutable': 'IPhoneMirroringCLI', 'CFBundlePackageType': 'APPL',
        'CFBundleShortVersionString': VERSION, 'CFBundleVersion': '4',
        'CFBundleIconFile': 'AppIcon.icns',
        'LSUIElement': True, 'LSMinimumSystemVersion': '15.0',
        'NSAccessibilityUsageDescription': '요청한 iPhone 미러링 창 조회와 기본 입력을 수행합니다.',
    }, stream)
subprocess.run(['codesign', '--force', '--sign', '-', str(APP)], check=True)
subprocess.run(['codesign', '--verify', '--strict', str(APP)], check=True)
(BIN / 'IPhoneMirroringCLI').unlink(missing_ok=True)
print(APP)
