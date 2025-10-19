#!/usr/bin/env python3
"""
项目清理脚本
清理缓存文件、临时文件和构建产物
"""

import os
import shutil
import glob
from pathlib import Path
import argparse

def clean_cache():
    """清理Python缓存文件"""
    print("🧹 清理Python缓存文件...")

    # 清理__pycache__
    cache_dirs = list(Path('.').rglob('__pycache__'))
    for cache_dir in cache_dirs:
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
            print(f"  删除: {cache_dir}")

    # 清理.pyc文件
    pyc_files = list(Path('.').rglob('*.pyc'))
    for pyc_file in pyc_files:
        pyc_file.unlink()
        print(f"  删除: {pyc_file}")

    # 清理.pyo文件
    pyo_files = list(Path('.').rglob('*.pyo'))
    for pyo_file in pyo_files:
        pyo_file.unlink()
        print(f"  删除: {pyo_file}")

def clean_coverage():
    """清理测试覆盖率文件"""
    print("🧹 清理测试覆盖率文件...")

    coverage_files = [
        '.coverage',
        'coverage.xml',
        'htmlcov/'
    ]

    for item in coverage_files:
        path = Path(item)
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  删除目录: {path}")
            else:
                path.unlink()
                print(f"  删除文件: {path}")

def clean_build():
    """清理构建文件"""
    print("🧹 清理构建文件...")

    build_dirs = ['build', 'dist', '*.egg-info']

    for pattern in build_dirs:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  删除目录: {path}")
            elif path.is_file():
                path.unlink()
                print(f"  删除文件: {path}")

def clean_logs():
    """清理日志文件"""
    print("🧹 清理日志文件...")

    log_files = list(Path('logs').glob('*.log')) if Path('logs').exists() else []

    for log_file in log_files:
        if log_file.name != 'README.md':
            log_file.unlink()
            print(f"  删除: {log_file}")

def clean_saves():
    """清理存档文件"""
    print("🧹 清理存档文件...")

    save_files = list(Path('saves').glob('*.json')) if Path('saves').exists() else []

    for save_file in save_files:
        if save_file.name != 'README.md':
            save_file.unlink()
            print(f"  删除: {save_file}")

def main():
    parser = argparse.ArgumentParser(description='项目清理工具')
    parser.add_argument('--all', action='store_true', help='清理所有文件')
    parser.add_argument('--cache', action='store_true', help='清理缓存文件')
    parser.add_argument('--coverage', action='store_true', help='清理覆盖率文件')
    parser.add_argument('--build', action='store_true', help='清理构建文件')
    parser.add_argument('--logs', action='store_true', help='清理日志文件')
    parser.add_argument('--saves', action='store_true', help='清理存档文件')

    args = parser.parse_args()

    if not any([args.all, args.cache, args.coverage, args.build, args.logs, args.saves]):
        args.all = True

    print("🚀 开始清理项目...")

    if args.all or args.cache:
        clean_cache()

    if args.all or args.coverage:
        clean_coverage()

    if args.all or args.build:
        clean_build()

    if args.all or args.logs:
        clean_logs()

    if args.all or args.saves:
        clean_saves()

    print("✅ 清理完成!")

if __name__ == "__main__":
    main()