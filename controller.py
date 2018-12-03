import socket, time, threading, sys
from _thread import *

from .util import *
import model, view, message, strategy


class Control(object):
    def __init__(self, file_id, total_pieces, finished_pieces={}):
        self.connections = {}
        self.file_id = file_id
        self.total_pieces = total_pieces
        self.peer_to_pieces = {}
        self.piece_to_peers = {}
        # TODO: now storing payload as values for simplicity
        self.finished_pieces = finished_pieces
        self.downloading_pieces = {}
        self.piece_objects = {}
        view.start_progress_plot(file_id, total_pieces)

    def add_peer(self, ip, port, conn):
        # Create the socket connection
        # Store in Connection object
        # skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sck.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # skt.connect((ip, port))
        new_conn = model.Connection(conn, ip, port)
        self.connections[(ip, port)] = new_conn
        self._new_peer_steps(new_conn)

    def add_to_finished_subpiece(self, piece, subpiece, payload):
        subpieces = self.downloading_pieces.get(piece, {})
        subpieces[subpiece] = payload
        self.downloading_pieces[piece] = subpieces

    def _new_peer_steps(self, conn):
        conn.announce_pieces(list(self.finished_pieces.keys()))

    def get_peer(self, ip, port):
        # TODO: check connections dead or not also
        # Return Connection object or None
        return self.connections[(ip, port)]

    def get_piece(self, piece):
        return self.piece_objects[piece]

    def peers_for_piece(self, piece):
        return self.piece_to_peers[piece]

    def peer_has_piece(self, ip, port, piece):
        self.peer_to_pieces[(ip, port)] = self.peer_to_pieces.get(
            (ip, port), []).append(piece)
        self.piece_to_peers[piece] = self.piece_to_peers.get(
            piece, []).append((ip, port))
        if not self.piece_objects.get(piece):
            self.piece_objects[piece] = model.Piece(piece, DEBUG_PIECE_SUBPIECES)

    def next_piece(self):
        return strategy.choose_next_piece(self.total_pieces,
            self.finished_pieces, self.peer_to_pieces,
            self.piece_to_peers)

    def peers_to_unchoke(self):
        return strategy.peers_to_unchoke(self.connections.values())

def _get_conn_from_control(control, ip, port):
    return control.get_peer(ip, port)

def connection_read_thread(control, ip, port):
    # Connection object
    conn = _get_conn_from_control(control, ip, port)
    while True:
        # Should block until some message arrives
        msg = message.skt_recv(conn.skt)
        msg.apply_to_conn_control(conn, control)

def connection_write_thread(control, ip, port):
    conn = _get_conn_from_control(control, ip, port)
    while True:
        # TODO: use condition variable
        msg = conn.serve_one()
        if msg:
            conn.to_send.append(msg)

def download_control_thread(control):
    while True:
        # choose_next_piece
        next_piece = control.next_piece()
        if not next_piece:
            # nothing to download
            time.sleep(10)
            continue
        # peers_for_piece
        peers_ip_ports = control.peers_for_piece(next_piece)
        piece = control.get_piece(next_piece)
        # Download from that peer
        for (ip, port) in peers_ip_ports:
            conn = _get_conn_from_control(control, ip, port)
            conn.send_type_only(model.INTEREST)
            subpiece = piece.thread_safe_next_subpiece()
            if subpiece == None:
                continue
            conn.send_request(next_piece, subpiece)

def upload_control_thread(control):
    while True:
        time.sleep(10)
        # peers_to_unchoke
        conns_to_unchoke = control.peers_to_unchoke()
        # Serve that peer
        for x in conns_to_unchoke:
            x.send_unchoke()

def main():
    finished_pieces = {}
    HOST = "127.0.0.1"
    PORT = sys.argv[1]
    for x in sys.argv[2:]:
        finished_pieces[x] = DEBUG_SUBPIECE_PAYLOAD * DEBUG_PIECE_SUBPIECES
    control = Control(1, 4, finished_pieces)
    upload_control_t = myThread(random_thread_id(), upload_control_thread, control)
    download_control_t = myThread(random_thread_id(), download_control_thread, control)
    upload_control_t.run()
    download_control_t.run()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        # a forever loop until client wants to exit 
        while True: 
            # establish connection with client 
            c, (ip, port) = s.accept()
            control.add_peer(ip, port, c)
            t1 = myThread(random_thread_id(), connection_read_thread, control, ip, port)
            t2 = myThread(random_thread_id(), connection_write_thread, control, ip, port)
            t1.run()
            t2.run()


