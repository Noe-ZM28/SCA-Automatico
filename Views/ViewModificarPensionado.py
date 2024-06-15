from tkinter import filedialog
import qrcode
from tkinter import messagebox as mb
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
from datetime import datetime
import traceback
from escpos.printer import USBNotFoundError

from Models.Queries import Pensionados
from Controllers.ConfigController import ConfigController
from Controllers.PrinterController import PrinterController
from Tools.Tools import Tools


class View_modificar_pensionados():
    """Clase para mostrar la ventana de modificacion de datos de un pensionado."""

    def __init__(self, datos_pensionado):
        """
        Constructor de la clase. Inicializa la ventana y los atributos.

        Args:
            datos_pensionado (tuple): Tupla con los datos del pensionado a modificar.
        """
        instance_config = ConfigController()
        self.printer_controller = PrinterController()
        self.query = Pensionados()
        self.instance_tools = Tools()
        self.datos_pensionado = datos_pensionado

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
            f"Modificar pensionado -> {self.nombre_estacionamiento}")

        # Configura la columna principal del panel para que use todo el espacio disponible
        self.panel_crud.columnconfigure(0, weight=1)

        # Variables para almacenar los datos del pensionado
        self.variable_numero_tarjeta = StringVar()
        self.variable_numero_tarjeta.set(datos_pensionado[0][0])

        self.variable_nombre = StringVar()
        self.variable_nombre.set(datos_pensionado[0][1])

        self.variable_apellido_1 = StringVar()
        self.variable_apellido_1.set(datos_pensionado[0][2])

        self.variable_apellido_2 = StringVar()
        self.variable_apellido_2.set(datos_pensionado[0][3])

        self.variable_telefono_1 = StringVar()
        self.variable_telefono_1.set(datos_pensionado[0][4])

        self.variable_telefono_2 = StringVar()
        self.variable_telefono_2.set(datos_pensionado[0][5])

        self.variable_ciudad = StringVar()
        self.variable_ciudad.set(datos_pensionado[0][6])

        self.variable_colonia = StringVar()
        self.variable_colonia.set(datos_pensionado[0][7])

        self.variable_cp = StringVar()
        self.variable_cp.set(datos_pensionado[0][8])

        self.variable_numero_calle = StringVar()
        self.variable_numero_calle.set(datos_pensionado[0][9])

        self.variable_placas = StringVar()
        self.variable_placas.set(datos_pensionado[0][10])

        self.variable_auto_modelo = StringVar()
        self.variable_auto_modelo.set(datos_pensionado[0][11])

        self.variable_auto_color = StringVar()
        self.variable_auto_color.set(datos_pensionado[0][12])

        self.variable_monto = StringVar()
        self.variable_monto.set(datos_pensionado[0][13])

        self.variable_cortesia = StringVar()
        self.variable_cortesia.set(datos_pensionado[0][14])

        self.variable_tolerancia = StringVar()
        self.variable_tolerancia.set(datos_pensionado[0][15])

        self.variable_vigencia = StringVar()
        self.variable_vigencia.set(datos_pensionado[0][16])

        self.variable_estatus = StringVar()
        self.variable_estatus.set(datos_pensionado[0][17])

        self.registros = None

        # Llama a la funcion interface() que configura la interfaz gráfica
        self.interface()

        self.panel_crud.resizable(False, False)

        # Inicia el loop principal de la ventana
        self.panel_crud.mainloop()

    def interface(self):
        """ Crea la interfaz gráfica de la ventana de modificacion."""

        # Crear un Label Frame principal para la seccion superior
        seccion_superior = tk.Frame(self.panel_crud)
        seccion_superior.columnconfigure(1, weight=1)
        seccion_superior.propagate(True)
        seccion_superior.grid(row=0, column=0, sticky=tk.NSEW)

        # Se crea un Label Frame para la seccion de la conexion
        etiqueta_user = tk.Label(seccion_superior, font=self.font_tittle_system,
                                 text=f'Bienvenido\nIngresa los datos del pensionado a modificar')
        etiqueta_user.grid(row=0, column=0, padx=5, pady=5)

        seccion_datos_pensionado = tk.LabelFrame(
            seccion_superior)
        seccion_datos_pensionado.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.NW)

        seccion_datos_personales_pensionado = tk.LabelFrame(
            seccion_datos_pensionado, font=self.font_subtittle_system, text="Datos personales del pensionado")
        seccion_datos_personales_pensionado.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.NW)

        etiqueta_numero_tarjeta = tk.Label(
            seccion_datos_personales_pensionado, font=self.font, text='Número de tarjeta: ')
        etiqueta_numero_tarjeta.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.NW)
        self.campo_numero_tarjeta = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_numero_tarjeta, state="disabled")
        self.campo_numero_tarjeta.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_nombre_pensionado = tk.Label(
            seccion_datos_personales_pensionado, font=self.font, text='Nombre: ')
        etiqueta_nombre_pensionado.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_nombre_pensinado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_nombre)
        campo_nombre_pensinado.grid(row=1, column=1, padx=5, pady=5)

        etiqueta_apellido_1_pensionado = tk.Label(
            seccion_datos_personales_pensionado, font=self.font, text='Primer apellido: ')
        etiqueta_apellido_1_pensionado.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_apellido_1_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_apellido_1)
        campo_apellido_1_pensionado.grid(row=2, column=1, padx=5, pady=5)

        etiqueta_apellido_2_pensionado = tk.Label(
            seccion_datos_personales_pensionado, font=self.font, text='Segundo apellido: ')
        etiqueta_apellido_2_pensionado.grid(
            row=3, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_apellido_2_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_apellido_2)
        campo_apellido_2_pensionado.grid(row=3, column=1, padx=5, pady=5)

        etiqueta_telefono_1_pensionado = tk.Label(
            seccion_datos_personales_pensionado, font=self.font, text='Telefono 1: ')
        etiqueta_telefono_1_pensionado.grid(
            row=4, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_telefono_1_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_telefono_1)
        campo_telefono_1_pensionado.grid(row=4, column=1, padx=5, pady=5)

        etiqueta_telefono_2_pensionado = tk.Label(
            seccion_datos_personales_pensionado, font=self.font, text='Telefono 2: ')
        etiqueta_telefono_2_pensionado.grid(
            row=5, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_telefono_2_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_telefono_2)
        campo_telefono_2_pensionado.grid(row=5, column=1, padx=5, pady=5)

        etiqueta_ciudad_pensionado = tk.Label(
            seccion_datos_personales_pensionado, font=self.font, text='Ciudad: ')
        etiqueta_ciudad_pensionado.grid(
            row=7, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_ciudad_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_ciudad)
        campo_ciudad_pensionado.grid(row=7, column=1, padx=5, pady=5)

        etiqueta_colonia_pensionado = tk.Label(
            seccion_datos_personales_pensionado, font=self.font, text='Colonia: ')
        etiqueta_colonia_pensionado.grid(
            row=8, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_colonia_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_colonia)
        campo_colonia_pensionado.grid(row=8, column=1, padx=5, pady=5)

        etiqueta_CP_pensionado = tk.Label(
            seccion_datos_personales_pensionado, font=self.font, text='CP: ')
        etiqueta_CP_pensionado.grid(
            row=9, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_CP_pensionado = tk.Entry(
            seccion_datos_personales_pensionado, font=self.font, textvariable=self.variable_cp)
        campo_CP_pensionado.grid(row=9, column=1, padx=5, pady=5)

        etiqueta_numero_calle_pensionado = tk.Label(
            seccion_datos_personales_pensionado, font=self.font, text='Numero de calle: ')
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
            seccion_datos_auto_pensionado, font=self.font, text='Placa: ')
        etiqueta_placa_auto_pensionado.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_placa_auto_pensionado = tk.Entry(
            seccion_datos_auto_pensionado, font=self.font, textvariable=self.variable_placas)
        campo_placa_auto_pensionado.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_modelo_auto_pensionado = tk.Label(
            seccion_datos_auto_pensionado, font=self.font, text='Modelo: ')
        etiqueta_modelo_auto_pensionado.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_placa_modelo_pensionado = tk.Entry(
            seccion_datos_auto_pensionado, font=self.font, textvariable=self.variable_auto_modelo)
        campo_placa_modelo_pensionado.grid(row=1, column=1, padx=5, pady=5)

        etiqueta_color_auto_pensionado = tk.Label(
            seccion_datos_auto_pensionado, font=self.font, text='Color: ')
        etiqueta_color_auto_pensionado.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_color_auto_pensionado = tk.Entry(
            seccion_datos_auto_pensionado, font=self.font, textvariable=self.variable_auto_color)
        campo_color_auto_pensionado.grid(row=2, column=1, padx=5, pady=5)

        seccion_datos_pension = tk.LabelFrame(
            seccion_derecha, font=self.font_subtittle_system, text="Datos del cobro")
        seccion_datos_pension.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.NW)

        etiqueta_monto_dato_pension = tk.Label(
            seccion_datos_pension, font=self.font, text='Monto X Mes: ')
        etiqueta_monto_dato_pension.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.NW)
        campo_monto_dato_pension = tk.Entry(
            seccion_datos_pension, font=self.font, textvariable=self.variable_monto, validate='key', validatecommand=(self.panel_crud.register(self.instance_tools.validate_entry_number), '%P'))
        campo_monto_dato_pension.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_cortesia_dato_pension = tk.Label(
            seccion_datos_pension, font=self.font, text='Cortesia: ')
        etiqueta_cortesia_dato_pension.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.NW)

        campo_cortesia_dato_pension = ttk.Combobox(
            seccion_datos_pension, width=5, state="readonly", font=self.font, textvariable=self.variable_cortesia)
        campo_cortesia_dato_pension["values"] = ["Si", "No"]

        campo_cortesia_dato_pension.grid(
            row=1, column=1, padx=1, pady=1, sticky=tk.NW)

        etiqueta_tolerancia = tk.Label(
            seccion_datos_pension, font=self.font, text='Tolerancia: ')
        etiqueta_tolerancia.grid(row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        self.campo_tolerancia = tk.Entry(
            seccion_datos_pension, font=self.font, textvariable=self.variable_tolerancia, validate='key', validatecommand=(self.panel_crud.register(self.instance_tools.validate_entry_number), '%P'))
        self.campo_tolerancia.grid(row=2, column=1, padx=5, pady=5)

        seccion_datos_pension = tk.LabelFrame(
            seccion_derecha, font=self.font_subtittle_system, text="QR de Tarjeton/Corbata")
        seccion_datos_pension.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.NW)

        boton_generar_QR_pensionado = tk.Button(
            seccion_datos_pension,  text='Generar QR', font=self.font_botones_interface,
            command=self.print_QR,
            background=self.button_color, fg=self.button_letters_color, anchor="center", width=27)
        boton_generar_QR_pensionado.grid(row=5, column=0, padx=5, pady=5)

        seccion_inferior = tk.Frame(self.panel_crud)
        seccion_inferior.grid(row=1, column=0)

        # Crea un boton y lo empaqueta en la seccion_botones_consulta
        boton_modificar_pensionado = tk.Button(
            seccion_inferior, text='Desactivar tarjeta', font=self.font_botones_interface, command=self.desactivar_tarjeta, background=self.button_color, fg=self.button_letters_color, anchor="center", width=27)
        boton_modificar_pensionado.grid(row=0, column=0, padx=5, pady=5)

        # Crea un boton y lo empaqueta en la seccion_botones_consulta
        boton_modificar_pensionado = tk.Button(
            seccion_inferior, text='Guardar Cambios', font=self.font_botones_interface, command=self.modificar_pensionado, background=self.button_color, fg=self.button_letters_color, anchor="center", width=27)
        boton_modificar_pensionado.grid(row=0, column=1, padx=5, pady=5)

    def print_QR(self):
        try:
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

    def desactivar_tarjeta(self):
        """ Desactiva temporal o permanentemente la tarjeta del pensionado."""
        mensaje = ""
        respuesta = mb.askyesno(
            "Advertencia", "¿Estas seguro de querer desactivar esta tarjeta?")
        if respuesta:
            pass
        else:
            self.campo_tolerancia.focus()
            return

        vigencia = self.variable_vigencia.get()
        if vigencia == 'None':
            vigencia = None

        if vigencia == None:
            mb.showinfo(
                "Alerta", "La tarjeta ya esta desactivada, para reactivar la tarjeta es necesario realizar un pago de la pension para asignar nueva fecha de vigencia")
            self.campo_tolerancia.focus()
            return

        respuesta = mb.askyesno(
            "Advertencia", "¿La desactivacion es temporal?")

        if respuesta:
            self.variable_estatus.set("InactivaTemp")
            mensaje = "temporalmente"

        else:
            self.variable_estatus.set("InactivaPerm")
            mensaje = "permanentemente"

        if vigencia:
            self.variable_vigencia.set(None)
            mb.showinfo("Alerta", f"Se ha desactivado {mensaje} la tarjeta")
            self.modificar_pensionado()

    def modificar_pensionado(self):
        """ Modifica los datos del pensionado en la base de datos."""
        try:
            # Obtener los datos del formulario
            variable_numero_tarjeta = self.variable_numero_tarjeta.get()
            variable_nombre = self.variable_nombre.get()
            variable_apellido_1 = self.variable_apellido_1.get()
            variable_apellido_2 = self.variable_apellido_2.get()

            variable_telefono_1 = self.variable_telefono_1.get()
            variable_telefono_2 = self.variable_telefono_2.get()
            variable_ciudad = self.variable_ciudad.get()
            variable_colonia = self.variable_colonia.get()
            variable_cp = self.variable_cp.get()
            variable_numero_calle = self.variable_numero_calle.get()

            variable_placas = self.variable_placas.get()
            variable_auto_modelo = self.variable_auto_modelo.get()
            variable_auto_color = self.variable_auto_color.get()

            variable_monto = int(self.variable_monto.get())
            variable_cortesia = self.variable_cortesia.get()
            variable_tolerancia = self.variable_tolerancia.get()
            fecha_modificacion_pensionado = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            vigencia = self.variable_vigencia.get()
            if vigencia == "None":
                vigencia = None
            estatus = self.variable_estatus.get()

            if len(variable_numero_tarjeta) == 0 or len(variable_nombre) == 0 or len(variable_apellido_1) == 0 or len(variable_apellido_2) == 0 or len(variable_telefono_1) == 0 or len(variable_telefono_2) == 0 or len(variable_ciudad) == 0 or len(variable_colonia) == 0 or len(variable_cp) == 0 or len(variable_numero_calle) == 0 or len(variable_placas) == 0 or len(variable_auto_modelo) == 0 or len(variable_auto_color) == 0 or len(str(variable_monto)) == 0 or len(variable_cortesia) == 0 or variable_tolerancia == 0:
                raise IndexError("No dejar campos en blanco")

            if variable_cortesia == "No" and variable_monto == 0:
                raise IndexError("Ingrese el monto a pagar")
            if variable_cortesia == "Si":
                variable_monto = 0

            datos_pensionado = (variable_numero_tarjeta, variable_nombre, variable_apellido_1, variable_apellido_2, variable_telefono_1, variable_telefono_2, variable_ciudad, variable_colonia, variable_cp,
                                variable_numero_calle, variable_placas, variable_auto_modelo, variable_auto_color, variable_monto, variable_cortesia, variable_tolerancia, fecha_modificacion_pensionado, vigencia, estatus)

            self.query.actualizar_pensionado(
                datos_pensionado=datos_pensionado, Num_tarjeta=variable_numero_tarjeta)
            mb.showinfo("Informacion",
                        "El pensionado fue modificado correctamente")
            self.instance_tools.desconectar(self.panel_crud)

        except IndexError as e:
            traceback.print_exc()
            mb.showerror("Error", e)
        except ValueError as e:
            traceback.print_exc()
            mb.showerror("Error", e)
        except Exception as e:
            traceback.print_exc()
            mb.showerror("Error", e)
