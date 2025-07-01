import requests
from requests.exceptions import RequestException

class APIClient:
    def __init__(self):
        self.base_url = "https://api.feishu.cn" # todo 读配置
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'xxx' # todo 读配置
        })

    def _request(self, method, endpoint, **kwargs):
        """Base request method with error handling"""
        url = self.base_url + endpoint
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            print(f"Request failed: {str(e)}")
            raise

    def get(self, endpoint, params=None):
        """Send GET request"""
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint, json=None):
        """Send POST request"""
        return self._request('POST', endpoint, json=json)

    def put(self, endpoint, json=None):
        """Send PUT request"""
        return self._request('PUT', endpoint, json=json)

    def delete(self, endpoint):
        """Send DELETE request"""
        return self._request('DELETE', endpoint)

    def close(self):
        """Close the session"""
        self.session.close()