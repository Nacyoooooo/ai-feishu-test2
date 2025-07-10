import logging

import pytest

from api.group.group import GroupAPI
from api.message.send_message_api import SendMessageAPI
from common.robot_common import get_app_access_token
from test_data import read_data_from_yaml

app_id = 'cli_a7fbac1977651013'
app_secret = 'We9ckOfILpoxrUQcafMvJfIYJgrw5IQx'
open_id = 'ou_1153fa978dae4500645ca3311c87631a'

@pytest.fixture
def setup_group():
    """测试前置：创建群聊，并返回群聊ID"""
    token = get_app_access_token(app_id, app_secret)['app_access_token']
    group_api = GroupAPI(token)
    create_resp = group_api.create_group(
        owner_id='',
        user_id_list=[open_id],
        bot_id_list=[],
        set_bot_manager="true"
    )
    group_id = create_resp['data']["chat_id"]
    logging.info(f"创建群聊成功，群聊ID: {group_id}")

    yield group_id

    group_api.delete_group(chat_id=group_id)

@pytest.mark.P0
@pytest.mark.parametrize('send_message_data', read_data_from_yaml(
        "message_case.yaml",
        "robot_not_in_group"
    ))
def test_robot_not_in_group(setup_group, send_message_data):
    token = get_app_access_token(send_message_data['app_id'], send_message_data['app_secret'])['app_access_token']
    message_api = SendMessageAPI(access_token=token)
    resp = message_api.send_message(
        receive_id=setup_group,
        receive_id_type="chat_id",
        content={"text": "test content"},
        msg_type="text",
    )
    assert resp["code"] == 230002, \
        logging.info(f"和预期结果不对应，预期结果：230025，实际结果：{resp['code']}")