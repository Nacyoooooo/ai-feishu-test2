import requests
from requests.exceptions import RequestException
import urllib.parse

class APIClient:
    def __init__(self):
        self.base_url = "https://open.feishu.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}' # todo 读配置
        })

    def _request(self, method, endpoint, **kwargs):
        """Base request method with error handling"""
        url = self.base_url + endpoint
        response = self.session.request(method, url, **kwargs)
        return response.json()

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

def get_app_access_token(app_id, app_secret):
    # 完整API地址
    url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal'
    
    # 请求体数据
    payload = {
        'app_id': app_id,
        'app_secret': app_secret
    }
    
    # 请求头
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # 发送POST请求
    response = requests.post(url, json=payload, headers=headers)
    
    return response.json()

if __name__=='__main__':
    from test_data import read_data_from_yaml
    conf=read_data_from_yaml('message_case.yaml', 'robot')
    print(get_app_access_token(conf['app_id'], conf['app_secret'])['app_access_token'])
