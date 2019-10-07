from flask_socketio import SocketIO
from netbeez import app, models
from netbeez.api import socketio
from .test import BaseTest


class TestDefault(BaseTest):
    def test_index(self):
        result = self.app.get("/")
        assert result.status_code == 200


class TestSocketIO(BaseTest):
    def test_connect(self):
        client = socketio.test_client(app)
        client.connect()
        client.get_received()  # clear buffer
        client.send({"key": "value"}, json=True)
        print(client.get_received())
        pass
