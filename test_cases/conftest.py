import sys
from pathlib import Path

import pytest
from test_data import read_data_from_yaml
from api.base_api import get_app_access_token
from api.employee.employee_api import EmployeeAPI
from api.group.group import GroupAPI

from common.robot_cluster import Cluster,Receiver,Robot

sys.path.append(str(Path(__file__).resolve().parent.parent))

app_id = 'cli_a8ee0c6a92e7501c'
app_secret = '9kbasiKxCyonOjJ2BCfXHcaKLKPA4fJT'
open_id = 'ou_adf4e416e22c12c5d4b40e347315f68c'

@pytest.fixture(scope='session', autouse=False)
def before_and_after():
    # before
    yield
    # after

@pytest.fixture
def setup_group():
    """测试前置：创建群聊，并返回群聊ID"""
    token = get_app_access_token(app_id, app_secret)
    group_api = GroupAPI(token['tenant_access_token'])
    create_resp = group_api.create_group(
        owner_id=open_id,
        user_id_list=[open_id],
        bot_id_list=[app_id],
        set_bot_manager="true"
    )
    group_id = create_resp['data']["chat_id"]

    yield group_id

    group_api.delete_group(chat_id=group_id)

@pytest.fixture
def create_user():
    """创建用户"""
    token = get_app_access_token(app_id, app_secret)
    employee_api = EmployeeAPI(token)
    create_employee_resp = employee_api.create_employee(employee_id_type="open_id", name="张三", mobile="13811112222")
    employee_id = create_employee_resp['data']['employee_id']
    yield employee_id
    employee_api.delete_employee("open_id", employee_id)

@pytest.fixture
def cluster():
    """创建集群"""
    robotsData = read_data_from_yaml(
    "robots.yaml",
    "robots"
    )
    receiversData = read_data_from_yaml(
    "robots.yaml",
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
    cluster = Cluster(robots=robots, receivers=receivers)

    yield cluster

