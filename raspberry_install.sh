#改源
#1.编辑sources.list 文件
sudo vim /etc/apt/sources.list
#deb http://mirrors.ustc.edu.cn/raspbian/raspbian/ stretch main contrib non-free rpi
#2.编辑raspi.list 文件
sudo vim /etc/apt/sources.list.d/raspi.list
#deb http://mirrors.ustc.edu.cn/archive.raspberrypi.org/debian/ stretch main ui staging
sudo apt-get update
#安装远程桌面访问
sudo apt-get install xrdp
sudo apt-get install vim
#打开设置,启用摄像头
sudo sudo raspi-config
#安装opencv
sudo apt-get install build-essential
sudo apt-get install libavformat-dev
sudo apt-get install ffmpeg
sudo apt-get install libcv-dev
sudo apt-get install libcvaux-dev
sudo apt-get install libhighgui-dev
sudo apt-get install libcblas-dev
sudo apt-get install libatlas-dev
sudo apt-get install libatlas3-base
sudo apt-get install libjasper-dev
sudo apt-get install qt4-dev-tools qt4-doc qt4-qtconfig
#读取摄像头
sudo vim /etc/modules #添加 bcm2835-v4l2
sudo pip3 install opencv-python
#安装pyzbar
sudo apt-get install python-zbar
sudo pip3 install pyzbar
#安装pyqt5
sudo apt-get install python3-pyqt5
#安装pynmea2
sudo pip3 install pynmea2
#安装语音库
sudo apt-get install espeak
sudo pip3 install pyttsx3
#安装中文输入法
sudo apt-get install scim-pinyin
#清理垃圾文件
#包管理的临时文件目录:
#包在
#/var/cache/apt/archives
#没有下载完的在
#/var/cache/apt/archives/partial

