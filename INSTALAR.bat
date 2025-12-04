@echo off
REM ============================================
REM   ZDex - Instalador Rápido para Windows
REM ============================================
REM   Este script prepara todo para usar ZDex
REM ============================================

echo.
echo ===============================================
echo   🦁 ZDex - Instalador Rapido
echo ===============================================
echo.

REM Verificar Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python no esta instalado
    echo.
    echo Por favor, instala Python 3.10 o superior:
    echo   1. Ve a https://www.python.org/downloads/
    echo   2. Descarga Python 3.11 o 3.12
    echo   3. IMPORTANTE: Marca "Add Python to PATH" durante instalacion
    echo   4. Reinicia este script
    echo.
    pause
    exit /b 1
)

python --version
echo ✓ Python encontrado
echo.

REM Verificar pip
echo [2/4] Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Instalando pip...
    python -m ensurepip --upgrade
)
echo ✓ pip OK
echo.

REM Instalar dependencias
echo [3/4] Instalando dependencias (esto puede tomar varios minutos)...
echo.
python -m pip install --upgrade pip

REM Instalar PyTorch CPU (más ligero)
echo Instalando PyTorch...
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

REM Instalar resto de dependencias
echo Instalando dependencias adicionales...
python -m pip install -r yolov12\requirements.txt

echo.
echo ✓ Dependencias instaladas
echo.

REM Verificar instalación
echo [4/4] Verificando instalacion...
python -c "import cv2; import torch; import tkinter; print('✓ Todas las dependencias OK')"
if errorlevel 1 (
    echo.
    echo ⚠ Algunas dependencias pueden faltar
    echo Intenta ejecutar ZDex de todos modos
)

echo.
echo ===============================================
echo   ✓ INSTALACION COMPLETADA
echo ===============================================
echo.
echo Para ejecutar ZDex:
echo   - Doble click en "ZDex.bat"
echo   - O ejecuta: python run_zdex.py
echo.
echo ===============================================
echo.
pause
