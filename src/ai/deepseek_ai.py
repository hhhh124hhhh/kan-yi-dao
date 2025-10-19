"""
DeepSeek AI实现模块
基于DeepSeek大语言模型的智能AI陪练系统
专为《是男人就砍一刀》游戏优化的中文AI助手
"""

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
import os
from dotenv import load_dotenv
from .rule_based_ai import RuleBasedAI

# 加载环境变量
load_dotenv()


class DeepSeekAI(AIBehaviorInterface, AILearningInterface, AIPersonalityInterface):
    """基于DeepSeek的AI实现 - 专为游戏优化的中文智能助手"""

    def __init__(self,
                 api_key: str = "",
                 model: str = "deepseek-chat",
                 base_url: str = "https://api.deepseek.com",
                 fallback_enabled: bool = True,
                 temperature: float = 0.7,
                 max_tokens: int = 150,
                 timeout: int = 10,
                 rate_limit: int = 60):
        super().__init__()

        # API配置
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY', '')
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.temperature = temperature
        self.max_tokens = max_tokens

        # 降级机制
        self.fallback_enabled = fallback_enabled
        self.fallback_ai = RuleBasedAI() if fallback_enabled else None

        # 请求控制
        self.request_times = []  # 记录请求时间，用于速率限制
        self.last_request_time = 0

        # DeepSeek特定配置
        self.system_prompt = self._build_game_optimized_prompt()
        self.conversation_history = []
        self.max_history_length = 8

        # 游戏专属角色设定
        self.game_personas = {
            'veteran_swordsman': {
                'name': '剑术导师',
                'description': '经验丰富的剑术大师，深谙各种刀法精髓',
                'speaking_style': '沉稳、专业，偶尔引用武学经典',
                'specialty': '技术指导、进阶建议'
            },
            'energetic_friend': {
                'name': '热血伙伴',
                'description': '充满激情的练刀伙伴，总是给玩家鼓励和支持',
                'speaking_style': '活泼、热情，使用现代网络用语',
                'specialty': '情绪激励、氛围营造'
            },
            'wacky_commentator': {
                'name': '搞笑解说员',
                'description': '幽默风趣的解说员，让练刀过程充满欢乐',
                'speaking_style': '诙谐、幽默，喜欢开玩笑和吐槽',
                'specialty': '娱乐效果、压力释放'
            },
            'strategic_analyst': {
                'name': '战术分析师',
                'description': '冷静理性的分析师，专注于数据统计和战术优化',
                'speaking_style': '理性、精确，使用数据和专业术语',
                'specialty': '数据分析、优化建议'
            }
        }
        self.current_persona = 'energetic_friend'

        # 学习和适应
        self.player_style_analysis = {
            'aggression_level': 0.5,      # 激进程度
            'consistency': 0.5,           # 稳定性
            'learning_speed': 0.5,        # 学习速度
            'preferred_timing': 1.0,      # 偏好的攻击间隔
            'reaction_pattern': 'neutral' # 反应模式
        }

        # 个性化回应模板
        self.response_templates = self._load_response_templates()

        self.logger = logging.getLogger(__name__)

    def _build_game_optimized_prompt(self) -> str:
        """构建游戏优化的系统提示词"""
        persona_info = self.game_personas[self.current_persona]

        return f"""你是《是男人就砍一刀》游戏的AI陪练助手，你的身份是{persona_info['name']}。

{persona_info['description']}

你的说话风格：{persona_info['speaking_style']}
你的专长：{persona_info['specialty']}

游戏背景：
- 这是一个解压向的砍击游戏，玩家通过反复砍击稻草人来获得爽感和成长
- 核心玩法循环：砍击 → 特效反馈 → 经验增长 → AI回应 → 升级变强
- 游戏目标是帮助玩家释放压力，获得成就感和爽快感

回应指导原则：
1. 语言简洁有力，1-2句话为佳，避免长篇大论
2. 语气要符合{persona_info['name']}的身份设定
3. 融入游戏元素，让回应更有代入感
4. 适当使用中文网络流行语和游戏梗（但要自然）
5. 根据玩家表现动态调整回应风格
6. 重点关注玩家的情绪体验和成长感受

特殊情境回应策略：
- 连击数高时：表达兴奋，可以用"起飞了！"、"这手感太爽了！"
- 暴击出现时：表达惊讶和赞美，"这刀太顶了！"、"伤害爆炸！"
- 敌人血量低时：催促终结，"收刀！"、"最后一击！"
- 升级时刻：热烈祝贺，"恭喜升级！"、"实力暴涨！"
- 体力不足时：调侃或关心，"没力了？"、"休息一下"
- 玩家失误时：鼓励为主，"没事，下一刀更狠！"

请用自然、生动的中文回应，让每一刀都充满仪式感！"""

    def _load_response_templates(self) -> Dict[str, List[str]]:
        """加载回应模板"""
        return {
            'high_combo': [
                "连击起飞了！这手感太顶了！🔥",
                "哇！这连击数有点离谱啊！",
                "停不下来了是吧！继续冲！",
                "这节奏感绝了！再来一波！"
            ],
            'crit_hit': [
                "暴击！这刀伤害直接拉满！⚡",
                "我的天！这一刀太顶了！",
                "暴击爽翻！伤害爆炸！💥",
                "这就是刀神的实力吗！"
            ],
            'level_up': [
                "升级成功！实力暴涨！🎉",
                "恭喜升级！又变强了！",
                "等级提升！离刀神更近一步！",
                "升级了！这波不亏！"
            ],
            'enemy_low_hp': [
                "稻草人快不行了！收刀！",
                "最后一击！给它个痛快！",
                "就差一点！加油啊兄弟！",
                "终结时刻！别手软！"
            ],
            'stamina_low': [
                "体力不太行了啊？休息一下？",
                "没蓝了？回回再来！",
                "体力告急！注意节奏！",
                "这体力用得太凶了点！"
            ],
            'high_damage': [
                "这伤害数值太夸张了！",
                "一刀破防！伤害超标！",
                "这就是满级的实力吗！",
                "伤害爆炸！太强了！"
            ],
            'encouragement': [
                "加油！坚持就是胜利！",
                "可以的！继续保持这状态！",
                "不错不错！有进步了！",
                "稳住！你能行的！"
            ]
        }

    def generate_response(self, context: AIContext) -> Optional[AIResponse]:
        """生成DeepSeek AI回应"""
        if not self.can_comment(context):
            return None

        # 检查速率限制
        if not self._check_rate_limit():
            self.logger.warning("DeepSeek API rate limit exceeded")
            if self.fallback_ai and self.fallback_enabled:
                return self.fallback_ai.generate_response(context)
            return None

        # 尝试使用DeepSeek生成回应
        try:
            response = self._generate_deepseek_response(context)
            if response:
                self.record_comment(response)
                self._update_learning_from_context(context)
                return response
        except Exception as e:
            self.logger.error(f"DeepSeek generation failed: {e}")

        # 降级到规则AI
        if self.fallback_ai and self.fallback_enabled:
            self.logger.info("Falling back to rule-based AI")
            fallback_response = self.fallback_ai.generate_response(context)
            if fallback_response:
                self._record_fallback_event(context)
                return fallback_response

        return None

    def _generate_deepseek_response(self, context: AIContext) -> Optional[AIResponse]:
        """调用DeepSeek API生成回应"""
        # 构建用户提示
        user_prompt = self._build_contextual_prompt(context)

        # 构建API请求
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 添加对话历史
        if self.conversation_history:
            messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history + [{"role": "user", "content": user_prompt}]

        # 调用DeepSeek API
        response_data = self._call_deepseek_api(messages)
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
            learning_data={
                'source': 'deepseek',
                'model': self.model,
                'persona': self.current_persona,
                'context': context.__dict__
            }
        )

    def _build_contextual_prompt(self, context: AIContext) -> str:
        """构建上下文感知的用户提示"""
        prompt_parts = []

        # 当前游戏状态
        prompt_parts.append("【当前游戏状态】")
        prompt_parts.append(f"玩家等级：Lv.{context.player_level}")
        prompt_parts.append(f"攻击力：{context.player_power}")
        prompt_parts.append(f"当前连击：{context.player_combo}连击")
        prompt_parts.append(f"稻草人血量：{int(context.enemy_hp_percent * 100)}%")
        prompt_parts.append(f"最近伤害：{context.recent_damage}")
        prompt_parts.append(f"玩家体力：{context.player_stamina}/100")
        prompt_parts.append(f"AI亲密度：{context.ai_affinity}/100")
        prompt_parts.append(f"当前位置：{context.location}")

        # 检测特殊情况
        special_situations = []
        if context.is_level_up:
            special_situations.append("🎉 玩家刚刚升级了！")
        if context.is_crit_hit:
            special_situations.append("⚡ 刚刚造成了暴击伤害！")
        if context.player_combo >= 15:
            special_situations.append(f"🔥 玩家打出了{context.player_combo}连击！")
        elif context.player_combo >= 8:
            special_situations.append(f"⚡ 玩家打出了{context.player_combo}连击！")
        if context.enemy_hp_percent < 0.2:
            special_situations.append("💀 稻草人濒临死亡！")
        if context.player_stamina < 20:
            special_situations.append("😮 玩家体力严重不足！")
        if context.recent_damage > 25:
            special_situations.append("💥 刚刚造成了超高伤害！")

        if special_situations:
            prompt_parts.append("\n【特殊事件】")
            prompt_parts.extend(special_situations)

        # 玩家行为分析
        prompt_parts.append("\n【玩家行为分析】")
        prompt_parts.append(f"攻击频率：{context.attack_frequency:.2f}刀/秒")
        prompt_parts.append(f"暴击频率：{context.crit_frequency:.1%}")
        prompt_parts.append(f"连击能力：{context.combo_tendency:.1%}")

        # 回应要求
        prompt_parts.append(f"\n请以{self.game_personas[self.current_persona]['name']}的身份，")
        prompt_parts.append("根据当前情况给出简短有力的回应（1-2句话）：")

        return "\n".join(prompt_parts)

    def _call_deepseek_api(self, messages: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        """调用DeepSeek API"""
        if not self.api_key:
            self.logger.warning("No DeepSeek API key provided")
            return None

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }

            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                self._record_request_time()
                return response.json()
            elif response.status_code == 429:
                self.logger.warning("DeepSeek API rate limit exceeded")
                return None
            else:
                self.logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None

        except requests.Timeout:
            self.logger.error("DeepSeek API request timeout")
            return None
        except requests.RequestException as e:
            self.logger.error(f"DeepSeek API network error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"DeepSeek API unexpected error: {e}")
            return None

    def _extract_ai_text(self, response_data: Dict[str, Any]) -> Optional[str]:
        """从DeepSeek API响应中提取AI文本"""
        try:
            if 'choices' in response_data:
                choices = response_data['choices']
                if choices and len(choices) > 0:
                    message = choices[0].get('message', {})
                    content = message.get('content', '')
                    if content:
                        # 清理可能的格式字符
                        return content.strip().strip('"\'')
            return None
        except Exception as e:
            self.logger.error(f"Error extracting DeepSeek text: {e}")
            return None

    def _check_rate_limit(self) -> bool:
        """检查API调用速率限制"""
        current_time = time.time()
        # 清理超过1分钟的请求记录
        self.request_times = [t for t in self.request_times if current_time - t < 60]

        # 检查是否超过速率限制
        if len(self.request_times) >= self.rate_limit:
            return False

        return True

    def _record_request_time(self) -> None:
        """记录API请求时间"""
        self.request_times.append(time.time())
        self.last_request_time = time.time()

    def _analyze_text_mood(self, text: str) -> AIMood:
        """分析文本情绪"""
        text_lower = text.lower()

        # DeepSeek特定的情绪关键词
        mood_keywords = {
            AIMood.EXCITED: ['兴奋', '激动', '太顶', '起飞', '爆炸', '爽', '牛', '强', '离谱', '夸张', '恐怖'],
            AIMood.ENCOURAGING: ['加油', '继续', '坚持', '努力', '可以', '相信', '一定能', '保持', '稳住'],
            AIMood.IMPRESSED: ['佩服', '厉害', '不错', '很好', '优秀', '惊人', '绝了', '太强了', '神了'],
            AIMood.MOCKING: ['哈哈', '呵呵', '搞笑', '笨', '不行', '差', '弱', '拉胯', '离谱（贬义）'],
            AIMood.NEUTRAL: ['好的', '嗯', '哦', '知道了', '明白', '收到'],
            AIMood.SERIOUS: ['记住', '注意', '重要', '关键', '必须', '应该', '需要'],
            AIMood.TIRED: ['累', '疲倦', '疲劳', '休息', '乏', '没力', '没蓝']
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

        return AIMood.NEUTRAL

    def _calculate_priority(self, context: AIContext, mood: AIMood) -> int:
        """计算回应优先级"""
        base_priority = 5

        # 游戏事件优先级调整
        if context.is_level_up:
            base_priority += 4
        if context.player_combo >= 15:
            base_priority += 3
        elif context.player_combo >= 8:
            base_priority += 2
        if context.is_crit_hit:
            base_priority += 2
        if context.enemy_hp_percent < 0.2:
            base_priority += 2
        if context.player_stamina < 20:
            base_priority += 1

        # 情绪优先级调整
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
            AIMood.EXCITED: 0.3,
            AIMood.ENCOURAGING: 0.8,
            AIMood.IMPRESSED: 1.2,
            AIMood.MOCKING: 1.8,
            AIMood.NEUTRAL: 1.5,
            AIMood.SERIOUS: 2.0,
            AIMood.TIRED: 2.5
        }

        modifier = cooldown_modifiers.get(mood, 1.0)
        return base_cooldown * modifier

    def _calculate_affinity_change(self, mood: AIMood) -> int:
        """根据情绪计算亲密度变化"""
        affinity_changes = {
            AIMood.EXCITED: 3,
            AIMood.ENCOURAGING: 2,
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
        if hasattr(self, 'current_response_text'):
            self.conversation_history.append({
                "role": "assistant",
                "content": self.current_response_text
            })

        # 限制历史长度
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history.pop(0)

        # 更新玩家风格分析
        self._update_player_style_analysis(context)

        # 动态调整人格
        self._adjust_persona_dynamically(context)

    def _update_player_style_analysis(self, context: AIContext) -> None:
        """更新玩家风格分析"""
        # 分析激进程度
        if context.attack_frequency > 2.0:
            self.player_style_analysis['aggression_level'] = min(1.0,
                self.player_style_analysis['aggression_level'] + 0.01)
        elif context.attack_frequency < 0.5:
            self.player_style_analysis['aggression_level'] = max(0.0,
                self.player_style_analysis['aggression_level'] - 0.01)

        # 分析连击能力
        if context.player_combo > 10:
            self.player_style_analysis['consistency'] = min(1.0,
                self.player_style_analysis['consistency'] + 0.02)

        # 分析暴击倾向
        if context.crit_frequency > 0.1:
            self.player_style_analysis['learning_speed'] = min(1.0,
                self.player_style_analysis['learning_speed'] + 0.01)

    def _adjust_persona_dynamically(self, context: AIContext) -> None:
        """根据玩家风格动态调整人格"""
        # 根据玩家表现选择合适的人格
        if self.player_style_analysis['aggression_level'] > 0.7:
            # 激进玩家 -> 热血伙伴
            self.current_persona = 'energetic_friend'
        elif self.player_style_analysis['consistency'] > 0.8:
            # 稳定玩家 -> 剑术导师
            self.current_persona = 'veteran_swordsman'
        elif context.ai_affinity > 70:
            # 高亲密度 -> 搞笑解说员
            self.current_persona = 'wacky_commentator'
        else:
            # 默认 -> 战术分析师
            self.current_persona = 'strategic_analyst'

        # 重新构建系统提示
        self.system_prompt = self._build_game_optimized_prompt()

    def _record_fallback_event(self, context: AIContext) -> None:
        """记录降级事件"""
        self.logger.info(f"DeepSeek AI fallback triggered for context: {context}")

    # 接口实现方法
    def update_learning_state(self, context: AIContext) -> None:
        """更新AI学习状态"""
        self._update_learning_from_context(context)

    def get_current_mood(self) -> AIMood:
        """获取当前情绪状态"""
        if self.bond > 80:
            return AIMood.EXCITED
        elif self.bond > 60:
            return AIMood.ENCOURAGING
        elif self.bond > 40:
            return AIMood.NEUTRAL
        elif self.bond > 20:
            return AIMood.SERIOUS
        else:
            return AIMood.TIRED

    def get_personality_traits(self) -> Dict[str, float]:
        """获取性格特征"""
        return {
            'enthusiasm': 0.9 if self.current_persona == 'energetic_friend' else 0.6,
            'patience': 0.8 if self.current_persona == 'veteran_swordsman' else 0.5,
            'humor': 0.9 if self.current_persona == 'wacky_commentator' else 0.4,
            'analytical': 0.9 if self.current_persona == 'strategic_analyst' else 0.5,
            'adaptability': 0.8
        }

    def adjust_response_tone(self, base_response: str, mood: AIMood) -> str:
        """根据性格调整回应语气"""
        # DeepSeek已经考虑了角色设定，这里可以不做额外调整
        return base_response

    def should_make_special_comment(self, context: AIContext) -> bool:
        """判断是否应该发表特殊评论"""
        # 在重要时刻总是发表评论
        return (context.is_level_up or
                context.player_combo >= 10 or
                context.is_crit_hit or
                context.enemy_hp_percent < 0.3)

    def analyze_player_pattern(self, context_history: List[AIContext]) -> Dict[str, Any]:
        """分析玩家行为模式"""
        if not context_history:
            return {}

        recent_contexts = context_history[-10:]  # 最近10个上下文

        # 计算平均攻击频率
        avg_frequency = sum(ctx.attack_frequency for ctx in recent_contexts) / len(recent_contexts)

        # 分析连击趋势
        max_combo = max(ctx.player_combo for ctx in recent_contexts)

        # 分析暴击倾向
        crit_rate = sum(1 for ctx in recent_contexts if ctx.is_crit_hit) / len(recent_contexts)

        return {
            'avg_attack_frequency': avg_frequency,
            'max_recent_combo': max_combo,
            'crit_tendency': crit_rate,
            'player_style': self.player_style_analysis,
            'recommended_persona': self.current_persona
        }

    def adapt_behavior(self, pattern_analysis: Dict[str, Any]) -> None:
        """根据模式分析调整行为"""
        if not pattern_analysis:
            return

        # 根据分析结果调整人格
        if pattern_analysis.get('avg_attack_frequency', 0) > 2.0:
            self.current_persona = 'energetic_friend'
        elif pattern_analysis.get('max_recent_combo', 0) > 20:
            self.current_persona = 'wacky_commentator'
        elif pattern_analysis.get('crit_tendency', 0) > 0.15:
            self.current_persona = 'veteran_swordsman'
        else:
            self.current_persona = 'strategic_analyst'

        # 重新构建提示
        self.system_prompt = self._build_game_optimized_prompt()

    def predict_player_action(self, context: AIContext) -> Optional[Dict[str, float]]:
        """预测玩家下一步行动"""
        return {
            'attack_probability': min(1.0, context.attack_frequency / 3.0),
            'crit_probability': context.crit_frequency,
            'combo_continuation_probability': min(1.0, context.player_combo / 20.0)
        }

    def set_persona(self, persona_name: str) -> bool:
        """设置AI角色"""
        if persona_name in self.game_personas:
            self.current_persona = persona_name
            self.system_prompt = self._build_game_optimized_prompt()
            self.logger.info(f"DeepSeek AI persona changed to: {persona_name}")
            return True
        return False

    def get_available_personas(self) -> List[str]:
        """获取可用的角色列表"""
        return list(self.game_personas.keys())

    def get_current_persona_info(self) -> Dict[str, str]:
        """获取当前角色信息"""
        return self.game_personas[self.current_persona].copy()

    def get_api_stats(self) -> Dict[str, Any]:
        """获取API使用统计"""
        return {
            'model': self.model,
            'total_requests': len(self.request_times),
            'recent_requests': len([t for t in self.request_times if time.time() - t < 300]),  # 5分钟内
            'rate_limit': self.rate_limit,
            'last_request_time': self.last_request_time,
            'api_key_configured': bool(self.api_key)
        }


# 注册DeepSeek AI类型
from .ai_factory import AIFactory
AIFactory.register_ai_type(
    name="deepseek_ai",
    ai_class=DeepSeekAI,
    description="基于DeepSeek大语言模型的智能AI，专为游戏优化的中文助手",
    default_config={
        "api_key": os.getenv('DEEPSEEK_API_KEY', ''),
        "model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "fallback_enabled": True,
        "temperature": 0.7,
        "max_tokens": 150,
        "timeout": 10,
        "rate_limit": 60
    }
)