import sys
from pathlib import Path

import pytest
from test_data import read_data_from_yaml
from api.base_api import get_app_access_token
from api.employee.employee_api import EmployeeAPI
from api.group.group import GroupAPI
from api.message.list_message_api import ListMessageAPI
from api.message.send_message_api import SendMessageAPI
from common.robot_cluster import Cluster,Receiver,Robot

robotsData = read_data_from_yaml(
    "robots.yaml",
    "robots"
    )
receiversData = read_data_from_yaml(
    "robots.yaml",
    "receivers"
    )

@pytest.fixture
def groupReceiver():
    """测试前置：创建群聊，并返回群聊实体"""
    robot = Robot(app_id=robotsData[0]['app_id'], app_secret=robotsData[0]['app_secret'], tags=robotsData[0]['tags'])
    receiver = Receiver(receiver_id=receiversData[0]['receiver_id'], tags=receiversData[0]['tags'],receiver_id_type=receiversData[0]['receiver_id_type'])

    group_api=GroupAPI(robot.access_token)
    createResp=group_api.create_group(user_id_list=[receiver.receiver_id],bot_id_list=[robot.app_id])
    
    receiver = Receiver(receiver_id=createResp['data']['chat_id'], tags=[],receiver_id_type='chat_id')

    yield receiver

    group_api.delete_group(receiver.receiver_id)
    # robot.delete_group(receiver.receiver_id)

@pytest.fixture
def groupReceiver():
    """测试前置：创建群聊，并返回群聊实体"""
    robot = Robot(app_id=robotsData[0]['app_id'], app_secret=robotsData[0]['app_secret'], tags=robotsData[0]['tags'])
    receiver = Receiver(receiver_id=receiversData[0]['receiver_id'], tags=receiversData[0]['tags'],receiver_id_type=receiversData[0]['receiver_id_type'])

    group_api=GroupAPI(robot.access_token)
    createResp=group_api.create_group(user_id_list=[receiver.receiver_id],bot_id_list=[robot.app_id,'cli_a8e0f7e7cbfb1013'])
    
    receiver = Receiver(receiver_id=createResp['data']['chat_id'], tags=[],receiver_id_type='chat_id')

    yield receiver

    group_api.delete_group(receiver.receiver_id)
    # robot.delete_group(receiver.receiver_id)