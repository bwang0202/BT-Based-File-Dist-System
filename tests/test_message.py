import pytest
import os
from .. import message

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