"""Recria a distribuição portátil x64 com Python embutido e um launcher C.

Requer internet, Python 3.12 e `python -m pip install ziglang==0.13.0`.
Execute da raiz do projeto: python build_tools/build_portable.py
Saída: portable/Framosik_Windows. Usa rodas Windows, mesmo em Linux.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile
import ziglang

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'portable'/'Framosik_Windows'
CACHE = ROOT/'portable'/'downloads'
CACHE.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
python_zip = CACHE/'python-3.12.10-embed-amd64.zip'
if not python_zip.exists():
    urllib.request.urlretrieve('https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip', python_zip)
subprocess.run([sys.executable, '-m', 'pip', 'download', '--dest', str(CACHE), '--only-binary=:all:',
                '--platform', 'win_amd64', '--python-version', '312', '--implementation', 'cp', '--abi', 'cp312',
                '-r', str(ROOT/'requirements.txt')], check=True)
runtime = OUT/'runtime'
site = runtime/'Lib'/'site-packages'
site.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(python_zip) as z:
    z.extractall(runtime)
for wheel in CACHE.glob('*.whl'):
    with zipfile.ZipFile(wheel) as z:
        z.extractall(site)
(runtime/'python312._pth').write_text('python312.zip\n.\nLib/site-packages\n../app\nimport site\n', encoding='ascii')
include = Path(ziglang.__file__).parent/'lib/libc/include/any-windows-any'
resource = CACHE/'framosik.res'
subprocess.run([sys.executable,'-m','ziglang','rc','/fo',str(resource),str(ROOT/'build_tools/framosik.rc')],cwd=ROOT,check=True)
subprocess.run([sys.executable, '-m', 'ziglang', 'cc', '-target', 'x86_64-windows-gnu', '-O2', '-nostdlib',
                '-I', str(include), '-Wno-macro-redefined', '-Wno-missing-declarations',
                '-Wl,--entry,entry', '-Wl,--subsystem,windows', str(ROOT/'build_tools/launcher.c'),
                str(resource), '-o', str(OUT/'Framosik.exe'), '-lkernel32', '-luser32'], check=True)
app = OUT/'app'
app.mkdir(exist_ok=True)
for file in ROOT.glob('*.py'):
    shutil.copy2(file, app/file.name)
shutil.copytree(ROOT/'assets', app/'assets', dirs_exist_ok=True)
shutil.copytree(ROOT/'examples', OUT/'examples', dirs_exist_ok=True)
shutil.copytree(ROOT/'licenses', OUT/'licenses', dirs_exist_ok=True)
shutil.copy2(ROOT/'README.md', OUT/'LEIA-ME.md')
shutil.copy2(ROOT/'THIRD_PARTY.md', OUT/'THIRD_PARTY.md')
shutil.copy2(ROOT/'build_tools/DIAGNOSTICO.bat', OUT/'DIAGNOSTICO.bat')
print(f'Pronto: {OUT}')
