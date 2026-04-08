# Buscador de Comprobantes SCT
## Documentación Técnica

**Versión:** 1.3.3  
**Fecha:** Abril 2026  
**Autor:** Osvaldo Rojas G.  
**Licencia:** MIT

---

## 📋 Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Requisitos Técnicos](#requisitos-técnicos)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Tecnologías Utilizadas](#tecnologías-utilizadas)
5. [Funcionalidades Técnicas](#funcionalidades-técnicas)
6. [Lógica de Búsqueda](#lógica-de-búsqueda)
7. [Formato del Archivo de Log](#formato-del-archivo-de-log)
8. [Compilación y Distribución](#compilación-y-distribución)
9. [Variables de Entorno](#variables-de-entorno)
10. [Solución de Problemas](#solución-de-problemas)

---

## Arquitectura del Sistema

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    INTERFAZ GRÁFICA                      │
│                    (Tkinter/ttk)                         │
├─────────────────────────────────────────────────────────┤
│  BuscadorComprobantes (Clase Principal)                 │
│  ├── crear_widgets()         # Construcción de UI       │
│  ├── buscar_comprobante_thread()  # Hilo de búsqueda    │
│  ├── buscar_comprobante_en_log()  # Parser del log      │
│  ├── mostrar_resultados()    # Visualización            │
│  └── guardar_comprobante()   # Exportación              │
├─────────────────────────────────────────────────────────┤
│              LÓGICA DE PROCESAMIENTO                     │
│  ├── Regex para extracción de datos                    │
│  ├── Búsqueda incremental por línea                    │
│  ├── Almacenamiento en array de objetos                │
│  └── Verificación de múltiples coincidencias           │
├─────────────────────────────────────────────────────────┤
│                   ARCHIVO DE LOG                         │
│              (Lectura con encoding utf-8)               │
└─────────────────────────────────────────────────────────┘
```

### Flujo de Datos

```
Usuario → Campos de entrada → Validación → Búsqueda (hilo)
                                                    ↓
                                           Lectura del log
                                                    ↓
                                          Parsing con Regex
                                                    ↓
                                           Extracción de datos
                                                    ↓
                                           Almacenamiento en array
                                                    ↓
                                           Visualización en UI
```

---

## Requisitos Técnicos

### Sistema Operativo
- Windows 10/11 (64 bits)
- .NET Framework 4.7.2+ (requerido por Inno Setup)

### Python (Desarrollo)
- **Versión:** Python 3.13.x
- **Arquitectura:** 64 bits (x64)

### Dependencias Python

```txt
tkinter          # Interfaz gráfica (incluida en Python)
tkcalendar       # Widget de calendario (pip install tkcalendar)
PyInstaller      # Empaquetado a ejecutable (pip install pyinstaller)
```

### Herramientas de Compilación
- **PyInstaller 6.16.0:** Empaquetado del ejecutable Python
- **Inno Setup 6.7.1:** Creación del instalador Windows

---

## Estructura del Proyecto

```
C:\SCTCliente\
├── nuevoBuscador.py              # Código fuente principal
├── imperial.ico                  # Ícono de la aplicación
├── installer.iss                 # Script de Inno Setup
├── installer_output/             # Instaladores compilados
│   └── BuscadorComprobantes_v1.3.3.exe
├── dist/                         # Build de PyInstaller (temporal)
│   └── BuscadorComprobantes/
│       ├── BuscadorComprobantes.exe
│       └── _internal/
│           ├── python313.dll
│           ├── imperial.ico
│           └── ... (dependencias)
├── build/                        # Archivos de compilación (temporal)
├── __pycache__/                  # Bytecode de Python (temporal)
└── docs/                         # Documentación
    ├── Manual_de_Usuario_v1.3.3.md
    ├── Documentacion_Tecnica_v1.3.3.md
    └── ...
```

### Archivos Importantes

| Archivo | Descripción |
|---------|-------------|
| `nuevoBuscador.py` | Script principal con toda la lógica |
| `installer.iss` | Configuración del instalador Inno Setup |
| `imperial.ico` | Ícono personalizado de la aplicación |

---

## Tecnologías Utilizadas

### Python 3.13
- Lenguaje principal de desarrollo
- Ventajas: Multiplataforma, sintaxis limpia, amplio ecosistema

### Tkinter + ttk
- Framework GUI nativo de Python
- Tema 'clam' personalizado
- Widgets utilizados: Frame, Label, Entry, Button, Text, Scrollbar

### tkcalendar
- Librería de terceros para el widget DateEntry
- Permite selección visual de fechas
- Fix aplicado para navegación entre meses/años

### Expresiones Regulares (re)
- Extracción de fecha, hora, monto, tarjeta y número de operación
- Patrones utilizados:
  ```python
  r'\d{4}-\d{2}-\d{2}'                    # Fecha
  r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'  # Fecha + hora
  r'\*+(\d+)'                              # Últimos dígitos de tarjeta
  r'\$\s*([\d\.]+)'                        # Monto
  r'Op\.?\s*(\d+)'                         # Número de operación
  ```

### Threading
- Búsqueda ejecutada en hilo separado para no bloquear la UI
- Actualización de UI mediante `root.after(0, ...)`

---

## Funcionalidades Técnicas

### 1. Búsqueda Incremental

La búsqueda utiliza un **contador de líneas** (`self.linea_actual`) para rastrear la posición en el archivo:

```python
# Leer todas las líneas una vez
with open(archivo_log, 'r', encoding='utf-8', errors='ignore') as archivo:
    todas_las_lineas = archivo.readlines()

# Iterar desde la línea actual
for idx_linea in range(self.linea_actual, len(todas_las_lineas)):
    linea = todas_las_lineas[idx_linea]
    # ... procesar ...
    
    # Cuando se encuentra un vale, guardar el índice
    self.linea_actual = idx_linea + 1
```

**Ventaja sobre `tell()/seek()`:**
- Evita el error "telling position disabled by next() call"
- Más compatible con Windows
- Funciona con archivos de texto en cualquier encoding

### 2. Almacenamiento de Vales

Cada vale encontrado se almacena como un objeto diccionario:

```python
vale = {
    "lineas": [...],                # Líneas del comprobante
    "hora": "10:31:24",            # Hora de transacción
    "numero_operacion": "001010007", # Nº de operación
    "fecha": "2026-04-06",         # Fecha
    "tarjeta": "6018",             # Últimos 4 dígitos
    "monto": "18.990"              # Monto formateado
}
```

Array de almacenamiento:
```python
self.vales_encontrados = []  # Lista de objetos vale
self.vale_actual_index = -1  # Índice del vale que se muestra
```

### 3. Verificación de Más Vales

Función que verifica si existen más coincidencias sin cerrar el archivo:

```python
def verificar_si_hay_mas_vales(self, lineas_restantes, fecha_buscar, tarjeta_buscar, monto_buscar):
    """Verifica si hay más vales en las líneas restantes"""
    # Escanea las líneas restantes buscando un comprobante completo
    # Retorna True si encuentra al menos uno más
```

### 4. Manejo de Recursos con PyInstaller

Función para obtener rutas de recursos compatibles con PyInstaller:

```python
def get_resource_path(relative_path):
    """Obtiene la ruta absoluta a un recurso"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller: recursos en carpeta temporal
        return os.path.join(sys._MEIPASS, relative_path)
    # Python normal: ruta relativa al script
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
```

### 5. Verificaciones de Seguridad (hasattr)

Para compatibilidad con UI personalizada:

```python
# Solo accede a widgets si existen
if hasattr(self, 'status_label'):
    self.status_label.config(text="...")

if hasattr(self, 'progress_bar'):
    self.progress_bar.start(10)
```

---

## Lógica de Búsqueda

### Algoritmo de Parsing

```
1. Abrir archivo de log
2. Leer todas las líneas
3. Iterar desde linea_actual hasta el final:
   
   a. Extraer contenido después de " - Line "
   b. Verificar si la línea contiene fecha (AAAA-MM-DD)
   c. Si la fecha no coincide, continuar
   
   d. Si encuentra "COMPROBANTE DE VENTA":
      - Iniciar nuevo comprobante
      - Reiniciar flags
   
   e. Dentro del comprobante:
      - Buscar número de operación (regex)
      - Buscar tarjeta (regex)
      - Buscar monto en línea "TOTAL" (regex)
      - Si tarjeta Y monto coinciden → vale encontrado
      - Si no coinciden → reiniciar comprobante
   
   f. Si encuentra "ACEPTO PAGAR SEGUN CONTRATO CON EMISOR":
      - Guardar posición actual (linea_actual)
      - Si vale completo → retornar éxito
      - Verificar si hay más vales
      - Retornar resultado

4. Si llega al final sin encontrar → retornar "no encontrado"
```

### Estados de Resultado

```python
# Éxito
{
    "exito": True,
    "lineas": [...],
    "hora": "10:31:24",
    "numero_operacion": "001010007",
    "archivo_leido_completo": False,
    "total_encontrados": 3,
    "indice_actual": 0,
    "hay_mas": True
}

# Archivo leído completo (sin más vales)
{
    "archivo_leido_completo": True,
    "mensaje": "Se han revisado todos los vales en el archivo",
    "total_encontrados": 3
}

# Error
{
    "error": "Archivo no encontrado: C:\\ruta\\archivo.log"
}

# No encontrado
{
    "exito": False,
    "mensaje": "No se encontró el comprobante"
}
```

---

## Formato del Archivo de Log

### Estructura Esperada

El archivo de log contiene líneas con el siguiente formato:

```
2026-04-06 10:31:24 - Line COMPROBANTE DE VENTA CON FIN
2026-04-06 10:31:24 - Line TARJETA DE CREDITO
2026-04-06 10:31:24 - Line IMPERIAL S.A.
2026-04-06 10:31:24 - Line NUMERO DE TARJETA
2026-04-06 10:31:24 - Line ************6018
2026-04-06 10:31:24 - Line MONTO           $       18.990
2026-04-06 10:31:24 - Line TOTAL           $       18.990
2026-04-06 10:31:24 - Line NUMERO DE OPERACION       001010007
2026-04-06 10:31:24 - Line ACEPTO PAGAR SEGUN CONTRATO CON EMISOR
```

### Campos Extraídos

| Campo | Patrón de Búsqueda | Ejemplo |
|-------|-------------------|---------|
| Fecha | `^\d{4}-\d{2}-\d{2}` | `2026-04-06` |
| Hora | `\d{2}:\d{2}:\d{2}` | `10:31:24` |
| Tarjeta | `\*+(\d+)` | `6018` (últimos 4 dígitos) |
| Monto | `TOTAL.*\$\s*([\d\.]+)` | `18.990` |
| Nº Operación | `Op\.?\s*(\d+)` | `001010007` |

### Marcadores de Comprobante

| Marcador | Significado |
|----------|-------------|
| `COMPROBANTE DE VENTA` | Inicio del comprobante |
| `ACEPTO PAGAR SEGUN CONTRATO CON EMISOR` | Fin del comprobante |
| `TOTAL` | Línea con el monto total |

---

## Compilación y Distribución

### Proceso de Build

#### Paso 1: Limpiar builds anteriores

```cmd
cd C:\SCTCliente
rmdir /s /q build dist __pycache__
del /q BuscadorComprobantes.spec
```

#### Paso 2: Compilar ejecutable con PyInstaller

```cmd
python -m PyInstaller --onedir --windowed --add-data "imperial.ico;." --name=BuscadorComprobantes nuevoBuscador.py
```

**Flags explicados:**
- `--onedir`: Crea carpeta con ejecutable y dependencias
- `--windowed`: Sin consola (aplicación GUI)
- `--add-data "imperial.ico;."`: Incluye el ícono en el paquete
- `--name=BuscadorComprobantes`: Nombre del ejecutable

**Resultado:**
```
dist/
└── BuscadorComprobantes/
    ├── BuscadorComprobantes.exe
    └── _internal/
        ├── python313.dll
        ├── imperial.ico
        ├── tk86t.dll
        └── ... (todas las dependencias)
```

#### Paso 3: Compilar instalador con Inno Setup

```cmd
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

**Resultado:**
```
installer_output/
└── BuscadorComprobantes_v1.3.3.exe
```

### Comando Completo (Automatizado)

```cmd
cd C:\SCTCliente && rmdir /s /q build dist __pycache__ 2>nul && del /q BuscadorComprobantes.spec 2>nul && python -m PyInstaller --onedir --windowed --add-data "imperial.ico;." --name=BuscadorComprobantes nuevoBuscador.py && "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

### Configuración de Inno Setup

Archivo `installer.iss`:

```ini
[Setup]
AppId={{A3F8B2C1-4D5E-6F7A-8B9C-0D1E2F3A4B5C}
AppName=Buscador de Comprobantes
AppVersion=1.3.3
DefaultDirName={autopf}\Buscador de Comprobantes
OutputDir=installer_output
OutputBaseFilename=BuscadorComprobantes_v{#MyAppVersion}
Compression=lzma2/ultra64

[Files]
Source: "dist\BuscadorComprobantes\BuscadorComprobantes.exe"; DestDir: "{app}"
Source: "dist\BuscadorComprobantes\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs

[Code]
// Verificación de variable de entorno SCT_HOME
function InitializeSetup(): Boolean;
begin
  // Código de verificación...
end;
```

---

## Variables de Entorno

### SCT_HOME

**Propósito:** Indica la ubicación base de los archivos del sistema SCT.

**Valor por defecto:** `C:\SCTCliente`

**Uso en la aplicación:**
```python
SCT_HOME = os.environ.get('SCT_HOME', r'C:\SCTCliente')
RUTA_LOG_DEFAULT = os.path.join(SCT_HOME, 'SCTCliente.log')
```

**Verificación en el instalador:**
El instalador verifica que `SCT_HOME` esté configurada y muestra una advertencia si no lo está.

### Configurar SCT_HOME

**Método 1: Interfaz gráfica**
1. Presione `Win + R`
2. Escriba `sysdm.cpl`
3. Pestaña "Opciones avanzadas" → "Variables de entorno"
4. En "Variables del usuario" o "Variables del sistema", haga clic en "Nueva"
5. Nombre: `SCT_HOME`
6. Valor: `C:\SCTCliente` (o la ruta correspondiente)

**Método 2: Línea de comandos (temporal)**
```cmd
set SCT_HOME=C:\SCTCliente
```

**Método 3: Línea de comandos (permanente)**
```cmd
setx SCT_HOME "C:\SCTCliente"
```

---

## Solución de Problemas

### Error: "telling position disabled by next() call"

**Causa:** Uso de `archivo.tell()` en archivos de texto en Windows.

**Solución:** Implementado contador de líneas (`linea_actual`) en lugar de posiciones de archivo.

### Error: Ícono no se muestra

**Causa:** PyInstaller no incluye el archivo `.ico` correctamente.

**Solución:**
1. Usar flag `--add-data "imperial.ico;."` en PyInstaller
2. Implementar función `get_resource_path()` con fallback a `sys._MEIPASS`
3. Verificar que `imperial.ico` existe en la carpeta del proyecto

### Error: AttributeError 'status_label'

**Causa:** Se eliminaron widgets de la UI pero el código los referencia.

**Solución:** Implementadas verificaciones `hasattr()` antes de acceder a widgets opcionales.

### Error: DateEntry se cierra al navegar

**Causa:** Conflictos con `grab_set()` del widget Toplevel de tkcalendar.

**Solución:** Patch aplicado en `_patch_calendar_grab()` para modificar el comportamiento del grab.

### La aplicación no encuentra comprobantes

**Verificaciones:**
1. ✅ Archivo de log existe en la ruta especificada
2. ✅ Variable `SCT_HOME` configurada correctamente
3. ✅ Fecha, tarjeta y monto coinciden exactamente con el log
4. ✅ Formato del log sigue la estructura esperada

### Error de encoding al leer el log

**Solución:** El archivo se abre con:
```python
open(archivo_log, 'r', encoding='utf-8', errors='ignore')
```
- `encoding='utf-8'`: Intenta leer como UTF-8
- `errors='ignore'`: Ignora caracteres que no puede decodificar

---

## Historial de Versiones

### v1.3.3 (Abril 2026)
- ✅ Versión incluida en el título de la ventana
- ✅ Fix del ícono con múltiples rutas de fallback
- ✅ Mejoras en la carga de recursos con PyInstaller

### v1.3.2 (Abril 2026)
- ✅ Función `get_resource_path()` para compatibilidad con PyInstaller
- ✅ Múltiples fallbacks para carga del ícono

### v1.3.1 (Abril 2026)
- ✅ Frame de navegación con botones ANTERIOR/SIGUIENTE
- ✅ Navegación entre vales ya encontrados
- ✅ Label informativo "Vale X de Y"
- ✅ Fix de verificaciones `hasattr()` para widgets opcionales

### v1.3.0 (Abril 2026)
- ✅ Búsqueda múltiple de comprobantes
- ✅ Botón "SIGUIENTE" para búsqueda incremental
- ✅ Extracción de hora y número de operación
- ✅ Almacenamiento de múltiples vales en array
- ✅ Guardado de todos los vales encontrados

### v1.2.0 (Abril 2026)
- ✅ Fix del error "telling position disabled by next() call"
- ✅ Cambio de posición de archivo a contador de líneas

### v1.1.0 (Abril 2026)
- ✅ Fix del DateEntry (cierre al navegar entre meses/años)
- ✅ Patch del grab behavior en tkcalendar

### v1.0.0 (Abril 2026)
- ✅ Versión inicial
- ✅ Búsqueda básica de comprobantes
- ✅ Interfaz gráfica con Tkinter
- ✅ Exportación a archivo de texto

---

**Documento creado:** Abril 2026  
**Última actualización:** Abril 2026
