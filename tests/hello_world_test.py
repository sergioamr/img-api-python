import unittest

from tests import api

class TestHelloWorld(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestHelloWorld, self).__init__(*args, **kwargs)

    def test_unit_test_sum(self):
        # Test the unit tests
        self.assertEqual(sum([1, 2, 3]), 6, "Unit test failed")

    def test_hello_world(self):
        json = api.hello_world()
        self.assertEqual(json['status'], "success", "Hello world failed")
        self.assertEqual(json['msg'], "hello world")

