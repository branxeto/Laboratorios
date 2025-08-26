#Generar un programa, en python3 utilizando ChatGPT, que permita obtener el mensaje transmitido en el paso2. Como no se sabe cual es el corrimiento utilizado, genere todas las combinaciones posibles e impr ́ımalas, indicando en verde la opci ́on m ́as probable de ser el mensaje en claro. Como parametros en el comando de ejecución, se tiene que pasar el nombre del archivo que contiene la captura de tipo pcapng

import argparse
import sys
import string
from collections import defaultdict
from scapy.all import rdpcap, ICMP, Raw

# Layout del payload (enviado en el paso 2)
PAYLOAD_LEN = 48
IDX_TS_START = 0x00
IDX_TS_END   = 0x08
IDX_CHAR     = 0x08
IDX_CONST2_START = 0x10
IDX_CONST2_END   = 0x30  # exclusivo

GREEN = "\033[92m"
RESET = "\033[0m"

def es_payload_valido(raw_bytes: bytes) -> bool:
    return raw_bytes is not None and len(raw_bytes) >= PAYLOAD_LEN

def extraer_grupos_por_timestamp(packets):
    """
    Agrupa los paquetes por el timestamp fijo [0x00:0x08] del payload ICMP (Echo Request).
    Devuelve dict: ts_bytes -> lista de (seq, time, char_byte, const_block)
    """
    grupos = defaultdict(list)
    for pkt in packets:
        if not pkt.haslayer(ICMP):
            continue
        icmp = pkt[ICMP]
        # Solo Echo Request
        if icmp.type != 8 or not pkt.haslayer(Raw):
            continue

        raw = bytes(pkt[Raw].load)
        if not es_payload_valido(raw):
            continue

        ts = raw[IDX_TS_START:IDX_TS_END]
        ch = raw[IDX_CHAR:IDX_CHAR+1]
        const_block = raw[IDX_CONST2_START:IDX_CONST2_END]  # para validación opcional

        seq = getattr(icmp, "seq", 0)
        t   = getattr(pkt, "time", 0.0)

        grupos[ts].append((seq, t, ch, const_block))
    return grupos

def reconstruir_mensaje(grupo):
    """
    Ordena por (seq, time) y concatena el byte de carácter.
    """
    ordenado = sorted(grupo, key=lambda x: (x[0], x[1]))
    chars = [item[2] for item in ordenado]
    # Convertir bytes (1 por paquete) a string, reemplazando no imprimibles
    msg_bytes = b"".join(chars)
    # Los envíos eran bytes individuales por carácter; se asume ASCII/UTF-8 básico
    return msg_bytes.decode("utf-8", errors="replace")

def cesar(texto, shift):
    res = []
    for c in texto:
        if 'a' <= c <= 'z':
            res.append(chr((ord(c) - 97 - shift) % 26 + 97))
        elif 'A' <= c <= 'Z':
            res.append(chr((ord(c) - 65 - shift) % 26 + 65))
        else:
            res.append(c)
    return "".join(res)

def score_es(texto):
    """
    Heurística simple para español: suma ocurrencias de palabras comunes,
    favorece imprimibles y proporción de vocales.
    """
    lower = texto.lower()

    # Palabras muy frecuentes en español
    comunes = [" el ", " la ", " los ", " las ", " de ", " y ", " en ", " que ", " por ", " con ",
               " se ", " no ", " un ", " una ", " para ", " es ", " al ", " como ", " del "]

    score = 0
    for w in comunes:
        score += lower.count(w) * 5

    # Muchas letras y espacios imprimibles => mejor
    imprimibles = sum(ch in string.printable for ch in texto)
    score += imprimibles

    # Proporción de letras y de vocales
    letras = sum(ch.isalpha() for ch in texto)
    if len(texto) > 0:
        ratio_letras = letras / len(texto)
        score += int(ratio_letras * 50)

    vocales = sum(ch in "aeiouáéíóúü" for ch in lower)
    if letras > 0:
        ratio_vocales = vocales / max(1, letras)
        # Un poco de peso a que se parezca a español (~40-50% vocales)
        score += int((1.0 - abs(ratio_vocales - 0.45)) * 40)

    # Penaliza caracteres de control raros
    raros = sum(ord(ch) < 32 and ch not in "\n\r\t" for ch in texto)
    score -= raros * 10

    return score

def elegir_mejor_candidato(candidatos):
    """
    candidatos: lista de (shift, texto_descifrado)
    devuelve (best_shift, best_texto, scores_dict)
    """
    scores = {}
    for s, t in candidatos:
        scores[s] = score_es(t)
    best_shift = max(scores, key=scores.get)
    return best_shift, dict(scores)

def decodificar_desde_pcap(pcap_path):
    pkts = rdpcap(pcap_path)
    grupos = extraer_grupos_por_timestamp(pkts)

    if not grupos:
        raise RuntimeError("No se encontraron ICMP Echo Request con payload válido en el pcapng.")

    # Elige el grupo con más paquetes (asumiendo que es el mensaje más largo)
    ts_mejor, grupo_mejor = max(grupos.items(), key=lambda kv: len(kv[1]))
    mensaje_crudo = reconstruir_mensaje(grupo_mejor)

    # Genera todos los corrimientos 0..25
    candidatos = [(s, cesar(mensaje_crudo, s)) for s in range(26)]
    best_shift, scores = elegir_mejor_candidato(candidatos)

    return mensaje_crudo, candidatos, best_shift, scores

def main():
    parser = argparse.ArgumentParser(
        description="Descifra mensaje ICMP (1 byte por paquete, offset 0x08) desde un pcapng usando todas las claves César."
    )
    parser.add_argument("pcapng", help="Ruta al archivo .pcapng con la captura")
    args = parser.parse_args()

    try:
        mensaje_crudo, candidatos, best_shift, scores = decodificar_desde_pcap(args.pcapng)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nBytes reconstruidos (como texto directo):\n{mensaje_crudo}\n")
    print("Pruebas de corrimiento César (0..25):")
    for s, t in candidatos:
        line = f"{s:2d} {t}"
        if s == best_shift:
            print(f"{GREEN}{line}{RESET}")
        else:
            print(line)

    print(f"\nClave más probable: {GREEN}{best_shift}{RESET}")

if __name__ == "__main__":
    main()
