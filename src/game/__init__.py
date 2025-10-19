"""
游戏核心模块
包含玩家、敌人、特效、UI等游戏核心功能
"""

# 导出核心类
from .player import Player
from .enemy import StrawDummy
from .effects import EffectManager
from .ui import UIManager
from .sound_manager import SoundManager
from .data_manager import DataManager
from .main import Game

__all__ = [
    'Player',
    'StrawDummy',
    'EffectManager',
    'UIManager',
    'SoundManager',
    'DataManager',
    'Game'
]