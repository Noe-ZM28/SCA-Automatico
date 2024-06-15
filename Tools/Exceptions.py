class WithoutParameter(Exception):
    """
    Clase de excepcion para manejar casos en los que falta un parámetro.

    Args:
        missing_parameter (str): El nombre del parámetro que falta.
    """

    def __init__(self, missing_parameter: str):
        """
        Inicia una nueva instancia de la excepcion WithoutParameter.

        Parámetros:
            missing_parameter (str): El nombre del parámetro que falta.
        """
        self.message = f"Ingrese: {missing_parameter}"
        super().__init__(self.message)


class AlreadyExist(Exception):
    """
    Clase de excepcion para manejar casos en los que ya existe un elemento.

    Args:
        message (str): Mensaje detallado sobre la existencia del elemento.
    """

    def __init__(self, message: str):
        """
        Inicia una nueva instancia de la excepcion AlreadyExist.

        Parámetros:
            message (str): Mensaje detallado sobre la existencia del elemento.
        """
        self.message = message
        super().__init__(self.message)


class NotExist(Exception):
    """
    Clase de excepcion para manejar casos en los que un elemento no existe.

    Args:
        message (str): Mensaje detallado sobre la no existencia del elemento.
    """

    def __init__(self, message: str):
        """
        Inicia una nueva instancia de la excepcion NotExist.

        Parámetros:
            message (str): Mensaje detallado sobre la no existencia del elemento.
        """
        self.message = message
        super().__init__(self.message)


class SystemError(Exception):
    """
    Clase de excepcion para manejar errores generales del sistema.

    Args:
        message (str): Mensaje detallado sobre el error del sistema.
    """

    def __init__(self, message: str):
        """
        Inicia una nueva instancia de la excepcion SystemError.

        Parámetros:
            message (str): Mensaje detallado sobre el error del sistema.
        """
        self.message = message
        super().__init__(self.message)


class ValidateDataError(Exception):
    """
    Clase de excepcion para manejar errores al validar informacion.

    Args:
        message (str): Mensaje detallado sobre el error del sistema.
    """

    def __init__(self, error_message: str):
        """
        Inicia una nueva instancia de la excepcion SystemError.

        Parámetros:
            message (str): Mensaje detallado sobre el error del sistema.
        """
        self.message = f"El valor del parametro: {error_message}"
        super().__init__(self.message)

class AuthError(Exception):
    """
    Clase de excepcion para manejar errores al validar informacion.

    Args:
        message (str): Mensaje detallado sobre el error del sistema.
    """

    def __init__(self, error_message):
        """
        Inicia una nueva instancia de la excepcion SystemError.

        Parámetros:
            message (str): Mensaje detallado sobre el error del sistema.
        """
        self.message = f"{error_message}"
        super().__init__(self.message)
