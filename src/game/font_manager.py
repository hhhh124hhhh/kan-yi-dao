"""
字体管理器 - 负责管理系统字体和文本渲染
优先使用系统自带的中文字体，支持智能回退机制
"""

import pygame
import logging
from typing import List, Dict, Optional, Tuple
from .game_constants import UIConstants


class FontManager:
    """字体管理器"""

    def __init__(self):
        """初始化字体管理器"""
        self.logger = logging.getLogger(__name__)

        # 系统字体优先级列表（按兼容性和质量排序）
        self.chinese_font_priorities = [
            # Windows系统字体
            [
                'Microsoft YaHei',      # 微软雅黑
                'SimHei',             # 黑体
                'SimSun',             # 宋体
                'FangSong',           # 仿宋
                'KaiTi',              # 楷体
                'FangSong_GB2312',     # 仿宋GB2312
            ],
            # macOS系统字体
            [
                'PingFang SC',        # 苹方SC
                'Hiragino Sans GB',   # 冬青黑体
                'STHeiti',           # 华文黑体
                'STSong',            # 华文宋体
                'STKaiti',          # 华文楷体
                'STFangsong',       # 华文仿宋
            ],
            # Linux系统字体
            [
                'Noto Sans CJK SC',   # Google Noto Sans
                'WenQuanYi Micro Hei', # 文泉驿微米黑
                'Source Han Sans CN', # 思源黑体
                'AR PL UMing CN',     # 文泉驿明体
                'AR PL UKai CN',     # 文泉驿楷体
                'AR PL Zenhei',      # 文泉驿正黑
            ],
            # 通用备选字体
            [
                'Arial Unicode MS',    # Arial Unicode (支持中文)
                'DejaVu Sans',         # DejaVu字体
                'Liberation Sans',     # Liberation字体
            ]
        ]

        # 字体缓存
        self.font_cache: Dict[str, pygame.font.Font] = {}

        # 可用字体列表
        self.available_chinese_fonts: List[str] = []

        # 检测系统可用字体
        self._detect_system_fonts()

        self.logger.info(f"字体管理器初始化完成，检测到 {len(self.available_chinese_fonts)} 个中文字体")

    def _detect_system_fonts(self) -> None:
        """检测系统可用的中文字体"""
        self.available_chinese_fonts = []

        for font_family in self.chinese_font_priorities:
            for font_name in font_family:
                try:
                    # 尝试创建字体
                    test_font = pygame.font.SysFont(font_name, 24)

                    # 测试中文渲染（使用常见的中文字符）
                    test_chars = "中文测试Text"
                    test_surface = test_font.render(test_chars, True, (255, 255, 255))

                    # 检查渲染结果
                    if test_surface.get_width() > 10:  # 确保不是空白的
                        self.available_chinese_fonts.append(font_name)
                        self.logger.debug(f"检测到可用字体: {font_name}")
                        break  # 找到可用字体就跳出

                except Exception as e:
                    self.logger.debug(f"字体 {font_name} 不可用: {e}")
                    continue

    def get_chinese_font(self, size: int = 24, bold: bool = False) -> pygame.font.Font:
        """
        获取中文字体

        Args:
            size: 字体大小
            bold: 是否使用粗体

        Returns:
            pygame.font.Font: 可用的字体对象
        """
        cache_key = f"chinese_{size}_{'bold' if bold else 'regular'}"

        if cache_key not in self.font_cache:
            self.font_cache[cache_key] = self._load_best_chinese_font(size, bold)

        return self.font_cache[cache_key]

    def _load_best_chinese_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        """
        加载最佳可用的中文字体

        Args:
            size: 字体大小
            bold: 是否使用粗体

        Returns:
            pygame.font.Font: 字体对象
        """
        # 尝试按优先级顺序加载字体
        for font_name in self.available_chinese_fonts:
            try:
                font = pygame.font.SysFont(font_name, size, bold=bold)

                # 验证字体是否真的支持中文
                test_surface = font.render("测试", True, (255, 255, 255))
                if test_surface.get_width() > 5:
                    return font

            except Exception as e:
                self.logger.warning(f"加载字体 {font_name} 失败: {e}")
                continue

        # 如果所有中文字体都失败，尝试通用字体
        fallback_fonts = ['Arial Unicode MS', 'DejaVu Sans']
        for font_name in fallback_fonts:
            try:
                font = pygame.font.SysFont(font_name, size, bold=bold)
                # 测试基本渲染能力
                test_surface = font.render("Test", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    self.logger.warning(f"使用回退字体: {font_name}")
                    return font

            except Exception as e:
                self.logger.warning(f"回退字体 {font_name} 也失败: {e}")
                continue

        # 最后使用默认字体
        try:
            font = pygame.font.Font(None, size, bold=bold)
            self.logger.warning("使用系统默认字体")
            return font

        except Exception as e:
            self.logger.error(f"创建默认字体失败: {e}")
            # 返回最小的字体对象作为最后保障
            return pygame.font.Font(None, 16)

    def get_fallback_font(self, size: int = 24) -> pygame.font.Font:
        """
        获取回退字体（用于紧急情况）

        Args:
            size: 字体大小

        Returns:
            pygame.font.Font: 默认字体对象
        """
        try:
            return pygame.font.Font(None, size)
        except:
            return pygame.font.Font(None, 16)

    def get_font_info(self) -> Dict[str, any]:
        """
        获取字体信息

        Returns:
            Dict[str, any]: 包含字体统计信息的字典
        """
        return {
            'available_chinese_fonts': len(self.available_chinese_fonts),
            'cached_fonts_count': len(self.font_cache),
            'font_priorities_count': len(self.chinese_font_priorities),
            'available_fonts': self.available_chinese_fonts.copy()[:5]  # 只显示前5个
        }

    def clear_cache(self) -> None:
        """清空字体缓存"""
        self.font_cache.clear()
        self.logger.info("字体缓存已清空")

    def preload_fonts(self, sizes: List[int] = [16, 18, 20, 24, 32, 48]) -> None:
        """
        预加载常用字体以提高性能

        Args:
            sizes: 要预加载的字体大小列表
        """
        for size in sizes:
            for bold in [False, True]:
                self.get_chinese_font(size, bold)

        self.logger.info(f"预加载字体完成，共加载了 {len(sizes) * 2} 个字体")

    def test_font_rendering(self, text: str = "中文测试文本") -> bool:
        """
        测试字体渲染功能

        Args:
            text: 测试文本

        Returns:
            bool: 渲染是否成功
        """
        try:
            font = self.get_chinese_font(24)
            surface = font.render(text, True, (255, 255, 255))
            return surface.get_width() > 0 and surface.get_height() > 0
        except Exception as e:
            self.logger.error(f"字体渲染测试失败: {e}")
            return False

    def get_font_style(self, font_type: str = 'chinese') -> str:
        """
        获取字体样式描述

        Args:
            font_type: 字体类型 ('chinese', 'english', 'system')

        Returns:
            str: 字体样式描述
        """
        if font_type == 'chinese':
            if self.available_chinese_fonts:
                return f"系统字体: {self.available_chinese_fonts[0]}"
            else:
                return "无可用中文字体，使用默认字体"
        elif font_type == 'english':
            return "系统默认字体"
        else:
            return "未知字体类型"


# 全局字体管理器实例
_font_manager_instance: Optional[FontManager] = None


def get_font_manager() -> FontManager:
    """
    获取全局字体管理器实例（单例模式）

    Returns:
        FontManager: 字体管理器实例
    """
    global _font_manager_instance
    if _font_manager_instance is None:
        _font_manager_instance = FontManager()
    return _font_manager_instance


def get_chinese_text_font(size: int = 24, bold: bool = False) -> pygame.font.Font:
    """
    快速获取中文字体（便捷函数）

    Args:
        size: 字体大小
        bold: 是否使用粗体

    Returns:
        pygame.font.Font: 中文字体对象
    """
    font_manager = get_font_manager()
    return font_manager.get_chinese_font(size, bold)