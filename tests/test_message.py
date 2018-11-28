import pytest
import os
from .. import message, model
from ..model import *

@pytest.fixture()
def skt_resource():
    pipein, pipeout = os.pipe()
    yield (pipein, pipeout)
    os.close(pipein)
    os.close(pipeout)

class TestSendRecvMsg(object):
    def test_basic(self, skt_resource):
        pipein, pipeout = skt_resource
        msg = os.urandom(200)
        message._skt_send_msg(pipeout, msg)
        assert message._skt_recv_msg(pipein) == msg

    def test_interest_choke(self, skt_resource):
        pipein, pipeout = skt_resource
        for x in [INTEREST, UNINTEREST, CHOKE, UNCHOKE]:
            message.skt_send(pipeout, Message(x))
            assert message.skt_recv(pipein).msg_type == x

    def test_request_cancel(self, skt_resource):
        pipein, pipeout = skt_resource
        pieces = [0, 2, 8, 9]
        subpieces = [0, 1, 100, 4000]
        for x in [REQUEST, CANCEL]:
            for p in pieces:
                for sp in subpieces:
                    message.skt_send(pipeout, Message(x, p, sp))
                    msg_recv = message.skt_recv(pipein)
                    assert msg_recv.msg_type == x
                    assert msg_recv.piece == p
                    assert msg_recv.subpiece == sp
                    assert msg_recv.payload == None

    def test_announce(self, skt_resource):
        pipein, pipeout = skt_resource
        ap = [0, 1, 3, 4, 6, 11, 132, 4134]
        message.skt_send(pipeout, Message(ANNOUNCE, ap=ap))
        msg_recv = message.skt_recv(pipein)
        assert msg_recv.msg_type == ANNOUNCE
        assert msg_recv.announce_pieces == ap