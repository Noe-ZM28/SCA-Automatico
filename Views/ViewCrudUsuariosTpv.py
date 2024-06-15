from tkinter import Toplevel, ttk, messagebox as mb
from tkinter import StringVar
from tkinter import Frame, LabelFrame, Button, Label, Entry
from tkinter import W

from Models.Queries import Usuarios
from .ViewAgregarUsuarioTpv import View_agregar_usuarios
from .ViewModificarUsuarioTpv import View_modificar_usuarios
from Controllers.ConfigController import ConfigController
from Tools.Tools import Tools


class ViewCRUDUsuarios:
    """Clase para mostrar la ventana de administracion de usuarios."""

    def __init__(self):
        """Constructor de la clase. Inicializa la ventana y los atributos."""
        # Crear la ventana principal
        instance_config = ConfigController()
        self.panel_crud = Toplevel()
        self.instance_tools = Tools()

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

        size = (size_text_font+25, size_text_font+5)
        self.hide_password_icon = self.instance_tools.get_icon(
            data_config["imagenes"]["hide_password_icon"], size)
        self.show_password_icon = self.instance_tools.get_icon(
            data_config["imagenes"]["show_password_icon"], size)
        data_config = None

        self.panel_crud.protocol(
            "WM_DELETE_WINDOW", lambda: self.instance_tools.desconectar(self.panel_crud))
        self.panel_crud.title(
            f"Administracion de usuarios -> {instance_config.get_config('general', 'informacion_estacionamiento', 'nombre_estacionamiento')}")
        self.panel_crud.columnconfigure(0, weight=1)

        self.ID_usuario = StringVar()
        self.registros = None
        self.controlador_crud_usuarios = Usuarios()
        self.interface()

        self.panel_crud.mainloop()

    def interface(self):
        """Crea la interfaz gráfica de la ventana."""
        # Crear un Label Frame principal para la seccion superior
        seccion_superior = LabelFrame(self.panel_crud, text='')
        seccion_superior.columnconfigure(1, weight=1)
        seccion_superior.propagate(True)
        seccion_superior.grid(row=0, column=0)

        # Seccion de bienvenida
        seccion_admin_usuarios = Frame(
            seccion_superior)
        seccion_admin_usuarios.grid(row=0, column=1)

        seccion_botones_admin_usuarios = Frame(
            seccion_admin_usuarios)
        seccion_botones_admin_usuarios.grid(row=0, column=1)

        # Boton para agregar usuario
        boton_agregar_usuario = Button(
            seccion_botones_admin_usuarios, text='Agregar usuario', command=lambda: [View_agregar_usuarios(), self.ver_usuarios()], background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_agregar_usuario.grid(row=0, column=0, padx=5, pady=5)

        # Campo de entrada para el ID del usuario
        etiqueta_user = Label(
            seccion_botones_admin_usuarios, text='Ingresa el ID del usuario: ', font=self.font)
        etiqueta_user.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        self.campo_user = Entry(
            seccion_botones_admin_usuarios, textvariable=self.ID_usuario, font=self.font)
        self.campo_user.grid(row=0, column=2, padx=5, pady=5)

        frame_botones = Frame(
            seccion_admin_usuarios)
        frame_botones.grid(row=0, column=3)

        # Boton para modificar usuario
        boton_modificar_usuario = Button(
            frame_botones, text='Modificar usuario', command=self.modificar_usuario, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_modificar_usuario.grid(row=0, column=0, padx=5, pady=5)

        # Boton para eliminar usuario
        boton_eliminar_usuario = Button(
            frame_botones, text='Eliminar usuario', command=self.eliminar_usuario, background=self.button_color, fg=self.button_letters_color, font=self.font_botones_interface)
        boton_eliminar_usuario.grid(row=1, column=0, padx=5, pady=5)

        # Tabla de usuarios
        self.seccion_tabla = LabelFrame(self.panel_crud)
        self.seccion_tabla.grid(row=1, column=0, sticky='NSEW', padx=5, pady=5)

        # Configuraciones de la tabla
        self.panel_crud.columnconfigure(0, weight=1)
        self.panel_crud.rowconfigure(2, weight=1)
        self.seccion_tabla.columnconfigure(0, weight=1)
        self.seccion_tabla.rowconfigure(0, weight=1)

        columnas = ['ID', 'Nombre de usuario', 'Nombre completo',
                    'Fecha Alta', 'Telefono', 'Telefono de Emergencia', 'Sucursal']

        # Crear un Treeview con una columna por cada campo de la tabla
        self.tabla = ttk.Treeview(self.seccion_tabla, columns=columnas)
        self.tabla.config(height=8)
        self.tabla.grid(row=0, column=0, sticky='NESW', padx=5, pady=5)

        # Define los encabezados de columna
        for i, headd in enumerate(columnas, start=1):
            self.tabla.heading(f'#{i}', text=headd)
            self.tabla.column(f'#{i}', width=100)

        self.tabla.column('#0', width=0, stretch=False)
        self.tabla.column('#1', width=25, stretch=False)
        self.tabla.column('#2', width=110, stretch=False)
        self.tabla.column('#3', width=210, stretch=False)
        self.tabla.column('#4', width=140, stretch=False)
        self.tabla.column('#5', width=100, stretch=False)
        self.tabla.column('#6', width=100, stretch=False)
        self.tabla.column('#7', width=120, stretch=False)

        # Crear un Scrollbar vertical y lo asocia con el Treeview
        scrollbar_Y = ttk.Scrollbar(
            self.seccion_tabla, orient='vertical', command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar_Y.set)
        scrollbar_Y.grid(row=0, column=1, sticky='NS')

        # Crear un Scrollbar horizontal y lo asocia con el Treeview
        scrollbar_X = ttk.Scrollbar(
            self.seccion_tabla, orient='horizontal', command=self.tabla.xview)
        self.tabla.configure(xscroll=scrollbar_X.set)
        scrollbar_X.grid(row=1, column=0, sticky='EW')

        self.tabla.grid(row=0, column=0, sticky='NESW', padx=5,
                        pady=5, ipadx=5, ipady=5, columnspan=2, rowspan=2)

        self.seccion_tabla.grid_rowconfigure(0, weight=1, minsize=0)

        self.campo_user.focus()
        self.ver_usuarios()

    def llenar_tabla(self, registros):
        """
        Llena la tabla con los registros que cumplen con los criterios de búsqueda.

        Args:
            registros (list): Un conjunto de tuplas que representan los registros obtenidos de la base de datos.
        """
        # Limpia la tabla antes de llenarla con nuevos registros
        self.vaciar_tabla()

        if self.registros:
            for registro in registros:
                self.tabla.insert('', 'end', values=registro)

    def vaciar_tabla(self):
        """Elimina todas las filas de la tabla."""
        self.tabla.delete(*self.tabla.get_children())

    def consultar_usuario(self, id):
        """
        Consulta un usuario en la base de datos.

        Args:
            id (int): El ID del usuario a consultar.

        Returns:
            bool: True si el usuario existe, False en caso contrario.
        """
        self.registros = self.controlador_crud_usuarios.consultar_usuario(
            id=id)
        if self.registros:
            return True
        else:
            return False

    def ver_usuarios(self):
        """Muestra todos los usuarios en la tabla."""
        self.registros = self.controlador_crud_usuarios.ver_usuarios()
        self.llenar_tabla(self.registros)
        self.campo_user.focus()

    def eliminar_usuario(self):
        """Elimina un usuario de la base de datos."""
        id = self.ID_usuario.get()

        if id == "":
            mb.showerror("Error", "Ingresa un ID")
            self.campo_user.focus()
            return None

        pregunta = mb.askokcancel(
            "Alerta", f"¿Estás seguro de eliminar al usuario con folio: {id}?")
        if pregunta:
            if self.consultar_usuario(id):
                self.controlador_crud_usuarios.eliminar_usuario(id)
                self.ver_usuarios()
                self.ID_usuario.set("")
                self.campo_user.focus()
            else:
                mb.showwarning(
                    "Error", f"No existe usuario con folio {id} o ya ha sido eliminado")
                self.ID_usuario.set("")
                self.ver_usuarios()
                self.campo_user.focus()
        else:
            self.ID_usuario.set("")
        self.campo_user.focus()

    def modificar_usuario(self):
        """Modifica un usuario en la base de datos."""
        id = self.ID_usuario.get()

        if id == "":
            mb.showerror("Error", "Ingresa un ID")
            self.campo_user.focus()
            return None

        if self.consultar_usuario(id) == False:
            mb.showwarning("Error", f"No existe usuario con folio {id}")
            self.ID_usuario.set("")
            self.ver_usuarios()
            self.campo_user.focus()
            return

        if mb.askokcancel(
                "Alerta", f"¿Estás seguro de modificar al usuario con folio: {id}?") == False:
            return

        usuario_informacion = self.controlador_crud_usuarios.consultar_usuario(
            id=id)
        View_modificar_usuarios(
            usuario_informacion=usuario_informacion, id=id)
        self.ver_usuarios()
        self.ID_usuario.set("")
        self.campo_user.focus()


if __name__ == '__main__':
    ViewCRUDUsuarios()
