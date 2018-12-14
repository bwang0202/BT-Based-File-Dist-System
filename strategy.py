from util import *
from random import randint
import functools

def choose_next_piece(finished_pieces, piece_to_peers, ongoing_pieces):
    # FIXME: how to guarentee this always succeeds
    for piece in piece_to_peers:
        if piece not in finished_pieces:
            if piece not in ongoing_pieces:
                return piece
    return None

def peers_to_unchoke(connections):
    if not SPEED_UNCHOKE:
        for conn in connections:
            print("peer_id %s download speed %s" % (str(conn.peer_id), str(conn.get_download_speed())))
        return (connections, [])
    if RANDOM_UNCHOKE:
        # Random unchoke
        if len(connections) == 0:
            return ([], [])
        to_unchokes = []
        for x in range(UNCHOKE_PEERS):
            to_unchoke = randint(0, len(connections) - 1)
            while to_unchoke in to_unchokes:
                to_unchoke = randint(0, len(connections) - 1)
            to_unchokes.append(to_unchoke)
        unchokes = []
        chokes = []
        for i in range(len(connections)):
            conn = connections[i]
            if i in to_unchokes:
                unchokes.append(conn)
            else:
                chokes.append(conn)
            print("peer_id %s download speed %s" % (str(conn.peer_id), str(conn.get_download_speed())))

        return (unchokes, chokes)
    else:
        # Speed based unchoke
        def download_speed_desc(x, y):
            return y.get_download_speed() - x.get_download_speed()
        conns = sorted(connections, key=functools.cmp_to_key(download_speed_desc))
        unchokes = conns[:UNCHOKE_PEERS]
        chokes = conns[UNCHOKE_PEERS:]
        for conn in unchokes:
            print("UNCHOKING peer_id %s download speed %s" % (str(conn.peer_id), str(conn.get_download_speed())))
        for conn in chokes:
            print("CHOKING peer_id %s download speed %s" % (str(conn.peer_id), str(conn.get_download_speed())))
        return (unchokes, chokes)