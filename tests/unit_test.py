from netbeez import app, models
from .test import BaseTest


class TestDefault(BaseTest):
    def test_index(self):
        result = self.app.get("/")
        assert result.status_code == 200
