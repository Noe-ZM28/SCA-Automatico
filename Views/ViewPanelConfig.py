from tkinter import Toplevel, ttk, font, messagebox as mb
from tkinter import Variable, StringVar, BooleanVar, IntVar
from tkinter import Frame, LabelFrame, Button, Label, Entry, Checkbutton, Listbox
from tkinter import W, NW, NS, CENTER, END
from tkinter import TclError, filedialog
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import locale
from platform import system

from .ViewAddEmail import AddEmail
from .ViewHitoryChanges import ViewHitoryChanges
from Controllers.ConfigController import ConfigController
from Controllers.PrinterController import PrinterController
from Tools.Exceptions import WithoutParameter, AlreadyExist, ValidateDataError
from Tools.Tools import Tools
from Tools.Security import Secure, ask_security_question
from Models.Model import Operacion
from Models.Queries import Cambios


class View_Panel_Config:
    def __init__(self) -> None:
        locale_time = 'es_ES' if system() == "Windows" else 'es_MX.utf8'
        locale.setlocale(locale.LC_TIME, locale_time)
        self.configuracion = Toplevel()
        # Establece que la ventana no sea redimensionable
        self.configuracion.resizable(False, False)
        self.instance_tools = Tools()
        self.instance_config = ConfigController()
        self.printer_controller = PrinterController()
        self.DB = Operacion()
        self.cambios_model = Cambios()

        self.get_config_data()
        self.interface()

        self.configuracion.title(
            f"Panel de Configuracion -> {self.nombre_estacionamiento}")

        # Se elimina la funcionalidad del boton de cerrar
        self.configuracion.protocol(
            "WM_DELETE_WINDOW",
            lambda: self.instance_tools.desconectar(self.configuracion))

        # Inicia el loop principal de la ventana
        self.configuracion.mainloop()

    def get_config_data(self) -> None:
        """
        Obtiene la configuracion del sistema desde el archivo de configuracion.

        La funcion asigna valores a diversas variables de instancia con base en la configuracion del sistema.

        No retorna ningún valor explicito, pero asigna valores a las variables de instancia de la clase.

        """
        try:
            self.current_page = None
            self.system_options = self.instance_config.get_config(
                "system_options")
            self.system_to_load = self.instance_config.get_config(
                "system_to_load")

            if self.system_to_load not in [0, 1]:
                self.system_to_load = 0

            self.state_form_config = "normal" if self.system_to_load == 0 else "disabled"

            self.variable_system_to_load = StringVar(
                value=self.system_options[self.system_to_load])

            data_config = self.instance_config.get_config(
                "general", "configuracion_sistema")

            # Configuracion de fechas del sistema
            self.formatos_fecha = data_config["formatos_fecha"]
            self.date_examples = [datetime.now().strftime(
                formato) for formato in self.formatos_fecha]
            self.date_format_system = "%Y-%m-%d %H:%M:%S"
            self.date_format_interface = data_config["formato_hora_interface"]
            self.date_format_ticket = data_config["formato_hora_boleto"]
            self.date_format_clock = data_config["formato_hora_reloj_expedidor_boleto"]

            # Configuracion de fuentes y estilos
            self.fuentes_sistema = list(font.families())
            self.fuente_sistema = data_config["fuente"]

            self.sizes_font = data_config["sizes_font"]

            self.size_text_font = data_config["size_text_font"]

            self.scale_image = 1 if self.size_text_font >= 25 else 2

            self.size_text_font_tittle_system = data_config["size_text_font_tittle_system"]
            self.size_text_font_subtittle_system = data_config["size_text_font_subtittle_system"]
            self.size_text_button_font = data_config["size_text_button_font"]

            self.variable_size_text_font = IntVar(value=self.size_text_font)
            self.variable_size_text_font_tittle_system = IntVar(
                value=self.size_text_font_tittle_system)
            self.variable_size_text_font_subtittle_system = IntVar(
                value=self.size_text_font_subtittle_system)
            self.variable_size_text_button_font = IntVar(
                value=self.size_text_button_font)

            self.font_subtittle_system = (
                self.fuente_sistema, self.size_text_font_subtittle_system, 'bold')
            self.font_tittle_system = (
                self.fuente_sistema, self.size_text_font_tittle_system, 'bold')
            self.font_botones_interface = (
                self.fuente_sistema, self.size_text_button_font, 'bold')
            self.font_text_interface = (
                self.fuente_sistema, self.size_text_font)
            self.font_text_entry_interface = (
                self.fuente_sistema, self.size_text_font, 'bold')
            self.font_new_email_window = (
                self.fuente_sistema, self.size_text_font+3)
            self.font_new_email_title_window = (
                self.fuente_sistema, self.size_text_font_tittle_system+3, 'bold')

            # Configuracion de colores
            self.button_color = data_config["color_botones_interface"]
            self.button_letters_color = data_config["color_letra_botones_interface"]

            self.button_color_cobro = data_config["color_boton_cobro"]
            self.button_letters_color_cobro = data_config["color_letra_boton_cobro"]

            # Configuracion de la impresora
            self.printer_idVendor = data_config["impresora"]["idVendor"]
            self.printer_idProduct = data_config["impresora"]["idProduct"]

            self.datalist_divices = self.instance_tools.get_usb_info()
            self.list_devices = self.instance_tools.get_devices_names_list(
                self.datalist_divices)

            self.printer_system = self.instance_tools.get_device_name(
                self.datalist_divices, self.printer_idVendor, self.printer_idProduct)
            self.variable_printer_system = StringVar(value=self.printer_system)

            # Otras configuraciones generales
            self.requiere_placa = data_config["requiere_placa"]
            self.penalizacion_con_importe = data_config["penalizacion_boleto_perdido"]
            self.show_clock = data_config["reloj"]
            self.envio_informacion = data_config["envio_informacion"]
            self.pantalla_completa = data_config["pantalla_completa"]

            self.imprime_contra_parabrisas = data_config["imprime_contra_parabrisas"]
            self.imprime_contra_localizacion = data_config["imprime_contra_localizacion"]
            self.solicita_datos_del_auto = data_config["solicita_datos_del_auto"]
            self.habilita_impresion_boleto_perdido = data_config["habilita_impresion_boleto_perdido"]

            self.size_font_boleto = data_config["size_font_boleto"]
            self.size_font_contra_parabrisas = data_config["size_font_contra_parabrisas"]
            self.size_font_contra_localizacion = data_config["size_font_contra_localizacion"]

            # Configuracion para pensionados
            data_config = self.instance_config.get_config(
                "general", "configuracion_pensionados")
            self.__contraseña_pensionados__ = data_config["password"]
            self.__iv_pensionados__ = data_config["iv"]
            self.valor_tarjeta = data_config["costo_tarjeta"]
            self.valor_reposicion_tarjeta = data_config["costo_reposicion_tarjeta"]
            self.penalizacion_diaria_pension = data_config["penalizacion_diaria"]

            # Informacion sobre el estacionamiento
            data_config = self.instance_config.get_config(
                "general", "informacion_estacionamiento")
            self.nombre_estacionamiento = data_config["nombre_estacionamiento"]
            self.email = data_config["email"]
            self.__password__ = data_config["password"]
            self.without_decode_email_system = True if self.__password__ == "" else False
            self.__iv_password__ = data_config["iv"]
            self.cantidad_cajones = data_config["cantidad_cajones"]
            self.nombre_entrada = data_config["nombre_entrada"]

            # Configuracion de imagenes
            data_config = self.instance_config.get_config(
                "general", "imagenes")
            self.logo_empresa = data_config["path_logo_boleto"]
            self.imagen_marcas_auto = data_config["path_marcas_auto"]
            self.default_image = data_config["default_image"]
            self.plantilla = data_config["plantilla"]
            self.logo = data_config["path_logo"]

            size = (self.size_text_font+20, self.size_text_font+5)
            self.hide_password_icon = self.instance_tools.get_icon(
                data_config["hide_password_icon"], size)
            self.show_password_icon = self.instance_tools.get_icon(
                data_config["show_password_icon"], size)

            size = (self.size_text_font+10, self.size_text_font+10)
            self.minus_icon = self.instance_tools.get_icon(
                data_config["minus_icon"], size)
            self.plus_icon = self.instance_tools.get_icon(
                data_config["plus_icon"], size)

            size = self.size_text_font+10
            self.config_icon = self.instance_tools.get_icon(
                data_config["config_icon"], (size, size))

            # Configuracion de tarifas
            data_config = self.instance_config.get_config("tarifa")

            self.tipo_tarifa_sistema = data_config["tipo_tarifa_sistema"]

            self.tarifa_boleto_perdido = data_config["tarifa_boleto_perdido"]
            self.variable_importe_boleto_perdido = IntVar()

            # Variables de tarifa sensilla
            self.tarifa_1_fraccion = data_config["tarifa_simple"]["tarifa_1_fraccion"]
            self.tarifa_2_fraccion = data_config["tarifa_simple"]["tarifa_2_fraccion"]
            self.tarifa_3_fraccion = data_config["tarifa_simple"]["tarifa_3_fraccion"]
            self.tarifa_hora = data_config["tarifa_simple"]["tarifa_hora"]
            self.inicio_cobro_fraccion = data_config["tarifa_simple"]["inicio_cobro_fraccion"]

            self.variable_inicio_cobro_cuartos_hora = IntVar()
            self.variable_importe_primer_cuarto_hora = IntVar()
            self.variable_importe_segundo_cuarto_hora = IntVar()
            self.variable_importe_tercer_cuarto_hora = IntVar()
            self.variable_importe_hora = IntVar()

            # Variables de tarifa personalizada
            self.config_0_1 = data_config["tarifa_personalizada"]["0"]["1"]
            self.config_0_2 = data_config["tarifa_personalizada"]["0"]["2"]
            self.config_0_3 = data_config["tarifa_personalizada"]["0"]["3"]
            self.config_0_hora = data_config["tarifa_personalizada"]["0"]["hora"]

            self.config_1_1 = data_config["tarifa_personalizada"]["1"]["1"]
            self.config_1_2 = data_config["tarifa_personalizada"]["1"]["2"]
            self.config_1_3 = data_config["tarifa_personalizada"]["1"]["3"]
            self.config_1_hora = data_config["tarifa_personalizada"]["1"]["hora"]

            self.config_2_1 = data_config["tarifa_personalizada"]["2"]["1"]
            self.config_2_2 = data_config["tarifa_personalizada"]["2"]["2"]
            self.config_2_3 = data_config["tarifa_personalizada"]["2"]["3"]
            self.config_2_hora = data_config["tarifa_personalizada"]["2"]["hora"]

            self.config_3_1 = data_config["tarifa_personalizada"]["3"]["1"]
            self.config_3_2 = data_config["tarifa_personalizada"]["3"]["2"]
            self.config_3_3 = data_config["tarifa_personalizada"]["3"]["3"]
            self.config_3_hora = data_config["tarifa_personalizada"]["3"]["hora"]

            self.config_4_1 = data_config["tarifa_personalizada"]["4"]["1"]
            self.config_4_2 = data_config["tarifa_personalizada"]["4"]["2"]
            self.config_4_3 = data_config["tarifa_personalizada"]["4"]["3"]
            self.config_4_hora = data_config["tarifa_personalizada"]["4"]["hora"]

            self.config_5_1 = data_config["tarifa_personalizada"]["5"]["1"]
            self.config_5_2 = data_config["tarifa_personalizada"]["5"]["2"]
            self.config_5_3 = data_config["tarifa_personalizada"]["5"]["3"]
            self.config_5_hora = data_config["tarifa_personalizada"]["5"]["hora"]

            self.config_6_1 = data_config["tarifa_personalizada"]["6"]["1"]
            self.config_6_2 = data_config["tarifa_personalizada"]["6"]["2"]
            self.config_6_3 = data_config["tarifa_personalizada"]["6"]["3"]
            self.config_6_hora = data_config["tarifa_personalizada"]["6"]["hora"]

            self.config_7_1 = data_config["tarifa_personalizada"]["7"]["1"]
            self.config_7_2 = data_config["tarifa_personalizada"]["7"]["2"]
            self.config_7_3 = data_config["tarifa_personalizada"]["7"]["3"]
            self.config_7_hora = data_config["tarifa_personalizada"]["7"]["hora"]

            self.config_8_1 = data_config["tarifa_personalizada"]["8"]["1"]
            self.config_8_2 = data_config["tarifa_personalizada"]["8"]["2"]
            self.config_8_3 = data_config["tarifa_personalizada"]["8"]["3"]
            self.config_8_hora = data_config["tarifa_personalizada"]["8"]["hora"]

            self.config_9_1 = data_config["tarifa_personalizada"]["9"]["1"]
            self.config_9_2 = data_config["tarifa_personalizada"]["9"]["2"]
            self.config_9_3 = data_config["tarifa_personalizada"]["9"]["3"]
            self.config_9_hora = data_config["tarifa_personalizada"]["9"]["hora"]

            self.config_10_1 = data_config["tarifa_personalizada"]["10"]["1"]
            self.config_10_2 = data_config["tarifa_personalizada"]["10"]["2"]
            self.config_10_3 = data_config["tarifa_personalizada"]["10"]["3"]
            self.config_10_hora = data_config["tarifa_personalizada"]["10"]["hora"]

            self.config_11_1 = data_config["tarifa_personalizada"]["11"]["1"]
            self.config_11_2 = data_config["tarifa_personalizada"]["11"]["2"]
            self.config_11_3 = data_config["tarifa_personalizada"]["11"]["3"]
            self.config_11_hora = data_config["tarifa_personalizada"]["11"]["hora"]

            self.config_12_1 = data_config["tarifa_personalizada"]["12"]["1"]
            self.config_12_2 = data_config["tarifa_personalizada"]["12"]["2"]
            self.config_12_3 = data_config["tarifa_personalizada"]["12"]["3"]
            self.config_12_hora = data_config["tarifa_personalizada"]["12"]["hora"]

            self.config_13_1 = data_config["tarifa_personalizada"]["13"]["1"]
            self.config_13_2 = data_config["tarifa_personalizada"]["13"]["2"]
            self.config_13_3 = data_config["tarifa_personalizada"]["13"]["3"]
            self.config_13_hora = data_config["tarifa_personalizada"]["13"]["hora"]

            self.config_14_1 = data_config["tarifa_personalizada"]["14"]["1"]
            self.config_14_2 = data_config["tarifa_personalizada"]["14"]["2"]
            self.config_14_3 = data_config["tarifa_personalizada"]["14"]["3"]
            self.config_14_hora = data_config["tarifa_personalizada"]["14"]["hora"]

            self.config_15_1 = data_config["tarifa_personalizada"]["15"]["1"]
            self.config_15_2 = data_config["tarifa_personalizada"]["15"]["2"]
            self.config_15_3 = data_config["tarifa_personalizada"]["15"]["3"]
            self.config_15_hora = data_config["tarifa_personalizada"]["15"]["hora"]

            self.config_16_1 = data_config["tarifa_personalizada"]["16"]["1"]
            self.config_16_2 = data_config["tarifa_personalizada"]["16"]["2"]
            self.config_16_3 = data_config["tarifa_personalizada"]["16"]["3"]
            self.config_16_hora = data_config["tarifa_personalizada"]["16"]["hora"]

            self.config_17_1 = data_config["tarifa_personalizada"]["17"]["1"]
            self.config_17_2 = data_config["tarifa_personalizada"]["17"]["2"]
            self.config_17_3 = data_config["tarifa_personalizada"]["17"]["3"]
            self.config_17_hora = data_config["tarifa_personalizada"]["17"]["hora"]

            self.config_18_1 = data_config["tarifa_personalizada"]["18"]["1"]
            self.config_18_2 = data_config["tarifa_personalizada"]["18"]["2"]
            self.config_18_3 = data_config["tarifa_personalizada"]["18"]["3"]
            self.config_18_hora = data_config["tarifa_personalizada"]["18"]["hora"]

            self.config_19_1 = data_config["tarifa_personalizada"]["19"]["1"]
            self.config_19_2 = data_config["tarifa_personalizada"]["19"]["2"]
            self.config_19_3 = data_config["tarifa_personalizada"]["19"]["3"]
            self.config_19_hora = data_config["tarifa_personalizada"]["19"]["hora"]

            self.config_20_1 = data_config["tarifa_personalizada"]["20"]["1"]
            self.config_20_2 = data_config["tarifa_personalizada"]["20"]["2"]
            self.config_20_3 = data_config["tarifa_personalizada"]["20"]["3"]
            self.config_20_hora = data_config["tarifa_personalizada"]["20"]["hora"]

            self.config_21_1 = data_config["tarifa_personalizada"]["21"]["1"]
            self.config_21_2 = data_config["tarifa_personalizada"]["21"]["2"]
            self.config_21_3 = data_config["tarifa_personalizada"]["21"]["3"]
            self.config_21_hora = data_config["tarifa_personalizada"]["21"]["hora"]

            self.config_22_1 = data_config["tarifa_personalizada"]["22"]["1"]
            self.config_22_2 = data_config["tarifa_personalizada"]["22"]["2"]
            self.config_22_3 = data_config["tarifa_personalizada"]["22"]["3"]
            self.config_22_hora = data_config["tarifa_personalizada"]["22"]["hora"]

            self.config_23_1 = data_config["tarifa_personalizada"]["23"]["1"]
            self.config_23_2 = data_config["tarifa_personalizada"]["23"]["2"]
            self.config_23_3 = data_config["tarifa_personalizada"]["23"]["3"]
            self.config_23_hora = data_config["tarifa_personalizada"]["23"]["hora"]

            self.config_24_1 = data_config["tarifa_personalizada"]["24"]["1"]
            self.config_24_2 = data_config["tarifa_personalizada"]["24"]["2"]
            self.config_24_3 = data_config["tarifa_personalizada"]["24"]["3"]
            self.config_24_hora = data_config["tarifa_personalizada"]["24"]["hora"]

            # Configuracion interna de DB
            data_config = self.instance_config.get_config(
                "funcionamiento_interno")
            self.db_usser = data_config["db"]["usuario"]
            self.__db_password__ = data_config["db"]["password"]
            self.__db_iv__ = data_config["db"]["iv"]
            self.db_host = data_config["db"]["host"]
            self.db_db = data_config["db"]["db"]

            # Configuracion de panel de usuarios
            self.usuario_panel_usuarios = data_config["panel_usuarios"]["usuario"]
            self.__contraseña_panel_usuarios__ = data_config["panel_usuarios"]["contraseña"]
            self.__iv_panel_usuarios__ = data_config["panel_usuarios"]["iv"]

            # Configuracion de panel de configuracion
            self.usuario_panel_config = data_config["panel_configuracion"]["usuario"]
            self.__contraseña_panel_config__ = data_config["panel_configuracion"]["contraseña"]
            self.__iv_panel_config__ = data_config["panel_configuracion"]["iv"]

            # Configuracion de envio
            data_config = self.instance_config.get_config(
                "general", "configuiracion_envio")
            self.destinatario_DB = data_config["destinatario_DB"]
            self.destinatario_corte = data_config["destinatario_corte"]
            self.destinatario_notificaciones = data_config["destinatario_notificaciones"]

            # Configuracion colores de reloj
            data_config = self.instance_config.get_config(
                "general", "configuiracion_reloj")
            self.color_primera_hora = data_config["color_primera_hora"]
            self.color_1_fraccion = data_config["color_1_fraccion"]
            self.color_2_fraccion = data_config["color_2_fraccion"]
            self.color_3_fraccion = data_config["color_3_fraccion"]
            self.color_hora_completa = data_config["color_hora_completa"]
            self.color_alerta = data_config["color_alerta"]

            self.variable_0_hora = IntVar()
            self.variable_0_1 = IntVar()
            self.variable_0_2 = IntVar()
            self.variable_0_3 = IntVar()

            self.variable_1_hora = IntVar()
            self.variable_1_1 = IntVar()
            self.variable_1_2 = IntVar()
            self.variable_1_3 = IntVar()

            self.variable_2_hora = IntVar()
            self.variable_2_1 = IntVar()
            self.variable_2_2 = IntVar()
            self.variable_2_3 = IntVar()

            self.variable_3_hora = IntVar()
            self.variable_3_1 = IntVar()
            self.variable_3_2 = IntVar()
            self.variable_3_3 = IntVar()

            self.variable_4_hora = IntVar()
            self.variable_4_1 = IntVar()
            self.variable_4_2 = IntVar()
            self.variable_4_3 = IntVar()

            self.variable_5_hora = IntVar()
            self.variable_5_1 = IntVar()
            self.variable_5_2 = IntVar()
            self.variable_5_3 = IntVar()

            self.variable_6_hora = IntVar()
            self.variable_6_1 = IntVar()
            self.variable_6_2 = IntVar()
            self.variable_6_3 = IntVar()

            self.variable_7_hora = IntVar()
            self.variable_7_1 = IntVar()
            self.variable_7_2 = IntVar()
            self.variable_7_3 = IntVar()

            self.variable_8_hora = IntVar()
            self.variable_8_1 = IntVar()
            self.variable_8_2 = IntVar()
            self.variable_8_3 = IntVar()

            self.variable_9_hora = IntVar()
            self.variable_9_1 = IntVar()
            self.variable_9_2 = IntVar()
            self.variable_9_3 = IntVar()

            self.variable_10_hora = IntVar()
            self.variable_10_1 = IntVar()
            self.variable_10_2 = IntVar()
            self.variable_10_3 = IntVar()

            self.variable_11_hora = IntVar()
            self.variable_11_1 = IntVar()
            self.variable_11_2 = IntVar()
            self.variable_11_3 = IntVar()

            self.variable_12_hora = IntVar()
            self.variable_12_1 = IntVar()
            self.variable_12_2 = IntVar()
            self.variable_12_3 = IntVar()

            self.variable_13_hora = IntVar()
            self.variable_13_1 = IntVar()
            self.variable_13_2 = IntVar()
            self.variable_13_3 = IntVar()

            self.variable_14_hora = IntVar()
            self.variable_14_1 = IntVar()
            self.variable_14_2 = IntVar()
            self.variable_14_3 = IntVar()

            self.variable_15_hora = IntVar()
            self.variable_15_1 = IntVar()
            self.variable_15_2 = IntVar()
            self.variable_15_3 = IntVar()

            self.variable_16_hora = IntVar()
            self.variable_16_1 = IntVar()
            self.variable_16_2 = IntVar()
            self.variable_16_3 = IntVar()

            self.variable_17_hora = IntVar()
            self.variable_17_1 = IntVar()
            self.variable_17_2 = IntVar()
            self.variable_17_3 = IntVar()

            self.variable_18_hora = IntVar()
            self.variable_18_1 = IntVar()
            self.variable_18_2 = IntVar()
            self.variable_18_3 = IntVar()

            self.variable_19_hora = IntVar()
            self.variable_19_1 = IntVar()
            self.variable_19_2 = IntVar()
            self.variable_19_3 = IntVar()

            self.variable_20_hora = IntVar()
            self.variable_20_1 = IntVar()
            self.variable_20_2 = IntVar()
            self.variable_20_3 = IntVar()

            self.variable_21_hora = IntVar()
            self.variable_21_1 = IntVar()
            self.variable_21_2 = IntVar()
            self.variable_21_3 = IntVar()

            self.variable_22_hora = IntVar()
            self.variable_22_1 = IntVar()
            self.variable_22_2 = IntVar()
            self.variable_22_3 = IntVar()

            self.variable_23_hora = IntVar()
            self.variable_23_1 = IntVar()
            self.variable_23_2 = IntVar()
            self.variable_23_3 = IntVar()

            self.variable_24_hora = IntVar()
            self.variable_24_1 = IntVar()
            self.variable_24_2 = IntVar()
            self.variable_24_3 = IntVar()

            self.variable_cantidad_cajones = IntVar()
            self.variable_nombre_entrada = StringVar(value=self.nombre_entrada)
            self.variable_costo_reposicion = IntVar()
            self.variable_penalizacion_diaria = IntVar()

            self.promociones = self.instance_config.get_promo_list()

            self.variable_inicio_cobro_cuartos_hora_promo_sensilla = IntVar()
            self.variable_importe_primer_cuarto_hora_promo_sensilla = IntVar()
            self.variable_importe_segundo_cuarto_hora_promo_sensilla = IntVar()
            self.variable_importe_tercer_cuarto_hora_promo_sensilla = IntVar()
            self.variable_importe_hora_promo_sensilla = IntVar()

            self.variable_tarifa_personalizada_0_1 = IntVar()
            self.variable_tarifa_personalizada_0_2 = IntVar()
            self.variable_tarifa_personalizada_0_3 = IntVar()
            self.variable_tarifa_personalizada_0_hora = IntVar()

            self.variable_tarifa_personalizada_1_1 = IntVar()
            self.variable_tarifa_personalizada_1_2 = IntVar()
            self.variable_tarifa_personalizada_1_3 = IntVar()
            self.variable_tarifa_personalizada_1_hora = IntVar()

            self.variable_tarifa_personalizada_2_1 = IntVar()
            self.variable_tarifa_personalizada_2_2 = IntVar()
            self.variable_tarifa_personalizada_2_3 = IntVar()
            self.variable_tarifa_personalizada_2_hora = IntVar()

            self.variable_tarifa_personalizada_3_1 = IntVar()
            self.variable_tarifa_personalizada_3_2 = IntVar()
            self.variable_tarifa_personalizada_3_3 = IntVar()
            self.variable_tarifa_personalizada_3_hora = IntVar()

            self.variable_tarifa_personalizada_4_1 = IntVar()
            self.variable_tarifa_personalizada_4_2 = IntVar()
            self.variable_tarifa_personalizada_4_3 = IntVar()
            self.variable_tarifa_personalizada_4_hora = IntVar()

            self.variable_tarifa_personalizada_5_1 = IntVar()
            self.variable_tarifa_personalizada_5_2 = IntVar()
            self.variable_tarifa_personalizada_5_3 = IntVar()
            self.variable_tarifa_personalizada_5_hora = IntVar()

            self.variable_tarifa_personalizada_6_1 = IntVar()
            self.variable_tarifa_personalizada_6_2 = IntVar()
            self.variable_tarifa_personalizada_6_3 = IntVar()
            self.variable_tarifa_personalizada_6_hora = IntVar()

            self.variable_tarifa_personalizada_7_1 = IntVar()
            self.variable_tarifa_personalizada_7_2 = IntVar()
            self.variable_tarifa_personalizada_7_3 = IntVar()
            self.variable_tarifa_personalizada_7_hora = IntVar()

            self.variable_tarifa_personalizada_8_1 = IntVar()
            self.variable_tarifa_personalizada_8_2 = IntVar()
            self.variable_tarifa_personalizada_8_3 = IntVar()
            self.variable_tarifa_personalizada_8_hora = IntVar()

            self.variable_tarifa_personalizada_9_1 = IntVar()
            self.variable_tarifa_personalizada_9_2 = IntVar()
            self.variable_tarifa_personalizada_9_3 = IntVar()
            self.variable_tarifa_personalizada_9_hora = IntVar()

            self.variable_tarifa_personalizada_10_1 = IntVar()
            self.variable_tarifa_personalizada_10_2 = IntVar()
            self.variable_tarifa_personalizada_10_3 = IntVar()
            self.variable_tarifa_personalizada_10_hora = IntVar()

            self.variable_tarifa_personalizada_11_1 = IntVar()
            self.variable_tarifa_personalizada_11_2 = IntVar()
            self.variable_tarifa_personalizada_11_3 = IntVar()
            self.variable_tarifa_personalizada_11_hora = IntVar()

            self.variable_tarifa_personalizada_12_1 = IntVar()
            self.variable_tarifa_personalizada_12_2 = IntVar()
            self.variable_tarifa_personalizada_12_3 = IntVar()
            self.variable_tarifa_personalizada_12_hora = IntVar()

            self.variable_tarifa_personalizada_13_1 = IntVar()
            self.variable_tarifa_personalizada_13_2 = IntVar()
            self.variable_tarifa_personalizada_13_3 = IntVar()
            self.variable_tarifa_personalizada_13_hora = IntVar()

            self.variable_tarifa_personalizada_14_1 = IntVar()
            self.variable_tarifa_personalizada_14_2 = IntVar()
            self.variable_tarifa_personalizada_14_3 = IntVar()
            self.variable_tarifa_personalizada_14_hora = IntVar()

            self.variable_tarifa_personalizada_15_1 = IntVar()
            self.variable_tarifa_personalizada_15_2 = IntVar()
            self.variable_tarifa_personalizada_15_3 = IntVar()
            self.variable_tarifa_personalizada_15_hora = IntVar()

            self.variable_tarifa_personalizada_16_1 = IntVar()
            self.variable_tarifa_personalizada_16_2 = IntVar()
            self.variable_tarifa_personalizada_16_3 = IntVar()
            self.variable_tarifa_personalizada_16_hora = IntVar()

            self.variable_tarifa_personalizada_17_1 = IntVar()
            self.variable_tarifa_personalizada_17_2 = IntVar()
            self.variable_tarifa_personalizada_17_3 = IntVar()
            self.variable_tarifa_personalizada_17_hora = IntVar()

            self.variable_tarifa_personalizada_18_1 = IntVar()
            self.variable_tarifa_personalizada_18_2 = IntVar()
            self.variable_tarifa_personalizada_18_3 = IntVar()
            self.variable_tarifa_personalizada_18_hora = IntVar()

            self.variable_tarifa_personalizada_19_1 = IntVar()
            self.variable_tarifa_personalizada_19_2 = IntVar()
            self.variable_tarifa_personalizada_19_3 = IntVar()
            self.variable_tarifa_personalizada_19_hora = IntVar()

            self.variable_tarifa_personalizada_20_1 = IntVar()
            self.variable_tarifa_personalizada_20_2 = IntVar()
            self.variable_tarifa_personalizada_20_3 = IntVar()
            self.variable_tarifa_personalizada_20_hora = IntVar()

            self.variable_tarifa_personalizada_21_1 = IntVar()
            self.variable_tarifa_personalizada_21_2 = IntVar()
            self.variable_tarifa_personalizada_21_3 = IntVar()
            self.variable_tarifa_personalizada_21_hora = IntVar()

            self.variable_tarifa_personalizada_22_1 = IntVar()
            self.variable_tarifa_personalizada_22_2 = IntVar()
            self.variable_tarifa_personalizada_22_3 = IntVar()
            self.variable_tarifa_personalizada_22_hora = IntVar()

            self.variable_tarifa_personalizada_23_1 = IntVar()
            self.variable_tarifa_personalizada_23_2 = IntVar()
            self.variable_tarifa_personalizada_23_3 = IntVar()
            self.variable_tarifa_personalizada_23_hora = IntVar()

            self.variable_tarifa_personalizada_24_1 = IntVar()
            self.variable_tarifa_personalizada_24_2 = IntVar()
            self.variable_tarifa_personalizada_24_3 = IntVar()
            self.variable_tarifa_personalizada_24_hora = IntVar()

            self.name_promocion = StringVar()
            self.id_promocion = StringVar()
            self.variable_promo_selected = StringVar()
            self.variable_nombre_estacionamiento = StringVar(
                value=self.nombre_estacionamiento)
            self.variable_correo_estacionamiento = StringVar(value=self.email)

            value = "" if self.without_decode_email_system else self.instance_tools.descifrar_AES(
                self.__password__, bytes.fromhex(self.__iv_password__))
            self.__variable_contraseña_correo__ = StringVar(value=value)
            value = None

            self.variable_contraseña_modulo_pensionados = StringVar(
                value=self.instance_tools.descifrar_AES(self.__contraseña_pensionados__, bytes.fromhex(self.__iv_pensionados__)))

            self.variable_path_logo = StringVar(value=self.logo)
            self.variable_logo_empresa = StringVar(value=self.logo_empresa)
            self.variable_imagen_marcas_auto = StringVar(
                value=self.imagen_marcas_auto)

            self.variable_db_usuario = StringVar(value=self.db_usser)
            self.__variable_db_contraseña__ = StringVar(
                value=self.instance_tools.descifrar_AES(self.__db_password__, bytes.fromhex(self.__db_iv__)))
            self.variable_db_host = StringVar(value=self.db_host)
            self.variable_db_db = StringVar(value=self.db_db)

            self.variable_destinatario_db = StringVar(
                value=self.destinatario_DB)
            self.variable_destinatario_corte = Variable(
                value=self.destinatario_corte)
            self.variable_destinatario_notificaciones = Variable(
                value=self.destinatario_notificaciones)

            self.variable_id_vendor_impresora = StringVar(
                value=self.printer_idVendor)
            self.variable_id_product_impresora = StringVar(
                value=self.printer_idProduct)

            self.variable_usuario_panel_usuarios = StringVar(
                value=self.usuario_panel_usuarios)
            self.variable_contraseña_panel_usuarios = StringVar(
                value=self.instance_tools.descifrar_AES(self.__contraseña_panel_usuarios__, bytes.fromhex(self.__iv_panel_usuarios__)))

            self.variable_usuario_panel_config = StringVar(
                value=self.usuario_panel_config)
            self.variable_contraseña_panel_config = StringVar(
                value=self.instance_tools.descifrar_AES(self.__contraseña_panel_config__, bytes.fromhex(self.__iv_panel_config__)))

            self.variable_formato_fecha_interface = StringVar(
                value=self.date_examples[self.date_format_interface])
            self.variable_formato_fecha_boleto = StringVar(
                value=self.date_examples[self.date_format_ticket])
            self.variable_formato_fecha_reloj = StringVar(
                value=self.date_examples[self.date_format_clock])
            self.variable_fuente_sistema = StringVar(value=self.fuente_sistema)
            self.variable_color_botones_sistema = StringVar(
                value=self.button_color)
            self.variable_color_letra_botones_sistema = StringVar(
                value=self.button_letters_color)
            self.variable_color_boton_cobro = StringVar(
                value=self.button_color_cobro)
            self.variable_color_letra_boton_cobro = StringVar(
                value=self.button_letters_color_cobro)

            self.variable_color_primera_hora = StringVar(
                value=self.color_primera_hora)
            self.variable_color_1_4_hora = StringVar(
                value=self.color_1_fraccion)
            self.variable_color_2_4_hora = StringVar(
                value=self.color_2_fraccion)
            self.variable_color_3_4_hora = StringVar(
                value=self.color_3_fraccion)
            self.variable_color_hora_completa = StringVar(
                value=self.color_hora_completa)
            self.variable_color_alerta = StringVar(value=self.color_alerta)

            self.variable_tipo_tarifa_sistema = BooleanVar(
                value=self.tipo_tarifa_sistema)

            self.variable_is_sensilla = BooleanVar()
            self.variable_is_personalizada = BooleanVar()

            self.variable_type_qr = BooleanVar()
            self.variable_type_button = BooleanVar()

            self.variable_requiere_placa = BooleanVar(
                value=self.requiere_placa)
            self.variable_penalizacion_boleto_perdido = BooleanVar(
                value=self.penalizacion_con_importe)
            self.variable_reloj_habilitado = BooleanVar(value=self.show_clock)
            self.variable_envio_informacion = BooleanVar(
                value=self.envio_informacion)
            self.variable_pantalla_completa = BooleanVar(
                value=self.pantalla_completa)

            self.variable_imprime_contra_parabrisas = BooleanVar(
                value=self.imprime_contra_parabrisas)
            self.variable_imprime_contra_localizacion = BooleanVar(
                value=self.imprime_contra_localizacion)
            self.variable_solicita_datos_del_auto = BooleanVar(
                value=self.solicita_datos_del_auto)
            self.variable_habilita_impresion_boleto_perdido = BooleanVar(
                value=self.habilita_impresion_boleto_perdido)

            self.variable_size_font_boleto = IntVar(
                value=self.size_font_boleto)
            self.variable_size_font_contra_parabrisas = IntVar(
                value=self.size_font_contra_parabrisas)
            self.variable_size_font_contra_localizacion = IntVar(
                value=self.size_font_contra_localizacion)

            self.visible_password_info_estacionamiento = BooleanVar(
                value=False)
            self.visible_password_modulo_pensionados = BooleanVar(value=False)
            self.visible_password_db = BooleanVar(value=False)
            self.visible_password_config_panel_usuarios = BooleanVar(
                value=False)
            self.visible_password_config_panel_config = BooleanVar(value=False)

            self.variable_costo_tarjeta = IntVar(value=self.valor_tarjeta)

            self.clean_data_form_tarifa(False)

            self.is_new_promo = True

        except Exception as e:
            mb.showerror(
                "Error", f"Error al cargar configuracion, inicie de nuevo el sistema.\n\nEn caso de que el error continue contacte a un administrador inmediatamente y muestre el siguiente error:\n\n\n{e}")
            raise SystemExit()

    def interface(self) -> None:
        modulo_configuracion = Frame(self.configuracion)
        modulo_configuracion.grid(
            column=0, row=0, padx=0, pady=0)

        self.cuaderno_configuracion = ttk.Notebook(modulo_configuracion)
        self.cuaderno_configuracion.grid(
            column=0, row=0, padx=0, pady=0)

        self.cuaderno_configuracion.bind(
            "<<NotebookTabChanged>>", self.on_tab_changed_config)

        self.view_config_interface_general()
        self.view_config_interface_interface()

        if self.system_to_load == 0:
            self.view_config_interface_tarifa()

        self.view_config_interface_funcionamiento_interno()

    def on_tab_changed_config(self, event):
        # Obtener el indice de la página actual
        new_page = self.cuaderno_configuracion.index("current")

        # Limpiar el contenido de la página anterior
        if self.current_page is not None:
            if self.system_to_load == 0:
                if self.current_page == 0:
                    self.clean_data_form_general()

                elif self.current_page == 1:
                    self.clean_data_form_interface()

                elif self.current_page == 2:
                    self.clean_data_form_tarifa()
                    self.clear_frame_tarifa()

                elif self.current_page == 3:
                    self.clean_data_form_interna()
            else:
                if self.current_page == 0:
                    self.clean_data_form_general()

                elif self.current_page == 1:
                    self.clean_data_form_interface()

                elif self.current_page == 2:
                    self.clean_data_form_interna()

        # Actualizar la página actual
        self.current_page = new_page

    def view_config_interface_tarifa(self):
        # Seccion para Tarifa
        seccion_configuracion_tarifa = Frame(self.cuaderno_configuracion)
        self.cuaderno_configuracion.add(
            seccion_configuracion_tarifa, text="Tarifas")

        seccion_configuracion_tarifa = LabelFrame(seccion_configuracion_tarifa)
        seccion_configuracion_tarifa.pack(
            expand=True, padx=0, pady=0, anchor='n')

        # Agregar otro cuaderno a seccion_configuracion_tarifa
        self.cuaderno_tarifa = ttk.Notebook(seccion_configuracion_tarifa)
        self.cuaderno_tarifa.grid(
            column=0, row=1, padx=0, pady=0)
        self.cuaderno_tarifa.bind(
            "<<NotebookTabChanged>>", self.on_tab_changed_config_tarifa)

        # Pestaña Tarifa General
        self.frame_tarifa_general = Frame(self.cuaderno_tarifa)
        self.cuaderno_tarifa.add(
            self.frame_tarifa_general, text="Tarifa general")

        self.frame_tarifa_general = Frame(self.frame_tarifa_general)
        self.frame_tarifa_general.pack(expand=True, padx=0, pady=0, anchor='n')

        frame_superior = Frame(self.frame_tarifa_general)
        frame_superior.grid(
            column=0, row=0, padx=0, pady=0)

        frame_Xd = Frame(frame_superior)
        frame_Xd.grid(
            column=0, row=0, padx=0, pady=0)

        frame = Frame(frame_Xd)
        frame.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)

        label = Label(frame,
                      text="Importe de boleto perdido", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=4, pady=3, sticky=NW)
        self.variable_importe_boleto_perdido.set(self.tarifa_boleto_perdido)
        entry_importe_boleto_perdido = Entry(
            frame, width=5, textvariable=self.variable_importe_boleto_perdido, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_boleto_perdido.grid(
            column=1, row=0, padx=4, pady=3, sticky=NW)

        self.label_tipo_promo = Label(
            frame_Xd, font=self.font_subtittle_system, bd=1, relief="solid")
        self.label_tipo_promo.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        self.boton_cambiar_tarifa = Button(
            frame_superior, text="Cambiar tipo de tarifa", height=1, anchor="center", font=self.font_subtittle_system, command=self.change_tarifa, background=self.button_color, fg=self.button_letters_color)
        self.boton_cambiar_tarifa.grid(
            column=2, row=0, padx=3, pady=3)

        self.frame_form_tarifa_general = Frame(self.frame_tarifa_general)
        self.frame_form_tarifa_general.grid(
            column=0, row=1, padx=0, pady=0)

        if self.tipo_tarifa_sistema:
            self.load_form_tarifa_simple()
        else:
            self.load_form_tarifa_avanzada()

        frame = Frame(self.frame_tarifa_general)
        frame.grid(
            column=0, row=2, padx=0, pady=0)

        boton_guardar = Button(frame, text="Guardar configuracion de tarifa", height=1, anchor="center", font=self.font_botones_interface,
                               background=self.button_color, fg=self.button_letters_color, command=self.save_data_tarifa)
        boton_guardar.grid(
            column=0, row=0, padx=3, pady=3)

        boton_cancelar = Button(frame, text="Cancelar", height=1, anchor="center", font=self.font_botones_interface,
                                background=self.button_color, fg=self.button_letters_color, command=self.clean_data_form_tarifa)
        boton_cancelar.grid(
            column=1, row=0, padx=3, pady=3)

        # Agrega seccion a self.cuaderno_configuracion
        self.tarifas_promociones_frame = Frame(self.cuaderno_tarifa)
        self.cuaderno_tarifa.add(
            self.tarifas_promociones_frame, text="Promociones")

        self.tarifas_promociones_frame = Frame(self.tarifas_promociones_frame)
        self.tarifas_promociones_frame.pack(
            expand=True, padx=0, pady=0, anchor='n')

        labelframe_form_info_tarifas = LabelFrame(
            self.tarifas_promociones_frame, text="Administracion de promociones", font=self.font_subtittle_system)
        labelframe_form_info_tarifas.grid(
            column=0, row=0, padx=0, pady=0)

        frame = Frame(labelframe_form_info_tarifas)
        frame.grid(
            column=0, row=0, padx=0, pady=0)

        checkbox_tarifa_sensilla = Checkbutton(frame, text="Tarifa Normal", variable=self.variable_is_sensilla, command=lambda:
                                               {self.instance_tools.cambiar_valor(self.variable_is_sensilla, self.variable_is_personalizada,
                                                                                  lambda: self.load_form_tarifa())}, font=self.font_text_interface)
        checkbox_tarifa_sensilla.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)

        checkbox_tarifa_personalizada = Checkbutton(frame, text="Tarifa Personalizada", variable=self.variable_is_personalizada, command=lambda:
                                                    {self.instance_tools.cambiar_valor(self.variable_is_personalizada, self.variable_is_sensilla,
                                                                                       lambda: self.load_form_tarifa())}, font=self.font_text_interface)
        checkbox_tarifa_personalizada.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)

        frame = Frame(labelframe_form_info_tarifas)
        frame.grid(
            column=1, row=0, padx=0, pady=0)

        checkbox_type_qr = Checkbutton(frame, text="Tipo QR", variable=self.variable_type_qr, command=lambda:
                                       {self.instance_tools.cambiar_valor(self.variable_type_qr, self.variable_type_button,
                                                                          lambda: self.update_interface_ID())}, font=self.font_text_interface)
        checkbox_type_qr.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)

        checkbox_type_button = Checkbutton(frame, text="Tipo Boton", variable=self.variable_type_button, command=lambda:
                                           {self.instance_tools.cambiar_valor(self.variable_type_button, self.variable_type_qr,
                                                                              lambda: self.update_interface_ID())}, font=self.font_text_interface)
        checkbox_type_button.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)

        self.labelframe_identity_promo = Frame(labelframe_form_info_tarifas)
        self.labelframe_identity_promo.grid(
            column=2, row=0, padx=0, pady=0)

        label = Label(
            self.labelframe_identity_promo, text="Nombre", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)
        self.entry_nombre_promocion = Entry(
            self.labelframe_identity_promo, width=10, textvariable=self.name_promocion, justify='center', font=self.font_text_interface)
        self.entry_nombre_promocion.grid(
            column=1, row=0, padx=0, pady=0)

        self.label_id_promocion = Label(
            self.labelframe_identity_promo, text="ID", font=self.font_text_interface)
        self.label_id_promocion.grid(
            column=0, row=1, padx=0, pady=0)
        self.entry_id_promocion = Entry(
            self.labelframe_identity_promo, width=10, textvariable=self.id_promocion, justify='center', font=self.font_text_interface)
        self.entry_id_promocion.grid(
            column=1, row=1, padx=0, pady=0)

        self.label_id_promocion.destroy()
        self.entry_id_promocion.destroy()

        self.combobox_promociones = ttk.Combobox(
            labelframe_form_info_tarifas, width=13, state="readonly", textvariable=self.variable_promo_selected, font=self.font_text_interface)
        self.combobox_promociones["values"] = [
            "Seleccione una opcion"] + self.promociones
        self.combobox_promociones.current(0)
        self.combobox_promociones.grid(
            column=4, row=0, padx=3, pady=3)

        self.boton_ver_tarifa = Button(
            labelframe_form_info_tarifas, height=1, anchor="center", text="Ver tarifa", font=self.font_botones_interface, background=self.button_color, fg=self.button_letters_color, command=self.load_data_form_tarifa)
        self.boton_ver_tarifa.grid(
            column=5, row=0, padx=3, pady=3)

        self.labelframe_form_tarifas = Frame(self.tarifas_promociones_frame)
        self.labelframe_form_tarifas.grid(
            column=0, row=3, padx=3, pady=0)

    def on_tab_changed_config_tarifa(self, event):
        # Obtener el indice de la página actual
        new_page = self.cuaderno_tarifa.index("current")

        # Limpiar el contenido de la página anterior
        if new_page == 0:
            self.clean_data_form_tarifa()

        elif new_page == 1:
            self.clear_frame_tarifa()

    def view_config_interface_general(self):
        seccion_configuracion_general = Frame(self.cuaderno_configuracion)
        self.cuaderno_configuracion.add(
            seccion_configuracion_general, text="General")

        seccion_configuracion_general = LabelFrame(
            seccion_configuracion_general)
        seccion_configuracion_general.pack(
            expand=True, padx=0, pady=0, anchor='n')

        labelframe_xd = Frame(seccion_configuracion_general)
        labelframe_xd.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)

        labelframe_izquierdo = Frame(labelframe_xd)
        labelframe_izquierdo.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)

        labelframe_derecho = Frame(labelframe_xd)
        labelframe_derecho.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe = Frame(labelframe_izquierdo)
        labelframe.grid(
            column=0, row=0, padx=3, pady=0, sticky=NW)

        labelframe_formulario_info_general_estacionamiento = LabelFrame(
            labelframe, text="Informacion del estacionamiento", font=self.font_subtittle_system)
        labelframe_formulario_info_general_estacionamiento.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_formulario_info_general_estacionamiento, text="Nombre", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        entry_nombre_estacionamiento = Entry(
            labelframe_formulario_info_general_estacionamiento, width=22, textvariable=self.variable_nombre_estacionamiento, justify='center', font=self.font_text_interface)
        entry_nombre_estacionamiento.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_formulario_info_general_estacionamiento, text="Correo", font=self.font_text_interface)
        label.grid(
            column=0, row=4, padx=3, pady=3, sticky=NW)

        self.entry_correo_estacionamiento = Entry(
            labelframe_formulario_info_general_estacionamiento, width=22, textvariable=self.variable_correo_estacionamiento, justify='center', font=self.font_text_interface, state=self.state_form_config)
        self.entry_correo_estacionamiento.grid(
            column=1, row=4, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_formulario_info_general_estacionamiento, text="Contraseña", font=self.font_text_interface)
        label.grid(
            column=0, row=5, padx=3, pady=3, sticky=W)

        self.entry_contraseña_correo = Entry(
            labelframe_formulario_info_general_estacionamiento, show="*", width=22, textvariable=self.__variable_contraseña_correo__, justify='center', font=self.font_text_interface, state=self.state_form_config)
        self.entry_contraseña_correo.grid(
            column=1, row=5, padx=3, pady=3)

        self.boton_hide_view_password_info_estacionamiento = ttk.Button(
            labelframe_formulario_info_general_estacionamiento, image=self.hide_password_icon, command=lambda: self.instance_tools.visible_password(
                self.boton_hide_view_password_info_estacionamiento, self.entry_contraseña_correo, self.visible_password_info_estacionamiento, self.show_password_icon, self.hide_password_icon), state=self.state_form_config)
        self.boton_hide_view_password_info_estacionamiento.grid(
            column=2, row=5, padx=3, pady=3)

        label = Label(
            labelframe_formulario_info_general_estacionamiento, text="Cantidad de cajones", font=self.font_text_interface)
        label.grid(
            column=0, row=6, padx=3, pady=3, sticky=NW)
        self.variable_cantidad_cajones.set(self.cantidad_cajones)
        entry_cantidad_cajones = Entry(
            labelframe_formulario_info_general_estacionamiento, width=22, textvariable=self.variable_cantidad_cajones, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'), state=self.state_form_config)
        entry_cantidad_cajones.grid(
            column=1, row=6, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_formulario_info_general_estacionamiento, text="Nombre de entrada\n(Para boleto)", font=self.font_text_interface)
        label.grid(
            column=0, row=7, padx=3, pady=3)
        entry_cantidad_cajones = Entry(
            labelframe_formulario_info_general_estacionamiento, width=22, textvariable=self.variable_nombre_entrada, justify='center', font=self.font_text_interface)
        entry_cantidad_cajones.grid(
            column=1, row=7, padx=3, pady=3)

        labelframe = LabelFrame(
            labelframe_izquierdo, text="Configuracion del sistema", font=self.font_subtittle_system)
        labelframe.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        labelframe_formulario_config_estacionamiento = LabelFrame(
            labelframe, text="Opciones de configuracion", font=self.font_subtittle_system)
        labelframe_formulario_config_estacionamiento.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        entry_requiere_placa = Checkbutton(
            labelframe_formulario_config_estacionamiento, variable=self.variable_requiere_placa, justify='center', text="Requiere placa para generar\nboleto", font=self.font_text_interface)
        entry_requiere_placa.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)

        entry_penalizacion_bolet_perdido = Checkbutton(
            labelframe_formulario_config_estacionamiento, variable=self.variable_penalizacion_boleto_perdido, justify='center', text="Suma  penalizacion de boleto\nperdido a importe", font=self.font_text_interface, state=self.state_form_config)
        entry_penalizacion_bolet_perdido.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)

        entry_reloj_habilitado = Checkbutton(
            labelframe_formulario_config_estacionamiento, variable=self.variable_reloj_habilitado, justify='center', text="Reloj habilitado", font=self.font_text_interface, state=self.state_form_config)
        entry_reloj_habilitado.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)

        entry_formato_envio_informacion = Checkbutton(
            labelframe_formulario_config_estacionamiento, variable=self.variable_envio_informacion, justify='center', text="Envio de informacion", font=self.font_text_interface, state=self.state_form_config)
        entry_formato_envio_informacion.grid(
            column=0, row=4, padx=0, pady=0, sticky=NW)

        entry_formato_pantalla_completa = Checkbutton(
            labelframe_formulario_config_estacionamiento, variable=self.variable_pantalla_completa, justify='center', text="Pantalla completa", font=self.font_text_interface)
        entry_formato_pantalla_completa.grid(
            column=0, row=5, padx=0, pady=0, sticky=NW)

        entry_imprime_contra_parabrisas = Checkbutton(
            labelframe_formulario_config_estacionamiento, variable=self.variable_imprime_contra_parabrisas, justify='center', text="Imprime contra de parabrisas", font=self.font_text_interface)
        entry_imprime_contra_parabrisas.grid(
            column=0, row=7, padx=0, pady=0, sticky=NW)

        entry_imprime_contra_localizacion = Checkbutton(
            labelframe_formulario_config_estacionamiento, variable=self.variable_imprime_contra_localizacion, justify='center', text="Imprime contra de localizacion", font=self.font_text_interface)
        entry_imprime_contra_localizacion.grid(
            column=0, row=8, padx=0, pady=0, sticky=NW)

        entry_solicita_datos_del_auto = Checkbutton(
            labelframe_formulario_config_estacionamiento, variable=self.variable_solicita_datos_del_auto, justify='center', text="Solicita datos del auto", font=self.font_text_interface)
        entry_solicita_datos_del_auto.grid(
            column=0, row=9, padx=0, pady=0, sticky=NW)

        entry_habilita_impresion_boleto_perdido = Checkbutton(
            labelframe_formulario_config_estacionamiento, variable=self.variable_habilita_impresion_boleto_perdido, justify='center', text="Habilita impresion de boleto perdido", font=self.font_text_interface, state=self.state_form_config)
        entry_habilita_impresion_boleto_perdido.grid(
            column=0, row=10, padx=0, pady=0, sticky=NW)

        list_size_font_tiket = [1, 2, 3]

        frame = LabelFrame(
            labelframe, text="Tamaño de letra\nde boleto", font=self.font_subtittle_system)
        frame.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        label = Label(
            frame, text="Boleto normal", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        combobox_size_font_ticket = ttk.Combobox(
            frame, width=2, state="readonly", textvariable=self.variable_size_font_boleto, font=self.font_text_interface, justify='center', values=list_size_font_tiket)
        combobox_size_font_ticket.grid(
            column=1, row=0, padx=3, pady=3, sticky=W)

        label = Label(
            frame, text="Contra de\nparabrisas", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        combobox_size_font_ticket = ttk.Combobox(
            frame, width=2, state="readonly", textvariable=self.variable_size_font_contra_parabrisas, font=self.font_text_interface, justify='center', values=list_size_font_tiket)
        combobox_size_font_ticket.grid(
            column=1, row=1, padx=3, pady=3, sticky=W)

        label = Label(
            frame, text="Contra de\nlocalizacion", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=3, pady=3, sticky=NW)

        combobox_size_font_ticket = ttk.Combobox(
            frame, width=2, state="readonly", textvariable=self.variable_size_font_contra_localizacion, font=self.font_text_interface, justify='center', values=list_size_font_tiket)
        combobox_size_font_ticket.grid(
            column=1, row=2, padx=3, pady=3, sticky=W)

        if self.system_to_load == 0:
            labelframe = LabelFrame(
                labelframe_izquierdo, text="Configuracion de pensionados", font=self.font_subtittle_system)
            labelframe.grid(
                column=0, row=2, padx=3, pady=3, sticky=NW)

            labelframe_formulario_pensionados = Frame(labelframe)
            labelframe_formulario_pensionados.grid(
                column=0, row=0, padx=3, pady=3, sticky=NW)

            label = Label(
                labelframe_formulario_pensionados, text="Contraseña del modulo", font=self.font_text_interface)
            label.grid(
                column=0, row=0, padx=3, pady=3, sticky=W)

            self.entry_contraseña_modulo_pensionados = Entry(
                labelframe_formulario_pensionados, show="*", width=9, textvariable=self.variable_contraseña_modulo_pensionados, justify='center', font=self.font_text_interface)
            self.entry_contraseña_modulo_pensionados.grid(
                column=1, row=0, padx=3, pady=3)

            self.boton_hide_view_password_modulo_pensionados = ttk.Button(
                labelframe_formulario_pensionados, image=self.hide_password_icon, command=lambda: self.instance_tools.visible_password(
                    self.boton_hide_view_password_modulo_pensionados, self.entry_contraseña_modulo_pensionados, self.visible_password_modulo_pensionados, self.show_password_icon, self.hide_password_icon))
            self.boton_hide_view_password_modulo_pensionados.grid(
                column=2, row=0, padx=3, pady=3)

            label = Label(
                labelframe_formulario_pensionados, text="Costo de tarjeta/tarjeton", font=self.font_text_interface)
            label.grid(
                column=0, row=1, padx=3, pady=3, sticky=NW)
            entry_costo_tarjeta = Entry(
                labelframe_formulario_pensionados, width=9, textvariable=self.variable_costo_tarjeta, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
            entry_costo_tarjeta.grid(
                column=1, row=1, padx=3, pady=3, sticky=NW)

            label = Label(
                labelframe_formulario_pensionados, text="Costo reposicion de tarjeta/tarjeton", font=self.font_text_interface)
            label.grid(
                column=0, row=2, padx=3, pady=3, sticky=NW)
            self.variable_costo_reposicion.set(self.valor_reposicion_tarjeta)
            entry_costo_reposicion = Entry(
                labelframe_formulario_pensionados, width=9, textvariable=self.variable_costo_reposicion, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
            entry_costo_reposicion.grid(
                column=1, row=2, padx=3, pady=3, sticky=NW)

            label = Label(
                labelframe_formulario_pensionados, text="Penalizacion diaria por pago atrasado", font=self.font_text_interface)
            label.grid(
                column=0, row=3, padx=3, pady=3, sticky=NW)
            self.variable_penalizacion_diaria.set(
                self.penalizacion_diaria_pension)
            entry_penalizacion_diaria = Entry(
                labelframe_formulario_pensionados, width=9, textvariable=self.variable_penalizacion_diaria, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
            entry_penalizacion_diaria.grid(
                column=1, row=3, padx=3, pady=3, sticky=NW)

        labelframe = LabelFrame(
            labelframe_derecho, text="Configuracion de imagenes de boleto", font=self.font_subtittle_system)
        labelframe.grid(
            column=1, row=0, padx=3, pady=3, sticky=NW)

        labelframe_formulario_boletos = Frame(labelframe)
        labelframe_formulario_boletos.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)

        labelframe_imagenes = Frame(labelframe_formulario_boletos)
        labelframe_imagenes.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe_logo = LabelFrame(
            labelframe_imagenes, text="Logo de empresa", font=self.font_subtittle_system)
        labelframe_logo.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)

        frame = Frame(labelframe_logo)
        frame.grid(
            column=0, row=0, padx=3, pady=3)

        label_logo = Label(frame)
        label_logo.grid(
            column=0, row=0, padx=3, pady=3)

        self.instance_tools.load_image(
            label_image=label_logo, path_image=self.logo, scale_image=self.scale_image)

        boton = Button(
            frame, text="Seleccionar logo", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton.configure(command=lambda:self.change_image_and_save_change(label_logo, self.variable_path_logo, "Logo de la empresa", "N/A", "N/A"))
        boton.grid(
            column=0, row=1, padx=2, pady=2)

        labelframe_imagen_carro = LabelFrame(
            labelframe_imagenes, text="Imagen de marcas de auto", font=self.font_subtittle_system)
        labelframe_imagen_carro.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        frame = Frame(labelframe_imagen_carro)
        frame.grid(
            column=0, row=0, padx=3, pady=3)

        label_marcas_auto = Label(frame)
        label_marcas_auto.grid(
            column=0, row=0, padx=3, pady=3)

        self.instance_tools.load_image(
            label_image=label_marcas_auto, path_image=self.imagen_marcas_auto)

        boton = Button(
            frame, text="Cambiar Imagen", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton.configure(
            command=lambda: self.change_image_and_save_change(label_marcas_auto, self.variable_imagen_marcas_auto, "Imagen de marcas de auto", "N/A", "N/A"))
        boton.grid(
            column=0, row=1, padx=2, pady=2)

        labelframe_generar_imagen = Frame(labelframe_formulario_boletos)
        labelframe_generar_imagen.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)

        labelframe_empresa = LabelFrame(
            labelframe_generar_imagen, font=self.font_subtittle_system, text="Datos de la empresa")
        labelframe_empresa.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        labelframe_form_empresa = Frame(labelframe_empresa)
        labelframe_form_empresa.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_empresa, text="Nombre", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)
        self.entry_nombre_empresa = Entry(
            labelframe_form_empresa, width=10, justify='center', font=self.font_text_interface)
        self.entry_nombre_empresa.grid(
            column=1, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_empresa, text="RFC", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)
        self.entry_RFC_empresa = Entry(
            labelframe_form_empresa, width=10, justify='center', font=self.font_text_interface)
        self.entry_RFC_empresa.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_empresa, text="Calle y número", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=3, pady=3)
        self.entry_calle_numero_empresa = Entry(
            labelframe_form_empresa, width=10, justify='center', font=self.font_text_interface)
        self.entry_calle_numero_empresa.grid(
            column=1, row=2, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_empresa, text="Colonia", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=3, pady=3, sticky=NW)
        self.entry_colonia_empresa = Entry(
            labelframe_form_empresa, width=10, justify='center', font=self.font_text_interface)
        self.entry_colonia_empresa.grid(
            column=1, row=3, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_empresa, text="CP", font=self.font_text_interface)
        label.grid(
            column=0, row=4, padx=3, pady=3, sticky=NW)
        self.entry_CP_empresa = Entry(
            labelframe_form_empresa, width=10, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        self.entry_CP_empresa.grid(
            column=1, row=4, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_empresa, text="Alcaldia", font=self.font_text_interface)
        label.grid(
            column=0, row=5, padx=3, pady=3, sticky=NW)
        self.entry_alcaldia_empresa = Entry(
            labelframe_form_empresa, width=10, justify='center', font=self.font_text_interface)
        self.entry_alcaldia_empresa.grid(
            column=1, row=5, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_empresa, text="Entidad Estatal", font=self.font_text_interface)
        label.grid(
            column=0, row=6, padx=3, pady=3)
        self.entry_entidad_estatal_empresa = Entry(
            labelframe_form_empresa, width=10, justify='center', font=self.font_text_interface)
        self.entry_entidad_estatal_empresa.grid(
            column=1, row=6, padx=3, pady=3, sticky=NW)

        frame = Frame(labelframe_generar_imagen)
        frame.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        labelframe_sucursal = LabelFrame(
            frame, font=self.font_subtittle_system, text="Datos de la sucursal")
        labelframe_sucursal.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        labelframe_form_sucursal = Frame(labelframe_sucursal)
        labelframe_form_sucursal.grid(
            column=0, row=0, padx=3, pady=0, sticky=NW)

        label = Label(
            labelframe_form_sucursal, text="Calle y número", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=3, pady=3)
        self.entry_calle_numero_sucursal = Entry(
            labelframe_form_sucursal, width=10, justify='center', font=self.font_text_interface)
        self.entry_calle_numero_sucursal.grid(
            column=1, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_sucursal, text="Colonia", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)
        self.entry_colonia_sucursal = Entry(
            labelframe_form_sucursal, width=10, justify='center', font=self.font_text_interface)
        self.entry_colonia_sucursal.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_sucursal, text="CP", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=3, pady=3, sticky=NW)
        self.entry_CP_sucursal = Entry(
            labelframe_form_sucursal, width=10, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        self.entry_CP_sucursal.grid(
            column=1, row=2, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_sucursal, text="Alcaldia", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=3, pady=3, sticky=NW)
        self.entry_alcaldia_sucursal = Entry(
            labelframe_form_sucursal, width=10, justify='center', font=self.font_text_interface)
        self.entry_alcaldia_sucursal.grid(
            column=1, row=3, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_sucursal, text="Entidad Estatal", font=self.font_text_interface)
        label.grid(
            column=0, row=4, padx=3, pady=3)
        self.entry_entidad_estatal_sucursal = Entry(
            labelframe_form_sucursal, width=10, justify='center', font=self.font_text_interface)
        self.entry_entidad_estatal_sucursal.grid(
            column=1, row=4, padx=3, pady=3, sticky=NW)

        labelframe_sucursal = LabelFrame(
            frame, font=self.font_subtittle_system, text="Datos para facturacion")
        labelframe_sucursal.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        labelframe_form_sucursal = Frame(labelframe_sucursal)
        labelframe_form_sucursal.grid(
            column=0, row=0, padx=3, pady=0, sticky=NW)

        label = Label(
            labelframe_form_sucursal, text="Correo", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=3, pady=3)
        self.entry_correo_factura = Entry(
            labelframe_form_sucursal, width=13, justify='center', font=self.font_text_interface)
        self.entry_correo_factura.grid(
            column=1, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_sucursal, text="Número tel", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)
        self.entry_numero_factura = Entry(
            labelframe_form_sucursal, width=13, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        self.entry_numero_factura.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        labelframe_botones_xd = Frame(labelframe)
        labelframe_botones_xd.grid(
            column=0, row=2, padx=3, pady=3)

        self.label_logo_datos = Label(labelframe)
        self.label_logo_datos.grid(
            column=0, row=3, padx=3, pady=3)

        boton_cargar_imagen_datos = Button(
            labelframe_botones_xd, text="Cargar Imagen", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface, command=lambda: self.change_image_and_save_change(self.label_logo_datos, self.variable_logo_empresa, "Imagen de ticket con datos (Importa imagen)", "N/A", "N/A"))
        boton_cargar_imagen_datos.grid(
            column=0, row=0, padx=2, pady=2)

        boton_generar_imagen_datos = Button(
            labelframe_botones_xd, text="Generar Imagen", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface, command=self.draw_info)
        boton_generar_imagen_datos.grid(
            column=1, row=0, padx=2, pady=2)

        boton_eliminar_imagen_datos = Button(
            labelframe_botones_xd, text="Guardar Imagen", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface, command=self.backup_image_system)
        boton_eliminar_imagen_datos.grid(
            column=2, row=0, padx=2, pady=2)

        self.instance_tools.load_image(
            label_image=self.label_logo_datos, path_image=self.logo_empresa, scale_image=self.scale_image)

        frame = Frame(seccion_configuracion_general)
        frame.grid(
            column=0, row=1, padx=0, pady=0)

        boton_guardar = Button(frame, text="Guardar configuracion general", height=1, anchor="center", font=self.font_botones_interface,
                               background=self.button_color, fg=self.button_letters_color, command=self.save_data_general)
        boton_guardar.grid(
            column=0, row=0, padx=3, pady=3)

        boton_cancelar = Button(frame, height=1, text="Cancelar", anchor="center", background=self.button_color,
                                fg=self.button_letters_color, font=self.font_botones_interface, command=self.clean_data_form_general)
        boton_cancelar.grid(
            column=1, row=0, padx=3, pady=3)

    def change_image_and_save_change(self, label_logo: Label, variable_path:StringVar,
                                     nombre_cambio, valor_anterior, valor_nuevo):
        nombre_usuario_activo = self.DB.nombre_usuario_activo()

        is_changed = self.instance_tools.load_image(label_image=label_logo, variable=variable_path, scale_image=self.scale_image)

        if is_changed:
            self.cambios_model.add_change(
                nombre_cambio = nombre_cambio,valor_anterior=valor_anterior, valor_nuevo=valor_nuevo,
                tipo_cambio = "Configuracion de imagenes del sistema", nombre_usuario= nombre_usuario_activo)
        
            state = self.printer_controller.print_changes(
                "Cambios de configuracion de imagenes del sistema", {nombre_cambio})

            if state != None:
                mb.showwarning("Alerta", state)

    def view_config_interface_funcionamiento_interno(self):
        # Agrega seccion a self.cuaderno_configuracion
        seccion_configuracion_funcionamiento_interno = Frame(
            self.cuaderno_configuracion)
        self.cuaderno_configuracion.add(
            seccion_configuracion_funcionamiento_interno, text="Funcionamiento interno")

        seccion_configuracion_funcionamiento_interno = LabelFrame(
            seccion_configuracion_funcionamiento_interno)
        seccion_configuracion_funcionamiento_interno.pack(
            expand=True, padx=0, pady=0, anchor='n')

        labelframe_xd = Frame(seccion_configuracion_funcionamiento_interno)
        labelframe_xd.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)

        frame_der = Frame(labelframe_xd)
        frame_der.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)

        labelframe = LabelFrame(
            frame_der, text="Configuracion de base de datos", font=self.font_subtittle_system)
        labelframe.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        labelframe_formulario_db = Frame(labelframe)
        labelframe_formulario_db.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_formulario_db, text="Nombre de usuario", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)
        self.entry_db_usuario = Entry(
            labelframe_formulario_db, width=15, textvariable=self.variable_db_usuario, justify='center', font=self.font_text_interface, state='readonly')
        self.entry_db_usuario.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_formulario_db, text="Contraseña", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=3, pady=3, sticky=W)
        self.entry_variable_db_contraseña = Entry(
            labelframe_formulario_db, show="*", width=15, textvariable=self.__variable_db_contraseña__, justify='center', font=self.font_text_interface, state='readonly')
        self.entry_variable_db_contraseña.grid(
            column=1, row=2, padx=3, pady=3)

        def view_if_active_form():
            if self.state_form:
                self.instance_tools.visible_password(
                    self.boton_hide_view_password_db,
                    self.entry_variable_db_contraseña,
                    self.visible_password_db,
                    self.show_password_icon,
                    self.hide_password_icon)

        self.boton_hide_view_password_db = ttk.Button(
            labelframe_formulario_db, image=self.hide_password_icon, command=view_if_active_form)
        self.boton_hide_view_password_db.grid(
            column=2, row=2, padx=3, pady=3)

        label = Label(
            labelframe_formulario_db, text="Host", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=3, pady=3, sticky=NW)
        self.entry_db_host = Entry(
            labelframe_formulario_db, width=15, textvariable=self.variable_db_host, justify='center', font=self.font_text_interface, state='readonly')
        self.entry_db_host.grid(
            column=1, row=3, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_formulario_db, text="Base de datos", font=self.font_text_interface)
        label.grid(
            column=0, row=4, padx=3, pady=3, sticky=NW)
        self.entry_db_db = Entry(
            labelframe_formulario_db, width=15, textvariable=self.variable_db_db, justify='center', font=self.font_text_interface, state='readonly')
        self.entry_db_db.grid(
            column=1, row=4, padx=3, pady=3, sticky=NW)

        self.botton_state_form_db_config = Button(labelframe, text="Activar configuracion", height=1, anchor="center",
                                                  font=self.font_botones_interface, background=self.button_color, fg=self.button_letters_color, command=self.state_form_db_config)
        self.botton_state_form_db_config.grid(
            column=0, row=2, padx=3, pady=3)

        self.state_form = False

        labelframe = LabelFrame(
            frame_der, text="Configuracion de la impresora", font=self.font_subtittle_system)
        labelframe.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        labelframe_impresora_info_devices = Frame(labelframe)
        labelframe_impresora_info_devices.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_impresora_info_devices, text="Seleccione la\nimpresora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)
        combobox_dispositivos = ttk.Combobox(
            labelframe_impresora_info_devices, width=20, state="readonly", textvariable=self.variable_printer_system, font=self.font_text_interface, justify='center')
        combobox_dispositivos["values"] = self.list_devices
        combobox_dispositivos.bind(
            "<<ComboboxSelected>>", self.load_ids_printter)
        combobox_dispositivos.grid(
            column=1, row=0, padx=3, pady=3, sticky=W)

        labelframe_impresora_info = Frame(labelframe)
        labelframe_impresora_info.grid(
            column=0, row=2, padx=3, pady=3)

        label = Label(
            labelframe_impresora_info, text="ID Vendor", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        entry_id_vendor_impresora = Entry(
            labelframe_impresora_info, width=15, textvariable=self.variable_id_vendor_impresora, justify='center', font=self.font_text_interface, state='readonly')
        entry_id_vendor_impresora.grid(
            column=1, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_impresora_info, text="ID Product", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        entry_id_product_impresora = Entry(
            labelframe_impresora_info, width=15, textvariable=self.variable_id_product_impresora, justify='center', font=self.font_text_interface, state='readonly')
        entry_id_product_impresora.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        labelframe = LabelFrame(
            frame_der, text="Configuracion de uso del sistema", font=self.font_subtittle_system)
        labelframe.grid(
            column=0, row=2, padx=3, pady=3, sticky=NW)

        labelframe_uso_info = Frame(labelframe)
        labelframe_uso_info.grid(
            column=0, row=0, padx=3, pady=3)

        label = Label(
            labelframe_uso_info, text="Uso", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=3, pady=3)

        combobox__uso_sistema = ttk.Combobox(
            labelframe_uso_info, width=17, state="readonly", textvariable=self.variable_system_to_load, font=self.font_text_interface)
        combobox__uso_sistema["values"] = self.system_options
        combobox__uso_sistema.grid(
            column=1, row=0, padx=3, pady=3)

        frame_izq = Frame(labelframe_xd)
        frame_izq.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe = LabelFrame(
            frame_der, text="Cargar archivo de configuracion\ndel sistema", font=self.font_subtittle_system)
        labelframe.grid(
            column=0, row=3, padx=3, pady=3, sticky=NW)

        labelframe_load_config_file = Frame(labelframe)
        labelframe_load_config_file.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        boton_load_file = Button(
            labelframe_load_config_file, text="Importar archivo de configuracion", height=1, anchor="center", font=self.font_botones_interface, background=self.button_color, fg=self.button_letters_color, command=self.instance_config.replace_config_file)
        boton_load_file.grid(
            column=0, row=0, padx=3, pady=3)

        boton_load_file = Button(
            labelframe_load_config_file, text="Exportar archivo de configuracion", height=1, anchor="center", font=self.font_botones_interface, background=self.button_color, fg=self.button_letters_color, command=lambda:self.instance_config.backup_config_file(self.nombre_estacionamiento, self.system_options[self.system_to_load]))
        boton_load_file.grid(
            column=0, row=1, padx=3, pady=3)

        boton_view_history = Button(
            labelframe_load_config_file, text="Ver historial de cambios", height=1, anchor="center", font=self.font_botones_interface, background=self.button_color, fg=self.button_letters_color, command=self.view_changes)
        boton_view_history.grid(
            column=0, row=2, padx=3, pady=3)

        labelframe = LabelFrame(
            frame_izq, text="Configuracion de las credenciales\ndel panel de configuracion", font=self.font_subtittle_system)
        labelframe.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        labelframe_config_panel_config = Frame(labelframe)
        labelframe_config_panel_config.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_config_panel_config, text="Usuario", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        self.entry_usuario_panel_config = Entry(
            labelframe_config_panel_config, width=15, textvariable=self.variable_usuario_panel_config, justify='center', font=self.font_text_interface)
        self.entry_usuario_panel_config.grid(
            column=1, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_config_panel_config, text="Contraseña", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=W)

        self.entry_contraseña_panel_config = Entry(
            labelframe_config_panel_config, show="*", width=15, textvariable=self.variable_contraseña_panel_config, justify='center', font=self.font_text_interface)
        self.entry_contraseña_panel_config.grid(
            column=1, row=1, padx=3, pady=3)

        self.boton_hide_view_password_config_panel_config = ttk.Button(
            labelframe_config_panel_config, image=self.hide_password_icon, command=lambda: self.instance_tools.visible_password(
                self.boton_hide_view_password_config_panel_config, self.entry_contraseña_panel_config, self.visible_password_config_panel_config, self.show_password_icon, self.hide_password_icon))
        self.boton_hide_view_password_config_panel_config.grid(
            column=2, row=1, padx=3, pady=3)

        if self.system_to_load == 0:
            labelframe = LabelFrame(
                frame_izq, text="Configuracion de las credenciales\ndel panel de usuarios", font=self.font_subtittle_system)
            labelframe.grid(
                column=0, row=1, padx=3, pady=3, sticky=NW)

            labelframe_config_panel_usuarios = Frame(labelframe)
            labelframe_config_panel_usuarios.grid(
                column=0, row=1, padx=3, pady=3, sticky=NW)

            label = Label(
                labelframe_config_panel_usuarios, text="Usuario", font=self.font_text_interface)
            label.grid(
                column=0, row=0, padx=3, pady=3, sticky=NW)

            self.entry_usuario_panel_usuarios = Entry(
                labelframe_config_panel_usuarios, width=15, textvariable=self.variable_usuario_panel_usuarios, justify='center', font=self.font_text_interface)
            self.entry_usuario_panel_usuarios.grid(
                column=1, row=0, padx=3, pady=3, sticky=NW)

            label = Label(
                labelframe_config_panel_usuarios, text="Contraseña", font=self.font_text_interface)
            label.grid(
                column=0, row=1, padx=3, pady=3, sticky=W)

            self.entry_contraseña_panel_usuarios = Entry(
                labelframe_config_panel_usuarios, show="*", width=15, textvariable=self.variable_contraseña_panel_usuarios, justify='center', font=self.font_text_interface)
            self.entry_contraseña_panel_usuarios.grid(
                column=1, row=1, padx=3, pady=3)

            self.boton_hide_view_password_config_panel_usuarios = ttk.Button(
                labelframe_config_panel_usuarios, image=self.hide_password_icon, command=lambda: self.instance_tools.visible_password(
                    self.boton_hide_view_password_config_panel_usuarios, self.entry_contraseña_panel_usuarios, self.visible_password_config_panel_usuarios, self.show_password_icon, self.hide_password_icon))
            self.boton_hide_view_password_config_panel_usuarios.grid(
                column=2, row=1, padx=3, pady=3)

            labelframe = LabelFrame(
                frame_izq, text="Configuracion de envio de informacion", font=self.font_subtittle_system)
            labelframe.grid(
                column=0, row=2, padx=3, pady=3, sticky=NW)

            labelframe_formulario_config_envio = Frame(labelframe)
            labelframe_formulario_config_envio.grid(
                column=0, row=2, padx=3, pady=3, sticky=NW)

            frame_destinatario_db = Frame(labelframe_formulario_config_envio)
            frame_destinatario_db.grid(
                column=0, row=0, padx=3, pady=3, sticky=NW)
            label = Label(
                frame_destinatario_db, text="Destinatario de\nbase de datos", font=self.font_text_interface)
            label.grid(
                column=0, row=0, padx=3, pady=3, sticky=NW)
            self.entry_destinatario_db = Entry(
                frame_destinatario_db, width=30, textvariable=self.variable_destinatario_db, justify='left', font=self.font_text_interface)
            self.entry_destinatario_db.grid(
                column=1, row=0, padx=3, pady=3, sticky=NW)

            frame_destinatario_corte = Frame(
                labelframe_formulario_config_envio)
            frame_destinatario_corte.grid(
                column=0, row=1, padx=3, pady=3, sticky=NW)

            label = Label(
                frame_destinatario_corte, text="Destinatarios de\ncorte", font=self.font_text_interface)
            label.grid(
                column=0, row=0, padx=3, pady=3, sticky=W)

            frame_correo = Frame(frame_destinatario_corte)
            frame_correo.grid(column=1, row=0, padx=3, pady=3, sticky=W)

            listbox_correos_corte = Listbox(
                frame_correo, height=3, font=self.font_text_interface, listvariable=self.variable_destinatario_corte)
            listbox_correos_corte.grid(row=0, column=0, padx=5, pady=5)
            listbox_correos_corte.configure(width=25)

            scrollbar = ttk.Scrollbar(
                frame_correo, orient="vertical", command=listbox_correos_corte.yview)
            scrollbar.grid(row=0, column=1, sticky=NS)
            listbox_correos_corte.configure(yscrollcommand=scrollbar.set)

            frame_botones = Frame(frame_destinatario_corte)
            frame_botones.grid(row=0, column=2, padx=2, pady=2)

            boton_add_email = ttk.Button(frame_botones, image=self.plus_icon, command=lambda: self.add_email(
                "destinatario_corte", self.variable_destinatario_corte, listbox_correos_corte))
            boton_add_email.grid(column=0, row=0, padx=2, pady=2)

            boton_delete_email = ttk.Button(frame_botones, image=self.minus_icon, command=lambda: self.delete_email(
                "destinatario_corte", self.variable_destinatario_corte, listbox_correos_corte))
            boton_delete_email.grid(column=0, row=1, padx=2, pady=2)

            frame_destinatario_notificaciones = Frame(
                labelframe_formulario_config_envio)
            frame_destinatario_notificaciones.grid(
                column=0, row=3, padx=3, pady=3, sticky=NW)

            label = Label(
                frame_destinatario_notificaciones, text="Destinatarios de\nnotificaciones", font=self.font_text_interface)
            label.grid(
                column=0, row=0, padx=3, pady=3, sticky=W)

            frame_correo = Frame(frame_destinatario_notificaciones)
            frame_correo.grid(column=1, row=0, padx=3, pady=3, sticky=W)

            listbox_correos_notificacion = Listbox(
                frame_correo, height=3, font=self.font_text_interface, listvariable=self.variable_destinatario_notificaciones)
            listbox_correos_notificacion.grid(row=0, column=0, padx=5, pady=5)
            listbox_correos_notificacion.configure(width=25)

            scrollbar = ttk.Scrollbar(
                frame_correo, orient="vertical", command=listbox_correos_notificacion.yview)
            scrollbar.grid(row=0, column=1, sticky=NS)
            listbox_correos_notificacion.configure(
                yscrollcommand=scrollbar.set)

            frame_botones = Frame(frame_destinatario_notificaciones)
            frame_botones.grid(row=0, column=2, padx=2, pady=2)

            boton_add_email = ttk.Button(frame_botones, image=self.plus_icon, command=lambda: self.add_email(
                "destinatario_notificaciones", self.variable_destinatario_notificaciones, listbox_correos_notificacion))
            boton_add_email.grid(column=0, row=0, padx=2, pady=2)

            boton_delete_email = ttk.Button(frame_botones, image=self.minus_icon, command=lambda: self.delete_email(
                "destinatario_notificaciones", self.variable_destinatario_notificaciones, listbox_correos_notificacion))
            boton_delete_email.grid(column=0, row=1, padx=2, pady=2)

        frame = Frame(seccion_configuracion_funcionamiento_interno)
        frame.grid(
            column=0, row=1, padx=0, pady=0)

        key_word = ttk.Button(
            frame, image=self.config_icon, command=self.change_key_word)
        key_word.grid(column=0, row=0, padx=2, pady=2)

        boton_guardar = Button(frame, text="Guardar configuracion de funcionamiento interno", height=1, anchor="center",
                               font=self.font_botones_interface, background=self.button_color, fg=self.button_letters_color, command=self.save_data_interna)
        boton_guardar.grid(
            column=1, row=0, padx=3, pady=3)

        boton_cancelar = Button(frame, height=1, text="Cancelar", anchor="center", background=self.button_color,
                                fg=self.button_letters_color, font=self.font_botones_interface, command=self.clean_data_form_interna)
        boton_cancelar.grid(
            column=2, row=0, padx=3, pady=3)

        labelframe_impresora_info = Frame(labelframe)
        labelframe_impresora_info.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

    def view_changes(self):
        if ask_security_question(self.configuracion) != True:
            return

        self.instance_tools.desactivar(self.configuracion)
        ViewHitoryChanges()
        self.instance_tools.activar(self.configuracion)

    def view_config_interface_interface(self):
        # Agrega seccion a self.cuaderno_configuracion
        seccion_configuracion_interface = Frame(
            self.cuaderno_configuracion)
        self.cuaderno_configuracion.add(
            seccion_configuracion_interface, text="Interface")

        seccion_configuracion_interface = LabelFrame(
            seccion_configuracion_interface)
        seccion_configuracion_interface.pack(
            expand=True, padx=0, pady=0, anchor='n')

        labelframe_xd = Frame(seccion_configuracion_interface)
        labelframe_xd.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)

        labelframe = Frame(labelframe_xd)
        labelframe.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)

        labelframe_formulario_info_formatos = Frame(labelframe)
        labelframe_formulario_info_formatos.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)

        labelframe_form_format_dates = LabelFrame(
            labelframe_formulario_info_formatos, text="Formatos de fecha", font=self.font_subtittle_system)
        labelframe_form_format_dates.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_format_dates, text="Interface", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        combobox_formato_fecha_interface = ttk.Combobox(
            labelframe_form_format_dates, width=25, state="readonly", textvariable=self.variable_formato_fecha_interface, font=self.font_text_interface)
        combobox_formato_fecha_interface["values"] = self.date_examples
        combobox_formato_fecha_interface.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_format_dates, text="Boleto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=3, pady=3, sticky=NW)

        combobox_formato_fecha_boleto = ttk.Combobox(
            labelframe_form_format_dates, width=25, state="readonly", textvariable=self.variable_formato_fecha_boleto, font=self.font_text_interface)
        combobox_formato_fecha_boleto["values"] = self.date_examples
        combobox_formato_fecha_boleto.grid(
            column=1, row=2, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_format_dates, text="Reloj de expedidor", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=3, pady=3, sticky=NW)

        combobox_formato_fecha_reloj = ttk.Combobox(
            labelframe_form_format_dates, width=25, state="readonly", textvariable=self.variable_formato_fecha_reloj, font=self.font_text_interface)
        combobox_formato_fecha_reloj["values"] = self.date_examples
        combobox_formato_fecha_reloj.grid(
            column=1, row=3, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_format_dates, text="Fuente del sistema", font=self.font_text_interface)
        label.grid(
            column=0, row=4, padx=3, pady=3, sticky=NW)
        combobox_fuente_sistema = ttk.Combobox(
            labelframe_form_format_dates, width=25, state="readonly", textvariable=self.variable_fuente_sistema, font=self.font_text_interface, justify='center')
        combobox_fuente_sistema["values"] = self.fuentes_sistema
        combobox_fuente_sistema.grid(
            column=1, row=4, padx=3, pady=3, sticky=NW)

        labelframe_formulario_color_botones = LabelFrame(
            labelframe_formulario_info_formatos, text="Color de fuentes del sistema", font=self.font_subtittle_system)
        labelframe_formulario_color_botones.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_formulario_color_botones, text="Color de botones de\n interface", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=3, pady=3, sticky=W)

        labelframe = Frame(labelframe_formulario_color_botones)
        labelframe.grid(
            column=1, row=0, padx=3, pady=3, sticky=NW)

        frame = Frame(labelframe)
        frame.grid(
            column=0, row=0, padx=3, pady=3)

        self.label_color_botones_sistema = Label(
            frame, bg=self.button_color, width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
        self.label_color_botones_sistema.grid(
            column=0, row=0, padx=3, pady=3)

        self.label_name_color_botones_sistema = Label(
            frame, text=self.button_color, width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
        self.label_name_color_botones_sistema.grid(
            column=0, row=1, padx=3, pady=3)

        boton = Button(
            labelframe, text="Cambiar color", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton.configure(command=lambda: self.instance_tools.change_color(variable=self.variable_color_botones_sistema,
                        label_color=self.label_color_botones_sistema, label_name_color=self.label_name_color_botones_sistema))
        boton.grid(
            column=1, row=0, padx=2, pady=2)

        label = Label(
            labelframe_formulario_color_botones, text="Color de texto de los\n botones de\nInterface", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=W)

        labelframe = Frame(labelframe_formulario_color_botones)
        labelframe.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        frame = Frame(labelframe)
        frame.grid(
            column=0, row=0, padx=3, pady=3)

        self.label_color_button_color = Label(frame, bg=self.button_letters_color, width=8,
                                              font=self.font_text_entry_interface, bd=2, relief="solid")
        self.label_color_button_color.grid(
            column=0, row=0, padx=3, pady=3)

        self.label_name_color_button_color = Label(frame, text=self.button_letters_color, width=8,
                                                   font=self.font_text_entry_interface, bd=2, relief="solid")
        self.label_name_color_button_color.grid(
            column=0, row=1, padx=3, pady=3)

        boton = Button(
            labelframe, text="Cambiar color", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton.configure(command=lambda: self.instance_tools.change_color(
            variable=self.variable_color_letra_botones_sistema, label_color=self.label_color_button_color, label_name_color=self.label_name_color_button_color))
        boton.grid(
            column=1, row=0, padx=2, pady=2)

        label = Label(
            labelframe_formulario_color_botones, text="Color de boton de\n cobro", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=3, pady=3, sticky=W)

        labelframe = Frame(labelframe_formulario_color_botones)
        labelframe.grid(
            column=1, row=2, padx=3, pady=3, sticky=NW)

        frame = Frame(labelframe)
        frame.grid(
            column=0, row=0, padx=3, pady=3)

        self.label_color_boton_cobro = Label(
            frame, bg=self.button_color_cobro, width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
        self.label_color_boton_cobro.grid(
            column=0, row=0, padx=3, pady=3)

        self.label_name_color_boton_cobro = Label(
            frame, text=self.button_color_cobro, width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
        self.label_name_color_boton_cobro.grid(
            column=0, row=1, padx=3, pady=3)

        boton = Button(
            labelframe, text="Cambiar color", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton.configure(command=lambda: self.instance_tools.change_color(variable=self.variable_color_boton_cobro,
                        label_color=self.label_color_boton_cobro, label_name_color=self.label_name_color_boton_cobro))
        boton.grid(
            column=1, row=0, padx=2, pady=2)

        label = Label(
            labelframe_formulario_color_botones, text="Color de texto de\nboton de cobro", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=3, pady=3, sticky=W)

        labelframe = Frame(labelframe_formulario_color_botones)
        labelframe.grid(
            column=1, row=3, padx=3, pady=3, sticky=NW)

        frame = Frame(labelframe)
        frame.grid(
            column=0, row=0, padx=3, pady=3)

        self.label_color_letra_boton_cobro = Label(frame, bg=self.button_letters_color_cobro, width=8,
                                                   font=self.font_text_entry_interface, bd=2, relief="solid")
        self.label_color_letra_boton_cobro.grid(
            column=0, row=0, padx=3, pady=3)

        self.label_name_color_letra_boton_cobro = Label(frame, text=self.button_letters_color_cobro, width=8,
                                                        font=self.font_text_entry_interface, bd=2, relief="solid")
        self.label_name_color_letra_boton_cobro.grid(
            column=0, row=1, padx=3, pady=3)

        boton = Button(
            labelframe, text="Cambiar color", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton.configure(command=lambda: self.instance_tools.change_color(
            variable=self.variable_color_letra_boton_cobro, label_color=self.label_color_letra_boton_cobro, label_name_color=self.label_name_color_letra_boton_cobro))
        boton.grid(
            column=1, row=0, padx=2, pady=2)

        if self.system_to_load == 0:
            labelframe = LabelFrame(labelframe_xd, text="Interface de reloj",
                                    font=self.font_subtittle_system)
            labelframe.grid(
                column=1, row=0, padx=3, pady=0, sticky=NW)

            labelframe_formulario_reloj = Frame(labelframe)
            labelframe_formulario_reloj.grid(
                column=0, row=0, padx=3, pady=3, sticky=NW)

            label = Label(
                labelframe_formulario_reloj, text="Color de la primera hora\n0 - 60  Minutos", font=self.font_text_interface)
            label.grid(
                column=0, row=0, padx=3, pady=3)

            labelframe = Frame(labelframe_formulario_reloj)
            labelframe.grid(
                column=1, row=0, padx=3, pady=3, sticky=NW)

            frame = Frame(labelframe)
            frame.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_color_primera_hora = Label(frame, bg=self.variable_color_primera_hora.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_color_primera_hora.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_name_color_primera_hora = Label(frame, text=self.variable_color_primera_hora.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_name_color_primera_hora.grid(
                column=0, row=1, padx=3, pady=3)

            boton = Button(
                labelframe, text="Cambiar color", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
            boton.configure(command=lambda: self.instance_tools.change_color(variable=self.variable_color_primera_hora,
                            label_color=self.label_color_primera_hora, label_name_color=self.label_name_color_primera_hora))
            boton.grid(
                column=1, row=0, padx=2, pady=2)

            label = Label(
                labelframe_formulario_reloj, text="Color 1/4 Hora\n01 - 15  Minutos", font=self.font_text_interface)
            label.grid(
                column=0, row=1, padx=3, pady=3)

            labelframe = Frame(labelframe_formulario_reloj)
            labelframe.grid(
                column=1, row=1, padx=3, pady=3, sticky=NW)

            frame = Frame(labelframe)
            frame.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_color_1_4_hora = Label(frame, bg=self.variable_color_1_4_hora.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_color_1_4_hora.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_name_color_1_4_hora = Label(frame, text=self.variable_color_1_4_hora.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_name_color_1_4_hora.grid(
                column=0, row=1, padx=3, pady=3)

            boton = Button(
                labelframe, text="Cambiar color", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
            boton.configure(command=lambda: self.instance_tools.change_color(variable=self.variable_color_1_4_hora,
                            label_color=self.label_color_1_4_hora, label_name_color=self.label_name_color_1_4_hora))
            boton.grid(
                column=1, row=0, padx=2, pady=2)

            label = Label(
                labelframe_formulario_reloj, text="Color 2/4 Hora\n16 - 30  Minutos", font=self.font_text_interface)
            label.grid(
                column=0, row=2, padx=3, pady=3)

            labelframe = Frame(labelframe_formulario_reloj)
            labelframe.grid(
                column=1, row=2, padx=3, pady=3, sticky=NW)

            frame = Frame(labelframe)
            frame.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_color_2_4_hora = Label(frame, bg=self.variable_color_2_4_hora.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_color_2_4_hora.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_name_color_2_4_hora = Label(frame, text=self.variable_color_2_4_hora.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_name_color_2_4_hora.grid(
                column=0, row=1, padx=3, pady=3)

            boton = Button(
                labelframe, text="Cambiar color", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
            boton.configure(command=lambda: self.instance_tools.change_color(variable=self.variable_color_2_4_hora,
                            label_color=self.label_color_2_4_hora, label_name_color=self.label_name_color_2_4_hora))
            boton.grid(
                column=1, row=0, padx=2, pady=2)

            label = Label(
                labelframe_formulario_reloj, text="Color 3/4 Hora\n31 - 45  Minutos", font=self.font_text_interface)
            label.grid(
                column=0, row=3, padx=3, pady=3)

            labelframe = Frame(labelframe_formulario_reloj)
            labelframe.grid(
                column=1, row=3, padx=3, pady=3, sticky=NW)

            frame = Frame(labelframe)
            frame.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_color_3_4_hora = Label(frame, bg=self.variable_color_3_4_hora.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_color_3_4_hora.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_name_color_3_4_hora = Label(frame, text=self.variable_color_3_4_hora.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_name_color_3_4_hora.grid(
                column=0, row=1, padx=3, pady=3)

            boton = Button(
                labelframe, text="Cambiar color", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
            boton.configure(command=lambda: self.instance_tools.change_color(variable=self.variable_color_3_4_hora,
                            label_color=self.label_color_3_4_hora, label_name_color=self.label_name_color_3_4_hora))
            boton.grid(
                column=1, row=0, padx=2, pady=2)

            label = Label(
                labelframe_formulario_reloj, text="Color hora completa\n46 - 60  Minutos", font=self.font_text_interface)
            label.grid(
                column=0, row=4, padx=3, pady=3)

            labelframe = Frame(labelframe_formulario_reloj)
            labelframe.grid(
                column=1, row=4, padx=3, pady=3, sticky=NW)

            frame = Frame(labelframe)
            frame.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_color_hora_completa = Label(frame, bg=self.variable_color_hora_completa.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_color_hora_completa.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_name_color_hora_completa = Label(frame, text=self.variable_color_hora_completa.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_name_color_hora_completa.grid(
                column=0, row=1, padx=3, pady=3)

            boton = Button(
                labelframe, text="Cambiar color", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
            boton.configure(command=lambda: self.instance_tools.change_color(variable=self.variable_color_hora_completa,
                            label_color=self.label_color_hora_completa, label_name_color=self.label_name_color_hora_completa))
            boton.grid(
                column=1, row=0, padx=2, pady=2)

            label = Label(
                labelframe_formulario_reloj, text="Color de alerta", font=self.font_text_interface)
            label.grid(
                column=0, row=5, padx=3, pady=3)

            labelframe = Frame(labelframe_formulario_reloj)
            labelframe.grid(
                column=1, row=5, padx=3, pady=3, sticky=NW)

            frame = Frame(labelframe)
            frame.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_color_alerta = Label(frame, bg=self.variable_color_alerta.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_color_alerta.grid(
                column=0, row=0, padx=3, pady=3)

            self.label_name_color_alerta = Label(frame, text=self.variable_color_alerta.get(
            ), width=8, font=self.font_text_entry_interface, bd=2, relief="solid")
            self.label_name_color_alerta.grid(
                column=0, row=1, padx=3, pady=3)

            boton = Button(
                labelframe, text="Cambiar color", anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
            boton.configure(command=lambda: self.instance_tools.change_color(variable=self.variable_color_alerta,
                            label_color=self.label_color_alerta, label_name_color=self.label_name_color_alerta))
            boton.grid(
                column=1, row=0, padx=2, pady=2)

        labelframe_size_font_system = LabelFrame(
            seccion_configuracion_interface, text="Tamaño de fuentes de la interface del sistema", font=self.font_subtittle_system)
        labelframe_size_font_system.grid(
            column=0, row=1, padx=3, pady=3)

        labelframe_form_size_font_system = Frame(
            labelframe_size_font_system)
        labelframe_form_size_font_system.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_size_font_system, text="Texto general", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=3, pady=3, sticky=NW)

        combobox_size_text_font = ttk.Combobox(
            labelframe_form_size_font_system, width=5, state="readonly", textvariable=self.variable_size_text_font, font=self.font_text_interface, justify='center', values=self.sizes_font)
        combobox_size_text_font.grid(
            column=1, row=2, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_size_font_system, text="Texto de botones", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=3, pady=3, sticky=NW)

        combobox_size_text_button_font = ttk.Combobox(
            labelframe_form_size_font_system, width=5, state="readonly", textvariable=self.variable_size_text_button_font, font=self.font_text_interface, justify='center', values=self.sizes_font)
        combobox_size_text_button_font.grid(
            column=1, row=3, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_size_font_system, text="Texto de titulos", font=self.font_text_interface)
        label.grid(
            column=0, row=4, padx=3, pady=3, sticky=NW)
        combobox_size_text_font_tittle_system = ttk.Combobox(
            labelframe_form_size_font_system, width=5, state="readonly", textvariable=self.variable_size_text_font_subtittle_system, font=self.font_text_interface, justify='center', values=self.sizes_font)
        combobox_size_text_font_tittle_system.grid(
            column=1, row=4, padx=3, pady=3, sticky=NW)

        label = Label(
            labelframe_form_size_font_system, text="Texto de subtitulos", font=self.font_text_interface)
        label.grid(
            column=0, row=5, padx=3, pady=3, sticky=NW)
        combobox_size_text_font_tittle_system = ttk.Combobox(
            labelframe_form_size_font_system, width=5, state="readonly", textvariable=self.variable_size_text_font_tittle_system, font=self.font_text_interface, justify='center', values=self.sizes_font)
        combobox_size_text_font_tittle_system.grid(
            column=1, row=5, padx=3, pady=3, sticky=NW)

        frame = Frame(seccion_configuracion_interface)
        frame.grid(
            column=0, row=2, padx=0, pady=0)

        boton_guardar = Button(frame, text="Guardar configuracion de interface", height=1, anchor="center", font=self.font_botones_interface,
                               background=self.button_color, fg=self.button_letters_color, command=self.save_data_interface)
        boton_guardar.grid(
            column=0, row=0, padx=3, pady=3)

        boton_cancelar = Button(frame, height=1, text="Cancelar", anchor="center", background=self.button_color,
                                fg=self.button_letters_color, font=self.font_botones_interface, command=self.clean_data_form_interface)
        boton_cancelar.grid(
            column=1, row=0, padx=3, pady=3)

    def change_key_word(self):
        if mb.askyesno("Alerta", "¿Esta seguro de querer cambiar la pregunta de seguridad?") == False:
            return

        if ask_security_question(self.configuracion) != True:
            return

        secure_instance = Secure()
        self.instance_tools.desactivar(self.configuracion)
        secure_instance.interface_add_security_question()
        self.instance_tools.activar(self.configuracion)

        secure_instance = None

    def load_form_tarifa_simple(self):
        self.label_tipo_promo.configure(
            text="La tarifa seleccionada es de tipo: Normal")

        labelframe_formulario_tarifa_simple = LabelFrame(
            self.frame_form_tarifa_general)
        labelframe_formulario_tarifa_simple.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        labelframe = Frame(labelframe_formulario_tarifa_simple)
        labelframe.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        label = Label(labelframe, text="Se cobra 1/4 de Hora apartir de",
                      font=self.font_text_interface, anchor="center")
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        self.variable_inicio_cobro_cuartos_hora.set(self.inicio_cobro_fraccion)
        combobox_inicio_cobro_cuartos_hora = ttk.Combobox(
            labelframe, textvariable=self.variable_inicio_cobro_cuartos_hora, width=3, justify=CENTER, state="readonly", values=[1, 2, 3, 4, 5, 6, 7, 8, 9,
                                                                                                                                 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], font=self.font_text_interface)
        combobox_inicio_cobro_cuartos_hora.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        label = Label(labelframe, text="Hora",
                      font=self.font_text_interface, anchor="center")
        label.grid(
            column=2, row=1, padx=3, pady=3, sticky=NW)

        frame_importe_hora = Frame(labelframe_formulario_tarifa_simple)
        frame_importe_hora.grid(
            column=0, row=2, padx=3, pady=3, sticky=NW)

        label = Label(frame_importe_hora,
                      text="Importe de 1/4 hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            frame_importe_hora, width=5, textvariable=self.variable_importe_primer_cuarto_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=0, padx=3, pady=3, sticky=NW)

        label = Label(frame_importe_hora,
                      text="Importe de 2/4 hora", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            frame_importe_hora, width=5, textvariable=self.variable_importe_segundo_cuarto_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        label = Label(frame_importe_hora,
                      text="Importe de 3/4 hora", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=3, pady=3, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            frame_importe_hora, width=5, textvariable=self.variable_importe_tercer_cuarto_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=3, pady=3, sticky=NW)

        label = Label(frame_importe_hora,
                      text="Importe de hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=3, pady=3, sticky=NW)
        entry_importe_hora = Entry(
            frame_importe_hora, width=5, textvariable=self.variable_importe_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=3, padx=3, pady=3, sticky=NW)

    def load_form_tarifa_avanzada(self):
        self.label_tipo_promo.configure(
            text="La tarifa seleccionada es de tipo: Avanzada")

        labelframe_horas = LabelFrame(self.frame_form_tarifa_general)
        labelframe_horas.grid(
            column=0, row=0, padx=3, pady=3)

        labelframe_0 = LabelFrame(labelframe_horas)
        labelframe_0.grid(
            column=0, row=0, padx=0, pady=0)

        label = Label(labelframe_0,
                      text="0 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_0)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_0_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_0_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_0_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora 00:00", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_0_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_1 = LabelFrame(labelframe_horas)
        labelframe_1.grid(
            column=1, row=0, padx=0, pady=0)

        label = Label(labelframe_1,
                      text="1 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_1)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_1_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_1_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_1_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_1_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_2 = LabelFrame(labelframe_horas)
        labelframe_2.grid(
            column=2, row=0, padx=0, pady=0)

        label = Label(labelframe_2,
                      text="2 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_2)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_2_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_2_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_2_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_2_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_3 = LabelFrame(labelframe_horas)
        labelframe_3.grid(
            column=3, row=0, padx=0, pady=0)

        label = Label(labelframe_3,
                      text="3 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_3)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_3_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_3_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_3_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_3_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_4 = LabelFrame(labelframe_horas)
        labelframe_4.grid(
            column=4, row=0, padx=0, pady=0)

        label = Label(labelframe_4,
                      text="4 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_4)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_4_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_4_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_4_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_4_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_5 = LabelFrame(labelframe_horas)
        labelframe_5.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe_5,
                      text="5 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_5)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_5_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_5_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_5_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_5_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_6 = LabelFrame(labelframe_horas)
        labelframe_6.grid(
            column=1, row=1, padx=0, pady=0)

        label = Label(labelframe_6,
                      text="6 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_6)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_6_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_6_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_6_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_6_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_7 = LabelFrame(labelframe_horas)
        labelframe_7.grid(
            column=2, row=1, padx=0, pady=0)

        label = Label(labelframe_7,
                      text="7 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_7)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_7_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_7_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_7_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_7_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_8 = LabelFrame(labelframe_horas)
        labelframe_8.grid(
            column=3, row=1, padx=0, pady=0)

        label = Label(labelframe_8,
                      text="8 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_8)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_8_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_8_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_8_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_8_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_9 = LabelFrame(labelframe_horas)
        labelframe_9.grid(
            column=4, row=1, padx=0, pady=0)

        label = Label(labelframe_9,
                      text="9 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_9)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_9_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_9_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_9_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_9_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_10 = LabelFrame(labelframe_horas)
        labelframe_10.grid(
            column=0, row=2, padx=0, pady=0)

        label = Label(labelframe_10,
                      text="10 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_10)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_10_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_10_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_10_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_10_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_11 = LabelFrame(labelframe_horas)
        labelframe_11.grid(
            column=1, row=2, padx=0, pady=0)

        label = Label(labelframe_11,
                      text="11 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_11)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_11_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_11_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_11_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_11_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_12 = LabelFrame(labelframe_horas)
        labelframe_12.grid(
            column=2, row=2, padx=0, pady=0)

        label = Label(labelframe_12,
                      text="12 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_12)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_12_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_12_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_12_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_12_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_13 = LabelFrame(labelframe_horas)
        labelframe_13.grid(
            column=3, row=2, padx=0, pady=0)

        label = Label(labelframe_13,
                      text="13 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_13)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_13_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_13_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_13_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_13_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_14 = LabelFrame(labelframe_horas)
        labelframe_14.grid(
            column=4, row=2, padx=0, pady=0)

        label = Label(labelframe_14,
                      text="14 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_14)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_14_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_14_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_14_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_14_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_15 = LabelFrame(labelframe_horas)
        labelframe_15.grid(
            column=0, row=3, padx=0, pady=0)

        label = Label(labelframe_15,
                      text="15 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_15)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_15_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_15_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_15_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_15_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_16 = LabelFrame(labelframe_horas)
        labelframe_16.grid(
            column=1, row=3, padx=0, pady=0)

        label = Label(labelframe_16,
                      text="16 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_16)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_16_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_16_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_16_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_16_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_17 = LabelFrame(labelframe_horas)
        labelframe_17.grid(
            column=2, row=3, padx=0, pady=0)

        label = Label(labelframe_17,
                      text="17 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_17)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_17_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_17_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_17_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_17_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_18 = LabelFrame(labelframe_horas)
        labelframe_18.grid(
            column=3, row=3, padx=0, pady=0)

        label = Label(labelframe_18,
                      text="18 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_18)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_18_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_18_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_18_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_18_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_19 = LabelFrame(labelframe_horas)
        labelframe_19.grid(
            column=4, row=3, padx=0, pady=0)

        label = Label(labelframe_19,
                      text="19 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_19)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_19_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_19_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_19_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_19_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_20 = LabelFrame(labelframe_horas)
        labelframe_20.grid(
            column=0, row=4, padx=0, pady=0)

        label = Label(labelframe_20,
                      text="20 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_20)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_20_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_20_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_20_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_20_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_21 = LabelFrame(labelframe_horas)
        labelframe_21.grid(
            column=1, row=4, padx=0, pady=0)

        label = Label(labelframe_21,
                      text="21 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_21)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_21_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_21_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_21_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_21_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_22 = LabelFrame(labelframe_horas)
        labelframe_22.grid(
            column=2, row=4, padx=0, pady=0)

        label = Label(labelframe_22,
                      text="22 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_22)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_22_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_22_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_22_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_22_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_23 = LabelFrame(labelframe_horas)
        labelframe_23.grid(
            column=3, row=4, padx=0, pady=0)

        label = Label(labelframe_23,
                      text="23 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_23)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_23_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_23_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_23_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_23_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_24 = LabelFrame(labelframe_horas)
        labelframe_24.grid(
            column=4, row=4, padx=0, pady=0)

        label = Label(labelframe_24,
                      text="24 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_24)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_24_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_24_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_24_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_24_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

    def load_ids_printter(self, event):
        id_vendor, id_product = self.instance_tools.get_device_ids(
            self.datalist_divices, self.variable_printer_system.get())
        self.variable_id_vendor_impresora.set(id_vendor)
        self.variable_id_product_impresora.set(id_product)

    def save_data_tarifa(self):
        try:
            nombre_usuario_activo = self.DB.nombre_usuario_activo()
            if nombre_usuario_activo is None:
                raise SystemError("No se puede guarda la informacion ya que no has iniciado sesion, reinicia el sistema e inicia sesion para poder hacert cambios en el sistema.\n\nSi consideras que se trata de un error ponte en contacto con un administrador inmediatamente")

            self.validate_data_tarifa()

        except TclError as e:
            mb.showerror("Error", "No debe de dejar campos en blanco")
            return
        except Exception as e:
            mb.showerror("Error", e)
            return

        changes = []
        tipo_cambio = "Configuracion de tarifa general"


        if self.variable_tipo_tarifa_sistema.get() != self.tipo_tarifa_sistema:
            estado_actual = "Tarifa normal" if self.variable_tipo_tarifa_sistema.get(
            ) else "Tarifa personalizada"
            estado_sistema = "Tarifa normal" if self.tipo_tarifa_sistema else "Tarifa personalizada"
            changes.append([
                f"Tarifa del sistema: {estado_sistema} -> {estado_actual}",
                lambda: {self.instance_config.set_config(
                    "tarifa", "tipo_tarifa_sistema", new_value=self.variable_tipo_tarifa_sistema.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tarifa del sistema",valor_anterior= estado_actual, valor_nuevo=estado_sistema, tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_importe_boleto_perdido.get() != self.tarifa_boleto_perdido:
            changes.append([
                f"Tarifa de boleto perdido: {self.tarifa_boleto_perdido} -> {self.variable_importe_boleto_perdido.get()}",
                lambda: {self.instance_config.set_config(
                    "tarifa", "tarifa_boleto_perdido", new_value=self.variable_importe_boleto_perdido.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tarifa de boleto perdido",valor_anterior= self.tarifa_boleto_perdido, valor_nuevo=self.variable_importe_boleto_perdido.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_inicio_cobro_cuartos_hora.get() != self.inicio_cobro_fraccion:
            changes.append([
                f"Inicio de cobro de fraccion: {self.inicio_cobro_fraccion}° Hora -> {self.variable_inicio_cobro_cuartos_hora.get()}° Hora",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_simple", "inicio_cobro_fraccion", new_value=self.variable_inicio_cobro_cuartos_hora.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Inicio de cobro de fraccion",valor_anterior= f"{self.inicio_cobro_fraccion}° Hora", valor_nuevo=f"{self.variable_inicio_cobro_cuartos_hora.get()}° Hora", tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_importe_primer_cuarto_hora.get() != self.tarifa_1_fraccion:
            changes.append([
                f"Tarifa simple 1° fraccion: {self.tarifa_1_fraccion} -> {self.variable_importe_primer_cuarto_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_simple", "tarifa_1_fraccion", new_value=self.variable_importe_primer_cuarto_hora.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tarifa simple 1° fraccion",valor_anterior= self.tarifa_1_fraccion, valor_nuevo=self.variable_importe_primer_cuarto_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_importe_segundo_cuarto_hora.get() != self.tarifa_2_fraccion:
            changes.append([
                f"Tarifa simple 2° fraccion: {self.tarifa_2_fraccion} -> {self.variable_importe_segundo_cuarto_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_simple", "tarifa_2_fraccion", new_value=self.variable_importe_segundo_cuarto_hora.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tarifa simple 2° fraccion",valor_anterior= self.tarifa_2_fraccion, valor_nuevo=self.variable_importe_segundo_cuarto_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_importe_tercer_cuarto_hora.get() != self.tarifa_3_fraccion:
            changes.append([
                f"Tarifa simple 3° fraccion: {self.tarifa_3_fraccion} -> {self.variable_importe_tercer_cuarto_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_simple", "tarifa_3_fraccion", new_value=self.variable_importe_tercer_cuarto_hora.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tarifa simple 3° fraccion",valor_anterior= self.tarifa_3_fraccion, valor_nuevo=self.variable_importe_tercer_cuarto_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_importe_hora.get() != self.tarifa_hora:
            changes.append([
                f"Tarifa simple hora completa: {self.tarifa_hora} -> {self.variable_importe_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_simple", "tarifa_hora", new_value=self.variable_importe_hora.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tarifa simple hora completa",valor_anterior= self.tarifa_hora, valor_nuevo=self.variable_importe_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_0_hora.get() != self.config_0_hora:
            changes.append([
                f"Tarifa avanzada Hora 0 hora completa: {self.config_0_hora} -> {self.variable_0_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "0", "hora", new_value=self.variable_0_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 0 hora completa",valor_anterior= self.config_0_hora, valor_nuevo=self.variable_0_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_0_1.get() != self.config_0_1:
            changes.append([
                f"Tarifa avanzada Hora 0 fraccion 1: {self.config_0_1} -> {self.variable_0_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "0", "1", new_value=self.variable_0_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 0 fraccion 1",valor_anterior= self.config_0_1, valor_nuevo=self.variable_0_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_0_2.get() != self.config_0_2:
            changes.append([
                f"Tarifa avanzada Hora 0 fraccion 2: {self.config_0_2} -> {self.variable_0_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "0", "2", new_value=self.variable_0_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 0 fraccion 2",valor_anterior= self.config_0_2, valor_nuevo=self.variable_0_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_0_3.get() != self.config_0_3:
            changes.append([
                f"Tarifa avanzada Hora 0 fraccion 3: {self.config_0_3} -> {self.variable_0_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "0", "3", new_value=self.variable_0_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 0 fraccion 3",valor_anterior= self.config_0_3, valor_nuevo=self.variable_0_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_1_hora.get() != self.config_1_hora:
            changes.append([
                f"Tarifa avanzada Hora 1 hora completa: {self.config_1_hora} -> {self.variable_1_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "1", "hora", new_value=self.variable_1_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 1 hora completa",valor_anterior= self.config_1_hora, valor_nuevo=self.variable_1_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_1_1.get() != self.config_1_1:
            changes.append([
                f"Tarifa avanzada Hora 1 fraccion 1: {self.config_1_1} -> {self.variable_1_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "1", "1", new_value=self.variable_1_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 1 fraccion 1",valor_anterior= self.config_1_1, valor_nuevo=self.variable_1_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_1_2.get() != self.config_1_2:
            changes.append([
                f"Tarifa avanzada Hora 1 fraccion 2: {self.config_1_2} -> {self.variable_1_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "1", "2", new_value=self.variable_1_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 1 fraccion 2",valor_anterior= self.config_1_2, valor_nuevo=self.variable_1_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_1_3.get() != self.config_1_3:
            changes.append([
                f"Tarifa avanzada Hora 1 fraccion 3: {self.config_1_3} -> {self.variable_1_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "1", "3", new_value=self.variable_1_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 1 fraccion 3",valor_anterior= self.config_1_3, valor_nuevo=self.variable_1_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_2_hora.get() != self.config_2_hora:
            changes.append([
                f"Tarifa avanzada Hora 2 hora completa: {self.config_2_hora} -> {self.variable_2_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "2", "hora", new_value=self.variable_2_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 2 hora completa",valor_anterior= self.config_2_hora, valor_nuevo=self.variable_2_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_2_1.get() != self.config_2_1:
            changes.append([
                f"Tarifa avanzada Hora 2 fraccion 1: {self.config_2_1} -> {self.variable_2_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "2", "1", new_value=self.variable_2_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 2 fraccion 1",valor_anterior= self.config_2_1, valor_nuevo=self.variable_2_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_2_2.get() != self.config_2_2:
            changes.append([
                f"Tarifa avanzada Hora 2 fraccion 2: {self.config_2_2} -> {self.variable_2_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "2", "2", new_value=self.variable_2_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 2 fraccion 2",valor_anterior= self.config_2_2, valor_nuevo=self.variable_2_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_2_3.get() != self.config_2_3:
            changes.append([
                f"Tarifa avanzada Hora 2 fraccion 3: {self.config_2_3} -> {self.variable_2_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "2", "3", new_value=self.variable_2_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 2 fraccion 3",valor_anterior= self.config_2_3, valor_nuevo=self.variable_2_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_3_hora.get() != self.config_3_hora:
            changes.append([
                f"Tarifa avanzada Hora 3 hora completa: {self.config_3_hora} -> {self.variable_3_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "3", "hora", new_value=self.variable_3_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 3 hora completa",valor_anterior= self.config_3_hora, valor_nuevo=self.variable_3_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_3_1.get() != self.config_3_1:
            changes.append([
                f"Tarifa avanzada Hora 3 fraccion 1: {self.config_3_1} -> {self.variable_3_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "3", "1", new_value=self.variable_3_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 3 fraccion 1",valor_anterior= self.config_3_1, valor_nuevo=self.variable_3_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_3_2.get() != self.config_3_2:
            changes.append([
                f"Tarifa avanzada Hora 3 fraccion 2: {self.config_3_2} -> {self.variable_3_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "3", "2", new_value=self.variable_3_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 3 fraccion 2",valor_anterior= self.config_3_2, valor_nuevo=self.variable_3_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_3_3.get() != self.config_3_3:
            changes.append([
                f"Tarifa avanzada Hora 3 fraccion 3: {self.config_3_3} -> {self.variable_3_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "3", "3", new_value=self.variable_3_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 3 fraccion 3",valor_anterior= self.config_3_3, valor_nuevo=self.variable_3_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_4_hora.get() != self.config_4_hora:
            changes.append([
                f"Tarifa avanzada Hora 4 hora completa: {self.config_4_hora} -> {self.variable_4_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "4", "hora", new_value=self.variable_4_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 4 hora completa",valor_anterior= self.config_4_hora, valor_nuevo=self.variable_4_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_4_1.get() != self.config_4_1:
            changes.append([
                f"Tarifa avanzada Hora 4 fraccion 1: {self.config_4_1} -> {self.variable_4_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "4", "1", new_value=self.variable_4_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 4 fraccion 1",valor_anterior= self.config_4_1, valor_nuevo=self.variable_4_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_4_2.get() != self.config_4_2:
            changes.append([
                f"Tarifa avanzada Hora 4 fraccion 2: {self.config_4_2} -> {self.variable_4_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "4", "2", new_value=self.variable_4_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 4 fraccion 2",valor_anterior= self.config_4_2, valor_nuevo=self.variable_4_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_4_3.get() != self.config_4_3:
            changes.append([
                f"Tarifa avanzada Hora 4 fraccion 3: {self.config_4_3} -> {self.variable_4_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "4", "3", new_value=self.variable_4_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 4 fraccion 3",valor_anterior= self.config_4_3, valor_nuevo=self.variable_4_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_5_hora.get() != self.config_5_hora:
            changes.append([
                f"Tarifa avanzada Hora 5 hora completa: {self.config_5_hora} -> {self.variable_5_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "5", "hora", new_value=self.variable_5_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 5 hora completa",valor_anterior= self.config_5_hora, valor_nuevo=self.variable_5_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_5_1.get() != self.config_5_1:
            changes.append([
                f"Tarifa avanzada Hora 5 fraccion 1: {self.config_5_1} -> {self.variable_5_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "5", "1", new_value=self.variable_5_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 5 fraccion 1",valor_anterior= self.config_5_1, valor_nuevo=self.variable_5_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_5_2.get() != self.config_5_2:
            changes.append([
                f"Tarifa avanzada Hora 5 fraccion 2: {self.config_5_2} -> {self.variable_5_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "5", "2", new_value=self.variable_5_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 5 fraccion 2",valor_anterior= self.config_5_2, valor_nuevo=self.variable_5_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_5_3.get() != self.config_5_3:
            changes.append([
                f"Tarifa avanzada Hora 5 fraccion 3: {self.config_5_3} -> {self.variable_5_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "5", "3", new_value=self.variable_5_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 5 fraccion 3",valor_anterior= self.config_5_3, valor_nuevo=self.variable_5_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_6_hora.get() != self.config_6_hora:
            changes.append([
                f"Tarifa avanzada Hora 6 hora completa: {self.config_6_hora} -> {self.variable_6_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "6", "hora", new_value=self.variable_6_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 6 hora completa",valor_anterior= self.config_6_hora, valor_nuevo=self.variable_6_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_6_1.get() != self.config_6_1:
            changes.append([
                f"Tarifa avanzada Hora 6 fraccion 1: {self.config_6_1} -> {self.variable_6_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "6", "1", new_value=self.variable_6_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 6 fraccion 1",valor_anterior= self.config_6_1, valor_nuevo=self.variable_6_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_6_2.get() != self.config_6_2:
            changes.append([
                f"Tarifa avanzada Hora 6 fraccion 2: {self.config_6_2} -> {self.variable_6_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "6", "2", new_value=self.variable_6_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 6 fraccion 2",valor_anterior= self.config_6_2, valor_nuevo=self.variable_6_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_6_3.get() != self.config_6_3:
            changes.append([
                f"Tarifa avanzada Hora 6 fraccion 3: {self.config_6_3} -> {self.variable_6_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "6", "3", new_value=self.variable_6_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 6 fraccion 3",valor_anterior= self.config_6_3, valor_nuevo=self.variable_6_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_7_hora.get() != self.config_7_hora:
            changes.append([
                f"Tarifa avanzada Hora 7 hora completa: {self.config_7_hora} -> {self.variable_7_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "7", "hora", new_value=self.variable_7_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 7 hora completa",valor_anterior= self.config_7_hora, valor_nuevo=self.variable_7_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_7_1.get() != self.config_7_1:
            changes.append([
                f"Tarifa avanzada Hora 7 fraccion 1: {self.config_7_1} -> {self.variable_7_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "7", "1", new_value=self.variable_7_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 7 fraccion 1",valor_anterior= self.config_7_1, valor_nuevo=self.variable_7_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_7_2.get() != self.config_7_2:
            changes.append([
                f"Tarifa avanzada Hora 7 fraccion 2: {self.config_7_2} -> {self.variable_7_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "7", "2", new_value=self.variable_7_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 7 fraccion 2",valor_anterior= self.config_7_2, valor_nuevo=self.variable_7_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_7_3.get() != self.config_7_3:
            changes.append([
                f"Tarifa avanzada Hora 7 fraccion 3: {self.config_7_3} -> {self.variable_7_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "7", "3", new_value=self.variable_7_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 7 fraccion 3",valor_anterior= self.config_7_3, valor_nuevo=self.variable_7_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_8_hora.get() != self.config_8_hora:
            changes.append([
                f"Tarifa avanzada Hora 8 hora completa: {self.config_8_hora} -> {self.variable_8_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "8", "hora", new_value=self.variable_8_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 8 hora completa",valor_anterior= self.config_8_hora, valor_nuevo=self.variable_8_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_8_1.get() != self.config_8_1:
            changes.append([
                f"Tarifa avanzada Hora 8 fraccion 1: {self.config_8_1} -> {self.variable_8_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "8", "1", new_value=self.variable_8_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 8 fraccion 1",valor_anterior= self.config_8_1, valor_nuevo=self.variable_8_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_8_2.get() != self.config_8_2:
            changes.append([
                f"Tarifa avanzada Hora 8 fraccion 2: {self.config_8_2} -> {self.variable_8_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "8", "2", new_value=self.variable_8_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 8 fraccion 2",valor_anterior= self.config_8_2, valor_nuevo=self.variable_8_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_8_3.get() != self.config_8_3:
            changes.append([
                f"Tarifa avanzada Hora 8 fraccion 3: {self.config_8_3} -> {self.variable_8_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "8", "3", new_value=self.variable_8_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 8 fraccion 3",valor_anterior= self.config_8_3, valor_nuevo=self.variable_8_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_9_hora.get() != self.config_9_hora:
            changes.append([
                f"Tarifa avanzada Hora 9 hora completa: {self.config_9_hora} -> {self.variable_9_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "9", "hora", new_value=self.variable_9_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 9 hora completa",valor_anterior= self.config_9_hora, valor_nuevo=self.variable_9_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_9_1.get() != self.config_9_1:
            changes.append([
                f"Tarifa avanzada Hora 9 fraccion 1: {self.config_9_1} -> {self.variable_9_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "9", "1", new_value=self.variable_9_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 9 fraccion 1",valor_anterior= self.config_9_1, valor_nuevo=self.variable_9_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_9_2.get() != self.config_9_2:
            changes.append([
                f"Tarifa avanzada Hora 9 fraccion 2: {self.config_9_2} -> {self.variable_9_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "9", "2", new_value=self.variable_9_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 9 fraccion 2",valor_anterior= self.config_9_2, valor_nuevo=self.variable_9_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_9_3.get() != self.config_9_3:
            changes.append([
                f"Tarifa avanzada Hora 9 fraccion 3: {self.config_9_3} -> {self.variable_9_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "9", "3", new_value=self.variable_9_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 9 fraccion 3",valor_anterior= self.config_9_3, valor_nuevo=self.variable_9_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_10_hora.get() != self.config_10_hora:
            changes.append([
                f"Tarifa avanzada Hora 10 hora completa: {self.config_10_hora} -> {self.variable_10_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "10", "hora", new_value=self.variable_10_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 10 hora completa",valor_anterior= self.config_10_hora, valor_nuevo=self.variable_10_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_10_1.get() != self.config_10_1:
            changes.append([
                f"Tarifa avanzada Hora 10 fraccion 1: {self.config_10_1} -> {self.variable_10_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "10", "1", new_value=self.variable_10_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 10 fraccion 1",valor_anterior= self.config_10_1, valor_nuevo=self.variable_10_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_10_2.get() != self.config_10_2:
            changes.append([
                f"Tarifa avanzada Hora 10 fraccion 2: {self.config_10_2} -> {self.variable_10_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "10", "2", new_value=self.variable_10_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 10 fraccion 2",valor_anterior= self.config_10_2, valor_nuevo=self.variable_10_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_10_3.get() != self.config_10_3:
            changes.append([
                f"Tarifa avanzada Hora 10 fraccion 3: {self.config_10_3} -> {self.variable_10_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "10", "3", new_value=self.variable_10_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 10 fraccion 3",valor_anterior= self.config_10_3, valor_nuevo=self.variable_10_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_11_hora.get() != self.config_11_hora:
            changes.append([
                f"Tarifa avanzada Hora 11 hora completa: {self.config_11_hora} -> {self.variable_11_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "11", "hora", new_value=self.variable_11_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 11 hora completa",valor_anterior= self.config_11_hora, valor_nuevo=self.variable_11_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_11_1.get() != self.config_11_1:
            changes.append([
                f"Tarifa avanzada Hora 11 fraccion 1: {self.config_11_1} -> {self.variable_11_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "11", "1", new_value=self.variable_11_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 11 fraccion 1",valor_anterior= self.config_11_1, valor_nuevo=self.variable_11_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_11_2.get() != self.config_11_2:
            changes.append([
                f"Tarifa avanzada Hora 11 fraccion 2: {self.config_11_2} -> {self.variable_11_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "11", "2", new_value=self.variable_11_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 11 fraccion 2",valor_anterior= self.config_11_2, valor_nuevo=self.variable_11_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_11_3.get() != self.config_11_3:
            changes.append([
                f"Tarifa avanzada Hora 11 fraccion 3: {self.config_11_3} -> {self.variable_11_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "11", "3", new_value=self.variable_11_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 11 fraccion 3",valor_anterior= self.config_11_3, valor_nuevo=self.variable_11_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_12_hora.get() != self.config_12_hora:
            changes.append([
                f"Tarifa avanzada Hora 12 hora completa: {self.config_12_hora} -> {self.variable_12_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "12", "hora", new_value=self.variable_12_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 12 hora completa",valor_anterior= self.config_12_hora, valor_nuevo=self.variable_12_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_12_1.get() != self.config_12_1:
            changes.append([
                f"Tarifa avanzada Hora 12 fraccion 1: {self.config_12_1} -> {self.variable_12_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "12", "1", new_value=self.variable_12_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 12 fraccion 1",valor_anterior= self.config_12_1, valor_nuevo=self.variable_12_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_12_2.get() != self.config_12_2:
            changes.append([
                f"Tarifa avanzada Hora 12 fraccion 2: {self.config_12_2} -> {self.variable_12_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "12", "2", new_value=self.variable_12_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 12 fraccion 2",valor_anterior= self.config_12_2, valor_nuevo=self.variable_12_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_12_3.get() != self.config_12_3:
            changes.append([
                f"Tarifa avanzada Hora 12 fraccion 3: {self.config_12_3} -> {self.variable_12_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "12", "3", new_value=self.variable_12_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 12 fraccion 3",valor_anterior= self.config_12_3, valor_nuevo=self.variable_12_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_13_hora.get() != self.config_13_hora:
            changes.append([
                f"Tarifa avanzada Hora 13 hora completa: {self.config_13_hora} -> {self.variable_13_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "13", "hora", new_value=self.variable_13_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 13 hora completa",valor_anterior= self.config_13_hora, valor_nuevo=self.variable_13_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_13_1.get() != self.config_13_1:
            changes.append([
                f"Tarifa avanzada Hora 13 fraccion 1: {self.config_13_1} -> {self.variable_13_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "13", "1", new_value=self.variable_13_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 13 fraccion 1",valor_anterior= self.config_13_1, valor_nuevo=self.variable_13_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_13_2.get() != self.config_13_2:
            changes.append([
                f"Tarifa avanzada Hora 13 fraccion 2: {self.config_13_2} -> {self.variable_13_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "13", "2", new_value=self.variable_13_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 13 fraccion 2",valor_anterior= self.config_13_2, valor_nuevo=self.variable_13_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_13_3.get() != self.config_13_3:
            changes.append([
                f"Tarifa avanzada Hora 13 fraccion 3: {self.config_13_3} -> {self.variable_13_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "13", "3", new_value=self.variable_13_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 13 fraccion 3",valor_anterior= self.config_13_3, valor_nuevo=self.variable_13_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_14_hora.get() != self.config_14_hora:
            changes.append([
                f"Tarifa avanzada Hora 14 hora completa: {self.config_14_hora} -> {self.variable_14_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "14", "hora", new_value=self.variable_14_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 14 hora completa",valor_anterior= self.config_14_hora, valor_nuevo=self.variable_14_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_14_1.get() != self.config_14_1:
            changes.append([
                f"Tarifa avanzada Hora 14 fraccion 1: {self.config_14_1} -> {self.variable_14_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "14", "1", new_value=self.variable_14_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 14 fraccion 1",valor_anterior= self.config_14_1, valor_nuevo=self.variable_14_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_14_2.get() != self.config_14_2:
            changes.append([
                f"Tarifa avanzada Hora 14 fraccion 2: {self.config_14_2} -> {self.variable_14_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "14", "2", new_value=self.variable_14_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 14 fraccion 2",valor_anterior= self.config_14_2, valor_nuevo=self.variable_14_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_14_3.get() != self.config_14_3:
            changes.append([
                f"Tarifa avanzada Hora 14 fraccion 3: {self.config_14_3} -> {self.variable_14_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "14", "3", new_value=self.variable_14_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 14 fraccion 3",valor_anterior= self.config_14_3, valor_nuevo=self.variable_14_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_15_hora.get() != self.config_15_hora:
            changes.append([
                f"Tarifa avanzada Hora 15 hora completa: {self.config_15_hora} -> {self.variable_15_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "15", "hora", new_value=self.variable_15_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 15 hora completa",valor_anterior= self.config_15_hora, valor_nuevo=self.variable_15_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_15_1.get() != self.config_15_1:
            changes.append([
                f"Tarifa avanzada Hora 15 fraccion 1: {self.config_15_1} -> {self.variable_15_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "15", "1", new_value=self.variable_15_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 15 fraccion 1",valor_anterior= self.config_15_1, valor_nuevo=self.variable_15_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_15_2.get() != self.config_15_2:
            changes.append([
                f"Tarifa avanzada Hora 15 fraccion 2: {self.config_15_2} -> {self.variable_15_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "15", "2", new_value=self.variable_15_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 15 fraccion 2",valor_anterior= self.config_15_2, valor_nuevo=self.variable_15_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_15_3.get() != self.config_15_3:
            changes.append([
                f"Tarifa avanzada Hora 15 fraccion 3: {self.config_15_3} -> {self.variable_15_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "15", "3", new_value=self.variable_15_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 15 fraccion 3",valor_anterior= self.config_15_3, valor_nuevo=self.variable_15_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_16_hora.get() != self.config_16_hora:
            changes.append([
                f"Tarifa avanzada Hora 16 hora completa: {self.config_16_hora} -> {self.variable_16_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "16", "hora", new_value=self.variable_16_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 16 hora completa",valor_anterior= self.config_16_hora, valor_nuevo=self.variable_16_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_16_1.get() != self.config_16_1:
            changes.append([
                f"Tarifa avanzada Hora 16 fraccion 1: {self.config_16_1} -> {self.variable_16_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "16", "1", new_value=self.variable_16_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 16 fraccion 1",valor_anterior= self.config_16_1, valor_nuevo=self.variable_16_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_16_2.get() != self.config_16_2:
            changes.append([
                f"Tarifa avanzada Hora 16 fraccion 2: {self.config_16_2} -> {self.variable_16_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "16", "2", new_value=self.variable_16_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 16 fraccion 2",valor_anterior= self.config_16_2, valor_nuevo=self.variable_16_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_16_3.get() != self.config_16_3:
            changes.append([
                f"Tarifa avanzada Hora 16 fraccion 3: {self.config_16_3} -> {self.variable_16_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "16", "3", new_value=self.variable_16_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 16 fraccion 3",valor_anterior= self.config_16_3, valor_nuevo=self.variable_16_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_17_hora.get() != self.config_17_hora:
            changes.append([
                f"Tarifa avanzada Hora 17 hora completa: {self.config_17_hora} -> {self.variable_17_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "17", "hora", new_value=self.variable_17_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 17 hora completa",valor_anterior= self.config_17_hora, valor_nuevo=self.variable_17_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_17_1.get() != self.config_17_1:
            changes.append([
                f"Tarifa avanzada Hora 17 fraccion 1: {self.config_17_1} -> {self.variable_17_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "17", "1", new_value=self.variable_17_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 17 fraccion 1",valor_anterior= self.config_17_1, valor_nuevo=self.variable_17_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_17_2.get() != self.config_17_2:
            changes.append([
                f"Tarifa avanzada Hora 17 fraccion 2: {self.config_17_2} -> {self.variable_17_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "17", "2", new_value=self.variable_17_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 17 fraccion 2",valor_anterior= self.config_17_2, valor_nuevo=self.variable_17_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_17_3.get() != self.config_17_3:
            changes.append([
                f"Tarifa avanzada Hora 17 fraccion 3: {self.config_17_3} -> {self.variable_17_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "17", "3", new_value=self.variable_17_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 17 fraccion 3",valor_anterior= self.config_17_3, valor_nuevo=self.variable_17_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_18_hora.get() != self.config_18_hora:
            changes.append([
                f"Tarifa avanzada Hora 18 hora completa: {self.config_18_hora} -> {self.variable_18_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "18", "hora", new_value=self.variable_18_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 18 hora completa",valor_anterior= self.config_18_hora, valor_nuevo=self.variable_18_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_18_1.get() != self.config_18_1:
            changes.append([
                f"Tarifa avanzada Hora 18 fraccion 1: {self.config_18_1} -> {self.variable_18_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "18", "1", new_value=self.variable_18_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 18 fraccion 1",valor_anterior= self.config_18_1, valor_nuevo=self.variable_18_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_18_2.get() != self.config_18_2:
            changes.append([
                f"Tarifa avanzada Hora 18 fraccion 2: {self.config_18_2} -> {self.variable_18_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "18", "2", new_value=self.variable_18_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 18 fraccion 2",valor_anterior= self.config_18_2, valor_nuevo=self.variable_18_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_18_3.get() != self.config_18_3:
            changes.append([
                f"Tarifa avanzada Hora 18 fraccion 3: {self.config_18_3} -> {self.variable_18_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "18", "3", new_value=self.variable_18_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 18 fraccion 3",valor_anterior= self.config_18_3, valor_nuevo=self.variable_18_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_19_hora.get() != self.config_19_hora:
            changes.append([
                f"Tarifa avanzada Hora 19 hora completa: {self.config_19_hora} -> {self.variable_19_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "19", "hora", new_value=self.variable_19_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 19 hora completa",valor_anterior= self.config_19_hora, valor_nuevo=self.variable_19_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_19_1.get() != self.config_19_1:
            changes.append([
                f"Tarifa avanzada Hora 19 fraccion 1: {self.config_19_1} -> {self.variable_19_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "19", "1", new_value=self.variable_19_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 19 fraccion 1",valor_anterior= self.config_19_1, valor_nuevo=self.variable_19_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_19_2.get() != self.config_19_2:
            changes.append([
                f"Tarifa avanzada Hora 19 fraccion 2: {self.config_19_2} -> {self.variable_19_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "19", "2", new_value=self.variable_19_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 19 fraccion 2",valor_anterior= self.config_19_2, valor_nuevo=self.variable_19_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_19_3.get() != self.config_19_3:
            changes.append([
                f"Tarifa avanzada Hora 19 fraccion 3: {self.config_19_3} -> {self.variable_19_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "19", "3", new_value=self.variable_19_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 19 fraccion 3",valor_anterior= self.config_19_3, valor_nuevo=self.variable_19_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_20_hora.get() != self.config_20_hora:
            changes.append([
                f"Tarifa avanzada Hora 20 hora completa: {self.config_20_hora} -> {self.variable_20_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "20", "hora", new_value=self.variable_20_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 20 hora completa",valor_anterior= self.config_20_hora, valor_nuevo=self.variable_20_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_20_1.get() != self.config_20_1:
            changes.append([
                f"Tarifa avanzada Hora 20 fraccion 1: {self.config_20_1} -> {self.variable_20_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "20", "1", new_value=self.variable_20_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 20 fraccion 1",valor_anterior= self.config_20_1, valor_nuevo=self.variable_20_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_20_2.get() != self.config_20_2:
            changes.append([
                f"Tarifa avanzada Hora 20 fraccion 2: {self.config_20_2} -> {self.variable_20_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "20", "2", new_value=self.variable_20_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 20 fraccion 2",valor_anterior= self.config_20_2, valor_nuevo=self.variable_20_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_20_3.get() != self.config_20_3:
            changes.append([
                f"Tarifa avanzada Hora 20 fraccion 3: {self.config_20_3} -> {self.variable_20_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "20", "3", new_value=self.variable_20_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 20 fraccion 3",valor_anterior= self.config_20_3, valor_nuevo=self.variable_20_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_21_hora.get() != self.config_21_hora:
            changes.append([
                f"Tarifa avanzada Hora 21 hora completa: {self.config_21_hora} -> {self.variable_21_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "21", "hora", new_value=self.variable_21_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 21 hora completa",valor_anterior= self.config_21_hora, valor_nuevo=self.variable_21_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_21_1.get() != self.config_21_1:
            changes.append([
                f"Tarifa avanzada Hora 21 fraccion 1: {self.config_21_1} -> {self.variable_21_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "21", "1", new_value=self.variable_21_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 21 fraccion 1",valor_anterior= self.config_21_1, valor_nuevo=self.variable_21_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_21_2.get() != self.config_21_2:
            changes.append([
                f"Tarifa avanzada Hora 21 fraccion 2: {self.config_21_2} -> {self.variable_21_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "21", "2", new_value=self.variable_21_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 21 fraccion 2",valor_anterior= self.config_21_2, valor_nuevo=self.variable_21_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_21_3.get() != self.config_21_3:
            changes.append([
                f"Tarifa avanzada Hora 21 fraccion 3: {self.config_21_3} -> {self.variable_21_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "21", "3", new_value=self.variable_21_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 21 fraccion 3",valor_anterior= self.config_21_3, valor_nuevo=self.variable_21_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_22_hora.get() != self.config_22_hora:
            changes.append([
                f"Tarifa avanzada Hora 22 hora completa: {self.config_22_hora} -> {self.variable_22_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "22", "hora", new_value=self.variable_22_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 22 hora completa",valor_anterior= self.config_22_hora, valor_nuevo=self.variable_22_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_22_1.get() != self.config_22_1:
            changes.append([
                f"Tarifa avanzada Hora 22 fraccion 1: {self.config_22_1} -> {self.variable_22_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "22", "1", new_value=self.variable_22_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 22 fraccion 1",valor_anterior= self.config_22_1, valor_nuevo=self.variable_22_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_22_2.get() != self.config_22_2:
            changes.append([
                f"Tarifa avanzada Hora 22 fraccion 2: {self.config_22_2} -> {self.variable_22_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "22", "2", new_value=self.variable_22_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 22 fraccion 2",valor_anterior= self.config_22_2, valor_nuevo=self.variable_22_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_22_3.get() != self.config_22_3:
            changes.append([
                f"Tarifa avanzada Hora 22 fraccion 3: {self.config_22_3} -> {self.variable_22_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "22", "3", new_value=self.variable_22_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 22 fraccion 3",valor_anterior= self.config_22_3, valor_nuevo=self.variable_22_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_23_hora.get() != self.config_23_hora:
            changes.append([
                f"Tarifa avanzada Hora 23 hora completa: {self.config_23_hora} -> {self.variable_23_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "23", "hora", new_value=self.variable_23_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 23 hora completa",valor_anterior= self.config_23_hora, valor_nuevo=self.variable_23_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_23_1.get() != self.config_23_1:
            changes.append([
                f"Tarifa avanzada Hora 23 fraccion 1: {self.config_23_1} -> {self.variable_23_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "23", "1", new_value=self.variable_23_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 23 fraccion 1",valor_anterior= self.config_23_1, valor_nuevo=self.variable_23_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_23_2.get() != self.config_23_2:
            changes.append([
                f"Tarifa avanzada Hora 23 fraccion 2: {self.config_23_2} -> {self.variable_23_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "23", "2", new_value=self.variable_23_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 23 fraccion 2",valor_anterior= self.config_23_2, valor_nuevo=self.variable_23_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_23_3.get() != self.config_23_3:
            changes.append([
                f"Tarifa avanzada Hora 23 fraccion 3: {self.config_23_3} -> {self.variable_23_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "23", "3", new_value=self.variable_23_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 23 fraccion 3",valor_anterior= self.config_23_3, valor_nuevo=self.variable_23_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_24_hora.get() != self.config_24_hora:
            changes.append([
                f"Tarifa avanzada Hora 24 hora completa: {self.config_24_hora} -> {self.variable_24_hora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "24", "hora", new_value=self.variable_24_hora.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 24 hora completa",valor_anterior= self.config_24_hora, valor_nuevo=self.variable_24_hora.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_24_1.get() != self.config_24_1:
            changes.append([
                f"Tarifa avanzada Hora 24 fraccion 1: {self.config_24_1} -> {self.variable_24_1.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "24", "1", new_value=self.variable_24_1.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 24 fraccion 1",valor_anterior= self.config_24_1, valor_nuevo=self.variable_24_1.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_24_2.get() != self.config_24_2:
            changes.append([
                f"Tarifa avanzada Hora 24 fraccion 2: {self.config_24_2} -> {self.variable_24_2.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "24", "2", new_value=self.variable_24_2.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 24 fraccion 2",valor_anterior= self.config_24_2, valor_nuevo=self.variable_24_2.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_24_3.get() != self.config_24_3:
            changes.append([
                f"Tarifa avanzada Hora 24 fraccion 3: {self.config_24_3} -> {self.variable_24_3.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "tarifa", "tarifa_personalizada", "24", "3", new_value=self.variable_24_3.get()),
               self.cambios_model.add_change(nombre_cambio = "Tarifa avanzada Hora 24 fraccion 3",valor_anterior= self.config_24_3, valor_nuevo=self.variable_24_3.get(), tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if len(changes) == 0:
            mb.showerror("Alerta", "Sin cambios para guardar")
            return

        if ask_security_question(self.configuracion) != True:
            return

        for _, method_save_change in changes:
            method_save_change()
        
        list_changes = [tittle_change for tittle_change, _ in changes]
        state = self.printer_controller.print_changes("Cambios de configuracion\nTarifa general", list_changes)
        
        if state != None:
            mb.showwarning("Alerta", state)

        self.exit_system("Configuracion de tarifa general")

    def validate_data_tarifa(self):
        if self.variable_importe_boleto_perdido.get() == 0:
            raise ValidateDataError("Boleto perdido, no puede ser igual a 0")

        if self.variable_tipo_tarifa_sistema.get():
            data_tarifa = [self.variable_importe_primer_cuarto_hora.get(), self.variable_importe_segundo_cuarto_hora.get(
            ), self.variable_importe_tercer_cuarto_hora.get(), self.variable_importe_hora.get()]

        else:
            data_tarifa = [
                self.variable_0_hora.get(), self.variable_0_1.get(
                ), self.variable_0_2.get(), self.variable_0_3.get(),
                self.variable_1_hora.get(), self.variable_1_1.get(
                ), self.variable_1_2.get(), self.variable_1_3.get(),
                self.variable_2_hora.get(), self.variable_2_1.get(
                ), self.variable_2_2.get(), self.variable_2_3.get(),
                self.variable_3_hora.get(), self.variable_3_1.get(
                ), self.variable_3_2.get(), self.variable_3_3.get(),
                self.variable_4_hora.get(), self.variable_4_1.get(
                ), self.variable_4_2.get(), self.variable_4_3.get(),
                self.variable_5_hora.get(), self.variable_5_1.get(
                ), self.variable_5_2.get(), self.variable_5_3.get(),
                self.variable_6_hora.get(), self.variable_6_1.get(
                ), self.variable_6_2.get(), self.variable_6_3.get(),
                self.variable_7_hora.get(), self.variable_7_1.get(
                ), self.variable_7_2.get(), self.variable_7_3.get(),
                self.variable_8_hora.get(), self.variable_8_1.get(
                ), self.variable_8_2.get(), self.variable_8_3.get(),
                self.variable_9_hora.get(), self.variable_9_1.get(
                ), self.variable_9_2.get(), self.variable_9_3.get(),
                self.variable_10_hora.get(), self.variable_10_1.get(
                ), self.variable_10_2.get(), self.variable_10_3.get(),
                self.variable_11_hora.get(), self.variable_11_1.get(
                ), self.variable_11_2.get(), self.variable_11_3.get(),
                self.variable_12_hora.get(), self.variable_12_1.get(
                ), self.variable_12_2.get(), self.variable_12_3.get(),
                self.variable_13_hora.get(), self.variable_13_1.get(
                ), self.variable_13_2.get(), self.variable_13_3.get(),
                self.variable_14_hora.get(), self.variable_14_1.get(
                ), self.variable_14_2.get(), self.variable_14_3.get(),
                self.variable_15_hora.get(), self.variable_15_1.get(
                ), self.variable_15_2.get(), self.variable_15_3.get(),
                self.variable_16_hora.get(), self.variable_16_1.get(
                ), self.variable_16_2.get(), self.variable_16_3.get(),
                self.variable_17_hora.get(), self.variable_17_1.get(
                ), self.variable_17_2.get(), self.variable_17_3.get(),
                self.variable_18_hora.get(), self.variable_18_1.get(
                ), self.variable_18_2.get(), self.variable_18_3.get(),
                self.variable_19_hora.get(), self.variable_19_1.get(
                ), self.variable_19_2.get(), self.variable_19_3.get(),
                self.variable_20_hora.get(), self.variable_20_1.get(
                ), self.variable_20_2.get(), self.variable_20_3.get(),
                self.variable_21_hora.get(), self.variable_21_1.get(
                ), self.variable_21_2.get(), self.variable_21_3.get(),
                self.variable_22_hora.get(), self.variable_22_1.get(
                ), self.variable_22_2.get(), self.variable_22_3.get(),
                self.variable_23_hora.get(), self.variable_23_1.get(
                ), self.variable_23_2.get(), self.variable_23_3.get(),
                self.variable_24_hora.get(), self.variable_24_1.get(),
                self.variable_24_2.get(), self.variable_24_3.get()]

        if data_tarifa.count(0) == len(data_tarifa) or data_tarifa.count(0) > 0:
            raise ValidateDataError(
                "De los cuartos de hora asi como del importe de la hora no puede ser igual a 0, si desea agregar una cortesia, vaya al apartado de tarifas y agrege una nueva tarifa sensilla con los valores a 0")

    def clean_data_form_tarifa(self, update_interface: bool = True):
        self.variable_tipo_tarifa_sistema.set(self.tipo_tarifa_sistema)

        self.variable_importe_boleto_perdido.set(self.tarifa_boleto_perdido)

        self.variable_inicio_cobro_cuartos_hora.set(self.inicio_cobro_fraccion)
        self.variable_importe_primer_cuarto_hora.set(self.tarifa_1_fraccion)
        self.variable_importe_segundo_cuarto_hora.set(self.tarifa_2_fraccion)
        self.variable_importe_tercer_cuarto_hora.set(self.tarifa_3_fraccion)
        self.variable_importe_hora.set(self.tarifa_hora)

        self.variable_0_hora.set(self.config_0_hora)
        self.variable_0_1.set(self.config_0_1)
        self.variable_0_2.set(self.config_0_2)
        self.variable_0_3.set(self.config_0_3)

        self.variable_1_hora.set(self.config_1_hora)
        self.variable_1_1.set(self.config_1_1)
        self.variable_1_2.set(self.config_1_2)
        self.variable_1_3.set(self.config_1_3)

        self.variable_2_hora.set(self.config_2_hora)
        self.variable_2_1.set(self.config_2_1)
        self.variable_2_2.set(self.config_2_2)
        self.variable_2_3.set(self.config_2_3)

        self.variable_3_hora.set(self.config_3_hora)
        self.variable_3_1.set(self.config_3_1)
        self.variable_3_2.set(self.config_3_2)
        self.variable_3_3.set(self.config_3_3)

        self.variable_4_hora.set(self.config_4_hora)
        self.variable_4_1.set(self.config_4_1)
        self.variable_4_2.set(self.config_4_2)
        self.variable_4_3.set(self.config_4_3)

        self.variable_5_hora.set(self.config_5_hora)
        self.variable_5_1.set(self.config_5_1)
        self.variable_5_2.set(self.config_5_2)
        self.variable_5_3.set(self.config_5_3)

        self.variable_6_hora.set(self.config_6_hora)
        self.variable_6_1.set(self.config_6_1)
        self.variable_6_2.set(self.config_6_2)
        self.variable_6_3.set(self.config_6_3)

        self.variable_7_hora.set(self.config_7_hora)
        self.variable_7_1.set(self.config_7_1)
        self.variable_7_2.set(self.config_7_2)
        self.variable_7_3.set(self.config_7_3)

        self.variable_8_hora.set(self.config_8_hora)
        self.variable_8_1.set(self.config_8_1)
        self.variable_8_2.set(self.config_8_2)
        self.variable_8_3.set(self.config_8_3)

        self.variable_9_hora.set(self.config_9_hora)
        self.variable_9_1.set(self.config_9_1)
        self.variable_9_2.set(self.config_9_2)
        self.variable_9_3.set(self.config_9_3)

        self.variable_10_hora.set(self.config_10_hora)
        self.variable_10_1.set(self.config_10_1)
        self.variable_10_2.set(self.config_10_2)
        self.variable_10_3.set(self.config_10_3)

        self.variable_11_hora.set(self.config_11_hora)
        self.variable_11_1.set(self.config_11_1)
        self.variable_11_2.set(self.config_11_2)
        self.variable_11_3.set(self.config_11_3)

        self.variable_12_hora.set(self.config_12_hora)
        self.variable_12_1.set(self.config_12_1)
        self.variable_12_2.set(self.config_12_2)
        self.variable_12_3.set(self.config_12_3)

        self.variable_13_hora.set(self.config_13_hora)
        self.variable_13_1.set(self.config_13_1)
        self.variable_13_2.set(self.config_13_2)
        self.variable_13_3.set(self.config_13_3)

        self.variable_14_hora.set(self.config_14_hora)
        self.variable_14_1.set(self.config_14_1)
        self.variable_14_2.set(self.config_14_2)
        self.variable_14_3.set(self.config_14_3)

        self.variable_15_hora.set(self.config_15_hora)
        self.variable_15_1.set(self.config_15_1)
        self.variable_15_2.set(self.config_15_2)
        self.variable_15_3.set(self.config_15_3)

        self.variable_16_hora.set(self.config_16_hora)
        self.variable_16_1.set(self.config_16_1)
        self.variable_16_2.set(self.config_16_2)
        self.variable_16_3.set(self.config_16_3)

        self.variable_17_hora.set(self.config_17_hora)
        self.variable_17_1.set(self.config_17_1)
        self.variable_17_2.set(self.config_17_2)
        self.variable_17_3.set(self.config_17_3)

        self.variable_18_hora.set(self.config_18_hora)
        self.variable_18_1.set(self.config_18_1)
        self.variable_18_2.set(self.config_18_2)
        self.variable_18_3.set(self.config_18_3)

        self.variable_19_hora.set(self.config_19_hora)
        self.variable_19_1.set(self.config_19_1)
        self.variable_19_2.set(self.config_19_2)
        self.variable_19_3.set(self.config_19_3)

        self.variable_20_hora.set(self.config_20_hora)
        self.variable_20_1.set(self.config_20_1)
        self.variable_20_2.set(self.config_20_2)
        self.variable_20_3.set(self.config_20_3)

        self.variable_21_hora.set(self.config_21_hora)
        self.variable_21_1.set(self.config_21_1)
        self.variable_21_2.set(self.config_21_2)
        self.variable_21_3.set(self.config_21_3)

        self.variable_22_hora.set(self.config_22_hora)
        self.variable_22_1.set(self.config_22_1)
        self.variable_22_2.set(self.config_22_2)
        self.variable_22_3.set(self.config_22_3)

        self.variable_23_hora.set(self.config_23_hora)
        self.variable_23_1.set(self.config_23_1)
        self.variable_23_2.set(self.config_23_2)
        self.variable_23_3.set(self.config_23_3)

        self.variable_24_hora.set(self.config_24_hora)
        self.variable_24_1.set(self.config_24_1)
        self.variable_24_2.set(self.config_24_2)
        self.variable_24_3.set(self.config_24_3)

        if update_interface:
            self.change_tarifa(False)

    def save_data_general(self):
        try:
            nombre_usuario_activo = self.DB.nombre_usuario_activo()
            if nombre_usuario_activo is None:
                raise SystemError("No se puede guarda la informacion ya que no has iniciado sesion, reinicia el sistema e inicia sesion para poder hacert cambios en el sistema.\n\nSi consideras que se trata de un error ponte en contacto con un administrador inmediatamente")
            self.validate_data_general()

            changes = []
            tipo_cambio = "Configuracion General"

            if self.variable_nombre_estacionamiento.get() != self.nombre_estacionamiento:
                changes.append([
                    f"Nombre de estacionamiento: {self.nombre_estacionamiento} -> {self.variable_nombre_estacionamiento.get()}",
                    lambda: {self.instance_config.set_config(
                        "general", "informacion_estacionamiento", "nombre_estacionamiento", new_value=self.variable_nombre_estacionamiento.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Nombre de estacionamiento",valor_anterior=self.nombre_estacionamiento, valor_nuevo=self.variable_nombre_estacionamiento.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])


            if self.variable_correo_estacionamiento.get() != self.email:
                changes.append([
                    f"Correo de estacionamiento: {self.email} -> {self.variable_correo_estacionamiento.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "informacion_estacionamiento", "email", new_value=self.variable_correo_estacionamiento.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Correo de estacionamiento",valor_anterior=self.email, valor_nuevo=self.variable_correo_estacionamiento.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            value = "" if self.without_decode_email_system else self.instance_tools.descifrar_AES(
                self.__password__, bytes.fromhex(self.__iv_password__))
            if self.__variable_contraseña_correo__.get() != value:
                password, iv = self.instance_tools.cifrar_AES(
                    self.__variable_contraseña_correo__.get())
                changes.append([
                    f"Contraseña de correo",
                    lambda p=password, tipo_cambio=tipo_cambio: {self.instance_config.set_config(
                        "general", "informacion_estacionamiento", "password", new_value=p),
                    self.cambios_model.add_change(
                        nombre_cambio = "Contraseña de correo",valor_anterior="N/A", valor_nuevo="N/A",
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])
                changes.append([
                    f"IV de contraseña de correo",
                    lambda iv_hex=iv.hex(): {self.instance_config.set_config(
                        "general", "informacion_estacionamiento", "iv", new_value=iv_hex)
               } ])
            value = None

            if self.variable_cantidad_cajones.get() != self.cantidad_cajones:
                changes.append([
                    f"Cantidad de cajones: {self.cantidad_cajones} -> {self.variable_cantidad_cajones.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "informacion_estacionamiento", "cantidad_cajones", new_value=self.variable_cantidad_cajones.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Cantidad de cajones",valor_anterior=self.cantidad_cajones, valor_nuevo=self.variable_cantidad_cajones.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_nombre_entrada.get() != self.nombre_entrada:
                changes.append([
                    f"Nombre de entrada: {self.nombre_entrada} -> {self.variable_nombre_entrada.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "informacion_estacionamiento", "nombre_entrada", new_value=self.variable_nombre_entrada.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Nombre de entrada",valor_anterior=self.nombre_entrada, valor_nuevo=self.variable_nombre_entrada.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])
                
            tipo_cambio = "Configuracion de pensionados"

            if self.variable_contraseña_modulo_pensionados.get() != self.instance_tools.descifrar_AES(self.__contraseña_pensionados__, bytes.fromhex(self.__iv_pensionados__)):
                password, iv = self.instance_tools.cifrar_AES(
                    self.variable_contraseña_modulo_pensionados.get())
                changes.append([
                    f"Contraseña de pensionados",
                    lambda p=password, tipo_cambio=tipo_cambio: {self.instance_config.set_config(
                        "general", "configuracion_pensionados", "password", new_value=p),
                    self.cambios_model.add_change(
                        nombre_cambio = "Contraseña de pensionados",valor_anterior="N/A", valor_nuevo="N/A",
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])
                changes.append([
                    f"IV de contraseña de pensionados",
                    lambda iv_hex=iv.hex(): {self.instance_config.set_config(
                        "general", "configuracion_pensionados", "iv", new_value=iv_hex)
               } ])

            if self.variable_costo_tarjeta.get() != self.valor_tarjeta:
                changes.append([
                    f"Costo de tarjeta: {self.valor_tarjeta} -> {self.variable_costo_tarjeta.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_pensionados", "costo_tarjeta", new_value=self.variable_costo_tarjeta.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Costo de tarjeta",valor_anterior=self.valor_tarjeta, valor_nuevo=self.variable_costo_tarjeta.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_costo_reposicion.get() != self.valor_reposicion_tarjeta:
                changes.append([
                    f"Costo de reposicion de tarjeta: {self.valor_reposicion_tarjeta} -> {self.variable_costo_reposicion.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_pensionados", "costo_reposicion_tarjeta", new_value=self.variable_costo_reposicion.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Costo de reposicion de tarjeta",valor_anterior=self.valor_reposicion_tarjeta, valor_nuevo=self.variable_costo_reposicion.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_penalizacion_diaria.get() != self.penalizacion_diaria_pension:
                changes.append([
                    f"Penalizacion de pago atrazado: {self.penalizacion_diaria_pension} -> {self.variable_penalizacion_diaria.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_pensionados", "penalizacion_diaria", new_value=self.variable_penalizacion_diaria.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Penalizacion de pago atrazado",valor_anterior=self.penalizacion_diaria_pension, valor_nuevo=self.variable_penalizacion_diaria.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])
                
            tipo_cambio = "Funcionalidades del sistema"

            if self.variable_requiere_placa.get() != self.requiere_placa:
                estado_actual = "Si" if self.variable_requiere_placa.get() else "No"
                estado_sistema = "Si" if self.requiere_placa else "No"
                changes.append([
                    f"Requiere ingresar placa para generar boleto: {estado_sistema} -> {estado_actual}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "requiere_placa", new_value=self.variable_requiere_placa.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Requiere ingresar placa para generar boleto",valor_anterior=estado_sistema, valor_nuevo=estado_actual,
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_penalizacion_boleto_perdido.get() != self.penalizacion_con_importe:
                estado_actual = "Si" if self.variable_penalizacion_boleto_perdido.get() else "No"
                estado_sistema = "Si" if self.penalizacion_con_importe else "No"
                changes.append([
                    f"Se suma penalizacion de boleto perdido a importe de boleto: {estado_sistema} -> {estado_actual}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "penalizacion_boleto_perdido", new_value=self.variable_penalizacion_boleto_perdido.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Se suma penalizacion de boleto perdido a importe de boleto",valor_anterior=estado_sistema, valor_nuevo=estado_actual,
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_reloj_habilitado.get() != self.show_clock:
                estado_actual = "Si" if self.variable_reloj_habilitado.get() else "No"
                estado_sistema = "Si" if self.show_clock else "No"
                changes.append([
                    f"Reloj activado: {estado_sistema} -> {estado_actual}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "reloj", new_value=self.variable_reloj_habilitado.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Reloj activado",valor_anterior=estado_sistema, valor_nuevo=estado_actual,
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_envio_informacion.get() != self.envio_informacion:
                estado_actual = "Si" if self.variable_envio_informacion.get() else "No"
                estado_sistema = "Si" if self.envio_informacion else "No"
                changes.append([
                    f"Envio de informacion activado: {estado_sistema} -> {estado_actual}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "envio_informacion", new_value=self.variable_envio_informacion.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Envio de informacion activado",valor_anterior=estado_sistema, valor_nuevo=estado_actual,
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_pantalla_completa.get() != self.pantalla_completa:
                estado_actual = "Si" if self.variable_pantalla_completa.get() else "No"
                estado_sistema = "Si" if self.pantalla_completa else "No"
                changes.append([
                    f"Pantalla completa activada: {estado_sistema} -> {estado_actual}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "pantalla_completa", new_value=self.variable_pantalla_completa.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Pantalla completa activada",valor_anterior=estado_sistema, valor_nuevo=estado_actual,
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_imprime_contra_parabrisas.get() != self.imprime_contra_parabrisas:
                estado_actual = "Si" if self.variable_imprime_contra_parabrisas.get() else "No"
                estado_sistema = "Si" if self.imprime_contra_parabrisas else "No"
                changes.append([
                    f"Imprime contra de parabrisas: {estado_sistema} -> {estado_actual}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "imprime_contra_parabrisas", new_value=self.variable_imprime_contra_parabrisas.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Imprime contra de parabrisas",valor_anterior=estado_sistema, valor_nuevo=estado_actual,
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_imprime_contra_localizacion.get() != self.imprime_contra_localizacion:
                estado_actual = "Si" if self.variable_imprime_contra_localizacion.get() else "No"
                estado_sistema = "Si" if self.imprime_contra_localizacion else "No"
                changes.append([
                    f"Imprime contra de localizacion: {estado_sistema} -> {estado_actual}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "imprime_contra_localizacion", new_value=self.variable_imprime_contra_localizacion.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Imprime contra de localizacion",valor_anterior=estado_sistema, valor_nuevo=estado_actual,
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_solicita_datos_del_auto.get() != self.solicita_datos_del_auto:
                estado_actual = "Si" if self.variable_solicita_datos_del_auto.get() else "No"
                estado_sistema = "Si" if self.solicita_datos_del_auto else "No"
                changes.append([
                    f"Solicita datos del auto: {estado_sistema} -> {estado_actual}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "solicita_datos_del_auto", new_value=self.variable_solicita_datos_del_auto.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Solicita datos del auto",valor_anterior=estado_sistema, valor_nuevo=estado_actual,
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_habilita_impresion_boleto_perdido.get() != self.habilita_impresion_boleto_perdido:
                estado_actual = "Si" if self.variable_habilita_impresion_boleto_perdido.get() else "No"
                estado_sistema = "Si" if self.habilita_impresion_boleto_perdido else "No"
                changes.append([
                    f"Habilita impresion de boleto perdido: {estado_sistema} -> {estado_actual}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "habilita_impresion_boleto_perdido", new_value=self.variable_habilita_impresion_boleto_perdido.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Habilita impresion de boleto perdido",valor_anterior=estado_sistema, valor_nuevo=estado_actual,
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_size_font_boleto.get() != self.size_font_boleto:
                changes.append([
                    f"Tamaño de letra de boleto: {self.size_font_boleto} -> {self.variable_size_font_boleto.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "size_font_boleto", new_value=self.variable_size_font_boleto.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tamaño de letra de boleto",valor_anterior=self.size_font_boleto, valor_nuevo=self.variable_size_font_boleto.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_size_font_contra_parabrisas.get() != self.size_font_contra_parabrisas:
                changes.append([
                    f"Tamaño de letra de contra se parabrisas: {self.size_font_contra_parabrisas} -> {self.variable_size_font_contra_parabrisas.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "size_font_contra_parabrisas", new_value=self.variable_size_font_contra_parabrisas.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tamaño de letra de contra se parabrisas",valor_anterior=self.size_font_contra_parabrisas, valor_nuevo=self.variable_size_font_contra_parabrisas.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if self.variable_size_font_contra_localizacion.get() != self.size_font_contra_localizacion:
                changes.append([
                    f"Tamaño de letra de contra se localizacion: {self.size_font_contra_localizacion} -> {self.variable_size_font_contra_localizacion.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "size_font_contra_localizacion", new_value=self.variable_size_font_contra_localizacion.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tamaño de letra de contra se localizacion",valor_anterior=self.size_font_contra_localizacion, valor_nuevo=self.variable_size_font_contra_localizacion.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
               } ])

            if len(changes) == 0:
                mb.showerror("Alerta", "Sin cambios para guardar")
                return

            if ask_security_question(self.configuracion) != True:
                return

            for _, method_save_change in changes:
                method_save_change()
            
            list_changes = [tittle_change for tittle_change, _ in changes]
            state = self.printer_controller.print_changes("Cambios de configuracion\nGeneral", list_changes)

            if state != None:
                mb.showwarning("Alerta", state)

            self.exit_system("Configuracion general")

        except TclError as e:
            mb.showerror("Error", "No debe de dejar campos en blanco")
            return
        except Exception as e:
            mb.showerror("Error", e)
            return
        finally:
            if self.visible_password_info_estacionamiento.get():
                self.instance_tools.visible_password(
                    self.boton_hide_view_password_info_estacionamiento, self.entry_contraseña_correo, self.visible_password_info_estacionamiento, self.show_password_icon, self.hide_password_icon)

            if self.visible_password_modulo_pensionados.get():
                self.instance_tools.visible_password(
                    self.boton_hide_view_password_modulo_pensionados, self.entry_contraseña_modulo_pensionados, self.visible_password_modulo_pensionados, self.show_password_icon, self.hide_password_icon)

    def validate_data_general(self):
        if self.variable_nombre_estacionamiento.get() == "":
            self.entry_contraseña_correo.focus()
            raise WithoutParameter("El nombre del estacionamiento")

        if self.variable_correo_estacionamiento.get() != "":
            self.instance_tools.validate_email(self.variable_correo_estacionamiento.get(
            ), self.entry_correo_estacionamiento, "Configuracion del sistema")

            if self.__variable_contraseña_correo__.get() == "":
                self.entry_contraseña_correo.focus()
                raise WithoutParameter("La contraseña del correo")

        if self.variable_contraseña_modulo_pensionados.get() == "":
            raise WithoutParameter("La contraseña del modulo de pensinados")

        if self.variable_destinatario_db.get() == "" and len(self.variable_destinatario_corte.get()) == 0 and len(self.variable_destinatario_notificaciones.get()) == 0 and self.variable_envio_informacion.get():
            mb.showinfo(
                "Recordatorio", "- No olvide configurar los correos electronicos a los que ese enviará la informacion")

    def clean_data_form_general(self):
        self.variable_nombre_estacionamiento.set(self.nombre_estacionamiento)
        self.variable_path_logo.set(self.logo)
        self.variable_imagen_marcas_auto.set(self.imagen_marcas_auto)
        self.variable_correo_estacionamiento.set(self.email)
        value = "" if self.without_decode_email_system else self.instance_tools.descifrar_AES(
            self.__password__, bytes.fromhex(self.__iv_password__))
        self.__variable_contraseña_correo__.set(value)
        value = None
        self.variable_cantidad_cajones.set(self.cantidad_cajones)
        self.variable_nombre_entrada.set(self.nombre_entrada)
        self.variable_contraseña_modulo_pensionados.set(
            self.instance_tools.descifrar_AES(self.__contraseña_pensionados__, bytes.fromhex(self.__iv_pensionados__)))
        self.variable_costo_tarjeta.set(self.valor_tarjeta)
        self.variable_costo_reposicion.set(self.valor_reposicion_tarjeta)
        self.variable_penalizacion_diaria.set(self.penalizacion_diaria_pension)
        self.variable_requiere_placa.set(self.requiere_placa)
        self.variable_penalizacion_boleto_perdido.set(
            self.penalizacion_con_importe)
        self.variable_reloj_habilitado.set(self.show_clock)
        self.variable_envio_informacion.set(self.envio_informacion)
        self.variable_pantalla_completa.set(self.pantalla_completa)

        self.variable_imprime_contra_parabrisas.set(
            self.imprime_contra_parabrisas)
        self.variable_imprime_contra_localizacion.set(
            self.imprime_contra_localizacion)
        self.variable_solicita_datos_del_auto.set(self.solicita_datos_del_auto)
        self.variable_habilita_impresion_boleto_perdido.set(self.habilita_impresion_boleto_perdido)

        self.variable_size_font_boleto.set(self.size_font_boleto)
        self.variable_size_font_contra_parabrisas.set(
            self.size_font_contra_parabrisas)
        self.variable_size_font_contra_localizacion.set(
            self.size_font_contra_localizacion)

        if self.visible_password_info_estacionamiento.get():
            self.instance_tools.visible_password(self.boton_hide_view_password_info_estacionamiento, self.entry_contraseña_correo,
                                                 self.visible_password_info_estacionamiento, self.show_password_icon, self.hide_password_icon)

        if self.visible_password_modulo_pensionados.get():
            self.instance_tools.visible_password(self.boton_hide_view_password_modulo_pensionados, self.entry_contraseña_modulo_pensionados,
                                                 self.visible_password_modulo_pensionados, self.show_password_icon, self.hide_password_icon)

    def save_data_interna(self):
        try:
            if self.variable_db_usuario.get() != self.db_usser or self.__variable_db_contraseña__.get() != self.instance_tools.descifrar_AES(self.__db_password__, bytes.fromhex(self.__db_iv__)) or self.variable_db_host.get() != self.db_host or self.variable_db_db.get() != self.db_db:
                nombre_usuario_activo = "N/A"
                
            else:
                nombre_usuario_activo = self.DB.nombre_usuario_activo()

            if nombre_usuario_activo is None:
                raise SystemError("No se puede guarda la informacion ya que no has iniciado sesion, reinicia el sistema e inicia sesion para poder hacert cambios en el sistema.\n\nSi consideras que se trata de un error ponte en contacto con un administrador inmediatamente")

            self.validate_data_interna()

        except TclError as e:
            mb.showerror("Error", "No debe de dejar campos en blanco")
            return
        except Exception as e:
            mb.showerror("Error", e)
            return

        changes = []
        tipo_cambio = "Funcionamiento interno"

        if self.variable_id_vendor_impresora.get() != self.printer_idVendor or self.variable_id_product_impresora.get() != self.printer_idProduct:
            changes.append([
                f"ID-Vendor de impresora: {self.printer_idVendor} -> {self.variable_id_vendor_impresora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "general", "configuracion_sistema", "impresora", "idVendor", new_value=self.variable_id_vendor_impresora.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Impresora",valor_anterior="N/A", valor_nuevo="N/A",
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

            changes.append([
                f"ID-Product de impresora: {self.printer_idProduct} -> {self.variable_id_product_impresora.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "general", "configuracion_sistema", "impresora", "idProduct", new_value=self.variable_id_product_impresora.get())
           } ])

            mb.showerror("Alerta", "Se detecta cambio en impresora, el sistema ignorará cualquier otro cambio y se reiniciará, en caso de haber hecho cualquier otra modificacion esta no se guardará por lo que deberá volver a hacerla.")

            if ask_security_question(self.configuracion) != True:
                return

            for _, method_save_change in changes:
                method_save_change()

            self.exit_system("Configuracion interna")

        if self.system_options.index(self.variable_system_to_load.get()) != self.system_to_load:
            changes.append([
                f"Uso del sistema: {self.system_options[self.system_to_load]} -> {self.system_options[self.system_options.index(self.variable_system_to_load.get())]}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config("system_to_load", new_value=self.system_options.index(self.variable_system_to_load.get())),
                    self.cambios_model.add_change(
                        nombre_cambio = "Uso del sistema",valor_anterior=self.system_options[self.system_to_load], valor_nuevo=self.system_options[self.system_options.index(self.variable_system_to_load.get())],
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

        tipo_cambio = "Configuracion de base de datos"

        if self.variable_db_usuario.get() != self.db_usser:
            changes.append([
                f"Nombre de usuario de DB: {self.db_usser} -> {self.variable_db_usuario.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "funcionamiento_interno", "db", "usuario", new_value=self.variable_db_usuario.get())
           } ])

        if self.__variable_db_contraseña__.get() != self.instance_tools.descifrar_AES(self.__db_password__, bytes.fromhex(self.__db_iv__)):
            password, iv = self.instance_tools.cifrar_AES(
                self.__variable_db_contraseña__.get())

            changes.append([
                f"Contraseña de usuario de DB",
                lambda p=password, tipo_cambio=tipo_cambio: {self.instance_config.set_config(
                    "funcionamiento_interno", "db", "password", new_value=p)
           } ])
            changes.append([
                f"IV de contraseña de usuario de DB",
                lambda iv_hex=iv.hex(): {self.instance_config.set_config(
                    "funcionamiento_interno", "db", "iv", new_value=iv_hex)
           } ])

        if self.variable_db_host.get() != self.db_host:
            changes.append([
                f"Host de DB: {self.db_host} -> {self.variable_db_host.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "funcionamiento_interno", "db", "host", new_value=self.variable_db_host.get())
           } ])

        if self.variable_db_db.get() != self.db_db:
            changes.append([
                f"Nombre de DB: {self.db_db} -> {self.variable_db_db.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "funcionamiento_interno", "db", "db", new_value=self.variable_db_db.get())
           } ])
            
        tipo_cambio = "Funcionamiento interno"

        if self.variable_usuario_panel_usuarios.get() != self.usuario_panel_usuarios:
            changes.append([
                f"Usuario de panel de administracion usuarios: {self.usuario_panel_usuarios} -> {self.variable_usuario_panel_usuarios.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "funcionamiento_interno", "panel_usuarios", "usuario", new_value=self.variable_usuario_panel_usuarios.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Usuario de panel de administracion usuarios",valor_anterior=self.usuario_panel_usuarios, valor_nuevo=self.variable_usuario_panel_usuarios.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if self.variable_contraseña_panel_usuarios.get() != self.instance_tools.descifrar_AES(self.__contraseña_panel_usuarios__, bytes.fromhex(self.__iv_panel_usuarios__)):
            password, iv = self.instance_tools.cifrar_AES(
                self.variable_contraseña_panel_usuarios.get())
            changes.append([
                f"Contraseña de panel de administracion usuarios",
                lambda p=password, tipo_cambio=tipo_cambio: {self.instance_config.set_config(
                    "funcionamiento_interno", "panel_usuarios", "contraseña", new_value=p),
                    self.cambios_model.add_change(
                        nombre_cambio = "Contraseña del panel de administracion usuarios",valor_anterior="N/A", valor_nuevo="N/A",
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])
            changes.append([
                f"IV de contraseña de panel de administracion usuarios",
                lambda iv_hex=iv.hex(): {self.instance_config.set_config(
                    "funcionamiento_interno", "panel_usuarios", "iv", new_value=iv_hex)
           } ])

        if self.variable_contraseña_panel_config.get() != self.instance_tools.descifrar_AES(self.__contraseña_panel_config__, bytes.fromhex(self.__iv_panel_config__)):
            password, iv = self.instance_tools.cifrar_AES(
                self.variable_contraseña_panel_config.get())
            changes.append([
                f"Contraseña de panel de configuracion",
                lambda p=password, tipo_cambio=tipo_cambio: {self.instance_config.set_config(
                    "funcionamiento_interno", "panel_configuracion", "contraseña", new_value=p),
                    self.cambios_model.add_change(
                        nombre_cambio = "Contraseña del panel de configuracion",valor_anterior="N/A", valor_nuevo="N/A",
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])
            changes.append([
                f"IV de contraseña de panel de configuracion",
                lambda iv_hex=iv.hex(): {self.instance_config.set_config(
                    "funcionamiento_interno", "panel_configuracion", "iv", new_value=iv_hex)
           } ])

        if self.variable_usuario_panel_config.get() != self.usuario_panel_config:
            changes.append([
                f"Usuario de panel de configuracion: {self.usuario_panel_config} -> {self.variable_usuario_panel_config.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "funcionamiento_interno", "panel_configuracion", "usuario", new_value=self.variable_usuario_panel_config.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Usuario de panel de configuracion",valor_anterior=self.usuario_panel_config, valor_nuevo=self.variable_usuario_panel_config.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        tipo_cambio = "Configuracion de envio de informacion"

        if self.variable_destinatario_db.get() != self.destinatario_DB:
            changes.append([
                f"Destinatario de envio de DB: {self.destinatario_DB} -> {self.variable_destinatario_db.get()}",
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "general", "configuiracion_envio", "destinatario_DB", new_value=self.variable_destinatario_db.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Destinatario de envio de DB",valor_anterior=self.destinatario_DB, valor_nuevo=self.variable_destinatario_db.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if list(self.variable_destinatario_corte.get()) != self.destinatario_corte:
            changes.append([
                f"Lista de destinatarios de envio de corte: {self.destinatario_corte} -> {list(self.variable_destinatario_corte.get())}".replace(
                    "'", ""),
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "general", "configuiracion_envio", "destinatario_corte", new_value=self.variable_destinatario_corte.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Lista de destinatarios de envio de corte",valor_anterior=", ".join(self.destinatario_corte), valor_nuevo=", ".join(self.variable_destinatario_corte.get()),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])

        if list(self.variable_destinatario_notificaciones.get()) != self.destinatario_notificaciones:
            changes.append([
                f"Lista de destinatarios de envio de notificaciones: {self.destinatario_notificaciones} -> {list(self.variable_destinatario_notificaciones.get())}".replace(
                    "'", ""),
                lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                    "general", "configuiracion_envio", "destinatario_notificaciones", new_value=self.variable_destinatario_notificaciones.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Lista de destinatarios de envio de notificaciones",valor_anterior=", ".join(self.destinatario_notificaciones), valor_nuevo=", ".join(self.variable_destinatario_notificaciones.get()),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
           } ])



        if len(changes) == 0:
            mb.showerror("Alerta", "Sin cambios para guardar")
            return
        else:
            if ask_security_question(self.configuracion, False) != True:
                return

            for _, method_save_change in changes:
                method_save_change()
            
            list_changes = [tittle_change for tittle_change, _ in changes]
            state = self.printer_controller.print_changes("Cambios de configuracion\nInterna", list_changes)
            
            if state != None:
                mb.showwarning("Alerta", state)

            self.exit_system("Configuracion interna")

        if self.state_form:
            self.state_form_db_config(False)

        if self.system_to_load == 0:

            if self.visible_password_db.get():
                self.instance_tools.visible_password(self.boton_hide_view_password_db, self.entry_variable_db_contraseña,
                                                     self.visible_password_db, self.show_password_icon, self.hide_password_icon)

            if self.visible_password_config_panel_usuarios.get():
                self.instance_tools.visible_password(self.boton_hide_view_password_config_panel_usuarios, self.entry_contraseña_panel_usuarios,
                                                     self.visible_password_config_panel_usuarios, self.show_password_icon, self.hide_password_icon)

            if self.visible_password_config_panel_config.get():
                self.instance_tools.visible_password(self.boton_hide_view_password_config_panel_config, self.entry_contraseña_panel_config,
                                                     self.visible_password_config_panel_config, self.show_password_icon, self.hide_password_icon)

    def state_form_db_config(self, state=None):
        if self.state_form == False:
            if mb.askyesno("Advertencia", "La siguiente seccion se configuracion es sensible por lo que no es recomendable modificar si no se tiene conocimiento de lo que se esta haciendo o si no se tienen indicaciones del personal correspondiente \n\n\t¿Esta seguro de querer continuar?") == False:
                return

        if ask_security_question(self.configuracion, False) != True:
            return

        self.state_form = not self.state_form if state == None else state

        state_entry = 'normal' if self.state_form else 'disabled'
        text = 'Desactivar configuracion' if self.state_form else 'Activar configuracion'

        self.botton_state_form_db_config.configure(text=text)

        self.entry_db_usuario.configure(state=state_entry)
        self.entry_variable_db_contraseña.configure(state=state_entry)
        self.entry_db_host.configure(state=state_entry)
        self.entry_db_db.configure(state=state_entry)

        if self.state_form == False and self.visible_password_db.get():
            self.instance_tools.visible_password(self.boton_hide_view_password_db, self.entry_variable_db_contraseña,
                                                 self.visible_password_db, self.show_password_icon, self.hide_password_icon)

    def validate_data_interna(self):

        if self.variable_db_usuario.get() == "":
            raise WithoutParameter(
                "El nombre de usuario para la base de datos")

        if self.__variable_db_contraseña__.get() == "":
            raise WithoutParameter(
                "La contraseña del usuario para la base de datos")

        if self.variable_db_host.get() == "":
            raise WithoutParameter("El host de la base de datos")

        if self.variable_db_db.get() == "":
            raise WithoutParameter("El nombre de la base de datoss")

        if self.variable_envio_informacion.get():
            if self.variable_destinatario_db.get() == "":
                raise SystemError(
                    "Esta activado el envio de informacion, tiene que ingresar el destinatario del envio de DB")

            if self.variable_destinatario_corte.get() == []:
                raise SystemError(
                    "Esta activado el envio de informacion, tiene que ingresar el destinatario del envio del corte")

            if self.variable_destinatario_notificaciones.get() == []:
                raise SystemError(
                    "Esta activado el envio de informacion, tiene que ingresar el destinatario del envio de las notificaciones")

        if self.system_to_load == 0:

            if self.variable_destinatario_db.get() != "":
                self.instance_tools.validate_email(self.variable_destinatario_db.get(
                ), self.entry_destinatario_db, "Destinatario de DB")

        if self.variable_usuario_panel_usuarios.get() == "" or self.variable_contraseña_panel_usuarios.get() == "":
            raise WithoutParameter(
                "Las credenciales para el usuario del panel de administracion de usuarios")

        if self.variable_usuario_panel_config.get() == "" or self.variable_contraseña_panel_config.get() == "":
            raise WithoutParameter(
                "Las credenciales para el usuario del panel de configuracion")

    def clean_data_form_interna(self):
        self.variable_system_to_load.set(
            self.system_options[self.system_to_load])

        self.variable_db_usuario.set(self.db_usser)
        self.__variable_db_contraseña__.set(
            self.instance_tools.descifrar_AES(self.__db_password__, bytes.fromhex(self.__db_iv__)))
        self.variable_db_host.set(self.db_host)
        self.variable_db_db.set(self.db_db)

        self.variable_usuario_panel_usuarios.set(self.usuario_panel_usuarios)
        self.variable_contraseña_panel_usuarios.set(
            self.instance_tools.descifrar_AES(self.__contraseña_panel_usuarios__, bytes.fromhex(self.__iv_panel_usuarios__)))

        self.variable_usuario_panel_config.set(self.usuario_panel_config)
        self.variable_contraseña_panel_config.set(
            self.instance_tools.descifrar_AES(self.__contraseña_panel_config__, bytes.fromhex(self.__iv_panel_config__)))

        self.variable_destinatario_db.set(self.destinatario_DB)
        self.variable_destinatario_corte.set(self.destinatario_corte)
        self.variable_destinatario_notificaciones.set(
            self.destinatario_notificaciones)

        self.variable_id_vendor_impresora.set(self.printer_idVendor)
        self.variable_id_product_impresora.set(self.printer_idProduct)

        if self.system_to_load == 0:
            if self.visible_password_config_panel_usuarios.get():
                self.instance_tools.visible_password(
                    self.boton_hide_view_password_config_panel_usuarios, self.entry_contraseña_panel_usuarios, self.visible_password_config_panel_usuarios, self.show_password_icon, self.hide_password_icon)

        if self.visible_password_db.get():
            self.instance_tools.visible_password(
                self.boton_hide_view_password_db, self.entry_variable_db_contraseña, self.visible_password_db, self.show_password_icon, self.hide_password_icon)

        if self.visible_password_config_panel_config.get():
            self.instance_tools.visible_password(
                self.boton_hide_view_password_config_panel_config, self.entry_contraseña_panel_config, self.visible_password_config_panel_config, self.show_password_icon, self.hide_password_icon)

        if self.state_form:
            self.state_form_db_config(False)

        self.variable_printer_system.set(self.printer_system)

    def save_data_interface(self):
        try:
            nombre_usuario_activo = self.DB.nombre_usuario_activo()
            if nombre_usuario_activo is None:
                raise SystemError("No se puede guarda la informacion ya que no has iniciado sesion, reinicia el sistema e inicia sesion para poder hacert cambios en el sistema.\n\nSi consideras que se trata de un error ponte en contacto con un administrador inmediatamente")

            changes = []
            tipo_cambio = "Configuracion de interface"

            if self.date_examples.index(self.variable_formato_fecha_interface.get()) != self.date_format_interface:
                changes.append([
                    f"Formato de fecha de interface: {self.date_examples[self.date_format_interface]} -> {self.date_examples[self.date_examples.index(self.variable_formato_fecha_interface.get())]}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config("general", "configuracion_sistema", "formato_hora_interface", new_value=self.date_examples.index(self.variable_formato_fecha_interface.get())),
                    self.cambios_model.add_change(
                        nombre_cambio = "Formato de fecha de interface",valor_anterior=self.date_examples[self.date_format_interface], valor_nuevo=self.date_examples[self.date_examples.index(self.variable_formato_fecha_interface.get())],
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
                } ])

            if self.date_examples.index(self.variable_formato_fecha_boleto.get()) != self.date_format_ticket:
                changes.append([
                    f"Formato de fecha de boleto: {self.date_examples[self.date_format_ticket]} -> {self.date_examples[self.date_examples.index(self.variable_formato_fecha_boleto.get())]}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config("general", "configuracion_sistema", "formato_hora_boleto", new_value=self.date_examples.index(self.variable_formato_fecha_boleto.get())),
                    self.cambios_model.add_change(
                        nombre_cambio = "Formato de fecha de boleto",valor_anterior=self.date_examples[self.date_format_ticket], valor_nuevo=self.date_examples[self.date_examples.index(self.variable_formato_fecha_boleto.get())],
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
                } ])

            if self.date_examples.index(self.variable_formato_fecha_reloj.get()) != self.date_format_clock:
                changes.append([
                    f"Formato de fecha de reloj de expedidor: {self.date_examples[self.date_format_clock]} -> {self.date_examples[self.date_examples.index(self.variable_formato_fecha_reloj.get())]}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config("general", "configuracion_sistema", "formato_hora_reloj_expedidor_boleto", new_value=self.date_examples.index(self.variable_formato_fecha_reloj.get())),
                    self.cambios_model.add_change(
                        nombre_cambio = "Formato de fecha de reloj de expedidor",valor_anterior=self.date_examples[self.date_format_clock], valor_nuevo=self.date_examples[self.date_examples.index(self.variable_formato_fecha_reloj.get())],
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
                } ])

            if self.variable_fuente_sistema.get() != self.fuente_sistema:
                changes.append([
                    f"Fuente del sistema: {self.fuente_sistema} -> {self.variable_fuente_sistema.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "fuente", new_value=self.variable_fuente_sistema.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Fuente del sistema",valor_anterior=self.fuente_sistema, valor_nuevo=self.variable_fuente_sistema.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_color_botones_sistema.get() != self.button_color:
                changes.append([
                    f"Color de botones de interface: {self.button_color} -> {self.variable_color_botones_sistema.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "color_botones_interface", new_value=self.variable_color_botones_sistema.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Color de botones de interface",valor_anterior=self.button_color, valor_nuevo=self.variable_color_botones_sistema.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_color_letra_botones_sistema.get() != self.button_letters_color:
                changes.append([
                    f"Color de letra de botones de interface: {self.button_letters_color} -> {self.variable_color_letra_botones_sistema.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "color_letra_botones_interface", new_value=self.variable_color_letra_botones_sistema.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Color de letra de botones de interface",valor_anterior=self.button_letters_color, valor_nuevo=self.variable_color_letra_botones_sistema.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_color_boton_cobro.get() != self.button_color_cobro:
                changes.append([
                    f"Color de boton de cobro: {self.button_color_cobro} -> {self.variable_color_boton_cobro.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "color_boton_cobro", new_value=self.variable_color_boton_cobro.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Color de boton de cobro",valor_anterior=self.button_color_cobro, valor_nuevo=self.variable_color_boton_cobro.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_color_letra_boton_cobro.get() != self.button_letters_color_cobro:
                changes.append([
                    f"Color de letra de boton de cobro: {self.button_letters_color_cobro} -> {self.variable_color_letra_boton_cobro.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "color_letra_boton_cobro", new_value=self.variable_color_letra_boton_cobro.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Color de letra de boton de cobro",valor_anterior=self.button_letters_color_cobro, valor_nuevo=self.variable_color_letra_boton_cobro.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_size_text_font.get() != self.size_text_font:
                changes.append([
                    f"Tamaño de fuente de texto general de la interface: {self.size_text_font} -> {self.variable_size_text_font.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "size_text_font", new_value=self.variable_size_text_font.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tamaño de fuente de texto general de la interface",valor_anterior=self.size_text_font, valor_nuevo=self.variable_size_text_font.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_size_text_button_font.get() != self.size_text_font:
                changes.append([
                    f"Tamaño de fuente de texto de botones de la interface: {self.size_text_button_font} -> {self.variable_size_text_button_font.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "size_text_button_font", new_value=self.variable_size_text_button_font.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tamaño de fuente de texto de botones de la interface",valor_anterior=self.size_text_font, valor_nuevo=self.variable_size_text_button_font.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_size_text_font_subtittle_system.get() != self.size_text_font_subtittle_system:
                changes.append([
                    f"Tamaño de fuente de texto de subtitulos de la interface: {self.size_text_font_subtittle_system} -> {self.variable_size_text_font_subtittle_system.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "size_text_font_subtittle_system", new_value=self.variable_size_text_font_subtittle_system.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tamaño de fuente de texto de subtitulos de la interface",valor_anterior=self.size_text_font_subtittle_system, valor_nuevo=self.variable_size_text_font_subtittle_system.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_size_text_font_tittle_system.get() != self.size_text_font_tittle_system:
                changes.append([
                    f"Tamaño de fuente de texto de titulos de la interface: {self.size_text_font_tittle_system} -> {self.variable_size_text_font_tittle_system.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuracion_sistema", "size_text_font_tittle_system", new_value=self.variable_size_text_font_tittle_system.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Tamaño de fuente de texto de titulos de la interface",valor_anterior=self.size_text_font_tittle_system, valor_nuevo=self.variable_size_text_font_tittle_system.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_color_primera_hora.get() != self.color_primera_hora:
                changes.append([
                    f"Color del 1° hora de reloj: {self.color_primera_hora} -> {self.variable_color_primera_hora.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuiracion_reloj", "color_primera_hora", new_value=self.variable_color_primera_hora.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Color del 1° hora de reloj",valor_anterior=self.color_primera_hora, valor_nuevo=self.variable_color_primera_hora.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_color_hora_completa.get() != self.color_hora_completa:
                changes.append([
                    f"Color hora completa de reloj: {self.color_hora_completa} -> {self.variable_color_hora_completa.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuiracion_reloj", "color_hora_completa", new_value=self.variable_color_hora_completa.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Color hora completa de reloj",valor_anterior=self.color_hora_completa, valor_nuevo=self.variable_color_hora_completa.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_color_1_4_hora.get() != self.color_1_fraccion:
                changes.append([
                    f"Color del 1° cuarto de hora de reloj: {self.color_1_fraccion} -> {self.variable_color_1_4_hora.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuiracion_reloj", "color_1_fraccion", new_value=self.variable_color_1_4_hora.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Color del 1° cuarto de hora de reloj",valor_anterior=self.color_1_fraccion, valor_nuevo=self.variable_color_1_4_hora.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_color_2_4_hora.get() != self.color_2_fraccion:
                changes.append([
                    f"Color del 2° cuarto de hora de reloj: {self.color_2_fraccion} -> {self.variable_color_2_4_hora.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuiracion_reloj", "color_2_fraccion", new_value=self.variable_color_2_4_hora.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Color del 2° cuarto de hora de reloj",valor_anterior=self.color_2_fraccion, valor_nuevo=self.variable_color_2_4_hora.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_color_3_4_hora.get() != self.color_3_fraccion:
                changes.append([
                    f"Color del 3° cuarto de hora de reloj: {self.color_3_fraccion} -> {self.variable_color_3_4_hora.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuiracion_reloj", "color_3_fraccion", new_value=self.variable_color_3_4_hora.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Color del 3° cuarto de hora de reloj",valor_anterior=self.color_3_fraccion, valor_nuevo=self.variable_color_3_4_hora.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if self.variable_color_alerta.get() != self.color_alerta:
                changes.append([
                    f"Color de alerta de reloj: {self.color_alerta} -> {self.variable_color_alerta.get()}",
                    lambda tipo_cambio = tipo_cambio:{self.instance_config.set_config(
                        "general", "configuiracion_reloj", "color_alerta", new_value=self.variable_color_alerta.get()),
                    self.cambios_model.add_change(
                        nombre_cambio = "Color de alerta de reloj",valor_anterior=self.color_alerta, valor_nuevo=self.variable_color_alerta.get(),
                        tipo_cambio = tipo_cambio, nombre_usuario= nombre_usuario_activo)
            } ])

            if len(changes) == 0:
                mb.showerror("Alerta", "Sin cambios para guardar")
                return

            if ask_security_question(self.configuracion) != True:
                return

            for _, method_save_change in changes:
                method_save_change()
            
            list_changes = [tittle_change for tittle_change, _ in changes]
            state = self.printer_controller.print_changes("Cambios de configuracion\nInterface", list_changes)

            if state != None:
                mb.showerror("Error", state)

            self.exit_system("Configuracion de interface")

        except Exception as e:
            mb.showerror("Error", e)
            return

    def clean_data_form_interface(self):
        self.variable_formato_fecha_interface.set(
            self.date_examples[self.date_format_interface])
        self.variable_formato_fecha_boleto.set(
            self.date_examples[self.date_format_ticket])
        self.variable_formato_fecha_reloj.set(
            self.date_examples[self.date_format_clock])

        self.variable_fuente_sistema.set(value=self.fuente_sistema)

        self.variable_color_botones_sistema.set(self.button_color)
        self.instance_tools.change_color(variable=self.variable_color_botones_sistema,
                                         label_color=self.label_color_botones_sistema, label_name_color=self.label_name_color_botones_sistema, color=self.button_color)

        self.variable_color_letra_botones_sistema.set(
            self.button_letters_color)
        self.instance_tools.change_color(
            variable=self.variable_color_letra_botones_sistema, label_color=self.label_color_button_color, label_name_color=self.label_name_color_button_color, color=self.button_letters_color)

        self.variable_color_boton_cobro.set(self.button_color_cobro)
        self.instance_tools.change_color(
            variable=self.variable_color_boton_cobro, label_color=self.label_color_boton_cobro, label_name_color=self.label_name_color_boton_cobro, color=self.button_color_cobro)

        self.variable_color_letra_boton_cobro.set(
            self.button_letters_color_cobro)
        self.instance_tools.change_color(
            variable=self.variable_color_letra_boton_cobro, label_color=self.label_color_letra_boton_cobro, label_name_color=self.label_name_color_letra_boton_cobro, color=self.button_letters_color_cobro)

        self.variable_size_text_font.set(self.size_text_font)
        self.variable_size_text_font_tittle_system.set(
            self.size_text_font_tittle_system)
        self.variable_size_text_font_subtittle_system.set(
            self.size_text_font_subtittle_system)
        self.variable_size_text_button_font.set(self.size_text_button_font)

        if self.system_to_load == 0:
            self.variable_color_primera_hora.set(self.color_primera_hora)
            self.instance_tools.change_color(variable=self.variable_color_primera_hora, label_color=self.label_color_primera_hora,
                                             label_name_color=self.label_name_color_primera_hora, color=self.color_primera_hora)

            self.variable_color_1_4_hora.set(self.color_1_fraccion)
            self.instance_tools.change_color(variable=self.variable_color_1_4_hora,
                                             label_color=self.label_color_1_4_hora, label_name_color=self.label_name_color_1_4_hora, color=self.color_1_fraccion)

            self.variable_color_2_4_hora.set(self.color_2_fraccion)
            self.instance_tools.change_color(variable=self.variable_color_2_4_hora,
                                             label_color=self.label_color_2_4_hora, label_name_color=self.label_name_color_2_4_hora, color=self.color_2_fraccion)

            self.variable_color_3_4_hora.set(self.color_3_fraccion)
            self.instance_tools.change_color(variable=self.variable_color_3_4_hora,
                                             label_color=self.label_color_3_4_hora, label_name_color=self.label_name_color_3_4_hora, color=self.color_3_fraccion)

            self.variable_color_hora_completa.set(self.color_hora_completa)
            self.instance_tools.change_color(variable=self.variable_color_hora_completa,
                                             label_color=self.label_color_hora_completa, label_name_color=self.label_name_color_hora_completa, color=self.color_hora_completa)

            self.variable_color_alerta.set(self.color_alerta)
            self.instance_tools.change_color(variable=self.variable_color_alerta,
                                             label_color=self.label_color_alerta, label_name_color=self.label_name_color_alerta, color=self.color_alerta)

    def change_tarifa(self, reverse: bool = True) -> None:
        """
        Cambia el tipo de tarifa entre simple y personalizada, actualizando los botones.

        :return: None
        """
        if reverse:
            self.variable_tipo_tarifa_sistema.set(
                not self.variable_tipo_tarifa_sistema.get())

        # Destruye el LabelFrame existente si ya hay alguno
        for widget in self.frame_form_tarifa_general.winfo_children():
            widget.destroy()

        form_to_load = self.load_form_tarifa_simple if self.variable_tipo_tarifa_sistema.get(
        ) else self.load_form_tarifa_avanzada

        form_to_load()

    def draw_info(self) -> None:
        try:
            nombre_usuario_activo = self.DB.nombre_usuario_activo()

            data = [self.entry_nombre_empresa,
                    self.entry_RFC_empresa,
                    self.entry_calle_numero_empresa,
                    self.entry_colonia_empresa,
                    self.entry_CP_empresa,
                    self.entry_alcaldia_empresa,
                    self.entry_entidad_estatal_empresa,
                    self.entry_calle_numero_sucursal,
                    self.entry_colonia_sucursal,
                    self.entry_CP_sucursal,
                    self.entry_alcaldia_sucursal,
                    self.entry_entidad_estatal_sucursal,
                    self.entry_correo_factura,
                    self.entry_numero_factura]

            for elemento in data:
                if elemento.get() == "":
                    elemento.focus()
                    raise SystemError(
                        "Para generar la Imagenes del sistema es necesario ingresar toda la informacion solicitada en el formulario")

            self.instance_tools.validate_email(self.entry_correo_factura.get(
            ), self.entry_correo_factura, "Facturacion de boleto")

            data = [
                self.entry_nombre_empresa.get(),
                f"RFC {self.entry_RFC_empresa.get()}",
                self.entry_calle_numero_empresa.get(),
                f"Col {self.entry_colonia_empresa.get()} C.P {self.entry_CP_empresa.get()}",
                f"Alc. {self.entry_alcaldia_empresa.get()} {self.entry_entidad_estatal_empresa.get()}"]

            # Especificar la fuente y el tamaño
            path = "./Public/Fonts/Calibri Regular.ttf"
            fuente = ImageFont.truetype(path, size=18)

            # Abrir la imagen base
            image = Image.open(self.plantilla)

            # Crear un objeto ImageDraw
            draw = ImageDraw.Draw(image)

            # Especificar el texto que deseas agregar
            y_position = 10
            x_position = 215
            for text in data:
                # Agregar el texto a la imagen
                draw.text((x_position, y_position), text,
                          font=fuente, fill=(0, 0, 0))
                y_position += 16

            y_position += 5

            data = ["Sucursal",
                    self.entry_calle_numero_sucursal.get(),
                    f"Col. {self.entry_colonia_sucursal.get()} C.P {self.entry_CP_sucursal.get()}",
                    f"Alc. {self.entry_alcaldia_sucursal.get()} {self.entry_entidad_estatal_sucursal.get()}"]

            for text in data:
                # Agregar el texto a la imagen
                draw.text((x_position, y_position), text,
                          font=fuente, fill=(0, 0, 0))
                y_position += 16

            y_position += 3
            x_position = 20

            draw.text((x_position, y_position),
                      f"Facturacion: {self.entry_correo_factura.get()}", font=fuente, fill=(0, 0, 0))

            y_position += 16
            x_position = 112
            draw.text((x_position, y_position),
                      f"Tel.{self.entry_numero_factura.get()}", font=fuente, fill=(0, 0, 0))

            # Abrir la imagen que deseas agregar
            imagen_a_agregar = Image.open(self.logo)

            # Agregar la imagen a la imagen base
            image.paste(imagen_a_agregar, (5, 20))

            # Guardar la imagen con el texto y la imagen agregados
            image.save(self.logo_empresa)

            is_changed = self.instance_tools.load_image(
                label_image=self.label_logo_datos, path_image=self.logo_empresa, scale_image=self.scale_image)

            if is_changed:
                self.cambios_model.add_change(
                    nombre_cambio = "Imagen de ticket con datos (crea imagen)",valor_anterior="N/A", valor_nuevo="N/A",
                    tipo_cambio = "Configuracion de imagenes del sistema", nombre_usuario= nombre_usuario_activo)

                state = self.printer_controller.print_changes("Cambios de configuracion\nImagenes del sistema", {"Imagen de ticket con datos (crea imagen)"})

            self.entry_nombre_empresa.focus()

            self.entry_nombre_empresa.delete(0, END)
            self.entry_RFC_empresa.delete(0, END)
            self.entry_calle_numero_empresa.delete(0, END)
            self.entry_colonia_empresa.delete(0, END)
            self.entry_CP_empresa.delete(0, END)
            self.entry_alcaldia_empresa.delete(0, END)
            self.entry_entidad_estatal_empresa.delete(0, END)
            self.entry_calle_numero_sucursal.delete(0, END)
            self.entry_colonia_sucursal.delete(0, END)
            self.entry_CP_sucursal.delete(0, END)
            self.entry_alcaldia_sucursal.delete(0, END)
            self.entry_entidad_estatal_sucursal.delete(0, END)
            self.entry_correo_factura.delete(0, END)
            self.entry_numero_factura.delete(0, END)

            if is_changed and state != None:
                mb.showwarning("Alerta", state)

        except Exception as e:
            mb.showerror("Error", e)
            return

    def backup_image_system(self):
        # Abrir la imagen base
        image = Image.open(self.logo_empresa)

        path_image = filedialog.asksaveasfilename(
            title="Seleccionar ruta para guardar Imagenes del sistema",
            initialfile=f'ImageData_{self.nombre_estacionamiento.replace(" ", "_")}',
            defaultextension="jpg",
            filetypes=[("Imagenes", "*.jpg;"), ("Todos los archivos", "*.*")]
        )

        if path_image == "":
            return

        # Guardar la imagen en blanco
        image.save(path_image)

        mb.showwarning(
            "Alerta", f"La imagen con datos del sistema fue guardada en la ubicacion indicada")

    def load_form_tarifa(self) -> None:
        # Destruye el LabelFrame existente si ya hay alguno
        for widget in self.labelframe_form_tarifas.winfo_children():
            widget.destroy()

        if self.variable_is_sensilla.get():
            self.load_form_tarifa_sensilla()
            self.load_botones_promo()

        elif self.variable_is_personalizada.get():
            self.load_form_tarifa_personalizada()
            self.load_botones_promo()

    def load_form_tarifa_sensilla(self):
        labelframe_form_tarifas = Frame(self.labelframe_form_tarifas)
        labelframe_form_tarifas.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_form_tarifas)
        labelframe.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        label = Label(labelframe, text="Se cobra 1/4 de Hora apartir de",
                      font=self.font_text_interface, anchor="center")
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)

        combobox_inicio_cobro_cuartos_hora = ttk.Combobox(
            labelframe, textvariable=self.variable_inicio_cobro_cuartos_hora_promo_sensilla, width=3, justify=CENTER, state="readonly", values=[1, 2, 3, 4, 5, 6, 7, 8, 9,
                                                                                                                                                10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], font=self.font_text_interface)
        combobox_inicio_cobro_cuartos_hora.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        label = Label(labelframe, text="Hora",
                      font=self.font_text_interface, anchor="center")
        label.grid(
            column=2, row=1, padx=3, pady=3, sticky=NW)

        frame_importe_hora = Frame(labelframe_form_tarifas)
        frame_importe_hora.grid(
            column=0, row=2, padx=3, pady=3, sticky=NW)

        label = Label(frame_importe_hora,
                      text="Importe de 1/4 hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            frame_importe_hora, width=5, textvariable=self.variable_importe_primer_cuarto_hora_promo_sensilla, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=0, padx=3, pady=3, sticky=NW)

        label = Label(frame_importe_hora,
                      text="Importe de 2/4 hora", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=3, pady=3, sticky=NW)
        entry_importe_cuarto_hora_promo_sensilla = Entry(
            frame_importe_hora, width=5, textvariable=self.variable_importe_segundo_cuarto_hora_promo_sensilla, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora_promo_sensilla.grid(
            column=1, row=1, padx=3, pady=3, sticky=NW)

        label = Label(frame_importe_hora,
                      text="Importe de 3/4 hora", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=3, pady=3, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            frame_importe_hora, width=5, textvariable=self.variable_importe_tercer_cuarto_hora_promo_sensilla, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=3, pady=3, sticky=NW)

        label = Label(frame_importe_hora,
                      text="Importe de hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=3, pady=3, sticky=NW)
        entry_importe_hora = Entry(
            frame_importe_hora, width=5, textvariable=self.variable_importe_hora_promo_sensilla, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=3, padx=3, pady=3, sticky=NW)

    def load_botones_promo(self):
        frame = Frame(self.labelframe_form_tarifas)
        frame.grid(
            column=0, row=1, padx=0, pady=0)

        self.boton_guardar_tarifa = Button(
            frame, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        self.boton_guardar_tarifa.grid(
            column=0, row=3, padx=3, pady=3)

        if self.is_new_promo:
            self.boton_guardar_tarifa.configure(
                text="Guardar tarifa", command=self.add_tarifa)
        else:
            self.boton_guardar_tarifa.configure(
                text="Actualizar tarifa", command=lambda: self.add_tarifa(True))

            text = "Deshabilitar tarifa" if self.is_active_promo else "Habilitar tarifa"

            self.boton_desactivar_tarifa = Button(
                frame, text=text, height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface, command=self.update_status_promo)
            self.boton_desactivar_tarifa.grid(
                column=1, row=3, padx=3, pady=3)

        self.boton_cancelar = Button(
            frame, text="Cancelar", height=1, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface, command=self.clear_frame_tarifa)
        self.boton_cancelar.grid(
            column=2, row=3, padx=3, pady=3)

    def load_form_tarifa_personalizada(self):
        labelframe_personalizada = Frame(self.labelframe_form_tarifas)
        labelframe_personalizada.grid(
            column=0, row=0, padx=3, pady=3, sticky=NW)

        labelframe_0 = LabelFrame(labelframe_personalizada)
        labelframe_0.grid(
            column=0, row=0, padx=0, pady=0)

        label = Label(labelframe_0,
                      text="0 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_0)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_0_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_0_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_0_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora 00:00", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_0_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_1 = LabelFrame(labelframe_personalizada)
        labelframe_1.grid(
            column=1, row=0, padx=0, pady=0)

        label = Label(labelframe_1,
                      text="1 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_1)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_1_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_1_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_1_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_1_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_2 = LabelFrame(labelframe_personalizada)
        labelframe_2.grid(
            column=2, row=0, padx=0, pady=0)

        label = Label(labelframe_2,
                      text="2 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_2)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_2_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_2_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_2_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_2_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_3 = LabelFrame(labelframe_personalizada)
        labelframe_3.grid(
            column=3, row=0, padx=0, pady=0)

        label = Label(labelframe_3,
                      text="3 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_3)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_3_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_3_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_3_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_3_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_4 = LabelFrame(labelframe_personalizada)
        labelframe_4.grid(
            column=4, row=0, padx=0, pady=0)

        label = Label(labelframe_4,
                      text="4 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_4)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_4_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_4_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_4_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_4_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_5 = LabelFrame(labelframe_personalizada)
        labelframe_5.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe_5,
                      text="5 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_5)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_5_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_5_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_5_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_5_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_6 = LabelFrame(labelframe_personalizada)
        labelframe_6.grid(
            column=1, row=1, padx=0, pady=0)

        label = Label(labelframe_6,
                      text="6 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_6)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_6_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_6_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_6_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_6_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_7 = LabelFrame(labelframe_personalizada)
        labelframe_7.grid(
            column=2, row=1, padx=0, pady=0)

        label = Label(labelframe_7,
                      text="7 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_7)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_7_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_7_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_7_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_7_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_8 = LabelFrame(labelframe_personalizada)
        labelframe_8.grid(
            column=3, row=1, padx=0, pady=0)

        label = Label(labelframe_8,
                      text="8 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_8)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_8_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_8_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_8_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_8_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_9 = LabelFrame(labelframe_personalizada)
        labelframe_9.grid(
            column=4, row=1, padx=0, pady=0)

        label = Label(labelframe_9,
                      text="9 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_9)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_9_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_9_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_9_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_9_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_10 = LabelFrame(labelframe_personalizada)
        labelframe_10.grid(
            column=0, row=2, padx=0, pady=0)

        label = Label(labelframe_10,
                      text="10 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_10)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_10_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_10_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_10_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_10_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_11 = LabelFrame(labelframe_personalizada)
        labelframe_11.grid(
            column=1, row=2, padx=0, pady=0)

        label = Label(labelframe_11,
                      text="11 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_11)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_11_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_11_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_11_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_11_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_12 = LabelFrame(labelframe_personalizada)
        labelframe_12.grid(
            column=2, row=2, padx=0, pady=0)

        label = Label(labelframe_12,
                      text="12 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_12)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_12_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_12_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_12_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_12_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_13 = LabelFrame(labelframe_personalizada)
        labelframe_13.grid(
            column=3, row=2, padx=0, pady=0)

        label = Label(labelframe_13,
                      text="13 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_13)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_13_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_13_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_13_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_13_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_14 = LabelFrame(labelframe_personalizada)
        labelframe_14.grid(
            column=4, row=2, padx=0, pady=0)

        label = Label(labelframe_14,
                      text="14 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_14)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_14_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_14_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_14_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_14_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_15 = LabelFrame(labelframe_personalizada)
        labelframe_15.grid(
            column=0, row=3, padx=0, pady=0)

        label = Label(labelframe_15,
                      text="15 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_15)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_15_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_15_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_15_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_15_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_16 = LabelFrame(labelframe_personalizada)
        labelframe_16.grid(
            column=1, row=3, padx=0, pady=0)

        label = Label(labelframe_16,
                      text="16 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_16)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_16_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_16_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_16_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_16_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_17 = LabelFrame(labelframe_personalizada)
        labelframe_17.grid(
            column=2, row=3, padx=0, pady=0)

        label = Label(labelframe_17,
                      text="17 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_17)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_17_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_17_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_17_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_17_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_18 = LabelFrame(labelframe_personalizada)
        labelframe_18.grid(
            column=3, row=3, padx=0, pady=0)

        label = Label(labelframe_18,
                      text="18 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_18)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_18_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_18_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_18_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_18_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_19 = LabelFrame(labelframe_personalizada)
        labelframe_19.grid(
            column=4, row=3, padx=0, pady=0)

        label = Label(labelframe_19,
                      text="19 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_19)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_19_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_19_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_19_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_19_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_20 = LabelFrame(labelframe_personalizada)
        labelframe_20.grid(
            column=0, row=4, padx=0, pady=0)

        label = Label(labelframe_20,
                      text="20 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_20)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_20_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_20_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_20_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_20_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_21 = LabelFrame(labelframe_personalizada)
        labelframe_21.grid(
            column=1, row=4, padx=0, pady=0)

        label = Label(labelframe_21,
                      text="21 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_21)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_21_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_21_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_21_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_21_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_22 = LabelFrame(labelframe_personalizada)
        labelframe_22.grid(
            column=2, row=4, padx=0, pady=0)

        label = Label(labelframe_22,
                      text="22 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_22)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_22_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_22_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_22_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_22_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_23 = LabelFrame(labelframe_personalizada)
        labelframe_23.grid(
            column=3, row=4, padx=0, pady=0)

        label = Label(labelframe_23,
                      text="23 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_23)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_23_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_23_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_23_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_23_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

        labelframe_24 = LabelFrame(labelframe_personalizada)
        labelframe_24.grid(
            column=4, row=4, padx=0, pady=0)

        label = Label(labelframe_24,
                      text="24 Hora", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0)

        labelframe = Frame(labelframe_24)
        labelframe.grid(
            column=0, row=1, padx=0, pady=0)

        label = Label(labelframe,
                      text="Primer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=1, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_24_1, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=1, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Segundo cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=2, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_24_2, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=2, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Tercer cuarto", font=self.font_text_interface)
        label.grid(
            column=0, row=3, padx=0, pady=0, sticky=NW)
        entry_importe_cuarto_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_24_3, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_cuarto_hora.grid(
            column=1, row=3, padx=0, pady=0, sticky=NW)

        label = Label(labelframe,
                      text="Hora completa", font=self.font_text_interface)
        label.grid(
            column=0, row=0, padx=0, pady=0, sticky=NW)
        entry_importe_hora = Entry(
            labelframe, width=4, textvariable=self.variable_tarifa_personalizada_24_hora, justify='center', font=self.font_text_interface, validate='key', validatecommand=(self.configuracion.register(self.instance_tools.validate_entry_number), '%P'))
        entry_importe_hora.grid(
            column=1, row=0, padx=0, pady=0, sticky=NW)

    def load_data_form_tarifa(self) -> None:
        self.clean_data_tarifa()

        name_promo = self.variable_promo_selected.get()

        if name_promo == "Seleccione una opcion" or "":
            mb.showerror("Error", "Seleccione una promocion")
            self.entry_nombre_promocion.focus()
            return

        self.is_new_promo = False

        self.entry_nombre_promocion.configure(state='readonly')

        real_name = self.instance_config.get_real_name_promo(name_promo)
        data_promo = self.instance_config.get_config("promociones", real_name)

        self.name_promocion.set(real_name)
        self.variable_type_qr.set(
            True if data_promo["tipo_lectura"] == "qr" else False)
        self.variable_type_button.set(
            True if data_promo["tipo_lectura"] == "boton" else False)

        self.update_interface_ID()
        if data_promo["tipo_lectura"] == "qr":
            self.id_promocion.set(real_name)
            self.name_promocion.set(name_promo)

        self.is_active_promo = data_promo["estatus"]

        self.variable_is_sensilla.set(
            True if data_promo["tipo_tarifa"] else False)
        self.variable_is_personalizada.set(
            True if data_promo["tipo_tarifa"] == False else False)

        if self.variable_is_sensilla.get():
            self.variable_inicio_cobro_cuartos_hora_promo_sensilla.set(
                data_promo["inicio_cobro_fraccion"])
            self.variable_importe_primer_cuarto_hora_promo_sensilla.set(
                data_promo["tarifa_1_fraccion"])
            self.variable_importe_segundo_cuarto_hora_promo_sensilla.set(
                data_promo["tarifa_2_fraccion"])
            self.variable_importe_tercer_cuarto_hora_promo_sensilla.set(
                data_promo["tarifa_3_fraccion"])
            self.variable_importe_hora_promo_sensilla.set(
                data_promo["tarifa_hora"])

        if self.variable_is_personalizada.get():
            self.variable_tarifa_personalizada_0_hora.set(
                data_promo["0"]["hora"])
            self.variable_tarifa_personalizada_0_1.set(data_promo["0"]["1"])
            self.variable_tarifa_personalizada_0_2.set(data_promo["0"]["2"])
            self.variable_tarifa_personalizada_0_3.set(data_promo["0"]["3"])

            self.variable_tarifa_personalizada_1_hora.set(
                data_promo["1"]["hora"])
            self.variable_tarifa_personalizada_1_1.set(data_promo["1"]["1"])
            self.variable_tarifa_personalizada_1_2.set(data_promo["1"]["2"])
            self.variable_tarifa_personalizada_1_3.set(data_promo["1"]["3"])

            self.variable_tarifa_personalizada_2_hora.set(
                data_promo["2"]["hora"])
            self.variable_tarifa_personalizada_2_1.set(data_promo["2"]["1"])
            self.variable_tarifa_personalizada_2_2.set(data_promo["2"]["2"])
            self.variable_tarifa_personalizada_2_3.set(data_promo["2"]["3"])

            self.variable_tarifa_personalizada_3_hora.set(
                data_promo["3"]["hora"])
            self.variable_tarifa_personalizada_3_1.set(data_promo["3"]["1"])
            self.variable_tarifa_personalizada_3_2.set(data_promo["3"]["2"])
            self.variable_tarifa_personalizada_3_3.set(data_promo["3"]["3"])

            self.variable_tarifa_personalizada_4_hora.set(
                data_promo["4"]["hora"])
            self.variable_tarifa_personalizada_4_1.set(data_promo["4"]["1"])
            self.variable_tarifa_personalizada_4_2.set(data_promo["4"]["2"])
            self.variable_tarifa_personalizada_4_3.set(data_promo["4"]["3"])

            self.variable_tarifa_personalizada_5_hora.set(
                data_promo["5"]["hora"])
            self.variable_tarifa_personalizada_5_1.set(data_promo["5"]["1"])
            self.variable_tarifa_personalizada_5_2.set(data_promo["5"]["2"])
            self.variable_tarifa_personalizada_5_3.set(data_promo["5"]["3"])

            self.variable_tarifa_personalizada_6_hora.set(
                data_promo["6"]["hora"])
            self.variable_tarifa_personalizada_6_1.set(data_promo["6"]["1"])
            self.variable_tarifa_personalizada_6_2.set(data_promo["6"]["2"])
            self.variable_tarifa_personalizada_6_3.set(data_promo["6"]["3"])

            self.variable_tarifa_personalizada_7_hora.set(
                data_promo["7"]["hora"])
            self.variable_tarifa_personalizada_7_1.set(data_promo["7"]["1"])
            self.variable_tarifa_personalizada_7_2.set(data_promo["7"]["2"])
            self.variable_tarifa_personalizada_7_3.set(data_promo["7"]["3"])

            self.variable_tarifa_personalizada_8_hora.set(
                data_promo["8"]["hora"])
            self.variable_tarifa_personalizada_8_1.set(data_promo["8"]["1"])
            self.variable_tarifa_personalizada_8_2.set(data_promo["8"]["2"])
            self.variable_tarifa_personalizada_8_3.set(data_promo["8"]["3"])

            self.variable_tarifa_personalizada_9_hora.set(
                data_promo["9"]["hora"])
            self.variable_tarifa_personalizada_9_1.set(data_promo["9"]["1"])
            self.variable_tarifa_personalizada_9_2.set(data_promo["9"]["2"])
            self.variable_tarifa_personalizada_9_3.set(data_promo["9"]["3"])

            self.variable_tarifa_personalizada_10_hora.set(
                data_promo["10"]["hora"])
            self.variable_tarifa_personalizada_10_1.set(data_promo["10"]["1"])
            self.variable_tarifa_personalizada_10_2.set(data_promo["10"]["2"])
            self.variable_tarifa_personalizada_10_3.set(data_promo["10"]["3"])

            self.variable_tarifa_personalizada_11_hora.set(
                data_promo["11"]["hora"])
            self.variable_tarifa_personalizada_11_1.set(data_promo["11"]["1"])
            self.variable_tarifa_personalizada_11_2.set(data_promo["11"]["2"])
            self.variable_tarifa_personalizada_11_3.set(data_promo["11"]["3"])

            self.variable_tarifa_personalizada_12_hora.set(
                data_promo["12"]["hora"])
            self.variable_tarifa_personalizada_12_1.set(data_promo["12"]["1"])
            self.variable_tarifa_personalizada_12_2.set(data_promo["12"]["2"])
            self.variable_tarifa_personalizada_12_3.set(data_promo["12"]["3"])

            self.variable_tarifa_personalizada_13_hora.set(
                data_promo["13"]["hora"])
            self.variable_tarifa_personalizada_13_1.set(data_promo["13"]["1"])
            self.variable_tarifa_personalizada_13_2.set(data_promo["13"]["2"])
            self.variable_tarifa_personalizada_13_3.set(data_promo["13"]["3"])

            self.variable_tarifa_personalizada_14_hora.set(
                data_promo["14"]["hora"])
            self.variable_tarifa_personalizada_14_1.set(data_promo["14"]["1"])
            self.variable_tarifa_personalizada_14_2.set(data_promo["14"]["2"])
            self.variable_tarifa_personalizada_14_3.set(data_promo["14"]["3"])

            self.variable_tarifa_personalizada_15_hora.set(
                data_promo["15"]["hora"])
            self.variable_tarifa_personalizada_15_1.set(data_promo["15"]["1"])
            self.variable_tarifa_personalizada_15_2.set(data_promo["15"]["2"])
            self.variable_tarifa_personalizada_15_3.set(data_promo["15"]["3"])

            self.variable_tarifa_personalizada_16_hora.set(
                data_promo["16"]["hora"])
            self.variable_tarifa_personalizada_16_1.set(data_promo["16"]["1"])
            self.variable_tarifa_personalizada_16_2.set(data_promo["16"]["2"])
            self.variable_tarifa_personalizada_16_3.set(data_promo["16"]["3"])

            self.variable_tarifa_personalizada_17_hora.set(
                data_promo["17"]["hora"])
            self.variable_tarifa_personalizada_17_1.set(data_promo["17"]["1"])
            self.variable_tarifa_personalizada_17_2.set(data_promo["17"]["2"])
            self.variable_tarifa_personalizada_17_3.set(data_promo["17"]["3"])

            self.variable_tarifa_personalizada_18_hora.set(
                data_promo["18"]["hora"])
            self.variable_tarifa_personalizada_18_1.set(data_promo["18"]["1"])
            self.variable_tarifa_personalizada_18_2.set(data_promo["18"]["2"])
            self.variable_tarifa_personalizada_18_3.set(data_promo["18"]["3"])

            self.variable_tarifa_personalizada_19_hora.set(
                data_promo["19"]["hora"])
            self.variable_tarifa_personalizada_19_1.set(data_promo["19"]["1"])
            self.variable_tarifa_personalizada_19_2.set(data_promo["19"]["2"])
            self.variable_tarifa_personalizada_19_3.set(data_promo["19"]["3"])

            self.variable_tarifa_personalizada_20_hora.set(
                data_promo["20"]["hora"])
            self.variable_tarifa_personalizada_20_1.set(data_promo["20"]["1"])
            self.variable_tarifa_personalizada_20_2.set(data_promo["20"]["2"])
            self.variable_tarifa_personalizada_20_3.set(data_promo["20"]["3"])

            self.variable_tarifa_personalizada_21_hora.set(
                data_promo["21"]["hora"])
            self.variable_tarifa_personalizada_21_1.set(data_promo["21"]["1"])
            self.variable_tarifa_personalizada_21_2.set(data_promo["21"]["2"])
            self.variable_tarifa_personalizada_21_3.set(data_promo["21"]["3"])

            self.variable_tarifa_personalizada_22_hora.set(
                data_promo["22"]["hora"])
            self.variable_tarifa_personalizada_22_1.set(data_promo["22"]["1"])
            self.variable_tarifa_personalizada_22_2.set(data_promo["22"]["2"])
            self.variable_tarifa_personalizada_22_3.set(data_promo["22"]["3"])

            self.variable_tarifa_personalizada_23_hora.set(
                data_promo["23"]["hora"])
            self.variable_tarifa_personalizada_23_1.set(data_promo["23"]["1"])
            self.variable_tarifa_personalizada_23_2.set(data_promo["23"]["2"])
            self.variable_tarifa_personalizada_23_3.set(data_promo["23"]["3"])

            self.variable_tarifa_personalizada_24_hora.set(
                data_promo["24"]["hora"])
            self.variable_tarifa_personalizada_24_1.set(data_promo["24"]["1"])
            self.variable_tarifa_personalizada_24_2.set(data_promo["24"]["2"])
            self.variable_tarifa_personalizada_24_3.set(data_promo["24"]["3"])

        self.load_form_tarifa()
        data_promo = None

    def add_tarifa(self, update_promo: bool = False) -> None:
        try:
            name_promo = self.name_promocion.get()
            id_promo = self.id_promocion.get()
            if update_promo == False:

                if name_promo in self.promociones:
                    raise AlreadyExist(
                        "Ya existe una promocion con ese nombre")

                if not self.variable_is_sensilla.get() and not self.variable_is_personalizada.get():
                    raise WithoutParameter("Tipo de promocion")

                if not self.variable_type_qr.get() and not self.variable_type_button.get():
                    raise WithoutParameter("Tipo de lectura de la promocion")

            if not name_promo:
                raise WithoutParameter("Nombre de la promocion")

            if len(name_promo) != 8:
                raise SystemError(
                    "El nombre de la promocion debe de ser de 8 caracteres")

            if self.variable_type_qr.get() and len(id_promo) != 8:
                raise SystemError(
                    "El identificador de la promocion debe de ser de 8 caracteres")

            if not id_promo and self.variable_type_qr.get():
                self.entry_id_promocion.focus()
                raise WithoutParameter("ID de la promocion")

            tipo_lectura = "qr" if self.variable_type_qr.get() else "boton"
            name_save = id_promo if self.variable_type_qr.get() else name_promo

            if self.variable_is_sensilla.get():
                data_promo = [self.variable_importe_primer_cuarto_hora_promo_sensilla.get(), self.variable_importe_segundo_cuarto_hora_promo_sensilla.get(
                ), self.variable_importe_tercer_cuarto_hora_promo_sensilla.get(), self.variable_importe_hora_promo_sensilla.get()]

                if all(elemento == 0 for elemento in data_promo):
                    if mb.askyesno(
                            "Alerta", f"Ha ingresado una promocion de cortecia, es decir que todos sus valores son 0 y no se cobrará nada al aplicarse ¿esta seguro de querer {'actualizar' if update_promo else 'registrar'} esta promocion?") == False:
                        return

                data_promo = {
                    "tipo_lectura": tipo_lectura,
                    "real_name": name_promo,
                    "estatus": True,
                    "tipo_tarifa": True,
                    "inicio_cobro_fraccion": self.variable_inicio_cobro_cuartos_hora_promo_sensilla.get(),
                    "tarifa_1_fraccion": self.variable_importe_primer_cuarto_hora_promo_sensilla.get(),
                    "tarifa_2_fraccion": self.variable_importe_segundo_cuarto_hora_promo_sensilla.get(),
                    "tarifa_3_fraccion": self.variable_importe_tercer_cuarto_hora_promo_sensilla.get(),
                    "tarifa_hora": self.variable_importe_hora_promo_sensilla.get()
                }

            if self.variable_is_personalizada.get():
                data_promo = [
                    self.variable_tarifa_personalizada_0_hora.get(), self.variable_tarifa_personalizada_0_1.get(
                    ), self.variable_tarifa_personalizada_0_2.get(), self.variable_tarifa_personalizada_0_3.get(),
                    self.variable_tarifa_personalizada_1_hora.get(), self.variable_tarifa_personalizada_1_1.get(
                    ), self.variable_tarifa_personalizada_1_2.get(), self.variable_tarifa_personalizada_1_3.get(),
                    self.variable_tarifa_personalizada_2_hora.get(), self.variable_tarifa_personalizada_2_1.get(
                    ), self.variable_tarifa_personalizada_2_2.get(), self.variable_tarifa_personalizada_2_3.get(),
                    self.variable_tarifa_personalizada_3_hora.get(), self.variable_tarifa_personalizada_3_1.get(
                    ), self.variable_tarifa_personalizada_3_2.get(), self.variable_tarifa_personalizada_3_3.get(),
                    self.variable_tarifa_personalizada_4_hora.get(), self.variable_tarifa_personalizada_4_1.get(
                    ), self.variable_tarifa_personalizada_4_2.get(), self.variable_tarifa_personalizada_4_3.get(),
                    self.variable_tarifa_personalizada_5_hora.get(), self.variable_tarifa_personalizada_5_1.get(
                    ), self.variable_tarifa_personalizada_5_2.get(), self.variable_tarifa_personalizada_5_3.get(),
                    self.variable_tarifa_personalizada_6_hora.get(), self.variable_tarifa_personalizada_6_1.get(
                    ), self.variable_tarifa_personalizada_6_2.get(), self.variable_tarifa_personalizada_6_3.get(),
                    self.variable_tarifa_personalizada_7_hora.get(), self.variable_tarifa_personalizada_7_1.get(
                    ), self.variable_tarifa_personalizada_7_2.get(), self.variable_tarifa_personalizada_7_3.get(),
                    self.variable_tarifa_personalizada_8_hora.get(), self.variable_tarifa_personalizada_8_1.get(
                    ), self.variable_tarifa_personalizada_8_2.get(), self.variable_tarifa_personalizada_8_3.get(),
                    self.variable_tarifa_personalizada_9_hora.get(), self.variable_tarifa_personalizada_9_1.get(
                    ), self.variable_tarifa_personalizada_9_2.get(), self.variable_tarifa_personalizada_9_3.get(),
                    self.variable_tarifa_personalizada_10_hora.get(), self.variable_tarifa_personalizada_10_1.get(
                    ), self.variable_tarifa_personalizada_10_2.get(), self.variable_tarifa_personalizada_10_3.get(),
                    self.variable_tarifa_personalizada_11_hora.get(), self.variable_tarifa_personalizada_11_1.get(
                    ), self.variable_tarifa_personalizada_11_2.get(), self.variable_tarifa_personalizada_11_3.get(),
                    self.variable_tarifa_personalizada_12_hora.get(), self.variable_tarifa_personalizada_12_1.get(
                    ), self.variable_tarifa_personalizada_12_2.get(), self.variable_tarifa_personalizada_12_3.get(),
                    self.variable_tarifa_personalizada_13_hora.get(), self.variable_tarifa_personalizada_13_1.get(
                    ), self.variable_tarifa_personalizada_13_2.get(), self.variable_tarifa_personalizada_13_3.get(),
                    self.variable_tarifa_personalizada_14_hora.get(), self.variable_tarifa_personalizada_14_1.get(
                    ), self.variable_tarifa_personalizada_14_2.get(), self.variable_tarifa_personalizada_14_3.get(),
                    self.variable_tarifa_personalizada_15_hora.get(), self.variable_tarifa_personalizada_15_1.get(
                    ), self.variable_tarifa_personalizada_15_2.get(), self.variable_tarifa_personalizada_15_3.get(),
                    self.variable_tarifa_personalizada_16_hora.get(), self.variable_tarifa_personalizada_16_1.get(
                    ), self.variable_tarifa_personalizada_16_2.get(), self.variable_tarifa_personalizada_16_3.get(),
                    self.variable_tarifa_personalizada_17_hora.get(), self.variable_tarifa_personalizada_17_1.get(
                    ), self.variable_tarifa_personalizada_17_2.get(), self.variable_tarifa_personalizada_17_3.get(),
                    self.variable_tarifa_personalizada_18_hora.get(), self.variable_tarifa_personalizada_18_1.get(
                    ), self.variable_tarifa_personalizada_18_2.get(), self.variable_tarifa_personalizada_18_3.get(),
                    self.variable_tarifa_personalizada_19_hora.get(), self.variable_tarifa_personalizada_19_1.get(
                    ), self.variable_tarifa_personalizada_19_2.get(), self.variable_tarifa_personalizada_19_3.get(),
                    self.variable_tarifa_personalizada_20_hora.get(), self.variable_tarifa_personalizada_20_1.get(
                    ), self.variable_tarifa_personalizada_20_2.get(), self.variable_tarifa_personalizada_20_3.get(),
                    self.variable_tarifa_personalizada_21_hora.get(), self.variable_tarifa_personalizada_21_1.get(
                    ), self.variable_tarifa_personalizada_21_2.get(), self.variable_tarifa_personalizada_21_3.get(),
                    self.variable_tarifa_personalizada_22_hora.get(), self.variable_tarifa_personalizada_22_1.get(
                    ), self.variable_tarifa_personalizada_22_2.get(), self.variable_tarifa_personalizada_22_3.get(),
                    self.variable_tarifa_personalizada_23_hora.get(), self.variable_tarifa_personalizada_23_1.get(
                    ), self.variable_tarifa_personalizada_23_2.get(), self.variable_tarifa_personalizada_23_3.get(),
                    self.variable_tarifa_personalizada_24_hora.get(), self.variable_tarifa_personalizada_24_1.get(), self.variable_tarifa_personalizada_24_2.get(), self.variable_tarifa_personalizada_24_3.get()]

                if all(elemento == 0 for elemento in data_promo):
                    raise ValidateDataError(
                        "De los cuartos de hora asi como del importe de la hora no puede ser igual a 0 para una tarifa personalizada, si desea agregar una cortesia, vaya al apartado de tarifas y agrege una nueva tarifa sensilla con los valores a 0")

                data_promo = {
                    "tipo_lectura": tipo_lectura,
                    "real_name": name_promo,
                    "estatus": True,
                    "tipo_tarifa": False,
                    "0": {
                        "hora": self.variable_tarifa_personalizada_0_hora.get(),
                        "1": self.variable_tarifa_personalizada_0_1.get(),
                        "2": self.variable_tarifa_personalizada_0_2.get(),
                        "3": self.variable_tarifa_personalizada_0_3.get()
                    },
                    "1": {
                        "hora": self.variable_tarifa_personalizada_1_hora.get(),
                        "1": self.variable_tarifa_personalizada_1_1.get(),
                        "2": self.variable_tarifa_personalizada_1_2.get(),
                        "3": self.variable_tarifa_personalizada_1_3.get()
                    },
                    "2": {
                        "hora": self.variable_tarifa_personalizada_2_hora.get(),
                        "1": self.variable_tarifa_personalizada_2_1.get(),
                        "2": self.variable_tarifa_personalizada_2_2.get(),
                        "3": self.variable_tarifa_personalizada_2_3.get()
                    },
                    "3": {
                        "hora": self.variable_tarifa_personalizada_3_hora.get(),
                        "1": self.variable_tarifa_personalizada_3_1.get(),
                        "2": self.variable_tarifa_personalizada_3_2.get(),
                        "3": self.variable_tarifa_personalizada_3_3.get()
                    },
                    "4": {
                        "hora": self.variable_tarifa_personalizada_4_hora.get(),
                        "1": self.variable_tarifa_personalizada_4_1.get(),
                        "2": self.variable_tarifa_personalizada_4_2.get(),
                        "3": self.variable_tarifa_personalizada_4_3.get()
                    },
                    "5": {
                        "hora": self.variable_tarifa_personalizada_5_hora.get(),
                        "1": self.variable_tarifa_personalizada_5_1.get(),
                        "2": self.variable_tarifa_personalizada_5_2.get(),
                        "3": self.variable_tarifa_personalizada_5_3.get()
                    },
                    "6": {
                        "hora": self.variable_tarifa_personalizada_6_hora.get(),
                        "1": self.variable_tarifa_personalizada_6_1.get(),
                        "2": self.variable_tarifa_personalizada_6_2.get(),
                        "3": self.variable_tarifa_personalizada_6_3.get()
                    },
                    "7": {
                        "hora": self.variable_tarifa_personalizada_7_hora.get(),
                        "1": self.variable_tarifa_personalizada_7_1.get(),
                        "2": self.variable_tarifa_personalizada_7_2.get(),
                        "3": self.variable_tarifa_personalizada_7_3.get()
                    },
                    "8": {
                        "hora": self.variable_tarifa_personalizada_8_hora.get(),
                        "1": self.variable_tarifa_personalizada_8_1.get(),
                        "2": self.variable_tarifa_personalizada_8_2.get(),
                        "3": self.variable_tarifa_personalizada_8_3.get()
                    },
                    "9": {
                        "hora": self.variable_tarifa_personalizada_9_hora.get(),
                        "1": self.variable_tarifa_personalizada_9_1.get(),
                        "2": self.variable_tarifa_personalizada_9_2.get(),
                        "3": self.variable_tarifa_personalizada_9_3.get()
                    },
                    "10": {
                        "hora": self.variable_tarifa_personalizada_10_hora.get(),
                        "1": self.variable_tarifa_personalizada_10_1.get(),
                        "2": self.variable_tarifa_personalizada_10_2.get(),
                        "3": self.variable_tarifa_personalizada_10_3.get()
                    },
                    "11": {
                        "hora": self.variable_tarifa_personalizada_11_hora.get(),
                        "1": self.variable_tarifa_personalizada_11_1.get(),
                        "2": self.variable_tarifa_personalizada_11_2.get(),
                        "3": self.variable_tarifa_personalizada_11_3.get()
                    },
                    "12": {
                        "hora": self.variable_tarifa_personalizada_12_hora.get(),
                        "1": self.variable_tarifa_personalizada_12_1.get(),
                        "2": self.variable_tarifa_personalizada_12_2.get(),
                        "3": self.variable_tarifa_personalizada_12_3.get()
                    },
                    "13": {
                        "hora": self.variable_tarifa_personalizada_13_hora.get(),
                        "1": self.variable_tarifa_personalizada_13_1.get(),
                        "2": self.variable_tarifa_personalizada_13_2.get(),
                        "3": self.variable_tarifa_personalizada_13_3.get()
                    },
                    "14": {
                        "hora": self.variable_tarifa_personalizada_14_hora.get(),
                        "1": self.variable_tarifa_personalizada_14_1.get(),
                        "2": self.variable_tarifa_personalizada_14_2.get(),
                        "3": self.variable_tarifa_personalizada_14_3.get()
                    },
                    "15": {
                        "hora": self.variable_tarifa_personalizada_15_hora.get(),
                        "1": self.variable_tarifa_personalizada_15_1.get(),
                        "2": self.variable_tarifa_personalizada_15_2.get(),
                        "3": self.variable_tarifa_personalizada_15_3.get()
                    },
                    "16": {
                        "hora": self.variable_tarifa_personalizada_16_hora.get(),
                        "1": self.variable_tarifa_personalizada_16_1.get(),
                        "2": self.variable_tarifa_personalizada_16_2.get(),
                        "3": self.variable_tarifa_personalizada_16_3.get()
                    },
                    "17": {
                        "hora": self.variable_tarifa_personalizada_17_hora.get(),
                        "1": self.variable_tarifa_personalizada_17_1.get(),
                        "2": self.variable_tarifa_personalizada_17_2.get(),
                        "3": self.variable_tarifa_personalizada_17_3.get()
                    },
                    "18": {
                        "hora": self.variable_tarifa_personalizada_18_hora.get(),
                        "1": self.variable_tarifa_personalizada_18_1.get(),
                        "2": self.variable_tarifa_personalizada_18_2.get(),
                        "3": self.variable_tarifa_personalizada_18_3.get()
                    },
                    "19": {
                        "hora": self.variable_tarifa_personalizada_19_hora.get(),
                        "1": self.variable_tarifa_personalizada_19_1.get(),
                        "2": self.variable_tarifa_personalizada_19_2.get(),
                        "3": self.variable_tarifa_personalizada_19_3.get()
                    },
                    "20": {
                        "hora": self.variable_tarifa_personalizada_20_hora.get(),
                        "1": self.variable_tarifa_personalizada_20_1.get(),
                        "2": self.variable_tarifa_personalizada_20_2.get(),
                        "3": self.variable_tarifa_personalizada_20_3.get()
                    },
                    "21": {
                        "hora": self.variable_tarifa_personalizada_21_hora.get(),
                        "1": self.variable_tarifa_personalizada_21_1.get(),
                        "2": self.variable_tarifa_personalizada_21_2.get(),
                        "3": self.variable_tarifa_personalizada_21_3.get()
                    },
                    "22": {
                        "hora": self.variable_tarifa_personalizada_22_hora.get(),
                        "1": self.variable_tarifa_personalizada_22_1.get(),
                        "2": self.variable_tarifa_personalizada_22_2.get(),
                        "3": self.variable_tarifa_personalizada_22_3.get()
                    },
                    "23": {
                        "hora": self.variable_tarifa_personalizada_23_hora.get(),
                        "1": self.variable_tarifa_personalizada_23_1.get(),
                        "2": self.variable_tarifa_personalizada_23_2.get(),
                        "3": self.variable_tarifa_personalizada_23_3.get()
                    },
                    "24": {
                        "hora": self.variable_tarifa_personalizada_24_hora.get(),
                        "1": self.variable_tarifa_personalizada_24_1.get(),
                        "2": self.variable_tarifa_personalizada_24_2.get(),
                        "3": self.variable_tarifa_personalizada_24_3.get()
                    }
                }

            if update_promo:
                if self.instance_config.type_promo(name_promo) == "qr" and self.variable_type_button.get():
                    name_save = name_promo
                    self.instance_config.del_config("promociones", id_promo)

                elif self.instance_config.type_promo(name_promo) == "boton" and self.variable_type_qr.get():
                    name_save = id_promo
                    self.instance_config.del_config("promociones", name_promo)

            self.instance_config.add_promo(name_save, data_promo)
            mb.showinfo(
                "Exito", f'La tarifa fue {"actualizada" if update_promo else "guardada"} exitosamente')
            
                    
            nombre_usuario_activo = self.DB.nombre_usuario_activo()

            self.cambios_model.add_change(
                nombre_cambio = f'Se {"actualiza" if update_promo else "añade"} la promocion {name_save}',valor_anterior="N/A", valor_nuevo="N/A",
                tipo_cambio = "Configuracion de promociones", nombre_usuario= nombre_usuario_activo)

            state = self.printer_controller.print_changes("Cambios de configuracion\nTarifa general", {f'Se {"actualiza" if update_promo else "añade"} la promocion {name_save}'})

            if state != None:
                mb.showwarning("Alerta", state)

            self.clear_frame_tarifa()

        except Exception as e:
            self.entry_nombre_promocion.focus()
            mb.showerror("Error", e)
        finally:
            self.entry_nombre_promocion.focus()

    def clean_data_tarifa(self) -> None:
        self.variable_inicio_cobro_cuartos_hora_promo_sensilla.set(1)
        self.variable_importe_primer_cuarto_hora_promo_sensilla.set(0)
        self.variable_importe_segundo_cuarto_hora_promo_sensilla.set(0)
        self.variable_importe_tercer_cuarto_hora_promo_sensilla.set(0)
        self.variable_importe_hora_promo_sensilla.set(0)

        self.variable_tarifa_personalizada_0_hora.set(0)
        self.variable_tarifa_personalizada_0_1.set(0)
        self.variable_tarifa_personalizada_0_2.set(0)
        self.variable_tarifa_personalizada_0_3.set(0)

        self.variable_tarifa_personalizada_1_hora.set(0)
        self.variable_tarifa_personalizada_1_1.set(0)
        self.variable_tarifa_personalizada_1_2.set(0)
        self.variable_tarifa_personalizada_1_3.set(0)

        self.variable_tarifa_personalizada_2_hora.set(0)
        self.variable_tarifa_personalizada_2_1.set(0)
        self.variable_tarifa_personalizada_2_2.set(0)
        self.variable_tarifa_personalizada_2_3.set(0)

        self.variable_tarifa_personalizada_3_hora.set(0)
        self.variable_tarifa_personalizada_3_1.set(0)
        self.variable_tarifa_personalizada_3_2.set(0)
        self.variable_tarifa_personalizada_3_3.set(0)

        self.variable_tarifa_personalizada_4_hora.set(0)
        self.variable_tarifa_personalizada_4_1.set(0)
        self.variable_tarifa_personalizada_4_2.set(0)
        self.variable_tarifa_personalizada_4_3.set(0)

        self.variable_tarifa_personalizada_5_hora.set(0)
        self.variable_tarifa_personalizada_5_1.set(0)
        self.variable_tarifa_personalizada_5_2.set(0)
        self.variable_tarifa_personalizada_5_3.set(0)

        self.variable_tarifa_personalizada_6_hora.set(0)
        self.variable_tarifa_personalizada_6_1.set(0)
        self.variable_tarifa_personalizada_6_2.set(0)
        self.variable_tarifa_personalizada_6_3.set(0)

        self.variable_tarifa_personalizada_7_hora.set(0)
        self.variable_tarifa_personalizada_7_1.set(0)
        self.variable_tarifa_personalizada_7_2.set(0)
        self.variable_tarifa_personalizada_7_3.set(0)

        self.variable_tarifa_personalizada_8_hora.set(0)
        self.variable_tarifa_personalizada_8_1.set(0)
        self.variable_tarifa_personalizada_8_2.set(0)
        self.variable_tarifa_personalizada_8_3.set(0)

        self.variable_tarifa_personalizada_9_hora.set(0)
        self.variable_tarifa_personalizada_9_1.set(0)
        self.variable_tarifa_personalizada_9_2.set(0)
        self.variable_tarifa_personalizada_9_3.set(0)

        self.variable_tarifa_personalizada_10_hora.set(0)
        self.variable_tarifa_personalizada_10_1.set(0)
        self.variable_tarifa_personalizada_10_2.set(0)
        self.variable_tarifa_personalizada_10_3.set(0)

        self.variable_tarifa_personalizada_11_hora.set(0)
        self.variable_tarifa_personalizada_11_1.set(0)
        self.variable_tarifa_personalizada_11_2.set(0)
        self.variable_tarifa_personalizada_11_3.set(0)

        self.variable_tarifa_personalizada_12_hora.set(0)
        self.variable_tarifa_personalizada_12_1.set(0)
        self.variable_tarifa_personalizada_12_2.set(0)
        self.variable_tarifa_personalizada_12_3.set(0)

        self.variable_tarifa_personalizada_13_hora.set(0)
        self.variable_tarifa_personalizada_13_1.set(0)
        self.variable_tarifa_personalizada_13_2.set(0)
        self.variable_tarifa_personalizada_13_3.set(0)

        self.variable_tarifa_personalizada_14_hora.set(0)
        self.variable_tarifa_personalizada_14_1.set(0)
        self.variable_tarifa_personalizada_14_2.set(0)
        self.variable_tarifa_personalizada_14_3.set(0)

        self.variable_tarifa_personalizada_15_hora.set(0)
        self.variable_tarifa_personalizada_15_1.set(0)
        self.variable_tarifa_personalizada_15_2.set(0)
        self.variable_tarifa_personalizada_15_3.set(0)

        self.variable_tarifa_personalizada_16_hora.set(0)
        self.variable_tarifa_personalizada_16_1.set(0)
        self.variable_tarifa_personalizada_16_2.set(0)
        self.variable_tarifa_personalizada_16_3.set(0)

        self.variable_tarifa_personalizada_17_hora.set(0)
        self.variable_tarifa_personalizada_17_1.set(0)
        self.variable_tarifa_personalizada_17_2.set(0)
        self.variable_tarifa_personalizada_17_3.set(0)

        self.variable_tarifa_personalizada_18_hora.set(0)
        self.variable_tarifa_personalizada_18_1.set(0)
        self.variable_tarifa_personalizada_18_2.set(0)
        self.variable_tarifa_personalizada_18_3.set(0)

        self.variable_tarifa_personalizada_19_hora.set(0)
        self.variable_tarifa_personalizada_19_1.set(0)
        self.variable_tarifa_personalizada_19_2.set(0)
        self.variable_tarifa_personalizada_19_3.set(0)

        self.variable_tarifa_personalizada_20_hora.set(0)
        self.variable_tarifa_personalizada_20_1.set(0)
        self.variable_tarifa_personalizada_20_2.set(0)
        self.variable_tarifa_personalizada_20_3.set(0)

        self.variable_tarifa_personalizada_21_hora.set(0)
        self.variable_tarifa_personalizada_21_1.set(0)
        self.variable_tarifa_personalizada_21_2.set(0)
        self.variable_tarifa_personalizada_21_3.set(0)

        self.variable_tarifa_personalizada_22_hora.set(0)
        self.variable_tarifa_personalizada_22_1.set(0)
        self.variable_tarifa_personalizada_22_2.set(0)
        self.variable_tarifa_personalizada_22_3.set(0)

        self.variable_tarifa_personalizada_23_hora.set(0)
        self.variable_tarifa_personalizada_23_1.set(0)
        self.variable_tarifa_personalizada_23_2.set(0)
        self.variable_tarifa_personalizada_23_3.set(0)

        self.variable_tarifa_personalizada_24_hora.set(0)
        self.variable_tarifa_personalizada_24_1.set(0)
        self.variable_tarifa_personalizada_24_2.set(0)
        self.variable_tarifa_personalizada_24_3.set(0)

        self.variable_is_sensilla.set(False)
        self.variable_is_personalizada.set(False)
        self.variable_type_qr.set(False)
        self.variable_type_button.set(False)
        self.id_promocion.set("")
        self.name_promocion.set("")
        self.entry_nombre_promocion.focus()

        self.update_interface_ID()

    def update_status_promo(self):
        self.is_active_promo
        name_promo = self.name_promocion.get()

        if mb.askyesno("Alerta", f'¿Esta seguro de querer {"deshabilitar" if self.is_active_promo else "habilitar"} la promocion {name_promo}?') == False:
            return
        
        name_promo = self.instance_config.get_real_name_promo(name_promo)

        self.instance_config.set_config("promociones",name_promo, "estatus", new_value=False if self.is_active_promo else True)

        nombre_usuario_activo = self.DB.nombre_usuario_activo()

        self.cambios_model.add_change(
            nombre_cambio = f'Se {"deshabilita" if self.is_active_promo else "habilita"} la promocion {name_promo}',valor_anterior="N/A", valor_nuevo="N/A",
            tipo_cambio = "Configuracion de promociones", nombre_usuario= nombre_usuario_activo)

        state = self.printer_controller.print_changes("Cambios de configuracion\nTarifa general", {f'Se {"deshabilita" if self.is_active_promo else "habilita"} la promocion {name_promo}'})

        if state != None:
            mb.showwarning("Alerta", state)

        mb.showinfo(
            "Exito", f'La tarifa fue {"deshabilitada exitosamente, no podrá seguir usandose hasta que se habilite de nuevo" if self.is_active_promo else f"habilitada exitosamente, puede comenzar a utilizar la promocion [{name_promo}]"}')

        self.clear_frame_tarifa()

    def clear_frame_tarifa(self):
        self.clean_data_tarifa()
        self.labelframe_form_tarifas.destroy()
        self.labelframe_form_tarifas = LabelFrame(
            self.tarifas_promociones_frame)
        self.labelframe_form_tarifas.grid(
            column=0, row=3, padx=3, pady=0)

        self.combobox_promociones["values"] = [
            "Seleccione una opcion"] + self.instance_config.get_promo_list()
        self.combobox_promociones.current(0)
        self.variable_promo_selected.set("Seleccione una opcion")
        self.is_new_promo = True
        self.entry_nombre_promocion.configure(state='normal')

    def delete_id_promo(self):
        self.label_id_promocion.destroy()
        self.entry_id_promocion.destroy()
        self.entry_nombre_promocion.focus()
        # print("se elimina entry_id_promocion")

    def restore_id_promo(self):
        # Volver a crear e insertar el widget en el mismo lugar
        self.label_id_promocion = Label(
            self.labelframe_identity_promo, text="ID", font=self.font_text_interface)
        self.label_id_promocion.grid(
            column=0, row=1, padx=0, pady=0)

        self.entry_id_promocion = Entry(
            self.labelframe_identity_promo, width=10, textvariable=self.id_promocion, justify='center', font=self.font_text_interface)
        self.entry_id_promocion.grid(
            column=1, row=1, padx=0, pady=0)
        self.entry_id_promocion.focus()

        state = 'readonly' if self.is_new_promo == False and self.instance_config.type_promo(
            self.variable_promo_selected.get()) == "qr" else 'normal'

        self.entry_id_promocion.configure(state=state)
        # print("se restaura entry_id_promocion")
        # print(f"estado del entry_id_promocion cambiado a: {state}")

    def update_interface_ID(self):
        if self.variable_type_qr.get():
            self.restore_id_promo()

        if self.variable_type_button.get() or (self.variable_type_qr.get() == False and self.variable_type_button.get() == False):
            self.delete_id_promo()

        # print(f"el widget entry_id_promocion: {'si' if self.entry_id_promocion.winfo_exists() else 'no'} existe\n")

    def add_email(self, type_email: str, list_email: Variable, list_box: Listbox):
        self.instance_tools.desactivar(self.configuracion)
        AddEmail(type_email, list_email, list_box)
        self.instance_tools.activar(self.configuracion)

    def delete_email(self, type_email: str, list_email: Variable, list_box: Listbox):
        try:
            indice = list_email.get().index(list_box.selection_get())
            email = indice
            if mb.askokcancel("Alerta", f"¿Esta seguro de querer eliminar el correo [{list_email.get()[indice]}] de la lista de {type_email.replace('_', ' de ')}?") == False:
                return

            if ask_security_question(self.configuracion) != True:
                return

            self.instance_config.del_config(
                "general", "configuiracion_envio", type_email, email)

            mb.showinfo(
                "Alerta", f"El correo fue eliminado exitosamente de la lista de {type_email.replace('_', ' de ')}")
            data_list_email = self.instance_config.get_config(
                "general", "configuiracion_envio", type_email)
            list_email.set(data_list_email)

        except Exception:
            return
        finally:
            list_box.selection_clear(0, END)

    def exit_system(self, modulo: str):
        mb.showwarning(
            "Alerta", f"El sistema se cerrara para guardar los cambios de del modulo de: {modulo}")
        raise SystemExit()


if __name__ == '__main__':
    View_Panel_Config()
