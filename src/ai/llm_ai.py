from typing import Optional, List, Dict, Any
from .ai_interface import (
    AIBehaviorInterface, AILearningInterface, AIPersonalityInterface,
    AIContext, AIResponse, AIMood
)
import random
import time
import json
import logging
import requests
from .rule_based_ai import RuleBasedAI


class LLMAI(AIBehaviorInterface, AILearningInterface, AIPersonalityInterface):
    """基于LLM的AI实现 - 使用大语言模型生成智能回应"""

    def __init__(self,
                 api_key: str = "",
                 model: str = "claude-3-haiku-20240307",
                 base_url: str = "https://open.bigmodel.cn/api/anthropic",
                 fallback_enabled: bool = True,
                 temperature: float = 0.8,
                 max_tokens: int = 150):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.fallback_enabled = fallback_enabled
        self.temperature = temperature
        self.max_tokens = max_tokens

        # 降级到规则AI
        self.fallback_ai = RuleBasedAI() if fallback_enabled else None

        # LLM配置
        self.system_prompt = self._build_system_prompt()
        self.conversation_history = []
        self.max_history_length = 10

        # 性格特征
        self.personality_traits = {
            'enthusiasm': 0.8,      # 热情程度
            'patience': 0.7,        # 耐心程度
            'competitiveness': 0.6, # 竞争性
            'humor': 0.5,           # 幽默感
            'wisdom': 0.8           # 智慧感
        }

        # AI角色设定
        self.ai_personas = {
            'enthusiastic_coach': {
                'name': '热血教练',
                'description': '一个充满激情的格斗教练，总是鼓励玩家追求更强的力量',
                'speaking_style': '充满激情，使用感叹号和鼓励性语言'
            },
            'wise_mentor': {
                'name': '智慧导师',
                'description': '一位经验丰富的导师，用智慧指导玩家的成长',
                'speaking_style': '沉稳、有哲理，偶尔说些人生感悟'
            },
            'competitive_rival': {
                'name': '竞争对手',
                'description': '一个友好的竞争对手，既想击败玩家又希望看到玩家变强',
                'speaking_style': '略带挑衅但友善，喜欢挑战和切磋'
            },
            'cheerful_friend': {
                'name': '开朗朋友',
                'description': '玩家的好朋友，总是轻松愉快地陪伴玩家',
                'speaking_style': '轻松幽默，喜欢开玩笑和调侃'
            }
        }
        self.current_persona = 'enthusiastic_coach'

        self.logger = logging.getLogger(__name__)

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        persona_info = self.ai_personas[self.current_persona]

        return f"""你是《是男人就砍一刀》游戏中的AI陪练，你的身份是{persona_info['name']}。

{persona_info['description']}

你的说话风格：{persona_info['speaking_style']}

背景设定：
- 这是一个解压向的动作游戏，玩家通过"砍击-反馈-升级-AI反应"的循环获得爽感
- 玩家正在砍稻草人练刀，从新手村开始成长
- 你既是陪练也是解说员，需要根据玩家情况给出合适的反馈
- 你的目标：让每一刀都成为释放压力的瞬间，给玩家持续的爽感和成长感

回应要求：
1. 保持简洁有力，1-2句话即可
2. 根据玩家表现调整语气和情绪
3. 偶尔加入一些游戏相关的术语或梗
4. 避免重复，保持新鲜感
5. 可以有一些幽默感，但不要过度
6. 关注玩家的成长和进步

根据不同的游戏情况给出相应的回应：
- 高连击时：表达兴奋和鼓励
- 暴击时：表示惊叹和赞美
- 敌人血量低时：催促玩家完成最后一击
- 升级时：祝贺并鼓励继续
- 体力不足时：提醒或调侃
- 长时间无动作时：鼓励或调侃
- 高伤害时：表达兴奋

请用中文回应，语气要符合你的角色设定。"""

    def generate_response(self, context: AIContext) -> Optional[AIResponse]:
        """使用LLM生成回应"""
        if not self.can_comment(context):
            return None

        # 尝试使用LLM生成回应
        try:
            response = self._generate_llm_response(context)
            if response:
                self.record_comment(response)
                self._update_learning_from_context(context)
                return response
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")

            # 降级到规则AI
            if self.fallback_ai and self.fallback_enabled:
                self.logger.info("Falling back to rule-based AI")
                fallback_response = self.fallback_ai.generate_response(context)
                if fallback_response:
                    # 记录降级事件
                    self._record_fallback_event(context)
                    return fallback_response

        return None

    def _generate_llm_response(self, context: AIContext) -> Optional[AIResponse]:
        """调用LLM API生成回应"""
        # 构建用户提示
        user_prompt = self._build_user_prompt(context)

        # 构建API请求
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 添加对话历史
        if self.conversation_history:
            messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history + [{"role": "user", "content": user_prompt}]

        # 调用API
        response_data = self._call_llm_api(messages)
        if not response_data:
            return None

        # 解析响应
        ai_text = self._extract_ai_text(response_data)
        if not ai_text:
            return None

        # 分析情绪
        mood = self._analyze_text_mood(ai_text)

        # 创建AI回应对象
        return AIResponse(
            text=ai_text,
            mood=mood,
            priority=self._calculate_priority(context, mood),
            cooldown_time=self._calculate_cooldown_time(mood),
            affinity_change=self._calculate_affinity_change(mood),
            learning_data={'source': 'llm', 'model': self.model}
        )

    def _build_user_prompt(self, context: AIContext) -> str:
        """构建用户提示"""
        prompt_parts = []

        # 当前游戏状态
        prompt_parts.append("当前游戏状态：")
        prompt_parts.append(f"- 玩家等级：{context.player_level}")
        prompt_parts.append(f"- 当前连击：{context.player_combo}")
        prompt_parts.append(f"- 攻击力：{context.player_power}")
        prompt_parts.append(f"- 稻草人血量：{int(context.enemy_hp_percent * 100)}%")
        prompt_parts.append(f"- 最近伤害：{context.recent_damage}")
        prompt_parts.append(f"- 玩家体力：{context.player_stamina}/100")
        prompt_parts.append(f"- 武器等级：{context.weapon_tier}")
        prompt_parts.append(f"- 总金币：{context.total_coins}")
        prompt_parts.append(f"- 当前位置：{context.location}")

        # 特殊情况
        special_situations = []
        if context.is_level_up:
            special_situations.append("玩家刚刚升级！")
        if context.is_crit_hit:
            special_situations.append("刚刚造成了暴击！")
        if context.player_combo >= 10:
            special_situations.append(f"玩家打出了{context.player_combo}连击！")
        if context.enemy_hp_percent < 0.3:
            special_situations.append("稻草人血量很低了！")
        if context.player_stamina < 30:
            special_situations.append("玩家体力不足！")
        if context.recent_damage > 20:
            special_situations.append("刚刚造成了高额伤害！")

        if special_situations:
            prompt_parts.append("\n特殊情况：")
            prompt_parts.extend(special_situations)

        # 玩家行为模式
        prompt_parts.append(f"\n玩家行为分析：")
        prompt_parts.append(f"- 攻击频率：{context.attack_frequency:.2f}次/秒")
        prompt_parts.append(f"- 暴击频率：{context.crit_frequency:.2%}")
        prompt_parts.append(f"- 连击倾向：{context.combo_tendency:.2%}")

        # AI与玩家关系
        prompt_parts.append(f"\nAI与玩家关系：")
        prompt_parts.append(f"- 亲密度：{context.ai_affinity}/100")

        # 指导要求
        prompt_parts.append("\n请根据以上情况，给出合适的回应（1-2句话）：")

        return "\n".join(prompt_parts)

    def _call_llm_api(self, messages: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """调用LLM API"""
        if not self.api_key:
            self.logger.warning("No API key provided for LLM AI")
            return None

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            data = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": messages
            }

            response = requests.post(
                f"{self.base_url}/v1/messages",
                headers=headers,
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None

        except requests.RequestException as e:
            self.logger.error(f"Network error calling LLM API: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error calling LLM API: {e}")
            return None

    def _extract_ai_text(self, response_data: Dict[str, Any]) -> Optional[str]:
        """从API响应中提取AI文本"""
        try:
            # 根据API格式提取文本
            if 'content' in response_data:
                content = response_data['content']
                if isinstance(content, list) and len(content) > 0:
                    return content[0].get('text', '')
                elif isinstance(content, str):
                    return content
            elif 'choices' in response_data:
                choices = response_data['choices']
                if choices and len(choices) > 0:
                    return choices[0].get('message', {}).get('content', '')

            return None
        except Exception as e:
            self.logger.error(f"Error extracting AI text: {e}")
            return None

    def _analyze_text_mood(self, text: str) -> AIMood:
        """分析文本情绪"""
        text_lower = text.lower()

        # 关键词映射到情绪
        mood_keywords = {
            AIMood.EXCITED: ['兴奋', '激动', '太棒', '完美', '厉害', '爽', '牛', '强'],
            AIMood.ENCOURAGING: ['加油', '继续', '坚持', '努力', '可以', '相信', '一定能'],
            AIMood.IMPRESSED: ['佩服', '厉害', '不错', '很好', '优秀', '惊人', '佩服'],
            AIMood.MOCKING: ['哈哈', '呵呵', '搞笑', '笨', '不行', '差', '弱'],
            AIMood.NEUTRAL: ['好的', '嗯', '哦', '知道了', '明白'],
            AIMood.SERIOUS: ['记住', '注意', '重要', '关键', '必须', '应该'],
            AIMood.TIRED: ['累', '疲倦', '疲劳', '休息', '乏']
        }

        # 计算每种情绪的得分
        mood_scores = {}
        for mood, keywords in mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                mood_scores[mood] = score

        # 返回得分最高的情绪
        if mood_scores:
            return max(mood_scores, key=mood_scores.get)

        # 默认情绪
        return AIMood.NEUTRAL

    def _calculate_priority(self, context: AIContext, mood: AIMood) -> int:
        """计算回应优先级"""
        base_priority = 5

        # 根据游戏情况调整优先级
        if context.is_level_up:
            base_priority += 4
        if context.player_combo >= 10:
            base_priority += 3
        if context.is_crit_hit:
            base_priority += 2
        if context.enemy_hp_percent < 0.3:
            base_priority += 2

        # 根据情绪调整优先级
        mood_modifiers = {
            AIMood.EXCITED: 2,
            AIMood.IMPRESSED: 1,
            AIMood.ENCOURAGING: 1,
            AIMood.MOCKING: 0,
            AIMood.NEUTRAL: 0,
            AIMood.SERIOUS: -1,
            AIMood.TIRED: -1
        }

        base_priority += mood_modifiers.get(mood, 0)

        return max(1, min(10, base_priority))

    def _calculate_cooldown_time(self, mood: AIMood) -> float:
        """根据情绪计算冷却时间"""
        base_cooldown = 2.0

        cooldown_modifiers = {
            AIMood.EXCITED: 0.5,
            AIMood.ENCOURAGING: 1.0,
            AIMood.IMPRESSED: 1.5,
            AIMood.MOCKING: 2.0,
            AIMood.NEUTRAL: 1.5,
            AIMood.SERIOUS: 2.0,
            AIMood.TIRED: 3.0
        }

        modifier = cooldown_modifiers.get(mood, 1.0)
        return base_cooldown * modifier

    def _calculate_affinity_change(self, mood: AIMood) -> int:
        """根据情绪计算亲密度变化"""
        affinity_changes = {
            AIMood.EXCITED: 2,
            AIMood.ENCOURAGING: 1,
            AIMood.IMPRESSED: 2,
            AIMood.MOCKING: -1,
            AIMood.NEUTRAL: 0,
            AIMood.SERIOUS: 1,
            AIMood.TIRED: -1
        }

        return affinity_changes.get(mood, 0)

    def _update_learning_from_context(self, context: AIContext) -> None:
        """从上下文更新学习数据"""
        # 更新对话历史
        self.conversation_history.append({
            "role": "assistant",
            "content": self.current_response_text if hasattr(self, 'current_response_text') else ""
        })

        # 限制历史长度
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history.pop(0)

    def _record_fallback_event(self, context: AIContext) -> None:
        """记录降级事件"""
        self.logger.info(f"LLM AI fallback triggered for context: {context}")

    def update_learning_state(self, context: AIContext) -> None:
        """更新AI学习状态"""
        # LLM AI的学习主要体现在对话历史的积累和个性化适应
        pass

    def get_current_mood(self) -> AIMood:
        """获取当前情绪状态"""
        # 基于亲密度和最近的表现
        if self.bond > 70:
            return AIMood.EXCITED
        elif self.bond > 50:
            return AIMood.ENCOURAGING
        elif self.bond > 30:
            return AIMood.NEUTRAL
        else:
            return AIMood.SERIOUS

    def get_personality_traits(self) -> Dict[str, float]:
        """获取性格特征"""
        return self.personality_traits.copy()

    def adjust_response_tone(self, base_response: str, mood: AIMood) -> str:
        """根据性格调整回应语气"""
        # LLM已经考虑了角色设定，这里可以不做调整或做微调
        return base_response

    def should_make_special_comment(self, context: AIContext) -> bool:
        """判断是否应该发表特殊评论"""
        # LLM会根据上下文自动判断是否需要特殊评论
        return True

    def analyze_player_pattern(self, context_history: List[AIContext]) -> Dict[str, Any]:
        """分析玩家行为模式"""
        # 这里可以添加更复杂的模式分析逻辑
        return {}

    def adapt_behavior(self, pattern_analysis: Dict[str, Any]) -> None:
        """根据模式分析调整行为"""
        # 可以根据分析结果调整系统提示词或角色设定
        if pattern_analysis.get('skill_level') == 'expert':
            self.current_persona = 'competitive_rival'
        elif pattern_analysis.get('skill_level') == 'beginner':
            self.current_persona = 'enthusiastic_coach'
        else:
            self.current_persona = 'wise_mentor'

        # 重新构建系统提示
        self.system_prompt = self._build_system_prompt()

    def predict_player_action(self, context: AIContext) -> Optional[Dict[str, float]]:
        """预测玩家下一步行动"""
        return {}

    def set_persona(self, persona_name: str) -> bool:
        """设置AI角色"""
        if persona_name in self.ai_personas:
            self.current_persona = persona_name
            self.system_prompt = self._build_system_prompt()
            self.logger.info(f"AI persona changed to: {persona_name}")
            return True
        return False

    def get_available_personas(self) -> List[str]:
        """获取可用的角色列表"""
        return list(self.ai_personas.keys())

    def get_current_persona_info(self) -> Dict[str, str]:
        """获取当前角色信息"""
        return self.ai_personas[self.current_persona].copy()


# 注册AI类型
from .ai_factory import AIFactory
AIFactory.register_ai_type(
    name="llm_ai",
    ai_class=LLMAI,
    description="基于LLM的智能AI，使用大语言模型生成个性化回应",
    default_config={
        "api_key": "",
        "model": "claude-3-haiku-20240307",
        "base_url": "https://open.bigmodel.cn/api/anthropic",
        "fallback_enabled": True,
        "temperature": 0.8,
        "max_tokens": 150
    }
)