import time
from typing import Any
import uuid
import json
import pytest
from common.robot_cluster import Cluster, Robot, Receiver
from test_data import read_data_from_yaml
from api.message.list_message_api import ListMessageAPI
from api.message.send_message_api import SendMessageAPI
# from . import logger


@pytest.mark.P0
@pytest.mark.parametrize('test_data', read_data_from_yaml(
    "list_message_case.yaml",
    "list_message_codes"
),
)
def test_list_messages_codes(groupReceiver:Receiver,cluster:Cluster, test_data:dict[str,Any]):
    """覆盖错误码"""
    if test_data.get('skip', False):
        pytest.skip(f"跳过测试: {test_data['case_name']}\n原因:{test_data.get('skip_reason','')}")
    
    # 初始化列表消息API
    send_robot = cluster.getRobot(tags=test_data['sendRobotTags'], max=1)[0]
    list_msg_api = ListMessageAPI(send_robot.access_token)
    # 读取群组消息
    list_resp = list_msg_api.list_messages(
        container_id=test_data.get('container_id',groupReceiver.receiver_id),
        container_id_type=test_data.get('container_id_type', 'chat'),
    )
    
    # 验证响应
    assert list_resp['code'] == test_data['expected_code'], f'读取消息失败: {list_resp}'

@pytest.mark.P0
@pytest.mark.parametrize('test_data', read_data_from_yaml(
    "list_message_case.yaml",
    "list_message"
))
def test_list_messages2(groupReceiverAuto:Receiver,cluster:Cluster, test_data:dict[str,Any]):
    """测试读取群组消息列表功能"""
    # 获取群聊ID
    
    # 获取发送消息的机器人
    send_robot = cluster.getRobot(tags=test_data['sendRobotTags'], max=1)[0]
    
    send_msg_api = SendMessageAPI(send_robot.access_token)
    # 生成UUID列表并存储
    uuid_messages = [str(uuid.uuid4()) for _ in range(test_data.get('msgCount',5))]
    
    # 遍历UUID列表发送消息
    for content in uuid_messages:
        send_resp = send_msg_api.send_message(
            receive_id=groupReceiverAuto.receiver_id, 
            receive_id_type=groupReceiverAuto.receiver_id_type,
            content={"text":content},
            msg_type='text',
        )
        # 验证消息发送成功
        assert send_resp['code'] == 0, f"消息发送失败: {send_resp}"
        time.sleep(1)  # 避免请求频率过高
    
    
    # 初始化列表消息API
    list_msg_api = ListMessageAPI(send_robot.access_token)
    
    # 读取群组消息
    list_resp = list_msg_api.list_messages(
        container_id=groupReceiverAuto.receiver_id,
        container_id_type='chat',
        page_size=test_data.get('page_size', 20), page_token=None
    )
    
    # 验证响应
    assert list_resp['code'] == test_data['expected_code'], f'读取消息失败: {list_resp}'
    assert 'data' in list_resp, '响应中缺少data字段'
    assert isinstance(list_resp['data']['items'], list), '消息列表格式不正确'
        # 提取返回的消息内容
    returned_contents = []
    for item in list_resp['data']['items']:
        # 跳过系统消息
        if item['msg_type'] == 'text':
            # 解析文本消息的JSON内容并提取text字段
            content_json = json.loads(item['body']['content'])
            returned_contents.append(content_json['text'])

    # 验证所有发送的UUID消息都在返回列表中
    for uuid_msg in uuid_messages:
        assert uuid_msg in returned_contents, f"发送的消息 {uuid_msg} 未在返回列表中找到"


    # # 如果期望有消息，验证消息内容
    # if test_data['expected_code'] == 0 and test_data.get('check_content', True):
    #     found = any(item['content'] == test_data['content'] for item in list_resp['data']['items'])
    #     assert found, f'未找到发送的消息内容: {test_data["content"]}'