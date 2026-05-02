# SDK Security & Permission Boundary Deep Research Report

Generated from: /home/leafliu/autoBMAD/autoBMAD/docuswarm
Log file: /home/leafliu/autoBMAD/logs/docuswarm-2026-05-01.log

---

## SEC-1: SDK cwd 被提升到仓库父目录，权限边界比实际需要更宽
**Severity:** Medium

### Evidence
- Log shows sdk_cwd=output
- CONFIRMED: SDK cwd (output) is OUTSIDE the repo root (/home/leafliu/autoBMAD).
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/independent.py: Uses self.project_root.parent as repo_root. If project_root is /home/leafliu/autoBMAD/autoBMAD, parent is /home/leafliu.
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/llm/session_manager.py: SessionManager receives and uses cwd parameter.

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/independent.py**
```python
        # P0 Fix: Use repo root for directory resolution, not autoBMAD subdirectory
        # project_root currently points to autoBMAD/, but node config paths are relative to repo root
        repo_root = (
            self.project_root.parent if self.project_root.name == "autoBMAD" else self.project_root
        )

        # Prepare permission directories (absolute paths from repo root)
        file_dirs = [
            str(repo_root / d)
            for d in node_config.tool_permissions.file_permissions.allowed_read_dirs
        ]
```

**Recommendation:** 明确区分: repo_root=/home/leafliu/autoBMAD, package_root=/home/leafliu/autoBMAD/autoBMAD, SDK cwd 默认应为 repo_root。增加 snapshot 测试覆盖这四个路径。

---

## SEC-2: auto_approve_tools: true 与 yolo=True 需要持续依赖 allowed_tools 正确生成
**Severity:** Medium

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/agents/independent.py: Found 4 occurrences of yolo=True in agent code.

**Recommendation:** 若 allowed_tools_generation_failed 发生，必须确认默认 allowed_tools 不会变宽。建议增加安全审计日志记录实际生效的 allowed_tools 列表。

---

## SEC-3: PathValidator 使用 prefix 检查，建议增加 resolve()+is_relative_to()
**Severity:** Low

### Evidence
- /home/leafliu/autoBMAD/autoBMAD/docuswarm/tools/file_tools_sdk.py: Uses startswith() for path validation. This can be bypassed with path traversal in some edge cases.

### Code Snippets
**/home/leafliu/autoBMAD/autoBMAD/docuswarm/tools/file_tools_sdk.py**
```python
            resolved_prefix = resolved_path.rstrip(os.sep) + os.sep

            if resolved_prefix.startswith(allowed_prefix) or resolved_path == allowed_dir:
                return resolved_path

```

**Recommendation:** 额外使用 Path.resolve().is_relative_to() 简化并降低跨平台歧义。

---
