import pytest

from api.base_api import get_app_access_token
from api.message.send_message_api import SendMessageAPI
from test_data import read_data_from_yaml
from test_cases import logger


@pytest.mark.P0
@pytest.mark.usefixtures("create_deleted_user")
@pytest.mark.parametrize('send_message_data', read_data_from_yaml(
    "message_case.yaml",
    "common_robot"
))
def test_user_deleted(create_deleted_user, send_message_data):
    token = get_app_access_token(send_message_data['app_id'], send_message_data['app_secret'])
    message_api = SendMessageAPI(access_token=token)
    resp = message_api.send_message(
        receive_id=create_deleted_user,
        receive_id_type="open_id",
        content={"text": "test content"},
        msg_type="text",
    )
    assert resp["code"] == 230013, \
        logger.info(f"和预期结果不对应，预期结果：230013，实际结果：{resp['code']}")
