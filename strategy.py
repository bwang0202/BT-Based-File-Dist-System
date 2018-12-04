
def choose_next_piece(total_pieces, finished_pieces,
        peer_to_pieces=None, piece_to_peers=None):
    for piece in piece_to_peers:
        if not finished_pieces.get(piece):
            return piece
    return None

def peers_to_unchoke(connections):
    # 4 based on download speed and one optimistic unchoke
    return connections