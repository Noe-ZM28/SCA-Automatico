import re
from pymysql import err
from tkinter import messagebox
import traceback
from datetime import datetime
from Tools.Tools import Tools

from .Model import Operacion


class Usuarios(Operacion):
    """
    Clase para interactuar con la tabla de Usuarios en la base de datos.

    Proporciona metodos para agregar, consultar, ver, eliminar y actualizar usuarios en la tabla de Usuarios.

    Metodos:
        - execute_query: Ejecuta una consulta en la base de datos.
        - agregar_usuarios: Agrega un nuevo usuario a la base de datos.
        - consultar_usuario: Consulta un usuario por su identificador en la base de datos.
        - ver_usuarios: Obtiene y muestra todos los usuarios en la tabla.
        - eliminar_usuario: Elimina un usuario de la base de datos.
        - actualizar_usuarios: Actualiza los datos de un usuario existente en la base de datos.

    """

    def execute_query(self, query: str) -> list:
        """
        Ejecuta una consulta en la base de datos y devuelve los resultados.

        Args:
            query (str): La consulta SQL a ejecutar.

        Raises:
            pymysql.err.OperationalError: Si la conexion se pierde.
            pymysql.err.ProgrammingError: Si la tabla no existe.

        Returns:
            List: Una lista con los resultados de la consulta.
        """
        try:
            # Inicia la conexion con la base de datos
            connection = self.abrir()
            
            if connection is None: return

            # Crea un objeto cursor para ejecutar la consulta
            cursor = connection.cursor()

            # Se ejecuta la consulta
            cursor.execute(query)

            # Obtiene los resultados de la consulta
            result = cursor.fetchall()

            # Confirma los cambios en la base de datos
            connection.commit()

            # Cierra el cursor
            cursor.close()

            # Cierra la conexion cn la base de datos
            connection.close()

            # Retorna los resultados de la consulta
            return result

        except err.OperationalError as e:
            print(e)
            traceback.print_exc()
            if "10054" in str(e):
                print(e)
                messagebox.showwarning(
                    "Error", "Se ha perdido la conexion con la base de datos, reinicie reinicie el sistema\nEn caso de que el error persista contacte a un administrador.")

        except err.ProgrammingError as error:
            traceback.print_exc()
            print(error)
            # Aqui se ejecuta el codigo en caso de que se genere la excepcion ProgrammingError
            error_message = str(error)
            match = re.search(r"\((\d+),", error_message)
            error_number = int(match.group(1))
            if error_number == 1146:
                print(error)
                messagebox.showwarning(
                    "Error", f"Error: La tabla no existe.\n Es probable que la conexion actual no cuente con la tabla a la que intenta acceder, de ser caso contrario contacte con un administrador.")
                return None

        except Exception as e:
            print(e)
            traceback.print_exc()
            messagebox.showwarning(
                "Error", f"Error al realizar la consulta, por favor contacte con un administrador y muestre el siguiente error:\n Error: {str(e)} ")
            return None

    def agregar_usuarios(self, datos: tuple) -> None:
        """
        Agrega un nuevo usuario a la base de datos.

        Args:
            datos (tuple): Una tupla con los datos del nuevo usuario a agregar.

        Returns:
            None.
        """
        datos = tuple(datos)

        query = f"INSERT INTO Usuarios (Usuario, Contrasena, Nom_usuario, Fecha_alta, Telefono1, TelefonoEmer, Sucursal) VALUES {datos};"

        # Se ejecuta la consulta
        self.execute_query(query)

    def consultar_usuario(self, id) -> list:
        """
        Consulta un usuario por su identificador en la base de datos.

        Args:
            id (int): El identificador del usuario a consultar.

        Returns:
            List: Una lista con los datos del usuario consultado.
        """
        query = f"SELECT Usuario, Contrasena, Nom_usuario, Telefono1, TelefonoEmer, Sucursal FROM Usuarios WHERE Id_usuario = '{id}'"

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado

    def ver_usuarios(self) -> list:
        """
        Obtiene y muestra todos los usuarios en la tabla.

        Returns:
            List: Una lista con los datos de todos los usuarios.
        """

        query = f"SELECT Id_usuario, Usuario, Nom_usuario, Fecha_alta, Telefono1, TelefonoEmer, Sucursal FROM Usuarios"

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado

    def eliminar_usuario(self, id: int) -> None:
        """
        Elimina un usuario de la base de datos.

        Args:
            id (int): El identificador del usuario a eliminar.
        """

        query = f"DELETE FROM Usuarios WHERE Id_usuario = {id}"

        # Se ejecuta la consulta
        self.execute_query(query)

    def actualizar_usuarios(self, datos: tuple, id: int) -> None:
        """
        Actualiza los datos de un usuario existente en la base de datos.

        Args:
            datos (tuple): Una tupla con los nuevos datos del usuario a actualizar.
            id (int): El identificador del usuario a actualizar.
        """
        datos = tuple(datos)

        query = f"UPDATE Usuarios SET Usuario = '{datos[0]}', Contrasena = '{datos[1]}', Nom_usuario = '{datos[2]}',  Telefono1 = '{datos[3]}', TelefonoEmer = '{datos[4]}', Sucursal = '{datos[5]}' WHERE Id_usuario = '{id}';"

        # Se ejecuta la consulta
        self.execute_query(query)


class Pensionados(Usuarios):
    """
    Clase para interactuar con la tabla de Pensionados en la base de datos.

    Esta clase hereda de la clase Usuarios y proporciona metodos adicionales para agregar, consultar, visualizar,
    eliminar y actualizar informacion relacionada con pensionados en la tabla de Pensionados.

    Metodos:
        - agregar_pensionado: Agrega un nuevo pensionado a la base de datos.
        - consultar_pensionado: Consulta un pensionado por su número de tarjeta en la base de datos.
        - ver_pensionados: Obtiene y muestra todos los pensionados en la tabla.
        - eliminar_pensionado: Elimina un pensionado de la base de datos.
        - actualizar_pensionado: Actualiza los datos de un pensionado existente en la base de datos.
        - desactivar_tarjetas_expiradas: Desactiva las tarjetas de pensionados cuya vigencia ha expirado.
        - ver_tarjetas_expiradas: Obtiene y muestra todas las tarjetas de pensionados cuya vigencia ha expirado.
        - get_Entradas_Totales_Pensionados: Obtiene el total de entradas de pensionados para un folio dado.
        - get_Salidas_Pensionados: Obtiene el total de salidas de pensionados para un corte dado.
        - get_Quedados_Pensionados: Obtiene el total de pensionados que aún permanecen dentro del estacionamiento.
        - Actualizar_Entradas_Pension: Actualiza el campo 'Corte' para las entradas de pensionados en un corte especifico.
        - get_Anteriores_Pensionados: Obtiene la cantidad de pensionados que permanecieron dentro del estacionamiento en cortes anteriores.
        - get_QR_id: Obtiene un nuevo identificador para la generacion de codigos QR para pensionados.
    """

    def agregar_pensionados(self, datos: tuple) -> None:
        """
        Agrega un nuevo pensionado a la base de datos.

        Args:
            datos (tuple): Una tupla con los datos del nuevo pensionado a agregar.

        Esta funcion agrega un nuevo pensionado a la base de datos con los datos proporcionados.
        """
        datos = tuple(datos)

        query = f"INSERT INTO Pensionados (Num_tarjeta, Nom_cliente, Apell1_cliente, Apell2_cliente, Fecha_alta, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Monto, Cortesia, Tolerancia, Vigencia) VALUES {datos};"

        # Se ejecuta la consulta
        self.execute_query(query)

    def consultar_pensionado(self, Num_tarjeta: int) -> list:
        """
        Consulta un pensionado por su número de tarjeta en la base de datos.

        Args:
            Num_tarjeta (int): El número de tarjeta del pensionado a consultar.

        Returns:
            list: Una lista con los datos del pensionado consultado.
        """
        query = f"SELECT Num_tarjeta, Nom_cliente, Apell1_cliente, Apell2_cliente, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Monto, Cortesia, Tolerancia, Fecha_vigencia, Vigencia FROM Pensionados WHERE Num_tarjeta = '{Num_tarjeta}'"

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado

    def ver_pensionados(self) -> list:
        """
        Obtiene y muestra todos los pensionados en la tabla.

        Returns:
            list: Una lista con los datos de todos los pensionados.
        """
        query = f"SELECT Num_tarjeta, Cortesia, Nom_cliente, Estatus, Fecha_vigencia, Tolerancia, Id_cliente, Vigencia FROM Pensionados ORDER BY Id_cliente DESC"

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado

    def eliminar_pensinado(self, id: int):
        """
        Elimina un pensionado de la base de datos.

        Args:
            id (int): El identificador del pensionado a eliminar.

        Esta funcion elimina un pensionado de la base de datos con el identificador proporcionado.
        """
        pass

    def actualizar_pensionado(self, datos_pensionado: tuple, Num_tarjeta: int) -> None:
        """
        Actualiza los datos de un pensionado existente en la base de datos.

        Args:
            datos_pensionado (tuple): Una tupla con los nuevos datos del pensionado a actualizar.
            Num_tarjeta (int): El número de tarjeta del pensionado a actualizar.


        Esta funcion actualiza los datos de un pensionado existente en la base de datos.
        """
        datos_pensionado = tuple(datos_pensionado)
        vigencia = datos_pensionado[17]
        if vigencia == None:
            vigencia = 'Null'
        else:
            vigencia = f"""'{vigencia}'"""

        query = f"""UPDATE Pensionados SET Num_tarjeta = '{datos_pensionado[0]}', Nom_cliente = '{datos_pensionado[1]}', Apell1_cliente = '{datos_pensionado[2]}', Apell2_cliente = '{datos_pensionado[3]}', Telefono1 = '{datos_pensionado[4]}', Telefono2 = '{datos_pensionado[5]}', Ciudad = '{datos_pensionado[6]}', Colonia = '{datos_pensionado[7]}', CP = '{datos_pensionado[8]}', Calle_num = '{datos_pensionado[9]}', Placas = '{datos_pensionado[10]}', Modelo_auto = '{datos_pensionado[11]}', Color_auto = '{datos_pensionado[12]}', Monto = '{datos_pensionado[13]}', Cortesia = '{datos_pensionado[14]}', Tolerancia = {datos_pensionado[15]}, Ult_Cambio = '{datos_pensionado[16]}', Fecha_vigencia = {vigencia}, Vigencia = '{datos_pensionado[18]}' WHERE Num_tarjeta = '{Num_tarjeta}';"""

        # Se ejecuta la consulta
        self.execute_query(query)
        
    def get_list_paids_pensiones(self, year_param: int, month_param: int, id_pension:int) -> tuple[list, list, list]:
        """
        Realiza una consulta SQL en la base de datos y devuelve registros junto con otros valores.

        :param year_param (int): Año para la consulta.
        :param month_param (int): Mes para la consulta.
        :return: Una tupla que contiene registros obtenidos, un parámetro y campos de la consulta.
        :raises Exception: Puede lanzar excepciones en caso de errores en la consulta o falta de registros.
        """
        instance_tools = Tools()
        start, end = instance_tools.get_start_end_month(
            year_param, month_param)

        query = f"""SELECT 
        Pensionados.Id_cliente AS ID, 
        Pensionados.Nom_cliente, 
        Pensionados.Apell1_cliente AS Apellido_1, 
        Pensionados.Apell2_cliente AS Apellido_2, 
        PagosPens.Fecha_pago,
        PagosPens.Fecha_vigencia,
        PagosPens.Monto,
        (SELECT nombre FROM MovsUsuarios WHERE CierreCorte BETWEEN PagosPens.Fecha_pago AND '{end}' LIMIT 1) AS Usuario,
        PagosPens.TipoPago 

        FROM PagosPens JOIN Pensionados ON PagosPens.Idcliente = Pensionados.Id_cliente
        WHERE Pensionados.id_cliente = {id_pension} AND PagosPens.Fecha_pago BETWEEN '{start}' AND '{end}';"""

        resultado = self.execute_query(query)
        
        return resultado
        
        

    def desactivar_tarjetas_expiradas(self, hoy: datetime) -> None:
        """
        Desactiva las tarjetas de pensionados cuya vigencia ha expirado.

        Args:
            hoy (datetime): La fecha y hora actuales.

        Esta funcion desactiva las tarjetas de pensionados cuya vigencia ha expirado, asignándoles el estado "InactivaPerm".
        """
        query = f"""UPDATE Pensionados SET Vigencia = 'InactivaPerm', Fecha_vigencia = NULL, Estatus = 'Afuera', Ult_Cambio = '{hoy}' WHERE Fecha_vigencia < DATE_ADD(CURDATE(), INTERVAL -2 MONTH);"""

        # Se ejecuta la consulta
        self.execute_query(query)

    def ver_tarjetas_expiradas(self) -> list:
        """
        Obtiene y muestra todas las tarjetas de pensionados cuya vigencia ha expirado.

        Returns:
            list: Una lista con los números de tarjeta y fechas de vigencia de las tarjetas expiradas.
        """
        query = f"""SELECT Num_tarjeta, Fecha_vigencia FROM Pensionados WHERE Fecha_vigencia < DATE_ADD(CURDATE(), INTERVAL -2 MONTH) ORDER BY Id_cliente DESC;"""

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado

    def get_Entradas_Totales_Pensionados(self, folio: int) -> int:
        """
        Obtiene el total de entradas de pensionados para un folio dado.

        Args:
            folio (int): El número de folio.

        Returns:
            int: El total de entradas de pensionados.
        """
        query = f"""SELECT COUNT(*) AS Entradas_Totales_Pensionados FROM MovimientosPens p INNER JOIN Cortes c ON p.Entrada BETWEEN c.FechaIni AND c.FechaFin WHERE c.Folio = {folio};"""

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado[0][0]

    def get_Salidas_Pensionados(self, corte: int) -> int:
        """
        Obtiene el total de salidas de pensionados para un corte dado.

        Args:
            corte (int): El número de corte.

        Returns:
            int: El total de salidas de pensionados.
        """
        query = f"""SELECT COUNT(*) AS Salidas_Pensionados FROM MovimientosPens WHERE Estatus = "Afuera" AND Salida BETWEEN (SELECT FechaIni from Cortes WHERE Folio = {corte}) AND (SELECT FechaFin from Cortes WHERE Folio = {corte}) AND Corte = {corte};"""

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado[0][0]

    def get_Quedados_Pensionados(self) -> int:
        """
        Obtiene el total de pensionados que aún permanecen dentro del estacionamiento.

        Returns:
            int: El total de pensionados dentro del estacionamiento.
        """
        query = f"""SELECT COUNT(*) AS Quedados_Pensionados FROM MovimientosPens WHERE Estatus = "Adentro" AND Corte = 0;"""

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado[0][0]

    def Actualizar_Entradas_Pension(self, corte: int) -> None:
        """
        Actualiza el campo 'Corte' para las entradas de pensionados en un corte especifico.

        Args:
            corte (int): El número de corte.
        """
        query = f"update MovimientosPens set Corte = {corte} where Corte = 0 AND Salida BETWEEN (SELECT FechaIni from Cortes WHERE Folio = {corte}) AND (SELECT FechaFin from Cortes WHERE Folio = {corte});"
        self.execute_query(query)

    def get_Anteriores_Pensionados(self, corte: int) -> int:
        """
        Obtiene la cantidad de pensionados que permanecieron dentro del estacionamiento en cortes anteriores.

        Args:
            corte (int): El número de corte actual.

        Returns:
            int: La cantidad de pensionados anteriores que permanecieron dentro.
        """
        query = f"""SELECT COALESCE(Pensionados_Quedados, 0) FROM Cortes WHERE Folio = {corte};"""

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        return resultado[0][0]

    def get_QR_id(self) -> int:
        """
        Obtiene un nuevo identificador para la generacion de codigos QR para pensionados.

        Returns:
            int: El nuevo identificador para la generacion de codigos QR.
        """
        query = f"""SELECT COALESCE(MAX(Id_cliente), 0) FROM Pensionados;"""

        # Se ejecuta la consulta y se obtiene el resultado.
        resultado = self.execute_query(query)

        ID = resultado[0][0] + 1

        return ID

class Cambios(Usuarios):
    """
    Clase para interactuar con la tabla de Cambios en la base de datos.

    Esta clase hereda de la clase Usuarios y proporciona metodos adicionales para agregar, consultar, visualizar,
    eliminar y actualizar informacion relacionada con cammbios en la tabla de Cambios.
    """
    def add_change(self, nombre_cambio:str, valor_anterior, valor_nuevo, tipo_cambio:str, nombre_usuario:str):
        query = f"""INSERT 
        INTO Cambios (nombre, valor_anterior, valor_nuevo, tipo_cambio, hora, nombre_usuario)
        VALUES ('{nombre_cambio}', '{valor_anterior}', '{valor_nuevo}', '{tipo_cambio}', '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', '{nombre_usuario}');"""
        self.execute_query(query)


    def get_list_changes(self, year_param: int, month_param: int) -> tuple[list, list, list]:
        """
        Realiza una consulta SQL en la base de datos y devuelve registros junto con otros valores.

        :param year_param (int): Año para la consulta.
        :param month_param (int): Mes para la consulta.
        :return: Una tupla que contiene registros obtenidos, un parámetro y campos de la consulta.
        :raises Exception: Puede lanzar excepciones en caso de errores en la consulta o falta de registros.
        """
        instance_tools = Tools()
        start, end = instance_tools.get_start_end_month(
            year_param, month_param)

        query = f"""SELECT hora, nombre, valor_anterior, valor_nuevo, tipo_cambio, nombre_usuario FROM Cambios WHERE hora BETWEEN '{start}' AND '{end}' ORDER BY id DESC;"""

        resultado = self.execute_query(query)
        
        return resultado
