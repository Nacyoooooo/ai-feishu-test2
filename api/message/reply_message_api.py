from api.base_api import APIClient
import json


class ReplyMessageAPI(APIClient):
    def __init__(self):
        super().__init__()
        
    def reply_message(self, message_id, content, msg_type="text", reply_in_thread=False, uuid=None):
        """回复飞书消息
        Args:
            message_id: 要回复的消息ID
            content: 消息内容字典，如{"text":"消息文本"}
            msg_type: 消息类型，默认为text
            reply_in_thread: 是否以话题形式回复，默认为False
            uuid: 消息唯一标识，选填
        Returns:
            响应结果
        """
        endpoint = f"/im/v1/messages/{message_id}/reply"
        data = {
            "content": json.dumps(content),
            "msg_type": msg_type,
            "reply_in_thread": reply_in_thread,
            "uuid": uuid
        }
        return self.post(endpoint, data)

