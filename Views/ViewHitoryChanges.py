from Controllers.ConfigController import ConfigController
from Controllers.PrinterController import PrinterController
from Models.Queries import Cambios
from Tools.Tools import Tools

import tkinter as tk
from tkinter import ttk
from tkinter import StringVar, IntVar, messagebox as mb
from datetime import datetime

class ViewHitoryChanges:
    def __init__(self) -> None:
        # Crea la ventana principal
        self.window_changes = tk.Toplevel()
        # instancia de la clase de herramientas
        self.instance_tools = Tools()
        self.instance_config = ConfigController()
        self.model_cambios = Cambios()
        self.printer_controller = PrinterController()

        # se elimina la funcinalidad del boton de cerrar
        self.window_changes.protocol(
            "WM_DELETE_WINDOW", lambda: self.instance_tools.desconectar(self.window_changes))
        # # deshabilita los botones de minimizar y maximizar
        # self.window_changes.attributes('-toolwindow', True)
        # # coloca la ventana al frente de otras ventanas
        # self.window_changes.attributes('-topmost', True)

        ancho_max = self.window_changes.winfo_screenwidth()
        alto_max = self.window_changes.winfo_screenheight()

        self.window_changes.resizable(True, False)
        self.get_config_data()

        self.window_changes.title(f'Historial de cambios -> {self.nombre_estacionamiento}')

        # Configura la columna principal del panel para que use todo el espacio disponible
        self.window_changes.columnconfigure(0, weight=1)

        self.max_size_x = None
        self.max_size_y = None

        # Crea las variables para almacenar los registros y las consultas a la base de datos
        self.registros = None

        self.variable_mes = StringVar()
        self.opciones_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        self.variable_años = IntVar(value=datetime.now().date().year)
        self.opciones_años = [i for i in range(2020, 2041)]


        self.view_campos_consulta()

        # Inicia el loop principal de la ventana
        self.window_changes.mainloop()

    def get_config_data(self) -> None:
        """
        Obtiene la configuracion del sistema desde el archivo de configuracion.

        La funcion asigna valores a diversas variables de instancia con base en la configuracion del sistema.

        No retorna ningún valor explicito, pero asigna valores a las variables de instancia de la clase.
        """
        try:
            data_config = self.instance_config.get_config(
                "general")

            self.nombre_estacionamiento = data_config["informacion_estacionamiento"]["nombre_estacionamiento"]

            data_config = data_config["configuracion_sistema"]

            # Configuracion de fechas del sistema
            formatos_fecha = data_config["formatos_fecha"]

            self.date_format_system = "%Y-%m-%d %H:%M:%S"
            self.date_format_interface = formatos_fecha[data_config["formato_hora_interface"]]
            self.date_format_ticket = formatos_fecha[data_config["formato_hora_boleto"]]

            # Configuracion de fuentes y estilos
            fuente_sistema = data_config["fuente"]

            size_text_font = data_config["size_text_font"]
            size_text_font_tittle_system = data_config["size_text_font_tittle_system"]
            size_text_font_subtittle_system = data_config["size_text_font_subtittle_system"]
            size_text_button_font = data_config["size_text_button_font"]

            self.font_entrada = (fuente_sistema, size_text_font+10)
            self.font_entrada_negritas = (
                fuente_sistema, size_text_font+10, 'bold')
            self.font_mensaje = (fuente_sistema, size_text_font+30)
            self.font_reloj = (fuente_sistema, size_text_font+55)
            self.font_cancel = (fuente_sistema, size_text_font+5)
            self.font_bienvenida = (fuente_sistema, size_text_font+15)
            self.font_entry_placa = (fuente_sistema, size_text_font+25, 'bold')
            self.font_view_importe = (fuente_sistema, size_text_font+38)
            self.font_pensiones_vencidas = (fuente_sistema, size_text_font+5)

            self.font_subtittle_system = (
                fuente_sistema, size_text_font_subtittle_system, 'bold')
            self.font_tittle_system = (
                fuente_sistema, size_text_font_tittle_system, 'bold')
            self.font_botones_interface = (
                fuente_sistema, size_text_button_font, 'bold')
            self.font_text_interface = (fuente_sistema, size_text_font)
            self.font_text_entry_interface = (
                fuente_sistema, size_text_font, 'bold')
            self.font_scrolledtext = (fuente_sistema, size_text_font)

            # Configuracion de colores
            self.button_color = data_config["color_botones_interface"]
            self.button_letters_color = data_config["color_letra_botones_interface"]

            self.button_color_cobro = data_config["color_boton_cobro"]
            self.button_letters_color_cobro = data_config["color_letra_boton_cobro"]

            data_config = None

        except Exception as e:
            mb.showerror(
                "Error", f"Error al cargar configuracion, inicie de nuevo el sistema.\n\nEn caso de que el error continue contacte a un administrador inmediatamente y muestre el siguiente error:\n\n\n{e}")
            raise SystemExit()


    def view_campos_consulta(self):
        """Crea y empaqueta los campos de consulta en la ventana."""
        # Label frame principal
        seccion_superior = tk.LabelFrame(self.window_changes, text='')
        seccion_superior.columnconfigure(1, weight=1)
        # seccion_superior.grid_propagate(True)
        seccion_superior.propagate(True)
        seccion_superior.grid(row=0, column=0, sticky=tk.NSEW)


        seccion_informacion = tk.LabelFrame(
            self.window_changes, text='Seleccione el mes a consultar', font=self.font_tittle_system)
        seccion_informacion.grid(row=1, column=0, padx=5, pady=5, sticky=tk.N)

        seccion_datos = tk.Frame(seccion_informacion)
        seccion_datos.grid(row=0, column=0, padx=5, pady=5)

        etiqueta_mes = tk.Label(
            seccion_datos, text='Seleccione Mes', font=self.font_subtittle_system)
        etiqueta_mes.grid(row=2, column=0, padx=5, pady=5)

        self.lista_desplegable_meses = ttk.Combobox(
            seccion_datos, values=self.opciones_meses, textvariable=self.variable_mes, state='readonly', width=12,  height=5, font=self.font_text_interface)
        self.lista_desplegable_meses.grid(row=2, column=1, padx=5, pady=5)
        self.lista_desplegable_meses.current(0)

        etiqueta_año = tk.Label(
            seccion_datos, text='Seleccione Año', font=self.font_subtittle_system)
        etiqueta_año.grid(row=3, column=0, padx=5, pady=5)

        self.lista_desplegable_años = ttk.Combobox(
            seccion_datos, values=self.opciones_años, textvariable=self.variable_años, state='readonly', width=12,  height=5, font=self.font_text_interface)
        self.lista_desplegable_años.grid(row=3, column=1, padx=5, pady=5)

        seccion_botones= tk.Frame(seccion_informacion)
        seccion_botones.grid(row=1, column=0, padx=0, pady=0)

        self.login_button = tk.Button(
            seccion_botones, text="Consultar", command=self.get_changes, width=10, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        self.login_button.grid(column=0, row=0, padx=5, pady=5)

        self.exit_button = tk.Button(
            seccion_botones, text="Cancelar", command=lambda: self.instance_tools.desconectar(self.window_changes), width=10, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        self.exit_button.grid(column=1, row=0, padx=5, pady=5)

        # Obtiene los nombres de las columnas de la tabla que se va a mostrar
        columnas = ['Fecha del cambio', 'Nombre del cambio', 'Valor anterior', 'Valor nuevo', 'Tipo de cambio', 'Nombre de usuario']

        labelframe_tabla = tk.LabelFrame(
            seccion_informacion)
        labelframe_tabla.grid(
            column=0, row=2, padx=2, pady=2, sticky=tk.NW)

        # Crea un Treeview con una columna por cada campo de la tabla
        self.tabla = ttk.Treeview(
            labelframe_tabla, columns=columnas)
        self.tabla.config(height=10)
        self.tabla.grid(row=0, column=0, padx=2, pady=5, sticky='NSEW')

        # Define los encabezados de columna
        for i, columna in enumerate(columnas):
            self.tabla.heading(f'#{i+1}', text=columna)

        self.tabla.column('#0', width=0, stretch=False)
        self.tabla.column('#1', width=120, stretch=False)
        self.tabla.column('#2', width=120, stretch=False)
        self.tabla.column('#3', width=120, stretch=False)
        self.tabla.column('#4', width=120, stretch=False)
        self.tabla.column('#5', width=120, stretch=False)
        self.tabla.column('#6', width=120, stretch=False)

        # Crea un Scrollbar vertical y lo asocia con el Treeview
        scrollbar_Y = ttk.Scrollbar(
            labelframe_tabla, orient='vertical', command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar_Y.set)
        scrollbar_Y.grid(row=0, column=1, sticky='NS')

        # Crea un Scrollbar horizontal y lo asocia con el Treeview
        scrollbar_X = ttk.Scrollbar(
            labelframe_tabla, orient='horizontal', command=self.tabla.xview)
        self.tabla.configure(xscroll=scrollbar_X.set)
        scrollbar_X.grid(row=1, column=0, sticky='EW')
        
        labelframe_tabla.grid_rowconfigure(0, weight=1, minsize=0, maxsize=None)

    def get_changes(self):
        try:
            year_param = self.variable_años.get()
            month_param = self.lista_desplegable_meses.current() + 1

            cambios = self.model_cambios.get_list_changes(year_param, month_param)
            self.tabla.delete(*self.tabla.get_children())

            if len(cambios) ==0:
                raise SystemError("No hay registro de cambios para la fecha indicada.\n\nSi consideras que se trata de un error ponte en contacto con un administrador inmediatamente")
            else:
                for cambio in cambios:
                    self.tabla.insert('', 'end', values=cambio)

        except Exception as e:
            print(e)
            mb.showwarning("Error", e)


