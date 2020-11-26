##Note that after encryption both cyphertext and key are cnverted to BASE64 format.
import rsa


def generate_keys(keylength):
    # generates key with length keylength
    # Remember that RSA can only encrypt messages smaller than the key!
    (pubkey, privkey) = rsa.newkeys(keylength)
    return pubkey, privkey


def encrypt_message(plain_text, pubkey):
    # Encrypts message to RSA cipher using the public key of the recipient
    # rsa.encrypt takes UTF-8 encoding only
    plain_text = plain_text.encode('utf8')
    cipher = rsa.encrypt(plain_text, pubkey)
    return cipher


def decrypt_message(cipher_text, privkey):
    # Decrypts the cipher to the original message using the recipients private key
    plain_message = rsa.decrypt(cipher_text, privkey)
    return plain_message.decode('utf8')


# NOTE Demo: Key length 1024 results in 117 bytes of space. More needed for more robust messaging,
# but key generation will take longer.
publicKey, privateKey = generate_keys(1024)
message = 'This is a sentence showing the limit of what we can do with a key of length 1024. A max of 117 bytes looks like this.'

cipher = encrypt_message(message, publicKey)
print('Cipher: ', cipher)

decodedMessage = decrypt_message(cipher, privateKey)
print('Plaintext:', decodedMessage)
