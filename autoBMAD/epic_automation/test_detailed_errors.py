#!/usr/bin/env python3
"""
验证详细错误信息的测试脚本

此脚本验证质量门禁系统能正确生成包含详细错误信息的JSON文件。
"""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from autoBMAD.epic_automation.controllers.quality_check_controller import QualityCheckController


async def async_return(value):
    """异步返回装饰器"""
    return value

def test_detailed_errors_in_result():
    """测试 QualityCheckController 是否在结果中包含详细错误信息"""
    print("测试 1: QualityCheckController 详细错误信息")

    # 创建模拟的 Agent
    mock_agent = MagicMock()
    mock_agent.execute = MagicMock()

    # 模拟执行结果（必须是异步的）
    async def mock_execute(source_dir):
        return {
            "status": "completed",
            "issues": [
                {
                    "filename": "test_file.py",
                    "line": 10,
                    "column": 5,
                    "code": "F401",
                    "message": "'os' imported but unused",
                    "severity": "error"
                },
                {
                    "filename": "test_file.py",
                    "line": 25,
                    "column": 20,
                    "code": "E501",
                    "message": "line too long",
                    "severity": "error"
                }
            ]
        }

    mock_agent.execute = mock_execute

    # 模拟解析错误方法
    mock_agent.parse_errors_by_file = MagicMock()
    mock_agent.parse_errors_by_file.return_value = {
        "test_file.py": [
            {
                "line": 10,
                "column": 5,
                "code": "F401",
                "message": "'os' imported but unused",
                "rule": "F401"
            },
            {
                "line": 25,
                "column": 20,
                "code": "E501",
                "message": "line too long",
                "rule": "E501"
            }
        ]
    }

    # 创建控制器
    controller = QualityCheckController(
        tool="ruff",
        agent=mock_agent,
        source_dir=".",
        max_cycles=1  # 使用较少的循环来快速测试
    )

    # 异步运行（使用事件循环）
    import asyncio
    result = asyncio.run(controller.run())

    # 验证结果
    print(f"  结果状态: {result['status']}")
    print(f"  工具: {result['tool']}")
    print(f"  循环次数: {result['cycles']}")

    # 检查是否包含详细错误信息
    assert "detailed_errors" in result, "结果中应该包含 detailed_errors 字段"

    detailed_errors = result["detailed_errors"]
    print(f"  详细错误信息: {json.dumps(detailed_errors, indent=2, ensure_ascii=False)}")

    # 验证详细错误信息结构
    assert "total_errors" in detailed_errors, "详细错误应该包含 total_errors"
    assert "by_file" in detailed_errors, "详细错误应该包含 by_file"

    assert detailed_errors["total_errors"] == 2, "总错误数应该是 2"
    assert "test_file.py" in detailed_errors["by_file"], "应该包含 test_file.py 的错误"

    file_errors = detailed_errors["by_file"]["test_file.py"]
    assert len(file_errors) == 2, "test_file.py 应该有 2 个错误"

    # 验证错误详情
    error1 = file_errors[0]
    assert error1["line"] == 10, "第一个错误的行号应该是 10"
    assert error1["column"] == 5, "第一个错误的列号应该是 5"
    assert error1["error_code"] == "F401", "第一个错误的代码应该是 F401"
    assert error1["message"] == "'os' imported but unused", "第一个错误的消息应该匹配"
    assert error1["rule"] == "F401", "第一个错误的规则应该是 F401"

    error2 = file_errors[1]
    assert error2["line"] == 25, "第二个错误的行号应该是 25"
    assert error2["column"] == 20, "第二个错误的列号应该是 20"
    assert error2["error_code"] == "E501", "第二个错误的代码应该是 E501"
    assert error2["message"] == "line too long", "第二个错误的消息应该匹配"
    assert error2["rule"] == "E501", "第二个错误的规则应该是 E501"

    print("  [PASS] QualityCheckController 详细错误信息测试通过\n")


def test_error_summary_json_includes_details():
    """测试错误汇总JSON是否包含详细错误信息"""
    print("测试 2: 错误汇总JSON包含详细错误信息")

    from autoBMAD.epic_automation.epic_driver import QualityGateOrchestrator

    # 创建临时目录
    import tempfile
    temp_dir = tempfile.mkdtemp()
    source_dir = Path(temp_dir) / "src"
    test_dir = Path(temp_dir) / "tests"
    source_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    # 创建协调器
    orchestrator = QualityGateOrchestrator(
        source_dir=str(source_dir),
        test_dir=str(test_dir),
        skip_quality=True,  # 跳过实际的质量检查
        skip_tests=True
    )

    # 模拟 results，包含详细错误信息
    orchestrator.results = {
        "ruff": {
            "result": {
                "status": "failed",
                "tool": "ruff",
                "cycles": 4,
                "max_cycles": 3,
                "final_error_files": ["test_file.py"],
                "detailed_errors": {
                    "total_errors": 2,
                    "by_file": {
                        "test_file.py": [
                            {
                                "line": 10,
                                "column": 5,
                                "error_code": "F401",
                                "message": "'os' imported but unused",
                                "rule": "F401"
                            },
                            {
                                "line": 25,
                                "column": 20,
                                "error_code": "E501",
                                "message": "line too long",
                                "rule": "E501"
                            }
                        ]
                    }
                }
            }
        }
    }

    # 创建质量警告
    issues = [
        {
            "tool": "ruff",
            "phase": "phase_1_ruff",
            "status": "max_cycles_exceeded",
            "cycles": 4,
            "max_cycles": 3,
            "remaining_files": ["test_file.py"]
        }
    ]

    # 生成错误汇总JSON
    json_path = orchestrator._write_error_summary_json("test_epic", issues)

    # 验证文件生成
    assert json_path is not None, "应该生成JSON文件"
    assert Path(json_path).exists(), "JSON文件应该存在"

    # 读取并验证JSON内容
    with open(json_path, 'r', encoding='utf-8') as f:
        error_data = json.load(f)

    print(f"  JSON文件路径: {json_path}")
    print(f"  Epic ID: {error_data['epic_id']}")

    # 验证基础结构
    assert "epic_id" in error_data
    assert "timestamp" in error_data
    assert "tools" in error_data

    # 验证工具错误包含详细错误信息
    assert len(error_data["tools"]) == 1, "应该有 1 个工具"

    ruff_tool = error_data["tools"][0]
    assert "error_details" in ruff_tool, "ruff工具应该包含 error_details 字段"

    error_details = ruff_tool["error_details"]
    print(f"  详细错误信息: {json.dumps(error_details, indent=2, ensure_ascii=False)}")

    # 验证详细错误信息结构
    assert error_details["total_errors"] == 2, "总错误数应该是 2"
    assert "test_file.py" in error_details["by_file"], "应该包含 test_file.py"

    file_errors = error_details["by_file"]["test_file.py"]
    assert len(file_errors) == 2, "test_file.py 应该有 2 个错误"

    # 清理
    import shutil
    shutil.rmtree(temp_dir)

    print("  [PASS] 错误汇总JSON包含详细错误信息测试通过\n")


if __name__ == "__main__":
    print("=" * 60)
    print("验证详细错误信息增强功能")
    print("=" * 60 + "\n")

    try:
        test_detailed_errors_in_result()
        test_error_summary_json_includes_details()

        print("=" * 60)
        print("所有测试通过！[PASS]")
        print("=" * 60)
        sys.exit(0)

    except AssertionError as e:
        print(f"\n[FAIL] 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
