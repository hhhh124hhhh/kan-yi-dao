"""
测试Mock数据生成器
生成测试中使用的模拟数据
"""

import random
import json
from typing import Dict, List, Any
from src.ai.ai_interface import AIResponse, AIMood


class MockAIResponseGenerator:
    """Mock AI响应生成器"""

    @staticmethod
    def generate_excited_response() -> AIResponse:
        """生成兴奋的AI响应"""
        texts = [
            "太棒了！继续加油！💪",
            "连击起飞了！这手感太顶了！🔥",
            "这一刀太完美了！✨",
            "伤害爆炸！🎯",
            "完美的连击！⚡"
        ]

        return AIResponse(
            text=random.choice(texts),
            mood=AIMood.EXCITED,
            priority=random.randint(7, 10),
            cooldown_time=random.uniform(0.5, 1.5),
            affinity_change=random.randint(2, 3),
            learning_data={'source': 'mock'}
        )

    @staticmethod
    def generate_encouraging_response() -> AIResponse:
        """生成鼓励的AI响应"""
        texts = [
            "加油！你可以的！👏",
            "坚持就是胜利！💪",
            "继续努力，快成功了！",
            "别放弃，再试一次！",
            "相信自己，你能行的！"
        ]

        return AIResponse(
            text=random.choice(texts),
            mood=AIMood.ENCOURAGING,
            priority=random.randint(5, 7),
            cooldown_time=random.uniform(1.0, 2.0),
            affinity_change=random.randint(1, 2),
            learning_data={'source': 'mock'}
        )

    @staticmethod
    def generate_impressed_response() -> AIResponse:
        """生成印象深刻的AI响应"""
        texts = [
            "哇！太厉害了！😮",
            "这一刀太惊艳了！⭐",
            "难以置信的实力！🏆",
            "令人惊叹的技巧！✨",
            "你的成长让我惊讶！"
        ]

        return AIResponse(
            text=random.choice(texts),
            mood=AIMood.IMPRESSED,
            priority=random.randint(6, 8),
            cooldown_time=random.uniform(1.2, 2.0),
            affinity_change=random.randint(2, 3),
            learning_data={'source': 'mock'}
        )

    @staticmethod
    def generate_neutral_response() -> AIResponse:
        """生成中性的AI响应"""
        texts = [
            "继续练习。",
            "保持节奏。",
            "很好。",
            "继续努力。",
            "可以的。"
        ]

        return AIResponse(
            text=random.choice(texts),
            mood=AIMood.NEUTRAL,
            priority=random.randint(3, 5),
            cooldown_time=random.uniform(1.5, 2.5),
            affinity_change=0,
            learning_data={'source': 'mock'}
        )

    @staticmethod
    def generate_random_response() -> AIResponse:
        """生成随机的AI响应"""
        generators = [
            MockAIResponseGenerator.generate_excited_response,
            MockAIResponseGenerator.generate_encouraging_response,
            MockAIResponseGenerator.generate_impressed_response,
            MockAIResponseGenerator.generate_neutral_response
        ]

        return random.choice(generators)()


class MockGameDataGenerator:
    """Mock游戏数据生成器"""

    @staticmethod
    def generate_player_stats() -> Dict[str, Any]:
        """生成随机玩家统计数据"""
        return {
            'level': random.randint(1, 20),
            'exp': random.randint(0, 1000),
            'attack_power': random.randint(5, 50),
            'stamina': random.randint(20, 100),
            'combo': random.randint(0, 30),
            'max_combo': random.randint(10, 50),
            'crit_rate': random.uniform(0.05, 0.25),
            'weapon_tier': random.randint(1, 5),
            'coins': random.randint(0, 1000),
            'total_damage_dealt': random.randint(0, 10000),
            'total_hits': random.randint(0, 1000),
            'total_crits': random.randint(0, 100),
            'location': random.choice(["新手村", "竹林道场", "血色战场", "无人废都"]),
            'ai_affinity': random.randint(10, 80)
        }

    @staticmethod
    def generate_enemy_stats() -> Dict[str, Any]:
        """生成随机敌人统计数据"""
        return {
            'hp': random.randint(50, 500),
            'max_hp': random.randint(100, 1000),
            'total_damage_taken': random.randint(0, 5000),
            'hits_received': random.randint(0, 500),
            'times_defeated': random.randint(0, 100),
            'last_damage': random.randint(5, 50),
            'wobble_angle': random.uniform(0, 2 * 3.14159),
            'hit_animation_timer': random.randint(0, 30),
            'death_animation_timer': random.randint(0, 90)
        }

    @staticmethod
    def generate_game_session_data() -> Dict[str, Any]:
        """生成游戏会话统计数据"""
        return {
            'session_duration': random.uniform(60, 1800),  # 1-30分钟
            'total_attacks': random.randint(10, 500),
            'total_damage': random.randint(100, 10000),
            'max_combo': random.randint(0, 50),
            'total_ex_gained': random.randint(0, 1000),
            'enemies_defeated': random.randint(0, 50),
            'ai_responses': random.randint(20, 200),
            'session_ending': random.choice(["quit", "defeat", "level_up", "timeout"])
        }


class MockScenarioData:
    """测试场景数据"""

    HIGH_COMBO_SCENARIO = {
        'player': {'level': 10, 'combo': 25, 'attack_power': 30},
        'enemy': {'hp': 30, 'max_hp': 100},
        'expected_ai_mood': AIMood.EXCITED
    }

    CRIT_HIT_SCENARIO = {
        'player': {'level': 5, 'recent_damage': 60, 'is_crit_hit': True},
        'enemy': {'hp': 40, 'max_hp': 100},
        'expected_ai_mood': AIMood.IMPRESSED
    }

    LEVEL_UP_SCENARIO = {
        'player': {'level': 3, 'is_level_up': True},
        'enemy': {'hp': 20, 'max_hp': 100},
        'expected_ai_mood': AIMood.EXCITED
    }

    LOW_STAMINA_SCENARIO = {
        'player': {'stamina': 15},
        'enemy': {'hp': 80, 'max_hp': 100},
        'expected_ai_mood': AIMood.TIRED
    }

    ENEMY_LOW_HP_SCENARIO = {
        'player': {},
        'enemy': {'hp': 15, 'max_hp': 100, 'hp_percent': 0.15},
        'expected_ai_mood': AIMood.EXCITED
    }


def generate_test_json_file(filename: str, data: Dict[str, Any]) -> str:
    """生成测试用的JSON文件"""
    from tests.helpers.path_utils import get_test_data_path

    test_data_path = get_test_data_path()
    file_path = test_data_path / filename

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return str(file_path)


def cleanup_test_files():
    """清理测试生成的临时文件"""
    from tests.helpers.path_utils import get_temp_path

    temp_path = get_temp_path()
    if temp_path.exists():
        import shutil
        shutil.rmtree(temp_path)
        temp_path.mkdir(exist_ok=True)


def load_test_json_file(filename: str) -> Dict[str, Any]:
    """加载测试JSON文件"""
    from tests.helpers.path_utils import get_test_data_path

    test_data_path = get_test_data_path()
    file_path = test_data_path / filename

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)