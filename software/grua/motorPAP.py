import RPi.GPIO as gpio
#libreria para controlar los pines de la RPi
import time
#libreria para usar el tiempo del sistema


class M_Carro():                                                                                                                                                        #velocidad MAX = 0.0007 Velocidad Min = 0.005 para A4988
    def __init__(self, dir, step):
        #metodo constructor
        self.__dir = dir
        self.__step = step
        #pines del motor

        #parámetros del motor      
        self.__distanciaMAX = 1720                                                                                                                                      
        #recorrido maximo permitido para el motor en pasos
        self.__distanciaMin = 0
        #recorrido minimo permitido para el motor en pasos
        self.__pasos = self.__distanciaMAX
        self.__pasosM = 0
        #se configuran los motores como si estuviesen al final de su recorrido
        #al encender la grua para obligar al operario a llevarla al inicio


        #variables internas de la clase
        self.__consigna  = 0.000000001   
        #Variable de consigna de velocidad del motor, es el valor de tiempo por flanco, es decir, el tiempo por medio paso
        #se establece un valor muy pequeño para reducir los tiempos de ejecucion
        self.__cargaMax0 = 1000
        #carga maxima soportada por la grua cuando distcarro es igual a 0
        #maximo valor que la celda de carga puede medir
        self.__cargaMax_distMax = 100
        #carga maxima soportada por la grua cuando distcarro esta en su valor maximo
        self.__cargaMax = ((self.__cargaMax0 - self.__cargaMax_distMax)/(self.__distanciaMAX-self.__distanciaMin))*(self.__distanciaMAX-self.__pasos)+ self.__cargaMax_distMax
        #recta de carga, sirve para calcular la carga maxima que puede soportar la grua a lo largo de la distancia del eje
        self.__velocidadMAX = 0
        #variable que sera usara para almacenar la velocidad maxima de este motor en funcion del peso

        gpio.setmode(gpio.BCM)      
        #Nombrado de pines en BCM
        gpio.setwarnings(False)     
        #Deshabilitar advertencias

        gpio.setup(self.__dir, gpio.OUT)    
        gpio.setup(self.__step, gpio.OUT)
        #Declaracion de pines como salida

        gpio.output(self.__dir, gpio.LOW)          
        gpio.output(self.__step, gpio.LOW)
        #Estado inicial de los pines

   
        
    def go(self, val, carga):        
    #Encargado de mover el motor segun el "valor" que llegue del cliente y el peso
    #El val recibido siempre esta entre 0 y 255

        self.__cargaMax = ((self.__cargaMax0 - self.__cargaMax_distMax)/(self.__distanciaMAX-self.__distanciaMin))*(self.__distanciaMAX-self.__pasos)+ self.__cargaMax_distMax
        #recta de carga, sirve para calcular la carga maxima que puede soportar la grua a lo largo de la distancia del eje

        self.__velocidadMAX = round(0.0007 + 0.0043*(carga/1000), 4)
        #velocidadMax permitida en funcion de la carga

        if val >135:
            #si val mayor que 135
            gpio.output(self.__dir, gpio.LOW)
            #sentido de giro anihorario
            self.__consigna = round(120/((val-135)*1228.6 +24000), 4)
            #se establece consigna en funcion del val recibido por el mando
            #el resultado corresponde con la frecuencia/2 de la señal

            if self.__velocidadMAX > self.__consigna:
                self.__consigna = self.__velocidadMAX
            #Se limita la velocidad del motor

            if((self.__pasos < self.__distanciaMAX) and (carga < self.__cargaMax)):
                
                #el motor solo se mueve si no esta en su final de recorrido y si la carga no es excedida
                gpio.output(self.__step, gpio.HIGH)
                #se setea la señal a high
                time.sleep(self.__consigna)
                #se espera un tiempo en high
                gpio.output(self.__step, gpio.LOW)
                #se setea la señal a low
                time.sleep(self.__consigna)
                #se espera un tiempo en low
                self.__pasos += 1
                #cada vez que el codigo pase por aqui se da por hecho que el motor ha avanzado un paso

        elif val < 115:
            #si val es menor que 115
            gpio.output(self.__dir, gpio.HIGH)
            #se establece sentido de giro horario
            self.__consigna =  round(1/(((115-val)/115)*1228.6 +200), 4)
            #se establece consigna en funcion del val recibido
            #el resultado corresponde con la frecuencia/2 de la señal

            if self.__velocidadMAX > self.__consigna:
                self.__consigna = self.__velocidadMAX
            #Se limita la velocidad del motor

            if(self.__pasos > self.__distanciaMin):
                
                #el motor solo se mueve en este sentido si no esta en el limite hacia el que se dirige
                gpio.output(self.__step, gpio.HIGH)
                #se setea la señal a high
                time.sleep(self.__consigna)
                #se espera un tiempo en high
                gpio.output(self.__step, gpio.LOW)
                #se setea la señal a low
                time.sleep(self.__consigna)
                #se espera un tiempo en low
                self.__pasos -= 1
                #cada vez que el codigo pase por aqui se da por hecho que el motor ha retrocedido un paso

    def getpasos(self):                         
        #Pasos avanzados desde origen
        return self.__pasos
        

    def getpasosM(self):                         
        #Pasos avanzados desde origen
        self.__pasosM = (self.__pasos*315)/1720
        #conversion de pasos a mm, 1720pasos son 315mm
        return int(self.__pasosM)
        #devuelve la distancia en mm

    def setpasos(self, pasos):                  
        #Modificar pasos
        self.__pasos = pasos
        #setea al valor que indiquemos en pasos
        #solamente es utilizado cuando se pulsa un final de carrera

    def getconsigna(self):
        return self.__consigna
        #devuelve la consigna calculada por el motor


class M_Orientacion(): #velocidad MAX = 0.001 Velocidad Min = 0.005 para A4988

    def __init__(self, dir, step):
        #metodo constructor
        self.__dir = dir
        self.__step = step
        #pines del motor

        #parámetros del motor
        self.__orientacionMAX= 2*903
        #903pasos son 360 grados, se deja dar dos vueltas a la pluma
        #recorrido maximo permitido para el motor en pasos
        self.__orientacionMIN = 0
        #recorrido minimo permitido para el motor en pasos        
        self.__distanciaMax = 1720
        #distancia maxima de la pluma para el calculo de la recta de carga
        self.__distanciaMin = 0
        #distancia minima de la pluma para el calculo de la recta de carga
        self.__pasos = self.__orientacionMAX
        #se configuran los motores como si estuviesen al final de su recorrido
        #al encender la grua para oblicar al operario a llevarla al inicio
        self.__pasosM = 0
        #variable para pasar de pasos a mm


        #variables internas de la clase

        self.__consigna  = 0.001
        #Variable de consigna de velocidad del motor, es el valor de tiempo por flanco, es decir, el tiempo por medio paso.
        self.__cargaMax0 = 1000
        #carga maxima soportada por la grua cuando distcarro es igual a 0
        self.__cargaMax_distMax = 100
        #carga maxima soportada por la grua cuando distcarro esta en su valor maximo
        self.__velocidadMAX = 0
        #variable que sera usara para almacenar la velocidad maxima de este motor en funcion del peso


        gpio.setmode(gpio.BCM)      
        #Nombrado de pines en BCM
        gpio.setwarnings(False)     
        #Deshabilitar advertencias

        gpio.setup(self.__dir, gpio.OUT)    
        gpio.setup(self.__step, gpio.OUT)
        #Declaración de pines como salida

        gpio.output(self.__dir, gpio.LOW)          
        gpio.output(self.__step, gpio.LOW)
        #Estado inicial de los pines


    def go(self, val, carga, pasos_carro):        
    #Encargado de mover el motor segun el "valor" que llegue del cliente y el peso
    #El val recibido siempre esta entre 0 y 255

        self.__cargaMax = ((self.__cargaMax0 - self.__cargaMax_distMax)/(self.__distanciaMax-self.__distanciaMin))*(self.__distanciaMax- pasos_carro)+ self.__cargaMax_distMax
        #recta de carga, sirve para calcular la carga maxima que puede soportar la grua a lo largo de la distancia del eje

        self.__velocidadMAX = round(0.001 + 0.004*(carga/1000), 4)
        #velocidadMax permitida en funcion de la carga

        if val >135:
            #si val mayor que 135
            gpio.output(self.__dir, gpio.HIGH)
            #sentido de giro horario

            self.__consigna = round((1.14-0.004*val)/120, 4)
            #se establece consigna en funcion del val recibido
            #el resultado corresponde con la frecuencia/2 de la señal

            if self.__velocidadMAX > self.__consigna:
                self.__consigna = self.__velocidadMAX
                #se limita la velocidad

            if((self.__pasos < self.__orientacionMAX) and ( carga < self.__cargaMax)):
                
                #el motor solo se mueve si no esta en su final de recorrido y si la carga no es excedida
                gpio.output(self.__step, gpio.HIGH)
                #se setea la señal a high
                time.sleep(self.__consigna)
                #se espera un tiempo en high
                gpio.output(self.__step, gpio.LOW)
                #se setea la señal a low
                time.sleep(self.__consigna)
                #se espera un tiempo en low
                self.__pasos += 1
                #cada vez que el codigo pase por aqui se da por hecho que el motor ha avanzado un paso

        elif val < 115: 
            #si val es menor que 115
            gpio.output(self.__dir, gpio.LOW)
            #se establece sentido de giro antihorario
            self.__consigna =  round((0.004*val/115) + 0.001, 4)
            #se establece consigna en funcion del val recibido
            #el resultado corresponde con la frecuencia/2 de la señal

            if self.__velocidadMAX > self.__consigna:
                self.__consigna = self.__velocidadMAX
                #se limita la velocidad

            if((self.__pasos > self.__orientacionMIN) and ( carga < self.__cargaMax)):
                #el motor solo se mueve si no esta en su final de recorrido y si la carga no es excedida
                gpio.output(self.__step, gpio.HIGH)
                #se setea la señal a high
                time.sleep(self.__consigna)
                #se espera un tiempo en high
                gpio.output(self.__step, gpio.LOW)
                #se setea la señal a low
                time.sleep(self.__consigna)
                #se espera un tiempo en low
                self.__pasos -= 1
                #cada vez que el codigo pase por aqui se da por hecho que el motor ha retrocedido un paso
    
    def getpasos(self):                         
        #Pasos avanzados desde origen
        return self.__pasos
        
    def getpasosM(self):                         
        #Pasos avanzados desde origen
        self.__pasosM = (self.__pasos*360)/903
        #conversion de pasos a grados, 903 pasos son 360 grados
        return int(self.__pasosM)
        #devuelve el valor en grados

    def setpasos(self, pasos):                  
        #Modificar pasos
        self.__pasos = pasos
        #setea al valor que indiquemos en pasos
        #solamente es utilizado cuando se pulsa un final de carrera

    def getconsigna(self):
        return self.__consigna
        #devuelve la consigna calculada por el motor

class M_Gancho(): #velocidad MAX = 0.0007 Velocidad Min = 0.005 para A4988
    def __init__(self, dir, step):
        #metodo constructor
        self.__dir = dir
        self.__step = step
        #pines del motor

        #parámetros del motor
        self.__alturaMAX = 6900     #803mm
        #recorrido maximo permitido para el motor en pasos
        self.__alturaMIN = 0
        #recorrido minimo permitido para el motor en pasos

        self.__distanciaMax = 1720
        #recorrido maximo de la pluma para calcular la recta de carga
        self.__distanciaMin = 0
        #recorrido minimo de la pluma para calcular la recta de carga
        self.__pasos = self.__alturaMAX
        self.__pasosM = 0
        #se configuran los motores como si estuviesen al final de su recorrido
        #al encender la grua para obligar al operario a llevarla al inicio

        #variables internas de la clase

        self.__consigna  = 0.0007      
        #Variable de consigna de velocidad del motor, es el valor de tiempo por flanco, es decir, el tiempo por medio paso.
        self.__cargaMax0 = 1000
        #carga maxima soportada por la grua cuando distcarro es igual a 0
        self.__cargaMax_distMax = 100
        #carga maxima soportada por la grua cuando distcarro esta en su valor maximo
        self.__velocidadMAX = 0
        #variable que sera usara para almacenar la velocidad maxima de este motor en funcion del peso

        gpio.setmode(gpio.BCM)      
        #Nombrado de pines en BCM
        gpio.setwarnings(False)     
        #Deshabilitar advertencias

        gpio.setup(self.__dir, gpio.OUT)    
        gpio.setup(self.__step, gpio.OUT)
        #Declaración de pines como salida

        gpio.output(self.__dir, gpio.LOW)          
        gpio.output(self.__step, gpio.LOW)
        #Estado inicial de los pines
   

    def go(self, val, carga, pasos_carro):        
    #Encargado de mover el motor segun el "valor" que llegue del cliente y el peso
    #El val recibido siempre esta entre 0 y 255
        self.__cargaMax = ((self.__cargaMax0 - self.__cargaMax_distMax)/(self.__distanciaMax-self.__distanciaMin))*(self.__distanciaMax-pasos_carro)+ self.__cargaMax_distMax
        #recta de carga, sirve para calcular la carga maxima que puede soportar la grua a lo largo de la distancia del eje

        self.__velocidadMAX = round(0.0007 + 0.0043*(carga/1000), 4)
        #velocidadMax permitida en funcion de la carga

        if val >135:
            #si val mayor que 135
            gpio.output(self.__dir, gpio.LOW)
            #sentido de giro anihorario
            self.__consigna = round(120/((val-135)*1228.6 +24000), 4)
            #se establece consigna en funcion del val recibido
            #el resultado corresponde con la frecuencia/2 de la señal

            if self.__velocidadMAX > self.__consigna:
                self.__consigna = self.__velocidadMAX
                #se limita la velocidad

            if ((self.__pasos > self.__alturaMIN) and (carga < self.__cargaMax)):
                #el motor solo se mueve si no esta en su final de recorrido y si la carga no es excedida
                gpio.output(self.__step, gpio.HIGH)
                #se setea la señal a high
                time.sleep(self.__consigna)
                #se espera un tiempo en high
                gpio.output(self.__step, gpio.LOW)
                #se setea la señal a low
                time.sleep(self.__consigna)
                #se espera un tiempo en low
                self.__pasos -= 1
                #cada vez que el codigo pase por aqui se da por hecho que el motor ha retrocede un paso
        
        elif val < 115: 
            #si val es menor que 115
            gpio.output(self.__dir, gpio.HIGH)
            #se establece sentido de giro horario
            self.__consigna =  round(1/(((115-val)/115)*1228.6 +200), 4)
            #se establece consigna en funcion del val recibido
            #el resultado corresponde con la frecuencia/2 de la señal

            if(self.__pasos < self.__alturaMAX):
                #el motor solo se mueve en este sentido si no esta en el limite hacia el que se dirige
                gpio.output(self.__step, gpio.HIGH)
                #se setea la señal a high
                time.sleep(self.__consigna)
                #se espera un tiempo en high
                gpio.output(self.__step, gpio.LOW)
                #se setea la señal a low
                time.sleep(self.__consigna)
                #se espera un tiempo en low
                self.__pasos += 1
                #cada vez que el codigo pase por aqui se da por hecho que el motor ha avanzado un paso       
        
    def getpasos(self):                        
    #Pasos avanzados desde origen
        return self.__pasos
    
    def getpasosM(self):                        
    #Pasos avanzados desde origen
        self.__pasosM = (self.__pasos*803)/self.__alturaMAX
        #conversion de pasos a mm, 6900 pasos son 803mm
        return int(self.__pasosM)
        #devuelve la distancia en mm
        
    def setpasos(self, pasos):                  
        #Modificar pasos
        self.__pasos = pasos
        #setea al valor que indiquemos en pasos
        #solamente es utilizado cuando se pulsa un final de carrera
        
    def getconsigna(self):
        return self.__consigna
        #devuelve la consigna calculada por el motor