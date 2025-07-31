#!/usr/bin/env python3
"""
Script completo para construir ejecutables y instaladores
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Instala PyInstaller"""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
        return True
    except ImportError:
        print("📦 Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print("✅ PyInstaller instalado")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error instalando PyInstaller")
            return False

def build_exe():
    """Construye el ejecutable .exe"""
    print("\n🔨 Construyendo DescuentosCL.exe...")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--console',
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
        '--add-data=INSTALACION.md;.',
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
        subprocess.check_call(cmd)
        print("✅ DescuentosCL.exe construido exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error construyendo .exe: {e}")
        return False

def create_launcher_bat():
    """Crea el archivo .bat launcher"""
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
    
    print("✅ DescuentosCL.bat creado")

def create_installer_bat():
    """Crea el script de instalación"""
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
    
    print("✅ instalar.bat creado")

def create_distribution_package():
    """Crea el paquete de distribución"""
    print("\n📦 Creando paquete de distribución...")
    
    dist_dir = Path('dist/DescuentosCL')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
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
    
    # Crear README para distribución
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

def check_inno_setup():
    """Verifica si Inno Setup está instalado"""
    inno_compiler = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if os.path.exists(inno_compiler):
        return inno_compiler
    return None

def build_msi():
    """Construye el instalador MSI usando Inno Setup"""
    print("\n🔨 Construyendo instalador MSI...")
    
    inno_compiler = check_inno_setup()
    if not inno_compiler:
        print("❌ Inno Setup no está instalado")
        print("📥 Descarga desde: https://jrsoftware.org/isdl.php")
        return False
    
    try:
        subprocess.check_call([inno_compiler, 'installer.iss'])
        print("✅ Instalador MSI construido exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error construyendo MSI: {e}")
        return False

def main():
    print("🔨 CONSTRUCTOR COMPLETO - DESCUENTOSCL")
    print("=" * 50)
    
    # Paso 1: Instalar PyInstaller
    if not install_pyinstaller():
        return 1
    
    # Paso 2: Crear archivos de soporte
    create_launcher_bat()
    create_installer_bat()
    
    # Paso 3: Construir ejecutable
    if not build_exe():
        return 1
    
    # Paso 4: Crear paquete de distribución
    create_distribution_package()
    
    # Paso 5: Intentar construir MSI
    print("\n🔍 Verificando Inno Setup...")
    if check_inno_setup():
        build_msi()
    else:
        print("⚠️  Inno Setup no encontrado - Solo se creará el .exe")
    
    print("\n" + "=" * 50)
    print("🎉 ¡CONSTRUCCIÓN COMPLETADA!")
    print("=" * 50)
    print("\n📦 Archivos generados:")
    print("  • dist/DescuentosCL.exe")
    print("  • dist/DescuentosCL/ (paquete completo)")
    print("  • DescuentosCL.bat (launcher)")
    print("  • instalar.bat (instalador)")
    
    if check_inno_setup():
        print("  • installer/DescuentosCL_Setup.exe (instalador MSI)")
    
    print("\n🚀 Para distribuir:")
    print("  1. Opción simple: dist/DescuentosCL.exe")
    print("  2. Opción completa: Comprime dist/DescuentosCL/")
    print("  3. Opción instalador: installer/DescuentosCL_Setup.exe")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 