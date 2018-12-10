# Python 3.7
import socket, time, threading, sys, threading, json, requests
from _thread import *

from util import *
import model, view, message, strategy

class Control(object):
    def __init__(self, file_id, peer_id, finished_pieces=[]):
        self.connections = {}
        self.file_id = file_id
        self.peer_id = peer_id
        self.next_piece_cv = threading.Condition()
        # Keep track of pieces/subpieces progress
        self.peer_pieces = {}
        self.piece_to_peers = {}
        self.finished_pieces = finished_pieces
        self.finished_subpieces = {}
        self.ongoing_pieces = []
        self.ongoing_pieces_request_subpieces = {}
        self.ongoing_peer_subpieces = {}

    def add_peer(self, ip, port, conn):
        # Create the socket connection, store in Connection object
        new_conn = model.Connection(conn, ip, port)
        self.connections[(ip, port)] = new_conn
        new_conn.announce_pieces(self.finished_pieces)

    def _available_peer_for_piece(self, piece):
        # find a peer for np
        requested_subpiece = self.ongoing_pieces_request_subpieces.get(piece, -1)
        for (ip, port) in self.piece_to_peers.get(piece):
            op_subpieces = self.ongoing_peer_subpieces.get((ip, port), [])
            if len(op_subpieces) < PIPELINED_REQUEST:
                requested_subpiece += 1
                # ongoing_pieces_request_subpieces
                self.ongoing_pieces_request_subpieces[piece] = requested_subpiece
                # ongoing_peer_subpieces
                op_subpieces.append((piece, requested_subpiece))
                self.ongoing_peer_subpieces[(ip, port)] = op_subpieces
                # ongoing_pieces
                if piece not in self.ongoing_pieces:
                    self.ongoing_pieces.append(piece)
                return (ip, port, piece, requested_subpiece)
        return None

    def _next_subpiece(self):
        # Return None if nothing to request next
        # On going piece first
        for piece in self.ongoing_pieces:
            # All subpieces has been requested
            requested_subpiece = self.ongoing_pieces_request_subpieces.get(piece, -1)
            if requested_subpiece == DEBUG_PIECE_SUBPIECES:
                continue
            nsp = self._available_peer_for_piece(piece)
            if nsp:
                return nsp

        # None of peers has room for on going pieces
        if len(self.ongoing_pieces) == CONCURRENT_PIECES:
            return None

        # Next piece
        np = strategy.choose_next_piece(self.finished_pieces, self.piece_to_peers,
                self.ongoing_pieces)
        if np is None:
            # Has no next piece
            return None
        return self._available_peer_for_piece(np)

    def next_subpiece(self):
        # return (ip, port, piece, subpiece)
        with self.next_piece_cv:
            # Block until next piece can be requested
            while True:
                nsp = self._next_subpiece()
                if not nsp:
                    self.next_piece_cv.wait()
                else:
                    break
            return nsp

    def add_to_finished_subpiece(self, ip, port, piece, subpiece, payload):
        need_annouce = False
        with self.next_piece_cv:
            self.ongoing_peer_subpieces[(ip, port)].remove((piece, subpiece))
            if piece not in self.finished_pieces:
                append_dict_dict(self.finished_subpieces, piece, subpiece, payload)
                if len(self.finished_subpieces[piece]) == DEBUG_PIECE_SUBPIECES:
                    self.finished_pieces.append(piece)
                    # TODO: Construct the piece
                    self.finished_subpieces.pop(piece)
                    self.ongoing_pieces.remove(piece)
                    self.ongoing_pieces_request_subpieces.pop(piece)
                    need_annouce = True
                    print_green("Received piece [%d]" % piece)
            self.next_piece_cv.notify()
        if need_annouce:
            for x in self.connections.values():
                x.announce_pieces([piece])

    def get_peer(self, ip, port):
        # TODO: check connections dead or not also
        return self.connections[(ip, port)]

    def peer_has_piece(self, ip, port, piece):
        with self.next_piece_cv:
            # Add to peer pieces
            append_dict_list(self.peer_pieces, (ip, port), piece)
            # Add to piece peers
            append_dict_list(self.piece_to_peers, piece, (ip, port))
            self.next_piece_cv.notify()

    def peers_to_unchoke(self):
        return strategy.peers_to_unchoke(self.connections.values())

def _get_conn_from_control(control, ip, port):
    return control.get_peer(ip, port)

def connection_read_thread(control, ip, port):
    # Connection object
    conn = _get_conn_from_control(control, ip, port)
    while True:
        # Block until some message arrives
        msg = message.skt_recv(conn.skt)
        msg.apply_to_conn_control(conn, control)

def connection_write_thread(control, ip, port):
    conn = _get_conn_from_control(control, ip, port)
    while True:
        # Block until there is something to send
        conn.serve_one()

def download_control_thread(control):
    counter = 0
    while True:
        counter += 1
        # Block until can request next subpiece
        (ip, port, piece, subpiece) = control.next_subpiece()
        conn = _get_conn_from_control(control, ip, port)
        conn.send_type_only(INTEREST)
        conn.send_request(piece, subpiece)
        # TODO FIXME: not really needed when next_subpiece actually blocks
        # because currently subpiece size is too small
        if counter == 3:
            time.sleep(1)
            counter = 0

def upload_control_thread(control):
    while True:
        # peers_to_unchoke
        conns_to_unchoke = control.peers_to_unchoke()
        # Serve that peer
        for x in conns_to_unchoke:
            x.send_unchoke()
        time.sleep(10)

def search_for_peers(control, url, infohash, p_port, host):
    known_peers = set()
    while True:
        time.sleep(5)
        resp = requests.get("http://%s/info_hash=%s&port=%d" % (url, infohash, p_port))
        peers = json.loads(resp.text)["peers"]
        for peer in peers:
            ip = peer[0]
            port = peer[1]
            if str(ip) == str(host) and p_port == port:
                continue
            if (ip, port) in known_peers:
                continue
            print("Adding peers %s:%s" % (str(ip), str(port)))
            known_peers.add((ip, port))
            skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skt.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            port = int(port)
            skt.connect((ip, port))
            control.add_peer(ip, port, skt)
            start_new_thread(connection_read_thread, (control, ip, port))
            start_new_thread(connection_write_thread, (control, ip, port))

def main():
    finished_pieces = []
    IP = "127.0.0.1"
    PORT = int(sys.argv[1])
    tracker_url = sys.argv[2]
    info_hash = sys.argv[3]
    for x in sys.argv[4:]:
        finished_pieces.append(int(x))
    print_green("Got pieces: %s" % str(finished_pieces))
    peer_id = "%s:%d" % (IP, PORT)
    control = Control(info_hash, peer_id, finished_pieces)
    start_new_thread(search_for_peers, (control, tracker_url, info_hash, PORT, IP))
    start_new_thread(upload_control_thread, (control, ))
    start_new_thread(download_control_thread, (control, ))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((IP, PORT))
        s.listen(5)
        # a forever loop until client wants to exit 
        while True: 
            # establish connection with client
            c, (ip, port) = s.accept()
            control.add_peer(ip, port, c)
            start_new_thread(connection_read_thread, (control, ip, port))
            start_new_thread(connection_write_thread, (control, ip, port))

if __name__ == '__main__': main()