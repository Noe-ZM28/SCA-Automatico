import pymysql
import random
from tkinter import messagebox as mb
import qrcode

class Operacion:
	def __init__(self):
		self.host = "169.254.202.242"
		self.user = "Aurelio"
		self.password = "RG980320"
		self.database = "Parqueadero1"

	def abrir(self):
		conexion=pymysql.connect(host=self.host,
								user=self.user,
								passwd=self.password,
								database=self.database)

		return conexion
		
	def Intervalo(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select id, Entrada, Salida, TiempoTotal, Importe, CorteInc, vobo, Placas, TarifaPreferente,TipoPromocion from Entradas where id >= 19096  "
		#sql="select id, Entrada, Salida, TiempoTotal, Importe, CorteInc, vobo, Placas, TarifaPreferente,TipoPromocion from Entradas where CorteInc = 0 and Importe is null and Salida is null "
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()
	def RFID(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="insert into Insidencia(Id, FechaAccesoNo) values (%s,%s)"
		cursor.execute(sql, datos)
		cone.commit()
		cone.close()
	def altaRegistroRFID(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="insert into Entradas(Entrada, CorteInc, Placas) values (%s,%s,%s)"
		cursor.execute(sql, datos)
		cone.commit()
		cone.close()

	def guardacobro(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql = "update Entradas set vobo = %s, Importe = %s, TiempoTotal = %s, Entrada = %s, Salida = %s,TarifaPreferente = %s where id = %s;"
		cursor.execute(sql, datos)
		cone.commit()
		cone.close()
	  

	def consulta(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select Entrada, Salida from Entradas where id=%s"
	   #sql="select descripcion, precio from articulos where codigo=%s"
		cursor.execute(sql, datos)
		cone.close()
		return cursor.fetchall()

	def recuperar_todos(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select id, Entrada, Salida from Entradas"
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()

	def recuperar_sincobro(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select id, Entrada, Salida, Importe from Entradas where CorteInc = 0 and Importe is not null "
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()
	def desglose_cobrados(self,Numcorte):
		cone=self.abrir()
		cursor=cone.cursor()
		#sql="SELECT TarifaPreferente,Importe, Count(*) as cuantos FROM Entradas where CorteInc = 6 "
		sql="SELECT TarifaPreferente,Importe, Count(*) as cuantos FROM Entradas where CorteInc = %s GROUP BY TarifaPreferente,Importe;"
		#sql="select id, Entrada, Salida, Importe from Entradas where CorteInc = 0 and Importe is not null "
		cursor.execute(sql,Numcorte)
		cone.close()
		return cursor.fetchall()
	def Autos_dentro(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select id, Entrada, Placas from Entradas where CorteInc = 0 and Importe is null and Salida is null "
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()

	def CuantosAutosdentro(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select count(*) from Entradas where CorteInc = 0 and Importe is null and Salida is null "
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()
	def Quedados_Sensor(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select Quedados from Cortes where Folio=%s"
	   #sql="select descripcion, precio from articulos where codigo=%s"
		cursor.execute(sql, datos)
		cone.close()
		return cursor.fetchall()

	def NumBolQued(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select NumBolQued from Cortes where Folio=%s"
	   #sql="select descripcion, precio from articulos where codigo=%s"
		cursor.execute(sql, datos)
		cone.close()
		return cursor.fetchall()
	def EntradasSensor(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select EntSens from AccesosSens where Folio=1"
	   #sql="select descripcion, precio from articulos where codigo=%s"
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()
	def SalidasSensor(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select SalSens from AccesosSens where Folio=1"
	   #sql="select descripcion, precio from articulos where codigo=%s"
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()

	def CuantosBoletosCobro(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select count(*) from Entradas where CorteInc = 0 and Importe is not null and Salida is not null "
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()

	def BEDCorte(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select count(*) from Entradas where ((vobo is null and TarifaPreferente is null) or (vobo = 'lmf' and TarifaPreferente = ''))"
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()

	def BAnteriores(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select count(*) from Entradas where vobo = 'ant' "
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()

	def corte(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select sum(importe) from Entradas where CorteInc = 0"
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()
	def MaxfolioEntrada(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select max(id) from Entradas;"
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()

	def Maxfolio_Cortes(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select max(Folio) from Cortes;"
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()

	def ActualizarEntradasConcorte(self, maxnum):
		cone=self.abrir()
		cursor=cone.cursor()
		sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
		#sql = "update Entradas set CorteInc=%s where TiempoTotal is not null and CorteInc=0;"
		cursor.execute(sql,maxnum)
		cone.commit()
		cone.close()

	def NocobradosAnt(self, vobo):
		cone=self.abrir()
		cursor=cone.cursor()
		sql = "update Entradas set vobo = %s where Importe is null and CorteInc=0;"
		cursor.execute(sql,vobo)
		cone.commit()
		cone.close()

	def obtenerNumCorte(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select max(Folio) from Cortes"
		#sql = "update Entradas set CorteInc = 1 WHERE Importe > 0"
		cursor.execute(sql)
		#cone.commit()
		cone.close()
		return cursor.fetchall()
	def MaxnumId(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select max(idInicial) from Cortes"
		#sql = "update Entradas set CorteInc = 1 WHERE Importe > 0"
		cursor.execute(sql)
		#cone.commit()
		cone.close()
		return cursor.fetchall()

	def AperturaManual(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="insert into Apertura(FechaIncidencia,CorteInc) values (%s,%s)"
		#sql = "update Entradas set CorteInc = 1 WHERE Importe > 0"
		cursor.execute(sql,datos)
		cone.commit()
		cone.close()
	def UltimoCorte(self):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="select max(FechaFin) from Cortes;"
		cursor.execute(sql)
		cone.close()
		return cursor.fetchall()
	def GuarCorte(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="insert into RegistroBarrera(Hora, Corte) values (%s,%s)"
		#sql = "update Entradas set vobo = %s where Importe is null and CorteInc=0;"
		cursor.execute(sql,datos)
		cone.commit()
		cone.close()        

####pensionados
	def ValidarPen(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="SELECT id_cliente FROM Pensionados WHERE Num_tarjeta=%s"
		cursor.execute(sql,datos)
		cone.close()
		return cursor.fetchall()       
	def ConsultaPensionado(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="SELECT Fecha_vigencia, Estatus, Vigencia, Tolerancia FROM Pensionados where id_cliente=%s"
		cursor.execute(sql,datos)
		cone.close()
		return cursor.fetchall()
	def UpdPensionado(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="UPDATE Pensionados SET Estatus=%s WHERE id_cliente=%s"
		#sql = "update Entradas set CorteInc = %s, vobo = %s where TiempoTotal is not null and CorteInc=0;"
		cursor.execute(sql, datos)
		cone.commit()
		cone.close()
	def MovsPensionado(self, datos):
		cone=self.abrir()
		cursor=cone.cursor()
		sql="INSERT INTO MovimientosPens(idcliente, num_tarjeta, Entrada, Estatus, Corte) values (%s,%s,%s,%s,%s)"
		cursor.execute(sql,datos)
		cone.commit()
		cone.close()



	def cifrar_folio(self, folio):
		"""
		Cifra un número de folio utilizando una tabla de sustitución numérica.

		Args:
			folio (int): Número de folio a cifrar.

		Returns:
			str: Número de folio cifrado.
		"""

		# Convierte el número de folio en una cadena de texto.
		folio = str(folio)

		# Genera un número aleatorio de 5 dígitos y lo convierte en una cadena de texto.
		num_random = random.randint(10000, 99999)
		numero_seguridad = str(num_random)

		# Concatena el número de seguridad al número de folio.
		folio = folio + numero_seguridad

		# Imprime el número de folio cifrado (sólo para propósitos de depuración).
		print(folio)

		# Tabla de sustitución numérica.
		tabla = {'0': '5', '1': '3', '2': '9', '3': '1', '4': '7', '5': '0', '6': '8', '7': '4', '8': '6', '9': '2'}

		# Convierte el número de folio cifrado a una lista de dígitos.
		digitos = list(folio)

		# Sustituye cada dígito por el número correspondiente en la tabla de sustitución.
		cifrado = [tabla[digito] for digito in digitos]

		# Convierte la lista cifrada de vuelta a una cadena de texto.
		cifrado = ''.join(cifrado)

		# Devuelve el número de folio cifrado.
		return cifrado


	def descifrar_folio(self, folio_cifrado):
		"""
		Descifra un número de folio cifrado utilizando una tabla de sustitución numérica.

		Args:
			folio_cifrado (str): Número de folio cifrado.

		Returns:
			str: Número de folio descifrado.
		"""
		try:
			# Verifica si el número de folio es válido.
			if len(folio_cifrado) <= 5:
				raise ValueError("El folio no es válido, escanee nuevamente, si el error persiste contacte con un administrador.")

			# Verifica si el número de folio tiene caracteres inválidos.
			caracteres_invalidos = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '{', '}', '[', ']', '|', '\\', ':', ';', '<', '>', ',', '.', '/', '?']
			if any(caracter in folio_cifrado for caracter in caracteres_invalidos):
				raise TypeError("El folio no tiene un formato válido")

			# Tabla de sustitución numérica.
			tabla = {'0': '5', '1': '3', '2': '9', '3': '1', '4': '7', '5': '0', '6': '8', '7': '4', '8': '6', '9': '2'}

			# Convierte el número de folio cifrado a una lista de dígitos.
			digitos_cifrados = list(folio_cifrado)

			# Crea una tabla de sustitución inversa invirtiendo la tabla original.
			tabla_inversa = {valor: clave for clave, valor in tabla.items()}

			# Sustituye cada dígito cifrado por el número correspondiente en la tabla de sustitución inversa.
			descifrado = [tabla_inversa[digito] for digito in digitos_cifrados]

			# Convierte la lista descifrada de vuelta a una cadena de texto.
			descifrado = ''.join(descifrado)

			# Elimina los últimos 4 dígitos, que corresponden al número aleatorio generado en la función cifrar_folio.
			descifrado = descifrado[:-5]

			# Retorna el folio descifrado.
			return descifrado

		# Maneja el error si el formato del número de folio es incorrecto.
		except TypeError as error:
			#mb.showerror("Error", f"El folio tiene un formato incorrecto, si el error persiste contacte a un administrador y muestre el siguiente error:\n{error}")
			return None

		# Maneja cualquier otro error que pueda ocurrir al descifrar el número de folio.
		except Exception as error:
			#mb.showerror("Error", f"Ha ocurrido un error al descifrar el folio, intente nuevamente, si el error persiste contacte a un administrador y muestre el siguiente error:\n{error}")
			return None


	def generar_QR(self, QR_info: str, path: str = "reducida.png") -> None:
		"""Genera un código QR a partir de la información dada y lo guarda en un archivo de imagen.

		Args:
			QR_info (str): La información para generar el código QR.
			path (str, optional): La ruta y el nombre del archivo de imagen donde se guardará el código QR, por defecto es "reducida.png".
		"""
		# Generar el código QR
		img = qrcode.make(QR_info)

		# Redimensionar el código QR a un tamaño específico
		img = img.get_image().resize((320, 320))

		# Guardar la imagen redimensionada en un archivo
		img.save(path)


