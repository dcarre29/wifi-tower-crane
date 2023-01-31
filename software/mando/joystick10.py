import board
#se importa para interactuar con los pines de la RPi
import busio
#Se importa para interactuar con el bus I2C
import ADS1x15.adafruit_ads1x15.ads1115 as ADS
#libreria para la gestion de canales ADC
from ADS1x15.adafruit_ads1x15.analog_in import AnalogIn
#libreria para el valor analogico del ADC


class Joystick():

    def __init__(self):
        #metodo constructor
        self.canal = busio.I2C(board.SCL, board.SDA)
        #declaracion de los pines del bus I2C
        self.adc = ADS.ADS1115(self.canal)
        #instanciacion del ADC
        self.__x = int(AnalogIn(self.adc, ADS.P2).value)
        #asignacion del valor del canal 2 del ADC al eje X
        self.__y = int(AnalogIn(self.adc, ADS.P1).value)
        #asignacion del valor del canal 1 del ADC al eje Y
        self.__z = int(AnalogIn(self.adc, ADS.P0).value)
        #asignacion del valor del canal 0 del ADC al eje Z


    def getAxis(self,eje):
        #metodo para transformar los datos del ADC
        if eje == 'x':
            #si eje corresponde a X
            self.__x = AnalogIn(self.adc, ADS.P2).value*(255/32768)
            #lectura del canal 2 y transformacion de 15 bits a 8 bits
            #para tener un valor de consigna mas estable
            if self.__x < 0: 
                self.__x = 0
            if self.__x > 255:
                self.__x = 255
            #Garantizacion de que el eje X estara entre 0 y 255
            return int(self.__x) 
            #retorna el valor calculado

        elif eje == 'y':
            #si eje corresponde a Y
            self.__y = AnalogIn(self.adc, ADS.P1).value*(255/32768)
            #lectura del canal 1 y transformacion de 15 bits a 8 bits
            #para tener un valor de consigna mas estable
            if self.__y < 0: 
                self.__y = 0
            if self.__y > 255:
                self.__y = 255
            #Garantizacion de que el eje y estara entre 0 y 255
            return int(self.__y)
            #retorna el valor calculado
            
        elif eje == 'z':
            #si eje corresponde a Z
            self.__z = AnalogIn(self.adc, ADS.P0).value*(255/32768)
            #lectura del canal 0 y transformacion de 15 bits a 8 bits
            #para tener un valor de consigna mas estable
            if self.__z < 0: 
                self.__z = 0
            if self.__z > 255:
                self.__z = 255
            #garantizacion de que el eje z estara entre 0 y 255
            return int(self.__z)
            #retorna el valor calculado