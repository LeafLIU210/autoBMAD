# Quick cleanup script for Claude prompt files in basedpyright-workflow\prompts
# Usage: .\clear_claude_prompts.ps1

$projectRoot = Split-Path -Parent $PSScriptRoot
$promptsDir = Join-Path $projectRoot "prompts"

if (-not (Test-Path $promptsDir)) {
    Write-Host "Prompts directory not found: $promptsDir" -ForegroundColor Yellow
    exit 0
}

$promptPattern = Join-Path $promptsDir "prompt-*.txt"
$promptFiles = Get-ChildItem -Path $promptPattern -ErrorAction SilentlyContinue

if ($promptFiles.Count -eq 0) {
    Write-Host "No Claude prompt files found in $promptsDir" -ForegroundColor Green
    exit 0
}

Write-Host "Found $($promptFiles.Count) Claude prompt files:" -ForegroundColor Yellow
foreach ($file in $promptFiles) {
    Write-Host "  - $($file.Name)" -ForegroundColor Gray
}

$response = Read-Host "Delete these prompt files? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    foreach ($file in $promptFiles) {
        try {
            Remove-Item -Path $file.FullName -Force
            Write-Host "Deleted: $($file.Name)" -ForegroundColor Green
        } catch {
            Write-Host "Failed to delete $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Write-Host "Cleanup completed!" -ForegroundColor Green
} else {
    Write-Host "Cleanup cancelled." -ForegroundColor Yellow
}
