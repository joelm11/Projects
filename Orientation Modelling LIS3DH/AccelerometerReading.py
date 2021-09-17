import serial
import struct
import sys
ser = serial.Serial()

def main():
    ser.baudrate = 57600
    ser.port = 'COM3'
    stall = input("Ready to go?")
    previous_unprocessed_data = 0
    ser.open()
    #for count in range(50):
    while(True):
        previous_unprocessed_data = getSensorData(previous_unprocessed_data)
    ser.close()
"""
MSP430 is bursting zyx output data from array
as bytes are received little-endian and pc is little-endian native, use '@'
whenever garbage data is received, the ordering of the bytes is messed up
"""
def getSensorData(data = 0):
    test_connection()
    data_as_bytes = ser.read_until(size = 6)
    try:
        unprocessed_data = struct.unpack('@hhh',data_as_bytes)
    except struct.error:
        unprocessed_data = data

    z,y,x = [elem * 9.806/16384 for elem in unprocessed_data]
    output = "Z acc: %.2f\t Y acc: %.2f\t X acc: %.2f"%(z,y,x)
    print(output)
    return unprocessed_data


def test_connection():
    testdata = ser.read_until(expected = b'\x40')

if __name__ == "__main__":
    main()
