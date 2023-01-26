from joystick10 import Joystick
import cv2 
import urllib.request 
import numpy as np
import time
import board
import busio
import ADS1x15.adafruit_ads1x15.ads1115 as ADS
from ADS1x15.adafruit_ads1x15.analog_in import AnalogIn
import socket
import sys

orientacion = 0
distcarro = 0
distcarga = 0
peso = 0
x = 0
y = 0
z = 0
serverAdress = ('192.168.1.135', 8080)
timeout = 0.5
paquetes = 0

url = 'http://192.168.1.134/cam-lo.jpg'

winName = 'Mi camara'
cv2.namedWindow(winName, cv2.WINDOW_NORMAL)

js = Joystick()




while True:
    

    try:
        sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) ## Objeto del socket cliente declarado como socket de flujo
        print('Conecting with: ', serverAdress)
        sc.connect(serverAdress)
        sc.settimeout(timeout)
        print("Conected")

        while True:
            x = js.getAxis("x")
            y = js.getAxis("y")
            z = js.getAxis("z")

            sc.send("ejex".encode('utf-8'))
            data = sc.recv(1)
            if data == bytes(1):
                sc.send(x.to_bytes(1,'big'))
                data = sc.recv(1)
                if data == bytes(1):
                    sc.send("ejey".encode('utf-8'))
                    data = sc.recv(1)
                    
                    if data == bytes(1):
                        sc.send(y.to_bytes(1,'big'))
                        data = sc.recv(1)

                        if data == bytes(1):
                            sc.send("ejez".encode('utf-8'))
                            data = sc.recv(1)

                            if data == bytes(1): 
                                    sc.send( z.to_bytes(1,'big'))
                                    data = sc.recv(1)
                                    #print("enviado")
                                    
                                    data = sc.recv(11).decode('utf-8')

                                    if data == 'orientacion':
                                        sc.send(bytes(1))
                                        orientacion = int.from_bytes(sc.recv(4),'big')
                                        sc.send(bytes(1))
                                        data = sc.recv(9).decode('utf-8')

                                        if data == "distcarro":
                                            sc.send(bytes(1))
                                            distcarro = int.from_bytes(sc.recv(4),'big')
                                            sc.send(bytes(1))
                                            data = sc.recv(9).decode('utf-8')

                                            if data == "distcarga": 
                                                sc.send(bytes(1))
                                                distcarga = int.from_bytes(sc.recv(4),'big')
                                                sc.send(bytes(1))
                                                data = sc.recv(4).decode('utf-8')

                                                if data == "peso":

                                                    sc.send(bytes(1))
                                                    peso = int.from_bytes(sc.recv(4),'big')
                                                    sc.send(bytes(1))
                                                    paquetes +=1
                                                    #print("{:>5}\t{:>5}\t{:>5}\t{:>5}\t{:>5}".format(orientacion, distcarro, distcarga, peso , paquetes))
                                            
                                            else:
                                                print("error en distcarga")
                                        else:
                                            print("error en distcarro")
                                    else: 
                                        print("error en orientacion")

            imgResponse = urllib.request.urlopen(url)
            imgNp = np.array(bytearray(imgResponse.read()), dtype = np.uint8)
            img = cv2.imdecode(imgNp, -1)


            cv2.setWindowProperty(winName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.putText(img,"Rotacion:", (0,235), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255,1)
            cv2.putText(img,"Carga:", (0,205), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255,1)
            cv2.putText(img,str(orientacion), (150,235), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255,1)
            cv2.putText(img,str(distcarro), (150,205), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255,1)
            cv2.imshow(winName, img)
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord('q'):
                break
        cv2.destroyAllWindows()
    
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        sc.close()
    except socket.timeout: 
        print("timeOut cliente")
        sc.close()

    


