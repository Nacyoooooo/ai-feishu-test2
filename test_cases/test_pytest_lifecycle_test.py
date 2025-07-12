"""
使用pytest fixture的生命周期管理测试
避免与pytest系统的冲突
"""

import pytest
import logging
from common.pytest_lifecycle_fixtures import (
    lifecycle_manager,
    test_lifecycle_context,
    create_lifecycle_config,
    performance_monitor,
    retry_fixture,
    preparation_phase,
    execution_phase,
    validation_phase,
    cleanup_phase
)
from common.test_lifecycle_manager import TestPhase
from common.robot_cluster import Cluster

logger = logging.getLogger(__name__)

def test_lifecycle_with_fixtures(
    robot_cluster: Cluster,
    lifecycle_manager,
    test_lifecycle_context,
    performance_monitor
):
    """
    使用pytest fixture的生命周期测试
    """
    logger.info("开始执行pytest fixture生命周期测试")
    
    # 创建生命周期配置
    config = create_lifecycle_config(
        test_id="pytest_lifecycle_test",
        phases=[TestPhase.PREPARATION, TestPhase.EXECUTION, TestPhase.VALIDATION],
        timeout=60,
        retry_count=1
    )
    
    # 使用生命周期上下文
    with test_lifecycle_context("pytest_lifecycle_test", config) as success:
        if success:
            # 准备阶段
            @preparation_phase
            def prepare_test_environment():
                logger.info("准备阶段：获取机器人实例")
                robots = robot_cluster.getRobot(tags={"name": "1"}, max=1)
                assert len(robots) > 0, "无法获取机器人实例"
                return robots[0]
            
            # 执行阶段
            @execution_phase
            def execute_test_logic(robot):
                logger.info("执行阶段：验证机器人实例")
                assert robot.app_id is not None, "机器人app_id不能为空"
                assert robot.access_token is not None, "机器人access_token不能为空"
                return robot
            
            # 验证阶段
            @validation_phase
            def validate_test_results(robot):
                logger.info("验证阶段：检查机器人配置")
                assert hasattr(robot, 'SendMessage'), "机器人缺少SendMessage方法"
                assert hasattr(robot, 'CreateGroup'), "机器人缺少CreateGroup方法"
                return True
            
            # 执行测试逻辑
            robot = prepare_test_environment()
            robot = execute_test_logic(robot)
            validate_test_results(robot)
            
            logger.info("pytest fixture生命周期测试执行完成")
            return True
        else:
            logger.error("生命周期执行失败")
            raise Exception("生命周期执行失败")

@pytest.mark.P0
def test_basic_functionality_with_retry(
    robot_cluster: Cluster,
    retry_fixture
):
    """
    使用重试机制的基础功能测试
    """
    logger.info("开始执行带重试机制的基础功能测试")
    
    def test_logic():
        """测试逻辑"""
        robots = robot_cluster.getRobot(tags={"name": "1"}, max=1)
        assert len(robots) > 0, "无法获取机器人实例"
        
        receivers = robot_cluster.getReceiver(tags={"name": "chenzhihao"}, max=1)
        assert len(receivers) > 0, "无法获取接收者实例"
        
        return True
    
    # 使用重试机制
    result = retry_fixture(test_logic, max_retries=2, delay=0.5)
    
    logger.info("带重试机制的基础功能测试执行完成")
    return result

@pytest.mark.P1
def test_simple_validation():
    """
    简单验证测试
    """
    logger.info("开始执行简单验证测试")
    
    @preparation_phase
    def prepare():
        logger.info("准备阶段：初始化测试数据")
        return {"test_data": "sample"}
    
    @execution_phase
    def execute(test_data):
        logger.info("执行阶段：处理测试数据")
        assert test_data["test_data"] == "sample"
        return test_data
    
    @validation_phase
    def validate(result):
        logger.info("验证阶段：验证结果")
        assert result["test_data"] == "sample"
        return True
    
    @cleanup_phase
    def cleanup():
        logger.info("清理阶段：清理测试数据")
        logger.info("测试数据清理完成")
    
    # 执行测试逻辑
    test_data = prepare()
    result = execute(test_data)
    validate(result)
    cleanup()
    
    logger.info("简单验证测试执行完成")
    return True

# 事件监控示例
def test_lifecycle_events(lifecycle_manager):
    """
    测试生命周期事件
    """
    logger.info("开始测试生命周期事件")
    
    # 定义事件处理器
    def on_test_completed(event_data):
        logger.info(f"测试完成事件: {event_data}")
    
    def on_test_failed(event_data):
        logger.error(f"测试失败事件: {event_data}")
    
    # 注册事件处理器
    lifecycle_manager.register_event_handler("test_completed", on_test_completed)
    lifecycle_manager.register_event_handler("test_failed", on_test_failed)
    
    # 创建测试配置
    config = create_lifecycle_config(
        test_id="event_test",
        phases=[TestPhase.PREPARATION, TestPhase.EXECUTION],
        timeout=30
    )
    
    # 注册测试
    lifecycle_manager.register_test("event_test", config)
    
    # 执行测试生命周期
    success = lifecycle_manager.execute_test_lifecycle("event_test")
    
    logger.info(f"生命周期事件测试完成，结果: {success}")
    return success 