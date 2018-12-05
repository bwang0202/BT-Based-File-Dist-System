
def choose_next_piece(finished_pieces, piece_to_peers, ongoing_pieces):
    # FIXME: how to guarentee this always succeeds
    for piece in piece_to_peers:
        if piece not in finished_pieces:
            if piece not in ongoing_pieces:
                return piece
    return None

def peers_to_unchoke(connections):
    # 4 based on download speed and one optimistic unchoke
    return connections