"""
《是男人就砍一刀》游戏配置文件
包含所有游戏常量、配置项和平衡参数
"""

import os
from typing import Dict, List, Tuple, Any
from pathlib import Path


# =============================================================================
# 屏幕和显示配置
# =============================================================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
SCREEN_TITLE = "是男人就砍一刀"

# 支持的分辨率
RESOLUTIONS = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1366, 768),
    (1920, 1080)
]

# 显示设置
DEFAULT_FULLSCREEN = False
DEFAULT_VSYNC = True
DEFAULT_SHOW_FPS = False


# =============================================================================
# 游戏平衡配置
# =============================================================================

# 玩家基础属性
BASE_ATTACK_POWER = 10
ATTACK_POWER_GROWTH = 5
BASE_STAMINA = 100
BASE_STAMINA_COST = 10
BASE_CRIT_RATE = 0.05
BASE_CRIT_DAMAGE_MULTIPLIER = 2.0

# 升级配置
EXP_BASE = 50
EXP_MULTIPLIER = 1.2
MAX_LEVEL = 100

# 连击系统
COMBO_RESET_TIME = 2.0  # 2秒内无攻击重置连击
COMBO_DAMAGE_MULTIPLIER = 0.1  # 每10连击增加10%伤害

# 体力系统
STAMINA_REGEN_RATE = 5  # 每秒恢复体力
STAMINA_REGEN_INTERVAL = 1.0  # 恢复间隔（秒）

# 武器系统
WEAPON_TIERS = {
    1: {
        "name": "生锈的刀",
        "description": "一把普通的生锈刀具",
        "damage_multiplier": 1.0,
        "attack_cooldown": 0.5,
        "color": (150, 150, 150),
        "cost": 0
    },
    2: {
        "name": "闪光短刀",
        "description": "经过打磨的短刀，更加锋利",
        "damage_multiplier": 1.2,
        "attack_cooldown": 0.45,
        "color": (100, 150, 255),
        "cost": 50
    },
    3: {
        "name": "黑金战刃",
        "description": "精工打造的黑金战刃，威力十足",
        "damage_multiplier": 1.5,
        "attack_cooldown": 0.6,
        "color": (50, 50, 50),
        "cost": 150
    },
    4: {
        "name": "神性之刃",
        "description": "蕴含神性力量的传奇武器",
        "damage_multiplier": 2.0,
        "attack_cooldown": 0.4,
        "color": (255, 255, 255),
        "cost": 300
    },
    5: {
        "name": "AI融合刃",
        "description": "与AI意识融合的未来武器",
        "damage_multiplier": 3.0,
        "attack_cooldown": 0.3,
        "color": (255, 0, 255),
        "cost": 500
    }
}

# 敌人配置
ENEMY_TYPES = {
    "straw_dummy": {
        "name": "稻草人",
        "base_hp": 100,
        "name": "稻草人",
        "location": "新手村",
        "description": "新手村的训练目标"
    },
    "bamboo_dummy": {
        "name": "竹人偶",
        "base_hp": 150,
        "name": "竹人偶",
        "location": "竹林道场",
        "description": "竹林道场的练手目标"
    },
    "skeleton": {
        "name": "骷髅士",
        "base_hp": 200,
        "name": "骷髅士",
        "location": "血色战场",
        "description": "古代战场的守护者"
    },
    "golem": {
        "name": "钢铁傀儡",
        "base_hp": 300,
        "name": "钢铁傀儡",
        "location": "无人废都",
        "description": "废弃都市的机械守卫"
    },
    "ai_shadow": {
        "name": "AI之影",
        "base_hp": 500,
        "name": "AI之影",
        "location": "意识空间",
        "description": "AI意识的化身"
    }
}

# 敌人难度缩放
ENEMY_SCALING_INTERVAL = 3  # 每3级玩家，敌人变强
ENEMY_SCALING_FACTOR = 0.2  # 缩放增量

# 金币系统
COIN_PER_DAMAGE = 1  # 每点伤害获得1金币的几率
COIN_PER_LEVEL = 10  # 每级奖励金币
COIN_PER_DEFEAT = 20  # 击败敌人奖励金币


# =============================================================================
# AI系统配置
# =============================================================================

# 默认AI类型 (rule_based, llm_ai, deepseek_ai)
DEFAULT_AI_TYPE = os.getenv('DEFAULT_AI_TYPE', 'rule_based')

# AI降级机制
ENABLE_AI_FALLBACK = os.getenv('ENABLE_AI_FALLBACK', 'true').lower() == 'true'

# AI评论配置
AI_COMMENT_COOLDOWN = float(os.getenv('AI_COMMENT_COOLDOWN', '2.0'))  # 最小评论间隔（秒）
AI_COMMENT_FREQUENCY = 0.3  # 评论频率（0-1）

# =============================================================================
# DeepSeek AI配置
# =============================================================================

# DeepSeek API配置
DEEPSEEK_CONFIG = {
    'api_key': os.getenv('DEEPSEEK_API_KEY', ''),
    'base_url': os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com'),
    'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
    'temperature': float(os.getenv('DEEPSEEK_TEMPERATURE', '0.7')),
    'max_tokens': int(os.getenv('DEEPSEEK_MAX_TOKENS', '150')),
    'timeout': int(os.getenv('DEEPSEEK_TIMEOUT', '10')),
    'rate_limit': int(os.getenv('DEEPSEEK_RATE_LIMIT', '60')),
    'fallback_enabled': True
}

# DeepSeek可用模型
DEEPSEEK_AVAILABLE_MODELS = {
    'deepseek-chat': {
        'name': 'DeepSeek Chat',
        'description': '通用对话模型，适合游戏AI助手',
        'max_tokens': 4096,
        'cost_per_token': 0.0001
    },
    'deepseek-coder': {
        'name': 'DeepSeek Coder',
        'description': '代码专用模型，可用于技术向游戏助手',
        'max_tokens': 4096,
        'cost_per_token': 0.0001
    }
}

# DeepSeek游戏专用人格配置
DEEPSEEK_GAME_PERSONAS = {
    'veteran_swordsman': {
        'name': '剑术导师',
        'description': '经验丰富的剑术大师，深谙各种刀法精髓',
        'system_prompt_suffix': '你是一位严谨的剑术导师，关注技术细节和动作要领。'
    },
    'energetic_friend': {
        'name': '热血伙伴',
        'description': '充满激情的练刀伙伴，总是给玩家鼓励和支持',
        'system_prompt_suffix': '你是一个热血沸腾的游戏伙伴，用网络流行语和梗来活跃气氛。'
    },
    'wacky_commentator': {
        'name': '搞笑解说员',
        'description': '幽默风趣的解说员，让练刀过程充满欢乐',
        'system_prompt_suffix': '你是一个搞笑主播，擅长吐槽和讲段子，让游戏充满欢乐。'
    },
    'strategic_analyst': {
        'name': '战术分析师',
        'description': '冷静理性的分析师，专注于数据统计和战术优化',
        'system_prompt_suffix': '你是一位数据分析师，专注于游戏数据、策略优化和效率提升。'
    }
}

# DeepSeek成本控制配置
DEEPSEEK_COST_CONTROL = {
    'daily_token_limit': 10000,  # 每日token使用限制
    'cost_warning_threshold': 0.8,  # 成本警告阈值（80%）
    'auto_fallback_threshold': 0.95,  # 自动降级阈值（95%）
    'usage_reset_hour': 0,  # 使用量重置时间（小时，0表示午夜）
}

# =============================================================================
# 其他LLM API配置（兼容性）
# =============================================================================

# 智谱AI配置
ZHIPU_CONFIG = {
    'api_key': os.getenv('ZHIPU_API_KEY', ''),
    'base_url': os.getenv('ZHIPU_BASE_URL', 'https://open.bigmodel.cn/api/anthropic'),
    'model': os.getenv('ZHIPU_MODEL', 'claude-3-haiku-20240307'),
    'temperature': 0.8,
    'max_tokens': 150,
    'timeout': 10
}

# OpenAI配置
OPENAI_CONFIG = {
    'api_key': os.getenv('OPENAI_API_KEY', ''),
    'base_url': os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
    'model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
    'temperature': 0.7,
    'max_tokens': 150,
    'timeout': 10
}

# AI亲密度系统
AI_INITIAL_BOND = 10
AI_MAX_BOND = 100
AI_BOND_GAIN_RATE = 1
AI_BOND_LOSS_RATE = 1

# AI情绪状态
AI_MOODS = {
    "neutral": "中性",
    "excited": "兴奋",
    "tired": "疲倦",
    "serious": "严肃",
    "impressed": "印象深刻",
    "encouraging": "鼓励",
    "mocking": "嘲讽"
}

# AI角色类型
AI_PERSONALITY_TYPES = {
    "enthusiastic_coach": "热血教练",
    "wise_mentor": "智慧导师",
    "competitive_rival": "竞争对手",
    "cheerful_friend": "开朗朋友"
}

# AI学习参数
AI_LEARNING_ENABLED = True
AI_PATTERN_HISTORY_SIZE = 100
AI_ANALYSIS_INTERVAL = 5.0  # 分析间隔（秒）


# =============================================================================
# 特效系统配置
# =============================================================================

# 特效限制
MAX_EFFECTS_PER_TYPE = 50
MAX_PARTICLES = 200

# 屏幕震动
SCREEN_SHAKE_INTENSITY = {
    "normal": 3,
    "crit": 8,
    "level_up": 10,
    "defeat": 5
}

# 特效持续时间
EFFECT_DURATIONS = {
    "slash": 15,
    "crit": 60,
    "combo": 45,
    "level_up": 120,
    "damage_number": 40,
    "exp_gain": 60,
    "coin": 40,
    "stamina_warning": 90,
    "screen_shake": 15
}

# 粒子配置
PARTICLE_GRAVITY = 0.2
PARTICLE_LIFETIME_MIN = 20
PARTICLE_LIFETIME_MAX = 40


# =============================================================================
# 音效系统配置
# =============================================================================

# 音频设置
SAMPLE_RATE = 22050
BUFFER_SIZE = 1024
CHANNEL_COUNT = 8

# 默认音量
DEFAULT_MASTER_VOLUME = 0.7
DEFAULT_SFX_VOLUME = 0.8
DEFAULT_MUSIC_VOLUME = 0.6

# 音效间隔
SOUND_MIN_INTERVALS = {
    "slash": 0.05,
    "crit": 0.1,
    "level_up": 1.0,
    "combo": 0.2,
    "coin": 0.05,
    "stamina_low": 2.0,
    "enemy_hit": 0.1,
    "enemy_defeat": 1.0,
    "button_click": 0.05,
    "ui_hover": 0.02,
    "error": 0.5
}

# 3D音效设置
MAX_3D_DISTANCE = 500
VOLUME_ROLLOFF_DISTANCE = 200


# =============================================================================
# UI系统配置
# =============================================================================

# UI元素位置（相对于屏幕尺寸）
UI_POSITIONS = {
    "status_bar": (0, 0, 1.0, 0.067),  # x, y, width, height
    "ai_dialog": (0.125, 0.133, 0.75, 0.1),  # 中心位置
    "hp_bar": (0.437, 0.3, 0.125, 0.017),
    "bottom_tips": (0.25, 0.95, 0.5, 0.05)
}

# 颜色方案
COLORS = {
    # 基础颜色
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "GRAY": (128, 128, 128),
    "LIGHT_GRAY": (200, 200, 200),
    "DARK_GRAY": (64, 64, 64),

    # 主题颜色
    "PRIMARY": (255, 200, 100),
    "SECONDARY": (100, 150, 255),
    "ACCENT": (255, 215, 0),
    "SUCCESS": (100, 255, 100),
    "WARNING": (255, 200, 100),
    "DANGER": (255, 100, 100),

    # UI颜色
    "BACKGROUND": (40, 40, 40),
    "PANEL": (60, 60, 60),
    "BORDER": (100, 100, 100),
    "TEXT": (255, 255, 255),
    "HP_BAR": (200, 50, 50),
    "HP_BAR_BG": (100, 30, 30),
    "STAMINA_BAR": (100, 150, 255),
    "STAMINA_BAR_BG": (50, 75, 127),
    "EXP_BAR": (100, 200, 100),
    "EXP_BAR_BG": (50, 100, 50),
    "AI_DIALOG_BG": (50, 50, 50),
    "COMBO_TEXT": (255, 200, 100),

    # 武器颜色
    "WEAPON_COLORS": {
        1: (150, 150, 150),  # 灰色
        2: (100, 150, 255),  # 蓝色
        3: (50, 50, 50),     # 黑色
        4: (255, 255, 255),  # 白色
        5: (255, 0, 255)     # 紫色
    }
}

# 字体大小
FONT_SIZES = {
    "SMALL": 16,
    "MEDIUM": 24,
    "LARGE": 32,
    "HUGE": 48
}


# =============================================================================
# 存档系统配置
# =============================================================================

# 存档文件
SAVE_DIRECTORY = "saves"
SAVE_FILE_NAME = "savegame.json"
BACKUP_FILE_NAME = "savegame_backup.json"
SETTINGS_FILE_NAME = "settings.json"

# 自动保存
AUTO_SAVE_ENABLED = True
AUTO_SAVE_INTERVAL = 300  # 5分钟
MAX_AUTO_SAVES = 10

# 备份设置
MAX_BACKUPS = 5
BACKUP_ON_SAVE = True

# 存档版本
CURRENT_SAVE_VERSION = "1.0.0"
SUPPORTED_VERSIONS = ["1.0.0"]


# =============================================================================
# 调试和开发配置
# =============================================================================

# 调试模式
DEBUG_MODE = False
DEBUG_SHOW_COLLISION_BOXES = False
DEBUG_SHOW_FPS = False
DEBUG_LOG_AI_RESPONSES = False

# 开发者选项
DEV_SKIP_INTRO = False
DEV_UNLIMITED_RESOURCES = False
DEV_GOD_MODE = False
DEV_INSTANT_LEVEL_UP = False

# 日志配置
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_TO_FILE = True
LOG_FILE_NAME = "game.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB

# 性能监控
PERFORMANCE_MONITORING = False
TRACK_FRAME_TIME = False
MAX_FRAME_TIME = 50  # 毫秒


# =============================================================================
# 游戏内容配置
# =============================================================================

# 地点/场景
GAME_LOCATIONS = {
    "新手村": {
        "description": "初学者的训练场",
        "enemy_type": "straw_dummy",
        "background_color": (135, 206, 235),  # 天蓝色
        "unlock_level": 1
    },
    "竹林道场": {
        "description": "提升技巧的修行地",
        "enemy_type": "bamboo_dummy",
        "background_color": (34, 139, 34),  # 绿色
        "unlock_level": 3
    },
    "血色战场": {
        "description": "真正的战斗场所",
        "enemy_type": "skeleton",
        "background_color": (139, 0, 0),  # 深红色
        "unlock_level": 5
    },
    "无人废都": {
        "description": "机械文明的遗迹",
        "enemy_type": "golem",
        "background_color": (105, 105, 105),  # 灰色
        "unlock_level": 8
    },
    "意识空间": {
        "description": "AI意识的内心世界",
        "enemy_type": "ai_shadow",
        "background_color": (75, 0, 130),  # 靛色
        "unlock_level": 10
    }
}

# 场景解锁条件
LOCATION_UNLOCK_CONDITIONS = {
    "竹林道场": lambda level: level >= 3,
    "血色战场": lambda level: level >= 5,
    "无人废都": lambda level: level >= 8,
    "意识空间": lambda level: level >= 10
}


# =============================================================================
# 网络和API配置（如需要）
# =============================================================================

# LLM API配置
LLM_API_CONFIG = {
    "enabled": False,  # 默认禁用
    "provider": "anthropic",  # 或 "openai"
    "base_url": "https://open.bigmodel.cn/api/anthropic",
    "model": "claude-3-haiku-20240307",
    "timeout": 10,
    "max_tokens": 150,
    "temperature": 0.8
}

# 在线功能
ONLINE_FEATURES = {
    "leaderboard": False,
    "achievements": False,
    "cloud_save": False,
    "statistics_sharing": False
}


# =============================================================================
# 工具函数
# =============================================================================

def get_weapon_config(tier: int) -> Dict[str, Any]:
    """获取武器配置"""
    return WEAPON_TIERS.get(tier, WEAPON_TIERS[1])

def get_enemy_config(enemy_type: str) -> Dict[str, Any]:
    """获取敌人配置"""
    return ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["straw_dummy"])

def get_location_config(location: str) -> Dict[str, Any]:
    """获取地点配置"""
    return GAME_LOCATIONS.get(location, GAME_LOCATIONS["新手村"])

def is_location_unlocked(location: str, player_level: int) -> bool:
    """检查地点是否解锁"""
    condition = LOCATION_UNLOCK_CONDITIONS.get(location)
    if condition:
        return condition(player_level)
    return False

def calculate_required_exp(level: int) -> int:
    """计算升级所需经验"""
    return int(EXP_BASE * (EXP_MULTIPLIER ** (level - 1)))

def calculate_combo_multiplier(combo: int) -> float:
    """计算连击伤害倍率"""
    return 1.0 + (combo // 10) * COMBO_DAMAGE_MULTIPLIER

def calculate_enemy_hp(base_hp: int, player_level: int) -> int:
    """计算敌人血量（考虑玩家等级缩放）"""
    scaling_levels = player_level // ENEMY_SCALING_INTERVAL
    scaling_factor = 1.0 + (scaling_levels * ENEMY_SCALING_FACTOR)
    return int(base_hp * scaling_factor)


# =============================================================================
# 环境检测和配置加载
# =============================================================================

def load_environment_config():
    """从环境变量加载配置"""
    global DEBUG_MODE, ONLINE_FEATURES, LLM_API_CONFIG

    # 调试模式
    if os.getenv("GAME_DEBUG", "").lower() in ["true", "1", "yes"]:
        DEBUG_MODE = True

    # 在线功能
    if os.getenv("GAME_ONLINE", "").lower() in ["true", "1", "yes"]:
        ONLINE_FEATURES = {key: True for key in ONLINE_FEATURES.keys()}

    # LLM API配置
    if os.getenv("GAME_LLM_ENABLED", "").lower() in ["true", "1", "yes"]:
        LLM_API_CONFIG["enabled"] = True
        if os.getenv("GAME_LLM_API_KEY"):
            LLM_API_CONFIG["api_key"] = os.getenv("GAME_LLM_API_KEY")
        if os.getenv("GAME_LLM_BASE_URL"):
            LLM_API_CONFIG["base_url"] = os.getenv("GAME_LLM_BASE_URL")


def validate_config():
    """验证配置的有效性"""
    errors = []

    # 验证屏幕尺寸
    if SCREEN_WIDTH <= 0 or SCREEN_HEIGHT <= 0:
        errors.append("屏幕尺寸必须大于0")

    # 验证FPS
    if FPS <= 0:
        errors.append("FPS必须大于0")

    # 验证武器配置
    for tier, config in WEAPON_TIERS.items():
        if config["damage_multiplier"] <= 0:
            errors.append(f"武器等级{tier}的伤害倍率必须大于0")
        if config["attack_cooldown"] <= 0:
            errors.append(f"武器等级{tier}的攻击冷却必须大于0")

    # 验证敌人配置
    for enemy_type, config in ENEMY_TYPES.items():
        if config["base_hp"] <= 0:
            errors.append(f"敌人{enemy_type}的基础血量必须大于0")

    if errors:
        raise ValueError(f"配置验证失败:\n" + "\n".join(errors))


# 在模块加载时执行配置
load_environment_config()
validate_config()