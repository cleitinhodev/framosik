"""Build, launch and package the native Windows executable."""
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def version_resource(version):
    from PyInstaller.utils.win32 import versioninfo as vi

    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-beta\.(\d+))?", version)
    if not match:
        raise ValueError(f"Invalid application version: {version}")
    numbers = tuple(int(value or 0) for value in match.groups())
    strings = {"CompanyName": "Bugzinho / CleitinhoDEV", "FileDescription": "Framosik",
               "FileVersion": version, "InternalName": "Framosik", "OriginalFilename": "Framosik.exe",
               "ProductName": "Framosik", "ProductVersion": version}
    table = vi.StringTable("040904B0", [vi.StringStruct(k, v) for k, v in strings.items()])
    info = vi.VSVersionInfo(
        ffi=vi.FixedFileInfo(filevers=numbers, prodvers=numbers, mask=0x3f,
                             flags=0, OS=0x40004, fileType=1, subtype=0, date=(0, 0)),
        kids=[vi.StringFileInfo([table]), vi.VarFileInfo([vi.VarStruct("Translation", [1033, 1200])])])
    dest = ROOT / "build" / "windows-version.txt"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(str(info), encoding="utf-8")
    return dest


def main():
    if sys.platform != "win32":
        raise SystemExit("Build on Windows. On Linux use build_tools/build_linux.py.")
    version = runpy.run_path(str(ROOT / "app_info.py"))["VERSION"]
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed",
                    "--onedir", "--name", "Framosik", "--icon", str(ROOT / "assets/icons/framosik.ico"),
                    "--version-file", str(version_resource(version)),
                    "--add-data", str(ROOT / "assets") + ";assets", str(ROOT / "main.py")],
                   cwd=ROOT, check=True)
    out = ROOT / "dist" / "Framosik"
    for directory in ("examples", "licenses", "docs/images"):
        shutil.copytree(ROOT / directory, out / directory, dirs_exist_ok=True)
    for name in ("README.md", "THIRD_PARTY.md", "CHANGELOG.md"):
        shutil.copy2(ROOT / name, out / name)
    subprocess.run([sys.executable, str(ROOT / "build_tools/build_tutorial.py"),
                    "--output", str(out / "Framosik-Tutorial.html")], check=True)
    subprocess.run([str(out / "Framosik.exe"), "--smoke-test"], check=True, timeout=60)
    shutil.make_archive(str(ROOT / "dist" / f"Framosik-{version}-Windows-x64"), "zip", out.parent, out.name)
    print("Windows build and executable smoke test passed.")


if __name__ == "__main__":
    main()
