from typing import Optional, List, Dict, Any
from .ai_interface import (
    AIBehaviorInterface, AILearningInterface, AIPersonalityInterface,
    AIContext, AIResponse, AIMood
)
import random
import time
import logging


class RuleBasedAI(AIBehaviorInterface, AILearningInterface, AIPersonalityInterface):
    """基于规则的AI实现 - 使用预定义规则生成回应"""

    def __init__(self,
                 personality_type: str = "encouraging",
                 comment_frequency: float = 0.3,
                 learning_enabled: bool = True):
        super().__init__()
        self.current_mood = AIMood.NEUTRAL
        self.personality_type = personality_type
        self.comment_frequency = comment_frequency
        self.learning_enabled = learning_enabled

        # 性格特征 (0-1)
        self.personality_traits = {
            'enthusiasm': 0.7,      # 热情程度
            'patience': 0.6,        # 耐心程度
            'competitiveness': 0.5, # 竞争性
            'humor': 0.4,           # 幽默感
            'wisdom': 0.6           # 智慧感
        }

        # 学习数据
        self.player_attack_patterns = {}
        self.player_success_rates = {}
        self.last_player_action = None
        self.consecutive_similar_actions = 0

        # 评论模板
        self.comment_templates = self._initialize_comment_templates()
        self.logger = logging.getLogger(__name__)

    def _initialize_comment_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """初始化评论模板"""
        return {
            'high_combo': [
                {"text": "连击！手感来了！再砍！⚔️", "mood": AIMood.EXCITED, "priority": 8},
                {"text": "完美节奏！继续保持！🔥", "mood": AIMood.EXCITED, "priority": 8},
                {"text": "这就是男人的节奏！💪", "mood": AIMood.ENCOURAGING, "priority": 7},
                {"text": "爽！再来十连击！⚡", "mood": AIMood.EXCITED, "priority": 9}
            ],
            'crit_hit': [
                {"text": "这一刀漂亮！🔥", "mood": AIMood.IMPRESSED, "priority": 7},
                {"text": "暴击！完美时机！⚡", "mood": AIMood.EXCITED, "priority": 8},
                {"text": "看到了吗？这就是力量！💥", "mood": AIMood.IMPRESSED, "priority": 7},
                {"text": "一刀入魂！太帅了！✨", "mood": AIMood.EXCITED, "priority": 9}
            ],
            'enemy_low_hp': [
                {"text": "就差一点！加油！💪", "mood": AIMood.ENCOURAGING, "priority": 6},
                {"text": "_finish_him！终结它！🎯", "mood": AIMood.EXCITED, "priority": 7},
                {"text": "稻草人在颤抖！🌾", "mood": AIMood.MOCKING, "priority": 5},
                {"text": "最后一击！展示你的实力！⚔️", "mood": AIMood.ENCOURAGING, "priority": 6}
            ],
            'level_up': [
                {"text": "升级了！你变强了...我能感觉到。💥", "mood": AIMood.SERIOUS, "priority": 9},
                {"text": "恭喜升级！新的力量觉醒了！✨", "mood": AIMood.EXCITED, "priority": 9},
                {"text": "不错不错，这才有男人的样子！👍", "mood": AIMood.IMPRESSED, "priority": 7},
                {"text": "成长了啊...让我更兴奋了！🔥", "mood": AIMood.EXCITED, "priority": 8}
            ],
            'low_stamina': [
                {"text": "体力不足了？休息一下也好。😌", "mood": AIMood.NEUTRAL, "priority": 5},
                {"text": "保存体力，男人要懂得张弛有度！💪", "mood": AIMood.ENCOURAGING, "priority": 6},
                {"text": "累了？这可不像你啊...💪", "mood": AIMood.MOCKING, "priority": 4},
                {"text": "调整呼吸，恢复体力再战！🌬️", "mood": AIMood.ENCOURAGING, "priority": 6}
            ],
            'high_damage': [
                {"text": "好爽啊！你这一刀真狠！🔥", "mood": AIMood.EXCITED, "priority": 8},
                {"text": "这就是我要的力量感！💥", "mood": AIMood.IMPRESSED, "priority": 7},
                {"text": "痛快！再来这样的！⚔️", "mood": AIMood.EXCITED, "priority": 8},
                {"text": "暴力美学！我喜欢！👍", "mood": AIMood.IMPRESSED, "priority": 7}
            ],
            'player_idle': [
                {"text": "停下来了？是在积蓄力量吗？🤔", "mood": AIMood.NEUTRAL, "priority": 4},
                {"text": "休息够了吗？男人要砍到天亮！🌅", "mood": AIMood.ENCOURAGING, "priority": 5},
                {"text": "怎么不砍了？稻草人会笑话你的😏", "mood": AIMood.MOCKING, "priority": 4},
                {"text": "准备下一次暴击吧！⚡", "mood": AIMood.ENCOURAGING, "priority": 5}
            ],
            'weapon_upgrade': [
                {"text": "武器升级了！手感应该更好了！✨", "mood": AIMood.EXCITED, "priority": 8},
                {"text": "新武器！试试它的锋利吧！⚔️", "mood": AIMood.ENCOURAGING, "priority": 7},
                {"text": "好装备配好男人！👍", "mood": AIMood.IMPRESSED, "priority": 6},
                {"text": "这下稻草人要遭殃了...😈", "mood": AIMood.MOCKING, "priority": 6}
            ],
            'location_change': [
                {"text": "新环境！适应一下节奏吧！🌍", "mood": AIMood.NEUTRAL, "priority": 6},
                {"text": "换个地方练刀，感觉不一样吧？🤔", "mood": AIMood.NEUTRAL, "priority": 5},
                {"text": "新场地！展示你的适应能力！💪", "mood": AIMood.ENCOURAGING, "priority": 6}
            ],
            'general_encouragement': [
                {"text": "不错，再来一刀！💪", "mood": AIMood.ENCOURAGING, "priority": 5},
                {"text": "手起刀落，这才是男人！⚔️", "mood": AIMood.IMPRESSED, "priority": 6},
                {"text": "看那节奏，多美啊...✨", "mood": AIMood.IMPRESSED, "priority": 5},
                {"text": "保持这个节奏！🎵", "mood": AIMood.ENCOURAGING, "priority": 5},
                {"text": "有进步！继续加油！🔥", "mood": AIMood.EXCITED, "priority": 6},
                {"text": "稳！准！狠！👍", "mood": AIMood.IMPRESSED, "priority": 6}
            ]
        }

    def generate_response(self, context: AIContext) -> Optional[AIResponse]:
        """根据上下文生成AI回应"""
        if not self.can_comment(context):
            return None

        # 随机决定是否评论（基于评论频率）
        if random.random() > self.comment_frequency:
            return None

        # 根据上下文选择回应类型
        response = self._select_response_by_context(context)

        if response:
            # 根据性格调整回应
            adjusted_text = self.adjust_response_tone(response.text, response.mood)
            response.text = adjusted_text

            # 记录评论
            self.record_comment(response)

            # 更新学习状态
            if self.learning_enabled:
                self._update_learning_from_context(context)

            return response

        return None

    def can_comment(self, context: AIContext) -> bool:
        """
        检查是否可以评论

        Args:
            context: AI上下文

        Returns:
            是否可以评论
        """
        # 检查冷却时间
        if hasattr(self, 'last_comment_time'):
            time_since_last = time.time() - self.last_comment_time
            # 基于情绪的最小冷却时间
            min_cooldown = getattr(self, 'current_cooldown', 1.0)
            if time_since_last < min_cooldown:
                return False

        # 检查上下文有效性
        if context is None:
            return False

        # 检查玩家状态
        if context.player_level <= 0 or context.player_power <= 0:
            return False

        # 检查敌人状态
        if context.enemy_hp_percent < 0 or context.enemy_hp_percent > 1:
            return False

        return True

    def _select_response_by_context(self, context: AIContext) -> Optional[AIResponse]:
        """根据上下文选择回应"""

        # 高优先级情况检查
        if context.is_level_up:
            return self._create_response_from_template('level_up')

        if context.player_combo >= 10:
            return self._create_response_from_template('high_combo')

        if context.is_crit_hit:
            return self._create_response_from_template('crit_hit')

        if context.enemy_hp_percent < 0.3:
            return self._create_response_from_template('enemy_low_hp')

        if context.player_stamina < 30:
            return self._create_response_from_template('low_stamina')

        if context.recent_damage > 20:
            return self._create_response_from_template('high_damage')

        # 中等优先级情况
        if context.weapon_tier > 1 and random.random() < 0.3:
            return self._create_response_from_template('weapon_upgrade')

        if context.time_since_last_comment > 10:  # 长时间无评论
            return self._create_response_from_template('player_idle')

        # 默认鼓励评论
        if random.random() < 0.4:
            return self._create_response_from_template('general_encouragement')

        return None

    def _create_response_from_template(self, template_type: str) -> Optional[AIResponse]:
        """从模板创建回应"""
        if template_type not in self.comment_templates:
            return None

        templates = self.comment_templates[template_type]
        if not templates:
            return None

        # 根据优先级和随机性选择模板
        weighted_templates = []
        for template in templates:
            weight = template['priority']
            weighted_templates.extend([template] * weight)

        if not weighted_templates:
            return None

        selected_template = random.choice(weighted_templates)

        return AIResponse(
            text=selected_template['text'],
            mood=selected_template['mood'],
            priority=selected_template['priority'],
            cooldown_time=self._calculate_cooldown_time(selected_template['mood']),
            affinity_change=self._calculate_affinity_change(selected_template['mood'])
        )

    def _calculate_cooldown_time(self, mood: AIMood) -> float:
        """根据情绪计算冷却时间"""
        base_cooldown = 2.0

        cooldown_modifiers = {
            AIMood.EXCITED: 0.5,      # 兴奋时评论更频繁
            AIMood.ENCOURAGING: 1.0,  # 正常频率
            AIMood.IMPRESSED: 1.5,    # 印象深刻时稍微慢一点
            AIMood.MOCKING: 2.0,      # 嘲讽时冷却长一点
            AIMood.NEUTRAL: 1.5,      # 中性状态正常频率
            AIMood.SERIOUS: 2.0,      # 严肃时较少评论
            AIMood.TIRED: 3.0         # 疲倦时很少评论
        }

        modifier = cooldown_modifiers.get(mood, 1.0)
        return base_cooldown * modifier

    def _calculate_affinity_change(self, mood: AIMood) -> int:
        """根据情绪计算亲密度变化"""
        affinity_changes = {
            AIMood.EXCITED: 2,        # 兴奋增加亲密度
            AIMood.ENCOURAGING: 1,    # 鼓励增加亲密度
            AIMood.IMPRESSED: 2,      # 印象深刻增加亲密度
            AIMood.MOCKING: -1,       # 嘲讽减少亲密度
            AIMood.NEUTRAL: 0,        # 中性无变化
            AIMood.SERIOUS: 1,        # 严肃略微增加
            AIMood.TIRED: -1          # 疲倦减少亲密度
        }

        return affinity_changes.get(mood, 0)

    def update_learning_state(self, context: AIContext) -> None:
        """更新AI学习状态"""
        if not self.learning_enabled:
            return

        # 记录玩家攻击模式
        attack_key = f"{context.attack_frequency:.2f}_{context.combo_tendency:.2f}"
        if attack_key not in self.player_attack_patterns:
            self.player_attack_patterns[attack_key] = 0
        self.player_attack_patterns[attack_key] += 1

        # 记录成功率（基于敌人血量变化）
        success_key = f"damage_{context.recent_damage}"
        if success_key not in self.player_success_rates:
            self.player_success_rates[success_key] = {'attempts': 0, 'success': 0}

        self.player_success_rates[success_key]['attempts'] += 1
        if context.enemy_hp_percent < 0.5:  # 认为成功
            self.player_success_rates[success_key]['success'] += 1

    def _update_learning_from_context(self, context: AIContext) -> None:
        """从上下文更新学习数据"""
        # 更新连续相似动作计数
        current_action = (context.player_combo, context.is_crit_hit, context.recent_damage)

        if self.last_player_action == current_action:
            self.consecutive_similar_actions += 1
        else:
            self.consecutive_similar_actions = 0
            self.last_player_action = current_action

    def get_current_mood(self) -> AIMood:
        """获取当前情绪状态"""
        # 根据亲密度调整基础情绪
        if self.bond > 70:
            base_mood = AIMood.EXCITED
        elif self.bond > 50:
            base_mood = AIMood.ENCOURAGING
        elif self.bond > 30:
            base_mood = AIMood.NEUTRAL
        else:
            base_mood = AIMood.SERIOUS

        # 考虑最近的情绪历史
        if self.mood_history:
            recent_moods = self.mood_history[-5:]  # 最近5次情绪
            mood_counts: Dict[AIMood, int] = {}
            for mood in recent_moods:
                if mood in mood_counts:
                    mood_counts[mood] += 1
                else:
                    mood_counts[mood] = 1

            # 如果某种情绪占主导，则使用该情绪
            if mood_counts:
                # 找到出现次数最多的mood
                dominant_mood = None
                max_count = 0
                for mood, count in mood_counts.items():
                    if count > max_count:
                        max_count = count
                        dominant_mood = mood
                
                if dominant_mood is not None and max_count >= 3:
                    return dominant_mood

        return base_mood

    def get_personality_traits(self) -> Dict[str, float]:
        """获取性格特征"""
        # 根据亲密度调整性格特征
        traits = self.personality_traits.copy()

        if self.bond > 60:
            traits['enthusiasm'] = min(1.0, traits['enthusiasm'] + 0.2)
            traits['humor'] = min(1.0, traits['humor'] + 0.1)
        elif self.bond < 30:
            traits['patience'] = max(0.0, traits['patience'] - 0.2)
            traits['competitiveness'] = min(1.0, traits['competitiveness'] + 0.1)

        return traits

    def adjust_response_tone(self, base_response: str, mood: AIMood) -> str:
        """根据性格调整回应语气"""
        traits = self.get_personality_traits()
        adjusted_response = base_response

        # 根据性格特征添加语气词
        if traits['enthusiasm'] > 0.7:
            enthusiastic_words = ["太棒了！", "完美！", "厉害！"]
            if random.random() < 0.3:
                adjusted_response = random.choice(enthusiastic_words) + adjusted_response

        if traits['humor'] > 0.6:
            humorous_endings = ["哈哈！", "😄", "有意思"]
            if random.random() < 0.2:
                adjusted_response += random.choice(humorous_endings)

        if traits['wisdom'] > 0.7:
            wise_prefixes = ["记住，", "要记住，", " wisdom地说，"]
            if random.random() < 0.1:
                adjusted_response = random.choice(wise_prefixes) + adjusted_response

        return adjusted_response

    def should_make_special_comment(self, context: AIContext) -> bool:
        """判断是否应该发表特殊评论"""
        # 特殊情况：
        # 1. 达到新高连击
        if context.player_combo > context.max_combo_achieved:
            return True

        # 2. 连续多次相似动作
        if self.consecutive_similar_actions > 5:
            return True

        # 3. 亲密度达到重要阈值
        if self.bond in [25, 50, 75, 90]:
            return True

        # 4. 特殊组合条件
        if (context.player_combo >= 5 and
            context.is_crit_hit and
            context.player_stamina > 80):
            return True

        return False

    def analyze_player_pattern(self, context_history: List[AIContext]) -> Dict[str, Any]:
        """分析玩家行为模式"""
        if not context_history:
            return {}

        # 分析攻击频率变化
        attack_freqs = [ctx.attack_frequency for ctx in context_history[-10:]]
        avg_attack_freq = sum(attack_freqs) / len(attack_freqs) if attack_freqs else 0

        # 分析连击模式
        combos = [ctx.player_combo for ctx in context_history[-10:]]
        max_combo = max(combos) if combos else 0
        avg_combo = sum(combos) / len(combos) if combos else 0

        # 分析暴击模式
        crits = [ctx.is_crit_hit for ctx in context_history[-10:]]
        crit_rate = sum(crits) / len(crits) if crits else 0

        return {
            'avg_attack_frequency': avg_attack_freq,
            'max_combo': max_combo,
            'avg_combo': avg_combo,
            'crit_rate': crit_rate,
            'pattern_consistency': self._calculate_pattern_consistency(context_history)
        }

    def _calculate_pattern_consistency(self, context_history: List[AIContext]) -> float:
        """计算模式一致性"""
        if len(context_history) < 5:
            return 0.0

        # 计算攻击间隔的一致性
        intervals = []
        for i in range(1, len(context_history)):
            interval = context_history[i].time_since_last_comment
            if interval < 10:  # 只考虑合理的间隔
                intervals.append(interval)

        if not intervals:
            return 0.0

        avg_interval = sum(intervals) / len(intervals)
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)

        # 一致性评分：方差越小一致性越高
        consistency = max(0, 1.0 - (variance / (avg_interval ** 2))) if avg_interval > 0 else 0
        return consistency

    def adapt_behavior(self, pattern_analysis: Dict[str, Any]) -> None:
        """根据模式分析调整行为"""
        if not pattern_analysis:
            return

        consistency = pattern_analysis.get('pattern_consistency', 0)
        crit_rate = pattern_analysis.get('crit_rate', 0)
        avg_combo = pattern_analysis.get('avg_combo', 0)

        # 根据玩家表现调整评论频率
        if consistency > 0.8:  # 玩家很稳定
            self.comment_frequency = min(0.5, self.comment_frequency + 0.1)
        elif consistency < 0.3:  # 玩家不稳定
            self.comment_frequency = max(0.2, self.comment_frequency - 0.1)

        # 根据连击表现调整性格
        if avg_combo > 10:
            self.personality_traits['enthusiasm'] = min(1.0, self.personality_traits['enthusiasm'] + 0.1)

    def predict_player_action(self, context: AIContext) -> Optional[Dict[str, float]]:
        """预测玩家下一步行动"""
        # 基于历史模式进行简单预测
        predictions = {
            'will_attack': 0.7,
            'will_crit': context.crit_frequency,
            'will_combo': context.combo_tendency,
            'will_rest': 0.1 if context.player_stamina < 30 else 0.05
        }

        return predictions

    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        base_stats = super().get_learning_stats()

        # 添加规则AI特有的统计
        rule_stats = {
            'personality_type': self.personality_type,
            'personality_traits': self.personality_traits,
            'comment_frequency': self.comment_frequency,
            'player_attack_patterns': self.player_attack_patterns,
            'player_success_rates': self.player_success_rates,
            'consecutive_similar_actions': self.consecutive_similar_actions
        }

        base_stats.update(rule_stats)
        return base_stats

    def reset_learning_state(self) -> None:
        """重置学习状态"""
        self.player_attack_patterns.clear()
        self.player_success_rates.clear()
        self.last_player_action = None
        self.consecutive_similar_actions = 0
        super().reset_state()


# 注册AI类型
from .ai_factory import AIFactory
AIFactory.register_ai_type(
    name="rule_based",
    ai_class=RuleBasedAI,
    description="基于规则的AI，使用预定义规则生成回应",
    default_config={
        "personality_type": "encouraging",
        "comment_frequency": 0.3,
        "learning_enabled": True
    }
)