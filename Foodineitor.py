from machine import Pin
from time import sleep
from hcsr04 import HCSR04
import network
import socket
import urequests

class Foodineitor:
    def __init__(self,Net_Name:str,Password:str):
        
        self.led = Pin(2,Pin.OUT,value=False)
        
        self.OperacionalData = {"Pagina":"Panel de Control","Gramos por Porción":100,"Horario":False,"Comida al día":2,"Horas":(6,12,18),"Comida en el plato":0,"Estado del contenedor":"Vacio"}
        self.Indices=[0]
        self.TextoBotón1 = {0:("Activar","#dcdcdc","4"),1:("Desactivar","#777777","5")}
        self.HorasDeHorarios = ""
        self.URLTime = "http://worldtimeapi.org/api/timezone/America/Bogota"
        
        self.pinesMotor = [Pin(x,Pin.OUT,value=False) for x in (5,18,19,21)]
        self.medidor = HCSR04 (trigger_pin = 5 , echo_pin = 18)
        
        self.sta_if = network.WLAN(network.STA_IF) # Instanciamos el objeto -sta_if- para controlar la interfaz STA
        self.sta_if.active(True)# Activamos la interfaz STA del ESP32
        self.sta_if.connect(Net_Name,Password)# Iniciamos la conexion con los datos de nuestro AP
        print("Connecting to network ", Net_Name +"...")
        
        while not self.sta_if.isconnected():sleep(0.1)
        
        lista = self.sta_if.ifconfig()
        print("Succesfuly connected :D")
        print("Your IP number is",lista[0])
        self.led.value(True);sleep(0.5);self.led.value(False)
        
        response = urequests.get(self.URLTime)
        self.datos = response.json()
        self.Fecha = str(self.datos["datetime"])
        self.HoraEnMin = int(self.Fecha[11:13])*60+int(self.Fecha[14:16])
        print(self.Fecha)
        
        self.GestorCodigos()
        
        self.Puerto = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.Puerto.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.Puerto.bind(('',80))
        self.Puerto.listen(5)
        
    def GestorCodigos(self):
        self.listaCodigos = {
            "Panel de Control":"""
            </head>
            <body>
            <h1 align="center">Panel de Control "Foodineitor"</h1>
            <h2 align="center">Gramos de comida por porción</h2>
            <p align="center">
                <a href="/PanelDeControl/cod=1">
                    <button style="height:50px;width:50px;background-color:#e0a7a7;border-color:#e0a7a7;color:white"><b><FONT SIZE=7>-</font></b></button>
                </a><FONT SIZE=6>&nbsp&nbsp&nbsp"""+str(self.OperacionalData["Gramos por Porción"])+"""gr.&nbsp&nbsp&nbsp</font>
                <a href="/PanelDeControl/cod=2">
                    <button style="height:50px;width:50px;background-color:#a7e0a7;border-color:#a7e0a7;color:white"><b><FONT SIZE=7>+</font></b></button>
                </a>
            </p>
            <h2 align="center">!Programa un Horario de alimentación¡</h2>
            <p align="center">
                <a href="/ProgramaHorario/cod=1">
                    <button style="height:50px;width:150px;background-color:#777777;border-color:#777777;color:white"><b><FONT SIZE=4>¡Programar Horario!</font></b></button>
                </a>
            </p>
            <h2 align="center">¡Revisa si tu mascota está recibiendo comida!</h2>
            <p align="center">
                <a href="/PaginaPrincipal/cod=1">
                    <button style="height:90px;width:150px;background-color:#777777;border-color:#777777;color:white"><b><FONT SIZE=4>Volver a la Página Principal</font></b></button>
                </a>
            </p>
            <h2 align="center">O haz clic a continuación para dejar caer el alimento ahora</h2>
            <p align="center">
                <a href="/PanelDeControl/cod=4">
                    <button style="height:50px;width:150px;background-color:#777777;border-color:#777777;color:white"><b><FONT SIZE=4>¡Alimentar ahora!</font></b></button>
                </a>
            </p>
            </body>
            """,#--------------------------------------------------------
            "Programa Horario":"""
            </head>
            <body>
            <h1 align="center">Horario de Alimentación</h1>
            <h2 align="center">Cantidad de porciones diarias</h2>
            <p align="center">
                <a href="/ProgramaHorario/cod=2">
                    <button style="height:50px;width:50px;background-color:#e0a7a7;border-color:#e0a7a7;color:white"><b><FONT SIZE=7>-</font></b></button>
                </a><FONT SIZE=6>&nbsp&nbsp&nbsp"""+str(self.OperacionalData["Comida al día"])+""" porciones&nbsp&nbsp&nbsp</font>
                <a href="/ProgramaHorario/cod=3">
                    <button style="height:50px;width:50px;background-color:#a7e0a7;border-color:#a7e0a7;color:white"><b><FONT SIZE=7>+</font></b></button>
                </a>
            </p>
            <p align="center">
                <a href="/ProgramaHorario/cod=4">
                    <button style="height:50px;width:200px;background-color:"""+self.TextoBotón1[self.Indices[0]][1]+""";border-color:black;color:black"><b><FONT SIZE=3>"""+self.TextoBotón1[self.Indices[0]][0]+""" programa por horario</font></b></button>
                </a>
            </p>
            <h2 align="center">Los horarios son: """+ self.HorasDeHorarios +"""</h2>
            <p align="center">
                <a href="/PanelDeControl/cod=3">
                    <button style="height:50px;width:200px;background-color:#777777;border-color:#777777;color:white"><b><FONT SIZE=4>Volver al Panel de Control</font></b></button>
                </a>
            </p>
            </body>
            """,#---------------------------------------------------------
            "Pagina Principal":"""
                <meta http-equiv="refresh" content="30">
            </head>
            <body>
            <h1 align="center">Bienvenid@ - Página principal</h1>
            <h2 align="center">¡Gestiona a Foodineitor para que tu mascota esté contenta!</h2>
            <p align="center">
                <a href="/PanelDeControl/cod=3">
                    <button style="height:50px;width:150px;background-color:#777777;border-color:#777777;color:white"><b><FONT SIZE=4>Ir al Panel de control</font></b></button>
                </a>
            </p>
            <p align="center"><FONT SIZE=5> Comida en el plato: <b>"""+str(self.OperacionalData["Comida en el plato"])+""" g </b></font></p>
            <p align="center"><FONT SIZE=5> Estado del contenedor: <b>"""+self.OperacionalData["Estado del contenedor"]+""" </b></font></p>
            <p align="center"><FONT SIZE=5>"""+str(self.Fecha)[11:19]+"""</font></p>
            </body>
            """
            }
        self.codigoHTML = """<!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Gestor Foodineitor</title>
        """+self.listaCodigos[self.OperacionalData["Pagina"]]
    
    def MainLoop(self):
        while True:
            cl,addr = self.Puerto.accept()
            print("Cliente conectado desde ",addr)
            request = cl.recv(1024)
            request = str(request)
            print("Contenido = ",request)
            
            if request.find("/PanelDeControl/cod=1") == 6:
                self.Set_Gramos(-10)
            elif request.find("/PanelDeControl/cod=2") == 6:
                self.Set_Gramos(10)
            elif request.find("/PanelDeControl/cod=3") == 6:
                self.Set_Pagina("Panel de Control")
            elif request.find("/PanelDeControl/cod=4") == 6:
                self.Alimentar()
            elif request.find("/ProgramaHorario/cod=1") == 6:
                self.Set_Pagina("Programa Horario")
            elif request.find("/ProgramaHorario/cod=2") == 6:
                self.Set_Porciones(-1)
            elif request.find("/ProgramaHorario/cod=3") == 6:
                self.Set_Porciones(1)
            elif request.find("/ProgramaHorario/cod=4") == 6:
                self.Des_Activar_Horario()
            elif request.find("/PaginaPrincipal/cod=1") == 6:
                self.LecturaSensores()
                self.Set_Pagina("Pagina Principal")
            
            self.GestorCodigos()
            
            respuesta = self.codigoHTML
            cl.send("HTTP/1.1 200 Ok\n")
            cl.send("Content-Type: text/html\n")
            cl.send("Connection: close\n\n")
            cl.sendall(respuesta)
            cl.close()
            
    def Set_Gramos(self,cambio:int):
        self.OperacionalData["Gramos por Porción"]+=cambio
        print(self.OperacionalData["Gramos por Porción"])
        
    def Set_Porciones(self,cambio:int):
        self.OperacionalData["Comida al día"]+=cambio
        self.OperacionalData["Horas"]=[4+(i+1)*18/(self.OperacionalData["Comida al día"]+1) for i in range(self.OperacionalData["Comida al día"])]
        self.HorasDeHorarios = ""
        valor1 = [str(int(i//1))+":"+str(round(60*(i%1))) for i in self.OperacionalData["Horas"]]
        for i in valor1:self.HorasDeHorarios+=i+" - "
        self.HorasDeHorarios=self.HorasDeHorarios[0:-2]
        print(self.OperacionalData["Comida al día"])
        print(self.OperacionalData["Horas"])
        print(self.HorasDeHorarios)
        
    def Des_Activar_Horario(self):
        self.OperacionalData["Horario"] = not self.OperacionalData["Horario"]
        self.Indices[0]=(self.Indices[0]+1)%2
        
    def Set_Pagina(self,URLdestino):
        self.OperacionalData["Pagina"]=URLdestino
        
    def LecturaSensores(self):
        response = urequests.get(self.URLTime)
        self.datos = response.json()
        self.Fecha = str(self.datos["datetime"])
        self.HoraEnMin = int(self.Fecha[11:13])*60+int(self.Fecha[14:16])
        print(self.Fecha)
        for i in self.OperacionalData["Horas"]:
            if round(i*60) == self.HoraEnMin and self.OperacionalData["Horario"]:self.Alimentar()
        
    def LeerSensorUltrasonido(self):
        distancia = 20
        area = 30
        densidad = 0.8
        try:
            distancia = round(self.medidor.distance_cm ()*2)/2
            print ("Distancia = ", distancia, " cm")
        except:
            print ("Error!")
        masa = (30-distancia)*area*densidad
        if distancia < 30:self.OperacionalData["Estado del contenedor"]="Con Comida"
        if masa >= 0:return masa
    
    def Alimentar(self,tiempo): #Movimiento del motor
        valor = self.LeerSensorUltrasonido()
        self.MoverMotor(tiempo)
        print("Alimentado")
        valor2 = self.LeerSensorUltrasonido()
        valor -= valor2
        self.OperacionalData["Comida en el plato"] = valor
        
    def MoverMotor(self,tiempo):
        for mover in [1,-1]:for i in range(1024*tiempo):self.PinesMotor[(1024+mover*i)%4].value(True);self.PinesMotor[(1024+mover*(i-1))%4].value(False);sleep(0.01)

#Robot = Foodineitor("santi_25", "lila1301")
Robot = Foodineitor("Camp Nou","JuanCamilo")
#Robot = Foodineitor("hello there","general kenobi")
Robot.MainLoop()