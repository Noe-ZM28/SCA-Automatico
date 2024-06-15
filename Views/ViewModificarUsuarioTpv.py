from tkinter import messagebox as mb
import tkinter as tk

from Models.Queries import Usuarios
from Controllers.ConfigController import ConfigController
from Tools.Tools import Tools


class View_modificar_usuarios:
    """Clase para mostrar la ventana de modificacion de datos de un usuario."""

    def __init__(self, usuario_informacion=None, id=None):
        """
        Constructor de la clase. Inicializa la ventana y los atributos.

        Args:
            usuario_informacion (tuple): Tupla con la informacion del usuario a modificar.
            id (int): Identificador del usuario a modificar.

        Returns:
            None
        """
        self.query = Usuarios()
        self.instance_config = ConfigController()
        self.instance_tools = Tools()

        self.usuario_informacion = usuario_informacion
        self.id = id

        # Crear la ventana principal
        self.panel_crud = tk.Toplevel()

        data_config = self.instance_config.get_config("general")
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
            f"Modificar usuarios -> {self.instance_config.get_config('general', 'informacion_estacionamiento', 'nombre_estacionamiento')}")

        # Configura la columna principal del panel para que use todo el espacio disponible
        self.panel_crud.columnconfigure(0, weight=1)

        # Variables para almacenar los datos del usuario
        self.usuario_nombre = tk.StringVar()
        self.usuario_nombre_completo = tk.StringVar()
        self.usuario_contraseña = tk.StringVar()
        self.usuario_telefono = tk.StringVar()
        self.usuario_telefono_emergencia = tk.StringVar()
        self.usuario_sucursal = tk.StringVar()

        # Establecer los valores iniciales de las variables con los datos del usuario a modificar
        self.usuario_nombre.set(self.usuario_informacion[0][0])
        self.usuario_contraseña.set(self.usuario_informacion[0][1])
        self.usuario_nombre_completo.set(self.usuario_informacion[0][2])
        self.usuario_telefono.set(self.usuario_informacion[0][3])
        self.usuario_telefono_emergencia.set(self.usuario_informacion[0][4])
        self.usuario_sucursal.set(self.usuario_informacion[0][5])

        # Llama a la funcion interface() que configura la interfaz gráfica
        self.interface()

        self.panel_crud.resizable(False, False)

        # Inicia el loop principal de la ventana
        self.panel_crud.mainloop()

    def interface(self):
        """Crea la interfaz gráfica de la ventana de modificacion."""
        # Se crea un Label Frame principal para la seccion superior
        seccion_superior = tk.LabelFrame(self.panel_crud, text='')
        seccion_superior.columnconfigure(1, weight=1)
        seccion_superior.propagate(True)
        seccion_superior.grid(row=0, column=0, sticky=tk.NSEW)

        seccion_logo = tk.LabelFrame(seccion_superior, text='')
        seccion_logo.grid(row=0, column=0, padx=5, sticky=tk.W)

        # Se crea un Label Frame para la seccion de la conexion
        etiqueta_user = tk.Label(
            seccion_superior, text=f'Bienvenido', font=self.font_tittle_system)
        etiqueta_user.grid(row=0, column=1, padx=5, pady=5)

        seccion_datos_usuario = tk.LabelFrame(
            self.panel_crud, text="Ingresa los datos del usuario a registrar", font=self.font_tittle_system)
        seccion_datos_usuario.grid(row=1, column=0, padx=10, pady=10)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Nombre de usuario: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        self.campo_nombre_usuario = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_nombre, font=self.font)
        self.campo_nombre_usuario.grid(row=0, column=1, padx=5, pady=5)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Nombre completo: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_nombre_usuario = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_nombre_completo, font=self.font)
        campo_nombre_usuario.grid(row=1, column=1, padx=5, pady=5)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Contraseña: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_nombre_usuario = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_contraseña, font=self.font)
        campo_nombre_usuario.grid(row=2, column=1, padx=5, pady=5)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Telefono: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=4, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_nombre_usuario = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_telefono, font=self.font)
        campo_nombre_usuario.grid(row=4, column=1, padx=5, pady=5)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Telefono de emergencia: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=5, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_nombre_usuario = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_telefono_emergencia, font=self.font)
        campo_nombre_usuario.grid(row=5, column=1, padx=5, pady=5)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_nombre_usuario = tk.Label(
            seccion_datos_usuario, text='Sucursal: ', font=self.font)
        etiqueta_nombre_usuario.grid(
            row=6, column=0, padx=5, pady=5, sticky=tk.W)

        # Crea el campo de entrada de texto para el nombre de usuario
        campo_nombre_usuario = tk.Entry(
            seccion_datos_usuario, textvariable=self.usuario_sucursal, font=self.font)
        campo_nombre_usuario.grid(row=6, column=1, padx=5, pady=5)

        # Crea un boton y lo empaqueta en la seccion_botones_consulta
        boton_agregar_usuario = tk.Button(
            self.panel_crud, text='Modificar usuario', command=self.modificar_usuario, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_agregar_usuario.grid(row=2, column=0, padx=5, pady=5)

        # Establecer el foco en el campo de entrada de texto para el nombre de usuario
        self.campo_nombre_usuario.focus()

    def modificar_usuario(self):
        """Modifica los datos del usuario en la base de datos."""
        try:
            # Obtener los datos del formulario
            usuario_nombre = self.usuario_nombre.get()
            usuario_contraseña = self.usuario_contraseña.get()
            usuario_nombre_completo = self.usuario_nombre_completo.get()
            usuario_telefono = self.usuario_telefono.get()
            usuario_telefono_emergencia = self.usuario_telefono_emergencia.get()
            usuario_sucursal = self.usuario_sucursal.get()

            # Validar los datos del formulario
            if len(usuario_nombre) == 0 or len(usuario_contraseña) == 0 or len(usuario_nombre_completo) == 0 or len(usuario_telefono) == 0 or len(usuario_telefono_emergencia) == 0 or len(usuario_sucursal) == 0:
                raise IndexError("No dejar campos en blanco")

            # Actualizar los datos del usuario en la base de datos
            datos_usuario = [usuario_nombre, usuario_contraseña, usuario_nombre_completo,
                             usuario_telefono, usuario_telefono_emergencia, usuario_sucursal]
            self.query.actualizar_usuarios(datos_usuario, self.id)

            # Mostrar mensaje de exito y cerrar la ventana
            mb.showinfo("Informacion",
                        "El usuario fue modificado correctamente")
            self.instance_tools.desconectar(self.panel_crud)

        except Exception as e:
            mb.showerror("Error", e)
        except IndexError as e:
            mb.showerror("Error", e)
