"""
测试用例生命周期管理器
基于当前项目的分层架构设计
"""

import time
import logging
import threading
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Callable
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class TestPhase(Enum):
    """测试阶段枚举"""
    PREPARATION = "preparation"      # 准备阶段
    EXECUTION = "execution"          # 执行阶段
    VALIDATION = "validation"        # 验证阶段
    CLEANUP = "cleanup"              # 清理阶段

class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "pending"              # 等待执行
    PREPARING = "preparing"          # 准备中
    EXECUTING = "executing"          # 执行中
    VALIDATING = "validating"        # 验证中
    CLEANING = "cleaning"            # 清理中
    COMPLETED = "completed"          # 已完成
    FAILED = "failed"                # 失败
    SKIPPED = "skipped"              # 跳过

@dataclass
class TestLifecycleConfig:
    """测试生命周期配置"""
    test_id: str
    phases: List[TestPhase]
    dependencies: Optional[List[str]] = None
    resources: Optional[Dict[str, Any]] = None
    cleanup_strategy: str = "immediate"  # immediate, deferred
    timeout: int = 300
    retry_count: int = 3
    skip_on_failure: bool = False

class TestLifecycleManager:
    """测试用例生命周期管理器"""
    
    def __init__(self):
        self.active_tests = {}           # 活跃测试跟踪
        self.test_configs = {}           # 测试配置
        self.execution_history = {}      # 执行历史
        self.lock = threading.Lock()     # 线程安全锁
        self.event_handlers = {}         # 事件处理器
        
        # 初始化默认事件处理器
        self._init_default_handlers()
    
    def _init_default_handlers(self):
        """初始化默认事件处理器"""
        self.event_handlers = {
            'test_started': [],
            'test_phase_completed': [],
            'test_failed': [],
            'test_completed': [],
            'resource_acquired': [],
            'resource_released': []
        }
    
    def register_test(self, test_id: str, config: TestLifecycleConfig):
        """注册测试用例"""
        with self.lock:
            self.test_configs[test_id] = config
            self.active_tests[test_id] = {
                'status': TestStatus.PENDING,
                'current_phase': None,
                'start_time': None,
                'end_time': None,
                'resources': set(),
                'error': None,
                'retry_count': 0
            }
            logger.info(f"注册测试用例: {test_id}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
            logger.info(f"注册事件处理器: {event_type}")
    
    def _emit_event(self, event_type: str, event_data: Dict):
        """触发事件"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    logger.error(f"事件处理器执行失败: {event_type}, 错误: {e}")
    
    def execute_test_lifecycle(self, test_id: str) -> bool:
        """执行完整的测试生命周期"""
        config = self.test_configs.get(test_id)
        if not config:
            logger.error(f"未找到测试配置: {test_id}")
            return False
        
        test_state = self.active_tests[test_id]
        test_state['start_time'] = time.time()
        test_state['status'] = TestStatus.PREPARING
        
        self._emit_event('test_started', {
            'test_id': test_id,
            'config': config,
            'start_time': test_state['start_time']
        })
        
        try:
            # 执行各个阶段
            for phase in config.phases:
                if not self._execute_phase(test_id, phase):
                    if config.skip_on_failure:
                        test_state['status'] = TestStatus.SKIPPED
                        logger.info(f"测试跳过: {test_id}")
                        return True
                    else:
                        test_state['status'] = TestStatus.FAILED
                        return False
            
            test_state['status'] = TestStatus.COMPLETED
            test_state['end_time'] = time.time()
            
            self._emit_event('test_completed', {
                'test_id': test_id,
                'duration': test_state['end_time'] - test_state['start_time']
            })
            
            return True
            
        except Exception as e:
            test_state['status'] = TestStatus.FAILED
            test_state['error'] = str(e)
            test_state['end_time'] = time.time()
            
            self._emit_event('test_failed', {
                'test_id': test_id,
                'error': str(e),
                'phase': test_state['current_phase']
            })
            
            logger.error(f"测试执行失败: {test_id}, 错误: {e}")
            return False
    
    def _execute_phase(self, test_id: str, phase: TestPhase) -> bool:
        """执行特定阶段"""
        config = self.test_configs[test_id]
        test_state = self.active_tests[test_id]
        
        test_state['current_phase'] = phase
        test_state['status'] = TestStatus(phase.value + "ing")
        
        logger.info(f"执行测试 {test_id} 的 {phase.value} 阶段")
        
        start_time = time.time()
        
        try:
            # 根据阶段执行相应的逻辑
            if phase == TestPhase.PREPARATION:
                result = self._prepare_test_environment(test_id)
            elif phase == TestPhase.EXECUTION:
                result = self._execute_test_logic(test_id)
            elif phase == TestPhase.VALIDATION:
                result = self._validate_test_results(test_id)
            elif phase == TestPhase.CLEANUP:
                result = self._cleanup_test_resources(test_id)
            else:
                result = True
            
            phase_duration = time.time() - start_time
            
            self._emit_event('test_phase_completed', {
                'test_id': test_id,
                'phase': phase.value,
                'duration': phase_duration,
                'success': result
            })
            
            return result
            
        except Exception as e:
            logger.error(f"阶段执行失败: {test_id}, 阶段: {phase.value}, 错误: {e}")
            return False
    
    def _prepare_test_environment(self, test_id: str) -> bool:
        """准备测试环境"""
        config = self.test_configs[test_id]
        test_state = self.active_tests[test_id]
        
        logger.info(f"准备测试环境: {test_id}")
        
        # 获取所需资源
        if config.resources:
            for resource_type, resource_config in config.resources.items():
                try:
                    # 这里可以集成现有的资源池
                    from .resource_pool import resource_pool
                    if resource_type == "token":
                        # 获取Token资源
                        app_id = resource_config.get('app_id')
                        app_secret = resource_config.get('app_secret')
                        if app_id and app_secret:
                            resource = resource_pool.get_token(app_id, app_secret)
                            test_state['resources'].add(f"token:{app_id}")
                            self._emit_event('resource_acquired', {
                                'test_id': test_id,
                                'resource_type': resource_type,
                                'resource': f"token:{app_id}"
                            })
                        else:
                            logger.error(f"Token配置不完整: {resource_config}")
                            return False
                    else:
                        logger.warning(f"未知资源类型: {resource_type}")
                        return False
                except Exception as e:
                    logger.error(f"获取资源失败: {resource_type}, 错误: {e}")
                    return False
        
        return True
    
    def _execute_test_logic(self, test_id: str) -> bool:
        """执行测试逻辑"""
        config = self.test_configs[test_id]
        test_state = self.active_tests[test_id]
        
        logger.info(f"执行测试逻辑: {test_id}")
        
        # 这里应该执行实际的测试函数
        # 由于我们使用装饰器模式，实际的测试逻辑会在装饰器的wrapper中执行
        # 所以这里只需要返回True，表示准备阶段完成
        return True
    
    def _validate_test_results(self, test_id: str) -> bool:
        """验证测试结果"""
        config = self.test_configs[test_id]
        test_state = self.active_tests[test_id]
        
        logger.info(f"验证测试结果: {test_id}")
        
        # 执行结果验证逻辑
        return True
    
    def _cleanup_test_resources(self, test_id: str) -> bool:
        """清理测试资源"""
        config = self.test_configs[test_id]
        test_state = self.active_tests[test_id]
        
        logger.info(f"清理测试资源: {test_id}")
        
        # 清理注册的资源
        if config.resources:
            for resource in test_state['resources']:
                try:
                    # 根据资源类型进行清理
                    if resource.startswith("token:"):
                        # Token资源不需要特殊清理，由资源池自动管理
                        logger.debug(f"Token资源无需手动清理: {resource}")
                    else:
                        logger.warning(f"未知资源类型，跳过清理: {resource}")
                    
                    self._emit_event('resource_released', {
                        'test_id': test_id,
                        'resource': resource
                    })
                except Exception as e:
                    logger.error(f"释放资源失败: {resource}, 错误: {e}")
        
        test_state['resources'].clear()
        return True
    
    @contextmanager
    def test_lifecycle_context(self, test_id: str):
        """测试生命周期上下文管理器"""
        try:
            yield self.execute_test_lifecycle(test_id)
        finally:
            # 确保清理工作被执行
            self._ensure_cleanup(test_id)
    
    def _ensure_cleanup(self, test_id: str):
        """确保清理工作被执行"""
        config = self.test_configs.get(test_id)
        if config and TestPhase.CLEANUP in config.phases:
            self._cleanup_test_resources(test_id)
    
    def get_test_status(self, test_id: str) -> Optional[TestStatus]:
        """获取测试状态"""
        test_state = self.active_tests.get(test_id)
        return test_state['status'] if test_state else None
    
    def get_test_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        with self.lock:
            summary = {
                'total_tests': len(self.active_tests),
                'completed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'pending_tests': 0,
                'test_details': {}
            }
            
            for test_id, test_state in self.active_tests.items():
                status = test_state['status']
                if status == TestStatus.COMPLETED:
                    summary['completed_tests'] += 1
                elif status == TestStatus.FAILED:
                    summary['failed_tests'] += 1
                elif status == TestStatus.SKIPPED:
                    summary['skipped_tests'] += 1
                elif status == TestStatus.PENDING:
                    summary['pending_tests'] += 1
                
                summary['test_details'][test_id] = {
                    'status': status.value,
                    'start_time': test_state['start_time'],
                    'end_time': test_state['end_time'],
                    'duration': test_state['end_time'] - test_state['start_time'] if test_state['end_time'] else None,
                    'error': test_state.get('error')
                }
            
            return summary

# 全局生命周期管理器实例
lifecycle_manager = TestLifecycleManager() 