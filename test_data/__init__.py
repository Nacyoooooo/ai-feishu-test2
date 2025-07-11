import yaml
import os

def read_data_from_yaml(file_path: str, key: str = None):

    """读取 YAML 文件，返回指定 Key 的数据"""
    # 获取当前文件所在目录（test_data目录）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接完整的文件路径
    full_path = os.path.join(current_dir, file_path)
    
    with open(full_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        return data.get(key) if key else data

def get_test_file_path(file_name: str) -> str:
    """获取test_data/file目录下测试文件的绝对路径
    Args:
        file_name: 文件名
    Returns:
        文件绝对路径
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_dir = os.path.join(current_dir, 'file')
    return os.path.join(file_dir, file_name)
