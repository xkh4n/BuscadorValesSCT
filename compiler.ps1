# ============================================================
# Compiler.ps1 - Build script con versionado automático
# ============================================================
# Limpia, incrementa la versión, compila el ejecutable con 
# módulos excluidos y genera el instalador con Inno Setup.
# ============================================================

# --- Configuración ---
$AppName = "BuscadorValesSCT"
$SourceScript = "nuevoBuscador.py"
$VersionFile = "version.txt"
$InstallerScript = "installer.iss"
$IconPath = "images/imperial.ico"
$InnoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
$LogDir = ".\build_logs"
$LogTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$LogDir\build_$LogTimestamp.log"

# --- Funciones de Logging ---
function Write-Log {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine = "[$timestamp] $Message"
    Add-Content -Path $LogFile -Value $logLine
    if ($Color -eq "Cyan") {
        Write-Host $Message -ForegroundColor Cyan
    } elseif ($Color -eq "Green") {
        Write-Host $Message -ForegroundColor Green
    } elseif ($Color -eq "Red") {
        Write-Host $Message -ForegroundColor Red
    } elseif ($Color -eq "Yellow") {
        Write-Host $Message -ForegroundColor Yellow
    } else {
        Write-Host $Message
    }
}

function Write-Step {
    param([string]$Message)
    Write-Log "`n==> $Message" "Cyan"
}

function Write-Ok {
    param([string]$Message)
    Write-Log "    OK: $Message" "Green"
}

function Write-Err {
    param([string]$Message)
    Write-Log "    ERROR: $Message" "Red"
}

function Write-Warn {
    param([string]$Message)
    Write-Log "    AVISO: $Message" "Yellow"
}

# --- Función para leer versión desde version.txt ---
function Get-CurrentVersion {
    $content = Get-Content $VersionFile -Raw
    $match = [regex]::Match($content, 'filevers=\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)')
    if ($match.Success) {
        return @{
            Major    = [int]$match.Groups[1].Value
            Minor    = [int]$match.Groups[2].Value
            Patch    = [int]$match.Groups[3].Value
            Revision = [int]$match.Groups[4].Value
            String   = "$($match.Groups[1].Value).$($match.Groups[2].Value).$($match.Groups[3].Value)"
        }
    }
    return $null
}

# --- Función para actualizar version.txt ---
function Update-VersionFile {
    param([int]$Major, [int]$Minor, [int]$Patch)
    
    $newVersion = "$Major.$Minor.$Patch.0"
    $newVersionDisplay = "$Major.$Minor.$Patch"
    
    $content = Get-Content $VersionFile -Raw
    
    # Actualizar filevers y prodvers
    $content = $content -replace 'filevers=\(\d+,\s*\d+,\s*\d+,\s*\d+\)', "filevers=($Major, $Minor, $Patch, 0)"
    $content = $content -replace 'prodvers=\(\d+,\s*\d+,\s*\d+,\s*\d+\)', "prodvers=($Major, $Minor, $Patch, 0)"
    $content = $content -replace "FileVersion',\s*u'[\d.]+'", "FileVersion', u'$newVersion'"
    $content = $content -replace "ProductVersion',\s*u'[\d.]+'", "ProductVersion', u'$newVersion'"
    
    Set-Content -Path $VersionFile -Value $content -NoNewline
    
    # Actualizar installer.iss
    if (Test-Path $InstallerScript) {
        $installerContent = Get-Content $InstallerScript -Raw
        $installerContent = $installerContent -replace '#define MyAppVersion "[\d.]+"', "#define MyAppVersion `"$newVersionDisplay`""
        $installerContent = $installerContent -replace 'OutputBaseFilename=BuscadorValesSCT_v[\d.]+', "OutputBaseFilename=BuscadorValesSCT_v$newVersionDisplay"
        Set-Content -Path $InstallerScript -Value $installerContent -NoNewline
    }
    
    # Actualizar versión en nuevoBuscador.py si existe APP_VERSION
    if (Test-Path $SourceScript) {
        $scriptContent = Get-Content $SourceScript -Raw
        if ($scriptContent -match 'APP_VERSION\s*=\s*"[\d.]+"') {
            $scriptContent = $scriptContent -replace 'APP_VERSION\s*=\s*"[\d.]+"', "APP_VERSION = `"$newVersionDisplay`""
            Set-Content -Path $SourceScript -Value $scriptContent -NoNewline
        }
    }
    
    return $newVersionDisplay
}

# --- Función para generar nombre del instalador ---
function Get-InstallerOutputName {
    param([string]$Version)
    return ".\installer\$($AppName)_v$Version.exe"
}

# ============================================================
# INICIO DEL SCRIPT
# ============================================================

# Crear directorio de logs si no existe
if (-Not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Iniciar log
"============================================================" | Out-File -FilePath $LogFile -Encoding UTF8
"  BUILD LOG: $AppName" | Out-File -FilePath $LogFile -Append -Encoding UTF8
"  Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -FilePath $LogFile -Append -Encoding UTF8
"============================================================" | Out-File -FilePath $LogFile -Append -Encoding UTF8

Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "  Build: $AppName" -ForegroundColor Magenta
Write-Host "  Log: $LogFile" -ForegroundColor DarkGray
Write-Host "============================================================" -ForegroundColor Magenta

# 1. Leer versión actual
Write-Step "Leyendo versión actual..."
$currentVersion = Get-CurrentVersion

if (-Not $currentVersion) {
    Write-Err "No se pudo leer la versión desde $VersionFile"
    exit 1
}

Write-Log "Versión actual: $($currentVersion.String)" "Cyan"

# 2. Preguntar tipo de incremento
Write-Host "`nSeleccione el tipo de cambio:" -ForegroundColor Yellow
Write-Host "  [1] MAJOR (cambio grande de lógica/funcionalidad)  -> $($currentVersion.Major + 1).0.0" -ForegroundColor White
Write-Host "  [2] MINOR (nueva funcionalidad menor)              -> $($currentVersion.Major).$($currentVersion.Minor + 1).0" -ForegroundColor White
Write-Host "  [3] PATCH (fix/corrección)                          -> $($currentVersion.Major).$($currentVersion.Minor).$($currentVersion.Patch + 1)" -ForegroundColor White
Write-Host "  [0] Sin cambios (mantener $($currentVersion.String))" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Ingrese opción (0-3)"

$newVersion = $currentVersion.String
$changeType = "Sin cambios"

switch ($choice) {
    "1" {
        $newVersion = Update-VersionFile -Major ($currentVersion.Major + 1) -Minor 0 -Patch 0
        $changeType = "MAJOR"
    }
    "2" {
        $newVersion = Update-VersionFile -Major $currentVersion.Major -Minor ($currentVersion.Minor + 1) -Patch 0
        $changeType = "MINOR"
    }
    "3" {
        $newVersion = Update-VersionFile -Major $currentVersion.Major -Minor $currentVersion.Minor -Patch ($currentVersion.Patch + 1)
        $changeType = "PATCH"
    }
    "0" {
        Write-Warn "Manteniendo versión $($currentVersion.String)"
    }
    default {
        Write-Err "Opción inválida. Cancelando build."
        exit 1
    }
}

if ($changeType -ne "Sin cambios") {
    Write-Ok "Versión actualizada a: $newVersion (Tipo: $changeType)"
    Write-Log "Cambio de versión: $($currentVersion.String) -> $newVersion ($changeType)" "Green"
}

# 3. Limpiar directorios anteriores
Write-Step "Limpiando archivos anteriores..."
Remove-Item -Path ".\build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".\dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path ".\$($AppName).spec" -Force -ErrorAction SilentlyContinue
Write-Ok "Limpieza completada."


# 5. Construir argumentos de PyInstaller como array
$PyInstallerArgs = @(
    "-m", "PyInstaller",
    "--onedir",
    "--windowed",
    "--name=$AppName",
    "--version-file=$VersionFile",
    "--icon=$IconPath",
    "--add-data=images/imperial.ico;."
)

$PyInstallerArgs += $SourceScript

# 6. Compilar con PyInstaller
Write-Step "Compilando ejecutable (v$newVersion)..."
& python @PyInstallerArgs 2>&1 | Out-File -FilePath $LogFile -Append -Encoding UTF8

# 7. Verificar resultado
if (-Not (Test-Path ".\dist\$AppName\$($AppName).exe")) {
    Write-Err "No se encontró el ejecutable. La compilación falló."
    exit 1
}
Write-Ok "Ejecutable compilado exitosamente."

$ExeSize = (Get-Item ".\dist\$AppName\$($AppName).exe").Length / 1MB
Write-Ok "Tamaño del .exe: $([math]::Round($ExeSize, 2)) MB"

# 8. Compilar instalador con Inno Setup
if (-Not (Test-Path $InnoSetupPath)) {
    Write-Err "Inno Setup no encontrado en: $InnoSetupPath"
    exit 1
}

Write-Step "Compilando instalador con Inno Setup..."
$innoOutput = & $InnoSetupPath .\installer.iss 2>&1
$innoOutput | Out-File -FilePath $LogFile -Append -Encoding UTF8

if ($LASTEXITCODE -ne 0) {
    Write-Err "La compilación del instalador falló."
    exit 1
}

# 9. Resultado final
$OutputInstaller = Get-InstallerOutputName -Version $newVersion

Write-Host "`n============================================================" -ForegroundColor Magenta
Write-Ok "Build completado exitosamente."
Write-Host "Versión: $newVersion" -ForegroundColor Green
Write-Host "Tipo de cambio: $changeType" -ForegroundColor Green
Write-Host "Instalador: $OutputInstaller" -ForegroundColor Green

if (Test-Path $OutputInstaller) {
    $InstallerSize = (Get-Item $OutputInstaller).Length / 1MB
    Write-Ok "Tamaño del instalador: $([math]::Round($InstallerSize, 2)) MB"
}

Write-Host "Log guardado en: $LogFile" -ForegroundColor DarkGray
Write-Host "============================================================`n" -ForegroundColor Magenta

# Guardar resumen en log
"============================================================" | Out-File -FilePath $LogFile -Append -Encoding UTF8
"  BUILD EXITOSO" | Out-File -FilePath $LogFile -Append -Encoding UTF8
"  Versión: $newVersion ($changeType)" | Out-File -FilePath $LogFile -Append -Encoding UTF8
"  Instalador: $OutputInstaller" | Out-File -FilePath $LogFile -Append -Encoding UTF8
"============================================================" | Out-File -FilePath $LogFile -Append -Encoding UTF8
