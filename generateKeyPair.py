from Crypto import Random
from Crypto.PublicKey import RSA

random_generator = Random.new().read
rsa = RSA.generate(1024, random_generator)
private_pem = rsa.exportKey()
with open('private.pem','wb') as f:
    f.write(private_pem)
public_pem = rsa.publickey().exportKey()
with open('public.pem','wb') as f:
    f.write(public_pem)
