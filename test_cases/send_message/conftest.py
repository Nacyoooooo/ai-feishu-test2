import sys
from pathlib import Path

import pytest

from api.base_api import get_app_access_token
from api.employee.employee_api import EmployeeAPI
from api.group.group import GroupAPI

sys.path.append(str(Path(__file__).resolve().parent.parent))

app_id = 'cli_a8ee0c6a92e7501c'
app_secret = '9kbasiKxCyonOjJ2BCfXHcaKLKPA4fJT'
open_id = 'ou_1153fa978dae4500645ca3311c87631a'


@pytest.fixture(scope='session', autouse=False)
def before_and_after():
    # before
    yield
    # after

@pytest.fixture
def setup_group():
    """测试前置：创建群聊，并返回群聊ID"""
    token = get_app_access_token('cli_a7fbac1977651013', 'We9ckOfILpoxrUQcafMvJfIYJgrw5IQx')
    group_api = GroupAPI(token)
    create_resp = group_api.create_group(
        owner_id='',
        user_id_list=['ou_1153fa978dae4500645ca3311c87631a'],
        bot_id_list=[],
        set_bot_manager="true"
    )
    group_id = create_resp['data']["chat_id"]

    yield group_id

    group_api.delete_group(chat_id=group_id)

@pytest.fixture
def create_deleted_user():
    """创建已离职用户"""
    token = get_app_access_token(app_id, app_secret)
    employee_api = EmployeeAPI(token)
    create_employee_resp = employee_api.create_employee(employee_id_type="open_id", name="张三", mobile="13811112222")
    employee_id = create_employee_resp['data']['employee_id']
    employee_api.delete_employee("open_id", employee_id)
    yield employee_id
