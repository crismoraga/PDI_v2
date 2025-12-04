#!/usr/bin/env python3
"""
ZDex Release Builder
====================
Script para crear un release distribuible de ZDex.

Uso:
    python build_release.py          # Build completo
    python build_release.py --test   # Solo verificar dependencias
"""

import subprocess
import sys
import shutil
import os
from pathlib import Path

# Colores para output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(msg):
    print(f"\n{Colors.BLUE}{Colors.BOLD}▶ {msg}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas."""
    print_step("Verificando dependencias...")
    
    required = ['pyinstaller', 'pillow', 'torch', 'cv2', 'numpy']
    missing = []
    
    for pkg in required:
        try:
            if pkg == 'cv2':
                import cv2
            elif pkg == 'pyinstaller':
                import PyInstaller
            elif pkg == 'pillow':
                from PIL import Image
            elif pkg == 'torch':
                import torch
            elif pkg == 'numpy':
                import numpy
            print_success(f"{pkg} instalado")
        except ImportError:
            missing.append(pkg)
            print_error(f"{pkg} NO instalado")
    
    if missing:
        print_warning(f"\nInstala las dependencias faltantes:")
        print(f"  pip install {' '.join(missing)}")
        if 'pyinstaller' in missing:
            print(f"  pip install pyinstaller")
        return False
    
    return True

def clean_build():
    """Limpiar directorios de builds anteriores."""
    print_step("Limpiando builds anteriores...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for d in dirs_to_clean:
        if os.path.exists(d):
            shutil.rmtree(d)
            print_success(f"Eliminado: {d}/")
    
    # Limpiar .spec files
    for spec in Path('.').glob('*.spec'):
        spec.unlink()
        print_success(f"Eliminado: {spec}")

def create_spec_file():
    """Crear archivo .spec personalizado para PyInstaller."""
    print_step("Creando configuración de PyInstaller...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
# ZDex PyInstaller Spec File

import sys
from pathlib import Path

block_cipher = None

# Rutas del proyecto
PROJECT_ROOT = Path(SPECPATH)

# Datos adicionales a incluir
added_files = [
    # Modelos (se descargan en primer uso, pero incluimos placeholder)
    (str(PROJECT_ROOT / 'models'), 'models'),
    # Datos iniciales
    (str(PROJECT_ROOT / 'data'), 'data'),
    # Taxonomía de especies
    (str(PROJECT_ROOT / 'taxonomy_release.txt'), '.'),
    # Geofence
    (str(PROJECT_ROOT / 'geofence_release.2025.02.27.0702.json'), '.'),
    # Info
    (str(PROJECT_ROOT / 'info.json'), '.'),
]

# Filtrar solo los que existen
added_files = [(src, dst) for src, dst in added_files if Path(src).exists()]

a = Analysis(
    ['run_zdex.py'],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PIL._tkinter_finder',
        'torch',
        'torchvision',
        'cv2',
        'numpy',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'requests',
        'json',
        'threading',
        'queue',
        'datetime',
        'pathlib',
        'ultralytics',
        'ultralytics.nn',
        'ultralytics.nn.modules',
        'ultralytics.utils',
        'zdex',
        'zdex.app',
        'zdex.camera',
        'zdex.config',
        'zdex.detector',
        'zdex.pipeline',
        'zdex.gamification',
        'zdex.geolocation',
        'zdex.species',
        'zdex.wikipedia_client',
        'zdex.data_store',
        'zdex.metrics',
        'zdex.ui',
        'zdex.ui.styles',
        'zdex.ui.panels',
        'zdex.ui.camera_canvas',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Solo necesario para reportes, no para app
        'jupyter',
        'notebook',
        'IPython',
        'pytest',
        'sphinx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ZDex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/zdex_icon.ico' if Path('assets/zdex_icon.ico').exists() else None,
)
'''
    
    with open('ZDex.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print_success("Creado: ZDex.spec")

def build_executable():
    """Construir el ejecutable con PyInstaller."""
    print_step("Construyendo ejecutable (esto puede tomar varios minutos)...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', 'ZDex.spec', '--clean'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Ejecutable creado exitosamente")
            return True
        else:
            print_error("Error en PyInstaller:")
            print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def create_release_package():
    """Crear el paquete final de release."""
    print_step("Creando paquete de release...")
    
    release_dir = Path('release')
    release_dir.mkdir(exist_ok=True)
    
    # Copiar ejecutable
    exe_path = Path('dist/ZDex.exe')
    if exe_path.exists():
        shutil.copy(exe_path, release_dir / 'ZDex.exe')
        print_success("Copiado: ZDex.exe")
    
    # Crear README para el release
    readme_content = '''# 🦁 ZDex — Instalación Rápida

## Windows

1. **Descarga** `ZDex.exe` de este release
2. **Ejecuta** `ZDex.exe` (doble click)
3. **¡Listo!** La aplicación se abrirá automáticamente

> ⚠️ Windows SmartScreen puede mostrar una advertencia. 
> Click en "Más información" → "Ejecutar de todos modos"

## Primera Ejecución

- Los modelos de IA se descargarán automáticamente (~500 MB)
- Esto solo ocurre la primera vez
- Requiere conexión a internet

## Requisitos

- Windows 10/11 (64-bit)
- 8 GB RAM mínimo
- Webcam (integrada o USB)
- Conexión a internet (primera vez)

## Problemas Comunes

### "Windows protegió tu PC"
1. Click en "Más información"
2. Click en "Ejecutar de todos modos"

### La cámara no funciona
1. Cierra Zoom, Teams, Skype
2. Verifica permisos en Configuración → Privacidad → Cámara

### Muy lento
- Cierra otras aplicaciones
- La primera detección es más lenta (carga de modelos)

## Soporte

- 📖 [Documentación completa](https://github.com/crismoraga/PDI_v2)
- 🐛 [Reportar problema](https://github.com/crismoraga/PDI_v2/issues)
- 📺 [Video demo](https://youtu.be/MNIEpdeGOdA)

---
*ZDex v3.0 — Universidad Técnica Federico Santa María*
'''
    
    with open(release_dir / 'README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print_success("Creado: README.md")
    
    # Crear ZIP del release
    print_step("Creando archivo ZIP...")
    shutil.make_archive('ZDex-v3.0-Windows', 'zip', release_dir)
    print_success("Creado: ZDex-v3.0-Windows.zip")
    
    return True

def create_portable_package():
    """Crear paquete portable (sin PyInstaller, requiere Python)."""
    print_step("Creando paquete portable (alternativo)...")
    
    portable_dir = Path('release-portable')
    portable_dir.mkdir(exist_ok=True)
    
    # Copiar código fuente necesario
    dirs_to_copy = ['zdex', 'models', 'data']
    files_to_copy = [
        'run_zdex.py', 
        'taxonomy_release.txt',
        'geofence_release.2025.02.27.0702.json',
        'info.json',
        'test_detection.py',
    ]
    
    for d in dirs_to_copy:
        if os.path.exists(d):
            shutil.copytree(d, portable_dir / d, dirs_exist_ok=True)
            print_success(f"Copiado: {d}/")
    
    for f in files_to_copy:
        if os.path.exists(f):
            shutil.copy(f, portable_dir / f)
            print_success(f"Copiado: {f}")
    
    # Crear requirements mínimo
    requirements = '''# ZDex - Requisitos mínimos
torch>=2.0.0
torchvision>=0.15.0
opencv-python>=4.8.0
pillow>=9.0.0
numpy>=1.24.0
requests>=2.28.0
ultralytics>=8.0.0
'''
    
    with open(portable_dir / 'requirements.txt', 'w') as f:
        f.write(requirements)
    print_success("Creado: requirements.txt")
    
    # Script de instalación rápida
    install_script = '''@echo off
echo ========================================
echo    ZDex - Instalador Rapido
echo ========================================
echo.

echo [1/3] Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no encontrado
    echo Descarga Python 3.10+ desde python.org
    pause
    exit /b 1
)

echo.
echo [2/3] Instalando dependencias...
pip install -r requirements.txt

echo.
echo [3/3] Instalacion completa!
echo.
echo Para ejecutar ZDex:
echo   python run_zdex.py
echo.
pause
'''
    
    with open(portable_dir / 'instalar.bat', 'w') as f:
        f.write(install_script)
    print_success("Creado: instalar.bat")
    
    # Script de ejecución
    run_script = '''@echo off
python run_zdex.py
if errorlevel 1 pause
'''
    
    with open(portable_dir / 'ZDex.bat', 'w') as f:
        f.write(run_script)
    print_success("Creado: ZDex.bat")
    
    # ZIP portable
    shutil.make_archive('ZDex-v3.0-Portable', 'zip', portable_dir)
    print_success("Creado: ZDex-v3.0-Portable.zip")
    
    return True

def print_summary():
    """Mostrar resumen final."""
    print(f"\n{'='*60}")
    print(f"{Colors.GREEN}{Colors.BOLD}✓ BUILD COMPLETADO{Colors.END}")
    print(f"{'='*60}\n")
    
    print("📦 Archivos generados:")
    
    if os.path.exists('ZDex-v3.0-Windows.zip'):
        size = os.path.getsize('ZDex-v3.0-Windows.zip') / (1024*1024)
        print(f"   • ZDex-v3.0-Windows.zip ({size:.1f} MB) - Ejecutable standalone")
    
    if os.path.exists('ZDex-v3.0-Portable.zip'):
        size = os.path.getsize('ZDex-v3.0-Portable.zip') / (1024*1024)
        print(f"   • ZDex-v3.0-Portable.zip ({size:.1f} MB) - Requiere Python")
    
    print(f"\n📋 Próximos pasos:")
    print(f"   1. Sube los .zip a GitHub Releases")
    print(f"   2. Crea un nuevo release en: github.com/crismoraga/PDI_v2/releases/new")
    print(f"   3. Tag sugerido: v3.0.0")
    print(f"   4. Adjunta los archivos .zip")

def main():
    print(f"\n{'='*60}")
    print(f"{Colors.BOLD}🦁 ZDex Release Builder{Colors.END}")
    print(f"{'='*60}")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('run_zdex.py'):
        print_error("Ejecuta este script desde el directorio raíz del proyecto")
        sys.exit(1)
    
    # Modo test
    if '--test' in sys.argv:
        check_dependencies()
        sys.exit(0)
    
    # Build completo
    if not check_dependencies():
        print_warning("\nInstalando PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    clean_build()
    create_spec_file()
    
    # Intentar build con PyInstaller
    exe_success = build_executable()
    
    if exe_success:
        create_release_package()
    else:
        print_warning("Build de ejecutable falló, creando solo paquete portable")
    
    # Siempre crear portable como alternativa
    create_portable_package()
    
    print_summary()

if __name__ == '__main__':
    main()
