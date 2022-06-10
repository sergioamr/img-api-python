import unittest

from imgapi import imgapi

class TestUser(unittest.TestCase):

    def setUp(self):
        print(" SETUP ")

    def test_sum(self):
        self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")

    def test_sum_tuple(self):
        self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")

