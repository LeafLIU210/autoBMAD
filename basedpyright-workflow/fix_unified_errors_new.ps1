# PowerShell Script: Process unified error files (basedpyright + ruff) one by one
# Updated: 2025-12-17
# Description: Auto-discovers unified error files and processes them with Claude Code

param(
    [string]$ErrorsFile = $null,      # Auto-discovery by default
    [int]$IntervalSeconds = 60,
    [switch]$TestMode = $false,       # For testing functions without running main script
    [switch]$IncludeRuff = $false,    # Include ruff errors in processing
    [switch]$PreferRuff = $false,     # Prefer ruff fixes over basedpyright when conflicts exist
    [switch]$ApplyRuffFixes = $false  # Apply ruff automatic fixes before Claude processing
)

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Determine script location and set base paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$WorkflowDir = Join-Path $ProjectRoot "basedpyright-workflow"
$ResultsDir = Join-Path $ProjectRoot ".bpr/results"

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
$logFile = Join-Path $ScriptDir "fix_unified_errors_$timestamp.log"

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
        [string]$SourceDir
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

        # Apply ruff fixes
        Push-Location $SourceDir
        $fixResult = & python -m ruff check --fix 2>&1
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

    # Path is already absolute, use it directly (Occam's razor: simplest solution)
    $fullPath = $FilePath

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

File content:
```python
$FileContent
```

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

    # Write prompt to temporary file for Claude
    $tempPromptFile = Join-Path $env:TEMP "claude_fix_prompt_$(Get-Random).txt"
    $claudePrompt | Out-File -FilePath $tempPromptFile -Encoding UTF8

    try {
        # Invoke Claude Code
        Write-Log "Calling Claude Code to fix $FilePath..." "INFO"
        $claudeResult = & claude $tempPromptFile 2>&1
        $claudeExitCode = $LASTEXITCODE

        if ($claudeExitCode -eq 0) {
            Write-Log "Claude successfully processed $FilePath" "SUCCESS"

            # Save Claude's response to log
            if ($claudeResult) {
                $claudeLog = Join-Path $ScriptDir "claude_fix_$(Split-Path $FilePath -Leaf)_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
                $claudeResult | Out-File -FilePath $claudeLog -Encoding UTF8
                Write-Log "Claude response saved to: $claudeLog" "INFO"
            }

            return $true
        } else {
            Write-Log "Claude failed to process $FilePath (exit code: $claudeExitCode)" "ERROR"
            if ($claudeResult) {
                Write-Log "Claude error output: $claudeResult" "ERROR"
            }
            return $false
        }

    } finally {
        # Clean up temporary file
        if (Test-Path $tempPromptFile) {
            Remove-Item $tempPromptFile -Force
        }
    }
}

# Display usage help function
function Show-Usage {
    Write-ColorOutput "" "Yellow"
    Write-ColorOutput "USAGE:" "Yellow"
    Write-ColorOutput "  .\fix_unified_errors_new.ps1 [[-ErrorsFile] <string>] [-IntervalSeconds <int>] [-IncludeRuff] [-PreferRuff] [-ApplyRuffFixes]" "White"
    Write-ColorOutput ""
    Write-ColorOutput "PARAMETERS:" "Yellow"
    Write-ColorOutput "  -ErrorsFile      Path to error JSON file (optional, auto-discovers by default)" "White"
    Write-ColorOutput "  -IntervalSeconds Seconds to wait between processing files (default: 60)" "White"
    Write-ColorOutput "  -IncludeRuff     Include ruff errors in processing" "White"
    Write-ColorOutput "  -PreferRuff      Prefer ruff fixes over basedpyright when conflicts exist" "White"
    Write-ColorOutput "  -ApplyRuffFixes  Apply ruff automatic fixes before Claude processing" "White"
    Write-ColorOutput ""
    Write-ColorOutput "EXAMPLES:" "Yellow"
    Write-ColorOutput "  # Process basedpyright errors only" "White"
    Write-ColorOutput "  .\fix_unified_errors_new.ps1" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "  # Process both basedpyright and ruff errors" "White"
    Write-ColorOutput "  .\fix_unified_errors_new.ps1 -IncludeRuff" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "  # Apply ruff auto-fixes and prefer ruff in conflicts" "White"
    Write-ColorOutput "  .\fix_unified_errors_new.ps1 -IncludeRuff -ApplyRuffFixes -PreferRuff" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "  # Use custom error file with ruff support" "White"
    Write-ColorOutput '  .\fix_unified_errors_new.ps1 -IncludeRuff -ErrorsFile "..\results\unified_errors_only_20241201_120000.json"' "Green"
    Write-ColorOutput ""
}

# Test mode - just validate functions and exit
if ($TestMode) {
    Write-Host "TEST MODE: Running functions validation..." -ForegroundColor Cyan
    Write-Host
    Write-Host "Test 1: Find-LatestErrorFile" -ForegroundColor Yellow
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
        Write-Log "Run 'python basedpyright-workflow/cli.py fix' to generate one" "WARN"
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
    if ($null -eq $testContent.errors_by_file -or $null -eq $testContent.metadata) {
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
Write-Log "Unified error fix script started" "INFO"
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
        $ruffSuccess = Invoke-RuffAutoFix -ProjectRoot $ProjectRoot -SourceDir $ProjectRoot
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
            # Handle PSCustomObject from JSON
            if ($errorsByTool -is [PSCustomObject]) {
                foreach ($property in $errorsByTool.PSObject.Properties) {
                    $toolSummary += "$($property.Name)($($property.Value))"
                }
            } else {
                # Handle hashtable
                foreach ($tool in $errorsByTool.Keys) {
                    $toolSummary += "$tool($($errorsByTool[$tool]))"
                }
            }
            Write-Log "Errors by tool: $($toolSummary -join ', ')"
        }

        # Show error distribution by rule (top 5)
        if ($errorsByRule) {
            # Handle PSCustomObject from JSON
            if ($errorsByRule -is [PSCustomObject]) {
                $topRules = $errorsByRule.PSObject.Properties | 
                    Sort-Object Value -Descending | 
                    Select-Object -First 5
            } else {
                # Handle hashtable
                $topRules = $errorsByRule.GetEnumerator() | 
                    Sort-Object Value -Descending | 
                    Select-Object -First 5
            }
            $ruleSummary = @()
            foreach ($rule in $topRules) {
                if ($rule -is [PSCustomObject]) {
                    $ruleSummary += "$($rule.Name)($($rule.Value))"
                } else {
                    $ruleSummary += "$($rule.Key)($($rule.Value))"
                }
            }
            Write-Log "Top rules: $($ruleSummary -join ', ')"
        }

        Write-Log ""

        # Convert PSCustomObject to Hashtable if needed
        $hashtableErrorsByTool = @{}
        if ($errorsByTool -is [PSCustomObject]) {
            foreach ($property in $errorsByTool.PSObject.Properties) {
                $hashtableErrorsByTool[$property.Name] = $property.Value
            }
        } elseif ($errorsByTool -is [hashtable]) {
            $hashtableErrorsByTool = $errorsByTool
        }

        # Process file with Claude
        $success = Invoke-ClaudeFix -FilePath $filePath -Errors $errors -ProjectRoot $ProjectRoot -ErrorsByTool $hashtableErrorsByTool -PreferRuff:$PreferRuff

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