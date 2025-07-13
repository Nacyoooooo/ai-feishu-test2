import pytest
from api.message.reply_message_api import ReplyMessageAPI
from test_data import read_data_from_yaml

@pytest.mark.P0
@pytest.mark.usefixtures("cluster")
@pytest.mark.parametrize('test_data', read_data_from_yaml(
    "reply_message_cases.yaml",
    "test_cases"
))
def test_reply_message(cluster, test_data):
    """测试回复消息"""
    if test_data.get('skip', False):
        pytest.skip("skip")
    
    receivers = cluster.getReceiver(tags=test_data['receiverTags'], max=1)
    robots = cluster.getRobot(tags=test_data['robotTags'], max=1)
    
    api_client = ReplyMessageAPI(robots[0].access_token)
    resp = api_client.reply_message(**test_data['params'])
    
    assert resp["code"] == test_data["expected_code"], \
        f"和预期结果不对应，预期结果：{test_data['expected_code']}，实际结果：{resp['code']}"