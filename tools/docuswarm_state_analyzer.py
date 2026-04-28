#!/usr/bin/env python3
"""DocuSwarm 状态持久化分析工具 (F1 Research Tool).

该工具用于深度分析 state_json 与 checkpoint 的状态差异，
帮助诊断状态持久化链路是否闭环。

用法:
    python tools/docuswarm_state_analyzer.py --db docuswarm.db
    python tools/docuswarm_state_analyzer.py --pipeline <pipeline_id>
    python tools/docuswarm_state_analyzer.py --check-all
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


def analyze_database(db_path: str) -> dict[str, Any]:
    """分析数据库状态.
    
    Returns:
        分析结果字典
    """
    results = {
        "db_path": db_path,
        "db_exists": Path(db_path).exists(),
        "pipelines_count": 0,
        "checkpoints_count": 0,
        "state_completeness_issues": [],
        "pipelines": [],
    }
    
    if not results["db_exists"]:
        return results
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # 统计 pipelines
        cursor = conn.execute("SELECT COUNT(*) as count FROM pipelines")
        results["pipelines_count"] = cursor.fetchone()["count"]
        
        # 统计 checkpoints
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM sqlite_master "
            "WHERE type='table' AND name='checkpoints'"
        )
        if cursor.fetchone()["count"] > 0:
            cursor = conn.execute("SELECT COUNT(*) as count FROM checkpoints")
            results["checkpoints_count"] = cursor.fetchone()["count"]
        
        # 分析每个 pipeline
        cursor = conn.execute(
            "SELECT pipeline_id, subject, status, current_node, state_json "
            "FROM pipelines ORDER BY created_at DESC LIMIT 10"
        )
        
        required_fields = [
            "pipeline_id", "subject_context", "current_node",
            "completed_nodes", "deliverables", "questions",
            "evaluations", "node_iterations", "session_ids",
            "session_metadata", "current_node_session_id",
            "status", "error", "shared_context",
        ]
        
        for row in cursor.fetchall():
            pipeline_info = {
                "pipeline_id": row["pipeline_id"],
                "subject": row["subject"],
                "status": row["status"],
                "current_node": row["current_node"],
            }
            
            # 分析 state_json
            state_json = row["state_json"]
            if state_json:
                try:
                    state = json.loads(state_json)
                    pipeline_info["state_keys"] = list(state.keys())
                    
                    # 检查缺失字段
                    missing_fields = [
                        f for f in required_fields
                        if f not in state
                    ]
                    if missing_fields:
                        pipeline_info["missing_fields"] = missing_fields
                        results["state_completeness_issues"].append({
                            "pipeline_id": row["pipeline_id"],
                            "missing_fields": missing_fields,
                        })
                    
                    # 检查 shared_context
                    if "shared_context" in state:
                        pipeline_info["has_shared_context"] = True
                        pipeline_info["shared_context_keys"] = list(
                            state["shared_context"].keys()
                        ) if isinstance(state["shared_context"], dict) else []
                    else:
                        pipeline_info["has_shared_context"] = False
                        
                except json.JSONDecodeError as e:
                    pipeline_info["state_json_error"] = str(e)
            else:
                pipeline_info["state_json_empty"] = True
            
            results["pipelines"].append(pipeline_info)
        
        conn.close()
        
    except Exception as e:
        results["error"] = str(e)
    
    return results


def analyze_pipeline_detail(db_path: str, pipeline_id: str) -> dict[str, Any]:
    """分析特定 pipeline 的详细信息.
    
    Args:
        db_path: 数据库路径
        pipeline_id: Pipeline ID
        
    Returns:
        详细分析结果
    """
    results = {
        "pipeline_id": pipeline_id,
        "found": False,
        "state_json": None,
        "checkpoint": None,
        "differences": [],
    }
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # 获取 pipeline 信息
        cursor = conn.execute(
            "SELECT * FROM pipelines WHERE pipeline_id = ?",
            (pipeline_id,)
        )
        row = cursor.fetchone()
        
        if row:
            results["found"] = True
            results["pipeline_info"] = {
                "subject": row["subject"],
                "status": row["status"],
                "current_node": row["current_node"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            
            # 解析 state_json
            if row["state_json"]:
                try:
                    results["state_json"] = json.loads(row["state_json"])
                except json.JSONDecodeError as e:
                    results["state_json_error"] = str(e)
        
        # 获取 checkpoints
        cursor = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='checkpoints'"
        )
        if cursor.fetchone():
            cursor = conn.execute(
                "SELECT * FROM checkpoints WHERE thread_id LIKE ?",
                (f"%{pipeline_id}%",)
            )
            checkpoints = []
            for row in cursor.fetchall():
                try:
                    checkpoint_data = json.loads(row["checkpoint"])
                    checkpoints.append({
                        "thread_id": row["thread_id"],
                        "checkpoint_id": row["checkpoint_id"],
                        "parent_checkpoint_id": row["parent_checkpoint_id"],
                        "data_keys": list(checkpoint_data.keys()) if isinstance(checkpoint_data, dict) else [],
                    })
                except json.JSONDecodeError:
                    checkpoints.append({
                        "thread_id": row["thread_id"],
                        "checkpoint_id": row["checkpoint_id"],
                        "error": "Failed to parse checkpoint",
                    })
            results["checkpoints"] = checkpoints
        
        conn.close()
        
    except Exception as e:
        results["error"] = str(e)
    
    return results


def print_analysis(results: dict[str, Any]) -> None:
    """打印分析结果."""
    print("=" * 60)
    print("DocuSwarm 状态持久化分析报告 (F1 Research Tool)")
    print("=" * 60)
    print()
    
    print(f"数据库路径: {results['db_path']}")
    print(f"数据库存在: {'✅' if results['db_exists'] else '❌'}")
    print()
    
    if not results["db_exists"]:
        print("❌ 数据库不存在")
        return
    
    print(f"Pipelines 数量: {results['pipelines_count']}")
    print(f"Checkpoints 数量: {results['checkpoints_count']}")
    print()
    
    # 完整性问题
    if results["state_completeness_issues"]:
        print("⚠️  State Json 完整性问题:")
        for issue in results["state_completeness_issues"]:
            print(f"  - Pipeline {issue['pipeline_id'][:20]}...")
            print(f"    缺失字段: {', '.join(issue['missing_fields'])}")
        print()
    else:
        print("✅ 未发现 state_json 完整性问题")
        print()
    
    # Pipeline 列表
    print("最近 10 个 Pipeline:")
    print("-" * 60)
    for p in results["pipelines"]:
        print(f"  ID: {p['pipeline_id'][:40]}...")
        print(f"  主题: {p.get('subject', 'N/A')}")
        print(f"  状态: {p.get('status', 'N/A')}")
        print(f"  当前节点: {p.get('current_node', 'N/A')}")
        
        if "state_keys" in p:
            print(f"  State 字段: {len(p['state_keys'])} 个")
            if "missing_fields" in p:
                print(f"  ⚠️  缺失字段: {', '.join(p['missing_fields'])}")
        
        if p.get("has_shared_context"):
            print(f"  ✅ 有 shared_context")
            print(f"     键: {p.get('shared_context_keys', [])}")
        elif "has_shared_context" in p:
            print(f"  ❌ 无 shared_context")
        
        print()


def print_pipeline_detail(results: dict[str, Any]) -> None:
    """打印 Pipeline 详细分析."""
    print("=" * 60)
    print(f"Pipeline 详细分析: {results['pipeline_id']}")
    print("=" * 60)
    print()
    
    if not results["found"]:
        print("❌ Pipeline 未找到")
        return
    
    info = results["pipeline_info"]
    print(f"主题: {info['subject']}")
    print(f"状态: {info['status']}")
    print(f"当前节点: {info['current_node']}")
    print(f"创建时间: {info['created_at']}")
    print(f"更新时间: {info['updated_at']}")
    print()
    
    if results["state_json"]:
        print("State JSON 内容:")
        print("-" * 60)
        print(json.dumps(results["state_json"], indent=2, ensure_ascii=False))
        print()
    
    if "checkpoints" in results:
        print(f"Checkpoints: {len(results['checkpoints'])} 个")
        for cp in results["checkpoints"]:
            print(f"  - ID: {cp.get('checkpoint_id', 'N/A')}")
            print(f"    Thread: {cp.get('thread_id', 'N/A')}")
            print(f"    数据键: {cp.get('data_keys', [])}")
        print()


def main() -> int:
    """主函数."""
    parser = argparse.ArgumentParser(
        description="DocuSwarm 状态持久化分析工具"
    )
    parser.add_argument(
        "--db",
        default="docuswarm.db",
        help="数据库路径 (默认: docuswarm.db)",
    )
    parser.add_argument(
        "--pipeline",
        help="分析特定 pipeline ID",
    )
    parser.add_argument(
        "--check-all",
        action="store_true",
        help="检查所有 pipeline 的完整性",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式",
    )
    
    args = parser.parse_args()
    
    if args.pipeline:
        results = analyze_pipeline_detail(args.db, args.pipeline)
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print_pipeline_detail(results)
    else:
        results = analyze_database(args.db)
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print_analysis(results)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
