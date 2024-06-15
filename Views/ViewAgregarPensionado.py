import qrcode
from escpos.printer import Usb, USBNotFoundError
from tkinter import messagebox as mb, ttk
import tkinter as tk
from tkinter import StringVar
from datetime import datetime
import traceback

from Models.Queries import Pensionados
from Controllers.ConfigController import ConfigController
from Controllers.PrinterController import PrinterController
from Tools.Tools import Tools


class View_agregar_pensionados:
    """Clase de la vista para agregar pensionados."""

    def __init__(self):
        """Inicializa una instancia de la clase ViewAgregarPensionados y crea la ventana principal de la interfaz."""
        instance_config = ConfigController()
        self.query = Pensionados()
        self.printer_controller = PrinterController()
        self.instance_tools = Tools()

        # Crea la ventana principal
        self.panel_crud = tk.Toplevel()
        data_config = instance_config.get_config("general")
        self.nombre_estacionamiento = data_config['informacion_estacionamiento']['nombre_estacionamiento']
        self.button_color = data_config["configuracion_sistema"]["color_botones_interface"]
        self.button_letters_color = data_config["configuracion_sistema"]["color_letra_botones_interface"]
        self.fuente_sistema = data_config["configuracion_sistema"]["fuente"]
        size_text_font = data_config["configuracion_sistema"]["size_text_font"]
        self.font = (self.fuente_sistema, size_text_font)

        self.size_text_font_tittle_system = data_config[
            "configuracion_sistema"]["size_text_font_tittle_system"]
        self.size_text_font_subtittle_system = data_config[
            "configuracion_sistema"]["size_text_font_subtittle_system"]
        self.size_text_button_font = data_config["configuracion_sistema"]["size_text_button_font"]

        self.font_subtittle_system = (
            self.fuente_sistema, self.size_text_font_subtittle_system, 'bold')
        self.font_tittle_system = (
            self.fuente_sistema, self.size_text_font_tittle_system, 'bold')
        self.font_botones_interface = (
            self.fuente_sistema, self.size_text_button_font, 'bold')

        # Se elimina la funcionalidad del boton de cerrar
        self.panel_crud.protocol(
            "WM_DELETE_WINDOW", lambda: self.instance_tools.desconectar(self.panel_crud))

        self.panel_crud.title(
            f"Agregar pensionado - {self.nombre_estacionamiento}")

        # Configura la columna principal del panel para que use todo el espacio disponible
        self.panel_crud.columnconfigure(0, weight=1)

        # Crea las variables para los datos del pensionado
        self.variable_numero_tarjeta = StringVar()
        self.variable_numero_tarjeta.set(self.query.get_QR_id())

        self.variable_nombre = StringVar()
        self.variable_apellido_1 = StringVar()
        self.variable_apellido_2 = StringVar()
        self.variable_fecha_alta = StringVar()
        self.variable_telefono_1 = StringVar()
        self.variable_telefono_2 = StringVar()
        self.variable_ciudad = StringVar()
        self.variable_colonia = StringVar()
        self.variable_cp = StringVar()
        self.variable_numero_calle = StringVar()

        self.variable_placas = StringVar()
        self.variable_auto_modelo = StringVar()
        self.variable_auto_color = StringVar()

        self.variable_monto = StringVar()
        self.variable_cortesia = StringVar()
        self.variable_tolerancia = StringVar()
        self.variable_tolerancia.set("5")

        self.__variable_es_reposicion = StringVar()

        self.registros = None

        # Llama a la funcion interface() que configura la interfaz gráfica
        self.interface()

        self.panel_crud.resizable(False, False)

        # Inicia el loop principal de la ventana
        self.panel_crud.mainloop()

    def interface(self):
        """Define la interfaz gráfica para agregar pensionados."""
        # Se crea un Label Frame principal para la seccion superior
        seccion_superior = tk.LabelFrame(self.panel_crud)
        seccion_superior.columnconfigure(1, weight=1)
        seccion_superior.propagate(True)
        seccion_superior.grid(row=0, column=0, sticky=tk.NSEW)

        # Se crea un Label Frame para la seccion de la conexion
        etiqueta_user = tk.Label(
            seccion_superior, text=f'Bienvenido', font=self.font_tittle_system)
        etiqueta_user.grid(row=0, column=0, padx=5, pady=5)

        seccion_tarjeta_reposicon = tk.Frame(seccion_superior)
        seccion_tarjeta_reposicon.grid(row=1, column=0)

        etiqueta_reposicion_info = tk.Label(
            seccion_tarjeta_reposicon, text='¿La tarjeta a registrar es de reposicion?: ', font=self.font_subtittle_system)
        etiqueta_reposicion_info.grid(row=0, column=0, padx=5, pady=5)

        campo_reposicion = ttk.Combobox(
            seccion_tarjeta_reposicon, width=5, state="readonly", textvariable=self.__variable_es_reposicion, font=self.font)
        campo_reposicion["values"] = ["Si", "No"]
        campo_reposicion.current(1)
        campo_reposicion.grid(row=0, column=1, padx=5, pady=5)

        seccion_datos_pensionado = tk.LabelFrame(
            seccion_superior, font=self.font_tittle_system, text="Ingresa los datos del pensionado a registrar")
        seccion_datos_pensionado.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.NW)

        seccion_datos_personales_pensionado = tk.LabelFrame(
            seccion_datos_pensionado, font=self.font_subtittle_system, text="Datos personales del pensionado")
        seccion_datos_personales_pensionado.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.NW)

        etiqueta_numero_tarjeta = tk.Label(
            seccion_datos_personales_pensionado, text='Número de tarjeta: ', font=self.font)
        etiqueta_numero_tarjeta.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.NW)
        self.campo_numero_tarjeta = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_numero_tarjeta, state='disabled')
        self.campo_numero_tarjeta.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_nombre_pensionado = tk.Label(
            seccion_datos_personales_pensionado, text='Nombre: ', font=self.font)
        etiqueta_nombre_pensionado.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_nombre_pensinado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_nombre)
        campo_nombre_pensinado.grid(row=1, column=1, padx=5, pady=5)

        etiqueta_apellido_1_pensionado = tk.Label(
            seccion_datos_personales_pensionado, text='Primer apellido: ', font=self.font)
        etiqueta_apellido_1_pensionado.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_apellido_1_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_apellido_1)
        campo_apellido_1_pensionado.grid(row=2, column=1, padx=5, pady=5)

        etiqueta_apellido_2_pensionado = tk.Label(
            seccion_datos_personales_pensionado, text='Segundo apellido: ', font=self.font)
        etiqueta_apellido_2_pensionado.grid(
            row=3, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_apellido_2_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_apellido_2)
        campo_apellido_2_pensionado.grid(row=3, column=1, padx=5, pady=5)

        etiqueta_telefono_1_pensionado = tk.Label(
            seccion_datos_personales_pensionado, text='Telefono 1: ', font=self.font)
        etiqueta_telefono_1_pensionado.grid(
            row=4, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_telefono_1_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_telefono_1)
        campo_telefono_1_pensionado.grid(row=4, column=1, padx=5, pady=5)

        etiqueta_telefono_2_pensionado = tk.Label(
            seccion_datos_personales_pensionado, text='Telefono 2: ', font=self.font)
        etiqueta_telefono_2_pensionado.grid(
            row=5, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_telefono_2_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_telefono_2)
        campo_telefono_2_pensionado.grid(row=5, column=1, padx=5, pady=5)

        etiqueta_ciudad_pensionado = tk.Label(
            seccion_datos_personales_pensionado, text='Ciudad: ', font=self.font)
        etiqueta_ciudad_pensionado.grid(
            row=7, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_ciudad_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_ciudad)
        campo_ciudad_pensionado.grid(row=7, column=1, padx=5, pady=5)

        etiqueta_colonia_pensionado = tk.Label(
            seccion_datos_personales_pensionado, text='Colonia: ', font=self.font)
        etiqueta_colonia_pensionado.grid(
            row=8, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_colonia_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_colonia)
        campo_colonia_pensionado.grid(row=8, column=1, padx=5, pady=5)

        etiqueta_CP_pensionado = tk.Label(
            seccion_datos_personales_pensionado, text='CP: ', font=self.font)
        etiqueta_CP_pensionado.grid(
            row=9, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_CP_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_cp)
        campo_CP_pensionado.grid(row=9, column=1, padx=5, pady=5)

        etiqueta_numero_calle_pensionado = tk.Label(
            seccion_datos_personales_pensionado, text='Numero de calle: ', font=self.font)
        etiqueta_numero_calle_pensionado.grid(
            row=10, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_numero_calle_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_numero_calle)
        campo_numero_calle_pensionado.grid(row=10, column=1, padx=5, pady=5)

        seccion_derecha = tk.Frame(seccion_datos_pensionado)
        seccion_derecha.grid(row=2, column=1, padx=5, pady=5, sticky=tk.NW)

        seccion_datos_auto_pensionado = tk.LabelFrame(
            seccion_derecha, font=self.font_subtittle_system, text="Datos del auto del pensionado")
        seccion_datos_auto_pensionado.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.NW)

        etiqueta_placa_auto_pensionado = tk.Label(
            seccion_datos_auto_pensionado, text='Placa: ', font=self.font)
        etiqueta_placa_auto_pensionado.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_placa_auto_pensionado = tk.Entry(
            seccion_datos_auto_pensionado, font=self.font, textvariable=self.variable_placas)
        campo_placa_auto_pensionado.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_modelo_auto_pensionado = tk.Label(
            seccion_datos_auto_pensionado, text='Modelo: ', font=self.font)
        etiqueta_modelo_auto_pensionado.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_placa_modelo_pensionado = tk.Entry(
            seccion_datos_auto_pensionado, font=self.font, textvariable=self.variable_auto_modelo)
        campo_placa_modelo_pensionado.grid(row=1, column=1, padx=5, pady=5)

        etiqueta_color_auto_pensionado = tk.Label(
            seccion_datos_auto_pensionado, text='Color: ', font=self.font)
        etiqueta_color_auto_pensionado.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_color_auto_pensionado = tk.Entry(
            seccion_datos_auto_pensionado, font=self.font, textvariable=self.variable_auto_color)
        campo_color_auto_pensionado.grid(row=2, column=1, padx=5, pady=5)

        seccion_datos_pension = tk.LabelFrame(
            seccion_derecha, font=self.font_subtittle_system, text="Datos de cobro de la pension")
        seccion_datos_pension.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.NW)

        etiqueta_monto_dato_pension = tk.Label(
            seccion_datos_pension, text='Monto X Mes: ', font=self.font)
        etiqueta_monto_dato_pension.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.NW)
        self.campo_monto_dato_pension = tk.Entry(
            seccion_datos_pension, font=self.font, textvariable=self.variable_monto, validate='key', validatecommand=(self.panel_crud.register(self.instance_tools.validate_entry_number), '%P'))
        self.campo_monto_dato_pension.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_cortesia_dato_pension = tk.Label(
            seccion_datos_pension, text='Cortesia: ', font=self.font)
        etiqueta_cortesia_dato_pension.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.NW)

        campo_cortesia_dato_pension = ttk.Combobox(
            seccion_datos_pension, width=5, state="readonly", font=self.font, textvariable=self.variable_cortesia)
        campo_cortesia_dato_pension["values"] = ["Si", "No"]
        campo_cortesia_dato_pension.current(1)
        campo_cortesia_dato_pension.grid(
            row=1, column=1, padx=1, pady=1, sticky=tk.NW)

        etiqueta_color_auto_pensionado = tk.Label(
            seccion_datos_pension, text='Tolerancia: ', font=self.font)
        etiqueta_color_auto_pensionado.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_color_auto_pensionado = tk.Entry(
            seccion_datos_pension, font=self.font, textvariable=self.variable_tolerancia, validate='key', validatecommand=(self.panel_crud.register(self.instance_tools.validate_entry_number), '%P'))
        campo_color_auto_pensionado.grid(row=2, column=1, padx=5, pady=5)

        # Crea un boton y lo empaqueta en la seccion_botones_consulta
        boton_agregar_pensionado = tk.Button(
            self.panel_crud, background=self.button_color, fg=self.button_letters_color, text="Agregar Pensionado", anchor="center", font=self.font_botones_interface, width=27, command=self.agregar_pensionado)
        boton_agregar_pensionado.grid(row=5, column=0, padx=5, pady=5)

        self.campo_numero_tarjeta.focus()

    def agregar_pensionado(self):
        """Agrega un nuevo pensionado con los datos ingresados."""
        try:
            pensionado_fecha_alta = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            variable_numero_tarjeta = self.variable_numero_tarjeta.get()
            variable_nombre = self.variable_nombre.get()
            variable_apellido_1 = self.variable_apellido_1.get()
            variable_apellido_2 = self.variable_apellido_2.get()
            variable_fecha_alta = pensionado_fecha_alta
            variable_telefono_1 = self.variable_telefono_1.get()
            variable_telefono_2 = self.variable_telefono_2.get()
            variable_ciudad = self.variable_ciudad.get()
            variable_colonia = self.variable_colonia.get()
            variable_cp = self.variable_cp.get()
            variable_numero_calle = self.variable_numero_calle.get()

            variable_placas = self.variable_placas.get()
            variable_auto_modelo = self.variable_auto_modelo.get()
            variable_auto_color = self.variable_auto_color.get()

            variable_monto = self.variable_monto.get()
            variable_cortesia = self.variable_cortesia.get()
            variable_tolerancia = self.variable_tolerancia.get()
            variable_estatus = "Inactiva"

            try:
                variable_monto = int(variable_monto)

            except Exception as e:
                traceback.print_exc()
                mb.showerror("Error", "Ingresa un monto valido")
                self.campo_monto_dato_pension.focus()
                return

            if self.__variable_es_reposicion.get() == "Si":
                respuesta = mb.askyesno(
                    "Advertencia", "¿Estas seguro de que la tarjeta registrada es de reposicion? De ser asi no olvides desactivar la antigua tarjeta")
                variable_estatus = "Reposicion"
                if respuesta is False:
                    return

            if len(variable_nombre) == 0 or len(variable_apellido_1) == 0 or len(variable_apellido_2) == 0 or len(variable_fecha_alta) == 0 or len(variable_telefono_1) == 0 or len(variable_telefono_2) == 0 or len(variable_ciudad) == 0 or len(variable_colonia) == 0 or len(variable_cp) == 0 or len(variable_numero_calle) == 0 or len(variable_placas) == 0 or len(variable_auto_modelo) == 0 or len(variable_auto_color) == 0 or len(variable_cortesia) == 0 or len(str(variable_tolerancia)) == 0:
                raise IndexError("No dejar campos en blanco")

            if variable_cortesia == "No" and variable_monto == 0:
                raise TypeError("Ingrese el monto a pagar")
            if variable_cortesia == "Si":
                variable_monto = 0

            if int(variable_tolerancia) == 0:
                raise TypeError("Ingrese una tolerancia valida")

            datos_pensionado = (variable_numero_tarjeta, variable_nombre, variable_apellido_1, variable_apellido_2, variable_fecha_alta, variable_telefono_1, variable_telefono_2, variable_ciudad,
                                variable_colonia, variable_cp, variable_numero_calle, variable_placas, variable_auto_modelo, variable_auto_color, variable_monto, variable_cortesia, variable_tolerancia, variable_estatus)

            resultado = self.query.consultar_pensionado(
                variable_numero_tarjeta)

            if len(resultado) > 0:
                self.variable_numero_tarjeta.set('')
                self.campo_numero_tarjeta.focus()
                raise SystemError(
                    "Ya existe un pensionado registrado con ese numero de tarjeta")

            self.query.agregar_pensionados(datos_pensionado)

            self.instance_tools.desconectar(self.panel_crud)
            mb.showinfo(
                "Informacion", "El pensionado fue añadido correctamente, realice su pago de pension para activar la tarjeta")

            state = self.printer_controller.print_QR_pension(
                self.variable_numero_tarjeta.get(),
                self.variable_placas.get(),
                self.variable_nombre.get(),
                self.variable_auto_modelo.get())

            if state is not None:
                raise SystemError(state)

        except Exception as e:
            mb.showerror("Error", e)
            return
