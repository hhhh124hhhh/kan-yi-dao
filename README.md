# 《是男人就砍一刀》

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Pygame Version](https://img.shields.io/badge/pygame-2.5+-green.svg)](https://pygame.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/your-username/kan-yi-dao)
[![Test Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](https://github.com/your-username/kan-yi-dao)

一个基于Pygame的解压向动作游戏，具有智能AI陪练系统和完整的游戏机制。

## 🎮 游戏特色

- ⚡ **爽快的打击感** - 流畅的攻击手感和即时反馈
- 🤖 **智能AI陪练** - 支持多种AI类型（规则AI、DeepSeek AI等）
- ✨ **丰富的特效系统** - 连击、暴击、升级等视觉反馈
- 💾 **完整的存档系统** - 支持多存档槽和自动保存
- 🎵 **沉浸式音效** - 攻击、暴击、升级等音效反馈
- 🔧 **高度可配置** - 灵活的游戏参数和AI设置
- 📊 **数据统计** - 详细的游戏数据追踪

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+ (推荐3.10+)
- **Pygame**: 2.5+
- **内存**: 2GB+ RAM
- **系统**: Windows/macOS/Linux

### 安装方式

#### 方式一：直接运行（推荐）

```bash
# 克隆项目
git clone https://github.com/hhhh124hhhh/kan-yi-dao.git

cd kan-yi-dao

# 安装依赖
pip install -r requirements.txt

# 运行游戏
python main.py
```

#### 方式二：使用虚拟环境（推荐开发使用）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行游戏
python main.py
```

#### 方式三：使用项目脚本（Linux/WSL）

```bash
# 使用便捷脚本
./scripts/run_game.sh

# 或使用音频兼容脚本（解决Linux音频问题）
./scripts/run_game_audio.sh
```

## 🎯 游戏操作

### 基础操作
- **鼠标左键**: 攻击稻草人
- **P**: 暂停/继续游戏
- **F1**: 显示/隐藏调试信息
- **F5**: 快速保存游戏
- **F9**: 加载最新存档
- **Ctrl+R**: 重置游戏
- **ESC**: 退出游戏

### 游戏机制

1. **攻击系统**
   - 点击攻击目标
   - 命中判定和伤害计算
   - 体力消耗和恢复
   - 连击和暴击系统

2. **成长系统**
   - 经验值累积
   - 自动升级机制
   - 攻击力提升
   - 武器升级系统

3. **AI反馈系统**
   - 智能评论和鼓励
   - 多种情绪状态
   - 个性化互动

## 🤖 AI系统

游戏支持多种AI陪练类型：

### 规则AI (Rule-based AI) - 默认
- ✅ 基于游戏状态的智能回应
- ✅ 响应快速，无需网络连接
- ✅ 适合离线使用
- ✅ 多种情绪状态和评论

### DeepSeek AI - 高级
- 🤖 基于DeepSeek大语言模型
- 🎭 支持多种角色设定（老兵剑士、热血伙伴等）
- 🧠 智能化、个性化的游戏评论
- 🔑 需要API密钥（可选）

### AI特性对比

| 特性 | 规则AI | DeepSeek AI |
|------|--------|-------------|
| 响应速度 | ⚡ 极快 | 🌐 网络 |
| 网络需求 | ❌ 不需要 | ✅ 需要 |
| 智能程度 | 🎯 中等 | 🧠 高级 |
| 个性化 | 📝 预设 | 🎭 动态 |
| 成本 | 💰 免费 | 💰 API费用 |

## 📁 项目架构

项目采用现代化的Python项目结构：

```
kan-yi-dao/
├── 📁 src/                     # 源代码目录
│   ├── 🎮 game/                # 游戏核心模块
│   │   ├── player.py           # 玩家系统
│   │   ├── enemy.py            # 敌人系统
│   │   ├── effects.py          # 特效系统
│   │   ├── ui.py               # UI界面
│   │   ├── sound_manager.py    # 音效管理
│   │   └── data_manager.py     # 数据管理
│   ├── 🤖 ai/                  # AI系统模块
│   │   ├── ai_interface.py     # AI接口定义
│   │   ├── ai_manager.py       # AI管理器
│   │   ├── ai_factory.py       # AI工厂
│   │   ├── rule_based_ai.py    # 规则AI
│   │   ├── deepseek_ai.py      # DeepSeek AI
│   │   └── context_engine.py   # 上下文引擎
│   └── ⚙️ config/              # 配置模块
│       ├── game_config.py      # 游戏配置
│       └── ai_config.py        # AI配置
├── 🧪 tests/                    # 测试代码目录
│   ├── 🎮 test_game/           # 游戏模块测试
│   ├── 🤖 test_ai/             # AI模块测试
│   ├── 🔗 test_integration/    # 集成测试
│   └── 🛠️ helpers/             # 测试辅助工具
├── 📚 docs/                     # 项目文档
├── 🎨 assets/                   # 游戏资源
│   ├── 🖼️ images/              # 图片资源
│   ├── 🎵 sounds/              # 音效资源
│   └── 📊 data/                # 数据文件
├── 🔧 scripts/                  # 工具脚本
├── 📄 requirements/             # 依赖管理
│   ├── requirements.txt         # 基础依赖
│   ├── requirements-dev.txt     # 开发依赖
│   └── requirements-test.txt    # 测试依赖
├── 🏗️ .github/                  # GitHub配置
│   └── 🔄 workflows/            # CI/CD工作流
├── 📋 pyproject.toml           # 项目配置
├── 🧪 pytest.ini               # 测试配置
├── 🌍 .env.example             # 环境变量模板
└── 🎮 main.py                  # 游戏入口文件
```

## 🔧 配置说明

### 环境变量配置

复制环境变量模板：
```bash
cp .env.example .env
```

在 `.env` 文件中可以配置以下选项：

```bash
# 游戏基础配置
GAME_MODE=development           # 游戏模式: development/production/testing
DEFAULT_AI_TYPE=rule_based     # 默认AI类型: rule_based/deepseek_ai
AUTO_SAVE_INTERVAL=300          # 自动保存间隔（秒）

# DeepSeek AI配置（可选）
DEEPSEEK_API_KEY=your_api_key   # DeepSeek API密钥
DEEPSEEK_MODEL=deepseek-chat    # 使用的模型
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 音频配置（Linux用户可能需要）
SDL_AUDIODRIVER=dummy           # 音频驱动设置

# 调试配置
DEBUG_MODE=false                # 调试模式
SHOW_FPS=true                   # 显示帧率
LOG_LEVEL=INFO                  # 日志级别
```

### 游戏内配置

游戏支持通过配置文件调整：
- 🎮 游戏参数（攻击力、经验倍率等）
- 🤖 AI行为（评论频率、性格等）
- 🎨 视觉效果（特效强度、UI布局等）
- 🎵 音效设置（音量、开关等）

## 🧪 测试系统

项目采用现代化的测试架构：

### 运行测试

```bash
# 安装测试依赖
pip install -r requirements-test.txt

# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_game/ -v
pytest tests/test_ai/ -v
pytest tests/test_integration/ -v

# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 并行运行测试（需要pytest-xdist）
pytest -n auto
```

### 测试架构

- **🧪 单元测试**: 测试各模块独立功能
- **🔗 集成测试**: 测试模块间协作
- **⚡ 性能测试**: 测试系统性能
- **🎮 游戏逻辑测试**: 测试游戏核心机制

### 测试工具

- **🏭 测试工厂**: 快速创建测试对象
- **🎭 Mock数据**: 生成测试用模拟数据
- **✅ 自定义断言**: 游戏专用断言工具
- **📊 路径管理**: 统一的测试路径处理

## 🛠️ 开发指南

### 开发环境设置

1. **安装开发依赖**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **代码质量检查**
   ```bash
   # 代码格式化
   black src/ tests/

   # 代码检查
   flake8 src/ tests/

   # 类型检查
   mypy src/

   # 导入排序
   isort src/ tests/
   ```

3. **运行完整测试**
   ```bash
   # 运行所有检查
   make check

   # 或手动运行
   black src/ tests/ && flake8 src/ tests/ && pytest
   ```

### 项目配置

项目使用 `pyproject.toml` 进行现代化配置：

- 🏗️ **构建系统**: setuptools配置
- 🧪 **测试配置**: pytest参数和标记
- 📊 **覆盖率**: 测试覆盖率设置
- 🎨 **代码格式**: Black格式化配置
- 🔍 **代码检查**: Flake8和MyPy配置
- 📦 **依赖管理**: 分层依赖管理

### 添加新功能

1. **功能开发**: 在对应模块中实现功能
2. **单元测试**: 编写相应的单元测试
3. **集成测试**: 确保与其他模块正常协作
4. **文档更新**: 更新相关文档和注释
5. **代码审查**: 通过所有质量检查

### 贡献指南

1. **Fork项目**
2. **创建功能分支**: `git checkout -b feature/amazing-feature`
3. **提交更改**: `git commit -m 'Add amazing feature'`
4. **推送分支**: `git push origin feature/amazing-feature`
5. **创建Pull Request**

## 📚 文档

- [📖 安装指南](docs/installation.md)
- [🔧 配置说明](docs/configuration.md)
- [🤖 AI系统指南](docs/ai_guide.md)
- [🏗️ 架构设计](docs/architecture.md)
- [🧪 测试指南](docs/testing.md)
- [🚀 部署指南](docs/deployment.md)

## 🎮 系统要求

### 最低要求
- **操作系统**: Windows 10 / macOS 10.14 / Ubuntu 18.04
- **Python**: 3.8+
- **内存**: 2GB RAM
- **存储**: 500MB 可用空间
- **显卡**: 支持OpenGL 2.1+

### 推荐配置
- **操作系统**: Windows 11 / macOS 12 / Ubuntu 20.04+
- **Python**: 3.10+
- **内存**: 4GB+ RAM
- **存储**: 1GB+ 可用空间
- **显卡**: 独立显卡

## 🔄 版本历史

- **v1.0.0** - 核心游戏功能
  - ✨ 基础攻击和成长系统
  - 🤖 规则AI陪练系统
  - 💾 存档和配置系统
  - 🧪 完整测试覆盖

- **v1.1.0** - AI增强版本
  - 🤖 DeepSeek AI集成
  - 🎭 多角色AI系统
  - 📊 游戏数据统计
  - 🔧 配置系统优化

- **v1.2.0** - 架构优化版本
  - 🏗️ 重构项目架构，采用现代化结构
  - 🔧 统一属性命名规范，解决技术债务
  - 🛡️ 建立启动时属性验证机制
  - 📚 完善测试体系和文档
  - 📊 25个核心测试100%通过
  - ✅ 游戏启动成功，完全消除属性错误

## 🤝 致谢

感谢以下开源项目：

- [🎮 Pygame](https://pygame.org) - 游戏引擎框架
- [🤖 DeepSeek](https://platform.deepseek.com) - AI模型支持
- [🌐 requests](https://requests.readthedocs.io) - HTTP请求库
- [🧪 pytest](https://pytest.org) - 测试框架
- [🎨 Black](https://black.readthedocs.io) - 代码格式化

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## ⭐ 支持

如果这个项目对你有帮助，请：

1. ⭐ 给项目一个Star
2. 🐛 报告Bug或提出建议
3. 📝 贡献代码或文档
4. 🔗 分享给朋友

---

**《是男人就砍一刀》** - 让每一次砍击都充满爽感！💪⚔️