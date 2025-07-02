import os
from .config import ConfigLoader

# 获取项目根目录下的test_data文件夹路径
TEST_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_data'))

# 初始化配置加载器，全局唯一实例
config = ConfigLoader(TEST_DATA_DIR)

# 提供便捷访问方式
__all__ = ['config']