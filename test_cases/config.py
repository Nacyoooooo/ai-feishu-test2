import yaml
import os
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.config: Dict[str, Any] = {}
        self.load_all_configs()
    
    def load_all_configs(self) -> None:
        """加载配置目录下所有YAML文件"""
        if not os.path.exists(self.config_dir):
            raise FileNotFoundError(f"配置目录不存在: {self.config_dir}")
        
        for filename in os.listdir(self.config_dir):
            if filename.endswith(('.yaml', '.yml')):
                file_path = os.path.join(self.config_dir, filename)
                self._load_single_file(file_path, filename)
    
    def _load_single_file(self, file_path: str, filename: str) -> None:
        """加载单个YAML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                if config_data:
                    # 使用文件名(不含扩展名)作为配置键
                    config_key = os.path.splitext(filename)[0]
                    self.config[config_key] = config_data
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败 {file_path}: {str(e)}") from e
    
    def __getitem__(self, key: str) -> Any:
        return self.config[key]
    
    def __getattr__(self, key: str) -> Any:
        return self.config.get(key)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.config.copy()