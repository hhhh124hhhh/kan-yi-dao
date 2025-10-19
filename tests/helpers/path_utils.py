"""
测试路径管理工具
统一管理测试环境的Python路径设置
"""

import sys
from pathlib import Path
from typing import List


def get_project_root() -> Path:
    """获取项目根目录路径"""
    # 从当前文件的helpers目录向上两级到达项目根目录
    return Path(__file__).parent.parent.parent


def get_src_path() -> Path:
    """获取src目录路径"""
    return get_project_root() / "src"


def setup_test_paths() -> None:
    """设置测试所需的Python路径

    确保项目结构如下时能正确导入：
    project_root/
    ├── src/
    │   ├── game/
    │   ├── ai/
    │   └── config/
    └── tests/
        ├── helpers/
        ├── test_game/
        ├── test_ai/
        └── test_integration/
    """

    src_path = get_src_path()
    src_path_str = str(src_path)

    # 避免重复添加
    if src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)


def get_test_data_path() -> Path:
    """获取测试数据目录路径"""
    return get_project_root() / "tests" / "test_data"


def get_temp_path() -> Path:
    """获取临时文件目录路径"""
    return get_project_root() / "tests" / "temp"


def ensure_test_directories() -> None:
    """确保测试所需的目录存在"""
    directories = [
        get_test_data_path(),
        get_temp_path(),
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def get_project_files(extension: str = "*.py") -> List[Path]:
    """
    获取项目中指定扩展名的所有文件

    Args:
        extension: 文件扩展名，如 "*.py", "*.md"

    Returns:
        文件路径列表
    """
    project_root = get_project_root()
    return list(project_root.rglob(extension))


# 在模块导入时自动设置路径
setup_test_paths()