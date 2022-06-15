import json
import requests

from imgapi.version import __version__


class ImgAPI():
    user = None
    token = None
    _instance = None

    def __new__(cls):
        # Singleton
        if cls._instance is None:
            print("================================")
            print(" IMGAPI Start v" + __version__)
            print("================================")
            cls._instance = super(ImgAPI, cls).__new__(cls)

        return cls._instance

    def get_api_url(self, url):
        api_url = self.api_entry + url
        if not self.token:
            return api_url

        if url.find("?") == -1:
            api_url += "?"
        else:
            api_url += "&"

        api_url += "key=" + self.token
        return api_url

    def setup(self, api_entry, props={}):
        self.props = props
        self.api_entry = api_entry

        if 'token' in props:
            self.token = props.token

    def api_call(self, url, data=None):
        api_url = self.get_api_url(url)
        try:
            if data:
                r = requests.post(api_url, json=data)
            else:
                r = requests.get(api_url)

        except requests.exceptions.RequestException as e:
            print(" Failed on request ")
            raise e

        return r.json()

    def api_upload(self, file_paths, gallery_id=None, data_list=None):
        files = {}

        data = None
        if data_list: data = {}

        for idx, path in enumerate(file_paths):
            f = open(path, 'rb')

            name = path.split("/")[-1]
            files[name] = (name, f)

            if data_list and len(data_list) > idx:
                data[name] = json.dumps(data_list[idx])

        if not files:
            return False

        upload_url = "/media/upload"
        if gallery_id: upload_url += "?gallery_id=" + gallery_id

        api_url = self.get_api_url(upload_url)
        try:

            r = requests.post(api_url, files=files, data=data)
        except requests.exceptions.RequestException as e:
            print(" Failed on request ")
            raise e

        return r.json()

    def create_user(self, user_data):
        json = self.api_call("/user/create", user_data)

        if 'error_msg' in json:
            print(" Failed creating user: " + str(json['error_msg']))
            return json

        if 'token' in json:
            self.token = json['token']

        if 'user' in json:
            self.user = json['user']
            return self.user

        return json

    def create_user_helper(self, username, password, email, first_name,
                           last_name):
        user_obj = {
            'username': username,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
        }
        return self.api_call("/user/create", user_obj)

    def hello_world(self):
        print(" Hello world ")
        return self.api_call("/hello_world")

    def get_token(self):
        if self.token:
            return self.token

        res = self.api_call("/user/token")
        if 'error_msg' in res:
            print("ERROR: " + res['error_msg'])
            return res

        if 'token' not in res:
            return res

        self.token = res['token']
        return self.token

    def create_gallery(self, gallery_def):
        json = self.api_call("/user/list/create", gallery_def)
        return json

    def get_gallery_by_id(self, gallery_id):
        json = self.api_call("/user/list/get_by_id/" + gallery_id)
        return json

    def remove_gallery_by_id(self, gallery_id):
        json = self.api_call("/user/me/list/" + gallery_id + "/remove")
        return json
