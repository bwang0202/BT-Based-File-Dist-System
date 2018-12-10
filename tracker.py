import BaseHTTPServer
from threading import Thread
from logging import basicConfig, INFO
from urllib import urlopen
from urlparse import parse_qs

from bcoding import bencode
from simpledb import Database


def decode_request(path):
    """ Return the decoded request string. """

    if path[0] == "/":
        path = path[1:]

    return parse_qs(path)


class Tracker():
    def __init__(self, host="", port=9010, interval=5, \
                 torrent_db="tracker.db", log="tracker.log", \
                 inmemory=True):
        """ Read in the initial values, load the database. """

        self.host = host
        self.port = port

        self.inmemory = inmemory

        self.server_class = BaseHTTPServer.HTTPServer
        self.httpd = self.server_class((self.host, self.port), \
                                       RequestHandler)

        self.running = False  # We're not running to begin with

        self.server_class.interval = interval

        # Set logging info
        basicConfig(filename=log, level=INFO)

        # If not in memory, give the database a file, otherwise it
        # will stay in memory
        if not self.inmemory:
            self.server_class.torrents = Database(torrent_db)
        else:
            self.server_class.torrents = Database(None)

    def runner(self):
        """ Keep handling requests, until told to stop. """

        while self.running:
            self.httpd.handle_request()

    def run(self):
        """ Start the runner, in a seperate thread. """

        if not self.running:
            self.running = True

            self.thread = Thread(target=self.runner)
            self.thread.start()

    def send_dummy_request(self):
        """ Send a dummy request to the server. """

        # To finish off httpd.handle_request()
        address = "http://127.0.0.1:" + str(self.port)
        urlopen(address)

    def stop(self):
        """ Stop the thread, and join to it. """

        if self.running:
            self.running = False

            self.send_dummy_request()
            self.thread.join()

    def __del__(self):
        """ Stop the tracker thread, write the database. """

        self.stop()
        self.httpd.server_close()


def add_peer(torrents, info_hash, peer_id, ip, port):
    if info_hash in torrents and (peer_id, ip, port) not in torrents[info_hash]:
        torrents[info_hash].append((peer_id, ip, port))
    if info_hash not in torrents:
        torrents[info_hash] = [(peer_id, ip, port)]


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def DO_GET(self, s):
        client_info = decode_request(s.path)
        if not client_info:
            s.send_error(403)
            return
        info_hash = client_info["info_hash"][0]
        ip = s.client_address[0]
        port = client_info["port"][0]
        peer_id = client_info["peer_id"][0]

        response = {}
        response["peers"] = s.server.torrent[info_hash]
        s.send_response(200)
        s.end_headers()
        s.wfile.write(bencode(response))


if __name__ == "__main__":
    tracker = Tracker()
    tracker.run()
