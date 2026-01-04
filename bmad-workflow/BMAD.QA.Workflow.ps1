# BMAD QA Workflow Integration
# Integrates QA tools automation into the main BMAD workflow
# Version: 1.0.0

# Import QA integration module
$qaModulePath = Join-Path $PSScriptRoot "qa" "BMAD.QA.Integration.ps1"
if (Test-Path $qaModulePath) {
    . $qaModulePath
} else {
    Write-Host "WARNING: QA integration module not found at $qaModulePath" -ForegroundColor Yellow
}

function Start-QAToolsWorkflow {
    <#
    .SYNOPSIS
    Execute QA tools workflow as part of the BMAD process

    .PARAMETER ProjectRoot
    Root directory of the project

    .PARAMETER StoryPath
    Path to the story markdown file

    .PARAMETER WorkflowState
    Current workflow state object

    .PARAMETER Config
    Configuration object

    .PARAMETER MaxRetries
    Maximum retry attempts for QA tools

    .RETURNS
    QAAggregateResult object
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectRoot,

        [Parameter(Mandatory=$true)]
        [string]$StoryPath,

        [Parameter(Mandatory=$false)]
        [object]$WorkflowState = $null,

        [Parameter(Mandatory=$false)]
        [object]$Config = $null,

        [Parameter(Mandatory=$false)]
        [int]$MaxRetries = 2
    )

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Starting QA Tools Integration" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    try {
        # Import QA module
        $qaModule = Join-Path $PSScriptRoot "qa" "BMAD.QA.Integration.ps1"
        if (Test-Path $qaModule) {
            . $qaModule
        } else {
            throw "QA integration module not found"
        }

        # Determine output directory
        $outputDir = Join-Path $PSScriptRoot "logs" "qa"

        # Run QA workflow
        $qaResult = Invoke-QAToolsWorkflow -ProjectRoot $ProjectRoot -MaxRetries $MaxRetries -SaveResults -OutputDir $outputDir

        # Update story file with QA results
        if (Test-Path $StoryPath) {
            Update-StoryWithQAStatus -StoryPath $StoryPath -QAResult $qaResult -WorkflowState $WorkflowState
        }

        # Update workflow state
        if ($WorkflowState) {
            $WorkflowState.LastQAResult = $qaResult.OverallStatus.ToString()

            # Save QA state
            $qaStateDir = Join-Path $PSScriptRoot "logs" "workflow"
            if (-not (Test-Path $qaStateDir)) {
                New-Item -Path $qaStateDir -ItemType Directory -Force | Out-Null
            }

            $qaStateFile = Join-Path $qaStateDir "qa_state_$($WorkflowState.WorkflowId).json"
            $qaStateData = @{
                WorkflowId = $WorkflowState.WorkflowId
                Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                OverallStatus = $qaResult.OverallStatus.ToString()
                BasedPyrightStatus = $qaResult.BasedPyrightResult.Status.ToString()
                FixtestStatus = $qaResult.FixtestResult.Status.ToString()
                Violations = @{
                    BasedPyright = $qaResult.BasedPyrightResult.ViolationCount
                    Fixtest = $qaResult.FixtestResult.ViolationCount
                }
                RetryCount = $qaResult.RetryCount
                Duration = @{
                    BasedPyright = $qaResult.BasedPyrightResult.DurationSeconds
                    Fixtest = $qaResult.FixtestResult.DurationSeconds
                    Total = $qaResult.BasedPyrightResult.DurationSeconds + $qaResult.FixtestResult.DurationSeconds
                }
            }

            $qaStateData | ConvertTo-Json -Depth 10 | Out-File -FilePath $qaStateFile -Encoding UTF8
        }

        Write-Host ""
        Write-Host "QA Tools Integration Completed" -ForegroundColor Green
        Write-Host "Overall Status: $($qaResult.OverallStatus)" -ForegroundColor $(if($qaResult.OverallStatus -eq 'Pass'){'Green'}else{'Yellow'})
        Write-Host ""

        return $qaResult

    } catch {
        Write-Host "QA Tools Integration Failed: $_" -ForegroundColor Red
        throw
    }
}

function Test-QAToolsPrerequisites {
    <#
    .SYNOPSIS
    Test if QA tools prerequisites are met

    .PARAMETER ProjectRoot
    Root directory of the project

    .RETURNS
    Boolean indicating if prerequisites are met
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectRoot
    )

    Write-Host "Checking QA tools prerequisites..." -ForegroundColor Cyan

    $allGood = $true

    # Check BasedPyright workflow
    $basedpyrightDir = Join-Path $ProjectRoot "basedpyright-workflow"
    if (-not (Test-Path $basedpyrightDir)) {
        Write-Host "❌ BasedPyright-Workflow directory not found: $basedpyrightDir" -ForegroundColor Red
        $allGood = $false
    } else {
        Write-Host "✅ BasedPyright-Workflow directory found" -ForegroundColor Green
    }

    # Check Fixtest workflow
    $fixtestDir = Join-Path $ProjectRoot "fixtest-workflow"
    if (-not (Test-Path $fixtestDir)) {
        Write-Host "❌ Fixtest-Workflow directory not found: $fixtestDir" -ForegroundColor Red
        $allGood = $false
    } else {
        Write-Host "✅ Fixtest-Workflow directory found" -ForegroundColor Green
    }

    # Check Python availability
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python available: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python not available or not in PATH" -ForegroundColor Red
        $allGood = $false
    }

    # Check pytest availability
    try {
        $pytestVersion = pytest --version 2>&1
        Write-Host "✅ Pytest available: $pytestVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Pytest not available - Fixtest may not work properly" -ForegroundColor Yellow
    }

    return $allGood
}

function Get-QAToolsStatus {
    <#
    .SYNOPSIS
    Get current QA tools status

    .PARAMETER ProjectRoot
    Root directory of the project

    .RETURNS
    Hashtable with QA tools status
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ProjectRoot
    )

    $status = @{
        BasedPyright = @{
            Available = $false
            LastRun = $null
            LastStatus = $null
            ViolationCount = 0
        }
        Fixtest = @{
            Available = $false
            LastRun = $null
            LastStatus = $null
            TestFiles = 0
            FailedFiles = 0
        }
        Overall = @{
            Ready = $false
            LastCheck = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        }
    }

    # Check BasedPyright
    $basedpyrightDir = Join-Path $ProjectRoot "basedpyright-workflow"
    if (Test-Path $basedpyrightDir) {
        $status.BasedPyright.Available = $true

        $resultsDir = Join-Path $basedpyrightDir "results"
        if (Test-Path $resultsDir) {
            $latestFile = Get-ChildItem -Path $resultsDir -Filter "basedpyright_check_result_*.json" |
                          Sort-Object LastWriteTime -Descending |
                          Select-Object -First 1

            if ($latestFile) {
                $status.BasedPyright.LastRun = $latestFile.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")

                try {
                    $data = Get-Content $latestFile.FullName | ConvertFrom-Json
                    $status.BasedPyright.LastStatus = "Completed"
                    # Extract violation count from JSON
                    if ($data.PSObject.Properties.Name -contains 'errors') {
                        $status.BasedPyright.ViolationCount = ($data.errors | Measure-Object).Count
                    }
                } catch {
                    $status.BasedPyright.LastStatus = "Unknown"
                }
            }
        }
    }

    # Check Fixtest
    $fixtestDir = Join-Path $ProjectRoot "fixtest-workflow"
    if (Test-Path $fixtestDir) {
        $status.Fixtest.Available = $true

        $fileslistDir = Join-Path $fixtestDir "fileslist"
        if (Test-Path $fileslistDir) {
            $latestList = Get-ChildItem -Path $fileslistDir -Filter "test_files_list_*.json" |
                          Sort-Object LastWriteTime -Descending |
                          Select-Object -First 1

            if ($latestList) {
                try {
                    $data = Get-Content $latestList.FullName | ConvertFrom-Json
                    $status.Fixtest.TestFiles = $data.Count
                } catch {
                    $status.Fixtest.TestFiles = 0
                }
            }
        }

        $summariesDir = Join-Path $fixtestDir "summaries"
        if (Test-Path $summariesDir) {
            $latestSummary = Get-ChildItem -Path $summariesDir -Filter "test_results_summary_*.json" |
                             Sort-Object LastWriteTime -Descending |
                             Select-Object -First 1

            if ($latestSummary) {
                $status.Fixtest.LastRun = $latestSummary.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")

                try {
                    $data = Get-Content $latestSummary.FullName | ConvertFrom-Json
                    $status.Fixtest.LastStatus = if ($data.files_with_errors.Count -eq 0) { "All Passed" } else { "Has Failures" }
                    $status.Fixtest.FailedFiles = $data.files_with_errors.Count
                } catch {
                    $status.Fixtest.LastStatus = "Unknown"
                }
            }
        }
    }

    # Overall readiness
    $status.Overall.Ready = ($status.BasedPyright.Available -and $status.Fixtest.Available)

    return $status
}

# Export functions
Export-ModuleMember -Function @(
    'Start-QAToolsWorkflow',
    'Test-QAToolsPrerequisites',
    'Get-QAToolsStatus'
)
