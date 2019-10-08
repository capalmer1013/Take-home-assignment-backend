from netbeez import app, models
from .test import BaseTest


class TestDefault(BaseTest):
    def test_index(self):
        result = self.app.get("/")
        assert result.status_code == 200


class TestSocketIO(BaseTest):
    def test_sendingValues(self):
        self.client.send({"key": "value"}, json=True)
        result = self.client.get_received()
        assert "error" in result[0]["args"]
        # create user
        with app.app_context():
            user_id = models.User_Account.create().id
        # send a value for them
        values = {
            "id": user_id,
            "sensor_type": "electricity_w",
            "sensor_name": "elec1",
            "value": 1.5,
        }
        self.client.send(values, json=True)

        # make sure it gets set
        result = self.app.get("/users/" + str(user_id))
        assert result.status_code == 200
        json_result = self.json_filter(result)
        assert len(json_result) == 1
        result = self.client.get_received()
        assert len(result) == 0
        # send values for invalid userid
        values["id"] += 1
        # make sure it's an error
        self.client.send(values, json=True)
        result = self.client.get_received()
        assert "error" in result[0]["args"]
