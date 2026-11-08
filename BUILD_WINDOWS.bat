@echo off
cd /d "%~dp0"
py -3 -m venv .build-venv
if errorlevel 1 goto error
.build-venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller==6.22.3
if errorlevel 1 goto error
.build-venv\Scripts\python.exe build_tools\build_windows.py
if errorlevel 1 goto error
echo Pronto: dist\Framosik\Framosik.exe
pause
exit /b 0
:error
echo A compilacao falhou. Consulte a mensagem acima.
pause
exit /b 1
