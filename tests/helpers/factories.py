"""
测试对象工厂
用于创建测试中使用的标准测试对象
"""

import random
from typing import Dict, Any, Optional
from src.game.player import Player
from src.game.enemy import StrawDummy
from src.ai.ai_interface import AIContext, AIMood


class PlayerFactory:
    """玩家对象工厂"""

    @staticmethod
    def create_basic_player(level: int = 1, attack_power: int = 10) -> Player:
        """创建基础玩家对象"""
        player = Player()
        player.level = level
        player.attack_power = attack_power
        return player

    @staticmethod
    def create_advanced_player(
        level: int = 5,
        attack_power: int = 25,
        combo: int = 0,
        max_combo: int = 20
    ) -> Player:
        """创建高级玩家对象"""
        player = Player()
        player.level = level
        player.attack_power = attack_power
        player.combo = combo
        player.max_combo = max_combo
        return player

    @staticmethod
    def create_max_level_player() -> Player:
        """创建满级玩家对象"""
        player = Player()
        player.level = 100
        player.attack_power = 500
        player.max_combo = 999
        player.weapon_tier = 5
        return player


class EnemyFactory:
    """敌人对象工厂"""

    @staticmethod
    def create_basic_enemy() -> StrawDummy:
        """创建基础敌人对象"""
        return StrawDummy()

    @staticmethod
    def create_low_hp_enemy() -> StrawDummy:
        """创建低血量敌人"""
        enemy = StrawDummy()
        enemy.hp = 20
        enemy.max_hp = 50
        return enemy

    @staticmethod
    def create_high_hp_enemy() -> StrawDummy:
        """创建高血量敌人"""
        enemy = StrawDummy()
        enemy.hp = 200
        enemy.max_hp = 500
        return enemy


class AIContextFactory:
    """AI上下文工厂"""

    @staticmethod
    def create_basic_context() -> AIContext:
        """创建基础AI上下文"""
        return AIContext(
            player_level=1,
            player_combo=0,
            player_power=10,
            enemy_hp_percent=1.0,
            recent_damage=0,
            ai_affinity=10,
            location="新手村",
            time_since_last_comment=5.0,
            player_stamina=100,
            is_level_up=False,
            is_crit_hit=False,
            attack_frequency=1.0,
            crit_frequency=0.05,
            combo_tendency=0.0,
            weapon_tier=1,
            total_coins=0
        )

    @staticmethod
    def create_high_combo_context(combo: int = 15) -> AIContext:
        """创建高连击AI上下文"""
        return AIContext(
            player_level=5,
            player_combo=combo,
            player_power=25,
            enemy_hp_percent=0.3,
            recent_damage=30,
            ai_affinity=60,
            location="竹林道场",
            time_since_last_comment=2.0,
            player_stamina=60,
            is_level_up=False,
            is_crit_hit=False,
            attack_frequency=2.5,
            crit_frequency=0.15,
            combo_tendency=0.8,
            weapon_tier=3,
            total_coins=200
        )

    @staticmethod
    def create_crit_hit_context() -> AIContext:
        """创建暴击AI上下文"""
        return AIContext(
            player_level=3,
            player_combo=5,
            player_power=15,
            enemy_hp_percent=0.7,
            recent_damage=50,
            ai_affinity=40,
            location="新手村",
            time_since_last_comment=3.0,
            player_stamina=80,
            is_level_up=False,
            is_crit_hit=True,
            attack_frequency=1.5,
            crit_frequency=0.20,
            combo_tendency=0.4,
            weapon_tier=2,
            total_coins=50
        )

    @staticmethod
    def create_level_up_context() -> AIContext:
        """创建升级AI上下文"""
        return AIContext(
            player_level=3,
            player_combo=0,
            player_power=20,
            enemy_hp_percent=0.5,
            recent_damage=25,
            ai_affinity=50,
            location="竹林道场",
            time_since_last_comment=1.0,
            player_stamina=100,
            is_level_up=True,
            is_crit_hit=False,
            attack_frequency=1.0,
            crit_frequency=0.1,
            combo_tendency=0.3,
            weapon_tier=2,
            total_coins=100
        )


class RandomDataFactory:
    """随机数据工厂"""

    @staticmethod
    def random_player_stats() -> Dict[str, Any]:
        """生成随机玩家统计数据"""
        return {
            'level': random.randint(1, 20),
            'attack_power': random.randint(5, 50),
            'combo': random.randint(0, 30),
            'stamina': random.randint(20, 100),
            'weapon_tier': random.randint(1, 5),
            'coins': random.randint(0, 1000),
            'location': random.choice(["新手村", "竹林道场", "血色战场", "无人废都"])
        }

    @staticmethod
    def random_ai_context() -> AIContext:
        """生成随机AI上下文"""
        stats = RandomDataFactory.random_player_stats()
        return AIContext(
            player_level=stats['level'],
            player_combo=stats['combo'],
            player_power=stats['attack_power'],
            enemy_hp_percent=random.uniform(0.1, 1.0),
            recent_damage=random.randint(5, 50),
            ai_affinity=random.randint(10, 80),
            location=stats['location'],
            time_since_last_comment=random.uniform(1.0, 10.0),
            player_stamina=stats['stamina'],
            is_level_up=random.choice([True, False]),
            is_crit_hit=random.choice([True, False]),
            attack_frequency=random.uniform(0.5, 3.0),
            crit_frequency=random.uniform(0.05, 0.25),
            combo_tendency=random.uniform(0.0, 1.0),
            weapon_tier=stats['weapon_tier'],
            total_coins=stats['coins']
        )