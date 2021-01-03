from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.Cipher import DES3
random_generator = Random.new().read
from Crypto.Cipher import PKCS1_OAEP

import base64
import json

#___________________________________________________________________________
#________Encryption object intantiated for every client or bank. 
#___________________________________________________________________________
class MyEncrypt:

    # Inits the object, generates your priv/ pub key
    def __init__(self):
        self.key = RSA.generate(1024, random_generator)
        self.pubkey = self.key.publickey()

    # Get your own pubkey in base64 format (can be sent over json easily)
    def getPubKeyB64(self):
        b64pubk = self.pubkey.exportKey(format='PEM', passphrase=None, pkcs=1)
        bytepubk = base64.b64encode(b64pubk)  
        asciipubk = bytepubk.decode('ascii')
        return asciipubk
    
    # Turn a base64 pubkey to a pubkey object
    def getKeyObjFromB64(self,b64key):
        decoded = base64.b64decode(b64key)  
        pubkobj = RSA.importKey(decoded, passphrase=None)
        return pubkobj

    # Encrypts a given string using a base64 pubkey given
    def encryptStringToB64(self, string, b64pubk):
        byteText = string.encode('utf-8')
        pubkObj = self.getKeyObjFromB64(b64pubk)
        cipher = PKCS1_OAEP.new(key=pubkObj)
        cipher_text = cipher.encrypt(byteText)
        print('Cipher text: (bytes)')
        print(cipher_text)
        encoded = base64.b64encode(cipher_text)  
        b64encrypted = encoded.decode('ascii') 
        return b64encrypted
    
    # Decrypts base64 text to string using your own private key
    def decryptB64(self,b64ciphertxt):
        ciphertxtbytes = base64.b64decode(b64ciphertxt)
        return self.decryptBytes(ciphertxtbytes).decode('utf-8')

    # Helper method used to decrypt
    def decryptBytes(self,myBytes):
        decrypt = PKCS1_OAEP.new(key=self.key)
        decrypted_message = decrypt.decrypt(myBytes)
        return decrypted_message


def tester():
    enc = MyEncrypt()
    pubk64 = enc.getPubKeyB64()
    encyptedB64 = enc.encryptStringToB64( 'CAN YOüuuuuü',pubk64)
    decryptedBytes = enc.decryptB64(encyptedB64)
    print(decryptedBytes)
    print(type(decryptedBytes))

# tester()