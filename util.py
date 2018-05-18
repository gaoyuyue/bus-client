import base64

import pygame
import qrcode
import cv2
import zbar
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from PIL import Image

def generateQRCode(str):
    qr = qrcode.QRCode(version=7, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(str)
    qr.make(fit=True)
    img = qr.make_image()
    img.save("qr.png")

def playMP3(path):
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

def scanningQRCode():
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    font = cv2.FONT_HERSHEY_SIMPLEX
    camera = cv2.VideoCapture(0)

    while (True):
        grabbed, frame = camera.read()
        if not grabbed:
            break
        pil = Image.fromarray(frame).convert('L')
        width, height = pil.size
        raw = pil.tobytes()
        zarimage = zbar.Image(width, height, 'Y800', raw)
        scanner.scan(zarimage)
        for symbol in zarimage:
            if not symbol.count:
                data = decrypt(symbol.data)
                playMP3(data)
                # print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
                print 'decoded', symbol.type, 'symbol', '"%s"' % data
                # cv2.putText(frame, symbol.data, (20, 100), font, 1, (0, 255, 0), 4)
                cv2.putText(frame, "hello:"+data, (20, 100), font, 1, (0, 255, 0), 4)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def encrypt(message):
    with open('public.pem') as f:
        key = f.read()
        rsakey = RSA.importKey(key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(message.encode(encoding="utf-8")))
        return cipher_text

def decrypt(message):
    with open('private.pem') as f:
        key = f.read()
        rsakey = RSA.importKey(key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        text = cipher.decrypt(base64.b64decode(message), "ERROR")
        return text

