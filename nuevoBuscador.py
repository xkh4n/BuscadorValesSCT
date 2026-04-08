import os
import re
from pathlib import Path
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from tkcalendar import DateEntry, Calendar
import sys

# Obtener ruta base para recursos (funciona con PyInstaller)
def get_resource_path(relative_path):
    """Obtiene la ruta absoluta a un recurso, funciona para desarrollo y PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # Ejecutándose desde PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    # Ejecutándose desde Python normal
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# Custom Calendar class with fixed navigation
class FixedCalendar(Calendar):
    """Calendar personalizado que previene el cierre accidental al navegar entre meses/años"""
    
    def _prev_month(self, event=None):
        """Ir al mes anterior sin cerrar el calendario"""
        self._date = self._date.replace(day=1) - timedelta(days=1)
        self._display_calendar()
        return "break"
    
    def _next_month(self, event=None):
        """Ir al mes siguiente sin cerrar el calendario"""
        if self._date.month == 12:
            self._date = self._date.replace(year=self._date.year + 1, month=1, day=1)
        else:
            self._date = self._date.replace(month=self._date.month + 1, day=1)
        self._display_calendar()
        return "break"
    
    def _prev_year(self, event=None):
        """Ir al año anterior sin cerrar el calendario"""
        self._date = self._date.replace(year=self._date.year - 1)
        self._display_calendar()
        return "break"
    
    def _next_year(self, event=None):
        """Ir al año siguiente sin cerrar el calendario"""
        self._date = self._date.replace(year=self._date.year + 1)
        self._display_calendar()
        return "break"

# Obtener ruta del archivo log desde variable de entorno SCT_HOME
SCT_HOME = os.environ.get('SCT_HOME', r'C:\SCTCliente')
RUTA_LOG_DEFAULT = os.path.join(SCT_HOME, 'SCTCliente.log')

class BuscadorComprobantes:
    def __init__(self, root):
        self.root = root
        
        # Versión de la aplicación
        self.APP_VERSION = "1.3.3"
        
        self.root.title(f"Buscador de Comprobantes de Venta v{self.APP_VERSION}")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configurar ícono de la ventana
        # Intentar múltiples rutas para asegurar que funcione con PyInstaller
        icon_path = get_resource_path('imperial.ico')
        
        # Si no encuentra el ícono en _MEIPASS, intentar ruta relativa
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'imperial.ico')
        
        # Si aún no existe, intentar desde el directorio del ejecutable
        if not os.path.exists(icon_path) and hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(os.path.dirname(sys.executable), 'imperial.ico')
        
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                # Si falla, intentar con el método alternativo
                try:
                    self.root.wm_iconbitmap(icon_path)
                except Exception:
                    pass  # Si todo falla, usar ícono por defecto

        # Configurar estilos
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colores
        self.COLOR_FONDO = '#FCF8F8'
        self.COLOR_TEXTO = '#050E3C'
        self.COLOR_TITULO = '#050E3C'
        
        # Configurar fondo de la ventana
        self.root.configure(bg=self.COLOR_FONDO)
        
        # Configurar estilos personalizados
        self.style.configure('TFrame', background=self.COLOR_FONDO)
        self.style.configure('TLabelFrame', background=self.COLOR_FONDO, foreground=self.COLOR_TEXTO, font=('Arial', 10, 'bold'))
        self.style.configure('TLabelFrame.Label', background=self.COLOR_FONDO, foreground=self.COLOR_TEXTO, font=('Arial', 10, 'bold'))
        self.style.configure('TLabel', background=self.COLOR_FONDO, foreground=self.COLOR_TEXTO)
        self.style.configure('TButton', background='#d4c5a9', foreground=self.COLOR_TEXTO, font=('Arial', 9, 'bold'))
        self.style.configure('Accent.TButton', background=self.COLOR_TITULO, foreground='#FCF6D9', font=('Arial', 9, 'bold'))
        self.style.configure('TEntry', fieldbackground='#ffffff', foreground=self.COLOR_TEXTO, insertcolor=self.COLOR_TEXTO)
        self.style.configure('TSeparator', background=self.COLOR_TEXTO)

        # Variables
        self.fecha_var = tk.StringVar()
        self.tarjeta_var = tk.StringVar()
        self.monto_var = tk.StringVar()
        self.ruta_log_var = tk.StringVar(value=RUTA_LOG_DEFAULT)
        self.comprobante_encontrado = None
        self.lineas_comprobante = None
        
        # Variables para búsqueda múltiple
        self.vales_encontrados = []  # Array de objetos con todos los vales encontrados
        self.vale_actual_index = -1  # Índice del vale que se está mostrando actualmente
        self.linea_actual = 0  # Línea actual en el archivo para búsqueda incremental (en lugar de posición)
        self.busqueda_en_curso = False  # Flag para indicar si estamos en medio de una búsqueda múltiple
        
        # Fecha por defecto: fecha del sistema
        self.fecha_default = datetime.now().strftime('%Y-%m-%d')
        self.fecha_var.set(self.fecha_default)

        # Crear interfaz
        self.crear_widgets()
        
    def crear_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=2)  # Panel izquierdo más ancho (datos de búsqueda)
        main_frame.columnconfigure(1, weight=4)  # Panel derecho más angosto (resultado)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        titulo = tk.Label(main_frame, text="BÚSQUEDA DE COMPROBANTES DE VENTA",
                         font=('Arial', 16, 'bold'), fg=self.COLOR_TITULO, bg=self.COLOR_FONDO)
        titulo.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Frame de entrada (lado izquierdo)
        input_frame = tk.LabelFrame(main_frame, text="Datos de búsqueda",
                                    bg=self.COLOR_FONDO, fg=self.COLOR_TEXTO,
                                    font=('Arial', 10, 'bold'), padx=10, pady=10)
        input_frame.grid(row=1, column=8, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Configurar grid del input_frame
        input_frame.columnconfigure(1, weight=1)

        # ============================================
        # SELECTOR DE FECHA (tkcalendar DateEntry)
        # ============================================
        ttk.Label(input_frame, text="📅 Fecha:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        fecha_frame = ttk.Frame(input_frame)
        fecha_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        self.fecha_calendar = DateEntry(fecha_frame,
                                        date_pattern='yyyy-MM-dd',
                                        font=('Arial', 10),
                                        width=15,
                                        background='darkblue',
                                        foreground='white',
                                        borderwidth=2,
                                        year=datetime.now().year,
                                        month=datetime.now().month,
                                        day=datetime.now().day)
        self.fecha_calendar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Sincronizar calendar -> variable
        self.fecha_calendar.bind('<<DateEntrySelected>>', self.on_calendar_change)
        
        # FIX: Patch del calendario para prevenir cierre accidental al navegar
        # Guardar referencia original
        self._original_calendar_show = None
        # Aplicar fix después de que el widget esté listo
        self.root.after(200, self._patch_calendar_grab)
        
        # Tarjeta
        ttk.Label(input_frame, text="💳 Tarjeta:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        tarjeta_entry = ttk.Entry(input_frame, textvariable=self.tarjeta_var, width=15, font=('Arial', 10))
        tarjeta_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Label(input_frame, text="(últimos 4 dígitos)", font=('Arial', 8, 'italic')).grid(row=1, column=2, sticky=tk.W, padx=(5, 0))
        
        # Monto
        ttk.Label(input_frame, text="💰 Monto:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        monto_entry = ttk.Entry(input_frame, textvariable=self.monto_var, width=15, font=('Arial', 10))
        monto_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Label(input_frame, text="(ejemplo: 8300 o 8.300)", font=('Arial', 8, 'italic')).grid(row=2, column=2, sticky=tk.W, padx=(5, 0))
        
        # Ruta del archivo log
        ttk.Label(input_frame, text="📁 Archivo Log:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        ruta_frame = ttk.Frame(input_frame)
        ruta_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ruta_entry = ttk.Entry(ruta_frame, textvariable=self.ruta_log_var, width=15, font=('Arial', 9))
        ruta_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(ruta_frame, text="📂 Examinar", command=self.seleccionar_archivo, width=10).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Separador
        ttk.Separator(input_frame, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        
        # Botones de acción
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)

        self.buscar_btn = ttk.Button(button_frame, text="BUSCAR", command=self.buscar_comprobante_thread,
                                     width=10, style="Accent.TButton")
        self.buscar_btn.pack(side=tk.LEFT, padx=5)

        self.siguiente_btn = ttk.Button(button_frame, text="SIGUIENTE", command=self.buscar_siguiente_vale,
                                        width=10, state='disabled')
        self.siguiente_btn.pack(side=tk.LEFT, padx=5)

        self.guardar_btn = ttk.Button(button_frame, text="GUARDAR", command=self.guardar_comprobante,
                                      width=10, state='disabled')
        self.guardar_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="LIMPIAR", command=self.limpiar_resultados, width=10).pack(side=tk.LEFT, padx=5)

        # Frame de navegación entre vales (oculto inicialmente)
        nav_frame = tk.Frame(input_frame, bg=self.COLOR_FONDO)
        nav_frame.grid(row=6, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        nav_frame.columnconfigure(0, weight=1)
        nav_frame.columnconfigure(2, weight=1)
        
        # Label de información de navegación
        self.nav_label = tk.Label(nav_frame, text="", font=('Arial', 9, 'bold'),
                                  fg=self.COLOR_TEXTO, bg=self.COLOR_FONDO)
        self.nav_label.grid(row=0, column=1, padx=10)
        
        # Botón ANTERIOR
        self.btn_anterior = ttk.Button(nav_frame, text="◀️ ANTERIOR", 
                                       command=self.navegar_anterior, width=12)
        self.btn_anterior.grid(row=0, column=0, padx=5)
        
        # Botón SIGUIENTE (navegación)
        self.btn_siguiente_nav = ttk.Button(nav_frame, text="SIGUIENTE ▶️", 
                                            command=self.navegar_siguiente, width=12)
        self.btn_siguiente_nav.grid(row=0, column=2, padx=5)
        
        # Ocultar frame de navegación inicialmente
        nav_frame.grid_remove()
        self.nav_frame = nav_frame

        # Frame de resultados (lado derecho)
        result_frame = tk.LabelFrame(main_frame, text="Resultado de la búsqueda",
                                     bg=self.COLOR_FONDO, fg=self.COLOR_TEXTO,
                                     font=('Arial', 10, 'bold'), padx=10, pady=10)
        result_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # Área de texto con scrollbar para mostrar el comprobante
        text_frame = ttk.Frame(result_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(text_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Text widget para mostrar resultados
        self.text_resultados = tk.Text(text_frame, wrap=tk.NONE, yscrollcommand=scroll_y.set,
                                       xscrollcommand=scroll_x.set, font=('Courier', 10),
                                       bg='#ffffff', fg=self.COLOR_TEXTO,
                                       insertbackground=self.COLOR_TEXTO)
        self.text_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.text_resultados.yview)
        scroll_x.config(command=self.text_resultados.xview)

        # Configurar tags para colorear el texto
        self.text_resultados.tag_config("info", foreground="#0066cc", font=('Arial', 10, 'bold'))
        self.text_resultados.tag_config("error", foreground="#cc0000", font=('Arial', 10, 'bold'))
        self.text_resultados.tag_config("success", foreground="#008800", font=('Arial', 10, 'bold'))
        self.text_resultados.tag_config("titulo", foreground=self.COLOR_TITULO, font=('Arial', 11, 'bold'))
        
        
    def seleccionar_archivo(self):
        """Abrir diálogo para seleccionar archivo .log"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de log",
            filetypes=[("Archivos de log", "*.log"), ("Todos los archivos", "*.*")]
        )
        if filename:
            self.ruta_log_var.set(filename)
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"📁 Archivo seleccionado: {os.path.basename(filename)}")

    def _patch_calendar_grab(self):
        """Aplica patch al calendario para evitar que se cierre al navegar entre meses/años.
        El problema principal es el grab_set() que causa conflictos con eventos."""
        try:
            # Acceder al calendario interno
            if hasattr(self.fecha_calendar, '_top_cal') and self.fecha_calendar._top_cal.winfo_exists():
                # El problema es el grab_set() que se llama cuando se muestra el calendario
                # Vamos a hacer un monkey-patch del método _drop_down para usar grab_set_global
                original_drop_down = self.fecha_calendar._drop_down
                
                def fixed_drop_down():
                    # Llamar al método original
                    original_drop_down()
                    # Después de mostrar el calendario, ajustar el grab
                    if hasattr(self.fecha_calendar, '_top_cal') and self.fecha_calendar._top_cal.winfo_viewable():
                        # Liberar el grab local y usar uno global que no interfiere con la navegación
                        self.fecha_calendar._top_cal.grab_release()
                        # Usar grab_set_global para que los clics en botones de navegación funcionen
                        self.fecha_calendar._top_cal.grab_set_global()
                
                # Reemplazar el método
                self.fecha_calendar._drop_down = fixed_drop_down
        except Exception as e:
            # Si el patch falla, continuar normalmente
            pass

    def _apply_calendar_fix(self):
        """Aplica fix para prevenir que el calendario se cierre al navegar entre meses/años.
        Este método se llama después de que el widget se inicializa completamente."""
        # No necesitamos hacer nada especial aquí - el fix principal está en 
        # el manejo del grab del Toplevel
        pass

    def on_calendar_focus_out(self, event=None):
        """Manejar el evento FocusOut del DateEntry"""
        # No hacer nada - prevenir que el foco cause cierre accidental
        pass

    def on_calendar_change(self, event=None):
        """Cuando se selecciona una fecha en el calendario"""
        fecha_seleccionada = self.fecha_calendar.get_date()
        # Formatear como YYYY-MM-DD
        fecha_formateada = fecha_seleccionada.strftime('%Y-%m-%d')
        self.fecha_var.set(fecha_formateada)
    
    def formatear_monto(self, monto_str):
        """Formatea el monto para que coincida con el formato del log"""
        monto_limpio = monto_str.replace('.', '').replace(',', '')
        
        if not monto_limpio.isdigit():
            return None
        
        monto_int = int(monto_limpio)
        
        if monto_int >= 1000:
            miles = monto_int // 1000
            resto = monto_int % 1000
            return f"{miles}.{resto:03d}"
        else:
            return str(monto_int)
    
    def buscar_comprobante_thread(self):
        """Ejecutar búsqueda en un hilo separado para no bloquear la interfaz"""
        # Validar campos
        if not self.validar_campos():
            return

        # Inicializar variables para búsqueda múltiple
        self.vales_encontrados = []
        self.vale_actual_index = -1
        self.linea_actual = 0
        self.busqueda_en_curso = False

        # Deshabilitar botón de búsqueda durante la operación
        self.buscar_btn.config(state='disabled')
        self.siguiente_btn.config(state='disabled')
        self.guardar_btn.config(state='disabled')
        
        if hasattr(self, 'progress_bar'):
            self.progress_bar.start(10)
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text="🔍 Buscando comprobante...")
        
        # Limpiar resultados anteriores
        self.text_resultados.delete(1.0, tk.END)
        self.text_resultados.insert(tk.END, "🔍 BUSCANDO COMPROBANTE...\n", "info")
        self.text_resultados.insert(tk.END, "=" * 60 + "\n", "info")
        self.text_resultados.insert(tk.END, f"📅 Fecha: {self.fecha_var.get()}\n", "info")
        self.text_resultados.insert(tk.END, f"💳 Tarjeta: ***{self.tarjeta_var.get()}\n", "info")
        self.text_resultados.insert(tk.END, f"💰 Monto: ${self.formatear_monto(self.monto_var.get())}\n", "info")
        self.text_resultados.insert(tk.END, "=" * 60 + "\n\n", "info")
        self.text_resultados.see(tk.END)
        
        # Ejecutar búsqueda en hilo separado
        thread = threading.Thread(target=self.realizar_busqueda, daemon=True)
        thread.start()
    
    def realizar_busqueda(self):
        """Realiza la búsqueda del comprobante"""
        try:
            comprobante = self.buscar_comprobante_en_log()

            # Actualizar interfaz desde el hilo principal
            self.root.after(0, self.mostrar_resultados, comprobante)
        except Exception as e:
            self.root.after(0, self.mostrar_error, str(e))

    def navegar_anterior(self):
        """Navega al vale anterior en los resultados encontrados"""
        if self.vale_actual_index > 0:
            self.vale_actual_index -= 1
            self.mostrar_vale_actual()
    
    def navegar_siguiente(self):
        """Navega al siguiente vale en los resultados encontrados"""
        if self.vale_actual_index < len(self.vales_encontrados) - 1:
            self.vale_actual_index += 1
            self.mostrar_vale_actual()
    
    def mostrar_vale_actual(self):
        """Muestra el vale actual sin buscar más"""
        if not self.vales_encontrados or self.vale_actual_index < 0:
            return
        
        vale = self.vales_encontrados[self.vale_actual_index]
        total_vales = len(self.vales_encontrados)
        indice_actual = self.vale_actual_index + 1
        
        # Limpiar y mostrar el vale
        self.text_resultados.delete(1.0, tk.END)
        
        # Encabezado
        self.text_resultados.insert(tk.END, "=" * 60 + "\n", "success")
        self.text_resultados.insert(tk.END, 
            f"📋 COMPROBANTE ENCONTRADO #{indice_actual}\n", 
            "titulo"
        )
        self.text_resultados.insert(tk.END, "=" * 60 + "\n\n", "success")
        
        # Metadatos
        if vale.get("hora"):
            self.text_resultados.insert(tk.END, f"🕐 Hora: {vale['hora']}\n", "info")
        if vale.get("numero_operacion"):
            self.text_resultados.insert(tk.END, f"🔢 Nº Operación: {vale['numero_operacion']}\n", "info")
        self.text_resultados.insert(tk.END, f"💳 Tarjeta: ***{vale['tarjeta']}\n", "info")
        self.text_resultados.insert(tk.END, f"💰 Monto: ${vale['monto']}\n", "info")
        self.text_resultados.insert(tk.END, "\n" + "-" * 60 + "\n", "info")
        
        # Líneas del comprobante
        for linea in vale["lineas"]:
            if " - Line " in linea:
                contenido = linea.split(" - Line ", 1)[1]
                self.text_resultados.insert(tk.END, contenido + "\n")
            else:
                self.text_resultados.insert(tk.END, linea + "\n")
        
        # Pie con información de navegación
        self.text_resultados.insert(tk.END, "\n" + "=" * 60 + "\n", "info")
        self.text_resultados.insert(tk.END, 
            f"Total encontrados: {total_vales} | Mostrando: #{indice_actual}\n", 
            "info"
        )
        self.text_resultados.see(tk.END)
        
        # Actualizar label de navegación
        self.nav_label.config(text=f"Vale {indice_actual} de {total_vales}")
        
        # Actualizar estado de botones de navegación
        self.btn_anterior.config(state='normal' if self.vale_actual_index > 0 else 'disabled')
        self.btn_siguiente_nav.config(state='normal' if self.vale_actual_index < total_vales - 1 else 'disabled')
        
        # Actualizar status_label si existe
        if hasattr(self, 'status_label'):
            self.status_label.config(
                text=f"✅ Mostrando comprobante #{indice_actual} de {total_vales}"
            )

    def buscar_siguiente_vale(self):
        """Busca el siguiente vale después del actual"""
        # Deshabilitar botón siguiente durante la búsqueda
        self.siguiente_btn.config(state='disabled')
        self.buscar_btn.config(state='disabled')
        
        if hasattr(self, 'progress_bar'):
            self.progress_bar.start(10)
        
        if hasattr(self, 'status_label'):
            self.status_label.config(text="🔍 Buscando siguiente comprobante...")

        # Ejecutar búsqueda en hilo separado
        thread = threading.Thread(target=self.realizar_busqueda_siguiente, daemon=True)
        thread.start()

    def realizar_busqueda_siguiente(self):
        """Realiza la búsqueda del siguiente vale"""
        try:
            comprobante = self.buscar_comprobante_en_log()

            # Actualizar interfaz desde el hilo principal
            self.root.after(0, self.mostrar_resultados, comprobante)
        except Exception as e:
            self.root.after(0, self.mostrar_error, str(e))
    
    def buscar_comprobante_en_log(self):
        """Busca el comprobante en el archivo log desde la línea actual"""
        archivo_log = self.ruta_log_var.get()
        fecha_buscar = self.fecha_var.get()
        tarjeta_buscar = self.tarjeta_var.get()
        monto_buscar = self.formatear_monto(self.monto_var.get())

        if not os.path.exists(archivo_log):
            return {"error": f"Archivo no encontrado: {archivo_log}"}

        lineas_vale = []
        dentro_comprobante = False
        tarjeta_encontrada = False
        monto_encontrado = False
        archivo_leido_completo = False
        hora_comprobante = None
        numero_operacion = None

        try:
            # Leer todas las líneas del archivo
            with open(archivo_log, 'r', encoding='utf-8', errors='ignore') as archivo:
                todas_las_lineas = archivo.readlines()
            
            # Iterar desde la línea actual
            for idx_linea in range(self.linea_actual, len(todas_las_lineas)):
                linea = todas_las_lineas[idx_linea]
                linea_limpia = linea.rstrip('\n\r')

                # Extraer el contenido después de "Line"
                contenido = linea_limpia
                if " - Line " in linea_limpia:
                    contenido = linea_limpia.split(" - Line ", 1)[1]
                elif " - Line" in linea_limpia:
                    contenido = ""

                # Verificar fecha
                linea_fecha = None
                if len(linea_limpia) >= 10 and re.match(r'\d{4}-\d{2}-\d{2}', linea_limpia):
                    linea_fecha = linea_limpia[:10]
                    # Extraer también la hora si está disponible
                    if len(linea_limpia) >= 19 and re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', linea_limpia):
                        hora_comprobante = linea_limpia[11:19]

                # Cambio de fecha
                if linea_fecha and linea_fecha != fecha_buscar:
                    if dentro_comprobante and not (tarjeta_encontrada and monto_encontrado):
                        lineas_vale = []
                        dentro_comprobante = False
                        tarjeta_encontrada = False
                        monto_encontrado = False
                    continue

                # Buscar inicio de comprobante
                if "COMPROBANTE DE VENTA" in contenido:
                    lineas_vale = []
                    dentro_comprobante = True
                    tarjeta_encontrada = False
                    monto_encontrado = False
                    lineas_vale.append(linea_limpia)
                    continue

                # Dentro del comprobante
                if dentro_comprobante:
                    lineas_vale.append(linea_limpia)

                    # Buscar número de operación
                    if not numero_operacion:
                        match_operacion = re.search(r'Op\.?\s*(\d+)', contenido, re.IGNORECASE)
                        if match_operacion:
                            numero_operacion = match_operacion.group(1)

                    # Buscar tarjeta
                    if not tarjeta_encontrada and re.search(r'\*+\d+', contenido):
                        match_tarjeta = re.search(r'\*+(\d+)', contenido)
                        if match_tarjeta:
                            ultimos_digitos = match_tarjeta.group(1)
                            if ultimos_digitos == tarjeta_buscar:
                                tarjeta_encontrada = True

                    # Buscar TOTAL
                    if not monto_encontrado and contenido.strip().startswith("TOTAL"):
                        match_monto = re.search(r'\$\s*([\d\.]+)', contenido)
                        if match_monto:
                            monto_linea = match_monto.group(1).strip()
                            if monto_linea == monto_buscar:
                                monto_encontrado = True
                            else:
                                lineas_vale = []
                                dentro_comprobante = False
                                tarjeta_encontrada = False
                                continue

                    # Buscar cierre
                    if "ACEPTO PAGAR SEGUN CONTRATO CON EMISOR" in contenido:
                        # Guardar la línea actual + 1 para continuar desde ahí
                        self.linea_actual = idx_linea + 1
                        
                        if tarjeta_encontrada and monto_encontrado:
                            # Crear objeto vale con todos los datos
                            vale = {
                                "lineas": lineas_vale,
                                "hora": hora_comprobante,
                                "numero_operacion": numero_operacion,
                                "fecha": fecha_buscar,
                                "tarjeta": tarjeta_buscar,
                                "monto": monto_buscar
                            }
                            
                            # Agregar al array de vales encontrados
                            self.vales_encontrados.append(vale)
                            self.vale_actual_index = len(self.vales_encontrados) - 1
                            
                            # Verificar si hay más vales en el resto del archivo
                            hay_mas = self.verificar_si_hay_mas_vales(
                                todas_las_lineas[idx_linea + 1:], 
                                fecha_buscar, 
                                tarjeta_buscar, 
                                monto_buscar
                            )
                            
                            if not hay_mas:
                                archivo_leido_completo = True
                            
                            return {
                                "exito": True, 
                                "lineas": lineas_vale,
                                "hora": hora_comprobante,
                                "numero_operacion": numero_operacion,
                                "archivo_leido_completo": archivo_leido_completo,
                                "total_encontrados": len(self.vales_encontrados),
                                "indice_actual": self.vale_actual_index,
                                "hay_mas": hay_mas
                            }
                        else:
                            lineas_vale = []
                            dentro_comprobante = False
                            tarjeta_encontrada = False
                            monto_encontrado = False
                            numero_operacion = None

            # Si llegamos aquí, se leyó el archivo completo
            archivo_leido_completo = True
            
            if len(self.vales_encontrados) > 0:
                # Ya no hay más vales
                return {
                    "archivo_leido_completo": True,
                    "mensaje": "Se han revisado todos los vales en el archivo",
                    "total_encontrados": len(self.vales_encontrados)
                }
            else:
                return {"exito": False, "mensaje": "No se encontró el comprobante"}

        except Exception as e:
            return {"error": str(e)}

    def verificar_si_hay_mas_vales(self, lineas_restantes, fecha_buscar, tarjeta_buscar, monto_buscar):
        """Verifica si hay más vales que coincidan en las líneas restantes"""
        dentro_comprobante = False
        tarjeta_encontrada = False
        monto_encontrado = False
        
        for linea in lineas_restantes:
            linea_limpia = linea.rstrip('\n\r')
            contenido = linea_limpia
            if " - Line " in linea_limpia:
                contenido = linea_limpia.split(" - Line ", 1)[1]
            
            # Verificar fecha
            if len(linea_limpia) >= 10 and re.match(r'\d{4}-\d{2}-\d{2}', linea_limpia):
                linea_fecha = linea_limpia[:10]
                if linea_fecha != fecha_buscar:
                    continue

            # Buscar inicio de comprobante
            if "COMPROBANTE DE VENTA" in contenido:
                dentro_comprobante = True
                tarjeta_encontrada = False
                monto_encontrado = False
                continue

            if dentro_comprobante:
                # Buscar tarjeta
                if not tarjeta_encontrada and re.search(r'\*+\d+', contenido):
                    match_tarjeta = re.search(r'\*+(\d+)', contenido)
                    if match_tarjeta and match_tarjeta.group(1) == tarjeta_buscar:
                        tarjeta_encontrada = True

                # Buscar TOTAL
                if not monto_encontrado and contenido.strip().startswith("TOTAL"):
                    match_monto = re.search(r'\$\s*([\d\.]+)', contenido)
                    if match_monto and match_monto.group(1).strip() == monto_buscar:
                        monto_encontrado = True

                # Si encontramos un vale completo, hay más
                if tarjeta_encontrada and monto_encontrado and "ACEPTO PAGAR SEGUN CONTRATO CON EMISOR" in contenido:
                    return True

        return False
    
    def mostrar_resultados(self, resultado):
        """Muestra los resultados en el área de texto"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.stop()

        self.buscar_btn.config(state='normal')

        if "error" in resultado:
            self.text_resultados.delete(1.0, tk.END)
            self.text_resultados.insert(tk.END, "❌ ERROR\n", "error")
            self.text_resultados.insert(tk.END, "=" * 60 + "\n", "error")
            self.text_resultados.insert(tk.END, resultado["error"], "error")
            if hasattr(self, 'status_label'):
                self.status_label.config(text="❌ Error en la búsqueda")
            self.siguiente_btn.config(state='disabled')
            # Ocultar frame de navegación en caso de error
            self.nav_frame.grid_remove()
            messagebox.showerror("Error", resultado["error"])
            return

        # Si no hay más vales pero ya teníamos encontrados
        if "archivo_leido_completo" in resultado and not resultado.get("exito", False):
            if resultado.get("total_encontrados", 0) > 0:
                # Ya se leyeron todos los vales
                self.siguiente_btn.config(state='disabled')
                
                # Mostrar frame de navegación si hay 2+ vales
                if len(self.vales_encontrados) >= 2:
                    self.nav_frame.grid()
                    self.nav_label.config(text=f"Vale {self.vale_actual_index + 1} de {len(self.vales_encontrados)}")
                    self.btn_anterior.config(state='normal' if self.vale_actual_index > 0 else 'disabled')
                    self.btn_siguiente_nav.config(state='normal' if self.vale_actual_index < len(self.vales_encontrados) - 1 else 'disabled')
                else:
                    self.nav_frame.grid_remove()
                
                if hasattr(self, 'status_label'):
                    self.status_label.config(
                        text=f"✅ Es el único vale que existe en el archivo "
                             f"(Total encontrados: {resultado['total_encontrados']})"
                    )
                # Mostrar mensaje en el área de texto
                self.text_resultados.insert(tk.END, "\n" + "=" * 60 + "\n", "info")
                self.text_resultados.insert(tk.END, 
                    "✅ ES EL ÚNICO VALE QUE EXISTE EN EL ARCHIVO\n", 
                    "success"
                )
                self.text_resultados.insert(tk.END, "=" * 60 + "\n", "info")
                self.text_resultados.insert(tk.END, 
                    f"Total de vales encontrados: {resultado['total_encontrados']}\n", 
                    "info"
                )
                self.text_resultados.insert(tk.END, 
                    "No se encontraron más coincidencias en el archivo.\n", 
                    "info"
                )
                self.text_resultados.see(tk.END)
                return
            else:
                self.text_resultados.delete(1.0, tk.END)
                self.text_resultados.insert(tk.END, "❌ COMPROBANTE NO ENCONTRADO\n", "error")
                self.text_resultados.insert(tk.END, "=" * 60 + "\n", "error")
                self.text_resultados.insert(tk.END, resultado.get("mensaje", "No se encontró el comprobante"), "error")
                if hasattr(self, 'status_label'):
                    self.status_label.config(text="❌ Comprobante no encontrado")
                self.siguiente_btn.config(state='disabled')
                return

        if resultado.get("exito"):
            self.lineas_comprobante = resultado["lineas"]
            self.comprobante_encontrado = True

            # Mostrar comprobante
            self.text_resultados.delete(1.0, tk.END)

            # Encabezado con información del vale
            total_vales = resultado.get("total_encontrados", 1)
            indice_actual = resultado.get("indice_actual", 0) + 1

            self.text_resultados.insert(tk.END, "=" * 60 + "\n", "success")
            self.text_resultados.insert(tk.END,
                f"📋 COMPROBANTE ENCONTRADO #{indice_actual}\n",
                "titulo"
            )
            self.text_resultados.insert(tk.END, "=" * 60 + "\n\n", "success")

            # Mostrar metadatos del vale
            if resultado.get("hora"):
                self.text_resultados.insert(tk.END, f"🕐 Hora: {resultado['hora']}\n", "info")
            if resultado.get("numero_operacion"):
                self.text_resultados.insert(tk.END, f"🔢 Nº Operación: {resultado['numero_operacion']}\n", "info")
            self.text_resultados.insert(tk.END, f"💳 Tarjeta: ***{self.tarjeta_var.get()}\n", "info")
            self.text_resultados.insert(tk.END, f"💰 Monto: ${self.formatear_monto(self.monto_var.get())}\n", "info")
            self.text_resultados.insert(tk.END, "\n" + "-" * 60 + "\n", "info")

            # Mostrar líneas del comprobante
            for linea in self.lineas_comprobante:
                if " - Line " in linea:
                    contenido = linea.split(" - Line ", 1)[1]
                    self.text_resultados.insert(tk.END, contenido + "\n")
                else:
                    self.text_resultados.insert(tk.END, linea + "\n")

            # Mostrar frame de navegación si hay 2+ vales
            if total_vales >= 2:
                self.nav_frame.grid()
                self.nav_label.config(text=f"Vale {indice_actual} de {total_vales}")
                self.btn_anterior.config(state='normal' if self.vale_actual_index > 0 else 'disabled')
                self.btn_siguiente_nav.config(state='normal' if self.vale_actual_index < total_vales - 1 else 'disabled')
            else:
                self.nav_frame.grid_remove()
            
            # Pie con información de navegación
            self.text_resultados.insert(tk.END, "\n" + "=" * 60 + "\n", "info")
            self.text_resultados.insert(tk.END, 
                f"Total encontrados: {total_vales} | Mostrando: #{indice_actual}\n", 
                "info"
            )
            
            # Verificar si hay más vales
            if resultado.get("hay_mas", False):
                self.text_resultados.insert(tk.END, 
                    "💡 Presione 'SIGUIENTE' para buscar más coincidencias\n", 
                    "info"
                )
                self.siguiente_btn.config(state='normal')
                if hasattr(self, 'status_label'):
                    self.status_label.config(
                        text=f"✅ Comprobante #{indice_actual} encontrado de {total_vales} "
                             f"(hay más disponibles)"
                    )
            else:
                self.text_resultados.insert(tk.END, 
                    "✅ Es el único vale que existe en el archivo\n", 
                    "success"
                )
                self.siguiente_btn.config(state='disabled')
                if hasattr(self, 'status_label'):
                    self.status_label.config(
                        text=f"✅ Es el único vale que existe en el archivo "
                             f"(Total: {total_vales})"
                    )
            
            self.text_resultados.see(tk.END)
            self.guardar_btn.config(state='normal')
            messagebox.showinfo("Éxito", 
                f"¡Comprobante encontrado exitosamente!\n\n"
                f"Total encontrados: {total_vales}\n"
                f"Mostrando: #{indice_actual}"
            )
        else:
            self.text_resultados.delete(1.0, tk.END)
            self.text_resultados.insert(tk.END, "❌ COMPROBANTE NO ENCONTRADO\n", "error")
            self.text_resultados.insert(tk.END, "=" * 60 + "\n", "error")
            self.text_resultados.insert(tk.END, resultado.get("mensaje", "No se encontró el comprobante"), "error")
            self.text_resultados.insert(tk.END, "\n\n📝 Posibles causas:\n", "info")
            self.text_resultados.insert(tk.END, "   • La fecha es incorrecta\n", "info")
            self.text_resultados.insert(tk.END, "   • Los dígitos de la tarjeta no coinciden\n", "info")
            self.text_resultados.insert(tk.END, "   • El monto es incorrecto\n", "info")
            self.text_resultados.insert(tk.END, "   • La transacción no existe en el archivo", "info")
            if hasattr(self, 'status_label'):
                self.status_label.config(text="❌ Comprobante no encontrado")
            self.siguiente_btn.config(state='disabled')
            self.guardar_btn.config(state='disabled')
    
    def mostrar_error(self, mensaje_error):
        """Muestra errores en la interfaz"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.stop()
        
        self.buscar_btn.config(state='normal')
        self.text_resultados.delete(1.0, tk.END)
        self.text_resultados.insert(tk.END, "❌ ERROR\n", "error")
        self.text_resultados.insert(tk.END, "=" * 60 + "\n", "error")
        self.text_resultados.insert(tk.END, mensaje_error, "error")
        if hasattr(self, 'status_label'):
            self.status_label.config(text="❌ Error en la búsqueda")
        messagebox.showerror("Error", mensaje_error)
    
    def validar_campos(self):
        """Valida que los campos estén correctamente llenos"""
        # Primero verificar si hay fecha seleccionada en el calendar
        try:
            fecha_calendar = self.fecha_calendar.get_date()
            if fecha_calendar:
                fecha_formateada = fecha_calendar.strftime('%Y-%m-%d')
                self.fecha_var.set(fecha_formateada)
        except:
            pass
        
        fecha = self.fecha_var.get().strip()
        if not fecha or len(fecha) != 10 or fecha[4] != '-' or fecha[7] != '-':
            messagebox.showwarning("Validación", "Por favor seleccione una fecha válida (YYYY-MM-DD)")
            return False
        
        tarjeta = self.tarjeta_var.get().strip()
        if not tarjeta or not tarjeta.isdigit() or len(tarjeta) < 4:
            messagebox.showwarning("Validación", "Por favor ingrese al menos 4 dígitos de la tarjeta")
            return False
        
        monto = self.monto_var.get().strip()
        if not monto:
            messagebox.showwarning("Validación", "Por favor ingrese un monto")
            return False
        
        monto_formateado = self.formatear_monto(monto)
        if not monto_formateado:
            messagebox.showwarning("Validación", "Por favor ingrese un monto válido (solo números)")
            return False
        
        archivo_log = self.ruta_log_var.get().strip()
        if not archivo_log:
            messagebox.showwarning("Validación", "Por favor seleccione un archivo de log")
            return False
        
        return True
    
    def guardar_comprobante(self):
        """Guarda todos los comprobantes encontrados en la ubicación seleccionada por el usuario"""
        if not self.vales_encontrados:
            messagebox.showwarning("Guardar", "No hay un comprobante para guardar")
            return

        # Solicitar ubicación para guardar
        fecha = self.fecha_var.get()
        tarjeta = self.tarjeta_var.get()
        monto = self.formatear_monto(self.monto_var.get())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if len(self.vales_encontrados) == 1:
            # Si hay un solo vale, usar el nombre original
            nombre_por_defecto = f"comprobante_{fecha}_{tarjeta}_{monto}_{timestamp}.txt"
        else:
            # Si hay múltiples vales, crear un archivo con todos
            nombre_por_defecto = f"comprobantes_{fecha}_{tarjeta}_{monto}_{timestamp}_({len(self.vales_encontrados)}_vales).txt"

        archivo_guardar = filedialog.asksaveasfilename(
            title="Guardar comprobante(s)",
            defaultextension=".txt",
            initialfile=nombre_por_defecto,
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )

        if not archivo_guardar:
            return

        try:
            with open(archivo_guardar, 'w', encoding='utf-8') as archivo:
                if len(self.vales_encontrados) == 1:
                    # Guardar un solo vale
                    vale = self.vales_encontrados[0]
                    # Agregar metadatos
                    archivo.write("=" * 60 + "\n")
                    archivo.write(f"COMPROBANTE ENCONTRADO\n")
                    archivo.write("=" * 60 + "\n")
                    if vale.get("hora"):
                        archivo.write(f"Hora: {vale['hora']}\n")
                    if vale.get("numero_operacion"):
                        archivo.write(f"Numero de Operacion: {vale['numero_operacion']}\n")
                    archivo.write(f"Tarjeta: ***{vale['tarjeta']}\n")
                    archivo.write(f"Monto: ${vale['monto']}\n")
                    archivo.write("=" * 60 + "\n\n")
                    
                    for linea in vale["lineas"]:
                        if " - Line " in linea:
                            contenido = linea.split(" - Line ", 1)[1]
                            archivo.write(contenido + '\n')
                        else:
                            archivo.write(linea + '\n')
                else:
                    # Guardar todos los vales
                    archivo.write("=" * 60 + "\n")
                    archivo.write(f"RESULTADOS DE BÚSQUEDA\n")
                    archivo.write("=" * 60 + "\n")
                    archivo.write(f"Fecha: {fecha}\n")
                    archivo.write(f"Tarjeta: ***{tarjeta}\n")
                    archivo.write(f"Monto: ${monto}\n")
                    archivo.write(f"Total comprobantes: {len(self.vales_encontrados)}\n")
                    archivo.write("=" * 60 + "\n\n")
                    
                    for i, vale in enumerate(self.vales_encontrados, 1):
                        archivo.write(f"\n{'=' * 60}\n")
                        archivo.write(f"COMPROBANTE #{i}\n")
                        archivo.write(f"{'=' * 60}\n")
                        if vale.get("hora"):
                            archivo.write(f"Hora: {vale['hora']}\n")
                        if vale.get("numero_operacion"):
                            archivo.write(f"Numero de Operacion: {vale['numero_operacion']}\n")
                        archivo.write(f"Tarjeta: ***{vale['tarjeta']}\n")
                        archivo.write(f"Monto: ${vale['monto']}\n")
                        archivo.write(f"{'=' * 60}\n\n")
                        
                        for linea in vale["lineas"]:
                            if " - Line " in linea:
                                contenido = linea.split(" - Line ", 1)[1]
                                archivo.write(contenido + '\n')
                            else:
                                archivo.write(linea + '\n')
                        
                        archivo.write("\n")

            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"✅ Comprobante(s) guardado(s) en: {os.path.basename(archivo_guardar)}")
            messagebox.showinfo("Éxito",
                f"Se guardaron {len(self.vales_encontrados)} comprobante(s) exitosamente en:\n{archivo_guardar}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el comprobante:\n{str(e)}")
    
    def limpiar_resultados(self):
        """Limpia los resultados y reinicia el estado"""
        # Limpiar variables
        self.tarjeta_var.set('')
        self.monto_var.set('')

        # Volver a fecha por defecto
        self.fecha_var.set(self.fecha_default)
        self.fecha_calendar.set_date(datetime.now())

        # Limpiar variables de búsqueda múltiple
        self.vales_encontrados = []
        self.vale_actual_index = -1
        self.linea_actual = 0
        self.busqueda_en_curso = False

        # Ocultar frame de navegación
        if hasattr(self, 'nav_frame'):
            self.nav_frame.grid_remove()

        # Limpiar resultados
        self.text_resultados.delete(1.0, tk.END)
        self.comprobante_encontrado = None
        self.lineas_comprobante = None
        self.guardar_btn.config(state='disabled')
        self.siguiente_btn.config(state='disabled')
        
        # Actualizar status_label solo si existe
        if hasattr(self, 'status_label'):
            self.status_label.config(text="✅ Listo para buscar")
        
        self.text_resultados.insert(tk.END, "✅ Listo para buscar un nuevo comprobante\n", "info")
        self.text_resultados.insert(tk.END, "=" * 60 + "\n", "info")
        self.text_resultados.insert(tk.END, "Ingrese los datos y presione BUSCAR", "info")


def main():
    """Función principal"""
    root = tk.Tk()
    app = BuscadorComprobantes(root)
    
    # Centrar la ventana en la pantalla
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()