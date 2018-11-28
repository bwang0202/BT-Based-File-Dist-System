import enum

ENDIAN = 'big'

interest = 1
uninterest = 2
unchoke = 3
choke = 4
request = 5
annouce = 6
payload = 7
cancel = 8

class Message(object):
    msg_type = 0
    piece = -1
    subpiece = -1
    payload = None
    annouce_pieces = None
    def __init__(self, t, p=None, sp=None, py=None, ap=None):
        self.msg_type = t
        if p:
            self.piece = p
        if sp:
            self.subpiece = sp
        if py:
            # TODO: file-like obj or bytearray
            self.payload = py
        if ap:
            self.annouce_pieces = ap

    def to_barray(self):
        barray = bytearray()
        barray += self.msg_type.to_bytes(1, ENDIAN)
        if self.piece != -1:
            barray += self.piece.to_bytes(4, ENDIAN)
        if self.subpiece != -1:
            barray += self.subpiece.to_bytes(4, ENDIAN)
        if self.payload:
            # TODO: file-like obj or bytearray
            barray += self.payload
        if self.annouce_pieces:
            barray += len(self.annouce_pieces).to_bytes(4, ENDIAN)
            for x in self.annouce_pieces:
                barray += x.to_bytes(4, ENDIAN)
        return barray
