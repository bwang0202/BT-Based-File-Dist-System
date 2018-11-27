import enums
import os
import struct

LENLEN = 4
ENDIAN = 'big'
MAGIC = b"BITTORRENT"

def _skt_send_msg(skt, msg):
    os.write(skt, MAGIC)
    os.write(skt, len(msg).to_bytes(LENLEN, byteorder=ENDIAN))
    os.write(skt, msg)
    return

def _skt_recv_msg(skt):
    msg = ""
    magic = os.read(skt, len(MAGIC))
    todo = 0
    if magic == MAGIC:
        todo = int.from_bytes(os.read(skt, LENLEN), byteorder=ENDIAN)
        msg = b""
        while todo > 0:
            readed = os.read(skt, todo)
            msg += readed
            todo -= len(readed)

    return msg