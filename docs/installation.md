# 安装指南

## 📋 系统要求

### 基本要求
- Python 3.8+
- 操作系统: Windows, macOS, Linux
- 内存: 至少 2GB RAM
- 存储: 至少 500MB 可用空间

### 推荐配置
- Python 3.10+
- 4GB+ RAM
- 独立显卡（支持硬件加速）

## 🚀 安装步骤

### 1. 获取源代码

#### 方式一：克隆Git仓库
```bash
git clone <repository-url>
cd 砍一刀
```

#### 方式二：下载压缩包
1. 下载项目压缩包
2. 解压到目标目录
3. 进入项目目录

### 2. 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. 安装依赖

#### 基础依赖（必需）
```bash
pip install -r requirements.txt
```

#### 开发依赖（可选）
```bash
pip install -r requirements-dev.txt
```

#### 测试依赖（可选）
```bash
pip install -r requirements-test.txt
```

### 4. 配置环境变量

#### 复制环境变量模板
```bash
cp .env.example .env
```

#### 编辑环境变量
使用文本编辑器打开 `.env` 文件，配置以下变量：

```bash
# 游戏基础配置
GAME_MODE=development
DEFAULT_AI_TYPE=rule_based

# DeepSeek AI配置（可选）
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEFAULT_AI_TYPE=deepseek_ai

# 音频配置（Linux用户可能需要）
SDL_AUDIODRIVER=dummy
```

### 5. 验证安装

#### 运行游戏
```bash
python main.py
```

如果看到游戏启动界面，说明安装成功！

#### 运行测试
```bash
# 运行所有测试
python run_tests.py

# 或使用pytest
pytest tests/ -v
```

## 🔧 常见问题

### 问题1: Pygame安装失败

**症状**: `pip install pygame` 失败

**解决方案**:
```bash
# Windows
pip install pygame --pre

# macOS
brew install sdl2 sdl2_mixer sdl2_ttf sdl2_image
pip install pygame

# Linux (Ubuntu/Debian)
sudo apt-get install python3-pygame
# 或
pip install pygame
```

### 问题2: 音频设备错误

**症状**: `pygame 2.6.1 (SDL 2.28.4, Python 3.12.3) Hello from the pygame community. https://www.pygame.org/contribute/ Game startup failed: dsp: No such audio device`

**解决方案**:
在 `.env` 文件中添加：
```bash
SDL_AUDIODRIVER=dummy
```

### 问题3: 字体渲染错误

**症状**: 游戏中文字体显示异常

**解决方案**:
1. 确保系统安装了中文字体
2. 在游戏中使用F1查看调试信息
3. 检查 `logs/game.log` 中的错误信息

### 问题4: AI模块导入错误

**症状**: `ModuleNotFoundError: No module named 'src.ai.xxx'`

**解决方案**:
```bash
# 检查Python路径
python -c "import sys; print(sys.path)"

# 确保在项目根目录运行
cd /path/to/砍一刀
python main.py
```

### 问题5: DeepSeek API错误

**症状**: API调用失败或回应异常

**解决方案**:
1. 检查API密钥是否正确
2. 确认网络连接正常
3. 检查API配额和限制
4. 在 `.env` 中设置 `ENABLE_AI_FALLBACK=true` 启用降级机制

## 📦 依赖包说明

### 核心依赖
- **pygame**: 游戏引擎和图形渲染
- **requests**: HTTP请求库（AI API调用）
- **python-dotenv**: 环境变量管理
- **typing-extensions**: 类型注解扩展

### 开发依赖
- **pytest**: 测试框架
- **black**: 代码格式化
- **flake8**: 代码检查
- **mypy**: 类型检查

### 可选依赖
- **sphinx**: 文档生成
- **pillow**: 图像处理
- **numpy**: 数学计算优化

## 🚀 高级配置

### 自定义安装路径

如果需要将游戏安装到特定路径：

```bash
# 使用setup.py安装
pip install -e .

# 或创建符号链接
ln -s /path/to/砍一刀/main.py /usr/local/bin/blade-game
```

### Docker安装

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

构建和运行：
```bash
docker build -t blade-game .
docker run -it --rm blade-game
```

## ✅ 安装验证清单

完成安装后，请验证以下项目：

- [ ] Python 3.8+ 已安装
- [ ] 虚拟环境已创建并激活
- [ ] 所有依赖包已安装
- [ ] `.env` 文件已配置
- [ ] `python main.py` 可以正常启动
- [ ] 游戏界面正常显示
- [ ] 鼠标点击可以攻击
- [ ] 音效正常播放（或静音模式正常）
- [ ] AI评论功能正常
- [ ] 测试套件运行通过

如果以上项目都正常，恭喜！你已经成功安装了《是男人就砍一刀》游戏！