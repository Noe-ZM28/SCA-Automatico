from .ConfigController import ConfigController


class CobroController:
    def __init__(self):
        self.instance_config = ConfigController()
        # Configuracion de tarifas
        data_config = self.instance_config.get_config("tarifa")

        self.tipo_tarifa_sistema = data_config["tipo_tarifa_sistema"]
        self.tarifa_boleto_perdido = data_config["tarifa_boleto_perdido"]

        self.tarifa_1_fraccion = data_config["tarifa_simple"]["tarifa_1_fraccion"]
        self.tarifa_2_fraccion = data_config["tarifa_simple"]["tarifa_2_fraccion"]
        self.tarifa_3_fraccion = data_config["tarifa_simple"]["tarifa_3_fraccion"]
        self.tarifa_hora = data_config["tarifa_simple"]["tarifa_hora"]
        self.inicio_cobro_fraccion = data_config["tarifa_simple"]["inicio_cobro_fraccion"]

        importe_dia_completo = self.tarifa_hora * 24
        importe_dia_completo_tarifa_personalizada = data_config["tarifa_personalizada"]["24"]["hora"]

        self.day_price = importe_dia_completo if self.tipo_tarifa_sistema else importe_dia_completo_tarifa_personalizada

    def get_importe_tarifa(self, minutos_dentro:int, horas_dentro:int, dias_dentro:int) -> int:
        importe = 0
        if self.tipo_tarifa_sistema:
            # Calcula la tarifa y el importe a pagar
            importe_cuarto_hora = 0
            if minutos_dentro == 0:
                importe_cuarto_hora = 0
            elif minutos_dentro < 16 and minutos_dentro >= 1:
                importe_cuarto_hora = self.tarifa_1_fraccion
            elif minutos_dentro < 31 and minutos_dentro >= 16:
                importe_cuarto_hora = self.tarifa_2_fraccion
            elif minutos_dentro < 46 and minutos_dentro >= 31:
                importe_cuarto_hora = self.tarifa_3_fraccion
            else:
                importe_cuarto_hora = self.tarifa_hora

            inicio_cobro_fraccion = self.inicio_cobro_fraccion - 1

            if dias_dentro == 0 and horas_dentro < inicio_cobro_fraccion:
                importe = self.tarifa_hora * horas_dentro if horas_dentro > 0 else self.tarifa_hora
            else:
                importe = (dias_dentro * self.day_price) + (horas_dentro * self.tarifa_hora) + importe_cuarto_hora
                if horas_dentro == 0 and minutos_dentro == 0 and dias_dentro == 0:
                    importe = self.tarifa_1_fraccion

            return importe

        else:
            # Calcula la tarifa y el importe a pagar
            if minutos_dentro == 0:
                importe_cuarto_hora = "hora"
            elif minutos_dentro < 16 and minutos_dentro >= 1:
                importe_cuarto_hora = "1"
            elif minutos_dentro < 31 and minutos_dentro >= 16:
                importe_cuarto_hora = "2"
            elif minutos_dentro < 46 and minutos_dentro >= 31:
                importe_cuarto_hora = "3"
            else:
                importe_cuarto_hora = "hora"
                horas_dentro +=1

            importe_dia_completo = self.day_price * dias_dentro

            importe = self.instance_config.get_config("tarifa", "tarifa_personalizada", str(horas_dentro), importe_cuarto_hora) + importe_dia_completo

        return importe

    def get_importe_promo(self, promo_id:str, minutos_dentro:int, horas_dentro:int, dias_dentro:int) -> tuple[int, str]:
        importe = 0
        data_config = self.instance_config.get_config("promociones", promo_id)
        tipo_tarifa = data_config["tipo_tarifa"]
        nombre_promo = data_config["real_name"]

        if tipo_tarifa:
            inicio_cobro_fraccion = data_config["inicio_cobro_fraccion"]
            tarifa_1_fraccion = data_config["tarifa_1_fraccion"]
            tarifa_2_fraccion = data_config["tarifa_2_fraccion"]
            tarifa_3_fraccion = data_config["tarifa_3_fraccion"]
            tarifa_hora = data_config["tarifa_hora"]

            # Calcula la tarifa y el importe a pagar
            importe_cuarto_hora = 0
            if minutos_dentro == 0:
                importe_cuarto_hora = 0
            elif minutos_dentro < 16 and minutos_dentro >= 1:
                importe_cuarto_hora = tarifa_1_fraccion
            elif minutos_dentro < 31 and minutos_dentro >= 16:
                importe_cuarto_hora = tarifa_2_fraccion
            elif minutos_dentro < 46 and minutos_dentro >= 31:
                importe_cuarto_hora = tarifa_3_fraccion
            else:
                importe_cuarto_hora = tarifa_hora

            inicio_cobro_fraccion = inicio_cobro_fraccion - 1

            if dias_dentro == 0 and horas_dentro < inicio_cobro_fraccion:
                importe = tarifa_hora * horas_dentro if horas_dentro > 0 else tarifa_hora
            else:
                importe = (dias_dentro * self.day_price) + (horas_dentro * tarifa_hora) + importe_cuarto_hora
                if horas_dentro == 0 and minutos_dentro == 0:
                    importe = tarifa_1_fraccion
                    
            importe = 0 if tarifa_hora == 0 else importe

        else:
            if minutos_dentro == 0:
                importe_cuarto_hora = "hora"
            elif minutos_dentro < 16 and minutos_dentro >= 1:
                importe_cuarto_hora = "1"
            elif minutos_dentro < 31 and minutos_dentro >= 16:
                importe_cuarto_hora = "2"
            elif minutos_dentro < 46 and minutos_dentro >= 31:
                importe_cuarto_hora = "3"
            else:
                importe_cuarto_hora = "hora"
                horas_dentro +=1

            importe_dia_completo = self.day_price * dias_dentro
            importe = data_config[str(horas_dentro)][importe_cuarto_hora]

            importe = importe + importe_dia_completo

        data_config = None

        return importe, nombre_promo


