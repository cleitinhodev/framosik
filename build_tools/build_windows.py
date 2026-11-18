"""Build nativo Windows: python build_tools/build_windows.py."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if sys.platform != 'win32':
    raise SystemExit('Execute este build no Windows. Para Linux use o empacotamento portátil com Zig.')
subprocess.run([sys.executable,'-m','PyInstaller','--noconfirm','--clean','--windowed','--onedir',
    '--name','Framosik','--icon',str(ROOT/'assets/icons/framosik.ico'),
    '--add-data',str(ROOT/'assets')+';assets',str(ROOT/'main.py')],cwd=ROOT,check=True)
out = ROOT/'dist/Framosik'
for directory in ['examples','licenses']:
    shutil.copytree(ROOT/directory,out/directory,dirs_exist_ok=True)
for name in ['README.md','THIRD_PARTY.md','CHANGELOG.md']:
    shutil.copy2(ROOT/name,out/name)
# Testa a versão empacotada, não apenas os módulos do ambiente de desenvolvimento.
subprocess.run([str(out/'Framosik.exe'),'--smoke-test'],check=True,timeout=60)
shutil.make_archive(str(ROOT/'dist/Framosik-0.4.0-Windows-x64'),'zip',out.parent,out.name)
print('Windows build and executable smoke test passed.')
