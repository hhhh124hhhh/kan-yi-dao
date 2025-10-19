# 《是男人就砍一刀》文档

## 📖 文档目录

### 🚀 快速开始
- [安装指南](installation.md) - 如何安装和配置游戏环境
- [快速上手](quickstart.md) - 游戏基本操作和玩法介绍

### 🤖 AI系统
- [DeepSeek AI指南](deepseek_guide.md) - DeepSeek AI配置和使用说明
- [AI系统架构](ai_architecture.md) - AI系统设计和扩展指南

### 🎮 游戏开发
- [API文档](api/) - 游戏API参考文档
- [架构设计](architecture.md) - 游戏整体架构说明
- [贡献指南](contributing.md) - 如何参与项目开发

### 🔧 开发工具
- [测试指南](testing.md) - 测试框架和测试编写指南
- [部署指南](deployment.md) - 如何部署和发布游戏

## 📋 项目概述

《是男人就砍一刀》是一个解压向的Pygame动作游戏，具有以下特色：

- ✨ **简单爽快的玩法** - 通过点击砍击获得爽感
- 🤖 **智能AI陪练** - 支持多种AI类型（规则AI、DeepSeek AI等）
- 🎨 **丰富的特效系统** - 连击、暴击、升级等视觉反馈
- 💾 **完整的存档系统** - 支持游戏进度保存和加载
- 🎵 **音效反馈** - 增强游戏沉浸感

## 🛠️ 技术栈

- **游戏引擎**: Pygame 2.5+
- **AI系统**: 支持规则AI、DeepSeek、智谱AI等
- **测试框架**: pytest
- **配置管理**: python-dotenv
- **日志系统**: Python logging

## 📁 项目结构

```
砍一刀/
├── src/                    # 源代码
│   ├── game/              # 游戏核心
│   ├── ai/                # AI系统
│   └── config/            # 配置管理
├── tests/                 # 测试代码
├── docs/                  # 项目文档
├── assets/                # 游戏资源
└── scripts/               # 工具脚本
```

## 🚀 快速开始

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd 砍一刀
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件配置API密钥等
   ```

4. **运行游戏**
   ```bash
   python main.py
   ```

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！请查看 [贡献指南](contributing.md) 了解详情。

## 📄 许可证

本项目采用 [MIT License](../LICENSE) 开源协议。