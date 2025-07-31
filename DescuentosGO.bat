@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 🚀 SISTEMA DE SCRAPING DE DESCUENTOS
echo ========================================
echo.

REM Cambiar al directorio del proyecto
cd /d "C:\Users\fesr_\AndroidStudioProjects\scraping"

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

REM Verificar importaciones principales
echo 🔍 Verificando dependencias...
python -c "import requests, bs4, matplotlib, pandas, numpy, colorama, tqdm; print('✅ Todas las dependencias están funcionando correctamente')" 2>nul
if errorlevel 1 (
    echo ⚠️ ADVERTENCIA: Algunas dependencias no se importaron correctamente
    echo 🔧 Esto no impedirá el funcionamiento básico del sistema
    echo.
)

REM Crear directorios necesarios
echo 📁 Creando directorios...
if not exist "data" mkdir data
if not exist "data\json" mkdir data\json
if not exist "data\csv" mkdir data\csv
if not exist "logs" mkdir logs
echo ✅ Directorios creados correctamente
echo.

REM Mostrar menú principal
echo ========================================
echo 🎯 MENÚ PRINCIPAL - DESCUENTOSGO
echo ========================================
echo.
echo 1. 🚀 Ejecutar scraping completo
echo 2. 🧪 Probar sistema de notificaciones Telegram
echo 3. 📊 Ver estadísticas y datos
echo 4. 🔧 Configurar Telegram
echo 5. 📋 Ver logs del sistema
echo 6. ❌ Salir
echo.
set /p choice="Selecciona una opción (1-6): "

if "%choice%"=="1" goto scraping
if "%choice%"=="2" goto test_telegram
if "%choice%"=="3" goto stats
if "%choice%"=="4" goto config_telegram
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto exit
goto invalid

:scraping
echo.
echo 🚀 Iniciando scraping completo...
python scraping_avanzado.py
echo.
echo ✅ Scraping completado
pause
goto menu

:test_telegram
echo.
echo 🧪 Probando sistema de notificaciones Telegram...
python test_telegram.py
echo.
pause
goto menu

:stats
echo.
echo 📊 Mostrando estadísticas...
if exist "data\products.db" (
    python -c "import sqlite3; conn = sqlite3.connect('data/products.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM productos'); count = cursor.fetchone()[0]; print(f'📦 Total de productos en base de datos: {count}'); conn.close()"
) else (
    echo ⚠️ No hay base de datos de productos
)
echo.
echo 📂 Archivos en carpeta data:
dir /b data\*.json 2>nul
dir /b data\*.csv 2>nul
echo.
pause
goto menu

:config_telegram
echo.
echo 🔧 Configuración de Telegram
echo ============================
echo.
echo 📱 Para configurar Telegram:
echo 1. Busca @BotFather en Telegram
echo 2. Crea un bot con /newbot
echo 3. Busca @userinfobot para obtener tu Chat ID
echo 4. Edita el archivo .env con tus credenciales
echo.
echo 💡 Comando para obtener Chat ID:
echo python get_chat_id.py
echo.
pause
goto menu

:logs
echo.
echo 📋 Logs del sistema
echo ===================
echo.
if exist "logs\*.log" (
    echo 📄 Archivos de log disponibles:
    dir /b logs\*.log
    echo.
    set /p logfile="Ingresa el nombre del archivo de log (o presiona Enter para el más reciente): "
    if "!logfile!"=="" (
        for /f "delims=" %%i in ('dir /b /o-d logs\*.log 2^>nul') do set logfile=%%i & goto show_log
    )
    :show_log
    if exist "logs\!logfile!" (
        echo.
        echo 📄 Contenido de logs\!logfile!:
        echo ================================
        type "logs\!logfile!"
    ) else (
        echo ❌ Archivo de log no encontrado
    )
) else (
    echo ⚠️ No hay archivos de log disponibles
)
echo.
pause
goto menu

:invalid
echo.
echo ❌ Opción inválida. Por favor selecciona 1-6.
echo.
pause
goto menu

:menu
cls
echo ========================================
echo 🚀 SISTEMA DE SCRAPING DE DESCUENTOS
echo ========================================
echo.
echo 1. 🚀 Ejecutar scraping completo
echo 2. 🧪 Probar sistema de notificaciones Telegram
echo 3. 📊 Ver estadísticas y datos
echo 4. 🔧 Configurar Telegram
echo 5. 📋 Ver logs del sistema
echo 6. ❌ Salir
echo.
set /p choice="Selecciona una opción (1-6): "

if "%choice%"=="1" goto scraping
if "%choice%"=="2" goto test_telegram
if "%choice%"=="3" goto stats
if "%choice%"=="4" goto config_telegram
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto exit
goto invalid

:exit
echo.
echo 👋 ¡Gracias por usar DescuentosGO!
echo 💡 Los datos se guardan en la carpeta 'data'
echo 📋 Los logs se guardan en la carpeta 'logs'
echo.
echo 💡 Presiona cualquier tecla para salir...
pause >nul
exit /b 0 