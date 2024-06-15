import random
import qrcode
from PIL import ImageTk, Image
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from tkinter import Toplevel, ttk, filedialog, messagebox as mb
from tkinter.colorchooser import askcolor
from tkinter import StringVar, BooleanVar, Variable
from tkinter import Label, Entry
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageTk
import re
import math
from subprocess import run, PIPE, CalledProcessError
from os import path, remove, listdir
from requests import get
from requests.exceptions import RequestException
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import qrcode

from Controllers.ConfigController import ConfigController
from .Exceptions import ValidateDataError, WithoutParameter, AuthError


class Tools:
    """
    Esta clase proporciona diversas herramientas y utilidades útiles para la gestion de dispositivos, manipulacion de datos, generacion de codigos QR, cálculos relacionados con pensiones, y más.
    Algunos de los metodos clave incluyen la obtencion de informacion sobre dispositivos USB, cifrado/descifrado de números de folio, generacion de codigos QR, y cálculos de fechas limite y penalizaciones.

    Metodos:
        - get_device_ids: Obtiene los IDs de vendor y product de un dispositivo según su nombre.
        - get_device_name: Obtiene el nombre de un dispositivo según sus IDs de vendor y product.
        - get_devices_names_list: Obtiene una lista de nombres de dispositivos a partir de un diccionario.
        - get_usb_info: Obtiene informacion sobre dispositivos USB conectados en un sistema Linux.
        - text_to_hexanumber: Convierte un número hexadecimal representado como cadena de texto a un entero.
        - get_icon: Obtiene una imagen redimensionada como icono.
        - cifrar_folio: Cifra un número de folio utilizando una tabla de sustitucion numerica.
        - descifrar_folio: Descifra un número de folio cifrado utilizando una tabla de sustitucion numerica.
        - generar_QR: Genera un codigo QR a partir de la informacion dada y lo guarda en un archivo de imagen.
        - get_day_name: Obtiene el nombre de un dia de la semana a partir de su número.
        - nueva_vigencia: Obtiene la fecha del último dia del mes siguiente a la fecha dada.
        - calcular_penalizacion_diaria: Calcula la penalizacion diaria basada en la diferencia de dias entre la fecha limite y la fecha actual.
        - get_date_limit: Calcula la fecha limite a partir de una fecha de inicio y una cantidad de dias de Tolerancia.
        - calcular_pago_media_pension: Calcula el pago de media pension para un pensionado según el monto de la pension.
        - desconectar: Cierra la ventana principal y detiene el hilo en el que se ejecuta.
        - desactivar: Desactiva la interfaz.
        - activar: Activa la interfaz.
        - get_id_from_QR: Obtiene el número de tarjeta del pensionado a partir del texto QR.
        - obtener_datos_servidor: Realiza una consulta al servidor y devuelve los datos obtenidos.
    """

    def __init__(self) -> None:
        """
        Inicializa la clase Tools.
        """
        self.__instance_config__ = ConfigController()

        data_config = self.__instance_config__.get_config(
            "general", "informacion_estacionamiento")
        self.nombre_estacionamiento = data_config["nombre_estacionamiento"]

        self.date_format_system = "%Y-%m-%d %H:%M:%S"

        data_config = None

    def get_start_end_month(self, year_param: int, month_param: int) -> tuple:
        """
        Obtiene la fecha y hora de inicio y fin de un mes.

        :param year_param (int): El año para el cual se desea obtener el mes.
        :param month_param (int): El mes que se desea obtener (1-12).

        :return (tuple): Una tupla que contiene la fecha y hora de inicio y fin del mes.
                 El formato de las fechas es 'YYYY-MM-DD HH:MM:SS'.
        """

        # Obtener la fecha del primer dia del mes
        first_day = date(year_param, month_param, 1)
        first_day_str = first_day.strftime('%Y-%m-%d 00:00:00')

        # Obtener la fecha del último dia del mes siguiente restando un dia al primer dia del mes despues del seleccionado
        last_day = (first_day + relativedelta(months=1)) - \
            relativedelta(days=1)

        # Convertir la fecha en formato de cadena
        last_day_str = last_day.strftime('%Y-%m-%d 23:59:59')

        return first_day_str, last_day_str

    def get_device_ids(self, data_devices: dict, name_device: str) -> list:
        """
        Obtiene los IDs de vendor y product de un dispositivo según su nombre.

        Args:
            data_devices (dict): Diccionario con informacion de dispositivos.
            name_device (str): Nombre del dispositivo.

        Returns:
            list: Lista con los IDs de vendor y product [id_vendor, id_product].
        """
        for device in data_devices:
            if device == name_device:
                return data_devices[device]["id_vendor"], data_devices[device]["id_product"]

        return None

    def get_device_name(self, data_devices: dict, id_vendor: str, id_product: str) -> str:
        """
        Obtiene el nombre de un dispositivo según sus IDs de vendor y product.

        Args:
            data_devices (dict): Diccionario con informacion de dispositivos.
            id_vendor (str): ID de vendor del dispositivo.
            id_product (str): ID de product del dispositivo.

        Returns:
            str: Nombre del dispositivo.
        """
        for device in data_devices:
            if data_devices[device]["id_vendor"] == id_vendor and data_devices[device]["id_product"] == id_product:
                return device
        return None

    def get_devices_names_list(self, data_devices: dict) -> list:
        """
        Obtiene una lista de nombres de dispositivos a partir de un diccionario.

        Args:
            data_devices (dict): Diccionario con informacion de dispositivos.

        Returns:
            list: Lista de nombres de dispositivos.
        """
        return [device for device in data_devices]

    def get_usb_info(self) -> dict:
        """
        Obtiene informacion sobre dispositivos USB conectados en un sistema Linux.

        Returns:
            dict: Diccionario con informacion de dispositivos USB.
        """
        # Comando para listar dispositivos USB
        command = "lsusb"

        # Ejecutar el comando y capturar la salida
        result = run(command, shell=True, stdout=PIPE, stderr=PIPE, text=True)

        # Filtrar la salida para obtener solo los IDs de los dispositivos USB (excluir "root hub")
        usb_info_lines = [line.split() for line in result.stdout.split(
            '\n') if "root hub" not in line and len(line) > 0]

        # Crear un diccionario para almacenar la informacion
        usb_info_dict = {}

        # Procesar cada linea y extraer informacion
        for line in usb_info_lines:
            id_vendor, id_product = line[5].split(":")
            name = " ".join(line[6:])
            usb_info_dict[name] = {
                "id_vendor": id_vendor, "id_product": id_product}

        return usb_info_dict

    def text_to_hexanumber(self, number_text: str):
        """
        Convierte un número hexadecimal representado como cadena de texto a un entero.

        Args:
            number_text (str): Número hexadecimal representado como cadena de texto.

        Returns:
            int: Número entero resultante de la conversion.
        """
        return int(number_text, 16)

    def get_icon(self, image: str, size: tuple = (50, 50)) -> ImageTk.PhotoImage:
        """
        Obtiene una imagen redimensionada como icono.

        Args:
            image (str): Ruta de la imagen.
            size (tuple): Tamaño del icono (por defecto, (50, 50)).

        Returns:
            ImageTk.PhotoImage: Objeto PhotoImage que representa el icono.
        """
        icon = Image.open(image)
        icon = icon.resize(size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(icon)

    def cifrar_folio(self, folio: int) -> str:
        """
        Cifra un número de folio utilizando una tabla de sustitucion numerica.

        Args:
            folio (int): Número de folio a cifrar.

        Returns:
            str: Número de folio cifrado.
        """

        # Convierte el número de folio en una cadena de texto.
        folio = str(folio)

        # Genera un número aleatorio de 5 digitos y lo convierte en una cadena de texto.
        num_random = random.randint(10000, 99999)
        numero_seguridad = str(num_random)

        # Concatena el número de seguridad al número de folio.
        folio = folio + numero_seguridad

        # Tabla de sustitucion numerica.
        tabla = {'0': '5', '1': '3', '2': '9', '3': '1', '4': '7',
                 '5': '0', '6': '8', '7': '4', '8': '6', '9': '2'}

        # Convierte el número de folio cifrado a una lista de digitos.
        digitos = list(folio)

        # Sustituye cada digito por el número correspondiente en la tabla de sustitucion.
        cifrado = [tabla[digito] for digito in digitos]

        # Convierte la lista cifrada de vuelta a una cadena de texto.
        cifrado = ''.join(cifrado)

        # Devuelve el número de folio cifrado.
        return cifrado

    def descifrar_folio(self, folio_cifrado: int) -> str:
        """
        Descifra un número de folio cifrado utilizando una tabla de sustitucion numerica.

        Args:
            folio_cifrado (int): Número de folio cifrado.

        Returns:
            str: Número de folio descifrado.
        """
        try:
            # Verifica si el número de folio es válido.
            if len(folio_cifrado) <= 5:
                raise ValueError(
                    "El folio no es válido, escanee nuevamente, si el error persiste contacte con un administrador.")

            # Verifica si el número de folio tiene caracteres inválidos.
            caracteres_invalidos = ['!', '@', '#', '$', '%', '^', '&', '*',
                                    '(', ')', '-', '_', '=', '+', '{', '}', '[', ']', '|', '\\', ':', ';', '<', '>', ',', '.', '/', '?']
            if any(caracter in folio_cifrado for caracter in caracteres_invalidos):
                raise TypeError("El folio no tiene un formato válido")

            # Tabla de sustitucion numerica.
            tabla = {'0': '5', '1': '3', '2': '9', '3': '1', '4': '7',
                     '5': '0', '6': '8', '7': '4', '8': '6', '9': '2'}

            # Convierte el número de folio cifrado a una lista de digitos.
            digitos_cifrados = list(folio_cifrado)

            # Crea una tabla de sustitucion inversa invirtiendo la tabla original.
            tabla_inversa = {valor: clave for clave, valor in tabla.items()}

            # Sustituye cada digito cifrado por el número correspondiente en la tabla de sustitucion inversa.
            descifrado = [tabla_inversa[digito] for digito in digitos_cifrados]

            # Convierte la lista descifrada de vuelta a una cadena de texto.
            descifrado = ''.join(descifrado)

            # Elimina los últimos 4 digitos, que corresponden al número aleatorio generado en la funcion cifrar_folio.
            descifrado = descifrado[:-5]

            # Retorna el folio descifrado.
            return descifrado

        # Maneja el error si el formato del número de folio es incorrecto.
        except TypeError as error:
            raise SystemError(
                f"El folio tiene un formato incorrecto, si el error persiste contacte a un administrador y muestre el siguiente error:\n\n\t{error}")

        # Maneja cualquier otro error que pueda ocurrir al descifrar el número de folio.
        except Exception as error:
            raise SystemError(
                f"Ha ocurrido un error al descifrar el folio, intente nuevamente, si el error persiste contacte a un administrador y muestre el siguiente error:\n\n\t{error}")

    def generar_QR(self, QR_info: str, path: str = "./Public/Img/reducida.png", zise=(320, 320)) -> str:
        """
        Genera un codigo QR a partir de la informacion dada y lo guarda en un archivo de imagen.

        Args:
            QR_info (str): La informacion para generar el codigo QR.
            path (str, optional): La ruta y el nombre del archivo de imagen donde se guardará el codigo QR, por defecto es "./Public/Img/reducida.png".

        Returns:
            str: Path de la imagen QR.
        """
        # Generar el codigo QR
        img = qrcode.make(QR_info)

        # Redimensionar el codigo QR a un tamaño especifico
        img = img.get_image().resize(zise)

        # Guardar la imagen redimensionada en un archivo
        img.save(path)

        return path

    def get_day_name(self, day_number: int) -> str:
        """
        Obtiene el nombre de un dia de la semana a partir de su número.

        Args:
            day_number (int): Número del dia de la semana (0 a 6).

        Returns:
            str: Nombre del dia de la semana.
        """
        days = ['Lunes', 'Martes', 'Miercoles',
                'Jueves', 'Viernes', 'Sabado', 'Domingo']
        return days[day_number]

    def nueva_vigencia(self, fecha, meses=1, cortesia=None) -> str:
        """
        Obtiene la fecha del último dia del mes siguiente a la fecha dada y la devuelve como una cadena de texto en el formato "%Y-%m-%d %H:%M:%S".

        Args:
            fecha (str or datetime): Fecha a partir de la cual se obtendrá la fecha del último dia del mes siguiente.
            meses (int): Número de meses a agregar (por defecto, 1).
            cortesia (str): Valor opcional para indicar cortesia (por defecto, None).

        Returns:
            str: Una cadena de texto en el formato "%Y-%m-%d %H:%M:%S" que representa la fecha del último dia del mes siguiente a la fecha dada.
        """

        nueva_vigencia = ''
        if fecha == None:
            # Obtener la fecha y hora actual en formato deseado
            fecha = datetime.strptime(
                datetime.today().strftime(self.date_format_system), self.date_format_system)

            fecha = fecha - relativedelta(months=1)

        # Convertir la fecha dada en un objeto datetime si es de tipo str
        elif isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d 23:59:59')

        if cortesia == "Si":
            nueva_vigencia = fecha + relativedelta(years=5)

        else:
            # Obtener la fecha del primer dia del siguiente mes
            mes_siguiente = fecha + relativedelta(months=meses, day=1)

            # Obtener la fecha del último dia del mes siguiente
            ultimo_dia_mes_siguiente = mes_siguiente + \
                relativedelta(day=31)
            if ultimo_dia_mes_siguiente.month != mes_siguiente.month:
                ultimo_dia_mes_siguiente -= relativedelta(days=1)

            nueva_vigencia = ultimo_dia_mes_siguiente

        # convertir la fecha en formato de cadena
        nueva_vigencia = nueva_vigencia.strftime('%Y-%m-%d 23:59:59')

        # Devolver el valor
        return nueva_vigencia

    def calcular_penalizacion_diaria(self, penalizacion_diaria: int, fecha_limite) -> tuple[int, int]:
        """
        Calcula la penalizacion diaria basada en la diferencia de dias entre la fecha limite y la fecha actual.

        Args:
            penalizacion_diaria (int): La cantidad de penalizacion por cada dia de atraso.
            fecha_limite (str or datetime): La fecha limite en formato self.date_format_system.

        Returns:
            tuple: Una tupla que contiene la penalizacion total a pagar por los dias de atraso y el número de dias atrasados.
        """

        # Obtener la fecha y hora actual en formato deseado
        hoy = datetime.strptime(
            datetime.now().strftime(self.date_format_system), self.date_format_system)

        # Convertir la fecha limite en un objeto datetime si es de tipo str
        if isinstance(fecha_limite, str):
            fecha_limite = datetime.strptime(
                fecha_limite, self.date_format_system)

        # Calcular la cantidad de dias de atraso
        fecha_atrasada = hoy - fecha_limite

        # print(f"fecha atrasada: {fecha_atrasada}")

        dias_atrasados = fecha_atrasada.days + 1  # Se suma 1 dia para corregir fecha
        # if dias_atrasados == 0:dias_atrasados = 1

        # Calcular la penalizacion total
        penalizacion = dias_atrasados * penalizacion_diaria

        return penalizacion, dias_atrasados

    def get_date_limit(self, date_start: datetime, Tolerance: int) -> datetime:
        """
        Calcula la fecha limite a partir de una fecha de inicio y una cantidad de dias de Tolerancia.

        Args:
            date_start (datetime): Fecha de inicio.
            Tolerance (int): Cantidad de dias laborables a agregar.

        Returns:
            datetime: Fecha limite despues de agregar la cantidad de dias laborables.
        """
        date_limit = date_start

        while Tolerance > 0:
            date_limit += timedelta(days=1)
            # Verifica si el dia no es fin de semana (lunes a viernes)
            if date_limit.weekday() < 5:
                Tolerance -= 1

        return date_limit

    def calcular_pago_media_pension(self, monto: int) -> int:
        """
        Calcula el pago de media pension para un pensionado según el monto de la pension.

        Args:
            monto (int): Monto de la pension.

        Returns:
            int: El pago de media pension.
        """
        mes_actual = date.today().month
        año_actual = date.today().year

        ultimo_dia_mes = date(año_actual, mes_actual, 1) + \
            relativedelta(day=31)
        dias_mes = ultimo_dia_mes.day

        dias_faltantes = dias_mes - date.today().day
        pago = math.ceil((monto / dias_mes) * dias_faltantes)

        return pago

    def desconectar(self, main_window: Toplevel) -> None:
        """
        Cierra la ventana y detiene el hilo en el que se ejecuta.

        Args:
            main_window (Toplevel): Ventana.
        """
        main_window.quit()
        main_window.destroy()

    def desactivar(self, main_window: Toplevel) -> None:
        """
        Oculta la ventana.

        Args:
            main_window (Toplevel): Ventana.
        """
        main_window.withdraw()  # oculta la ventana

    def activar(self, main_window: Toplevel) -> None:
        """
        Muestra la interface.

        Args:
            main_window (Toplevel): Ventana.
        """
        main_window.deiconify()

    def get_id_from_QR(self, qr_text: str) -> str:
        """
        Obtiene el número de tarjeta del pensionado a partir del texto QR.

        Args:
            qr_text (str): El texto QR que contiene la informacion necesaria.

        Returns:
            str: El número de tarjeta del pensionado.

        Example:
        >>> qr_text = "Pension-NombreEstacionamiento-12345"
        >>> id_numero = estacionamiento.get_id_from_QR(qr_text)
        >>> print(id_numero)
        "12345"
        """
        # La posicion del identificador es determinada por la longitud de la cadena f"Pension-{self.nombre_estacionamiento}-"
        position_id = len(f"Pension-{self.nombre_estacionamiento}-")

        # Retorna el número de tarjeta del pensionado
        return qr_text[position_id:]

    def visible_password(self, button: ttk.Button, entry_password: Entry, visible: BooleanVar, show_password_icon, hide_password_icon) -> None:
        """
        Cambia la visibilidad del campo de contraseña entre texto visible y asteriscos.

        Args:
            button (ttk.Button): El boton que activa/desactiva la visibilidad.
            entry_password (Entry): El campo de entrada de contraseña.
            visible (BooleanVar): Una variable booleana que indica si la contraseña es visible o no.
            show_password_icon: Icono que muestra que la contraseña es visible.
            hide_password_icon: Icono que muestra que la contraseña no es visible.

        Returns:
            None
        """
        visible.set(not visible.get())

        character_to_show = "" if visible.get() else "*"
        icon = show_password_icon if visible.get() else hide_password_icon

        entry_password.configure(show=character_to_show)
        button.configure(image=icon)

    def validate_entry_number(self, nuevo_valor) -> None:
        """
        Valida si un nuevo valor es un número entero.

        Args:
            nuevo_valor (any): El valor a validar.

        Returns:
            bool: True si el valor es un número entero, False de lo contrario.
        """
        try:
            return True if nuevo_valor == "" or nuevo_valor.isdigit() else False
        except ValueError:
            return False

    def check_and_save_change(changes: list, variable: Variable, current_value, description: str, old_value, new_value, save_function) -> None:
        """
        Verifica si hay un cambio en una variable y lo guarda junto con una descripcion.

        Args:
            changes (list): Lista de cambios.
            variable (Variable): La variable Tkinter a verificar.
            current_value: El valor actual de la variable.
            description (str): Una descripcion del cambio.
            old_value: El valor anterior.
            new_value: El valor nuevo.
            save_function: La funcion para guardar el cambio.

        Returns:
            None
        """
        if variable.get() != current_value:
            changes.append(f"{description}: {old_value} -> {new_value}")
            save_function()

    def validate_email(self, email: str, entry_email: Entry, what_email: str) -> None:
        """
        Valida si una cadena de texto es un correo electronico válido.

        Args:
            email (str): El correo electronico a validar.
            entry_email (Entry): El campo de entrada donde se ingreso el correo electronico.
            what_email (str): Una descripcion del proposito del correo electronico.
        Raises:
            ValidateDataError: Cando el correo no sea valido

        Returns:
            None
        """
        patron_correo = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(patron_correo, email) is None:
            entry_email.focus()
            raise ValidateDataError(
                f"Correo para {what_email} debe de tener un correo valido")

    def load_image(self, label_image: Label, variable: StringVar = None, path_image: str = None, scale_image: int = 2) -> bool:
        """
        Carga una imagen desde un archivo y la muestra en un widget Label.

        Args:
            label_image (Label): El widget Label donde se mostrará la imagen.
            variable (StringVar, optional): La variable Tkinter que contiene la ruta de la imagen.
            path_image (str, optional): La ruta de la imagen a cargar, or defecto es None, en este caso abrirá una ventana para seleccionar la imagen.
            scale_image (int, optional): El factor de escala para ajustar el tamaño de la imagen por defecto es 2.

        Returns:
            None
        """
        if path_image is None:
            path_image = filedialog.askopenfilename(
                title="Seleccionar archivo",
                filetypes=[("Todos los archivos", "*.*")])
            
            if path_image == '':
                return False
            self.replace_image(variable.get(), path_image)

            # Cargar la imagen con PIL
            image = Image.open(variable.get())
        else:
            image = Image.open(path_image)

        # Cambiar tamaño de la imagen
        image = image.resize(
            (image.width // scale_image, image.height // scale_image), Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(image)

        # Configurar la imagen en el Label
        label_image.configure(image=image)
        label_image.image = image

        return True
        

    def change_color(self, variable: StringVar, label_color: Label, label_name_color: Label, color: str = None) -> None:
        """
        Cambia el color de fondo de una etiqueta y actualiza las etiquetas con el color seleccionado.

        Args:
            variable (StringVar): Variable de cadena Tkinter que almacena el color seleccionado.
            label_color (Label): Etiqueta que muestra el color de fondo.
            label_name_color (Label): Etiqueta que muestra el nombre del color.
            color (str, optional): El color seleccionado. Si no se proporciona, se abre un cuadro de diálogo de seleccion de color.

        Returns:
            None
        """
        if color is None:
            # Selecciona un color mediante el cuadro de diálogo de seleccion de color
            color = askcolor(title="Selecciona un color")[1]
            if color is None:
                return

        # Actualiza la variable y las etiquetas con el color seleccionado
        variable.set(color)
        label_color.configure(bg=color)
        label_name_color.configure(text=color)

    def replace_image(self, image_old: str, image_new: str) -> None:
        """
        Reemplaza una imagen existente con otra imagen.

        Args:
            image_old (str): La ruta de la imagen a reemplazar.
            image_new (str): La ruta de la nueva imagen.

        Returns:
            None
        """
        try:
            _, ext = path.splitext(image_new)
            if ext.lower() not in [".png", ".jpeg", ".jpg"]:
                raise SystemError("Formato incorrecto de archivo, debe de ser una imagen")
            
            # Abrir la imagen base
            imagen_base = Image.open(image_old)

            # Abrir la nueva imagen que deseas agregar o reemplazar
            nueva_imagen = Image.open(image_new)

            # Ajustar la nueva imagen al tamaño de la imagen base
            nueva_imagen = nueva_imagen.resize(imagen_base.size)

            # Superponer la nueva imagen sobre la imagen base
            imagen_base.paste(nueva_imagen, (0, 0))

            # Guardar la imagen resultante
            imagen_base.save(image_old)
        
        except Exception as e:
            mb.showerror("Error", f"{e}")

    def cambiar_valor(self, variable_actual: BooleanVar, variable_contraria: BooleanVar, method) -> None:
        """
        Cambia el valor de una variable booleana y llama a una funcion dada.

        Args:
            variable_actual (BooleanVar): La variable booleana actual.
            variable_contraria (BooleanVar): La variable booleana contraria.
            method: La funcion que se debe llamar despues de cambiar el valor.

        Returns:
            None
        """

        if variable_actual.get():
            variable_actual.set(True)
            variable_contraria.set(False)
        else:
            variable_actual.set(False)
            variable_contraria.set(True)

        method()

    def check_internet_connection(self, url: str = "http://www.google.com", timeout: int = 10) -> bool:
        """
        Verifica si hay una conexion activa a Internet.

        Args:
            url (str, optional): La URL a la que se realizará la peticion. Por defecto es "http://www.google.com".
            timeout (int, optional): El tiempo máximo en segundos para esperar la respuesta. Por defecto es 10.

        Returns:
            bool: True si hay una conexion activa a Internet, False si no se puede establecer la conexion.
        """
        try:
            response = get(url, timeout=timeout)
            # Lanza una excepcion si la respuesta HTTP no es exitosa
            response.raise_for_status()
            print("Conexion a Internet activa.")
            return True

        except RequestException:
            print("No se pudo establecer conexion a Internet.")
            return False

    def is_file_empty(self, file_path) -> bool:
        """
        Verifica si un archivo está vacio.

        Args:
            file_path (str): La ruta del archivo que se va a verificar.

        Returns:
            bool: True si el archivo está vacio, False si no lo está.
        """
        try:
            # Obtiene el tamaño del archivo en bytes y verifica si es cero
            return True if path.getsize(file_path) == 0 else False

        except Exception as e:
            # Maneja cualquier error que pueda ocurrir
            print(f"Error al verificar el archivo: {e}")
            return False

    def remove_file(self, path_file: str) -> None:
        """
        Elimina un archivo del sistema.

        Args:
            path_file (str): La ruta del archivo que se va a eliminar.

        Returns:
            None
        """
        try:
            # Intenta eliminar el archivo
            remove(path_file)
            print(f"Archivo [{path_file}] fue eliminado exitosamente.")
        except Exception as e:
            # Maneja cualquier error que pueda ocurrir al intentar eliminar el archivo
            print(f"No se pudo eliminar el archivo [{path_file}]: {e}")

    def compress_to_zip(self, source: str, output_filename: str = None, is_dir: bool = False, rename: bool = True) -> None:
        """
        Comprime un archivo o directorio en un archivo ZIP.

        Args:
            source (str): Ruta al archivo o directorio que se comprimirá.
            output_filename (str): Nombre del archivo ZIP de salida. Si no se proporciona, se usará el nombre del archivo fuente con extension ".zip".
            is_dir (bool): Indica si el origen es un directorio. Por defecto es False.
            rename (bool): Indica si se deben renombrar los archivos en el archivo ZIP. Por defecto es True.

        Returns:
            str or None: Ruta absoluta del archivo ZIP si la compresion es exitosa, None si hay algún error.
        """
        try:
            # Si no se proporciona un nombre de archivo de salida, usamos el nombre del archivo fuente con extension ".zip"
            output_filename = output_filename or f"{source}.zip"

            if is_dir:
                position_number = len(
                    f"{self.nombre_estacionamiento}_Corte_N°_")
                files = listdir(source)
                for id, file in enumerate(files):
                    _, ext = path.splitext(file)
                    if ext.lower() != ".txt":
                        files.remove(file)

                if rename:
                    first_number = files[0][position_number:-4]
                    last_number = files[len(files)-1][position_number:-4]

                    numbers = f"Cortes {first_number} a {last_number}" if first_number != last_number else f"Corte {first_number}"
                    output_filename = f"{source[:-6]+numbers}.zip".replace(
                        " ", "_")

            with ZipFile(output_filename, 'w', ZIP_DEFLATED) as zipf:
                if is_dir:
                    for file in files:
                        file_path = path.join(source, file)
                        # Agregar archivos del directorio al ZIP con su ruta relativa
                        zipf.write(file_path, arcname=path.relpath(
                            file_path, source))
                else:
                    # Agregar archivo al ZIP con su nombre base
                    arcname = path.basename(source)
                    zipf.write(source, arcname)

            print("Archivo comprimido correctamente")
            return path.abspath(output_filename)

        except Exception as e:
            print(f'Error al comprimir el archivo: {e}')
            return None

    def get_DB(self, backup_path: str = './public/db.sql') -> str:
        """
        Genera un respaldo de la base de datos utilizando el comando mysqldump.

        Args:
            backup_path (str, optional): La ruta donde se guardará el archivo de respaldo. Por defecto es './public/db.sql'.

        Returns:
            str or None: La ruta del archivo de respaldo si se crea exitosamente, None si ocurre un error.
        """
        try:
            # Configuracion de la base de datos
            dataconfig = self.__instance_config__.get_config(
                "funcionamiento_interno", "db")
            host = dataconfig["host"]
            user = dataconfig["usuario"]
            __password__ = dataconfig["password"]
            __iv__ = dataconfig["iv"]
            database = dataconfig["db"]

            # Comando mysqldump (dependiendo del sistema operativo)
            command = f"mysqldump -h {host} -u {user} -p{self.descifrar_AES(__password__, bytes.fromhex(__iv__))} {database} > {backup_path}"
            # command = f"cd C:/xampp/mysql/bin && mysqldump -h {host} -u {user} -p{self.descifrar_AES(__password__, bytes.fromhex(__iv__))} {database} > {backup_path}"

            run(command, shell=True)

            if path.exists(backup_path) and not self.is_file_empty(backup_path):
                print("Base de datos respaldada exitosamente.")
                backup_path = path.abspath(backup_path)
                return backup_path
            else:
                print("El archivo de respaldo no se creo correctamente.")
                self.remove_file(backup_path)
                return None

        except CalledProcessError:
            print("Error al crear el respaldo.")
            return None

    def cifrar_AES(self, texto_plano: str) -> tuple[str, bytes]:
        """
        Cifra el texto plano utilizando el algoritmo AES en modo CBC.

        Args:
            texto_plano (str): Texto plano a cifrar.

        Returns:
            tuple: Una tupla con dos elementos:
                texto_cifrado (str): Texto cifrado en Base64.
                iv (bytes): Vector de inicializacion utilizado en el cifrado.
        """
        __clave__: str = "PASE"
        try:
            # Convertir la clave en una clave de 32 caracteres
            clave_hash = hashlib.sha256(__clave__.encode()).digest()

            # Crear un objeto de cifrado AES
            cipher = AES.new(clave_hash, AES.MODE_CBC)

            # Cifrar el texto plano y convertirlo en una cadena de bytes
            texto_cifrado_bytes = cipher.encrypt(
                pad(texto_plano.encode(), AES.block_size))

            # Codificar la cadena de bytes en Base64
            texto_cifrado = base64.b64encode(texto_cifrado_bytes).decode()

            # Retornar el texto cifrado y el vector de inicializacion
            return texto_cifrado, cipher.iv

        except AttributeError:
            mb.showerror(
                "Error", "La informacion a codificar debe ser un string")
        except Exception as e:
            print(e)
            mb.showerror(
                "Error", f"Error al encriptar, intente nuevamente, si el error persiste contacte a un adminsitrador y muestre el siguiente mensaje de error:\n{e}.")

    def descifrar_AES(self, texto_cifrado: str, iv: bytes) -> str:
        """
        Descifra el texto cifrado utilizando el algoritmo AES en modo CBC.

        Args:
            texto_cifrado (str): Texto cifrado en Base64 a descifrar.
            iv (bytes): Vector de inicializacion utilizado en el cifrado.

        Returns:
            str: Texto descifrado.
        """
        __clave__: str = "PASE"
        try:
            # Convertir la clave en una clave de 32 caracteres
            clave_hash = hashlib.sha256(__clave__.encode()).digest()

            # Decodificar el texto cifrado de Base64
            texto_cifrado_bytes = base64.b64decode(texto_cifrado)

            # Convertir el vector de inicializacion a una cadena de texto en formato hexadecimal
            iv_hex = iv.hex()

            # Convertir la cadena de texto hexadecimal en bytes
            iv_bytes = bytes.fromhex(iv_hex)

            # Crear un objeto de descifrado AES
            cipher = AES.new(clave_hash, AES.MODE_CBC, iv_bytes)

            # Descifrar el texto cifrado y eliminar el relleno
            texto_descifrado_bytes = cipher.decrypt(texto_cifrado_bytes)
            texto_descifrado = unpad(
                texto_descifrado_bytes, AES.block_size).decode()

            # Retornar el texto descifrado
            return texto_descifrado

        except Exception as e:
            print(e)
            mb.showerror(
                "Error", f"Error al desencriptar, intente nuevamente, si el error persiste contacte a un adminsitrador y muestre el siguiente mensaje de error:\n{e}.")
            return None



class BlinkingLabel:
    """
    Clase para manejar el parpadeo de etiquetas.

    Attributes:
        color_alert (str): El color de alerta que se alternará durante el parpadeo.

    Methods:
        toggle_color: Alterna entre el color de fondo original y el color de alerta en el Label.
        start_blinking: Inicia el parpadeo del Label.
        stop_blinking: Detiene el parpadeo del Label y restaura el color de fondo original.
    """

    def __init__(self, color_alert: str) -> None:
        """
        Inicializa una nueva instancia de la clase BlinkingLabel.

        Args:
            color_alert (str): El color de alerta que se alternará durante el parpadeo.
        """
        self.label = None
        self._original_bg = None
        self._blink_id = None
        self.color_alert = color_alert

    def toggle_color(self) -> None:
        """
        Alterna entre el color de fondo original y el color de alerta en el Label.

        Returns:
            None
        """
        if self.label.cget("bg") == self.color_alert:
            self.label.config(bg=self._original_bg)
        else:
            self.label.config(bg=self.color_alert)
        # Configura el siguiente parpadeo
        self._blink_id = self.label.after(
            self.blink_interval, self.toggle_color)

    def start_blinking(self, label: Label, interval_ms: int) -> None:
        """
        Inicia el parpadeo del Label.
        Args:
            label (Label): El widget Label al que se aplicará el parpadeo.
            interval_ms (int): El intervalo de tiempo en milisegundos para el parpadeo.
        Returns:
            None
        """
        self.stop_blinking()
        self.label = label

        self._original_bg = self.label.cget("bg")
        self._blink_id = None
        self.blink_interval = interval_ms

        self.toggle_color()

    def stop_blinking(self) -> None:
        """
        Detiene el parpadeo del Label y restaura el color de fondo original.

        Returns:
            None
        """
        if self.label is not None:
            self.label.config(bg=self._original_bg)

        if self._blink_id is not None:
            # Cancela el proximo parpadeo si está programado
            self.label.after_cancel(self._blink_id)
            self._original_bg = None
            self._blink_id = None
            print("se detiene parpadeo")
