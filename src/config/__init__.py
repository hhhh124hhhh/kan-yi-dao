"""
配置模块
包含游戏配置、AI配置等
"""

# 导出配置（settings.py将重命名自config.py）
try:
    from .settings import *
except ImportError:
    # 如果settings.py不存在，尝试导入config.py
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from config import *  # 兼容旧版本

__all__ = [
    # 屏幕配置
    'SCREEN_WIDTH', 'SCREEN_HEIGHT', 'FPS', 'SCREEN_TITLE',
    'DEFAULT_FULLSCREEN', 'DEFAULT_VSYNC', 'DEFAULT_SHOW_FPS',

    # 游戏配置
    'BASE_ATTACK_POWER', 'ATTACK_POWER_GROWTH', 'BASE_STAMINA',
    'BASE_CRIT_RATE', 'BASE_CRIT_DAMAGE_MULTIPLIER',
    'EXP_BASE', 'EXP_MULTIPLIER', 'MAX_LEVEL',

    # AI配置
    'DEFAULT_AI_TYPE', 'ENABLE_AI_FALLBACK', 'AI_COMMENT_COOLDOWN',
    'DEEPSEEK_CONFIG', 'DEEPSEEK_AVAILABLE_MODELS',

    # 其他配置...
]