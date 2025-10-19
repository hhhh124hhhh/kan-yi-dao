import pygame
import random
import math
import logging
from typing import Optional, Tuple
from enum import Enum


class EnemyType(Enum):
    """敌人类型枚举"""
    STRAW_DUMMY = "straw_dummy"      # 稻草人
    BAMBOO_DUMMY = "bamboo_dummy"    # 竹人偶
    SKELETON = "skeleton"            # 骷髅
    GOLEM = "golem"                  # 傀儡
    AI_SHADOW = "ai_shadow"          # AI之影


class StrawDummy:
    """稻草人 - 新手村的训练目标"""

    def __init__(self):
        # 基础属性
        self.hp = 100
        self.max_hp = 100
        self.rect = pygame.Rect(370, 220, 60, 100)  # 按UI.md位置调整
        self.enemy_type = EnemyType.STRAW_DUMMY
        self.name = "稻草人"

        # 日志
        self.logger = logging.getLogger(__name__)

        # 受击相关
        self.last_damage = 0
        self.is_alive = True

        # 动画相关
        self.hit_animation_timer = 0
        self.death_animation_timer = 0
        self.wobble_angle = 0
        self.wobble_speed = 0

        # 视觉效果
        self.base_color = (200, 180, 140)  # 稻草黄色
        self.current_color = self.base_color
        self.particles = []

        # 统计数据
        self.total_damage_taken = 0
        self.hits_received = 0
        self.times_defeated = 0

        # 升级相关（随着玩家等级提升）
        self.level_scaling = 1.0

    def hit(self, damage: int) -> bool:
        """
        受到伤害

        Args:
            damage: 伤害值

        Returns:
            是否成功命中
        """
        if not self.is_alive:
            return False

        # 应用伤害
        actual_damage = int(damage * self.level_scaling)
        self.hp -= actual_damage
        self.last_damage = actual_damage
        self.total_damage_taken += actual_damage
        self.hits_received += 1

        # 启动受击动画
        self.hit_animation_timer = 15
        self.wobble_speed = random.uniform(-0.2, 0.2)

        # 创建粒子效果
        self._create_hit_particles()

        # 检查是否死亡
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            self.death_animation_timer = 90  # 1.5秒死亡动画
            self.times_defeated += 1
            self.logger.info(f"稻草人倒下了！第{self.times_defeated}次被击败 🌾")
            return True

        return True

    def _create_hit_particles(self) -> None:
        """创建受击粒子效果"""
        # 在受击位置创建稻草粒子
        for _ in range(random.randint(3, 8)):
            particle = {
                'pos': list(self.rect.center),
                'vel': [random.uniform(-3, 3), random.uniform(-5, -1)],
                'life': random.randint(20, 40),
                'max_life': 40,
                'size': random.randint(2, 4),
                'color': (
                    random.randint(180, 220),
                    random.randint(160, 200),
                    random.randint(120, 160)
                )
            }
            self.particles.append(particle)

    def update(self, dt: float = 1/60) -> None:
        """
        更新敌人状态

        Args:
            dt: 时间增量
        """
        # 更新受击动画
        if self.hit_animation_timer > 0:
            self.hit_animation_timer -= 1
            # 受击时颜色变红
            flash_intensity = self.hit_animation_timer / 15
            self.current_color = (
                min(255, self.base_color[0] + int(55 * flash_intensity)),
                max(0, self.base_color[1] - int(50 * flash_intensity)),
                max(0, self.base_color[2] - int(40 * flash_intensity))
            )
        else:
            self.current_color = self.base_color

        # 更新摇晃动画
        if self.wobble_speed != 0:
            self.wobble_angle += self.wobble_speed
            self.wobble_speed *= 0.95  # 阻尼

            if abs(self.wobble_speed) < 0.01:
                self.wobble_speed = 0
                self.wobble_angle = 0

        # 更新死亡动画
        if not self.is_alive and self.death_animation_timer > 0:
            self.death_animation_timer -= 1

            # 死亡时逐渐倒下
            if self.death_animation_timer == 0:
                self.respawn()

        # 更新粒子效果
        self._update_particles(dt)

    def _update_particles(self, dt: float) -> None:
        """更新粒子效果"""
        for particle in self.particles[:]:
            # 更新位置
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]

            # 应用重力
            particle['vel'][1] += 0.3

            # 更新生命值
            particle['life'] -= 1

            # 移除死亡粒子
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def respawn(self) -> None:
        """重生"""
        self.hp = self.max_hp
        self.is_alive = True
        self.last_damage = 0
        self.hit_animation_timer = 0
        self.wobble_angle = 0
        self.wobble_speed = 0
        self.logger.info("稻草人重新站了起来！🌾")

    def scale_with_player_level(self, player_level: int) -> None:
        """
        根据玩家等级调整难度

        Args:
            player_level: 玩家等级
        """
        # 每3级玩家提升，稻草人变得更强
        scale_factor = 1.0 + (player_level // 3) * 0.2
        self.level_scaling = scale_factor

        # 提升最大血量
        new_max_hp = int(100 * scale_factor)
        if new_max_hp != self.max_hp:
            self.max_hp = new_max_hp
            # 如果当前正在重生，也更新当前血量
            if self.is_alive:
                self.hp = min(self.hp, self.max_hp)

    def get_hp_percentage(self) -> float:
        """
        获取血量百分比

        Returns:
            血量百分比 (0-1)
        """
        return self.hp / self.max_hp if self.max_hp > 0 else 0

    def get_status_info(self) -> dict:
        """
        获取状态信息

        Returns:
            状态信息字典
        """
        return {
            'name': self.name,
            'type': self.enemy_type.value,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'hp_percent': self.get_hp_percentage(),
            'is_alive': self.is_alive,
            'last_damage': self.last_damage,
            'total_damage_taken': self.total_damage_taken,
            'hits_received': self.hits_received,
            'times_defeated': self.times_defeated,
            'level_scaling': self.level_scaling
        }

    def draw(self, screen: pygame.Surface) -> None:
        """
        绘制稻草人

        Args:
            screen: 屏幕对象
        """
        # 计算绘制位置（考虑摇晃）
        center_x = self.rect.centerx + int(math.sin(self.wobble_angle) * 5)
        center_y = self.rect.centery

        if not self.is_alive:
            # 死亡动画：倒下效果
            fall_progress = 1 - (self.death_animation_timer / 90)
            fall_angle = fall_progress * math.pi / 3  # 倒下60度

            # 计算倒下后的位置
            offset_x = int(math.sin(fall_angle) * self.rect.height // 2)
            offset_y = int((1 - math.cos(fall_angle)) * self.rect.height // 2)

            center_x += offset_x
            center_y += offset_y

        # 绘制稻草人主体
        self._draw_strawman_body(screen, center_x, center_y)

        # 绘制粒子效果
        self._draw_particles(screen)

        # 绘制血条
        self._draw_hp_bar(screen)

        # 绘制名字
        self._draw_name(screen)

    def _draw_strawman_body(self, screen: pygame.Surface, center_x: int, center_y: int) -> None:
        """绘制稻草人身体"""
        # 身体（椭圆形）
        body_rect = pygame.Rect(
            center_x - 20,
            center_y - 30,
            40,
            60
        )
        pygame.draw.ellipse(screen, self.current_color, body_rect)
        pygame.draw.ellipse(screen, (100, 80, 60), body_rect, 2)

        # 头部（圆形）
        head_pos = (center_x, center_y - 45)
        pygame.draw.circle(screen, self.current_color, head_pos, 15)
        pygame.draw.circle(screen, (100, 80, 60), head_pos, 15, 2)

        # 眼睛
        eye_y = center_y - 45
        if self.is_alive:
            # 正常眼睛
            pygame.draw.circle(screen, (0, 0, 0), (center_x - 5, eye_y), 2)
            pygame.draw.circle(screen, (0, 0, 0), (center_x + 5, eye_y), 2)
        else:
            # X眼睛（死亡状态）
            pygame.draw.line(screen, (0, 0, 0), (center_x - 7, eye_y - 3), (center_x - 3, eye_y + 3), 2)
            pygame.draw.line(screen, (0, 0, 0), (center_x - 7, eye_y + 3), (center_x - 3, eye_y - 3), 2)
            pygame.draw.line(screen, (0, 0, 0), (center_x + 3, eye_y - 3), (center_x + 7, eye_y + 3), 2)
            pygame.draw.line(screen, (0, 0, 0), (center_x + 3, eye_y + 3), (center_x + 7, eye_y - 3), 2)

        # 手臂（线条）
        arm_y = center_y - 20
        pygame.draw.line(screen, self.current_color, (center_x - 20, arm_y), (center_x - 30, arm_y + 10), 3)
        pygame.draw.line(screen, self.current_color, (center_x + 20, arm_y), (center_x + 30, arm_y + 10), 3)

        # 装饰：稻草纹理
        for i in range(5):
            y_pos = center_y - 25 + i * 10
            pygame.draw.line(screen, (150, 130, 100), (center_x - 15, y_pos), (center_x + 15, y_pos), 1)

    def _draw_particles(self, screen: pygame.Surface) -> None:
        """绘制粒子效果"""
        for particle in self.particles:
            alpha = particle['life'] / particle['max_life']
            size = int(particle['size'] * alpha)
            if size > 0:
                pygame.draw.circle(
                    screen,
                    particle['color'],
                    (int(particle['pos'][0]), int(particle['pos'][1])),
                    size
                )

    def _draw_hp_bar(self, screen: pygame.Surface) -> None:
        """绘制血条"""
        if not self.is_alive:
            return

        # 血条位置
        bar_width = 60
        bar_height = 6
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 15

        # 背景
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # 血量
        hp_width = int(bar_width * self.get_hp_percentage())
        hp_color = (
            int(255 * (1 - self.get_hp_percentage())),  # 红色渐变
            int(100 * self.get_hp_percentage()),        # 绿色渐变
            0
        )
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, hp_width, bar_height))

        # 边框
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)

    def _draw_name(self, screen: pygame.Surface) -> None:
        """绘制名字"""
        try:
            # 使用中文字体系统渲染敌人名称
            from .font_manager import get_chinese_text_font
            from .text_localization import get_localization
            
            # 获取本地化系统
            localization = get_localization()
            
            # 使用中文字体渲染敌人名称
            font = get_chinese_text_font(18)  # 使用18号字体
            text = font.render(self.name, True, (200, 200, 200))
            text_rect = text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 5)
            screen.blit(text, text_rect)
        except Exception as e:
            # 如果字体加载失败，使用默认字体作为回退
            try:
                font = pygame.font.Font(None, 18)
                text = font.render(self.name, True, (200, 200, 200))
                text_rect = text.get_rect(centerx=self.rect.centerx, top=self.rect.bottom + 5)
                screen.blit(text, text_rect)
            except:
                pass  # 如果仍然失败，跳过名字绘制

    def reset(self) -> None:
        """重置状态"""
        self.__init__()


# 保持向后兼容的Dummy类
class Dummy(StrawDummy):
    """向后兼容的Dummy类"""
    pass
