from typing import Dict, Type, Optional, Any, List
from .ai_interface import AIBehaviorInterface, AILearningInterface, AIPersonalityInterface
import logging


class AIFactory:
    """AI实例工厂类 - 负责创建和管理不同类型的AI实例"""

    _ai_types: Dict[str, Type[AIBehaviorInterface]] = {}
    _ai_configs: Dict[str, Dict[str, Any]] = {}
    _ai_descriptions: Dict[str, str] = {}
    _logger = logging.getLogger(__name__)

    @classmethod
    def register_ai_type(cls,
                        name: str,
                        ai_class: Type[AIBehaviorInterface],
                        description: str = "",
                        default_config: Optional[Dict[str, Any]] = None) -> None:
        """
        注册AI类型

        Args:
            name: AI类型名称
            ai_class: AI类
            description: AI描述
            default_config: 默认配置
        """
        if not issubclass(ai_class, AIBehaviorInterface):
            raise ValueError(f"AI class {ai_class.__name__} must inherit from AIBehaviorInterface")

        cls._ai_types[name] = ai_class
        cls._ai_descriptions[name] = description
        cls._ai_configs[name] = default_config or {}

        cls._logger.info(f"Registered AI type: {name} -> {ai_class.__name__}")

    @classmethod
    def create_ai(cls,
                 ai_type: str,
                 config: Optional[Dict[str, Any]] = None,
                 **kwargs) -> AIBehaviorInterface:
        """
        创建AI实例

        Args:
            ai_type: AI类型名称
            config: 配置字典
            **kwargs: 额外参数

        Returns:
            AI实例
        """
        if ai_type not in cls._ai_types:
            available_types = list(cls._ai_types.keys())
            raise ValueError(f"Unknown AI type: {ai_type}. Available types: {available_types}")

        ai_class = cls._ai_types[ai_type]

        # 合并默认配置和用户配置
        final_config = cls._ai_configs[ai_type].copy()
        if config:
            final_config.update(config)

        # 添加额外参数
        final_config.update(kwargs)

        try:
            ai_instance = ai_class(**final_config)
            cls._logger.info(f"Created AI instance: {ai_type} with config: {final_config}")
            return ai_instance
        except Exception as e:
            cls._logger.error(f"Failed to create AI instance {ai_type}: {e}")
            raise

    @classmethod
    def get_available_types(cls) -> List[str]:
        """
        获取可用的AI类型列表

        Returns:
            AI类型名称列表
        """
        return list(cls._ai_types.keys())

    @classmethod
    def get_ai_description(cls, ai_type: str) -> str:
        """
        获取AI类型描述

        Args:
            ai_type: AI类型名称

        Returns:
            AI描述
        """
        return cls._ai_descriptions.get(ai_type, "No description available")

    @classmethod
    def get_ai_config(cls, ai_type: str) -> Dict[str, Any]:
        """
        获取AI类型默认配置

        Args:
            ai_type: AI类型名称

        Returns:
            默认配置字典
        """
        return cls._ai_configs.get(ai_type, {}).copy()

    @classmethod
    def is_ai_type_registered(cls, ai_type: str) -> bool:
        """
        检查AI类型是否已注册

        Args:
            ai_type: AI类型名称

        Returns:
            是否已注册
        """
        return ai_type in cls._ai_types

    @classmethod
    def unregister_ai_type(cls, ai_type: str) -> bool:
        """
        注销AI类型

        Args:
            ai_type: AI类型名称

        Returns:
            是否成功注销
        """
        if ai_type in cls._ai_types:
            del cls._ai_types[ai_type]
            del cls._ai_configs[ai_type]
            del cls._ai_descriptions[ai_type]
            cls._logger.info(f"Unregistered AI type: {ai_type}")
            return True
        return False

    @classmethod
    def create_ai_with_fallback(cls,
                               primary_type: str,
                               fallback_type: str = "rule_based",
                               config: Optional[Dict[str, Any]] = None,
                               **kwargs) -> AIBehaviorInterface:
        """
        创建AI实例，带降级机制

        Args:
            primary_type: 主要AI类型
            fallback_type: 降级AI类型
            config: 配置字典
            **kwargs: 额外参数

        Returns:
            AI实例
        """
        try:
            return cls.create_ai(primary_type, config, **kwargs)
        except Exception as e:
            cls._logger.warning(f"Failed to create primary AI {primary_type}, falling back to {fallback_type}: {e}")
            if primary_type != fallback_type:
                return cls.create_ai(fallback_type, config, **kwargs)
            else:
                raise

    @classmethod
    def get_ai_info(cls, ai_type: str) -> Dict[str, Any]:
        """
        获取AI类型完整信息

        Args:
            ai_type: AI类型名称

        Returns:
            AI信息字典
        """
        if ai_type not in cls._ai_types:
            return {}

        ai_class = cls._ai_types[ai_type]
        return {
            'name': ai_type,
            'class_name': ai_class.__name__,
            'description': cls._ai_descriptions[ai_type],
            'default_config': cls._ai_configs[ai_type].copy(),
            'supports_learning': issubclass(ai_class, AILearningInterface),
            'supports_personality': issubclass(ai_class, AIPersonalityInterface),
            'module': ai_class.__module__
        }

    @classmethod
    def list_all_ai_info(cls) -> Dict[str, Dict[str, Any]]:
        """
        列出所有AI类型信息

        Returns:
            所有AI信息字典
        """
        return {ai_type: cls.get_ai_info(ai_type) for ai_type in cls._ai_types.keys()}

    @classmethod
    def validate_ai_config(cls, ai_type: str, config: Dict[str, Any]) -> bool:
        """
        验证AI配置

        Args:
            ai_type: AI类型名称
            config: 配置字典

        Returns:
            配置是否有效
        """
        if ai_type not in cls._ai_types:
            return False

        # 基础验证：检查配置是否包含必要字段
        required_fields = []  # 可以在具体AI类中定义

        for field in required_fields:
            if field not in config:
                return False

        return True

    @classmethod
    def reset_factory(cls) -> None:
        """重置工厂（主要用于测试）"""
        cls._ai_types.clear()
        cls._ai_configs.clear()
        cls._ai_descriptions.clear()
        cls._logger.info("AI Factory reset")


class AILoader:
    """AI加载器 - 负责动态加载AI模块"""

    @staticmethod
    def load_ai_module(module_path: str) -> None:
        """
        动态加载AI模块

        Args:
            module_path: 模块路径
        """
        try:
            import importlib
            importlib.import_module(module_path)
            AIFactory._logger.info(f"Loaded AI module: {module_path}")
        except ImportError as e:
            AIFactory._logger.error(f"Failed to load AI module {module_path}: {e}")
            raise

    @staticmethod
    def auto_register_ai_modules() -> None:
        """自动注册所有AI模块"""
        # 自动加载并注册已知的AI模块
        try:
            # 加载DeepSeek AI模块
            from . import deepseek_ai
            AIFactory._logger.info("DeepSeek AI module loaded successfully")
        except ImportError as e:
            AIFactory._logger.warning(f"Failed to load DeepSeek AI module: {e}")

        try:
            # 加载LLM AI模块
            from . import llm_ai
            AIFactory._logger.info("LLM AI module loaded successfully")
        except ImportError as e:
            AIFactory._logger.warning(f"Failed to load LLM AI module: {e}")

        try:
            # 加载规则AI模块
            from . import rule_based_ai
            AIFactory._logger.info("Rule-based AI module loaded successfully")
        except ImportError as e:
            AIFactory._logger.warning(f"Failed to load rule-based AI module: {e}")


# 预注册一些基础AI类型占位符
def _register_builtin_ai_types():
    """注册内置AI类型（这里只是占位，实际AI类在其他文件中实现）"""
    pass


def initialize_ai_factory():
    """初始化AI工厂，注册所有可用的AI类型"""
    AIFactory._logger.info("Initializing AI Factory...")

    # 自动注册AI模块
    AILoader.auto_register_ai_modules()

    # 注册内置AI类型
    _register_builtin_ai_types()

    # 记录已注册的AI类型
    available_types = AIFactory.get_available_types()
    AIFactory._logger.info(f"Available AI types: {available_types}")

    return available_types


# 初始化时注册内置AI类型
_register_builtin_ai_types()

# 自动初始化（仅在模块导入时执行一次）
if not AIFactory._ai_types:
    initialize_ai_factory()