# DeepSeek AI集成使用指南

## 📖 概述

《是男人就砍一刀》游戏现已集成DeepSeek大语言模型AI，提供更智能、更富有个性的游戏陪练体验。DeepSeek AI专门为游戏场景优化，支持中文对话，能够根据玩家行为动态调整回应风格。

## 🚀 快速开始

### 1. 获取DeepSeek API密钥

1. 访问 [DeepSeek平台](https://platform.deepseek.com/)
2. 注册账号并登录
3. 在控制台创建新的API密钥
4. 复制API密钥备用

### 2. 配置环境变量

创建 `.env` 文件（基于 `.env.example`）：

```bash
# 复制模板文件
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEFAULT_AI_TYPE=deepseek_ai
```

### 3. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装完整开发环境（可选）
pip install -r requirements-dev.txt
```

### 4. 运行游戏

```bash
python main.py
```

## ⚙️ 详细配置

### 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DEEPSEEK_API_KEY` | - | DeepSeek API密钥（必需） |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | API基础URL |
| `DEEPSEEK_MODEL` | `deepseek-chat` | 使用的模型 |
| `DEEPSEEK_TEMPERATURE` | `0.7` | 回应随机性（0-1） |
| `DEEPSEEK_MAX_TOKENS` | `150` | 最大回应长度 |
| `DEEPSEEK_TIMEOUT` | `10` | 请求超时时间（秒） |
| `DEEPSEEK_RATE_LIMIT` | `60` | 每分钟请求限制 |
| `DEFAULT_AI_TYPE` | `rule_based` | 默认AI类型 |
| `ENABLE_AI_FALLBACK` | `true` | 是否启用降级机制 |

### AI类型选择

游戏支持多种AI类型：

- `rule_based`: 基于规则的AI（默认，免费）
- `llm_ai`: 基于智谱AI的LLM
- `deepseek_ai`: 基于DeepSeek的AI（推荐）

在 `.env` 文件中设置：

```bash
DEFAULT_AI_TYPE=deepseek_ai
```

或者在游戏中动态切换：

```python
from ai_manager import AIManager

# 创建DeepSeek AI
ai_manager = AIManager("deepseek_ai")

# 动态切换
ai_manager.switch_ai_type("deepseek_ai")
```

## 🎭 AI角色系统

DeepSeek AI提供4种游戏专用角色：

### 1. 剑术导师 (veteran_swordsman)
- **特点**: 经验丰富，专业严谨
- **说话风格**: 沉稳、专业，偶尔引用武学经典
- **适合场景**: 技术指导、进阶建议
- **示例语录**: "这一刀的角度很好，记住这个要领"

### 2. 热血伙伴 (energetic_friend)
- **特点**: 充满激情，鼓励为主
- **说话风格**: 活泼、热情，使用现代网络用语
- **适合场景**: 情绪激励、氛围营造
- **示例语录**: "起飞了兄弟！这手感太顶了！🔥"

### 3. 搞笑解说员 (wacky_commentator)
- **特点**: 幽默风趣，娱乐至上
- **说话风格**: 诙谐、幽默，喜欢开玩笑和吐槽
- **适合场景**: 娱乐效果、压力释放
- **示例语录**: "哈哈哈这刀也太离谱了！稻草人：我太难了"

### 4. 战术分析师 (strategic_analyst)
- **特点**: 冷静理性，数据导向
- **说话风格**: 理性、精确，使用数据和专业术语
- **适合场景**: 数据分析、优化建议
- **示例语录**: "当前攻击频率1.5刀/秒，暴击率12.3%，建议优化连击节奏"

### 切换角色

```python
# 在游戏中切换AI角色
ai_manager.ai_engine.set_persona('wacky_commentator')

# 获取当前角色信息
persona_info = ai_manager.ai_engine.get_current_persona_info()
print(f"当前角色: {persona_info['name']}")
```

## 🎮 游戏中的AI行为

### 触发场景

DeepSeek AI会在以下情况下发表评论：

1. **连击时刻**
   - 8连击以上：基础鼓励
   - 15连击以上：高度兴奋
   - 20连击以上：超神赞美

2. **暴击时刻**
   - 造成暴击时立即回应
   - 根据伤害大小调整赞美程度

3. **升级时刻**
   - 玩家升级时热烈祝贺
   - 结合当前等级给出鼓励

4. **关键战斗时刻**
   - 敌人血量低于20%时催促
   - 体力不足时关心提醒

5. **特殊成就**
   - 高额伤害、完美连击等

### 回应风格示例

#### 热血伙伴风格
```
玩家15连击 → "起飞了！这连击数有点离谱啊！"
造成暴击 → "暴击爽翻！伤害爆炸！💥"
升级时刻 → "恭喜升级！实力暴涨！🎉"
体力不足 → "没蓝了兄弟？回回再来！"
```

#### 剑术导师风格
```
玩家15连击 → "连击流畅度很好，节奏把握精准"
造成暴击 → "这一刀力道十足，角度恰到好处"
升级时刻 → "修为精进，基础更加扎实"
体力不足 → "注意呼吸节奏，合理分配体力"
```

## 🔧 高级配置

### 成本控制

为控制API使用成本，可设置以下限制：

```python
# 在config.py中配置
DEEPSEEK_COST_CONTROL = {
    'daily_token_limit': 10000,        # 每日token限制
    'cost_warning_threshold': 0.8,     # 80%时警告
    'auto_fallback_threshold': 0.95,   # 95%时自动降级
    'usage_reset_hour': 0              # 午夜重置
}
```

### 自定义系统提示

可以修改AI的系统提示来自定义回应风格：

```python
# 在deepseek_ai.py中修改
def _build_game_optimized_prompt(self) -> str:
    return f"""
    你是游戏AI助手...
    自定义你的回应规则和风格
    """
```

### 批量配置示例

创建 `deepseek_config.json`:

```json
{
    "api_settings": {
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 150
    },
    "personality_settings": {
        "default_persona": "energetic_friend",
        "auto_switch": true,
        "switch_triggers": {
            "high_combo": "wacky_commentator",
            "low_stamina": "veteran_swordsman"
        }
    },
    "cost_control": {
        "daily_limit": 50000,
        "enable_fallback": true
    }
}
```

## 📊 监控和调试

### API使用统计

```python
# 获取API使用统计
stats = ai_manager.ai_engine.get_api_stats()
print(f"总请求数: {stats['total_requests']}")
print(f"最近5分钟: {stats['recent_requests']}")
print(f"速率限制: {stats['rate_limit']}")
```

### 日志记录

DeepSeek AI会自动记录详细日志：

```bash
# 查看日志文件
tail -f logs/game.log

# 过滤DeepSeek相关日志
grep "DeepSeek" logs/game.log
```

### 测试模式

启用测试模式使用模拟数据：

```bash
# 在.env文件中设置
TEST_MODE=true
MOCK_AI_RESPONSES=true
```

## 🧪 测试

### 运行DeepSeek AI测试

```bash
# 运行专门的DeepSeek测试
python -m pytest tests/test_deepseek_ai.py -v

# 运行所有AI相关测试
python -m pytest tests/test_ai_* -v

# 生成覆盖率报告
python -m pytest tests/test_deepseek_ai.py --cov=deepseek_ai --cov-report=html
```

### 手动测试

```python
# 创建测试脚本 test_deepseek_manual.py
from deepseek_ai import DeepSeekAI
from ai_interface import AIContext, AIMood

# 创建AI实例
ai = DeepSeekAI(api_key='your_key')

# 创建测试上下文
context = AIContext(
    player_level=10,
    player_combo=20,
    player_power=25,
    enemy_hp_percent=0.1,
    recent_damage=50,
    ai_affinity=80,
    location="竹林道场",
    time_since_last_comment=5.0,
    player_stamina=30,
    is_crit_hit=True,
    is_level_up=False
)

# 测试回应生成
response = ai.generate_response(context)
if response:
    print(f"AI回应: {response.text}")
    print(f"情绪: {response.mood.value}")
    print(f"优先级: {response.priority}")
else:
    print("未生成回应")
```

## 🔧 故障排除

### 常见问题

#### 1. API密钥错误
```
错误: DeepSeek API error: 401 - Unauthorized
解决: 检查API密钥是否正确设置
```

#### 2. 网络连接问题
```
错误: DeepSeek API network error
解决: 检查网络连接和代理设置
```

#### 3. 速率限制
```
错误: DeepSeek API rate limit exceeded
解决: 降低请求频率或升级API计划
```

#### 4. 降级到规则AI
```
信息: Falling back to rule-based AI
原因: DeepSeek API不可用或配置错误
```

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.getLogger('deepseek_ai').setLevel(logging.DEBUG)
   ```

2. **检查配置**
   ```python
   from config import DEEPSEEK_CONFIG
   print(DEEPSEEK_CONFIG)
   ```

3. **测试API连接**
   ```python
   # 测试API可用性
   ai = DeepSeekAI(api_key='your_key')
   print(f"API Key配置: {bool(ai.api_key)}")
   ```

## 🚀 性能优化

### 缓存策略

```python
# 启用响应缓存
ai = DeepSeekAI(
    api_key='your_key',
    enable_cache=True,
    cache_ttl=300  # 5分钟缓存
)
```

### 异步请求

```python
# 使用异步模式（高级用法）
import asyncio

async def async_ai_response():
    response = await ai.generate_response_async(context)
    return response
```

### 批量处理

```python
# 批量生成回应（减少API调用）
contexts = [context1, context2, context3]
responses = ai.generate_batch_responses(contexts)
```

## 📈 最佳实践

### 1. API使用优化
- 合理设置`max_tokens`避免浪费
- 使用适当的`temperature`平衡创意和稳定性
- 启用降级机制确保服务可用性

### 2. 成本控制
- 设置每日token限制
- 监控API使用量
- 在非关键时刻使用规则AI

### 3. 用户体验
- 根据玩家水平选择合适的角色
- 避免过于频繁的AI评论
- 保持回应的新鲜感和多样性

### 4. 安全考虑
- 妥善保管API密钥
- 使用环境变量存储敏感信息
- 定期轮换API密钥

## 🤝 社区和支持

### 反馈渠道
- GitHub Issues: 报告bug和功能请求
- 游戏内反馈: 使用F1+R键收集调试信息

### 贡献指南
- 欢迎提交新的角色设定
- 分享有趣的AI对话示例
- 改进回应模板和提示词

---

**注意**: DeepSeek AI需要有效的API密钥才能使用。请确保遵守DeepSeek平台的使用条款和服务协议。