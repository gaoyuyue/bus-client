import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
# import pygame
import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import time
import serial
import pynmea2
import requests

licensePlate = 1
busBookServerAddress = "http://10.55.90.6:8000"
positionServerAddress = "http://10.55.90.6:8099"
serialPort = "/dev/ttyUSB1"
audioPath = "/home/pi/audio"

class PostHandler(QThread):
    def __init__(self,url,parent=None):
        super(PostHandler, self).__init__(parent)
        self.url = url
        self.changed=False

    def run(self):
        while not self.isInterruptionRequested():
            if self.changed:
                response = requests.post(self.url, data=self.data)
                print(response.content)
                self.changed = False

    def gpsChange(self,data):
        if data[0] != "无信号":
            self.changed = True
            self.data = {"key":busMarkId,"latitude":data[1],"longitude":data[2]}

    def scanChange(self,data):
        self.changed = True
        self.data = {"id":data}

class GPSHandler(QThread):
    gps = pyqtSignal(list)

    def __init__(self,parent=None):
        super(GPSHandler, self).__init__(parent)
    def run(self):
        ser = serial.Serial(serialPort, 9600)
        while not self.isInterruptionRequested():
            self.getGpsInfo(ser)
            time.sleep(1)

    def getGpsInfo(self,ser):
        line = bytes.decode(ser.readline())
        if line.startswith('$GNRMC'):
            rmc = pynmea2.parse(line)
            lat = rmc.lat
            lon = rmc.lon
            timestamp = str(rmc.timestamp)
            if lat != "" and lon != "" and timestamp != "":
                self.gps.emit([timestamp,float(lat)/100, float(lon)/100])
            else:
                self.gps.emit([ "无信号","无信号", "无信号"])

class ScanningHandler(QThread):
    seatNum = pyqtSignal(int)
    id = pyqtSignal(int)

    def __init__(self,busInfo,parent=None):
        super(ScanningHandler, self).__init__(parent)
        self.busNum = busInfo["busNum"]
        self.busNumInfoId = busInfo["busNumInfoId"]

    def run(self):
        self.scanning()

    def decrypt(self,message):
        with open('private.pem') as f:
            key = f.read()
            rsakey = RSA.importKey(key)
            cipher = Cipher_pkcs1_v1_5.new(rsakey)
            text = cipher.decrypt(base64.b64decode(message), "ERROR")
            return text

    def playMP3(self,path):
        pass
        #pygame.mixer.init()
        #pygame.mixer.music.load(path)
        #pygame.mixer.music.play()

    def scanning(self):
        results = set()
        camera = cv2.VideoCapture(0)

        last = ""
        while (camera.isOpened() and not self.isInterruptionRequested()):
            grabbed, frame = camera.read()
            if not grabbed:
                break
            pil = Image.fromarray(frame).convert('L')
            width, height = pil.size
            raw = pil.tobytes()
            zarimage = decode((raw, width, height))

            for symbol in zarimage:
                data = bytes.decode(self.decrypt(symbol.data))
                if last == data:
                    continue
                else:
                    last = data
                if data == "":
                    continue
                result = data.split(":")
                if len(result) != 4 or result[0] == "" or result[1] == "" or result[2] == "" or result[3] == "":
                    continue
                if result[0] != str(self.busNumInfoId):
                    continue
                if result[1] != str(self.busNum):
                    self.playMP3(audioPath + "s" + result[1] + ".mp3")
                else:
                    if result[2] in results:
                        self.playMP3(audioPath + "e.mp3")
                    else:
                        results.add(result[2])
                        self.seatNum.emit(int(result[2]))
                        self.id.emit(int(result[3]))
                        self.playMP3(audioPath + "c" + result[2] + ".mp3")
                print('decoded:' + symbol.type + 'symbol:' + data)
        camera.release()

class BusNumberDialog(QDialog):
    selected = pyqtSignal(dict)

    def __init__(self,parent=None):
        super(BusNumberDialog, self).__init__(parent)
        self.setWindowTitle("车号")

    def show(self):
        selectLayout = QVBoxLayout()

        self.directionComboBox = QComboBox(self)
        self.directionComboBox.addItem("-----------请选择发车方向---------")
        self.directionComboBox.addItem("唐山----曹妃甸","01")
        self.directionComboBox.addItem("曹妃甸----唐山","10")
        self.routeComboBox = QComboBox(self)
        self.routeComboBox.addItem("-----------请选择发车线路---------")
        self.startTimeComboBox = QComboBox(self)
        self.startTimeComboBox.addItem("-----------请选择发车时间---------")
        self.busNumComboBox = QComboBox(self)
        self.busNumComboBox.addItem("-----------请选择车号---------")

        selectButton = QPushButton('确认选择')
        self.directionComboBox.setLayout(selectLayout)
        self.routeComboBox.setLayout(selectLayout)
        self.startTimeComboBox.setLayout(selectLayout)
        self.busNumComboBox.setLayout(selectLayout)
        selectButton.setLayout(selectLayout)

        selectButton.clicked.connect(self.select)
        self.directionComboBox.currentIndexChanged.connect(self.getRoute)
        self.routeComboBox.currentIndexChanged.connect(self.getStartTime)
        self.startTimeComboBox.currentIndexChanged.connect(self.getBusNum)

        layout = QVBoxLayout()
        layout.addWidget(self.directionComboBox)
        layout.addWidget(self.routeComboBox)
        layout.addWidget(self.startTimeComboBox)
        layout.addWidget(self.busNumComboBox)
        layout.addWidget(selectButton)
        self.setLayout(layout)
        super(BusNumberDialog, self).show()

    def getRoute(self):
        print("direction")
        print(self.directionComboBox.currentIndex())
        if self.directionComboBox.currentIndex() <= 0:
            self.routeComboBox.clear()
            self.routeComboBox.addItem("-----------请选择发车线路---------")
        else:
            self.routeComboBox.clear()
            self.routeComboBox.addItem("-----------请选择发车线路---------")
            response = requests.get(busBookServerAddress + "/public/getRoute", params={"direction": self.directionComboBox.currentData()})
            for e in response.json():
                self.routeComboBox.addItem(e["routeName"],e["routeId"])

    def getStartTime(self):
        print("route")
        print(self.routeComboBox.currentIndex())
        if self.routeComboBox.currentIndex() <= 0:
            self.startTimeComboBox.clear()
            self.startTimeComboBox.addItem("-----------请选择发车时间---------")
        else:
            self.startTimeComboBox.clear()
            self.startTimeComboBox.addItem("-----------请选择发车时间---------")
            response = requests.get(busBookServerAddress + "/public/getBusNumInfo",
                                    params={"routeId": self.routeComboBox.currentData()})
            print(response.json())
            for e in response.json():
                self.startTimeComboBox.addItem(e["startTime"], e["busNumInfoId"])

    def getBusNum(self):
        print("startTime")
        print(self.startTimeComboBox.currentIndex())
        if self.startTimeComboBox.currentIndex() <= 0:
            self.busNumComboBox.clear()
            self.busNumComboBox.addItem("-----------请选择车号---------")
        else:
            self.busNumComboBox.clear()
            self.busNumComboBox.addItem("-----------请选择车号---------")
            response = requests.get(busBookServerAddress + "/public/getBusMark",
                                    params={"busNumInfoId": self.startTimeComboBox.currentData()})
            print(response.json())
            for e in response.json():
                self.busNumComboBox.addItem(e["busMark"], e["busMarkInfoId"])

    def select(self):
        if self.directionComboBox.currentIndex() == 0 or self.routeComboBox.currentIndex() == 0 or self.startTimeComboBox.currentIndex() == 0 or self.busNumComboBox.currentIndex() == 0:
            QMessageBox.warning(self, "Warring",
                                self.tr("信息输入不完整"),
                                QMessageBox.Ok, QMessageBox.Ok)
        else:
            button = QMessageBox.question(self, "Question",
                                          self.tr("确定选择?"),
                                          QMessageBox.Ok | QMessageBox.Cancel,
                                          QMessageBox.Ok)
            if button == QMessageBox.Ok:
                response = requests.post(busBookServerAddress + "/public/postBusMark",
                                        data={"busMarkInfoId": self.busNumComboBox.currentData(),
                                                "deviceId": licensePlate})
                result = response.json()
                print(result)
                if result == 1:
                    self.selected.emit({"busNum":self.busNumComboBox.currentIndex(),
                                         "busNumInfoId":self.startTimeComboBox.currentData()})
                    global busMarkId
                    busMarkId = self.busNumComboBox.currentData()
                    self.close()
                elif result == -1:
                    QMessageBox.warning(self, "Warring",
                                         self.tr("此车号已被其他设备绑定"),
                                         QMessageBox.Ok,
                                         QMessageBox.Ok)
                else:
                    pass


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
        response = requests.get(busBookServerAddress + "/public/getBusCapacity")
        for i in range(response.json()):
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

    def show(self,busInfo):
        self.scanning_process = ScanningHandler(busInfo)
        self.scanning_process.seatNum.connect(self.setSeat)
        self.scanning_process.start()
        self.scanning_post = PostHandler(busBookServerAddress + "/public/postOn")
        self.scanning_process.id.connect(self.scanning_post.scanChange)
        self.scanning_post.start()
        self.gps_process = GPSHandler()
        self.gps_process.gps.connect(self.setPosition)
        self.gps_process.start()
        self.gps_post = PostHandler(positionServerAddress + "/position")
        self.gps_process.gps.connect(self.gps_post.gpsChange)
        self.gps_post.start()
        super(SeatDialog, self).show()

    def setSeat(self,num):
        b = self.findChild(QPushButton, str(num))
        b.setStyleSheet('background-color:red')
        print(str(num))

    def setPosition(self,info):
        timestamp = info[0]
        lat = str(info[1])
        lon = str(info[2])
        self.latText.setText(lat)
        self.lonText.setText(lon)
        self.timeText.setText(timestamp)

    def close(self):
        self.gps_process.requestInterruption()
        self.gps_post.requestInterruption()
        self.scanning_process.requestInterruption()
        self.scanning_post.requestInterruption()
        super(SeatDialog, self).close()

app = QApplication(sys.argv)
busNumberDialog = BusNumberDialog()
busNumberDialog.show()
seatDialog = SeatDialog()
busNumberDialog.selected.connect(seatDialog.show)
app.exec_()