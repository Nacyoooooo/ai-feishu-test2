import os

from .config import ConfigLoader

# 获取项目根目录下的test_data文件夹路径
TEST_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_data'))

# 初始化配置加载器，全局唯一实例
config = ConfigLoader(TEST_DATA_DIR)

# 提供便捷访问方式
__all__ = ['config']

import logging


def setup_logger(name=__name__, level=logging.INFO):
    """配置模块级 logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger(name="test_cases")
