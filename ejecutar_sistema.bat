
@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 🚀 SISTEMA DE SCRAPING DE DESCUENTOS
echo ========================================
echo.

REM Verificar si Python está instalado
echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo 📥 Por favor instala Python desde https://python.org
    echo 💡 Asegúrate de marcar "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python encontrado: !PYTHON_VERSION!
echo.

REM Verificar si pip está disponible
echo 🔍 Verificando pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: pip no está disponible
    echo 📥 Reinstala Python para incluir pip
    pause
    exit /b 1
)

echo ✅ pip disponible
echo.

REM Verificar si requirements.txt existe
if not exist "requirements.txt" (
    echo ❌ ERROR: No se encontró requirements.txt
    echo 📁 Asegúrate de estar en el directorio correcto del proyecto
    pause
    exit /b 1
)

REM Instalar/actualizar dependencias
echo 📦 Instalando dependencias...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo ❌ ERROR: Fallo al instalar dependencias
    echo 🔧 Intenta ejecutar: python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas correctamente
echo.

REM Verificar que las dependencias se importen correctamente
echo 🔍 Verificando importaciones...
python -c "import requests, bs4, lxml, matplotlib; print('✅ Todas las dependencias funcionan correctamente')" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Problema con las dependencias
    echo 🔧 Reinstala las dependencias manualmente
    pause
    exit /b 1
)

echo ✅ Sistema verificado correctamente
echo.

REM Crear directorios necesarios si no existen
if not exist "data" mkdir data
if not exist "data\json" mkdir data\json
if not exist "data\csv" mkdir data\csv
if not exist "logs" mkdir logs

echo ========================================
echo 🚀 Iniciando sistema de scraping...
echo ========================================
echo.

REM Ejecutar el sistema con manejo de errores
python main_cli.py

if errorlevel 1 (
    echo.
    echo ❌ El sistema terminó con errores
    echo 📋 Revisa los logs para más detalles
    echo.
) else (
    echo.
    echo ✅ Sistema ejecutado correctamente
    echo.
)

echo ========================================
echo 📊 Sistema terminado
echo ========================================
echo.
echo 💡 Presiona cualquier tecla para salir...
pause >nul 