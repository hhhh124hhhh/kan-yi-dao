import pygame
import math
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class UIElement:
    """UI元素数据结构"""
    rect: pygame.Rect
    element_type: str
    data: Dict[str, Any]
    visible: bool = True
    enabled: bool = True


class UIManager:
    """UI管理器 - 负责绘制所有用户界面元素"""

    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 字体缓存
        self.fonts = {
            'small': pygame.font.Font(None, 16),
            'medium': pygame.font.Font(None, 24),
            'large': pygame.font.Font(None, 32),
            'huge': pygame.font.Font(None, 48)
        }

        # UI元素位置（按UI.md规范）
        self.status_bar_rect = pygame.Rect(0, 0, screen_width, 40)
        self.ai_dialog_rect = pygame.Rect(100, 80, 600, 60)
        self.hp_bar_rect = pygame.Rect(350, 180, 100, 10)
        self.bottom_tips_rect = pygame.Rect(200, 570, 400, 30)

        # UI状态
        self.current_ai_text = ""
        self.ai_text_timer = 0
        self.ai_text_max_duration = 300  # 5秒

        # 动画相关
        self.animations = []
        self.pulsing_elements = {}

        # 颜色定义
        self.colors = {
            'background': (40, 40, 40),
            'panel': (60, 60, 60),
            'border': (100, 100, 100),
            'text': (255, 255, 255),
            'accent': (255, 200, 100),
            'success': (100, 255, 100),
            'warning': (255, 200, 100),
            'danger': (255, 100, 100),
            'hp_bar': (200, 50, 50),
            'hp_bar_bg': (100, 30, 30),
            'stamina_bar': (100, 150, 255),
            'stamina_bar_bg': (50, 75, 127),
            'exp_bar': (100, 200, 100),
            'exp_bar_bg': (50, 100, 50),
            'ai_dialog_bg': (50, 50, 50),
            'combo_text': (255, 200, 100)
        }

        # UI元素列表
        self.ui_elements = []

        # 统计数据
        self.stats = {
            'frames_rendered': 0,
            'last_render_time': 0,
            'avg_render_time': 0.0
        }

    def draw_status_bar(self, screen: pygame.Surface, player) -> None:
        """
        绘制顶部状态栏

        Args:
            screen: 屏幕对象
            player: 玩家对象
        """
        # 背景
        pygame.draw.rect(screen, self.colors['background'], self.status_bar_rect)
        pygame.draw.rect(screen, self.colors['border'], self.status_bar_rect, 2)

        # 等级信息
        level_text = self.fonts['medium'].render(f"[等级] Lv.{player.level}", True, self.colors['text'])
        screen.blit(level_text, (10, 10))

        # 攻击力信息
        power_text = self.fonts['medium'].render(f"[攻击力] {player.attack_power}", True, self.colors['accent'])
        screen.blit(power_text, (150, 10))

        # 武器等级
        weapon_text = self.fonts['medium'].render(f"[武器] Lv.{player.weapon_tier}", True, self.colors['text'])
        screen.blit(power_text, (300, 10))

        # 经验条
        exp_ratio = player.exp / player.next_exp
        exp_bar_width = int(150 * exp_ratio)
        exp_bar_rect = pygame.Rect(450, 15, 150, 10)

        # 经验条背景
        pygame.draw.rect(screen, self.colors['exp_bar_bg'], exp_bar_rect)
        # 经验条
        pygame.draw.rect(screen, self.colors['exp_bar'], (exp_bar_rect.x, exp_bar_rect.y, exp_bar_width, exp_bar_rect.height))
        # 边框
        pygame.draw.rect(screen, self.colors['border'], exp_bar_rect, 1)

        # 经验百分比
        exp_percent = int(exp_ratio * 100)
        exp_text = self.fonts['small'].render(f"{exp_percent}%", True, self.colors['text'])
        screen.blit(exp_text, (610, 17))

        # 金币信息
        coins_text = self.fonts['medium'].render(f"💰 {player.coins}", True, (255, 215, 0))
        screen.blit(coins_text, (680, 10))

    def draw_ai_dialog(self, screen: pygame.Surface, ai_text: str) -> None:
        """
        绘制AI对话区域

        Args:
            screen: 屏幕对象
            ai_text: AI对话文本
        """
        if not ai_text:
            return

        # 背景
        dialog_rect = self.ai_dialog_rect.copy()
        pygame.draw.rect(screen, self.colors['ai_dialog_bg'], dialog_rect)
        pygame.draw.rect(screen, self.colors['border'], dialog_rect, 2)

        # 分行处理长文本
        max_width = dialog_rect.width - 20
        lines = self._wrap_text(ai_text, max_width)

        # 绘制文本
        y_offset = 10
        for line in lines:
            text = self.fonts['medium'].render(f"💬 {line}", True, (200, 255, 200))
            text_rect = text.get_rect(x=dialog_rect.x + 10, y=dialog_rect.y + y_offset)
            screen.blit(text, text_rect)
            y_offset += 25

    def _wrap_text(self, text: str, max_width: int) -> list:
        """文本换行处理"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            text_surface = self.fonts['medium'].render(test_line, True, (255, 255, 255))

            if text_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # 单词太长，强制换行
                    lines.append(word)
                    current_line = []

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def draw_hp_bar(self, screen: pygame.Surface, enemy) -> None:
        """
        绘制敌人血条

        Args:
            screen: 屏幕对象
            enemy: 敌人对象
        """
        if not enemy.is_alive:
            return

        # 血条位置（在敌人上方）
        bar_width = 80
        bar_height = 8
        bar_x = enemy.rect.centerx - bar_width // 2
        bar_y = enemy.rect.top - 20

        # 背景
        hp_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, self.colors['hp_bar_bg'], hp_bg_rect)

        # 血量
        hp_percent = enemy.get_hp_percentage()
        hp_width = int(bar_width * hp_percent)
        hp_rect = pygame.Rect(bar_x, bar_y, hp_width, bar_height)

        # 根据血量百分比选择颜色
        if hp_percent > 0.6:
            hp_color = self.colors['success']
        elif hp_percent > 0.3:
            hp_color = self.colors['warning']
        else:
            hp_color = self.colors['danger']

        pygame.draw.rect(screen, hp_color, hp_rect)

        # 边框
        pygame.draw.rect(screen, self.colors['border'], hp_bg_rect, 1)

        # HP文字
        hp_text = self.fonts['small'].render(f"{enemy.hp}/{enemy.max_hp}", True, self.colors['text'])
        hp_text_rect = hp_text.get_rect(centerx=enemy.rect.centerx, y=bar_y - 15)
        screen.blit(hp_text, hp_text_rect)

    def draw_combo_counter(self, screen: pygame.Surface, player) -> None:
        """
        绘制连击计数器

        Args:
            screen: 屏幕对象
            player: 玩家对象
        """
        if player.combo <= 1:
            return

        # 连击文字
        combo_text = f"x{player.combo}"
        font = self.fonts['huge'] if player.combo >= 10 else self.fonts['large']

        # 添加脉冲效果
        scale = 1.0 + 0.1 * math.sin(time.time() * 5)
        if player.combo >= 20:
            scale *= 1.2

        text = font.render(combo_text, True, self.colors['combo_text'])

        if scale != 1.0:
            scaled_size = (int(text.get_width() * scale), int(text.get_height() * scale))
            text = pygame.transform.scale(text, scaled_size)

        # 位置（屏幕中央偏下）
        text_rect = text.get_rect(centerx=screen.get_width() // 2, y=450)
        screen.blit(text, text_rect)

        # 连击提示
        if player.combo >= 10:
            tip_text = f"连击x{player.combo}! 伤害+{int((player.combo // 10) * 10)}%"
            tip_surface = self.fonts['medium'].render(tip_text, True, self.colors['accent'])
            tip_rect = tip_surface.get_rect(centerx=screen.get_width() // 2, y=text_rect.bottom + 10)
            screen.blit(tip_surface, tip_rect)

    def draw_bottom_tips(self, screen: pygame.Surface) -> None:
        """
        绘制底部操作提示

        Args:
            screen: 屏幕对象
        """
        tips = "[左键] 挥刀 | [右键] 切换武器 | [ESC] 退出游戏"
        text = self.fonts['small'].render(tips, True, (150, 150, 150))
        text_rect = text.get_rect(centerx=screen.get_width() // 2, y=self.bottom_tips_rect.y)
        screen.blit(text, text_rect)

    def draw_stamina_bar(self, screen: pygame.Surface, player) -> None:
        """
        绘制体力条

        Args:
            screen: 屏幕对象
            player: 玩家对象
        """
        # 体力条位置（左下角）
        bar_width = 200
        bar_height = 15
        bar_x = 10
        bar_y = screen.get_height() - 40

        # 背景
        stamina_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, self.colors['stamina_bar_bg'], stamina_bg_rect)

        # 体力值
        stamina_percent = player.stamina / player.max_stamina
        stamina_width = int(bar_width * stamina_percent)
        stamina_rect = pygame.Rect(bar_x, bar_y, stamina_width, bar_height)

        # 根据体力百分比选择颜色
        if stamina_percent > 0.5:
            stamina_color = self.colors['stamina_bar']
        elif stamina_percent > 0.25:
            stamina_color = self.colors['warning']
        else:
            stamina_color = self.colors['danger']

        pygame.draw.rect(screen, stamina_color, stamina_rect)

        # 边框
        pygame.draw.rect(screen, self.colors['border'], stamina_bg_rect, 1)

        # 体力文字
        stamina_text = f"体力: {player.stamina}/{player.max_stamina}"
        text = self.fonts['small'].render(stamina_text, True, self.colors['text'])
        text_rect = text.get_rect(x=bar_x + bar_width + 10, centery=bar_y + bar_height // 2)
        screen.blit(text, text_rect)

        # 体力不足警告
        if stamina_percent < 0.3:
            warning_text = "体力不足!"
            warning_surface = self.fonts['medium'].render(warning_text, True, self.colors['danger'])
            warning_rect = warning_surface.get_rect(centerx=screen.get_width() // 2, y=bar_y - 30)
            screen.blit(warning_surface, warning_rect)

    def draw_level_up_notification(self, screen: pygame.Surface, player) -> None:
        """
        绘制升级提示

        Args:
            screen: 屏幕对象
            player: 玩家对象
        """
        if not player.just_leveled_up or player.level_up_timer <= 0:
            return

        # 计算透明度
        alpha = min(255, player.level_up_timer * 4)

        # 升级文字
        level_text = f"LEVEL UP! Lv.{player.level}"
        font = self.fonts['huge']
        text = font.render(level_text, True, (255, 215, 0))

        # 创建透明surface
        text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        text_surface.fill((0, 0, 0, 0))
        text_surface.blit(text, (0, 0))

        # 位置（屏幕中央）
        text_rect = text_surface.get_rect(centerx=screen.get_width() // 2, y=200)
        screen.blit(text_surface, text_rect)

        # 属性提升提示
        stats_text = f"攻击力+5 体力上限+10 暴击率+2%"
        stats_surface = self.fonts['medium'].render(stats_text, True, (255, 255, 255))
        stats_rect = stats_surface.get_rect(centerx=screen.get_width() // 2, y=text_rect.bottom + 20)
        screen.blit(stats_surface, stats_rect)

    def draw_crit_notification(self, screen: pygame.Surface, pos: Tuple[int, int]) -> None:
        """
        绘制暴击提示

        Args:
            screen: 屏幕对象
            pos: 位置
        """
        crit_text = "暴击!"
        text = self.fonts['large'].render(crit_text, True, (255, 50, 50))
        text_rect = text.get_rect(center=pos)
        screen.blit(text, text_rect)

    def draw_debug_info(self, screen: pygame.Surface, debug_data: Dict[str, Any]) -> None:
        """
        绘制调试信息

        Args:
            screen: 屏幕对象
            debug_data: 调试数据
        """
        y_offset = 50
        for key, value in debug_data.items():
            text = self.fonts['small'].render(f"{key}: {value}", True, (200, 200, 200))
            screen.blit(text, (10, y_offset))
            y_offset += 20

    def update_ai_text(self, ai_text: str) -> None:
        """
        更新AI对话文本

        Args:
            ai_text: AI对话文本
        """
        self.current_ai_text = ai_text
        self.ai_text_timer = self.ai_text_max_duration

    def update(self, dt: float) -> None:
        """
        更新UI状态

        Args:
            dt: 时间增量
        """
        # 更新AI文本计时器
        if self.ai_text_timer > 0:
            self.ai_text_timer -= 1
            if self.ai_text_timer <= 0:
                self.current_ai_text = ""

        # 更新动画
        self._update_animations(dt)

        # 更新脉冲元素
        self._update_pulsing_elements(dt)

    def _update_animations(self, dt: float) -> None:
        """更新动画"""
        for animation in self.animations[:]:
            animation['timer'] -= 1
            if animation['timer'] <= 0:
                self.animations.remove(animation)

    def _update_pulsing_elements(self, dt: float) -> None:
        """更新脉冲元素"""
        current_time = time.time()
        for key in self.pulsing_elements:
            self.pulsing_elements[key] = math.sin(current_time * 3) * 0.1 + 1.0

    def add_animation(self, animation_type: str, duration: int, data: Dict[str, Any]) -> None:
        """
        添加动画

        Args:
            animation_type: 动画类型
            duration: 持续时间
            data: 动画数据
        """
        animation = {
            'type': animation_type,
            'timer': duration,
            'data': data
        }
        self.animations.append(animation)

    def get_ui_stats(self) -> Dict[str, Any]:
        """获取UI统计信息"""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """重置统计数据"""
        self.stats = {
            'frames_rendered': 0,
            'last_render_time': 0,
            'avg_render_time': 0.0
        }

    def draw(self, screen: pygame.Surface, player, enemy, debug_data: Optional[Dict[str, Any]] = None) -> None:
        """
        绘制所有UI元素

        Args:
            screen: 屏幕对象
            player: 玩家对象
            enemy: 敌人对象
            debug_data: 调试数据
        """
        start_time = time.time()

        # 按层级绘制UI元素
        self.draw_status_bar(screen, player)
        self.draw_hp_bar(screen, enemy)
        self.draw_stamina_bar(screen, player)
        self.draw_ai_dialog(screen, self.current_ai_text)
        self.draw_combo_counter(screen, player)
        self.draw_bottom_tips(screen)
        self.draw_level_up_notification(screen, player)

        # 调试信息（可选）
        if debug_data:
            self.draw_debug_info(screen, debug_data)

        # 更新统计
        render_time = time.time() - start_time
        self.stats['frames_rendered'] += 1
        total_frames = self.stats['frames_rendered']
        self.stats['avg_render_time'] = (self.stats['avg_render_time'] * (total_frames - 1) + render_time) / total_frames
        self.stats['last_render_time'] = render_time

    def set_colors(self, color_scheme: Dict[str, Tuple[int, int, int]]) -> None:
        """
        设置颜色方案

        Args:
            color_scheme: 颜色方案
        """
        self.colors.update(color_scheme)

    def get_element_rect(self, element_name: str) -> Optional[pygame.Rect]:
        """
        获取UI元素矩形

        Args:
            element_name: 元素名称

        Returns:
            元素矩形
        """
        rect_map = {
            'status_bar': self.status_bar_rect,
            'ai_dialog': self.ai_dialog_rect,
            'hp_bar': self.hp_bar_rect,
            'bottom_tips': self.bottom_tips_rect
        }
        return rect_map.get(element_name)

    def is_point_in_ui(self, pos: Tuple[int, int]) -> Optional[str]:
        """
        检查点是否在UI区域内

        Args:
            pos: 位置坐标

        Returns:
            UI元素名称，如果不在任何UI内则返回None
        """
        for element_name, rect in [
            ('status_bar', self.status_bar_rect),
            ('ai_dialog', self.ai_dialog_rect),
            ('hp_bar', self.hp_bar_rect),
            ('bottom_tips', self.bottom_tips_rect)
        ]:
            if rect.collidepoint(pos):
                return element_name
        return None

    def clear_ai_text(self) -> None:
        """清除AI对话文本"""
        self.current_ai_text = ""
        self.ai_text_timer = 0

    def resize(self, new_width: int, new_height: int) -> None:
        """
        调整UI大小

        Args:
            new_width: 新宽度
            new_height: 新高度
        """
        self.screen_width = new_width
        self.screen_height = new_height

        # 重新计算UI位置
        self.status_bar_rect = pygame.Rect(0, 0, new_width, 40)
        self.ai_dialog_rect = pygame.Rect(new_width // 2 - 300, 80, 600, 60)
        self.bottom_tips_rect = pygame.Rect(new_width // 2 - 200, new_height - 30, 400, 30)