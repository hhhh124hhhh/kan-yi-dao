from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time


class AIMood(Enum):
    """AI情绪状态枚举"""
    NEUTRAL = "neutral"      # 中性
    EXCITED = "excited"      # 兴奋
    TIRED = "tired"         # 疲倦
    SERIOUS = "serious"      # 严肃
    IMPRESSED = "impressed"  # 印象深刻
    ENCOURAGING = "encouraging"  # 鼓励
    MOCKING = "mocking"      # 嘲讽


@dataclass
class AIContext:
    """AI上下文信息"""
    player_level: int         # 玩家等级
    player_combo: int         # 当前连击数
    player_power: int         # 玩家攻击力
    enemy_hp_percent: float   # 敌人血量百分比
    recent_damage: int        # 最近造成的伤害
    ai_affinity: int          # AI亲密度
    location: str             # 当前位置
    time_since_last_comment: float  # 距离上次评论的时间
    player_stamina: int       # 玩家体力值
    weapon_tier: int          # 武器等级
    total_coins: int          # 总金币数
    is_crit_hit: bool         # 是否暴击
    is_level_up: bool         # 是否刚升级
    max_combo_achieved: int   # 达到的最大连击

    # 学习相关数据
    attack_frequency: float   # 攻击频率
    crit_frequency: float     # 暴击频率
    combo_tendency: float     # 连击倾向


@dataclass
class AIResponse:
    """AI回应数据结构"""
    text: str                 # 回应文本
    mood: AIMood             # 情绪状态
    priority: int            # 优先级 (1-10)
    cooldown_time: float     # 冷却时间（秒）
    affinity_change: int     # 亲密度变化值
    learning_data: Optional[Dict[str, Any]] = None  # 学习相关数据


class AIBehaviorInterface(ABC):
    """AI行为抽象基类"""

    def __init__(self):
        self.bond = 10                    # 与玩家关系值
        self.last_comment_time = 0        # 上次评论时间
        self.learning_state = {}          # 学习状态
        self.comment_history = []         # 评论历史
        self.mood_history = []            # 情绪历史

    @abstractmethod
    def generate_response(self, context: AIContext) -> Optional[AIResponse]:
        """
        根据上下文生成AI回应

        Args:
            context: 当前游戏上下文

        Returns:
            AI回应对象，如果没有合适回应则返回None
        """
        pass

    @abstractmethod
    def update_learning_state(self, context: AIContext) -> None:
        """
        更新AI学习状态

        Args:
            context: 当前游戏上下文
        """
        pass

    @abstractmethod
    def get_current_mood(self) -> AIMood:
        """
        获取当前情绪状态

        Returns:
            当前情绪状态
        """
        pass

    def update_affinity(self, change: int) -> None:
        """
        更新亲密度

        Args:
            change: 亲密度变化值
        """
        self.bond = max(0, min(100, self.bond + change))

    def can_comment(self, context: AIContext) -> bool:
        """
        检查是否可以发表评论

        Args:
            context: 当前游戏上下文

        Returns:
            是否可以评论
        """
        return context.time_since_last_comment >= self.get_min_comment_interval()

    def get_min_comment_interval(self) -> float:
        """
        获取最小评论间隔

        Returns:
            最小间隔时间（秒）
        """
        return 2.0  # 默认2秒冷却

    def record_comment(self, response: AIResponse) -> None:
        """
        记录评论历史

        Args:
            response: AI回应
        """
        self.comment_history.append({
            'text': response.text,
            'mood': response.mood.value,
            'timestamp': time.time(),
            'priority': response.priority
        })

        # 保留最近50条评论
        if len(self.comment_history) > 50:
            self.comment_history.pop(0)

    def get_learning_stats(self) -> Dict[str, Any]:
        """
        获取学习统计信息

        Returns:
            学习统计数据
        """
        return {
            'bond': self.bond,
            'total_comments': len(self.comment_history),
            'learning_state': self.learning_state,
            'mood_distribution': self._calculate_mood_distribution()
        }

    def _calculate_mood_distribution(self) -> Dict[str, float]:
        """
        计算情绪分布

        Returns:
            情绪分布统计
        """
        if not self.comment_history:
            return {}

        mood_counts = {}
        for comment in self.comment_history:
            mood = comment['mood']
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

        total = len(self.comment_history)
        return {mood: count / total for mood, count in mood_counts.items()}

    def reset_state(self) -> None:
        """重置AI状态"""
        self.bond = 10
        self.last_comment_time = 0
        self.learning_state = {}
        self.comment_history = []
        self.mood_history = []


class AILearningInterface(ABC):
    """AI学习功能接口"""

    @abstractmethod
    def analyze_player_pattern(self, context_history: List[AIContext]) -> Dict[str, Any]:
        """
        分析玩家行为模式

        Args:
            context_history: 上下文历史记录

        Returns:
            分析结果
        """
        pass

    @abstractmethod
    def adapt_behavior(self, pattern_analysis: Dict[str, Any]) -> None:
        """
        根据模式分析调整行为

        Args:
            pattern_analysis: 模式分析结果
        """
        pass

    @abstractmethod
    def predict_player_action(self, context: AIContext) -> Optional[Dict[str, float]]:
        """
        预测玩家下一步行动

        Args:
            context: 当前上下文

        Returns:
            预测结果（包含概率）
        """
        pass


class AIPersonalityInterface(ABC):
    """AI性格特征接口"""

    @abstractmethod
    def get_personality_traits(self) -> Dict[str, float]:
        """
        获取性格特征

        Returns:
            性格特征字典
        """
        pass

    @abstractmethod
    def adjust_response_tone(self, base_response: str, mood: AIMood) -> str:
        """
        根据性格调整回应语气

        Args:
            base_response: 基础回应
            mood: 情绪状态

        Returns:
            调整后的回应
        """
        pass

    @abstractmethod
    def should_make_special_comment(self, context: AIContext) -> bool:
        """
        判断是否应该发表特殊评论

        Args:
            context: 当前上下文

        Returns:
            是否应该发表特殊评论
        """
        pass