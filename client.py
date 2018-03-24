import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import pygame
import cv2
import zbar
from PIL import Image

def decrypt(message):
    with open('private.pem') as f:
        key = f.read()
        rsakey = RSA.importKey(key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        text = cipher.decrypt(base64.b64decode(message), "ERROR")
        return text

def playMP3(path):
    pygame.mixer.init()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()

def scanningQRCode(id,path):
    results = set()
    scanner = zbar.ImageScanner()
    scanner.parse_config('enable')
    font = cv2.FONT_HERSHEY_SIMPLEX
    camera = cv2.VideoCapture(0)

    last = ""
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
                if last == data :
                    continue
                else:
                    last = data
                result = data.split(":")
                if result[0] != id:
                    playMP3(path+"s"+result[0]+".mp3")
                else:
                    if result[1] in results:
                        playMP3(path+"e.mp3")
                    else:
                        results.add(result[1])
                        playMP3(path+"c"+result[1]+".mp3")
                # print 'decoded', symbol.type, 'symbol', '"%s"' % symbol.data
                print 'decoded', symbol.type, 'symbol', '"%s"' % data
                # cv2.putText(frame, symbol.data, (20, 100), font, 1, (0, 255, 0), 4)
                cv2.putText(frame, data, (20, 100), font, 1, (0, 255, 0), 4)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

scanningQRCode("1","/home/pi/audio/")