import re
import serial

ser = serial.Serial('/dev/ttyUSB1',9600)
ser.write('AT+CIPSTART="TCP","101.200.46.138",80\r'.encode('utf-8'))
while True:
    line = ser.readline()
    print line
    if re.search(b'CONNECT',line):
        break
    elif re.search(b'ERROR',line):
        print 'error'
        break

s = "GET / HTTP/1.1 \r".encode('utf-8')
n = len(s)
ser.write('AT+CIPSEND='+str(n)+'\r'.encode('utf-8'))
while True:
    s = ser.read(1)
    if s == b'>':
        ser.write(s)
        while True:
            line = ser.readline()
            if re.search(b'IPD,',line):
                m = line.split(",")[1].split(":")
                l = int(m[0])-len(m[1])
                response = m[1] + ser.read(l)
                print response
                break
# AT+CIPSTART=TCP,139.199.123.243,8080
# AT+CIPSEND=20

