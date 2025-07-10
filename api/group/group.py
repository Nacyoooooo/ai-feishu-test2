from api.base_api import APIClient
import json


class GroupAPI(APIClient):
    def __init__(self, access_token):
        self.access_token = access_token
        super().__init__()

    def create_group(self, owner_id, user_id_list, bot_id_list):
        """创建群聊
        Args:
            owner_id: 群主ID
            user_id_list: 用户ID列表
            bot_id_list: 机器人ID列表
        Returns:
            响应结果
        """
        endpoint = f"/open-apis/im/v1/chats?set_bot_manager=false&user_id_type=open_id"
        data = {
            "owner_id": owner_id,
            "user_id_list": user_id_list,
            "bot_id_list": bot_id_list,
            "name": "默认群聊",
            "chat_mode": "group",
            "chat_type": "private"
        }
        return self.post(endpoint, json=data)

    def delete_group(self, chat_id):
        """解散群聊
        Args:
            chat_id: 群聊ID
        Returns:
            响应结果
        """
        endpoint = f"/open-apis/im/v1/chats/{chat_id}"
        return self.delete(endpoint)

