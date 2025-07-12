import logging

import pytest

from common.robot_cluster import Cluster, Robot, Receiver
from test_data import read_data_from_yaml, get_test_file_path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# @pytest.fixture
# def setup_cluster():
#     """测试前置：加载机器人和接收者基础数据"""
#     # 加载机器人和接收者基础数据
#     robots_data = read_data_from_yaml("send_message_case.yaml", "robots")
#     receivers_data = read_data_from_yaml("send_message_case.yaml", "receivers")

#     robots = [Robot(app_id=r['app_id'], app_secret=r['app_secret'], tags=r['tags']) for r in robots_data]
#     receivers = [Receiver(receiver_id=r['receiver_id'], tags=r['tags'], receiver_id_type=r['receiver_id_type']) for r in receivers_data]
#     cluster = Cluster(robots=robots, receivers=receivers)

#     yield cluster

@pytest.mark.P0
@pytest.mark.parametrize('test_data', read_data_from_yaml(
    "send_message_case.yaml",
    "send_files"
))
@pytest.mark.usefixtures("cluster")
def test_complete_group_message_flow(cluster:Cluster, test_data):
    robot = cluster.getRobot(test_data['robotTags'])[0]
    file_path = get_test_file_path(test_data['filePath'])
    resp = robot.send_file(file_path, test_data['fileType'])
    assert resp['code'] == test_data['expected_code']
