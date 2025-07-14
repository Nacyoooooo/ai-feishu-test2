from api.base_api import APIClient
import json


class SendMessageAPI(APIClient):
    def __init__(self, access_token):
        self.access_token = access_token
        super().__init__()

    def send_message(self, receive_id, content={"text":"test content"}, receive_id_type="open_id", msg_type="text", uuid=None):
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
        return self.post(endpoint, data)
