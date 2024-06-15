from Controllers.ConfigController import ConfigController
__instance_config__ = ConfigController()
from tkinter import messagebox as mb

def main():
    """
    Funcion principal para cargar el sistema según la configuracion.
    """
    try:
        # Obtener el sistema a cargar desde la configuracion
        system_to_load = __instance_config__.get_config("system_to_load")

        if system_to_load == 0:
            # Importar la clase del sistema de cobro
            #from Views.ViewCobro import ViewCobro as System
            from Views.ViewLoginSystem import LoginSystem as System

        elif system_to_load == 1:
            # Importar la clase del sistema de entrada
            from Views.ViewEntrada import ViewEntrada as System

        else:
            # Importar la clase del sistema de seleccion
            from Views.ViewLoginPanelConfig import View_Login as System

        # Iniciar el sistema
        System()

    except FileNotFoundError as e:
        if mb.askyesno("Error", "No existe archivo de configuracion en el sistema, ¿cuenta con algun archivo de configuración?"):
            __instance_config__.replace_config_file()
        
        mb.showinfo("Advertencia", "El sistema cargará la configuración por defecto, posterior a ello asegurece de hacer las configuraciones permitentes para el correcto funcionamiento del sistema de acuerdo a sus necesidades")
        __instance_config__.load_default_config_file()

    except Exception as e:
        mb.showerror("Error inesperado, contacte inmediatamente con un administrador y muestre el siguiente mensaje de error: ", f"{e}")

if __name__ == "__main__":
    # Ejecutar la funcion main si este script es el punto de entrada
    main()

