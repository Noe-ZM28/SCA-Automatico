from escpos.exceptions import USBNotFoundError
from usb.core import NoBackendError

from escpos.printer import Usb as Printer
from datetime import datetime
import traceback

from Models.Model import Operacion
from Controllers.ConfigController import ConfigController
from Tools.Tools import Tools

from Tools.ErrorMesages import PrinterControllerErrorMessages, PrinterControllerTypeErrorMessages


class PrinterController:
    """
    Clase que controla la impresion de boletos y comprobantes utilizando una impresora USB.

    Esta clase se encarga de obtener la configuracion necesaria, como rutas de imágenes y formatos de fecha,
    y proporciona metodos para imprimir boletos de entrada, boletos de perdida, comprobantes de pago, entre otros.

    Metodos:
        - print_ticket: Imprime un boleto de entrada.
        - print_lose_ticket: Imprime un boleto de perdida.
        - print_pension_exit_ticket: Imprime un boleto de salida para pensionados.
        - print_pension_enter_ticket: Imprime un boleto de entrada para pensionados.
        - print_pension_pay_ticket: Imprime un comprobante de pago para pensionados.
        - print_cancel_ticket: Imprime un boleto cancelado.
        - print_payment_ticket: Imprime un comprobante de pago.
        - re_print_payment_ticket: Reimprime un comprobante de pago.
        - print_entradas_sin_corte: Imprime boletos de entrada sin corte asociado.
        - print_QR_pension: Imprime un QR de pension.
        - create_mesage_error: Crea un mensaje de error combinando el tipo de error y el mensaje de error proporcionados.
    """

    def __init__(self):
        """
        Inicializa una instancia de la clase PrinterController y obtiene datos de configuracion.
        """
        self.__instance_config__ = ConfigController()
        self.__instance_tools__ = Tools()
        self.__DB__ = Operacion()
        self.__get_data__()

    def __get_data__(self):
        """
        Obtiene la configuracion necesaria para la impresion desde el archivo de configuracion.
        """
        self.__system_to_load__ = data_config = self.__instance_config__.get_config(
            "system_to_load")
        data_config = self.__instance_config__.get_config("general")

        self.nombre_entrada = data_config["informacion_estacionamiento"]["nombre_entrada"]
        self.nombre_estacionamiento = data_config["informacion_estacionamiento"]["nombre_estacionamiento"]

        self.logo_empresa = data_config["imagenes"]["path_logo_boleto"]
        self.imagen_marcas_auto = data_config["imagenes"]["path_marcas_auto"]

        # Configuracion de fechas del sistema
        formatos_fecha = data_config["configuracion_sistema"]["formatos_fecha"]

        self.date_format_system = "%Y-%m-%d %H:%M:%S"
        self.date_format_ticket = formatos_fecha[data_config["configuracion_sistema"]
                                                 ["formato_hora_boleto"]]

        # Configuracion de la impresora
        self.printer_idVendor = self.__instance_tools__.text_to_hexanumber(
            data_config["configuracion_sistema"]["impresora"]["idVendor"])
        self.printer_idProduct = self.__instance_tools__.text_to_hexanumber(
            data_config["configuracion_sistema"]["impresora"]["idProduct"])

        # Otras configuraciones generales
        self.imprime_contra_parabrisas = data_config["configuracion_sistema"]["imprime_contra_parabrisas"]
        self.imprime_contra_localizacion = data_config["configuracion_sistema"]["imprime_contra_localizacion"]
        self.solicita_datos_del_auto = data_config["configuracion_sistema"]["solicita_datos_del_auto"]

        self.size_font_boleto = data_config["configuracion_sistema"]["size_font_boleto"]
        self.size_font_contra_parabrisas = data_config["configuracion_sistema"]["size_font_contra_parabrisas"]
        self.size_font_contra_localizacion = data_config[
            "configuracion_sistema"]["size_font_contra_localizacion"]

        data_config = None

    def check_printer(self):
        try:
            printer = Printer(self.printer_idVendor, self.printer_idProduct)
            pass

        except (USBNotFoundError, NoBackendError) as e:
            state = False
        except Exception as e:
            traceback.print_exc()
            state = False
        else:
            printer.close()
            state = True
        finally:
            return state

    def print_changes(self, title_changes:str, changes_list:list):
        try:
            mesage = None
            # Instancia el objeto Printer para imprimir el resultado
            printer = Printer(self.printer_idVendor, self.printer_idProduct)

            # Alinea el texto al centro
            printer.set(align="center")
            
            printer.text(f"{title_changes}\n")

            printer.set(align="left")
            
            for i, change in enumerate(changes_list):
                printer.text(f"{i+1}) {change}\n")

            printer.cut()
            printer.close()

        except (USBNotFoundError, NoBackendError) as e:
            mesage = self.create_mesage_error(
                PrinterControllerTypeErrorMessages.CHANGES_TICKET,
                PrinterControllerErrorMessages.ERROR_EXTEND_MESSAGE_INTERNAL_ERROR
            )
        except Exception as e:
            traceback.print_exc()
            mesage = PrinterControllerErrorMessages.UNKOWN_ERROR.value + e
        finally:
            return mesage

    def print_ticket(self,  folio: int, placa: str):
        """
        Imprime un boleto de entrada.

        Args:
            folio (int): Número de folio del boleto.
            placa (str): Número de placa del vehiculo.

        Returns:
            None
        """
        try:
            mesage = None
            printer = Printer(self.printer_idVendor, self.printer_idProduct)
            folio_cifrado = self.__instance_tools__.cifrar_folio(folio=folio)
            print(f"QR entrada: {folio_cifrado}")

            # Generar QR
            path = self.__instance_tools__.generar_QR(folio_cifrado)

            # Obtener la hora de entrada
            horaentrada = datetime.now()

            # Datos para el registro de la entrada
            corteNum = 0
            datos = (horaentrada.strftime(
                self.date_format_system), corteNum, placa)

            printer.set(height=self.size_font_boleto, align='center')
            printer.image(self.logo_empresa)
            printer.text("\nBOLETO DE ENTRADA\n")
            printer.text(f"ENTRADA -> {self.nombre_entrada}\n")
            printer.text("-" * 30 + "\n")
            printer.text(f'FOLIO 000{folio}\n')
            printer.text(
                f'Entro: {horaentrada.strftime(self.date_format_ticket)}\n')
            printer.text(f'Placas: {placa}\n')
            printer.image(path)
            printer.image(self.imagen_marcas_auto)
            printer.text("-" * 30 + "\n")
            printer.cut()

            if self.imprime_contra_parabrisas:
                printer.set(height=self.size_font_contra_parabrisas, align='center')
                printer.text("BOLETO PARABRISAS\n")
                printer.text(f'FOLIO 000{folio}\n')
                printer.text(
                    f'Entro: {horaentrada.strftime(self.date_format_ticket)}\n')
                printer.text(f'Placas:  {placa}\n')
                printer.set("left")

                if self.solicita_datos_del_auto:
                    printer.set(height=self.size_font_contra_parabrisas, align="left")
                    printer.text('Color:_____________________ \n')
                    printer.text('Marca:_____________________ \n')

                printer.cut()

            if self.imprime_contra_localizacion:
                printer.set(height=self.size_font_contra_localizacion, align='center')
                printer.text("BOLETO LOCALIZACION\n")
                printer.set(height=self.size_font_contra_localizacion, align='right')
                printer.text(f'FOLIO 000{folio}\n')
                printer.text(
                    f'Entro: {horaentrada.strftime(self.date_format_ticket)}\n')
                printer.text(f'Placas: {placa}\n')

                if self.solicita_datos_del_auto:
                    printer.set(height=self.size_font_contra_localizacion, align="left")
                    printer.text('Color:_____________________ \n')
                    printer.text('Marca:_____________________ \n')
                    printer.text("Lugar:_____________________ \n")

                printer.cut()

            printer.close()

            self.__DB__.altaRegistroRFID(datos)

        except (USBNotFoundError, NoBackendError) as e:
            type_error = PrinterControllerTypeErrorMessages.TICKET_ERROR
            error_message = PrinterControllerErrorMessages.ERROR_EXTEND_MESSAGE_INTERNAL_ERROR

            mesage = self.create_mesage_error(
                type_error,
                error_message)

        except Exception as e:
            traceback.print_exc()
            mesage = PrinterControllerErrorMessages.UNKOWN_ERROR.value + e
        finally:
            return mesage

    def print_lose_ticket(self, folio: int):
        """
        Imprime un boleto especial sin QR para poder cobrar boletos perdidos.

        Args:
            folio (int): Número de folio del boleto.

        Returns:
            None
        """
        try:
            mesage = None
            printer = Printer(self.printer_idVendor, self.printer_idProduct)
            printer.set(align="left")
            horaentrada = datetime.now()

            corteNum = 0
            placa = "BoletoPerdido"
            datos = (horaentrada.strftime(
                self.date_format_system), corteNum, placa)

            # aqui lo imprimimos

            printer.set(align="center")
            printer.image(self.logo_empresa)
            printer.text("-" * 30 + "\n")
            printer.text("B O L E T O  P E R D I D O\n")
            printer.text("BOLETO DE ENTRADA\n")
            printer.text(
                f'Entro: {horaentrada.strftime(self.date_format_ticket)}\n')
            printer.text(f'Placas {placa}\n')
            printer.text(f'Folio 000{folio}\n')
            printer.text("B O L E T O  P E R D I D O\n")
            printer.text("-" * 30 + "\n")

            printer.cut()
            printer.close()

            # Agregar registro del pago a la base de datos
            self.__DB__.altaRegistroRFID(datos)
        except (USBNotFoundError, NoBackendError) as e:
            mesage = self.create_mesage_error(
                PrinterControllerTypeErrorMessages.LOSE_TICKET_ERROR,
                PrinterControllerErrorMessages.ERROR_EXTEND_MESSAGE_INTERNAL_ERROR)

        except Exception as e:
            traceback.print_exc()
            mesage = PrinterControllerErrorMessages.UNKOWN_ERROR.value + e
        finally:
            return mesage

    def print_pension_pay_ticket(self,id: str,  Nom_cliente: str, Apell1_cliente: str, Apell2_cliente: str, fecha_pago: str, vigencia: str, monto: float, usuario: str, tipo_pago: str, title:str="Comprobante de pago"):
        """
        Imprime un comprobante de pago para una pension.

        Args:
            id (str): Identificacion única del pensionado.
            Nom_cliente (str): Nombre del pensionado.
            Apell1_cliente (str): Primer apellido del pensionado.
            Apell2_cliente (str): Segundo apellido del pensionado.
            fecha_pago (str): Fecha en que se realizo el pago.
            vigencia (str): Fecha de vigencia de la pension.
            monto (float): Monto pagado.
            usuario (str): Nombre del usuario que realizo el cobro.
            tipo_pago (str): Tipo de pago realizado.
            title (str): Titulo del comprobante, por defecto es "Comprobante de pago".

        Returns:
            None
        """
        try:
            mesage = None
            # NOTA: Refactorizar para que utilice una lista en vez de multiples parametros

            printer = Printer(self.printer_idVendor, self.printer_idProduct)
            # Establece la alineacion del texto al centro
            printer.set(align="center")

            # Agrega informacion sobre el pago al comprobante
            printer.image(self.logo_empresa)
            printer.text("-" * 30 + "\n")
            # Agrega un encabezado al comprobante
            printer.text(f"{title}\n\n")

            # Establece la alineacion del texto a la izquierda
            printer.set(align="left")

            printer.text(f"ID: {id.replace(' ', '_')}\n")
            printer.text(f"Nombre: {Nom_cliente}\n")
            printer.text(f"Apellido 1: {Apell1_cliente}\n")
            printer.text(f"Apellido 2: {Apell2_cliente}\n")
            printer.text(f"Fecha de pago: {fecha_pago}\n")
            printer.text(f"Monto pagado: ${monto}\n")
            printer.text(f"Tipo de pago: {tipo_pago}\n")
            printer.text(f"Cobro: {usuario}\n\n")
            printer.text(f"Fecha de vigencia: {vigencia}\n")

            printer.text("-" * 30 + "\n")

            # Corta el papel para finalizar la impresion
            printer.cut()
            printer.close()
        except (USBNotFoundError, NoBackendError) as e:
            mesage = self.create_mesage_error(
                PrinterControllerTypeErrorMessages.PENSION_PAY_TICKET,
                PrinterControllerErrorMessages.ERROR_EXTEND_MESSAGE_INTERNAL_ERROR)
        except Exception as e:
            traceback.print_exc()
            mesage = PrinterControllerErrorMessages.UNKOWN_ERROR.value + e
        finally:
            return mesage

    def print_cancel_ticket(self, folio: int, entrada: str, salida: str, motivo: str):
        """
        Imprime un comprobante para un boleto cancelado con la informacion proporcionada.

        Args:
            folio (int): Número de folio del boleto cancelado.
            entrada (str): Hora de entrada del boleto.
            salida (str): Hora de salida del boleto (si aplica).
            motivo (str): Motivo de la cancelacion.

        Returns:
            None
        """
        try:
            mesage = None
            printer = Printer(self.printer_idVendor, self.printer_idProduct)
            printer.set(align="center")
            printer.text(f"Boleto Cancelado\n")

            # Seccion de comprobante para boletos cancelados
            printer.set(align="left")

            printer.text(f'Folio: {folio}\n')
            printer.text(f'Entrada: {entrada}\n')
            printer.text(f'Salida: {salida}\n')
            printer.text(f'Motivo: {motivo}\n')

            # Corta el papel para finalizar la impresion
            printer.cut()
            printer.close()
        except (USBNotFoundError, NoBackendError) as e:
            mesage = self.create_mesage_error(
                PrinterControllerTypeErrorMessages.CANCEL_TICKET,
                PrinterControllerErrorMessages.ERROR_EXTEND_MESSAGE_INTERNAL_ERROR)
        except Exception as e:
            traceback.print_exc()
            mesage = PrinterControllerErrorMessages.UNKOWN_ERROR.value + e
        finally:
            return mesage

    def print_payment_ticket(self, data: list):
        """
        Imprime un comprobante de pago con la informacion proporcionada.

        Args:
            data (list): Lista con la informacion del pago, incluyendo Placa, Folio,
                        TarifaPreferente, Importe, Entrada, Salida, y TiempoTotal.

        Returns:
            None
        """
        try:
            mesage = None
            printer = Printer(self.printer_idVendor, self.printer_idProduct)

            # Obtiene los valores de diferentes variables desde las variables de control
            Placa = data[0]
            Folio = data[1]
            TarifaPreferente = data[2]
            Importe = data[3]
            Entrada = data[4]
            Salida = data[5]
            TiempoTotal = data[6]

            printer.set(align="center")

            printer.text('Comprobante de pago\n')

            valor = 'N/A'

            if Placa == "BoletoPerdido":
                # Si es un boleto perdido, muestra un mensaje especial
                printer.text("BOLETO PERDIDO\n")
                Entrada = valor
                Salida = valor
                TiempoTotal = valor

            # Imprimir el logo
            printer.image(self.logo_empresa)
            print("Imprime logo")

            printer.set(align="left")
            printer.text(f"\nEl importe es: ${Importe}\n")
            printer.text(f'El auto entro: {Entrada}\n')
            printer.text(f'El auto salio: {Salida}\n')
            printer.text(f'El auto permanecio: {TiempoTotal}\n')
            printer.text(f'El folio del boleto es: {Folio}\n')
            printer.text(f'TIPO DE COBRO: {TarifaPreferente}\n')
            printer.cut()

            printer.set(align="center")
            printer.text('CONTRA\n')

            printer.set(align="left")
            printer.text(f"El importe es: ${Importe}\n")
            printer.text(f'El auto entro: {Entrada}\n')
            printer.text(f'El auto salio: {Salida}\n')
            printer.text(f'El auto permanecio: {TiempoTotal}\n')
            printer.text(f'El folio del boleto es: {Folio}\n')
            printer.text(f'TIPO DE COBRO: {TarifaPreferente}\n')
            printer.cut()

            if self.imprime_contra_localizacion:
                printer.set(align="center")
                printer.text('CHOFER\n')

                printer.set(align="left")
                printer.text(f"El importe es: ${Importe}\n")
                printer.text(f'El auto entro: {Entrada}\n')
                printer.text(f'El auto salio: {Salida}\n')
                printer.text(f'El auto permanecio: {TiempoTotal}\n')
                printer.text(f'El folio del boleto es: {Folio}\n')
                printer.text(f'TIPO DE COBRO: {TarifaPreferente}\n')
                printer.cut()

            printer.close()
        except (USBNotFoundError, NoBackendError) as e:
            mesage = self.create_mesage_error(
                PrinterControllerTypeErrorMessages.PAYMENT_TICKET,
                PrinterControllerErrorMessages.ERROR_EXTEND_MESSAGE_INTERNAL_ERROR
            )
        except Exception as e:
            traceback.print_exc()
            mesage = PrinterControllerErrorMessages.UNKOWN_ERROR.value + e
        finally:
            return mesage

    def re_print_payment_ticket(self, data: list):
        """
        Reimprime un comprobante de pago con informacion ya guardada en la base de datos.

        Args:
            data (list): Lista con la informacion del pago, incluyendo Placa, Folio,
                        TarifaPreferente, Importe, Entrada, Salida, TiempoTotal, y Motivo
                        (en caso de ser un boleto cancelado).

        Returns:
            None
        """
        try:
            mesage = None
            printer = Printer(self.printer_idVendor, self.printer_idProduct)

            # Obtiene los valores de diferentes variables desde las variables de control
            Placa = data[0]
            Folio = data[1]
            TarifaPreferente = data[2]
            Importe = data[3]
            Entrada = data[4]
            Salida = data[5]
            TiempoTotal = data[6]
            Motivo = data[7]

            printer.set(align="center")

            printer.text('Reimpresion de comprobante')

            valor = 'N/A'

            if Placa == "BoletoPerdido":
                # Si es un boleto perdido, muestra un mensaje especial
                printer.text("BOLETO PERDIDO\n")
                Entrada = valor
                Salida = valor
                TiempoTotal = valor

            # Imprimir el logo
            printer.image(self.logo_empresa)
            print("Imprime logo")

            printer.set(align="left")
            printer.text(f"El importe es: ${Importe}\n")
            printer.text(f'El auto entro: {Entrada}\n')
            printer.text(f'El auto salio: {Salida}\n')
            printer.text(f'El auto permanecio: {TiempoTotal}\n')
            printer.text(f'El folio del boleto es: {Folio}\n')
            printer.text(f'Tipo de cobro: {TarifaPreferente}\n')

            if TarifaPreferente == "CDO":
                print("")
                printer.text(f'Motivo: {Motivo}\n')

            printer.cut()
            printer.close()
        except (USBNotFoundError, NoBackendError) as e:
            mesage = self.create_mesage_error(
                PrinterControllerTypeErrorMessages.RE_PAYMENT_TICKET,
                PrinterControllerErrorMessages.ERROR_EXTEND_MESSAGE_INTERNAL_ERROR
            )
        except Exception as e:
            traceback.print_exc()
            mesage = PrinterControllerErrorMessages.UNKOWN_ERROR.value + e
        finally:
            return mesage

    def print_entradas_sin_corte(self, data: tuple):
        """
        Imprime la informacion de las entradas sin corte.

        Args:
            data (tuple): Tupla con informacion de entradas, cada fila contiene
                        el Folio, Hora de Entrada y Hora de Salida (si aplica) y
                        el Importe.

        Returns:
            None
        """
        try:
            mesage = None
            printer = Printer(self.printer_idVendor, self.printer_idProduct)
            printer.set(align="left")
            for fila in data:
                print("")
                printer.text(f"Folio: {fila[0]}\n")
                printer.text(
                    f"Entro: {fila[1].strftime(self.date_format_ticket)}\n")
                printer.text(
                    f"Salio: {fila[2].strftime(self.date_format_ticket) if fila[2] != None else ''}\n")
                printer.text(f"Importe: {fila[3]}\n\n")

            printer.cut()
            printer.close()
        except (USBNotFoundError, NoBackendError) as e:
            mesage = self.create_mesage_error(
                PrinterControllerTypeErrorMessages.NONE_MESAGE,
                PrinterControllerErrorMessages.ERROR_EXTEND_MESSAGE_INTERNAL_ERROR
            )
        except Exception as e:
            traceback.print_exc()
            mesage = PrinterControllerErrorMessages.UNKOWN_ERROR.value + e
        finally:
            return mesage

    def print_QR_pension(self, id: str, placas: str, nombre: str, auto_modelo: str):
        """
        Imprime un codigo QR relacionado con la pension.

        Args:
            id (str): Identificacion única del pensionado.
            placas (str): Número de placas del auto asociado a la pension.
            nombre (str): Nombre del propietario de la pension.
            auto_modelo (str): Modelo del auto asociado a la pension.

        Returns:
            None
        """
        try:
            mesage = None
            printer = Printer(self.printer_idVendor, self.printer_idProduct)
            QR = f"Pension-{self.nombre_estacionamiento}-{id}".replace(
                ' ', '_')

            name_image = f"{QR}_{placas}_{nombre}.png".replace(' ', '_')
            path = f"./Public/QR_pensiones/{name_image}"

            self.__instance_tools__.generar_QR(
                QR_info=QR, path=path, zise=(600, 600))

            qr_pension = './Public/Img/QR_pension.png'
            self.__instance_tools__.generar_QR(QR_info=QR, path=qr_pension)

            # Instanciar el objeto Printer para imprimir el resultado

            # Alinea al centro el texto
            printer.set(align="center")
            printer.text("QR de pension\n")
            # Imprimir separadores y mensaje de resultado en la consola
            printer.text("-" * 30 + "\n")
            printer.image(qr_pension)
            print("imprime QR")
            printer.text("-" * 30 + "\n")
            printer.text(f"Placas: {placas}\n")
            printer.text(f"Modelo: {auto_modelo}\n")
            printer.text(f"Nombre: {nombre}\n")
            printer.text(f"ID: {QR}\n")
            printer.cut()
            printer.close()
        except (USBNotFoundError, NoBackendError) as e:
            mesage = self.create_mesage_error(
                PrinterControllerTypeErrorMessages.QR_PENSION,
                PrinterControllerErrorMessages.ERROR_EXTEND_MESSAGE_INTERNAL_ERROR
            )
        except Exception as e:
            traceback.print_exc()
            mesage = PrinterControllerErrorMessages.UNKOWN_ERROR.value + e
        finally:
            return mesage

    def print_state_send_data(self, message_send_database: str, message_send_corte: str):
        """
        Imprime el estado del envio de datos.

        Args:
            message_send_database (str): Mensaje del estatus de envio de datos a la base de datos.
            message_send_corte (str): Mensaje del estatus de envio del corte.
        """
        try:
            mesage = None
            # Instancia el objeto Printer para imprimir el resultado
            printer = Printer(self.printer_idVendor, self.printer_idProduct)

            # Alinea el texto al centro
            printer.set(align="center")

            # Imprime separadores y mensajes de resultado en la consola
            printer.text("-" * 30 + "\n")
            printer.text(f"{message_send_database}\n")
            printer.text(f"{message_send_corte}\n")
            printer.text("-" * 30 + "\n")
            printer.cut()
            printer.close()
        except (USBNotFoundError, NoBackendError) as e:
            mesage = self.create_mesage_error(
                PrinterControllerTypeErrorMessages.STATE_SEND_DATA,
                PrinterControllerErrorMessages.ERROR_EXTEND_MESSAGE_INTERNAL_ERROR
            )
        except Exception as e:
            traceback.print_exc()
            mesage = PrinterControllerErrorMessages.UNKOWN_ERROR.value + e
        finally:
            return mesage

    def create_mesage_error(self, type_mesage_error: PrinterControllerTypeErrorMessages, mesage_error: PrinterControllerErrorMessages) -> str:
        """
        Crea un mensaje de error combinando el tipo de error y el mensaje de error proporcionados.

        Args:
            type_mesage_error (PrinterControllerTypeErrorMessages): Tipo de error.
            mesage_error (PrinterControllerErrorMessages): Mensaje de error.

        Returns:
            str: Mensaje de error concatenado.
        """
        return type_mesage_error.value + " " + mesage_error.value
   