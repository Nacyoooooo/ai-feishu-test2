import logging

import pytest

from api.message_api import SendMessageAPI
from test_data import read_data_from_yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class TestSendMessage:

    @pytest.mark.P0
    @pytest.mark.parametrize('send_message_data', read_data_from_yaml(
        "message_case.yaml",
        "send_message"
    ))
    def test_send_message(self, send_message_data):
        message_api = SendMessageAPI()
        """测试发送消息API，增加详细日志和错误处理"""
        receive_id = send_message_data['receive_id']
        receive_type = send_message_data['receive_id_type']

        resp = message_api.send_message(receive_id=receive_id, receive_id_type=receive_type,
                                            content=send_message_data['content'],
                                            msg_type="text")
        assert resp["code"] == send_message_data["expected_code"], \
            logging.info(f"和预期结果不对应，预期结果：{send_message_data['expected_code']}，实际结果：{resp['code']}")


if __name__ == '__main__':
    pytest.main(["-m", "P0", __file__])
