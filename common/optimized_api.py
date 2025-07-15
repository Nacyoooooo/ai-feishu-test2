import requests
import time
import logging
import threading
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class OptimizedAPIClient:
    """优化的API客户端，包含重试机制和连接复用"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.session = requests.Session()
        self.timeout = timeout
        
        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        # 配置连接适配器
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'FeishuTestFramework/1.0'
        })
    
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, 
             json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """发送POST请求"""
        start_time = time.time()
        try:
            response = self.session.post(
                url, 
                data=data, 
                json=json, 
                timeout=self.timeout,
                **kwargs
            )
            elapsed = time.time() - start_time
            logger.debug(f"POST {url} - 状态码: {response.status_code}, 耗时: {elapsed:.2f}s")
            return response
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            logger.error(f"POST {url} 失败 - 耗时: {elapsed:.2f}s, 错误: {e}")
            raise
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """发送GET请求"""
        start_time = time.time()
        try:
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.timeout,
                **kwargs
            )
            elapsed = time.time() - start_time
            logger.debug(f"GET {url} - 状态码: {response.status_code}, 耗时: {elapsed:.2f}s")
            return response
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            logger.error(f"GET {url} 失败 - 耗时: {elapsed:.2f}s, 错误: {e}")
            raise
    
    def close(self):
        """关闭会话"""
        self.session.close()

class ThreadSafeMessageSender:
    """线程安全的消息发送器"""
    
    def __init__(self, robot, receiver):
        self.robot = robot
        self.receiver = receiver
        self.lock = threading.Lock()
        self.results = []
    
    def send_messages_concurrently(self, content: Dict[str, Any], 
                                 count: int, uuid, msg_type: str = "text") -> List[Dict[str, Any]]:
        """并发发送消息"""
        import threading
        
        def send_single():
            try:
                resp = self.robot.SendMessage(
                    receiver=self.receiver,
                    content=content,
                    msg_type=msg_type,
                    uuid=uuid
                )
                with self.lock:
                    self.results.append(resp)
            except Exception as e:
                logger.error(f"发送消息失败: {e}")
                with self.lock:
                    self.results.append({"code": -1, "error": str(e)})
        
        # 清空之前的结果
        self.results.clear()
        
        # 创建并启动线程
        threads = [threading.Thread(target=send_single) for _ in range(count)]
        for t in threads:
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        return self.results.copy() 