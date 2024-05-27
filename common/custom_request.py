import requests
from typing import Any


class CustomRequest:

    def __init__(self, base_url: str, headers: dict = None):
        self.base_url = base_url
        self.headers = headers

    def do_get(self, endpoint: str) -> Any:
        try:
            url = self.base_url + endpoint
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error on do get: {e}")
