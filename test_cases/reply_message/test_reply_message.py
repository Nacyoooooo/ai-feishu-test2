import pytest
from typing import Any
from api.message.reply_message_api import ReplyMessageAPI
from test_data import read_data_from_yaml
from common.robot_cluster import Cluster

@pytest.mark.P0
@pytest.mark.usefixtures("cluster")
@pytest.mark.parametrize('test_data', read_data_from_yaml(
    "reply_message_case.yaml",
    "reply_message_cases"
))
def test_reply_message(cluster: Cluster, test_data: dict[str, Any]):
    if test_data.get('skip', False):
        pytest.skip("skip")
    receivers = cluster.getReceiver(tags=test_data['receiverTags'], max=1)
    robots = cluster.getRobot(tags=test_data['robotTags'], max=1)
    api_client = ReplyMessageAPI(robots[0].access_token)
    test_data['params']['message_id'] = "om_x100b480c8f45e4b00f105cda99a01a9"
    resp = api_client.reply_message(**test_data['params'])
    assert resp["code"] == test_data["expected_code"], \
        f"和预期结果不对应，预期结果：{test_data['expected_code']}，实际结果：{resp['code']}"

def test_message_length_exceed_limit(cluster: Cluster):
    """测试消息体长度超出限制（230025）"""
    receivers = cluster.getReceiver(tags={"性质": "人", "机器人1": "可见"}, max=1)
    robots = cluster.getRobot(tags={"desc": "全功能"}, max=1)
    api_client = ReplyMessageAPI(robots[0].access_token)
    超长文本 = "a" * 150 * 1024 + "b"  # 150KB + 1字节
    params = {
        "message_id": "om_x100b480c8f45e4b00f105cda99a01a9",
        "msg_type": "text",
        "content": {"text": 超长文本}
    }
    resp = api_client.reply(**params)
    assert resp["code"] == 230025, f"预期错误码230025，实际：{resp['code']}"

def test_exceed_frequency_limit(cluster: Cluster):
    """测试超出调用频率限制（230020）"""
    receivers = cluster.getReceiver(tags={"性质": "人", "机器人1": "可见"}, max=1)
    robots = cluster.getRobot(tags={"desc": "全功能"}, max=1)
    api_client = ReplyMessageAPI(robots[0].access_token)
    params = {
        "message_id": "om_x100b480c8f45e4b00f105cda99a01a9",
        "msg_type": "text",
        "content": {"text": "测试频率限制"}
    }
    # 短时间内发送多次请求触发限制
    for _ in range(20):
        resp = api_client.reply(**params)
    assert resp["code"] == 230020, f"预期错误码230020，实际：{resp['code']}"
