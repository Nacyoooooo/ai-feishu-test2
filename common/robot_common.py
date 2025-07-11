import requests

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
    
    return response.json()['app_access_token']

__all__ = ['get_app_access_token']