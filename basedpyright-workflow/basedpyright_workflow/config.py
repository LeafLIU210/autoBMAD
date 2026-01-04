"""简化配置模块.

仅从 pyproject.toml 读取配置，遵循奥卡姆剃刀原则。
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore


@dataclass
class Config:
    """工作流配置."""

    source_dir: Path = field(default_factory=lambda: Path("src"))
    output_dir: Path = field(default_factory=lambda: Path(".bpr"))
    include_ruff: bool = True
    ruff_fix: bool = False
    ruff_select: list[str] = field(default_factory=lambda: ["E", "W", "F", "I"])
    ruff_ignore: list[str] = field(default_factory=lambda: ["E501"])


def load_config(project_root: Path | None = None) -> Config:
    """从 pyproject.toml 加载配置.

    Args:
        project_root: 项目根目录，默认为当前目录

    Returns:
        Config 配置对象
    """
    if project_root is None:
        project_root = Path.cwd()

    config = Config()
    pyproject = project_root / "pyproject.toml"

    if not pyproject.exists():
        return config

    try:
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return config

    # 读取 [tool.basedpyright-workflow] 配置
    tool_config: dict[str, Any] = data.get("tool", {}).get("basedpyright-workflow", {})

    if "source_dir" in tool_config:
        config.source_dir = Path(tool_config["source_dir"])
    if "output_dir" in tool_config:
        config.output_dir = Path(tool_config["output_dir"])
    if "include_ruff" in tool_config:
        config.include_ruff = bool(tool_config["include_ruff"])
    if "ruff_fix" in tool_config:
        config.ruff_fix = bool(tool_config["ruff_fix"])
    if "ruff_select" in tool_config:
        config.ruff_select = list(tool_config["ruff_select"])
    if "ruff_ignore" in tool_config:
        config.ruff_ignore = list(tool_config["ruff_ignore"])

    return config
