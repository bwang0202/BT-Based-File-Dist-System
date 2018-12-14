from util import *
from random import randint

def choose_next_piece(finished_pieces, piece_to_peers, ongoing_pieces):
    # FIXME: how to guarentee this always succeeds
    for piece in piece_to_peers:
        if piece not in finished_pieces:
            if piece not in ongoing_pieces:
                return piece
    return None

def peers_to_unchoke(connections):
    if not SPEED_UNCHOKE:
        return (connections, connections)
    # 4 based on download speed and one optimistic unchoke
    # First try random unchoke
    if len(connections) == 0:
        return (connections, connections)
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