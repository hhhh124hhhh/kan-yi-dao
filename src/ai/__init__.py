"""
AI系统模块
包含AI接口、工厂、各种AI实现等
"""

# 导出AI相关类
from .ai_interface import (
    AIBehaviorInterface,
    AILearningInterface,
    AIPersonalityInterface,
    AIContext,
    AIResponse,
    AIMood
)
from .ai_factory import AIFactory, AILoader, initialize_ai_factory
from .ai_manager import AIManager

# 导入AI实现以触发注册
from . import rule_based_ai
from . import llm_ai
from . import deepseek_ai

__all__ = [
    'AIBehaviorInterface',
    'AILearningInterface',
    'AIPersonalityInterface',
    'AIContext',
    'AIResponse',
    'AIMood',
    'AIFactory',
    'AILoader',
    'initialize_ai_factory',
    'AIManager',
    'rule_based_ai',
    'llm_ai',
    'deepseek_ai'
]