import sys
from pathlib import Path

import pytest
import logging
from typing import Dict, Any
from test_data import read_data_from_yaml
from api.base_api import get_app_access_token
from api.employee.employee_api import EmployeeAPI
from api.group.group import GroupAPI

from common.robot_cluster import Cluster, Robot, Receiver
from common.resource_pool import resource_pool

sys.path.append(str(Path(__file__).resolve().parent.parent))

logger = logging.getLogger(__name__)

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
    group_api = GroupAPI(token)
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

@pytest.fixture(scope="session")
def robot_cluster():
    """会话级别的机器人集群，避免重复初始化"""
    logger.info("初始化机器人集群...")
    
    # 加载配置数据 - 从正确的文件读取
    robots_data = read_data_from_yaml("robots.yaml", "robots")
    receivers_data = read_data_from_yaml("robots.yaml", "receivers")
    
    # 添加错误检查
    if not robots_data:
        raise ValueError("无法从robots.yaml读取robots数据")
    if not receivers_data:
        raise ValueError("无法从robots.yaml读取receivers数据")
    
    # 创建机器人和接收者实例
    robots = [
        Robot(app_id=r['app_id'], app_secret=r['app_secret'], tags=r['tags']) 
        for r in robots_data
    ]
    receivers = [
        Receiver(receiver_id=r['receiver_id'], tags=r['tags'], 
                receiver_id_type=r['receiver_id_type']) 
        for r in receivers_data
    ]
    
    cluster = Cluster(robots=robots, receivers=receivers)
    logger.info(f"机器人集群初始化完成，机器人数量: {len(robots)}, 接收者数量: {len(receivers)}")
    
    yield cluster
    
    # 清理资源
    logger.info("清理机器人集群资源...")
    cleanup_groups(cluster)

@pytest.fixture(scope="session")
def test_data():
    """会话级别的测试数据加载"""
    logger.info("加载测试数据...")
    data = read_data_from_yaml("send_message_case.yaml")
    logger.info("测试数据加载完成")
    return data

@pytest.fixture(scope="function")
def performance_monitor():
    """性能监控夹具"""
    import time
    start_time = time.time()
    
    yield
    
    elapsed = time.time() - start_time
    logger.info(f"测试执行时间: {elapsed:.2f}秒")

def cleanup_groups(cluster: Cluster):
    """清理所有创建的群组"""
    try:
        registered_groups = resource_pool.get_registered_groups()
        if registered_groups:
            logger.info(f"开始清理 {len(registered_groups)} 个群组...")
            
            # 获取第一个机器人用于清理
            robots = cluster.getRobot(tags={"name": "1"}, max=1)
            if robots:
                robot = robots[0]
                for chat_id in registered_groups:
                    try:
                        resp = robot.delete_group(chat_id=chat_id)
                        if resp['code'] == 0:
                            logger.info(f"成功删除群组: {chat_id}")
                        else:
                            logger.warning(f"删除群组失败: {chat_id}, 错误码: {resp['code']}")
                    except Exception as e:
                        logger.error(f"删除群组异常: {chat_id}, 错误: {e}")
            
            resource_pool.clear_group_registry()
            logger.info("群组清理完成")
    except Exception as e:
        logger.error(f"清理群组时发生异常: {e}")

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_execution.log', encoding='utf-8')
        ]
    )

@pytest.fixture(scope="session", autouse=True)
def cleanup_session():
    """会话结束时的清理工作"""
    yield
    logger.info("会话结束，执行最终清理...")
    resource_pool.cleanup_expired_tokens()

