import pymysql
from tkinter import messagebox as mb
from enum import Enum
import traceback

from Controllers.ConfigController import ConfigController
from Tools.Tools import Tools


class ModelErrorMessages(Enum):
    """
    Enums que define los mensajes de error.
    """
    ERROR_EXTEND_MESSAGE_INTERNAL_ERROR: str = "\n\n\tError: No se puede conectar con la base de datos.\n\nPasos a seguir:\n1) Reinicie el sistema.\n2) En caso de que se siga mostrando este mensaje de error apague y encienda nuevamente la computadora.\n\n3) De no solucionarse el error contacte inmediatamente con un administrador, si este ya se encuentra con usted pida que verifique la configuracion de la base de datos del panel de configuracion y que esta sea correcta."

    UNKOWN_MESAGE_ERROR = "Error desconocido, contacte con un administrador y muestre el siguiente error: "

    NONE_MESAGE: str = ""


class ModelTypeErrorMessages(Enum):
    """
    Enums que define los tipos de errores.
    """
    CONECTION_ERROR: str = "Error de conexion"
    
    UNKOWN_ERROR = "Error desconocido"
    


    NONE_MESAGE: str = ""


class Operacion:
    def __init__(self):
        __instance_config__ = ConfigController()
        self.__instance_tools__ = Tools()

        dataconfig = __instance_config__.get_config(
            "funcionamiento_interno", "db")
        self.__host__ = dataconfig["host"]
        self.__user__ = dataconfig["usuario"]
        self.__db_password__ = dataconfig["password"]
        self.__db_iv__ = dataconfig["iv"]
        self.__db__ = dataconfig["db"]

        dataconfig = None

    def abrir(self):
        """
        Abre una conexion a la base de datos utilizando los parámetros proporcionados.

        Returns:
            pymysql.connections.Connection: Objeto de conexion a la base de datos.

        Raises:
            pymysql.err.OperationalError: Si hay un error durante la conexion.
        """
        try:
            mesage = None
            conexion = pymysql.connect(
                host=self.__host__,
                user=self.__user__,
                passwd=self.__instance_tools__.descifrar_AES(self.__db_password__, bytes.fromhex(self.__db_iv__)),
                database=self.__db__)
            return conexion
        except pymysql.err.OperationalError as e:
            mesage = self.create_mesage_error(
                ModelTypeErrorMessages.CONECTION_ERROR,
                ModelErrorMessages.ERROR_EXTEND_MESSAGE_INTERNAL_ERROR)

        except Exception as e:
            traceback.print_exc()
            mesage = self.create_mesage_error(
                ModelTypeErrorMessages.UNKOWN_ERROR,
                ModelErrorMessages.UNKOWN_MESAGE_ERROR) + e
        finally:
            if mesage != None:
                mb.showerror("Error", mesage)

    def create_mesage_error(self, type_mesage_error: ModelTypeErrorMessages, mesage_error: ModelErrorMessages) -> str:
        """
        Crea un mensaje de error combinando el tipo de error y el mensaje de error proporcionados.

        Args:
            type_mesage_error (ModelTypeErrorMessages): Tipo de error.
            mesage_error (ModelErrorMessages): Mensaje de error.

        Returns:
            str: Mensaje de error concatenado.
        """
        return type_mesage_error.value + " " + mesage_error.value

    def altaRegistroRFID(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "insert into Entradas(Entrada, CorteInc, Placas) values (%s,%s,%s)"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def guardacobro(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "update Entradas set Motivo = %s, vobo = %s, Importe = %s, TiempoTotal = %s, Entrada = %s, Salida = %s,TarifaPreferente = %s, QRPromo = %s where id = %s;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def desgloce_cancelados(self, corte):
        cone = self.abrir()
        cursor = cone.cursor()
        query = f"SELECT id, Motivo FROM Entradas WHERE TarifaPreferente = 'CDO' AND CorteInc = {corte}"
        cursor.execute(query)
        cone.close()
        return cursor.fetchall()

    def ValidaPromo(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select id from Entradas where QRPromo = %s "
        # sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def consulta(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select Entrada, Salida, id, TiempoTotal, TarifaPreferente, Importe, Placas, Motivo from Entradas where id=%s"
       # sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def recuperar_sincobro(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select id, Entrada, Salida, Importe from Entradas where CorteInc = 0 and Importe is not null "
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def desglose_cobrados(self, Numcorte):
        cone = self.abrir()
        cursor = cone.cursor()
        # sql="SELECT TarifaPreferente,Importe, Count(*) as cuantos FROM Entradas where CorteInc = 6 "
        # sql="SELECT TarifaPreferente,Importe, Count(*) as cuantos FROM Entradas where CorteInc = %s GROUP BY TarifaPreferente,Importe;"
        sql = "SELECT Count(*),TarifaPreferente,Importe, Count(*)*Importe  as cuantos FROM Entradas where CorteInc = %s GROUP BY TarifaPreferente,Importe;"
        # sql="select id, Entrada, Salida, Importe from Entradas where CorteInc = 0 and Importe is not null "
        cursor.execute(sql, Numcorte)
        cone.close()
        return cursor.fetchall()

    def Autos_dentro(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select id, Entrada, Placas from Entradas where CorteInc = 0 and Importe is null and Salida is null "
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def CuantosAutosdentro(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select count(*) from Entradas where CorteInc = 0 and Importe is null and Salida is null "
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()[0][0]

    def Quedados_Sensor(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select Quedados from Cortes where Folio=%s"
       # sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()[0][0]

    def NumBolQued(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select NumBolQued from Cortes where Folio=%s"
       # sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def EntradasSensor(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select EntSens from AccesosSens where Folio=1"
       # sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def SalidasSensor(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select SalSens from AccesosSens where Folio=1"
       # sql="select descripcion, precio from articulos where codigo=%s"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def CuantosBoletosCobro(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select count(*) from Entradas where CorteInc = 0 and Importe is not null and Salida is not null "
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()[0][0]

    def BEDCorte(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select count(*) from Entradas where ((vobo is null and TarifaPreferente is null) or (vobo = 'lmf' and TarifaPreferente = ''))"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()[0][0]

    def BAnteriores(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select count(*) from Entradas where vobo = 'ant' "
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()[0][0]

    def corte(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select COALESCE(sum(importe), 0) from Entradas where CorteInc = 0"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()[0][0]

    def MaxfolioEntrada(self) -> int:
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select max(id) from Entradas;"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()[0][0]

    def Maxfolio_Cortes(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select max(Folio) from Cortes;"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()[0][0]

    def ActualizarEntradasConcorte(self, maxnum):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
        # sql = "update Entradas set CorteInc=%s where TiempoTotal is not null and CorteInc=0;"
        cursor.execute(sql, maxnum)
        cone.commit()
        cone.close()

    def NocobradosAnt(self, vobo):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "update Entradas set vobo = %s where Importe is null and CorteInc=0;"
        cursor.execute(sql, vobo)
        cone.commit()
        cone.close()

    def obtenerNumCorte(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select max(Folio) from Cortes"
        # sql = "update Entradas set CorteInc = 1 WHERE Importe > 0"
        cursor.execute(sql)
        # cone.commit()
        cone.close()
        return cursor.fetchall()

    def MaxnumId(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select max(idInicial) from Cortes"
        # sql = "update Entradas set CorteInc = 1 WHERE Importe > 0"
        cursor.execute(sql)
        # cone.commit()
        cone.close()
        return cursor.fetchall()[0][0]

    def GuarCorte(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "insert into Cortes(Importe, FechaIni, FechaFin,Quedados,idInicial,NumBolQued, Pensionados_Quedados) values (%s,%s,%s,%s,%s,%s,%s)"
        # sql = "update Entradas set CorteInc = 1 WHERE Importe > 0"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def UltimoCorte(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "select max(FechaFin) from Cortes;"
        # sql="select max(FechaFin) from Cortes;"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()[0][0]

    def Cortes_MaxMin(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "SELECT max(FechaFin), min(FechaFin) FROM Cortes where MONTH(FechaFin)=%s AND YEAR(FechaFin)=%s "
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def Cortes_Folio(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "SELECT Folio FROM Cortes where FechaFin=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def Registros_corte(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        # CorteInc > (%s-1) AND CorteInc < (%s+1)
        sql = "SELECT id, Entrada, Salida, TiempoTotal, Importe, CorteInc, Placas, TarifaPreferente FROM Entradas where CorteInc > (%s-1) AND CorteInc < (%s+1)"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def Totales_corte(self, datos1):
        cone = self.abrir()
        cursor = cone.cursor()
        # Entrada > %s AND Entrada < %s
        sql = "SELECT sum(Importe), max(CorteInc), min(CorteInc) FROM Entradas where CorteInc > (%s-1) AND CorteInc < (%s+1)"
        cursor.execute(sql, datos1)
        cone.close()
        return cursor.fetchall()

 ##### USUARIOS###

    def ConsultaUsuario(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "SELECT Id_usuario, Contrasena, Nom_usuario FROM Usuarios WHERE Usuario = %s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def CajeroenTurno(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "SELECT min(id_movs), nombre, inicio, turno, Idusuario FROM MovsUsuarios where CierreCorte is null"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def IniciosdeTurno(self, dato):
        cone = self.abrir()
        cursor = cone.cursor()
        # and CierreCorte = 'No aplica'  Idusuario = %s and
        sql = "SELECT inicio, usuario FROM MovsUsuarios where inicio > %s"
        cursor.execute(sql, dato)
        cone.close()
        return cursor.fetchall()

    def ActualizaUsuario(self, actual):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "INSERT INTO MovsUsuarios(Idusuario, usuario, inicio, nombre, turno) values (%s,%s,%s,%s,%s)"
        # sql="INSERT INTO PagosPens(idcliente, num_tarjeta, Fecha_pago, Fecha_vigencia, Mensualidad, Monto) values (%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, actual)
        cone.commit()
        cone.close()

    def Cierreusuario(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "update MovsUsuarios set CierreCorte = %s where  id_movs = %s;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def NoAplicausuario(self, dato):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "update MovsUsuarios set CierreCorte = 'No aplica' where  id_movs > %s;"
        cursor.execute(sql, dato)
        cone.commit()
        cone.close()

    def Boletos_perdidos_generados(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = """SELECT COUNT(*) AS "BOLETOS PERDIDOS GENERADOS" FROM Entradas WHERE `Placas` = "BoletoPerdido" AND CorteInc = 0;"""
        cursor.execute(sql)
        cone.commit()

        resultados = cursor.fetchall()[0][0]

        # Se cierra la conexion con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados

    def Boletos_perdidos_generados_desglose(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = """SELECT id, Entrada, Salida, Placas FROM Entradas WHERE `Placas` = "BoletoPerdido" AND CorteInc = 0;"""
        cursor.execute(sql)
        cone.commit()

        resultados = cursor.fetchall()

        # Se cierra la conexion con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados

    def Boletos_perdidos_cobrados(self, Numcorte):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = """SELECT COUNT(*) AS "BOLETOS PERDIDOS COBRADOS" FROM Entradas WHERE `Placas` = "BoletoPerdido" AND CorteInc = %s AND TarifaPreferente IS NOT NULL;"""
        cursor.execute(sql, Numcorte)
        cone.commit()
        resultados = cursor.fetchall()[0][0]

        # Se cierra la conexion con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados

    def Boletos_perdidos_cobrados_desglose(self, Numcorte):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = """SELECT id, Entrada, Salida, Placas FROM Entradas WHERE `Placas` = "BoletoPerdido" AND CorteInc = %s AND TarifaPreferente IS NOT NULL;"""
        cursor.execute(sql, Numcorte)
        cone.commit()
        resultados = cursor.fetchall()

        # Se cierra la conexion con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados

    def Boletos_perdidos_no_cobrados(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = """SELECT COUNT(*) AS "BOLETOS PERDIDOS NO COBRADOS" FROM Entradas WHERE `Placas` = "BoletoPerdido" AND CorteInc = 0 AND TarifaPreferente IS NULL;"""
        cursor.execute(sql)
        cone.commit()
        resultados = cursor.fetchall()[0][0]

        # Se cierra la conexion con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados


# PENSIONADOS

    def ValidarRFID(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "SELECT id_cliente FROM Pensionados WHERE Num_tarjeta=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()[0][0]

    def AltaPensionado(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "INSERT INTO Pensionados(Num_tarjeta, Nom_cliente, Apell1_cliente, Apell2_cliente, Fecha_alta, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Monto, Cortesia, Tolerancia) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # datos=(numtarjeta, Nombre, ApellidoPat, ApellidoMat, fechaAlta, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle, Placa, Modelo, Color, montoxmes, cortesia, tolerancia)
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def ConsultaPensionado(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "SELECT Nom_cliente, Apell1_cliente, Apell2_cliente, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle_num, Placas, Modelo_auto, Color_auto, Fecha_vigencia, Estatus, Vigencia, Monto, Cortesia, Tolerancia FROM Pensionados where id_cliente=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def ModificarPensionado(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "UPDATE Pensionados SET Num_tarjeta=%s, Nom_cliente=%s, Apell1_cliente=%s, Apell2_cliente=%s, Telefono1=%s, Telefono2=%s, Ciudad=%s, Colonia=%s, CP=%s, Calle_num=%s, Placas=%s, Modelo_auto=%s, Color_auto=%s, Monto=%s, Cortesia=%s, Tolerancia=%s, Ult_Cambio=%s WHERE id_cliente=%s"
        # datos=(numtarjeta, Nombre, ApellidoPat, ApellidoMat, Telefono1, Telefono2, Ciudad, Colonia, CP, Calle, Placa, Modelo,                    Color, montoxmes, cortesia, tolerancia, PensionadoOpen)
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def CobrosPensionado(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "INSERT INTO PagosPens(idcliente, num_tarjeta, Fecha_pago, Fecha_vigencia, Mensualidad, Monto, TipoPago) values (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def UpdMovsPens(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "UPDATE MovimientosPens SET Salida=%s, TiempoTotal =%s, Estatus=%s WHERE idcliente=%s and Salida is null"
        # sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def UpdPens2(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "UPDATE Pensionados SET Estatus=%s WHERE id_cliente=%s"
        # sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def ValidarTarj(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "SELECT id_cliente, Estatus FROM Pensionados WHERE Num_tarjeta=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def TreaPenAdentro(self):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = """SELECT Num_tarjeta, Nom_cliente, Apell1_cliente, Placas, Modelo_auto from Pensionados where Estatus = "Adentro";"""
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def nombre_usuario_activo(self):
        """
        Esta funcion realiza una consulta a la base de datos para obtener el nombre del usuario que esta activo.
        Args:
        - self: referencia a la clase donde está definida la funcion.
        Returns:
        - resultados: lista de tuplas que contienen la siguiente informacion:
            - nombre: El nombre del usuario
        Esta funcion utiliza la libreria de MySQL Connector para conectarse a la base de datos y ejecutar una consulta SQL.
        """

        # Se establece la conexion con la base de datos.
        cone = self.abrir()

        # Se crea un cursor para ejecutar la consulta.
        cursor = cone.cursor()

        # Se define la consulta SQL.
        sql = f"""SELECT nombre FROM MovsUsuarios WHERE CierreCorte IS Null"""

        # Se ejecuta la consulta y se almacenan los resultados en una lista de tuplas.
        cursor.execute(sql)
        resultados = cursor.fetchall()[0][0]

        # Se cierra la conexion con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados

    def total_pensionados_corte(self, corte):
        """
        Realiza una consulta a la base de datos para obtener la cantidad y el importe total de los pagos de pensiones 
        realizados en un corte especifico.
        Args:
            self: referencia a la clase donde está definida la funcion.
            corte (int): el número de folio del corte que se desea consultar.
        Returns:
            resultados (list): una lista de tuplas que contienen la siguiente informacion:
                - Cuantos (int): la cantidad de pagos de pensiones realizados en el corte.
                - Concepto (str): una cadena que indica el tipo de pago (en este caso, siempre será "Pensionados").
                - ImporteTotal (float): el importe total de los pagos de pensiones realizados en el corte.
        Esta funcion utiliza la libreria de MySQL Connector para conectarse a la base de datos y ejecutar una consulta SQL.
        """
        # Se establece la conexion con la base de datos.
        cone = self.abrir()

        # Se crea un cursor para ejecutar la consulta.
        cursor = cone.cursor()

        # Se define la consulta SQL.
        sql = f"""SELECT COUNT(*) AS Cuantos, TipoPago AS Concepto, COALESCE(FORMAT(SUM(p.Monto), 2), 0) AS ImporteTotal FROM PagosPens p INNER JOIN Cortes c ON p.Fecha_pago BETWEEN c.FechaIni AND c.FechaFin WHERE c.Folio = {corte} GROUP BY TipoPago;"""

        # Se ejecuta la consulta y se almacenan los resultados en una lista de tuplas.
        cursor.execute(sql)
        resultados = cursor.fetchall()

        # Se cierra la conexion con la base de datos.
        cone.close()

        # Se devuelve la lista de tuplas con los resultados de la consulta.
        return resultados

    # pensionados
    def ValidarPen(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "SELECT id_cliente FROM Pensionados WHERE Num_tarjeta=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def UpdPensionado(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "UPDATE Pensionados SET Estatus=%s WHERE id_cliente=%s"
        # sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def Upd_Pensionado(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "UPDATE Pensionados SET Vigencia=%s, Fecha_vigencia=%s WHERE id_cliente=%s"
        # sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def MovsPensionado(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "INSERT INTO MovimientosPens(idcliente, num_tarjeta, Entrada, Estatus, Corte) values (%s,%s,%s,%s,%s)"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()

    def consultar_UpdMovsPens(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "SELECT Entrada FROM MovimientosPens WHERE idcliente=%s and Salida is null"
        # sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
        cursor.execute(sql, datos)
        cone.commit()
        cone.close()
        return cursor.fetchall()[0][0]

    def ConsultaPensionado_entrar(self, datos):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = "SELECT Fecha_vigencia, Estatus, Vigencia, Tolerancia, Placas, Nom_cliente, Apell1_cliente, Apell2_cliente FROM Pensionados where id_cliente=%s"
        cursor.execute(sql, datos)
        cone.close()
        return cursor.fetchall()

    def consultar_corte(self, corte: int):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = f"SELECT FechaIni, FechaFin, Importe, NumBolQued, idInicial FROM Cortes WHERE Folio = {corte}"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def consultar_informacion_corte(self, corte: int):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = f"SELECT nombre, turno FROM MovsUsuarios WHERE inicio BETWEEN (SELECT FechaIni from Cortes WHERE Folio = {corte}) AND (SELECT FechaFin from Cortes WHERE Folio = {corte})"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()

    def Cuantos_Boletos_Cobro_Reimpresion(self, corte: int):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = f"SELECT count(*) from Entradas where CorteInc = {corte}"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()[0][0]

    def boletos_expedidos_reimpresion(self, corte: int):
        cone = self.abrir()
        cursor = cone.cursor()
        sql = f"SELECT COUNT(id) FROM Entradas WHERE Entrada BETWEEN (SELECT FechaIni from Cortes WHERE Folio = {corte}) AND (SELECT FechaFin from Cortes WHERE Folio = {corte})"
        cursor.execute(sql)
        cone.close()
        return cursor.fetchall()[0][0]

    def obtener_lista_de(self, tabla: str, listar: str, revez: str = None) -> tuple:
        """
        Devuelve una lista con los valores únicos de la columna especificada de la tabla 'Entradas' de la base de datos.
        :param tabla (str): Nombre de la tabla de la que se quiere hacer la consulta.
        :param listar (str): Nombre de la columna de la tabla de la que se quieren obtener los valores únicos.
        :param revez: (str or None) Si se especifica 'D', devuelve los valores en orden descendente;
            si se especifica 'A', los devuelve en orden ascendente; si no se especifica, los devuelve en el orden en que se encuentran en la tabla.
        :return:
            - lista_sin_nones (list): Una lista con los valores únicos de la columna especificada de la tabla 'Entradas',
                sin incluir valores 'None'.
        """
        cone = self.abrir()
        cursor = cone.cursor()

        # Si revez es igual a 'D', la consulta se hace en orden descendente.
        if revez == 'D':
            query = f"SELECT DISTINCT {listar} FROM {tabla} ORDER BY {listar} DESC;"
        # Si revez es igual a 'A', la consulta se hace en orden ascendente.
        elif revez == 'A':
            query = f"SELECT DISTINCT {listar} FROM {tabla} ORDER BY {listar} ASC;"
        # Si revez no está definido, se realiza una consulta simple.
        if revez == None:
            query = f"SELECT DISTINCT {listar} FROM {tabla};"

        cursor.execute(query)
        cone.close()
        return cursor.fetchall()
