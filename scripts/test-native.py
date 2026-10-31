from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
BUILD.mkdir(exist_ok=True)
subprocess.run(['xcrun', 'swiftc', '-module-cache-path', str(BUILD / 'swift-module-cache'),
                str(ROOT / 'native/Errors.swift'), str(ROOT / 'native/WindowPolicy.swift'), str(ROOT / 'native/tests/main.swift'),
                '-o', str(BUILD / 'window-policy-tests')], check=True)
subprocess.run([str(BUILD / 'window-policy-tests')], check=True)
subprocess.run(['xcrun', 'swiftc', '-module-cache-path', str(BUILD / 'swift-module-cache'),
                str(ROOT / 'native/NavigationPolicy.swift'), str(ROOT / 'native/tests/navigation/main.swift'),
                '-o', str(BUILD / 'navigation-regression-tests')], check=True)
subprocess.run([str(BUILD / 'navigation-regression-tests')], check=True)
