import unittest
from unittest.mock import Mock, patch
import pytest
import pygame

# 导入测试辅助工具
from tests.helpers.assertions import GameTestAssertions

from src.game.effects import EffectManager, EffectType, Effect, Particle


class TestEffectManager(unittest.TestCase):
    """特效管理器单元测试"""

    def setUp(self):
        """测试前准备"""
        # 初始化pygame（测试需要）
        pygame.init()
        pygame.mixer.init()  # 避免声音相关错误

        self.effect_manager = EffectManager(800, 600)

    def tearDown(self):
        """测试后清理"""
        pygame.quit()

    def test_effect_manager_initialization(self):
        """测试特效管理器初始化"""
        self.assertEqual(self.effect_manager.screen_width, 800)
        self.assertEqual(self.effect_manager.screen_height, 600)
        self.assertEqual(len(self.effect_manager.effects), 0)
        self.assertEqual(len(self.effect_manager.particles), 0)
        self.assertEqual(self.effect_manager.screen_shake_offset, [0, 0])

    def test_create_slash_effect(self):
        """测试砍击特效创建"""
        start_pos = (100, 100)
        end_pos = (200, 150)

        self.effect_manager.create_slash_effect(start_pos, end_pos, is_crit=False)

        # 应该创建一个特效和多个粒子
        self.assertEqual(len(self.effect_manager.effects), 1)
        self.assertGreater(len(self.effect_manager.particles), 0)

        effect = self.effect_manager.effects[0]
        self.assertEqual(effect.type, EffectType.SLASH)
        self.assertEqual(effect.pos, start_pos)

    def test_create_crit_effect(self):
        """测试暴击特效创建"""
        damage = 50
        pos = (300, 200)

        self.effect_manager.create_crit_effect(damage, pos)

        # 应该创建暴击特效、伤害数字和爆炸粒子
        self.assertGreater(len(self.effect_manager.effects), 1)
        self.assertGreater(len(self.effect_manager.particles), 20)  # 暴击应该有更多粒子

        # 检查是否有暴击特效
        crit_effects = [e for e in self.effect_manager.effects if e.type == EffectType.CRIT]
        self.assertGreater(len(crit_effects), 0)

        # 检查是否有伤害数字
        damage_effects = [e for e in self.effect_manager.effects if e.type == EffectType.DAMAGE_NUMBER]
        self.assertGreater(len(damage_effects), 0)

        # 检查屏幕震动
        self.assertGreater(self.effect_manager.screen_shake_intensity, 0)

    def test_create_combo_effect(self):
        """测试连击特效创建"""
        combo_count = 15
        pos = (400, 300)

        self.effect_manager.create_combo_effect(combo_count, pos)

        # 应该创建连击特效
        combo_effects = [e for e in self.effect_manager.effects if e.type == EffectType.COMBO]
        self.assertEqual(len(combo_effects), 1)

        effect = combo_effects[0]
        self.assertEqual(effect.data['combo'], combo_count)

        # 高连击应该创建环状粒子
        if combo_count >= 10:
            self.assertGreater(len(self.effect_manager.particles), 0)

    def test_create_level_up_effect(self):
        """测试升级特效创建"""
        pos = (400, 200)

        self.effect_manager.create_level_up_effect(pos)

        # 应该创建升级特效
        level_effects = [e for e in self.effect_manager.effects if e.type == EffectType.LEVEL_UP]
        self.assertEqual(len(level_effects), 1)

        # 应该创建大量粒子
        self.assertGreater(len(self.effect_manager.particles), 40)

        # 强烈屏幕震动
        self.assertEqual(self.effect_manager.screen_shake_intensity, 10)

    def test_create_damage_number(self):
        """测试伤害数字创建"""
        damage = 25
        pos = (300, 250)

        self.effect_manager.create_damage_number(damage, pos, is_crit=False)

        damage_effects = [e for e in self.effect_manager.effects if e.type == EffectType.DAMAGE_NUMBER]
        self.assertEqual(len(damage_effects), 1)

        effect = damage_effects[0]
        self.assertEqual(effect.data['text'], str(damage))

    def test_create_exp_gain_effect(self):
        """测试经验获得特效创建"""
        exp_amount = 100
        pos = (200, 150)

        self.effect_manager.create_exp_gain_effect(exp_amount, pos)

        exp_effects = [e for e in self.effect_manager.effects if e.type == EffectType.EXP_GAIN]
        self.assertEqual(len(exp_effects), 1)

        effect = exp_effects[0]
        self.assertEqual(effect.data['text'], f"+{exp_amount} 经验")

    def test_create_stamina_warning(self):
        """测试体力警告创建"""
        pos = (400, 400)

        self.effect_manager.create_stamina_warning(pos)

        warning_effects = [e for e in self.effect_manager.effects if e.type == EffectType.STAMINA_WARNING]
        self.assertEqual(len(warning_effects), 1)

        effect = warning_effects[0]
        self.assertEqual(effect.data['text'], "体力不足！")

    def test_create_screen_shake(self):
        """测试屏幕震动创建"""
        intensity = 5
        duration = 20

        self.effect_manager.create_screen_shake(intensity, duration)

        self.assertEqual(self.effect_manager.screen_shake_intensity, intensity)
        self.assertEqual(self.effect_manager.screen_shake_duration, duration)

    def test_update_effects(self):
        """测试特效更新"""
        # 创建一些特效
        self.effect_manager.create_slash_effect((100, 100), (200, 150))
        self.effect_manager.create_damage_number(15, (150, 120))

        initial_effect_count = len(self.effect_manager.effects)

        # 更新足够多次让特效消失
        for _ in range(100):
            self.effect_manager.update()

        # 特效应该消失
        self.assertLess(len(self.effect_manager.effects), initial_effect_count)

    def test_update_particles(self):
        """测试粒子更新"""
        # 创建一些粒子
        self.effect_manager.create_crit_effect(30, (200, 200))
        initial_particle_count = len(self.effect_manager.particles)

        # 更新多次让粒子消失
        for _ in range(50):
            self.effect_manager.update()

        # 粒子应该消失
        self.assertLess(len(self.effect_manager.particles), initial_particle_count)

    def test_update_screen_shake(self):
        """测试屏幕震动更新"""
        # 创建屏幕震动
        self.effect_manager.create_screen_shake(5, 15)

        # 更新直到震动结束
        for _ in range(20):
            self.effect_manager.update()

        # 震动应该结束
        self.assertEqual(self.effect_manager.screen_shake_duration, 0)
        self.assertEqual(self.effect_manager.screen_shake_intensity, 0)
        self.assertEqual(self.effect_manager.screen_shake_offset, [0, 0])

    def test_clear_all_effects(self):
        """测试清除所有特效"""
        # 创建一些特效
        self.effect_manager.create_slash_effect((100, 100), (200, 150))
        self.effect_manager.create_damage_number(15, (150, 120))
        self.effect_manager.create_screen_shake(3, 10)

        # 清除特效
        self.effect_manager.clear_all_effects()

        # 检查清除效果
        self.assertEqual(len(self.effect_manager.effects), 0)
        self.assertEqual(len(self.effect_manager.particles), 0)
        self.assertEqual(self.effect_manager.screen_shake_offset, [0, 0])
        self.assertEqual(self.effect_manager.screen_shake_intensity, 0)
        self.assertEqual(self.effect_manager.screen_shake_duration, 0)

    def test_get_stats(self):
        """测试统计信息获取"""
        # 创建一些特效
        self.effect_manager.create_slash_effect((100, 100), (200, 150))
        self.effect_manager.create_damage_number(15, (150, 120))

        stats = self.effect_manager.get_stats()

        # 检查必要字段
        required_fields = [
            'total_effects_created',
            'total_particles_created',
            'active_effects',
            'active_particles'
        ]

        for field in required_fields:
            self.assertIn(field, stats)

        # 应该有创建的特效和粒子
        self.assertGreater(stats['total_effects_created'], 0)
        self.assertGreater(stats['total_particles_created'], 0)

    def test_reset_stats(self):
        """测试统计重置"""
        # 创建一些特效
        self.effect_manager.create_slash_effect((100, 100), (200, 150))

        # 重置统计
        self.effect_manager.reset_stats()

        stats = self.effect_manager.get_stats()

        # 检查重置效果
        self.assertEqual(stats['total_effects_created'], 0)
        self.assertEqual(stats['total_particles_created'], 0)

    def test_effect_lifecycle(self):
        """测试特效生命周期"""
        # 创建砍击特效
        self.effect_manager.create_slash_effect((100, 100), (200, 150))
        effect = self.effect_manager.effects[0]

        initial_timer = effect.timer

        # 更新一次
        self.effect_manager.update()

        # 计时器应该减少
        self.assertEqual(effect.timer, initial_timer - 1)

        # 更新直到特效消失
        while effect in self.effect_manager.effects:
            self.effect_manager.update()

        # 特效应该从列表中移除
        self.assertNotIn(effect, self.effect_manager.effects)

    def test_particle_lifecycle(self):
        """测试粒子生命周期"""
        # 创建暴击特效（包含粒子）
        self.effect_manager.create_crit_effect(30, (200, 200))

        if self.effect_manager.particles:
            particle = self.effect_manager.particles[0]
            initial_life = particle.life
            initial_pos_y = particle.pos[1]

            # 更新一次
            self.effect_manager.update()

            # 生命值应该减少
            self.assertEqual(particle.life, initial_life - 1)

            # 位置应该变化（重力影响）
            # 粒子可能向上或向下移动，检查是否发生变化
            self.assertNotEqual(particle.pos[1], initial_pos_y)

    def test_max_effects_limit(self):
        """测试特效数量限制"""
        # 创建大量相同类型的特效
        for _ in range(100):
            self.effect_manager.create_damage_number(10, (100, 100))

        # 特效数量应该被限制
        damage_effects = [e for e in self.effect_manager.effects if e.type == EffectType.DAMAGE_NUMBER]
        self.assertLessEqual(len(damage_effects), self.effect_manager.max_effects_per_type)


class TestEffectStructures(unittest.TestCase):
    """特效数据结构单元测试"""

    def setUp(self):
        """测试前准备"""
        pygame.init()
        pygame.mixer.init()

    def tearDown(self):
        """测试后清理"""
        pygame.quit()

    def test_effect_creation(self):
        """测试Effect创建"""
        effect = Effect(
            type=EffectType.SLASH,
            pos=(100, 100),
            timer=30,
            data={"test": "data"}
        )

        self.assertEqual(effect.type, EffectType.SLASH)
        self.assertEqual(effect.pos, (100, 100))
        self.assertEqual(effect.timer, 30)
        self.assertEqual(effect.data["test"], "data")
        self.assertGreater(effect.created_time, 0)

    def test_particle_creation(self):
        """测试Particle创建"""
        particle = Particle(
            pos=[100.0, 200.0],
            vel=[1.0, -2.0],
            life=30,
            max_life=30,
            size=3,
            color=(255, 255, 255),
            gravity=0.5,
            fade=True
        )

        self.assertEqual(particle.pos, [100.0, 200.0])
        self.assertEqual(particle.vel, [1.0, -2.0])
        self.assertEqual(particle.life, 30)
        self.assertEqual(particle.max_life, 30)
        self.assertEqual(particle.size, 3)
        self.assertEqual(particle.color, (255, 255, 255))
        self.assertEqual(particle.gravity, 0.5)
        self.assertTrue(particle.fade)


if __name__ == '__main__':
    unittest.main()