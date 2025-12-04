@echo off
REM ============================================
REM   ZDex - Launcher
REM ============================================

echo.
echo  🦁 Iniciando ZDex...
echo.

python run_zdex.py

if errorlevel 1 (
    echo.
    echo ===============================================
    echo   ⚠ ZDex se cerro con un error
    echo ===============================================
    echo.
    echo Posibles soluciones:
    echo   1. Ejecuta INSTALAR.bat primero
    echo   2. Verifica que la camara no este en uso
    echo   3. Cierra Zoom/Teams/Skype
    echo.
    pause
)
