import enum
from util import *
import message, view, controller

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

    def __str__(self):
        return "%d" % (self.msg_type)

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
            print_yellow("Received INTEREST from %d" % conn.peer_id)
            conn.set_interested(True)
        elif self.msg_type == UNINTEREST:
            print_yellow("Received UNINTEREST from %d" % conn.peer_id)
            conn.set_interested(False)
        elif self.msg_type == CHOKE:
            print_yellow("Received CHOKE from %d" % conn.peer_id)
            conn.set_choked(True)
        elif self.msg_type == UNCHOKE:
            print_yellow("Received UNCHOKE from %d" % conn.peer_id)
            conn.set_choked(False)
        elif self.msg_type == REQUEST:
            if conn.get_interested():
                print_blue("About to send payload [%d:%d]" % (self.piece, self.subpiece))
                conn.send_payload(self.piece, self.subpiece, DEBUG_SUBPIECE_PAYLOAD)
            else:
                pass
                #print("[apply_to_conn_control] conn not interested yet")
        elif self.msg_type == ANNOUNCE:
            for x in self.announce_pieces:
                control.peer_has_piece(conn.ip, conn.port, x)
        elif self.msg_type == PAYLOAD:
            # TODO: write to file etc.
            print_blue("Received payload [%d:%d]" % (self.piece, self.subpiece))
            control.add_to_finished_subpiece(conn.ip, conn.port,
                self.piece, self.subpiece, self.payload)
        elif self.msg_type == PEERID:
            conn.set_peer_id(self.piece)
        else:
            # not implemented
            pass

class Connection(object):
    """
    Represents a Connection to a peer
    """
    def __init__(self, skt, ip, port, peer_id=0):
        self.skt = skt
        self.ip = ip
        self.port = port
        self.peer_id = peer_id
        self.choked = True
        self.choking = True
        self.interested = False
        self.interesting = False
        self.payloads_to_send = []
        self.requests_to_send = []
        self.controls_to_send = []
        self.lock = threading.Lock()
        self.send_cv = threading.Condition(self.lock)

    def set_peer_id(self, peer_id):
        self.peer_id = peer_id

    def get_interested(self):
        with self.lock:
            return self.interested

    def set_interested(self, interested):
        with self.lock:
            self.interested = interested

    def set_choked(self, choked):
        with self.send_cv:
            old_choked = self.choked
            self.choked = choked
            if old_choked and not self.choked \
                    and len(self.requests_to_send):
                self.send_cv.notify()

    def set_choking(self, choking):
        with self.send_cv:
            old_choking = self.old_choking
            self.choking = choking
            if old_choking and not self.choking \
                    and len(self.payloads_to_send):
                self.send_cv.notify()

    def announce_pieces(self, pieces):
        with self.send_cv:
            self.controls_to_send.append(Message(ANNOUNCE, ap=pieces))
            if len(self.controls_to_send) == 1:
                self.send_cv.notify()

    def send_peer_id(self, peer_id):
        with self.send_cv:
            self.controls_to_send.append(Message(PEERID, p=peer_id))
            if len(self.controls_to_send) == 1:
                self.send_cv.notify()

    def send_type_only(self, t):
        with self.send_cv:
            self.controls_to_send.append(Message(t))
            if len(self.controls_to_send) == 1:
                self.send_cv.notify()

    def send_unchoke(self):
        with self.send_cv:
            self.controls_to_send.insert(0, Message(UNCHOKE))
            if len(self.controls_to_send) == 1:
                self.send_cv.notify()

    def send_request(self, piece, subpiece):
        with self.send_cv:
            self.requests_to_send.append(
                Message(REQUEST, p=piece, sp=subpiece))
            if not self.choked and len(self.requests_to_send) == 1:
                self.send_cv.notify()

    def send_payload(self, piece, subpiece, payload):
        with self.send_cv:
            self.payloads_to_send.append(Message(PAYLOAD, p=piece,
                sp=subpiece, py=payload))
            if not self.choking and len(self.payloads_to_send) == 1:
                self.send_cv.notify()

    def _nothing_to_send(self):
        if len(self.controls_to_send):
            #print("controls_to_send %d" % len(self.controls_to_send))
            return False
        if not self.choked and len(self.requests_to_send):
            #print("requests_to_send %d" % len(self.requests_to_send))
            return False
        if not self.choking and len(self.payloads_to_send):
            #print("payloads_to_send %d" % len(self.payloads_to_send))
            return False
        return True

    def _msg_to_send(self):
        #print("[_msg_to_send] %d %d %d" % (len(self.controls_to_send),
        #    len(self.requests_to_send), len(self.payloads_to_send)))
        if len(self.controls_to_send):
            return self.controls_to_send.pop(0)
        if not self.choked and len(self.requests_to_send):
            return self.requests_to_send.pop(0)
        if not self.choking and len(self.payloads_to_send):
            return self.payloads_to_send.pop(0)
        return None

    def serve_one(self):
        with self.send_cv:
            while self._nothing_to_send():
                self.send_cv.wait()

            msg = self._msg_to_send()
                
            if msg.msg_type == CHOKE:
                if self.choking:
                    return
                self.choking = True
            elif msg.msg_type == UNCHOKE:
                if not self.choking:
                    return
                self.choking = False
            elif msg.msg_type == INTEREST:
                if self.interesting:
                    return
                self.interesting = True
            elif msg.msg_type == UNINTEREST:
                if not self.interesting:
                    return
                self.interesting = False

            message.skt_send(self.skt, msg)

            if msg.msg_type == REQUEST:
                print_red("Sent request for [%d:%d]" % (msg.piece, msg.subpiece))
            elif msg.msg_type == PAYLOAD:
                print_red("Sent payload [%d:%d]" % (msg.piece, msg.subpiece))

