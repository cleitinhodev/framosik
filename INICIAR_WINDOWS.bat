@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
  if errorlevel 1 goto error
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 goto error
)
.venv\Scripts\python.exe main.py
if errorlevel 1 goto error
exit /b 0
:error
 echo Nao foi possivel iniciar. Instale Python 3.12 de 64 bits e tente novamente.
 pause
 exit /b 1
