from datetime import datetime, timedelta
from escpos.printer import Usb
import traceback
import tkinter as tk
from operacion import Operacion
from time import sleep

import RPi.GPIO as io           # Importa libreria de I/O (entradas / salidas)

from enum import Enum


class System_Messages(Enum):
    """
    Enumeración de mensajes con descripciones.

    Los miembros de esta enumeración representan mensajes comunes
    y tienen asociadas cadenas descriptivas.
    """
    PROCEED:str = "\nAvance\n"
    WITHOUT_ACCESS:str = "\nSin registro de entrada\n"
    NOT_EXIST_PENSION:str = "\nNo existe Pensionado\n"
    DESACTIVATE_CARD:str = "\nTarjeta desactivada\n"
    PENSION_OUTSIDE:str = "\nEl Pensionado ya salió\n"

    NOT_EXIST_TICKET:str = "\nNo existe un auto con dicho código\n"
    NOT_PAY_TICKET:str = "\nBoleto sin pagar\nPase a estación de cobro"
    RE_USED_TICKET:str = "\nBoleto ya usado\n"

    ERROR:str = "\nHa ocurrido un error\n Lea nuevamente la tarjeta"
    ERROR_QR:str = "Error al leer codigo QR\nAsegurese de haber leido el\ncomprobante de pago y no el boleto"
    DEFAULT_TEXT:str = "\nPresente boleto\n"
    NONE_MESAGE:str = "\n...\n"

class Pines(Enum):
    """
    Enumeración de pines y descripcion

    (En caso de modificar un PIN tambien modificar su comentario)
    """
    PIN_BARRERA:int = 13 # gpio13,pin33,Salida

    PIN_INDICADOR_BARRERA:int = 26 # gpio26,pin37,Salida

class State(Enum):
    ON = 0
    OFF = 1

io.setmode(io.BCM)              # modo in/out pin del micro
io.setwarnings(False)           # no señala advertencias de pin ya usados

io.setup(Pines.PIN_BARRERA.value,io.OUT)           # configura en el micro las salidas
io.setup(Pines.PIN_INDICADOR_BARRERA.value,io.OUT)  

io.output(Pines.PIN_BARRERA.value, State.OFF.value)
io.output(Pines.PIN_INDICADOR_BARRERA.value, State.OFF.value)


nombre_estacionamiento = 'Hidalgo 401'
nombre_salida = "Punto Santa Rosa"

font_mensaje = ('Arial', 40)
font_reloj = ('Arial', 65)

fullscreen = True


class Entrada:
    def __init__(self):
        """
        Constructor de la clase Entrada.

        Inicializa los atributos y crea la interfaz gráfica.
        """
        # Objeto para interactuar con la base de datos
        self.DB = Operacion()

        # Objeto para crear la ventana principal
        self.root=tk.Tk()

        # Título de la ventana
        self.root.title(f"{nombre_estacionamiento} Salida {nombre_salida}")

        if fullscreen:
            # Obtener el ancho y alto de la pantalla
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            # Configura la ventana para que ocupe toda la pantalla
            # self.root.geometry(f"{screen_width}x{screen_height}+0+0")

            self.root.attributes('-fullscreen', True)  
            self.fullScreenState = False
            self.root.bind("<F11>", self.enter_fullscreen)
            self.root.bind("<Escape>", self.exit_fullscreen)

        # Colocar el LabelFrame en las coordenadas calculadas
        self.principal = tk.LabelFrame(self.root)
        self.principal.pack(expand=True, padx=5, pady=5, anchor='n')

        # Variable para guardar el máximo id de la base de datos
        self.MaxId = tk.StringVar()

        # Variable para guardar el número de la tarjeta RFID
        self.variable_salida = tk.StringVar()

        # Variable para guardar la placa del vehículo
        self.Placa = tk.StringVar()

        # Método para mostrar la interface
        self.Interface()

        # Método para verificar las entradas de los sensores
        self.check_inputs() 

        # Iniciar el bucle principal de la ventana
        self.root.mainloop() 

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

        # Label para mostrar el mensaje de bienvenida
        label_entrada = tk.Label(frame_mensaje_bienvenida, text=f"¡Hasta pronto!", font=font_mensaje, justify='center')
        label_entrada.grid(row=0, column=0)


        frame_info = tk.LabelFrame(seccion_entrada)
        frame_info.grid(column=0, row=2, padx=2, pady=2)

        # Label para mostrar el mensaje del sistema
        self.label_informacion = tk.Label(frame_info, text=System_Messages.DEFAULT_TEXT.value, width=27, font=font_mensaje, justify='center') 
        self.label_informacion.grid(column=0, row=0, padx=2, pady=2)


        frame_inferior = tk.LabelFrame(seccion_entrada)
        frame_inferior.grid(column=0, row=3, padx=2, pady=2)

        # Frame para mostrar el campo de entrada de la placa
        frame_info_placa=tk.Frame(frame_inferior)
        frame_info_placa.grid(column=0, row=0, padx=2, pady=2)

        # Entry para ingresar el número de la tarjeta
        self.entry_salida=tk.Entry(frame_info_placa, width=50, textvariable=self.variable_salida, font=('Arial', 10, 'bold'), justify='center')

        # Asignar la función Pensionados al evento de presionar la tecla Enter
        self.entry_salida.bind('<Return>', self.salida_cliente) 
        self.entry_salida.grid(column=0, row=0, padx=2, pady=2)

        frame_reloj = tk.Frame(frame_inferior)
        frame_reloj.grid(column=0, row=1, padx=2, pady=2)

        # Label para mostrar la hora actual
        self.Reloj = tk.Label(frame_reloj, font=font_reloj, justify='center')
        self.Reloj.grid(column=0, row=0, padx=2, pady=2)

        frame_etiquetas = tk.Frame(frame_inferior)
        frame_etiquetas.grid(column=0, row=2, padx=2, pady=2)

        # Dar el foco al entry de la tarjeta
        self.entry_salida.focus()

    def check_inputs(self):
        """
        Actualiza reloj de salida.
        """
        # Obtener la fecha y hora actual con el formato deseado
        fecha_hora =datetime.now().strftime("%d-%b-%Y %H:%M:%S")

        # Actualizar el label del reloj con la fecha y hora
        self.Reloj.config(text=fecha_hora)
  
        # Llamar al método check_inputs cada 60 milisegundos
        self.root.after(60, self.check_inputs)

    def salida_cliente(self, event):
        try:
            datos = self.variable_salida.get()
            print(datos)

            if not datos:
                self.show_message(System_Messages.DEFAULT_TEXT)
                return

            if len(datos) == 10:
                print("salida - pensionado")
                self.salida_pensionados(self)
                return

            elif len(datos) > 19:
                folio = datos[16:]
                print(folio)

                respuesta=self.DB.consulta(folio)
                if len(respuesta) == 0:
                    self.show_message(System_Messages.NOT_EXIST_TICKET)
                    self.variable_salida.set("")
                    return

                fecha_salida = respuesta[0][1]
                estatus = respuesta[0][2]

                if fecha_salida == None:
                    self.show_message(System_Messages.NOT_PAY_TICKET)
                    self.variable_salida.set("")
                    return

                if estatus == "Afuera":
                    self.show_message(System_Messages.RE_USED_TICKET)
                    self.variable_salida.set("")
                    return


                estatus=("Afuera", folio)
                self.DB.ActualizaSalida(estatus)

                # Ejecutar el método abrir_barrera
                self.variable_salida.set("")
                self.abrir_barrera()

            else:
                self.show_message(System_Messages.ERROR_QR)
                self.variable_salida.set("")
                return

        # Si ocurre una excepción
        except Exception as e:
            self.variable_salida.set("")
            # Imprimir la excepción en la consola
            print(e)
            # Imprimir la traza de la excepción en la consola
            traceback.print_exc()
            # Mostrar el mensaje de que ha ocurrido un error
            self.show_message(System_Messages.ERROR)


    def salida_pensionados(self, event):
        tarjeta = int(self.variable_salida.get())

        Existe=self.DB.ValidarPen(tarjeta)
        if len(Existe) == 0 :
            self.show_message(System_Messages.NOT_EXIST_PENSION)
            self.variable_salida.set("")
            return

        respuesta=self.DB.ConsultaPensionado(Existe)
        #Fecha_vigencia, Estatus, Vigencia
        for fila in respuesta:
            Fecha_vigencia=fila[0]
            Estatus=fila[1]
            Vigencia=fila[2]

        if Estatus == None:
            self.show_message(System_Messages.WITHOUT_ACCESS)
            self.variable_salida.set("")
            return

        if Estatus == 'Afuera':
            self.show_message(System_Messages.PENSION_OUTSIDE)
            self.variable_salida.set("")
            return

        if Fecha_vigencia == None:
            self.show_message(System_Messages.DESACTIVATE_CARD)
            self.variable_salida.set("")
            return

        # Consulta la hora de entrada del pensionado
        entrada = self.DB.consultar_UpdMovsPens(Existe)

        # Obtener la fecha y hora actual en formato deseado
        entrada = entrada.strftime("%Y-%m-%d %H:%M:%S")

        # Convertir la cadena de caracteres en un objeto datetime
        Entrada = datetime.strptime(entrada, "%Y-%m-%d %H:%M:%S")

        Salida = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        # Convertir la cadena de caracteres en un objeto datetime
        Salida = datetime.strptime(Salida, "%Y-%m-%d %H:%M:%S")

        # Calcular el tiempo total en el estacionamiento
        tiempo_total = Salida - Entrada

        # Preparar los datos para la actualizacion en la base de datos
        datos = (Salida, tiempo_total, 'Afuera', Existe)
        datos1 = ('Afuera', Existe)

        self.DB.UpdMovsPens(datos)
        self.DB.UpdPens2(datos1)

        self.abrir_barrera()
        self.variable_salida.set("")
        self.entry_salida.focus()


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

        self.show_message(System_Messages.DEFAULT_TEXT)

    def show_message(self, message: System_Messages) -> None:
        """
        Muestra un mensaje en la interfaz.

        :param message (str): Mensaje a mostrar.
        :return: None
        """
        # Configurar el label de información con el texto del mensaje
        self.label_informacion.config(text=message.value)
        # Limpiar el entry de la tarjeta
        self.variable_salida.set("")
        # Dar el foco al entry de la tarjeta
        self.entry_salida.focus()

    def enter_fullscreen(self, event):
        """
        Cambia el modo de pantalla completa de la ventana.

        :param event: Evento de teclado.
        :return: None
        """
        # Cambiar el estado de pantalla completa al opuesto
        self.fullScreenState = not self.fullScreenState
        # Configurar el atributo de pantalla completa de la ventana
        self.root.attributes("-fullscreen", self.fullScreenState)
        # Dar el foco al entry de la tarjeta
        self.entry_salida.focus() 

    def exit_fullscreen(self, event):
        """
        Sale del modo de pantalla completa de la ventana.

        :param event: Evento de teclado.
        :return: None
        """
        # Dar el foco al entry de la tarjeta
        self.entry_salida.focus()
        # Cambiar el estado de pantalla completa a falso
        self.fullScreenState = False
        # Configurar el atributo de pantalla completa de la ventana
        self.root.attributes("-fullscreen", self.fullScreenState)



if __name__ == '__main__':
    # Crear un objeto de la clase Entrada
    Entrada()

