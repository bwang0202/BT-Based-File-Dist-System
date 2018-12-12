import model
from util import *

def _skt_send_msg(skt, msg):
    skt.send(MAGIC)
    skt.send(len(msg).to_bytes(LENLEN, ENDIAN))
    skt.send(msg)

def _skt_recv_msg(connection):
    msg = ""
    skt = connection.get_skt()
    magic = skt.recv(len(MAGIC))
    todo = 0
    if magic == MAGIC:
        todo = int.from_bytes(skt.recv(LENLEN), ENDIAN)
        msg = b""
        while todo > 0:
            start = epoch_microsec()
            readed = skt.recv(todo)
            end = epoch_microsec()
            connection.update_download_speed(len(readed), start, end)
            msg += readed
            todo -= len(readed)
    return msg

def skt_send(skt, message):
    """
    skt, socket
    message, Message object
    """
    _skt_send_msg(skt, message.to_barray())

def skt_recv(connection):
    """
    return a Message object
    """
    msg = _skt_recv_msg(connection)
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
            # Actually is msg[idx:], to save memory use a costant
            # since the purpose of this project is to distribute
            # content, thus receiving it in memory is good enough,
            # no need to actually write it to file system.
            py = 'PAYLOAD'
    if t == ANNOUNCE:
        ap_len = int.from_bytes(msg[idx:idx + 4], ENDIAN)
        idx = idx + 4
        ap = []
        for i in range(ap_len):
            ap.append(int.from_bytes(msg[idx:idx + 4], ENDIAN))
            idx = idx + 4
    if t == PEERID:
        p = int.from_bytes(msg[idx:idx + 4], ENDIAN)
    return model.Message(t, p, sp, py, ap)
