from api.base_api import APIClient
import json

class SendMessageAPI(APIClient):
    def __init__(self, base_url=None):
        super().__init__()  # 移除base_url参数，修复父类构造函数参数不匹配问题
        
    def send_message(self, receive_id, content, msg_type="text", uuid=None, receive_id_type="open_id"):
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
        # 验证receive_id_type是否合法
        valid_types = {'user_id', 'open_id', 'union_id', 'email', 'chat_id'}
        if receive_id_type not in valid_types:
            raise ValueError(f"receive_id_type必须是以下之一: {', '.join(valid_types)}")
        
        endpoint = f"/im/v1/messages?receive_id_type={receive_id_type}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        data = {
            "content": json.dumps(content),
            "msg_type": msg_type,
            "receive_id": receive_id,
            "uuid": uuid
        }
        return self._request("POST", endpoint, headers=headers, json=data)