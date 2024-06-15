import json
from tkinter import filedialog, messagebox as mb
from os import path
from datetime import datetime


class ConfigController:
    """
    ConfigController maneja la lectura, escritura y manipulacion de un archivo JSON que actúa como archivo de configuracion.

    El archivo JSON contiene informacion estructurada que puede incluir configuraciones generales, opciones del sistema,
    y detalles específicos de promociones. Este controlador proporciona metodos para acceder, modificar y gestionar
    dicha informacion de manera eficiente.


    Metodos:
        - get_config: Obtiene un valor de configuracion del archivo JSON.
        - set_config: Establece un valor de configuracion en el archivo JSON.
        - del_config: Elimina un elemento del archivo JSON de configuracion.
        - get_promo_list: Obtiene una lista de nombres de promociones filtrados por tipo y estado.
        - add_promo: Añade una nueva promocion al archivo JSON.
        - get_real_name_promo: Obtiene el nombre real de una promocion a partir de su nombre.
        - type_promo: Obtiene el tipo de lectura de una promocion a partir de su nombre.
    """

    def __init__(self):
        """
        Inicializa un objeto ConfigController.

        El archivo JSON especificado se utiliza como archivo de configuracion.
        """
        # Ruta al archivo de configuracion JSON
        self.__json_path__ = './Config/config.json'
        
    def get_config(self, *args: tuple):
        """
        Obtiene un valor de configuracion del archivo JSON.

        Args:
            *args (tuple): Una serie de claves para acceder al valor deseado en el JSON.

        Raises:
            FileNotFoundError: Si el archivo de configuracion no se encuentra.
            KeyError: Si no se encuentra la configuracion solicitada.
            Exception: Cualquier otra excepcion durante la lectura del archivo.

        Returns:
            current_data (any): El valor de configuracion obtenido del archivo JSON.

        Example:
        >>> print(ConfigController().get_config("general", "configuracion_sistema", "impresora", "idVendor"))
        >>> "04b8"
        """
        try:
            with open(self.__json_path__, encoding='utf-8') as f:
                data = dict(json.load(f))
 
                # Acceder a la informacion en funcion de los argumentos proporcionados
                current_data = data.copy()
                data = None
                for arg in args:
                    current_data = current_data[arg]

                return current_data

        except FileNotFoundError as e:
            raise FileNotFoundError("Archivo de configuracion no encontrado") from e

        except KeyError as e:
            raise KeyError("No se encontro la configuracion") from e

        except Exception as e:
            raise Exception(f"Error al obtener configuracion: {e}") from e

    def set_config(self, *args: tuple, new_value) -> None:
        """
        Establece un valor de configuracion en el archivo JSON.

        Args:
            *args (tuple): Una serie de claves para acceder al valor deseado en el JSON.
            new_value: El nuevo valor que se establecerá.

        Raises:
            FileNotFoundError: Si el archivo de configuracion no se encuentra.
            Exception: Cualquier otra excepcion durante la lectura o escritura del archivo.

        Returns:
            None


        Example:
        >>> ConfigController().set_config("general", "configuracion_sistema", "impresora", "idVendor", new_value = "04b8")
        """
        try:
            with open(self.__json_path__, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Acceder y actualizar la informacion en funcion de los argumentos proporcionados
            current_data = data
            for arg in args[:-1]:
                current_data = current_data[arg]
            current_data[args[-1]] = new_value

            # Guardar los cambios en el archivo
            with open(self.__json_path__, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except FileNotFoundError as e:
            raise FileNotFoundError("Archivo de configuracion no encontrado") from e
        except Exception as e:
            raise Exception(f"Error al guardar configuracion: {e}") from e

    def del_config(self, *args: tuple) -> None:
        """
        Elimina un elemento del archivo JSON de configuracion.

        Args:
            *args (tuple): Una serie de claves para acceder al elemento a eliminar.

        Raises:
            Exception: Cualquier excepcion durante la eliminacion del elemento.

        Returns:
            None

        Example:
            >>> ConfigController().del_config("promociones", "Oficina")
        """
        try:
            # Paso 1: Cargar el contenido actual del archivo JSON
            with open(self.__json_path__, encoding='utf-8') as f:
                data = json.load(f)

            # Acceder y actualizar la informacion en funcion de los argumentos proporcionados
            current_data = data
            for arg in args[:-1]:
                current_data = current_data[arg]

            # Eliminar el elemento
            del current_data[args[-1]]

            # Guardar la estructura de datos actualizada en el archivo JSON
            with open(self.__json_path__, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except FileNotFoundError as e:
            raise FileNotFoundError("Archivo de configuracion no encontrado") from e

        except KeyError as e:
            raise KeyError("No se encontro la configuracion") from e

        except Exception as e:
            raise Exception(f"Error al eliminar configuracion: {e}") from e

    def get_promo_list(self, type_promo: str = None, status: bool = True) -> list:
        """
        Obtiene una lista de nombres de promociones.

        Args:
            type_promo (str, optional): Tipo de promocion a filtrar (predeterminado es None).
            status (bool, optional): Estado de la promocion a filtrar (predeterminado es True).

        Returns:
            promo_names (list): Lista de nombres de promociones filtradas.
        """
        data = self.get_config("promociones")
        promo_names = []

        if type_promo is None:
            for promo in data:
                if data[promo]["tipo_lectura"] == "qr":
                    promo = data[promo]["real_name"]
                promo_names.append(promo)
            return promo_names

        for promo in data:
            if data[promo]["tipo_lectura"] == type_promo and data[promo]["estatus"] == status:
                promo_names.append(promo)

        return promo_names

    def add_promo(self, name_promo: str, data_promo: dict) -> None:
        """
        Añade una nueva promocion al archivo JSON.

        Args:
            name_promo (str): Nombre de la nueva promocion.
            data_promo (dict): Datos de la nueva promocion.

        Returns:
            None
        """
        try:
            # Intenta abrir el archivo de configuracion existente
            with open(self.__json_path__, "r", encoding='utf-8') as f:
                data = json.load(f)

            # Agrega la nueva promocion al diccionario de promociones
            data['promociones'][name_promo] = data_promo

            # Guarda el diccionario de promociones en el archivo JSON
            with open(self.__json_path__, "w", encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except FileNotFoundError as e:
            print(e)
            print('No se encuentra archivo de configuracion')

        except Exception as e:
            print(e)

    def get_real_name_promo(self, promo_name: str) -> str:
        """
        Obtiene el nombre real de una promocion a partir de su nombre.

        Args:
            promo_name (str): Nombre de la promocion.

        Returns:
            str: Nombre real de la promocion.
        """
        data = self.get_config("promociones")
        for promo in data:
            if data[promo]["real_name"] == promo_name:
                return promo

    def type_promo(self, promo_name: str) -> str:
        """
        Obtiene el tipo de lectura de una promocion a partir de su nombre.

        Args:
            promo_name (str): Nombre de la promocion.

        Returns:
            str: Tipo de lectura de la promocion.
        """
        data = self.get_config("promociones")
        for promo in data:
            if promo_name == promo:
                return data[promo]["tipo_lectura"]

            if promo_name == data[promo]["real_name"]:
                return data[promo]["tipo_lectura"]

    def replace_config_file(self) -> None:
        """
        Reemplaza el archivo de configuracion actual con otro seleccionado por el usuario.
        """
        try:
            # Solicitar al usuario que seleccione un archivo de configuracion
            path_file = filedialog.askopenfilename(
                title="Seleccionar archivo de configuracion",
                filetypes=[("Todos los archivos", "*.*")]
            )

            if path_file == "" or None:
                return
        
            _, ext = path.splitext(path_file)
            if ext.lower() != ".json":
                raise SystemError("Formato incorrecto de archivo, debe de ser .json")

            # Si el usuario cancela la seleccion, regresar
            if path_file == "":
                return

            # Cargar el archivo de configuracion seleccionado por el usuario
            with open(path_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Guardar los cambios en el archivo de configuracion
            with open(self.__json_path__, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            mb.showwarning(
                "Alerta", f"El sistema se cerrara para cargar el archivo de configuracion")
            raise SystemExit()

        except Exception as e:
            mb.showerror("Error", f"{e}")

    def backup_config_file(self, parking_name: str, system_to_load: str) -> None:
        """
        Realiza una copia de seguridad del archivo de configuracion actual.

        Args:
            parking_name (str): El nombre del estacionamiento.
            system_to_load (str): El tipo de sistema actual.
        """
        # Solicitar al usuario que seleccione la ruta para guardar la copia de seguridad
        path_file = filedialog.asksaveasfilename(
            title="Seleccionar ruta para guardar archivo de configuracion",
            initialfile=f'ConfigFile_{parking_name}_{system_to_load}_{datetime.now().strftime("%Y-%m-%d")}'.replace(" ", "_"),
            defaultextension="json",
            filetypes=[("Todos los archivos", "*.*")]
        )

        # Si el usuario cancela la seleccion, regresar
        if path_file == "" or None:
            return

        # Cargar el contenido del archivo de configuracion actual
        with open(self.__json_path__, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Guardar una copia de seguridad en la ruta seleccionada por el usuario
        with open(path_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        mb.showwarning(
            "Alerta", f"El archivo de configuracion del sistema fue guardado en la ubicacion indicada")

    def load_default_config_file(self) -> None:
        """
        Carga el archivo de configuracion por defecto del sistema.
        """
        try:
            path_file = './Config/default_config.json'

            # Cargar el archivo de configuracion seleccionado por el usuario
            with open(path_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Guardar los cambios en el archivo de configuracion
            with open(self.__json_path__, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            mb.showwarning(
                "Alerta", f"El sistema se cerrara para cargar el archivo de configuracion")

            raise SystemExit()

        except Exception as e:
            mb.showerror("Error inesperado, contacte inmediatamente con un administrador y muestre el siguiente mensaje de error: ", f"{e}")
