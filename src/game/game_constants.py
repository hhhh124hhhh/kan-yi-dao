"""
游戏常量定义
定义游戏中使用的所有常量和标准属性名，确保命名一致性
"""

from enum import Enum
from typing import Dict, Any

# ==================== 游戏基础常量 ====================

class ScreenConstants:
    """屏幕相关常量"""
    DEFAULT_WIDTH = 800
    DEFAULT_HEIGHT = 600
    DEFAULT_FPS = 60

class GameConstants:
    """游戏基础常量"""
    DEFAULT_PLAYER_LEVEL = 1
    DEFAULT_ATTACK_POWER = 10
    DEFAULT_STAMINA = 100
    DEFAULT_MAX_STAMINA = 100
    DEFAULT_COINS = 0
    DEFAULT_COMBO = 0
    DEFAULT_WEAPON_TIER = 1

# ==================== 玩家属性标准命名 ====================

class PlayerAttributes:
    """玩家属性标准命名常量"""

    # 核心属性
    LEVEL = "level"
    EXP = "exp"
    NEXT_EXP = "next_exp"
    ATTACK_POWER = "attack_power"

    # 体力系统
    STAMINA = "stamina"
    MAX_STAMINA = "max_stamina"

    # 连击系统
    COMBO = "combo"
    MAX_COMBO = "max_combo"

    # 暴击系统
    CRIT_RATE = "crit_rate"
    CRIT_DAMAGE = "crit_damage"

    # 武器和金币
    WEAPON_TIER = "weapon_tier"
    COINS = "coins"

    # 位置和AI
    LOCATION = "location"
    AI_AFFINITY = "ai_affinity"

    # 状态标记
    JUST_LEVELED_UP = "just_leveled_up"

    # 时间相关
    LAST_ATTACK_TIME = "last_attack_time"
    ATTACK_COOLDOWN = "attack_cooldown"

# ==================== 敌人属性标准命名 ====================

class EnemyAttributes:
    """敌人属性标准命名常量"""

    # 生命系统
    HP = "hp"
    MAX_HP = "max_hp"
    LAST_DAMAGE = "last_damage"

    # 状态
    IS_ALIVE = "is_alive"

    # 统计数据
    TOTAL_DAMAGE_TAKEN = "total_damage_taken"
    HITS_RECEIVED = "hits_received"
    TIMES_DEFEATED = "times_defeated"

    # 缩放系统
    LEVEL_SCALING = "level_scaling"

# ==================== 游戏机制常量 ====================

class GameMechanics:
    """游戏机制相关常量"""

    # 体力系统
    STAMINA_ATTACK_COST = 10
    STAMINA_REGEN_RATE = 5
    STAMINA_REGEN_INTERVAL = 1.0
    STAMINA_WARNING_THRESHOLD = 30

    # 连击系统
    COMBO_RESET_TIME = 2.0
    COMBO_DAMAGE_MULTIPLIER = {
        0: 1.0,
        5: 1.1,
        10: 1.2,
        15: 1.3,
        20: 1.4
    }

    # 暴击系统
    DEFAULT_CRIT_RATE = 0.05
    DEFAULT_CRIT_DAMAGE_MULTIPLIER = 2.0

    # 升级系统
    EXP_BASE = 50
    EXP_MULTIPLIER = 1.2
    ATTACK_POWER_PER_LEVEL = 5

    # 武器系统
    WEAPON_ATTACK_POWER_BONUS = {
        1: 0,
        2: 3,
        3: 7,
        4: 12,
        5: 18
    }

    # 敌人缩放
    ENEMY_SCALING_PER_LEVEL = 0.2
    ENEMY_MAX_SCALING = 2.0

# ==================== 位置常量 ====================

class Locations:
    """游戏位置常量"""
    NEWBIE_VILLAGE = "新手村"
    BAMBOO_DOJO = "竹林道场"
    BLOODY_BATTLEFIELD = "血色战场"
    ABANDONED_CITY = "无人废都"

# ==================== UI相关常量 ====================

class UIConstants:
    """UI相关常量"""

    # 颜色定义
    COLORS = {
        "WHITE": (255, 255, 255),
        "BLACK": (0, 0, 0),
        "RED": (255, 0, 0),
        "GREEN": (0, 255, 0),
        "BLUE": (0, 0, 255),
        "YELLOW": (255, 255, 0),
        "ORANGE": (255, 165, 0),
        "PURPLE": (128, 0, 128),
        "CYAN": (0, 255, 255),
        "GRAY": (128, 128, 128),
        "LIGHT_GRAY": (200, 200, 200),
        "DARK_GRAY": (50, 50, 50)
    }

    # 字体大小
    FONT_SIZES = {
        "SMALL": 16,
        "MEDIUM": 24,
        "LARGE": 32,
        "HUGE": 48
    }

# ==================== 音效常量 ====================

class SoundConstants:
    """音效相关常量"""

    # 音效名称
    SOUNDS = {
        "SLASH": "slash",
        "ENEMY_HIT": "enemy_hit",
        "CRIT_HIT": "crit_hit",
        "LEVEL_UP": "level_up",
        "COIN": "coin",
        "STAMINA_LOW": "stamina_low",
        "COMBO_HIGH": "combo_high"
    }

    # 音量设置
    DEFAULT_VOLUME = 0.7
    MAX_VOLUME = 1.0

# ==================== 调试常量 ====================

class DebugConstants:
    """调试相关常量"""

    # 调试信息字段名
    DEBUG_FIELDS = {
        "FPS": "FPS",
        "DELTA_TIME": "DT",
        "PLAYER_LEVEL": "Player Level",
        "PLAYER_STAMINA": "Player Stamina",
        "ENEMY_HP": "Enemy HP",
        "COMBO": "Combo",
        "AI_MOOD": "AI Mood",
        "EFFECTS_COUNT": "Effects",
        "PARTICLES_COUNT": "Particles"
    }

# ==================== 属性验证映射 ====================

PLAYER_ATTRIBUTE_MAP = {
    "level": PlayerAttributes.LEVEL,
    "exp": PlayerAttributes.EXP,
    "next_exp": PlayerAttributes.NEXT_EXP,
    "attack_power": PlayerAttributes.ATTACK_POWER,
    "stamina": PlayerAttributes.STAMINA,
    "max_stamina": PlayerAttributes.MAX_STAMINA,
    "combo": PlayerAttributes.COMBO,
    "max_combo": PlayerAttributes.MAX_COMBO,
    "crit_rate": PlayerAttributes.CRIT_RATE,
    "crit_damage": PlayerAttributes.CRIT_DAMAGE,
    "weapon_tier": PlayerAttributes.WEAPON_TIER,
    "coins": PlayerAttributes.COINS,
    "location": PlayerAttributes.LOCATION,
    "ai_affinity": PlayerAttributes.AI_AFFINITY,
    "just_leveled_up": PlayerAttributes.JUST_LEVELED_UP,
    "last_attack_time": PlayerAttributes.LAST_ATTACK_TIME,
    "attack_cooldown": PlayerAttributes.ATTACK_COOLDOWN
}

ENEMY_ATTRIBUTE_MAP = {
    "hp": EnemyAttributes.HP,
    "max_hp": EnemyAttributes.MAX_HP,
    "last_damage": EnemyAttributes.LAST_DAMAGE,
    "is_alive": EnemyAttributes.IS_ALIVE,
    "total_damage_taken": EnemyAttributes.TOTAL_DAMAGE_TAKEN,
    "hits_received": EnemyAttributes.HITS_RECEIVED,
    "times_defeated": EnemyAttributes.TIMES_DEFEATED,
    "level_scaling": EnemyAttributes.LEVEL_SCALING
}

# ==================== 属性验证函数 ====================

def validate_player_attributes(obj: Any) -> Dict[str, Any]:
    """
    验证对象是否包含所有必需的玩家属性

    Args:
        obj: 要验证的对象

    Returns:
        包含验证结果的字典
    """
    missing_attrs = []
    for attr_name, attr_const in PLAYER_ATTRIBUTE_MAP.items():
        if not hasattr(obj, attr_name):
            missing_attrs.append(attr_name)

    return {
        "is_valid": len(missing_attrs) == 0,
        "missing_attributes": missing_attrs,
        "total_attributes": len(PLAYER_ATTRIBUTE_MAP)
    }

def validate_enemy_attributes(obj: Any) -> Dict[str, Any]:
    """
    验证对象是否包含所有必需的敌人属性

    Args:
        obj: 要验证的对象

    Returns:
        包含验证结果的字典
    """
    missing_attrs = []
    for attr_name, attr_const in ENEMY_ATTRIBUTE_MAP.items():
        if not hasattr(obj, attr_name):
            missing_attrs.append(attr_name)

    return {
        "is_valid": len(missing_attrs) == 0,
        "missing_attributes": missing_attrs,
        "total_attributes": len(ENEMY_ATTRIBUTE_MAP)
    }

def get_safe_attribute(obj: Any, attr_name: str, default: Any = None) -> Any:
    """
    安全地获取对象属性，支持标准属性名映射

    Args:
        obj: 目标对象
        attr_name: 属性名
        default: 默认值

    Returns:
        属性值或默认值
    """
    # 尝试直接获取
    if hasattr(obj, attr_name):
        return getattr(obj, attr_name)

    # 尝试通过映射获取
    for standard_name, mapped_name in PLAYER_ATTRIBUTE_MAP.items():
        if attr_name == mapped_name and hasattr(obj, standard_name):
            return getattr(obj, standard_name)

    for standard_name, mapped_name in ENEMY_ATTRIBUTE_MAP.items():
        if attr_name == mapped_name and hasattr(obj, standard_name):
            return getattr(obj, standard_name)

    return default