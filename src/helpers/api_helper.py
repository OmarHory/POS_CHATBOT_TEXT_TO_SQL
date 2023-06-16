import requests


class APIHelper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.foodics.com/v5/"

    def get(self, endpoint, params=None):
        url = self.base_url + endpoint
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        print(headers)
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def post(self, endpoint, data=None):
        url = self.base_url + endpoint
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def put(self, endpoint, data=None):
        url = self.base_url + endpoint
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.put(url, headers=headers, json=data)
        return response.json()

    def delete(self, endpoint):
        url = self.base_url + endpoint
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.delete(url, headers=headers)
        return response.json()
