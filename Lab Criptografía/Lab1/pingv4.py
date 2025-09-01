#!/usr/bin/env python3
import os
import sys
import time
import random
import socket
import struct

# -------- Config --------
DEST_IP = "8.8.8.8"            # IP por defecto (no se pasa por argv)
DATA_LEN = 48                  # bytes de DATA en ICMP
SEND_INTERVAL_SEC = 0.2        # pausa entre paquetes
START_ID = random.randint(1, 0x7FFF)  # ID inicial (luego se incrementa)
START_SEQ = 1                  # Seq inicial (luego se incrementa)


# -------- Utilidades --------
def icmp_checksum(data: bytes) -> int:
    """Calcula el checksum de ICMP (RFC 1071)."""
    if len(data) % 2:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        w = data[i] << 8 | data[i+1]
        s = (s + w) & 0xffffffff

    # Fold a 16 bits
    while (s >> 16):
        s = (s & 0xFFFF) + (s >> 16)

    return (~s) & 0xFFFF


def build_icmp_packet(icmp_id: int, seq: int, payload: bytes) -> bytes:
    """Crea un paquete ICMP Echo Request (Type=8, Code=0) con DATA=payload."""
    icmp_type = 8  # Echo Request
    icmp_code = 0
    chksum = 0

    header = struct.pack('!BBHHH', icmp_type, icmp_code, chksum, icmp_id, seq)
    packet = header + payload

    chksum = icmp_checksum(packet)
    header = struct.pack('!BBHHH', icmp_type, icmp_code, chksum, icmp_id, seq)
    return header + payload


def make_payload_for_byte(b: int) -> bytes:
    """
    Construye DATA de 48 bytes.
    Primer byte = b (el 'carácter'), el resto se rellena con ceros.
    """
    if not (0 <= b <= 255):
        raise ValueError("Byte fuera de rango (0-255).")

    filler = b'\x00' * (DATA_LEN - 1)
    return bytes([b]) + filler


# -------- Main --------
def main():
    if len(sys.argv) < 2:
        print(f"Uso: {os.path.basename(sys.argv[0])} <string_a_enviar>")
        print("Ejemplo: sudo python3 readv2.py \"Hola\"")
        sys.exit(1)

    message = sys.argv[1]

    # Convertimos a bytes (UTF-8). Se enviará un byte por paquete.
    data_bytes = message.encode('utf-8')

    # Socket RAW para ICMP
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        print("Error: se requieren privilegios de administrador para sockets RAW (prueba con sudo).")
        sys.exit(1)

    icmp_id = START_ID
    seq = START_SEQ

    print(f"Destino: {DEST_IP}")
    print(f"Bytes a enviar (UTF-8): {len(data_bytes)} (uno por paquete, DATA={DATA_LEN} bytes)")
    print(f"ID inicial: {icmp_id}, Seq inicial: {seq}")
    print("Enviando...\n")

    sent = 0
    for b in data_bytes:
        payload = make_payload_for_byte(b)
        packet = build_icmp_packet(icmp_id, seq, payload)

        try:
            sock.sendto(packet, (DEST_IP, 0))
            print(f"Enviado: char_byte={b} (0x{b:02x}) id={icmp_id} seq={seq}")
        except Exception as e:
            print(f"Fallo al enviar id={icmp_id} seq={seq}: {e}")

        icmp_id += 1
        seq += 1
        sent += 1
        time.sleep(SEND_INTERVAL_SEC)

    sock.close()
    print(f"\nListo. Paquetes ICMP enviados: {sent}")


if __name__ == "__main__":
    main()
