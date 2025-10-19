import unittest
from unittest.mock import Mock

# 导入测试辅助工具
from tests.helpers.factories import EnemyFactory
from tests.helpers.assertions import GameTestAssertions

from src.game.enemy import StrawDummy, Dummy, EnemyType


class TestStrawDummy(unittest.TestCase):
    """稻草人单元测试"""

    def setUp(self):
        """测试前准备"""
        self.straw_dummy = StrawDummy()

    def test_straw_dummy_initialization(self):
        """测试稻草人初始化"""
        self.assertEqual(self.straw_dummy.hp, 100)
        self.assertEqual(self.straw_dummy.max_hp, 100)
        self.assertEqual(self.straw_dummy.enemy_type, EnemyType.STRAW_DUMMY)
        self.assertEqual(self.straw_dummy.name, "稻草人")
        self.assertTrue(self.straw_dummy.is_alive)
        self.assertEqual(self.straw_dummy.total_damage_taken, 0)
        self.assertEqual(self.straw_dummy.hits_received, 0)
        self.assertEqual(self.straw_dummy.times_defeated, 0)

    def test_hit_damage(self):
        """测试受击伤害"""
        initial_hp = self.straw_dummy.hp
        damage = 20

        hit = self.straw_dummy.hit(damage)

        self.assertTrue(hit)
        self.assertEqual(self.straw_dummy.hp, initial_hp - damage)
        self.assertEqual(self.straw_dummy.last_damage, damage)
        self.assertEqual(self.straw_dummy.total_damage_taken, damage)
        self.assertEqual(self.straw_dummy.hits_received, 1)

    def test_hit_when_dead(self):
        """测试死亡时受击"""
        # 设置为死亡状态
        self.straw_dummy.hp = 0
        self.straw_dummy.is_alive = False

        hit = self.straw_dummy.hit(20)

        self.assertFalse(hit)

    def test_death_and_respawn(self):
        """测试死亡和重生"""
        # 造成致命伤害
        hit = self.straw_dummy.hit(150)  # 超过最大血量

        self.assertTrue(hit)
        self.assertFalse(self.straw_dummy.is_alive)
        self.assertEqual(self.straw_dummy.hp, 0)
        self.assertEqual(self.straw_dummy.times_defeated, 1)
        self.assertGreater(self.straw_dummy.death_animation_timer, 0)

        # 模拟死亡动画结束
        for _ in range(self.straw_dummy.death_animation_timer):
            self.straw_dummy.update()

        # 检查重生
        self.assertTrue(self.straw_dummy.is_alive)
        self.assertEqual(self.straw_dummy.hp, self.straw_dummy.max_hp)
        self.assertEqual(self.straw_dummy.last_damage, 0)

    def test_get_hp_percentage(self):
        """测试血量百分比"""
        # 满血状态
        self.assertEqual(self.straw_dummy.get_hp_percentage(), 1.0)

        # 半血状态
        self.straw_dummy.hp = 50
        self.assertEqual(self.straw_dummy.get_hp_percentage(), 0.5)

        # 空血状态
        self.straw_dummy.hp = 0
        self.assertEqual(self.straw_dummy.get_hp_percentage(), 0.0)

    def test_scale_with_player_level(self):
        """测试随玩家等级缩放"""
        # 等级1：无缩放
        self.straw_dummy.scale_with_player_level(1)
        self.assertEqual(self.straw_dummy.level_scaling, 1.0)
        self.assertEqual(self.straw_dummy.max_hp, 100)

        # 等级3：缩放因子1.2
        self.straw_dummy.scale_with_player_level(3)
        self.assertEqual(self.straw_dummy.level_scaling, 1.2)
        self.assertEqual(self.straw_dummy.max_hp, 120)  # 100 * 1.2

        # 等级6：缩放因子1.4
        self.straw_dummy.scale_with_player_level(6)
        self.assertEqual(self.straw_dummy.level_scaling, 1.4)
        self.assertEqual(self.straw_dummy.max_hp, 140)  # 100 * 1.4

    def test_apply_damage_scaling(self):
        """测试伤害缩放应用"""
        # 设置缩放因子
        self.straw_dummy.scale_with_player_level(6)  # 1.4倍缩放

        # 造成20点伤害
        self.straw_dummy.hit(20)

        # 实际伤害应该是 20 * 1.4 = 28
        # 由于当前hp是100，缩放后max_hp是140，但是hp会保持为min(100, 140) = 100
        # 所以hp应该是 100 - 28 = 72
        expected_hp = 72
        self.assertEqual(self.straw_dummy.hp, expected_hp)

    def test_get_status_info(self):
        """测试状态信息获取"""
        status = self.straw_dummy.get_status_info()

        # 检查必要字段
        required_fields = [
            'name', 'type', 'hp', 'max_hp', 'hp_percent',
            'is_alive', 'last_damage', 'total_damage_taken',
            'hits_received', 'times_defeated', 'level_scaling'
        ]

        for field in required_fields:
            self.assertIn(field, status)

        self.assertEqual(status['name'], "稻草人")
        self.assertEqual(status['type'], "straw_dummy")
        self.assertEqual(status['hp'], 100)
        self.assertEqual(status['max_hp'], 100)

    def test_particles_creation(self):
        """测试粒子创建"""
        initial_particle_count = len(self.straw_dummy.particles)

        # 造成伤害触发粒子效果
        self.straw_dummy.hit(15)

        # 应该创建新粒子
        self.assertGreater(len(self.straw_dummy.particles), initial_particle_count)

    def test_update_particles(self):
        """测试粒子更新"""
        # 创建一些粒子
        self.straw_dummy.hit(20)

        initial_particle_count = len(self.straw_dummy.particles)

        # 更新多次
        for _ in range(50):
            self.straw_dummy.update()

        # 粒子应该消失
        self.assertLess(len(self.straw_dummy.particles), initial_particle_count)

    def test_hit_animation(self):
        """测试受击动画"""
        # 造成伤害
        self.straw_dummy.hit(15)

        # 检查动画计时器
        self.assertGreater(self.straw_dummy.hit_animation_timer, 0)

        # 颜色应该改变（需要调用update来触发颜色变化）
        self.straw_dummy.update()
        self.assertNotEqual(self.straw_dummy.current_color, self.straw_dummy.base_color)

        # 更新直到动画结束
        for _ in range(self.straw_dummy.hit_animation_timer):
            self.straw_dummy.update()

        # 颜色应该恢复
        self.assertEqual(self.straw_dummy.current_color, self.straw_dummy.base_color)

    def test_wobble_effect(self):
        """测试摇晃效果"""
        # 造成伤害
        self.straw_dummy.hit(15)

        # 应该有摇晃速度
        self.assertNotEqual(self.straw_dummy.wobble_speed, 0)

        # 更新多次（摇晃应该逐渐停止）
        for _ in range(100):  # 增加更新次数
            self.straw_dummy.update()

        # 摇晃应该停止（考虑到浮点数精度问题）
        self.assertAlmostEqual(self.straw_dummy.wobble_speed, 0, places=2)
        self.assertEqual(self.straw_dummy.wobble_angle, 0)

    def test_reset(self):
        """测试重置"""
        # 修改一些状态
        self.straw_dummy.hp = 50
        self.straw_dummy.times_defeated = 3
        self.straw_dummy.is_alive = False

        # 重置
        self.straw_dummy.reset()

        # 检查重置效果
        self.assertEqual(self.straw_dummy.hp, 100)
        self.assertEqual(self.straw_dummy.times_defeated, 0)
        self.assertTrue(self.straw_dummy.is_alive)
        self.assertEqual(self.straw_dummy.total_damage_taken, 0)
        self.assertEqual(self.straw_dummy.hits_received, 0)


class TestDummy(unittest.TestCase):
    """Dummy类向后兼容性测试"""

    def setUp(self):
        """测试前准备"""
        self.dummy = Dummy()

    def test_dummy_is_straw_dummy(self):
        """测试Dummy类是StrawDummy的别名"""
        self.assertIsInstance(self.dummy, StrawDummy)

    def test_dummy_initialization(self):
        """测试Dummy初始化"""
        self.assertEqual(self.dummy.name, "稻草人")
        self.assertEqual(self.dummy.enemy_type, EnemyType.STRAW_DUMMY)

    def test_dummy_hit_method(self):
        """测试Dummy的hit方法"""
        initial_hp = self.dummy.hp
        hit = self.dummy.hit(20)

        self.assertTrue(hit)
        self.assertEqual(self.dummy.hp, initial_hp - 20)


if __name__ == '__main__':
    unittest.main()