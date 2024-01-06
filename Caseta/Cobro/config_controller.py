import json


class ConfigController:
    def __init__(self):
        """
        Inicializa un objeto ConfigController.
        """
        # Ruta al archivo de configuración JSON
        self.__json_path = '../Configuracion/config.json'
        self.__json_path = r'Caseta\Configuracion\config.json'

    def get_config(self, *args: tuple):
        """
        Obtiene un valor de configuración del archivo JSON.

        :param args (tuple): Una serie de claves para acceder al valor deseado en el JSON.

        :raises FileNotFoundError: Si el archivo de configuración no se encuentra.
        :raises Exception: Cualquier otra excepción durante la lectura del archivo.

        :return:
            - current_data: El valor de configuración obtenido del archivo JSON.

        Ejemplo 1:
        >>> config_controller = ConfigController()
        >>> print(config_controller.get_config("funcionamiento_interno", "db", "usuario"))
        >>> "Jhon Doe"

        Ejemplo 2:
        >>> print(config_controller.get_config("general", "configuracion_sistema", "impresora", "idVendor"))
        >>> "0x04b8"
        """
        try:
            with open(self.__json_path, encoding='utf-8') as f:
                data = json.load(f)

                # Acceder a la información en función de los argumentos proporcionados
                current_data = data
                for arg in args:
                    current_data = current_data[arg]

                return current_data

        except FileNotFoundError:
            print('No se puede obtener configuracion')
            raise  # Re-raise la excepción para que sea manejada externamente
        except Exception as e:
            print(e)
            raise  # Re-raise la excepción para que sea manejada externamente

    def set_config(self, *args: tuple, new_value):
        """
        Establece un valor de configuración en el archivo JSON.

        :param args (tuple): Una serie de claves para acceder al valor deseado en el JSON.
        :param new_value: El nuevo valor que se establecerá.

        :raises FileNotFoundError: Si el archivo de configuración no se encuentra.
        :raises Exception: Cualquier otra excepción durante la lectura o escritura del archivo.

        :return: None


        Ejemplo 1:
        >>> config_controller = ConfigController()
        >>> config_controller.set_config("funcionamiento_interno", "db", "usuario", new_value="Jhon Doe"

        Ejemplo 2:
        >>> config_controller.set_config("general", "configuracion_sistema", "impresora", "idVendor = "0x04b8")
        """
        try:
            with open(self.__json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Acceder y actualizar la información en función de los argumentos proporcionados
            current_data = data
            for arg in args[:-1]:
                current_data = current_data[arg]
            current_data[args[-1]] = new_value

            # Guardar los cambios en el archivo
            with open(self.__json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except FileNotFoundError:
            print('No se puede guardar configuracion')
            raise  # Re-raise la excepción para que sea manejada externamente
        except Exception as e:
            print(e)
            raise  # Re-raise la excepción para que sea manejada externamente
