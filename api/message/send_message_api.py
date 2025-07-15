import json

import requests

from api.base_api import APIClient
from common.rate_limiter import get_global_rate_limiter


class SendMessageAPI(APIClient):
    def __init__(self, access_token):
        self.rate_limiter = get_global_rate_limiter()
        self.access_token = access_token
        super().__init__()

    def send_message(self, receive_id, content, receive_id_type, msg_type, uuid=None, ignore_limit=False):
        """发送飞书消息
        Args:
            receive_id: 接收者ID
            content: 消息内容字典，如{"text":"消息文本"}
            msg_type: 消息类型，默认为text
            uuid: 消息唯一标识，选填
            receive_id_type: 接收者ID类型，可选值: user_id, open_id, union_id, email, chat_id
        Returns:
            响应结果
        """
        endpoint = f"/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
        data = {
            "content": json.dumps(content),
            "msg_type": msg_type,
            "receive_id": receive_id,
            "uuid": uuid
        }
        if ignore_limit:
            return self.post(endpoint, data)
        acquired = acquire()
        while acquired is False:
            acquired = acquire()
        return self.post(endpoint, data)

def acquire():
    response = requests.get('http://localhost:8080/limit')
    result = response.json()
    if isinstance(result, bool):
        return result
    return None
