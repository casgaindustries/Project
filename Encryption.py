##Note that after encryption both cyphertext and key are cnverted to BASE64 format.
import rsa
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import generate
from Crypto.Cipher import PKCS1_OAEP
import base64


def generate_keys():
    # generates key with length keylength
    # Remember that RSA can only encrypt messages smaller than the key!
    key = generate(2048)
    public_key = key.publickey().exportKey("PEM")
    private_key = key.exportKey("PEM")

    return public_key, private_key


def encrypt_message(plain_text, pub_key):
    # Encrypts message to RSA cipher using the public key of the recipient
    # rsa.encrypt takes UTF-8 encoding only
    message = plain_text
    rsa_pubkey = RSA.importKey(pub_key)
    rsa_pubkey = PKCS1_OAEP.new(rsa_pubkey)
    cipher = rsa_pubkey.encrypt(message.encode())

    return cipher


def decrypt_message(cipher_text, priv_key):
    # Decrypts the cipher to the original message using the recipients private key
    rsa_privkey = RSA.importKey(priv_key)
    rsa_privkey = PKCS1_OAEP.new(rsa_privkey)
    decrypted = rsa_privkey.decrypt(cipher_text)
    return decrypted


def to_base64(obj):
    # Encodes object to base 64
    b64_key = base64.b64encode(obj, altchars=None)
    return b64_key


def from_base64(obj):
    # Encodes object to base64
    plain_key = base64.b64decode(obj, altchars=None)
    return plain_key