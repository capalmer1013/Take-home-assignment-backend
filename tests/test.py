from netbeez import app, models


class BaseTest(object):
    def clearDb(self):
        with app.app_context():
            models.User_Account.query.delete()
            models.Data_Stream.query.delete()
            models.db.session.commit()

    def setup_method(self, method):
        self.app = app.test_client()
        self.testCredential = {
            "user_id": "auth0|5c89789c9686f13c3cd1850b",
            "title": "login for test account",
            "third_party_username": "mfoucault",
            "password": "postmodernism",
        }
        self.testUser = {
            "user_id": self.testCredential["user_id"],
            "username": "theUserName",
        }
        self.clearDb()

    def teardown_method(self, method):
        self.clearDb()
        pass

    def json_check(self, result, expectedStatus=200, expectedResponse=None):
        """
        :param result: response object from app
        :param expectedStatus: status code expected, default 200
        :param expectedResponse: list of expected keys, or dict of expected keys and values
        :return:
        """
        # Validate json
        assert result.is_json, "Response mimetype must be application/json"
        # May return 'None' if json fails to parse
        assert result.get_json() is not None, "Invalid JSON in response body"
        json_result = result.get_json()

        assert result.status_code == expectedStatus

        if isinstance(expectedResponse, list):
            for each in expectedResponse:
                assert each in json_result

        elif isinstance(expectedResponse, dict):
            for each in expectedResponse:
                assert each in json_result
                assert json_result[each] == expectedResponse[each]

        return json_result
