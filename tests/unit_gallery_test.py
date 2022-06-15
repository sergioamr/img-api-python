import unittest
from tests import api

class TestUser(unittest.TestCase):
    def test_create_open_gallery(self):

        gallery_def = {
            'title' : 'My test gallery',
            'header' : 'My Gallery Title',
            'description' : 'My Description',
            'is_public': True,
            'allow_public_upload': False,
        }

        gallery = api.create_gallery(gallery_def)
        self.assertEqual(gallery['name'], "my_test_gallery")

        gallery_check = api.get_gallery_by_id(gallery['id'])
        self.assertEqual(gallery['name'], gallery_check['name'])

        ret = api.remove_gallery_by_id(gallery['id'])
        self.assertEqual(ret['status'], 'success')
        self.assertEqual(ret['deleted'], True)






