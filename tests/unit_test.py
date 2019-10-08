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
        result = client.get_received()[0]["args"]
        assert "error" in result
        # create user
        with app.app_context():
            user = models.User_Account.create()
            print(user.id)
        # send a value for them
        # make sure it gets set
        values = {"id", "sensor_type", "sensor_name", "value"}

        # send values for invalid userid
        # make sure it's an error
