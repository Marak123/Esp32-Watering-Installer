import requests

class MyHttpRequest:
    def __init__(self, url=""):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
        }
        self._jsonVersion = None

    def get(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            if response.status_code == 200:
                return response.content
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def post(self, data):
        try:
            response = requests.post(self.url, data=data, headers=self.headers)
            if response.status_code == 200:
                return response.content
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def JSONrequest(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def getJSON(self):
        if self._jsonVersion is None:
            self._jsonVersion = self.JSONrequest()
        return self._jsonVersion