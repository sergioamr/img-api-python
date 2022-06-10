import unittest
from tests import api

class TestUser(unittest.TestCase):
    def test_get_token(self):
        json = api.get_token()
        self.assertEqual(json['status'], "success", "Token failed")
        self.assertEqual(len(json['token']), 201)

