#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import string
from scapy.all import rdpcap, ICMP, Raw

GREEN = "\033[92m"
RESET = "\033[0m"

# Palabras comunes en español para heurística
PALABRAS_ES = {
    "el","la","de","que","y","en","a","los","se","del","las","por","un","para","con",
    "no","una","su","al","lo","como","mas","más","pero","sus","le","ya","o","este",
    "si","sí","porque","esta","entre","cuando","muy","sin","sobre","tambien","también",
    "me","hasta","hay","donde","dónde","quien","quién","desde","todo","es","ser","fue","son"
}

def extraer_texto_desde_pcap(ruta_pcap: str) -> str:
    """
    Lee la captura y concatena el primer byte de DATA
    de cada paquete ICMP Echo Request (type=8) que tenga payload.
    """
    pkts = rdpcap(ruta_pcap)
    chars = []

    for p in pkts:
        if p.haslayer(ICMP) and p.haslayer(Raw):
            icmp_layer = p[ICMP]
            if icmp_layer.type == 8:  # Solo Echo Request
                data: bytes = p[Raw].load
                if data and len(data) >= 1:
                    b0 = data[0]
                    try:
                        c = chr(b0)
                    except ValueError:
                        c = '?'
                    chars.append(c)

    return "".join(chars)

def cesar_decode(texto: str, shift: int) -> str:
    """Corrimiento César sobre letras A-Z, a-z. Otros caracteres se mantienen."""
    res = []
    for ch in texto:
        if 'A' <= ch <= 'Z':
            res.append(chr((ord(ch) - ord('A') - shift) % 26 + ord('A')))
        elif 'a' <= ch <= 'z':
            res.append(chr((ord(ch) - ord('a') - shift) % 26 + ord('a')))
        else:
            res.append(ch)
    return "".join(res)

def puntuar_texto(t: str) -> float:
    """
    Heurística para estimar qué corrimiento es más probable:
      - % de letras y espacios
      - coincidencias con palabras frecuentes
    """
    if not t:
        return -1e9
    n = len(t)
    letras = sum(ch.isalpha() for ch in t)
    espacios = t.count(' ')
    score = (letras/n)*2 + (espacios/n)

    # Normalización y conteo de palabras frecuentes
    tabla_trad = str.maketrans({c: ' ' for c in string.punctuation + "¡!¿?«»“”…"})
    limpio = t.lower().translate(tabla_trad)
    tokens = [tok for tok in limpio.split() if tok]

    reemplazos = str.maketrans("áéíóúü", "aeiouu")
    tokens = [tok.translate(reemplazos) for tok in tokens]

    hits = sum(1 for tok in tokens if tok in PALABRAS_ES)
    score += hits * 3
    return score

def main():
    parser = argparse.ArgumentParser(description="Decodifica caracteres enviados en ICMP Echo Request usando corrimiento César.")
    parser.add_argument("pcap", help="Ruta del archivo .pcap/.pcapng")
    args = parser.parse_args()

    texto_cifrado = extraer_texto_desde_pcap(args.pcap)
    if not texto_cifrado:
        print("No se encontraron caracteres en paquetes ICMP Echo Request con DATA.")
        return

    candidatos = []
    for shift in range(26):
        dec = cesar_decode(texto_cifrado, shift)
        score = puntuar_texto(dec)
        candidatos.append((shift, dec, score))

    mejor_shift, mejor_texto, _ = max(candidatos, key=lambda x: x[2])

    for shift, dec, score in candidatos:
        linea = f"[shift={shift:02d}] {dec}"
        if shift == mejor_shift:
            print(f"{GREEN}{linea}{RESET}")
        else:
            print(linea)

    print("\n>>> Más probable:", f"shift={mejor_shift}", f"-> \"{mejor_texto}\"")

if __name__ == "__main__":
    main()
