# Notas de la Versión 1.4.0
## Buscador de Comprobantes SCT

**Fecha de lanzamiento:** 8 de abril de 2026
**Versión:** 1.4.0
**Tipo:** Actualización menor (nueva funcionalidad)

---

## Resumen

Esta versión incluye la nueva funcionalidad de **impresión directa de comprobantes**, un **sistema de versionado automático** y un **script de compilación optimizado** con generación de logs.

---

## Novedades

### ✨ Nueva Funcionalidad: Impresión de Comprobantes

1. **Botón IMPRIMIR con ícono**
   - Nuevo botón "🖨️ IMPRIMIR" en la barra de acciones
   - Ícono de impresora para identificación visual rápida
   - Se habilita automáticamente al encontrar un comprobante

2. **Impresión directa en impresora de recibos**
   - Imprime solo el texto del vale (sin metadatos adicionales)
   - Compatible con impresoras de recibos de 104mm
   - Usa la impresora predeterminada del sistema
   - Confirmación antes de imprimir

3. **Contenido de impresión optimizado**
   - Solo se imprime el contenido del comprobante tal como aparece en el archivo log
   - Desde "COMPROBANTE DE VENTA" hasta "ACEPTO PAGAR SEGUN CONTRATO CON EMISOR"
   - Sin encabezados ni pies de página adicionales

### 🔧 Mejoras en el Proceso de Build

1. **Script de compilación mejorado (`compiler.ps1`)**
   - Versionado automático con incremento MAJOR/MINOR/PATCH
   - Logs de compilación en `build_logs/`
   - Exclusión de módulos innecesarios para reducir tamaño
   - Validación en cada paso del proceso

2. **Sistema de versionado automático**
   - Actualiza `version.txt`, `installer.iss` y `nuevoBuscador.py` simultáneamente
   - Soporte para versionado semántico (MAJOR.MINOR.PATCH)
   - Prompt interactivo para seleccionar tipo de cambio

3. **Reducción del tamaño del instalador**
   - Exclusión de datos de localización de babel (solo se mantiene español)
   - Exclusión de módulos no utilizados (unittest, pdb, etc.)

---

## Correcciones

### 🐛 Bugs Corregidos

| ID | Descripción | Impacto |
|----|-------------|---------|
| #003 | Ruta incorrecta del ícono en accesos directos del instalador | Visual |
| #004 | Inconsistencia entre OutputDir en compiler.ps1 e installer.iss | Build |
| #005 | Archivo temporal de impresión eliminado antes de procesarse | Funcional |

---

## Cambios Técnicos

### Nuevos Imports

**Archivo:** `nuevoBuscador.py`

```python
import win32print
import win32api
```

> **Nota:** Requiere `pip install pywin32` para desarrollo. El instalador final incluye estos módulos automáticamente.

### Nuevo Método de Impresión

```python
def imprimir_comprobante(self):
    """Imprime el comprobante actual en una impresora de recibos"""
    # Obtiene impresora predeterminada
    # Construye contenido solo con líneas del vale
    # Crea archivo temporal y envía a impresión
```

### Script compiler.ps1 (nuevo)

Reemplaza al anterior `compiler.ps1` con:
- Función `Get-CurrentVersion` - Lee versión desde `version.txt`
- Función `Update-VersionFile` - Actualiza todos los archivos de versión
- Función `Write-Log` - Genera logs de compilación
- Prompt interactivo para seleccionar tipo de cambio

---

## Compatibilidad

### Sistemas Operativos Soportados

- ✅ Windows 10 (64 bits)
- ✅ Windows 11 (64 bits)

### Requisitos

- Variable de entorno `SCT_HOME` configurada
- Archivo de log accesible en la ruta configurada
- Impresora de recibos configurada (opcional, para imprimir)

### Dependencias de Desarrollo

```bash
pip install tkcalendar pyinstaller pywin32
```

---

## Instalación

### Nueva Instalación

1. Descargue `BuscadorValesSCT_v1.4.0.exe`
2. Ejecute el instalador
3. Siga el asistente de instalación

### Actualización desde Versiones Anteriores

1. Descargue la versión 1.4.0
2. Ejecute el instalador (sobrescribirá la versión anterior)
3. No se perderán datos ni configuraciones

---

## Funcionalidades de la Versión

### Características Principales

✅ **Búsqueda de Comprobantes**
- Búsqueda por fecha, tarjeta y monto
- Visualización completa del comprobante encontrado

✅ **Búsqueda Múltiple**
- Encuentra todas las transacciones con los mismos datos
- Botón "SIGUIENTE" para continuar la búsqueda

✅ **Navegación entre Resultados**
- Botones ANTERIOR/SIGUIENTE para revisar vales encontrados
- Label informativo "Vale X de Y"

✅ **Extracción de Metadatos**
- Hora de la transacción
- Número de operación

✅ **Exportación de Resultados**
- Guardar comprobante(s) en archivo de texto
- Archivo incluye metadatos de cada vale

✅ **IMPRESIÓN DE COMPROBANTES** (NUEVO)
- Botón dedicado con ícono de impresora
- Impresión directa en impresora de recibos
- Solo imprime el contenido del vale

### Correcciones Incluidas de Versiones Anteriores

✅ Fix del DateEntry (navegación entre meses/años)
✅ Fix del error "telling position disabled by next() call"
✅ Verificaciones `hasattr()` para widgets opcionales
✅ Función `get_resource_path()` para PyInstaller
✅ Ruta correcta del ícono en instalador

---

## Guía de Compilación (Desarrolladores)

### Uso del Script compiler.ps1

```powershell
.\compiler.ps1
```

El script preguntará el tipo de cambio:
- **[1] MAJOR** - Cambio grande de lógica/funcionalidad
- **[2] MINOR** - Nueva funcionalidad menor
- **[3] PATCH** - Fix/corrección
- **[0] Sin cambios** - Mantener versión actual

### Logs de Compilación

Cada build genera un log en `build_logs/build_YYYYMMDD_HHMMSS.log`

### Backups

El script anterior se mantiene como `compiler-bck.ps1` por si se necesita revertir.

---

## Problemas Conocidos

No hay problemas conocidos en esta versión.

---

## Feedback y Soporte

Para reportar errores o solicitar mejoras:

- **Repositorio:** https://github.com/xkh4n/BuscadorValesSCT.git
- **Incluir en el reporte:**
  - Versión de la aplicación (visible en el título)
  - Sistema operativo
  - Pasos para reproducir el problema
  - Capturas de pantalla si aplica

---

## Próximas Versiones

### Roadmap Propuesto

**v1.5.0 (Futuro)**
- [ ] Búsqueda por rango de fechas
- [ ] Filtros avanzados (terminal, empleado, etc.)
- [ ] Exportación a Excel/PDF
- [ ] Historial de búsquedas recientes

**v2.0.0 (Futuro)**
- [ ] Interfaz rediseñada
- [ ] Base de datos local para historial
- [ ] Reportes estadísticos

---

## Créditos

**Desarrollador:** Osvaldo Rojas G.
**Licencia:** MIT
**Tecnologías:** Python 3.13, Tkinter, PyInstaller, Inno Setup, pywin32

---

**Fecha de publicación:** 8 de abril de 2026
