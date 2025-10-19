import pygame
import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# 初始化Pygame字体模块
pygame.init()
pygame.font.init()

# 使用相对导入
from src.game.font_manager import FontManager
from src.game.text_localization import TextLocalization
from src.game.effects import EffectManager
from src.game.enemy import StrawDummy
from src.game.ui import UIManager


class TestChineseTextRendering(unittest.TestCase):
    """测试中文文本渲染功能"""

    def setUp(self):
        """测试初始化"""
        # 初始化各个系统
        self.font_manager = FontManager()
        self.localization = TextLocalization()
        self.effect_manager = EffectManager()
        self.ui_manager = UIManager()
        
        # 创建测试敌人
        self.enemy = StrawDummy()

    def tearDown(self):
        """测试清理"""
        pass

    def test_font_manager_chinese_rendering(self):
        """测试字体管理器中文渲染"""
        # 测试获取中文字体
        font = self.font_manager.get_chinese_font(24)
        self.assertIsNotNone(font)
        
        # 测试中文文本渲染
        test_text = "测试中文渲染"
        try:
            # 检查字体是否可以渲染文本（不实际渲染到surface）
            self.assertTrue(hasattr(font, 'render'))
        except Exception as e:
            self.fail(f"中文字体渲染失败: {e}")

    def test_localization_chinese_rendering(self):
        """测试本地化系统中文渲染"""
        # 测试UI文本渲染
        ui_text = self.localization.get_ui_text('level')
        self.assertIn('等级', ui_text)
        
        # 测试游戏玩法文本渲染
        gameplay_text = self.localization.get_gameplay_text('level_up')
        self.assertIn('升级', gameplay_text)
        
        # 测试敌人文本渲染
        enemy_text = self.localization.get_enemy_text('strawman')
        self.assertIn('稻草人', enemy_text)

    def test_effect_manager_chinese_rendering(self):
        """测试特效管理器中文渲染"""
        # 测试伤害数字创建（不实际渲染）
        try:
            # 创建一个简单的伤害数字特效
            self.effect_manager.create_damage_number(100, (100, 100))
            
            # 检查特效是否创建成功
            self.assertGreater(len(self.effect_manager.effects), 0)
            
            # 更新特效
            self.effect_manager.update()
            
            # 验证特效数据正确性
            damage_effect = self.effect_manager.effects[0]
            self.assertEqual(damage_effect.type.name, 'DAMAGE_NUMBER')
        except Exception as e:
            self.fail(f"特效中文渲染测试失败: {e}")

    def test_enemy_name_rendering(self):
        """测试敌人名称渲染"""
        try:
            # 检查敌人名称是否正确
            self.assertEqual(self.enemy.name, "稻草人")
            
            # 检查敌人类型
            self.assertEqual(self.enemy.enemy_type.value, "straw_dummy")
        except Exception as e:
            self.fail(f"敌人名称渲染测试失败: {e}")

    def test_ui_chinese_rendering(self):
        """测试UI中文渲染"""
        # 创建模拟玩家对象
        player = Mock()
        player.level = 1
        player.attack_power = 10
        player.weapon_tier = 1
        player.coins = 100
        player.exp = 50
        player.next_exp = 100
        player.stamina = 50
        player.max_stamina = 100
        player.combo = 5
        player.just_leveled_up = False
        player.level_up_timer = 0
        
        try:
            # 测试UI管理器功能（不实际渲染）
            # 验证字体系统初始化
            self.assertIn('small', self.ui_manager.fonts)
            self.assertIn('medium', self.ui_manager.fonts)
            self.assertIn('large', self.ui_manager.fonts)
            self.assertIn('huge', self.ui_manager.fonts)
            
            # 测试本地化系统
            self.assertIsNotNone(self.ui_manager.localization)
        except Exception as e:
            self.fail(f"UI中文渲染测试失败: {e}")

    def test_all_chinese_fonts_available(self):
        """测试所有中文字体可用性"""
        # 检查字体管理器是否检测到中文字体
        available_fonts = self.font_manager.available_chinese_fonts
        self.assertIsInstance(available_fonts, list)
        
        # 检查字体信息
        font_info = self.font_manager.get_font_info()
        self.assertIn('available_chinese_fonts', font_info)
        self.assertIn('cached_fonts_count', font_info)

    def test_text_localization_completeness(self):
        """测试文本本地化完整性"""
        # 验证文本数据库完整性
        validation_result = self.localization.validate_text_completeness()
        self.assertTrue(validation_result['is_complete'])
        
        # 获取文本统计信息
        stats = self.localization.get_text_statistics()
        self.assertGreater(stats['total_texts'], 0)
        self.assertGreater(stats['total_text_types'], 0)


if __name__ == '__main__':
    unittest.main()