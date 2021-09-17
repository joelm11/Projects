import serial
import struct
import sys

class SerialData():

    def __init__(self):
        self.ser = serial.Serial()
        self.ser.baudrate = 57600
        self.ser.port = 'COM3'
        self.x,self.y,self.z = 0,0,0
        self.previous_unprocessed_data = [0,0,0]

#MSP430 is bursting zyx output data from array
#as bytes are received little-endian and pc is little-endian native, use '@'
    def getSensorData(self, data = [0,0,0]):
        self.test_connection()
        data_as_bytes = self.ser.read_until(size = 6)
        try:
            unprocessed_data = struct.unpack('@hhh',data_as_bytes)
        except struct.error:
            #print(data_as_bytes)
            unprocessed_data = data

        self.z,self.y,self.x = [elem * 9.806/16384 for elem in unprocessed_data]
        self.output = "Z acc: %.2f\tY acc: %.2f\tX acc: %.2f"%(self.z,self.y,self.x)
        self.previous_unprocessed_data = unprocessed_data
        print(self.output)

    def test_connection(self):
        testdata = self.ser.read_until(expected = b'\x40')
