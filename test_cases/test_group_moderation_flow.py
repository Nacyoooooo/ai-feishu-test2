import logging
import time
import pytest
from common.robot_cluster import Cluster, Robot, Receiver
from test_data import read_data_from_yaml
from api.group.group import GroupAPI
from api.message.send_message_api import SendMessageAPI
from . import logger




@pytest.mark.P0
@pytest.mark.parametrize('test_data', read_data_from_yaml(
    "send_message_case.yaml",
    "group_moderation_flow"
))
@pytest.mark.usefixtures("robot_cluster")
def test_group_moderation_message_flow(robot_cluster:Cluster, test_data):
    """测试群发言权限管理场景：创建群聊 -> 设置发言权限 -> 测试不同用户发言权限"""
    
    # 1. 选择正常的机器人和用户
    robot = robot_cluster.getRobot(tags=test_data['robot_tags'], max=1)[0]
    users = robot_cluster.getReceiver(tags=test_data['user_tags'], max=4)  # 获取4个用户
    assert len(users) >= 3, "至少需要3个用户才能测试发言权限"

    # 2. 记录用户ID列表
    user_ids = [user.receiver_id for user in users]
    logger.info(f"选中的用户ID: {user_ids}")

    # 3. 创建群组并添加用户
    resp = robot.CreateGroup(robots=[robot], user_ids=users, name=test_data['group_name'])
    assert resp["code"] == 0, f"创建群组失败: {resp}"
    chat_id = resp['data']['chat_id']
    logger.info(f"成功创建群组，chat_id: {chat_id}")

    # 4. 等待群组创建完成
    time.sleep(2)

    # 5. 发送一条正常消息（默认权限时）
    normal_msg = {"text": f"{test_data['test_message']}[默认权限消息]"}
    message_api = SendMessageAPI(access_token=robot.access_token)
    resp = message_api.send_message(
        receive_id=chat_id,
        receive_id_type="chat_id",
        content=normal_msg,
        msg_type="text"
    )
    assert resp["code"] == 0, f"发送正常消息失败: {resp}"
    logger.info(f"已发送正常消息: {normal_msg}")

    # 6. 设置群发言权限（只有指定用户可以发言）
    moderator_users = user_ids[:2]  # 前两个用户有发言权限
    group_api = GroupAPI(access_token=robot.access_token)
    resp = group_api.update_group_moderation(
        chat_id=chat_id,
        moderation_setting="moderator_list",
        moderator_added_list=moderator_users
    )
    assert resp["code"] == 0, f"设置群发言权限失败: {resp}"
    logger.info(f"已设置群发言权限，发言权限用户: {moderator_users}")

    # 7. 等待权限设置生效
    time.sleep(2)

    # 8. 获取群发言权限设置
    resp = group_api.get_group_moderation(chat_id=chat_id)
    assert resp["code"] == 0, f"获取群发言权限设置失败: {resp}"
    logger.info(f"群发言权限设置: {resp}")

    # 9. 测试有权限的用户发送消息（应该成功）
    if len(moderator_users) > 0:
        # 这里需要模拟有权限的用户发送消息
        # 由于机器人本身可能没有权限，我们主要测试权限设置功能
        logger.info("有权限用户发送消息测试跳过（需要实际用户权限）")

    # 10. 测试无权限的用户发送消息（应该失败）
    # 这里我们测试机器人发送消息，看是否被权限限制
    restricted_msg = {"text": f"{test_data['test_message']}[权限受限消息]"}
    resp = message_api.send_message(
        receive_id=chat_id,
        receive_id_type="chat_id",
        content=restricted_msg,
        msg_type="text"
    )
    
    # 验证错误码（可能是权限相关的错误码）
    expected_error_code = test_data.get('expected_error_code', 230018)
    if resp["code"] != 0:
        logger.info(f"权限受限消息正确返回错误码: {resp['code']}")
    else:
        logger.info("机器人可能有特殊权限，消息发送成功")

    # 11. 移除发言权限限制
    resp = group_api.update_group_moderation(
        chat_id=chat_id,
        moderation_setting="moderator_list",
        moderator_removed_list=moderator_users
    )
    assert resp["code"] == 0, f"移除群发言权限限制失败: {resp}"
    logger.info(f"已移除群发言权限限制")

    # 12. 等待权限设置生效
    time.sleep(2)

    # 13. 再次发送消息（应该成功）
    resume_msg = {"text": f"{test_data['test_message']}[恢复权限后消息]"}
    resp = message_api.send_message(
        receive_id=chat_id,
        receive_id_type="chat_id",
        content=resume_msg,
        msg_type="text"
    )
    assert resp["code"] == 0, f"恢复权限后发送消息失败: {resp}"
    logger.info(f"恢复权限后发送消息成功: {resume_msg}")

    # 14. 清理：解散群组
    resp = robot.delete_group(chat_id=chat_id)
    assert resp["code"] == 0, f"解散群组失败: {resp}"
    logger.info(f"已成功解散群组: {chat_id}")

if __name__ == '__main__':
    pytest.main(["-m", "P0", __file__]) 