@echo off
cd /d "%~dp0"
echo Framosik - diagnostico de inicializacao
runtime\python.exe -c "import sys; print(sys.version); import numpy, cv2, PIL; from PySide6.QtWidgets import QApplication; print('Dependencias OK')"
if errorlevel 1 goto done
runtime\python.exe app\main.py
:done
pause
