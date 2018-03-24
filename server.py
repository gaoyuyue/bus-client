import base64

import qrcode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5


def encrypt(message):
    with open('public.pem') as f:
        key = f.read()
        rsakey = RSA.importKey(key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(message.encode(encoding="utf-8")))
        return cipher_text

def generateQRCode(str):
    qr = qrcode.QRCode(version=7, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(str)
    qr.make(fit=True)
    img = qr.make_image()
    img.save("qr.png")

data = encrypt("2:2")
generateQRCode(data)