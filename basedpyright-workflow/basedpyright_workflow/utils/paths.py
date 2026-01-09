"""路径处理工具模块.

提供统一的路径处理和目录管理功能。
"""

from pathlib import Path


def setup_directories(base_dir: Path = None) -> tuple[Path, Path, Path]:
    """设置并返回源代码、结果和报告目录路径.

    Args:
        base_dir: 基础目录（默认为当前工作目录）

    Returns:
        (source_dir, results_dir, reports_dir) 元组

    Examples:
        >>> from pathlib import Path
        >>> src, res, rep = setup_directories(Path.cwd())
        >>> all(isinstance(p, Path) for p in [src, res, rep])
        True
    """
    if base_dir is None:
        base_dir = Path.cwd()

    source_dir = base_dir / "src"
    results_dir = base_dir / "results"
    reports_dir = base_dir / "reports"

    # 确保目录存在
    results_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    return source_dir, results_dir, reports_dir


def get_absolute_path(path: str | Path) -> Path:
    """获取绝对路径并解析符号链接.

    Args:
        path: 路径字符串或Path对象

    Returns:
        绝对路径对象

    Raises:
        FileNotFoundError: 如果路径不存在

    Examples:
        >>> path = get_absolute_path(".")
        >>> path.is_absolute()
        True
    """
    path_obj = Path(path) if isinstance(path, str) else path
    absolute = path_obj.resolve()

    if not absolute.exists():
        raise FileNotFoundError(f"路径不存在: {absolute}")

    return absolute


def get_relative_path(from_path: Path, to_path: Path) -> Path | None:
    """获取从一个路径到另一个路径的相对路径.

    Args:
        from_path: 起始路径
        to_path: 目标路径

    Returns:
        相对路径或 None（如果无法计算）

    Examples:
        >>> from pathlib import Path
        >>> get_relative_path(Path("/a/b"), Path("/a/b/c/d"))
        WindowsPath('c/d')
    """
    try:
        return to_path.relative_to(from_path)
    except ValueError:
        # 路径不在同一目录树下
        return None
