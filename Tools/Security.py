from Controllers.ConfigController import ConfigController
from Controllers.EmailController import SendData
from Models.Model import Operacion
from .Exceptions import WithoutParameter, AuthError
from .Tools import Tools

from tkinter import Label, Entry, W, Button, Frame
from tkinter import Toplevel, messagebox as mb
from tkinter import BooleanVar
from random import randint
from threading import Thread
from datetime import datetime


class Secure:
    """
    Clase que gestiona la seguridad y configuracion del sistema, incluyendo la administracion de preguntas y respuestas de seguridad. Proporciona metodos para registrar y validar preguntas de seguridad.

    Attributes:
        success (bool): Indica si la operacion fue exitosa.

    Methods:
        - interface_add_security_question(): Inicializa una instancia de la clase Secure y crea la ventana principal para registrar preguntas de seguridad.
        - add_security_question(): Registra una pregunta de seguridad en la configuracion del sistema.
        - interface_ask_security_question(): Inicializa una instancia de la clase Secure y crea la ventana principal para ingresar respuestas de seguridad.
        - read_security_question(): Lee la respuesta de seguridad ingresada por el usuario y realiza validaciones.
        - validate(entry: Entry): Valida que un campo de entrada no este vacio.

    """

    def __init__(self) -> None:
        self.__tools__ = Tools()
        self.__config__ = ConfigController()
        self.success = None

    def __load_data__(self) -> None:
        """
        Carga datos de configuracion para la interfaz.

        Returns:
            None
        """
        data_config = self.__config__.get_config("general")
        self.button_color = data_config["configuracion_sistema"]["color_botones_interface"]
        self.button_letters_color = data_config["configuracion_sistema"]["color_letra_botones_interface"]
        self.fuente_sistema = data_config["configuracion_sistema"]["fuente"]
        size_text_font = data_config["configuracion_sistema"]["size_text_font"]

        size_text_font_tittle_system = data_config[
            "configuracion_sistema"]["size_text_font_tittle_system"]
        size_text_font_subtittle_system = data_config[
            "configuracion_sistema"]["size_text_font_subtittle_system"]
        self.size_text_button_font = data_config["configuracion_sistema"]["size_text_button_font"]

        self.font_subtittle_system = (
            self.fuente_sistema, size_text_font_subtittle_system, 'bold')
        self.font_tittle_system = (
            self.fuente_sistema, size_text_font_tittle_system, 'bold')
        self.font_botones_interface = (
            self.fuente_sistema, self.size_text_button_font, 'bold')

        size = (size_text_font_subtittle_system+20,
                size_text_font_subtittle_system+5)
        self.hide_password_icon = self.__tools__.get_icon(
            data_config["imagenes"]["hide_password_icon"], size)
        self.show_password_icon = self.__tools__.get_icon(
            data_config["imagenes"]["show_password_icon"], size)
        data_config = None

    def interface_add_security_question(self) -> None:
        """
        Inicializa una instancia de la clase Login y crea la ventana principal de la interfaz.

        Returns:
            None
        """
        # Crea la ventana principal
        self.window = Toplevel()
        self.__load_data__()
        # Se elimina la funcionalidad del boton de cerrar
        self.window.protocol(
            "WM_DELETE_WINDOW", lambda: self.__tools__.desconectar(self.window))

        # Establece el tamaño de la ventana y su titulo
        self.window.title(
            f"Registrar pregunta de seguridad")

        # Establece que la ventana no sea redimensionable
        self.window.resizable(False, False)

        label = Label(
            self.window, text='Ingresa la respuesta', font=self.font_tittle_system)
        label.grid(row=0, column=0, padx=5, pady=5)

        frame = Frame(
            self.window)
        frame.grid(row=1, column=0, padx=5, pady=5)

        # Crea el campo de entrada de texto para la contraseña
        self.entry_add_answer = Entry(
            frame, show="*", justify="center", font=self.font_subtittle_system, width=30)
        self.entry_add_answer.grid(row=0, column=0, padx=5, pady=5)

        visible_password = BooleanVar(value=False)
        boton_hide_view_password = Button(
            frame, image=self.hide_password_icon, command=lambda: self.__tools__.visible_password(
                boton_hide_view_password, self.entry_add_answer, visible_password, self.show_password_icon, self.hide_password_icon))
        boton_hide_view_password.grid(
            column=1, row=0, padx=5, pady=5)

        frame_xd = Frame(self.window)
        frame_xd.grid(row=2, column=0)

        # Crea el boton para ingresar los datos del usuario y llama al metodo get_data del controlador para procesar los datos
        self.boton_entrar = Button(
            frame_xd, text='Registrar respuesta', command=self.add_security_question, anchor="center", width=20, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        self.boton_entrar.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        self.boton = Button(
            frame_xd, text='Cancelar', command=lambda: self.__tools__.desconectar(self.window), anchor="center", width=10, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        self.boton.grid(row=0, column=1, padx=5, pady=5, sticky=W)

        self.entry_add_answer.focus()

        # Inicia el loop principal de la ventana
        self.window.mainloop()

    def add_security_question(self) -> None:
        """
        Registra una pregunta de seguridad en la configuracion del sistema.

        Returns:
            None
        """
        self.validate(self.entry_add_answer)
        answer, iv = self.__tools__.cifrar_AES(self.entry_add_answer.get())
        cc = ConfigController()
        cc.set_config("general", "configuracion_sistema",
                      "security", "a", new_value=answer)
        answer = None
        cc.set_config("general", "configuracion_sistema",
                      "security", "p", new_value=iv.hex())
        iv = None
        cc = None
        self.__tools__.desconectar(self.window)
        mb.showwarning(
            "Alerta", f"El sistema se cerrara para guardar los cambios")
        raise SystemExit()

    def interface_ask_security_question(self) -> None:
        """
        Inicializa una instancia de la clase Login y crea la ventana principal de la interfaz.

        Returns:
            None
        """
        questions = open("./Public/txt/questions.txt", encoding='utf-8')
        questions = [question for question in questions if question != ""]

        # Crea la ventana principal
        self.window = Toplevel()
        self.__load_data__()
        # Se elimina la funcionalidad del boton de cerrar
        self.window.protocol(
            "WM_DELETE_WINDOW", lambda: self.__tools__.desconectar(self.window))

        # Establece el tamaño de la ventana y su titulo
        self.window.title(
            f"Pregunta se seguridad")

        # Establece que la ventana no sea redimensionable
        self.window.resizable(False, False)

        label = Label(
            self.window, text=questions[randint(0, len(questions)-1)], font=self.font_tittle_system)
        label.grid(row=0, column=0)

        frame = Frame(
            self.window)
        frame.grid(row=1, column=0, padx=5, pady=5)

        # Crea el campo de entrada de texto para la contraseña
        self.entry_read_answer = Entry(
            frame, show="*", justify="center", font=self.font_subtittle_system, width=30)
        self.entry_read_answer.grid(row=0, column=0, padx=5, pady=5)

        visible_password = BooleanVar(value=False)
        boton_hide_view_password = Button(
            frame, image=self.hide_password_icon, command=lambda: self.__tools__.visible_password(
                boton_hide_view_password, self.entry_read_answer, visible_password, self.show_password_icon, self.hide_password_icon))
        boton_hide_view_password.grid(
            column=1, row=0, padx=5, pady=5)

        frame_xd = Frame(self.window)
        frame_xd.grid(row=2, column=0)

        # Crea el boton para ingresar los datos del usuario y llama al metodo get_data del controlador para procesar los datos
        self.boton_entrar = Button(
            frame_xd, text='Ingresar', command=self.read_security_question, anchor="center", width=10, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        self.boton_entrar.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        self.boton = Button(
            frame_xd, text='Cancelar', command=lambda: self.__tools__.desconectar(self.window), anchor="center", width=10, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        self.boton.grid(row=0, column=1, padx=5, pady=5, sticky=W)

        self.entry_read_answer.focus()

        # Inicia el loop principal de la ventana
        self.window.mainloop()

    def read_security_question(self) -> None:
        """
        Lee la respuesta de seguridad ingresada por el usuario y realiza validaciones.

        Raises:
            AuthError: Se genera si la respuesta ingresada no coincide con la respuesta almacenada.
            Exception: Se genera para manejar otros posibles errores.

        Returns:
            None
        """
        try:
            self.validate(self.entry_read_answer)

            cc = ConfigController()
            a = cc.get_config(
                "general", "configuracion_sistema", "security", "a")
            p = cc.get_config(
                "general", "configuracion_sistema", "security", "p")

            self.state = False

            if self.entry_read_answer.get() != self.__tools__.descifrar_AES(a, bytes.fromhex(p)):
                self.success = False
                raise AuthError("Respuesta incorrecta")

            self.success = True
            self.__tools__.desconectar(self.window)

        except AuthError as e:
            self.__tools__.desconectar(self.window)
            mb.showerror("Error", e)

        except Exception as e:
            mb.showerror("Error", e)

    def validate(self, entry: Entry) -> None:
        """
        Valida que un campo de entrada no este vacio.

        Args:
            entry (Entry): Campo de entrada a validar.

        Raises:
            WithoutParameter: Se genera si el campo de entrada está vacio.

        Returns:
            None
        """
        if entry.get() == "":
            raise WithoutParameter("Respuesta de seguridad")


def ask_security_question(main_window: Toplevel, check_conection:bool=True)->bool:
    # Obtenemos los datos del Cajero en Turno

    if check_conection:
        user = Operacion().CajeroenTurno()[0][1]
        if user is None:
            mb.showwarning("Alerta", "No se ha iniciado sesion en el sistema, no es posible continuar, reinicie el sistema e inicie sesion para     continuar, en caso de considerar que se trate de un error, contacte inmediatamente con un administrador inmediatamente.")
            return False

    __secure_instance__ = Secure()
    __instance_tools__ = Tools()
    __instance_tools__.desactivar(main_window)
    __secure_instance__.interface_ask_security_question()
    __instance_tools__.activar(main_window)

    return __secure_instance__.success

