from tkinter import Toplevel, messagebox as mb
from tkinter import Variable, StringVar, IntVar
from tkinter import Frame, LabelFrame, Button, Label, Entry, Listbox
from tkinter import W


from Controllers.ConfigController import ConfigController
from Tools.Exceptions import WithoutParameter
from Tools.Tools import Tools


class AddEmail:
    def __init__(self, type_email: str, list_email: Variable, list_box: Listbox) -> None:
        self.type_email = type_email
        self.list_email = list_email
        self.list_box = list_box

        # Crea la ventana principal
        self.window_add_email = Toplevel()

        # Crea las variables para el email
        self.new_email = StringVar()

        # Establece que la ventana no sea redimensionable
        self.window_add_email.resizable(False, False)

        self.instance_tools = Tools()
        self.instance_config = ConfigController()
        
        self.load_data()
        self.interface()
    
    def load_data(self):
        
        # Informacion sobre el estacionamiento
        data_config = self.instance_config.get_config(
            "general", "informacion_estacionamiento")
        self.nombre_estacionamiento = data_config["nombre_estacionamiento"]   

        data_config = self.instance_config.get_config(
            "general", "configuracion_sistema")

        # Configuracion de fuentes y estilos
        self.fuente_sistema = data_config["fuente"]
        self.size_text_font = data_config["size_text_font"]

        self.size_text_font_tittle_system = data_config["size_text_font_tittle_system"]

        self.font_new_email_window = (
            self.fuente_sistema, self.size_text_font+3)
        self.font_new_email_title_window = (
            self.fuente_sistema, self.size_text_font_tittle_system+3, 'bold')

        # Configuracion de colores
        self.button_color = data_config["color_botones_interface"]
        self.button_letters_color = data_config["color_letra_botones_interface"]
        
        data_config = None

    def interface(self):
        # Se elimina la funcionalidad del boton de cerrar
        self.window_add_email.protocol(
            "WM_DELETE_WINDOW", self.exit_add_email)

        # Establece el tamaño de la ventana y su titulo
        self.window_add_email.title(
            f"Agregar {self.type_email.replace('_', ' de ')} -> {self.nombre_estacionamiento}")

        # Establece que la ventana no sea redimensionable
        self.window_add_email.resizable(False, False)

        # Crea un frame para el formulario
        seccion_formulario = LabelFrame(
            self.window_add_email)
        seccion_formulario.grid(row=0, column=0, padx=5, pady=5)

        label = Label(
            seccion_formulario, text="Agregar email", font=self.font_new_email_title_window)
        label.grid(
            column=0, row=0, padx=3, pady=3)

        frame = Frame(seccion_formulario)
        frame.grid(row=1, column=0, padx=5, pady=5)

        # Crea la etiqueta para el campo de entrada de texto del nombre de usuario
        etiqueta_user = Label(
            frame, text='Nuevo email', font=self.font_new_email_window)
        etiqueta_user.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        # Crea el campo de entrada de texto para el nombre de usuario
        self.entry_email = Entry(
            frame, width=40, textvariable=self.new_email, font=self.font_new_email_window)
        self.entry_email.grid(row=0, column=1, padx=5, pady=5)

        frame = Frame(seccion_formulario)
        frame.grid(row=2, column=0)

        # Crea el boton para ingresar los datos del usuario y llama al metodo get_data del controlador para procesar los datos
        boton_entrar = Button(
            frame, text='Agregar email', command=self.add_email, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_new_email_window)
        boton_entrar.grid(row=0, column=0, padx=5, pady=5)

        boton_cancelar = Button(
            frame, text='Cancelar', command=self.exit_add_email, anchor="center", background=self.button_color, fg=self.button_letters_color, font=self.font_new_email_window)
        boton_cancelar.grid(row=0, column=1, padx=5, pady=5)

        self.entry_email.focus()

        # Inicia el loop principal de la ventana
        self.window_add_email.mainloop()

    def add_email(self):

        try:
            email = self.new_email.get()

            if email == "":
                raise WithoutParameter(self.type_email.replace('_', ' de '))

            self.instance_tools.validate_email(
                email, self.entry_email, self.type_email.replace('_', ' de '))

            data_list_email = [
                email] + self.instance_config.get_config("general", "configuiracion_envio", self.type_email)

            if data_list_email.count(email) > 1:
                raise SystemError(
                    f"El correo [{email}] ya esta registrado en la lista de {self.type_email.replace('_', ' de ')}")

            self.instance_config.set_config(
                "general", "configuiracion_envio", self.type_email, new_value=data_list_email)
            self.list_email.set(data_list_email)

            if mb.askyesno("Alerta", "El correo fue agregado exitosamente.\n¿desea agregar un nuevo correo?"):
                self.entry_email.focus()
            else:
                self.exit_add_email()

        except Exception as e:
            mb.showerror("Error", e)
        finally:
            self.new_email.set("")
   
    def exit_add_email(self):
        self.instance_tools.desconectar(self.window_add_email)


