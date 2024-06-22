from enum import Enum


class PrinterControllerErrorMessages(Enum):
    """
    Enums que define los mensajes de error para la clase PrinterController.
    """
    ERROR_EXTEND_MESSAGE_INTERNAL_ERROR: str = "\n\n\tError: Impresora apagada o desconectada.\nPasos a seguir:\n1) Verifique que la impresora este encendida.\n2) Verifique que la impresora este conectada correctamente.\n3) Reinicie el sistema.\n4) En caso de que se siga mostrando este mensaje de error apague y encienda nuevamente la computadora.\n\n5) En caso de no solucionarse el error contacte inmediatamente con un administrador, si este ya se encuentra con usted pida que verifique la configuracion de la impresora dentro del panel de configuracion y que sea visible el nombre de una impresora en caso contrario que seleccione una."
    ERROR_SIMPLE_MESSAGE_INTERNAL_ERROR: str = "Impresora apagada o desconectada, reiniciar"
    UNKOWN_ERROR = "Error desconocido, contacte con un administrador y muestre el siguiente error: "

    NONE_MESAGE: str = ""


class PrinterControllerTypeErrorMessages(Enum):
    """
    Enums que define los tipos de errores para la clase PrinterController.
    """
    TICKET_ERROR: str = "No se puede imprimir boleto"
    LOSE_TICKET_ERROR: str = "No se puede imprimir boleto perdido"
    PENSION_EXIT_TICKET: str = "No se puede imprimir comprobante de salida de pensionado"
    PENSION_ENTER_TICKET: str = "No se puede imprimir comprobante de entrada de pensionado"
    PENSION_PAY_TICKET: str = "No se puede imprimir comprobante de pago de pension"
    CANCEL_TICKET: str = "No se puede imprimir comprobante de cancelacion de boleto"
    PAYMENT_TICKET: str = "Se realiza registro de pago, pero no se puede imprimir comprobante de pago"
    RE_PAYMENT_TICKET: str = "No se puede reimprimir comprobante de pago"
    QR_PENSION: str = "No se puede imprimir QR de pensionado"
    STATE_SEND_DATA: str = "No se puede imprimir comprobante de envio"
    CHANGES_TICKET: str = "No se pueden imprimir la lista de cambios"

    NONE_MESAGE: str = ""
