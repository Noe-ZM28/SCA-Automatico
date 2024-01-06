
from datetime import datetime, time, timedelta
from escpos.printer import *
import traceback
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext as st

import operacion
from time import sleep
import RPi.GPIO as io           # Importa libreria de I/O (entradas / salidas)

loop = 21                      #gpio5,pin29,entrada loop                    
boton = 20                     #gpio6,pin31,entrada boton
SenBBoleto = 16                #gpio13,pin33,sensor boleto
barrera = 17                  #gpio17,pin11,Salida barrera
out1 = 22                     #gpio22,pin15,Salida indicador loop
out2 = 18                     #gpio18,pin12,Salida indicador boton
out3 = 27                     #gpio27,pin13,Salida indicador barrera

io.setmode(io.BCM)              # modo in/out pin del micro
io.setwarnings(False)           # no señala advertencias de pin ya usados
io.setup(loop,io.IN)             # configura en el micro las entradas
io.setup(boton,io.IN)             # configura en el micro las entradas
io.setup(SenBBoleto,io.IN)             # configura en el micro las entradas
io.setup(barrera,io.OUT)           # configura en el micro las salidas
io.setup(out1,io.OUT)           # configura en el micro las salidas
io.setup(out2,io.OUT)
io.setup(out3,io.OUT)  

io.output(barrera,1)
io.output(out1,1)
io.output(out2,1)
io.output(out3,1)

BanLoop =1
BanBoton=1
BanSenBoleto=0
BanImpresion=0 #No ha impreso

logo_1 = "LOGO1.jpg"
AutoA = "AutoA.png"
qr_imagen = "reducida.png"

# Configuracion de las entradas y las salidas del micro
# -----------------------------------------------------
class FormularioOperacion:
    def __init__(self):
        #creamos un objeto que esta en el archivo operacion dentro la clase Operacion
        self.DB=operacion.Operacion()
        self.ventana1=tk.Tk()
        self.ventana1.title("BOLETERA DE ENTRADA")
        self.ventana1.configure(bg = 'blue')
        self.cuaderno1 = ttk.Notebook(self.ventana1)
        self.cuaderno1.config(cursor="")         # Tipo de cursor
        self.ExpedirRfid()
        self.check_inputs()

        self.IntBoton()
        self.Intloop()
        self.cuaderno1.grid(column=0, row=0, padx=5, pady=5)
        self.ventana1.mainloop()
    ###########################Inicia Pagina1##########################
# Funcion de lectura de las entradas
# -----------------------------------
    def ExpedirRfid(self):    
        self.pagina1 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina1, text="Expedir Boleto")
        #enmarca los controles LabelFrame
        self.labelframe1=ttk.LabelFrame(self.pagina1, text="Dar Entrada")
        self.labelframe1.grid(column=1, row=0, padx=0, pady=0)
        self.Adentroframe=ttk.LabelFrame(self.pagina1, text="Autos DENTRO")
        self.Adentroframe.grid(column=2, row=0, padx=0, pady=0)
        self.MaxId=tk.StringVar()
        self.entryMaxId=ttk.Entry(self.labelframe1, width=10, textvariable=self.MaxId, state="readonly")
        self.entryMaxId.grid(column=1, row=0, padx=4, pady=4)
        self.lbltitulo=ttk.Label(self.labelframe1, text="FOLIO")
        self.lbltitulo.grid(column=0, row=0, padx=0, pady=0)
        self.presenciaAuto = ttk.Label(self.labelframe1, text="TIPO DE ENTRADA", width = 17)#, background = '#CCC')
        self.presenciaAuto.grid(column=0, row=6, padx=0, pady=0)
        self.loopDet = ttk.Label(self.pagina1, text="siente auto", width = 17)#, background = '#FD6')
        self.loopDet.grid(column=1, row=8, padx=0, pady=0)
        self.BotDet = ttk.Label(self.pagina1, text="Boton", width = 17)#, background = '#CCC')
        self.BotDet.grid(column=1, row=12, padx=0, pady=0)
        self.SenBol = ttk.Label(self.pagina1, text="Sensor Boleto", width = 17)#, background = '#CCC')
        self.SenBol.grid(column=1, row=13, padx=0, pady=0)
        
        #self.Reloj = ttk.Label(self.pagina1, text="Hora y fecha", width = 10, background = '#FD6')
        #self.Reloj.grid(column=0, row=6, padx=0, pady=0)

        self.Reloj = ttk.Label(self.pagina1, text="Reloj") #Creación del Label
        self.Reloj.config(width =10)
        self.Reloj.config(background="white") #Cambiar color de fondo
        self.Reloj.config(font=('Arial', 80)) #Cambiar tipo y tamaño de fuente
        self.Reloj.grid(column=1, row=4, padx=0, pady=0)   
        
        self.mi_reloj = ttk.Label(self.pagina1, text="Reloj") #Creación del Label
        self.mi_reloj.config(width =10)
        self.mi_reloj.config(background="white") #Cambiar color de fondo
        self.mi_reloj.config(font=('Arial', 80)) #Cambiar tipo y tamaño de fuente
        self.mi_reloj.grid(column=1, row=6, padx=0, pady=0)        
        #####tomar placas del auto
        self.Placa=tk.StringVar()
        self.entryPlaca=tk.Entry(self.labelframe1, width=15, textvariable=self.Placa)
        self.entryPlaca.grid(column=1, row=1, padx=4, pady=4)
        self.lblPlaca=ttk.Label(self.labelframe1, text="COLOCAR PLACAS")
        self.lblPlaca.grid(column=0, row=1, padx=0, pady=0)

        self.labelhr=ttk.Label(self.labelframe1, text="HORA ENTRADA")
        self.labelhr.grid(column=0, row=2, padx=0, pady=0)

        self.scrolledtext=st.ScrolledText(self.Adentroframe, width=20, height=3)
        self.scrolledtext.grid(column=1,row=0, padx=4, pady=4)
        self.Autdentro=tk.Button(self.Adentroframe, text="Boletos sin Cobro", command=self.Autdentro, width=15, height=1, anchor="center")
        self.Autdentro.grid(column=2, row=0, padx=4, pady=4)
        self.labeRFID=ttk.Label(self.Adentroframe, text="LECTURA RFID")
        self.labeRFID.grid(column=1, row=3, padx=0, pady=0)
        self.RFID=tk.StringVar()
        self.entryRFID=tk.Entry(self.Adentroframe, width=20, textvariable=self.RFID)
        self.entryRFID.grid(column=1, row=1, padx=4, pady=4)
        self.botonPent=tk.Button(self.Adentroframe, text="DeclararlaEnt", command= self.check_inputs, width=15, height=1, anchor="center")
        self.botonPent.grid(column=2, row=1, padx=4, pady=4)            
 

        self.boton1=tk.Button(self.labelframe1, text="Generar Entrada", command=self.agregarRegistroRFID, width=13, height=3, anchor="center", background="blue")
        self.boton1.grid(column=1, row=4, padx=4, pady=4)

        self.boton2=tk.Button(self.pagina1, text="Salir del programa", command=quit, width=15, height=1, anchor="center", background="blue")
        self.boton2.grid(column=0, row=0, padx=4, pady=4)  

        ###Pensionados
        self.labelframe3=ttk.LabelFrame(self.pagina1, text="PENSIONADOS")
        self.labelframe3.grid(column=1, row=2, padx=0, pady=0)        
        self.labelTarjeta=ttk.Label(self.labelframe3, text="Num. Tarjeta:")
        self.labelTarjeta.grid(column=0, row=2, padx=0, pady=0)
        self.NumTarjeta4=tk.StringVar()
        self.entryNumTarjeta4=tk.Entry(self.labelframe3, width=20, textvariable=self.NumTarjeta4)
        #self.entryNumTarjeta4.bind('Return', self.Pensionados)
        self.entryNumTarjeta4.grid(column=1, row=2, padx=4, pady=4)
        self.entryNumTarjeta4.focus()
        self.labelMensaje=ttk.Label(self.labelframe3, text="")
        self.labelMensaje.grid(column=2, row=2, padx=0, pady=0)

        #self.botonPensinados=tk.Button(self.labelframe3, text="Entrada", command=self.Pensionados, width=10, height=1, anchor="center")
        #self.botonPensinados.grid(column=2, row=2, padx=4, pady=4)  
    def SenBoleto(self): #Detecta presencia de automovil
        global SenBBoleto
        if io.input(SenBBoleto):
                 
                io.output(out3,1)#con un "1" se apaga el led
                #self.loopDet.config(text = "Inicio", background = '#CCC')                
                BanSenBoleto = 1
                print('no siente boleto '+str(BanSenBoleto))
                #self.check_inputs()
        else:                
                 
                io.output(out3,0)                              
                #self.loopDet.config(text = "Auto", background = 'red')
                BanSenBoleto = 0
                print('siente boleto '+str(BanSenBoleto))
                #self.check_inputs()

    def Intloop(self): #Detecta presencia de automovil
        global BanLoop
        if io.input(loop):
                print('no hay auto') 
                io.output(out1,1)#con un "1" se apaga el led
                #self.loopDet.config(text = "Inicio", background = '#CCC')                
                BanLoop = 1
                #BanImpresion = 0
                #self.check_inputs()
        else:                
                print('hay auto') 
                io.output(out1,0)                              
                #self.loopDet.config(text = "Auto", background = 'red')
                BanLoop = 0
                #self.check_inputs()
    def IntBoton(self): #Detecta presencia de automovil
        global BanBoton
        if io.input(boton):
                        #self.BotDet.config(text = "Presione Boton",background="#CCC")
                        print('solto boton')
                        io.output(out2,1)
                        BanBoton = 1
        else:
                        print('presiono boton')            
                        io.output(out2,0)
                        #self.BotDet.config(text = "Imprimiendo",background="red")
                        BanBoton = 0
                        #self.agregarRegistroRFID()

    io.add_event_detect(loop, io.BOTH, callback = Intloop)
    io.add_event_detect(boton, io.BOTH, callback = IntBoton)
    io.add_event_detect(SenBBoleto, io.BOTH, callback = SenBoleto)


    def check_inputs(self):
        global BanBoton
        global BanLoop
        global BanImpresion
    
        if BanLoop == 0:
                self.loopDet.config(text = " hay auto", background = 'green')
                tarjeta=str(self.entryNumTarjeta4.get(),)
                if len(tarjeta) == 10:
                    #mb.showwarning("IMPORTANTE", "ENTRO")
                    self.Pensionados(self)
        else:
                self.loopDet.config(text = "No Siente Auto", background = '#CCC')
                self.labelMensaje.config(text= "No ejecuta Pensionado")
                self.NumTarjeta4.set("")               
                self.entryNumTarjeta4.focus()
                BanImpresion = 0
        if (BanBoton == 1):#BanBoton == 1 no esta oprimido el boton
            self.BotDet.config(text = "solto Boton ",background="#CCC")
            #print(str(BanSenBoleto))
            if BanImpresion == 1: #and BanSenBoleto == 1:# mando a imprimir y ya no tiene boleto en la boquilla
                self.SenBol.config(text = "No siente boleto ")
                #print("En BanBoton= 1 "+str(BanSenBoleto))

                                    #io.output(out2,1)
        else:    
                self.BotDet.config(text = "presiono Boton imprime ",background="green")
                print("BanSenBoleto ",str(BanSenBoleto))
                print("BanImpresion ",str(BanImpresion))
                print("BamLoop ",str(BanLoop))
                if BanLoop==0 and BanImpresion == 0:
                    #io.output(out2,0)             
                   print('imprimir')
                   #print(str(BanSenBoleto))
                   self.agregarRegistroRFID()
                   io.output(out3,1)#con un "1" se apaga el led
                   io.output(barrera,0)#con un "0" abre la barrera
                   time.sleep (1)
                   io.output(barrera,1)
                   #BanImpresion = 0
                   BanImpresion = 1
                   if BanSenBoleto == 1:
                      print("En BanSenBoleto= 1 "+str(BanSenBoleto))
                      # self.SenBol.config(text = "No siente boleto ")
                      # io.output(out3,1)#con un "1" se apaga el led
                       #io.output(barrera,0)#con un "0" abre la barrera
                       #time.sleep (1)
                       #io.output(barrera,1)
                   else:                   
                      self.SenBol.config(text = "siente boleto ")
                    
                else:
                   print ('no puede imprimir porque no tiene Auto')
                   #print(str(BanSenBoleto))
                   self.BotDet.config(text = "no puede imprimir no hay auto ",background="red")


        now =datetime.now() 
        fecha1= now.strftime("%d-%b-%Y ")
        hora1= now.strftime("%H:%M:%S")    
        self.Reloj.config(text=fecha1)            
        self.mi_reloj.config(text=hora1)    
        self.ventana1.after(60, self.check_inputs)          # activa un timer de 50mSeg.
   
    def Autdentro(self):
        respuesta=self.DB.Autos_dentro()
        self.scrolledtext.delete("1.0", tk.END)
        for fila in respuesta:
            self.scrolledtext.insert(tk.END, "Entrada num: "+str(fila[0])+"\nEntro: "+str(fila[1])+"\n\n")

    def agregarRegistroRFID(self):
        placa = self.Placa.get()
        Corte = 0

        MaxFolio=self.DB.MaxfolioEntrada()
        folio_boleto = MaxFolio + 1
        self.MaxId.set(folio_boleto)

        folio_cifrado = self.DB.cifrar_folio(folio = folio_boleto)
        # print(f"QR entrada: {folio_cifrado}")

        #Generar QR
        self.DB.generar_QR(folio_cifrado)

        fechaEntro = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        datos=(fechaEntro, Corte, placa)

        printer = Usb(0x04b8, 0x0e15, 0)

        # printer.image(logo_1)
        printer.text("--------------------------------------\n")
        printer.set("center")
        printer.text("BOLETO DE ENTRADA\n")
        printer.set(height=2, align='center')
        printer.text(f'Folio 000{folio_boleto}\n')

        printer.set("center")        
        printer.text(f'Entro: {fechaEntro[:-3]}\n')
        printer.text('Monterrey No. 75\n')
        printer.text('Entrada Durango \n')
        printer.set(align = "left")
        printer.image(qr_imagen)

        printer.text("--------------------------------------\n")
        printer.cut()

        printer.close()

        self.DB.altaRegistroRFID(datos)
        self.Placa.set('')


        
        
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$impresion fin$$$$$$$$$$$$$$$$        

    def Pensionados(self, event):
        try:
            numtarjeta=self.NumTarjeta4.get()

            print(numtarjeta)
            Existe = self.DB.ValidarPen(numtarjeta)
            tarjeta = int(Existe)

            if len(Existe) == 0:
                self.label_informacion.config(text="No existe Pensionado")
                self.NumTarjeta4.set("")
                self.entryNumTarjeta4.focus()
                return

            respuesta = self.DB.ConsultaPensionado(Existe)

            for fila in respuesta:
                VigAct = fila[0]
                Estatus = fila[1]
                Tolerancia = int(fila[3])

            if VigAct is None:
                self.label_informacion.config(text="Tarjeton desactivado")
                self.Placa.set("")
                self.entry_placa.focus()
                return

            elif Estatus == 'Adentro':
                self.label_informacion.config(text="El Pensionado ya está dentro")
                self.Placa.set("")
                self.entry_placa.focus()
                return

            # Obtener la fecha y hora actual en formato deseado
            VigAct = VigAct.strftime("%Y-%m-%d %H:%M:%S")
            # Convertir la cadena de caracteres en un objeto datetime
            VigAct = datetime.strptime(VigAct, "%Y-%m-%d %H:%M:%S")

            # Obtener la fecha y hora actual en formato deseado
            hoy = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            # Convertir la cadena de caracteres en un objeto datetime
            hoy = datetime.strptime(hoy, "%Y-%m-%d %H:%M:%S")

            limite = self.get_date_limit(VigAct, Tolerancia)
            print(limite)

            if hoy >= limite:
                self.label_informacion.config(text="Vigencia Vencida")
                self.Placa.set("")
                self.entry_placa.focus()
                return

            datos = (Existe, tarjeta, hoy, 'Adentro', 0)
            datos1 = ('Adentro', Existe)
            self.DB.MovsPensionado(datos)
            self.DB.UpdPensionado(datos1)

            self.NumTarjeta4.set("")               
            self.entryNumTarjeta4.focus()

            self.abrir_barrera()

        except Exception as e:
            print(e)
            traceback.print_exc()
            self.label_informacion.config(text="Ha ocurrido un error")
            self.Placa.set("")
            self.entry_placa.focus()
            return


    def abrir_barrera(self):
        """Esta funcion se encarga de abrir la barrera."""
        # Con un "1" se apaga el led
        io.output(out3,1)

        # Con un "0" abre la barrera
        io.output(out1, 0)
        sleep(1)
        io.output(out1, 1)

        print('------------------------------')
        print("Se abre barrera")
        print('------------------------------')


    def get_date_limit(self, date_start:datetime, Tolerance:int) -> datetime:
        """
        Calcula la fecha límite a partir de una fecha de inicio y una cantidad de días de tolerancia.

        :param date_start (datetime): Fecha de inicio.
        :param Tolerance (int): Cantidad de días laborables a agregar.
        :return (datetime): Fecha límite después de agregar la cantidad de días laborables.
        """
        date_limit = date_start

        while Tolerance > 0:
            date_limit  += timedelta(days=1)
            # Verifica si el día no es fin de semana (lunes a viernes)
            if date_limit.weekday() < 5:
                Tolerance -= 1
        
        return date_limit







aplicacion1=FormularioOperacion()


