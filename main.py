#!/usr/bin/env python3
"""
《是男人就砍一刀》游戏入口文件
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# 导入环境变量加载
from dotenv import load_dotenv
load_dotenv()

# 导入游戏主类
from src.game.main import Game

# 导入AI模块以确保注册（重要！）
from src.ai import rule_based_ai, llm_ai, deepseek_ai


def print_banner():
    """打印游戏启动横幅"""
    banner = """
╔══════════════════════════════════════╗
║         是男人就砍一刀                ║
║                                      ║
║        一个解压向的动作游戏            ║
║        具有AI陪练系统                  ║
╚══════════════════════════════════════╝
    """
    print(banner)


def check_dependencies():
    """检查依赖是否安装"""
    try:
        import pygame
        print(f"✅ Pygame {pygame.version.ver} 已安装")
    except ImportError:
        print("❌ Pygame 未安装，请运行: pip install -r requirements.txt")
        return False

    try:
        import requests
        print("✅ Requests 已安装")
    except ImportError:
        print("❌ Requests 未安装，请运行: pip install -r requirements.txt")
        return False

    return True


def main():
    """主函数"""
    print_banner()

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    print("🚀 启动游戏中...")

    try:
        # 创建并运行游戏
        game = Game()  # 使用配置中的默认AI类型

        print("🎮 游戏控制说明:")
        print("  - 鼠标左键: 攻击")
        print("  - P: 暂停/继续")
        print("  - F1: 显示/隐藏调试信息")
        print("  - F5: 快速保存")
        print("  - F9: 加载存档")
        print("  - Ctrl+R: 重置游戏")
        print("  - ESC: 退出游戏")
        print()

        game.run()

    except KeyboardInterrupt:
        print("\n👋 游戏被用户中断")
    except Exception as e:
        print(f"❌ 游戏启动失败: {e}")
        print("\n🔧 故障排除建议:")
        print("  1. 确保已安装所有依赖: pip install -r requirements.txt")
        print("  2. 检查音频设备是否可用")
        print("  3. 尝试设置环境变量: SDL_AUDIODRIVER=dummy")
        print("  4. 查看日志文件: logs/game.log")
        sys.exit(1)


if __name__ == "__main__":
    main()