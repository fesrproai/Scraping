#!/usr/bin/env python3
"""
Script para crear un ejecutable del sistema de scraping para el escritorio
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Instala PyInstaller si no está instalado"""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
        return True
    except ImportError:
        print("📦 Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("✅ PyInstaller instalado correctamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error instalando PyInstaller")
            return False

def create_spec_file():
    """Crea el archivo .spec para el ejecutable"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Archivos y directorios a incluir
added_files = [
    ('utils', 'utils'),
    ('scrapers', 'scrapers'),
    ('data', 'data'),
    ('requirements.txt', '.'),
]

# Imports ocultos necesarios
hidden_imports = [
    'requests',
    'beautifulsoup4',
    'lxml',
    'matplotlib',
    'numpy',
    'sqlite3',
    'json',
    'csv',
    'datetime',
    'hashlib',
    'difflib',
    're',
    'os',
    'sys',
    'pathlib'
]

a = Analysis(
    ['main_cli.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Sistema_Descuentos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
'''
    
    with open('Sistema_Descuentos.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Archivo .spec creado")

def build_executable():
    """Construye el ejecutable"""
    print("🔨 Construyendo ejecutable...")
    
    try:
        # Usar PyInstaller para crear el ejecutable
        subprocess.check_call([
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--console',
            '--name=Sistema_Descuentos',
            '--add-data=utils;utils',
            '--add-data=scrapers;scrapers',
            '--add-data=data;data',
            '--hidden-import=requests',
            '--hidden-import=beautifulsoup4',
            '--hidden-import=lxml',
            '--hidden-import=matplotlib',
            '--hidden-import=numpy',
            '--hidden-import=sqlite3',
            '--hidden-import=json',
            '--hidden-import=csv',
            '--hidden-import=datetime',
            '--hidden-import=hashlib',
            '--hidden-import=difflib',
            '--hidden-import=re',
            'main_cli.py'
        ])
        
        print("✅ Ejecutable creado exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error construyendo ejecutable: {e}")
        return False

def create_desktop_shortcut():
    """Crea un acceso directo en el escritorio"""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    exe_path = os.path.join("dist", "Sistema_Descuentos.exe")
    
    if os.path.exists(exe_path):
        # Copiar al escritorio
        desktop_exe = os.path.join(desktop_path, "Sistema_Descuentos.exe")
        shutil.copy2(exe_path, desktop_exe)
        print(f"✅ Ejecutable copiado al escritorio: {desktop_exe}")
        return True
    else:
        print("❌ No se encontró el ejecutable")
        return False

def main():
    """Función principal"""
    print("🚀 Creando ejecutable para el escritorio...")
    print("=" * 50)
    
    # Paso 1: Instalar PyInstaller
    if not install_pyinstaller():
        return False
    
    # Paso 2: Crear archivo .spec
    create_spec_file()
    
    # Paso 3: Construir ejecutable
    if not build_executable():
        return False
    
    # Paso 4: Crear acceso directo en escritorio
    if create_desktop_shortcut():
        print("\n🎉 ¡Ejecutable creado exitosamente!")
        print("📁 Ubicación: Escritorio/Sistema_Descuentos.exe")
        print("💡 Puedes hacer doble clic para ejecutar desde cualquier lugar")
        return True
    
    return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Error en el proceso")
        sys.exit(1) 