from Crypto.Random import get_random_bytes

# Item 1
print("Ingrese llave de cifrado: ")
llave = input()
print("Ingrese vector de inicialización: ")
IV = input()
print("Ingrese texto a cifrar: ")
texto = input()

# Item 2
def adjust_key(key, length):
    key_bytes = key.encode('utf-8')
    current_length = len(key_bytes)
    
    print("Llave inicial: ", key_bytes)
    if current_length < length:
        key_bytes += get_random_bytes(length - current_length)
    elif current_length > length:
        key_bytes = key_bytes[:length]
    print("Llave ajustada: ", key_bytes)
    return key_bytes

# Item 3
