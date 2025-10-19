"""
《是男人就砍一刀》游戏源代码包
"""

__version__ = "1.0.0"
__title__ = "是男人就砍一刀"
__author__ = "Game Developer"
__description__ = "一个解压向的砍击游戏，具有AI陪练系统"

# 导出主要模块
from . import game
from . import ai
from . import config

__all__ = ['game', 'ai', 'config', '__version__', '__title__', '__author__']