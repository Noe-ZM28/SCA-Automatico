import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from escpos.printer import Usb
from os import path, getcwd, listdir

from .ConfigController import ConfigController
from Tools.Tools import Tools


class SendEmail:
    """
    Clase que permite enviar correos electronicos con archivos adjuntos.

    Esta clase proporciona funcionalidades para enviar correos electronicos con archivos adjuntos,
    utilizando un servidor SMTP especificado. Requiere credenciales de inicio de sesion para el servidor.

    Atributos:
        username (str): Nombre de usuario para la cuenta de correo electronico.
        password (str): Contraseña para la cuenta de correo electronico.
        iv (str): Vector de inicializacion para descifrar la contraseña.
        smtp_server (str): Servidor SMTP para el envio de correos electronicos.
        smtp_port (int): Puerto del servidor SMTP.

    Metodos:
        send_mail: Envia un correo electronico con un archivo adjunto.

    Ejemplo:
        >>> send_email = SendEmail(username='tu_correo@gmail.com', password='tu_contraseña', iv='tu_vector_inicializacion')
        >>> send_email.send_mail(to_email='destinatario@gmail.com', subject='Asunto del correo', message='Cuerpo del correo', zip_file='ruta_al_archivo_adjunto.zip')
    """

    def __init__(self, username: str, password: str, iv: str, smtp_server: str = "smtp.pasesa.com.mx", smtp_port: int = 1025) -> None:
        """
        Inicializa una instancia de la clase SendEmail para enviar correos electronicos con archivos adjuntos.

        Args:
            username (str): El nombre de usuario para la cuenta de correo electronico.
            password (str): La contraseña para la cuenta de correo electronico.
            iv (str): El vector de inicializacion para descifrar la contraseña.
            smtp_server (str, opcional): El servidor SMTP para el envio de correos. Por defecto es "smtp.pasesa.com.mx".
            smtp_port (int, opcional): El puerto del servidor SMTP. Por defecto es 1025.
        """
        self.username = username
        self.password = password
        self.iv = iv
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.instance_tools = Tools()

    def send_mail(self, to_email, subject: str, message: str, zip_file: str = None) -> bool:
        """
        Envia un correo electronico con un archivo adjunto.

        Args:
            to_email (str | list): La direccion de correo electronico del destinatario(s).
            subject (str): El asunto del correo electronico.
            message (str): El contenido del correo electronico.
            zip_file (str | None) (Opcional): Ruta al archivo .zip que se adjuntará al correo.

        Returns:
            bool: True si el correo se envia exitosamente, False si hay algún error.
        """
        from_email = self.username

        # Verificar la conexion a Internet antes de intentar enviar el correo
        if not self.instance_tools.check_internet_connection():
            return False

        try:
            # Crea la estructura del correo
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = ", ".join(to_email) if isinstance(
                to_email, list) else to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))
            
            if zip_file != None:
                # Adjuntar el archivo al correo
                with open(zip_file, 'rb') as f:
                    attached_file = MIMEApplication(f.read(), _subtype="zip")
                    filename = path.basename(zip_file)
                    # print(filename)
                    attached_file.add_header(
                        'content-disposition', 'attachment', filename=filename)
                    msg.attach(attached_file)

            # Conectar al servidor SMTP y enviar el correo
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                # Iniciar la conexion segura TLS
                server.starttls()
                # Inicio de sesion
                server.login(
                    self.username, self.instance_tools.descifrar_AES(self.password, bytes.fromhex(self.iv)))
                # Enviar correo
                server.sendmail(from_email, to_email, msg.as_string())
                # Terminar la sesion
                server.quit()

            print('Correo enviado exitosamente')
            return True

        except Exception as e:
            print(e)
            return False


class SendData(SendEmail):
    """
    Clase que hereda de SendEmail y se especializa en enviar datos especificos por correo electronico.

    Esta clase extiende la funcionalidad de SendEmail para enviar datos especificos,
    como copias de seguridad de la base de datos y cortes del estacionamiento.

    Metodos:
        - send_database: Envia la base de datos por correo electronico.
        - send_corte: Envia los cortes del estacionamiento por correo electronico.
        - send_other_corte: Envia notificacion de la reimpresion de un corte por correo electronico.
    """

    def __init__(self) -> None:
        """
        Inicializa una instancia de la clase SendData.

        La clase hereda de SendEmail y utiliza la configuracion proporcionada por ConfigController.
        """

        self.instance_tools = Tools()
        instance_config = ConfigController()

        # Nombre del estacionamiento
        self.nombre_estacionamiento = instance_config.get_config(
            "general", "informacion_estacionamiento", "nombre_estacionamiento")

        # Datos de acceso a la cuenta de correo
        data = instance_config.get_config(
            "general", "informacion_estacionamiento")
        self.username = data["email"]
        self.password = data["password"]
        self.iv = data["iv"]

        # Correos para enviar la informacion
        data = instance_config.get_config(
            "general", "configuiracion_envio")
        self.EMAIL_send_database = data["destinatario_DB"]
        self.EMAIL_send_corte = data["destinatario_corte"]
        self.EMAIL_notification = data["destinatario_notificaciones"]
        data = None

        self.is_send_database = False
        self.is_send_corte = False

    def send_database(self) -> str:
        """
        Envia el corte por correo electronico.

        Returns:
            str: Mensaje informativo sobre el resultado del envio del correo.
        """
        try:
            if self.EMAIL_send_database == "":
                return "Error: No se puede enviar la base de datos\nConfigure correo electronico de envio de DB e intente nuevamente"

            email_database = SendEmail(
                username=self.username,
                password=self.password,
                iv=self.iv)

            # Generar ruta y obtener el archivo de respaldo de la base de datos
            path_db = getcwd() + \
                f'/db_{self.nombre_estacionamiento}.sql'.replace(" ", "_")
            db_file = self.instance_tools.get_DB(path_db)

            if db_file is None:
                return "Error: No se pudo generar el respaldo de la base de datos\n"

            zip_file = self.instance_tools.compress_to_zip(db_file)
            if zip_file is None:
                return "Error: No se pudo generar el respaldo de la base de datos\n"

            self.instance_tools.remove_file(db_file)

            # Crear el asunto y mensaje del correo
            hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subject = f"[{self.nombre_estacionamiento}][{hora}] Envio de Base de datos"
            message = f"Base de datos del estacionamiento: {self.nombre_estacionamiento}."

            # Enviar el correo y manejar el resultado
            if email_database.send_mail(to_email=self.EMAIL_send_database, subject=subject, message=message, zip_file=zip_file) == False:
                self.instance_tools.remove_file(zip_file)
                return "Error: No se pudo enviar la base de datos\n"

            self.instance_tools.remove_file(zip_file)
            return "Base de datos enviada exitosamente\n"

        except Exception as e:
            print(e)
            self.instance_tools.remove_file(zip_file)
            return "Error: No se pudo enviar la base de datos\n"

    def send_corte(self) -> str:
        """
        Envia la base de datos por correo electronico.

        Returns:
            str: Mensaje informativo sobre el resultado del envio del correo.
        """
        try:
            if len(self.EMAIL_send_corte) == 0:
                return "Error: No se puede enviar el corte\nConfigure correo electronico de envio de cortes"
            
            dir_path = path.abspath("./Public/Cortes")
            files = listdir(dir_path)
            if len(files) == 1:
                return "No hay cortes para enviar\n"

            # Inicializar herramientas de correo electronico y envio
            email_corte = SendEmail(
                username=self.username,
                password=self.password,
                iv=self.iv)

            zip_file = self.instance_tools.compress_to_zip(
                source=dir_path, is_dir=True)

            # Crear el asunto y mensaje del correo
            hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subject = f"[{self.nombre_estacionamiento}]-[{hora}] Envio de {path.basename(zip_file).replace('_', ' ')[:-4]}"
            message = f"Corte del estacionamiento: {self.nombre_estacionamiento}."

            # Enviar el correo y manejar el resultado
            if email_corte.send_mail(to_email=self.EMAIL_send_corte, subject=subject, message=message, zip_file=zip_file):
                self.instance_tools.remove_file(zip_file)

                for id, file in enumerate(files):
                    file_path = path.join(dir_path, file)
                    _, ext = path.splitext(file)
                    if ext.lower() == ".txt":
                        self.instance_tools.remove_file(file_path)

                return "Corte enviado exitosamente\n"

        except Exception as e:
            print(e)
            self.instance_tools.remove_file(zip_file)
            return "Error: No se pudo enviar el corte\n"

    def send_other_corte(self):
        """
        Envia notificacion de la reimpresion de un corte por correo electronico.

        Returns:
            str: Mensaje informativo sobre el resultado del envio del correo.
        """
        if len(self.EMAIL_notification) == 0:
            return

        dir_path = path.abspath("./Public/Reimpresion_Cortes/")
        files = listdir(dir_path)
        if len(files) == 0:
            return

        # Inicializar herramientas de correo electronico y envio
        email_corte = SendEmail(
            username=self.username,
            password=self.password,
            iv=self.iv)

        zip_file = self.instance_tools.compress_to_zip(
            source=dir_path, is_dir=True, rename=False)

        # Crear el asunto y mensaje del correo
        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"[{self.nombre_estacionamiento}]-[{hora}] Notificacion de reimpresion de corte"
        message = f"Notificacion de reimpresion de corte del estacionamiento: {self.nombre_estacionamiento}."

        # Enviar el correo y manejar el resultado
        email_corte.send_mail(to_email=self.EMAIL_notification,
                              subject=subject, message=message, zip_file=zip_file)

        self.instance_tools.remove_file(zip_file)

    def send_system_notification(self, message:str):
        """
        Envia notificacion del sistema por correo electronico.

        Args:
            message(str): Mensaje a enviar.
        
        Returns:
            str: Mensaje informativo sobre el resultado del envio del correo.
        """
        if len(self.EMAIL_notification) == 0:
            return

        # Inicializar herramientas de correo electronico y envio
        email_corte = SendEmail(
            username=self.username,
            password=self.password,
            iv=self.iv)

        # Crear el asunto y mensaje del correo
        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"[{self.nombre_estacionamiento}]-[{hora}] Notificacion del sistema"

        # Enviar el correo y manejar el resultado
        email_corte.send_mail(to_email=self.EMAIL_notification,
                              subject=subject, message=message)







