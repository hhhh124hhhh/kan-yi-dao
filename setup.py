"""
《是男人就砍一刀》游戏安装配置
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README文件
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# 读取requirements文件
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding='utf-8').splitlines()
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="blade-game",
    version="1.0.0",
    author="Game Developer",
    author_email="developer@example.com",
    description="一个解压向的Pygame动作游戏，具有AI陪练系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/blade-game",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment :: Arcade",
        "Topic :: Multimedia :: Games",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "ai": [
            "openai>=1.0.0",
            "anthropic>=0.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "blade-game=game.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "game": [
            "assets/images/*",
            "assets/sounds/*",
            "assets/fonts/*",
        ],
    },
    keywords=[
        "game", "pygame", "action", "ai", "chinese", "relaxing",
        "stress-relief", "arcade", "single-player"
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-username/blade-game/issues",
        "Source": "https://github.com/your-username/blade-game",
        "Documentation": "https://blade-game.readthedocs.io/",
    },
)