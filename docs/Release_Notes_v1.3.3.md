# Notas de la Versión 1.3.3
## Buscador de Comprobantes SCT

**Fecha de lanzamiento:** 6 de abril de 2026  
**Versión:** 1.3.3  
**Tipo:** Actualización menor

---

## Resumen

Esta versión incluye mejoras en la presentación de la aplicación y corrección del ícono en el ejecutable compilado.

---

## Novedades

### ✨ Mejoras

1. **Versión visible en el título de la ventana**
   - El título ahora muestra: "Buscador de Comprobantes de Venta **v1.3.3**"
   - Permite identificar rápidamente la versión instalada
   - Facilita el soporte técnico y reporte de errores

2. **Corrección del ícono de la aplicación**
   - Se arregló el problema donde se mostraba el ícono por defecto de Tkinter
   - Ahora se muestra correctamente el ícono personalizado (imperial.ico)
   - Múltiples rutas de fallback para asegurar compatibilidad con PyInstaller

---

## Correcciones

### 🐛 Bugs Corregidos

| ID | Descripción | Impacto |
|----|-------------|---------|
| #001 | Ícono por defecto de Tkinter en lugar del personalizado | Visual |
| #002 | Versión no visible en la interfaz | Usabilidad |

---

## Cambios Técnicos

### Código Modificado

**Archivo:** `nuevoBuscador.py`

```python
# Antes
self.root.title("Buscador de Comprobantes de Venta")
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'imperial.ico')

# Después
self.APP_VERSION = "1.3.3"
self.root.title(f"Buscador de Comprobantes de Venta v{self.APP_VERSION}")

# Nueva función para obtener rutas de recursos
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
```

### Mejoras en la Carga del Ícono

Se implementaron múltiples rutas de fallback:
1. Ruta desde `sys._MEIPASS` (PyInstaller)
2. Ruta relativa al script (Python normal)
3. Ruta desde el directorio del ejecutable
4. Manejo de excepciones con try-except

---

## Compatibilidad

### Sistemas Operativos Soportados

- ✅ Windows 10 (64 bits)
- ✅ Windows 11 (64 bits)

### Requisitos

- Variable de entorno `SCT_HOME` configurada
- Archivo de log accesible en la ruta configurada

---

## Instalación

### Nueva Instalación

1. Descargue `BuscadorComprobantes_v1.3.3.exe`
2. Ejecute el instalador
3. Siga el asistente de instalación

### Actualización desde Versiones Anteriores

1. Descargue la versión 1.3.3
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
- Verificación automática de más coincidencias

✅ **Navegación entre Resultados**
- Botones ANTERIOR/SIGUIENTE para revisar vales encontrados
- Label informativo "Vale X de Y"
- Frame de navegación aparece automáticamente con 2+ vales

✅ **Extracción de Metadatos**
- Hora de la transacción
- Número de operación
- Permite diferenciar comprobantes idénticos

✅ **Exportación de Resultados**
- Guardar comprobante individual
- Guardar todos los comprobantes encontrados
- Archivo incluye metadatos de cada vale

### Correcciones Incluidas de Versiones Anteriores

✅ Fix del DateEntry (navegación entre meses/años)  
✅ Fix del error "telling position disabled by next() call"  
✅ Verificaciones `hasattr()` para widgets opcionales  
✅ Función `get_resource_path()` para PyInstaller  

---

## Problemas Conocidos

No hay problemas conocidos en esta versión.

---

## Feedback y Soporte

Para reportar errores o solicitar mejoras:

- **Repositorio:** https://github.com/osvaldorojasg
- **Incluir en el reporte:**
  - Versión de la aplicación (visible en el título)
  - Sistema operativo
  - Pasos para reproducir el problema
  - Capturas de pantalla si aplica

---

## Próximas Versiones

### Roadmap Propuesto

**v1.4.0 (Futuro)**
- [ ] Búsqueda por rango de fechas
- [ ] Filtros avanzados (terminal, empleado, etc.)
- [ ] Exportación a Excel/PDF
- [ ] Historial de búsquedas recientes

**v1.5.0 (Futuro)**
- [ ] Comparación automática de comprobantes
- [ ] Detección de duplicados
- [ ] Estadísticas de búsqueda

---

## Créditos

**Desarrollador:** Osvaldo Rojas G.  
**Licencia:** MIT  
**Tecnologías:** Python 3.13, Tkinter, PyInstaller, Inno Setup

---

**Fecha de publicación:** 6 de abril de 2026
