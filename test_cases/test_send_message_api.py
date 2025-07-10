import logging

import pytest

from common.robot_cluster import Cluster, Robot, Receiver
# from api.message.send_message_api import SendMessageAPI
from test_data import read_data_from_yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TestSend:

    @classmethod
    def setup_class(cls):
        robotsData = read_data_from_yaml(
        "send_message_case.yaml",
        "robots"
        )
        receiversData = read_data_from_yaml(
        "send_message_case.yaml",
        "receivers"
        )
        robots = []
        for robot in robotsData:
            robot = Robot(app_id=robot['app_id'], app_secret=robot['app_secret'], tags=robot['tags'])
            robots.append(robot)
        receivers = []
        for receiver in receiversData:
            receiver = Receiver(receiver_id=receiver['receiver_id'], tags=receiver['tags'],receiver_id_type=receiver['receiver_id_type'])
            receivers.append(receiver)
        
        # 创建集群
        cls.cluster = Cluster(robots=robots, receivers=receivers)

    @pytest.mark.P0
    @pytest.mark.parametrize('send_message_data', read_data_from_yaml(
        "send_message_case.yaml",
        "send_message"
    ))
    def test_send_message2(self, send_message_data):
        """测试发送消息"""
        receivers = self.cluster.getReceiver(tags=send_message_data['receiverTags'],max=1)
        robots = self.cluster.getRobot(tags=send_message_data['robotTags'],max=1)
        resp = robots[0].SendMessage(receivers[0],content=send_message_data['content'],msg_type=send_message_data['msg_type'])
        assert resp["code"] == send_message_data["expected_code"], \
            logging.info(f"和预期结果不对应，预期结果：{send_message_data['expected_code']}，实际结果：{resp[0]['code']}")
    
    @pytest.mark.P0
    @pytest.mark.parametrize('group', read_data_from_yaml(
        "send_message_case.yaml",
        "group"
    ))
    def test_create_group(self, group):
        """创建群组"""
        receivers = self.cluster.getReceiver(tags=group['receiverTags'],max=-1)
        robots = self.cluster.getRobot(tags=group['robotTags'],max=-1)
        resp = robots[0].CreateGroup(robots=robots,user_ids=receivers)
        assert resp['code'] ==0
        assert resp['data']['chat_id'] is not None
        chat_id = resp['data']['chat_id']
        """解散群组"""
        resp2 = robots[0].delete_group(chat_id=chat_id)
        assert resp2['code'] ==0


if __name__ == '__main__':
    pytest.main(["-m", "P0", __file__])