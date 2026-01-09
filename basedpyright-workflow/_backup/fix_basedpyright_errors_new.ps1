# PowerShell Script: Process basedpyright error files one by one
# Updated: 2025-11-29
# Description: Auto-discovers basedpyright error files and processes them with Claude Code

param(
    [string]$ErrorsFile = $null,  # Auto-discovery by default
    [int]$IntervalSeconds = 60,
    [switch]$TestMode = $false    # For testing functions without running main script
)

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Determine script location and set base paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$WorkflowDir = Join-Path $ProjectRoot "basedpyright-workflow"
$ResultsDir = Join-Path $WorkflowDir "results"

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
$logFile = Join-Path $ScriptDir "fix_basedpyright_errors_$timestamp.log"

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
        default { "White" }
    }
    Write-Host $logMsg -ForegroundColor $color

    # Write to log file (plain text)
    Add-Content -Path $logFile -Value $logMsg -Encoding UTF8
}

# Find latest error file function
function Find-LatestErrorFile {
    param(
        [string]$ResultsDir
    )

    if (-not (Test-Path $ResultsDir)) {
        return $null
    }

    $errorFiles = Get-ChildItem -Path $ResultsDir -Filter "basedpyright_errors_only_*.json" |
                  Sort-Object LastWriteTime -Descending

    if ($errorFiles.Count -eq 0) {
        return $null
    }

    return $errorFiles[0].FullName
}

# Display usage help function
function Show-Usage {
    Write-ColorOutput "" "Yellow"
    Write-ColorOutput "USAGE:" "Yellow"
    Write-ColorOutput "  .\fix_basedpyright_errors_new.ps1 [[-ErrorsFile] <string>] [-IntervalSeconds <int>]" "White"
    Write-ColorOutput ""
    Write-ColorOutput "PARAMETERS:" "Yellow"
    Write-ColorOutput "  -ErrorsFile        Path to error JSON file (optional, auto-discovers by default)" "White"
    Write-ColorOutput "  -IntervalSeconds  Seconds to wait between processing files (default: 300)" "White"
    Write-ColorOutput ""
    Write-ColorOutput "EXAMPLES:" "Yellow"
    Write-ColorOutput "  # Use auto-discovered latest error file" "White"
    Write-ColorOutput "  .\fix_basedpyright_errors_new.ps1" "Green"
    Write-ColorOutput ""
    Write-ColorOutput "  # Specify custom error file" "White"
    Write-ColorOutput '  .\fix_basedpyright_errors_new.ps1 -ErrorsFile "..\results\custom_errors.json"' "Green"
    Write-ColorOutput ""
    Write-ColorOutput "  # Use auto-discovery with custom interval" "White"
    Write-ColorOutput "  .\fix_basedpyright_errors_new.ps1 -IntervalSeconds 600" "Green"
    Write-ColorOutput ""
}

# Test mode - just validate functions and exit
if ($TestMode) {
    Write-Host "TEST MODE: Running functions validation..." -ForegroundColor Cyan
    Write-Host
    Write-Host "Test 1: Find-LatestErrorFile" -ForegroundColor Yellow
    $ResultsDir = Join-Path $ProjectRoot "basedpyright-workflow\results"
    $testFile = Find-LatestErrorFile -ResultsDir $ResultsDir
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
    $ErrorsFile = Find-LatestErrorFile -ResultsDir $ResultsDir

    if (-not $ErrorsFile) {
        Write-Log "No error files found in $ResultsDir" "WARN"
        Write-Log "Expected: basedpyright_errors_only_YYYYMMDDD_HHMMSS.json" "WARN"
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
Write-Log "basedpyright error fix script started" "INFO"
Write-Log "Error file: $ErrorsFile" "INFO"
Write-Log "Interval: $IntervalSeconds seconds" "INFO"
Write-Log "Log file: $logFile" "INFO"
Write-Log "==========================================" "INFO"

try {
    # Read JSON file
    Write-Log "Reading error file..."
    $jsonContent = Get-Content -Path $ErrorsFile -Encoding UTF8 -Raw | ConvertFrom-Json
    
    # Extract errors_by_file array from new JSON structure
    $errorsData = $jsonContent.errors_by_file
    $totalFiles = $errorsData.Count
    $currentFile = 0
    
    # Display metadata
    $metadata = $jsonContent.metadata
    Write-Log "Source file: $($metadata.source_file)"
    Write-Log "Total files with errors: $($metadata.total_files_with_errors)"
    Write-Log "Total errors: $($metadata.total_errors)"
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

        Write-Log "=========================================="
        Write-Log "Processing file [$currentFile/$totalFiles]: $filePath"
        Write-Log "Error count: $errorCount"
        
        # Display error distribution by rule
        Write-Log "Errors by rule:"
        foreach ($rule in $errorsByRule.PSObject.Properties) {
            Write-Log "  - $($rule.Name): $($rule.Value)"
        }
        Write-Log "=========================================="

        # Build error information with complete details
        $errorsText = ""
        foreach ($errorItem in $errors) {
            $line = $errorItem.line
            $column = $errorItem.column
            $msg = $errorItem.message
            $rule = $errorItem.rule
            $errorsText += "File: ${filePath}`n"
            $errorsText += "Line: ${line}, Column: ${column}`n"
            $errorsText += "Rule: ${rule}`n"
            $errorsText += "Error: ${msg}`n"
            $errorsText += "`n---`n"
        }

        # Build Claude command with complete error details
        $promptText = @"
Fix all basedpyright errors in file: $filePath

Total errors: $errorCount

Error details:
$errorsText

Please fix all these errors while maintaining code functionality.
"@

        Write-Log "Executing command: claude --dangerously-skip-permissions"
        Write-Log "Starting new PowerShell window..."
        Write-Log "Prompt preview (first 200 chars): $($promptText.Substring(0, [Math]::Min(200, $promptText.Length)))..."

        try {
            # Create prompts directory if it doesn't exist
            $promptsDir = Join-Path $WorkflowDir "prompts"
            if (-not (Test-Path $promptsDir)) {
                New-Item -ItemType Directory -Path $promptsDir -Force | Out-Null
            }

            # Create prompt file for this file's errors
            $safeFileName = [System.IO.Path]::GetFileName($filePath) -replace '\W', '-'
            $safeTimestamp = $timestamp -replace '_', '-'
            $promptFileName = "prompt-$safeFileName-$safeTimestamp.txt"
            $promptFilePath = Join-Path $promptsDir $promptFileName

            # Save prompt to file
            $promptText | Out-File -FilePath $promptFilePath -Encoding UTF8

            # Create a safe path version for command injection (replace backslashes with underscores)
            $safePathForCommand = $promptFilePath -replace '\\', '_'

            # Build command using @file syntax with quotes
            # Use -f format operator to avoid PowerShell treating "@$" as splat operator
            # Use safePathForCommand to avoid backslash issues
            $commandStr = 'claude --dangerously-skip-permissions "@{0}"' -f $safePathForCommand

            # Start new PowerShell window
            $proc = Start-Process -FilePath "powershell.exe" `
                -ArgumentList "-NoExit", "-Command", $commandStr `
                -PassThru

            Write-Log "Started new window (Process ID: $($proc.Id))"
            Write-Log "Claude command is executing in new window"
            Write-Log "File: $filePath"
            Write-Log "Prompt file: $promptFilePath"

        } catch {
            Write-Log "ERROR: Execution failed - $($_.Exception.Message)"
            Write-Log "Stack trace: $($_.ScriptStackTrace)"
        }

        # If not the last file, wait
        if ($currentFile -lt $totalFiles) {
            Write-Log "Waiting $IntervalSeconds seconds before processing next file..."

            $nextExecTime = (Get-Date).AddSeconds($IntervalSeconds)
            $timeStr = $nextExecTime.ToString("yyyy-MM-dd HH:mm:ss")
            Write-Log "Next execution time: $timeStr"

            # Countdown display
            for ($j = $IntervalSeconds; $j -gt 0; $j--) {
                $mins = [Math]::Floor($j / 60)
                $secs = $j % 60
                $pct = (($IntervalSeconds - $j) / $IntervalSeconds) * 100
                $status = "Remaining time: $mins min $secs sec"
                Write-Progress -Activity "Waiting for next processing" -Status $status -PercentComplete $pct
                Start-Sleep -Seconds 1
            }
            Write-Progress -Activity "Waiting for next processing" -Completed
        }
    }

    Write-Log ""
    Write-Log "=========================================="
    Write-Log "All files processed"
    Write-Log "Total processed files: $totalFiles"
    Write-Log "Log saved to: $logFile"
    Write-Log "=========================================="

} catch {
    Write-Log "ERROR: Exception occurred during processing - $($_.Exception.Message)"
    Write-Log "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

# Optional: Keep window open after completion
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")