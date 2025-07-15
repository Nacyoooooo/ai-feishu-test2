import uuid
from time import sleep
from typing import Any

import pytest

from common.optimized_api import ThreadSafeMessageSender
from common.robot_cluster import Cluster
from test_data import read_data_from_yaml


@pytest.mark.P0
@pytest.mark.usefixtures("robot_cluster")
@pytest.mark.parametrize('send_message_data', read_data_from_yaml(
    "send_message_case.yaml",
    "send_message"
))
def test_send_message2(robot_cluster: Cluster, send_message_data: dict[str, Any], performance_monitor):
    """测试发送消息"""
    if send_message_data.get('skip', False):
        pytest.skip("skip")
    receivers = robot_cluster.getReceiver(tags=send_message_data['receiverTags'], max=1)
    robots = robot_cluster.getRobot(tags=send_message_data['robotTags'], max=1)
    resp = robots[0].SendMessage(receivers[0], content=send_message_data['content'],
                                 msg_type=send_message_data['msg_type'])

    assert resp["code"] == send_message_data["expected_code"], \
        f"和预期结果不对应，预期结果：{send_message_data['expected_code']}，实际结果：{resp['code']}"


@pytest.mark.P0
@pytest.mark.usefixtures("robot_cluster")
@pytest.mark.parametrize('group', read_data_from_yaml(
    "send_message_case.yaml",
    "group"
))
def test_create_group(robot_cluster: Cluster, group: dict[str, Any], performance_monitor):
    """创建群组"""
    receivers = robot_cluster.getReceiver(tags=group['receiverTags'], max=-1)
    robots = robot_cluster.getRobot(tags=group['robotTags'], max=-1)
    resp = robots[0].CreateGroup(robots=robots, user_ids=receivers)
    assert resp['code'] == 0
    assert resp['data']['chat_id'] is not None
    chat_id = resp['data']['chat_id']
    """解散群组"""
    resp2 = robots[0].delete_group(chat_id=chat_id)
    assert resp2['code'] == 0


@pytest.mark.P0
@pytest.mark.usefixtures("robot_cluster")
def test_message_too_long(robot_cluster: Cluster, performance_monitor):
    """测试发送超长消息"""
    receivers = robot_cluster.getReceiver(tags={"状态": "在职"}, max=1)
    robots = robot_cluster.getRobot(tags={"name": "1"}, max=1)
    long_content = {"text": "a" * 150 * 1024}
    resp = robots[0].SendMessage(receivers[0], content=long_content, msg_type="text")
    assert resp["code"] == 230025, \
        f"和预期结果不对应，预期结果：230025，实际结果：{resp['code']}"


@pytest.mark.P1
@pytest.mark.usefixtures("robot_cluster")
@pytest.mark.parametrize('rates', read_data_from_yaml(
    "send_message_case.yaml",
    "rates"
))
def test_message_rate_limit(robot_cluster: Cluster, rates: dict[str, Any], performance_monitor):
    """测试发送消息的速率"""
    if rates.get('skip', False):
        pytest.skip("skip")
    receivers = robot_cluster.getReceiver(tags=rates['receiverTags'], max=1)
    robots = robot_cluster.getRobot(tags=rates['robotTags'], max=1)
    content = {"text": "测QPS"}

    # 使用线程安全的消息发送器
    sender = ThreadSafeMessageSender(robots[0], receivers[0])
    resp_list = sender.send_messages_concurrently(content, rates['threads'], None, "text")

    assert any(resp["code"] == rates['expected_code'] for resp in resp_list)


@pytest.mark.P1
@pytest.mark.usefixtures("robot_cluster")
@pytest.mark.parametrize('same', read_data_from_yaml(
    "send_message_case.yaml",
    "same"
))
def test_message_same(robot_cluster: Cluster, same: dict[str, Any], performance_monitor):
    """测试发送消息的重复"""
    sleep(1)
    receivers = robot_cluster.getReceiver(tags=same['receiverTags'], max=1)
    robots = robot_cluster.getRobot(tags=same['robotTags'], max=1)
    content = {"text": "查重"}
    uuid_with_hyphens = str(uuid.uuid4())

    # 使用线程安全的消息发送器
    sender = ThreadSafeMessageSender(robots[0], receivers[0])
    resp_list = sender.send_messages_concurrently(content, same['threads'], uuid_with_hyphens, "text")

    assert any(resp["code"] == same['expected_code'] for resp in resp_list)


if __name__ == '__main__':
    pytest.main(["-m", "P0", __file__])
