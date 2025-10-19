from typing import List, Dict, Any, Optional, Tuple
from .ai_interface import AIContext
import time
import math
from collections import deque
from dataclasses import dataclass
import logging


@dataclass
class PlayerPattern:
    """玩家行为模式数据结构"""
    avg_attack_interval: float = 2.0    # 平均攻击间隔
    attack_frequency: float = 0.5       # 攻击频率（每秒）
    crit_frequency: float = 0.1         # 暴击频率
    combo_tendency: float = 0.3         # 连击倾向（0-1）
    stamina_management: float = 0.8     # 体力管理能力
    aggression_level: float = 0.5       # 攻击性水平
    consistency_score: float = 0.7      # 一致性评分
    max_combo_achieved: int = 0         # 达到的最大连击
    total_attacks: int = 0              # 总攻击次数
    total_damage: int = 0               # 总伤害
    preferred_attack_timing: List[float] = None  # 偏好的攻击时机


@dataclass
class GameStateSnapshot:
    """游戏状态快照"""
    timestamp: float
    player_level: int
    player_hp: int  # 注意：这里实际存储的是player的stamina值，为了保持历史兼容性
    player_stamina: int
    enemy_hp: int
    combo_count: int
    recent_damage: int
    is_crit: bool
    location: str


class ContextEngine:
    """上下文管理器 - 负责分析玩家行为模式和构建AI上下文"""

    def __init__(self, max_history_size: int = 200):
        self.max_history_size = max_history_size
        self.context_history: List[AIContext] = []
        self.game_state_snapshots: List[GameStateSnapshot] = []
        self.player_patterns = PlayerPattern()
        self.attack_timestamps = deque(maxlen=50)  # 最近50次攻击时间
        self.combo_timestamps = deque(maxlen=20)   # 最近20次连击时间
        self.crit_timestamps = deque(maxlen=30)    # 最近30次暴击时间
        self.logger = logging.getLogger(__name__)

        # 统计数据
        self.session_start_time = time.time()
        self.last_analysis_time = time.time()
        self.analysis_interval = 5.0  # 每5秒分析一次模式

    def build_context(self,
                     player,
                     enemy,
                     ai_agent,
                     additional_data: Optional[Dict[str, Any]] = None) -> AIContext:
        """
        构建当前游戏上下文

        Args:
            player: 玩家对象
            enemy: 敌人对象
            ai_agent: AI代理对象
            additional_data: 额外数据

        Returns:
            构建好的AI上下文
        """
        current_time = time.time()

        # 计算时间相关数据
        time_since_last_comment = current_time - getattr(ai_agent, 'last_comment_time', 0)
        time_since_last_attack = self._calculate_time_since_last_attack(current_time)
        time_since_last_crit = self._calculate_time_since_last_crit(current_time)

        # 获取玩家数据
        player_data = self._extract_player_data(player)
        enemy_data = self._extract_enemy_data(enemy)
        ai_data = self._extract_ai_data(ai_agent)

        # 构建上下文
        context = AIContext(
            player_level=player_data['level'],
            player_combo=player_data['combo'],
            player_power=player_data['attack_power'],
            enemy_hp_percent=enemy_data['hp_percent'],
            recent_damage=enemy_data['last_damage'],
            ai_affinity=ai_data['bond'],
            location=player_data['location'],
            time_since_last_comment=time_since_last_comment,
            player_stamina=player_data['stamina'],
            weapon_tier=player_data['weapon_tier'],
            total_coins=player_data['coins'],
            is_crit_hit=enemy_data['last_damage'] > player_data['attack_power'] * 1.5,
            is_level_up=player_data['just_leveled_up'],
            max_combo_achieved=player_data['max_combo'],
            attack_frequency=self.player_patterns.attack_frequency,
            crit_frequency=self.player_patterns.crit_frequency,
            combo_tendency=self.player_patterns.combo_tendency
        )

        # 添加额外数据
        if additional_data:
            for key, value in additional_data.items():
                if hasattr(context, key):
                    setattr(context, key, value)

        # 记录历史
        self._record_context(context)
        self._record_game_state_snapshot(player, enemy, current_time)

        # 定期分析玩家模式
        if current_time - self.last_analysis_time >= self.analysis_interval:
            self._analyze_player_patterns()
            self.last_analysis_time = current_time

        return context

    def _extract_player_data(self, player) -> Dict[str, Any]:
        """提取玩家数据"""
        return {
            'level': getattr(player, 'level', 1),
            'combo': getattr(player, 'combo', 0),
            'attack_power': getattr(player, 'attack_power', 10),
            'stamina': getattr(player, 'stamina', 100),
            'weapon_tier': getattr(player, 'weapon_tier', 1),
            'coins': getattr(player, 'coins', 0),
            'location': getattr(player, 'location', '新手村'),
            'max_combo': getattr(player, 'max_combo', 0),
            'just_leveled_up': getattr(player, 'just_leveled_up', False)
        }

    def _extract_enemy_data(self, enemy) -> Dict[str, Any]:
        """提取敌人数据"""
        max_hp = getattr(enemy, 'max_hp', 100)
        current_hp = getattr(enemy, 'hp', max_hp)
        return {
            'hp_percent': current_hp / max_hp if max_hp > 0 else 0,
            'last_damage': getattr(enemy, 'last_damage', 0)
        }

    def _extract_ai_data(self, ai_agent) -> Dict[str, Any]:
        """提取AI数据"""
        return {
            'bond': getattr(ai_agent, 'bond', 10)
        }

    def _record_context(self, context: AIContext) -> None:
        """记录上下文历史"""
        self.context_history.append(context)
        if len(self.context_history) > self.max_history_size:
            self.context_history.pop(0)

    def _record_game_state_snapshot(self, player, enemy, timestamp: float) -> None:
        """记录游戏状态快照"""
        snapshot = GameStateSnapshot(
            timestamp=timestamp,
            player_level=getattr(player, 'level', 1),
            player_hp=getattr(player, 'stamina', 100),  # 使用stamina而不是hp
            player_stamina=getattr(player, 'stamina', 100),
            enemy_hp=getattr(enemy, 'hp', 100),
            combo_count=getattr(player, 'combo', 0),
            recent_damage=getattr(enemy, 'last_damage', 0),
            is_crit=getattr(enemy, 'last_damage', 0) > getattr(player, 'attack_power', 10) * 1.5,
            location=getattr(player, 'location', '新手村')
        )
        self.game_state_snapshots.append(snapshot)

        # 限制快照数量
        if len(self.game_state_snapshots) > self.max_history_size:
            self.game_state_snapshots.pop(0)

    def record_attack_event(self, is_crit: bool = False) -> None:
        """
        记录攻击事件

        Args:
            is_crit: 是否暴击
        """
        current_time = time.time()
        self.attack_timestamps.append(current_time)
        if is_crit:
            self.crit_timestamps.append(current_time)

    def record_combo_event(self, combo_count: int) -> None:
        """
        记录连击事件

        Args:
            combo_count: 连击数
        """
        current_time = time.time()
        self.combo_timestamps.append((current_time, combo_count))

        # 更新最大连击记录
        if combo_count > self.player_patterns.max_combo_achieved:
            self.player_patterns.max_combo_achieved = combo_count

    def _calculate_time_since_last_attack(self, current_time: float) -> float:
        """计算距离上次攻击的时间"""
        if not self.attack_timestamps:
            return float('inf')
        return current_time - self.attack_timestamps[-1]

    def _calculate_time_since_last_crit(self, current_time: float) -> float:
        """计算距离上次暴击的时间"""
        if not self.crit_timestamps:
            return float('inf')
        return current_time - self.crit_timestamps[-1]

    def _analyze_player_patterns(self) -> None:
        """分析玩家行为模式"""
        if len(self.attack_timestamps) < 2:
            return

        # 分析攻击频率
        self._analyze_attack_frequency()

        # 分析暴击频率
        self._analyze_crit_frequency()

        # 分析连击倾向
        self._analyze_combo_tendency()

        # 分析体力管理
        self._analyze_stamina_management()

        # 分析攻击性水平
        self._analyze_aggression_level()

        # 分析一致性
        self._analyze_consistency()

        self.logger.debug(f"Updated player patterns: {self.player_patterns}")

    def _analyze_attack_frequency(self) -> None:
        """分析攻击频率"""
        if len(self.attack_timestamps) < 2:
            return

        # 计算平均攻击间隔
        intervals = []
        for i in range(1, len(self.attack_timestamps)):
            interval = self.attack_timestamps[i] - self.attack_timestamps[i-1]
            intervals.append(interval)

        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            self.player_patterns.avg_attack_interval = avg_interval
            self.player_patterns.attack_frequency = 1.0 / avg_interval if avg_interval > 0 else 0

    def _analyze_crit_frequency(self) -> None:
        """分析暴击频率"""
        total_attacks = len(self.attack_timestamps)
        total_crits = len(self.crit_timestamps)

        if total_attacks > 0:
            self.player_patterns.crit_frequency = total_crits / total_attacks

    def _analyze_combo_tendency(self) -> None:
        """分析连击倾向"""
        if not self.combo_timestamps:
            return

        # 计算平均连击数和最大连击数
        combo_values = [combo for _, combo in self.combo_timestamps]
        if combo_values:
            avg_combo = sum(combo_values) / len(combo_values)
            # 将平均连击数标准化到0-1范围
            self.player_patterns.combo_tendency = min(1.0, avg_combo / 10.0)

    def _analyze_stamina_management(self) -> None:
        """分析体力管理能力"""
        if len(self.game_state_snapshots) < 10:
            return

        # 分析体力的使用和恢复模式
        stamina_values = [snapshot.player_stamina for snapshot in self.game_state_snapshots[-20:]]
        if stamina_values:
            avg_stamina = sum(stamina_values) / len(stamina_values)
            max_stamina = max(stamina_values)

            # 体力管理评分：基于平均体力水平和最大体力
            self.player_patterns.stamina_management = avg_stamina / max_stamina if max_stamina > 0 else 0

    def _analyze_aggression_level(self) -> None:
        """分析攻击性水平"""
        # 基于攻击频率和连击倾向计算攻击性
        attack_factor = min(1.0, self.player_patterns.attack_frequency / 2.0)  # 每秒2次攻击为高攻击性
        combo_factor = self.player_patterns.combo_tendency

        self.player_patterns.aggression_level = (attack_factor + combo_factor) / 2.0

    def _analyze_consistency(self) -> None:
        """分析一致性评分"""
        if len(self.attack_timestamps) < 5:
            return

        # 计算攻击间隔的一致性
        intervals = []
        for i in range(1, len(self.attack_timestamps)):
            interval = self.attack_timestamps[i] - self.attack_timestamps[i-1]
            intervals.append(interval)

        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            variance = sum((interval - avg_interval) ** 2 for interval in intervals) / len(intervals)
            std_dev = math.sqrt(variance)

            # 一致性评分：标准差越小，一致性越高
            consistency = max(0, 1.0 - (std_dev / avg_interval)) if avg_interval > 0 else 0
            self.player_patterns.consistency_score = consistency

    def get_player_insights(self) -> Dict[str, Any]:
        """
        获取玩家洞察分析

        Returns:
            玩家洞察数据
        """
        return {
            'patterns': self.player_patterns,
            'session_duration': time.time() - self.session_start_time,
            'total_attacks': len(self.attack_timestamps),
            'total_crits': len(self.crit_timestamps),
            'max_combo_streak': self.player_patterns.max_combo_achieved,
            'attack_style': self._classify_attack_style(),
            'skill_level': self._estimate_skill_level(),
            'recommendations': self._generate_recommendations()
        }

    def _classify_attack_style(self) -> str:
        """分类攻击风格"""
        if self.player_patterns.aggression_level > 0.7:
            if self.player_patterns.combo_tendency > 0.6:
                return "激进连击型"
            else:
                return "激进稳定型"
        elif self.player_patterns.combo_tendency > 0.6:
            return "技巧连击型"
        elif self.player_patterns.consistency_score > 0.7:
            return "稳定节奏型"
        else:
            return "谨慎试探型"

    def _estimate_skill_level(self) -> str:
        """估算技能水平"""
        skill_score = (
            self.player_patterns.combo_tendency * 0.3 +
            self.player_patterns.stamina_management * 0.2 +
            self.player_patterns.consistency_score * 0.2 +
            self.player_patterns.crit_frequency * 0.3
        )

        if skill_score > 0.8:
            return "专家"
        elif skill_score > 0.6:
            return "熟练"
        elif skill_score > 0.4:
            return "中级"
        elif skill_score > 0.2:
            return "初级"
        else:
            return "新手"

    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if self.player_patterns.stamina_management < 0.5:
            recommendations.append("注意体力管理，避免体力耗尽")

        if self.player_patterns.combo_tendency < 0.3:
            recommendations.append("尝试保持连击，提升伤害输出")

        if self.player_patterns.consistency_score < 0.5:
            recommendations.append("保持稳定的攻击节奏")

        if self.player_patterns.crit_frequency < 0.1:
            recommendations.append("关注时机，提升暴击率")

        return recommendations

    def reset_engine(self) -> None:
        """重置上下文引擎"""
        self.context_history.clear()
        self.game_state_snapshots.clear()
        self.attack_timestamps.clear()
        self.combo_timestamps.clear()
        self.crit_timestamps.clear()
        self.player_patterns = PlayerPattern()
        self.session_start_time = time.time()
        self.last_analysis_time = time.time()

    def export_analysis_data(self) -> Dict[str, Any]:
        """
        导出分析数据

        Returns:
            完整的分析数据
        """
        return {
            'player_patterns': self.player_patterns.__dict__,
            'context_history_count': len(self.context_history),
            'session_stats': {
                'duration': time.time() - self.session_start_time,
                'total_attacks': len(self.attack_timestamps),
                'total_crits': len(self.crit_timestamps),
                'max_combo': self.player_patterns.max_combo_achieved
            },
            'insights': self.get_player_insights()
        }