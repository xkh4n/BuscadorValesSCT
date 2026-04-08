# Limpiar build y dist (NO borramos el .spec)
Write-Host "Limpiando archivos anteriores..." -ForegroundColor Cyan
Remove-Item -Path ".\build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".\dist" -Recurse -Force -ErrorAction SilentlyContinue

# Compilar ejecutable con PyInstaller (genera nuevo spec desde el código fuente)
Write-Host "`nCompilando ejecutable con PyInstaller..." -ForegroundColor Cyan
python -m PyInstaller --onedir --windowed --name=BuscadorValesSCT --version-file=version.txt --icon=images/imperial.ico --add-data "images/imperial.ico;." nuevoBuscador.py

# Verificar que la compilación fue exitosa
if (-Not (Test-Path ".\dist\BuscadorValesSCT\BuscadorValesSCT.exe")) {
    Write-Host "`nERROR: No se encontró el ejecutable. La compilación falló." -ForegroundColor Red
    exit 1
}

Write-Host "`nEjecutable compilado exitosamente." -ForegroundColor Green

# Compilar instalador con Inno Setup
Write-Host "`nCompilando instalador con Inno Setup..." -ForegroundColor Cyan
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" .\installer.iss

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: La compilación del instalador falló." -ForegroundColor Red
    exit 1
}

Write-Host "`nBuild completado exitosamente." -ForegroundColor Green
Write-Host "Instalador generado" -ForegroundColor Green
