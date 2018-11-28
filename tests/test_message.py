import pytest
import os
from .. import message, model
from ..model import Message

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

    def test_interest(self, skt_resource):
        pipein, pipeout = skt_resource
        message.skt_send(pipeout, Message(model.interest))
        assert message.skt_recv(pipein).msg_type == model.interest