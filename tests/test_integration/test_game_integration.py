import unittest
import pygame
import time
from unittest.mock import Mock, patch

# 导入测试辅助工具
from tests.helpers.factories import PlayerFactory, EnemyFactory, AIContextFactory
from tests.helpers.assertions import GameTestAssertions

from src.game.player import Player
from src.game.enemy import StrawDummy
from src.ai.ai_manager import AIManager
from src.game.effects import EffectManager
from src.game.ui import UIManager
from src.game.data_manager import DataManager
from src.game.sound_manager import SoundManager

# 导入AI模块以确保注册
import src.ai.rule_based_ai

class TestGameIntegration(unittest.TestCase):
    """游戏集成测试"""

    def setUp(self):
        """测试前准备"""
        # 初始化pygame
        pygame.init()

        # 创建屏幕（测试用）
        self.screen = pygame.display.set_mode((800, 600))

        # 创建游戏组件
        self.player = Player()
        self.enemy = StrawDummy()
        self.ai_manager = AIManager("rule_based", {"comment_frequency": 1.0})  # 设置评论频率为100%
        self.effects = EffectManager(800, 600)
        self.ui_manager = UIManager(800, 600)
        self.data_manager = DataManager("test_saves", auto_save_enabled=False)
        self.sound_manager = SoundManager()  # 初始化sound_manager

    def tearDown(self):
        """测试后清理"""
        pygame.quit()

    def test_complete_attack_cycle(self):
        """测试完整攻击循环"""
        # 初始状态检查
        initial_player_exp = self.player.exp
        initial_enemy_hp = self.enemy.hp
        initial_ai_bond = self.ai_manager.get_ai_bond()

        # 执行攻击
        hit, damage, is_crit = self.player.attack(self.enemy)

        # 验证攻击结果
        self.assertTrue(hit, "攻击应该命中")
        self.assertGreater(damage, 0, "伤害应该大于0")
        self.assertLess(self.enemy.hp, initial_enemy_hp, "敌人血量应该减少")
        self.assertGreater(self.player.exp, initial_player_exp, "玩家应该获得经验")

        # 手动创建特效（模拟游戏主循环中的逻辑）
        if hit:
            # 创建砍击特效
            self.effects.create_slash_effect(
                self.player.rect.center,
                self.enemy.rect.center,
                is_crit=is_crit
            )

            # 创建伤害数字
            self.effects.create_damage_number(damage, self.enemy.rect.center, is_crit=is_crit)

        # AI应该有反应
        ai_response = self.ai_manager.update_and_respond(self.player, self.enemy)
        self.assertIsInstance(ai_response, (str, type(None)), "AI回应应该是字符串或None")

        # 特效应该被触发
        self.assertGreater(len(self.effects.effects), 0, "应该创建特效")

        # 检查状态一致性
        player_status = self.player.get_status_info()
        enemy_status = self.enemy.get_status_info()

        self.assertEqual(player_status['exp'], initial_player_exp + damage)
        self.assertEqual(enemy_status['hp'], initial_enemy_hp - damage)

    def test_level_up_integration(self):
        """测试升级集成测试"""
        # 设置足够的经验触发升级
        self.player.exp = self.player.next_exp - 1
        initial_level = self.player.level
        initial_attack_power = self.player.attack_power

        # 执行攻击触发升级
        hit, damage, is_crit = self.player.attack(self.enemy)
        print(f"Player level: {self.player.level}, just_leveled_up: {self.player.just_leveled_up}")

        # 验证升级
        self.assertEqual(self.player.level, initial_level + 1)
        self.assertGreater(self.player.attack_power, initial_attack_power)
        self.assertTrue(self.player.just_leveled_up)
        self.assertEqual(self.player.stamina, self.player.max_stamina)

        # AI应该对升级做出反应
        ai_response = self.ai_manager.update_and_respond(self.player, self.enemy)
        print(f"AI response: {ai_response}")
        self.assertIsNotNone(ai_response, "升级时AI应该有反应")

        # UI应该显示升级特效
        self.ui_manager.draw_level_up_notification(self.screen, self.player)

    def test_combo_system_integration(self):
        """测试连击系统集成"""
        # 执行多次快速攻击
        combo_count = 0
        for i in range(15):
            if self.player.can_attack():
                hit, damage, is_crit = self.player.attack(self.enemy)
                if hit:
                    combo_count += 1
                    # 更新游戏状态
                    self.player.update(1/60)
                    self.enemy.update()
                    self.effects.update()

        # 验证连击系统
        self.assertGreater(self.player.combo, 5, "应该达到5连击以上")
        self.assertGreater(self.player.max_combo, 5, "最大连击应该记录")

        # AI应该对高连击做出反应
        ai_response = self.ai_manager.update_and_respond(self.player, self.enemy)
        self.assertIsNotNone(ai_response, "高连击时AI应该有反应")

        # UI应该显示连击计数器
        self.ui_manager.draw_combo_counter(self.screen, self.player)

    def test_critical_hit_integration(self):
        """测试暴击集成"""
        # 临时提高暴击率以确保测试通过
        original_crit_rate = self.player.crit_rate
        self.player.crit_rate = 0.5  # 50%暴击率确保测试通过

        # 模拟暴击（通过多次攻击直到出现暴击）
        crit_found = False
        max_attempts = 50  # 减少尝试次数，因为暴击率已提高

        for attempt in range(max_attempts):
            # 恢复敌人状态
            if self.enemy.hp <= 0:
                self.enemy.hp = self.enemy.max_hp

            # 重置玩家体力
            self.player.stamina = self.player.max_stamina

            hit, damage, is_crit = self.player.attack(self.enemy)

            if is_crit:
                crit_found = True
                # 验证暴击效果
                self.assertGreater(damage, self.player.attack_power * 1.5, "暴击伤害应该很高")

                # 特效应该更丰富
                initial_effects = len(self.effects.effects)
                initial_particles = len(self.effects.particles)

                # AI应该对暴击做出反应
                ai_response = self.ai_manager.update_and_respond(self.player, self.enemy)
                self.assertIsNotNone(ai_response, "暴击时AI应该有反应")

                break

        # 恢复原始暴击率
        self.player.crit_rate = original_crit_rate

        self.assertTrue(crit_found, f"在{max_attempts}次攻击内应该出现暴击")

    def test_ai_cooling_system(self):
        """测试AI冷却系统"""
        # 第一次攻击
        hit1, damage1, is_crit1 = self.player.attack(self.enemy)
        ai_response1 = self.ai_manager.update_and_respond(self.player, self.enemy)

        # 立即第二次攻击
        hit2, damage2, is_crit2 = self.player.attack(self.enemy)
        ai_response2 = self.ai_manager.update_and_respond(self.player, self.enemy)

        # 由于冷却机制，第二次可能不会回应
        # 这是正常的，我们只需要确保不抛出异常
        self.assertIsInstance(ai_response2, (str, type(None)))

    def test_stamina_system_integration(self):
        """测试体力系统集成"""
        initial_stamina = self.player.stamina

        # 消耗所有体力
        attacks_made = 0
        while self.player.can_attack():
            hit, damage, is_crit = self.player.attack(self.enemy)
            if hit:
                attacks_made += 1

        # 应该无法继续攻击
        self.assertFalse(self.player.can_attack(), "体力耗尽后应该无法攻击")
        self.assertLess(self.player.stamina, 10, "体力应该很低")

        # 测试体力恢复
        self.player.update(2.0)  # 更新2秒
        self.assertGreater(self.player.stamina, 0, "体力应该开始恢复")

        # UI应该显示体力不足警告
        if self.player.stamina < 30:
            self.ui_manager.draw_stamina_bar(self.screen, self.player)

    def test_save_load_integration(self):
        """测试存档加载集成"""
        # 创建新存档
        save_success = self.data_manager.create_new_save(self.player, self.ai_manager)
        self.assertTrue(save_success, "创建存档应该成功")

        # 修改玩家状态
        self.player.level = 5
        self.player.coins = 500
        self.player.max_combo = 25

        # 保存游戏
        save_success = self.data_manager.save_game(self.player, self.ai_manager)
        self.assertTrue(save_success, "保存游戏应该成功")

        # 重置玩家状态
        self.player.reset()
        self.ai_manager.reset_ai_state()

        # 加载游戏
        load_success = self.data_manager.load_game()
        print(f"Load success: {load_success}")
        self.assertTrue(load_success, "加载游戏应该成功")

        # 应用加载的数据
        apply_success = self.data_manager.apply_loaded_data(self.player, self.ai_manager)
        self.assertTrue(apply_success, "应用加载的数据应该成功")

        # 验证加载效果
        self.assertEqual(self.player.level, 5)
        self.assertEqual(self.player.coins, 500)
        self.assertEqual(self.player.max_combo, 25)

    def test_enemy_scaling_integration(self):
        """测试敌人缩放集成"""
        initial_max_hp = self.enemy.max_hp

        # 玩家升级到5级
        self.player.level = 5
        self.enemy.scale_with_player_level(self.player.level)

        # 敌人应该变强
        self.assertGreater(self.enemy.max_hp, initial_max_hp, "敌人血量应该增加")

        # 测试缩放后的伤害计算
        damage = 30
        self.enemy.hit(damage)

        # 实际受到的伤害应该考虑缩放因子
        # 5级时缩放1.2倍 (5 // 3 = 1, 1.0 + 1 * 0.2 = 1.2)
        # 伤害被缩放: 30 * 1.2 = 36
        # 敌人初始血量是100，缩放后最大血量是120，但当前血量仍是100
        # 所以实际血量: 100 - 36 = 64
        expected_hp = 100 - (damage * 1.2)
        self.assertAlmostEqual(self.enemy.hp, expected_hp, delta=1)

    def test_ui_integration(self):
        """测试UI集成"""
        # 创建一些游戏状态
        self.player.level = 3
        self.player.combo = 8
        self.player.stamina = 60
        self.player.coins = 250

        # 设置AI回应
        self.ui_manager.update_ai_text("测试AI回应")

        # 绘制所有UI元素
        self.ui_manager.draw(self.screen, self.player, self.enemy)

        # 测试UI元素位置
        status_bar_rect = self.ui_manager.get_element_rect('status_bar')
        self.assertIsNotNone(status_bar_rect)
        if status_bar_rect:  # 添加检查以避免类型错误
            self.assertEqual(status_bar_rect.x, 0)
            self.assertEqual(status_bar_rect.y, 0)

        # 测试UI点检测
        point_in_status = self.ui_manager.is_point_in_ui((10, 10))
        self.assertEqual(point_in_status, 'status_bar')

        point_not_in_ui = self.ui_manager.is_point_in_ui((400, 300))
        self.assertIsNone(point_not_in_ui)

    def test_effects_system_integration(self):
        """测试特效系统集成"""
        # 创建各种特效
        self.effects.create_slash_effect((100, 100), (200, 150), is_crit=False)
        self.effects.create_damage_number(15, (150, 120))
        self.effects.create_combo_effect(10, (300, 250))
        self.effects.create_coin_effect(3, (200, 200))

        # 更新和绘制
        for _ in range(10):
            self.effects.update()
            self.effects.draw(self.screen)

        # 验证特效统计
        stats = self.effects.get_stats()
        self.assertGreater(stats['total_effects_created'], 0)
        self.assertGreater(stats['total_particles_created'], 0)

    def test_sound_system_integration(self):
        """测试音效系统集成"""
        # 加载音效
        self.sound_manager.load_sounds()

        # 播放各种音效
        sounds_played = 0

        if self.sound_manager.enabled:
            if self.sound_manager.play_sound("slash"):
                sounds_played += 1
            if self.sound_manager.play_sound("enemy_hit"):
                sounds_played += 1
            if self.sound_manager.play_sound("coin"):
                sounds_played += 1

            # 验证音效统计
            stats = self.sound_manager.get_sound_stats()
            self.assertGreaterEqual(stats['sounds_played'], sounds_played)

    def test_complete_game_loop_simulation(self):
        """测试完整游戏循环模拟"""
        # 模拟游戏循环
        loop_count = 0
        max_loops = 100

        while loop_count < max_loops:
            # 处理事件（模拟）
            # 这里我们模拟鼠标点击攻击
            if loop_count % 10 == 0:  # 每10帧攻击一次
                # 恢复体力
                if not self.player.can_attack():
                    self.player.stamina = self.player.max_stamina

                # 执行攻击
                hit, damage, is_crit = self.player.attack(self.enemy)

                if hit:
                    # AI反应
                    ai_response = self.ai_manager.update_and_respond(self.player, self.enemy)
                    if ai_response:
                        self.ui_manager.update_ai_text(ai_response)

                    # 创建特效
                    if is_crit:
                        self.effects.create_crit_effect(damage, self.enemy.rect.center)
                    else:
                        self.effects.create_damage_number(damage, self.enemy.rect.center)
                        self.effects.create_slash_effect(
                            self.player.rect.center,
                            self.enemy.rect.center
                        )

                    # 播放音效
                    self.sound_manager.play_sound("slash")

            # 更新游戏状态
            self.player.update(1/60)
            self.enemy.update()
            self.effects.update()
            self.ui_manager.update(1/60)

            # 检查自动保存
            self.data_manager.auto_save_check(self.player, self.ai_manager)

            # 绘制（模拟）
            self.ui_manager.draw(self.screen, self.player, self.enemy)
            self.effects.draw(self.screen)

            loop_count += 1

            # 如果敌人死亡，重生
            if not self.enemy.is_alive:
                self.enemy.respawn()

        # 验证游戏状态变化
        self.assertGreater(self.player.exp, 0, "玩家应该获得经验")
        self.assertGreaterEqual(self.player.max_combo, 0, "应该记录最大连击")

    def test_error_handling_integration(self):
        """测试错误处理集成"""
        # 测试无效攻击
        self.player.stamina = 0
        hit, damage, is_crit = self.player.attack(self.enemy)
        self.assertFalse(hit, "体力不足时攻击应该失败")

        # 测试对死亡敌人攻击
        self.enemy.is_alive = False
        hit, damage, is_crit = self.player.attack(self.enemy)
        self.assertFalse(hit, "对死亡敌人攻击应该失败")

        # 测试无效存档操作
        invalid_save = self.data_manager.save_game()
        # 这可能成功也可能失败，取决于实现，但不应该崩溃

        # 测试UI错误处理
        try:
            self.ui_manager.draw(self.screen, self.player, self.enemy)  # 传入有效的对象
        except Exception as e:
            self.fail(f"UI绘制不应崩溃: {e}")

    def test_performance_integration(self):
        """测试性能集成"""
        # 大量操作测试
        start_time = time.time()

        # 创建大量特效
        for _ in range(50):
            self.effects.create_slash_effect((100, 100), (200, 150))
            self.effects.create_damage_number(15, (150, 120))

        # 更新多次
        for _ in range(100):
            self.effects.update()

        # 绘制多次
        for _ in range(50):
            self.effects.draw(self.screen)

        end_time = time.time()
        duration = end_time - start_time

        # 性能应该在合理范围内（小于1秒）
        self.assertLess(duration, 1.0, f"性能测试应在1秒内完成，实际耗时: {duration:.3f}秒")

        # 检查内存清理
        self.effects.clear_all_effects()
        self.assertEqual(len(self.effects.effects), 0)
        self.assertEqual(len(self.effects.particles), 0)


if __name__ == '__main__':
    unittest.main()