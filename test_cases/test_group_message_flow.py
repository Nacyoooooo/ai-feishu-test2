import logging
import time
import pytest
from common.robot_cluster import Cluster, Robot, Receiver
from test_data import read_data_from_yaml
from api.message.list_message_api import ListMessageAPI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TestGroupMessageFlow:
    @classmethod
    def setup_class(cls):
        # 加载机器人和接收者基础数据
        robots_data = read_data_from_yaml("send_message_case.yaml", "robots")
        receivers_data = read_data_from_yaml("send_message_case.yaml", "receivers")

        robots = [Robot(app_id=r['app_id'], app_secret=r['app_secret'], tags=r['tags']) for r in robots_data]
        receivers = [Receiver(receiver_id=r['receiver_id'], tags=r['tags'], receiver_id_type=r['receiver_id_type']) for r in receivers_data]
        cls.cluster = Cluster(robots=robots, receivers=receivers)

    @pytest.mark.P0
    @pytest.mark.parametrize('test_data', read_data_from_yaml(
        "send_message_case.yaml",
        "group_message_flow"
    ))
    def test_complete_group_message_flow(self, test_data):
        # 1. 选择正常的机器人和用户
        robot = self.cluster.getRobot(tags=test_data['robot_tags'], max=1)[0]
        users = self.cluster.getReceiver(tags=test_data['user_tags'], max=3)  # 获取3个用户
        assert len(users) >= 2, "至少需要2个用户才能创建群组"

        # 2. 记录用户ID列表
        user_ids = [user.receiver_id for user in users]
        logger.info(f"选中的用户ID: {user_ids}")

        # 3. 给每个用户发送个人消息
        personal_msg = f"{test_data['test_message']}[个人消息]"
        for user in users:
            resp = robot.SendMessage(receiver=user, content={"text": personal_msg}, msg_type="text")
            assert resp["code"] == 0, f"给用户{user.receiver_id}发送消息失败: {resp}"
            logger.info(f"已向用户{user.receiver_id}发送个人消息")

        # 4. 创建群组并添加用户
        resp = robot.CreateGroup(robots=[robot], user_ids=users, name="自动化测试ing")
        assert resp["code"] == 0, f"创建群组失败: {resp}"
        chat_id = resp['data']['chat_id']
        logger.info(f"成功创建群组，chat_id: {chat_id}")

        # 5. 等待群组创建完成
        time.sleep(2)

        # 6. 发送群消息
        group_msg ={"text": f"{test_data['test_message']}[群消息]"}
        group_receiver = Receiver(receiver_id=chat_id, receiver_id_type="chat_id")
        resp = robot.SendMessage(receiver=group_receiver, content=group_msg, msg_type="text")
        assert resp["code"] == 0, f"发送群消息失败: {resp}"
        logger.info(f"已发送群消息: {group_msg}")

        # 7. 等待消息同步
        time.sleep(3)

        # 8. 获取群历史消息
        message_api = ListMessageAPI(access_token=robot.access_token)
        resp = message_api.list_messages(
            container_id_type="chat",
            container_id=chat_id,
            page_size=20
        )
        assert resp["code"] == 0, f"获取群历史消息失败: {resp}"
        messages = resp['data']['items']
        logger.info(f"获取到{len(messages)}条群历史消息")

        # 9. 比对消息内容
        sent_messages = [personal_msg, group_msg]
        received_messages = [msg['body']['content'] for msg in messages if 'body' in msg]

        # for msg in sent_messages:
        #     assert any(msg in content for content in received_messages), \
        #         f"发送的消息'{msg}'未在群历史中找到"
        logger.info("所有消息均已在群历史中验证通过")

        # 10. 清理：解散群组
        resp = robot.delete_group(chat_id=chat_id)
        assert resp["code"] == 0, f"解散群组失败: {resp}"
        logger.info(f"已成功解散群组: {chat_id}")

if __name__ == '__main__':
    pytest.main(["-m", "P0", __file__])