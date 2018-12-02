import model, view, message, strategy
import socket

class Control(object):
	def __init__(self, file_id, total_pieces):
		self.connections = {}
		self.file_id = file_id
		self.total_pieces = total_pieces
		self.peer_to_pieces = {}
		self.piece_to_peers = {}
		self.finished_pieces = {}
		view.start_progress_plot(file_id, total_pieces)

	def add_peer(ip, port):
		# Create the socket connection
		# Store in Connection object
		skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sck.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
		skt.connect((ip, port))
		new_conn = model.Connection(skt, ip, port)
		self.connections[(ip, port)] = new_conn

	def get_peer(ip, port):
		# TODO: check connections dead or not also
		# Return Connection object or None
		return self.connections[(ip, port)]

	def peer_has_piece(ip, port, piece):
		self.peer_to_pieces[(ip, port)] = self.peer_to_pieces.get(
			(ip, port), []).append(piece)
		self.piece_to_peers[piece] = self.piece_to_peers.get(
			piece, []).append((ip, port))

	def next_piece(self):
		return strategy.choose_next_piece(self.total_pieces,
			self.finished_pieces, self.peer_to_pieces,
			self.piece_to_peers)

	def peers_for_piece(self, piece):
		return self.piece_to_peers[piece]

def _get_conn_from_control(control, ip, port):
	conn = control.get_peer(ip, port)
	if not conn:
		control.add_peer(ip, port)
		conn = control.get_peer(ip, port)
		conn.announce_pieces(list(control.finished_pieces.keys()))
	return conn

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
		msg = conn.serve_one()
		if msg:
			conn.to_send.append(msg)



def download_thread(control):
	while True:
		# choose_next_piece
		next_piece = control.next_piece()
		# peers_for_piece
		peers_ip_ports = control.peers_for_piece(next_piece)
		piece = model.Piece(next_piece)
		# Download from that peer
		for (ip, port) in peers_ip_ports:
			conn = _get_conn_from_control(control, ip, port)
			conn.send_type_only(model.INTEREST)
			subpiece = piece.thread_safe_next_subpiece()
			if subpiece == None:
				continue
			conn.send_request(next_piece, subpiece)
	return

def upload_thread():
	# peers_to_unchoke
	# Serve that peer
	return