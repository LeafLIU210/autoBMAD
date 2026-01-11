"""文件扫描工具模块.

提供统一的文件扫描功能，支持递归查找Python文件。
"""

from pathlib import Path
from typing import List


def get_python_files(source_dir: Path) -> List[Path]:
    """递归扫描指定目录下的所有Python文件.

    Args:
        source_dir: 源代码目录路径

    Returns:
        Python文件路径列表（已排序）

    Examples:
        >>> from pathlib import Path
        >>> files = get_python_files(Path("src"))
        >>> len(files) > 0
        True
    """
    if not source_dir.exists():
        raise FileNotFoundError(f"源目录不存在: {source_dir}")

    if not source_dir.is_dir():
        raise NotADirectoryError(f"路径不是目录: {source_dir}")

    # 递归查找所有.py文件，排除隐藏文件
    python_files = [
        path for path in source_dir.rglob("*.py")
        if not path.name.startswith(".")
    ]

    # 按路径排序确保一致性
    return sorted(python_files)


def get_latest_file(directory: Path, pattern: str) -> Path | None:
    """获取指定目录中匹配模式的最新文件.

    Args:
        directory: 搜索目录
        pattern: 文件模式（如 "*.json"）

    Returns:
        最新文件路径或 None

    Examples:
        >>> from pathlib import Path
        >>> file = get_latest_file(Path("results"), "*.json")
        >>> file is None or file.exists()
        True
    """
    if not directory.exists():
        return None

    files = sorted(
        directory.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    return files[0] if files else None
