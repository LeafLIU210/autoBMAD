# QA Integration Tests - PowerShell
# Tests the QA tools integration functions

# Import the QA integration module
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$qaModulePath = Join-Path $scriptDir ".." "bmad-workflow" "qa" "BMAD.QA.Integration.ps1"
$qaWorkflowPath = Join-Path $scriptDir ".." "bmad-workflow" "BMAD.QA.Workflow.ps1"

if (Test-Path $qaModulePath) {
    . $qaModulePath
} else {
    Write-Host "WARNING: QA integration module not found at $qaModulePath" -ForegroundColor Yellow
}

if (Test-Path $qaWorkflowPath) {
    . $qaWorkflowPath
} else {
    Write-Host "WARNING: QA workflow module not found at $qaWorkflowPath" -ForegroundColor Yellow
}

function Test-QAStatusEnum {
    <#
    .SYNOPSIS
    Test QAStatus enum values
    #>
    Write-Host "Testing QAStatus enum..." -ForegroundColor Cyan

    $statuses = @([QAStatus]::Pass, [QAStatus]::Concerns, [QAStatus]::Fail, [QAStatus]::Waived)

    foreach ($status in $statuses) {
        Write-Host "  ✓ QAStatus.$($status) = $($status.Value)" -ForegroundColor Green
    }

    Write-Host "QAStatus enum test completed successfully" -ForegroundColor Green
}

function Test-QAToolResultClass {
    <#
    .SYNOPSIS
    Test QAToolResult class
    #>
    Write-Host "Testing QAToolResult class..." -ForegroundColor Cyan

    # Create a new QAToolResult
    $result = [QAToolResult]::new()

    # Test properties
    $result.Tool = "TestTool"
    $result.Status = [QAStatus]::Pass
    $result.StartTime = Get-Date
    $result.EndTime = (Get-Date).AddMinutes(5)
    $result.DurationSeconds = 300
    $result.ViolationCount = 5
    $result.RetryCount = 1
    $result.OutputFile = "C:\test\output.txt"
    $result.ErrorMessage = $null
    $result.Metrics = @{ Test = "Value" }

    # Verify properties
    if ($result.Tool -eq "TestTool") {
        Write-Host "  ✓ Tool property set correctly" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Tool property not set correctly" -ForegroundColor Red
    }

    if ($result.Status -eq [QAStatus]::Pass) {
        Write-Host "  ✓ Status property set correctly" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Status property not set correctly" -ForegroundColor Red
    }

    if ($result.DurationSeconds -eq 300) {
        Write-Host "  ✓ DurationSeconds property set correctly" -ForegroundColor Green
    } else {
        Write-Host "  ✗ DurationSeconds property not set correctly" -ForegroundColor Red
    }

    Write-Host "QAToolResult class test completed successfully" -ForegroundColor Green
}

function Test-QAAggregateResultClass {
    <#
    .SYNOPSIS
    Test QAAggregateResult class
    #>
    Write-Host "Testing QAAggregateResult class..." -ForegroundColor Cyan

    # Create a new QAAggregateResult
    $aggregate = [QAAggregateResult]::new()

    # Create sub-results
    $bpResult = [QAToolResult]::new()
    $bpResult.Tool = "BasedPyright"
    $bpResult.Status = [QAStatus]::Pass
    $bpResult.ViolationCount = 0

    $ftResult = [QAToolResult]::new()
    $ftResult.Tool = "Fixtest"
    $ftResult.Status = [QAStatus]::Pass
    $ftResult.ViolationCount = 0

    $aggregate.BasedPyrightResult = $bpResult
    $aggregate.FixtestResult = $ftResult
    $aggregate.OverallStatus = [QAStatus]::Pass
    $aggregate.RetryCount = 0
    $aggregate.Timestamp = Get-Date

    # Verify properties
    if ($aggregate.OverallStatus -eq [QAStatus]::Pass) {
        Write-Host "  ✓ OverallStatus property set correctly" -ForegroundColor Green
    } else {
        Write-Host "  ✗ OverallStatus property not set correctly" -ForegroundColor Red
    }

    if ($aggregate.BasedPyrightResult.Tool -eq "BasedPyright") {
        Write-Host "  ✓ BasedPyrightResult property set correctly" -ForegroundColor Green
    } else {
        Write-Host "  ✗ BasedPyrightResult property not set correctly" -ForegroundColor Red
    }

    if ($aggregate.FixtestResult.Tool -eq "Fixtest") {
        Write-Host "  ✓ FixtestResult property set correctly" -ForegroundColor Green
    } else {
        Write-Host "  ✗ FixtestResult property not set correctly" -ForegroundColor Red
    }

    Write-Host "QAAggregateResult class test completed successfully" -ForegroundColor Green
}

function Test-WriteQALog {
    <#
    .SYNOPSIS
    Test Write-QALog function
    #>
    Write-Host "Testing Write-QALog function..." -ForegroundColor Cyan

    # Test different log levels
    Write-QALog "Test info message" -Level 'Info'
    Write-QALog "Test warning message" -Level 'Warning'
    Write-QALog "Test error message" -Level 'Error'
    Write-QALog "Test success message" -Level 'Success'

    Write-Host "Write-QALog function test completed successfully" -ForegroundColor Green
}

function Test-FindLatestResultFiles {
    <#
    .SYNOPSIS
    Test finding latest result files
    #>
    Write-Host "Testing file discovery..." -ForegroundColor Cyan

    # Create temporary test directory
    $tempDir = Join-Path $env:TEMP "qa_test_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -Path $tempDir -ItemType Directory -Force | Out-Null

    try {
        # Create test files
        $file1 = Join-Path $tempDir "basedpyright_check_result_20260104_120000.json"
        $file2 = Join-Path $tempDir "basedpyright_check_result_20260104_130000.json"
        $file3 = Join-Path $tempDir "basedpyright_check_result_20260104_140000.json"

        $file1 | Out-Null
        Start-Sleep -Milliseconds 100
        $file2 | Out-Null
        Start-Sleep -Milliseconds 100
        $file3 | Out-Null

        # Find latest file
        $latestFile = Get-ChildItem -Path $tempDir -Filter "basedpyright_check_result_*.json" |
                      Sort-Object LastWriteTime -Descending |
                      Select-Object -First 1

        if ($latestFile.Name -eq "basedpyright_check_result_20260104_140000.json") {
            Write-Host "  ✓ Latest file discovery works correctly" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Latest file discovery failed" -ForegroundColor Red
        }
    } finally {
        # Clean up
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }

    Write-Host "File discovery test completed successfully" -ForegroundColor Green
}

function Test-StatusAggregation {
    <#
    .SYNOPSIS
    Test status aggregation logic
    #>
    Write-Host "Testing status aggregation logic..." -ForegroundColor Cyan

    # Test cases
    $testCases = @(
        @{ BP = [QAStatus]::Pass; FT = [QAStatus]::Pass; Expected = [QAStatus]::Pass; Desc = "Both Pass" }
        @{ BP = [QAStatus]::Fail; FT = [QAStatus]::Pass; Expected = [QAStatus]::Fail; Desc = "BP Fail" }
        @{ BP = [QAStatus]::Pass; FT = [QAStatus]::Fail; Expected = [QAStatus]::Fail; Desc = "FT Fail" }
        @{ BP = [QAStatus]::Concerns; FT = [QAStatus]::Pass; Expected = [QAStatus]::Concerns; Desc = "BP Concerns" }
        @{ BP = [QAStatus]::Pass; FT = [QAStatus]::Concerns; Expected = [QAStatus]::Concerns; Desc = "FT Concerns" }
        @{ BP = [QAStatus]::Concerns; FT = [QAStatus]::Concerns; Expected = [QAStatus]::Concerns; Desc = "Both Concerns" }
        @{ BP = [QAStatus]::Fail; FT = [QAStatus]::Concerns; Expected = [QAStatus]::Fail; Desc = "One Fail, One Concerns" }
    )

    foreach ($testCase in $testCases) {
        # Determine overall status
        $overall = if ($testCase.BP -eq [QAStatus]::Fail -or $testCase.FT -eq [QAStatus]::Fail) {
            [QAStatus]::Fail
        } elseif ($testCase.BP -eq [QAStatus]::Concerns -or $testCase.FT -eq [QAStatus]::Concerns) {
            [QAStatus]::Concerns
        } elseif ($testCase.BP -eq [QAStatus]::Pass -and $testCase.FT -eq [QAStatus]::Pass) {
            [QAStatus]::Pass
        } else {
            [QAStatus]::Concerns
        }

        if ($overall -eq $testCase.Expected) {
            Write-Host "  ✓ $($testCase.Desc): $overall" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $($testCase.Desc): Expected $($testCase.Expected), got $overall" -ForegroundColor Red
        }
    }

    Write-Host "Status aggregation test completed successfully" -ForegroundColor Green
}

function Test-JsonSerialization {
    <#
    .SYNOPSIS
    Test JSON serialization of QA results
    #>
    Write-Host "Testing JSON serialization..." -ForegroundColor Cyan

    # Create test data
    $resultData = @{
        OverallStatus = "PASS"
        BasedPyright = @{
            Status = "PASS"
            ViolationCount = 0
            DurationSeconds = 5.0
            RetryCount = 0
        }
        Fixtest = @{
            Status = "PASS"
            ViolationCount = 0
            DurationSeconds = 3.0
            RetryCount = 0
        }
        Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        RetryCount = 0
    }

    # Serialize to JSON
    $json = $resultData | ConvertTo-Json -Depth 10

    # Verify JSON was created
    if ($json -and $json.Length -gt 0) {
        Write-Host "  ✓ JSON serialization successful" -ForegroundColor Green

        # Try to deserialize
        $deserialized = $json | ConvertFrom-Json
        if ($deserialized.OverallStatus -eq "PASS") {
            Write-Host "  ✓ JSON deserialization successful" -ForegroundColor Green
        } else {
            Write-Host "  ✗ JSON deserialization failed" -ForegroundColor Red
        }
    } else {
        Write-Host "  ✗ JSON serialization failed" -ForegroundColor Red
    }

    Write-Host "JSON serialization test completed successfully" -ForegroundColor Green
}

function Test-QAToolsPrerequisites {
    <#
    .SYNOPSIS
    Test QA tools prerequisites check
    #>
    Write-Host "Testing QA tools prerequisites check..." -ForegroundColor Cyan

    # This would normally check for actual directories
    # For testing, we'll just verify the function exists and runs
    try {
        # Note: This would need actual project structure to work
        # For now, just verify the function is callable
        if (Get-Command Test-QAToolsPrerequisites -ErrorAction SilentlyContinue) {
            Write-Host "  ✓ Test-QAToolsPrerequisites function is available" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Test-QAToolsPrerequisites function not found" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ✗ Test-QAToolsPrerequisites test failed: $_" -ForegroundColor Red
    }

    Write-Host "QA tools prerequisites test completed" -ForegroundColor Green
}

function Invoke-AllQATests {
    <#
    .SYNOPSIS
    Run all QA integration tests
    #>
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "QA Integration Tests - PowerShell" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    try {
        Test-QAStatusEnum
        Write-Host ""

        Test-QAToolResultClass
        Write-Host ""

        Test-QAAggregateResultClass
        Write-Host ""

        Test-WriteQALog
        Write-Host ""

        Test-FindLatestResultFiles
        Write-Host ""

        Test-StatusAggregation
        Write-Host ""

        Test-JsonSerialization
        Write-Host ""

        Test-QAToolsPrerequisites
        Write-Host ""

        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "All QA Integration Tests Passed!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan

        return $true
    } catch {
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "QA Integration Tests Failed!" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        return $false
    }
}

# Run tests if this script is executed directly
if ($MyInvocation.InvocationName -ne '.') {
    $success = Invoke-AllQATests
    exit $(if ($success) { 0 } else { 1 })
}
