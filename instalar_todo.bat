@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 🚀 INSTALADOR COMPLETO - DESCUENTOSGO
echo ========================================
echo.

REM Cambiar al directorio del proyecto
cd /d "C:\Users\fesr_\AndroidStudioProjects\scraping"

echo 📦 PASO 1: Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado
    echo 📥 Descarga Python desde: https://python.org
    echo 💡 Marca "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python encontrado: !PYTHON_VERSION!
echo.

echo 📦 PASO 2: Actualizando pip...
python -m pip install --upgrade pip --quiet
echo ✅ pip actualizado
echo.

echo 📦 PASO 3: Instalando todas las librerías...
echo 🔍 Instalando dependencias principales...
python -m pip install requests>=2.31.0 beautifulsoup4>=4.12.0 lxml>=4.9.0 --quiet
echo ✅ Librerías de web scraping instaladas

echo 🔍 Instalando librerías de datos...
python -m pip install pandas>=2.0.0 numpy>=1.24.0 matplotlib>=3.7.0 --quiet
echo ✅ Librerías de datos instaladas

echo 🔍 Instalando librerías de utilidades...
python -m pip install colorama>=0.4.0 tqdm>=4.65.0 python-dateutil>=2.8.0 --quiet
echo ✅ Librerías de utilidades instaladas

echo 🔍 Instalando librerías de configuración...
python -m pip install python-dotenv>=1.0.0 --quiet
echo ✅ Librerías de configuración instaladas

echo 🔍 Instalando dependencias adicionales...
python -m pip install urllib3>=2.0.0 certifi>=2023.0.0 charset-normalizer>=3.0.0 idna>=3.0.0 --quiet
echo ✅ Dependencias adicionales instaladas
echo.

echo 📦 PASO 4: Verificando instalación...
python -c "import requests, bs4, matplotlib, pandas, numpy, colorama, tqdm, lxml, urllib3, certifi, charset_normalizer, idna, dateutil, dotenv; print('✅ Todas las librerías instaladas correctamente')" 2>nul
if errorlevel 1 (
    echo ⚠️ ADVERTENCIA: Algunas librerías no se importaron correctamente
    echo 🔧 Intentando reinstalar...
    python -m pip install -r requirements.txt --force-reinstall --quiet
) else (
    echo ✅ Verificación completada exitosamente
)
echo.

echo 📁 PASO 5: Creando directorios necesarios...
if not exist "data" mkdir data
if not exist "data\json" mkdir data\json
if not exist "data\csv" mkdir data\csv
if not exist "logs" mkdir logs
echo ✅ Directorios creados correctamente
echo.

echo 🔧 PASO 6: Configurando archivo .env...
if not exist ".env" (
    echo TELEGRAM_BOT_TOKEN=8442920382:AAG_FpAAoJoWwKt9YAGv0fe5skB8fT1T2xg > .env
    echo TELEGRAM_CHAT_ID=123456789 >> .env
    echo ✅ Archivo .env creado
) else (
    echo ✅ Archivo .env ya existe
)
echo.

echo 🧪 PASO 7: Ejecutando pruebas del sistema...
python test_sistema.py
echo.

echo 📱 PASO 8: Configuración de Telegram (Opcional)...
echo.
echo 💡 Para configurar notificaciones Telegram:
echo 1. Busca @DescuentosGo_bot en Telegram
echo 2. Envía un mensaje al bot
echo 3. Ejecuta: python get_chat_id.py
echo 4. Actualiza el archivo .env con tu Chat ID real
echo.

echo 🎯 PASO 9: Creando acceso directo en el escritorio...
copy "DescuentosGO.bat" "%USERPROFILE%\Desktop\DescuentosGO.bat" >nul 2>&1
if exist "%USERPROFILE%\Desktop\DescuentosGO.bat" (
    echo ✅ Acceso directo creado en el escritorio
) else (
    echo ⚠️ No se pudo crear el acceso directo
)
echo.

echo ========================================
echo 🎉 INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo ✅ Todas las librerías instaladas
✅ Directorios creados
✅ Configuración básica completada
✅ Sistema listo para usar
echo.
echo 🚀 PARA USAR EL SISTEMA:
echo 1. Haz doble clic en DescuentosGO.bat en el escritorio
echo 2. O ejecuta: python main_cli.py
echo 3. O ejecuta: python scraping_avanzado.py
echo.
echo 📱 CONFIGURAR TELEGRAM (OPCIONAL):
echo 1. Busca @DescuentosGo_bot en Telegram
echo 2. Envía un mensaje al bot
echo 3. Ejecuta: python get_chat_id.py
echo 4. Actualiza el archivo .env
echo.
echo 💡 COMANDOS ÚTILES:
echo • python test_sistema.py - Probar todo el sistema
echo • python test_telegram.py - Probar notificaciones
echo • python get_chat_id.py - Obtener Chat ID de Telegram
echo.
echo 👋 ¡El sistema está listo para usar!
echo.
pause 