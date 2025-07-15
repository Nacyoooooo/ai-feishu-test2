import threading

import pytest

from api.message.send_message_api import SendMessageAPI
from common.robot_common import get_app_access_token
from test_data import read_data_from_yaml
from . import logger


class TestSendMessage:

    @pytest.mark.P0
    @pytest.mark.parametrize('send_message_data', read_data_from_yaml(
        "message_case.yaml",
        "send_message"
    ))
    def test_send_message(self, send_message_data):
        # API内部问题先跳过
        if 'skip' in send_message_data and send_message_data['skip'] is True:
            pytest.skip("skip")
        token = get_app_access_token(send_message_data['app_id'], send_message_data['app_secret'])
        """测试发送消息API，增加详细日志和错误处理"""
        message_api = SendMessageAPI(access_token=token)
        receive_id = send_message_data['receive_id']
        receive_type = send_message_data['receive_id_type']

        resp = message_api.send_message(receive_id=receive_id, receive_id_type=receive_type,
                                        content=send_message_data['content'],
                                        msg_type="text")
        assert resp["code"] == send_message_data["expected_code"], \
            logger.info(f"和预期结果不对应，预期结果：{send_message_data['expected_code']}，实际结果：{resp}")

    @pytest.mark.P0
    def test_message_rate_limit(self):
        """阈值50次/秒"""
        token = get_app_access_token("cli_a8ee0c6a92e7501c", "9kbasiKxCyonOjJ2BCfXHcaKLKPA4fJT")
        message_api = SendMessageAPI(access_token=token)
        resp_list = []

        def send_request():
            resp = message_api.send_message(
                receive_id="ou_adf4e416e22c12c5d4b40e347315f68c",
                receive_id_type="open_id",
                content={"text": "test"},
                msg_type="text",
                ignore_limit=True
            )
            if resp["code"] == 230020:
                resp_list.append(resp)

        threads = []
        for _ in range(50):
            t = threading.Thread(target=send_request)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        assert any(resp["code"] == 230020 for resp in resp_list)


class TestListMessage:
    @pytest.mark.P0
    @pytest.mark.parametrize('list_message_data', read_data_from_yaml(
        "message_case.yaml",
        "list_message"
    ))
    def test_list_message(self, list_message_data):
        from api.message.list_message_api import ListMessageAPI
        from common.robot_common import get_app_access_token
        """测试获取历史消息API"""
        if 'skip' in list_message_data and list_message_data['skip'] is True:
            pytest.skip("skip")
        token = get_app_access_token(list_message_data['app_id'],
                                     list_message_data['app_secret'])
        message_api = ListMessageAPI(access_token=token)

        resp = message_api.list_messages(
            container_id_type=list_message_data['container_id_type'],
            container_id=list_message_data['container_id'],
            start_time=list_message_data.get('start_time'),
            end_time=list_message_data.get('end_time'),
            sort_type=list_message_data.get('sort_type', 'ByCreateTimeAsc'),
            page_size=list_message_data.get('page_size', 20),
            page_token=list_message_data.get('page_token')
        )

        assert resp["code"] == list_message_data["expected_code"], \
            f"响应码不匹配，预期: {list_message_data['expected_code']}, 实际: {resp['code']}"

        if resp["code"] == 0:
            assert "items" in resp["data"], "成功响应应包含消息列表"
            logger.info(f"获取到 {len(resp['data']['items'])} 条消息")


if __name__ == '__main__':
    pytest.main(["-m", "P0", __file__])
