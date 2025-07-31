@echo off
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
