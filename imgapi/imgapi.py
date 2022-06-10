import json
import requests

class imgapi():
    def __init__(self, api_entry):
        self.api_entry = api_entry
        self.token = None

    def api_call(self, url, data=None):
        api_url = self.api_entry + url
        if self.token:
            if url.find("?"):
                api_url += "&"
            else:
                api_url += "?"

            api_url += "key=" + self.token

        if data:
            r = requests.post(api_url, json=data)
        else:
            r = requests.get(api_url)

        return r.json()

    def create_user(username, password, email):

        return True
