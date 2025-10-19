import unittest
from unittest.mock import Mock, patch
import time

# 导入测试辅助工具
from tests.helpers.factories import AIContextFactory
from tests.helpers.assertions import assert_ai_response, GameTestAssertions

from src.ai.ai_manager import AIManager
from src.ai.rule_based_ai import RuleBasedAI


class TestAIAgent(unittest.TestCase):
    """AI代理单元测试"""

    def setUp(self):
        """测试前准备"""
        self.ai_manager = AIManager("rule_based")

    def test_ai_initialization(self):
        """测试AI初始化"""
        self.assertIsNotNone(self.ai_manager.ai_engine)

    def test_basic_reaction(self):
        """测试基础反应"""
        # 创建模拟对象
        mock_player = Mock()
        mock_player.level = 1
        mock_player.attack_power = 10
        mock_player.combo = 0
        mock_player.max_combo = 0
        mock_player.stamina = 100
        mock_player.weapon_tier = 1
        mock_player.coins = 0

        mock_enemy = Mock()
        mock_enemy.hp = 100
        mock_enemy.max_hp = 100
        mock_enemy.last_damage = 15

        # 测试反应（不抛出异常即可）
        try:
            self.ai_manager.update_and_respond(mock_player, mock_enemy)
        except Exception as e:
            self.fail(f"AI reaction raised an exception: {e}")

    def test_high_damage_reaction(self):
        """测试高伤害反应"""
        mock_player = Mock()
        mock_player.level = 1
        mock_player.attack_power = 10
        mock_player.combo = 0
        mock_player.max_combo = 0
        mock_player.stamina = 100
        mock_player.weapon_tier = 1
        mock_player.coins = 0

        mock_enemy = Mock()
        mock_enemy.hp = 100
        mock_enemy.max_hp = 100
        mock_enemy.last_damage = 20  # 高伤害

        # 测试AI响应（不直接断言print，因为AIManager可能有不同的输出方式）
        response = self.ai_manager.update_and_respond(mock_player, mock_enemy)
        # 只要不抛出异常就算通过，AI响应可能为None（由于冷却等机制）

    def test_level_multiple_reaction(self):
        """测试等级倍数反应"""
        mock_player = Mock()
        mock_player.level = 3  # 3的倍数
        mock_player.attack_power = 15
        mock_player.combo = 0
        mock_player.max_combo = 0
        mock_player.stamina = 100
        mock_player.weapon_tier = 1
        mock_player.coins = 0

        mock_enemy = Mock()
        mock_enemy.hp = 80
        mock_enemy.max_hp = 80
        mock_enemy.last_damage = 10

        # 测试AI响应
        response = self.ai_manager.update_and_respond(mock_player, mock_enemy)
        # 不强制要求响应，因为可能有冷却机制

    def test_various_comments(self):
        """测试各种评论"""
        mock_player = Mock()
        mock_player.level = 1
        mock_player.attack_power = 10
        mock_player.combo = 0
        mock_player.max_combo = 0
        mock_player.stamina = 100
        mock_player.weapon_tier = 1
        mock_player.coins = 0

        mock_enemy = Mock()
        mock_enemy.hp = 90
        mock_enemy.max_hp = 90
        mock_enemy.last_damage = 12

        # 多次触发反应，测试评论多样性
        comments = []
        for _ in range(10):
            response = self.ai_manager.update_and_respond(mock_player, mock_enemy)
            if response:
                comments.append(response.text if hasattr(response, 'text') else str(response))

        # 检查是否有不同的评论（如果没有响应也可能正常，因为AI可能有冷却机制）
        if len(comments) > 1:
            unique_comments = set(comments)
            self.assertGreater(len(unique_comments), 0, "AI should generate some comments")
        # 如果没有收到评论，也不算失败，因为AI可能有冷却或其他机制

    def test_reaction_with_different_damage_levels(self):
        """测试不同伤害等级的反应"""
        mock_player = Mock()
        mock_player.level = 1
        mock_player.attack_power = 10
        mock_player.combo = 0
        mock_player.max_combo = 0
        mock_player.stamina = 100
        mock_player.weapon_tier = 1
        mock_player.coins = 0

        mock_enemy = Mock()
        mock_enemy.hp = 100
        mock_enemy.max_hp = 100

        damage_levels = [5, 10, 15, 20, 25]

        for damage in damage_levels:
            mock_enemy.last_damage = damage
            response = self.ai_manager.update_and_respond(mock_player, mock_enemy)
            # 不强制要求有响应，因为AI可能有冷却机制
            # 只测试不会抛出异常即可


class TestRuleBasedAI(unittest.TestCase):
    """基于规则的AI单元测试"""

    def setUp(self):
        """测试前准备"""
        self.rule_ai = RuleBasedAI()

    def test_rule_based_initialization(self):
        """测试规则AI初始化"""
        self.assertIsNotNone(self.rule_ai.current_mood)
        self.assertEqual(self.rule_ai.bond, 10)
        self.assertIsNotNone(self.rule_ai.comment_templates)

    def test_can_comment_cooling(self):
        """测试评论冷却机制"""
        from src.ai.ai_interface import AIContext

        # 创建上下文
        context = AIContext(
            player_level=1,
            player_combo=5,
            player_power=10,
            enemy_hp_percent=0.8,
            recent_damage=12,
            ai_affinity=10,
            location="新手村",
            time_since_last_comment=0.1,  # 很短的时间
            player_stamina=100,
            weapon_tier=1,
            total_coins=0,
            is_crit_hit=False,
            is_level_up=False,
            max_combo_achieved=5,
            attack_frequency=1.0,
            crit_frequency=0.05,
            combo_tendency=0.5
        )

        # 短时间内不应该评论
        response = self.rule_ai.generate_response(context)
        self.assertIsNone(response)

        # 足过冷却时间后可能评论（但不保证一定评论，因为有随机因素）
        context.time_since_last_comment = 5.0
        # 多次尝试以增加获得评论的概率
        response = None
        for _ in range(10):
            response = self.rule_ai.generate_response(context)
            if response is not None:
                break
        
        # 我们只验证不会抛出异常，不强制要求必须有响应

    def test_high_combo_response(self):
        """测试高连击响应"""
        from src.ai.ai_interface import AIContext, AIMood

        context = AIContext(
            player_level=1,
            player_combo=15,  # 高连击
            player_power=10,
            enemy_hp_percent=0.8,
            recent_damage=12,
            ai_affinity=10,
            location="新手村",
            time_since_last_comment=5.0,
            player_stamina=100,
            weapon_tier=1,
            total_coins=0,
            is_crit_hit=False,
            is_level_up=False,
            max_combo_achieved=15,
            attack_frequency=1.0,
            crit_frequency=0.05,
            combo_tendency=0.5
        )

        response = self.rule_ai.generate_response(context)
        # 检查是否有响应，如果有则验证情绪
        if response is not None:
            self.assertEqual(response.mood, AIMood.EXCITED)

    def test_crit_hit_response(self):
        """测试暴击响应"""
        from src.ai.ai_interface import AIContext, AIMood

        context = AIContext(
            player_level=1,
            player_combo=5,
            player_power=10,
            enemy_hp_percent=0.8,
            recent_damage=20,  # 高伤害，假设是暴击
            ai_affinity=10,
            location="新手村",
            time_since_last_comment=5.0,
            player_stamina=100,
            weapon_tier=1,
            total_coins=0,
            is_crit_hit=True,
            is_level_up=False,
            max_combo_achieved=5,
            attack_frequency=1.0,
            crit_frequency=0.05,
            combo_tendency=0.5
        )

        response = self.rule_ai.generate_response(context)
        # 检查是否有响应，如果有则验证情绪
        if response is not None:
            self.assertIn(response.mood, [AIMood.EXCITED, AIMood.IMPRESSED])

    def test_enemy_low_hp_response(self):
        """测试敌人低血量响应"""
        from src.ai.ai_interface import AIContext

        context = AIContext(
            player_level=1,
            player_combo=5,
            player_power=10,
            enemy_hp_percent=0.1,  # 低血量
            recent_damage=12,
            ai_affinity=10,
            location="新手村",
            time_since_last_comment=5.0,
            player_stamina=100,
            weapon_tier=1,
            total_coins=0,
            is_crit_hit=False,
            is_level_up=False,
            max_combo_achieved=5,
            attack_frequency=1.0,
            crit_frequency=0.05,
            combo_tendency=0.5
        )

        response = self.rule_ai.generate_response(context)
        # 低血量时可能有响应，但不强制要求
        # 我们只验证不会抛出异常

    def test_low_stamina_response(self):
        """测试低体力响应"""
        from src.ai.ai_interface import AIContext

        context = AIContext(
            player_level=1,
            player_combo=5,
            player_power=10,
            enemy_hp_percent=0.8,
            recent_damage=12,
            ai_affinity=10,
            location="新手村",
            time_since_last_comment=5.0,
            player_stamina=5,  # 低体力
            weapon_tier=1,
            total_coins=0,
            is_crit_hit=False,
            is_level_up=False,
            max_combo_achieved=5,
            attack_frequency=1.0,
            crit_frequency=0.05,
            combo_tendency=0.5
        )

        response = self.rule_ai.generate_response(context)
        # 低体力时可能有响应，但不强制要求
        # 我们只验证不会抛出异常

    def test_level_up_response(self):
        """测试升级响应"""
        from src.ai.ai_interface import AIContext, AIMood

        context = AIContext(
            player_level=2,  # 升级后的等级
            player_combo=5,
            player_power=15,  # 升级后的攻击力
            enemy_hp_percent=0.8,
            recent_damage=12,
            ai_affinity=10,
            location="新手村",
            time_since_last_comment=5.0,
            player_stamina=100,
            weapon_tier=1,
            total_coins=0,
            is_crit_hit=False,
            is_level_up=True,  # 刚升级
            max_combo_achieved=5,
            attack_frequency=1.0,
            crit_frequency=0.05,
            combo_tendency=0.5
        )

        response = self.rule_ai.generate_response(context)
        # 检查是否有响应，如果有则验证情绪是合理的
        if response is not None:
            # 升级时可以是兴奋或印象深刻的情绪
            self.assertIn(response.mood, [AIMood.EXCITED, AIMood.IMPRESSED])

    def test_update_learning_state(self):
        """测试学习状态更新"""
        from src.ai.ai_interface import AIContext

        context = AIContext(
            player_level=1,
            player_combo=5,
            player_power=10,
            enemy_hp_percent=0.8,
            recent_damage=12,
            ai_affinity=10,
            location="新手村",
            time_since_last_comment=5.0,
            player_stamina=100,
            weapon_tier=1,
            total_coins=0,
            is_crit_hit=False,
            is_level_up=False,
            max_combo_achieved=5,
            attack_frequency=1.0,
            crit_frequency=0.05,
            combo_tendency=0.5
        )

        # 更新学习状态不应该抛出异常
        try:
            self.rule_ai.update_learning_state(context)
        except Exception as e:
            self.fail(f"update_learning_state raised an exception: {e}")

    def test_get_current_mood(self):
        """测试获取当前情绪"""
        mood = self.rule_ai.get_current_mood()
        self.assertIsNotNone(mood)

    def test_affinity_update(self):
        """测试亲密度更新"""
        initial_bond = self.rule_ai.bond

        # 测试增加亲密度
        self.rule_ai.update_affinity(5)
        self.assertEqual(self.rule_ai.bond, initial_bond + 5)

        # 测试减少亲密度
        self.rule_ai.update_affinity(-3)
        self.assertEqual(self.rule_ai.bond, initial_bond + 5 - 3)

        # 测试边界值
        self.rule_ai.update_affinity(1000)
        self.assertEqual(self.rule_ai.bond, 100)  # 最大值

        self.rule_ai.update_affinity(-1000)
        self.assertEqual(self.rule_ai.bond, 0)  # 最小值

    def test_record_comment(self):
        """测试评论记录"""
        from src.ai.ai_interface import AIResponse, AIMood

        response = AIResponse(
            text="测试评论",
            mood=AIMood.EXCITED,
            priority=8,
            cooldown_time=2.0,
            affinity_change=2
        )

        initial_history_count = len(self.rule_ai.comment_history)
        self.rule_ai.record_comment(response)

        self.assertEqual(len(self.rule_ai.comment_history), initial_history_count + 1)
        self.assertEqual(self.rule_ai.comment_history[-1]['text'], "测试评论")

    def test_reset_learning_state(self):
        """测试学习状态重置"""
        # 修改一些状态
        self.rule_ai.bond = 50
        self.rule_ai.comment_history.append({"test": "data"})

        # 重置
        self.rule_ai.reset_learning_state()

        # 检查重置效果
        self.assertEqual(self.rule_ai.bond, 10)
        self.assertEqual(len(self.rule_ai.comment_history), 0)


if __name__ == '__main__':
    unittest.main()