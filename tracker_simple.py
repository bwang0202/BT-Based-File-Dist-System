# Python2.7
import time
import BaseHTTPServer
from urlparse import parse_qs
import json

HOST_NAME = 'localhost' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8999 # Maybe set this to 9000.
data = None

def decode_request(path):
    """ Return the decoded request string. """
    if path[0] == "/":
        path = path[1:]

    return parse_qs(path)

class PeersData():
    def __init__(self):
        self.torrents = {}

    def add_peer(self, info_hash, peer_id, ip, port):
        if info_hash in self.torrents and (peer_id, ip, port) not in self.torrents[info_hash]:
            self.torrents[info_hash].append((peer_id, ip, port))
        if info_hash not in self.torrents:
            self.torrents[info_hash] = [(peer_id, ip, port)]

    def get_peers(self):
        return self.torrents


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(s):
        """Respond to a GET request."""
        global data
        client_info = decode_request(s.path)
        if not client_info:
            s.send_error(403)
            return
        info_hash = client_info["info_hash"][0]
        ip = s.client_address[0]
        port = client_info["port"][0]
        peer_id = client_info["peer_id"][0]

        response = {}
        response["peers"] = data.get_peers().get(info_hash, [])
        data.add_peer(info_hash, peer_id, ip, port)
        s.send_response(200)
        s.end_headers()
        s.wfile.write(json.dumps(response))

if __name__ == '__main__':
    global data
    server_class = BaseHTTPServer.HTTPServer
    data = PeersData()
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)