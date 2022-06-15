import unittest
from tests import api

class TestUser(unittest.TestCase):
    def test_get_token(self):
        token = api.get_token()
        print(" Token " + str(len(token)))
        self.assertGreaterEqual(len(token), 150)

