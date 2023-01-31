import socket
#Libreria para la comunicacion socket
import time
#libreria para controlar el tiempo
import logging
#libreria para depurar los hilos
from motorPAP import M_Carro, M_Gancho, M_Orientacion
#libreria para el manejo de los motores de la grua
import threading
#libreria para el manejo de hilos
import RPi.GPIO as GPIO
#libreria para el manejo del los pines de la RPi
from hx711 import HX711
#libreria para el manejo del sensor de peso


#variables a enviar
orientacion = 255
#variable cuyo valor sera equivalente a la orientacion de la pluma con respecto a su 0
distcarro = 254                                                     
#variable cuyo valor sera equivalente a la distancia del carro a la torre siendo 0 cuando carro y torre estan pegados
discarga = 253                                                      
#variable cuyo valor sera equivalente a la distancia desde el gancho al carro siento 0 cuando el cable esta totalmente recogido 
peso = 0                                                         
#variable cuyo valor es equivalente al peso de la carga
unidadReferencia = 1773                                             
#variable para calibrar la celula de carga cuando su peso es 0
                                                                    
#variables motores
vejex = 130                                                         
#valor del ejex del joystick que se corresponde con la consigna de velocidad del motor del carro
vejey = 130                                                         
#valor del ejey del joystick que se corresponde con la consigna de velocidad del motor del cable
vejez = 130                                                         
#valor del ejez del joystick que se corresponde con la consigna de velocidad del motor de orientacion
paquetes  = 0
#variable para contar el numero de ciclos del bucle comunicacion

vejexrecibido = 130
#valor de consigna que se recibe para el motor del carro
vejeyrecibido = 130
#valor de consigna que se recibe para el motor del cable
vejezrecibido = 130
#valor de consigna que se recibe para el motor del orientacion
pesoleido= 0
#valor del peso que se lee en la celda de carga

semaforoX = threading.Lock()
semaforoY = threading.Lock()
semaforoZ = threading.Lock()
semaforoPeso = threading.Lock()
#semaforos para cada eje y el peso
#estos semaforos serviran para evitar leer informacion justo en el momento que se esta escribiendo

#Instancia de los motores con los pines en modo BCM
motor1 = M_Carro(15, 25)                                        
#motor del Carro con los pines dir y step respectivamente
#velocidad MAX = 0.0007 Velocidad Min  0.005 para A4988
motor2 = M_Orientacion(27, 22)                                        
#motor del orientacion con los pines dir y step respectivamente
#velocidad MAX = 0.001 Velocidad Min  0.005 para A4988
motor3 = M_Gancho(18, 17)                                
#motor del Gancho con los pines dir y step respectivamente
#velocidad MAX = 0.0007 Velocidad Min  0.005 para A4988


fc_cable = 24
#Pin del final de carrera del cable
fc_carro = 23
#pin del final de carrera del carro

GPIO.setup(fc_cable, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)         
#configuracion del final de carrera para el cable con el pin correspondiente
#configuracion pull-down
GPIO.setup(fc_carro, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)        
#configuracion del final de carrera para el carro de la pluma con el pin correspondiente
#configuracion pull-down

                                                 
celula = HX711(5,6)                                                
#instancia de la cecula de carga, pines DOUT y SCK respectivamente
celula.set_reading_format("MSB", "MSB")                             
#orden de lectura de bytes y de bits
celula.set_reference_unit(unidadReferencia)
#se establece la referencia                                                                                                           

celula.reset()
#reset del sensor de peso para poder tararlo
celula.tare()
#tara del sensor de peso

def comunicacion():                                                 
    #Método al que accede el hilo para comunicarse con el cliente
    global vejexrecibido, vejeyrecibido, vejezrecibido, pesoleido                     
    #Declaración de las variables dentro del metodo para poder modificarse
    while True: 
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      
        #Creamos el socket del servidor

        serverAdress = ('192.168.1.136', 8080)                      
        #Tupla de dirección y puerto del servidor
        print(' Starting server ...' , serverAdress)
        #impresion de estado por consola
        ss.bind(serverAdress)                                       
        #Se construye el servidor
        ss.listen(1)                                                
        #Esperamos conexion de un solo cliente
        print('Waiting for a client...')
        #impresion de estado por consola
        connection, clientAdress = ss.accept()                      
        #Envio confirmacion de conexion al cliente

        try: 
            print('Conection from ... ', clientAdress)
            #impresion de estado por consola                                                                                                                                       #borrar despues de acabar proyecto, se utilizo para definir el timeout
            connection.settimeout(0.8)
            #se establece el tiempo maximo de inactividad en la comunicacion
            while True:                                                                                                                    #borrar despues de acabar proyecto, se utilizo para definir el timeout  
                semaforoPeso.acquire()
                #se bloquea el acceso de lectura a la variable pesoleido                                                                                                                                
                pesoleido = int(celula.get_weight(1))
                #actualizacion del peso actual                    
                if pesoleido <0:
                    pesoleido = 0
                #descartamos pesos negativos debido a que la comunicacion no soporta
                #variables con valores negativos
                semaforoPeso.release()
                #Se desbloquea el acceso de lectura de la variable pesoleido


                #intercambio de datos entre cliente y servidor
                semaforoX.acquire()
                #se bloquea el acceso de lectura a la variable vejexrecibido
                vejexrecibido = int.from_bytes(connection.recv(1), 'big')
                #recepcion valor de eje x del joystick del mando, se corresponde con el movimiento del carro
                semaforoX.release()
                #Se desbloquea el acceso de lectura de la variable
                connection.send(orientacion.to_bytes(15, 'big'))    
                #envio del estado de la variable orientacion al mando
                semaforoY.acquire()
                #se bloquea el acceso de lectura a la variable vejeyrecibido
                vejeyrecibido = int.from_bytes(connection.recv(1), 'big')   
                #recepcion valor de eje y del joystick del mando, se corresponde con el movimiento del cable
                semaforoY.release()
                #Se desbloquea el acceso de lectura de la variable
                connection.send(distcarro.to_bytes(15, 'big'))      
                #envio del valor de la variable distcarro al mando
                semaforoZ.acquire()
                #se bloquea el acceso de lectura a la variable vejezrecibido
                vejezrecibido = int.from_bytes(connection.recv(1), 'big')   
                #recepcion valor de eje z del joystick del mando, se corresponde con el movimiento de orientacion
                semaforoZ.release()
                #Se desbloquea el acceso de lectura de la variable
                connection.send(discarga.to_bytes(15, 'big'))
                #envio del valor de la variable discarga al mando
                data = connection.recv(4).decode('utf-8')           
                #recepcion del la peticion peso desde el mando
                if data == 'peso':
                    connection.send(peso.to_bytes(15, 'big'))       
                    #envio del valor de peso al mando                              

        except KeyboardInterrupt:
            print('cerrado por teclado')
            #impresion de estado por consola
            connection.close()
            ss.close()
            
        except socket.timeout:
            #tratamiento de la excepcion timeout
            print("Time out en el servidor")
            #impresion de estado por consola
            vejexrecibido = 120                                            
            vejeyrecibido = 120
            vejezrecibido = 120
            #actualizacion de las variables consigna para dejar los motores en bloqueo                                                                                                                                       #borrar al finalizar el proyecto
            continue                                                
            #volvemos a esperar una conexion de cliente dentro del bucle
        except BrokenPipeError: 
            #tratamiento de la excepcion cuando hay cierre o fallo de conexion
            vejexrecibido = 120                                            
            vejeyrecibido = 120
            vejezrecibido = 120
            #actualizacion de las variables consigna para dejar los motores en bloqueo                                                                                                                                 #borrar al finalizar el proyecto
            continue
            #volvemos a esperar una conexion de cliente
        except ConnectionResetError:
            #tratamiento de la excepcion cuando hay cierre o fallo de conexion
            vejexrecibido = 120                                            
            vejeyrecibido = 120
            vejezrecibido = 120
            #actualizacion de las variables consigna para dejar los motores en bloqueo
            continue
        

def m1(): 
    #motor1 = motor carro
    global distcarro, peso, vejex
    #variable a global a actualizar
    while True:
                                                                                                                                                                #print("{:>5}\t{:>5}\t{:>5}\t{:>5}".format(vejex, vejey, vejez, paquetes))
        distcarro = motor1.getpasosM()
        #actualizacion de la distancia recorrida
        if not semaforoX.locked():
            #si el semaforo correspondiente no esta bloqueado actualiza el valor
            vejex = vejexrecibido
        if not semaforoPeso.locked():
            peso = pesoleido
            #si el semaforo correspondiente no esta bloqueado actualiza el valor

        motor1.go(vejex, carga = peso)
        #envio de consigna actual y el peso de la grua al motor para moverlo

        if (GPIO.input(fc_carro)): 
            motor1.setpasos(0)
        #en caso de que el final de carrera sea pulsado, la variable distcarro sera igual a 0

          
        

def m2(): 
    #motor2 = motor orientacion
    global orientacion, peso, vejez
    #variable a global a actualizar
    while True:
        orientacion =  motor2.getpasosM()
        #actualizacion de la distancia recorrida
        if not semaforoZ.locked():
            #si el semaforo correspondiente no esta bloqueado actualiza el valor
            vejez = vejezrecibido
        if not semaforoPeso.locked():
            #si el semaforo correspondiente no esta bloqueado actualiza el valor
            peso = pesoleido
        motor2.go(vejez, carga = peso, pasos_carro = motor1.getpasos())
        #envio de consigna al motor para moverlo     
        

def m3(): 
    #motor3 = motor gancho 
    global discarga, vejey, peso
    #variable a global a actualizar    
    while True:

        discarga = motor3.getpasosM()
        #actualizacion de la distancia recorrida
        if not semaforoY.locked():
            #si el semaforo correspondiente no esta bloqueado actualiza el valor
            vejey = vejeyrecibido
        if not semaforoPeso.locked():
            #si el semaforo correspondiente no esta bloqueado actualiza el valor
            peso = pesoleido
        motor3.go(vejey, carga = peso, pasos_carro= motor1.getpasos())
        #envio de consigna al motor para moverlo
        if (GPIO.input(fc_cable)): 
            motor3.setpasos(0)
        #en caso de que el final de carrera sea pulsado, la variable discarga sera igual a 0



hilo1 = threading.Thread(target= m1, name= "motor1")
hilo2 = threading.Thread(target= m2, name= "motor2")
hilo3 = threading.Thread(target= m3, name= "motor3")
hilo4 = threading.Thread(target= comunicacion, name= "comunicacion")
#Instanciacion de los hilos, se pone asocia con un metodo objetivo y se pone nombre a cada hilo
                                                                                                                                                     #borrar el try y except al acabar el proyecto
hilo4.start()
hilo1.start()
hilo2.start()
hilo3.start()
#lanzamiento de todos los hilos

