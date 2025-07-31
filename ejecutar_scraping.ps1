# Script de PowerShell para ejecutar el Sistema de Scraping de Descuentos

Write-Host "SISTEMA DE SCRAPING DE DESCUENTOS" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "Version optimizada para PowerShell" -ForegroundColor Cyan
Write-Host "Guarda datos localmente sin Firebase" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Verificar si Python esta instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python no esta instalado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "OPCIONES DISPONIBLES:" -ForegroundColor Cyan
Write-Host "1. Ejecutar demostracion" -ForegroundColor White
Write-Host "2. Ejecutar scraping completo" -ForegroundColor White
Write-Host "3. Ejecutar scraping avanzado" -ForegroundColor White
Write-Host "4. Ejecutar sistema completo (CLI)" -ForegroundColor White
Write-Host "5. Ver archivos generados" -ForegroundColor White
Write-Host "6. Salir" -ForegroundColor White
Write-Host ""

$opcion = Read-Host "Selecciona una opcion (1-6)"

if ($opcion -eq "1") {
    Write-Host ""
    Write-Host "Ejecutando demostracion..." -ForegroundColor Green
    python demo_scraping.py
}
elseif ($opcion -eq "2") {
    Write-Host ""
    Write-Host "Ejecutando scraping completo..." -ForegroundColor Green
    python scraping_final.py
}
elseif ($opcion -eq "3") {
    Write-Host ""
    Write-Host "Ejecutando scraping avanzado..." -ForegroundColor Green
    python scraping_avanzado.py
}
elseif ($opcion -eq "4") {
    Write-Host ""
    Write-Host "Ejecutando sistema completo (CLI)..." -ForegroundColor Green
    python main_cli.py
}
elseif ($opcion -eq "5") {
    Write-Host ""
    Write-Host "Archivos en la carpeta 'data':" -ForegroundColor Cyan
    if (Test-Path "data") {
        Get-ChildItem "data" -Filter "*.json" | ForEach-Object {
            $size = [math]::Round($_.Length / 1KB, 2)
            Write-Host "   $($_.Name) ($size KB)" -ForegroundColor White
        }
    } else {
        Write-Host "   No hay archivos generados aun" -ForegroundColor Yellow
    }
}
elseif ($opcion -eq "6") {
    Write-Host ""
    Write-Host "Hasta luego!" -ForegroundColor Green
}
else {
    Write-Host "Opcion invalida" -ForegroundColor Red
}

Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 