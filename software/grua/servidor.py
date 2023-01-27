import socket
import sys
import busio
import time
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from motorPAP import Motor
import threading
import logging



#variables a enviar
orientacion = 255
distcarro = 254
discarga = 253
peso = 252
#variables a recibir
vejex = 0
vejey = 0
vejez = 0
paquetes  = 0

#Instancia de los motores con los pines en modo BCM
motor1 = Motor(15, 14, 4)
motor2 = Motor(17, 27, 18)
motor3 = Motor(24, 22, 23)
#velocidad MAX = 0.0007 Velocidad Min  0.005 para A4988



#i2c = busio.I2C(board.SCL, board.SDA)   #Declaracion de pines bus I2C
#ads = ADS.ADS1115(i2c)                  #Instancia del ADC1115




def comunicacion():
    global vejex, vejey, vejez, paquetes
    while True: 
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        serverAdress = ('192.168.1.135', 8080)
        print(' Starting server ...' , serverAdress)
        ss.bind(serverAdress)
        ss.listen(1)  #Esperamos conexion de un solo cliente
        print('Waiting for a client...')
        connection, clientAdress = ss.accept()  #Envio confirmacion al cliente

        try: 
            print('Conection from ... ', clientAdress)
            hilo1.marcha = True
            hilo2.marcha = True
            hilo3.marcha = True
            #connection.settimeout(0.5)
            while True:

                data = connection.recv(4).decode('utf-8')
        
                if data == 'ejex':
                    connection.send(bytes(1))

                    vejex = int.from_bytes(connection.recv(15), 'big')
                    connection.send(bytes(1))

                    data = connection.recv(4).decode('utf-8')

                    if data == 'ejey':
                        connection.send(bytes(1))
                        vejey = int.from_bytes(connection.recv(15), 'big')
                        connection.send(bytes(1))
                        data = connection.recv(4).decode('utf-8')
                
                        if data == 'ejez':
                            connection.send(bytes(1))
                            vejez = int.from_bytes(connection.recv(15), 'big')
                            connection.send(bytes(1))
                            

                        else:
                            print("error en eje z")

                    else:
                        print("error en eje y")

                else: 
                    print('error en x')    
         
                connection.send("orientacion".encode('utf-8'))
                data = connection.recv(1)
                if data == bytes(1):
                    connection.send(orientacion.to_bytes(1, 'big'))
                    data = connection.recv(1)

                    if data == bytes(1): 
                        connection.send("distcarro".encode('utf-8'))
                        data = connection.recv(1)

                        if data == bytes(1):
                            connection.send(distcarro.to_bytes(1, 'big'))
                            data = connection.recv(1)

                            if data == bytes(1): 
                                connection.send("distcarga".encode('utf-8'))
                                data = connection.recv(1)

                                if data == bytes(1): 
                                    connection.send(discarga.to_bytes(1,'big'))
                                    data = connection.recv(1)

                                    if data == bytes(1): 
                                        connection.send("peso".encode('utf-8'))
                                        data = connection.recv(1)

                                        if data == bytes(1): 
                                            connection.send(peso.to_bytes(1,'big'))
                                            data = connection.recv(1)
                                            paquetes +=1
                                       

        except KeyboardInterrupt:
            print('anulado por el servidor')
    
            connection.close()
            ss.close()
            print('cerrado2')

        except socket.timeout:
            print("Time out en el servidor")
            hilo1.marcha = False
            hilo2.marcha = False
            hilo3.marcha = False
            continue
            #Aquí abría que poner las consignas de todo a cero o matarlos hilos
            # y volver a esperar una conexión con el cliente

        finally: 
            connection.close()
            print('cerrado')

def m1():
    global orientacion
     
    hilo1 = threading.currentThread()
    while getattr(hilo1, "marcha", True):
            #print("{:>5}\t{:>5}\t{:>5}\t{:>5}".format(vejex, vejey, vejez, paquetes))
        if (vejex<115 or vejex > 135):
            motor1.go(vejex)
            consignaM1 = motor1.getconsigna()
            print("M1" + " " + str(consignaM1))
        else:
            motor1.stop()

        orientacion = motor1.getpasos()

def m2():
    global distcarro
    
    hilo2 = threading.currentThread()
    while getattr(hilo2, "marcha", True):
        if (vejey<115 or vejey > 135):
            motor2.go(vejey)
            consignaM2 = motor2.getconsigna()
            print("M2" + " " + str(consignaM2))
        else:
            motor2.stop()
        distcarro =  motor2.getpasos()

def m3():
    global discarga
    hilo3 = threading.currentThread()
    while getattr(hilo3, "marcha", True):
        if (vejez<115 or vejez > 135):
            motor3.go(vejez)
            consignaM3 = motor3.getconsigna()
            print("M3" + " "+ str(consignaM3))
        else:
            motor3.stop()
        discarga = motor3.getpasos()



#Instanciacion de los hilos
hilo1 = threading.Thread(target= m1, name= "motor1")
hilo2 = threading.Thread(target= m2, name= "motor2")
hilo3 = threading.Thread(target= m3, name= "motor3")
hilo4 = threading.Thread(target= comunicacion, name= "comunicacion")


try:
    hilo1.marcha = False
    hilo2.marcha = False
    hilo3.marcha = False
    hilo4.start()
    hilo1.start()
    hilo2.start()
    hilo3.start()
    
except KeyboardInterrupt:
    hilo1.marcha = False #Hacemos que terminen los hilos
    hilo2.marcha = False
    hilo3.marcha = False
    motor1.offmotor()
    motor2.offmotor()
    motor3.offmotor()
    print('motor apagado')
