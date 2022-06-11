import os

import unittest
from tests import api

class TestUpload(unittest.TestCase):

    def test_upload_files(self):
        import json

        basepath = "tests/upload/"
        file_list = []
        data = {}

        idx = 0
        for entry in os.listdir(basepath):
            data[entry] = json.dumps({"my_title": str(idx) + ":: My test title"})
            file_list.append(os.path.join(basepath, entry))
            idx += 1

        json_res = api.api_upload(file_list, data=data)
        self.assertEqual(json_res['status'], "success", "Upload failed")

        media = json_res['media_files'][0]
        self.assertEqual(media['my_title'], "0:: My test title",
                         "Failed to update title")
