from .model import *
import os

LENLEN = 4
MAGIC = b"BITTORRENT"

def _skt_send_msg(skt, msg):
    os.write(skt, MAGIC)
    os.write(skt, len(msg).to_bytes(LENLEN, ENDIAN))
    os.write(skt, msg)

def _skt_recv_msg(skt):
    msg = ""
    magic = os.read(skt, len(MAGIC))
    todo = 0
    if magic == MAGIC:
        todo = int.from_bytes(os.read(skt, LENLEN), ENDIAN)
        msg = b""
        while todo > 0:
            readed = os.read(skt, todo)
            msg += readed
            todo -= len(readed)
    return msg

def skt_send(skt, message):
    """
    skt, socket
    message, Message object
    """
    _skt_send_msg(skt, message.to_barray())

def skt_recv(skt):
    """
    return a Message object
    """
    msg = _skt_recv_msg(skt)
    t = msg[0]
    p = None
    sp = None
    py = None
    ap = None
    idx = 1
    if t == REQUEST or t == CANCEL or t == PAYLOAD:
        p = int.from_bytes(msg[idx:idx + 4], ENDIAN)
        sp = int.from_bytes(msg[idx + 4:idx + 8], ENDIAN)
        idx = idx + 8
        if t == PAYLOAD:
            py = msg[idx:]
    if t == ANNOUNCE:
        ap_len = int.from_bytes(msg[idx:idx + 4], ENDIAN)
        idx = idx + 4
        ap = []
        for i in range(ap_len):
            ap.append(int.from_bytes(msg[idx:idx + 4], ENDIAN))
            idx = idx + 4
    return Message(t, p, sp, py, ap)
