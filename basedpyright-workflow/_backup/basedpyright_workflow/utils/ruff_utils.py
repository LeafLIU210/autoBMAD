"""Ruff工具函数

提供ruff相关的工具函数，包括：
- ruff安装验证和版本检查
- ruff配置文件生成和管理
- ruff输出格式转换
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import tempfile


class RuffNotInstalledError(Exception):
    """Ruff未安装错误"""
    pass


class RuffExecutionError(Exception):
    """Ruff执行错误"""
    pass


def check_ruff_installation() -> bool:
    """检查ruff是否已安装

    Returns:
        bool: ruff是否已安装
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_ruff_version() -> Optional[str]:
    """获取ruff版本

    Returns:
        Optional[str]: ruff版本字符串，如果未安装则返回None
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def validate_ruff_installation() -> None:
    """验证ruff安装，如果未安装则抛出异常"""
    if not check_ruff_installation():
        raise RuffNotInstalledError(
            "Ruff未安装。请使用以下命令安装：\n"
            "pip install ruff\n"
            "或者: pipx install ruff"
        )


def generate_ruff_config(config_dict: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
    """生成ruff配置文件

    Args:
        config_dict: ruff配置字典
        output_path: 输出文件路径，如果为None则使用临时文件

    Returns:
        Path: 配置文件路径
    """
    if output_path is None:
        temp_dir = Path(tempfile.mkdtemp())
        output_path = temp_dir / "ruff.toml"

    # 转换配置格式
    ruff_config = {
        "line-length": config_dict.get("line_length", 88),
        "target-version": config_dict.get("target_version", "py311"),
        "select": config_dict.get("select_rules", ["E", "W", "F", "I"]),
        "ignore": config_dict.get("ignore_rules", ["E501"]),
        "extend-exclude": config_dict.get("extend_exclude", []),
    }

    # 如果有fix_only规则，添加到配置
    if config_dict.get("fix_only"):
        ruff_config["fix"] = {
            "select": config_dict["fix_only"]
        }

    if config_dict.get("preview", False):
        ruff_config["preview"] = True

    # 写入配置文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("[tool.ruff]\n")
            for key, value in ruff_config.items():
                if isinstance(value, list):
                    f.write(f"{key} = {json.dumps(value)}\n")
                elif isinstance(value, bool):
                    f.write(f"{key} = {str(value).lower()}\n")
                elif isinstance(value, dict):
                    f.write(f"[{key}]\n")
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, list):
                            f.write(f"{sub_key} = {json.dumps(sub_value)}\n")
                        else:
                            f.write(f"{sub_key} = {sub_value}\n")
                else:
                    f.write(f"{key} = {value}\n")

        return output_path

    except Exception as e:
        raise RuffExecutionError(f"生成ruff配置文件失败: {e}")


def run_ruff_check(
    source_dir: Path,
    config: Dict[str, Any],
    output_format: str = "json",
    fix: bool = False,
    fix_only: Optional[List[str]] = None,
    config_file: Optional[Path] = None
) -> Tuple[int, str, str]:
    """运行ruff检查

    Args:
        source_dir: 源代码目录
        config: ruff配置
        output_format: 输出格式 (json, text, concise)
        fix: 是否应用修复
        fix_only: 仅修复指定规则
        config_file: 配置文件路径

    Returns:
        Tuple[int, str, str]: (返回码, 标准输出, 标准错误)
    """
    validate_ruff_installation()

    # 构建命令
    cmd = [sys.executable, "-m", "ruff", "check", str(source_dir)]

    # 添加输出格式
    if output_format == "json":
        cmd.extend(["--output-format=json"])
    elif output_format == "concise":
        cmd.extend(["--output-format=concise"])

    # 添加配置文件
    if config_file:
        cmd.extend(["--config", str(config_file)])

    # 添加修复选项
    if fix:
        cmd.append("--fix")

    if fix_only:
        cmd.extend(["--select", ",".join(fix_only)])

    # 添加预览选项
    if config.get("preview", False):
        cmd.append("--preview")

    # 添加排除规则
    extend_exclude = config.get("extend_exclude", [])
    if extend_exclude:
        cmd.extend(["--extend-exclude", ",".join(extend_exclude)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.get("timeout_seconds", 300)
        )
        return result.returncode, result.stdout, result.stderr

    except subprocess.TimeoutExpired as e:
        raise RuffExecutionError(f"ruff执行超时: {e}")
    except Exception as e:
        raise RuffExecutionError(f"ruff执行失败: {e}")


def run_ruff_format(
    source_dir: Path,
    config: Dict[str, Any],
    check_only: bool = False,
    diff: bool = False,
    config_file: Optional[Path] = None
) -> Tuple[int, str, str]:
    """运行ruff格式化

    Args:
        source_dir: 源代码目录
        config: ruff配置
        check_only: 仅检查格式，不修改文件
        diff: 显示差异而不修改
        config_file: 配置文件路径

    Returns:
        Tuple[int, str, str]: (返回码, 标准输出, 标准错误)
    """
    validate_ruff_installation()

    # 构建命令
    cmd = [sys.executable, "-m", "ruff", "format", str(source_dir)]

    # 添加配置文件
    if config_file:
        cmd.extend(["--config", str(config_file)])

    # 检查模式
    if check_only:
        cmd.append("--check")

    # 差异模式
    if diff:
        cmd.append("--diff")

    # 添加排除规则
    extend_exclude = config.get("extend_exclude", [])
    if extend_exclude:
        cmd.extend(["--extend-exclude", ",".join(extend_exclude)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.get("timeout_seconds", 300)
        )
        return result.returncode, result.stdout, result.stderr

    except subprocess.TimeoutExpired as e:
        raise RuffExecutionError(f"ruff format执行超时: {e}")
    except Exception as e:
        raise RuffExecutionError(f"ruff format执行失败: {e}")


def parse_ruff_json_output(json_output: str) -> Dict[str, Any]:
    """解析ruff JSON输出

    Args:
        json_output: ruff JSON格式输出

    Returns:
        Dict[str, Any]: 解析后的结果
    """
    try:
        if not json_output.strip():
            return {"issues": [], "summary": {"error_count": 0, "warning_count": 0}}

        data = json.loads(json_output)

        # 统计错误和警告
        error_count = 0
        warning_count = 0
        fixable_count = 0

        for issue in data:
            if issue.get("fix", {}).get("applicability") == "automatic":
                fixable_count += 1

        # 按严重程度分类（简化分类，ruff主要使用error类型）
        error_count = len([i for i in data if i.get("severity") == "error"])

        return {
            "issues": data,
            "summary": {
                "total_count": len(data),
                "error_count": error_count,
                "warning_count": warning_count,
                "fixable_count": fixable_count
            }
        }

    except json.JSONDecodeError as e:
        raise RuffExecutionError(f"解析ruff JSON输出失败: {e}")


def convert_ruff_to_pyright_format(ruff_result: Dict[str, Any]) -> Dict[str, Any]:
    """将ruff结果转换为basedpyright格式

    Args:
        ruff_result: ruff检查结果

    Returns:
        Dict[str, Any]: basedpyright格式的结果
    """
    issues = ruff_result.get("issues", [])
    summary = ruff_result.get("summary", {})

    # 转换问题格式
    converted_files = {}

    for issue in issues:
        file_path = issue.get("filename", "")
        if not file_path:
            continue

        if file_path not in converted_files:
            converted_files[file_path] = {
                "file": file_path,
                "errors": [],
                "warnings": []
            }

        # 转换问题格式
        converted_issue = {
            "message": issue.get("message", ""),
            "severity": issue.get("severity", "error"),
            "code": issue.get("code", ""),
            "range": {
                "start": {
                    "line": issue.get("location", {}).get("row", 0) - 1,  # 转换为0基索引
                    "character": issue.get("location", {}).get("column", 0) - 1
                },
                "end": {
                    "line": issue.get("end_location", {}).get("row", 0) - 1,
                    "character": issue.get("end_location", {}).get("column", 0) - 1
                }
            },
            "rule": issue.get("code", ""),
            "fix": issue.get("fix", None),
            "tool": "ruff"
        }

        if issue.get("severity") == "error":
            converted_files[file_path]["errors"].append(converted_issue)
        else:
            converted_files[file_path]["warnings"].append(converted_issue)

    # 生成统计信息
    total_files = len(converted_files)
    total_errors = sum(len(f["errors"]) for f in converted_files.values())
    total_warnings = sum(len(f["warnings"]) for f in converted_files.values())

    return {
        "version": "ruff-integrated",
        "totalFiles": total_files,
        "errors": total_errors,
        "warnings": total_warnings,
        "time": "0s",  # ruff很快，但保持格式兼容
        "files": list(converted_files.values()),
        "summary": summary,
        "tool": "ruff"
    }


def get_ruff_rules_info() -> Dict[str, str]:
    """获取ruff规则信息

    Returns:
        Dict[str, str]: 规则代码到描述的映射
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "rule", "--all"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return {}

        rules = {}
        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                code, description = line.split(':', 1)
                rules[code.strip()] = description.strip()

        return rules

    except Exception:
        return {}