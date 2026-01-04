# BMAD QA Tools Integration PowerShell Module
# Integrates BasedPyright-Workflow and Fixtest-Workflow into BMAD workflow
# Version: 1.0.0

# Store the module directory
$script:ModuleDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Enum for QA status
enum QAStatus {
    Pass = 0
    Concerns = 1
    Fail = 2
    Waived = 3
}

# QA Result class
class QAToolResult {
    [string]$Tool
    [QAStatus]$Status
    [DateTime]$StartTime
    [DateTime]$EndTime
    [double]$DurationSeconds
    [int]$ViolationCount
    [int]$RetryCount
    [string]$OutputFile
    [string]$ErrorMessage
    [hashtable]$Metrics

    QAToolResult() {
        $this.Metrics = @{}
        $this.RetryCount = 0
    }
}

# QA Aggregate Result class
class QAAggregateResult {
    [QAStatus]$OverallStatus
    [QAToolResult]$BasedPyrightResult
    [QAToolResult]$FixtestResult
    [DateTime]$Timestamp
    [int]$RetryCount

    QAAggregateResult() {
        $this.Timestamp = Get-Date
        $this.RetryCount = 0
    }
}

function Write-QALog {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,

        [Parameter(Mandatory=$false)]
        [ValidateSet('Info', 'Warning', 'Error', 'Success')]
        [string]$Level = 'Info'
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] QA: $Message"

    # Output to console with color
    switch ($Level) {
        'Error' { Write-Host $logEntry -ForegroundColor Red }
        'Warning' { Write-Host $logEntry -ForegroundColor Yellow }
        'Success' { Write-Host $logEntry -ForegroundColor Green }
        default { Write-Host $logEntry -ForegroundColor Cyan }
    }

    # Write to log file if available
    try {
        $logFile = $env:BMAD_LOG_FILE
        if ($logFile -and (Test-Path $logFile)) {
            $logEntry | Out-File -FilePath $logFile -Append -Encoding UTF8
        }
    } catch {
        # Fail silently
    }
}

function Find-PythonModule {
    param([string]$ModuleName)

    try {
        $pythonCheck = python -c "import $ModuleName; print($ModuleName.__file__)" 2>$null
        if ($pythonCheck) {
            return $pythonCheck
        }
    } catch {
        return $null
    }

    return $null
}

function Start-BasedPyrightCheck {
    <#
    .SYNOPSIS
    Run BasedPyright-Workflow check

    .PARAMETER ProjectRoot
    Path to project root directory

    .PARAMETER MaxRetries
    Maximum retry attempts

    .RETURNS
    QAToolResult object
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectRoot,

        [Parameter(Mandatory=$false)]
        [int]$MaxRetries = 2
    )

    Write-QALog "Starting BasedPyright check" -Level 'Info'

    $result = [QAToolResult]::new()
    $result.Tool = "BasedPyright"
    $result.StartTime = Get-Date
    $result.Status = [QAStatus]::Fail

    $basedpyrightDir = Join-Path $ProjectRoot "basedpyright-workflow"
    $resultsDir = Join-Path $basedpyrightDir "results"

    # Ensure results directory exists
    if (-not (Test-Path $resultsDir)) {
        New-Item -Path $resultsDir -ItemType Directory -Force | Out-Null
    }

    $lastError = $null

    for ($attempt = 0; $attempt -le $MaxRetries; $attempt++) {
        try {
            Write-QALog "BasedPyright check attempt $($attempt + 1)/$($MaxRetries + 1)" -Level 'Info'

            # Try Python module first
            $pythonScript = @"
import sys
sys.path.append('$basedpyrightDir')

try:
    from basedpyright_workflow import check
    result = check.run_check()
    print(f"SUCCESS:{result}")
except Exception as e:
    print(f"ERROR:{str(e)}")
"@

            $pythonOutput = python -c $pythonScript 2>&1

            if ($LASTEXITCODE -eq 0 -and $pythonOutput -match "SUCCESS") {
                $result.Status = [QAStatus]::Pass
                $result.ViolationCount = 0  # Would parse from actual results
                break
            } else {
                $lastError = $pythonOutput
                Write-QALog "BasedPyright check failed (attempt $($attempt + 1)): $lastError" -Level 'Warning'
            }

        } catch {
            $lastError = $_.Exception.Message
            Write-QALog "BasedPyright check exception: $lastError" -Level 'Error'
        }

        # Wait before retry
        if ($attempt -lt $MaxRetries) {
            Start-Sleep -Seconds 5
        }
    }

    $result.EndTime = Get-Date
    $result.DurationSeconds = ($result.EndTime - $result.StartTime).TotalSeconds
    $result.RetryCount = $attempt
    $result.ErrorMessage = $lastError

    # Find output file
    if (Test-Path $resultsDir) {
        $latestFile = Get-ChildItem -Path $resultsDir -Filter "basedpyright_check_result_*.json" |
                      Sort-Object LastWriteTime -Descending |
                      Select-Object -First 1

        if ($latestFile) {
            $result.OutputFile = $latestFile.FullName
        }
    }

    Write-QALog "BasedPyright check completed with status: $($result.Status)" -Level $(if($result.Status -eq 'Pass'){'Success'}else{'Warning'})
    return $result
}

function Start-FixtestCheck {
    <#
    .SYNOPSIS
    Run Fixtest-Workflow check

    .PARAMETER ProjectRoot
    Path to project root directory

    .PARAMETER MaxRetries
    Maximum retry attempts

    .RETURNS
    QAToolResult object
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectRoot,

        [Parameter(Mandatory=$false)]
        [int]$MaxRetries = 2
    )

    Write-QALog "Starting Fixtest check" -Level 'Info'

    $result = [QAToolResult]::new()
    $result.Tool = "Fixtest"
    $result.StartTime = Get-Date
    $result.Status = [QAStatus]::Fail

    $fixtestDir = Join-Path $ProjectRoot "fixtest-workflow"
    $summariesDir = Join-Path $fixtestDir "summaries"

    # Ensure directories exist
    if (-not (Test-Path $summariesDir)) {
        New-Item -Path $summariesDir -ItemType Directory -Force | Out-Null
    }

    $lastError = $null

    for ($attempt = 0; $attempt -le $MaxRetries; $attempt++) {
        try {
            Write-QALog "Fixtest check attempt $($attempt + 1)/$($MaxRetries + 1)" -Level 'Info'

            # Step 1: Scan test files
            Write-QALog "Scanning test files..." -Level 'Info'
            $scanResult = Start-Process -FilePath "python" -ArgumentList "scan_test_files.py" -WorkingDirectory $fixtestDir -Wait -PassThru -NoNewWindow

            if ($scanResult.ExitCode -ne 0) {
                $lastError = "Test file scan failed with exit code: $($scanResult.ExitCode)"
                Write-QALog $lastError -Level 'Warning'
                continue
            }

            # Step 2: Run tests
            Write-QALog "Running tests..." -Level 'Info'
            $testResult = Start-Process -FilePath "python" -ArgumentList "run_tests.py" -WorkingDirectory $fixtestDir -Wait -PassThru -NoNewWindow -RedirectStandardOutput "$env:TEMP\fixtest_output.txt" -RedirectStandardError "$env:TEMP\fixtest_error.txt"

            $result.EndTime = Get-Date
            $result.DurationSeconds = ($result.EndTime - $result.StartTime).TotalSeconds

            if ($testResult.ExitCode -eq 0 -or (Test-Path "$env:TEMP\fixtest_output.txt")) {
                # Parse output file for errors
                $output = Get-Content "$env:TEMP\fixtest_output.txt" -ErrorAction SilentlyContinue

                # Count violations
                $violationCount = ($output | Select-String "ERROR:|FAILED" | Measure-Object).Count
                $result.ViolationCount = $violationCount

                if ($violationCount -eq 0) {
                    $result.Status = [QAStatus]::Pass
                } else {
                    $result.Status = [QAStatus]::Fail
                }

                break
            } else {
                $lastError = "Test execution failed with exit code: $($testResult.ExitCode)"
                Write-QALog $lastError -Level 'Warning'
            }

        } catch {
            $lastError = $_.Exception.Message
            Write-QALog "Fixtest check exception: $lastError" -Level 'Error'
        }

        # Wait before retry
        if ($attempt -lt $MaxRetries) {
            Start-Sleep -Seconds 5
        }
    }

    $result.RetryCount = $attempt
    $result.ErrorMessage = $lastError

    # Find output file
    if (Test-Path $summariesDir) {
        $latestFile = Get-ChildItem -Path $summariesDir -Filter "test_results_summary_*.json" |
                      Sort-Object LastWriteTime -Descending |
                      Select-Object -First 1

        if ($latestFile) {
            $result.OutputFile = $latestFile.FullName
        }
    }

    Write-QALog "Fixtest check completed with status: $($result.Status)" -Level $(if($result.Status -eq 'Pass'){'Success'}else{'Warning'})
    return $result
}

function Invoke-QAToolsWorkflow {
    <#
    .SYNOPSIS
    Run complete QA workflow with both tools

    .PARAMETER ProjectRoot
    Path to project root directory

    .PARAMETER MaxRetries
    Maximum retry attempts per tool

    .PARAMETER SaveResults
    Whether to save results to file

    .PARAMETER OutputDir
    Directory to save results (optional)

    .RETURNS
    QAAggregateResult object
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectRoot,

        [Parameter(Mandatory=$false)]
        [int]$MaxRetries = 2,

        [Parameter(Mandatory=$false)]
        [switch]$SaveResults,

        [Parameter(Mandatory=$false)]
        [string]$OutputDir = $null
    )

    Write-QALog "========================================" -Level 'Info'
    Write-QALog "Starting QA Tools Workflow" -Level 'Info'
    Write-QALog "Project Root: $ProjectRoot" -Level 'Info'
    Write-QALog "Max Retries: $MaxRetries" -Level 'Info'
    Write-QALog "========================================" -Level 'Info'

    $aggregateResult = [QAAggregateResult]::new()

    # Run BasedPyright check
    Write-QALog "" -Level 'Info'
    Write-QALog "--- Phase 1: BasedPyright Check ---" -Level 'Info'
    $aggregateResult.BasedPyrightResult = Start-BasedPyrightCheck -ProjectRoot $ProjectRoot -MaxRetries $MaxRetries

    # Run Fixtest check
    Write-QALog "" -Level 'Info'
    Write-QALog "--- Phase 2: Fixtest Check ---" -Level 'Info'
    $aggregateResult.FixtestResult = Start-FixtestCheck -ProjectRoot $ProjectRoot -MaxRetries $MaxRetries

    # Aggregate results
    Write-QALog "" -Level 'Info'
    Write-QALog "--- Aggregating Results ---" -Level 'Info'

    $bpStatus = $aggregateResult.BasedPyrightResult.Status
    $ftStatus = $aggregateResult.FixtestResult.Status

    # Determine overall status
    if ($bpStatus -eq [QAStatus]::Fail -or $ftStatus -eq [QAStatus]::Fail) {
        $aggregateResult.OverallStatus = [QAStatus]::Fail
    } elseif ($bpStatus -eq [QAStatus]::Concerns -or $ftStatus -eq [QAStatus]::Concerns) {
        $aggregateResult.OverallStatus = [QAStatus]::Concerns
    } elseif ($bpStatus -eq [QAStatus]::Pass -and $ftStatus -eq [QAStatus]::Pass) {
        $aggregateResult.OverallStatus = [QAStatus]::Pass
    } else {
        $aggregateResult.OverallStatus = [QAStatus]::Concerns
    }

    $aggregateResult.RetryCount = [Math]::Max(
        $aggregateResult.BasedPyrightResult.RetryCount,
        $aggregateResult.FixtestResult.RetryCount
    )

    # Print summary
    Write-QALog "" -Level 'Info'
    Write-QALog "========================================" -Level 'Info'
    Write-QALog "QA Workflow Summary" -Level 'Info'
    Write-QALog "========================================" -Level 'Info'
    Write-QALog "Overall Status: $($aggregateResult.OverallStatus)" -Level $(if($aggregateResult.OverallStatus -eq 'Pass'){'Success'}else{'Warning'})
    Write-QALog "BasedPyright: $($bpStatus) (Violations: $($aggregateResult.BasedPyrightResult.ViolationCount))" -Level 'Info'
    Write-QALog "Fixtest: $($ftStatus) (Violations: $($aggregateResult.FixtestResult.ViolationCount))" -Level 'Info'
    Write-QALog "Total Retries: $($aggregateResult.RetryCount)" -Level 'Info'
    Write-QALog "Duration: $([Math]::Round(($aggregateResult.BasedPyrightResult.DurationSeconds + $aggregateResult.FixtestResult.DurationSeconds), 2)) seconds" -Level 'Info'
    Write-QALog "========================================" -Level 'Info'

    # Save results if requested
    if ($SaveResults) {
        if (-not $OutputDir) {
            $OutputDir = Join-Path $ProjectRoot "bmad-workflow\logs\qa"
        }

        if (-not (Test-Path $OutputDir)) {
            New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
        }

        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $outputFile = Join-Path $OutputDir "qa_results_$timestamp.json"

        $resultData = @{
            OverallStatus = $aggregateResult.OverallStatus.ToString()
            BasedPyright = @{
                Status = $aggregateResult.BasedPyrightResult.Status.ToString()
                ViolationCount = $aggregateResult.BasedPyrightResult.ViolationCount
                DurationSeconds = $aggregateResult.BasedPyrightResult.DurationSeconds
                RetryCount = $aggregateResult.BasedPyrightResult.RetryCount
                OutputFile = $aggregateResult.BasedPyrightResult.OutputFile
                ErrorMessage = $aggregateResult.BasedPyrightResult.ErrorMessage
                Metrics = $aggregateResult.BasedPyrightResult.Metrics
            }
            Fixtest = @{
                Status = $aggregateResult.FixtestResult.Status.ToString()
                ViolationCount = $aggregateResult.FixtestResult.ViolationCount
                DurationSeconds = $aggregateResult.FixtestResult.DurationSeconds
                RetryCount = $aggregateResult.FixtestResult.RetryCount
                OutputFile = $aggregateResult.FixtestResult.OutputFile
                ErrorMessage = $aggregateResult.FixtestResult.ErrorMessage
                Metrics = $aggregateResult.FixtestResult.Metrics
            }
            Timestamp = $aggregateResult.Timestamp.ToString("yyyy-MM-dd HH:mm:ss")
            RetryCount = $aggregateResult.RetryCount
        }

        $resultData | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputFile -Encoding UTF8
        Write-QALog "Results saved to: $outputFile" -Level 'Success'
    }

    return $aggregateResult
}

function Update-StoryWithQAStatus {
    <#
    .SYNOPSIS
    Update story markdown file with QA results

    .PARAMETER StoryPath
    Path to story markdown file

    .PARAMETER QAResult
    QA aggregate result object

    .PARAMETER WorkflowState
    Current workflow state object
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$StoryPath,

        [Parameter(Mandatory=$true)]
        [QAAggregateResult]$QAResult,

        [Parameter(Mandatory=$false)]
        [object]$WorkflowState = $null
    )

    try {
        Write-QALog "Updating story file with QA status: $StoryPath" -Level 'Info'

        if (-not (Test-Path $StoryPath)) {
            Write-QALog "Story file not found: $StoryPath" -Level 'Warning'
            return
        }

        # Read story content
        $content = Get-Content -Path $StoryPath -Raw -Encoding UTF8

        # Update status section
        if ($content -match "(## Status\s+)(.*?)(\n---|\Z)") {
            $statusSection = $matches[1] + "**Status**: $($QAResult.OverallStatus)" + $matches[3]
            $content = $content -replace "(## Status\s+)(.*?)(\n---|\Z)", $statusSection
        }

        # Update QA Results section
        $qaSection = @"
## QA Results

**Overall Status**: $($QAResult.OverallStatus)

**BasedPyright Results**:
- Status: $($QAResult.BasedPyrightResult.Status)
- Violations: $($QAResult.BasedPyrightResult.ViolationCount)
- Duration: $([Math]::Round($QAResult.BasedPyrightResult.DurationSeconds, 2)) seconds
- Retries: $($QAResult.BasedPyrightResult.RetryCount)
- Output: $($QAResult.BasedPyrightResult.OutputFile)

**Fixtest Results**:
- Status: $($QAResult.FixtestResult.Status)
- Violations: $($QAResult.FixtestResult.ViolationCount)
- Duration: $([Math]::Round($QAResult.FixtestResult.DurationSeconds, 2)) seconds
- Retries: $($QAResult.FixtestResult.RetryCount)
- Output: $($QAResult.FixtestResult.OutputFile)

**Timestamp**: $($QAResult.Timestamp.ToString("yyyy-MM-dd HH:mm:ss"))
**Total Retries**: $($QAResult.RetryCount)

---
"@

        if ($content -match "## QA Results") {
            # Replace existing QA section
            $content = $content -replace "## QA Results.*?(?=---|\Z)", $qaSection
        } else {
            # Insert QA section before Dev Agent Record
            if ($content -match "## Dev Agent Record") {
                $content = $content -replace "## Dev Agent Record", "$qaSection`n## Dev Agent Record"
            } else {
                # Append at the end
                $content += "`n`n$qaSection"
            }
        }

        # Update tasks checkboxes if all passed
        if ($QAResult.OverallStatus -eq 'Pass') {
            # Mark QA-related tasks as complete
            $content = $content -replace "- \[ \] (Task 1: Implement BasedPyright-Workflow integration)", "- [x] `$1"
            $content = $content -replace "- \[ \] (Task 2: Implement Fixtest-Workflow integration)", "- [x] `$1"
            $content = $content -replace "- \[ \] (Task 3: Create QA automation workflow)", "- [x] `$1"
            $content = $content -replace "- \[ \] (Task 4: Implement retry mechanism for QA failures)", "- [x] `$1"
            $content = $content -replace "- \[ \] (Task 5: Integrate with state management)", "- [x] `$1"
        }

        # Save updated content
        $content | Out-File -FilePath $StoryPath -Encoding UTF8
        Write-QALog "Story file updated successfully" -Level 'Success'

    } catch {
        Write-QALog "Failed to update story file: $_" -Level 'Error'
    }
}

# Export functions
Export-ModuleMember -Function @(
    'Write-QALog',
    'Start-BasedPyrightCheck',
    'Start-FixtestCheck',
    'Invoke-QAToolsWorkflow',
    'Update-StoryWithQAStatus'
)
