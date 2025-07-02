import pytest
import json
import logging
from typing import Dict, Any, List
from api.send_message_api import SendMessageAPI
from test_cases import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 移除read_test_data()函数及相关代码

@pytest.fixture(scope="function")
def message_api():
    access_token = config.message_config.get("access_token")
    if not access_token:
        pytest.fail("access_token not found in test_data/message_config.yaml")
    api = SendMessageAPI()
    api.token = access_token
    return api

# 验证测试数据结构
if 'message_config' not in config.config:
    pytest.fail("test_data目录下未找到message_config.yaml文件")

message_config = config.message_config
required_keys = ['receive_id', 'test_messages', 'access_token']
for key in required_keys:
    if key not in message_config:
        pytest.fail(f"message_config缺少必要字段: {key}")

if not isinstance(message_config['test_messages'], list):
    pytest.fail("test_messages必须是列表类型")

for i, case in enumerate(message_config['test_messages']):
    if not isinstance(case, dict) or 'content' not in case or 'expected_code' not in case:
        pytest.fail(f"测试用例 {i} 格式不正确，必须包含'content'和'expected_code'字段")

@pytest.mark.parametrize('test_case', config.message_config['test_messages'])
def test_send_message(message_api: SendMessageAPI, test_case: Dict[str, Any]):
    """测试发送消息API，增加详细日志和错误处理"""
    receive_id = config.message_config['receive_id']
    logger.info(f"开始测试发送消息: {test_case['content']}")
    logger.info(f"接收者ID: {receive_id}")
    
    try:
        response = message_api.send_message(
            receive_id=receive_id,
            content=test_case['content'],
            msg_type="text"
        )
        
        # 记录响应信息
        logger.info(f"API响应数据: {response}")
        # 验证业务错误码
        assert response.get("code") == test_case['expected_code'], f"消息发送失败: {response}"
        assert response.get("msg") == "success", f"API返回非成功状态: {response.get('msg')}"
        assert "message_id" in response["data"], "响应数据中缺少message_id"
        assert response["data"]["message_id"], "message_id为空值"
        response_data = response
        
        # 断言状态码
        assert response_data.get('code') == test_case['expected_code'], \
            f"消息发送失败，错误码: {response_data.get('code')}, 错误信息: {response_data.get('msg')}"
        assert 'data' in response_data, "响应中缺少data字段"
        assert 'message_id' in response_data['data'], "响应中缺少message_id字段"
        
        logger.info(f"测试用例通过: {test_case['content']}")
        
    except json.JSONDecodeError:
        logger.error(f"响应内容不是有效的JSON: {response.text}")
        raise
    except AssertionError as e:
        logger.error(f"断言失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        raise