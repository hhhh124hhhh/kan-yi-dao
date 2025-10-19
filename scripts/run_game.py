#!/usr/bin/env python3
"""
游戏启动脚本 - 自动处理环境配置
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_audio_driver():
    """设置音频驱动"""
    # Linux系统设置静音音频驱动
    if os.name == 'posix':
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        print("🔊 设置音频驱动为静音模式")

def check_dependencies():
    """检查依赖"""
    try:
        import pygame
        print(f"✅ Pygame {pygame.version.ver} 已安装")
    except ImportError:
        print("❌ Pygame 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pygame"])
        print("✅ Pygame 安装完成")

    try:
        import requests
        print("✅ Requests 已安装")
    except ImportError:
        print("❌ Requests 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"])
        print("✅ Requests 安装完成")

def main():
    """主启动函数"""
    print("🎮 《是男人就砍一刀》启动器")
    print("=" * 40)

    # 设置音频驱动
    setup_audio_driver()

    # 检查依赖
    check_dependencies()

    # 设置环境变量
    os.environ['PYTHONPATH'] = str(Path(__file__).parent.parent / "src")

    print("🚀 启动游戏...")
    print()

    # 启动游戏
    try:
        import subprocess
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 游戏启动失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 游戏被用户中断")
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()