import pytest

from api.base_api import get_app_access_token
from api.message.send_message_api import SendMessageAPI
from test_cases import logger


@pytest.mark.P0
def test_message_too_long(self):
    token = get_app_access_token("cli_a8ee0c6a92e7501c", "9kbasiKxCyonOjJ2BCfXHcaKLKPA4fJT")
    message_api = SendMessageAPI(access_token=token)
    long_content = {"text": "a" * 150 * 1024}
    resp = message_api.send_message(
        receive_id="ou_adf4e416e22c12c5d4b40e347315f68c",
        receive_id_type="open_id",
        content=long_content
    )
    assert resp["code"] == 230025, \
        logger.info(f"和预期结果不对应，预期结果：230025，实际结果：{resp['code']}")