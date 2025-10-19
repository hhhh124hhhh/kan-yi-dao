# 《是男人就砍一刀》项目结构

```
砍一刀/
├── 📄 README.md                    # 项目说明文档
├── 📄 LICENSE                      # MIT开源许可证
├── 📄 .gitignore                   # Git忽略文件
├── 📄 .env.example                 # 环境变量模板
├── 📄 requirements.txt             # 基础依赖包
├── 📄 requirements-dev.txt         # 开发依赖包
├── 📄 requirements-test.txt        # 测试依赖包
├── 📄 setup.py                     # 包安装配置
├── 📄 main.py                      # 🎮 游戏入口文件
├── 📄 pytest.ini                  # 测试配置
├── 📄 run_tests.py                 # 测试运行脚本
│
├── 📁 src/                         # 📦 源代码目录
│   ├── 📄 __init__.py
│   ├── 📁 game/                    # 🎮 游戏核心模块
│   │   ├── 📄 __init__.py
│   │   ├── 📄 player.py             # 👤 玩家类
│   │   ├── 📄 enemy.py              # 👹 敌人类
│   │   ├── 📄 effects.py            # ✨ 特效系统
│   │   ├── 📄 ui.py                 # 🖼️ UI系统
│   │   ├── 📄 sound_manager.py      # 🔊 音效管理
│   │   ├── 📄 data_manager.py       # 💾 数据管理
│   │   └── 📄 main.py               # 🎮 游戏主类
│   │
│   ├── 📁 ai/                      # 🤖 AI系统模块
│   │   ├── 📄 __init__.py
│   │   ├── 📄 ai_interface.py       # 🔌 AI接口定义
│   │   ├── 📄 ai_factory.py         # 🏭 AI工厂
│   │   ├── 📄 ai_manager.py         # 👥 AI管理器
│   │   ├── 📄 context_engine.py     # 🧠 上下文引擎
│   │   ├── 📄 rule_based_ai.py      # 📋 规则AI
│   │   ├── 📄 llm_ai.py              # 🧠 LLM AI
│   │   └── 📄 deepseek_ai.py        # 🔥 DeepSeek AI
│   │
│   └── 📁 config/                  # ⚙️ 配置模块
│       ├── 📄 __init__.py
│       └── 📄 settings.py           # 📋 配置文件
│
├── 📁 tests/                       # 🧪 测试目录
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py               # 🧪 pytest配置
│   ├── 📁 test_game/               # 🎮 游戏测试
│   │   ├── 📄 __init__.py
│   │   ├── 📄 test_player.py
│   │   ├── 📄 test_enemy.py
│   │   └── 📄 test_effects.py
│   ├── 📁 test_ai/                 # 🤖 AI测试
│   │   ├── 📄 __init__.py
│   │   ├── 📄 test_ai_agent.py
│   │   └── 📄 test_deepseek_ai.py
│   └── 📁 test_integration/        # 🔗 集成测试
│       ├── 📄 __init__.py
│       └── 📄 test_game_integration.py
│
├── 📁 docs/                        # 📚 文档目录
│   ├── 📄 README.md                # 📖 文档首页
│   ├── 📄 installation.md          # 🔧 安装指南
│   ├── 📄 deepseek_guide.md        # 🤖 DeepSeek使用指南
│   ├── 📄 PRD.MD                   # 📋 产品需求文档
│   ├── 📄 UI.md                    # 🎨 UI设计文档
│   └── 📄 注意事项.md              # ⚠️ 注意事项
│
├── 📁 assets/                      # 🎨 游戏资源目录
│   ├── 📁 images/                  # 🖼️ 图片资源
│   ├── 📁 sounds/                  # 🔊 音效资源
│   ├── 📁 fonts/                   # 🔤 字体资源
│   └── 📁 data/                    # 📊 游戏数据
│
├── 📁 scripts/                     # 🛠️ 脚本目录
│   └── 📄 run_game.py              # 🎮 游戏启动脚本
│
├── 📁 logs/                        # 📝 日志目录
├── 📁 saves/                       # 💾 存档目录
└── 📁 .github/                     # 🐙 GitHub配置
    └── 📁 workflows/               # 🔄 GitHub Actions
```

## 🎯 核心文件说明

### 游戏入口
- **`main.py`** - 游戏启动入口，包含横幅显示和依赖检查
- **`scripts/run_game.py`** - 智能启动脚本，自动处理环境配置

### 游戏核心 (src/game/)
- **`player.py`** - 玩家角色类，包含攻击、升级、连击等机制
- **`enemy.py`** - 敌人类（稻草人），包含血量和受击逻辑
- **`effects.py`** - 特效系统，处理伤害数字、连击效果等
- **`ui.py`** - 用户界面系统，显示状态栏、AI对话等
- **`main.py`** - 游戏主循环类，管理游戏状态和事件处理

### AI系统 (src/ai/)
- **`ai_interface.py`** - AI行为接口定义
- **`ai_factory.py`** - AI实例工厂，支持动态创建不同类型AI
- **`ai_manager.py`** - AI管理器，统一管理AI实例和上下文
- **`deepseek_ai.py`** - DeepSeek大语言模型AI实现
- **`rule_based_ai.py`** - 基于规则的AI实现

### 配置系统 (src/config/)
- **`settings.py`** - 游戏配置，包含屏幕设置、游戏平衡参数、AI配置等

### 测试系统 (tests/)
- **`test_game/`** - 游戏核心功能测试
- **`test_ai/`** - AI系统测试
- **`test_integration/`** - 集成测试

## 🚀 运行方式

### 方式一：直接运行
```bash
python main.py
```

### 方式二：使用启动脚本
```bash
python scripts/run_game.py
```

### 方式三：安装后运行
```bash
pip install -e .
blade-game
```

## 🔧 开发模式

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
python run_tests.py

# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/
```

## 📦 项目特色

✅ **标准Python项目结构** - 符合PEP标准和开源项目规范
✅ **模块化架构** - 清晰的代码组织和依赖关系
✅ **完整测试覆盖** - 单元测试、集成测试、AI测试
✅ **智能AI系统** - 支持多种AI类型，可扩展设计
✅ **详细文档** - 完善的安装、开发、API文档
✅ **生产就绪** - 包含日志、错误处理、配置管理
✅ **GitHub友好** - 标准的开源项目配置

这个项目结构支持快速开发、易于维护，并符合GitHub开源项目的最佳实践！