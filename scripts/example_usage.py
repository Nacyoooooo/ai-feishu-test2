#!/usr/bin/env python3
"""
使用示例：基于API接口文档进行测试用例扩展
展示如何使用测试生成器覆盖参数异常场景
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from generate_tests_from_api_doc import TestCaseGenerator

# 添加项目路径
sys.path.append(str(project_root))

from test_generators import (
    APIDocumentParser,
    ParameterAnomalyGenerator,
    ComprehensiveTestGenerator
)
from test_data import read_data_from_yaml

def example_1_generate_from_api_doc():
    """示例1：从API文档生成测试用例"""
    print("="*60)
    print("示例1：从API文档生成测试用例")
    print("="*60)
    
    # 创建测试生成器
    generator = TestCaseGenerator()
    
    # 假设我们有一个API文档文件
    api_doc_path = "api_docs/feishu_message_api.json"
    
    if Path(api_doc_path).exists():
        # 从API文档生成测试用例
        results = generator.generate_from_api_doc(
            api_doc_path=api_doc_path,
            output_dir="generated_tests",
            test_type="all"
        )
        
        print("生成结果:")
        for test_type, data in results.items():
            if isinstance(data, dict) and "count" in data:
                print(f"  {test_type}: {data['count']} 个测试用例")
    else:
        print(f"API文档文件不存在: {api_doc_path}")
        print("使用飞书特定测试用例生成...")
        example_2_feishu_specific_tests()

def example_2_feishu_specific_tests():
    """示例2：生成飞书特定测试用例"""
    print("\n" + "="*60)
    print("示例2：生成飞书特定测试用例")
    print("="*60)
    
    # 创建测试生成器
    generator = TestCaseGenerator()
    
    # 生成飞书特定测试用例
    results = generator.generate_feishu_specific_tests("generated_tests")
    
    print("生成结果:")
    for test_type, data in results.items():
        if isinstance(data, dict) and "count" in data:
            print(f"  {test_type}: {data['count']} 个测试用例")
            print(f"    文件: {data['file']}")
            print(f"    代码: {data['code_file']}")

def example_3_parameter_anomaly_testing():
    """示例3：参数异常测试"""
    print("\n" + "="*60)
    print("示例3：参数异常测试")
    print("="*60)
    
    # 加载参数异常测试用例
    anomaly_cases = read_data_from_yaml("parameter_anomaly_cases.yaml", "send_message_anomalies")
    
    print(f"加载了 {len(anomaly_cases)} 个参数异常测试用例")
    
    # 创建API客户端
    from api.message.send_message_api import SendMessageAPI
    from common.robot_common import get_app_access_token
    
    token = get_app_access_token("cli_a8ee0c6a92e7501c", "9kbasiKxCyonOjJ2BCfXHcaKLKPA4fJT")
    api_client = SendMessageAPI(access_token=token)
    
    # 执行参数异常测试
    test_results = []
    for case in anomaly_cases:  # 只测试前5个用例作为示例
        print(f"\n测试: {case['test_name']}")
        print(f"描述: {case['description']}")
        
        # 构造测试数据
        test_data = {
            "receive_id": "ou_adf4e416e22c12c5d4b40e347315f68c",
            "receive_id_type": "open_id",
            "content": {"text": "test"},
            "msg_type": "text"
        }
        
        # 设置异常参数
        if case['parameter_name'] in test_data:
            test_data[case['parameter_name']] = case['test_value']
        else:
            # 如果参数不在基础数据中，添加到content中
            test_data["content"] = {case['parameter_name']: case['test_value']}
        
        try:
            # 执行测试
            response = api_client.send_message(**test_data)
            actual_code = response.get('code')
            expected_code = case['expected_code']
            
            # 验证结果
            if actual_code == expected_code:
                print(f"  ✅ 通过 - 预期错误码: {expected_code}, 实际错误码: {actual_code}")
                test_results.append({"case": case['test_name'], "status": "PASS", "code": actual_code})
            else:
                print(f"  ❌ 失败 - 预期错误码: {expected_code}, 实际错误码: {actual_code}")
                test_results.append({"case": case['test_name'], "status": "FAIL", "expected": expected_code, "actual": actual_code})
                
        except Exception as e:
            print(f"  ⚠️  异常 - {e}")
            test_results.append({"case": case['test_name'], "status": "ERROR", "error": str(e)})
    
    # 打印测试结果统计
    print(f"\n测试结果统计:")
    total = len(test_results)
    passed = len([r for r in test_results if r['status'] == 'PASS'])
    failed = len([r for r in test_results if r['status'] == 'FAIL'])
    error = len([r for r in test_results if r['status'] == 'ERROR'])
    
    print(f"  总计: {total}")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print(f"  异常: {error}")
    print(f"  成功率: {passed/total*100:.1f}%")

def example_4_comprehensive_testing():
    """示例4：综合测试"""
    print("\n" + "="*60)
    print("示例4：综合测试")
    print("="*60)
    
    # 创建综合测试生成器
    generator = ComprehensiveTestGenerator()
    
    # 模拟API规范
    api_spec = {
        "paths": {
            "/open-apis/im/v1/messages": {
                "post": {
                    "parameters": [
                        {
                            "name": "receive_id",
                            "type": "string",
                            "required": True,
                            "description": "接收者ID"
                        },
                        {
                            "name": "receive_id_type",
                            "type": "string",
                            "required": True,
                            "description": "接收者ID类型"
                        }
                    ],
                    "requestBody": {
                        "properties": {
                            "content": {
                                "type": "object",
                                "description": "消息内容"
                            },
                            "msg_type": {
                                "type": "string",
                                "description": "消息类型"
                            }
                        }
                    }
                }
            }
        }
    }
    
    # 生成综合测试用例
    test_cases = generator.generate_comprehensive_tests(api_spec)
    
    print(f"生成了 {len(test_cases)} 个综合测试用例")
    
    # 按类别统计
    categories = {}
    for case in test_cases:
        category = case.category.value
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    print("\n测试用例分类统计:")
    for category, count in categories.items():
        print(f"  {category}: {count} 个")
    
    # 生成测试代码
    test_code = generator.generate_test_code(test_cases)
    
    # 保存测试代码
    output_file = "generated_tests/test_comprehensive_generated.py"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"\n测试代码已保存到: {output_file}")

def example_5_api_document_parsing():
    """示例5：API文档解析"""
    print("\n" + "="*60)
    print("示例5：API文档解析")
    print("="*60)
    
    # 创建API文档解析器
    parser = APIDocumentParser()
    
    # 模拟飞书API文档内容
    api_doc_content = """
# 飞书消息API文档

## POST /open-apis/im/v1/messages
发送消息

### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| receive_id | string | 是 | 接收者ID |
| receive_id_type | string | 是 | 接收者ID类型 |
| content | object | 是 | 消息内容 |
| msg_type | string | 是 | 消息类型 |
| uuid | string | 否 | 消息唯一标识 |

### 响应
- 200: 成功
- 400: 参数错误 (230001)
- 403: 权限不足 (230006)
- 429: 频率限制 (230020)
"""
    
    # 解析API文档
    endpoints = parser.parse_feishu_api_doc(api_doc_content)
    
    print(f"解析到 {len(endpoints)} 个API端点")
    
    for endpoint in endpoints:
        print(f"\n端点: {endpoint.method} {endpoint.path}")
        print(f"描述: {endpoint.description}")
        print(f"参数数量: {len(endpoint.parameters)}")
        
        for param in endpoint.parameters:
            print(f"  - {param.name}: {param.type} ({'必填' if param.required else '可选'})")
    
    # 生成API规范
    api_spec = parser.generate_api_spec(endpoints)
    
    # 保存API规范
    spec_file = "generated_tests/api_spec_parsed.json"
    Path(spec_file).parent.mkdir(parents=True, exist_ok=True)
    parser.save_api_spec(api_spec, spec_file)
    
    print(f"\nAPI规范已保存到: {spec_file}")

def main():
    """主函数"""
    print("基于API接口文档进行测试用例扩展示例")
    print("覆盖参数异常场景的测试用例生成")
    
    # 运行所有示例
    example_1_generate_from_api_doc()
    example_2_feishu_specific_tests()
    example_3_parameter_anomaly_testing()
    example_4_comprehensive_testing()
    example_5_api_document_parsing()
    
    print("\n" + "="*60)
    print("所有示例执行完成")
    print("="*60)
    
    print("\n使用说明:")
    print("1. 运行参数异常测试: python scripts/example_usage.py")
    print("2. 生成飞书特定测试: python generate_tests_from_api_doc.py --feishu-only")
    print("3. 从API文档生成测试: python generate_tests_from_api_doc.py --api-doc api_docs/feishu_api.json")
    print("4. 运行生成的测试: pytest generated_tests/")

if __name__ == "__main__":
    main() 