# PowerShell Script: Process project error files one by one
# Designed for use within project folders
# Updated: 2025-12-17
# Description: Auto-discovers error files and processes them with Claude Code

param(
    [string]$ErrorsFile = $null,      # Auto-discovery by default
    [int]$IntervalSeconds = 60,
    [switch]$TestMode = $false,       # For testing functions without running main script
    [switch]$IncludeRuff = $false,    # Include ruff errors in processing
    [switch]$PreferRuff = $false,     # Prefer ruff fixes over basedpyright when conflicts exist
    [switch]$ApplyRuffFixes = $false,  # Apply ruff automatic fixes before Claude processing
    [string]$ProjectPath = "."         # Project root path (default: current directory)
)

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Determine project and output directories
$ProjectRoot = if ($ProjectPath -eq ".") { Get-Location } else { Resolve-Path $ProjectPath }

# Try to read .bpr.json for results directory
$BprConfigPath = Join-Path $ProjectRoot ".bpr.json"
$OutputDir = Join-Path $ProjectRoot ".bpr"  # Default output directory

if (Test-Path $BprConfigPath) {
    try {
        $config = Get-Content -Path $BprConfigPath -Encoding UTF8 | ConvertFrom-Json
        if ($config.results_directory) {
            $ResultsDir = Join-Path $ProjectRoot $config.results_directory
            Write-Host "Using configured results directory: $($config.results_directory)"
        } else {
            $ResultsDir = Join-Path $OutputDir "results"
        }
    } catch {
        Write-Host "Warning: Failed to read .bpr.json, using default paths: $_" -ForegroundColor Yellow
        $ResultsDir = Join-Path $OutputDir "results"
    }
} else {
    $ResultsDir = Join-Path $OutputDir "results"
}

# Helper function for colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [switch]$NoTimestamp = $false
    )
    $ts = if ($NoTimestamp) { "" } else { Get-Date -Format "yyyy-MM-dd HH:mm:ss" }
    if ($ts) {
        $ts = "[$ts] "
    }
    Write-Host "$ts$Message" -ForegroundColor $Color
}

# Log file path
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $OutputDir "fix_project_errors_$timestamp.log"

# Write log function (with color support for console)
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMsg = "[$ts] $Message"

    # Write to console with color
    $color = switch ($Level.ToUpper()) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO_RUFF" { "Cyan" }
        "INFO_PYRIGHT" { "Magenta" }
        default { "White" }
    }
    Write-Host $logMsg -ForegroundColor $color

    # Write to log file (plain text)
    Add-Content -Path $logFile -Value $logMsg -Encoding UTF8
}

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
    Write-Log "Created output directory: $OutputDir" "INFO"
}

if (-not (Test-Path $ResultsDir)) {
    New-Item -Path $ResultsDir -ItemType Directory -Force | Out-Null
    Write-Log "Created results directory: $ResultsDir" "INFO"
}

# Find latest error file function (supports both basedpyright and unified error files)
function Find-LatestErrorFile {
    param(
        [string]$ResultsDir,
        [switch]$IncludeRuff
    )

    if (-not (Test-Path $ResultsDir)) {
        return $null
    }

    # Priority order: unified errors > basedpyright errors
    if ($IncludeRuff) {
        # Look for unified error files first
        $unifiedErrorFiles = Get-ChildItem -Path $ResultsDir -Filter "unified_errors_only_*.json" |
                              Sort-Object LastWriteTime -Descending

        if ($unifiedErrorFiles.Count -gt 0) {
            return $unifiedErrorFiles[0].FullName
        }
    }

    # Fall back to basedpyright error files
    $errorFiles = Get-ChildItem -Path $ResultsDir -Filter "basedpyright_errors_only_*.json" |
                  Sort-Object LastWriteTime -Descending

    if ($errorFiles.Count -eq 0) {
        return $null
    }

    return $errorFiles[0].FullName
}

# Apply ruff automatic fixes function
function Invoke-RuffAutoFix {
    param(
        [string]$ProjectRoot,
        [string]$SourceDir = $null
    )

    try {
        Write-Log "Applying ruff automatic fixes..." "INFO_RUFF"

        # Check if ruff is installed
        $ruffCheck = & python -m ruff --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Ruff not installed, skipping automatic fixes" "WARN"
            return $false
        }

        Write-Log "Found ruff: $ruffCheck" "INFO_RUFF"

        # Use project root as source directory if not specified
        $fixSourceDir = if ($SourceDir) { $SourceDir } else { $ProjectRoot }

        # Apply ruff fixes
        Push-Location $fixSourceDir
        $fixResult = & python -m ruff check --fix --output-format=full 2>&1
        $fixExitCode = $LASTEXITCODE
        Pop-Location

        if ($fixExitCode -eq 0) {
            Write-Log "Ruff fixes applied successfully" "SUCCESS"
            if ($fixResult) {
                Write-Log "Ruff output: $fixResult" "INFO_RUFF"
            }
            return $true
        } else {
            Write-Log "Ruff fixes completed with warnings" "WARN"
            if ($fixResult) {
                Write-Log "Ruff output: $fixResult" "INFO_RUFF"
            }
            return $true  # Still consider it successful if some issues remain
        }

    } catch {
        Write-Log "Error applying ruff fixes: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Check if a Python file exists and get its content
function Get-PythonFileContent {
    param(
        [string]$FilePath,
        [string]$ProjectRoot
    )

    # Check if FilePath is already absolute
    if ([System.IO.Path]::IsPathRooted($FilePath)) {
        $fullPath = $FilePath
    } else {
        $fullPath = Join-Path $ProjectRoot $FilePath
    }

    if (-not (Test-Path $fullPath)) {
        Write-Log "File not found: $fullPath" "ERROR"
        return $null
    }

    try {
        return Get-Content -Path $fullPath -Encoding UTF8 -Raw
    } catch {
        Write-Log "Error reading file $fullPath : $($_.Exception.Message)" "ERROR"
        return $null
    }
}

# Generate Claude prompt for fixing errors
function New-ClaudePrompt {
    param(
        [string]$FilePath,
        [array]$Errors,
        [string]$FileContent,
        [hashtable]$ErrorsByTool,
        [switch]$PreferRuff
    )

    # Group errors by tool
    $basedpyrightErrors = $Errors | Where-Object { $_.tool -eq "basedpyright" -or -not $_.tool }
    $ruffErrors = $Errors | Where-Object { $_.tool -eq "ruff" }

    $prompt = @"
Please fix the Python code in the following file: $FilePath

"@

    if ($basedpyrightErrors.Count -gt 0) {
        $prompt += @"

BasedPyright type errors ($($basedpyrightErrors.Count)):
"@
        foreach ($error in $basedpyrightErrors) {
            $lineNum = $error.line
            $colNum = $error.column
            $message = $error.message
            $rule = $error.rule
            $prompt += "  Line $lineNum, Col ${colNum}: [$rule] $message`n"
        }
    }

    if ($ruffErrors.Count -gt 0) {
        $prompt += @"

Ruff lint errors ($($ruffErrors.Count)):
"@
        foreach ($error in $ruffErrors) {
            $lineNum = $error.line
            $colNum = $error.column
            $message = $error.message
            $rule = $error.rule
            $fixable = if ($error.fixable) { " (auto-fixable)" } else { "" }
            $prompt += "  Line $lineNum, Col ${colNum}: [$rule]$fixable $message`n"
        }
    }

    # Add conflict resolution guidance
    if ($basedpyrightErrors.Count -gt 0 -and $ruffErrors.Count -gt 0) {
        $prompt += @"

Conflict Resolution Guidance:
- Type errors (BasedPyright) have higher priority than style issues (Ruff)
- If BasedPyright and Ruff suggest different fixes for the same issue, prefer BasedPyright's approach
- Ruff auto-fixable issues should be addressed automatically when possible
"@

        if ($PreferRuff) {
            $prompt += "- User preference: Prefer Ruff fixes over BasedPyright when both are available`n"
        }
    }

    $prompt += @"

Requirements:
1. Fix all the errors listed above
2. Maintain code functionality and readability
3. Follow Python best practices
4. Preserve existing code style where possible
5. Add comments explaining complex fixes if necessary

Please provide the complete fixed file content.
"@

    return $prompt
}

# Clean up Claude prompt files from prompts directory
function Clear-ClaudePromptFiles {
    param(
        [switch]$WhatIf,
        [string]$ProjectPath = "."
    )

    $ProjectRoot = if ($ProjectPath -eq ".") { Get-Location } else { Resolve-Path $ProjectPath }
    $promptsDir = Join-Path $ProjectRoot "basedpyright-workflow\prompts"
    $promptPattern = Join-Path $promptsDir "prompt-*.txt"

    if (-not (Test-Path $promptsDir)) {
        Write-Log "Prompts directory not found: $promptsDir" "INFO"
        return
    }

    $promptFiles = Get-ChildItem -Path $promptPattern -ErrorAction SilentlyContinue

    if ($promptFiles.Count -eq 0) {
        Write-Log "No Claude prompt files found to clean up in $promptsDir" "INFO"
        return
    }

    Write-Log "Found $($promptFiles.Count) Claude prompt files" "INFO"

    foreach ($file in $promptFiles) {
        try {
            if ($WhatIf) {
                Write-Log "[WhatIf] Would delete: $($file.FullName)" "INFO"
            } else {
                Remove-Item -Path $file.FullName -Force
                Write-Log "Deleted prompt file: $($file.FullName)" "INFO"
            }
        } catch {
            Write-Log "Failed to delete $($file.FullName): $($_.Exception.Message)" "WARN"
        }
    }

    if (-not $WhatIf) {
        Write-Log "Prompt file cleanup completed" "SUCCESS"
    }
}

# Process a single file with Claude
function Invoke-ClaudeFix {
    param(
        [string]$FilePath,
        [array]$Errors,
        [string]$ProjectRoot,
        [hashtable]$ErrorsByTool,
        [switch]$PreferRuff
    )

    Write-Log "Processing $FilePath with Claude..." "INFO"

    # Get file content
    $fileContent = Get-PythonFileContent -FilePath $FilePath -ProjectRoot $ProjectRoot
    if (-not $fileContent) {
        return $false
    }

    # Generate Claude prompt
    $claudePrompt = New-ClaudePrompt -FilePath $FilePath -Errors $Errors -FileContent $fileContent -ErrorsByTool $ErrorsByTool -PreferRuff:$PreferRuff

    # Write prompt to prompts directory for Claude
    $promptsDir = Join-Path $ProjectRoot "basedpyright-workflow\prompts"
    if (-not (Test-Path $promptsDir)) {
        New-Item -Path $promptsDir -ItemType Directory -Force | Out-Null
        Write-Log "Created prompts directory: $promptsDir" "INFO"
    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $fileName = [IO.Path]::GetFileNameWithoutExtension($FilePath) -replace '[^a-zA-Z0-9]', '_'
    $tempPromptFile = Join-Path $promptsDir "prompt-${fileName}-${timestamp}.txt"
    $claudePrompt | Out-File -FilePath $tempPromptFile -Encoding UTF8

    try {
        # Launch Claude Code in new interactive PowerShell window
        Write-Log "Calling Claude Code to fix $FilePath..." "INFO"

        # Use Start-Process to create new interactive window with --dangerously-skip-permissions
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "claude --dangerously-skip-permissions `"$tempPromptFile`"" -NoNewWindow:$false

        Write-Log "Claude Code window launched for $FilePath" "SUCCESS"
        Write-Log "Claude prompt saved to: $tempPromptFile" "INFO"

        return $true

    } catch {
        Write-Log "Failed to launch Claude Code for $FilePath : $($_.Exception.Message)" "ERROR"
        return $false

    } finally {
        # Note: Temporary file is not deleted immediately because Claude needs to read it
        # User can manually delete temp files after processing: Remove-Item $env:TEMP\claude_fix_prompt_*.txt
        Write-Log "Temporary prompt file not auto-deleted (Claude needs it): $tempPromptFile" "INFO"
    }
}

# Display usage help function
function Show-Usage {
    Write-ColorOutput "" "Yellow"
    Write-ColorOutput "USAGE:" "Yellow"
    Write-ColorOutput "  .\fix_project_errors.ps1 [[-ErrorsFile] <string>] [-ProjectPath <path>] [-IntervalSeconds <int>] [-IncludeRuff] [-PreferRuff] [-ApplyRuffFixes]" "White"
    Write-ColorOutput ""
    Write-ColorOutput "PARAMETERS:" "Yellow"
    Write-ColorOutput "  -ErrorsFile      Path to error JSON file (optional, auto-discovers by default)" "White"
    Write-ColorOutput "  -ProjectPath     Project root path (default: current directory)" "White"
    Write-ColorOutput "  -IntervalSeconds Seconds to wait between processing files (default: 60)" "White"
    Write-ColorOutput "  -IncludeRuff     Include ruff errors in processing" "White"
    Write-ColorOutput "  -PreferRuff      Prefer ruff fixes over basedpyright when conflicts exist" "White"
    Write-ColorOutput "  -ApplyRuffFixes  Apply ruff automatic fixes before Claude processing" "White"
    Write-ColorOutput ""
    Write-ColorOutput "EXAMPLES:" "Yellow"
    Write-ColorOutput "  # Process errors in current project" "White"
    Write-ColorOutput "  .\fix_project_errors.ps1" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "  # Process errors in specified project" "White"
    Write-ColorOutput '  .\fix_project_errors.ps1 -ProjectPath "..\my-project"' "Green"
    Write-ColorOutput ""
    Write-ColorOutput "  # Include ruff errors and apply fixes" "White"
    Write-ColorOutput "  .\fix_project_errors.ps1 -IncludeRuff -ApplyRuffFixes" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "  # Use custom error file with ruff support" "White"
    Write-ColorOutput '  .\fix_project_errors.ps1 -IncludeRuff -ErrorsFile ".bmad\results\unified_errors_only_20241201_120000.json"' "Green"
    Write-ColorOutput ""
}

# Test mode - just validate functions and exit
if ($TestMode) {
    Write-Host "TEST MODE: Running functions validation..." -ForegroundColor Cyan
    Write-Host
    Write-Host "Test 1: Path configuration" -ForegroundColor Yellow
    Write-Host "Project root: $ProjectRoot" -ForegroundColor Green
    Write-Host "Output dir: $OutputDir" -ForegroundColor Green
    Write-Host "Results dir: $ResultsDir" -ForegroundColor Green
    Write-Host
    Write-Host "Test 2: Find-LatestErrorFile" -ForegroundColor Yellow
    $testFile = Find-LatestErrorFile -ResultsDir $ResultsDir -IncludeRuff:$IncludeRuff
    Write-Host "Found: $testFile" -ForegroundColor Green
    Write-Host
    Write-Host "All tests complete!" -ForegroundColor Cyan
    exit 0
}

# Validate interval parameter
if ($IntervalSeconds -le 0) {
    Write-Log "ERROR: IntervalSeconds must be a positive integer" "ERROR"
    Show-Usage
    exit 1
}

# Auto-discover error file if not specified
if (-not $ErrorsFile) {
    Write-Log "Auto-discovering latest error file..." "INFO"
    $ErrorsFile = Find-LatestErrorFile -ResultsDir $ResultsDir -IncludeRuff:$IncludeRuff

    if (-not $ErrorsFile) {
        Write-Log "No error files found in $ResultsDir" "WARN"
        $fileTypes = if ($IncludeRuff) { "unified_errors_only_*.json or basedpyright_errors_only_*.json" } else { "basedpyright_errors_only_*.json" }
        Write-Log "Expected: $fileTypes" "WARN"
        Write-Log "Run 'basedpyright-workflow fix' to generate error files" "WARN"
        Write-Log "Make sure you have .bpr.json configuration file in your project root" "WARN"
        Show-Usage
        exit 1
    }

    Write-Log "Found error file: $(Split-Path $ErrorsFile -Leaf)" "SUCCESS"
}

# Check if error file exists
if (-not (Test-Path $ErrorsFile)) {
    Write-Log "Cannot find error file: $ErrorsFile" "ERROR"
    Write-Log "Please check the file path and try again" "ERROR"
    Show-Usage
    exit 1
}

# Validate JSON file
Write-Log "Validating error file format..." "INFO"
try {
    $testContent = Get-Content -Path $ErrorsFile -Encoding UTF8 -Raw | ConvertFrom-Json
    if (-not $testContent.errors_by_file -or -not $testContent.metadata) {
        Write-Log "Invalid error file format" "ERROR"
        Write-Log "Expected structure: {metadata: {...}, errors_by_file: [...]}" "ERROR"
        exit 1
    }
} catch {
    Write-Log "Failed to parse JSON file: $($_.Exception.Message)" "ERROR"
    exit 1
}

Write-Log "" "INFO"
Write-Log "==========================================" "INFO"
Write-Log "Project error fix script started" "INFO"
Write-Log "Project root: $ProjectRoot" "INFO"
Write-Log "Error file: $ErrorsFile" "INFO"
Write-Log "Include Ruff: $IncludeRuff" "INFO"
Write-Log "Prefer Ruff: $PreferRuff" "INFO"
Write-Log "Apply Ruff Fixes: $ApplyRuffFixes" "INFO"
Write-Log "Interval: $IntervalSeconds seconds" "INFO"
Write-Log "Log file: $logFile" "INFO"
Write-Log "==========================================" "INFO"

try {
    # Apply ruff automatic fixes if requested
    if ($ApplyRuffFixes) {
        $ruffSuccess = Invoke-RuffAutoFix -ProjectRoot $ProjectRoot
        if ($ruffSuccess) {
            Write-Log "Ruff automatic fixes completed, proceeding with Claude processing" "SUCCESS"
        } else {
            Write-Log "Ruff automatic fixes failed, continuing with Claude processing only" "WARN"
        }
    }

    # Read JSON file
    Write-Log "Reading error file..."
    $jsonContent = Get-Content -Path $ErrorsFile -Encoding UTF8 -Raw | ConvertFrom-Json

    # Extract errors_by_file array
    $errorsData = $jsonContent.errors_by_file
    $totalFiles = $errorsData.Count
    $currentFile = 0

    # Display metadata
    $metadata = $jsonContent.metadata
    Write-Log "Source file: $($metadata.source_file)" "INFO"
    Write-Log "Tools used: $($metadata.tools -join ', ')" "INFO"
    Write-Log "Total files with errors: $($metadata.total_files_with_errors)" "INFO"
    Write-Log "Total errors: $($metadata.total_errors)" "INFO"
    Write-Log ""

    Write-Log "Found $totalFiles files with errors"
    Write-Log ""

    # Process each file
    foreach ($fileEntry in $errorsData) {
        $currentFile++
        $filePath = $fileEntry.file
        $errors = $fileEntry.errors
        $errorCount = $fileEntry.error_count
        $errorsByRule = $fileEntry.errors_by_rule
        $errorsByTool = $fileEntry.errors_by_tool

        Write-Log "=========================================="
        Write-Log "Processing file [$currentFile/$totalFiles]: $filePath"
        Write-Log "Error count: $errorCount"

        # Show error distribution by tool
        if ($errorsByTool) {
            $toolSummary = @()
            foreach ($tool in $errorsByTool.Keys) {
                $toolSummary += "$tool($($errorsByTool[$tool]))"
            }
            Write-Log "Errors by tool: $($toolSummary -join ', ')"
        }

        # Show error distribution by rule (top 5)
        if ($errorsByRule) {
            # Convert PSCustomObject to Hashtable if needed
            $hashtableErrorsByRule = @{}
            if ($errorsByRule -is [PSCustomObject]) {
                foreach ($property in $errorsByRule.PSObject.Properties) {
                    $hashtableErrorsByRule[$property.Name] = $property.Value
                }
            } elseif ($errorsByRule -is [hashtable]) {
                $hashtableErrorsByRule = $errorsByRule
            }

            if ($hashtableErrorsByRule.Count -gt 0) {
                $topRules = $hashtableErrorsByRule.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 5
                $ruleSummary = @()
                foreach ($rule in $topRules) {
                    $ruleSummary += "$($rule.Key)($($rule.Value))"
                }
                Write-Log "Top rules: $($ruleSummary -join ', ')"
            }
        }

        Write-Log ""

        # Convert ErrorsByTool to Hashtable if needed
        $errorsByToolHashtable = @{}
        if ($errorsByTool -is [PSCustomObject]) {
            foreach ($property in $errorsByTool.PSObject.Properties) {
                $errorsByToolHashtable[$property.Name] = $property.Value
            }
        } elseif ($errorsByTool -is [hashtable]) {
            $errorsByToolHashtable = $errorsByTool
        } else {
            $errorsByToolHashtable = @{}  # Default to empty hashtable
        }

        # Process file with Claude
        $success = Invoke-ClaudeFix -FilePath $filePath -Errors $errors -ProjectRoot $ProjectRoot -ErrorsByTool $errorsByToolHashtable -PreferRuff:$PreferRuff

        if ($success) {
            Write-Log "Successfully processed $filePath" "SUCCESS"
        } else {
            Write-Log "Failed to process $filePath" "ERROR"
        }

        # Wait between files (except for the last one)
        if ($currentFile -lt $totalFiles) {
            Write-Log "Waiting $IntervalSeconds seconds before next file..." "INFO"
            Start-Sleep -Seconds $IntervalSeconds
        }

        Write-Log ""
    }

    Write-Log "==========================================" "SUCCESS"
    Write-Log "All files processed successfully!" "SUCCESS"
    Write-Log "==========================================" "SUCCESS"

} catch {
    Write-Log "Script failed with error: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    exit 1
}

Write-Log "Script completed. Log file: $logFile" "INFO"
Write-Log "" "INFO"
Write-Log "NOTE: Claude prompt files in basedpyright-workflow\\prompts were not deleted." "WARN"
Write-Log "To clean up prompt files, run: Clear-ClaudePromptFiles" "WARN"