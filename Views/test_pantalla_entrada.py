from datetime import datetime, timedelta
from escpos.printer import Usb
import traceback
import tkinter as tk
from tkinter import messagebox as mb, ttk
from Models.Model import Operacion
from Tools.Tools import Tools
from time import sleep
from Tools.Exceptions import WithoutParameter, SystemError, NotExist

import RPi.GPIO as io           # Importa libreria de I/O (entradas / salidas)
from Controllers.ConfigController import ConfigController
from Controllers.PrinterController import PrinterController
from .ViewLoginPanelConfig import View_Login

from enum import Enum
instance_config = ConfigController()
printer_controller = PrinterController()

data_config = instance_config.get_config("funcionamiento_interno", "pines")

class Colors(Enum):
    """
    Enumeración que representa colores predefinidos.

    Cada color tiene un nombre asociado y un código hexadecimal.
    """
    # Códigos hexadecimales para los colores
    GREEN:str = "#00FF00"
    RED:str = "#FF0000"

class Alerts(Enum):
    """
    Enumeración de mensajes con descripciones.

    Los miembros de esta enumeración representan mensajes comunes
    y tienen asociadas cadenas descriptivas.
    """
    AUTO_EXISTS:str = "Hay auto"
    AUTO_NOT_EXISTS:str = "No hay auto"

    BUTTON_PRESSED:str = "Boton presionado."
    BUTTON_NOT_PRESSED:str = "Boton sin precionar"

class System_Messages(Enum):
    """
    Enumeración de mensajes con descripciones.

    Los miembros de esta enumeración representan mensajes comunes
    y tienen asociadas cadenas descriptivas.
    """
    TAKE_TICKET:str = "Tome su boleto\n"
    NOT_AUTO:str = "No hay auto\n"

    NOT_EXIST_PENSION:str = "No existe Pensionado\n"
    DESACTIVATE_CARD:str = "Tarjeta desactivada\n"

    PENSION_INSIDE:str = "El Pensionado ya está dentro\n"
    PENSION_EXPIRED:str = "Pensión vencida\n"

    PROCEED:str = "Avance\n"
    PRESS_BUTTON:str = "Precione boton\n"
    ERROR:str = "Ha ocurrido un error\n Lea nuevamente la tarjeta"

    NONE_MESAGE:str = "...\n"

class Pines(Enum):
    """
    Enumeración de pines y descripcion

    (En caso de modificar un PIN tambien modificar su comentario)
    """
    PIN_BARRERA:int = data_config["Entrada"]["barrera"]# 13 # gpio13,pin33,Salida 
    PIN_BOTON:int =data_config["Entrada"]["boton"]# 18 # gpio18,pin12,Salida 
    PIN_SENSOR_AUTO:int = data_config["Entrada"]["sensor"]#4 # gpio4,pin7,Entrada 


    PIN_INDICADOR_BARRERA:int = 26 # gpio26,pin37,Salida 
    PIN_INDICADOR_BOTON:int = 6 # gpio6,pin31,Salida
    PIN_INDICADOR_SENSOR_AUTO:int = 19 # gpio19,pin35,Salida

class State(Enum):
    ON = 0
    OFF = 1



io.setmode(io.BCM)              # modo in/out pin del micro
io.setwarnings(False)           # no señala advertencias de pin ya usados

io.setup(Pines.PIN_SENSOR_AUTO.value,io.IN)             # configura en el micro las entradas
io.setup(Pines.PIN_BOTON.value,io.IN)             # configura en el micro las entradas


io.setup(Pines.PIN_BARRERA.value,io.OUT)           # configura en el micro las salidas
io.setup(Pines.PIN_INDICADOR_SENSOR_AUTO.value,io.OUT)           # configura en el micro las salidas
io.setup(Pines.PIN_INDICADOR_BOTON.value,io.OUT)
io.setup(Pines.PIN_INDICADOR_BARRERA.value,io.OUT)  


io.output(Pines.PIN_BARRERA.value, State.OFF.value)
io.output(Pines.PIN_INDICADOR_SENSOR_AUTO.value, State.OFF.value)
io.output(Pines.PIN_INDICADOR_BOTON.value, State.OFF.value)
io.output(Pines.PIN_INDICADOR_BARRERA.value, State.OFF.value)

BanLoop = State.OFF.value
BanBoton = State.OFF.value
BanSenBoleto = State.ON.value
BanImpresion = State.ON.value #No ha impreso

logo_1 = "LOGO1.jpg"
AutoA = "AutoA.png"
qr_imagen = "reducida.png"
 
nombre_estacionamiento = 'Hidalgo 401'
nombre_entrada = "Punto Santa Rosa"

font_entrada = ('Arial', 20)
font_entrada_negritas = ('Arial', 20, 'bold')
font_mensaje = ('Arial', 40)
font_reloj = ('Arial', 65)

font_etiquetas = ('Arial', 30, 'bold')

fullscreen = False


class Entrada:
    def __init__(self):
        """
        Constructor de la clase Entrada.

        Inicializa los atributos y crea la interfaz gráfica.
        """
        # Objeto para interactuar con la base de datos
        self.DB=Operacion()

        self.instance_tools = Tools()

        # Objeto para crear la ventana principal
        self.root=tk.Tk()

        # Título de la ventana
        self.root.title(f"{nombre_estacionamiento} Entrada {nombre_entrada}")

        if fullscreen:
            # Obtener el ancho y alto de la pantalla
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Configura la ventana para que ocupe toda la pantalla
            # self.root.geometry(f"{screen_width}x{screen_height}+0+0")


        # Colocar el LabelFrame en las coordenadas calculadas
        self.principal = tk.LabelFrame(self.root)
        self.principal.pack(expand=True, padx=5, pady=5, anchor='n')

        # Variable para guardar el máximo id de la base de datos
        self.MaxId = tk.StringVar()

        # Variable para guardar el número de la tarjeta RFID
        self.variable_numero_tarjeta = tk.StringVar()

        # Variable para guardar la placa del vehículo
        self.Placa = tk.StringVar()
        
        self.get_data()

        # Método para mostrar la interface
        self.Interface()

        # Método para verificar las entradas de los sensores
        self.check_inputs() 

        # Iniciar el bucle principal de la ventana
        self.root.mainloop()
        
    def get_data(self):
        data_config = instance_config.get_config("general")
        self.button_color = data_config["configuracion_sistema"]["color_botones_interface"]
        self.button_letters_color = data_config["configuracion_sistema"]["color_letra_botones_interface"]
        self.fuente_sistema = data_config["configuracion_sistema"]["fuente"]
        size_text_font = data_config["configuracion_sistema"]["size_text_font"] + 10

        self.size_text_font_tittle_system = data_config[
            "configuracion_sistema"]["size_text_font_tittle_system"] + 10
        self.size_text_font_subtittle_system = data_config[
            "configuracion_sistema"]["size_text_font_subtittle_system"] + 10
        self.size_text_button_font = data_config["configuracion_sistema"]["size_text_button_font"] + 10

        self.font_subtittle_system = (
            self.fuente_sistema, self.size_text_font_subtittle_system, 'bold')
        self.font_tittle_system = (
            self.fuente_sistema, self.size_text_font_tittle_system, 'bold')
        self.font_botones_interface = (
            self.fuente_sistema, self.size_text_button_font, 'bold')
        self.font = self.font_subtittle_system

        size = (size_text_font+30, size_text_font+10)
        self.hide_password_icon = self.instance_tools.get_icon(
            data_config["imagenes"]["hide_password_icon"], size)
        self.show_password_icon = self.instance_tools.get_icon(
            data_config["imagenes"]["show_password_icon"], size)
        size = size_text_font+15
        self.config_icon = self.instance_tools.get_icon(
            data_config["imagenes"]["config_icon"], (size, size))
        data_config = None

    def Interface(self):
        """
        Crea los widgets de la interfaz gráfica y los coloca en el frame principal.
        """
        # Frame para contener los elementos de la entrada
        seccion_entrada = tk.Frame(self.principal)
        seccion_entrada.grid(column=0, row=0, padx=2, pady=2, sticky=tk.NSEW)

        frame_bienvenida = tk.Frame(seccion_entrada)
        frame_bienvenida.grid(column=0, row=0, padx=2, pady=2)

        frame_mensaje_bienvenida = tk.Frame(frame_bienvenida)
        frame_mensaje_bienvenida.grid(column=0, row=0, padx=2, pady=2)

        # Asegura que la fila y la columna del frame se expandan con el contenedor
        frame_mensaje_bienvenida.grid_rowconfigure(0, weight=1)
        frame_mensaje_bienvenida.grid_columnconfigure(0, weight=1)

        frame_form = tk.Frame(
            frame_mensaje_bienvenida)
        frame_form.grid(
            column=0, row=0, padx=5, pady=5)

        # Botones de salir y entrar
        boton_config = ttk.Button(
            frame_form, image=self.config_icon, command=self.view_config_panel)
        boton_config.grid(column=0, row=0, padx=5, pady=5)

        # Label para mostrar el mensaje de bienvenida
        label_entrada = tk.Label(frame_mensaje_bienvenida, text=f"Bienvenido(a)", font=font_mensaje, justify='center')
        label_entrada.grid(row=0, column=1)


        frame_info = tk.LabelFrame(seccion_entrada)
        frame_info.grid(column=0, row=2, padx=2, pady=2)

        # Label para mostrar el mensaje del sistema
        self.label_informacion = tk.Label(frame_info, text=System_Messages.NONE_MESAGE.value, width=25, font=font_mensaje, justify='center') 
        self.label_informacion.grid(column=0, row=0, padx=2, pady=2)


        frame_inferior = tk.LabelFrame(seccion_entrada)
        frame_inferior.grid(column=0, row=3, padx=2, pady=2)

        # Frame para mostrar el campo de entrada de la placa
        frame_info_placa=tk.Frame(frame_inferior)
        frame_info_placa.grid(column=0, row=0, padx=2, pady=2)

        # Entry para ingresar el número de la tarjeta
        self.entry_numero_tarjeta=tk.Entry(frame_info_placa, width=50, textvariable=self.variable_numero_tarjeta, font=('Arial', 10, 'bold'), justify='center')

        # Asignar la función Pensionados al evento de presionar la tecla Enter
        self.entry_numero_tarjeta.bind('<Return>', self.Pensionados) 
        self.entry_numero_tarjeta.grid(column=0, row=0, padx=2, pady=2)

        frame_reloj = tk.Frame(frame_inferior)
        frame_reloj.grid(column=0, row=1, padx=2, pady=2)

        # Label para mostrar la hora actual
        self.Reloj = tk.Label(frame_reloj, font=font_reloj, justify='center')
        self.Reloj.grid(column=0, row=0, padx=2, pady=2)

        frame_etiquetas = tk.Frame(frame_inferior)
        frame_etiquetas.grid(column=0, row=2, padx=2, pady=2)
        
        # Label para mostrar el estado del sensor de auto
        self.label_auto = tk.Label(frame_etiquetas, text=Alerts.AUTO_EXISTS.value, width=15, font=font_etiquetas, justify='center', background=Colors.GREEN.value)
        self.label_auto.grid(column=0, row=0, padx=2, pady=2)
        
        # Label para mostrar el estado del botón
        self.label_boton = tk.Label(frame_etiquetas, text=Alerts.BUTTON_PRESSED.value, width=15, font=font_etiquetas, justify='center', background=Colors.GREEN.value) 
        self.label_boton.grid(column=1, row=0, padx=2, pady=2)

        # Dar el foco al entry de la tarjeta
        self.entry_numero_tarjeta.focus()

    def view_config_panel(self):
        self.instance_tools.desactivar(self.root)
        View_Login(False)
        self.instance_tools.activar(self.root)

    def interrupcion_SENSOR_AUTO(self):
        """Detecta presencia de automovil"""
        global BanLoop
        # Si el sensor de auto no detecta un auto
        if io.input(Pines.PIN_SENSOR_AUTO.value):

            # Imprimir en la consola que no hay auto
            print('no hay auto') 

            # Apagar el indicador de sensor de auto
            io.output(Pines.PIN_INDICADOR_SENSOR_AUTO.value, State.OFF.value)#con un "1" se apaga el led
          
            # Cambiar el estado del sensor de auto a apagado
            BanLoop = State.OFF.value

        # Si el sensor de auto detecta un auto
        else:
            # Imprimir en la consola que hay auto
            print('hay auto') 

            # Encender el indicador de sensor de auto
            io.output(Pines.PIN_INDICADOR_SENSOR_AUTO.value ,State.ON.value)

            # Cambiar el estado del sensor de auto a encendido
            BanLoop = State.ON.value

    def interrupcion_DETECCION_BOLETO(self):
        """Detecta presion de boton"""
        global BanBoton
        # Si el botón no está presionado
        if io.input(Pines.PIN_BOTON.value):
    
            # Imprimir en la consola que soltó el botón
            print('solto boton')

            # Apagar el indicador de botón
            io.output(Pines.PIN_INDICADOR_BOTON.value, State.OFF.value)

            # Cambiar el estado del botón a apagado
            BanBoton = State.OFF.value

        # Si el botón está presionado
        else:
            # Imprimir en la consola que presionó el botón
            print('presiono boton')
           
            # Encender el indicador de botón
            io.output(Pines.PIN_INDICADOR_BOTON.value ,State.ON.value)

            # Cambiar el estado del botón a encendido
            BanBoton = State.ON.value

    # Agregar eventos para detectar los cambios en los sensores y botones
    io.add_event_detect(Pines.PIN_SENSOR_AUTO.value, io.BOTH, callback = interrupcion_SENSOR_AUTO)
    io.add_event_detect(Pines.PIN_BOTON.value, io.BOTH, callback = interrupcion_DETECCION_BOLETO)

    def check_inputs(self):
        """
        Método para verificar las entradas de los sensores y botones.

        Actualiza los labels de la interfaz gráfica y ejecuta las acciones correspondientes.
        """
        global BanBoton
        global BanLoop
        global BanImpresion
    
        # Si hay un auto en el sensor de auto
        if BanLoop == State.ON.value:
            # Cambiar el label de auto a verde y con el mensaje de que hay auto
            self.change_info_label(self.label_auto, Alerts.AUTO_EXISTS, Colors.GREEN)

            # Obtener el número de la tarjeta del entry
            tarjeta = self.entry_numero_tarjeta.get()

            # Si el número de la tarjeta tiene 10 caracteres
            if len(tarjeta) == 10:
                # Ejecutar el método Pensionados

                self.Pensionados(self)
        # Si no hay un auto en el sensor de auto
        else:
            # Cambiar el label de auto a rojo y con el mensaje de que no hay auto
            self.change_info_label(self.label_auto, Alerts.AUTO_NOT_EXISTS, Colors.RED)

            # Imprimir en la consola que no ejecuta Pensionado
            print("No ejecuta Pensionado")

            # Limpiar el entry de la tarjeta
            self.variable_numero_tarjeta.set("")

            # Dar el foco al entry de la tarjeta
            self.entry_numero_tarjeta.focus()

            # Cambiar el estado de impresión a encendido
            BanImpresion = State.ON.value

        # Si el botón está presionado
        if BanBoton == State.ON.value:
            # Cambiar el label de botón a verde y con el mensaje de que el botón está presionado
            self.change_info_label(self.label_boton, Alerts.BUTTON_PRESSED, Colors.GREEN)
            # Imprimir en la consola el estado del sensor de boleto, el estado de impresión y el estado del sensor de auto
            print("BanSenBoleto ",str(BanSenBoleto))
            print("BanImpresion ",str(BanImpresion))
            print("BamLoop ",str(BanLoop))

            # Si hay un auto en el sensor de auto y el estado de impresión está encendido
            if BanLoop ==State.ON.value and BanImpresion == State.ON.value:
                # Imprimir en la consola que va a imprimir el boleto
                print('imprimir boleto')

                # Ejecutar el método generar_boleto
                self.generar_boleto()

                # Ejecutar el método abrir_barrera
                self.abrir_barrera()

                # Cambiar el estado de impresión a apagado
                BanImpresion = State.OFF.value

                # Si el sensor de boleto no detecta un boleto
                if BanSenBoleto == State.OFF.value:
                    # Imprimir en la consola el estado del sensor de boleto
                    print("En BanSenBoleto= 1 "+str(BanSenBoleto))

                # Si el sensor de boleto detecta un boleto
                else:
                    # Mostrar el mensaje de que tome su boleto
                    self.show_message(System_Messages.TAKE_TICKET)

            # Si no hay un auto en el sensor de auto o el estado de impresión está apagado
            else:
                # Mostrar el mensaje de que presione el botón
                self.show_message(System_Messages.PRESS_BUTTON)

                # Imprimir en la consola que no puede imprimir porque no tiene auto
                print ('no puede imprimir porque no tiene Auto')

        # Si el botón no está presionado
        else:
            # Cambiar el label de botón a rojo y con el mensaje de que el botón no está presionado
            self.change_info_label(self.label_boton, Alerts.BUTTON_NOT_PRESSED, Colors.RED)

            # if BanImpresion == 1: #and BanSenBoleto == 1:# mando a imprimir y ya no tiene boleto en la boquilla
            #     self.SenBol.config(text = "No siente boleto ")



        # Con un "1" se apaga el led
        io.output(Pines.PIN_INDICADOR_BARRERA.value, State.OFF.value)


        # Obtener la fecha y hora actual con el formato deseado
        fecha_hora =datetime.now().strftime("%d-%b-%Y %H:%M:%S")

        # Actualizar el label del reloj con la fecha y hora
        self.Reloj.config(text=fecha_hora)
  
        # Llamar al método check_inputs cada 60 milisegundos
        self.root.after(60, self.check_inputs)


    def generar_boleto(self):
        try:
            # Obtener la placa del vehiculo desde la variable Placa
            # placa = self.Placa.get()

            # Validar si se requiere una placa y si no se ingreso ninguna
            # if not placa and self.requiere_placa:
            #     raise WithoutParameter("Placa del auto")

            folio_boleto = self.DB.MaxfolioEntrada() + 1
            self.MaxId.set(folio_boleto)

            state = printer_controller.print_ticket(folio_boleto, "placa")

            if state != None:
                mb.showwarning("Alerta", state)
                state = ""
                return

            state=f"Se genera boleto"

        except Exception as e:
            state=e

        finally:
            self.label_informacion.config(text=state)
            self.entry_numero_tarjeta.focus()
            self.Placa.set("")


    def Pensionados(self, event):
        """
        Maneja la entrada de pensionados.

        :param event: Evento de teclado.
        :return: None
        """
        try:
            # Obtener el número de la tarjeta del entry
            numtarjeta = self.variable_numero_tarjeta.get()

            # Imprimir el número de la tarjeta en la consola
            print(numtarjeta)
            
            # Validar si el número de la tarjeta existe en la base de datos
            Existe = self.DB.ValidarPen(numtarjeta)

            # Si el número de la tarjeta no existe
            if len(Existe) == 0:
                # Mostrar el mensaje de que no existe pensionado
                self.show_message(System_Messages.NOT_EXIST_PENSION)
                # Terminar la función
                return

            # Consultar los datos del pensionado en la base de datos
            respuesta = self.DB.ConsultaPensionado(Existe)

            # Recorrer la respuesta de la consulta
            for fila in respuesta:
                # Obtener la vigencia actual, el estatus y la tolerancia del pensionado
                VigAct = fila[0]
                Estatus = fila[1]
                Tolerancia = int(fila[3])

            # Si la vigencia actual es nula
            if VigAct is None:
                # Mostrar el mensaje de que la tarjeta está desactivada
                self.show_message(System_Messages.DESACTIVATE_CARD)
                # Terminar la función
                return

            # Si el estatus es adentro
            elif Estatus == 'Adentro':
                # Mostrar el mensaje de que el pensionado ya está dentro
                self.show_message(System_Messages.PENSION_INSIDE)
                # Terminar la función
                return

            # Obtener la fecha y hora actual en formato deseado
            VigAct = VigAct.strftime("%Y-%m-%d %H:%M:%S")
            # Convertir la cadena de caracteres en un objeto datetime
            VigAct = datetime.strptime(VigAct, "%Y-%m-%d %H:%M:%S")

            # Obtener la fecha y hora actual en formato deseado
            hoy = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            # Convertir la cadena de caracteres en un objeto datetime
            hoy = datetime.strptime(hoy, "%Y-%m-%d %H:%M:%S")

            # Obtener la fecha y hora límite para la entrada del pensionado
            limite = self.get_date_limit(VigAct, Tolerancia)
            # Imprimir la fecha y hora límite en la consola
            print(limite)

            # Si la fecha y hora actual es mayor o igual que la fecha y hora límite
            if hoy >= limite:
                # Mostrar el mensaje de que la pensión está vencida
                self.show_message(System_Messages.PENSION_EXPIRED)
                # Terminar la función
                return

            # Crear una tupla con los datos del movimiento del pensionado
            datos = (Existe, numtarjeta, hoy, 'Adentro', 0)

            # Crear una tupla con los datos para actualizar el estatus del pensionado
            datos1 = ('Adentro', Existe)

            # Agregar el movimiento del pensionado a la base de datos
            self.DB.MovsPensionado(datos)

            # Actualizar el estatus del pensionado en la base de datos
            self.DB.UpdPensionado(datos1)

            # Limpiar el entry de la tarjeta
            self.variable_numero_tarjeta.set("")               
            # Dar el foco al entry de la tarjeta
            self.entry_numero_tarjeta.focus()

            # Abrir la barrera
            self.abrir_barrera()

        # Si ocurre una excepción
        except Exception as e:
            # Limpiar el entry de la tarjeta
            self.variable_numero_tarjeta.set("")               
            # Dar el foco al entry de la tarjeta
            self.entry_numero_tarjeta.focus()
            # Imprimir la excepción en la consola
            print(e)
            # Imprimir la traza de la excepción en la consola
            traceback.print_exc()
            # Mostrar el mensaje de que ha ocurrido un error
            self.show_message(System_Messages.ERROR)

    def abrir_barrera(self) -> None:
        """
        Abre la barrera.

        :return: None
        """
        # Mostrar el mensaje de que avance
        self.show_message(System_Messages.PROCEED)

        # Esperar un segundo
        sleep(1)

        # Apagar el indicador de barrera
        io.output(Pines.PIN_INDICADOR_BARRERA.value,State.OFF.value)

        # Abrir la barrera
        io.output(Pines.PIN_BARRERA.value, State.ON.value)
        # Esperar un segundo
        sleep(1)
        # Cerrar la barrera
        io.output(Pines.PIN_BARRERA.value, State.OFF.value)

        # Imprimir el mensaje de que se abre la barrera en la consola
        print('------------------------------')
        print("****** Se abre barrera *******")
        print('------------------------------')

    def get_date_limit(self, date_start:datetime, Tolerance:int) -> datetime:
        """
        Calcula la fecha límite a partir de una fecha de inicio y una cantidad de días de tolerancia.

        :param date_start (datetime): Fecha de inicio.
        :param Tolerance (int): Cantidad de días laborables a agregar.
        :return (datetime): Fecha límite después de agregar la cantidad de días laborables.
        """
        # Inicializar la fecha límite con la fecha de inicio
        date_limit = date_start

        # Mientras queden días de tolerancia
        while Tolerance > 0:
            # Sumar un día a la fecha límite
            date_limit  += timedelta(days=1)
            # Verifica si el día no es fin de semana (lunes a viernes)
            if date_limit.weekday() < 5:
                # Restar un día de tolerancia
                Tolerance -= 1
        
        # Devolver la fecha límite
        return date_limit

    def show_message(self, message: System_Messages) -> None:
        """
        Muestra un mensaje en la interfaz.

        :param message (str): Mensaje a mostrar.
        :return: None
        """
        # Configurar el label de información con el texto del mensaje
        self.label_informacion.config(text=message.value)
        # Limpiar el entry de la tarjeta
        self.variable_numero_tarjeta.set("")
        # Dar el foco al entry de la tarjeta
        self.entry_numero_tarjeta.focus()

    def change_info_label(self, label:tk.Label, new_text:Alerts, new_color:Colors) -> None:
        """
        Cambia el mensje de la etiqueta espeficicada asi como su color.

        :param label (tk.Label): Etiqueta a modificar.
        :param new_text (System_Messages): Mensaje a mostrar.
        :param new_color (Colors): Nuevo color para la etiqueta.

        :return: None
        """
        # Configurar el label con el nuevo texto y el nuevo color
        label.config(text=new_text.value, background=new_color.value)


if __name__ == '__main__':
    # Crear un objeto de la clase Entrada
    Entrada()

