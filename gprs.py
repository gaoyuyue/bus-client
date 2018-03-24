import re
import serial

ser = serial.Serial('/dev/ttyUSB1')
ser.write('AT\r'.encode('utf-8'))
while True:
    line = ser.readline()
    print line
    if re.search(b'OK',line):
        break