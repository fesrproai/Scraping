@echo off
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
