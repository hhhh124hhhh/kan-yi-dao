import pygame
import random
import math
import time
from typing import List, Dict, Any, Tuple, Optional
from enum import Enum
from dataclasses import dataclass


class EffectType(Enum):
    """特效类型枚举"""
    SLASH = "slash"
    CRIT = "crit"
    COMBO = "combo"
    LEVEL_UP = "level_up"
    SCREEN_SHAKE = "screen_shake"
    DAMAGE_NUMBER = "damage_number"
    HEALING = "healing"
    COIN = "coin"
    STAMINA_WARNING = "stamina_warning"
    EXP_GAIN = "exp_gain"
    ATTACK_TRAIL = "attack_trail"


@dataclass
class Effect:
    """特效数据结构"""
    type: EffectType
    pos: Tuple[int, int]
    timer: int
    data: Dict[str, Any] = None
    created_time: float = 0.0

    def __post_init__(self):
        if self.created_time == 0.0:
            self.created_time = time.time()


@dataclass
class Particle:
    """粒子数据结构"""
    pos: List[float]
    vel: List[float]
    life: int
    max_life: int
    size: int
    color: Tuple[int, int, int]
    gravity: float = 0.2
    fade: bool = True


class EffectManager:
    """特效管理器 - 负责游戏中的所有视觉效果"""

    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.effects: List[Effect] = []
        self.particles: List[Particle] = []
        self.screen_width = screen_width
        self.screen_height = screen_height

        # 屏幕震动
        self.screen_shake_offset = [0, 0]
        self.screen_shake_intensity = 0
        self.screen_shake_duration = 0

        # 字体缓存
        self.fonts = {
            'small': pygame.font.Font(None, 18),
            'medium': pygame.font.Font(None, 24),
            'large': pygame.font.Font(None, 36),
            'huge': pygame.font.Font(None, 48)
        }

        # 特效池（对象池优化）
        self.effect_pool = {}
        self.max_effects_per_type = 50

        # 统计数据
        self.stats = {
            'total_effects_created': 0,
            'total_particles_created': 0,
            'active_effects': 0,
            'active_particles': 0
        }

    def create_slash_effect(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                          is_crit: bool = False) -> None:
        """
        创建砍击特效

        Args:
            start_pos: 起始位置
            end_pos: 结束位置
            is_crit: 是否暴击
        """
        effect = Effect(
            type=EffectType.SLASH,
            pos=start_pos,
            timer=15,
            data={
                'end_pos': end_pos,
                'is_crit': is_crit,
                'progress': 0.0
            }
        )
        self._add_effect(effect)

        # 创建砍击粒子
        self._create_slash_particles(start_pos, end_pos, is_crit)

        # 暴击时添加屏幕震动
        if is_crit:
            self.create_screen_shake(intensity=5)

    def _create_slash_particles(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                               is_crit: bool) -> None:
        """创建砍击粒子"""
        particle_count = 15 if is_crit else 8
        color = (255, 100, 100) if is_crit else (255, 255, 200)

        for _ in range(particle_count):
            # 在砍击路径上随机分布粒子
            t = random.random()
            x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
            y = start_pos[1] + (end_pos[1] - start_pos[1]) * t

            particle = Particle(
                pos=[x + random.randint(-10, 10), y + random.randint(-10, 10)],
                vel=[random.uniform(-5, 5), random.uniform(-8, -2)],
                life=random.randint(20, 40),
                max_life=40,
                size=random.randint(2, 4) if is_crit else random.randint(1, 3),
                color=color,
                gravity=0.3
            )
            self.particles.append(particle)
            self.stats['total_particles_created'] += 1

    def create_crit_effect(self, damage: int, pos: Tuple[int, int]) -> None:
        """
        创建暴击特效

        Args:
            damage: 伤害值
            pos: 位置
        """
        # 创建大伤害数字
        self.create_damage_number(damage, pos, is_crit=True)

        # 创建暴击文字
        crit_effect = Effect(
            type=EffectType.CRIT,
            pos=pos,
            timer=60,
            data={
                'text': '暴击!',
                'scale': 0.1,
                'target_scale': 1.5,
                'color': (255, 50, 50)
            }
        )
        self._add_effect(crit_effect)

        # 创建爆炸粒子
        self._create_explosion_particles(pos, (255, 100, 100), 25)

        # 屏幕震动
        self.create_screen_shake(intensity=8)

    def create_combo_effect(self, combo_count: int, pos: Tuple[int, int]) -> None:
        """
        创建连击特效

        Args:
            combo_count: 连击数
            pos: 位置
        """
        # 连击数字特效
        combo_effect = Effect(
            type=EffectType.COMBO,
            pos=pos,
            timer=45,
            data={
                'combo': combo_count,
                'scale': 0.1,
                'target_scale': 1.0 + combo_count * 0.05,
                'rotation': 0
            }
        )
        self._add_effect(combo_effect)

        # 连击粒子效果
        if combo_count >= 10:
            self._create_combo_ring_particles(pos, combo_count)

    def _create_combo_ring_particles(self, pos: Tuple[int, int], combo_count: int) -> None:
        """创建连击环状粒子"""
        ring_count = min(combo_count // 10, 5)  # 最多5个环

        for ring in range(ring_count):
            particle_count = 20
            radius = 20 + ring * 15

            for i in range(particle_count):
                angle = (2 * math.pi * i) / particle_count
                x = pos[0] + radius * math.cos(angle)
                y = pos[1] + radius * math.sin(angle)

                # 向外扩散的速度
                vel_angle = angle + random.uniform(-0.2, 0.2)
                speed = random.uniform(2, 4)

                particle = Particle(
                    pos=[x, y],
                    vel=[speed * math.cos(vel_angle), speed * math.sin(vel_angle)],
                    life=30,
                    max_life=30,
                    size=3,
                    color=(255, 200, 100),
                    gravity=0,
                    fade=True
                )
                self.particles.append(particle)
                self.stats['total_particles_created'] += 1

    def create_level_up_effect(self, pos: Tuple[int, int]) -> None:
        """
        创建升级特效

        Args:
            pos: 位置
        """
        # 升级文字特效
        level_effect = Effect(
            type=EffectType.LEVEL_UP,
            pos=pos,
            timer=120,
            data={
                'text': 'LEVEL UP!',
                'scale': 0.1,
                'target_scale': 2.0,
                'color': (255, 215, 0),  # 金色
                'rings': []
            }
        )
        self._add_effect(level_effect)

        # 创建升级光环
        self._create_level_up_rings(pos)

        # 创建金色粒子
        self._create_explosion_particles(pos, (255, 215, 0), 50)

        # 强烈屏幕震动
        self.create_screen_shake(intensity=10, duration=30)

    def _create_level_up_rings(self, pos: Tuple[int, int]) -> None:
        """创建升级光环"""
        for i in range(3):
            ring = {
                'radius': 10,
                'max_radius': 80 + i * 20,
                'thickness': 3,
                'alpha': 255,
                'speed': 2 + i * 0.5,
                'color': (255, 215, 0)
            }
            # 添加到升级特效的数据中
            if self.effects and self.effects[-1].type == EffectType.LEVEL_UP:
                self.effects[-1].data['rings'].append(ring)

    def create_damage_number(self, damage: int, pos: Tuple[int, int],
                           is_crit: bool = False, is_poison: bool = False) -> None:
        """
        创建伤害数字

        Args:
            damage: 伤害值
            pos: 位置
            is_crit: 是否暴击
            is_poison: 是否中毒伤害
        """
        # 确定颜色
        if is_crit:
            color = (255, 50, 50)
            font = self.fonts['huge']
        elif is_poison:
            color = (100, 255, 100)
            font = self.fonts['medium']
        else:
            color = (255, 200, 100)
            font = self.fonts['large']

        effect = Effect(
            type=EffectType.DAMAGE_NUMBER,
            pos=pos,
            timer=40,
            data={
                'text': str(damage),
                'color': color,
                'font': font,
                'vel_y': -3,
                'start_y': pos[1],
                'alpha': 255
            }
        )
        self._add_effect(effect)

    def create_exp_gain_effect(self, exp_amount: int, pos: Tuple[int, int]) -> None:
        """
        创建经验获得特效

        Args:
            exp_amount: 经验值
            pos: 位置
        """
        effect = Effect(
            type=EffectType.EXP_GAIN,
            pos=pos,
            timer=60,
            data={
                'text': f'+{exp_amount} EXP',
                'color': (100, 255, 100),
                'vel_y': -2,
                'start_y': pos[1],
                'alpha': 255
            }
        )
        self._add_effect(effect)

    def create_coin_effect(self, coin_amount: int, pos: Tuple[int, int]) -> None:
        """
        创建金币特效

        Args:
            coin_amount: 金币数量
            pos: 位置
        """
        for i in range(coin_amount):
            # 创建金币粒子
            particle = Particle(
                pos=[pos[0] + random.randint(-20, 20), pos[1]],
                vel=[random.uniform(-3, 3), random.uniform(-8, -4)],
                life=40,
                max_life=40,
                size=4,
                color=(255, 215, 0),
                gravity=0.5,
                fade=False
            )
            self.particles.append(particle)
            self.stats['total_particles_created'] += 1

        # 显示金币数量文字
        if coin_amount > 1:
            effect = Effect(
                type=EffectType.COIN,
                pos=pos,
                timer=40,
                data={
                    'text': f'+{coin_amount} 金币',
                    'color': (255, 215, 0),
                    'vel_y': -2,
                    'start_y': pos[1],
                    'alpha': 255
                }
            )
            self._add_effect(effect)

    def create_stamina_warning(self, pos: Tuple[int, int]) -> None:
        """
        创建体力不足警告

        Args:
            pos: 位置
        """
        effect = Effect(
            type=EffectType.STAMINA_WARNING,
            pos=pos,
            timer=90,
            data={
                'text': '体力不足!',
                'color': (100, 100, 255),
                'alpha': 0,
                'target_alpha': 200,
                'pulse_time': 0
            }
        )
        self._add_effect(effect)

    def create_screen_shake(self, intensity: int = 3, duration: int = 15) -> None:
        """
        创建屏幕震动

        Args:
            intensity: 震动强度
            duration: 震动持续时间
        """
        self.screen_shake_intensity = intensity
        self.screen_shake_duration = duration

    def create_attack_trail(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> None:
        """
        创建攻击轨迹

        Args:
            start_pos: 起始位置
            end_pos: 结束位置
        """
        effect = Effect(
            type=EffectType.ATTACK_TRAIL,
            pos=start_pos,
            timer=10,
            data={
                'end_pos': end_pos,
                'alpha': 200
            }
        )
        self._add_effect(effect)

    def _create_explosion_particles(self, pos: Tuple[int, int],
                                  color: Tuple[int, int, int], count: int) -> None:
        """创建爆炸粒子"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)

            particle = Particle(
                pos=list(pos),
                vel=[speed * math.cos(angle), speed * math.sin(angle)],
                life=random.randint(20, 40),
                max_life=40,
                size=random.randint(2, 6),
                color=color,
                gravity=0.1,
                fade=True
            )
            self.particles.append(particle)
            self.stats['total_particles_created'] += 1

    def _add_effect(self, effect: Effect) -> None:
        """添加特效到管理器"""
        # 检查特效数量限制
        effect_type_count = sum(1 for e in self.effects if e.type == effect.type)
        if effect_type_count < self.max_effects_per_type:
            self.effects.append(effect)
            self.stats['total_effects_created'] += 1

    def update(self, dt: float = 1/60) -> None:
        """
        更新所有特效

        Args:
            dt: 时间增量
        """
        # 更新特效
        for effect in self.effects[:]:
            effect.timer -= 1

            # 更新特定类型的特效
            if effect.type == EffectType.DAMAGE_NUMBER:
                self._update_damage_number(effect, dt)
            elif effect.type == EffectType.CRIT:
                self._update_crit_effect(effect, dt)
            elif effect.type == EffectType.COMBO:
                self._update_combo_effect(effect, dt)
            elif effect.type == EffectType.LEVEL_UP:
                self._update_level_up_effect(effect, dt)
            elif effect.type == EffectType.EXP_GAIN:
                self._update_exp_gain_effect(effect, dt)
            elif effect.type == EffectType.COIN:
                self._update_coin_effect(effect, dt)
            elif effect.type == EffectType.STAMINA_WARNING:
                self._update_stamina_warning(effect, dt)
            elif effect.type == EffectType.SLASH:
                self._update_slash_effect(effect, dt)
            elif effect.type == EffectType.ATTACK_TRAIL:
                self._update_attack_trail(effect, dt)

            # 移除完成的特效
            if effect.timer <= 0:
                self.effects.remove(effect)

        # 更新粒子
        for particle in self.particles[:]:
            # 更新位置
            particle.pos[0] += particle.vel[0]
            particle.pos[1] += particle.vel[1]

            # 应用重力
            particle.vel[1] += particle.gravity

            # 更新生命值
            particle.life -= 1

            # 移除死亡粒子
            if particle.life <= 0:
                self.particles.remove(particle)

        # 更新屏幕震动
        self._update_screen_shake()

        # 更新统计数据
        self.stats['active_effects'] = len(self.effects)
        self.stats['active_particles'] = len(self.particles)

    def _update_damage_number(self, effect: Effect, dt: float) -> None:
        """更新伤害数字"""
        effect.data['vel_y'] += 0.2  # 重力
        effect.pos = (effect.pos[0], effect.pos[1] + effect.data['vel_y'])
        effect.data['alpha'] = max(0, effect.data['alpha'] - 6)

    def _update_crit_effect(self, effect: Effect, dt: float) -> None:
        """更新暴击特效"""
        # 缩放动画
        if effect.data['scale'] < effect.data['target_scale']:
            effect.data['scale'] += 0.1

        # 上升动画
        effect.pos = (effect.pos[0], effect.pos[1] - 2)

    def _update_combo_effect(self, effect: Effect, dt: float) -> None:
        """更新连击特效"""
        # 缩放动画
        if effect.data['scale'] < effect.data['target_scale']:
            effect.data['scale'] += 0.05

        # 旋转动画
        effect.data['rotation'] += 5

        # 上升动画
        effect.pos = (effect.pos[0], effect.pos[1] - 1)

    def _update_level_up_effect(self, effect: Effect, dt: float) -> None:
        """更新升级特效"""
        # 缩放动画
        if effect.data['scale'] < effect.data['target_scale']:
            effect.data['scale'] += 0.03

        # 更新光环
        for ring in effect.data['rings']:
            ring['radius'] += ring['speed']
            ring['alpha'] = max(0, ring['alpha'] - 3)

        # 移除完成的光环
        effect.data['rings'] = [r for r in effect.data['rings'] if r['alpha'] > 0]

    def _update_exp_gain_effect(self, effect: Effect, dt: float) -> None:
        """更新经验获得特效"""
        effect.data['vel_y'] += 0.1
        effect.pos = (effect.pos[0], effect.pos[1] + effect.data['vel_y'])
        effect.data['alpha'] = max(0, effect.data['alpha'] - 4)

    def _update_coin_effect(self, effect: Effect, dt: float) -> None:
        """更新金币特效"""
        effect.data['vel_y'] += 0.1
        effect.pos = (effect.pos[0], effect.pos[1] + effect.data['vel_y'])
        effect.data['alpha'] = max(0, effect.data['alpha'] - 6)

    def _update_stamina_warning(self, effect: Effect, dt: float) -> None:
        """更新体力警告"""
        effect.data['pulse_time'] += dt
        pulse = math.sin(effect.data['pulse_time'] * 8)
        effect.data['alpha'] = int(effect.data['target_alpha'] * (0.5 + 0.5 * pulse))

    def _update_slash_effect(self, effect: Effect, dt: float) -> None:
        """更新砍击特效"""
        effect.data['progress'] = min(1.0, effect.data['progress'] + 0.1)

    def _update_attack_trail(self, effect: Effect, dt: float) -> None:
        """更新攻击轨迹"""
        effect.data['alpha'] = max(0, effect.data['alpha'] - 20)

    def _update_screen_shake(self) -> None:
        """更新屏幕震动"""
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= 1

            # 计算震动偏移
            if self.screen_shake_intensity > 0:
                self.screen_shake_offset[0] = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
                self.screen_shake_offset[1] = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
        else:
            self.screen_shake_offset = [0, 0]
            self.screen_shake_intensity = 0

    def draw(self, screen: pygame.Surface) -> None:
        """
        绘制所有特效

        Args:
            screen: 屏幕对象
        """
        # 应用屏幕震动偏移
        if self.screen_shake_duration > 0:
            screen_offset = self.screen_shake_offset.copy()
        else:
            screen_offset = [0, 0]

        # 绘制特效
        for effect in self.effects:
            self._draw_effect(screen, effect, screen_offset)

        # 绘制粒子
        for particle in self.particles:
            self._draw_particle(screen, particle, screen_offset)

    def _draw_effect(self, screen: pygame.Surface, effect: Effect, offset: List[int]) -> None:
        """绘制单个特效"""
        draw_pos = (effect.pos[0] + offset[0], effect.pos[1] + offset[1])

        if effect.type == EffectType.DAMAGE_NUMBER:
            self._draw_damage_number(screen, effect, draw_pos)
        elif effect.type == EffectType.CRIT:
            self._draw_crit_effect(screen, effect, draw_pos)
        elif effect.type == EffectType.COMBO:
            self._draw_combo_effect(screen, effect, draw_pos)
        elif effect.type == EffectType.LEVEL_UP:
            self._draw_level_up_effect(screen, effect, draw_pos)
        elif effect.type == EffectType.EXP_GAIN:
            self._draw_text_effect(screen, effect, draw_pos)
        elif effect.type == EffectType.COIN:
            self._draw_text_effect(screen, effect, draw_pos)
        elif effect.type == EffectType.STAMINA_WARNING:
            self._draw_stamina_warning(screen, effect, draw_pos)
        elif effect.type == EffectType.SLASH:
            self._draw_slash_effect(screen, effect, draw_pos)
        elif effect.type == EffectType.ATTACK_TRAIL:
            self._draw_attack_trail(screen, effect, draw_pos)

    def _draw_damage_number(self, screen: pygame.Surface, effect: Effect, pos: Tuple[int, int]) -> None:
        """绘制伤害数字"""
        color = (*effect.data['color'], effect.data['alpha'])
        text = effect.data['font'].render(effect.data['text'], True, color[:3])
        text_rect = text.get_rect(center=pos)

        # 添加阴影效果
        shadow_text = effect.data['font'].render(effect.data['text'], True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(pos[0] + 2, pos[1] + 2))

        screen.blit(shadow_text, shadow_rect)
        screen.blit(text, text_rect)

    def _draw_crit_effect(self, screen: pygame.Surface, effect: Effect, pos: Tuple[int, int]) -> None:
        """绘制暴击特效"""
        font = self.fonts['huge']
        text = font.render(effect.data['text'], True, effect.data['color'])

        # 应用缩放
        if effect.data['scale'] != 1.0:
            scaled_size = (int(text.get_width() * effect.data['scale']),
                          int(text.get_height() * effect.data['scale']))
            text = pygame.transform.scale(text, scaled_size)

        text_rect = text.get_rect(center=pos)
        screen.blit(text, text_rect)

    def _draw_combo_effect(self, screen: pygame.Surface, effect: Effect, pos: Tuple[int, int]) -> None:
        """绘制连击特效"""
        font = self.fonts['large']
        text = font.render(f"x{effect.data['combo']}", True, (255, 200, 100))

        # 应用缩放和旋转
        if effect.data['scale'] != 1.0 or effect.data['rotation'] != 0:
            text = pygame.transform.scale(text,
                (int(text.get_width() * effect.data['scale']),
                 int(text.get_height() * effect.data['scale'])))
            text = pygame.transform.rotate(text, effect.data['rotation'])

        text_rect = text.get_rect(center=pos)
        screen.blit(text, text_rect)

    def _draw_level_up_effect(self, screen: pygame.Surface, effect: Effect, pos: Tuple[int, int]) -> None:
        """绘制升级特效"""
        # 绘制光环
        for ring in effect.data['rings']:
            if ring['alpha'] > 0:
                color = (*ring['color'], ring['alpha'])
                pygame.draw.circle(screen, color[:3], pos, ring['radius'], ring['thickness'])

        # 绘制文字
        font = self.fonts['huge']
        text = font.render(effect.data['text'], True, effect.data['color'])

        if effect.data['scale'] != 1.0:
            scaled_size = (int(text.get_width() * effect.data['scale']),
                          int(text.get_height() * effect.data['scale']))
            text = pygame.transform.scale(text, scaled_size)

        text_rect = text.get_rect(center=pos)
        screen.blit(text, text_rect)

    def _draw_text_effect(self, screen: pygame.Surface, effect: Effect, pos: Tuple[int, int]) -> None:
        """绘制文字特效"""
        if effect.data['alpha'] > 0:
            color = (*effect.data['color'], effect.data['alpha'])
            text = self.fonts['medium'].render(effect.data['text'], True, color[:3])
            text_rect = text.get_rect(center=pos)
            screen.blit(text, text_rect)

    def _draw_stamina_warning(self, screen: pygame.Surface, effect: Effect, pos: Tuple[int, int]) -> None:
        """绘制体力警告"""
        if effect.data['alpha'] > 0:
            color = (*effect.data['color'], effect.data['alpha'])
            text = self.fonts['medium'].render(effect.data['text'], True, color[:3])
            text_rect = text.get_rect(center=pos)
            screen.blit(text, text_rect)

    def _draw_slash_effect(self, screen: pygame.Surface, effect: Effect, pos: Tuple[int, int]) -> None:
        """绘制砍击特效"""
        end_pos = effect.data['end_pos']
        alpha = int(255 * (1 - effect.data['progress']))

        if alpha > 0:
            color = (255, 255, 200) if not effect.data['is_crit'] else (255, 100, 100)

            # 绘制砍击线条
            pygame.draw.line(screen, color, pos, end_pos, 3)

            # 绘制砍击光晕
            for i in range(3):
                glow_alpha = alpha // (i + 1)
                glow_color = (*color, glow_alpha)
                pygame.draw.line(screen, glow_color[:3], pos, end_pos, 6 - i * 2)

    def _draw_attack_trail(self, screen: pygame.Surface, effect: Effect, pos: Tuple[int, int]) -> None:
        """绘制攻击轨迹"""
        if effect.data['alpha'] > 0:
            end_pos = effect.data['end_pos']
            color = (200, 200, 255, effect.data['alpha'])
            pygame.draw.line(screen, color[:3], pos, end_pos, 2)

    def _draw_particle(self, screen: pygame.Surface, particle: Particle, offset: List[int]) -> None:
        """绘制粒子"""
        pos = (int(particle.pos[0] + offset[0]), int(particle.pos[1] + offset[1]))

        if particle.fade:
            alpha = particle.life / particle.max_life
            color = (*particle.color, int(255 * alpha))
        else:
            color = particle.color

        pygame.draw.circle(screen, color[:3], pos, particle.size)

    def clear_all_effects(self) -> None:
        """清除所有特效"""
        self.effects.clear()
        self.particles.clear()
        self.screen_shake_offset = [0, 0]
        self.screen_shake_intensity = 0
        self.screen_shake_duration = 0

    def get_stats(self) -> Dict[str, Any]:
        """获取特效统计信息"""
        return self.stats.copy()

    def reset_stats(self) -> None:
        """重置统计数据"""
        self.stats = {
            'total_effects_created': 0,
            'total_particles_created': 0,
            'active_effects': 0,
            'active_particles': 0
        }
