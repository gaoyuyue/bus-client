import sys
from urllib import request
from urllib import parse
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import pygame
import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import time
import serial
import pynmea2

licensePlate = "ABC"
address = "http://10.55.90.6:8080"
positionInfoId = 0

class PostHandler(QThread):
    def __init__(self,url,parent=None):
        super(PostHandler, self).__init__(parent)
        self.url = url
        self.changed=False

    def run(self):
        while True:
            if self.changed:
                data = parse.urlencode(self.data).encode('utf-8')
                req = request.Request(self.url, data)
                request.urlopen(req)
                self.changed = False

    def gpsChange(self,data):
        self.changed = True
        self.data = {"id":str(positionInfoId),"lat":data[0],"lon":data[1],"timestamp":data[2]}

    def scanChange(self,data):
        self.changed = True
        self.data = {"id":str(data)}

class GPSHandler(QThread):
    gps = pyqtSignal(list)

    def __init__(self,parent=None):
        super(GPSHandler, self).__init__(parent)
    def run(self):
        ser = serial.Serial("/dev/ttyUSB0", 9600)
        while True:
            self.getGpsInfo(ser)
            time.sleep(1)

    def getGpsInfo(self,ser):
        line = bytes.decode(ser.readline())
        if line.startswith('$GNRMC'):
            rmc = pynmea2.parse(line)
            print(rmc)
            lat = rmc.lat
            lon = rmc.lon
            timestamp = str(rmc.timestamp)
            if lat != "" and lon != "" and timestamp != "":
                self.gps.emit([timestamp,lat,lon])
            else:
                self.gps.emit([ "16:06","3920.2856", "11858.5302"])

class LoadDialog(QDialog):
    def __init__(self,parent=None):
        super(LoadDialog, self).__init__(parent)
        self.setWindowTitle(self.tr("启动"))
        self.gifLabel = QLabel()
        self.textLabel = QLabel(self.tr("连接中..."))
        self.textLabel.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.gifLabel,0)
        layout.addWidget(self.textLabel,1)
        self.setLayout(layout)

        movie = QMovie("./loading.gif")
        movie.setCacheMode(QMovie.CacheAll)
        movie.setSpeed(100)
        self.gifLabel.setMovie(movie)
        movie.start()
        self.connect_process = ConnectHandler(self.textLabel)
        self.connect_process.busCount.connect(self.close)
        self.connect_process.start()

class ScanningHandler(QThread):
    seatNum = pyqtSignal(int)
    id = pyqtSignal(int)

    def __init__(self,busNum,parent=None):
        super(ScanningHandler, self).__init__(parent)
        self.busNum = busNum

    def run(self):
        self.scanning("/home/pi/audio/")

    def decrypt(self,message):
        with open('private.pem') as f:
            key = f.read()
            rsakey = RSA.importKey(key)
            cipher = Cipher_pkcs1_v1_5.new(rsakey)
            text = cipher.decrypt(base64.b64decode(message), "ERROR")
            return text

    def playMP3(self,path):
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

    def scanning(self,path):
        results = set()
        camera = cv2.VideoCapture(0)

        last = ""
        while (camera.isOpened()):
            grabbed, frame = camera.read()
            if not grabbed:
                break
            pil = Image.fromarray(frame).convert('L')
            width, height = pil.size
            raw = pil.tobytes()
            zarimage = decode((raw, width, height))

            for symbol in zarimage:
                # if not symbol.count:
                data = bytes.decode(self.decrypt(symbol.data))
                if last == data:
                    continue
                else:
                    last = data
                if data == "":
                    continue
                result = data.split(":")
                if len(result) != 3 or result[0] == "" or result[1] == "" or result[2] == "":
                    continue
                if result[0] != str(self.busNum):
                    self.playMP3(path + "s" + result[0] + ".mp3")
                else:
                    if result[1] in results:
                        self.playMP3(path + "e.mp3")
                    else:
                        results.add(result[1])
                        self.seatNum.emit(int(result[1]))
                        self.id.emit(int(result[2]))
                        self.playMP3(path + "c" + result[1] + ".mp3")
                print('decoded:' + symbol.type + 'symbol:' + data)
        camera.release()

class ConnectHandler(QThread):
    busCount = pyqtSignal(int)

    def __init__(self,textLabel,parent=None):
        self.textLabel = textLabel
        super(ConnectHandler, self).__init__(parent)

    def run(self):
        while True:
            b = self.connect(self.textLabel)
            if b :
                break
            else:
                self.slotCritical()

    def slotCritical(self):
        QMessageBox.critical(self, "Critical",
                             self.tr("链接失败！"))

    def connect(self,textLabel):
        response = request.urlopen("http://172.30.0.11")
        if response.getcode() == 200:
            self.busCount.emit(10)
            textLabel.setText("链接成功！")
            return True
        else:
            textLabel.setText("链接失败！")
            return False

class BusNumberDialog(QDialog):
    busNumber = pyqtSignal(int)
    def __init__(self,parent=None):
        super(BusNumberDialog, self).__init__(parent)
        self.setWindowTitle("车号")

    def show(self,num):
        layout = QGridLayout()
        col = 4
        for i in range(num):
            r = i / col
            c = i % col
            b = QPushButton(str(i + 1))
            b.clicked.connect(self.setBus)
            layout.addWidget(b, r, c)
        self.setLayout(layout)
        super(BusNumberDialog, self).show()

    def setBus(self):
        b = self.sender()
        self.slotQuestion(b.text())

    def slotQuestion(self,num):
        button = QMessageBox.question(self, "Question",
                                      self.tr("确定选择车号"+num+"?"),
                                      QMessageBox.Ok | QMessageBox.Cancel,
                                      QMessageBox.Ok)
        if button == QMessageBox.Ok:
            self.request(int(num))
        else:
            return

    def request(self,num):
        values = {'licensePlate': licensePlate, 'number': str(num)}
        data = parse.urlencode(values).encode('utf-8')
        req = request.Request(address+"/setBusNumber", data)
        response = request.urlopen(req)
        if response.getcode() == 200:
            global positionInfoId
            positionInfoId = int(response.read())
            self.busNumber.emit(num)
            self.close()

class SeatDialog(QDialog):
    def __init__(self,parent=None):
        super(SeatDialog, self).__init__(parent)
        self.setWindowTitle("车辆状态")
        latLabel = QLabel("纬度：")
        lonLabel = QLabel("经度：")
        timeLabel = QLabel("时间：")
        self.latText = QLabel()
        self.lonText = QLabel()
        self.timeText = QLabel()
        poistionBox = QGroupBox("定位信息")
        headerLayout = QHBoxLayout()
        headerLayout.addWidget(latLabel)
        headerLayout.addWidget(self.latText)
        headerLayout.addWidget(lonLabel)
        headerLayout.addWidget(self.lonText)
        headerLayout.addWidget(timeLabel)
        headerLayout.addWidget(self.timeText)
        poistionBox.setLayout(headerLayout)
        seatBox = QGroupBox("座位号")
        bodyLayout = QGridLayout()
        col = 4
        for i in range(50):
            r = i / col
            c = i % col
            b = QPushButton(str(i+1))
            b.setObjectName(str(i+1))
            b.setStyleSheet('background-color:green')
            bodyLayout.addWidget(b,r,c)
        seatBox.setLayout(bodyLayout)
        layout = QVBoxLayout()
        layout.addWidget(poistionBox)
        layout.addWidget(seatBox)
        self.setLayout(layout)

    def show(self,num):
        scanning_process = ScanningHandler(num)
        scanning_process.seatNum.connect(self.setSeat)
        scanning_process.start()
        scanning_post = PostHandler(address+"/getOn")
        scanning_process.id.connect(scanning_post.scanChange)
        scanning_post.start()
        gps_process = GPSHandler()
        gps_process.gps.connect(self.setPosition)
        gps_process.start()
        gps_post = PostHandler(address+"/addGps")
        gps_process.gps.connect(gps_post.gpsChange)
        gps_post.start()
        super(SeatDialog, self).show()

    def setSeat(self,num):
        b = self.findChild(QPushButton, str(num))
        b.setStyleSheet('background-color:red')
        print(str(num))

    def setPosition(self,info):
        timestamp = info[0]
        lat = str(float(info[1])/100)
        lon = str(float(info[2])/100)
        self.latText.setText(lat)
        self.lonText.setText(lon)
        self.timeText.setText(timestamp)

app = QApplication(sys.argv)
dialog = LoadDialog()
dialog.show()
busNumberDialog = BusNumberDialog()
dialog.connect_process.busCount.connect(busNumberDialog.show)
seatDialog = SeatDialog()
busNumberDialog.busNumber.connect(seatDialog.show)
app.exec_()