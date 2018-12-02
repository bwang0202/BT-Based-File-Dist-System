import enum
import threading

ENDIAN = 'big'

INTEREST = 1
UNINTEREST = 2
UNCHOKE = 3
CHOKE = 4
REQUEST = 5
ANNOUNCE = 6
PAYLOAD = 7
CANCEL = 8

class Message(object):
    """
    Represents a Message to send
    """
    msg_type = 0
    piece = -1
    subpiece = -1
    payload = None
    announce_pieces = None
    def __init__(self, t, p=None, sp=None, py=None, ap=None):
        self.msg_type = t
        if p is not None:
            self.piece = p
        if sp is not None:
            self.subpiece = sp
        if py is not None:
            # TODO: file-like obj or bytearray
            self.payload = py
        if ap is not None:
            self.announce_pieces = ap

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
        if self.announce_pieces:
            barray += len(self.announce_pieces).to_bytes(4, ENDIAN)
            for x in self.announce_pieces:
                barray += x.to_bytes(4, ENDIAN)
        return barray

    def apply_to_conn_control(self, conn, control):
        # self, the msg received
        if self.msg_type == INTEREST:
            conn.interested = True
        elif self.msg_type == UNINTEREST:
            self.interested = False
        elif self.msg_type == CHOKE:
            self.choked = True
        elif self.msg_type == UNCHOKE:
            self.choked = False
        elif self.msg_type == REQUEST:
            if self.interested:
                conn.requesting(self.piece, self.subpiece)
        elif self.msg_type == ANNOUNCE:
            for x in self.announce_pieces:
                control.peer_has_piece(conn.ip, conn.port, x)
        elif self.msg_type == PAYLOAD:
            # TODO: write to file etc.

            piece = control.get_piece(self.piece)
            subpiece = piece.thread_safe_next_subpiece()
            if subpiece:
                conn.send_request(self, self.piece, subpiece)
        else:
            # not implemented
            pass

class Connection(object):
    """
    Represents a Connection to a peer
    """
    def __init__(self, skt, ip, port):
        self.skt = skt
        self.ip = ip
        self.port = port
        self.choked = True
        self.interested = False
        self.choking = True
        self.to_send = []
        self.lock = threading.Lock()

    def requesting(self, piece, subpiece):
        self.to_serve.append((piece, subpiece))

    def announce_pieces(self, pieces):
        with self.lock:
            self.to_send.append(Message(ANNOUNCE, ap=pieces))

    def send_type_only(self, t):
        with self.lock:
            self.to_send.append(Message(t))

    def send_unchoke(self):
        with self.lock:
            self.to_send.insert(0, Message(UNCHOKE))

    def send_request(self, piece, subpiece):
        with self.lock:
            self.to_send.append(Message(REQUEST, p=piece, sp=subpiece))

    def send_payload(self, piece, subpiece, payload):
        with self.lock:
            self.to_send.append(Message(PAYLOAD, p=piece,
                sp=subpiece, payload=payload))

    def serve_one(self):
        with self.lock:
            if self.to_send:
                msg = self.to_send.pop(0)
                if msg.msg_type == REQUEST and self.choked:
                    return msg
                if msg.msg_type == PAYLOAD and self.choking:
                    return msg
                message.skt_send(self.skt, msg)
            return None

class Piece(object):
    def __init__(self, piece_number, total_subpieces=20):
        self.piece_number = piece_number
        self.total_subpieces = total_subpieces
        self.next_subpiece = 0
        self.lock = threading.Lock()

    def thread_safe_next_subpiece(self):
        with self.lock:
            if self.next_subpiece == total_subpieces:
                return None
            self.next_subpiece += 1
            return self.next_subpiece - 1
