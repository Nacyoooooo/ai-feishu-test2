import pytest
import json
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List
from api.send_message_api import SendMessageAPI
from test_cases import config
from test_data import read_data_from_yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class TestSendMessage:
    @pytest.mark.parametrize('test_case',  read_data_from_yaml(
        "message_config.yaml",
        "test_messages"
    ))
    def test_send_message(self, test_case: Dict[str, Any]):
        # 初始化 SendMessageAPI 实例
        message_api = SendMessageAPI(test_case['access_token'])
        """测试发送消息API，增加详细日志和错误处理"""
        receive_id = test_case['receive_id']
        logger.info(f"开始测试发送消息: {test_case['content']}")
        logger.info(f"接收者ID: {receive_id}")
        
        try:
            response = message_api.send_message(
                receive_id=receive_id,
                content=test_case['content'],
                msg_type="text"
            )
            # 记录响应信息
            logger.info(f"API响应数据: {response}")            # 验证业务错误码            assert response.get("code") == test_case['expected_code'], f"消息发送失败: {response}"            assert response.get("msg") == "success", f"API返回非成功状态: {response.get('msg')}"            assert "message_id" in response["data"], "响应数据中缺少message_id"            assert response["data"]["message_id"], "message_id为空值"            response_data = response
            
            # # 断言状态码
            # assert response_data.get('code') == test_case['expected_code'], \
            #     f"消息发送失败，错误码: {response_data.get('code')}, 错误信息: {response_data.get('msg')}"
            # assert 'data' in response_data, "响应中缺少data字段"
            # assert 'message_id' in response_data['data'], "响应中缺少message_id字段"
            
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

if __name__ == '__main__':
    pytest.main(["-m", "P0", __file__])