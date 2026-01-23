# autoBMAD-epic-automation Skill 安装脚本 (Windows PowerShell)

$SKILL_NAME = "autoBMAD-epic-automation"
$SKILL_FILE = "$SKILL_NAME.skill"

Write-Host "=== 安装 $SKILL_NAME Skill ===" -ForegroundColor Cyan
Write-Host ""

# 检查 skill 文件是否存在
if (-not (Test-Path ".claude/skills/$SKILL_FILE")) {
    Write-Host "❌ 错误: 找不到 skill 文件: .claude/skills/$SKILL_FILE" -ForegroundColor Red
    exit 1
}

# 验证 skill 文件
Write-Host "✓ Skill 文件存在: .claude/skills/$SKILL_FILE" -ForegroundColor Green

# 使用 Compress-Archive 或直接检查 ZIP 结构
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead(".claude/skills/$SKILL_FILE")
    $entry = $zip.Entries | Where-Object { $_.Name -eq "SKILL.md" }
    if ($entry) {
        Write-Host "✓ Skill 文件格式正确" -ForegroundColor Green
    } else {
        Write-Host "❌ 错误: Skill 文件格式无效" -ForegroundColor Red
        exit 1
    }
    $zip.Dispose()
} catch {
    Write-Host "❌ 错误: 无法读取 skill 文件" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Skill 安装验证通过!" -ForegroundColor Green
Write-Host ""
Write-Host "使用方法:" -ForegroundColor Yellow
Write-Host ""
Write-Host "完整工作流 (SM-Dev-QA + 质量门控):" -ForegroundColor Cyan
Write-Host "  PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/your-epic.md --verbose" -ForegroundColor White
Write-Host ""
Write-Host "独立质量门控 (Ruff + BasedPyright + Pytest):" -ForegroundColor Cyan
Write-Host "  PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-quality --verbose" -ForegroundColor White
Write-Host ""
Write-Host "快速开发（跳过质量门控）:" -ForegroundColor Cyan
Write-Host "  PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-epic docs/epics/your-epic.md --skip-quality --verbose" -ForegroundColor White
Write-Host ""
Write-Host "仅质量检查（跳过测试）:" -ForegroundColor Cyan
Write-Host "  PYTHONPATH=. python autoBMAD/epic_automation/epic_driver.py run-quality --skip-tests --verbose" -ForegroundColor White
