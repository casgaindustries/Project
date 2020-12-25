# from cryptography.fernet import Fernet
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.Cipher import DES3
random_generator = Random.new().read
from Crypto.Cipher import PKCS1_OAEP

import base64
import json

print('That worked?')

key = RSA.generate(1024, random_generator)
public_key = key.publickey() 

bobj = key.publickey().exportKey(format='PEM', passphrase=None, pkcs=1)

d = {}

encoded = base64.b64encode(bobj)  # b'ZGF0YSB0byBiZSBlbmNvZGVk' (notice the "b")
d['bytes'] = encoded.decode('ascii')            # 'ZGF0YSB0byBiZSBlbmNvZGVk'
d['other data'] = "other data!!! ü"
# print(d)
djson = json.dumps(d).encode('utf-8')

dloaded = json.loads(djson)
print(dloaded)
decoded = base64.b64decode(dloaded['bytes'])  # b'data to be encoded'

print(decoded)

pubk2 = RSA.importKey(decoded, passphrase=None)

print(pubk2)

txt = b'yeeet boyyy'

cipher = PKCS1_OAEP.new(key=pubk2)
#Encrypting the message with the PKCS1_OAEP object
cipher_text = cipher.encrypt(txt)
print(cipher_text)
#Instantiating PKCS1_OAEP object with the private key for decryption
decrypt = PKCS1_OAEP.new(key=key)
#Decrypting the message with the PKCS1_OAEP object
decrypted_message = decrypt.decrypt(cipher_text)
print(decrypted_message)

