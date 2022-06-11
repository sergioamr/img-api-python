import os
import unittest
from tests import api


class TestUpload(unittest.TestCase):

    def test_upload_files(self):

        basepath = "tests/upload/"
        file_list = []
        for entry in os.listdir(basepath):
            file_list.append(os.path.join(basepath, entry))

        json = api.api_upload(file_list, data={"my_title": "Test Upload"})
        self.assertEqual(json['status'], "success", "Upload failed")

        media = json['media_files'][0]
        self.assertEqual(media['my_title'], "Test Upload", "Failed to update title")
