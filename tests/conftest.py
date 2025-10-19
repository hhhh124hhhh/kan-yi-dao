"""
pytest配置文件
包含测试夹具和通用配置
"""

import sys
import os
import pytest
import pygame

# 导入统一的路径管理工具
from tests.helpers.path_utils import setup_test_paths, ensure_test_directories

# 导入环境变量加载
from dotenv import load_dotenv
load_dotenv()

# 在pytest启动时设置测试环境路径
setup_test_paths()

# 确保测试所需目录存在
ensure_test_directories()


@pytest.fixture(scope="session")
def init_pygame():
    """初始化pygame用于测试"""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_screen():
    """创建模拟的pygame屏幕"""
    pygame.init()
    screen = pygame.Surface((800, 600))
    yield screen
    pygame.quit()


@pytest.fixture
def test_ai_context():
    """创建测试用的AI上下文"""
    from src.ai.ai_interface import AIContext

    return AIContext(
        player_level=5,
        player_combo=10,
        player_power=15,
        enemy_hp_percent=0.6,
        recent_damage=20,
        ai_affinity=50,
        location="新手村",
        time_since_last_comment=3.0,
        player_stamina=80,
        is_level_up=False,
        is_crit_hit=True,
        attack_frequency=1.5,
        crit_frequency=0.12,
        combo_tendency=0.7,
        weapon_tier=2,
        total_coins=100
    )