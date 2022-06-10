import unittest
from tests import api

class TestUser(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        print(" IMGAPI Unit testing ")
        super(TestUser, self).__init__(*args, **kwargs)

    def setUp(self):
        print(" SETUP ")

