#!/bin/bash
# autoBMAD-epic-automation Skill 安装脚本

SKILL_NAME="autoBMAD-epic-automation"
SKILL_FILE="${SKILL_NAME}.skill"

echo "=== 安装 ${SKILL_NAME} Skill ==="
echo ""

# 检查 skill 文件是否存在
if [ ! -f ".claude/skills/${SKILL_FILE}" ]; then
    echo "❌ 错误: 找不到 skill 文件: .claude/skills/${SKILL_FILE}"
    exit 1
fi

# 验证 skill 文件
echo "✓ Skill 文件存在: .claude/skills/${SKILL_FILE}"
unzip -l ".claude/skills/${SKILL_FILE}" | grep -q "SKILL.md"
if [ $? -eq 0 ]; then
    echo "✓ Skill 文件格式正确"
else
    echo "❌ 错误: Skill 文件格式无效"
    exit 1
fi

echo ""
echo "✅ Skill 安装验证通过!"
echo ""
echo "使用方法:"
echo ""
echo "完整工作流 (SM-Dev-QA + 质量门控):"
echo "  PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/your-epic.md --verbose"
echo ""
echo "独立质量门控 (Ruff + BasedPyright + Pytest):"
echo "  PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-quality --verbose"
echo ""
echo "快速开发（跳过质量门控）:"
echo "  PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/your-epic.md --skip-quality --verbose"
echo ""
echo "仅质量检查（跳过测试）:"
echo "  PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-quality --skip-tests --verbose"
