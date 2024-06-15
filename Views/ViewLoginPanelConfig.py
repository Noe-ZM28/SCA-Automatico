import tkinter as tk
from tkinter import messagebox as mb
from datetime import datetime
from threading import Thread

from .ViewPanelConfig import View_Panel_Config
from Controllers.ConfigController import ConfigController
from Controllers.EmailController import SendData
from Tools.Tools import Tools
from Models.Model import Operacion

class View_Login:
    """Clase de la vista del login."""

    def __init__(self, comprobe_conection_db:bool = True):
        """Inicializa una instancia de la clase Login y crea la ventana principal de la interfaz."""
        # Crea la ventana principal
        self.window_login = tk.Toplevel()
        self.instance_config = ConfigController()
        self.instance_tools = Tools()
        self.send_data = SendData()
        self.comprobe_conection_db = comprobe_conection_db

        data_config = self.instance_config.get_config("general")
        self.button_color = data_config["configuracion_sistema"]["color_botones_interface"]
        self.button_letters_color = data_config["configuracion_sistema"]["color_letra_botones_interface"]
        self.fuente_sistema = data_config["configuracion_sistema"]["fuente"]
        size_text_font = data_config["configuracion_sistema"]["size_text_font"] + 15

        self.size_text_font_tittle_system = data_config[
            "configuracion_sistema"]["size_text_font_tittle_system"] + 10
        self.size_text_font_subtittle_system = data_config[
            "configuracion_sistema"]["size_text_font_subtittle_system"] + 10
        self.size_text_button_font = data_config[
            "configuracion_sistema"]["size_text_button_font"] + 10

        self.font_subtittle_system = (
            self.fuente_sistema, self.size_text_font_subtittle_system, 'bold')
        self.font_tittle_system = (
            self.fuente_sistema, self.size_text_font_tittle_system, 'bold')
        self.font_botones_interface = (
            self.fuente_sistema, self.size_text_button_font, 'bold')
        self.font = self.font_subtittle_system

        size = (size_text_font+20, size_text_font+5)
        self.hide_password_icon = self.instance_tools.get_icon(
            data_config["imagenes"]["hide_password_icon"], size)
        self.show_password_icon = self.instance_tools.get_icon(
            data_config["imagenes"]["show_password_icon"], size)
        data_config = None

        # Se elimina la funcionalidad del boton de cerrar
        self.window_login.protocol(
            "WM_DELETE_WINDOW", lambda: self.instance_tools.desconectar(self.window_login))

        # Establece el tamaño de la ventana y su titulo
        self.window_login.title(
            f"Login Panel de configuracion -> {self.instance_config.get_config('general', 'informacion_estacionamiento', 'nombre_estacionamiento')}")
        # Establece el tamaño máximo de la ventana para que ocupe toda la pantalla
        ancho_max = self.window_login.winfo_screenwidth()
        alto_max = self.window_login.winfo_screenheight()
        self.window_login.wm_maxsize(ancho_max, alto_max)

        # Establece la posicion inicial de la ventana en la pantalla
        pos_x = int(ancho_max/3)
        pos_y = int(alto_max/10)
        self.window_login.geometry(f"+{pos_x}+{pos_y}")
        
        self.success_access = None

        # Establece que la ventana no sea redimensionable
        self.window_login.resizable(False, False)

        # Crea las variables para los datos de usuario y tema
        self.user = tk.StringVar()
        self.password = tk.StringVar()

        # Llama al metodo "interface()" para construir la interfaz gráfica
        self.interface()

        # Inicia el loop principal de la ventana
        self.window_login.mainloop()

    def interface(self):
        """Define la interfaz gráfica de usuario."""
        # Crea un frame principal para la ventana
        self.seccion_principal = tk.LabelFrame(self.window_login)
        self.seccion_principal.grid(row=0, column=0, sticky=tk.NSEW)

        # Crea un frame para el formulario
        self.seccion_formulario = tk.LabelFrame(
            self.seccion_principal, text='Ingresa los siguientes datos', font=self.font_tittle_system)
        self.seccion_formulario.grid(row=0, column=0, sticky=tk.NSEW)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_user = tk.Label(
            self.seccion_formulario, text='Nombre de usuario', font=self.font)
        etiqueta_user.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_user = tk.Entry(
            self.seccion_formulario, textvariable=self.user, font=self.font, justify="center", width = 15)
        campo_user.grid(row=0, column=1, padx=5, pady=5)

        # Crea la etiqueta para el campo de entrada de texto de la contraseña
        etiqueta_password = tk.Label(
            self.seccion_formulario, text='Contraseña', font=self.font)
        etiqueta_password.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para la contraseña
        campo_password = tk.Entry(
            self.seccion_formulario, textvariable=self.password, show="*", font=self.font, justify="center", width = 15)
        campo_password.grid(row=1, column=1, padx=5, pady=5)

        visible_password = tk.BooleanVar(value=False)
        boton_hide_view_password = tk.Button(
            self.seccion_formulario, image=self.hide_password_icon, command=lambda: self.instance_tools.visible_password(
                boton_hide_view_password, campo_password, visible_password, self.show_password_icon, self.hide_password_icon))
        boton_hide_view_password.grid(
            column=2, row=1, padx=5, pady=5)

        frame = tk.Frame(self.seccion_principal)
        frame.grid(row=1, column=0)

        # Crea el boton para ingresar los datos del usuario y llama al metodo get_data del controlador para procesar los datos
        self.boton_entrar = tk.Button(
            frame, text='Entrar', command=self.view_panel, anchor="center", width=10, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        self.boton_entrar.grid(row=0, column=0, padx=5, pady=5)

        self.boton = tk.Button(
            frame, text='Cancelar', command=lambda: self.instance_tools.desconectar(self.window_login), anchor="center", width=10, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        self.boton.grid(row=0, column=1, padx=5, pady=5)

        campo_user.focus()

    def view_panel(self):
        self.get_data(user=self.user.get(), password=self.password.get())

    def get_data(self, user=None, password=None):
        """Obtiene los datos de usuario y contraseña ingresados y verifica si son correctos.

        Args:
            user (str): Nombre de usuario ingresado.
            password (str): Contraseña ingresada.
        """
        actual_user = "No es posible obtener usuario"
        if self.comprobe_conection_db:
            actual_user = Operacion().CajeroenTurno()[0][1]
            if actual_user is None:
                mb.showerror("Error", "No se puede continuar ya que no has iniciado sesion, reinicia el sistema e inicia sesion para poder continuar.\n\nSi consideras que se trata de un error ponte en contacto con un administrador inmediatamente")
                self.instance_tools.desconectar(self.window_login)
                return

        data = self.instance_config.get_config('funcionamiento_interno', 'panel_configuracion')
        hour = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if user != data['usuario'] or password != self.instance_tools.descifrar_AES(data['contraseña'], bytes.fromhex(data['iv'])):
            self.success_access = False
            mb.showerror(
                "Error", "La contraseña o el nombre de usuario es erroneo, intente nuevamente")
            self.password.set("")
            self.user.set("")
        else:
            self.success_access = True

        if self.success_access is not None:
            message = f'[{hour}]- El usuario [{actual_user}] {"accedio" if self.success_access else "intento acceder"} al panel de configuracion del sistema.'

            thread = Thread(target=lambda:self.send_data.send_system_notification(message))
            thread.start()

        if self.success_access:
            self.instance_tools.desactivar(self.window_login)
            View_Panel_Config()
            self.instance_tools.activar(self.window_login)
            self.instance_tools.desconectar(self.window_login)
        else:
            return


