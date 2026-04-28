"""
F3: SDK [ICON] Skills [ICON]

[ICON]SDK [ICON] Skills [ICON] cwd [ICON]

[ICON]
- SessionManager [ICON] options [ICON] setting_sources = ["project"]
- allowed_tools [ICON] "Skill"
- [ICON] orchestrator [ICON] independent agent [ICON] SessionManager [ICON]
  [ICON] pipeline [ICON] / output [ICON] work_dir
- SessionManager.__init__() [ICON] work_dir [ICON] _cwd [ICON] _output_dir [ICON] work_dir

[ICON]:
    python tools/docuswarm_f3_sdk_skills_debugger.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from autoBMAD.docuswarm.llm.session_manager import SessionManager


def test_session_manager_cwd():
    """[ICON] SessionManager [ICON] cwd [ICON]."""
    print("=" * 80)
    print("F3 SDK Skills [ICON]")
    print("=" * 80)
    
    # [ICON] orchestrator [ICON] SessionManager [ICON]
    output_dir = project_root / "output" / "pipe-123"
    
    print("\n[ICON] [ICON]:")
    print(f"  - [ICON]: {project_root}")
    print(f"  - Skills [ICON]: {project_root / '.claude' / 'skills'}")
    print(f"  - [ICON]: {output_dir}")
    
    # [ICON] skills [ICON]
    skills_dir = project_root / ".claude" / "skills"
    if skills_dir.exists():
        print(f"\n[ICON] Skills [ICON]")
        skill_files = list(skills_dir.glob("*/SKILL.md"))
        print(f"  - [ICON] skills: {len(skill_files)}")
        for skill_file in skill_files[:5]:  # [ICON]5[ICON]
            print(f"    - {skill_file.parent.name}")
    else:
        print(f"\n[ICON] Skills [ICON]: {skills_dir}")
    
    # [ICON] SessionManager [ICON] ([ICON] - [ICON] work_dir)
    print("\n" + "-" * 60)
    print("[ICON] [ICON] 1: [ICON] SessionManager ([ICON] work_dir)")
    print("-" * 60)
    
    sm_old = SessionManager(work_dir=output_dir, node_id="analyst")
    print(f"\n  cwd: {sm_old.cwd}")
    print(f"  output_dir: {sm_old.output_dir}")
    print(f"  cwd [ICON]: {'[OK] [ICON]' if sm_old.cwd == project_root else '[FAIL] [ICON]'}")
    
    is_cwd_correct_old = sm_old.cwd == project_root
    
    # [ICON] SessionManager [ICON] ([ICON] - [ICON] cwd [ICON] output_dir)
    print("\n" + "-" * 60)
    print("[ICON] [ICON] 2: [ICON] SessionManager (cwd + output_dir)")
    print("-" * 60)
    
    sm_new = SessionManager(
        cwd=project_root,
        output_dir=output_dir,
        node_id="analyst"
    )
    print(f"\n  cwd: {sm_new.cwd}")
    print(f"  output_dir: {sm_new.output_dir}")
    print(f"  cwd [ICON]: {'[OK] [ICON]' if sm_new.cwd == project_root else '[FAIL] [ICON]'}")
    
    is_cwd_correct_new = sm_new.cwd == project_root
    
    # [ICON] allowed_tools [ICON]
    print("\n" + "-" * 60)
    print("[ICON] [ICON] 3: allowed_tools [ICON]")
    print("-" * 60)
    
    # [ICON] _build_allowed_tools [ICON]
    allowed_tools = sm_new._build_allowed_tools()
    has_skill_tool = "Skill" in allowed_tools
    
    print(f"\n  allowed_tools: {allowed_tools}")
    print(f"  [ICON] 'Skill' [ICON]: {'[OK] [ICON]' if has_skill_tool else '[FAIL] [ICON]'}")
    
    return {
        "cwd_correct_old": is_cwd_correct_old,
        "cwd_correct_new": is_cwd_correct_new,
        "has_skill_tool": has_skill_tool,
        "project_root": str(project_root),
        "old_cwd": str(sm_old.cwd),
        "new_cwd": str(sm_new.cwd),
    }


def analyze_orchestrator_usage():
    """[ICON] orchestrator [ICON] SessionManager [ICON]."""
    print("\n" + "=" * 80)
    print("F3 Orchestrator [ICON]")
    print("=" * 80)
    
    orchestrator_file = project_root / "autoBMAD" / "docuswarm" / "pipeline" / "orchestrator.py"
    independent_file = project_root / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
    
    print("""
[ICON]:

1. Orchestrator._create_session_manager() (orchestrator.py:171-180)
   ```python
   session_manager = SessionManager(
       work_dir=work_dir,  # <- [ICON] output/pipe-xxx
       config=None,
   )
   ```
   [ICON]: [ICON] work_dir[ICON] cwd[ICON] cwd = work_dir

2. IndependentAgent._create_pipeline_session_manager() (independent.py:1072-1080)
   ```python
   return SessionManager(
       work_dir=work_dir,  # <- [ICON]
       agent_file=self._agent_file,
       config=...,
       node_id=node_id,
       file_dirs=file_dirs,
       search_dirs=search_dirs,
       tool_permissions=tool_permissions,
   )
   ```
   [ICON]: [ICON] work_dir[ICON]cwd [ICON]

3. SessionManager.__init__() (session_manager.py:100-107)
   ```python
   if work_dir is not None:
       self._cwd = cwd or work_dir
       self._output_dir = output_dir or work_dir
   else:
       self._cwd = cwd or Path.cwd()
       self._output_dir = output_dir or self._cwd
   ```
   [ICON]: [ICON] work_dir [ICON]cwd [ICON] output_dir [ICON] work_dir

SDK Skills [ICON]:
- setting_sources = ["project"] [ICON]SDK [ICON] cwd [ICON] .claude/skills/
- [ICON] cwd [ICON] output/pipe-xxx[ICON] .claude/skills/
- [ICON]: [ICON] Skills [ICON]

[ICON]:

[ICON] A: [ICON] Orchestrator [ICON] IndependentAgent
   1. Orchestrator [ICON] ([ICON])
   2. [ICON] SessionManager [ICON] cwd=project_root
   3. IndependentAgent [ICON]

[ICON] B: SessionManager [ICON]
   1. [ICON] SessionManager [ICON]
   2. [ICON] .claude/skills/ [ICON] pyproject.toml [ICON]
   3. [ICON] cwd [ICON]

[ICON] C: [ICON]
   1. [ICON] docuswarm.yaml [ICON] PROJECT_ROOT
   2. SessionManager [ICON] cwd
""")


def check_current_usage():
    """[ICON]."""
    print("\n" + "-" * 60)
    print("[ICON] [ICON]")
    print("-" * 60)
    
    orchestrator_file = project_root / "autoBMAD" / "docuswarm" / "pipeline" / "orchestrator.py"
    independent_file = project_root / "autoBMAD" / "docuswarm" / "agents" / "independent.py"
    
    issues_found = []
    
    # [ICON] orchestrator
    with open(orchestrator_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "SessionManager(work_dir=" in content and "cwd=" not in content.split("SessionManager")[1].split(")")[0]:
        issues_found.append("Orchestrator: SessionManager [ICON] cwd [ICON]")
        print("[ICON] Orchestrator: SessionManager [ICON] work_dir [ICON] cwd")
    else:
        print("? Orchestrator: [ICON]")
    
    # [ICON] independent agent
    with open(independent_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "SessionManager(work_dir=" in content and "cwd=" not in content.split("SessionManager")[1].split(")")[0]:
        issues_found.append("IndependentAgent: SessionManager [ICON] cwd [ICON]")
        print("[ICON] IndependentAgent: SessionManager [ICON] work_dir [ICON] cwd")
    else:
        print("? IndependentAgent: [ICON]")
    
    # [ICON] SessionManager [ICON] cwd [ICON]
    session_manager_file = project_root / "autoBMAD" / "docuswarm" / "llm" / "session_manager.py"
    with open(session_manager_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "cwd:" in content or "cwd=" in content:
        print("[ICON] SessionManager [ICON] cwd [ICON]")
    else:
        issues_found.append("SessionManager: [ICON] cwd [ICON]")
        print("[ICON] SessionManager [ICON] cwd [ICON]")
    
    return issues_found


def main():
    """[ICON]."""
    print("\n[DEBUG] DocuSwarm F3 SDK Skills [ICON]\n")
    
    results = test_session_manager_cwd()
    analyze_orchestrator_usage()
    issues = check_current_usage()
    
    # [ICON]
    print("\n" + "=" * 80)
    print("F3 [ICON]")
    print("=" * 80)
    print(f"""
[ICON]:
- [ICON] cwd [ICON]: {'[ICON] [ICON]' if results['cwd_correct_old'] else '[ICON] [ICON]'}
- [ICON] cwd [ICON]: {'[ICON] [ICON]' if results['cwd_correct_new'] else '[ICON] [ICON]'}
- allowed_tools [ICON] 'Skill': {'[ICON] [ICON]' if results['has_skill_tool'] else '[ICON] [ICON]'}

[ICON]:
- [ICON]: {results['project_root']}
- [ICON] cwd: {results['old_cwd']}
- [ICON] cwd: {results['new_cwd']}

[ICON]:
{chr(10).join(f"  - {issue}" for issue in issues) if issues else "  - [ICON]"}

[ICON]:
{"[ICON] [ICON] - [ICON] SessionManager [ICON]cwd [ICON]SDK [ICON] Skills [ICON]"
if not results['cwd_correct_old'] else 
"[ICON] cwd [ICON]"}

[ICON]:
- 01-skills-introduction-mechanism.md [ICON]"[ICON] Skills [ICON]"[ICON]
- 02-node-task-skill-mapping.md [ICON] skill_ref -> SDK Skills [ICON]"[ICON]"
- quick reference [ICON] SDK [ICON] Skill [ICON]

[ICON]: [ICON]"[ICON]"[ICON] cwd [ICON]
      [ICON] SDK [ICON]

[ICON]: HIGH
""")
    
    return 0 if results['cwd_correct_old'] else 1


if __name__ == "__main__":
    sys.exit(main())
