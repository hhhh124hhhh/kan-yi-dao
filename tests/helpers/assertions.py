"""
自定义断言工具
提供更丰富的测试断言方法
"""

import pygame
from src.ai.ai_interface import AIResponse, AIMood
from typing import Any, List, Optional, Tuple, Union


def assert_ai_response(
    response: Optional[AIResponse],
    expected_text_contains: Optional[str] = None,
    expected_mood: Optional[AIMood] = None,
    expected_priority_range: Optional[Tuple[int, int]] = None,
    message: str = "AI响应断言失败"
) -> None:
    """
    断言AI响应的各种属性

    Args:
        response: AI响应对象
        expected_text_contains: 期望包含的文本内容
        expected_mood: 期望的情绪状态
        expected_priority_range: 期望的优先级范围 (min, max)
        message: 断言失败时的消息
    """
    if response is None:
        raise AssertionError(f"{message}: AI响应为空")

    if expected_text_contains and expected_text_contains not in response.text:
        raise AssertionError(
            f"{message}: 响应文本不包含期望内容: {expected_text_contains}"
        )

    if expected_mood and response.mood != expected_mood:
        raise AssertionError(
            f"{message}: 情绪状态不匹配，期望: {expected_mood.value}, 实际: {response.mood.value}"
        )

    if expected_priority_range:
        min_priority, max_priority = expected_priority_range
        if not (min_priority <= response.priority <= max_priority):
            raise AssertionError(
                f"{message}: 优先级超出范围，期望: {expected_priority_range}, "
                f"实际: {response.priority}"
            )


def assert_rect_overlap(
    rect1: pygame.Rect,
    rect2: pygame.Rect,
    message: str = "矩形重叠断言失败"
) -> None:
    """
    断言两个矩形重叠

    Args:
        rect1: 第一个矩形
        rect2: 第二个矩形
        message: 断言失败时的消息
    """
    if not rect1.colliderect(rect2):
        raise AssertionError(f"{message}: 矩形不重叠")


def assert_color_similarity(
    color1: tuple,
    color2: tuple,
    tolerance: int = 5,
    message: str = "颜色相似度断言失败"
) -> None:
    """
    断言两个颜色相似

    Args:
        color1: 第一个颜色 (R, G, B)
        color2: 第二个颜色 (R, G, B)
        tolerance: 颜色差异容忍度
        message: 断言失败时的消息
    """
    if len(color1) != 3 or len(color2) != 3:
        raise ValueError("颜色必须是3元组 (R, G, B)")

    diff = sum(abs(c1 - c2) for c1, c2 in zip(color1, color2))
    if diff > tolerance:
        raise AssertionError(
            f"{message}: 颜色差异过大，差异: {diff}, 容忍度: {tolerance}"
        )


def assert_range_inclusive(
    value: float,
    min_val: float,
    max_val: float,
    message: str = "范围断言失败"
) -> None:
    """
    断言值在指定范围内（包含边界）

    Args:
        value: 要检查的值
        min_val: 最小值
        max_val: 最大值
        message: 断言失败时的消息
    """
    if not (min_val <= value <= max_val):
        raise AssertionError(
            f"{message}: 值 {value} 不在范围 [{min_val}, {max_val}] 内"
        )


def assert_percentage(
    value: float,
    message: str = "百分比断言失败"
) -> None:
    """
    断言值在0-100百分比范围内

    Args:
        value: 要检查的值
        message: 断言失败时的消息
    """
    assert_range_inclusive(value, 0.0, 100.0, f"{message}: 百分比值")


def assert_not_empty(
    value: Any,
    message: str = "非空断言失败"
) -> None:
    """
    断言值不为空

    Args:
        value: 要检查的值
        message: 断言失败时的消息
    """
    if value is None:
        raise AssertionError(f"{message}: 值为None")

    if isinstance(value, (str, list, tuple)) and len(value) == 0:
        raise AssertionError(f"{message}: 值为空序列")

    if isinstance(value, (dict)) and len(value) == 0:
        raise AssertionError(f"{message}: 值为空字典")


def assert_probability(
    value: float,
    message: str = "概率断言失败"
) -> None:
    """
    断言值在有效概率范围内 [0, 1]

    Args:
        value: 要检查的概率值
        message: 断言失败时的消息
    """
    assert_range_inclusive(value, 0.0, 1.0, f"{message}: 概率值")


class GameTestAssertions:
    """游戏测试专用断言集合"""

    @staticmethod
    def assert_player_stats_valid(player, message: str = "玩家状态无效"):
        """断言玩家状态有效"""
        assert_not_empty(player.level, f"{message}: 等级无效")
        assert_not_empty(player.attack_power, f"{message}: 攻击力无效")
        assert_range_inclusive(player.level, 1, 100, f"{message}: 等级超出范围")
        assert_range_inclusive(player.attack_power, 1, 1000, f"{message}: 攻击力超出范围")
        assert_percentage(player.stamina, f"{message}: 体力值不是百分比")

    @staticmethod
    def assert_enemy_stats_valid(enemy, message: str = "敌人状态无效"):
        """断言敌人状态有效"""
        assert_not_empty(enemy.hp, f"{message}: 生命值无效")
        assert_not_empty(enemy.max_hp, f"{message}: 最大生命值无效")
        assert_range_inclusive(enemy.hp, 0, enemy.max_hp, f"{message}: 生命值超出范围")
        assert_percentage(enemy.hp / enemy.max_hp * 100, f"{message}: 生命值百分比计算错误")

    @staticmethod
    def assert_collision_valid(player_rect: pygame.Rect, enemy_rect: pygame.Rect, message: str = "碰撞检测无效"):
        """断言碰撞检测逻辑正确"""
        # 碰撞检测是否合理（比如攻击范围是否合理）
        attack_range = 100  # 假设最大攻击范围
        distance = ((player_rect.centerx - enemy_rect.centerx) ** 2 +
                    (player_rect.centery - enemy_rect.centery) ** 2) ** 0.5

        assert_range_inclusive(distance, 0, attack_range * 2, f"{message}: 攻击距离超出合理范围")