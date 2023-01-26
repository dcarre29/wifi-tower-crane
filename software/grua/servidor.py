import socket
import sys
import busio
import time
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

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



i2c = busio.I2C(board.SCL, board.SDA)   #Declaracion de pines bus I2C
ads = ADS.ADS1115(i2c)                  #Instancia del ADC1115
while True:
    try:
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        serverAdress = ('192.168.1.135', 8080)
        print(' Starting server ...' , serverAdress)
        ss.bind(serverAdress)
        ss.listen(1)  #Esperamos conexion de un solo cliente
        print('Waiting for a client...')

        connection, clientAdress = ss.accept()  #Envio confirmacion al cliente


        print('Conection from ... ', clientAdress)

        connection.settimeout(5)
        while True:

            data = connection.recv(4).decode('utf-8')
        
            if data == 'ejex':
                connection.send(bytes(1))

                vejex = int.from_bytes(connection.recv(1), 'big')
                connection.send(bytes(1))

                data = connection.recv(4).decode('utf-8')
                
                if data == 'ejey':
                    connection.send(bytes(1))
                    vejey = int.from_bytes(connection.recv(1), 'big')
                    connection.send(bytes(1))
                    data = connection.recv(4).decode('utf-8')
                
                    if data == 'ejez':
                        connection.send(bytes(1))
                        vejez = int.from_bytes(connection.recv(1), 'big')
                        connection.send(bytes(1))
                        print("{:>5}\t{:>5}\t{:>5}\t{:>5}".format(vejex, vejey, vejez, paquetes))


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
        print('cerrado')

    except socket.timeout:
        print("Time out en el servidor")
        ss.close()
        time.sleep(3)
        continue
        #Aqui abria que poner las consignas de todo a cero o matarlos hilos
        # y volver a esperar una conexion con el cliente

    except BrokenPipeError:
        print("fallo en comunicacion")
        ss.close()
        continue
    '''except OSError:
        ss.close()
        print("Error")
        break
    '''
