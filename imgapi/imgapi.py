import json
import requests


class ImgAPI():
    _instance = None
    token = None

    def __new__(cls):
        # Singleton
        if cls._instance is None:
            print("================================")
            print(" IMGAPI Start ")
            print("================================")
            cls._instance = super(ImgAPI, cls).__new__(cls)

        return cls._instance

    def setup(self, api_entry, props={}):
        self.props = props
        self.api_entry = api_entry

        if 'token' in props:
            self.token = props.token

    def api_call(self, url, data=None):
        api_url = self.api_entry + url
        if self.token:
            if url.find("?"):
                api_url += "&"
            else:
                api_url += "?"

            api_url += "key=" + self.token

        try:
            if data:
                r = requests.post(api_url, json=data)
            else:
                r = requests.get(api_url)

        except requests.exceptions.RequestException as e:
            print(" Failed on request ")
            raise e

        return r.json()

    def create_user(self, user_data):
        return self.api_call("/create", user_data)

    def create_user_helper(self, username, password, email, first_name,
                           last_name):
        user_obj = {
            'username': username,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
        }
        return self.api_call("/create_user", user_obj)

    def hello_world(self):
        print(" Hello world ")
        return self.api_call("/hello_world")
