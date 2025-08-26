# Creame un código en Python3 que permita cifrar texto utilizando cifrado Cesar. Ademas se tiene que ingresar como el texto a cifrar y el número de corrimientos. necesito que, al ingresar en consola directamente: "sudo python3 cesar.py "criptografia y seguridad en redes" 9" el codigo al ejecutarse sea capaz de directamente de ahi reconocer el texto que se busca cifrar y y el 9 como la cantidad de corrimiento, sin necesidad de pedirlo al usuario nuevamente
import sys

def cifrado_cesar(texto, corrimiento):
    resultado = ""
    for caracter in texto:
        if caracter.isupper():
            resultado += chr((ord(caracter) - 65 + corrimiento) % 26 + 65)
        elif caracter.islower():
            resultado += chr((ord(caracter) - 97 + corrimiento) % 26 + 97)
        else:
            resultado += caracter
    return resultado


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 cesar.py \"<texto>\" <corrimiento>")
        sys.exit(1)

    # El primer argumento después del nombre del script es el texto
    texto = sys.argv[1]
    # El segundo argumento es el corrimiento
    corrimiento = int(sys.argv[2])

    texto_cifrado = cifrado_cesar(texto, corrimiento)
    print(texto_cifrado)
