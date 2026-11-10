"""Build Linux x86_64. Optionally package an existing release checkout."""
import argparse
import ast
import hashlib
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.source.resolve()
    if sys.platform != 'linux' or platform.machine() not in {'x86_64', 'AMD64'}:
        raise SystemExit('Build on Linux x86_64 (Ubuntu 22.04 recommended).')
    info = ast.parse((root/'app_info.py').read_text())
    version = next(ast.literal_eval(n.value) for n in info.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'VERSION' for t in n.targets))
    tag = os.environ.get('RELEASE_TAG')
    if tag and tag != 'v'+version:
        raise SystemExit('Release tag does not match application version.')
    subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir',
                    '--name', 'Framosik', '--add-data', str(root/'assets')+':assets',
                    str(root/'main.py')], cwd=root, check=True)
    out = root/'dist/Framosik'
    for directory in ['examples', 'licenses']:
        shutil.copytree(root/directory, out/directory, dirs_exist_ok=True)
    for name in ['README.md', 'THIRD_PARTY.md', 'CHANGELOG.md']:
        shutil.copy2(root/name, out/name)
    packaging = Path(__file__).resolve().parent
    shutil.copy2(packaging.parent/'LINUX.md', out/'LEIA-ME-LINUX.md')
    shutil.copy2(__file__, out/'build_linux.py')
    # Test the frozen executable, then test an extracted copy from another cwd.
    env = dict(os.environ, QT_QPA_PLATFORM='offscreen')
    subprocess.run([str(out/'Framosik'), '--smoke-test'], env=env, check=True, timeout=60)
    archive = root/'dist'/f'Framosik-{version}-Linux-x86_64.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        tar.add(out, arcname='Framosik')
    with tempfile.TemporaryDirectory(prefix='framosik extract ') as temp:
        with tarfile.open(archive) as tar:
            tar.extractall(temp, filter='data')
        executable = Path(temp)/'Framosik/Framosik'
        subprocess.run(['xvfb-run', '-a', str(executable), '--smoke-test'], cwd=temp,
                       env=dict(os.environ, QT_QPA_PLATFORM='xcb'), check=True, timeout=60)
    with archive.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    archive.with_suffix(archive.suffix+'.sha256').write_text(f'{digest}  {archive.name}\n')
    print(f'Built and tested: {archive}')


if __name__ == '__main__':
    main()
