import RPi.GPIO as gpio
import time


class Motor(): #velocidad MAX = 0.0007 Velocidad Min = 0.005 para A4988
    def __init__(self, dir, step, sleep):
        #pines del motor
        self.__dir = dir
        self.__step = step
        self.__sleep = sleep

        #parámetros del motor
        
        self.__velocidad = 0
        self.__pasos =0
        self.__aceleracion = 0
        
        #variables internas de la clase
        self.__vranterior = 0       #valor recibido anterior
        self.__sentido = False      #Variable de sentido del motor
        self.__consigna  = 1/200      #Variable de consigna de velocidad del motor, es el valor de tiempo por flanco, es decir, el tiempo por medio paso.
        

        gpio.setmode(gpio.BCM)      #Nombrado de pines en BCM
        gpio.setwarnings(False)     #Deshabilitar advertencias

        gpio.setup(self.__dir, gpio.OUT)    #Declaración de pines como salida
        gpio.setup(self.__step, gpio.OUT)
        gpio.setup(self.__sleep, gpio.OUT)

        gpio.output(self.__dir, 0)          #Estado inicial de los pines
        gpio.output(self.__step, 0)
        gpio.output(self.__sleep, 0)

   

    def go(self, val):        #Encargado de mover el motor segun el "valor" que llegue del cliente

       
        if val >135 :
            self.__sentido = True
            self.__consigna = 120/((val-135)*1228.6 +24000)#1/ ((val - 135)/(255-135))*1228.6 +200
        elif val < 115: 
            self.__sentido = False
            self.__consigna =  1/((val/115)*1228.6 +200)
      
        

        gpio.output(self.__dir, self.__sentido)
        gpio.output(self.__sleep, 1)

        
        time.sleep(self.__consigna)
        gpio.output(self.__step, gpio.HIGH)
        time.sleep(self.__consigna)
        gpio.output(self.__step, gpio.LOW)

        if self.__sentido:            
            self.__pasos += 1
            
        else:
            self.__pasos -= 1
        if self.__pasos <0 :                    #PARA ORIENTACION ESTO NO VALE, SI ESTAMOS EN 0 Y DECREMENTA DEBE SER 360
            self.__pasos = 0
        self.__velocidad = 1/(self.__consigna*2)


    def stop(self): 
        gpio.output(self.__dir, 0)
        gpio.output(self.__step, 0)
        gpio.output(self.__sleep, 1)

    def offmotor(self):
        gpio.output(self.__sleep, gpio.LOW)     #Deshabilita la potencia en el A4988 dejando el motor sin alimentacion

    def getpasos(self):                         #Pasos avanzados desde origen
        return self.__pasos

    def setpasos(self, pasos):                  #Modificar pasos
        self.__pasos = pasos

    def getconsigna(self):
        return self.__consigna