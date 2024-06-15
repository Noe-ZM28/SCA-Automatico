from escpos.printer import USBNotFoundError
from datetime import datetime
from tkinter import Tk, messagebox as mb, ttk, StringVar, Frame, LabelFrame, Button, Label, Entry, NW, TclError
import locale
from platform import system

from Models.Model import Operacion
from Controllers.ConfigController import ConfigController
from Controllers.PrinterController import PrinterController
from Tools.Exceptions import WithoutParameter, NotExist
from Tools.Tools import Tools
from .ViewLoginPanelConfig import View_Login


class ViewEntrada:
    def __init__(self):
        locale_time = 'es_ES' if system() == "Windows" else 'es_MX.utf8'
        locale.setlocale(locale.LC_TIME, locale_time)

        self.instance_config = ConfigController()
        self.printer_controller = PrinterController()
        self.instance_tools = Tools()
        self.DB = Operacion()
        self.root = Tk()

        self.get_config_data()

        self.root.title(f"{self.nombre_estacionamiento} Entrada")

        if self.pantalla_completa:
            # Obtener el ancho y alto de la pantalla
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Configura la ventana para que ocupe toda la pantalla
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # Colocar el LabelFrame en las coordenadas calculadas
        self.principal = LabelFrame(self.root)
        self.principal.pack(expand=True, padx=5, pady=5, anchor='n')

        self.interface_entrada()
        self.check_inputs()

        self.root.mainloop()
        ########################### Inicia Pagina1##########################

    def get_config_data(self) -> None:
        """
        Obtiene la configuracion del sistema desde el archivo de configuracion.

        La funcion asigna valores a diversas variables de instancia con base en la configuracion del sistema.

        No retorna ningún valor explicito, pero asigna valores a las variables de instancia de la clase.
        """
        try:
            self.fecha_interna_entrada = None
            self.fecha_interna_salida = None

            data_config = self.instance_config.get_config(
                "general")

            self.nombre_estacionamiento = data_config["informacion_estacionamiento"]["nombre_estacionamiento"]

            data_config = data_config["configuracion_sistema"]

            # Configuracion de fechas del sistema
            formatos_fecha = data_config["formatos_fecha"]

            self.date_format_system = "%Y-%m-%d %H:%M:%S"
            self.date_format_ticket = formatos_fecha[data_config["formato_hora_boleto"]]
            self.date_format_clock = formatos_fecha[data_config["formato_hora_reloj_expedidor_boleto"]]

            # Configuracion de fuentes y estilos
            fuente_sistema = data_config["fuente"]

            size_text_font = data_config["size_text_font"]
            size_text_font_subtittle_system = data_config["size_text_font_subtittle_system"]
            size_text_button_font = data_config["size_text_button_font"]

            self.font_entrada = (fuente_sistema, size_text_font+10)
            self.font_entrada_negritas = (
                fuente_sistema, size_text_font+10, 'bold')
            self.font_mensaje = (fuente_sistema, size_text_font+30)
            self.font_reloj = (fuente_sistema, size_text_font+55)
            self.font_bienvenida = (fuente_sistema, size_text_font+15)
            self.font_entry_placa = (fuente_sistema, size_text_font+25, 'bold')

            self.font_subtittle_system = (
                fuente_sistema, size_text_font_subtittle_system, 'bold')
            self.font_botones_interface = (
                fuente_sistema, size_text_button_font, 'bold')
            self.font_text_interface = (fuente_sistema, size_text_font)
            self.font_text_entry_interface = (
                fuente_sistema, size_text_font, 'bold')
            self.font_scrolledtext = (fuente_sistema, size_text_font)

            # Configuracion de colores
            self.button_color = data_config["color_botones_interface"]
            self.button_letters_color = data_config["color_letra_botones_interface"]

            # Configuracion de la impresora
            self.printer_idVendor = self.instance_tools.text_to_hexanumber(
                data_config["impresora"]["idVendor"])
            self.printer_idProduct = self.instance_tools.text_to_hexanumber(
                data_config["impresora"]["idProduct"])

            # Otras configuraciones generales
            self.requiere_placa = data_config["requiere_placa"]
            self.pantalla_completa = data_config["pantalla_completa"]

            self.imprime_contra_parabrisas = data_config["imprime_contra_parabrisas"]
            self.imprime_contra_localizacion = data_config["imprime_contra_localizacion"]
            self.solicita_datos_del_auto = data_config["solicita_datos_del_auto"]

            # Configuracion de imagenes
            data_config = self.instance_config.get_config(
                "general", "imagenes")
            self.logo_empresa = data_config["path_logo_boleto"]
            self.imagen_marcas_auto = data_config["path_marcas_auto"]

            size = size_text_font+10
            self.config_icon = self.instance_tools.get_icon(
                data_config["config_icon"], (size, size))

            data_config = None

        except Exception as e:
            mb.showerror(
                "Error", f"Error al cargar configuracion, inicie de nuevo el sistema.\n\nEn caso de que el error continue contacte a un administrador inmediatamente y muestre el siguiente error:\n\n\n{e}")
            raise SystemExit

    def interface_entrada(self):
        seccion_entrada = Frame(self.principal)
        seccion_entrada.grid(column=0, row=0, padx=2, pady=2)

        frame_bienvenida = Frame(seccion_entrada)
        frame_bienvenida.grid(column=0, row=0, padx=2, pady=2)

        # Asegura que la fila y la columna del frame se expandan con el contenedor
        frame_bienvenida.grid_rowconfigure(0, weight=1)
        frame_bienvenida.grid_columnconfigure(0, weight=1)

        boton_config = ttk.Button(
            frame_bienvenida, image=self.config_icon, command=self.view_config_panel)
        boton_config.grid(column=0, row=0)

        label_entrada = Label(
            frame_bienvenida, text=f"Bienvenido(a) al estacionamiento {self.nombre_estacionamiento}", font=self.font_bienvenida, justify='center')
        label_entrada.grid(
            row=0, column=1)

        frame_datos_entrada = Frame(seccion_entrada)
        frame_datos_entrada.grid(column=0, row=1, padx=2, pady=2)

        frame_info_cliente = Frame(frame_datos_entrada)
        frame_info_cliente.grid(column=0, row=0, padx=2, pady=2)

        frame_info_placa = Frame(frame_info_cliente)
        frame_info_placa.grid(column=0, row=0, padx=2, pady=2)

        label_placa = Label(
            frame_info_placa, text="Ingrese Placa", font=self.font_bienvenida)
        label_placa.grid(column=0, row=0, padx=2, pady=2)

        # Entrada para la placa
        self.Placa = StringVar()
        self.entry_placa = Entry(
            frame_info_placa, width=20, textvariable=self.Placa, font=self.font_entry_placa, justify='center')
        self.entry_placa.bind(
            '<Return>', self.Pensionados)
        self.entry_placa.grid(
            column=0, row=1, padx=2, pady=2)

        frame_boton = Frame(frame_datos_entrada)
        frame_boton.grid(column=2, row=0, padx=2, pady=2)

        frame_folio = Frame(frame_boton)
        frame_folio.grid(column=0, row=0, padx=2, pady=2)

        label_folio = Label(frame_folio, text="Folio:", font=self.font_entrada)
        label_folio.grid(column=0, row=0, padx=2, pady=2, sticky="nsew")
        self.MaxId = StringVar()
        entryMaxId = Entry(frame_folio, width=10, textvariable=self.MaxId,
                           state="readonly", font=self.font_entrada)
        entryMaxId.grid(column=1, row=0, padx=2, pady=2, sticky=NW)

        boton_entrada = Button(frame_boton, text="Generar Entrada", width=15, height=3, anchor="center", background=self.button_color,
                               fg=self.button_letters_color, font=self.font_entrada_negritas, command=self.generar_boleto)
        boton_entrada.grid(column=0, row=1, padx=2, pady=2)

        frame_info = LabelFrame(seccion_entrada)  # , background = '#CCC')
        frame_info.grid(column=0, row=2, padx=2, pady=2)

        self.label_informacion = Label(
            frame_info, text="... ", width=25, font=self.font_mensaje, justify='center')
        self.label_informacion.grid(column=0, row=0, padx=2, pady=2)

        frame_reloj = Frame(seccion_entrada)
        frame_reloj.grid(column=0, row=3, padx=2, pady=2)

        self.Reloj = Label(frame_reloj, text="Reloj", background="white",
                           font=self.font_reloj, justify='center')
        self.Reloj.grid(column=0, row=0, padx=2, pady=2)
        self.entry_placa.focus()


    def check_inputs(self):
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

        # Llamar a la funcion check_inputs despues de 60 milisegundos
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

            self.label_informacion.config(text=f"Se genera boleto")


        except Exception as e:
            state=e

        finally:
            self.label_informacion.config(text=state)
            self.entry_placa.focus()
            self.Placa.set("")

    def Pensionados(self, event):
        try:
            numero_tarjeta = self.instance_tools.get_id_from_QR(
                self.Placa.get())

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

            self.Placa.set("")
            self.entry_placa.focus()
            self.label_informacion.config(
                text=f"Entro pensionado ID-{numero_tarjeta}")

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
                raise SystemError(state)

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

    def view_config_panel(self):
        self.instance_tools.desactivar(self.root)
        View_Login()
        self.instance_tools.activar(self.root)


if __name__ == '__main__':
    ViewEntrada()
