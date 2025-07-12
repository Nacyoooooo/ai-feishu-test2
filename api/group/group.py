from api.base_api import APIClient
import json


class GroupAPI(APIClient):
    def __init__(self, access_token):
        self.access_token = access_token
        super().__init__()

    def create_group(self, user_id_list:list[str], bot_id_list:list[str],owner_id=None, set_bot_manager="false",name="默认群聊"):
        """创建群聊
        Args:
            owner_id: 群主ID
            user_id_list: 用户ID列表
            bot_id_list: 机器人ID列表
            set_bot_manager: 机器人是否是管理员
        Returns:
            响应结果
        """
        endpoint = f"/open-apis/im/v1/chats?set_bot_manager={set_bot_manager}&user_id_type=open_id"
        data = {
            "owner_id": owner_id,
            "user_id_list": user_id_list,
            "bot_id_list": bot_id_list,
            "name": name,
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

    def update_group_moderation(self, chat_id, moderation_setting, moderator_added_list=None, 
                               moderator_removed_list=None, user_id_type="open_id"):
        """更新群发言权限
        Args:
            chat_id: 群聊ID
            moderation_setting: 发言权限设置类型，如"moderator_list"
            moderator_added_list: 新增的发言权限用户ID列表
            moderator_removed_list: 移除的发言权限用户ID列表
            user_id_type: 用户ID类型，默认为"open_id"
        Returns:
            响应结果
        """
        endpoint = f"/open-apis/im/v1/chats/{chat_id}/moderation?user_id_type={user_id_type}"
        data = {
            "moderation_setting": moderation_setting
        }
        
        if moderator_added_list:
            data["moderator_added_list"] = moderator_added_list
        if moderator_removed_list:
            data["moderator_removed_list"] = moderator_removed_list
            
        return self.put(endpoint, json=data)

    def get_group_moderation(self, chat_id, user_id_type="open_id"):
        """获取群发言权限设置
        Args:
            chat_id: 群聊ID
            user_id_type: 用户ID类型，默认为"open_id"
        Returns:
            响应结果
        """
        endpoint = f"/open-apis/im/v1/chats/{chat_id}/moderation?user_id_type={user_id_type}"
        return self.get(endpoint)

