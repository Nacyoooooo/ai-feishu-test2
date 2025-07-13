import pytest

from common.robot_cluster import Cluster, Robot, Receiver
from test_data import read_data_from_yaml, get_test_file_path


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
    "send_files_to_user"
))
@pytest.mark.usefixtures("robot_cluster")
def test_complete_group_message_flow(robot_cluster:Cluster, test_data):
    """测试机器人不是资源所有者"""
    # 文件所有者
    fileOwnerRobot = robot_cluster.getRobot(tags=test_data['fileOwnerRobotTags'], max=1)[0]
    # 发送人
    sendfileRobot = robot_cluster.getRobot(tags=test_data['sendfileRobotTags'], max=1)[0]
    # 接收者
    user = robot_cluster.getReceiver(tags=test_data['receiverTags'], max=1)[0]  # 获取1个用户

    file_path = get_test_file_path(test_data['file'])

    resp = fileOwnerRobot.send_file(file_path, test_data['fileType'])

    # 必须上传成功
    assert resp['code']==0,f'发送文件失败,失败原因:{resp}'

    file_key=resp['data']['file_key']

    resp = sendfileRobot.SendMessage(
        receiver=user,
        msg_type=test_data['msg_type'],
        content={
            "file_key": file_key
        }
    )

    # 必须上传成功
    assert resp['code']==test_data['expected_code'],f'发送文件失败,失败原因:{resp}'

