param()

Write-Host "🔧 Corrigiendo terminaciones de línea para compatibilidad Windows..." -ForegroundColor Cyan

# Lista de archivos que necesitan corrección de terminaciones de línea
$filesToFix = @(
    ".\README.md",
    ".\docs\Documentacion_Tecnica_v1.3.3.md",
    ".\docs\ENTREGA_PRODUCCION.md", 
    ".\docs\INDICE_DOCUMENTACION.md",
    ".\docs\Manual_de_Usuario_v1.3.3.md",
    ".\docs\RESUMEN_RAPIDO.md",
    ".\docs\Release_Notes_v1.3.3.md"
)

$fixedCount = 0
$skippedCount = 0

foreach ($file in $filesToFix) {
    if (Test-Path $file) {
        Write-Host "  🔄 Procesando: $file" -ForegroundColor Yellow
        
        try {
            # Leer contenido y verificar si tiene CRLF
            $content = Get-Content $file -Raw
            
            if ($content -and $content.Contains("`r`n")) {
                # Corregir terminaciones de línea CRLF -> LF
                $fixedContent = $content -replace "`r`n", "`n"
                
                # Crear archivo temporal
                $tempFile = "$file.tmp"
                Set-Content $tempFile -Value $fixedContent -NoNewline
                
                # Reemplazar archivo original
                Move-Item $tempFile $file -Force
                
                Write-Host "    ✅ Corregido: CRLF -> LF" -ForegroundColor Green
                $fixedCount++
            } else {
                Write-Host "    ✅ Ya tiene formato correcto (LF)" -ForegroundColor Green
                $skippedCount++
            }
        } catch {
            Write-Host "    ❌ Error al procesar: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⚠️  Archivo no encontrado: $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📊 Resumen de correcciones:" -ForegroundColor Cyan
Write-Host "  • Archivos corregidos: $fixedCount" -ForegroundColor Green
Write-Host "  • Archivos ya correctos: $skippedCount" -ForegroundColor Yellow
Write-Host "  • Total procesados: $($fixedCount + $skippedCount)" -ForegroundColor White

if ($fixedCount -gt 0) {
    Write-Host ""
    Write-Host "✅ Correcciones aplicadas exitosamente." -ForegroundColor Green
    Write-Host "💡 Ahora puedes levantar el stack de bases de datos con: .\run.ps1 bdd dev" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "✅ No se necesitaron correcciones. El proyecto ya está listo." -ForegroundColor Green
}