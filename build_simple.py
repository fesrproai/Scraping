#!/usr/bin/env python3
"""
Script simple para construir el ejecutable
"""

import os
import sys
import subprocess

def main():
    print("🔨 Construyendo DescuentosCL.exe...")
    
    # Instalar PyInstaller si no está instalado
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Comando para construir el ejecutable
    cmd = [
        'pyinstaller',
        '--onefile',  # Un solo archivo
        '--console',  # Con consola
        '--name=DescuentosCL',
        '--add-data=config;config',
        '--add-data=scrapers;scrapers',
        '--add-data=core;core',
        '--add-data=database;database',
        '--add-data=scheduler;scheduler',
        '--add-data=api;api',
        '--add-data=utils;utils',
        '--add-data=frontend;frontend',
        '--add-data=.env.example;.',
        '--add-data=requirements.txt;.',
        '--add-data=README.md;.',
        '--hidden-import=selenium',
        '--hidden-import=selenium.webdriver',
        '--hidden-import=selenium.webdriver.chrome.options',
        '--hidden-import=firebase_admin',
        '--hidden-import=firebase_admin.credentials',
        '--hidden-import=firebase_admin.firestore',
        '--hidden-import=flask',
        '--hidden-import=flask_cors',
        '--hidden-import=schedule',
        '--hidden-import=fake_useragent',
        '--hidden-import=retrying',
        '--hidden-import=beautifulsoup4',
        '--hidden-import=lxml',
        '--hidden-import=requests',
        '--hidden-import=python-dotenv',
        'main.py'
    ]
    
    try:
        print("🔨 Ejecutando PyInstaller...")
        subprocess.check_call(cmd)
        
        print("\n✅ ¡Ejecutable creado exitosamente!")
        print("📁 Ubicación: dist/DescuentosCL.exe")
        print("\n🚀 Para usar:")
        print("  dist/DescuentosCL.exe --store all")
        print("  dist/DescuentosCL.exe --store paris --verbose")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 