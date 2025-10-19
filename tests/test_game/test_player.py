"""
玩家系统单元测试
"""

import unittest
from unittest.mock import Mock, patch

# 导入测试辅助工具
from tests.helpers.factories import PlayerFactory
from tests.helpers.assertions import GameTestAssertions
from tests.helpers.mock_data import MockGameDataGenerator

# 导入被测试的模块
from src.game.player import Player


class TestPlayer(unittest.TestCase):
    """玩家系统单元测试"""

    def setUp(self):
        """测试前准备"""
        self.player = Player()

    def test_player_initialization(self):
        """测试玩家初始化"""
        # 检查初始属性
        self.assertEqual(self.player.level, 1)
        self.assertEqual(self.player.exp, 0)
        self.assertEqual(self.player.attack_power, 10)
        self.assertEqual(self.player.combo, 0)
        self.assertEqual(self.player.max_combo, 0)
        self.assertEqual(self.player.stamina, 100)
        self.assertEqual(self.player.max_stamina, 100)
        self.assertEqual(self.player.crit_rate, 0.05)
        self.assertEqual(self.player.weapon_tier, 1)
        self.assertEqual(self.player.coins, 0)
        self.assertEqual(self.player.location, "新手村")
        self.assertEqual(self.player.ai_affinity, 10)

    def test_calc_exp_needed(self):
        """测试经验计算公式"""
        # 等级1需要50经验
        self.assertEqual(self.player.calc_exp_needed(1), 50)
        # 等级2需要60经验 (50 * 1.2)
        self.assertEqual(self.player.calc_exp_needed(2), 60)
        # 等级3需要72经验 (60 * 1.2)
        self.assertEqual(self.player.calc_exp_needed(3), 72)

    def test_calc_damage(self):
        """测试伤害计算"""
        # 测试基础伤害
        damage, is_crit = self.player.calc_damage()
        self.assertIn(damage, range(self.player.attack_power - 2, self.player.attack_power + 6))
        self.assertIsInstance(is_crit, bool)

        # 测试暴击（需要多次测试因为有随机性）
        crit_count = 0
        total_tests = 100
        for _ in range(total_tests):
            damage, is_crit = self.player.calc_damage()
            if is_crit:
                crit_count += 1
                # 暴击伤害应该是基础伤害的2倍
                self.assertGreater(damage, self.player.attack_power)

        # 暴击率应该在合理范围内（5%左右，允许一定误差）
        crit_rate = crit_count / total_tests
        self.assertGreater(crit_rate, 0)
        self.assertLess(crit_rate, 0.2)  # 不应该超过20%

    def test_can_attack(self):
        """测试攻击条件检查"""
        # 初始状态应该可以攻击
        self.assertTrue(self.player.can_attack())

        # 体力不足时不能攻击
        self.player.stamina = 5
        self.assertFalse(self.player.can_attack())

        # 恢复体力后可以攻击
        self.player.stamina = 100
        self.assertTrue(self.player.can_attack())

    def test_use_stamina(self):
        """测试体力消耗"""
        initial_stamina = self.player.stamina

        # 正常消耗
        self.assertTrue(self.player.use_stamina(10))
        self.assertEqual(self.player.stamina, initial_stamina - 10)

        # 体力不足时无法消耗
        self.assertFalse(self.player.use_stamina(200))
        self.assertEqual(self.player.stamina, initial_stamina - 10)

    def test_regen_stamina(self):
        """测试体力恢复"""
        self.player.stamina = 50
        self.player.regen_stamina(20)
        self.assertEqual(self.player.stamina, 70)

        # 不能超过最大体力
        self.player.regen_stamina(100)
        self.assertEqual(self.player.stamina, self.player.max_stamina)

    def test_increase_combo(self):
        """测试连击增加"""
        initial_combo = self.player.combo

        self.player.increase_combo()
        self.assertEqual(self.player.combo, initial_combo + 1)

        # 最大连击应该更新
        self.assertEqual(self.player.max_combo, self.player.combo)

    def test_reset_combo(self):
        """测试连击重置"""
        self.player.combo = 10
        self.player.reset_combo()
        self.assertEqual(self.player.combo, 0)

    def test_get_combo_multiplier(self):
        """测试连击倍率"""
        # 无连击时倍率为1
        self.player.combo = 0
        self.assertEqual(self.player.get_combo_multiplier(), 1.0)

        # 10连击时倍率为1.1
        self.player.combo = 10
        self.assertEqual(self.player.get_combo_multiplier(), 1.1)

        # 20连击时倍率为1.2
        self.player.combo = 20
        self.assertEqual(self.player.get_combo_multiplier(), 1.2)

    def test_add_exp(self):
        """测试经验增加"""
        initial_exp = self.player.exp
        self.player.add_exp(30)
        self.assertEqual(self.player.exp, initial_exp + 30)

    def test_level_up(self):
        """测试升级"""
        # 设置刚好升级的经验
        self.player.exp = self.player.next_exp - 1
        initial_level = self.player.level
        initial_attack_power = self.player.attack_power

        self.player.add_exp(1)

        # 检查升级
        self.assertEqual(self.player.level, initial_level + 1)
        self.assertGreater(self.player.attack_power, initial_attack_power)
        self.assertEqual(self.player.exp, 0)  # 经验应该重置
        self.assertEqual(self.player.stamina, self.player.max_stamina)  # 体力应该回满
        self.assertTrue(self.player.just_leveled_up)

    def test_add_coins(self):
        """测试金币增加"""
        initial_coins = self.player.coins
        self.player.add_coins(50)
        self.assertEqual(self.player.coins, initial_coins + 50)

    def test_use_coins(self):
        """测试金币使用"""
        initial_coins = self.player.coins
        self.player.add_coins(100)

        # 正常使用
        self.assertTrue(self.player.use_coins(30))
        self.assertEqual(self.player.coins, initial_coins + 100 - 30)

        # 金币不足时无法使用
        self.assertFalse(self.player.use_coins(200))
        self.assertEqual(self.player.coins, initial_coins + 100 - 30)

    def test_upgrade_weapon(self):
        """测试武器升级"""
        # 添加足够的金币
        self.player.coins = 100
        initial_weapon_tier = self.player.weapon_tier
        initial_attack_power = self.player.attack_power

        success = self.player.upgrade_weapon()

        if success:
            self.assertEqual(self.player.weapon_tier, initial_weapon_tier + 1)
            self.assertGreater(self.player.attack_power, initial_attack_power)
        else:
            self.assertEqual(self.player.weapon_tier, initial_weapon_tier)
            self.assertEqual(self.player.attack_power, initial_attack_power)

    def test_set_location(self):
        """测试位置设置"""
        new_location = "竹林道场"
        self.player.set_location(new_location)
        self.assertEqual(self.player.location, new_location)

    def test_update(self):
        """测试状态更新"""
        initial_stamina = self.player.stamina
        self.player.stamina = 50

        # 模拟时间流逝
        self.player.update(1.0)  # 1秒

        # 体力应该恢复
        self.assertGreater(self.player.stamina, 50)
        self.assertLessEqual(self.player.stamina, self.player.max_stamina)

    def test_get_status_info(self):
        """测试状态信息获取"""
        status = self.player.get_status_info()

        # 检查必要字段
        required_fields = [
            'level', 'exp', 'next_exp', 'exp_percent',
            'attack_power', 'combo', 'max_combo',
            'stamina', 'max_stamina', 'crit_rate',
            'weapon_tier', 'coins', 'location', 'ai_affinity'
        ]

        for field in required_fields:
            self.assertIn(field, status)

    def test_reset(self):
        """测试重置"""
        # 修改一些属性
        self.player.level = 5
        self.player.coins = 1000
        self.player.combo = 20

        # 重置
        self.player.reset()

        # 检查是否恢复初始状态
        self.assertEqual(self.player.level, 1)
        self.assertEqual(self.player.coins, 0)
        self.assertEqual(self.player.combo, 0)

    def test_attack_with_mock_enemy(self):
        """测试攻击（使用模拟敌人）"""
        # 创建模拟敌人
        mock_enemy = Mock()
        mock_enemy.hit = Mock(return_value=True)
        mock_enemy.hp = 100
        mock_enemy.max_hp = 100

        # 确保可以攻击
        self.player.stamina = 100

        # 执行攻击
        hit, damage, is_crit = self.player.attack(mock_enemy)

        # 检查结果
        self.assertTrue(hit)
        self.assertGreater(damage, 0)
        self.assertIsInstance(is_crit, bool)
        mock_enemy.hit.assert_called_once()

        # 检查副作用
        self.assertGreater(self.player.exp, 0)
        self.assertGreaterEqual(self.player.coins, 0)


if __name__ == '__main__':
    unittest.main()