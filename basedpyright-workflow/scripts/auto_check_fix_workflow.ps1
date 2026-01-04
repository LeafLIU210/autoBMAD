# PowerShell Script: Automated BasedPyright Check, Report and Fix Workflow
# Created: 2025-11-09
# Description: Run basedpyright check, generate reports, and auto-fix errors with Claude

param(
    [string]$SrcDir = "src",
    [int]$FixIntervalSeconds = 300
)

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Log file path
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logFile = Join-Path $scriptDir "auto_workflow_$timestamp.log"

# Write log function
function Write-Log {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMsg = "[$ts] $Message"
    Write-Host $logMsg
    Add-Content -Path $logFile -Value $logMsg -Encoding UTF8
}

# Check Python environment
function Test-PythonEnvironment {
    Write-Log "Checking Python environment..."
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "Python version: $pythonVersion"
        return $true
    } catch {
        Write-Log "ERROR: Python not found, please ensure Python is installed and in PATH"
        return $false
    }
}

# Check if basedpyright is installed
function Test-BasedPyright {
    Write-Log "Checking basedpyright installation..."
    try {
        $basedpyrightVersion = basedpyright --version 2>&1
        Write-Log "basedpyright version: $basedpyrightVersion"
        return $true
    } catch {
        Write-Log "WARNING: basedpyright not found, attempting to install..."
        try {
            python -m pip install basedpyright
            Write-Log "SUCCESS: basedpyright installed"
            return $true
        } catch {
            Write-Log "ERROR: Failed to install basedpyright"
            return $false
        }
    }
}

# Step 1: Run basedpyright check
function Step1-RunBasedPyrightCheck {
    Write-Log ""
    Write-Log "=========================================="
    Write-Log "Step 1: Run BasedPyright Check"
    Write-Log "=========================================="
    
    $checkScript = Join-Path $scriptDir "run_basedpyright_check.py"
    
    if (-not (Test-Path $checkScript)) {
        Write-Log "ERROR: Check script not found at $checkScript"
        return $null
    }
    
    Write-Log "Executing: python `"$checkScript`" $SrcDir"
    
    try {
        # Execute check script
        $output = python "$checkScript" $SrcDir 2>&1
        $exitCode = $LASTEXITCODE
        
        # Output results
        $output | ForEach-Object { Write-Log $_ }
        
        if ($exitCode -eq 0 -or $exitCode -eq 1) {
            Write-Log "SUCCESS: Step 1 completed - BasedPyright check finished"
            
            # Find latest generated result files
            $resultsDir = Join-Path (Split-Path -Parent $scriptDir) "results"
            $latestJsonFile = Get-ChildItem -Path $resultsDir -Filter "basedpyright_check_result_*.json" | 
                Sort-Object LastWriteTime -Descending | 
                Select-Object -First 1
            
            $latestTxtFile = Get-ChildItem -Path $resultsDir -Filter "basedpyright_check_result_*.txt" | 
                Sort-Object LastWriteTime -Descending | 
                Select-Object -First 1
            
            return @{
                Success = $true
                JsonFile = $latestJsonFile.FullName
                TxtFile = $latestTxtFile.FullName
            }
        } else {
            Write-Log "ERROR: Check script failed with exit code: $exitCode"
            return $null
        }
        
    } catch {
        Write-Log "ERROR: Exception while executing check script - $($_.Exception.Message)"
        Write-Log "Stack trace: $($_.ScriptStackTrace)"
        return $null
    }
}

# Step 2: Generate report
function Step2-GenerateReport {
    param(
        [string]$TxtFile,
        [string]$JsonFile
    )
    
    Write-Log ""
    Write-Log "=========================================="
    Write-Log "Step 2: Generate Error Report"
    Write-Log "=========================================="
    
    $reportScript = Join-Path $scriptDir "generate_basedpyright_report.py"
    
    if (-not (Test-Path $reportScript)) {
        Write-Log "ERROR: Report script not found at $reportScript"
        return $false
    }
    
    Write-Log "Executing: python `"$reportScript`" `"$TxtFile`" `"$JsonFile`""
    
    try {
        # Execute report generation script
        $output = python "$reportScript" "$TxtFile" "$JsonFile" 2>&1
        $exitCode = $LASTEXITCODE
        
        # Output results
        $output | ForEach-Object { Write-Log $_ }
        
        if ($exitCode -eq 0) {
            Write-Log "SUCCESS: Step 2 completed - Report generated"
            return $true
        } else {
            Write-Log "ERROR: Report generation failed with exit code: $exitCode"
            return $false
        }
        
    } catch {
        Write-Log "ERROR: Exception while generating report - $($_.Exception.Message)"
        Write-Log "Stack trace: $($_.ScriptStackTrace)"
        return $false
    }
}

# Step 3: Convert errors to JSON format for fixing
function Step3-ConvertErrorsToJson {
    param([string]$JsonFile)
    
    Write-Log ""
    Write-Log "=========================================="
    Write-Log "Step 3: Convert Errors to Fix-Ready JSON"
    Write-Log "=========================================="
    
    $convertScript = Join-Path $scriptDir "convert_errors_to_json.py"
    
    if (-not (Test-Path $convertScript)) {
        Write-Log "ERROR: Convert script not found at $convertScript"
        return $null
    }
    
    # convert_errors_to_json.py needs txt file as input
    # Find corresponding txt file
    $resultsDir = Join-Path (Split-Path -Parent $scriptDir) "results"
    $latestTxtFile = Get-ChildItem -Path $resultsDir -Filter "basedpyright_check_result_*.txt" | 
        Sort-Object LastWriteTime -Descending | 
        Select-Object -First 1
    
    if (-not $latestTxtFile) {
        Write-Log "ERROR: No txt format check result file found"
        return $null
    }
    
    $txtFile = $latestTxtFile.FullName
    Write-Log "Using txt file: $txtFile"
    Write-Log "Executing: python `"$convertScript`" `"$txtFile`""
    
    try {
        # Execute conversion script
        $output = python "$convertScript" "$txtFile" 2>&1
        $exitCode = $LASTEXITCODE
        
        # Output results
        $output | ForEach-Object { Write-Log $_ }
        
        if ($exitCode -eq 0) {
            Write-Log "SUCCESS: Step 3 completed - Errors converted to JSON"
            
            # Find latest generated errors JSON file
            $latestErrorsFile = Get-ChildItem -Path $resultsDir -Filter "basedpyright_errors_only_*.json" | 
                Sort-Object LastWriteTime -Descending | 
                Select-Object -First 1
            
            if ($latestErrorsFile) {
                return $latestErrorsFile.FullName
            } else {
                Write-Log "WARNING: Generated errors JSON file not found"
                return $null
            }
        } else {
            Write-Log "ERROR: Conversion script failed with exit code: $exitCode"
            return $null
        }
        
    } catch {
        Write-Log "ERROR: Exception while converting errors - $($_.Exception.Message)"
        Write-Log "Stack trace: $($_.ScriptStackTrace)"
        return $null
    }
}

# Step 4: Auto-fix errors
function Step4-AutoFixErrors {
    param(
        [string]$ErrorsJsonFile,
        [int]$IntervalSeconds
    )
    
    Write-Log ""
    Write-Log "=========================================="
    Write-Log "Step 4: Auto-Fix Errors with Claude"
    Write-Log "=========================================="
    
    $fixScript = Join-Path (Split-Path -Parent $scriptDir) "fix_project_errors.ps1"
    
    if (-not (Test-Path $fixScript)) {
        Write-Log "ERROR: Fix script not found at $fixScript"
        return $false
    }
    
    Write-Log "Executing: powershell.exe -File `"$fixScript`" -ErrorsFile `"$ErrorsJsonFile`" -IntervalSeconds $IntervalSeconds"
    
    try {
        # Execute fix script in new window
        $proc = Start-Process -FilePath "powershell.exe" `
            -ArgumentList "-NoExit", "-File", "`"$fixScript`"", "-ErrorsFile", "`"$ErrorsJsonFile`"", "-IntervalSeconds", "$IntervalSeconds" `
            -PassThru
        
        Write-Log "SUCCESS: Step 4 started - Fix script running in new window (Process ID: $($proc.Id))"
        Write-Log "Fix script will iterate through all error files and fix with Claude"
        Write-Log "Fix interval: $IntervalSeconds seconds"
        
        return $true
        
    } catch {
        Write-Log "ERROR: Exception while starting fix script - $($_.Exception.Message)"
        Write-Log "Stack trace: $($_.ScriptStackTrace)"
        return $false
    }
}

# Main workflow
function Main {
    Write-Log "=========================================="
    Write-Log "BasedPyright Auto Check-Fix Workflow"
    Write-Log "=========================================="
    Write-Log "Source directory: $SrcDir"
    Write-Log "Fix interval: $FixIntervalSeconds seconds"
    Write-Log "Log file: $logFile"
    Write-Log "=========================================="
    Write-Log ""
    
    # Check environment
    if (-not (Test-PythonEnvironment)) {
        Write-Log "Environment check failed, exiting"
        exit 1
    }
    
    if (-not (Test-BasedPyright)) {
        Write-Log "basedpyright check failed, exiting"
        exit 1
    }
    
    Write-Log "SUCCESS: Environment check passed"
    Write-Log ""
    
    # Step 1: Run check
    $step1Result = Step1-RunBasedPyrightCheck
    if (-not $step1Result -or -not $step1Result.Success) {
        Write-Log "Step 1 failed, workflow terminated"
        exit 1
    }
    
    $jsonFile = $step1Result.JsonFile
    $txtFile = $step1Result.TxtFile
    
    Write-Log ""
    Write-Log "Generated files:"
    Write-Log "  - JSON result: $jsonFile"
    Write-Log "  - TXT result: $txtFile"
    
    # Step 2: Generate report
    $step2Result = Step2-GenerateReport -TxtFile $txtFile -JsonFile $jsonFile
    if (-not $step2Result) {
        Write-Log "Step 2 failed, but continuing with next steps"
    }
    
    # Step 3: Convert errors to JSON
    $errorsJsonFile = Step3-ConvertErrorsToJson -JsonFile $jsonFile
    if (-not $errorsJsonFile) {
        Write-Log "Step 3 failed, cannot continue to fix step"
        Write-Log ""
        Write-Log "Workflow partially completed (check and report generated)"
        exit 1
    }
    
    Write-Log ""
    Write-Log "Errors JSON file: $errorsJsonFile"
    
    # Step 4: Auto-fix
    $step4Result = Step4-AutoFixErrors -ErrorsJsonFile $errorsJsonFile -IntervalSeconds $FixIntervalSeconds
    if (-not $step4Result) {
        Write-Log "Step 4 failed"
        exit 1
    }
    
    Write-Log ""
    Write-Log "=========================================="
    Write-Log "Workflow Completed"
    Write-Log "=========================================="
    Write-Log "1. SUCCESS: BasedPyright check completed"
    Write-Log "2. SUCCESS: Error report generated"
    Write-Log "3. SUCCESS: Errors JSON generated"
    Write-Log "4. SUCCESS: Auto-fix script started (running in new window)"
    Write-Log ""
    Write-Log "Please check the newly opened window to monitor fix progress"
    Write-Log "Log file: $logFile"
    Write-Log "=========================================="
}

# Execute main workflow
try {
    Main
} catch {
    Write-Log "ERROR: Uncaught exception during workflow execution"
    Write-Log "Exception message: $($_.Exception.Message)"
    Write-Log "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}

# Keep window open
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
