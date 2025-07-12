import threading
import time
import logging
from typing import Dict, List, Optional
from .robot_common import get_app_access_token

logger = logging.getLogger(__name__)

class ResourcePool:
    """资源池管理器，负责Token缓存和资源清理"""
    
    def __init__(self):
        self.token_cache: Dict[str, Dict] = {}
        self.group_registry: List[str] = []
        self.lock = threading.Lock()
        self.token_expiry = 7200  # Token有效期2小时
    
    def get_token(self, app_id: str, app_secret: str) -> str:
        """获取Token，带缓存机制"""
        with self.lock:
            current_time = time.time()
            
            # 检查缓存中是否有有效的Token
            if app_id in self.token_cache:
                cached_data = self.token_cache[app_id]
                if current_time - cached_data['timestamp'] < self.token_expiry:
                    logger.debug(f"使用缓存的Token: {app_id}")
                    return cached_data['token']
            
            # 获取新Token
            try:
                token = get_app_access_token(app_id, app_secret)
                self.token_cache[app_id] = {
                    'token': token,
                    'timestamp': current_time
                }
                logger.info(f"获取新Token成功: {app_id}")
                return token
            except Exception as e:
                logger.error(f"获取Token失败: {app_id}, 错误: {e}")
                raise
    
    def register_group(self, chat_id: str) -> None:
        """注册创建的群组，用于后续清理"""
        with self.lock:
            if chat_id not in self.group_registry:
                self.group_registry.append(chat_id)
                logger.info(f"注册群组: {chat_id}")
    
    def get_registered_groups(self) -> List[str]:
        """获取所有注册的群组"""
        with self.lock:
            return self.group_registry.copy()
    
    def clear_group_registry(self) -> None:
        """清空群组注册表"""
        with self.lock:
            self.group_registry.clear()
            logger.info("清空群组注册表")
    
    def cleanup_expired_tokens(self) -> None:
        """清理过期的Token缓存"""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, data in self.token_cache.items()
                if current_time - data['timestamp'] >= self.token_expiry
            ]
            for key in expired_keys:
                del self.token_cache[key]
            if expired_keys:
                logger.info(f"清理过期Token: {expired_keys}")

# 全局资源池实例
resource_pool = ResourcePool() 