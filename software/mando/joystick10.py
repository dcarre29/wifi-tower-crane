import time
import board
import busio
import ADS1x15.adafruit_ads1x15.ads1115 as ADS
from ADS1x15.adafruit_ads1x15.analog_in import AnalogIn



class Joystick():

    def __init__(self):

        self.canal = busio.I2C(board.SCL, board.SDA)
        self.adc = ADS.ADS1115(self.canal)
        self.__x = int(AnalogIn(self.adc, ADS.P2).value)
        self.__y = int(AnalogIn(self.adc, ADS.P1).value)
        self.__z = int(AnalogIn(self.adc, ADS.P0).value)


    def getAxis(self,eje):
        if eje == 'x':
            self.__x = AnalogIn(self.adc, ADS.P2).value*(255/32768)
            if self.__x < 0: 
                self.__x = 0
            if self.__x > 255:
                self.__x = 255

            return int(self.__x) 

        elif eje == 'y':

            self.__y = AnalogIn(self.adc, ADS.P1).value*(255/32768)

            if self.__y < 0: 
                self.__y = 0
            if self.__y > 255:
                self.__y = 255

            return int(self.__y)
            
        elif eje == 'z':

            self.__z = AnalogIn(self.adc, ADS.P0).value*(255/32768)
            if self.__z < 0: 
                self.__z = 0
            if self.__z > 255:
                self.__z = 255

            return int(self.__z)