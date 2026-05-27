"""
bmad_dependency_scanner.py

深度扫描 autoBMAD 包对 `.bmad-core/`（BMAD v4 安装）和 `_bmad/`（BMAD v6 安装）
两个外部目录的依赖情况。

扫描维度：
1. 目录存在性与基本结构画像
2. 源码（autoBMAD/**/*.py）中的字符串/路径引用，区分：
   - Python 文件路径硬编码（Path/open/read_text 等）
   - Claude CLI @ 引用（如 @.bmad-core\\agents\\sm.md）
   - 默认参数（如 tasks_dir=".bmad-core/tasks"）
3. 配置 YAML/TOML/JSON 中的引用
4. 文档（*.md）中的引用（仅统计，不视为代码依赖）
5. 引用目标的真实存在性校验（dead reference 检测）
6. 引用方向反向：_bmad 与 .bmad-core 中是否反向依赖 autoBMAD

输出：
- 终端打印分级摘要
- 可选 JSON 报告：--output <path>

用法：
    python tools/bmad_dependency_scanner.py
    python tools/bmad_dependency_scanner.py --output .tmp/bmad_dependency_report.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTOBMAD_DIR = PROJECT_ROOT / "autoBMAD"
BMAD_CORE_DIR = PROJECT_ROOT / ".bmad-core"
BMAD_V6_DIR = PROJECT_ROOT / "_bmad"

CODE_EXTS = {".py"}
CONFIG_EXTS = {".yaml", ".yml", ".toml", ".json"}
DOC_EXTS = {".md", ".rst", ".txt"}
SKIP_DIRS = {"__pycache__", ".pytest-temp", ".pytest_cache", "htmlcov",
             ".venv", "node_modules", ".git", ".ruff_cache"}

# 引用模式
BMAD_CORE_PATTERNS = [
    re.compile(r"\.bmad-core[\\/][\w\-./\\]+", re.IGNORECASE),
    re.compile(r"@\.bmad-core[\\\\/][\w\-.\\\\/]+", re.IGNORECASE),
]
BMAD_V6_PATTERNS = [
    # 排除 .bmad-core/_bmad-output 类目录，仅匹配独立 _bmad 路径段
    re.compile(r"(?<![\w\-])_bmad[\\/][\w\-./\\]+"),
]

# Python 中表征"运行时使用"的关键词（优先级权重）
RUNTIME_KEYWORDS = (
    "Path(", "open(", "read_text", "read_bytes", "load(", "loads(",
    "exists()", "is_file()", "is_dir()", "iterdir(", "rglob(", "glob(",
)
PROMPT_KEYWORDS = ("@.bmad-core", "@_bmad", "f'@", 'f"@', "prompt", "Prompt")


@dataclass
class Reference:
    file: str            # 相对项目根的路径
    line: int
    snippet: str         # 截断后的源行
    target: str          # 命中的字符串（如 .bmad-core/tasks/sm.md）
    target_dir: str      # ".bmad-core" 或 "_bmad"
    kind: str            # "code-runtime" | "code-prompt" | "code-default-arg" | "config" | "doc"


@dataclass
class DirProfile:
    path: str
    exists: bool
    file_count: int = 0
    top_level: list[str] = field(default_factory=list)
    size_kb: float = 0.0


@dataclass
class Report:
    project_root: str
    bmad_core: DirProfile
    bmad_v6: DirProfile
    autobmad_refs_to_bmad_core: list[Reference] = field(default_factory=list)
    autobmad_refs_to_bmad_v6: list[Reference] = field(default_factory=list)
    reverse_refs_in_bmad_core: list[Reference] = field(default_factory=list)
    reverse_refs_in_bmad_v6: list[Reference] = field(default_factory=list)
    dead_targets_bmad_core: list[str] = field(default_factory=list)
    dead_targets_bmad_v6: list[str] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


def profile_dir(p: Path) -> DirProfile:
    if not p.exists():
        return DirProfile(path=str(p), exists=False)
    files = [f for f in p.rglob("*") if f.is_file()]
    size = sum(f.stat().st_size for f in files) / 1024
    top = sorted({entry.name for entry in p.iterdir()})
    return DirProfile(
        path=str(p.relative_to(PROJECT_ROOT)),
        exists=True,
        file_count=len(files),
        top_level=top,
        size_kb=round(size, 1),
    )


def iter_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return out


def classify_kind(ext: str, line: str) -> str:
    if ext == ".py":
        if any(kw in line for kw in PROMPT_KEYWORDS):
            return "code-prompt"
        if any(kw in line for kw in RUNTIME_KEYWORDS):
            return "code-runtime"
        if "=" in line and any(seg in line for seg in (
            ".bmad-core", "_bmad/", "_bmad\\")):
            return "code-default-arg"
        return "code-other"
    if ext in CONFIG_EXTS:
        return "config"
    return "doc"


def scan_file(file: Path) -> list[Reference]:
    refs: list[Reference] = []
    try:
        text = file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return refs
    rel = str(file.relative_to(PROJECT_ROOT))
    ext = file.suffix.lower()
    for lineno, line in enumerate(text.splitlines(), 1):
        for pat in BMAD_CORE_PATTERNS:
            for m in pat.finditer(line):
                refs.append(Reference(
                    file=rel, line=lineno, snippet=line.strip()[:200],
                    target=m.group(0), target_dir=".bmad-core",
                    kind=classify_kind(ext, line),
                ))
        for pat in BMAD_V6_PATTERNS:
            for m in pat.finditer(line):
                refs.append(Reference(
                    file=rel, line=lineno, snippet=line.strip()[:200],
                    target=m.group(0), target_dir="_bmad",
                    kind=classify_kind(ext, line),
                ))
    return refs


def normalize_target(target: str) -> Path:
    """将 '@.bmad-core\\agents\\sm.md' 等归一为 PROJECT_ROOT 相对路径。"""
    raw = target.lstrip("@").replace("\\", "/")
    # 去除尾随标点（引号、括号、逗号）
    raw = raw.rstrip("'\",) ;}")
    return PROJECT_ROOT / raw


def check_dead(refs: list[Reference]) -> list[str]:
    seen: dict[str, bool] = {}
    for r in refs:
        if r.target in seen:
            continue
        # 含模板占位符则跳过 ({task_name})
        if "{" in r.target and "}" in r.target:
            seen[r.target] = True
            continue
        p = normalize_target(r.target)
        seen[r.target] = p.exists()
    return [t for t, ok in seen.items() if not ok]


def build_summary(report: Report) -> dict[str, Any]:
    def by_kind(refs: list[Reference]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for r in refs:
            counts[r.kind] = counts.get(r.kind, 0) + 1
        return counts

    def top_files(refs: list[Reference], n: int = 8) -> list[dict[str, Any]]:
        agg: dict[str, int] = {}
        for r in refs:
            agg[r.file] = agg.get(r.file, 0) + 1
        return [{"file": f, "hits": c}
                for f, c in sorted(agg.items(), key=lambda x: -x[1])[:n]]

    return {
        "autobmad_to_bmad_core": {
            "total": len(report.autobmad_refs_to_bmad_core),
            "by_kind": by_kind(report.autobmad_refs_to_bmad_core),
            "top_files": top_files(report.autobmad_refs_to_bmad_core),
        },
        "autobmad_to_bmad_v6": {
            "total": len(report.autobmad_refs_to_bmad_v6),
            "by_kind": by_kind(report.autobmad_refs_to_bmad_v6),
            "top_files": top_files(report.autobmad_refs_to_bmad_v6),
        },
        "reverse_bmad_core_to_autobmad": len(report.reverse_refs_in_bmad_core),
        "reverse_bmad_v6_to_autobmad": len(report.reverse_refs_in_bmad_v6),
        "dead_targets": {
            ".bmad-core": report.dead_targets_bmad_core,
            "_bmad": report.dead_targets_bmad_v6,
        },
    }


def reverse_scan(root: Path) -> list[Reference]:
    """检测 root（.bmad-core 或 _bmad）中是否反向引用 autoBMAD/docuswarm。"""
    if not root.exists():
        return []
    refs: list[Reference] = []
    pattern = re.compile(r"autoBMAD|docuswarm|epic_automation")
    for f in iter_files(root):
        if f.suffix.lower() not in (CODE_EXTS | CONFIG_EXTS | DOC_EXTS):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rel = str(f.relative_to(PROJECT_ROOT))
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in pattern.finditer(line):
                refs.append(Reference(
                    file=rel, line=lineno, snippet=line.strip()[:200],
                    target=m.group(0), target_dir=root.name,
                    kind="config" if f.suffix.lower() in CONFIG_EXTS else "doc",
                ))
    return refs


def run() -> Report:
    report = Report(
        project_root=str(PROJECT_ROOT),
        bmad_core=profile_dir(BMAD_CORE_DIR),
        bmad_v6=profile_dir(BMAD_V6_DIR),
    )

    forward: list[Reference] = []
    for f in iter_files(AUTOBMAD_DIR):
        if f.suffix.lower() not in (CODE_EXTS | CONFIG_EXTS | DOC_EXTS):
            continue
        forward.extend(scan_file(f))

    report.autobmad_refs_to_bmad_core = [r for r in forward if r.target_dir == ".bmad-core"]
    report.autobmad_refs_to_bmad_v6 = [r for r in forward if r.target_dir == "_bmad"]

    report.reverse_refs_in_bmad_core = reverse_scan(BMAD_CORE_DIR)
    report.reverse_refs_in_bmad_v6 = reverse_scan(BMAD_V6_DIR)

    report.dead_targets_bmad_core = check_dead(report.autobmad_refs_to_bmad_core)
    report.dead_targets_bmad_v6 = check_dead(report.autobmad_refs_to_bmad_v6)

    report.summary = build_summary(report)
    return report


def print_human(report: Report) -> None:
    print("=" * 78)
    print("autoBMAD 对 .bmad-core / _bmad 的依赖扫描报告")
    print("=" * 78)
    print(f"project_root: {report.project_root}\n")

    print(f"[目录画像] .bmad-core: exists={report.bmad_core.exists}, "
          f"files={report.bmad_core.file_count}, size={report.bmad_core.size_kb} KB")
    if report.bmad_core.top_level:
        print(f"  top-level: {report.bmad_core.top_level}")
    print(f"[目录画像] _bmad     : exists={report.bmad_v6.exists}, "
          f"files={report.bmad_v6.file_count}, size={report.bmad_v6.size_kb} KB")
    if report.bmad_v6.top_level:
        print(f"  top-level: {report.bmad_v6.top_level}")
    print()

    s = report.summary
    print("[正向引用] autoBMAD → .bmad-core")
    print(f"  total = {s['autobmad_to_bmad_core']['total']}")
    print(f"  by_kind = {s['autobmad_to_bmad_core']['by_kind']}")
    for tf in s["autobmad_to_bmad_core"]["top_files"]:
        print(f"    - {tf['file']}: {tf['hits']}")
    print()

    print("[正向引用] autoBMAD → _bmad")
    print(f"  total = {s['autobmad_to_bmad_v6']['total']}")
    print(f"  by_kind = {s['autobmad_to_bmad_v6']['by_kind']}")
    for tf in s["autobmad_to_bmad_v6"]["top_files"]:
        print(f"    - {tf['file']}: {tf['hits']}")
    print()

    print(f"[反向引用] .bmad-core → autoBMAD: {s['reverse_bmad_core_to_autobmad']}")
    print(f"[反向引用] _bmad → autoBMAD     : {s['reverse_bmad_v6_to_autobmad']}")
    print()

    if s["dead_targets"][".bmad-core"]:
        print("[死引用] .bmad-core 内不存在的目标:")
        for t in s["dead_targets"][".bmad-core"]:
            print(f"    ✗ {t}")
    else:
        print("[死引用] .bmad-core 全部命中（或被 {占位符} 跳过）")
    if s["dead_targets"]["_bmad"]:
        print("[死引用] _bmad 内不存在的目标:")
        for t in s["dead_targets"]["_bmad"]:
            print(f"    ✗ {t}")
    else:
        print("[死引用] _bmad 全部命中（或被 {占位符} 跳过）")
    print()

    print("[详细引用 (前 30 条)]")
    all_refs = (report.autobmad_refs_to_bmad_core + report.autobmad_refs_to_bmad_v6)
    for r in all_refs[:30]:
        print(f"  {r.target_dir:>11s} | {r.kind:<18s} | {r.file}:{r.line} | {r.target}")
    if len(all_refs) > 30:
        print(f"  ... 余 {len(all_refs) - 30} 条略")


def to_jsonable(report: Report) -> dict[str, Any]:
    d = asdict(report)
    return d


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=str, default=None,
                        help="可选 JSON 报告输出路径")
    args = parser.parse_args()

    report = run()
    print_human(report)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(to_jsonable(report), ensure_ascii=False, indent=2),
                       encoding="utf-8")
        print(f"\n[已写入] {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
