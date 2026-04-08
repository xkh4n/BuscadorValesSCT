# Buscador de Comprobantes SCT

## Descripción

Herramienta de escritorio para buscar y extraer comprobantes de venta desde archivos de log del sistema SCT. Permite localizar transacciones específicas utilizando filtros de fecha, tarjeta y monto, con soporte para búsqueda múltiple y navegación entre resultados.

**Versión actual:** 1.3.3  
**Plataforma:** Windows 10/11 (64 bits)  
**Licencia:** MIT

---

## 📦 Instalación Rápida

### Para Usuarios Finales

1. Descargue el instalador: `BuscadorComprobantes_v1.3.3.exe`
2. Ejecute el archivo descargado
3. Siga el asistente de instalación
4. Abra la aplicación desde el menú Inicio

### Para Desarrolladores

```bash
# Clonar o copiar el proyecto
cd C:\SCTCliente

# Instalar dependencias
pip install tkcalendar pyinstaller pywin32

# Ejecutar directamente desde Python
python nuevoBuscador.py

# Compilar ejecutable
python -m PyInstaller --onedir --windowed --add-data "imperial.ico;." --name=BuscadorComprobantes nuevoBuscador.py

# Compilar instalador
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

---

## 📚 Documentación

### Para Usuarios

| Documento | Descripción |
|-----------|-------------|
| [Manual de Usuario](docs/Manual_de_Usuario_v1.3.3.md) | Guía completa de uso, funcionalidades y preguntas frecuentes |
| [Release Notes](docs/Release_Notes_v1.3.3.md) | Novedades, correcciones y cambios de la versión actual |

### Para Personal Técnico

| Documento | Descripción |
|-----------|-------------|
| [Documentación Técnica](docs/Documentacion_Tecnica_v1.3.3.md) | Arquitectura, lógica de búsqueda, compilación y troubleshooting |

---

## ✨ Características Principales

### 🔍 Búsqueda de Comprobantes
- Búsqueda por **fecha**, **últimos 4 dígitos de tarjeta** y **monto**
- Visualización completa del comprobante encontrado
- Extracción automática de **hora** y **número de operación**

### 📊 Búsqueda Múltiple
- Encuentra **todas las transacciones** con los mismos datos
- Botón **"SIGUIENTE"** para continuar buscando en el archivo
- Indicadores visuales de progreso y disponibilidad

### 🔄 Navegación entre Resultados
- Botones **ANTERIOR/SIGUIENTE** para revisar vales encontrados
- Label informativo **"Vale X de Y"**
- Frame de navegación aparece automáticamente con 2+ vales

### 💾 Exportación
- Guardar comprobante individual o todos los encontrados
- Archivo de texto con metadatos completos
- Nombre automático descriptivo

### 🎨 Interfaz Amigable
- Diseño limpio y profesional
- Colores corporativos personalizados
- Calendario visual para selección de fechas
- Compatible con UI personalizada del usuario

---

## 🖼️ Captura de Pantalla

```
┌─────────────────────────────────────────────────────────┐
│     Buscador de Comprobantes de Venta v1.3.3           │
├─────────────────────────────────────────────────────────┤
│  Datos de búsqueda          │  Resultado de la búsqueda │
│                             │                          │
│  📅 Fecha: [06/04/2026  ▼]  │  📋 COMPROBANTE #1        │
│  💳 Tarjeta: [6018]         │  Hora: 10:31:24           │
│  💰 Monto: [18990]          │  Nº Op: 001010007         │
│  📁 Archivo Log: [____]     │  Tarjeta: ***6018         │
│                   [Examinar]│  Monto: $18.990           │
│                             │  ────────────────────     │
│  ┌──────────────────────┐   │  COMPROBANTE DE VENTA...  │
│  │  [BUSCAR] [SIGUIENTE]│   │                          │
│  │  [GUARDAR] [LIMPIAR] │   │                          │
│  └──────────────────────┘   │                          │
│                             │                          │
│  ┌────────────────────────┐ │                          │
│  │[◀️ANTERIOR][2 de 5][SIG▶️]│ │                          │
│  └────────────────────────┘ │                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Requisitos del Sistema

### Mínimos
- **Sistema Operativo:** Windows 10 (64 bits)
- **Procesador:** 1 GHz
- **RAM:** 2 GB
- **Espacio en disco:** 50 MB
- **Variable de entorno:** `SCT_HOME` configurada

### Recomendados
- **Sistema Operativo:** Windows 11 (64 bits)
- **RAM:** 4 GB o más
- **Espacio en disco:** 100 MB libres

---

## 📋 Guía de Inicio Rápido

### Paso 1: Abrir la Aplicación
- Busque "Buscador de Comprobantes" en el menú Inicio
- O haga doble clic en el acceso directo del escritorio

### Paso 2: Configurar la Búsqueda
1. **Fecha:** Seleccione la fecha de la transacción usando el calendario
2. **Tarjeta:** Ingrese los últimos 4 dígitos (ejemplo: `6018`)
3. **Monto:** Ingrese el monto (ejemplo: `18990` o `18.990`)
4. **Archivo Log:** Verifique que la ruta sea correcta (o use "Examinar")

### Paso 3: Buscar
- Haga clic en **"BUSCAR"**
- Espere a que se complete la búsqueda
- El comprobante aparecerá en el panel derecho

### Paso 4: Navegar (si hay múltiples resultados)
- Use los botones **"ANTERIOR"** y **"SIGUIENTE ▶️"** para revisar todos los vales
- El label central muestra "Vale X de Y"

### Paso 5: Buscar Más (si es necesario)
- Si aparece el mensaje "hay más disponibles"
- Haga clic en **"SIGUIENTE"** (sin flechas) para continuar la búsqueda

### Paso 6: Guardar
- Haga clic en **"GUARDAR"**
- Seleccione la ubicación
- Confirme el nombre del archivo
- ¡Listo!

---

## 🐛 Solución de Problemas Comunes

### Problema: No encuentra el comprobante

**Solución:**
- ✅ Verifique que la fecha es correcta
- ✅ Confirme los últimos 4 dígitos de la tarjeta
- ✅ Asegúrese de que el monto es exacto
- ✅ Verifique que el archivo de log existe

### Problema: El archivo de log no se carga

**Solución:**
- ✅ Verifique que `SCT_HOME` está configurada
- ✅ Use el botón "Examinar" para seleccionar manualmente
- ✅ Confirme que tiene permisos de lectura

### Problema: Se muestra el ícono por defecto

**Solución:**
- ✅ Reinstale la versión 1.3.3 o superior
- ✅ Verifique que `imperial.ico` existe en la carpeta de instalación

---

## 📞 Soporte

### Contacto
- **Desarrollador:** Osvaldo Rojas G.
- **Repositorio:** https://github.com/osvaldorojasg

### Al Reportar un Error
Incluya:
1. Versión de la aplicación (visible en el título)
2. Sistema operativo (Windows 10/11)
3. Descripción detallada del problema
4. Pasos para reproducir
5. Capturas de pantalla si aplica

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulte el archivo LICENSE para más detalles.

---

## 🙏 Agradecimientos

- Python Software Foundation
- Tkinter/Ttk developers
- PyInstaller team
- Inno Setup team
- tkcalendar contributors

---

**Última actualización:** 6 de abril de 2026  
**Versión del documento:** 1.3.3
