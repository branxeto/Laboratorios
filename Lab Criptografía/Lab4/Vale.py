from Crypto.Cipher import DES, DES3, AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

def ajustar_clave(clave, size):
    clave = clave.encode('utf-8')
    if len(clave) < size:
        clave += get_random_bytes(size - len(clave))
    elif len(clave) > size:
        clave = clave[:size]
    return clave

def cifradoDES(clave, vector, texto):
    clave = ajustar_clave(clave, 8)
    print(clave.hex())
    iv = ajustar_clave(vector, 8)
    print(iv.hex())
    cipher = DES.new(clave, DES.MODE_CBC, iv)
    texto_bytes = texto.encode('utf-8')
    cifrado = cipher.encrypt(pad(texto_bytes, DES.block_size))
    print(cifrado.hex())
    return cifrado

def cifradoDES3(clave, vector, texto):
    clave = ajustar_clave(clave, 24)
    iv = ajustar_clave(vector, 8)
    cipher = DES3.new(clave, DES3.MODE_CBC, iv)
    texto_bytes = texto.encode('utf-8')
    cifrado = cipher.encrypt(pad(texto_bytes, DES3.block_size))
    print(cifrado.hex())
    return cifrado

def cifradoAES(clave, vector, texto):
    clave = ajustar_clave(clave, 32)
    iv = ajustar_clave(vector, 16)
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    texto_bytes = texto.encode('utf-8')
    cifrado = cipher.encrypt(pad(texto_bytes, AES.block_size))
    print(cifrado.hex())
    return cifrado

def descifradoDES(clave, vector, texto):
    clave = ajustar_clave(clave, 8)
    iv = ajustar_clave(vector, 8)
    cipher = DES.new(clave, DES.MODE_CBC, iv)
    texto_bytes = bytes.fromhex(texto)
    descifrado = unpad(cipher.decrypt(texto_bytes), DES.block_size)
    print(descifrado.decode('utf-8'))

def descifradoDES3(clave, vector, texto):
    clave = ajustar_clave(clave, 24)
    iv = ajustar_clave(vector, 8)
    cipher = DES3.new(clave, DES3.MODE_CBC, iv)
    texto_bytes = bytes.fromhex(texto)
    descifrado = unpad(cipher.decrypt(texto_bytes), DES3.block_size)
    print(descifrado.decode('utf-8'))

def descifradoAES(clave, vector, texto):
    clave = ajustar_clave(clave, 32)
    iv = ajustar_clave(vector, 16)
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    texto_bytes = bytes.fromhex(texto)
    descifrado = unpad(cipher.decrypt(texto_bytes), AES.block_size)
    print(descifrado.decode('utf-8'))

def main():

    clave = input("Ingrese la clave: ")
    vector = input("Ingrese el Vector de Inicialización: ")
    texto = input("Ingrese el texto a cifrar o descifrar: ")

    print("\n¿Qué desea realizar?\n")
    print("1. Proceso de cifrado.")
    print("2. Proceso de descifrado.")
    opcion = input("Seleccione una opción: ")

    if opcion == "1":
        print("\n¿Qué algoritmo de cifrado desea utilizar?\n")
        print("1. Cifrado DES.")
        print("2. Cifrado DES3.")
        print("3. Cifrado AES.")
        algoritmo = input("Seleccione una opción: ")

        if algoritmo == "1":
            cifradoDES(clave, vector, texto)

        elif algoritmo == "2":
            cifradoDES3(clave, vector, texto)

        elif algoritmo == "3":
            cifradoAES(clave, vector, texto)

        else:
            print("Opción no válida.")

    elif opcion == "2":
        print("\n¿Qué algoritmo de descifrado desea utilizar?\n")
        print("1. Descifrado DES.")
        print("2. Descifrado DES3.")
        print("3. Descifrado AES.")
        algoritmo = input("Seleccione una opción: ")

        if algoritmo == "1":
            descifradoDES(clave, vector, texto)

        elif algoritmo == "2":
            descifradoDES3(clave, vector, texto)

        elif algoritmo == "3":
            descifradoAES(clave, vector, texto)

        else:
            print("Opción no válida.")

    else:
        print("Opción no válida.")

if __name__ == "__main__":
    main()