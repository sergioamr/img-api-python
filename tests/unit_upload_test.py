import os
import unittest
from tests import api

class TestUpload(unittest.TestCase):
    def test_upload_files(self):

        basepath = "tests/upload/"
        file_list = []
        for entry in os.listdir(basepath):
            file_list.append(os.path.join(basepath, entry))

        json = api.api_upload(file_list)
        self.assertEqual(json['status'], "success", "Token failed")
        self.assertEqual(len(json['token']), 201)

