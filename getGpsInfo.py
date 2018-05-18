import serial
import pynmea2
import time
# import sched
from threading import Timer

def getGps(ser):
    line = ser.readline()
    if line.startswith('$GNRMC'):
        rmc = pynmea2.parse(line)
        print rmc
        lat = rmc.lat
        lon = rmc.lon
        timestamp = rmc.timestamp
        if lat != "" and lon != "":
            print "Latitude: ", float(lat)/100
            print "Longitude: ", float(lon)/100
            print "TimeStamp: ", timestamp

ser = serial.Serial("/dev/ttyUSB0",9600)
# while True:
#     line = ser.readline()
#     if line.startswith('$GNRMC'):
#         rmc = pynmea2.parse(line)
#         lat = rmc.lat
#         lon = rmc.lon
#         if lat != "" and lon != "":
#             print "Latitude: ", float(lat)/100
#             print "Longitude: ", float(lon)/100
# schedule = sched.scheduler(time.time, time.sleep)
# schedule.enter(10,0,getGps,ser)
Timer(5,getGps,(ser,)).start()
# while True:
#     pass
    # getGps(ser)