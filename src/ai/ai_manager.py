from typing import Optional, Dict, Any, List
from .ai_interface import AIBehaviorInterface, AIContext, AIResponse, AIMood
from .ai_factory import AIFactory
from .context_engine import ContextEngine
import logging
import time


class AIManager:
    """统一AI管理器 - 负责管理AI实例和上下文处理"""

    def __init__(self,
                 ai_type: str = "rule_based",
                 ai_config: Optional[Dict[str, Any]] = None,
                 enable_learning: bool = True):
        """
        初始化AI管理器

        Args:
            ai_type: AI类型
            ai_config: AI配置
            enable_learning: 是否启用学习功能
        """
        self.enable_learning = enable_learning
        self.context_engine = ContextEngine()
        self.current_response: Optional[AIResponse] = None
        self.response_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
        
        # 初始化日志记录器
        self.logger = logging.getLogger(__name__)

        # 创建AI实例
        try:
            self.ai_engine = AIFactory.create_ai(ai_type, ai_config or {})
            self.current_ai_type = ai_type
            self.logger.info(f"AI Manager initialized with {ai_type} AI")
        except Exception as e:
            self.logger.error(f"Failed to create AI {ai_type}: {e}")
            # 尝试创建默认规则AI
            try:
                self.ai_engine = AIFactory.create_ai("rule_based")
                self.current_ai_type = "rule_based"
                self.logger.warning("Fell back to rule_based AI")
            except Exception as fallback_error:
                self.logger.error(f"Failed to create fallback AI: {fallback_error}")
                raise

        # 统计数据
        self.stats = {
            'total_responses': 0,
            'successful_responses': 0,
            'fallback_responses': 0,
            'avg_response_time': 0.0,
            'mood_distribution': {},
            'last_update_time': time.time()
        }

    def update_and_respond(self,
                          player,
                          enemy,
                          additional_context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        更新AI状态并生成回应

        Args:
            player: 玩家对象
            enemy: 敌人对象
            additional_context: 额外上下文信息

        Returns:
            AI回应文本，如果没有回应则返回None
        """
        start_time = time.time()

        try:
            # 构建上下文
            context = self.context_engine.build_context(player, enemy, self.ai_engine, additional_context)

            # 更新AI学习状态
            if self.enable_learning:
                self.ai_engine.update_learning_state(context)

            # 记录攻击事件
            if hasattr(enemy, 'last_damage') and enemy.last_damage > 0:
                is_crit = enemy.last_damage > player.attack_power * 1.5
                self.context_engine.record_attack_event(is_crit)

            # 记录连击事件
            if hasattr(player, 'combo') and player.combo > 0:
                self.context_engine.record_combo_event(player.combo)

            # 生成回应
            response = self.ai_engine.generate_response(context)

            if response:
                self._process_successful_response(response, context)
                return response.text
            else:
                self._process_no_response(context)

            # 更新统计
            self._update_stats(start_time, False)

            return None

        except Exception as e:
            self.logger.error(f"Error in AI update and respond: {e}")
            self._update_stats(start_time, False)
            return None

    def _process_successful_response(self, response: AIResponse, context: AIContext) -> None:
        """处理成功的AI回应"""
        self.current_response = response

        # 更新亲密度
        if hasattr(self.ai_engine, 'update_affinity'):
            self.ai_engine.update_affinity(response.affinity_change)

        # 记录回应历史
        self._record_response(response, context)

        # 更新情绪历史
        if hasattr(self.ai_engine, 'mood_history'):
            self.ai_engine.mood_history.append(response.mood)
            if len(self.ai_engine.mood_history) > 20:
                self.ai_engine.mood_history.pop(0)

        self.logger.debug(f"AI response: {response.text} (mood: {response.mood.value})")

    def _process_no_response(self, context: AIContext) -> None:
        """处理无回应的情况"""
        self.current_response = None
        self.logger.debug("AI chose not to respond")

    def _record_response(self, response: AIResponse, context: AIContext) -> None:
        """记录回应历史"""
        record = {
            'timestamp': time.time(),
            'response_text': response.text,
            'mood': response.mood.value,
            'priority': response.priority,
            'context': {
                'player_level': context.player_level,
                'player_combo': context.player_combo,
                'enemy_hp_percent': context.enemy_hp_percent,
                'location': context.location
            }
        }

        self.response_history.append(record)
        if len(self.response_history) > self.max_history_size:
            self.response_history.pop(0)

    def _update_stats(self, start_time: float, success: bool) -> None:
        """更新统计数据"""
        response_time = time.time() - start_time

        self.stats['total_responses'] += 1

        if success:
            self.stats['successful_responses'] += 1

        # 更新平均响应时间
        total = self.stats['total_responses']
        current_avg = self.stats['avg_response_time']
        self.stats['avg_response_time'] = (current_avg * (total - 1) + response_time) / total

        # 更新情绪分布
        if self.current_response:
            mood = self.current_response.mood.value
            if mood not in self.stats['mood_distribution']:
                self.stats['mood_distribution'][mood] = 0
            self.stats['mood_distribution'][mood] += 1

        self.stats['last_update_time'] = time.time()

    def get_current_mood(self) -> AIMood:
        """获取AI当前情绪"""
        return self.ai_engine.get_current_mood()

    def get_ai_bond(self) -> int:
        """获取AI与玩家的亲密度"""
        return getattr(self.ai_engine, 'bond', 10)

    def switch_ai_type(self, new_type: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        切换AI类型

        Args:
            new_type: 新的AI类型
            config: 新AI的配置

        Returns:
            是否切换成功
        """
        try:
            # 保存当前状态（如果可能）
            old_bond = self.get_ai_bond()
            old_stats = self.get_ai_stats()

            # 创建新的AI实例
            new_ai = AIFactory.create_ai(new_type, config)

            # 迁移状态
            if hasattr(new_ai, 'bond'):
                new_ai.bond = old_bond

            # 替换AI引擎
            self.ai_engine = new_ai
            self.current_ai_type = new_type

            self.logger.info(f"Switched AI type from {self.current_ai_type} to {new_type}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to switch AI type to {new_type}: {e}")
            return False

    def get_available_ai_types(self) -> List[str]:
        """获取可用的AI类型列表"""
        return AIFactory.get_available_types()

    def get_ai_info(self) -> Dict[str, Any]:
        """获取当前AI信息"""
        ai_info = AIFactory.get_ai_info(self.current_ai_type)
        ai_info['current_bond'] = self.get_ai_bond()
        ai_info['current_mood'] = self.get_current_mood().value
        ai_info['stats'] = self.stats.copy()
        return ai_info

    def get_ai_stats(self) -> Dict[str, Any]:
        """获取AI统计信息"""
        stats = self.stats.copy()

        # 添加AI特定的统计信息
        if hasattr(self.ai_engine, 'get_learning_stats'):
            ai_specific_stats = self.ai_engine.get_learning_stats()
            stats['ai_specific'] = ai_specific_stats

        # 添加上下文引擎统计
        context_insights = self.context_engine.get_player_insights()
        stats['player_insights'] = context_insights

        return stats

    def get_player_insights(self) -> Dict[str, Any]:
        """获取玩家洞察分析"""
        return self.context_engine.get_player_insights()

    def get_response_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取回应历史"""
        return self.response_history[-limit:] if limit > 0 else self.response_history.copy()

    def force_response(self,
                      player,
                      enemy,
                      context_override: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        强制生成回应（忽略冷却时间）

        Args:
            player: 玩家对象
            enemy: 敌人对象
            context_override: 上下文覆盖

        Returns:
            AI回应文本
        """
        try:
            # 构建基础上下文
            context = self.context_engine.build_context(player, enemy, self.ai_engine)

            # 应用上下文覆盖
            if context_override:
                for key, value in context_override.items():
                    if hasattr(context, key):
                        setattr(context, key, value)

            # 临时禁用冷却检查
            original_can_comment = self.ai_engine.can_comment
            self.ai_engine.can_comment = lambda context: True

            try:
                # 生成回应
                response = self.ai_engine.generate_response(context)
                if response:
                    self._process_successful_response(response, context)
                    return response.text
            finally:
                # 恢复原始方法
                self.ai_engine.can_comment = original_can_comment

            return None

        except Exception as e:
            self.logger.error(f"Error in force_response: {e}")
            return None

    def reset_ai_state(self) -> None:
        """重置AI状态"""
        # 使用hasattr检查方法是否存在，然后调用
        if hasattr(self.ai_engine, 'reset_state') and callable(getattr(self.ai_engine, 'reset_state', None)):
            self.ai_engine.reset_state()
        elif hasattr(self.ai_engine, 'reset_learning_state') and callable(getattr(self.ai_engine, 'reset_learning_state', None)):
            self.ai_engine.reset_learning_state()

        self.context_engine.reset_engine()
        self.current_response = None
        self.response_history.clear()
        self.stats = {
            'total_responses': 0,
            'successful_responses': 0,
            'fallback_responses': 0,
            'avg_response_time': 0.0,
            'mood_distribution': {},
            'last_update_time': time.time()
        }

        self.logger.info("AI Manager state reset")

    def export_ai_data(self) -> Dict[str, Any]:
        """导出AI相关数据"""
        return {
            'ai_type': self.current_ai_type,
            'ai_info': self.get_ai_info(),
            'ai_stats': self.get_ai_stats(),
            'player_insights': self.get_player_insights(),
            'response_history': self.get_response_history(),
            'context_engine_data': self.context_engine.export_analysis_data()
        }

    def import_ai_data(self, data: Dict[str, Any]) -> bool:
        """导入AI相关数据"""
        try:
            # 恢复AI类型
            if 'ai_type' in data and data['ai_type'] != self.current_ai_type:
                self.switch_ai_type(data['ai_type'])

            # 恢复AI状态
            if 'ai_info' in data and 'current_bond' in data['ai_info']:
                if hasattr(self.ai_engine, 'bond'):
                    self.ai_engine.bond = data['ai_info']['current_bond']

            # 恢复统计数据
            if 'ai_stats' in data:
                self.stats.update(data['ai_stats'].get('stats', {}))

            self.logger.info("AI data imported successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error importing AI data: {e}")
            return False

    def set_ai_personality(self, personality_config: Dict[str, Any]) -> bool:
        """设置AI性格配置"""
        try:
            if hasattr(self.ai_engine, 'set_persona') and callable(getattr(self.ai_engine, 'set_persona', None)):
                persona_name = personality_config.get('persona_name')
                if persona_name:
                    return self.ai_engine.set_persona(persona_name)
            elif hasattr(self.ai_engine, 'personality_traits') and hasattr(self.ai_engine, 'personality_traits'):
                self.ai_engine.personality_traits.update(personality_config)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error setting AI personality: {e}")
            return False

    def get_ai_capabilities(self) -> Dict[str, bool]:
        """获取AI能力信息"""
        capabilities = {
            'supports_learning': hasattr(self.ai_engine, 'update_learning_state'),
            'supports_personality': hasattr(self.ai_engine, 'personality_traits'),
            'supports_pattern_analysis': hasattr(self.ai_engine, 'analyze_player_pattern'),
            'supports_prediction': hasattr(self.ai_engine, 'predict_player_action'),
            'supports_adaptation': hasattr(self.ai_engine, 'adapt_behavior'),
            'supports_mood_tracking': hasattr(self.ai_engine, 'mood_history'),
            'is_llm_based': self.current_ai_type == 'llm_ai'
        }

        return capabilities

    def health_check(self) -> Dict[str, Any]:
        """AI系统健康检查"""
        health_status = {
            'overall_status': 'healthy',
            'issues': [],
            'warnings': [],
            'info': {}
        }

        # 检查AI引擎状态
        try:
            mood = self.get_current_mood()
            health_status['info']['current_mood'] = mood.value
        except Exception as e:
            health_status['issues'].append(f"AI engine error: {e}")
            health_status['overall_status'] = 'unhealthy'

        # 检查上下文引擎状态
        try:
            insights = self.context_engine.get_player_insights()
            health_status['info']['context_engine_status'] = 'operational'
        except Exception as e:
            health_status['issues'].append(f"Context engine error: {e}")
            health_status['overall_status'] = 'degraded'

        # 检查统计信息
        if self.stats['total_responses'] > 0:
            success_rate = self.stats['successful_responses'] / self.stats['total_responses']
            health_status['info']['success_rate'] = f"{success_rate:.2%}"

            if success_rate < 0.5:
                health_status['warnings'].append("Low AI response success rate")

        # 检查响应时间
        if self.stats['avg_response_time'] > 1.0:
            health_status['warnings'].append("High average response time")

        health_status['info']['ai_type'] = self.current_ai_type
        health_status['info']['total_responses'] = self.stats['total_responses']

        return health_status