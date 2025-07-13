#!/usr/bin/env python3
"""
直接运行 example_3_parameter_anomaly_testing
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    print("="*60)
    print("运行 example_3_parameter_anomaly_testing")
    print("="*60)
    
    try:
        # 导入并运行示例函数
        from scripts.example_usage import example_3_parameter_anomaly_testing
        example_3_parameter_anomaly_testing()
        
        print("\n" + "="*60)
        print("✅ 示例执行完成")
        print("="*60)
        return 0
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保 scripts/example_usage.py 文件存在")
        return 1
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 