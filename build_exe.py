#!/usr/bin/env python3
"""
Script para construir el ejecutable del sistema de scraping
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """Instala las dependencias necesarias para PyInstaller"""
    print("📦 Instalando dependencias...")
    
    requirements = [
        'pyinstaller',
        'auto-py-to-exe'  # Interfaz gráfica opcional
    ]
    
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])
            print(f"✅ {req} instalado")
        except subprocess.CalledProcessError:
            print(f"❌ Error instalando {req}")
            return False
    
    return True

def create_spec_file():
    """Crea el archivo .spec para PyInstaller"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Archivos y directorios a incluir
added_files = [
    ('config', 'config'),
    ('scrapers', 'scrapers'),
    ('core', 'core'),
    ('database', 'database'),
    ('scheduler', 'scheduler'),
    ('api', 'api'),
    ('utils', 'utils'),
    ('frontend', 'frontend'),
    ('.env.example', '.'),
    ('requirements.txt', '.'),
    ('README.md', '.'),
    ('INSTALACION.md', '.'),
]

# Archivos ocultos (no mostrar en consola)
hidden_imports = [
    'selenium',
    'selenium.webdriver',
    'selenium.webdriver.chrome.options',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support',
    'selenium.webdriver.support.expected_conditions',
    'selenium.common.exceptions',
    'firebase_admin',
    'firebase_admin.credentials',
    'firebase_admin.firestore',
    'flask',
    'flask_cors',
    'schedule',
    'fake_useragent',
    'retrying',
    'aiohttp',
    'asyncio',
    'pandas',
    'numpy',
    'beautifulsoup4',
    'lxml',
    'requests',
    'python-dotenv',
    'gunicorn',
    'react',
    'react-dom',
    'react-router-dom',
    'axios',
    'react-icons',
    'tailwindcss',
    'autoprefixer',
    'postcss'
]

a = Analysis(
    ['main.py'],
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
    name='DescuentosCL',
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('DescuentosCL.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Archivo .spec creado")

def create_launcher_script():
    """Crea un script launcher para el ejecutable"""
    launcher_content = '''@echo off
chcp 65001 >nul
title DescuentosCL - Sistema de Scraping

echo.
echo ========================================
echo    DESCUENTOSCL - SISTEMA DE SCRAPING
echo ========================================
echo.

:menu
echo Selecciona una opción:
echo.
echo 1. Ejecutar scraping completo
echo 2. Probar scrapers individuales
echo 3. Iniciar scheduler automático
echo 4. Iniciar API web
echo 5. Configurar Firebase
echo 6. Ver ayuda
echo 7. Salir
echo.

set /p choice="Ingresa tu opción (1-7): "

if "%choice%"=="1" goto full_scraping
if "%choice%"=="2" goto test_scrapers
if "%choice%"=="3" goto scheduler
if "%choice%"=="4" goto api
if "%choice%"=="5" goto config
if "%choice%"=="6" goto help
if "%choice%"=="7" goto exit
goto menu

:full_scraping
echo.
echo 🚀 Iniciando scraping completo...
echo.
DescuentosCL.exe --store all --verbose
echo.
pause
goto menu

:test_scrapers
echo.
echo 🧪 Iniciando pruebas de scrapers...
echo.
DescuentosCL.exe test_scrapers.py --store all --save-report
echo.
pause
goto menu

:scheduler
echo.
echo ⏰ Iniciando scheduler automático...
echo.
DescuentosCL.exe scheduler/scheduler.py
echo.
pause
goto menu

:api
echo.
echo 🌐 Iniciando API web...
echo.
DescuentosCL.exe api/app.py
echo.
pause
goto menu

:config
echo.
echo ⚙️  Configuración de Firebase
echo.
echo 1. Ve a https://console.firebase.google.com
echo 2. Crea un nuevo proyecto
echo 3. Ve a Configuración > Cuentas de servicio
echo 4. Genera una nueva clave privada
echo 5. Copia el archivo .env.example a .env
echo 6. Edita .env con tus credenciales
echo.
echo ¿Necesitas ayuda? Revisa INSTALACION.md
echo.
pause
goto menu

:help
echo.
echo 📖 AYUDA - DESCUENTOSCL
echo ========================
echo.
echo COMANDOS DISPONIBLES:
echo.
echo DescuentosCL.exe --store all
echo   Ejecuta scraping en todas las tiendas
echo.
echo DescuentosCL.exe --store paris
echo   Ejecuta scraping solo en Paris
echo.
echo DescuentosCL.exe --store falabella
echo   Ejecuta scraping solo en Falabella
echo.
echo DescuentosCL.exe --min-discount 80
echo   Filtra productos con 80%% o más descuento
echo.
echo DescuentosCL.exe --dry-run
echo   Ejecuta sin guardar en Firebase
echo.
echo OPCIONES DISPONIBLES:
echo --store: paris, falabella, ripley, lapolar, hites, sodimac, all
echo --min-discount: porcentaje mínimo (default: 70)
echo --verbose: mostrar logs detallados
echo --dry-run: no guardar en base de datos
echo.
echo TIENDAS SOPORTADAS:
echo • Paris.cl - Ropa, tecnología, hogar
echo • Falabella.com - Categorización excelente
echo • Ripley.cl - Fácil scraping, muchos descuentos
echo • La Polar.cl - Vestuario y hogar
echo • Hites.com - Productos rebajados
echo • Sodimac.cl - Hogar y construcción
echo.
pause
goto menu

:exit
echo.
echo 👋 ¡Gracias por usar DescuentosCL!
echo.
exit
'''
    
    with open('DescuentosCL.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✅ Script launcher creado")

def create_installer_script():
    """Crea un script de instalación"""
    installer_content = '''@echo off
chcp 65001 >nul
title Instalador DescuentosCL

echo.
echo ========================================
echo    INSTALADOR DESCUENTOSCL
echo ========================================
echo.

echo 🚀 Iniciando instalación...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado
    echo.
    echo Por favor instala Python 3.8+ desde:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python detectado
echo.

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas
echo.

REM Crear archivo de configuración
if not exist .env (
    echo ⚙️  Creando archivo de configuración...
    copy .env.example .env
    echo ✅ Archivo .env creado
    echo.
    echo ⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales de Firebase
    echo.
) else (
    echo ✅ Archivo .env ya existe
)

echo.
echo ========================================
echo    INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo 🎉 ¡DescuentosCL ha sido instalado correctamente!
echo.
echo PRÓXIMOS PASOS:
echo 1. Configura Firebase (edita .env)
echo 2. Ejecuta: DescuentosCL.bat
echo 3. Selecciona "Configurar Firebase" en el menú
echo.
echo Para más información, revisa:
echo • README.md
echo • INSTALACION.md
echo.
pause
'''
    
    with open('instalar.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("✅ Script de instalación creado")

def build_executable():
    """Construye el ejecutable usando PyInstaller"""
    print("🔨 Construyendo ejecutable...")
    
    try:
        # Usar el archivo .spec personalizado
        subprocess.check_call([
            'pyinstaller',
            '--clean',
            '--noconfirm',
            'DescuentosCL.spec'
        ])
        
        print("✅ Ejecutable construido exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error construyendo ejecutable: {e}")
        return False

def create_distribution():
    """Crea el paquete de distribución"""
    print("📦 Creando paquete de distribución...")
    
    dist_dir = Path('dist/DescuentosCL')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # Crear directorio de distribución
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copiar archivos necesarios
    files_to_copy = [
        'DescuentosCL.bat',
        'instalar.bat',
        'README.md',
        'INSTALACION.md',
        '.env.example',
        'requirements.txt'
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy2(file, dist_dir)
    
    # Copiar ejecutable
    exe_path = Path('dist/DescuentosCL.exe')
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir)
    
    # Crear archivo README para distribución
    dist_readme = '''# DescuentosCL - Sistema de Scraping

## 🚀 Instalación Rápida

1. **Ejecuta el instalador:**
   ```
   instalar.bat
   ```

2. **Configura Firebase:**
   - Edita el archivo `.env` con tus credenciales
   - Sigue las instrucciones en `INSTALACION.md`

3. **Ejecuta el sistema:**
   ```
   DescuentosCL.bat
   ```

## 📋 Requisitos

- Windows 10/11
- Python 3.8+ (se instala automáticamente)
- Conexión a internet
- Cuenta de Firebase (gratuita)

## 🛠️ Comandos Disponibles

```
DescuentosCL.exe --store all          # Todas las tiendas
DescuentosCL.exe --store paris        # Solo Paris
DescuentosCL.exe --min-discount 80    # 80%+ descuento
DescuentosCL.exe --verbose            # Logs detallados
```

## 🏪 Tiendas Soportadas

- **Paris.cl** - Ropa, tecnología, hogar
- **Falabella.com** - Categorización excelente
- **Ripley.cl** - Fácil scraping, muchos descuentos
- **La Polar.cl** - Vestuario y hogar
- **Hites.com** - Productos rebajados
- **Sodimac.cl** - Hogar y construcción

## 📞 Soporte

Para ayuda adicional, revisa:
- `README.md` - Documentación completa
- `INSTALACION.md` - Guía de instalación
- Logs en `scraping.log`

---
Desarrollado con ❤️ para encontrar las mejores ofertas en Chile
'''
    
    with open(dist_dir / 'README_DISTRIBUCION.md', 'w', encoding='utf-8') as f:
        f.write(dist_readme)
    
    print("✅ Paquete de distribución creado")
    print(f"📁 Ubicación: {dist_dir.absolute()}")

def main():
    print("🔨 CONSTRUCTOR DE EJECUTABLE - DESCUENTOSCL")
    print("=" * 50)
    
    # Paso 1: Instalar dependencias
    if not install_requirements():
        print("❌ Error instalando dependencias")
        return 1
    
    # Paso 2: Crear archivos de configuración
    create_spec_file()
    create_launcher_script()
    create_installer_script()
    
    # Paso 3: Construir ejecutable
    if not build_executable():
        print("❌ Error construyendo ejecutable")
        return 1
    
    # Paso 4: Crear distribución
    create_distribution()
    
    print("\n" + "=" * 50)
    print("🎉 ¡CONSTRUCCIÓN COMPLETADA!")
    print("=" * 50)
    print("\n📦 Archivos generados:")
    print("  • dist/DescuentosCL/DescuentosCL.exe")
    print("  • dist/DescuentosCL/DescuentosCL.bat")
    print("  • dist/DescuentosCL/instalar.bat")
    print("  • dist/DescuentosCL/README_DISTRIBUCION.md")
    print("\n🚀 Para distribuir:")
    print("  1. Comprime la carpeta dist/DescuentosCL/")
    print("  2. Comparte el archivo ZIP")
    print("  3. Los usuarios ejecutan instalar.bat")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 