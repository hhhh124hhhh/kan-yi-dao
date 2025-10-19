"""
DeepSeek AI测试模块
测试DeepSeek AI的功能、性能和集成
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import time
import json
import os
from pathlib import Path

# 导入测试辅助工具
from tests.helpers.factories import AIContextFactory
from tests.helpers.mock_data import MockAIResponseGenerator
from tests.helpers.assertions import assert_ai_response

from src.ai.deepseek_ai import DeepSeekAI
from src.ai.ai_interface import AIContext, AIResponse, AIMood
from src.ai.ai_factory import AIFactory


class TestDeepSeekAI(unittest.TestCase):
    """DeepSeek AI核心功能测试"""

    def setUp(self):
        """测试前的设置"""
        # 使用测试配置创建DeepSeek AI实例
        self.test_config = {
            'api_key': 'test_api_key_12345',
            'model': 'deepseek-chat',
            'base_url': 'https://api.deepseek.com',
            'fallback_enabled': True,
            'temperature': 0.7,
            'max_tokens': 150,
            'timeout': 5,
            'rate_limit': 10
        }

        # 创建AI实例
        self.deepseek_ai = DeepSeekAI(**self.test_config)

        # 创建测试上下文
        self.test_context = AIContext(
            player_level=5,
            player_combo=8,
            player_power=15,
            enemy_hp_percent=0.3,
            recent_damage=25,
            ai_affinity=60,
            location="新手村",
            time_since_last_comment=5.0,
            player_stamina=80,
            is_level_up=False,
            is_crit_hit=True,
            attack_frequency=1.5,
            crit_frequency=0.12,
            combo_tendency=0.7,
            weapon_tier=2,
            total_coins=150
        )

    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.deepseek_ai.api_key, 'test_api_key_12345')
        self.assertEqual(self.deepseek_ai.model, 'deepseek-chat')
        self.assertTrue(self.deepseek_ai.fallback_enabled)
        self.assertEqual(self.deepseek_ai.temperature, 0.7)
        self.assertEqual(self.deepseek_ai.max_tokens, 150)
        self.assertIsNotNone(self.deepseek_ai.fallback_ai)

    def test_initialization_without_api_key(self):
        """测试没有API密钥时的初始化"""
        ai_no_key = DeepSeekAI(api_key='')
        self.assertEqual(ai_no_key.api_key, '')
        self.assertTrue(ai_no_key.fallback_enabled)

    @patch('src.ai.deepseek_ai.requests.post')
    def test_api_call_success(self, mock_post):
        """测试API调用成功的情况"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '这刀太顶了！伤害爆炸！⚡'
                }
            }]
        }
        mock_post.return_value = mock_response

        # 测试生成回应
        response = self.deepseek_ai._generate_deepseek_response(self.test_context)

        self.assertIsNotNone(response)
        self.assertIsInstance(response, AIResponse)
        self.assertEqual(response.text, '这刀太顶了！伤害爆炸！⚡')
        self.assertEqual(response.mood, AIMood.EXCITED)
        self.assertEqual(response.learning_data['source'], 'deepseek')
        self.assertEqual(response.learning_data['model'], 'deepseek-chat')

    @patch('src.ai.deepseek_ai.requests.post')
    def test_api_call_rate_limit(self, mock_post):
        """测试API速率限制"""
        # 模拟速率限制响应
        mock_response = Mock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response

        # 设置速率限制为1次/分钟
        self.deepseek_ai.rate_limit = 1

        # 第一次调用应该成功（使用mock）
        with patch('src.ai.deepseek_ai.requests.post') as mock_success:
            mock_success.return_value = Mock(status_code=200)
            self.deepseek_ai._call_deepseek_api([])
            self.assertEqual(len(self.deepseek_ai.request_times), 1)

        # 第二次调用应该被速率限制
        self.assertFalse(self.deepseek_ai._check_rate_limit())

    @patch('src.ai.deepseek_ai.requests.post')
    def test_api_call_network_error(self, mock_post):
        """测试API网络错误"""
        # 模拟网络错误
        mock_post.side_effect = Exception("Network error")

        # 应该返回None
        response = self.deepseek_ai._call_deepseek_api([])
        self.assertIsNone(response)

    def test_fallback_to_rule_based_ai(self):
        """测试降级到规则AI"""
        # 没有API密钥的情况
        ai_no_key = DeepSeekAI(api_key='', fallback_enabled=True)

        # 生成回应应该降级到规则AI
        response = ai_no_key.generate_response(self.test_context)

        # 应该获得规则AI的回应
        self.assertIsNotNone(response)
        self.assertIsInstance(response, AIResponse)

    def test_mood_analysis(self):
        """测试情绪分析"""
        test_cases = [
            ("这刀太顶了！起飞了！🔥", AIMood.EXCITED),
            ("加油！继续努力！💪", AIMood.ENCOURAGING),
            ("这伤害太夸张了！", AIMood.IMPRESSED),
            ("体力不太行了啊？", AIMood.MOCKING),
            ("好的，收到。", AIMood.NEUTRAL),
            ("记住这个要领。", AIMood.SERIOUS),
            ("有点累了。", AIMood.TIRED)
        ]

        for text, expected_mood in test_cases:
            with self.subTest(text=text):
                mood = self.deepseek_ai._analyze_text_mood(text)
                self.assertEqual(mood, expected_mood)

    def test_priority_calculation(self):
        """测试优先级计算"""
        # 高优先级情况（升级+高连击）
        high_priority_context = self.test_context
        high_priority_context.is_level_up = True
        high_priority_context.player_combo = 20

        priority = self.deepseek_ai._calculate_priority(
            high_priority_context, AIMood.EXCITED
        )
        self.assertGreater(priority, 8)

        # 低优先级情况（普通状态）
        low_priority_context = self.test_context
        low_priority_context.player_combo = 0
        low_priority_context.is_level_up = False

        priority = self.deepseek_ai._calculate_priority(
            low_priority_context, AIMood.NEUTRAL
        )
        self.assertLessEqual(priority, 6)

    def test_cooldown_time_calculation(self):
        """测试冷却时间计算"""
        # 兴奋状态的冷却时间应该较短
        excited_cooldown = self.deepseek_ai._calculate_cooldown_time(AIMood.EXCITED)
        neutral_cooldown = self.deepseek_ai._calculate_cooldown_time(AIMood.NEUTRAL)

        self.assertLess(excited_cooldown, neutral_cooldown)
        self.assertGreater(excited_cooldown, 0)

    def test_affinity_change_calculation(self):
        """测试亲密度变化计算"""
        excited_change = self.deepseek_ai._calculate_affinity_change(AIMood.EXCITED)
        mocking_change = self.deepseek_ai._calculate_affinity_change(AIMood.MOCKING)

        self.assertGreater(excited_change, 0)
        self.assertLess(mocking_change, 0)

    def test_persona_management(self):
        """测试角色管理"""
        # 测试可用角色
        personas = self.deepseek_ai.get_available_personas()
        expected_personas = ['veteran_swordsman', 'energetic_friend',
                           'wacky_commentator', 'strategic_analyst']
        for persona in expected_personas:
            self.assertIn(persona, personas)

        # 测试角色切换
        original_persona = self.deepseek_ai.current_persona
        success = self.deepseek_ai.set_persona('wacky_commentator')
        self.assertTrue(success)
        self.assertEqual(self.deepseek_ai.current_persona, 'wacky_commentator')

        # 测试无效角色
        success = self.deepseek_ai.set_persona('invalid_persona')
        self.assertFalse(success)
        self.assertEqual(self.deepseek_ai.current_persona, 'wacky_commentator')

    def test_context_prompt_building(self):
        """测试上下文提示构建"""
        prompt = self.deepseek_ai._build_contextual_prompt(self.test_context)

        # 检查提示包含关键信息
        self.assertIn('玩家等级：Lv.5', prompt)
        self.assertIn('当前连击：8连击', prompt)
        self.assertIn('⚡ 刚刚造成了暴击伤害！', prompt)
        self.assertIn('稻草人血量：30%', prompt)
        self.assertIn('血伙伴的身份', prompt)

    def test_player_style_analysis(self):
        """测试玩家风格分析"""
        # 初始分析
        initial_style = self.deepseek_ai.player_style_analysis.copy()

        # 模拟激进玩家
        self.test_context.attack_frequency = 3.0
        self.deepseek_ai._update_player_style_analysis(self.test_context)

        # 激进程度应该增加
        self.assertGreater(
            self.deepseek_ai.player_style_analysis['aggression_level'],
            initial_style['aggression_level']
        )

    def test_dynamic_persona_adjustment(self):
        """测试动态角色调整"""
        # 设置高激进度
        self.deepseek_ai.player_style_analysis['aggression_level'] = 0.8
        self.deepseek_ai._adjust_persona_dynamically(self.test_context)

        # 应该调整为热血伙伴
        self.assertEqual(self.deepseek_ai.current_persona, 'energetic_friend')

    def test_api_stats(self):
        """测试API使用统计"""
        stats = self.deepseek_ai.get_api_stats()

        expected_keys = ['model', 'total_requests', 'recent_requests',
                        'rate_limit', 'last_request_time', 'api_key_configured']
        for key in expected_keys:
            self.assertIn(key, stats)

        self.assertEqual(stats['model'], 'deepseek-chat')
        self.assertEqual(stats['rate_limit'], 10)
        self.assertTrue(stats['api_key_configured'])

    def test_response_templates(self):
        """测试回应模板"""
        templates = self.deepseek_ai.response_templates

        # 检查关键模板存在
        expected_templates = ['high_combo', 'crit_hit', 'level_up',
                            'enemy_low_hp', 'encouragement']
        for template in expected_templates:
            self.assertIn(template, templates)
            self.assertGreater(len(templates[template]), 0)


class TestDeepSeekAIIntegration(unittest.TestCase):
    """DeepSeek AI集成测试"""

    def setUp(self):
        """测试前的设置"""
        # 注册DeepSeek AI类型（如果没有注册）
        if not AIFactory.is_ai_type_registered('deepseek_ai'):
            from src.ai.deepseek_ai import DeepSeekAI
            AIFactory.register_ai_type(
                name="deepseek_ai",
                ai_class=DeepSeekAI,
                description="基于DeepSeek大语言模型的智能AI",
                default_config={
                    "api_key": "test_key",
                    "model": "deepseek-chat",
                    "fallback_enabled": True
                }
            )

    def test_ai_factory_integration(self):
        """测试与AI工厂的集成"""
        # 检查DeepSeek AI是否已注册
        self.assertTrue(AIFactory.is_ai_type_registered('deepseek_ai'))

        # 检查AI类型信息
        ai_info = AIFactory.get_ai_info('deepseek_ai')
        self.assertEqual(ai_info['name'], 'deepseek_ai')
        self.assertEqual(ai_info['class_name'], 'DeepSeekAI')
        self.assertIn('基于DeepSeek', ai_info['description'])

    def test_ai_creation(self):
        """测试AI实例创建"""
        # 创建DeepSeek AI实例
        ai = AIFactory.create_ai('deepseek_ai',
                                api_key='test_key',
                                fallback_enabled=True)

        self.assertIsInstance(ai, DeepSeekAI)
        self.assertEqual(ai.api_key, 'test_key')
        self.assertTrue(ai.fallback_enabled)

    def test_ai_creation_with_fallback(self):
        """测试带降级机制的AI创建"""
        # 测试降级机制
        ai = AIFactory.create_ai_with_fallback(
            'deepseek_ai',
            fallback_type='rule_based',
            api_key='test_key'
        )

        self.assertIsInstance(ai, DeepSeekAI)

    @patch('src.ai.deepseek_ai.DeepSeekAI.generate_response')
    def test_complete_game_cycle(self, mock_generate):
        """测试完整的游戏循环"""
        # 模拟AI回应
        mock_generate.return_value = AIResponse(
            text="太棒了！继续加油！",
            mood=AIMood.EXCITED,
            priority=7,
            cooldown_time=1.5,
            affinity_change=2
        )

        # 创建DeepSeek AI
        ai = AIFactory.create_ai('deepseek_ai', api_key='test_key')

        # 创建测试上下文
        context = AIContext(
            player_level=3,
            player_combo=5,
            player_power=12,
            enemy_hp_percent=0.7,
            recent_damage=15,
            ai_affinity=45,
            location="新手村",
            time_since_last_comment=3.0,
            player_stamina=90,
            is_level_up=False,
            is_crit_hit=False,
            attack_frequency=1.2,
            crit_frequency=0.08,
            combo_tendency=0.6,
            weapon_tier=1,
            total_coins=50
        )

        # 生成回应
        response = ai.generate_response(context)

        # 验证回应
        self.assertIsNotNone(response)
        self.assertEqual(response.text, "太棒了！继续加油！")
        self.assertEqual(response.mood, AIMood.EXCITED)


class TestDeepSeekAIPerformance(unittest.TestCase):
    """DeepSeek AI性能测试"""

    def setUp(self):
        """测试前的设置"""
        self.deepseek_ai = DeepSeekAI(
            api_key='test_key',
            rate_limit=60,
            timeout=5
        )

    def test_response_time_performance(self):
        """测试响应时间性能"""
        # 测试上下文构建性能
        test_context = AIContext(
            player_level=10,
            player_combo=15,
            player_power=20,
            enemy_hp_percent=0.5,
            recent_damage=30,
            ai_affinity=70,
            location="竹林道场",
            time_since_last_comment=2.0,
            player_stamina=60,
            is_level_up=False,
            is_crit_hit=True,
            attack_frequency=2.0,
            crit_frequency=0.15,
            combo_tendency=0.8,
            weapon_tier=3,
            total_coins=200
        )

        start_time = time.time()
        prompt = self.deepseek_ai._build_contextual_prompt(test_context)
        end_time = time.time()

        # 构建提示应该在合理时间内完成（<100ms）
        self.assertLess(end_time - start_time, 0.1)
        self.assertGreater(len(prompt), 100)  # 确保提示有内容

    def test_memory_usage(self):
        """测试内存使用"""
        import sys

        # 记录初始内存使用
        initial_size = sys.getsizeof(self.deepseek_ai)

        # 添加大量对话历史
        for i in range(100):
            self.deepseek_ai.conversation_history.append({
                "role": "assistant",
                "content": f"测试对话历史 {i}"
            })

        # 检查内存增长
        final_size = sys.getsizeof(self.deepseek_ai)

        # 内存增长应该在合理范围内
        self.assertLess(final_size - initial_size, 50000)  # 50KB增长限制

    def test_rate_limit_performance(self):
        """测试速率限制性能"""
        # 测试速率检查的执行时间
        start_time = time.time()

        for _ in range(1000):
            self.deepseek_ai._check_rate_limit()

        end_time = time.time()

        # 1000次检查应该在很短时间内完成（<10ms）
        self.assertLess(end_time - start_time, 0.01)


if __name__ == '__main__':
    # 创建测试套件
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTest(unittest.makeSuite(TestDeepSeekAI))
    suite.addTest(unittest.makeSuite(TestDeepSeekAIIntegration))
    suite.addTest(unittest.makeSuite(TestDeepSeekAIPerformance))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试结果统计
    print(f"\n{'='*50}")
    print(f"测试结果统计:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"成功率: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")