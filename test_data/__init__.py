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
