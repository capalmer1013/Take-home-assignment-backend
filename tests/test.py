from netbeez import app, models
from netbeez.api import socketio


class BaseTest(object):
    def clearDb(self):
        with app.app_context():
            models.Data_Stream.query.delete()
            models.User_Account.query.delete()
            models.db.session.commit()

    def setup_method(self, method):
        self.app = app.test_client()
        self.client = socketio.test_client(app)
        self.client.connect()
        self.client.get_received()  # clear buffer
        self.clearDb()

    def teardown_method(self, method):
        self.clearDb()
        pass

    def json_filter(self, result):
        # Validate json
        assert result.is_json
        # May return 'None' if json fails to parse
        json_result = result.get_json()
        assert json_result is not None

        return json_result
