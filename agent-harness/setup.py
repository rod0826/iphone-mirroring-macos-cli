import platform

from setuptools import Distribution, find_namespace_packages, setup
from setuptools.command.bdist_wheel import bdist_wheel


class NativeDistribution(Distribution):
    def has_ext_modules(self):
        return True


class MacWheel(bdist_wheel):
    """The helper is a native executable targeting macOS 15+, not pure Python."""
    def get_tag(self):
        return 'py3', 'none', f'macosx_15_0_{platform.machine()}'

setup(
    name='cli-anything-iphone-mirroring', version='0.1.0', python_requires='>=3.10',
    packages=find_namespace_packages(include=['cli_anything.*']),
    install_requires=['click>=8.1,<9', 'prompt_toolkit>=3,<4'],
    extras_require={'test': ['pytest>=8,<10']},
    cmdclass={'bdist_wheel': MacWheel},
    distclass=NativeDistribution,
    package_data={'cli_anything.iphone_mirroring': [
        'bin/IPhoneMirroringCLI.app/Contents/Info.plist',
        'bin/IPhoneMirroringCLI.app/Contents/MacOS/*',
        'bin/IPhoneMirroringCLI.app/Contents/_CodeSignature/*', 'skills/*.md', 'README.md'
    ]},
    entry_points={'console_scripts': [
        'cli-anything-iphone-mirroring=cli_anything.iphone_mirroring.iphone_mirroring_cli:main'
    ]},
)
