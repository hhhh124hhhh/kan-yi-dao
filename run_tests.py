#!/usr/bin/env python3
"""
游戏测试运行脚本
运行《是男人就砍一刀》项目的所有测试
"""

import sys
import os
import subprocess
import time
from pathlib import Path

class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests"
        self.report_dir = self.project_root / "test_reports"
        self.coverage_dir = self.project_root / "coverage"

        # 确保目录存在
        self.report_dir.mkdir(exist_ok=True)
        self.coverage_dir.mkdir(exist_ok=True)

        # 测试配置
        self.test_config = {
            'unit_tests': [
                'tests/test_player.py',
                'tests/test_ai_agent.py',
                'tests/test_enemy.py',
                'tests/test_effects.py'
            ],
            'integration_tests': [
                'tests/test_game_integration.py'
            ],
            'slow_tests': [
                'tests/test_game_integration.py::TestGameIntegration::test_complete_game_loop_simulation',
                'tests/test_game_integration.py::TestGameIntegration::test_performance_integration'
            ]
        }

    def check_dependencies(self):
        """检查测试依赖"""
        print("🔍 检查测试依赖...")

        try:
            import pytest
            print(f"✅ pytest 版本: {pytest.__version__}")
        except ImportError:
            print("❌ pytest 未安装")
            print("请运行: pip install -r requirements-test.txt")
            return False

        try:
            import pygame
            print(f"✅ pygame 版本: {pygame.version.ver}")
        except ImportError:
            print("❌ pygame 未安装")
            print("请运行: pip install pygame")
            return False

        return True

    def run_unit_tests(self) -> bool:
        """运行单元测试"""
        print("\n🧪 运行单元测试...")

        cmd = [
            sys.executable, "-m", "pytest",
            "-v",
            "--tb=short",
            "--durations=10",
            "-m", "unit or not slow",
            "--junitxml", f"{self.report_dir}/unit_results.xml"
        ] + self.test_config['unit_tests']

        return self._run_command("单元测试", cmd)

    def run_integration_tests(self) -> bool:
        """运行集成测试"""
        print("\n🔗 运行集成测试...")

        cmd = [
            sys.executable, "-m", "pytest",
            "-v",
            "--tb=short",
            "--durations=10",
            "-m", "integration",
            "--junitxml", f"{self.report_dir}/integration_results.xml"
        ] + self.test_config['integration_tests']

        return self._run_command("集成测试", cmd)

    def run_slow_tests(self) -> bool:
        """运行慢速测试"""
        print("\n🐌 运行慢速测试...")

        cmd = [
            sys.executable, "-m", "pytest",
            "-v",
            "--tb=short",
            "--durations=10",
            "-m", "slow",
            "--junitxml", f"{self.report_dir}/slow_results.xml"
        ] + self.test_config['slow_tests']

        return self._run_command("慢速测试", cmd)

    def run_coverage_tests(self) -> bool:
        """运行覆盖率测试"""
        print("\n📊 运行覆盖率测试...")

        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=.",
            "--cov-report=html",
            "--cov-html", f"{self.coverage_dir}",
            "--cov-report=term",
            "--cov-report=xml",
            "--cov-xml", f"{self.report_dir}/coverage.xml",
            "--cov-report=annotate-missing",
            "--junitxml", f"{self.report_dir}/coverage_results.xml"
        ]

        return self._run_command("覆盖率测试", cmd)

    def run_performance_tests(self) -> bool:
        """运行性能测试"""
        print("\n⚡ 运行性能测试...")

        cmd = [
            sys.executable, "-m", "pytest",
            "-v",
            "--tb=short",
            "--benchmark-only",
            "--benchmark-json",
            f"--benchmark-json={self.report_dir}/benchmark.json",
            "--junitxml",
            f"--junitxml={self.report_dir}/performance_results.xml"
        ]

        return self._run_command("性能测试", cmd, check_returncode=False)

    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print("🚀 运行所有测试...")
        print("=" * 60)

        # 检查依赖
        if not self.check_dependencies():
            return False

        # 记录开始时间
        start_time = time.time()

        # 按顺序运行测试
        results = []

        # 1. 单元测试
        if not self.run_unit_tests():
            results.append("单元测试失败")

        # 2. 集成测试
        if not self.run_integration_tests():
            results.append("集成测试失败")

        # 3. 覆盖率测试
        if not self.run_coverage_tests():
            results.append("覆盖率测试失败")

        # 4. 慢速测试（可选）
        slow_result = self.run_slow_tests()
        if not slow_result:
            print("⚠️ 慢速测试未通过或被跳过")

        # 5. 性能测试（可选）
        perf_result = self.run_performance_tests()
        if not perf_result:
            print("⚠️ 性能测试未通过或被跳过")

        # 计算总耗时
        end_time = time.time()
        duration = end_time - start_time

        # 输出总结
        print("\n" + "=" * 60)
        print(f"🏁 测试完成！总耗时: {duration:.2f}秒")

        if not results:
            print("✅ 所有测试通过！")
            self._print_test_summary()
            return True
        else:
            print("❌ 以下测试失败:")
            for result in results:
                print(f"  - {result}")
            return False

    def run_quick_tests(self) -> bool:
        """运行快速测试（跳过慢速测试）"""
        print("⚡ 运行快速测试...")
        print("=" * 50)

        # 检查依赖
        if not self.check_dependencies():
            return False

        start_time = time.time()

        # 只运行单元测试和集成测试
        results = []

        if not self.run_unit_tests():
            results.append("单元测试失败")

        if not self.run_integration_tests():
            results.append("集成测试失败")

        # 快速覆盖率测试
        if not self.run_coverage_tests():
            results.append("覆盖率测试失败")

        end_time = time.time()
        duration = end_time - start_time

        print("\n" + "=" * 50)
        print(f"⚡ 快速测试完成！耗时: {duration:.2f}秒")

        if not results:
            print("✅ 快速测试全部通过！")
            return True
        else:
            print("❌ 快速测试失败:")
            for result in results:
                print(f"  - {result}")
            return False

    def _run_command(self, test_name: str, cmd: list, check_returncode: bool = True) -> bool:
        """运行命令"""
        try:
            print(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=check_returncode
            )

            if result.stdout:
                print(result.stdout)

            if result.stderr and result.returncode != 0:
                print(f"错误输出: {result.stderr}")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print(f"❌ {test_name} 超时")
            return False
        except Exception as e:
            print(f"❌ {test_name} 执行失败: {e}")
            return False

    def _print_test_summary(self):
        """打印测试总结"""
        print("\n📋 测试报告:")
        print(f"📁 测试报告目录: {self.report_dir}")
        print(f"📊 覆盖率报告: {self.coverage_dir}/index.html")

        # 列出生成的报告文件
        report_files = list(self.report_dir.glob("*.xml"))
        if report_files:
            print(f"📄 JUnit XML报告: {len(report_files)}个文件")

    def generate_html_report(self) -> None:
        """生成HTML测试报告"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>《是男人就砍一刀》测试报告</title>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: #f0f0f0;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                .test-type {{
                    background: #e8f4f8;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                }}
                .success {{
                    color: #28a745;
                }}
                .error {{
                    color: #dc3545;
                }}
                .coverage {{
                    background: #fff3cd;
                    padding: 15px;
                    border-radius: 5px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>《是男人就砍一刀》测试报告</h1>
                <p>生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div class="section">
                <h2>测试概览</h2>
                <div class="test-type">
                    <h3>🧪 单元测试</h3>
                    <p>测试各个组件的独立功能</p>
                    <ul>
                        <li>玩家系统 (Player)</li>
                        <li>AI系统 (AIAgent, RuleBasedAI)</li>
                        <li>敌人系统 (StrawDummy)</li>
                        <li>特效系统 (EffectManager)</li>
                    </ul>
                </div>

                <div class="test-type">
                    <h3>🔗 集成测试</h3>
                    <p>测试组件间的交互</p>
                    <ul>
                        <li>完整攻击循环</li>
                        <li>升级系统</li>
                        <li>连击系统</li>
                        <li>AI反应机制</li>
                    </ul>
                </div>
            </div>

            <div class="section">
                <h2>测试覆盖率</h2>
                <div class="coverage">
                    <p>详细的代码覆盖率报告请查看:</p>
                    <p><a href="../coverage/index.html">HTML覆盖率报告</a></p>
                </div>
            </div>

            <div class="section">
                <h2>如何运行测试</h2>
                <table>
                    <tr>
                        <th>命令</th>
                        <th>描述</th>
                    </tr>
                    <tr>
                        <td><code>python run_tests.py</code></td>
                        <td>运行所有测试</td>
                    </tr>
                    <tr>
                        <td><code>python run_tests.py quick</code></td>
                        <td>运行快速测试</td>
                    </tr>
                    <tr>
                        <td><code>pytest</code></td>
                        <td>使用pytest直接运行</td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """

        html_file = self.report_dir / "index.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"📄 HTML报告已生成: {html_file}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="《是男人就砍一刀》测试运行器")
    parser.add_argument(
        'mode',
        nargs='?',
        choices=['all', 'quick', 'unit', 'integration', 'coverage', 'slow', 'performance'],
        default='all',
        help='测试运行模式'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='生成HTML报告'
    )

    args = parser.parse_args()

    runner = TestRunner()

    try:
        success = True

        if args.mode == 'all':
            success = runner.run_all_tests()
        elif args.mode == 'quick':
            success = runner.run_quick_tests()
        elif args.mode == 'unit':
            success = runner.run_unit_tests()
        elif args.mode == 'integration':
            success = runner.run_integration_tests()
        elif args.mode == 'coverage':
            success = runner.run_coverage_tests()
        elif args.mode == 'slow':
            success = runner.run_slow_tests()
        elif args.mode == 'performance':
            success = runner.run_performance_tests()

        if args.report:
            runner.generate_html_report()

        # 设置退出码
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试运行器错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()