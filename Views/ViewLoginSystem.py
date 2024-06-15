from datetime import datetime
from tkinter import messagebox as mb
from tkinter import Tk, ttk, LabelFrame, Frame, StringVar, Label, Entry, Button, BooleanVar, NW

from Models.Model import Operacion
from .ViewCobro import ViewCobro
from .ViewLoginPanelConfig import View_Login
from Controllers.ConfigController import ConfigController
from Tools.Tools import Tools


class LoginSystem:
    def __init__(self):
        """
        Inicializa la ventana de inicio de sesion.
        """
        # Inicializacion de la ventana y configuracion de la pantalla completa
        self.root = Tk()
        self.model = Operacion()
        self.instance_config = ConfigController()
        self.instance_tools = Tools()
        self.get_data()
        self.interface()

    def get_data(self):
        data_config = self.instance_config.get_config("general")
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

    def interface(self):
        self.root.title("Registro Inicio de Turno")
        self.root.attributes('-fullscreen', True)
        self.fullscreen_state = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.quit_fullscreen)

        # Creacion del marco de la ventana
        self.login_frame = LabelFrame(
            self.root, text="Inicio de Turno", font=self.font_tittle_system)
        self.login_frame.pack(
            expand=True, padx=5, pady=5, anchor='center')

        # Definicion de variables de entrada
        self.username_var = StringVar()
        self.password_var = StringVar()
        self.shift_var = StringVar()

        frame_form = Frame(
            self.login_frame)
        frame_form.grid(
            column=0, row=0, padx=5, pady=5)

        # Entradas de texto y etiquetas
        label = Label(frame_form, text="Usuario",
                      font=self.font_subtittle_system)
        label.grid(column=0, row=0, padx=0, pady=5, sticky=NW)
        self.username_entry = Entry(frame_form, width=15, textvariable=self.username_var,
                                    font=self.font_subtittle_system, justify="center")
        self.username_entry.grid(column=1, row=0, padx=5, pady=5, sticky=NW)
        self.username_entry.focus()

        label = Label(
            frame_form, text="Contraseña", font=self.font_subtittle_system)
        label.grid(
            column=0, row=1, padx=0, pady=5, sticky=NW)

        frame = Frame(
            frame_form)
        frame.grid(
            column=1, row=1, padx=5, pady=0)

        self.password_entry = Entry(
            frame, width=10, textvariable=self.password_var, show="*", font=self.font_subtittle_system, justify='center')
        self.password_entry.grid(
            column=1, row=0, padx=5, pady=5, sticky=NW)

        visible_password_admin_pension = BooleanVar(value=False)
        boton_hide_view_password_admin_pension = Button(
            frame, image=self.hide_password_icon, command=lambda: self.instance_tools.visible_password(
                boton_hide_view_password_admin_pension, self.password_entry, visible_password_admin_pension, self.show_password_icon, self.hide_password_icon))
        boton_hide_view_password_admin_pension.grid(
            column=2, row=0, padx=5, pady=0)

        self.shift_entry = Entry(frame_form, width=15, textvariable=self.shift_var,
                                 font=self.font_subtittle_system, justify="center", validate='key', validatecommand=(self.root.register(self.instance_tools.validate_entry_number), '%P'))
        self.shift_entry.grid(column=1, row=2, padx=5, pady=5, sticky=NW)
        self.shift_label = Label(
            frame_form, text="Turno", font=self.font_subtittle_system)
        self.shift_label.grid(column=0, row=2, padx=0, pady=5, sticky=NW)

        frame_form = Frame(
            self.login_frame)
        frame_form.grid(
            column=0, row=1, padx=5, pady=5)

        # Botones de salir y entrar
        boton_config = ttk.Button(
            frame_form, image=self.config_icon, command=self.view_config_panel)
        boton_config.grid(column=0, row=0, padx=5, pady=5)

        self.login_button = Button(frame_form, text="Entrar", command=self.login, width=10,
                                   height=1, anchor="center", background="green", font=self.font_botones_interface)
        self.login_button.grid(column=1, row=0, padx=5, pady=5)

        self.exit_button = Button(frame_form, text="Salir", command=self.quit, width=10,
                                  height=1, anchor="center", background="red", font=self.font_botones_interface)
        self.exit_button.grid(column=2, row=0, padx=5, pady=5)

        self.root.mainloop()

    def view_config_panel(self):
        self.instance_tools.desactivar(self.root)
        View_Login(False)
        self.instance_tools.activar(self.root)

    def login(self):
        """
        Realiza la validacion del inicio de sesion.
        """
        username = self.username_var.get()
        password = self.password_var.get()
        shift = self.shift_var.get()

        # Validar que los campos no esten vacios
        if not username:
            mb.showwarning("IMPORTANTE", "Escriba su usuario")
            self.username_entry.focus()
            return

        if not password:
            mb.showwarning("IMPORTANTE", "Escriba su contraseña")
            self.password_entry.focus()
            return

        if not shift:
            mb.showwarning("IMPORTANTE", "Escriba su turno")
            self.shift_entry.focus()
            return

        user_info = self.model.ConsultaUsuario(username)

        if not user_info:
            mb.showwarning(
                "IMPORTANTE", "El usuario ingresado no existe, revise su informacion")
            self.username_var.set("")
            self.password_var.set("")
            self.shift_var.set("")
            self.username_entry.focus()
            return

        for info in user_info:
            user_id = str(info[0])
            user_password = str(info[1])
            name = str(info[2])

        if password != user_password:
            mb.showwarning(
                "IMPORTANTE", "La contraseña no coincide, vuelva a capturarla")
            self.password_var.set("")
            self.password_entry.focus()
            return

        start_time = datetime.today()
        user_data = (user_id, username, start_time, name, shift)
        self.model.ActualizaUsuario(user_data)
        self.quit()

        ViewCobro()

    def toggle_fullscreen(self, event):
        """Alternar entre pantalla completa"""

        self.fullscreen_state = not self.fullscreen_state
        self.root.attributes("-fullscreen", self.fullscreen_state)
        self.username_entry.focus()

    def quit_fullscreen(self, event):
        """Salir del modo pantalla completa."""

        self.fullscreen_state = False
        self.root.attributes("-fullscreen", self.fullscreen_state)

    def quit(self):
        """
        Cerrar la ventana.
        """
        self.root.destroy()
        print('Saliendo del sistema...')


if __name__ == '__main__':
    app = LoginSystem()
