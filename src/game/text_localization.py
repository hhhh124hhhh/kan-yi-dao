"""
文本本地化系统 - 负责管理游戏中的所有文本内容
支持中文显示和多种文本类型管理
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum
from .font_manager import get_chinese_text_font


class TextType(Enum):
    """文本类型枚举"""
    UI = "ui"                    # UI界面文本
    GAMEPLAY = "gameplay"        # 游戏玩法文本
    EFFECT = "effect"            # 特效文本
    ENEMY = "enemy"              # 敌人相关文本
    SYSTEM = "system"            # 系统消息文本
    ACHIEVEMENT = "achievement"  # 成就文本
    MENU = "menu"                # 菜单文本


class TextLocalization:
    """文本本地化管理器"""

    def __init__(self):
        """初始化文本本地化系统"""
        self.logger = logging.getLogger(__name__)

        # 文本数据库
        self.text_database = self._initialize_text_database()

        # 字体缓存
        self.font_cache: Dict[int, Any] = {}

        self.logger.info("文本本地化系统初始化完成")

    def _initialize_text_database(self) -> Dict[str, Dict[str, str]]:
        """
        初始化文本数据库

        Returns:
            Dict[str, Dict[str, str]]: 文本数据库
        """
        return {
            # UI界面文本
            TextType.UI.value: {
                "pause_title": "游戏暂停",
                "pause_resume": "按 P 继续",
                "pause_exit": "ESC 退出",
                "pause_help": "游戏帮助",
                "level": "等级",
                "exp": "经验",
                "coins": "金币",
                "combo": "连击",
                "stamina": "体力",
                "attack_power": "攻击力",
                "enemy_hp": "敌人血量",
                "game_time": "游戏时间",
                "victory": "胜利！",
                "defeat": "失败！",
                "loading": "加载中...",
                "press_any_key": "按任意键继续"
            },

            # 游戏玩法文本
            TextType.GAMEPLAY.value: {
                "level_up": "升级了！",
                "new_high_score": "新纪录！",
                "combo_break": "连击中断",
                "stamina_warning": "体力不足！",
                "critical_hit": "暴击！",
                "perfect_attack": "完美攻击！",
                "miss": "未命中",
                "game_start": "游戏开始",
                "game_over": "游戏结束",
                "restart": "重新开始",
                "quit": "退出游戏"
            },

            # 特效文本
            TextType.EFFECT.value: {
                "damage_prefix": "",
                "crit_damage_prefix": "暴击！",
                "heal_prefix": "恢复",
                "exp_gain": "经验",
                "coin_gain": "金币",
                "combo_text": "连击",
                "max_combo": "最高连击",
                "power_up": "力量提升",
                "speed_up": "速度提升",
                "defense_up": "防御提升"
            },

            # 敌人相关文本
            TextType.ENEMY.value: {
                "strawman": "稻草人",
                "training_dummy": "训练假人",
                "boss": "首领",
                "enemy_defeated": "已被击败",
                "new_enemy": "新敌人出现",
                "enemy_weak": "敌人虚弱",
                "enemy_enraged": "敌人狂暴"
            },

            # 系统消息文本
            TextType.SYSTEM.value: {
                "save_complete": "游戏已保存",
                "save_failed": "保存失败",
                "load_complete": "游戏已加载",
                "load_failed": "加载失败",
                "settings_saved": "设置已保存",
                "error_font_load": "字体加载失败",
                "error_file_missing": "文件缺失",
                "error_network": "网络错误",
                "warning_low_memory": "内存不足警告"
            },

            # 成就文本
            TextType.ACHIEVEMENT.value: {
                "first_blood": "初次击杀",
                "combo_master": "连击大师",
                "level_veteran": "等级老兵",
                "damage_king": "伤害之王",
                "persistent_player": "坚持不懈",
                "speed_runner": "极速通关",
                "perfectionist": "完美主义",
                "explorer": "探索者"
            },

            # 菜单文本
            TextType.MENU.value: {
                "new_game": "新游戏",
                "continue_game": "继续游戏",
                "load_game": "加载游戏",
                "save_game": "保存游戏",
                "settings": "设置",
                "about": "关于",
                "exit": "退出",
                "language": "语言",
                "sound": "音效",
                "graphics": "图形",
                "controls": "控制",
                "back": "返回",
                "confirm": "确认",
                "cancel": "取消"
            }
        }

    def get_text(self, text_type: TextType, text_key: str, **kwargs) -> str:
        """
        获取本地化文本

        Args:
            text_type: 文本类型
            text_key: 文本键值
            **kwargs: 格式化参数

        Returns:
            str: 本地化文本
        """
        try:
            # 获取文本数据库
            type_database = self.text_database.get(text_type.value, {})

            # 获取原始文本
            original_text = type_database.get(text_key, text_key)

            # 如果有格式化参数，进行格式化
            if kwargs:
                try:
                    return original_text.format(**kwargs)
                except (KeyError, ValueError) as e:
                    self.logger.warning(f"文本格式化失败: {original_text}, 参数: {kwargs}, 错误: {e}")
                    return original_text

            return original_text

        except Exception as e:
            self.logger.error(f"获取文本失败: type={text_type}, key={text_key}, 错误: {e}")
            return text_key  # 返回键值作为回退

    def render_text(self, text: str, font_size: int = 24, color: tuple = (255, 255, 255),
                   bold: bool = False, antialias: bool = True) -> Any:
        """
        渲染中文文本为Surface

        Args:
            text: 要渲染的文本
            font_size: 字体大小
            color: 文本颜色
            bold: 是否粗体
            antialias: 是否抗锯齿

        Returns:
            pygame.Surface: 渲染后的文本Surface
        """
        try:
            # 获取字体
            font = get_chinese_text_font(font_size, bold)

            # 渲染文本
            surface = font.render(text, antialias, color)

            return surface

        except Exception as e:
            self.logger.error(f"文本渲染失败: text='{text}', size={font_size}, 错误: {e}")
            # 创建回退Surface
            import pygame
            try:
                fallback_font = pygame.font.Font(None, font_size)
                return fallback_font.render(text, antialias, color)
            except:
                # 最后的回退方案
                fallback_font = pygame.font.Font(None, 16)
                return fallback_font.render("Text Error", antialias, (255, 0, 0))

    def get_ui_text(self, key: str, **kwargs) -> str:
        """获取UI文本的便捷方法"""
        return self.get_text(TextType.UI, key, **kwargs)

    def get_gameplay_text(self, key: str, **kwargs) -> str:
        """获取游戏玩法文本的便捷方法"""
        return self.get_text(TextType.GAMEPLAY, key, **kwargs)

    def get_effect_text(self, key: str, **kwargs) -> str:
        """获取特效文本的便捷方法"""
        return self.get_text(TextType.EFFECT, key, **kwargs)

    def get_enemy_text(self, key: str, **kwargs) -> str:
        """获取敌人文本的便捷方法"""
        return self.get_text(TextType.ENEMY, key, **kwargs)

    def get_system_text(self, key: str, **kwargs) -> str:
        """获取系统文本的便捷方法"""
        return self.get_text(TextType.SYSTEM, key, **kwargs)

    def get_achievement_text(self, key: str, **kwargs) -> str:
        """获取成就文本的便捷方法"""
        return self.get_text(TextType.ACHIEVEMENT, key, **kwargs)

    def get_menu_text(self, key: str, **kwargs) -> str:
        """获取菜单文本的便捷方法"""
        return self.get_text(TextType.MENU, key, **kwargs)

    def format_damage_text(self, damage: int, is_crit: bool = False) -> str:
        """
        格式化伤害文本

        Args:
            damage: 伤害值
            is_crit: 是否暴击

        Returns:
            str: 格式化后的伤害文本
        """
        if is_crit:
            return f"{self.get_effect_text('crit_damage_prefix')}{damage}"
        else:
            return f"{self.get_effect_text('damage_prefix')}{damage}"

    def format_exp_text(self, exp_amount: int) -> str:
        """
        格式化经验文本

        Args:
            exp_amount: 经验值

        Returns:
            str: 格式化后的经验文本
        """
        return f"+{exp_amount} {self.get_effect_text('exp_gain')}"

    def format_coin_text(self, coin_amount: int) -> str:
        """
        格式化金币文本

        Args:
            coin_amount: 金币数量

        Returns:
            str: 格式化后的金币文本
        """
        return f"+{coin_amount} {self.get_effect_text('coin_gain')}"

    def format_combo_text(self, combo_count: int) -> str:
        """
        格式化连击文本

        Args:
            combo_count: 连击数

        Returns:
            str: 格式化后的连击文本
        """
        return f"{self.get_effect_text('combo_text')} {combo_count}"

    def get_enemy_name(self, enemy_type: str) -> str:
        """
        获取敌人名称

        Args:
            enemy_type: 敌人类型

        Returns:
            str: 敌人名称
        """
        return self.get_enemy_text(enemy_type.lower())

    def add_custom_text(self, text_type: TextType, key: str, text: str) -> None:
        """
        添加自定义文本

        Args:
            text_type: 文本类型
            key: 文本键值
            text: 文本内容
        """
        if text_type.value not in self.text_database:
            self.text_database[text_type.value] = {}

        self.text_database[text_type.value][key] = text
        self.logger.info(f"添加自定义文本: {text_type.value}.{key} = '{text}'")

    def get_all_texts_by_type(self, text_type: TextType) -> Dict[str, str]:
        """
        获取指定类型的所有文本

        Args:
            text_type: 文本类型

        Returns:
            Dict[str, str]: 文本字典
        """
        return self.text_database.get(text_type.value, {}).copy()

    def validate_text_completeness(self) -> Dict[str, Any]:
        """
        验证文本完整性

        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_complete": True,
            "missing_texts": {},
            "total_text_types": len(TextType),
            "total_texts": 0
        }

        for text_type in TextType:
            type_texts = self.text_database.get(text_type.value, {})
            result["total_texts"] += len(type_texts)

            if not type_texts:
                result["is_complete"] = False
                result["missing_texts"][text_type.value] = "整个文本类型缺失"

        return result

    def get_text_statistics(self) -> Dict[str, Any]:
        """
        获取文本统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = {
            "total_text_types": len(TextType),
            "total_texts": 0,
            "texts_by_type": {},
            "longest_text": "",
            "longest_text_length": 0
        }

        for text_type in TextType:
            type_texts = self.text_database.get(text_type.value, {})
            text_count = len(type_texts)
            stats["texts_by_type"][text_type.value] = text_count
            stats["total_texts"] += text_count

            # 查找最长的文本
            for text in type_texts.values():
                if len(text) > stats["longest_text_length"]:
                    stats["longest_text"] = text
                    stats["longest_text_length"] = len(text)

        return stats


# 全局文本本地化实例
_localization_instance: Optional[TextLocalization] = None


def get_localization() -> TextLocalization:
    """
    获取全局文本本地化实例（单例模式）

    Returns:
        TextLocalization: 文本本地化实例
    """
    global _localization_instance
    if _localization_instance is None:
        _localization_instance = TextLocalization()
    return _localization_instance


def get_text(text_type: TextType, text_key: str, **kwargs) -> str:
    """
    快速获取本地化文本（便捷函数）

    Args:
        text_type: 文本类型
        text_key: 文本键值
        **kwargs: 格式化参数

    Returns:
        str: 本地化文本
    """
    localization = get_localization()
    return localization.get_text(text_type, text_key, **kwargs)


def render_chinese_text(text: str, font_size: int = 24, color: tuple = (255, 255, 255),
                      bold: bool = False) -> Any:
    """
    快速渲染中文文本（便捷函数）

    Args:
        text: 要渲染的文本
        font_size: 字体大小
        color: 文本颜色
        bold: 是否粗体

    Returns:
        pygame.Surface: 渲染后的文本Surface
    """
    localization = get_localization()
    return localization.render_text(text, font_size, color, bold)