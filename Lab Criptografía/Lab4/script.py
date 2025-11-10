from Crypto.Random import get_random_bytes
from Crypto.Cipher import DES, AES, DES3
from Crypto.Util.Padding import pad

# Item 2
def adjust_key(key, length):
    key_bytes = key.encode('utf-8')
    current_length = len(key_bytes)
    
    print("Llave inicial: ", key_bytes.hex())
    if current_length < length:
        key_bytes += get_random_bytes(length - current_length)
    elif current_length > length:
        key_bytes = key_bytes[:length]
    print("Llave ajustada: ", key_bytes.hex())
    return key_bytes

# Item 3
def encrypt_DES(key, IV, text):
    text = text.encode('utf-8')
    if len(text) % 8 != 0:
        text = pad(text, 8)
    cipher = DES.new(key, DES.MODE_CBC, IV)
    msg = cipher.encrypt(text)
    print("Texto a cifrar con DES: ", text.hex())
    print("Texto cifrado con DES: ", msg.hex())
    return msg

def decrypt_DES(key, IV, ciphertext):
    cipher = DES.new(key, DES.MODE_CBC, IV)
    msg = cipher.decrypt(ciphertext)
    print("Texto descifrado con DES: ", msg.hex())
    return msg

def encrypt_3DES(key, IV, text):
    text = text.encode('utf-8')
    if len(text) % 8 != 0:
        text = pad(text, 8)
    cipher = DES3.new(key, DES3.MODE_CBC, IV)
    msg = cipher.encrypt(text)
    print("Texto a cifrar con 3DES: ", text.hex())
    print("Texto cifrado con 3DES: ", msg.hex())
    return msg

def decrypt_3DES(key, IV, ciphertext):
    cipher = DES3.new(key, DES3.MODE_CBC, IV)
    msg = cipher.decrypt(ciphertext)
    print("Texto descifrado con 3DES: ", msg.hex())
    return msg

def encrypt_AES(key, IV, text):
    text = text.encode('utf-8')
    if len(text) % 16 != 0:
        text = pad(text, 16)
    cipher = AES.new(key, AES.MODE_CBC, IV)
    msg = cipher.encrypt(text)
    print("Texto a cifrar con AES: ", text.hex())
    print("Texto cifrado con AES: ", msg.hex())
    return msg

def decrypt_AES(key, IV, ciphertext):
    cipher = AES.new(key, AES.MODE_CBC, IV)
    msg = cipher.decrypt(ciphertext)
    print("Texto descifrado con AES: ", msg.hex())
    return msg

# Ejecucion de todo
def main():
    # Item 1
    print("Ingrese llave de cifrado: ")
    key = input()
    print("Ingrese vector de inicialización: ")
    IV = input()
    print("Ingrese texto a cifrar: ")
    texto = input()
    print("Texto en hexadecimal: ", texto.encode('utf-8').hex())
    
    # Item 2
    print("<--- Ajuste de llaves DES ---->")
    key_DES = adjust_key(key, 8)
    print("<--- Ajuste de llaves AES ---->")
    key_AES = adjust_key(key, 32)
    print("<--- Ajuste de llaves 3DES ---->")
    key_3DES = adjust_key(key, 24)

    print("<--- Ajuste de vector de inicialización DES y 3DES ---->")
    IV_DES_3DES = adjust_key(IV, 8)
    print("<--- Ajuste de vector de inicialización AES ---->")
    IV_AES = adjust_key(IV, 16)
    
    print("<----- Cifrado de texto DES ----->")
    decrypted_DES = encrypt_DES(key_DES, IV_DES_3DES, texto)
    print("<----- Cifrado de texto 3DES ----->")
    decrypted_3DES = encrypt_3DES(key_3DES, IV_DES_3DES, texto)
    print("<----- Cifrado de texto AES ----->")
    decrypted_AES = encrypt_AES(key_AES, IV_AES, texto)
    
    print("<----- Descifrado de texto DES ----->")
    decrypt_DES(key_DES, IV_DES_3DES, decrypted_DES)
    print("<----- Descifrado de texto 3DES ----->")
    decrypt_3DES(key_3DES, IV_DES_3DES, decrypted_3DES)
    print("<----- Descifrado de texto AES ----->")
    decrypt_AES(key_AES, IV_AES, decrypted_AES)
    
main()