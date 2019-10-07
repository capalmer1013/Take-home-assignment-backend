from flask_socketio import SocketIO
from netbeez import app, models
from .test import BaseTest

socketio = SocketIO(app)


class TestDefault(BaseTest):
    def test_index(self):
        result = self.app.get("/")
        assert result.status_code == 200


class TestSocketIO(BaseTest):
    def test_connect(self):
        client = socketio.test_client(app)
        print(client)
        pass
