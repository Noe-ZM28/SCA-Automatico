from tkinter import messagebox as mb, ttk
import tkinter as tk
from datetime import datetime

from Models.Queries import Usuarios
from Controllers.ConfigController import ConfigController
from Tools.Tools import Tools


class View_agregar_usuarios:
    """
    Clase para mostrar la ventana de agregar usuarios.
    """

    def __init__(self):
        """
        Constructor de la clase. Inicializa la ventana y los atributos.
        """
        self.query = Usuarios()
        self.panel_crud = tk.Toplevel()
        instance_config = ConfigController()
        self.instance_tools = Tools()

        self.panel_crud.protocol(
            "WM_DELETE_WINDOW", lambda: self.instance_tools.desconectar(self.panel_crud))
        self.panel_crud.title(
            f"Agregar usuarios -> {instance_config.get_config('general', 'informacion_estacionamiento', 'nombre_estacionamiento')}")
        self.panel_crud.columnconfigure(0, weight=1)

        data_config = instance_config.get_config("general")
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
        size = (size_text_font+20, size_text_font+5)
        self.hide_password_icon = self.instance_tools.get_icon(
            data_config["imagenes"]["hide_password_icon"], size)
        self.show_password_icon = self.instance_tools.get_icon(
            data_config["imagenes"]["show_password_icon"], size)
        data_config = None

        # Variables para almacenar datos de usuario
        self.usuario_nombre = tk.StringVar()
        self.usuario_nombre_completo = tk.StringVar()
        self.usuario_contraseña = tk.StringVar()
        self.usuario_telefono = tk.StringVar()
        self.usuario_telefono_emergencia = tk.StringVar()
        self.usuario_sucursal = tk.StringVar()

        self.registros = None
        self.interface()

        self.panel_crud.resizable(False, False)
        self.panel_crud.mainloop()

    def interface(self):
        """
        Crea la interfaz gráfica de la ventana.
        """
        seccion_superior = tk.LabelFrame(self.panel_crud, text='')
        seccion_superior.columnconfigure(1, weight=1)
        seccion_superior.propagate(True)
        seccion_superior.grid(row=0, column=0, sticky=tk.NSEW)

        etiqueta_user = tk.Label(
            seccion_superior, text=f'Bienvenido/a', font=self.font_tittle_system)
        etiqueta_user.grid(row=0, column=1, padx=5, pady=5)

        seccion_datos_usuario = tk.LabelFrame(
            self.panel_crud, text="Ingresa los datos del usuario a registrar", font=self.font_tittle_system)
        seccion_datos_usuario.grid(row=1, column=0, padx=10, pady=10)

        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Nombre de usuario: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.campo_nombre_usuario = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_nombre, font=self.font)
        self.campo_nombre_usuario.grid(row=0, column=1, padx=5, pady=5)

        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Nombre completo: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W)

        campo_nombre_usuario = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_nombre_completo, font=self.font)
        campo_nombre_usuario.grid(row=1, column=1, padx=5, pady=5)

        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Contraseña: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.W)

        campo_contraseña = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_contraseña, show="*", font=self.font)
        campo_contraseña.grid(row=2, column=1, padx=5, pady=5)

        visible_password = tk.BooleanVar(value=False)
        boton_hide_view_password = ttk.Button(
            seccion_datos_usuario, image=self.hide_password_icon, command=lambda: self.instance_tools.visible_password(
                boton_hide_view_password, campo_contraseña, visible_password, self.show_password_icon, self.hide_password_icon))
        boton_hide_view_password.grid(
            column=2, row=2, padx=5, pady=5)

        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Telefono: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=4, column=0, padx=5, pady=5, sticky=tk.W)

        campo_nombre_usuario = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_telefono, font=self.font)
        campo_nombre_usuario.grid(row=4, column=1, padx=5, pady=5)

        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Telefono de emergencia: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=5, column=0, padx=5, pady=5, sticky=tk.W)

        campo_nombre_usuario = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_telefono_emergencia, font=self.font)
        campo_nombre_usuario.grid(row=5, column=1, padx=5, pady=5)

        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Sucursal: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=6, column=0, padx=5, pady=5, sticky=tk.W)

        campo_nombre_usuario = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_sucursal, font=self.font)
        campo_nombre_usuario.grid(row=6, column=1, padx=5, pady=5)

        boton_agregar_usuario = tk.Button(
            self.panel_crud,  text='Agregar usuario', command=self.agregar_usuario, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_agregar_usuario.grid(row=2, column=0, padx=5, pady=5)

        self.campo_nombre_usuario.focus()

    def agregar_usuario(self):
        """
        Agrega un nuevo usuario a la base de datos con los datos proporcionados en la interfaz.
        """
        try:
            usuario_nombre = self.usuario_nombre.get()
            usuario_contraseña = self.usuario_contraseña.get()
            usuario_nombre_completo = self.usuario_nombre_completo.get()
            usuario_fecha_alta = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            usuario_telefono = self.usuario_telefono.get()
            usuario_telefono_emergencia = self.usuario_telefono_emergencia.get()
            usuario_sucursal = self.usuario_sucursal.get()

            if len(usuario_nombre) == 0 or len(usuario_contraseña) == 0 or len(usuario_nombre_completo) == 0 or len(usuario_fecha_alta) == 0 or len(usuario_telefono) == 0 or len(usuario_telefono_emergencia) == 0 or len(usuario_sucursal) == 0:
                raise IndexError("No dejar campos en blanco")

            datos_usuario = [usuario_nombre, usuario_contraseña, usuario_nombre_completo,
                             usuario_fecha_alta, usuario_telefono, usuario_telefono_emergencia, usuario_sucursal]

            self.query.agregar_usuarios(datos_usuario)

            self.instance_tools.desconectar(self.panel_crud)
        except Exception as e:
            mb.showerror("Error", e)
