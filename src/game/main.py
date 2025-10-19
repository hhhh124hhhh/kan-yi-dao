"""
游戏主类模块
包含游戏的核心循环和状态管理
"""

import pygame
import sys
import os
import time
import logging
from typing import Optional
from pathlib import Path

# 导入游戏组件
from .player import Player
from .enemy import StrawDummy
from .ui import UIManager
from .sound_manager import SoundManager
from .data_manager import DataManager
from .game_constants import DebugConstants, validate_player_attributes, validate_enemy_attributes

# 导入字体和文本系统
from .font_manager import get_chinese_text_font
from .text_localization import get_localization, TextType

# 导入AI管理器
from ai.ai_manager import AIManager

# 导入配置
from config.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SCREEN_TITLE,
    DEFAULT_FULLSCREEN, DEFAULT_VSYNC, DEFAULT_SHOW_FPS,
    DEFAULT_AI_TYPE
)


class Game:
    """游戏主类"""

    def __init__(self, ai_type: str = None):
        """初始化游戏

        Args:
            ai_type: AI类型，如果不指定则使用配置中的默认类型
        """
        # 设置日志
        self._setup_logging()

        # 初始化pygame
        self._init_pygame()

        # 创建游戏组件
        self._create_game_components(ai_type or DEFAULT_AI_TYPE)

        # 验证核心游戏对象的属性完整性
        self._validate_game_objects()

        # 游戏状态
        self.running = True
        self.paused = False
        self.clock = pygame.time.Clock()
        self.dt = 0

        # 调试信息
        self.debug_info = {}
        self.show_debug = False

        self.logger.info("游戏初始化完成")

    def _setup_logging(self):
        """设置日志系统"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "game.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _init_pygame(self):
        """初始化pygame"""
        pygame.init()
        pygame.mixer.init()

        # 设置窗口
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        if DEFAULT_VSYNC:
            flags |= pygame.DOUBLEBUF

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            flags=flags
        )
        pygame.display.set_caption(SCREEN_TITLE)

        # 设置图标（如果有的话）
        self._set_window_icon()

        self.logger.info(f"pygame初始化完成 - 屏幕尺寸: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    def _set_window_icon(self):
        """设置窗口图标"""
        # 这里可以设置游戏图标
        # icon_surface = pygame.image.load("assets/images/icon.png")
        # pygame.display.set_icon(icon_surface)
        pass

    def _create_game_components(self, ai_type: str):
        """创建游戏组件"""
        # 玩家
        self.player = Player()

        # 敌人
        self.enemy = StrawDummy()

        # AI管理器
        self.ai_manager = AIManager(ai_type, enable_learning=True)

        # 特效管理器
        from .effects import EffectManager
        self.effects = EffectManager(SCREEN_WIDTH, SCREEN_HEIGHT)

        # UI管理器
        self.ui_manager = UIManager(SCREEN_WIDTH, SCREEN_HEIGHT)

        # 音效管理器
        self.sound_manager = SoundManager()
        self.sound_manager.load_sounds()

        # 数据管理器
        self.data_manager = DataManager()

        # 尝试加载存档
        self._try_load_save()

    def _try_load_save(self):
        """尝试加载存档"""
        if self.data_manager.load_game():
            self.data_manager.apply_loaded_data(self.player, self.ai_manager)
            self.logger.info("游戏存档加载成功")
        else:
            # 创建新存档
            self.data_manager.create_new_save(self.player, self.ai_manager)
            self.logger.info("创建新游戏存档")

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)

            elif event.type == pygame.KEYUP:
                self._handle_keyup(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mousedown(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouseup(event)

    def _handle_keydown(self, event):
        """处理键盘按下事件"""
        if event.key == pygame.K_ESCAPE:
            self.running = False

        elif event.key == pygame.K_p:
            self.paused = not self.paused
            self.logger.info(f"游戏{'暂停' if self.paused else '继续'}")

        elif event.key == pygame.K_F1:
            self.show_debug = not self.show_debug
            self.logger.info(f"调试信息显示: {self.show_debug}")

        elif event.key == pygame.K_F5:
            self._quick_save()

        elif event.key == pygame.K_F9:
            self._load_save()

        elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self._reset_game()

    def _handle_keyup(self, event):
        """处理键盘释放事件"""
        pass

    def _handle_mousedown(self, event):
        """处理鼠标按下事件"""
        if not self.paused and event.button == 1:  # 左键攻击
            self._handle_attack(event.pos)

    def _handle_mouseup(self, event):
        """处理鼠标释放事件"""
        pass

    def _handle_attack(self, mouse_pos):
        """处理攻击"""
        # 检查是否可以攻击
        if not self.player.can_attack():
            # 体力不足提示
            if self.player.stamina < 30:
                self.effects.create_stamina_warning(self.player.rect.center)
                self.sound_manager.play_sound("stamina_low")
            return

        # 执行攻击
        hit, damage, is_crit = self.player.attack(self.enemy)

        if hit:
            # 创建砍击特效
            self.effects.create_slash_effect(
                self.player.rect.center,
                self.enemy.rect.center,
                is_crit=is_crit
            )

            # 创建伤害数字
            self.effects.create_damage_number(damage, self.enemy.rect.center, is_crit=is_crit)

            # 暴击特效
            if is_crit:
                self.effects.create_crit_effect(damage, self.enemy.rect.center)
                self.sound_manager.play_sound("crit")

            # 连击特效
            if self.player.combo >= 5:
                self.effects.create_combo_effect(self.player.combo, self.enemy.rect.center)
                if self.player.combo >= 10:
                    self.sound_manager.play_sound("combo")

            # 击败特效
            if not self.enemy.is_alive:
                self.effects.create_coin_effect(5, self.enemy.rect.center)
                self.sound_manager.play_sound("enemy_defeat")
                self.player.add_coins(5)

            # 生成经验特效
            exp_gained = damage
            if is_crit:
                exp_gained = int(exp_gained * 1.5)
            self.effects.create_exp_gain_effect(exp_gained, self.enemy.rect.center)

            # AI反应
            ai_response = self.ai_manager.update_and_respond(self.player, self.enemy)
            if ai_response:
                self.ui_manager.update_ai_text(ai_response)

            # 播放音效
            self.sound_manager.play_sound("slash")

        else:
            # 攻击失败（通常不可能）
            self.sound_manager.play_sound("error")

    def _quick_save(self):
        """快速保存"""
        if self.data_manager.save_game(self.player, self.ai_manager):
            self.logger.info("快速保存成功")
        else:
            self.logger.warning("快速保存失败")

    def _load_save(self):
        """加载存档"""
        if self.data_manager.load_game():
            self.data_manager.apply_loaded_data(self.player, self.ai_manager)
            self.logger.info("存档加载成功")
        else:
            self.logger.warning("存档加载失败")

    def _reset_game(self):
        """重置游戏"""
        self.player.reset()
        self.enemy.reset()
        self.ai_manager.reset_ai_state()
        self.effects.clear_all_effects()
        self.ui_manager.clear_ai_text()
        self.logger.info("游戏已重置")

    def update(self):
        """更新游戏状态"""
        if not self.paused:
            # 更新游戏对象
            self.player.update(self.dt)
            self.enemy.update()
            self.effects.update(self.dt)
            self.ui_manager.update(self.dt)

            # 更新AI
            self.ai_manager.update_and_respond(self.player, self.enemy)

            # 自动保存检查
            self.data_manager.auto_save_check(self.player, self.ai_manager)

            # 更新调试信息
            self._update_debug_info()

    def _update_debug_info(self):
        """更新调试信息"""
        # 使用标准化的调试字段名
        self.debug_info = {
            DebugConstants.DEBUG_FIELDS["FPS"]: int(self.clock.get_fps()),
            DebugConstants.DEBUG_FIELDS["DELTA_TIME"]: f"{self.dt:.3f}",
            DebugConstants.DEBUG_FIELDS["PLAYER_LEVEL"]: self.player.level,
            DebugConstants.DEBUG_FIELDS["PLAYER_STAMINA"]: f"{self.player.stamina}/{self.player.max_stamina}",
            DebugConstants.DEBUG_FIELDS["ENEMY_HP"]: f"{self.enemy.hp}/{self.enemy.max_hp}",
            DebugConstants.DEBUG_FIELDS["COMBO"]: self.player.combo,
            DebugConstants.DEBUG_FIELDS["AI_MOOD"]: self.ai_manager.get_current_mood().value,
            DebugConstants.DEBUG_FIELDS["EFFECTS_COUNT"]: len(self.effects.effects),
            DebugConstants.DEBUG_FIELDS["PARTICLES_COUNT"]: len(self.effects.particles)
        }

    def render(self):
        """渲染游戏画面"""
        # 清屏
        self.screen.fill((20, 20, 20))

        # 绘制游戏对象
        self.enemy.draw(self.screen)
        self.player.draw(self.screen)

        # 绘制特效（在游戏对象之上）
        self.effects.draw(self.screen)

        # 绘制UI（在所有内容之上）
        self.ui_manager.draw(
            self.screen,
            self.player,
            self.enemy,
            self.debug_info if self.show_debug else None
        )

        # 暂停提示
        if self.paused:
            self._draw_pause_overlay()

        pygame.display.flip()

    def _draw_pause_overlay(self):
        """绘制暂停覆盖层"""
        # 获取文本本地化系统
        localization = get_localization()

        # 半透明黑色覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # 暂停文字
        pause_title = localization.get_ui_text('pause_title')
        text = localization.render_text(pause_title, 48, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

        # 操作提示
        continue_text = localization.get_ui_text('pause_resume')
        exit_text = localization.get_ui_text('pause_exit')
        hint_text = f"{continue_text}, {exit_text}"

        text_small = localization.render_text(hint_text, 24, (200, 200, 200))
        text_rect_small = text_small.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(text_small, text_rect_small)

    def run(self):
        """运行游戏主循环"""
        self.logger.info("游戏开始运行")

        try:
            while self.running:
                self.dt = self.clock.tick(FPS) / 1000.0  # 转换为秒

                self.handle_events()
                self.update()
                self.render()

        except KeyboardInterrupt:
            self.logger.info("游戏被用户中断")
        except Exception as e:
            self.logger.error(f"游戏运行时发生错误: {e}")
            raise
        finally:
            self._cleanup()

    def _cleanup(self):
        """清理资源"""
        # 保存游戏
        try:
            if hasattr(self, 'data_manager') and self.data_manager:
                self.data_manager.save_game(self.player, self.ai_manager)
                self.logger.info("游戏已保存")
        except Exception as e:
            self.logger.error(f"保存游戏时出错: {e}")

        # 清理音效
        try:
            if hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager.cleanup()
        except Exception as e:
            self.logger.error(f"清理音效时出错: {e}")

    def _validate_game_objects(self):
        """
        验证核心游戏对象的属性完整性

        Raises:
            AttributeError: 如果游戏对象缺少必需属性
        """
        # 验证Player对象
        player_validation = validate_player_attributes(self.player)
        if not player_validation["is_valid"]:
            missing_attrs = player_validation["missing_attributes"]
            error_msg = f"Player对象缺少必需属性: {', '.join(missing_attrs)}"
            self.logger.error(error_msg)
            raise AttributeError(error_msg)

        # 验证Enemy对象
        enemy_validation = validate_enemy_attributes(self.enemy)
        if not enemy_validation["is_valid"]:
            missing_attrs = enemy_validation["missing_attributes"]
            error_msg = f"Enemy对象缺少必需属性: {', '.join(missing_attrs)}"
            self.logger.error(error_msg)
            raise AttributeError(error_msg)

        self.logger.info("游戏对象属性验证通过")

    def cleanup(self):
        """清理游戏资源"""
        # 保存游戏
        try:
            if hasattr(self, 'data_manager') and self.data_manager:
                self.data_manager.save_game(self.player, self.ai_manager)
                self.logger.info("游戏已保存")
        except Exception as e:
            self.logger.error(f"保存游戏时出错: {e}")

        # 清理音效
        try:
            if hasattr(self, 'sound_manager') and self.sound_manager:
                self.sound_manager.cleanup()
        except Exception as e:
            self.logger.error(f"清理音效时出错: {e}")

        # 清理其他资源
        try:
            if hasattr(self, 'ai_manager') and self.ai_manager:
                self.ai_manager.reset_ai_state()
        except Exception as e:
            self.logger.error(f"清理AI时出错: {e}")

        pygame.quit()
        self.logger.info("游戏退出")