#Generar un programa, en python3 utilizando ChatGPT, que permita enviar los ca- racteres del string (el del paso 1) en varios paquetes ICMP request (un caracter por paquete en el campo data de ICMP). El comando para ejecutar el código no tiene que tener el código IP a utilizar, tiene que tener por defecto la IP 8.8.8.8.
#
#!/usr/bin/env python3
# pingv4.py
# Enviar un string como múltiples ICMP Echo Request (1 carácter por paquete).
# Requisitos: sudo apt install python3-scapy  (o)  sudo pip3 install scapy

#!/usr/bin/env python3
# pingv4.py
# Enviar un string como múltiples ICMP Echo Request (1 carácter por paquete, payload de 48 bytes).
# Requisitos: sudo apt install python3-scapy  (o)  sudo pip3 install scapy

import argparse
import sys
import time
import os
import struct
from scapy.all import IP, ICMP, Raw, send  # usa sr1 si quieres verificar respuestas

# --- Layout del payload (48 bytes = 0x30) ---
# [0x00:0x08) -> 8 bytes: timestamp fijo (double big-endian)
# [0x08:0x09) -> 1 byte: carácter que varía por paquete
# [0x09:0x10) -> 7 bytes: encabezado fijo 'INFOHDR' como relleno
# [0x10:0x30) -> 32 bytes: bloque constante (se mantiene entre paquetes)

PAYLOAD_LEN = 0x30  # 48 bytes
IDX_TS_START = 0x00
IDX_TS_END = 0x08
IDX_CHAR = 0x08
IDX_FILL_START = 0x09
IDX_FILL_END = 0x10
IDX_CONST2_START = 0x10
IDX_CONST2_END = 0x30  # exclusivo

FILL_BYTES = b"INFOHDR"  # 7 bytes para [0x09..0x0F]

def construir_payload_base() -> bytearray:
    """Construye el payload base de 48 bytes con timestamp fijo y bloques constantes."""
    if PAYLOAD_LEN != 48:
        raise ValueError("El payload debe ser exactamente de 48 bytes.")
    payload = bytearray(PAYLOAD_LEN)

    # Timestamp fijo (double big-endian)
    ts0 = time.time()
    payload[IDX_TS_START:IDX_TS_END] = struct.pack("!d", ts0)

    # Relleno fijo en [0x09:0x10)
    payload[IDX_FILL_START:IDX_FILL_END] = FILL_BYTES.ljust(IDX_FILL_END - IDX_FILL_START, b"\x00")

    # Bloque constante [0x10:0x30)
    const_block = os.urandom(IDX_CONST2_END - IDX_CONST2_START)
    payload[IDX_CONST2_START:IDX_CONST2_END] = const_block

    # El byte [0x08] (carácter variable) se setea por paquete
    payload[IDX_CHAR] = 0x00

    return payload

def enviar_icmp_por_caracter(destino: str, mensaje: str, intervalo: float, ttl: int,
                             id_base: int, seq_base: int):
    if not mensaje:
        print("Nada que enviar: el mensaje está vacío.")
        return

    base = construir_payload_base()

    for i, ch in enumerate(mensaje):
        # Convertir a un solo byte (si UTF-8 produce varios, se usa el primero)
        ch_b = ch.encode("utf-8", errors="replace")[:1] or b"\x00"

        payload = bytearray(base)
        payload[IDX_CHAR] = ch_b[0]  # solo cambia este byte

        icmp_pkt = ICMP(
            type=8, code=0,
            id=((id_base + i) & 0xFFFF),     # identificación coherente
            seq=((seq_base + i) & 0xFFFF)    # secuencia coherente
        )
        ip_pkt = IP(dst=destino, ttl=ttl)
        pkt = ip_pkt / icmp_pkt / Raw(load=bytes(payload))

        try:
            send(pkt, verbose=False)
            print(f"Enviado: char='{ch}' (0x{ch_b.hex()}) -> {destino}  id={icmp_pkt.id} seq={icmp_pkt.seq}")
        except PermissionError:
            print("Error: se requieren privilegios (sudo) o setcap cap_net_raw a python3.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error al enviar paquete para '{ch}': {e}", file=sys.stderr)

        if i < len(mensaje) - 1 and intervalo > 0:
            time.sleep(intervalo)

def main():
    parser = argparse.ArgumentParser(
        description="Envía un string como múltiples ICMP Echo Request (1 carácter por paquete, payload=48 bytes). "
                    "Mantiene timestamp [0x00:0x08) y bloque constante [0x10:0x30)."
    )
    parser.add_argument("mensaje", help="Texto a enviar (1 carácter por paquete ICMP)")
    parser.add_argument("-i", "--intervalo", type=float, default=0.1, help="Pausa entre paquetes en segundos (default: 0.1)")
    parser.add_argument("--ttl", type=int, default=64, help="TTL IP (default: 64)")
    parser.add_argument("--id-base", type=int, default=0x1234, help="ICMP id base (0-65535, default: 0x1234)")
    parser.add_argument("--seq-base", type=int, default=1, help="ICMP seq base (0-65535, default: 1)")
    parser.add_argument("--dest", default="8.8.8.8", help="(Opcional) IP/host destino. Por defecto 8.8.8.8")
    args = parser.parse_args()

    enviar_icmp_por_caracter(
        destino=args.dest,
        mensaje=args.mensaje,
        intervalo=args.intervalo,
        ttl=args.ttl,
        id_base=args.id_base,
        seq_base=args.seq_base
    )

if __name__ == "__main__":
    main()