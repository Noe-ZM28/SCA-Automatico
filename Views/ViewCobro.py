from datetime import datetime
from escpos.printer import Usb as Printer, USBNotFoundError
from usb.core import NoBackendError

import tkinter as tk
from tkinter import ttk, messagebox as mb, scrolledtext as st, simpledialog, TclError
import xlsxwriter
from time import sleep
from threading import Thread
from os import path, listdir
import locale
from platform import system

from .ViewReloj import RelojAnalogico
from .ViewAgregarPensionado import View_agregar_pensionados
from .ViewModificarPensionado import View_modificar_pensionados
from .ViewLoginPanelUsuarios import View_Login as login_panel_usuarios
from .ViewLoginPanelConfig import View_Login as login_panel_config
from .ViewPaidPension import ViewPaidPension
from Tools.Tools import Tools
from Tools.Security import ask_security_question
from Tools.Exceptions import WithoutParameter, SystemError, NotExist
from Models.Queries import Pensionados
from Models.Model import Operacion
from Controllers.ConfigController import ConfigController
from Controllers.CobroController import CobroController
from Controllers.EmailController import SendData
from Controllers.PrinterController import PrinterController


class ViewCobro:
    def __init__(self) -> None:
        locale_time = 'es_ES' if system() == "Windows" else 'es_MX.utf8'
        locale.setlocale(locale.LC_TIME, locale_time)

        self.send_data_controller = SendData()
        self.instance_config = ConfigController()
        self.instance_cobro_controller = CobroController()
        self.printer_controller = PrinterController()
        self.instance_tools = Tools()
        self.controlador_crud_pensionados = Pensionados()
        self.DB = Operacion()
        self.root = tk.Tk()
        # Establece que la ventana no sea redimensionable
        self.root.resizable(False, False)
        self.get_config_data()

        # Se elimina la funcionalidad del boton de cerrar
        self.root.protocol(
            "WM_DELETE_WINDOW", self.Cerrar_Programa)


        self.folio_auxiliar = None

        self.root.title(f"{self.nombre_estacionamiento} COBRO")

        if self.pantalla_completa:
            # Obtener el ancho y alto de la pantalla
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Configura la ventana para que ocupe toda la pantalla
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Colocar el LabelFrame en las coordenadas calculadas
        principal = tk.LabelFrame(self.root)
        principal.pack(expand=True, padx=3, pady=3, anchor='n')

        self.cuaderno_modulos = ttk.Notebook(principal)
        # Asociar el evento <<NotebookTabChanged>> a la funcion on_tab_changed
        self.cuaderno_modulos.bind(
            "<<NotebookTabChanged>>", self.on_tab_changed)

        self.cuaderno_modulos.config(cursor="")         # Tipo de cursor
        self.modulo_expedir_boletos()
        self.check_inputs()
        self.modulo_cobro()
        self.modulo_corte()
        self.modulo_pensionados()
        self.cuaderno_modulos.grid(
            column=0, row=0, padx=2, pady=5)
        if self.show_clock:
            self.reloj = RelojAnalogico()

        self.root.mainloop()

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
            self.date_format_clock = formatos_fecha[data_config["formato_hora_reloj_expedidor_boleto"]]

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

            # Configuracion de la impresora
            self.printer_idVendor = self.instance_tools.text_to_hexanumber(
                data_config["impresora"]["idVendor"])
            self.printer_idProduct = self.instance_tools.text_to_hexanumber(
                data_config["impresora"]["idProduct"])

            # Otras configuraciones generales
            self.requiere_placa = data_config["requiere_placa"]
            self.penalizacion_con_importe = data_config["penalizacion_boleto_perdido"]
            self.show_clock = data_config["reloj"]
            self.envio_informacion = data_config["envio_informacion"]
            self.pantalla_completa = data_config["pantalla_completa"]
            self.habilita_impresion_boleto_perdido = data_config["habilita_impresion_boleto_perdido"]

            self.imprime_contra_parabrisas = data_config["imprime_contra_parabrisas"]
            self.imprime_contra_localizacion = data_config["imprime_contra_localizacion"]
            self.solicita_datos_del_auto = data_config["solicita_datos_del_auto"]

            # Configuracion para pensionados
            data_config = self.instance_config.get_config(
                "general", "configuracion_pensionados")
            self.__contraseña_pensionados__ = data_config["password"]
            self.__iv_pensionados__ = data_config["iv"]
            self.valor_tarjeta = data_config["costo_tarjeta"]
            self.valor_reposicion_tarjeta = data_config["costo_reposicion_tarjeta"]
            self.penalizacion_diaria_pension = data_config["penalizacion_diaria"]

            # Configuracion de imagenes
            data_config = self.instance_config.get_config(
                "general", "imagenes")
            self.logo_empresa = data_config["path_logo_boleto"]
            self.imagen_marcas_auto = data_config["path_marcas_auto"]

            size = (size_text_font+10, size_text_font+10)
            self.config_icon = self.instance_tools.get_icon(
                data_config["config_icon"], size)
            self.users_icon = self.instance_tools.get_icon(
                data_config["users_icon"], size)

            size = (size_text_font+20, size_text_font+5)
            self.hide_password_icon = self.instance_tools.get_icon(
                data_config["hide_password_icon"], size)
            self.show_password_icon = self.instance_tools.get_icon(
                data_config["show_password_icon"], size)

            # Configuracion de tarifas
            data_config = self.instance_config.get_config("tarifa")

            self.tipo_tarifa_sistema = data_config["tipo_tarifa_sistema"]
            self.tarifa_boleto_perdido = data_config["tarifa_boleto_perdido"]

            self.tarifa_1_fraccion = data_config["tarifa_simple"]["tarifa_1_fraccion"]
            self.tarifa_2_fraccion = data_config["tarifa_simple"]["tarifa_2_fraccion"]
            self.tarifa_3_fraccion = data_config["tarifa_simple"]["tarifa_3_fraccion"]
            self.tarifa_hora = data_config["tarifa_simple"]["tarifa_hora"]

            self.inicio_cobro_fraccion = data_config["tarifa_simple"]["inicio_cobro_fraccion"]

            self.importe_dia_completo_tarifa_personalizada = data_config[
                "tarifa_personalizada"]["24"]["hora"]

            data_config = None
            self.fecha_interna_entrada = None
            self.fecha_interna_salida = None

        except Exception as e:
            mb.showerror(
                "Error", f"Error al cargar configuracion, inicie de nuevo el sistema.\n\nEn caso de que el error continue contacte a un administrador inmediatamente y muestre el siguiente error:\n\n\n{e}")
            raise SystemExit()

    def send_all_data(self):
        try:
            # Ejecutar la funcion para enviar los correos electronicos
            message_send_database = self.send_data_controller.send_database()
            message_send_corte = self.send_data_controller.send_corte()

            state = self.printer_controller.print_state_send_data(message_send_database, message_send_corte)

            if state != None:
                mb.showwarning("Alerta", state)
                return

        except Exception as e:
            print(e)

    def modulo_expedir_boletos(self) -> None:
        """
        Crea el modulo de expedicion de boletos en la interfaz gráfica.

        Este modulo incluye elementos como la bienvenida, la entrada de datos del cliente, la generacion de entrada,
        informacion sobre el folio, y un reloj.

        No retorna ningún valor.

        :return: None
        """
        # Crear un frame principal para el modulo
        seccion_expedir_boletos = tk.Frame(self.cuaderno_modulos)

        self.cuaderno_modulos.add(
            seccion_expedir_boletos, text="Expedir Boleto")

        seccion_expedir_boletos = tk.LabelFrame(seccion_expedir_boletos)
        seccion_expedir_boletos.pack(
            expand=True, padx=5, pady=5, anchor='center')

        # Seccion de bienvenida
        frame_bienvenida = tk.Frame(seccion_expedir_boletos)
        frame_bienvenida.grid(
            column=0, row=0, padx=2, pady=2)

        label_entrada = tk.Label(
            frame_bienvenida, text=f"Bienvenido(a) al estacionamiento {self.nombre_estacionamiento}", font=self.font_bienvenida, justify='center')
        label_entrada.grid(
            row=0, column=0)

        # Seccion de entrada de datos del cliente
        frame_datos_entrada = tk.Frame(seccion_expedir_boletos)
        frame_datos_entrada.grid(
            column=0, row=1, padx=2, pady=2)

        frame_info_placa = tk.Frame(frame_datos_entrada)
        frame_info_placa.grid(
            column=0, row=0, padx=2, pady=2)

        label_placa = tk.Label(
            frame_info_placa, text="Ingrese Placa", font=self.font_bienvenida)
        label_placa.grid(
            column=0, row=0, padx=2, pady=2)

        # Entrada para la placa
        self.Placa = tk.StringVar()
        self.entry_placa = tk.Entry(
            frame_info_placa, width=20, textvariable=self.Placa, font=self.font_entry_placa, justify='center')
        self.entry_placa.bind(
            '<Return>', self.Pensionados)
        self.entry_placa.grid(
            column=0, row=1, padx=2, pady=2)

        # Seccion de botones
        frame_boton = tk.Frame(frame_datos_entrada)
        frame_boton.grid(
            column=2, row=0, padx=2, pady=2)

        # Seccion de folio
        frame_folio = tk.Frame(frame_boton)
        frame_folio.grid(
            column=0, row=0, padx=2, pady=2)

        label_folio = tk.Label(
            frame_folio, text="Folio", font=self.font_entrada)
        label_folio.grid(
            column=0, row=0, padx=2, pady=2, sticky="nsew")

        # Entrada para el folio
        self.MaxId = tk.StringVar()
        entryMaxId = ttk.Entry(
            frame_folio, width=12, textvariable=self.MaxId, state="readonly", justify='center', font=self.font_entrada)
        entryMaxId.grid(
            column=1, row=0, padx=2, pady=2, sticky=tk.NW)

        # Boton para generar entrada
        boton_entrada = tk.Button(frame_boton, text="Generar Entrada", height=3, anchor="center",
                                  background=self.button_color, fg=self.button_letters_color, font=self.font_entrada_negritas, command=self.generar_boleto)
        boton_entrada.grid(
            column=0, row=1, padx=2, pady=2)

        # Seccion de informacion
        frame_info = tk.LabelFrame(seccion_expedir_boletos)
        frame_info.grid(
            column=0, row=2, padx=2, pady=2)

        # Etiqueta para mostrar informacion
        self.label_informacion = tk.Label(
            frame_info, text="... ", width=25, font=self.font_mensaje, justify='center')
        self.label_informacion.grid(
            column=0, row=0, padx=2, pady=2)

        # Seccion de reloj
        frame_reloj = tk.Frame(seccion_expedir_boletos)
        frame_reloj.grid(
            column=0, row=3, padx=2, pady=2)

        # Etiqueta para mostrar el reloj
        self.Reloj = tk.Label(
            frame_reloj, text="Reloj", background="white", font=self.font_reloj, justify='center')
        self.Reloj.grid(
            column=0, row=0, padx=2, pady=2)

        # Establecer el foco en la entrada de la placa
        self.entry_placa.focus()

    def check_inputs(self) -> None:
        """
        Funcion para actualizar periodicamente la fecha y hora en la interfaz.

        Esta funcion utiliza la etiqueta Reloj para mostrar la fecha y hora actuales y se llama a si misma
        utilizando el metodo after para actualizar continuamente la hora en la interfaz.

        :return: None
        """
        # Obtener la fecha y hora actual
        fecha_hora = datetime.now().strftime(self.date_format_clock)

        # Configurar la etiqueta Reloj con la fecha y hora actuales
        self.Reloj.config(text=fecha_hora)

        # Llamar a la funcion check_inputs despues de 60 milisegundos (1 minuto)
        self.root.after(60, self.check_inputs)

    def generar_boleto(self):
        try:
            # Obtener la placa del vehiculo desde la variable Placa
            placa = self.Placa.get()

            # Validar si se requiere una placa y si no se ingreso ninguna
            if not placa and self.requiere_placa:
                raise WithoutParameter("Placa del auto")

            folio_boleto = self.DB.MaxfolioEntrada() + 1
            self.MaxId.set(folio_boleto)

            state = self.printer_controller.print_ticket(folio_boleto, placa)

            if state != None:
                mb.showwarning("Alerta", state)
                state = ""
                return

            state=f"Se genera boleto"
            self.BoletoDentro()

        except Exception as e:
            state=e

        finally:
            self.label_informacion.config(text=state)
            self.entry_placa.focus()
            self.Placa.set("")

    def modulo_cobro(self) -> None:
        """
        Configura y muestra el modulo de cobro en la interfaz gráfica.

        Este metodo configura y organiza diferentes elementos de la interfaz de usuario
        relacionados con el modulo de cobro, como lectura de QR, informacion de promociones,
        datos de cobro y boletos perdidos o dañados.

        :return: None
        """
        self.modulo_cobro = tk.Frame(self.cuaderno_modulos)
        self.cuaderno_modulos.add(self.modulo_cobro, text="Modulo de Cobro")

        self.modulo_cobro = tk.LabelFrame(self.modulo_cobro)
        self.modulo_cobro.pack(expand=True, padx=5, pady=5, anchor='n')

        self.FOLIO_QR = tk.Frame(self.modulo_cobro)
        self.FOLIO_QR.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.NW)

        labelframe_leer_qr = tk.LabelFrame(
            self.FOLIO_QR, text="Cobro de boleto", font=self.font_tittle_system)
        labelframe_leer_qr.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.NW)

        # se crea objeto para ver pedir el folio la etiqueta con texto
        label1 = tk.Label(labelframe_leer_qr, text="Lector QR",
                          font=self.font_text_entry_interface)
        label1.grid(
            column=0, row=0, padx=2, pady=2)
        self.folio = tk.StringVar()
        self.entryfolio = tk.Entry(
            labelframe_leer_qr, textvariable=self.folio, justify='center', font=self.font_text_interface, width=17)
        # con esto se lee automatico y se va a consultar
        self.entryfolio.bind('<Return>', self.consultar)
        self.entryfolio.grid(
            column=1, row=0, padx=2, pady=2)

        label = tk.Label(labelframe_leer_qr, text="Entro",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=1, padx=2, pady=2)
        # se crea objeto para mostrar el dato de la  Entrada solo lectura
        self.fecha_entrada = tk.StringVar()
        entry_fecha_entrada = ttk.Entry(
            labelframe_leer_qr, textvariable=self.fecha_entrada, state="readonly", justify='center', font=self.font_text_interface, width=17)
        entry_fecha_entrada.grid(
            column=1, row=1, padx=2, pady=2, sticky=tk.NW)

        label = tk.Label(labelframe_leer_qr, text="Salio",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=2, padx=2, pady=2)
        # se crea objeto para mostrar el dato la Salida solo lectura
        self.fecha_salida = tk.StringVar()
        entry_fecha_salida = ttk.Entry(
            labelframe_leer_qr, textvariable=self.fecha_salida, state="readonly", justify='center', font=self.font_text_interface, width=17)
        entry_fecha_salida.grid(
            column=1, row=2, padx=2, pady=2, sticky=tk.NW)

        labelframe_promociones = tk.LabelFrame(
            self.FOLIO_QR, text="Promociones", font=self.font_tittle_system)
        labelframe_promociones.grid(
            column=0, row=1, padx=2, pady=2, sticky=tk.NW)

        self.labelframe_promocion_qr = tk.LabelFrame(
            labelframe_promociones, text="Aplicar promocion de QR", font=self.font_subtittle_system)
        self.labelframe_promocion_qr.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.NW)

        self.promolbl1 = tk.Label(
            self.labelframe_promocion_qr, text="Codigo QR", font=self.font_text_entry_interface)
        self.promolbl1.grid(
            column=0, row=0, padx=2, pady=2)
        # creamos un objeto para obtener la lectura de la PROMOCION
        self.promo = tk.StringVar()
        self.entrypromo = tk.Entry(
            self.labelframe_promocion_qr, textvariable=self.promo, justify='center', font=self.font_text_interface, width=16)
        # con esto se lee automatico
        self.entrypromo.bind('<Return>', self.aplicar_promocion_qr)
        self.entrypromo.grid(
            column=1, row=0, padx=2, pady=2)

        # este es donde pongo el tipo de PROMOCION
        self.promo_auxiliar = tk.StringVar()
        self.TarifaPreferente = tk.StringVar()
        self.entryTarifaPreferente = tk.Entry(
            self.labelframe_promocion_qr, textvariable=self.TarifaPreferente, state="readonly", justify='center', font=self.font_text_interface, width=16)
        self.entryTarifaPreferente.grid(
            column=1, row=1, padx=2, pady=2)

        labelframe_promo_botones = tk.LabelFrame(
            labelframe_promociones, text="Aplicar promocion de boton", font=self.font_subtittle_system)
        labelframe_promo_botones.grid(
            column=0, row=1, padx=2, pady=2)

        textos_botones = self.instance_config.get_promo_list("boton")
        # textos_botones = [f"Promo {i+1}" for i in range(5)]

        canvas = tk.Canvas(labelframe_promo_botones)
        canvas.grid(row=0, column=0)

        scrollbar = ttk.Scrollbar(
            labelframe_promo_botones, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        canvas.configure(yscrollcommand=scrollbar.set)

        content_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)

        self.boton1 = tk.Button(content_frame, width=10, height=2, font=self.font_botones_interface)

        for i in range(0, len(textos_botones), 2):
            self.boton1 = tk.Button(
                content_frame, text=textos_botones[i], width=10, height=2, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
            self.boton1.configure(command=lambda b=self.boton1: aplicar_promo(b))
            self.boton1.grid(
                column=0, row=i, padx=2, pady=2)

            if i + 1 < len(textos_botones):
                boton2 = tk.Button(
                    content_frame, text=textos_botones[i + 1], width=10, height=2, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
                boton2.configure(command=lambda b=boton2: aplicar_promo(b))
                boton2.grid(
                    column=1, row=i, padx=2, pady=2)

        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Establecer tamaño minimo para el Canvas
        canvas.update_idletasks()
        canvas.config(width=max(content_frame.winfo_reqwidth(),
                      200), height=self.boton1.winfo_height()*2.5)

        def on_scroll(event):
            if len(textos_botones) > 4:
                canvas.yview_scroll(-1 * (event.delta // 120), "units")

        def on_enter(event):
            canvas.bind_all("<MouseWheel>", on_scroll)

        def on_leave(event):
            canvas.unbind_all("<MouseWheel>")

        content_frame.bind("<Enter>", on_enter)
        content_frame.bind("<Leave>", on_leave)

        def aplicar_promo(button: tk.Button):
            self.aplicar_promocion_boton(button.cget('text'))

        # en otro frame
        labelframe_info_cobro = tk.LabelFrame(
            self.modulo_cobro, text="Datos de cobro de boleto", font=self.font_tittle_system)
        labelframe_info_cobro.grid(
            column=1, row=0, padx=2, pady=2, sticky=tk.NW)

        self.labelframe3 = tk.LabelFrame(
            labelframe_info_cobro, text="Tiempo y salida", font=self.font_subtittle_system)
        self.labelframe3.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.NW)

        labelframe_info_salida = tk.Frame(self.labelframe3)
        labelframe_info_salida.grid(
            column=0, row=0, padx=0, pady=0, sticky=tk.NW)

        label = tk.Label(labelframe_info_salida, text="Hora Salida",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=0, padx=2, pady=2)
        self.copia_fecha_salida = tk.StringVar()
        self.entry_copia_fecha_salida = tk.Entry(
            labelframe_info_salida, textvariable=self.copia_fecha_salida, state="readonly", justify='center', font=self.font_text_interface, width=17)
        self.entry_copia_fecha_salida.grid(
            column=1, row=0)

        label = tk.Label(labelframe_info_salida, text="TiempoTotal",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=1, padx=2, pady=2)
        self.TiempoTotal = tk.StringVar()
        self.TiempoTotal_auxiliar = tk.StringVar()
        self.entryTiempoTotal = tk.Entry(
            labelframe_info_salida, textvariable=self.TiempoTotal_auxiliar, state="readonly", justify='center', font=self.font_text_interface, width=17)
        self.entryTiempoTotal.grid(
            column=1, row=1)

        label = tk.Label(labelframe_info_salida, text="Importe",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=2, padx=2, pady=2)

        self.importe = tk.IntVar()

        self.label_show_importe = tk.Label(
            labelframe_info_salida, text="")
        self.label_show_importe.config(
            width=4, background="white", font=self.font_view_importe)
        self.label_show_importe.grid(
            column=1, row=2, padx=3, pady=3)

        labelframe_info_cobro_boleto = tk.LabelFrame(
            labelframe_info_cobro, text='Datos de pago', font=self.font_subtittle_system)
        labelframe_info_cobro_boleto.grid(
            column=0, row=2, padx=2, pady=2, sticky=tk.NW)

        frame_info_pago = tk.Frame(
            labelframe_info_cobro_boleto)
        frame_info_pago.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.NW)

        label = tk.Label(
            frame_info_pago, text="Cantidad entregada", font=self.font_text_entry_interface)
        label.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.NW)
        self.cuantopagasen = tk.IntVar(value=100)
        entry_info_cantidad_entregada = tk.Entry(
            frame_info_pago, width=11, textvariable=self.cuantopagasen, justify='center', font=self.font_text_interface)
        entry_info_cantidad_entregada.grid(
            column=1, row=0, sticky=tk.NW)

        label = tk.Label(frame_info_pago, text="El importe",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=1, padx=2, pady=2, sticky=tk.NW)
        self.elimportees = tk.IntVar()
        self.entryelimportees = tk.Entry(
            frame_info_pago, width=11, textvariable=self.elimportees, state="readonly", justify='center', font=self.font_text_interface)
        self.entryelimportees.grid(
            column=1, row=1, sticky=tk.NW)

        label = tk.Label(frame_info_pago, text="El cambio",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=2, padx=2, pady=2, sticky=tk.NW)
        self.elcambioes = tk.IntVar()
        self.entryelcambioes = tk.Entry(
            frame_info_pago, width=11, textvariable=self.elcambioes, state="readonly", justify='center', font=self.font_text_interface)
        self.entryelcambioes.grid(
            column=1, row=2, sticky=tk.NW)

        bcambio = tk.Button(
            labelframe_info_cobro_boleto, text="Cobrar boleto", command=self.calcular_cambio, height=2, anchor="center", background=self.button_color_cobro, fg=self.button_letters_color_cobro, font=self.font_botones_interface)
        bcambio.grid(
            column=0, row=1, padx=5, pady=5)

        self.label15 = tk.Label(
            labelframe_info_cobro, text="Viabilidad de cobro", font=self.font_text_interface)
        self.label15.grid(
            column=0, row=3, padx=3, pady=3)

        self.labelPerdido_principal = tk.LabelFrame(
            self.modulo_cobro, text="Boletos Dañados/Perdidos", font=self.font_tittle_system)
        self.labelPerdido_principal.grid(
            column=2, row=0, padx=0, pady=0, sticky=tk.NW)

        self.labelPerdido = tk.Frame(
            self.labelPerdido_principal)
        self.labelPerdido.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.NW)

        self.label_frame_folio = tk.Frame(
            self.labelPerdido)
        self.label_frame_folio.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.NW)

        self.lblFOLIO = tk.Label(
            self.label_frame_folio, text="Ingrese folio", font=self.font_subtittle_system)
        self.lblFOLIO.grid(
            column=0, row=0, sticky=tk.NW, padx=2, pady=2)

        self.PonerFOLIO = tk.StringVar()
        self.entryPonerFOLIO = tk.Entry(
            self.label_frame_folio, width=17, textvariable=self.PonerFOLIO, font=self.font_text_interface, justify='center')
        self.entryPonerFOLIO.grid(
            column=1, row=0, sticky=tk.NW, padx=2, pady=5)

        self.label_botones_boletos_perdido = tk.LabelFrame(
            self.labelPerdido_principal, text="Boleto dañado o perdido", font=self.font_subtittle_system)
        self.label_botones_boletos_perdido.grid(
            column=0, row=1, padx=2, pady=2, sticky=tk.NW)

        self.boton_boleto_dañado = tk.Button(
            self.label_botones_boletos_perdido, text="Boleto Dañado", command=self.BoletoDañado, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface, width=25)
        self.boton_boleto_dañado.grid(
            column=0, row=0, sticky=tk.NE, padx=3, pady=3)

        self.boton3 = tk.Button(
            self.label_botones_boletos_perdido, text="Boleto Perdido CON FOLIO", command=self.BoletoPerdido_conFolio, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface, width=25)
        self.boton3.grid(
            column=0, row=1, sticky=tk.NE, padx=3, pady=3)


        if self.habilita_impresion_boleto_perdido:
            self.boton3 = tk.Button(
                self.label_botones_boletos_perdido, text="Boleto Perdido SIN FOLIO", command=self.BoletoPerdido_sinFolio, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface, width=25)
            self.boton3.grid(
                column=0, row=2, sticky=tk.NE, padx=3, pady=3)

        self.labelPerdido2 = tk.LabelFrame(
            self.labelPerdido_principal, text="Boletos sin cobro", font=self.font_subtittle_system)
        self.labelPerdido2.grid(
            column=0, row=2, padx=2, pady=2, sticky=tk.NW)

        self.scrolledtxt_boletos = st.ScrolledText(
            self.labelPerdido2, height=7, width=26, font=self.font_scrolledtext)

        self.scrolledtxt_boletos.grid(
            column=0, row=0, padx=10, pady=10)

        boton = tk.Button(
            self.labelPerdido2, text="Ver boletos sin cobro", command=self.BoletoDentro, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton.grid(
            column=0, row=1)

        self.BoletoDentro()

    def BoletoDentro(self) -> None:
        """
        Recupera informacion sobre los autos actualmente dentro del estacionamiento y la muestra en el widget scrolledtxt.

        Esta funcion realiza la consulta a la base de datos para obtener la informacion de los autos dentro del estacionamiento,
        y luego muestra dicha informacion en el widget de texto con desplazamiento.

        :return: None
        """
        self.scrolledtxt_boletos.config(state="normal")
        # Obtener la respuesta de la base de datos con la informacion de autos dentro
        respuesta = self.DB.Autos_dentro()

        # Limpiar el contenido actual del widget scrolledtxt
        self.scrolledtxt_boletos.delete("1.0", tk.END)

        if len(respuesta) == 0:
            self.scrolledtxt_boletos.insert(
                tk.END, f"No hay boletos")
        else:
            # Iterar sobre la respuesta y agregar la informacion al widget scrolledtxt
            for fila in respuesta:
                # Formatear la informacion y agregar al widget scrolledtxt
                self.scrolledtxt_boletos.insert(
                    tk.END, f"Folio: {fila[0]}\nEntro: {fila[1].strftime(self.date_format_interface)}\nPlacas: {fila[2]}\n\n")

        self.scrolledtxt_boletos.config(state="disabled")

    def BoletoPerdido_conFolio(self) -> None:
        """
        Esta funcion se encarga de manejar el cobro de un boleto perdido con folio.

        Verifica si se ha ingresado un número de folio para el boleto perdido y realiza las operaciones correspondientes.
        Calcula la permanencia del vehiculo y el importe a cobrar.
        Establece el concepto del boleto como "Per" de perdido.

        :param self: Objeto de la clase que contiene los atributos y metodos necesarios.

        :return: None
        """
        try:
            datos = self.PonerFOLIO.get()

            if len(datos) == 0:
                self.entryPonerFOLIO.focus()
                raise WithoutParameter("Folio del boleto")

            self.folio.set(datos)
            datos = self.folio.get()
            self.folio_auxiliar = datos
            importe = 0

            # Consultar los datos correspondientes al folio
            respuesta = self.DB.consulta(datos)
            if len(respuesta) == 0:
                # Limpiar campos y mostrar mensaje de error
                self.limpiar_campos()
                self.entryfolio.focus()
                raise SystemError("No existe un auto con ese folio")

            self.fecha_interna_entrada = respuesta[0][0]
            self.fecha_interna_salida = respuesta[0][1]

            self.fecha_entrada.set(
                self.fecha_interna_entrada.strftime(self.date_format_interface))
            self.fecha_salida.set(self.fecha_interna_salida.strftime(
                self.date_format_interface) if respuesta[0][1] != None else "")

            # Calcular la permanencia
            self.CalculaPermanencia()

            importe = self.tarifa_boleto_perdido + self.importe.get() if self.penalizacion_con_importe else self.tarifa_boleto_perdido

            # Establecer el importe y mostrarlo
            self.mostrar_importe(importe)

            # Realizar otras operaciones y configuraciones
            self.TarifaPreferente.set("Per")
            self.promo.set("")
            self.PonerFOLIO.set("")

            if self.show_clock:
                self.reloj.update_data(self.TarifaPreferente.get(), importe)
        except Exception as e:
            mb.showerror("Error", e)

    def BoletoPerdido_sinFolio(self) -> None:
        """
        Esta funcion se encarga de imprimir un boleto perdido sin un número de folio especificado.

        Verifica si se ha confirmado la impresion del boleto perdido.
        Genera un boleto nuevo para poder cobrar boletos que han sido extraviados.
        Agrega el registro del pago a la base de datos.

        :return: None
        """
        try:
            if mb.askokcancel("Advertencia", f"¿Esta seguro de imprimir un boleto perdido?") == False:
                return

            folio_boleto = self.DB.MaxfolioEntrada() + 1

            state = self.printer_controller.print_lose_ticket(folio_boleto)

            if state != None:
                raise SystemError(state)

            self.BoletoDentro()

        except Exception as e:
            mb.showerror("Error", e)

        finally:
            self.entry_placa.focus()
            self.Placa.set("")
            self.limpiar_campos()

    def consultar(self, event) -> None:
        """
        Consulta la informacion asociada a un folio y la muestra en la interfaz gráfica.

        Esta funcion se ejecuta al activarse el evento (por ejemplo, presionar Enter en un campo de entrada).
        Consulta la base de datos con el folio proporcionado, descifra el folio si es necesario, y muestra la informacion
        correspondiente en la interfaz gráfica.

        :param event: Evento que activa la funcion.
        :return: None
        """
        try:
            # Vaciar campo de importe
            self.label_show_importe.config(text="")

            # Obtener el folio ingresado en la caja de texto
            datos = str(self.folio.get())

            # Si la caja de texto está vacia, limpiar la informacion en pantalla y enfocar la caja de texto
            if len(datos) == 0:
                self.limpiar_campos()
                self.entryfolio.focus()
                return

            # Si se detecta la palabra "pension" en el dato, realizar accion para PensionadosSalida
            if "pension" in datos.lower():
                self.PensionadosSalida()
                return

            # Verificar si el dato parece ser un folio o una promocion
            if len(datos) > 20:
                raise SystemError("Leer primero el folio")

            # Descifrar el folio si es necesario y obtener su valor
            folio = self.instance_tools.descifrar_folio(folio_cifrado=datos)
            if folio is None:
                return

            self.folio.set(folio)
            folio = self.folio.get()
            self.folio_auxiliar = folio
            print(f"\nFolio descifrado: {folio}")

            # Realizar la consulta en la base de datos con el folio obtenido
            respuesta = self.DB.consulta(folio)

            # Mostrar mensaje si no se encuentra informacion asociada al folio
            if len(respuesta) == 0:
                raise SystemError("No existe un auto con ese folio")

            # Actualizar campos de la interfaz con la informacion obtenida de la consulta
            self.fecha_interna_entrada = respuesta[0][0]
            self.fecha_interna_salida = respuesta[0][1] if respuesta[0][1] != None else ""

            self.fecha_entrada.set(
                self.fecha_interna_entrada.strftime(self.date_format_interface))
            self.fecha_salida.set(self.fecha_interna_salida.strftime(
                self.date_format_interface) if respuesta[0][1] != None else "")

            self.Placa.set(respuesta[0][6])
            self.CalculaPermanencia()

        except Exception as e:
            mb.showerror("Error", e)
            self.limpiar_campos()
        finally:
            # Reiniciar los valores de varios atributos
            self.entryfolio.focus()

    def CalculaPermanencia(self) -> None:
        """
        Esta funcion calcula la permanencia del folio seleccionado.

        Realiza diferentes cálculos basados en la informacion del boleto y actualiza los valores correspondientes.

        :param self: Objeto de la clase que contiene los atributos y metodos necesarios.

        :return: None
        """
        # Borra el valor actual del importe
        self.label_show_importe.config(text="")

        # Obtiene el valor de salida
        salida = self.fecha_salida.get()

        if salida != "":
            self.label15.configure(text=("Este Boleto ya Tiene cobro"))

            # Realiza una consulta con el folio seleccionado para obtener informacion adicional del boleto
            respuesta = self.DB.consulta({self.folio.get()})

            if mb.askyesno("Advertencia", "Este boleto ya tiene cobro ¿Desea reimprimir el comprobante de pago?") == False:
                return

            self.fecha_interna_entrada = respuesta[0][0]
            self.fecha_interna_salida = respuesta[0][1]

            Entrada = self.fecha_interna_entrada.strftime(
                self.date_format_interface)
            Salida = self.fecha_interna_salida.strftime(
                self.date_format_interface)

            folio = respuesta[0][2]
            TiempoTotal = str(respuesta[0][3])
            TarifaPreferente = respuesta[0][4]
            Importe = respuesta[0][5]
            Placas = respuesta[0][6]
            Motivo = respuesta[0][7]

            data = [Placas, folio, TarifaPreferente, Importe, self.fecha_interna_entrada.strftime(
                self.date_format_ticket), self.fecha_interna_salida.strftime(self.date_format_ticket), TiempoTotal[:-3], Motivo]

            state = self.printer_controller.re_print_payment_ticket(data)

            # Reinicia los valores de varios atributos
            self.limpiar_campos()
            self.entryfolio.focus()

            if state != None:
                mb.showwarning("Alerta", state)

            return

        # Si el valor de salida tiene menos de 5 caracteres, significa que no ha sido cobrado
        self.TarifaPreferente.set("Normal")
        self.label15.configure(text="Lo puedes COBRAR")

        # Obtiene la fecha actual
        Salida = datetime.strptime(datetime.now().strftime(
            self.date_format_system), self.date_format_system)
        self.fecha_interna_salida = Salida
        self.copia_fecha_salida.set(
            Salida.strftime(self.date_format_interface))

        # Obtiene la fecha del boleto seleccionado y realiza las conversiones necesarias
        Entrada = self.fecha_interna_entrada

        TiempoTotal = Salida - Entrada

        # Calcula la diferencia en dias, horas y minutos
        self.dias_dentro = TiempoTotal.days
        segundos_vividos = TiempoTotal.seconds

        self.horas_dentro, segundos_vividos = divmod(segundos_vividos, 3600)
        self.minutos_dentro, segundos_vividos = divmod(segundos_vividos, 60)

        self.TiempoTotal.set(TiempoTotal)
        self.TiempoTotal_auxiliar.set(self.TiempoTotal.get()[:-3])

        importe = self.instance_cobro_controller.get_importe_tarifa(
            minutos_dentro=self.minutos_dentro,
            horas_dentro=self.horas_dentro, 
            dias_dentro=self.dias_dentro
        )

        # Establecer el importe y mostrarlo
        self.mostrar_importe(importe)

        # Coloca el foco en el campo entrypromo
        self.entrypromo.focus()

        if self.show_clock:
            self.reloj.set_time(
                entrada=str(Entrada),
                salida=str(Salida),
                days=self.dias_dentro,
                hour=self.horas_dentro,
                minute=self.minutos_dentro,
                seconds=segundos_vividos,
                importe=importe)

            # Espera un segundo para que de tiempo a cargar la animacion
            sleep(0.5)

    def calcular_cambio(self) -> None:
        """
        Calcula el cambio a devolver al cliente despues de un pago.

        Esta funcion verifica el folio, la validez del pago y realiza cálculos para determinar el cambio a devolver al cliente.
        Luego, realiza acciones adicionales como guardar el cobro y generar comprobantes.

        :return: None
        """
        try:
            # Obtener el folio
            folio = self.folio.get()

            # Verificar si el folio es válido
            if len(folio) == 0 or self.folio_auxiliar != folio:
                raise SystemError("vuelva a escanear el QR del boleto")

            # Obtener el importe del pago
            importe = self.importe.get()
            self.elimportees.set(importe)

            # Obtener el monto pagado por el cliente
            valorescrito = self.cuantopagasen.get()

            # Calcular el cambio a devolver
            cambio = valorescrito - importe
            self.elcambioes.set(cambio)

            # Realizar acciones adicionales como guardar el cobro y generar comprobantes
            self.GuardarCobro()

            data = [self.Placa.get(), self.folio.get(), self.TarifaPreferente.get(), self.importe.get(), self.fecha_interna_entrada.strftime(
                self.date_format_ticket), self.fecha_interna_salida.strftime(self.date_format_ticket), self.TiempoTotal.get()[:-3]]


            state = self.printer_controller.print_payment_ticket(
                data)

            if state != None:
                raise SystemError(state)

        except Exception as e:
            mb.showerror("Error", e)
        finally:
            # Reiniciar los valores de varios atributos
            self.entryfolio.focus()
            self.limpiar_campos()

    def GuardarCobro(self, motive: str = None) -> None:
        """Guarda la informacion de un cobro realizado en la base de datos."""
        try:
            # Obtener el valor del codigo QR de promocion (si está presente, de lo contrario, será None)
            QRPromo = self.promo_auxiliar.get()
            if QRPromo == '':
                QRPromo = None

            # Obtener el valor del folio del boleto
            folio = self.folio.get()

            # Realiza una consulta con el folio seleccionado para obtener informacion adicional del boleto
            respuesta = self.DB.consulta(folio)

            if len(respuesta) == 0:
                raise SystemError(
                    "Ha ocurrido un error al realizar el cobro, escanee nuevamente el QR")

            # Obtener valores adicionales del boleto
            Entrada = self.fecha_interna_entrada
            Salida = self.fecha_interna_salida

            TiempoTotal = self.TiempoTotal.get()
            TarifaPreferente = self.TarifaPreferente.get()
            importe = self.importe.get()

            self.label15.configure(text="SI se debe modificar")

            # Valor para verificar el cobro (valor de ejemplo)
            vobo = "lmf"

            # Crear una tupla con los datos del cobro
            datos = (motive, vobo, importe, TiempoTotal, Entrada,
                     Salida, TarifaPreferente, QRPromo, folio)

            # Guardar el cobro en la base de datos
            self.DB.guardacobro(datos)

        except Exception as e:
            mb.showerror("Error", e)

    def aplicar_promocion_qr(self, event) -> None:
        """
        Esta funcion se encarga de aplicar una promocion al boleto seleccionado.

        :param event: Evento que activa la funcion.

        :return: None
        """
        try:
            # Valida si el boleto está leido
            if not self.folio.get():
                self.entryfolio.focus()
                raise SystemError("Leer boleto para aplicar promocion")

            # Valida si el boleto está cobrado como perdido
            TarifaPreferente = self.TarifaPreferente.get()
            if TarifaPreferente == "Per":
                self.promo.set('')
                self.promo_auxiliar.set('')
                self.entrypromo.focus()
                raise SystemError(
                    "A los boletos cobrados como perdidos no se pueden aplicar promociones")

            # Valida que solo se pueda aplicar una promocion por boleto
            if TarifaPreferente not in ["Normal", "Danado"]:
                self.promo.set('')
                self.entrypromo.focus()
                raise SystemError(
                    "Solo se puede aplicar una promocion por boleto")

            # Obtiene el tipo de promocion
            QRPromo = self.promo.get()

            # Obtiene las primeras 8 letras de la promocion (se asume que son suficientes para identificar el tipo de promocion)
            TipoPromo = QRPromo[:8]
            
            aux_promo = TipoPromo.lower()

            lista = [promo.lower() for promo in self.instance_config.get_promo_list("qr")]

            # Verifica si la promocion es conocida en el diccionario PROMOCIONES
            if aux_promo not in lista:
            # if TipoPromo.lower() not in [promo.lower() for promo in self.instance_config.get_promo_list("qr")]:
                self.promo.set('')
                self.promo_auxiliar.set('')
                self.entrypromo.focus()
                raise SystemError(
                    "Promocion desconocida, escanee nuevamente el QR de promocion")

            index_promo = lista.index(aux_promo)
            TipoPromo = self.instance_config.get_promo_list("qr")[index_promo]

            # Valida si la promocion ya fue aplicada previamente
            respuesta = self.DB.ValidaPromo(QRPromo)

            if len(respuesta) > 0:
                self.promo.set('')
                self.promo_auxiliar.set('')
                self.entrypromo.focus()
                raise SystemError("La Promocion ya fue aplicada")

            self.promo_auxiliar.set(QRPromo)

            importe, nombre_promo = self.instance_cobro_controller.get_importe_promo(
                promo_id = TipoPromo,
                minutos_dentro=self.minutos_dentro,
                horas_dentro=self.horas_dentro, 
                dias_dentro=self.dias_dentro
            )

            # Añade "Danado" a la descripcion de la promocion si el boleto está marcado como "Danado"
            text_promo = nombre_promo + TarifaPreferente if TarifaPreferente == "Danado" else nombre_promo

            # Establece el tipo de promocion y muestra el importe actualizado
            self.TarifaPreferente.set(text_promo)
            self.promo.set("")
            self.mostrar_importe(importe)

            if self.show_clock:
                self.reloj.update_data(text_promo, importe)

        except Exception as e:
            mb.showerror("Error", e)

    def aplicar_promocion_boton(self, promo: str) -> None:
        """
        Esta funcion se encarga de aplicar una promocion al boleto seleccionado.

        :param event: Evento que activa la funcion.

        :return: None
        """
        try:
            # Valida si el boleto está leido
            if not self.folio.get():
                self.entryfolio.focus()
                raise SystemError("Leer boleto para aplicar promocion")

            # Valida si el boleto está cobrado como perdido
            TarifaPreferente = self.TarifaPreferente.get()
            if TarifaPreferente == "Per":
                self.entrypromo.focus()
                raise SystemError(
                    "A los boletos cobrados como perdidos no se pueden aplicar promociones")

            # Valida que solo se pueda aplicar una promocion por boleto
            if TarifaPreferente not in ["Normal", "Danado"]:
                self.entrypromo.focus()
                raise SystemError(
                    "Solo se puede aplicar una promocion por boleto")

            # Valida si realmente se quiere aplicar la promocion
            if mb.askyesno("Advertencia", f"¿Esta seguro de querer aplicar la promocion [{promo}] a este boleto?") is False:
                return

            TipoPromo = promo

            importe, _ = self.instance_cobro_controller.get_importe_promo(
                promo_id = TipoPromo,
                minutos_dentro=self.minutos_dentro,
                horas_dentro=self.horas_dentro, 
                dias_dentro=self.dias_dentro
            )

            # Añade "Danado" a la descripcion de la promocion si el boleto está marcado como "Danado"
            text_promo = TipoPromo + TarifaPreferente if TarifaPreferente == "Danado" else TipoPromo

            # Establece el tipo de promocion y muestra el importe actualizado
            self.TarifaPreferente.set(text_promo)
            self.promo.set("")
            self.mostrar_importe(importe)

            if self.show_clock:
                self.reloj.update_data(text_promo, importe)

        except Exception as e:
            mb.showerror("Error", e)

        finally:
            data_config = None
            self.promo.set("")
            self.promo_auxiliar.set("")


    def PensionadosSalida(self) -> None:
        """
        Esta funcion se encarga de registrar la salida de un pensionado del estacionamiento.

        :return: None
        """
        try:
            numtarjeta = self.instance_tools.get_id_from_QR(self.folio.get())

            # Valida si existe un pensionado con ese número de tarjeta
            respuesta = self.DB.ValidarTarj(numtarjeta)

            if len(respuesta) == 0:
                raise SystemError(
                    "No existe Pensionado para ese número de Tarjeta")

            for fila in respuesta:
                Existe = fila[0]
                Estatus = fila[1]

            if Estatus == None:
                raise SystemError("El Pensionado no tiene registro de Entrada")

            elif Estatus == "Afuera":
                raise SystemError("El Pensionado con ese QR ya esta Afuera")

            # Consulta la hora de entrada del pensionado
            Entrada = self.DB.consultar_UpdMovsPens(Existe)

            Salida = datetime.strptime(datetime.now().strftime(
                self.date_format_system), self.date_format_system)

            # Calcular el tiempo total en el estacionamiento
            tiempo_total = Salida - Entrada

            # Preparar los datos para la actualizacion en la base de datos
            datos = (Salida, tiempo_total, 'Afuera', Existe)
            datos1 = ('Afuera', Existe)

            # Actualizar la tabla de movimientos del pensionado
            self.DB.UpdMovsPens(datos)

            # Actualizar el estatus del pensionado
            self.DB.UpdPens2(datos1)

            mb.showinfo("Pension", 'Se registra salida de pension')

            state = self.printer_controller.print_pension_exit_ticket(
                self.folio.get(),
                Entrada.strftime(self.date_format_ticket),
                Salida.strftime(self.date_format_ticket),
                tiempo_total)

            if state != None:
                raise SystemError(state)

        except Exception as e:
            mb.showwarning("Error", e)
            return
        finally:
            self.folio.set("")
            self.entryfolio.focus()
            self.ver_pensionados()
            self.PenAdentro()

    def modulo_corte(self) -> None:
        self.motive_cancel = tk.StringVar()

        self.modulo_corte = tk.Frame(self.cuaderno_modulos)
        self.cuaderno_modulos.add(self.modulo_corte, text="Modulo de Corte")

        self.modulo_corte = tk.LabelFrame(self.modulo_corte)
        self.modulo_corte.pack(expand=True, padx=5, pady=5, anchor='n')

        frame_derecho = tk.LabelFrame(
            self.modulo_corte, text="Funciones", font=self.font_tittle_system)
        frame_derecho.grid(
            column=0, row=0, sticky=tk.NW)

        frame_entradas = tk.LabelFrame(
            frame_derecho, text="Entradas sin corte", font=self.font_subtittle_system)
        frame_entradas.grid(
            column=0, row=0, padx=1, pady=1)

        self.scrolledtext_entradas_sin_corte = st.ScrolledText(
            frame_entradas, height=4, width=26, font=self.font_scrolledtext)
        self.scrolledtext_entradas_sin_corte.grid(
            column=0, row=0, padx=1, pady=1)

        boton_entradas = tk.Button(
            frame_entradas, text="Entradas sin corte", command=self.ver_entradas_sin_corte, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_entradas.grid(
            column=0, row=1, padx=2, pady=2)

        label_frame_corte_anterior = tk.LabelFrame(
            frame_derecho, text="Consultar cortes", font=self.font_subtittle_system)
        label_frame_corte_anterior.grid(
            column=0, row=1, padx=3, pady=3, sticky=tk.N)

        label_etiquetas_corte = tk.Frame(label_frame_corte_anterior)
        label_etiquetas_corte.grid(
            column=0, row=0, padx=3, pady=3)

        etiqueta_corte = tk.Label(
            label_etiquetas_corte, text="Corte a consultar", font=self.font_text_entry_interface)
        etiqueta_corte.grid(
            column=0, row=0, padx=1, pady=1)

        self.corte_anterior = tk.StringVar()
        self.entry_cortes_anteriores = tk.Entry(
            label_etiquetas_corte, width=12, textvariable=self.corte_anterior, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.root.register(self.instance_tools.validate_entry_number), '%P'))
        self.entry_cortes_anteriores.grid(
            column=1, row=0)

        boton_corte = tk.Button(label_frame_corte_anterior, text="Reimprimir corte", background=self.button_color,
                                fg=self.button_letters_color, font=self.font_botones_interface, command=self.reimprimir_corte, height=1, anchor="center")
        boton_corte.grid(
            column=0, row=1, padx=2, pady=2)

        frame_config_admin = tk.LabelFrame(
            frame_derecho, text="Administrar", font=self.font_subtittle_system)
        frame_config_admin.grid(
            column=0, row=2, padx=1, pady=1, sticky=tk.N)

        frame_reporte_mensual = tk.Frame(frame_config_admin)
        frame_reporte_mensual.grid(
            column=1, row=0, padx=1, pady=1, sticky=tk.N)

        frame = tk.Frame(frame_reporte_mensual)
        frame.grid(
            column=0, row=0, padx=3, pady=3)

        label = tk.Label(frame, text="Mes",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=0, padx=1, pady=1)
        combobox_mes_corte = ttk.Combobox(
            frame, width=6, justify=tk.RIGHT, state="readonly", font=self.font_text_entry_interface)
        combobox_mes_corte["values"] = ["1", "2", "3",
                                        "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        combobox_mes_corte.current(0)
        combobox_mes_corte.grid(
            column=1, row=0, padx=1, pady=1)

        label = tk.Label(frame, text="Año",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=1, padx=1, pady=1)
        self.AnoCorte = tk.IntVar()
        Ano = datetime.now().date().year
        self.AnoCorte.set(Ano)
        self.entryAnoCorte = tk.Entry(
            frame, width=7, textvariable=self.AnoCorte, justify='center', font=self.font_text_interface)
        self.entryAnoCorte.grid(
            column=1, row=1)

        boton_reporte_corte = tk.Button(
            frame_reporte_mensual, text="Reporte de Corte", command=self.Reporte_Corte, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_reporte_corte.grid(
            column=0, row=1, padx=2, pady=2)

        seccion_botones = tk.Frame(
            frame_config_admin)
        seccion_botones.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.SW)

        boton_usuarios = ttk.Button(
            seccion_botones, image=self.users_icon, command=self.view_panel_usuarios)
        boton_usuarios.grid(
            column=0, row=0, padx=2, pady=2)

        boton_config = ttk.Button(
            seccion_botones, image=self.config_icon, command=self.view_panel_configuracion)
        boton_config.grid(
            column=1, row=0, padx=2, pady=2)

        frame_izqierdo = tk.LabelFrame(
            self.modulo_corte, text="Informacion del corte", font=self.font_tittle_system)
        frame_izqierdo.grid(
            column=1, row=0, sticky=tk.NW)

        frame_generar_corte = tk.LabelFrame(
            frame_izqierdo, text="Generar Corte", font=self.font_subtittle_system)
        frame_generar_corte.grid(
            column=0, row=0, padx=3, pady=3, sticky=tk.NW)

        frame_corte = tk.Frame(frame_generar_corte)
        frame_corte.grid(
            column=0, row=0, padx=0, pady=0)

        frame_data = tk.Frame(frame_corte)
        frame_data.grid(
            column=0, row=0, padx=3, pady=3)

        label = tk.Label(
            frame_data, text="El importe del corte es", font=self.font_text_entry_interface)
        label.grid(
            column=0, row=1, padx=1, pady=1, sticky=tk.W)
        self.importe_corte = tk.StringVar()
        entry_importe_corte = tk.Entry(
            frame_data, width=20, textvariable=self.importe_corte, state="readonly", justify='center', font=self.font_text_interface)
        entry_importe_corte.grid(
            column=1, row=1, padx=1, pady=1, sticky=tk.W)

        label = tk.Label(frame_data, text="Fecha de fin del corte",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=2, padx=1, pady=1, sticky=tk.W)
        self.fecha_fin_corte = tk.StringVar()
        entry_fecha_fin_corte = tk.Entry(
            frame_data, width=20, textvariable=self.fecha_fin_corte, state="readonly", justify='center', font=self.font_text_interface)
        entry_fecha_fin_corte.grid(
            column=1, row=2, padx=1, pady=1, sticky=tk.W)

        label = tk.Label(frame_data, text="Fecha de inicio del corte",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=3, padx=1, pady=1, sticky=tk.W)
        self.fecha_inicio_corte = tk.StringVar()
        entry_fecha_inicio_corte = tk.Entry(
            frame_data, width=20, textvariable=self.fecha_inicio_corte, state="readonly", justify='center', font=self.font_text_interface)
        entry_fecha_inicio_corte.grid(
            column=1, row=3, padx=1, pady=1, sticky=tk.W)

        frame_botones = tk.Frame(frame_corte)
        frame_botones.grid(
            column=1, row=0, padx=2, pady=2)

        boton_calcular_corte = tk.Button(
            frame_botones, text="Calcular Corte", command=self.Calcular_Corte, height=1, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_calcular_corte.grid(
            column=0, row=0, padx=5, pady=5)

        boton_generar_corte = tk.Button(
            frame_botones, text="Generar Corte", command=self.Guardar_Corte, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_generar_corte.grid(
            column=0, row=1, padx=5, pady=5)

        frame_desgloce_boletos = tk.LabelFrame(
            frame_izqierdo, text="Desgloce de boletos", font=self.font_subtittle_system)
        frame_desgloce_boletos.grid(
            column=0, row=1, padx=3, pady=3, sticky=tk.N)

        frame_boletos = tk.Frame(
            frame_desgloce_boletos)
        frame_boletos.grid(
            column=0, row=1, padx=3, pady=3)

        label = tk.Label(frame_boletos, text="Boletos Cobrados",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=1, padx=1, pady=1, sticky=tk.NW)
        self.boletos_cobrados = tk.StringVar()
        entry_boletos_cobrados = tk.Entry(
            frame_boletos, width=5, textvariable=self.boletos_cobrados, state="readonly", justify='center', font=self.font_text_interface)
        entry_boletos_cobrados.grid(
            column=1, row=1, padx=1, pady=1, sticky=tk.NW)

        label = tk.Label(frame_boletos, text="Boletos Expedidos",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=2, padx=1, pady=1, sticky=tk.NW)
        self.boletos_expedidos = tk.StringVar()
        entry_boletos_expedidos = tk.Entry(
            frame_boletos, width=5, textvariable=self.boletos_expedidos, state="readonly", justify='center', font=self.font_text_interface)
        entry_boletos_expedidos.grid(
            column=1, row=2, padx=1, pady=1, sticky=tk.NW)

        label = tk.Label(frame_boletos, text="Boletos Turno Anterior",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=3, padx=1, pady=1, sticky=tk.NW)
        self.boletos_turno_anterior = tk.StringVar()
        entry_boletos_turno_anterior = tk.Entry(
            frame_boletos, width=5, textvariable=self.boletos_turno_anterior, state="readonly", justify='center', font=self.font_text_interface)
        entry_boletos_turno_anterior.grid(
            column=1, row=3, padx=1, pady=1, sticky=tk.NW)

        label = tk.Label(frame_boletos, text="Boletos Por Cobrar",
                         font=self.font_text_entry_interface)
        label.grid(
            column=0, row=4, padx=1, pady=1, sticky=tk.NW)
        self.boletos_por_cobrar = tk.StringVar()
        entry_boletos_por_cobrar = tk.Entry(
            frame_boletos, width=5, textvariable=self.boletos_por_cobrar, state="readonly", justify='center', font=self.font_text_interface)
        entry_boletos_por_cobrar.grid(
            column=1, row=4, padx=1, pady=1, sticky=tk.NW)

        # label = tk.Label(frame_boletos, text="Salida de Autos",font=self.font_text_entry_interface)
        # label.grid(
        #     column=3, row=1, padx=1, pady=1, sticky=tk.NW)
        # self.SalidaAutos = tk.StringVar()
        # entrySalidaAutos = tk.Entry(
        #     frame_boletos, width=5, textvariable=self.SalidaAutos, state="readonly" , justify='center',font=self.font_text_interface)
        # entrySalidaAutos.grid(
        #     column=2, row=1, padx=1, pady=1, sticky=tk.NW)

        # label = tk.Label(frame_boletos, text="Entrada de Autos",font=self.font_text_entry_interface)
        # label.grid(
        #     column=3, row=2, padx=1, pady=1, sticky=tk.NW)
        # self.SensorEntrada = tk.StringVar()
        # entrySensorEntrada = tk.Entry(
        #     frame_boletos, width=5, textvariable=self.SensorEntrada, state="readonly" , justify='center',font=self.font_text_interface)
        # entrySensorEntrada.grid(
        #     column=2, row=2, padx=1, pady=1, sticky=tk.NW)

        # label = tk.Label(
        #     frame_boletos, text="Autos del Turno anterior", font=self.font_text_entry_interface)
        # label.grid(
        #     column=3, row=3, padx=1, pady=1, sticky=tk.NW)
        # self.Autos_Anteriores = tk.StringVar()
        # entryAutos_Anteriores = tk.Entry(
        #     frame_boletos, width=5, textvariable=self.Autos_Anteriores, state="readonly", justify='center', font=self.font_text_interface)
        # entryAutos_Anteriores.grid(
        #     column=2, row=3, padx=1, pady=1, sticky=tk.NW)

        # label = tk.Label(
        #     frame_boletos, text="Autos en Estacionamiento",font=self.font_text_entry_interface)
        # label.grid(
        #     column=3, row=4, padx=1, pady=1, sticky=tk.NW)
        # self.AutosEnEstacionamiento = tk.StringVar()
        # entryAutosEnEstacionamiento = tk.Entry(
        #     frame_boletos, width=5, textvariable=self.AutosEnEstacionamiento, state="readonly" , justify='center',font=self.font_text_interface)
        # entryAutosEnEstacionamiento.grid(
        #     column=2, row=4, padx=1, pady=1, sticky=tk.NW)

        boton_actualizar_boletos = tk.Button(
            frame_desgloce_boletos, text="Actualizar", command=self.Puertoycontar, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_actualizar_boletos.grid(
            column=0, row=0, padx=3, pady=3)

        boton_cancelar_boleto = tk.Button(
            frame_izqierdo, text="Cancelar Boleto", command=self.BoletoCancelado, height=2,anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_cancelar_boleto.grid(
            column=0, row=2, padx=2, pady=2)

        self.ver_entradas_sin_corte(print_text=False)

    def view_panel_usuarios(self):
        self.instance_tools.desactivar(self.root)
        login_panel_usuarios()
        self.instance_tools.activar(self.root)

    def view_panel_configuracion(self):
        self.instance_tools.desactivar(self.root)
        login_panel_config()
        self.instance_tools.activar(self.root)

    def reimprimir_corte(self) -> None:
        try:
            mesage = None
            if ask_security_question(self.root) != True:
                return

            numero_corte = self.entry_cortes_anteriores.get()
            if not numero_corte:
                self.entry_cortes_anteriores.focus()
                self.corte_anterior.set("")
                raise WithoutParameter("Número de corte a consultar")

            corte_info = self.DB.consultar_corte(numero_corte)

            if len(corte_info) == 0:
                raise NotExist(
                    "No hay informacion que corresponda al corte solicitado")

            printer = Printer(self.printer_idVendor, self.printer_idProduct)

            numero_corte = int(numero_corte)
            for info in corte_info:
                inicio_corte_fecha = self.DB.consultar_corte(
                    numero_corte-1)[0][1]
                final_corte_fecha = info[1]
                importe_corte = info[2]
                BAnterioresImpr = info[3]
                folio_final = info[4]

            folio_inicio = self.DB.consultar_corte(numero_corte-1)[0][4]

            corte_info = self.DB.consultar_informacion_corte(numero_corte)
            for info in corte_info:
                nombre_cajero = info[0]
                turno_cajero = info[1]


            list_corte = []

            printer.set(align="center")
            txt = f"REIMPRESION DEL CORTE {numero_corte}\n"
            printer.text(txt)
            list_corte.append(txt)
            printer.set(align="left")

            txt = f"Cajero que lo consulta: {self.DB.CajeroenTurno()[0][1]}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Hora de consulta: {datetime.now().strftime(self.date_format_system)}\n\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Est {self.nombre_estacionamiento} CORTE Num {numero_corte}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f'IMPORTE: ${importe_corte}\n\n'
            printer.text(txt)
            list_corte.append(txt)

            nombre_dia_inicio = self.instance_tools.get_day_name(
                inicio_corte_fecha.weekday())
            inicio_corte_fecha = datetime.strftime(
                inicio_corte_fecha, '%d-%b-%Y a las %H:%M:%S')
            txt = f'Inicio: {nombre_dia_inicio} {inicio_corte_fecha}\n'
            printer.text(txt)
            list_corte.append(txt)

            nombre_dia_fin = self.instance_tools.get_day_name(
                final_corte_fecha.weekday())
            final_corte_fecha = datetime.strftime(
                final_corte_fecha, "%d-%b-%Y a las %H:%M:%S")
            txt = f'Final: {nombre_dia_fin} {final_corte_fecha}\n\n'
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Folio {folio_inicio} al inicio del turno\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Folio {folio_final} al final del turno\n\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Cajero en Turno: {nombre_cajero}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Turno: {turno_cajero}\n"
            printer.text(txt)
            list_corte.append(txt)

            BolCobrImpresion = self.DB.Cuantos_Boletos_Cobro_Reimpresion(
                numero_corte)

            txt = f"Boletos Cobrados: {BolCobrImpresion}\n"
            printer.text(txt)
            list_corte.append(txt)

            BEDespuesCorteImpre = self.DB.boletos_expedidos_reimpresion(
                numero_corte)
            txt = f'Boletos Expedidos: {BEDespuesCorteImpre}\n'
            printer.text(txt)
            list_corte.append(txt)

            BAnterioresImpr = self.DB.consultar_corte(numero_corte-1)[0][3]
            txt = f"Boletos Turno Anterior: {BAnterioresImpr}\n"
            printer.text(txt)
            list_corte.append(txt)

            BDentroImp = (int(BAnterioresImpr) +
                          int(BEDespuesCorteImpre)) - (int(BolCobrImpresion))
            txt = f'Boletos dejados: {BDentroImp}\n'
            printer.text(txt)
            list_corte.append(txt)

            txt = "----------------------------------\n\n"
            printer.text(txt)
            list_corte.append(txt)

            respuesta = self.DB.desglose_cobrados(numero_corte)

            printer.set(align="center")
            txt = "Cantidad e Importes\n\n"
            printer.text(txt)
            list_corte.append(txt)
            printer.set(align="left")

            txt = "Cantidad - Tarifa - valor C/U - Total \n"
            printer.text(txt)
            list_corte.append(txt)

            for fila in respuesta:
                txt = f"  {str(fila[0])}  -  {str(fila[1])}  -  ${str(fila[2])}   -  ${str(fila[3])}\n\n"
                printer.text(txt)
                list_corte.append(txt)

            else:
                txt = f"{BolCobrImpresion} Boletos        Suma total ${importe_corte}\n"
                printer.text(txt)
                list_corte.append(txt)

            txt = "----------------------------------\n\n"
            printer.text(txt)
            list_corte.append(txt)

            desgloce_cancelados = self.DB.desgloce_cancelados(numero_corte)
            if len(desgloce_cancelados) > 0:
                printer.set(align="center")
                txt = "Boletos cancelados\n\n"
                printer.text(txt)
                list_corte.append(txt)
                printer.set(align="left")

                for boleto in desgloce_cancelados:
                    txt = f"Folio:{boleto[0]} - Motivo: {boleto[1]}\n"
                    printer.text(txt)
                    list_corte.append(txt)

                txt = "----------------------------------\n\n"
                printer.text(txt)
                list_corte.append(txt)

            Quedados_Pensionados = self.controlador_crud_pensionados.get_Anteriores_Pensionados(
                numero_corte)
            Entradas_Totales_Pensionados = self.controlador_crud_pensionados.get_Entradas_Totales_Pensionados(
                numero_corte)
            Salidas_Pensionados = self.controlador_crud_pensionados.get_Salidas_Pensionados(
                numero_corte)
            Anteriores_Pensionados = self.controlador_crud_pensionados.get_Anteriores_Pensionados(
                numero_corte - 1)

            quedados_totales = Quedados_Pensionados - Anteriores_Pensionados

            Quedados = 0 if quedados_totales < 0 else quedados_totales

            if Entradas_Totales_Pensionados > 0 or Salidas_Pensionados > 0 or Quedados_Pensionados > 0:

                printer.set(align="center")
                txt = "Entradas de pensionados\n\n"
                printer.text(txt)
                list_corte.append(txt)
                printer.set(align="left")

                txt = f"Anteriores: {Anteriores_Pensionados}\n"
                printer.text(txt)
                list_corte.append(txt)

                txt = f"Entradas: {Entradas_Totales_Pensionados}\n"
                printer.text(txt)
                list_corte.append(txt)

                txt = f"Salidas: {Salidas_Pensionados}\n"
                printer.text(txt)
                list_corte.append(txt)

                txt = f"Quedados: {Quedados}\n"
                printer.text(txt)
                list_corte.append(txt)

                # Imprime separador
                txt = "----------------------------------\n\n"
                printer.text(txt)
                list_corte.append(txt)

            # Obtiene la cantidad e importes de las pensiones para el corte actual
            respuesta = self.DB.total_pensionados_corte(numero_corte)

            # Si hay pensionados en el corte, se procede a imprimir la seccion correspondiente
            if len(respuesta) > 0:
                printer.set(align="center")
                txt = "Cantidad e Importes Pensiones\n\n"
                printer.text(txt)
                list_corte.append(txt)

                printer.set(align="left")
                txt = "Cuantos - Concepto - ImporteTotal \n"
                printer.text(txt)
                list_corte.append(txt)

                for fila in respuesta:
                    txt = f"   {str(fila[0])}   -  {str(fila[1])}   -   ${str(fila[2])}\n"
                    printer.text(txt)
                    list_corte.append(txt)

                else:
                    txt = f"----------------------------------\n"
                    printer.text(txt)
                    list_corte.append(txt)

            # Imprime ultimo separador
            txt = "----------------------------------\n"
            printer.text(txt)
            list_corte.append(txt)

            # Corta el papel
            printer.cut()
            printer.close()

            txt_file_corte = f"./Public/Reimpresion_Cortes/Reimpresion_{self.nombre_estacionamiento.replace(' ', '_')}_Corte_N°_{numero_corte}.txt"

            with open(file=txt_file_corte, mode="w") as file:
                file.writelines(list_corte)
                file.close()

            thread = Thread(target=self.send_data_controller.send_other_corte)
            thread.start()

        except (USBNotFoundError, NoBackendError) as e:
            mesage = "No se puede reimprimir corte, No se detecta impresora\n\n\tError: Impresora apagada o desconectada.\nPasos a seguir:\n1) Verifique que la impresora este encendida.\n2) Verifique que la impresora este conectada correctamente.\n3) Reinicie el sistema.\n4) En caso de que se siga mostrando este mensaje de error apague y encienda nuevamente la computadora.\n\n5) En caso de no solucionarse el error contacte inmediatamente con un administrador, si este ya se encuentra con usted pida que verifique la configuracion de la impresora dentro del panel de configuracion y que sea visible el nombre de una impresora en caso contrario que seleccione una."

        except Exception as e:
            mb.showerror("Error", f"Error desconocido, contacte con un administrador y muestre el siguiente error: {e}")
        finally:
            self.entry_cortes_anteriores.focus()
            self.corte_anterior.set("")

            if mesage != None:
                mb.showerror("Error", mesage)

    def BoletoCancelado(self) -> None:
        self.instance_tools.desactivar(self.root)
        # Crear la ventana principal
        self.cancel_window = tk.Toplevel()
        self.cancel_window.title("Cancelar Boleto")

        # Se elimina la funcionalidad del boton de cerrar
        self.cancel_window.protocol("WM_DELETE_WINDOW", lambda: {
                                    self.instance_tools.activar(self.root), self.cancel_window.destroy()})

        # Elevar la ventana secundaria al frente de todas las otras ventanas
        self.cancel_window.lift()

        # Colocar el LabelFrame en las coordenadas calculadas
        principal_frame_cancel = tk.LabelFrame(self.cancel_window)
        principal_frame_cancel.pack(expand=True, padx=3, pady=3, anchor='n')

        labelframe_cancelar_boleto = tk.LabelFrame(
            principal_frame_cancel, text="Cancelar Boleto")
        labelframe_cancelar_boleto.grid(
            column=0, row=0, padx=3, pady=3)

        labelframe_cancelar_boleto_folio = tk.Frame(labelframe_cancelar_boleto)
        labelframe_cancelar_boleto_folio.grid(
            column=0, row=0, padx=3, pady=3)

        etiqueta = tk.Label(labelframe_cancelar_boleto_folio,
                            text="Ingresa el Folio a cancelar: ", font=self.font_cancel)
        etiqueta.grid(
            column=0, row=0, padx=2, pady=2)

        self.FolioCancelado = tk.StringVar()
        self.entry_folio_cancelado = tk.Entry(
            labelframe_cancelar_boleto_folio, width=10, textvariable=self.FolioCancelado, justify='center', font=self.font_cancel)
        self.entry_folio_cancelado.grid(
            column=1, row=0, padx=2, pady=2)
        self.entry_folio_cancelado.focus()

        # Crear una etiqueta
        etiqueta = tk.Label(labelframe_cancelar_boleto,
                            text="Ingresa el motivo de la cancelacion del boleto", font=self.font_cancel)
        etiqueta.grid(
            column=0, row=1, padx=2, pady=5)

        self.EntryMotive_Cancel = tk.Entry(
            labelframe_cancelar_boleto, font=self.font_cancel, width=30, textvariable=self.motive_cancel, justify='center')
        self.EntryMotive_Cancel.grid(
            column=0, row=2, padx=2, pady=2)

        # Crear un boton para obtener el texto
        boton = tk.Button(labelframe_cancelar_boleto, text="Cancelar Boleto", command=lambda: cancelar_boleto(
        ), background=self.button_color, fg=self.button_letters_color, height=2, font=self.font_cancel)
        boton.grid(
            column=0, row=3, padx=2, pady=2)

        labelframe_lista_boletos = tk.LabelFrame(
            principal_frame_cancel, text="Lista de boletos")
        labelframe_lista_boletos.grid(
            column=1, row=0, padx=3, pady=3)

        self.boton7 = tk.Button(labelframe_lista_boletos, text="Actualizar", command=lambda: boletos_dentro(
        ), height=1, background=self.button_color, fg=self.button_letters_color, font=self.font_cancel)
        self.boton7.grid(
            column=0, row=0, padx=1, pady=1)

        scroller_boletos_dentro = st.ScrolledText(
            labelframe_lista_boletos, height=8, width=26, font=self.font_scrolledtext)
        scroller_boletos_dentro.grid(
            column=0, row=1, padx=2, pady=2)

        def boletos_dentro():
            scroller_boletos_dentro.config(state="normal")
            respuesta = self.DB.Autos_dentro()
            scroller_boletos_dentro.delete("1.0", tk.END)
            if len(respuesta) == 0:
                scroller_boletos_dentro.insert(
                    tk.END, f"No hay boletos")
            else:
                for fila in respuesta:
                    scroller_boletos_dentro.insert(
                        tk.END, f"Folio: {fila[0]}\nEntro: {fila[1].strftime(self.date_format_interface)}\nPlacas: {fila[2]}\n\n")


            scroller_boletos_dentro.config(state="disabled")

        boletos_dentro()

        def cancelar_boleto():
            try:
                folio = self.FolioCancelado.get()
                if not folio:
                    raise WithoutParameter("Folio a cancelar")

                motive_cancel = self.motive_cancel.get()
                if not motive_cancel:
                    self.EntryMotive_Cancel.focus()
                    raise WithoutParameter(
                        "Motivo por el cual se esta cancelando el boleto")

                cancelar = mb.askokcancel(
                    "Advertencia", f"¿Estas seguro de querer cancelar el boleto con folio: {self.FolioCancelado.get()}?")
                if cancelar == False:
                    return

                self.folio.set(folio)

                folio = self.folio.get()
                respuesta = self.DB.consulta(folio)

                if len(respuesta) == 0:
                    raise SystemError("No existe un auto con ese folio")

                self.fecha_interna_salida = respuesta[0][1]
                Placas = respuesta[0][6]

                if self.fecha_interna_salida is not None:
                    self.motive_cancel.set("")
                    self.folio.set("")
                    raise SystemError(
                        "No se puede cancelar un boleto ya cobrado")

                if Placas == "BoletoPerdido":
                    self.motive_cancel.set("")
                    self.folio.set("")
                    raise SystemError(
                        "El folio ingresado corresponde a una reposicion de un boleto perdido, no se puede cancelar.")

                self.fecha_interna_entrada = respuesta[0][0]
                self.fecha_entrada.set(
                    self.fecha_interna_entrada.strftime(self.date_format_interface))

                self.CalculaPermanencia()
                importe = 0

                # Establecer el importe y mostrarlo
                self.mostrar_importe(importe)

                self.TarifaPreferente.set("CDO")

                self.GuardarCobro(motive_cancel)

                state = self.printer_controller.print_cancel_ticket(
                    folio,
                    self.fecha_interna_entrada,
                    datetime.now().strftime(self.date_format_system),
                    motive_cancel)

                self.cancel_window.destroy()
                self.instance_tools.activar(self.root)

                if state != None:
                    raise SystemError(state)

            except Exception as e:
                mb.showerror("Error", e)
            finally:
                self.limpiar_campos()
                self.entryfolio.focus()
                self.FolioCancelado.set("")
                self.Puertoycontar()

    def ver_entradas_sin_corte(self, print_text=True) -> None:
        self.scrolledtext_entradas_sin_corte.config(state="normal")
        respuesta = self.DB.recuperar_sincobro()
        self.scrolledtext_entradas_sin_corte.delete("1.0", tk.END)

        if len(respuesta) == 0:
            self.scrolledtext_entradas_sin_corte.insert(
                tk.END, f"No hay entradas sin corte")
        else:
            for fila in respuesta:
                self.scrolledtext_entradas_sin_corte.insert(
                    tk.END, f"Folio: {fila[0]}\nEntro: {fila[1].strftime(self.date_format_interface)}\nSalio: {fila[2].strftime(self.date_format_interface) if fila[2] != None else ''}\nImporte: {fila[3]}\n\n")

        if print_text and len(respuesta) > 0:
            state = self.printer_controller.print_entradas_sin_corte(respuesta)

            if state != None:
                mb.showwarning("Alerta", state)
                return

        self.scrolledtext_entradas_sin_corte.config(state="disabled")

    def Calcular_Corte(self) -> None:
        self.importe_corte.set(self.DB.corte())

        # Se obtiene la fecha del ultimo corte
        self.fecha_inicio_corte.set(self.DB.UltimoCorte())

        # Se obtiene la fecha actual
        self.fecha_fin_corte.set(
            datetime.now().strftime(self.date_format_system))

    def Guardar_Corte(self) -> None:
        try:
            mesage = None
            self.Calcular_Corte()
            self.Puertoycontar()

            # Obtenemos los datos del Cajero en Turno
            cajero = self.DB.CajeroenTurno()
            for fila in cajero:
                id_cajero = fila[0]
                nombre_cajero = fila[1]
                inicio_corte = self.fecha_inicio_corte.get()
                turno_cajero = fila[3]

            if id_cajero is None:
                raise SystemError("No se puede generar corte ya que no has iniciado sesion, reinicia el sistema e inicia sesion para poder generar el corte.\n\nSi consideras que se trata de un error ponte en contacto con un administrador inmediatamente")

            printer = Printer(self.printer_idVendor, self.printer_idProduct)

            fecha_hoy = datetime.now().strftime(self.date_format_system)
            datos = (fecha_hoy, id_cajero)
            self.DB.Cierreusuario(datos)

            self.DB.NoAplicausuario(id_cajero)

            # la fecha final de este corte que es la actual
            fechaDECorte = self.fecha_fin_corte.get()

            # el importe se obtiene de la suma
            importe_corte = self.importe_corte.get()
            AEE = self.DB.CuantosAutosdentro()
            maxnumid = self.DB.MaxfolioEntrada()
            NumBolQued = self.boletos_por_cobrar.get()
            Quedados_Pensionados = self.controlador_crud_pensionados.get_Quedados_Pensionados()

            datos = (importe_corte, inicio_corte, fechaDECorte, AEE,
                    maxnumid, NumBolQued, Quedados_Pensionados)
            self.DB.GuarCorte(datos)

            numero_corte = self.DB.Maxfolio_Cortes()
            # este es para que la instruccion no marque error
            ActEntradas = (numero_corte, "cor")

            printer.set(align="left")

            # printer.image(self.logo_empresa)

            list_corte = []

            txt = f"Est {self.nombre_estacionamiento} CORTE Num {numero_corte}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f'IMPORTE: ${importe_corte}\n\n'
            printer.text(txt)
            list_corte.append(txt)

            inicio_corte_fecha = datetime.strptime(
                self.fecha_inicio_corte.get(), self.date_format_system)
            nombre_dia_inicio = self.instance_tools.get_day_name(
                inicio_corte_fecha.weekday())
            inicio_corte_fecha = datetime.strftime(
                inicio_corte_fecha, '%d-%b-%Y a las %H:%M:%S')
            txt = f'Inicio: {nombre_dia_inicio} {inicio_corte_fecha}\n'
            printer.text(txt)
            list_corte.append(txt)

            final_corte_fecha = datetime.strptime(
                self.fecha_fin_corte.get(), self.date_format_system)
            nombre_dia_fin = self.instance_tools.get_day_name(
                final_corte_fecha.weekday())
            final_corte_fecha = datetime.strftime(
                final_corte_fecha, "%d-%b-%Y a las %H:%M:%S")
            txt = f'Final: {nombre_dia_fin} {final_corte_fecha}\n\n'
            printer.text(txt)
            list_corte.append(txt)

            MaxFolio = self.DB.MaxfolioEntrada()
            BEDespuesCorteImpre = self.boletos_expedidos.get()
            folio_inicio = int(MaxFolio)-int(BEDespuesCorteImpre)

            txt = f"Folio {folio_inicio} al inicio del turno\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Folio {MaxFolio} al final del turno\n\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Cajero en Turno: {nombre_cajero}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f"Turno: {turno_cajero}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = '------------------------------\n'
            printer.text(txt)
            list_corte.append(txt)

            inicios = self.DB.IniciosdeTurno(inicio_corte)
            for fila in inicios:
                txt = "Sesion "+fila[1]+": "+str(fila[0])+"\n"
                printer.text(txt)
                list_corte.append(txt)
            else:
                txt = "----------------------------------\n\n"
                printer.text(txt)
                list_corte.append(txt)

            BolCobrImpresion = self.boletos_cobrados.get()
            txt = f"Boletos Cobrados: {BolCobrImpresion}\n"
            printer.text(txt)
            list_corte.append(txt)

            txt = f'Boletos Expedidos: {BEDespuesCorteImpre}\n'
            printer.text(txt)
            list_corte.append(txt)

            BAnterioresImpr = self.boletos_turno_anterior.get()
            txt = f"Boletos Turno Anterior: {BAnterioresImpr}\n"
            printer.text(txt)
            list_corte.append(txt)

            BDentroImp = (int(BAnterioresImpr) +
                        int(BEDespuesCorteImpre))-(int(BolCobrImpresion))
            txt = f'Boletos dejados: {BDentroImp}\n'
            printer.text(txt)
            list_corte.append(txt)

            txt = '------------------------------\n\n'
            printer.text(txt)
            list_corte.append(txt)

            self.importe_corte.set("")
            self.DB.ActualizarEntradasConcorte(ActEntradas)
            self.controlador_crud_pensionados.Actualizar_Entradas_Pension(
                numero_corte)
            self.DB.NocobradosAnt('ant')

            self.corte_anterior.set(numero_corte)
            Numcorte = self.corte_anterior.get()
            respuesta = self.DB.desglose_cobrados(Numcorte)

            printer.set(align="center")
            txt = "Cantidad e Importes\n\n"
            printer.text(txt)
            list_corte.append(txt)
            printer.set(align="left")

            txt = "Cantidad - Tarifa - valor C/U - Total \n"
            printer.text(txt)
            list_corte.append(txt)

            for fila in respuesta:
                txt = f"  {str(fila[0])}  -  {str(fila[1])}  -  ${str(fila[2])}   -  ${str(fila[3])}\n"
                printer.text(txt)
                list_corte.append(txt)

            else:
                txt = f"\n{BolCobrImpresion} Boletos        Suma total ${importe_corte}\n\n"
                printer.text(txt)
                list_corte.append(txt)

            txt = "----------------------------------\n\n"
            printer.text(txt)
            list_corte.append(txt)

            desgloce_cancelados = self.DB.desgloce_cancelados(numero_corte)
            if len(desgloce_cancelados) > 0:
                txt = "Boletos cancelados\n\n"
                printer.text(txt)
                list_corte.append(txt)

                for boleto in desgloce_cancelados:
                    txt = f"Folio:{boleto[0]} - Motivo: {boleto[1]}\n"
                    printer.text(txt)
                    list_corte.append(txt)

                txt = "----------------------------------\n\n"
                printer.text(txt)
                list_corte.append(txt)

            Entradas_Totales_Pensionados = self.controlador_crud_pensionados.get_Entradas_Totales_Pensionados(
                numero_corte)
            Salidas_Pensionados = self.controlador_crud_pensionados.get_Salidas_Pensionados(
                numero_corte)
            Anteriores_Pensionados = self.controlador_crud_pensionados.get_Anteriores_Pensionados(
                numero_corte-1)

            quedados_totales = Quedados_Pensionados - Anteriores_Pensionados
            Quedados = 0 if quedados_totales < 0 else quedados_totales
            if Entradas_Totales_Pensionados > 0 or Salidas_Pensionados > 0 or Quedados_Pensionados > 0:

                printer.set(align="center")
                txt = "Entradas de pensionados\n\n"
                printer.text(txt)
                list_corte.append(txt)
                printer.set(align="left")

                txt = f"Anteriores: {Anteriores_Pensionados}\n"
                printer.text(txt)
                list_corte.append(txt)

                txt = f"Entradas: {Entradas_Totales_Pensionados}\n"
                printer.text(txt)
                list_corte.append(txt)

                txt = f"Salidas: {Salidas_Pensionados}\n"
                printer.text(txt)
                list_corte.append(txt)

                txt = f"Quedados: {Quedados}\n"
                printer.text(txt)
                list_corte.append(txt)

                txt = "----------------------------------\n\n"
                printer.text(txt)
                list_corte.append(txt)

            # Obtiene la cantidad de boletos perdidos generados
            Boletos_perdidos_generados = self.DB.Boletos_perdidos_generados()
            # Obtiene el desglose de los boletos perdidos generados
            Boletos_perdidos_generados_desglose = self.DB.Boletos_perdidos_generados_desglose()
            # Obtiene la cantidad de boletos perdidos cobrados
            Boletos_perdidos_cobrados = self.DB.Boletos_perdidos_cobrados(Numcorte)
            # Obtiene el desglose de los boletos perdidos cobrados
            Boletos_perdidos_cobrados_desglose = self.DB.Boletos_perdidos_cobrados_desglose(
                Numcorte)
            # Obtiene la cantidad de boletos perdidos no cobrados
            Boletos_perdidos_no_cobrados = self.DB.Boletos_perdidos_no_cobrados()

            # Si hay boletos perdidos generados, cobrados o no cobrados, se procede a imprimir el reporte
            if Boletos_perdidos_generados > 0 or Boletos_perdidos_cobrados > 0 or Boletos_perdidos_no_cobrados > 0:
                # Imprime el encabezado de la seccion de boletos perdidos

                printer.set(align="center")
                txt = "BOLETOS PERDIDOS"+'\n'
                printer.text(txt)
                list_corte.append(txt)
                printer.set(align="left")

                # Imprime la cantidad de boletos perdidos generados y su desglose
                txt = f"Boletos perdidos generados: {Boletos_perdidos_generados + Boletos_perdidos_cobrados}" + '\n'
                printer.text(txt)
                list_corte.append(txt)

                for boleto in Boletos_perdidos_cobrados_desglose:
                    txt = f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n"
                    printer.text(txt)
                    list_corte.append(txt)

                for boleto in Boletos_perdidos_generados_desglose:
                    txt = f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n"
                    printer.text(txt)
                    list_corte.append(txt)

                # Imprime separador
                txt = "**********************************\n"
                printer.text(txt)
                list_corte.append(txt)

                # Imprime la cantidad de boletos perdidos cobrados y su desglose
                txt = f"Boletos perdidos cobrados: {Boletos_perdidos_cobrados}" + '\n\n'
                printer.text(txt)
                list_corte.append(txt)

                for boleto in Boletos_perdidos_cobrados_desglose:
                    txt = f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\nFecha salida:{boleto[2]}\n"
                    printer.text(txt)
                    list_corte.append(txt)

                txt = "**********************************\n"
                printer.text(txt)
                list_corte.append(txt)

                # Imprime la cantidad de boletos perdidos no cobrados y su desglose
                txt = f"Boletos perdidos quedados: {Boletos_perdidos_no_cobrados}\n"
                printer.text(txt)
                list_corte.append(txt)

                for boleto in Boletos_perdidos_generados_desglose:
                    txt = f"Folio:{boleto[0]}\nFecha entrada:{boleto[1]}\n"
                    printer.text(txt)
                    list_corte.append(txt)

                # Imprime separador
                txt = "----------------------------------\n\n"
                printer.text(txt)
                list_corte.append(txt)

            # Obtiene la cantidad e importes de las pensiones para el corte actual
            respuesta = self.DB.total_pensionados_corte(Numcorte)

            # Si hay pensionados en el corte, se procede a imprimir la seccion correspondiente
            if len(respuesta) > 0:
                printer.set(align="center")
                txt = "Cantidad e Importes Pensiones\n\n"
                printer.text(txt)
                list_corte.append(txt)
                printer.set(align="left")

                txt = "Cuantos - Concepto - ImporteTotal \n"
                printer.text(txt)
                list_corte.append(txt)

                for fila in respuesta:
                    txt = f"   {str(fila[0])}   -  {str(fila[1])}   -   ${str(fila[2])}\n"
                    printer.text(txt)
                    list_corte.append(txt)

                else:
                    txt = f"----------------------------------\n"
                    printer.text(txt)
                    list_corte.append(txt)

            dir_path = path.abspath("./Public/Reimpresion_Cortes/")
            files = listdir(dir_path)
            if len(files) > 1:
                printer.set(align="center")
                txt = "Reimpresiones de corte\n\n"
                printer.text(txt)
                list_corte.append(txt)
                printer.set(align="left")

                for file in files:
                    _, ext = path.splitext(file)
                    if ext.lower() == ".txt":
                        file_path = path.join(dir_path, file)
                        txt = "-----------------\n"
                        printer.text(txt)
                        list_corte.append(txt)

                        # Abrir el archivo y leer las primeras tres lineas
                        with open(file_path, 'r', encoding='utf-8') as f:
                            primeras_lineas = [next(f) for _ in range(3)]
                            f.close()

                        # Imprimir el nombre del archivo y las primeras tres lineas
                        for linea in primeras_lineas:
                            txt = f"{linea}"
                            printer.text(txt)
                            list_corte.append(txt)
                        self.instance_tools.remove_file(file_path)
                txt = "-----------------\n"
                printer.text(txt)
                list_corte.append(txt)

                # Imprime ultimo separador
                txt = "----------------------------------\n"
                printer.text(txt)
                list_corte.append(txt)

            # Imprime ultimo separador
            txt = "----------------------------------\n"
            printer.text(txt)
            list_corte.append(txt)

            # Corta el papel
            printer.cut()
            printer.close()

            txt_file_corte = f"./Public/Cortes/{self.nombre_estacionamiento}_Corte_N°_{numero_corte}.txt".replace(' ', '_')

            with open(file=txt_file_corte, mode="w") as file:
                file.writelines(list_corte)
                file.close()

            # Cierra el programa al final del reporte
            self.Cerrar_Programa()


        except (USBNotFoundError, NoBackendError) as e:
            mesage = "No se puede generar corte, No se detecta impresora\n\n\tError: Impresora apagada o desconectada.\nPasos a seguir:\n1) Verifique que la impresora este encendida.\n2) Verifique que la impresora este conectada correctamente.\n3) Reinicie el sistema.\n4) En caso de que se siga mostrando este mensaje de error apague y encienda nuevamente la computadora.\n\n5) En caso de no solucionarse el error contacte inmediatamente con un administrador, si este ya se encuentra con usted pida que verifique la configuracion de la impresora dentro del panel de configuracion y que sea visible el nombre de una impresora en caso contrario que seleccione una."

        except Exception as e:
            mb.showerror("Error", f"Error desconocido, contacte con un administrador y muestre el siguiente error: {e}")

        finally:
            if mesage != None:
                mb.showerror("Error", mesage)
                


    def Cerrar_Programa(self) -> None:
        self.root.destroy()
        if self.envio_informacion:
            thread = Thread(target=self.send_all_data)
            thread.start()

            while thread.is_alive():
                continue
            #self.instance_tools.desconectar()
            raise SystemExit()


    def Reporte_Corte(self) -> None:
        contrasena = simpledialog.askinteger(
            "Contrasena", "Capture su Contrasena")  # minvalue=8, maxvalue=8
        if contrasena is not None:
            if contrasena == 13579:
                # mb.showinfo("Contrasena Correcta ", contrasena)
                try:
                    mes = self.comboMesCorte.get()
                    Ano = int(self.entryAnoCorte.get(), )
                    # mb.showinfo("msj uno",mes)
                    # mb.showinfo("msj dos",Ano)
                    if Ano is None:
                        mb.showwarning(
                            "IMPORTANTE", "Debe capturar el Ano del reporte")
                        return
                    elif Ano <= 0:
                        mb.showwarning(
                            "IMPORTANTE", "Distribucion debe ser un numero positivo mayor a cero")
                        return
                    else:
                        Libro = '/home/pi/Documents/XlsCorte' + \
                            str(mes)+'-'+str(Ano)+'  ' + \
                            str(datetime.now().date())+'.xlsx'
                        # mb.showinfo("msj uno",mes)
                        # mb.showinfo("msj dos",Ano)
                        datos = (mes, Ano)
                        # Obtenemos Fecha (Inicialy Final) del mes que solicita el reporte
                        CorteMaxMin = self.DB.Cortes_MaxMin(datos)
                        for fila in CorteMaxMin:
                            UltFecha = fila[0]
                            IniFecha = fila[1]
                        # Obtenemos Primer y Ultimo Folio de Cortes del Mes que se solicita el reporte
                        datos = (IniFecha)
                        CorteIni = self.DB.Cortes_Folio(datos)
                        # mb.showinfo("msj uno",UltFecha)
                        datos = (UltFecha)
                        # CorteFin=self.DB.Cortes_FolioFin(datos)
                        # mb.showinfo("msj uno",CorteFin)
                        CorteFin = self.DB.Cortes_Folio(datos)
                        # mb.showinfo("msj uno",CorteIni)
                        # mb.showinfo("msj dos",CorteFin)
                        # Obtnemos los Registros entre estos dos Folios para el cuerpo del reporte
                        datos = (CorteIni, CorteFin)
                        # datos=(IniFecha, UltFecha)
                        Registros = self.DB.Registros_corte(datos)
                        TotalesCorte = self.DB.Totales_corte(datos)
                        workbook = xlsxwriter.Workbook(Libro)
                        worksheet = workbook.add_worksheet('CORTE')
                        # Definimos Encabezado Principal
                        # Obtnemos imagen del Encabezado
                        # Insert de Logo (imagen.png)
                        worksheet.insert_image(
                            'A1', 'LOGO.jpg', {'x_scale': 0.85, 'y_scale': 0.85})
                        cell_format0 = workbook.add_format()
                        cell_format0 = workbook.add_format(
                            {'align': 'right', 'bold': True})
                        cell_format3 = workbook.add_format()
                        cell_format3 = workbook.add_format(
                            {'bold': True, 'size': 14})
                        cell_format4 = workbook.add_format()
                        cell_format4 = workbook.add_format(
                            {'bold': True, 'align': 'center'})
                        # Aqui debe ir el nombre de la sucursal pero de d[onde lo obtengo?
                        worksheet.write('C3', 'REPORTE DE CORTE', cell_format3)
                        worksheet.write('F4', 'PERIODO', cell_format4)
                        worksheet.write('F5', 'Inicio')
                        worksheet.write('F6', 'Fin')
                        worksheet.write('F7', 'Cortes')
                        worksheet.write(
                            'F8', 'Suma del Periodo:', cell_format0)
                        # Definimos Formatos de celda del encabezado
                        cell_format1 = workbook.add_format()
                        cell_format1 = workbook.add_format(
                            {'bold': True, 'align': 'right', 'num_format': '$#,##0.00', 'bg_color': '#D9D9D9'})
                        # {'num_format': 'dd/mm/yy'}
                        cell_format2 = workbook.add_format()
                        # Format string.
                        cell_format2.set_num_format('dd/mm/yy h:mm:ss')
                        # Colocamos Totales del Encabezado
                        worksheet.write('G5', IniFecha, cell_format2)
                        worksheet.write('G6', UltFecha, cell_format2)
                        for fila in TotalesCorte:
                            worksheet.write('G8', fila[0], cell_format1)
                            worksheet.write(
                                'G7', str(fila[2]) + " al " + str(fila[1]))
                        # mb.showinfo("msj Totale",str(fila[2]))

                        # Definimos Formato y Ancho de Fila Encabezado del cuerpo del reporte
                        cell_format = workbook.add_format(
                            {'bold': True, 'align': 'center', 'text_wrap': True, 'border': 1, 'pattern': 1, 'bg_color': '#D9D9D9'})  # 808080
                        worksheet.set_row(10, 34, cell_format)
                        # Definimos anchos de Columna del cuerpo del reporte
                        worksheet.set_column(0, 0, 10)
                        worksheet.set_column(1, 2, 30)
                        worksheet.set_column(3, 4, 14)
                        worksheet.set_column(5, 5, 13)
                        worksheet.set_column(6, 6, 30)
                        worksheet.set_column(7, 7, 10)
                        # Definimos Nombres de columnas del cuerpo del reporte
                        worksheet.write('A11', 'FOLIO')
                        worksheet.write('B11', 'FECHA Y HORA ENT')
                        worksheet.write('C11', 'FECHA Y HORA SAL')
                        worksheet.write('D11', 'TIEMPO')
                        worksheet.write('E11', 'PRECIO')
                        worksheet.write('F11', 'CORTES')
                        worksheet.write('G11', 'DESCRIPCION')
                        worksheet.write('H11', 'PROM')
                        # Definimos Formatos de celda para datos del cuerpo del reporte
                        # {'num_format': 'hh:mm:ss'}
                        cell_format3 = workbook.add_format()
                        # cell_format3.set_num_format({'align':'right','h:mm:ss'})  # Format string.
                        cell_format3 = workbook.add_format(
                            {'align': 'right', 'num_format': 'h:mm:ss'})
                        cell_format4 = workbook.add_format()
                        cell_format4 = workbook.add_format(
                            {'align': 'right', 'num_format': '$#,##0'})
                        row = 11
                        col = 0
                        for fila in Registros:
                            worksheet.write(row, col,   fila[0])  # Folio A12
                            # Fecha Hora Entrada B12
                            worksheet.write(row, col+1, fila[1], cell_format2)
                            # Fecha Hora Salida C12
                            worksheet.write(row, col+2, fila[2], cell_format2)
                            worksheet.write(
                                row, col+3, fila[3], cell_format3)  # Tiempo D12
                            worksheet.write(
                                row, col+4, fila[4], cell_format4)  # Precio E12
                            worksheet.write(row, col+5, fila[5])  # Cortes F12
                            # Descripcion G12
                            worksheet.write(row, col+6, fila[6])
                            # Promociones H12
                            worksheet.write(row, col+7, fila[7])
                            row += 1
                        workbook.close()
                        mb.showinfo("Reporte de Corte", 'Reporte Guardado')
                except:
                    print('lo que escribiste no es un entero')
                    mb.showwarning(
                        "IMPORTANTE", "Ha ocurrido un error: Revise los datos capturados")
            else:
                mb.showwarning("ERROR", 'Contrasena Incorrecta')

    def Puertoycontar(self) -> None:

        self.boletos_cobrados.set(self.DB.CuantosBoletosCobro())

        MaxFolioCorte = self.DB.Maxfolio_Cortes()

        # self.boletos_expedidos.set(self.DB.BEDCorte()) # revision pendiente
        # self.boletos_turno_anterior.set(self.DB.BAnteriores()) # revision pendiente

        self.boletos_turno_anterior.set(self.DB.Quedados_Sensor(MaxFolioCorte))

        maxNumidIni = self.DB.MaxnumId()
        maxFolioEntradas = self.DB.MaxfolioEntrada()
        BEDCorte = maxFolioEntradas - maxNumidIni
        self.boletos_expedidos.set(BEDCorte)

        self.boletos_por_cobrar.set(self.DB.CuantosAutosdentro())

        # self.Autos_Anteriores.set(self.DB.Quedados_Sensor(MaxFolioCorte))

    ###################### Fin de Pagina2 Inicio Pagina3 ###############################
    def modulo_pensionados(self) -> None:
        self.registros = None
        self.tipo_pago_ = None

        frame_modulo_pensionados = tk.Frame(self.cuaderno_modulos)
        self.cuaderno_modulos.add(
            frame_modulo_pensionados, text="Modulo Pensionados")

        frame_modulo_pensionados = tk.LabelFrame(frame_modulo_pensionados)
        frame_modulo_pensionados.pack(expand=True, padx=5, pady=5, anchor='n')

        # enmarca los controles LabelFrame
        labelframe_pensionados = tk.Frame(
            frame_modulo_pensionados)
        labelframe_pensionados.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.NW)

        labelframe_admin_pensionados = tk.Frame(
            labelframe_pensionados)
        labelframe_admin_pensionados.grid(
            column=0, row=0, padx=2, pady=2)

        label_frame_datos_pago = tk.Frame(labelframe_admin_pensionados)
        label_frame_datos_pago.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.NW)

        # Pago, Vigencia y Numero de tarjeta
        labelframe_pensionados_datos_pago = tk.LabelFrame(
            label_frame_datos_pago, text="Consultar pensionado", font=self.font_subtittle_system)
        labelframe_pensionados_datos_pago.grid(
            column=0, row=0, padx=0, pady=0, sticky=tk.NW)

        labelframe_consulta_pensionados = tk.Frame(
            labelframe_pensionados_datos_pago)
        labelframe_consulta_pensionados.grid(
            column=0, row=0, padx=0, pady=0)

        label = tk.Label(
            labelframe_consulta_pensionados, text="Número de tarjeta", font=self.font_text_entry_interface)
        label.grid(
            column=0, row=0, padx=2, pady=2)
        self.variable_numero_tarjeta = tk.StringVar()
        self.caja_texto_numero_tarjeta = ttk.Entry(
            labelframe_consulta_pensionados, width=20, textvariable=self.variable_numero_tarjeta, justify='center', font=self.font_text_interface)
        self.caja_texto_numero_tarjeta.grid(
            column=1, row=0, padx=2, pady=2)

        boton_consultar_pensionado = tk.Button(
            labelframe_consulta_pensionados, text="Consultar", command=self.ConsulPagoPen, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_consultar_pensionado.grid(
            column=2, row=0, padx=2, pady=2)

        labelframe_datos_pago = tk.Frame(labelframe_pensionados_datos_pago)
        labelframe_datos_pago.grid(
            column=0, row=1, padx=0, pady=0)

        label = tk.Label(
            labelframe_datos_pago, text="Monto Mensual", font=self.font_text_entry_interface)
        label.grid(
            column=0, row=1, padx=2, pady=2, sticky=tk.NW)
        self.Monto = tk.StringVar()
        entryMonto = ttk.Entry(labelframe_datos_pago, width=5,
                               textvariable=self.Monto, state="readonly", justify='center', font=self.font_text_interface)
        entryMonto.grid(
            column=1, row=1, padx=2, pady=2, sticky=tk.NW)

        label = tk.Label(
            labelframe_datos_pago, text="Mensualidades\na Pagar", font=self.font_text_entry_interface)
        label.grid(
            column=0, row=2, padx=2, pady=2, sticky=tk.NW)
        self.meses_pago = tk.StringVar()
        self.comboMensual = ttk.Combobox(
            labelframe_datos_pago, width=3, justify='center', state="readonly", textvariable=self.meses_pago, font=self.font_text_entry_interface)
        self.comboMensual["values"] = ["1", "2", "3", "4",
                                       "5", "6", "7", "8", "9", "10", "11", "12"]
        self.comboMensual.current(0)
        self.comboMensual.grid(
            column=1, row=2, padx=2, pady=2, sticky=tk.NW)

        label = tk.Label(
            labelframe_datos_pago, text="Vigencia", font=self.font_text_entry_interface)
        label.grid(
            column=3, row=1, padx=2, pady=2, sticky=tk.NW)
        self.Vigencia = tk.StringVar()
        cata_texto_vigencia = ttk.Entry(
            labelframe_datos_pago, width=9, textvariable=self.Vigencia, state="readonly", justify='center', font=self.font_text_interface)
        cata_texto_vigencia.grid(
            column=4, row=1, padx=2, pady=2, sticky=tk.NW)

        label = tk.Label(
            labelframe_datos_pago, text="Estatus", font=self.font_text_entry_interface)
        label.grid(
            column=3, row=2, padx=2, pady=2, sticky=tk.NW)
        self.Estatus = tk.StringVar()
        cata_texto_estatus = ttk.Entry(
            labelframe_datos_pago,  width=9, textvariable=self.Estatus, state="readonly", justify='center', font=self.font_text_interface)
        cata_texto_estatus.grid(
            column=4, row=2, padx=2, pady=2, sticky=tk.NW)

        self.etiqueta_informacion = tk.Label(
            labelframe_pensionados_datos_pago, text="", font=self.font_text_entry_interface, bd=2, relief="solid")
        self.etiqueta_informacion.grid(
            column=0, row=2, padx=0, pady=0)

        label_frame_tipo_pago = tk.LabelFrame(
            label_frame_datos_pago, text="Pago de pension", font=self.font_subtittle_system)
        label_frame_tipo_pago.grid(
            column=1, row=0, padx=2, pady=0, sticky=tk.NW)

        self.variable_tipo_pago_efectivo = tk.BooleanVar()
        checkbox_efectivo = tk.Checkbutton(label_frame_tipo_pago, text="Efectivo", variable=self.variable_tipo_pago_efectivo, command=lambda: {
                                           self.cambiar_valor(self.variable_tipo_pago_transferencia)}, font=self.font_text_entry_interface)
        checkbox_efectivo.grid(
            column=0, row=0, padx=2, pady=0, sticky=tk.NW)

        self.variable_tipo_pago_transferencia = tk.BooleanVar()
        checkbox_transferencia = tk.Checkbutton(label_frame_tipo_pago, text="Transferencia", variable=self.variable_tipo_pago_transferencia, command=lambda: {
                                                self.cambiar_valor(self.variable_tipo_pago_efectivo)}, font=self.font_text_entry_interface)
        checkbox_transferencia.grid(
            column=0, row=1, padx=2, pady=0, sticky=tk.NW)

        self.etiqueta_informacion_pago = tk.Label(
            label_frame_tipo_pago, text="$0.00", font=self.font_text_entry_interface)
        self.etiqueta_informacion_pago.grid(
            column=0, row=3, padx=2, pady=0)

        boton_cobrar_pension = tk.Button(
            label_frame_tipo_pago, text="Cobrar Pension", command=self.Cobro_Pensionado, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_cobrar_pension.grid(
            column=0, row=4, padx=3, pady=3)

        labelframe_pensionados_acciones = tk.LabelFrame(
            labelframe_admin_pensionados, text="Administrar pensionados", font=self.font_subtittle_system)
        labelframe_pensionados_acciones.grid(
            column=21, row=0, padx=2, pady=2, sticky=tk.NW)

        self.boton_agregar_pensionado = tk.Button(
            labelframe_pensionados_acciones, background=self.button_color, fg=self.button_letters_color, text="Agregar pensionado", anchor="center", font=self.font_botones_interface, width=21, command=self.agregar_pensionado)
        self.boton_agregar_pensionado.grid(
            column=0, row=0, padx=2, pady=2)

        self.boton_modificar_pensionado = tk.Button(
            labelframe_pensionados_acciones, background=self.button_color, fg=self.button_letters_color, text="Modificar pensionado", anchor="center", command=self.modificar_pensionado, font=self.font_botones_interface, width=21)
        self.boton_modificar_pensionado.grid(
            column=0, row=1, padx=2, pady=2)

        labelframe_pensionados_acciones_contraseña = tk.Frame(
            labelframe_pensionados_acciones)
        labelframe_pensionados_acciones_contraseña.grid(
            column=0, row=2, padx=2, pady=2)

        lbldatos21 = tk.Label(
            labelframe_pensionados_acciones_contraseña, text="Contraseña", font=self.font_text_entry_interface)
        lbldatos21.grid(
            column=0, row=0, padx=0, pady=4)

        self.variable_contraseña_pensionados = tk.StringVar()
        self.campo_texto_contraseña_pensionados = ttk.Entry(
            labelframe_pensionados_acciones_contraseña, width=10, textvariable=self.variable_contraseña_pensionados, show="*", font=self.font_text_interface, justify='center')
        self.campo_texto_contraseña_pensionados.grid(
            column=1, row=0, padx=0, pady=4)

        visible_password_admin_pension = tk.BooleanVar(value=False)
        boton_hide_view_password_admin_pension = ttk.Button(
            labelframe_pensionados_acciones_contraseña, image=self.hide_password_icon, command=lambda: self.instance_tools.visible_password(
                boton_hide_view_password_admin_pension, self.campo_texto_contraseña_pensionados, visible_password_admin_pension, self.show_password_icon, self.hide_password_icon))
        boton_hide_view_password_admin_pension.grid(
            column=2, row=0, padx=0, pady=0)

        boton_reimprimir_comprobante = tk.Button(
            labelframe_pensionados_acciones, text="Imprimir comprobante de\npago anterior", command=self.re_print_pension_pay_ticket, height=2, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_reimprimir_comprobante.grid(
            column=0, row=3, padx=3, pady=3)


        labelframe_info_pensionados = tk.LabelFrame(
            labelframe_pensionados, text="Ver pensionados", font=self.font_subtittle_system)
        labelframe_info_pensionados.grid(
            column=0, row=1, padx=2, pady=0, sticky=tk.NW)

        labelframe_tabla_pensionados = tk.LabelFrame(
            labelframe_info_pensionados)
        labelframe_tabla_pensionados.grid(
            column=0, row=0, padx=2, pady=2, sticky=tk.NW)

        labelframe_tabla_pensionados.columnconfigure(0, weight=1)
        labelframe_tabla_pensionados.rowconfigure(0, weight=1)

        # Obtiene los nombres de las columnas de la tabla que se va a mostrar
        columnas = ['N° de tarjeta', 'Cortesia', 'Nombre',
                    'Estado', 'Vigencia', 'Tolerancia', 'ID', 'Estatus']

        # Crea un Treeview con una columna por cada campo de la tabla
        self.tabla = ttk.Treeview(
            labelframe_tabla_pensionados, columns=columnas)
        self.tabla.config(height=9)
        self.tabla.grid(row=0, column=0, padx=2, pady=5, sticky='NSEW')

        # Define los encabezados de columna
        i = 1
        for headd in columnas:
            self.tabla.heading(f'#{i}', text=headd)
            self.tabla.column(f'#{i}', stretch=True)
            i += 1

        self.tabla.column('#0', width=0, stretch=False)
        self.tabla.column('#1', width=85, stretch=False)
        self.tabla.column('#2', width=60, stretch=False)
        self.tabla.column('#3', width=70, stretch=False)
        self.tabla.column('#4', width=70, stretch=False)
        self.tabla.column('#5', width=120, stretch=False)
        self.tabla.column('#6', width=75, stretch=False)
        self.tabla.column('#7', width=0, stretch=False)
        self.tabla.column('#8', width=75, stretch=False)

        # Crea un Scrollbar vertical y lo asocia con el Treeview
        scrollbar_Y = ttk.Scrollbar(
            labelframe_tabla_pensionados, orient='vertical', command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar_Y.set)
        scrollbar_Y.grid(row=0, column=1, sticky='NS')

        # Crea un Scrollbar horizontal y lo asocia con el Treeview
        scrollbar_X = ttk.Scrollbar(
            labelframe_tabla_pensionados, orient='horizontal', command=self.tabla.xview)
        self.tabla.configure(xscroll=scrollbar_X.set)
        scrollbar_X.grid(row=1, column=0, sticky='EW')

        # Empaqueta el Treeview en el labelframe
        self.tabla.grid(row=0, column=0, padx=2, pady=5)

        labelframe_pensionados_dentro = tk.LabelFrame(
            labelframe_info_pensionados)
        labelframe_pensionados_dentro.grid(
            column=1, row=0, padx=2, pady=2, sticky=tk.NW)

        self.label_pensionados_dentro = tk.Label(
            labelframe_pensionados_dentro, text="", font=self.font_text_entry_interface)
        self.label_pensionados_dentro.grid(
            column=0, row=0, padx=2, pady=3, sticky=tk.N)

        self.scroll_pensionados_dentro = st.ScrolledText(
            labelframe_pensionados_dentro, height=9, width=26, font=self.font_scrolledtext)
        self.scroll_pensionados_dentro.grid(
            column=0, row=1, padx=2, pady=2)

        boton5 = tk.Button(
            labelframe_pensionados_dentro, text="Actualizar", command=self.PenAdentro, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton5.grid(
            column=0, row=2, padx=2, pady=4)

        self.tarjetas_expiradas()
        self.ver_pensionados()
        self.PenAdentro()

    def ConsulPagoPen(self) -> None:
        """Consulta la informacion de un pensionado y muestra los detalles del pago.

        Obtiene la informacion del pensionado asociado al número de tarjeta ingresado,
        calcula el monto a pagar y muestra los detalles del pago en la interfaz gráfica.

        Returns:
            None
        """
        numtarjeta = self.variable_numero_tarjeta.get()

        if not numtarjeta:
            mb.showwarning("IMPORTANTE", "Debe Leer el Numero de Tarjeta")
            self.limpiar_datos_pago()
            return

        numtarjeta = self.instance_tools.get_id_from_QR(numtarjeta)

        resultado = self.DB.ValidarRFID(numtarjeta)

        if not resultado:
            mb.showwarning(
                "IMPORTANTE", "No existe cliente para ese numero de Tarjeta")
            self.limpiar_datos_pago()
            return

        respuesta = self.DB.ConsultaPensionado(resultado)

        if not respuesta:
            mb.showwarning(
                "IMPORTANTE", "No se encontro informacion para el cliente")
            return

        cliente = respuesta[0]
        VigAct = cliente[12]
        Estatus = cliente[14]
        monto = cliente[15]
        cortesia = cliente[16]
        Tolerancia = int(cliente[17])

        self.Monto.set(monto)
        self.Vigencia.set(VigAct)
        self.Estatus.set(Estatus)
        pago = 0
        nummes = int(self.meses_pago.get())

        self.etiqueta_informacion.configure(text="")
        if cortesia == "Si":
            self.etiqueta_informacion.configure(
                text="El Pensionado cuenta con Cortesia")

        # Logica para determinar el pago según el estatus del pensionado
        # y mostrar mensajes informativos
        if Estatus == "Inactiva":
            # Cálculo del pago con penalizacion para estatus Inactiva
            pago = self.instance_tools.calcular_pago_media_pension(monto)
            nummes = 1
            self.valor_tarjeta_pension = self.valor_tarjeta
            if cortesia == "Si":
                pago = 0
                self.valor_tarjeta_pension = 0
            total = pago + self.valor_tarjeta_pension
            self.etiqueta_informacion.configure(text="Tarjeta desactivada")
            mb.showwarning(
                "IMPORTANTE", f"La tarjeta esta desactivada, por lo que el pensionado solo pagará los dias faltantes del mes junto al precio de la tarjeta, posteriormente solo pagará el valor registrado de la pension.\n\nPago pension: {pago}\nPago tarjeton:    {self.valor_tarjeta_pension}\nPago total:        {total}")
            pago = total

        elif Estatus == "InactivaPerm":
            # Cálculo del pago con penalizacion para estatus InactivaPerm
            self.valor_tarjeta_pension = self.valor_tarjeta
            pago_mensualidad = monto * nummes
            total = pago_mensualidad + self.valor_tarjeta_pension

            self.etiqueta_informacion.configure(
                text="Tarjeta desactivada de forma permanente")
            mb.showwarning(
                "IMPORTANTE", f"La tarjeta esta desactivada de forma permanente, por lo que el pensionado pagará una penalizacion correspondiente al precio de la tarjeta ademas de su respectiva mensualidad.\n\nPago pension: {pago_mensualidad}\nPenalizacion:    {self.valor_tarjeta_pension}\nPago total:        {total}")
            pago = total

        elif Estatus == "InactivaTemp":
            pago_mensualidad = monto * nummes

            self.etiqueta_informacion.configure(
                text="Tarjeta desactivada de forma temporal")
            mb.showwarning(
                "IMPORTANTE", f"La tarjeta esta desactivada de forma temporal, por lo que el pensionado solo pagará su respectiva mensualidad.")
            pago = pago_mensualidad

        elif Estatus == "Reposicion":
            self.etiqueta_informacion.configure(text="Tarjeta de reposicion")
            mb.showwarning(
                "IMPORTANTE", "La tarjeta es de reposicion por lo que el pensionado solo pagará dicho valor")
            pago = self.valor_reposicion_tarjeta

        elif VigAct != None:

            # Obtener la fecha y hora actual en formato deseado
            hoy = datetime.strptime(datetime.now().strftime(
                self.date_format_system), self.date_format_system)

            limite = self.instance_tools.get_date_limit(VigAct, Tolerancia)
            print(f"limite: {limite}")

            penalizacion_pension = 0

            if hoy > limite:
                penalizacion_pension, dias_atrasados = self.instance_tools.calcular_penalizacion_diaria(
                    penalizacion_diaria=self.penalizacion_diaria_pension,
                    fecha_limite=limite)

                mb.showwarning(
                    "IMPORTANTE", f"Vigencia Vencida por {dias_atrasados} dias, se aplicará una penalizacion de ${penalizacion_pension}.00 sumado a su pago de pension.")
                self.caja_texto_numero_tarjeta.focus()

            pago = (monto * nummes) + penalizacion_pension

        self.etiqueta_informacion_pago.configure(text=f"${pago}.00")

    def Cobro_Pensionado(self) -> None:
        """Realiza el cobro de la pension al pensionado y actualiza su informacion en la base de datos.

        Realiza el cobro correspondiente a la pension del pensionado según su estado,
        tipo de pension y forma de pago seleccionada. Actualiza la informacion del pensionado
        en la base de datos con los nuevos datos de vigencia y estatus. Además, imprime un comprobante
        de pago y muestra mensajes informativos.

        Raises:
            TypeError: Si no se ha seleccionado una forma de pago.
        """
        tarjeta = self.variable_numero_tarjeta.get()
        nummes = int(self.meses_pago.get())

        try:
            if not tarjeta:
                self.caja_texto_numero_tarjeta.focus()
                raise SystemError("Debe Leer el Numero de Tarjeta")

            # Verificar que se ha seleccionado una forma de pago
            if not self.variable_tipo_pago_transferencia.get() and not self.variable_tipo_pago_efectivo.get():
                raise SystemError("Selecciona una forma de pago")

            tarjeta = self.instance_tools.get_id_from_QR(tarjeta)

            Existe = self.DB.ValidarRFID(tarjeta)

            if not Existe:
                self.limpiar_datos_pago()
                raise SystemError("No existe cliente para ese numero de Tarjeta")

            respuesta = self.DB.ConsultaPensionado(Existe)

            if not respuesta:
                self.limpiar_datos_pago()
                raise SystemError("No se encontro informacion para el cliente")

            usuario = self.DB.nombre_usuario_activo()
            # usuario = "prueba"

            cliente = respuesta[0]
            Nom_cliente = cliente[0]
            Apell1_cliente = cliente[1]
            Apell2_cliente = cliente[2]
            VigAct = cliente[12]
            Estatus = cliente[14]
            monto = cliente[15]
            cortesia = cliente[16]
            Tolerancia = int(cliente[17])

            fechaPago = datetime.now().strftime(self.date_format_system)
            pago = 0
            if Estatus == "Inactiva":
                pago = self.instance_tools.calcular_pago_media_pension(monto)
                nummes = 1
                total = pago + self.valor_tarjeta
                pago = total
                if cortesia == "Si":
                    pago = 0

            elif Estatus == "InactivaPerm":
                if cortesia == "Si":
                    pago = 0
                pago = monto * nummes
                total = pago + self.valor_tarjeta
                pago = total

            elif Estatus == "InactivaTemp":
                if cortesia == "Si":
                    pago = 0
                pago_mensualidad = monto * nummes
                pago = pago_mensualidad

            elif Estatus == "Reposicion":
                pago = self.valor_reposicion_tarjeta

            elif VigAct != None:

                # Obtener la fecha y hora actual en formato deseado
                hoy = datetime.strptime(datetime.now().strftime(
                    self.date_format_system), self.date_format_system)

                limite = self.instance_tools.get_date_limit(VigAct, Tolerancia)
                print(f"limite: {limite}")

                penalizacion_pension = 0

                if hoy > limite:
                    penalizacion_pension, _ = self.instance_tools.calcular_penalizacion_diaria(
                        penalizacion_diaria=self.penalizacion_diaria_pension,
                        fecha_limite=limite)

                pago = (monto * nummes) + penalizacion_pension

            if cortesia == "Si":
                pago = 0
                NvaVigencia = self.instance_tools.nueva_vigencia(
                    fecha=VigAct,
                    cortesia="Si")

            else:
                NvaVigencia = self.instance_tools.nueva_vigencia(
                    fecha=VigAct,
                    meses=nummes)

            datos = (Existe, tarjeta, fechaPago, NvaVigencia,
                     nummes, pago, self.tipo_pago_)
            datos1 = ("Activo", NvaVigencia, Existe)

            self.DB.CobrosPensionado(datos)
            self.DB.Upd_Pensionado(datos1)

            mb.showinfo("IMPORTANTE", "PAGO realizado con exito")

            state = self.printer_controller.print_pension_pay_ticket(
                id=self.variable_numero_tarjeta.get(),
                Nom_cliente=Nom_cliente,
                Apell1_cliente=Apell1_cliente,
                Apell2_cliente=Apell2_cliente,
                fecha_pago=fechaPago,
                vigencia=NvaVigencia[:10],
                monto=pago,
                usuario=usuario,
                tipo_pago=self.tipo_pago_
            )

            if state != None:
                self.limpiar_datos_pago()
                raise SystemError(state)

        except Exception as e:
            print(e)
            mb.showwarning("Error", e)

    def re_print_pension_pay_ticket(self):
        tarjeta = self.variable_numero_tarjeta.get()
        contraseña = self.variable_contraseña_pensionados.get()

        try:
            if not tarjeta:
                self.caja_texto_numero_tarjeta.focus()
                raise SystemError("Debe Leer el Numero de Tarjeta")

            if len(contraseña) == 0:
                self.campo_texto_contraseña_pensionados.focus()
                raise WithoutParameter(
                    "La contraseña del modulo de pensionados.")
                
            if contraseña != self.instance_tools.descifrar_AES(self.__contraseña_pensionados__, bytes.fromhex(self.__iv_pensionados__)):
                self.variable_contraseña_pensionados.set("")
                self.campo_texto_contraseña_pensionados.focus()
                raise SystemError("Contraseña incorrecta")

            tarjeta = self.instance_tools.get_id_from_QR(tarjeta)

            id_pension = self.DB.ValidarRFID(tarjeta)

            if not id_pension:
                self.limpiar_datos_pago()
                self.caja_texto_numero_tarjeta.focus()
                raise SystemError("No existe cliente para ese numero de Tarjeta")

            respuesta = self.DB.ConsultaPensionado(id_pension)

            if not respuesta:
                self.limpiar_datos_pago()
                self.caja_texto_numero_tarjeta.focus()
                raise SystemError("No se encontro informacion para el cliente")

            self.instance_tools.desactivar(self.root)
            ViewPaidPension(id_pension)
            self.instance_tools.activar(self.root)
            self.limpiar_datos_pago()


        except Exception as e:
            print(e)
            mb.showwarning("Error", e)



    def PenAdentro(self) -> None:
        """Muestra en la interfaz gráfica la lista de pensionados que están adentro.

        Obtiene la lista de pensionados que están dentro del lugar y muestra sus nombres
        y detalles en un ScrolledText en la interfaz gráfica.
        """
        self.scroll_pensionados_dentro.config(state="normal")
        respuesta = self.DB.TreaPenAdentro()
        self.scroll_pensionados_dentro.delete("1.0", tk.END)
        cont = 0

        if len(respuesta) == 0:
            self.scroll_pensionados_dentro.insert(
                tk.END, f"No hay pensionados dentro")
        else:
            for fila in respuesta:
                self.scroll_pensionados_dentro.insert(
                    tk.END, f"{cont+1}) Pension-{self.nombre_estacionamiento.replace(' ', '_')}-{fila[0]}\n")
                self.scroll_pensionados_dentro.insert(
                    tk.END, f"   {fila[1]} {fila[2]}\n")
                self.scroll_pensionados_dentro.insert(
                    tk.END, f"   {fila[3]} - {fila[4]}\n\n")
                cont = cont + 1


        self.scroll_pensionados_dentro.config(state="disabled")

        self.label_pensionados_dentro.configure(
            text=f"Pensionados dentro: {cont}")

    def cambiar_valor(self, contrario: tk.BooleanVar):
        """Cambia el valor de la variable según las variables de tipo de pago seleccionadas.
        Args:
            contrario (tk.BooleanVar): Una variable booleana que se utiliza para establecer un valor opuesto.
        Returns:
            None
        """
        try:
            # Establece la variable contrario como False
            contrario.set(False)

            # Si la variable de tipo de pago transferencia está seleccionada, establece tipo_pago_ como "Transferencia"
            if self.variable_tipo_pago_transferencia.get():
                self.tipo_pago_ = "Transferencia"

            # Si la variable de tipo de pago efectivo está seleccionada, establece tipo_pago_ como "Efectivo"
            elif self.variable_tipo_pago_efectivo.get():
                self.tipo_pago_ = "Efectivo"

            # Si ninguna de las variables de tipo de pago está seleccionada, establece tipo_pago_ como None
            else:
                self.tipo_pago_ = None

        except Exception as e:
            # Si ocurre un error, no hace nada
            pass

    def vaciar_tipo_pago(self) -> None:
        """Vacia las variables de tipo de pago.
        Returns:
            None
        """
        # Establece las variables de tipo de pago como False
        self.variable_tipo_pago_transferencia.set(False)
        self.variable_tipo_pago_efectivo.set(False)

    def BoletoDañado(self) -> None:
        """
        Esta funcion se encarga de manejar el cobro de un boleto dañado.

        Verifica si se ha ingresado un número de folio para el boleto dañado y realiza las operaciones correspondientes.
        Muestra informacion relevante del boleto dañado y establece el tipo de pago como "Danado".

        :param self: Objeto de la clase que contiene los atributos y metodos necesarios.

        :return: None
        """
        try:
            datos = self.PonerFOLIO.get()
            self.folio.set(str(datos))
            datos = self.folio.get()
            self.folio_auxiliar = datos

            if len(datos) == 0:
                self.entryPonerFOLIO.focus()
                raise WithoutParameter("Folio del boleto dañado")

            respuesta = self.DB.consulta(datos)
            if len(respuesta) == 0:
                self.entryfolio.focus()
                raise SystemError("No existe un auto con ese folio")

            if respuesta[0][6] == "BoletoPerdido":
                self.entryfolio.focus()
                raise SystemError(
                    "No se puede cobrar como Danado un boleto perdido")

            self.fecha_interna_entrada = respuesta[0][0]
            self.fecha_interna_salida = respuesta[0][1] if respuesta[0][1] != None else ""

            self.fecha_entrada.set(
                self.fecha_interna_entrada.strftime(self.date_format_interface))
            self.fecha_salida.set(
                self.fecha_interna_salida.strftime(self.date_format_interface) if respuesta[0][1] != None else "")

            self.CalculaPermanencia()
            self.TarifaPreferente.set("Danado")
            self.PonerFOLIO.set('')


        except Exception as e:
            mb.showerror("Error", e)
            self.limpiar_campos()

    def view_config_panel(self):
        self.instance_tools.desactivar(self.root)
        login_panel_config()
        self.instance_tools.activar(self.root)

    def desactivar_botones(self) -> None:
        """Esta funcion deshabilita los botones que permiten agregar y modificar pensionados en la interfaz gráfica."""
        self.instance_tools.desactivar(self.root)
        self.boton_agregar_pensionado.configure(state='disabled')
        self.boton_modificar_pensionado.configure(state='disabled')

    def activar_botones(self) -> None:
        """Esta funcion habilita los botones que permiten agregar y modificar pensionados en la interfaz gráfica."""
        self.instance_tools.activar(self.root)
        self.boton_agregar_pensionado.configure(state='normal')
        self.boton_modificar_pensionado.configure(state='normal')

    def limpiar_campos(self) -> None:
        """Limpia los campos y reinicia los valores de los atributos relacionados con la interfaz gráfica.

        Esta funcion reinicia los valores de varios atributos de la interfaz gráfica a su estado inicial,
        lo que implica limpiar campos de entrada de texto y etiquetas, y establecer valores por defecto en algunos atributos.
        """
        # Reinicia los valores de varios atributos
        self.folio.set("")
        self.Placa.set("")
        self.fecha_entrada.set("")
        self.fecha_salida.set("")
        self.fecha_interna_entrada = None
        self.fecha_interna_salida = None
        self.copia_fecha_salida.set("")
        self.importe.set("")
        self.TiempoTotal.set("")
        self.TiempoTotal_auxiliar.set("")
        self.promo.set("")
        self.promo_auxiliar.set('')
        self.PonerFOLIO.set("")
        self.label15.configure(text="")
        self.TarifaPreferente.set("")
        self.label_show_importe.config(text="")
        self.folio_auxiliar = None
        self.motive_cancel.set("")
        self.BoletoDentro()

        if self.show_clock:
            self.reloj.clear_data()

    def vaciar_tabla(self) -> None:
        """Vacia la tabla de datos.

        Esta funcion elimina todas las filas de la tabla que muestra los datos de pensionados en la interfaz gráfica.
        """
        # Elimina todas las filas de la tabla
        self.tabla.delete(*self.tabla.get_children())

    def llenar_tabla(self, registros: list):
        """
        Llena la tabla con los registros que cumplen con los criterios de búsqueda.

        :param registros: (list) Una lista de tuplas que representan los registros obtenidos de la base de datos.

        :raises None:

        :return: None
        """
        # Limpia la tabla antes de llenarla con nuevos registros
        self.vaciar_tabla()

        if self.registros:
            for registro in registros:
                # Pasa los valores del registro como tupla
                self.tabla.insert('', 'end', values=registro)

    def ver_pensionados(self) -> None:
        """
        Obtiene y muestra todos los pensionados en la tabla.

        Esta funcion obtiene todos los registros de pensionados desde la base de datos y luego los muestra
        en la tabla de la interfaz gráfica.
        """
        self.registros = self.controlador_crud_pensionados.ver_pensionados()
        self.llenar_tabla(self.registros)

    def eliminar_pensionado(self) -> None:
        """Elimina el pensionado seleccionado."""
        pass

    def agregar_pensionado(self) -> None:
        """
        Abre la ventana para agregar un nuevo pensionado.

        Esta funcion desactiva los botones, verifica la contraseña, y luego abre la ventana para agregar un nuevo pensionado.
        """
        try:
            self.desactivar_botones()
            contraseña = self.variable_contraseña_pensionados.get()

            if len(contraseña) == 0:
                self.campo_texto_contraseña_pensionados.focus()
                raise WithoutParameter(
                    "La contraseña para agregar un pensionado")
            if contraseña != self.instance_tools.descifrar_AES(self.__contraseña_pensionados__, bytes.fromhex(self.__iv_pensionados__)):
                self.variable_contraseña_pensionados.set("")
                self.campo_texto_contraseña_pensionados.focus()
                raise SystemError("Contraseña incorrecta")

            View_agregar_pensionados()

            self.limpiar_datos_pago()
            self.ver_pensionados()

        except Exception as e:
            mb.showerror("Error", e)
        finally:
            self.variable_contraseña_pensionados.set("")
            self.campo_texto_contraseña_pensionados.focus()
            self.activar_botones()

    def modificar_pensionado(self) -> None:
        """
        Abre la ventana para modificar los datos de un pensionado existente.

        Esta funcion desactiva los botones, verifica la contraseña y el número de tarjeta del pensionado,
        y luego abre la ventana para modificar los datos del pensionado existente.
        """
        try:
            self.desactivar_botones()
            contraseña = self.variable_contraseña_pensionados.get()
            numero_tarjeta = self.variable_numero_tarjeta.get()

            if len(numero_tarjeta) == 0:
                self.caja_texto_numero_tarjeta.focus()
                raise WithoutParameter(
                    "El número de tarjeta del pensionado a modificar")

            numero_tarjeta = self.instance_tools.get_id_from_QR(numero_tarjeta)

            if len(contraseña) == 0:
                self.campo_texto_contraseña_pensionados.focus()
                raise WithoutParameter(
                    "La contraseña para agregar un pensionado")

            if contraseña != self.instance_tools.descifrar_AES(self.__contraseña_pensionados__, bytes.fromhex(self.__iv_pensionados__)):
                self.variable_contraseña_pensionados.set("")
                self.campo_texto_contraseña_pensionados.focus()
                raise SystemError("Contraseña incorrecta")

            resultado = self.controlador_crud_pensionados.consultar_pensionado(
                numero_tarjeta)

            if len(resultado) == 0:
                self.limpiar_datos_pago()
                SystemError(
                    "No está registrado un pensionado con dicho número de tarjeta")

            View_modificar_pensionados(datos_pensionado=resultado)

        except Exception as e:
            mb.showerror("Error", e)
        finally:
            self.ver_pensionados()
            self.campo_texto_contraseña_pensionados.focus()
            self.variable_contraseña_pensionados.set("")
            self.variable_numero_tarjeta.set("")
            self.caja_texto_numero_tarjeta.focus()
            self.activar_botones()

    def limpiar_datos_pago(self) -> None:
        """
        Limpia y reinicia los datos relacionados con el pago de pensiones en la interfaz gráfica.

        Esta funcion reinicia los valores y la informacion mostrada en la interfaz gráfica
        relacionados con el pago de pensiones.
        """
        self.etiqueta_informacion.configure(text="")
        self.etiqueta_informacion_pago.configure(text="")
        self.variable_numero_tarjeta.set("")
        self.variable_contraseña_pensionados.set("")
        self.caja_texto_numero_tarjeta.focus()
        self.Monto.set("")
        self.comboMensual.current(0)
        self.Vigencia.set("")
        self.Estatus.set("")
        self.vaciar_tipo_pago()
        self.ver_pensionados()

    def Pensionados(self, event):
        try:
            numero_tarjeta = self.instance_tools.get_id_from_QR(self.Placa.get())

            print(numero_tarjeta)
            Existe = self.DB.ValidarPen(numero_tarjeta)

            if len(Existe) == 0:
                raise SystemError("No existe Pensionado")

            respuesta = self.DB.ConsultaPensionado_entrar(Existe)

            for fila in respuesta:
                VigAct = fila[0]
                Estatus = fila[1]
                Tolerancia = int(fila[3])
                Placas = fila[4]
                Nom_cliente = fila[5]
                Apell1_cliente = fila[6]
                Apell2_cliente = fila[7]

            if VigAct is None:
                raise SystemError("Tarjeton desactivado")

            elif Estatus == 'Adentro':
                raise SystemError("El Pensionado ya está dentro")

            # Obtener la fecha y hora actual en formato deseado
            VigAct = datetime.strptime(VigAct.strftime(
                self.date_format_system), self.date_format_system)

            # Obtener la fecha y hora actual en formato deseado
            hoy = datetime.strptime(datetime.today().strftime(
                self.date_format_system), self.date_format_system)

            limite = self.instance_tools.get_date_limit(VigAct, Tolerancia)
            print(limite)

            if hoy >= limite:
                raise SystemError("Vigencia Vencida")

            Entrada = datetime.today()
            datos = (Existe, numero_tarjeta, Entrada, 'Adentro', 0)
            datos1 = ('Adentro', Existe)
            self.DB.MovsPensionado(datos)
            self.DB.UpdPensionado(datos1)

            self.label_informacion.config(
                text=f"Entro pensionado ID-{numero_tarjeta}")

            self.ver_pensionados()
            self.PenAdentro()

            # Generar QR
            path = self.instance_tools.generar_QR(self.Placa.get())
            print(f"QR pension: {self.Placa.get()}")

            state = self.printer_controller.print_pension_enter_ticket(
                path,
                self.Placa.get(),
                f"{Nom_cliente} {Apell1_cliente} {Apell2_cliente}",
                hoy.strftime(self.date_format_ticket),
                Placas,
                VigAct)

            if state != None:
                raise NotExist(state)


        except TclError as e:
            print(e)
            self.label_informacion.config(text="El QR es Invalido")
            return
        except Exception as e:
            if isinstance(e, NotExist):
                mb.showwarning("Alerta", e)
            else:
                self.label_informacion.config(text=e)
            return
        finally:
            self.Placa.set("")
            self.entry_placa.focus()

    def tarjetas_expiradas(self) -> None:
        """
        Muestra las tarjetas vencidas en una ventana aparte.

        Esta funcion obtiene las tarjetas vencidas desde la base de datos, las muestra en una ventana aparte
        y luego desactiva las tarjetas vencidas en la base de datos.
        """
        tarjetas_expiradas = self.controlador_crud_pensionados.ver_tarjetas_expiradas()

        if len(tarjetas_expiradas) == 0:
            return

        self.mostrar_tabla_tarjetas_expiradas(tarjetas_expiradas)

    def mostrar_tabla_tarjetas_expiradas(self, datos: list):
        """
        Muestra una ventana con la tabla de tarjetas vencidas.

        :param datos: (list) Una lista de tuplas con los datos de las tarjetas vencidas.

        Esta funcion muestra una ventana con una tabla que contiene los datos de las tarjetas vencidas
        obtenidos desde la base de datos.
        """
        ventana = tk.Toplevel()
        ventana.title("Tarjetas vencidas")

        # Se elimina la funcionalidad del boton de cerrar
        ventana.protocol("WM_DELETE_WINDOW", lambda: cerrar_ventana())

        # Deshabilita los botones de minimizar y maximizar
        # ventana.attributes('-toolwindow', True)

        # Crear un Frame para contener la tabla y la etiqueta
        frame_tabla = tk.Frame(ventana)
        frame_tabla.pack(padx=10, pady=10)

        # Agregar etiqueta "Lista de tarjetas vencidas"
        etiqueta_titulo = tk.Label(
            frame_tabla, text="Lista de tarjetas vencidas", font=self.font_pensiones_vencidas)
        etiqueta_titulo.pack(side=tk.TOP, pady=10)

        # Crear el scroll de lado izquierdo
        scroll_y = tk.Scrollbar(frame_tabla, orient=tk.VERTICAL)

        # Crear la tabla utilizando el widget Treeview de ttk
        tabla = ttk.Treeview(frame_tabla, yscrollcommand=scroll_y.set)
        tabla["columns"] = ("Num_tarjeta", "Fecha_vigencia")

        # Configurar las columnas
        # Columna invisible para los indices
        tabla.column("#0", width=0, stretch=tk.NO)
        tabla.column("Num_tarjeta", anchor=tk.CENTER, width=110)
        tabla.column("Fecha_vigencia", anchor=tk.CENTER, width=120)

        # Configurar los encabezados de las columnas
        tabla.heading("#0", text="", anchor=tk.W)
        tabla.heading("Num_tarjeta", text="Número de Tarjeta",
                      anchor=tk.CENTER)
        tabla.heading("Fecha_vigencia",
                      text="Fecha de Vigencia", anchor=tk.CENTER)

        # Insertar datos en la tabla
        for tarjeta, fecha in datos:
            tabla.insert("", "end", values=(tarjeta, fecha))

        # Configurar el scrollbar vertical para que controle la tabla
        scroll_y.config(command=tabla.yview)

        # Empacar el scrollbar vertical en el marco
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        tabla.pack(padx=10, pady=10)

        def cerrar_ventana():
            # Obtener la fecha y hora actual en formato deseado
            hoy = datetime.now().strftime(self.date_format_system)

            self.controlador_crud_pensionados.desactivar_tarjetas_expiradas(
                hoy)
            self.ver_pensionados()
            ventana.destroy()

        # Agregar boton "Aceptar" en color rojo centrado debajo de la tabla
        btn_aceptar = tk.Button(
            ventana, text="Aceptar", command=cerrar_ventana, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        btn_aceptar.pack(side=tk.BOTTOM, pady=10)

        # Obtener las dimensiones de la ventana principal
        self.root.update_idletasks()
        ancho_ventana_principal = self.root.winfo_width()
        alto_ventana_principal = self.root.winfo_height()

        # Obtener las dimensiones de la pantalla
        ancho_pantalla = ventana.winfo_screenwidth()
        alto_pantalla = ventana.winfo_screenheight()

        # Calcular la posicion de la ventana secundaria para que quede en el centro de la pantalla
        x = self.root.winfo_x() + (ancho_ventana_principal - ventana.winfo_width()) // 2
        y = self.root.winfo_y() + (alto_ventana_principal - ventana.winfo_height()) // 2

        # Verificar que la ventana secundaria no quede fuera de la pantalla
        x = max(0, min(x, ancho_pantalla - ventana.winfo_width()))
        y = max(0, min(y, alto_pantalla - ventana.winfo_height()))

        # Posicionar la ventana secundaria en el centro de la pantalla
        ventana.geometry(f"+{x}+{y}")

        # Elevar la ventana secundaria al frente de todas las otras ventanas
        ventana.lift()

    def mostrar_importe(self, text_importe: int):
        """
        Muestra el importe en la interfaz gráfica.

        :param text_importe: (int) El importe a mostrar.

        Esta funcion muestra el importe en la interfaz gráfica, actualizando el valor en la etiqueta correspondiente.
        """
        self.importe.set(text_importe)
        self.label_show_importe.config(text=self.importe.get())

    def on_tab_changed(self, event) -> None:
        """
        Hace focus en el entry principal de cada pagina cuando se desplaza entre hojas
        """
        # Obtener el indice de la pestaña actual
        current_tab_index = self.cuaderno_modulos.index(
            self.cuaderno_modulos.select())

        # Comprobar si la pestaña actual es la que se desea
        if current_tab_index == 0:
            # Hacer focus en el widget deseado
            self.entry_placa.focus()

        # Comprobar si la pestaña actual es la que se desea
        elif current_tab_index == 1:
            # Hacer focus en el widget deseado
            self.entryfolio.focus()

        # Comprobar si la pestaña actual es la que se desea
        elif current_tab_index == 2:
            self.entry_cortes_anteriores.focus()
            self.Calcular_Corte()
            self.Puertoycontar()

        # Comprobar si la pestaña actual es la que se desea
        elif current_tab_index == 3:
            # Hacer focus en el widget deseado
            self.caja_texto_numero_tarjeta.focus()


if __name__ == '__main__':
    ViewCobro()
