import os
import logging
from typing import Optional, Any

from api.message.send_message_api import SendMessageAPI
from api.group.group import GroupAPI
from api.file.upload_file_api import UploadFileAPI
# tag是标签
from .robot_common import get_app_access_token
from .resource_pool import resource_pool

logger = logging.getLogger(__name__)
# 单个接收者
class Receiver:
    def __init__(self,receiver_id,tags:dict[str, str]={},receiver_id_type="open_id"):
        self.tags=tags
        self.receiver_id=receiver_id
        self.receiver_id_type=receiver_id_type
# 单个机器人
class Robot:
    def __init__(self, app_id, app_secret,tags:dict[str, str]={}):
        self.tags=tags
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = resource_pool.get_token(app_id, app_secret)
    
    def SendMessage(self,receiver:Receiver,content:Any,msg_type:str,uuid:Optional[str]=None):
        message_api = SendMessageAPI(access_token=self.access_token)
        resp = message_api.send_message(receive_id=receiver.receiver_id, receive_id_type=receiver.receiver_id_type,
                                            content=content,
                                            msg_type=msg_type,uuid=uuid)
        return resp
    
    def CreateGroup(self,robots:list['Robot'],user_ids:list['Receiver'],owner_id:Optional[str]=None,name="默认群聊"):
        group_api = GroupAPI(access_token=self.access_token)
        resp = group_api.create_group(bot_id_list=[robot.app_id for robot in robots],\
            user_id_list=[user.receiver_id for user in user_ids],\
                owner_id=owner_id,name=name)
        return resp
    
    def delete_group(self,chat_id:str):
        group_api = GroupAPI(access_token=self.access_token)
        resp = group_api.delete_group(chat_id=chat_id)
        return resp
    
    def send_file(self,file_path:str,file_type:str):
        upload_api = UploadFileAPI(access_token=self.access_token)
        resp = upload_api.upload_file(file_type=file_type, file_name=file_path, file_path=file_path)
        return resp
# 集群
class Cluster:
    def __init__(self, robots:list[Robot],receivers:list[Receiver]):
        self.robots = robots
        self.receivers =receivers
    
    def getRobot(self,tags:dict[str, str],max:int=1):
        matching_robots = [
            robot for robot in self.robots
            if all(robot.tags.get(k) == v for k, v in tags.items())
        ]
        if max > 0:
            return matching_robots[:max]
        return matching_robots
    
    def getReceiver(self,tags:dict[str, str],max:int=1):
        matching_receivers = [
            receiver for receiver in self.receivers
            if all(receiver.tags.get(k) == v for k, v in tags.items())
        ]
        if max > 0:
            return matching_receivers[:max]
        return matching_receivers
    
                 
        
        
        
    
    