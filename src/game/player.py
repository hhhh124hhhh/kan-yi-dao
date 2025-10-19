import pygame
import random
import time
import math
from typing import Tuple, Optional, Any

# 导入游戏常量
from .game_constants import (
    PlayerAttributes, GameConstants, GameMechanics, Locations,
    validate_player_attributes, get_safe_attribute
)


class Player:
    def __init__(self):
        # 基础属性 - 使用常量定义
        self.attack_power = GameConstants.DEFAULT_ATTACK_POWER
        self.exp = 0
        self.level = GameConstants.DEFAULT_PLAYER_LEVEL
        self.rect = pygame.Rect(380, 400, 40, 80)

        # 核心属性 - 使用标准命名
        self.combo = 0  # 默认连击数为0
        self.max_combo = 0
        self.stamina = GameConstants.DEFAULT_STAMINA
        self.max_stamina = GameConstants.DEFAULT_MAX_STAMINA
        self.crit_rate = GameMechanics.DEFAULT_CRIT_RATE
        self.crit_damage = GameMechanics.DEFAULT_CRIT_DAMAGE_MULTIPLIER
        self.weapon_tier = GameConstants.DEFAULT_WEAPON_TIER
        self.coins = GameConstants.DEFAULT_COINS
        self.location = Locations.NEWBIE_VILLAGE
        self.ai_affinity = 10
        self.attack_cooldown = 0

        # 时间相关
        self.last_attack_time = 0
        self.last_combo_time = 0
        self.combo_reset_time = GameMechanics.COMBO_RESET_TIME
        self.stamina_regen_timer = 0
        self.stamina_regen_interval = GameMechanics.STAMINA_REGEN_INTERVAL
        self.stamina_regen_amount = GameMechanics.STAMINA_REGEN_RATE

        # 升级相关
        self.next_exp = self.calc_exp_needed(self.level)
        self.just_leveled_up = False
        self.level_up_timer = 0

        # 动画相关
        self.attack_animation_timer = 0
        self.color = (200, 200, 255)  # 玩家颜色

        # 属性验证 - 确保所有必需属性都存在
        self._validate_attributes()

    def calc_exp_needed(self, level: int) -> int:
        """
        计算升级所需经验

        Args:
            level: 玩家等级

        Returns:
            升级所需经验值
        """
        # 使用指数增长公式
        base_exp = 50
        growth_factor = 1.2
        return int(base_exp * (growth_factor ** (level - 1)))

    def calc_damage(self) -> Tuple[int, bool]:
        """
        计算伤害（含暴击判定）

        Returns:
            (伤害值, 是否暴击)
        """
        base_damage = self.attack_power

        # 武器等级加成
        weapon_bonus = 1.0 + (self.weapon_tier - 1) * 0.2
        base_damage = int(base_damage * weapon_bonus)

        # 随机浮动
        damage = base_damage + random.randint(-2, 5)

        # 暴击判定
        is_crit = random.random() < self.crit_rate
        if is_crit:
            damage = int(damage * self.crit_damage)

        return max(1, damage), is_crit

    def can_attack(self) -> bool:
        """
        检查是否可以攻击

        Returns:
            是否可以攻击
        """
        current_time = time.time()

        # 检查攻击冷却
        if self.attack_cooldown > 0:
            if current_time - self.last_attack_time < self.attack_cooldown:
                return False

        # 检查体力
        if self.stamina < 10:  # 每次攻击消耗10体力
            return False

        return True

    def use_stamina(self, amount: int) -> bool:
        """
        消耗体力

        Args:
            amount: 消耗数量

        Returns:
            是否成功消耗
        """
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False

    def regen_stamina(self, amount: int) -> None:
        """
        恢复体力

        Args:
            amount: 恢复数量
        """
        self.stamina = min(self.max_stamina, self.stamina + amount)

    def increase_combo(self) -> None:
        """增加连击数"""
        current_time = time.time()

        # 检查连击是否超时
        if current_time - self.last_combo_time > self.combo_reset_time:
            self.combo = 0

        self.combo += 1
        self.last_combo_time = current_time

        # 更新最大连击记录
        if self.combo > self.max_combo:
            self.max_combo = self.combo

    def reset_combo(self) -> None:
        """重置连击"""
        self.combo = 0

    def update_combo(self) -> None:
        """更新连击状态（检查超时）"""
        current_time = time.time()
        if current_time - self.last_combo_time > self.combo_reset_time:
            self.reset_combo()

    def get_combo_multiplier(self) -> float:
        """
        获取连击伤害倍率

        Returns:
            伤害倍率
        """
        # 每10连击增加10%伤害
        combo_bonus = math.floor(self.combo / 10) * 0.1
        return 1.0 + combo_bonus

    def attack(self, enemy) -> Tuple[bool, int, bool]:
        """
        攻击敌人

        Args:
            enemy: 敌人对象

        Returns:
            (是否命中, 伤害值, 是否暴击)
        """
        # 检查是否可以攻击
        if not self.can_attack():
            return False, 0, False

        # 消耗体力
        if not self.use_stamina(10):
            return False, 0, False

        # 计算伤害
        damage, is_crit = self.calc_damage()

        # 应用连击倍率
        combo_mult = self.get_combo_multiplier()
        final_damage = int(damage * combo_mult)

        # 攻击敌人
        hit = enemy.hit(final_damage)
        if hit:
            # 增加连击
            self.increase_combo()

            # 获得经验
            exp_gained = final_damage
            if is_crit:
                exp_gained = int(exp_gained * 1.5)  # 暴击获得额外经验

            self.add_exp(exp_gained)

            # 更新攻击时间
            self.last_attack_time = time.time()

            # 启动攻击动画
            self.attack_animation_timer = 10

            # 获得金币
            self.add_coins(random.randint(1, 3))

            return True, final_damage, is_crit

        return False, 0, False

    def add_exp(self, amount: int) -> None:
        """
        增加经验值

        Args:
            amount: 经验值数量
        """
        self.exp += amount

        # 检查升级
        while self.exp >= self.next_exp:
            self.level_up()

    def level_up(self) -> None:
        """升级"""
        old_level = self.level

        self.level += 1
        self.exp -= self.next_exp
        self.next_exp = self.calc_exp_needed(self.level)

        # 提升属性
        self.attack_power += 5
        self.max_stamina += 10
        self.stamina = self.max_stamina  # 升级回满体力

        # 提升暴击率（上限30%）
        self.crit_rate = min(0.30, self.crit_rate + 0.02)

        # 标记刚升级
        self.just_leveled_up = True
        self.level_up_timer = 60  # 1秒的升级提示时间

        # 增加AI亲密度
        self.ai_affinity += 2

        print(f"升级！等级 {self.level}, 攻击力 {self.attack_power}, 暴击率 {self.crit_rate:.1%}")

    def add_coins(self, amount: int) -> None:
        """
        增加金币

        Args:
            amount: 金币数量
        """
        self.coins += amount

    def use_coins(self, amount: int) -> bool:
        """
        使用金币

        Args:
            amount: 使用数量

        Returns:
            是否成功使用
        """
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False

    def upgrade_weapon(self) -> bool:
        """
        升级武器

        Returns:
            是否升级成功
        """
        upgrade_cost = self.weapon_tier * 50

        if self.use_coins(upgrade_cost):
            self.weapon_tier += 1
            self.attack_power += 3
            print(f"武器升级！当前等级：{self.weapon_tier}, 攻击力+{3}")
            return True

        return False

    def set_location(self, new_location: str) -> None:
        """
        设置当前位置

        Args:
            new_location: 新位置名称
        """
        self.location = new_location

    def update(self, dt: float) -> None:
        """
        更新玩家状态

        Args:
            dt: 时间增量（秒）
        """
        current_time = time.time()

        # 更新连击状态
        self.update_combo()

        # 体力恢复
        self.stamina_regen_timer += dt
        if self.stamina_regen_timer >= self.stamina_regen_interval:
            self.regen_stamina(self.stamina_regen_amount)
            self.stamina_regen_timer = 0

        # 更新升级提示计时器
        if self.level_up_timer > 0:
            self.level_up_timer -= 1
            if self.level_up_timer == 0:
                self.just_leveled_up = False

        # 更新攻击动画
        if self.attack_animation_timer > 0:
            self.attack_animation_timer -= 1

        # 更新攻击冷却
        if self.attack_cooldown > 0:
            elapsed = current_time - self.last_attack_time
            if elapsed >= self.attack_cooldown:
                self.attack_cooldown = 0

    def draw(self, screen) -> None:
        """
        绘制玩家

        Args:
            screen: 屏幕对象
        """
        # 攻击动画效果
        color = self.color
        if self.attack_animation_timer > 0:
            # 攻击时闪白光
            flash_intensity = self.attack_animation_timer / 10
            color = (
                min(255, self.color[0] + int(100 * flash_intensity)),
                min(255, self.color[1] + int(100 * flash_intensity)),
                min(255, self.color[2] + int(100 * flash_intensity))
            )

        # 绘制玩家
        pygame.draw.rect(screen, color, self.rect)

        # 绘制武器效果
        if self.weapon_tier > 1:
            weapon_color = self._get_weapon_color()
            weapon_rect = pygame.Rect(self.rect.right - 5, self.rect.centery - 2, 15, 4)
            pygame.draw.rect(screen, weapon_color, weapon_rect)

        # 升级特效
        if self.just_leveled_up and self.level_up_timer > 0:
            self._draw_level_up_effect(screen)

    def _get_weapon_color(self) -> Tuple[int, int, int]:
        """获取武器颜色"""
        weapon_colors = {
            1: (150, 150, 150),  # 灰色
            2: (100, 150, 255),  # 蓝色
            3: (50, 50, 50),     # 黑色
            4: (255, 255, 255),  # 白色
            5: (255, 0, 255)     # 紫色
        }
        return weapon_colors.get(self.weapon_tier, (150, 150, 150))

    def _draw_level_up_effect(self, screen) -> None:
        """绘制升级特效"""
        # 在玩家周围绘制光环
        center = self.rect.center
        radius = 30 + (60 - self.level_up_timer)

        # 透明度渐变
        alpha = self.level_up_timer / 60

        # 绘制多个圆环
        for i in range(3):
            ring_radius = radius + i * 10
            color = (
                int(255 * alpha),
                int(215 * alpha),
                int(0 * alpha)
            )
            pygame.draw.circle(screen, color, center, ring_radius, 2)

    def get_status_info(self) -> dict:
        """
        获取玩家状态信息

        Returns:
            状态信息字典
        """
        return {
            PlayerAttributes.LEVEL: self.level,
            PlayerAttributes.EXP: self.exp,
            PlayerAttributes.NEXT_EXP: self.next_exp,
            'exp_percent': self.exp / self.next_exp,
            PlayerAttributes.ATTACK_POWER: self.attack_power,
            PlayerAttributes.COMBO: self.combo,
            PlayerAttributes.MAX_COMBO: self.max_combo,
            PlayerAttributes.STAMINA: self.stamina,
            PlayerAttributes.MAX_STAMINA: self.max_stamina,
            PlayerAttributes.CRIT_RATE: self.crit_rate,
            PlayerAttributes.WEAPON_TIER: self.weapon_tier,
            PlayerAttributes.COINS: self.coins,
            PlayerAttributes.LOCATION: self.location,
            PlayerAttributes.AI_AFFINITY: self.ai_affinity
        }

    def _validate_attributes(self):
        """
        验证Player对象是否包含所有必需的属性

        Raises:
            AttributeError: 如果缺少必需属性
        """
        validation_result = validate_player_attributes(self)
        if not validation_result["is_valid"]:
            missing_attrs = validation_result["missing_attributes"]
            error_msg = f"Player对象缺少必需属性: {', '.join(missing_attrs)}"
            raise AttributeError(error_msg)

    def get_safe_attr(self, attr_name: str, default: Any = None) -> Any:
        """
        安全地获取属性，支持标准属性名映射

        Args:
            attr_name: 属性名
            default: 默认值

        Returns:
            属性值或默认值
        """
        return get_safe_attribute(self, attr_name, default)

    def has_standard_attributes(self) -> bool:
        """
        检查是否包含所有标准玩家属性

        Returns:
            bool: 是否包含所有标准属性
        """
        return validate_player_attributes(self)["is_valid"]

    def reset(self) -> None:
        """重置玩家状态"""
        self.__init__()
