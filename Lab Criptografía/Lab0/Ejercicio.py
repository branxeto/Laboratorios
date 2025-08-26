abecedario_numerico = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h', 8:'i', 9:'j', 10:'k', 11:'l', 12:'m', 13:'n', 14:'o', 15:'p', 16:'q', 17:'r', 18:'s', 19:'t', 20:'u', 21:'v', 22:'w', 23:'x', 24:'y', 25:'z'}
abecedario = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7, 'i':8, 'j':9, 'k':10, 'l':11, 'm':12, 'n':13, 'o':14, 'p':15, 'q':16, 'r':17, 's':18, 't':19, 'u':20, 'v':21, 'w':22, 'x':23, 'y':24, 'z':25}

def cifrar_cesar(texto, desplazamiento):
    texto = texto.replace(' ', '')
    palabra = ''
    for char in texto:
        numero_char = abecedario[char] - desplazamiento
        if(numero_char < 0):
            numero_char = 26 + numero_char
        palabra += abecedario_numerico[numero_char]
    return palabra

def cifrar_vigenere(texto, clave):
    texto = texto.replace(' ', '')
    palabra = ''
    iter = 0
    for char in texto:
        if(iter >= len(clave)):
            iter = 0
        numero_char = (abecedario[char] + abecedario[clave[iter]]) % 26
        palabra += abecedario_numerico[numero_char]
        iter += 1
    return palabra

print('Ingrese el tipo de cifrado (1: Cifrado por César, 2: Cifrado por Vigenére)')

tipo_cifrado = int(input())
if (tipo_cifrado == 1):
    print('Ingrese el texto a cifrar:')
    texto = input()
    print('Ingrese el desplazamiento:')
    desplazamiento = int(input())
    texto_cifrado = cifrar_cesar(texto, desplazamiento)
    print('Texto cifrado:')
    print(texto_cifrado)
else:
    print('Ingrese el texto a cifrar:')
    texto = input()
    print('Ingrese la clave:')
    clave = input()
    texto_cifrado = cifrar_vigenere(texto, clave)
    print('Texto cifrado:')
    print(texto_cifrado)
