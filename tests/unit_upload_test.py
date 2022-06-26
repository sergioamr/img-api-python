import os
import json
import unittest

from tests import api


class TestUpload(unittest.TestCase):

    def test_upload_files(self):
        import json

        basepath = "tests/upload/"
        file_list = []
        data = []

        idx = 0
        for entry in os.listdir(basepath):
            data.append({"my_title": str(idx) + ":: My test title"})
            file_list.append(os.path.join(basepath, entry))
            idx += 1

        json_res = api.api_upload(file_list, data_list=data)
        self.assertEqual(json_res['status'], "success", "Upload failed")

        media = json_res['media_files'][0]
        self.assertEqual(media['my_title'], "0:: My test title",
                         "Failed to update title")

    def test_md5(self):
        basepath = "tests/upload/"

        ret = api.api_check_md5(basepath + "rock.jpg")

        media = ret['media_files'][0]

        print(" json " + json.dumps(ret))

        self.assertEqual(media['checksum_md5'], "5630690be0473b151169f98eda4c8258")
        self.assertEqual(media['file_size'], 294518)
