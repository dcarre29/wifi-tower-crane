from joystick10 import Joystick 
#se importa la libreria Joystick para el manejo del joystick
import cv2 
#se importa la libreria open-CV para el manejo de las partes gráficas
import urllib.request 
#se importa la libreria urllib para enviar peticiones HTTP a una url
import numpy as np
#se importa la libreria numpy para trabajar con arrays
import socket
#se importa la libreria socket para la comunicacion mando grua
from threading import Thread
#se importa la libreria thread para el manejo de los hilos
import RPi.GPIO as GPIO
#libreria para el manejo del los pines de la RPi


orientacion = 0
distcarro = 0
distcarga = 0
peso = 0
#valores iniciales de los parametros de posicionamiento de la grua
x = 130
y = 130
z = 130
#valores iniciales de las consignas del mando
#correspondientes a motores frenados

serverAdress = ('192.168.1.136', 8080)
#direccion del servidor IP y puerto
timeout =0.8
#tiempo limite de bloqueo en el metodo recv
                                                                                                                     
#variables de la parte grafica
url = 'http://192.168.1.138/cam-hi.jpg'
#direccion url de la camara
winName = 'Mi camara'
#nombre de la ventana que abriremos con opencv
font = cv2.FONT_HERSHEY_SIMPLEX
#tipo de letra
color=(0, 233,255)
#color de la letra en RGB
fontScale = 1
#tamaño de letra
thickness = 2
#grosor de la letra
cv2.namedWindow(winName, cv2.WINDOW_NORMAL)
#creacion de la ventana para el LCD
js = Joystick()
#instanciacion de la clase joystick

b_accion = 18
#numero de pin del boton accion
GPIO.setup(b_accion, GPIO.IN, pull_up_down= GPIO.PUD_DOWN)
#configuracion del boton de accion
#configuracion pull-down


def electronica(): 
    #Verificamos el estado de la electronica del mando
    global x, y, z
    #variables globales que se manipulan en este metodo
    #en este metodo se manipulan las consignas del joystick

    while True:        
        if(GPIO.input(b_accion) == True):
            #si el boton de accion está pulsado
            x = js.getAxis("x")
            y = js.getAxis("y")
            z = js.getAxis("z")
        #obtencion de los valores del ADC para cada eje transformados
        #entre 0 y 255.
        else:
        #si no esta pulsado
            x = y = z = 120
        #enviamos 120 para frenar motores

        
       
def comunicacion(): 
    #Enviamos y recibimos las variables
    global orientacion, distcarga, distcarro, peso, paquetes
    #variables globales que se manipulan en este metodo

    while True:
        try:
            sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            #Objeto del socket cliente declarado como socket de flujo
            print('Conecting with: ', serverAdress)
            #impresion del estado por consola
            sc.connect(serverAdress)
            #se envia peticion de conexion al servidor
            #permanece bloqueado hasta recibir confirmacion
            sc.settimeout(timeout)
            #se establece el tiempo maximo de bloqueo en el metodo recv
            print("Conected")
            #impresion del estado por consola

            while True:
                sc.send( x.to_bytes(1,'big'))
                #envio de la consigna del eje x en bytes
                orientacion = int.from_bytes(sc.recv(15),'big')
                #recepcion de la variable orientacion de la grua
                sc.send( y.to_bytes(1,'big'))
                #envio de la consigna del eje y en bytes
                distcarro = int.from_bytes(sc.recv(15),'big')
                #recepcion de la variable distcarro de la grua
                sc.send( z.to_bytes(1,'big'))
                #envio de la consigna del eje z en bytes
                distcarga = int.from_bytes(sc.recv(15),'big')
                #recepcion de la variable distcarga de la grua
                sc.send("peso".encode('utf-8'))
                #envio de la orden peso a la grua
                peso = int.from_bytes(sc.recv(15),'big')
                #recepcion del peso transportado por la grua

                
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            sc.close()

        except socket.timeout:
            #tratamiento de la excepcion timeout
            print("timeOut cliente")
            #impresion del estado por consola
            cv2.destroyAllWindows()
            #destruccion de la ventana grafica
            sc.close()
            #cierre del socket
            
    

def grafica(): 
    #metodo que se encarga de la parte grafica del mando
    while True: 
        try:
            while True:
                imgResponse = urllib.request.urlopen(url,timeout=5)
                #se abre el URL declarado anteriormente
                
                imgNp = np.array(bytearray(imgResponse.read()), dtype = np.uint8)
                #se transforman los datos recibidos en un array de bytes
                
                img = cv2.imdecode(imgNp, -1)
                #se tranforman los arrays en un streaming de imagenes
                cv2.setWindowProperty(winName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                #configuramos la pantalla como pantalla completa
                cv2.putText(img,"Orientacion:", (0,430), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                cv2.putText(img,"Distcarro:", (0,460), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                cv2.putText(img,str(orientacion), (210,430), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                cv2.putText(img,"mm", (270,430), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                cv2.putText(img,str(distcarro), (210,460), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                cv2.putText(img,"mm", (270,460), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                cv2.putText(img,"DistCarga:", (340,460), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                cv2.putText(img,"Peso:", (340,430), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                cv2.putText(img,str(distcarga), (500,460), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                cv2.putText(img,"mm", (570,460), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                cv2.putText(img,str(peso), (500,430), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                cv2.putText(img,"g", (570,430), cv2.FONT_HERSHEY_SIMPLEX, fontScale ,color, thickness)
                #se superponen las variables de posicionamiento de la grua en el streaming
                cv2.imshow(winName, img)
                #se refresca la imagen

                tecla = cv2.waitKey(1) & 0xFF
                if tecla == ord('q'):
                    break
                #atajo de teclado para cerrar la ventana

        except ConnectionResetError:
            continue
            #si se resetea la conxion se vuelve a conectar
        cv2.destroyAllWindows()
        #si el hilo termina se cierra la ventana


hilo1 = Thread(target=comunicacion, name=comunicacion)
hilo2 = Thread(target=grafica, name= grafica)
hilo3 = Thread(target=electronica, name= electronica)
#se declaran los hilos y se asocian al metodo correspondiente

hilo1.start()
hilo2.start()
hilo3.start()

#se lanzan los tres hilos