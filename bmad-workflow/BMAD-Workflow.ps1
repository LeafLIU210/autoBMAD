# BMAD Workflow Automation - Main Entry Point
# This script provides easy access to the BMAD workflow system
# Version: 1.0.1 - Fixed logging and module imports

param(
    [Parameter(Mandatory=$false)]
    [string]$StoryPath,

    [Parameter(Mandatory=$false)]
    [string]$ConfigPath = $null,  # Auto-detect if not specified

    [Parameter(Mandatory=$false)]
    [switch]$Help,

    [Parameter(Mandatory=$false)]
    [switch]$Status,

    [Parameter(Mandatory=$false)]
    [switch]$Cleanup,

    [Parameter(Mandatory=$false)]
    [switch]$Test
)

# Get script directory (bmad-workflow directory)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Auto-detect workflow directory if running from parent directory
if ($ScriptDir -match "bmad-workflow$") {
    $WorkflowDir = $ScriptDir
} else {
    # If running from parent directory, find the bmad-workflow subdirectory
    $WorkflowDir = Join-Path $ScriptDir "bmad-workflow"
    if (-not (Test-Path $WorkflowDir)) {
        $WorkflowDir = $ScriptDir  # Fallback to current script directory
    }
}

# Create log directory and file
$logTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$logDirectory = Join-Path $WorkflowDir "logs"
$logFile = Join-Path $logDirectory "bmad-workflow-$logTimestamp.log"

# Ensure log directory exists
if (-not (Test-Path $logDirectory)) {
    try {
        New-Item -Path $logDirectory -ItemType Directory -Force | Out-Null
        Write-Host "Created log directory: $logDirectory" -ForegroundColor Green
    } catch {
        Write-Warning "Could not create log directory: $_"
    }
}

# Enhanced logging function
function Write-WorkflowLog {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,

        [Parameter(Mandatory=$false)]
        [ValidateSet('Info', 'Warning', 'Error', 'Success', 'Debug')]
        [string]$Level = 'Info',

        [Parameter(Mandatory=$false)]
        [switch]$NoConsole
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    # Write to console unless suppressed
    if (-not $NoConsole) {
        switch ($Level) {
            'Error' { Write-Host $logEntry -ForegroundColor Red }
            'Warning' { Write-Host $logEntry -ForegroundColor Yellow }
            'Success' { Write-Host $logEntry -ForegroundColor Green }
            'Info' { Write-Host $logEntry -ForegroundColor Cyan }
            'Debug' { Write-Host $logEntry -ForegroundColor Gray }
            default { Write-Host $logEntry }
        }
    }

    # Always write to log file
    try {
        $logEntry | Out-File -FilePath $logFile -Append -Encoding UTF8 -ErrorAction SilentlyContinue
    } catch {
        Write-Warning "Failed to write to log file: $_"
    }
}

# Auto-detect config path if not specified
if (-not $ConfigPath) {
    $defaultConfigPath = Join-Path $WorkflowDir "workflow.config.yaml"
    if (Test-Path $defaultConfigPath) {
        $ConfigPath = $defaultConfigPath
    } else {
        Write-Error "Configuration file not found in $WorkflowDir"
        exit 1
    }
}

# Start logging immediately
Write-WorkflowLog "BMAD Workflow started" -Level 'Info'
Write-WorkflowLog "Script Directory: $ScriptDir" -Level 'Debug'
Write-WorkflowLog "Workflow Directory: $WorkflowDir" -Level 'Debug'
Write-WorkflowLog "Log File: $logFile" -Level 'Debug'
Write-WorkflowLog "Story Path: $StoryPath" -Level 'Info'
Write-WorkflowLog "Config Path: $ConfigPath" -Level 'Info'

# Import required modules with error handling
$modulesToImport = @(
    "BMAD.Workflow.Core.ps1",
    "BMAD.Claude.Interface.ps1",
    "BMAD.Job.Manager.ps1",
    "BMAD.State.Manager.ps1",
    "BMAD.Hooks.Handler.ps1"
)

$importedModules = @()
$failedModules = @()

Write-WorkflowLog "Importing BMAD workflow modules..." -Level 'Info'

foreach ($module in $modulesToImport) {
    $modulePath = Join-Path $WorkflowDir $module

    if (Test-Path $modulePath) {
        try {
            # Use dot-sourcing instead of Import-Module for better compatibility
            . $modulePath
            $importedModules += $module
            Write-WorkflowLog "✓ Successfully loaded: $module" -Level 'Success'
        } catch {
            $errorMsg = "✗ Failed to load $module`: $_"
            $failedModules += "$module`: $_"
            Write-WorkflowLog $errorMsg -Level 'Error'
        }
    } else {
        $errorMsg = "✗ Module file not found: $modulePath"
        $failedModules += "$module`: File not found"
        Write-WorkflowLog $errorMsg -Level 'Error'
    }
}

Write-WorkflowLog "Module import complete. Success: $($importedModules.Count), Failed: $($failedModules.Count)" -Level 'Info'

if ($failedModules.Count -gt 0) {
    Write-WorkflowLog "Failed modules: $($failedModules -join '; ')" -Level 'Warning'
    Write-WorkflowLog "Continuing with available functionality..." -Level 'Warning'
}

# Main functionality
if ($Help) {
    Write-WorkflowLog "Displaying help information" -Level 'Info'
    Write-Host @"
BMAD Workflow Automation

USAGE:
    .\BMAD-Workflow.ps1 -StoryPath <path> [options]

PARAMETERS:
    -StoryPath <path>     Path to the story document to process
    -ConfigPath <path>    Path to workflow configuration (default: ./config/workflow.config.yaml)
    -Help                 Show this help message
    -Status               Show system status
    -Cleanup              Cleanup old workflows and logs
    -Test                 Run system tests

EXAMPLES:
    .\BMAD-Workflow.ps1 -StoryPath "./docs/stories/example-story.md"
    .\BMAD-Workflow.ps1 -StoryPath "docs\stories\sample-bubble-sort-story.md"
    .\BMAD-Workflow.ps1 -Status
    .\BMAD-Workflow.ps1 -Cleanup
"@
    Write-WorkflowLog "Help displayed, exiting" -Level 'Info'
    exit 0
}

if ($Status) {
    Write-WorkflowLog "Checking system status" -Level 'Info'
    Write-Host "BMAD Workflow System Status" -ForegroundColor Cyan
    Write-Host "=========================="

    try {
        # Show job statistics
        if (Get-Command Get-JobPoolStatistics -ErrorAction SilentlyContinue) {
            $stats = Get-JobPoolStatistics
            Write-Host "Job Statistics:" -ForegroundColor Yellow
            $stats.PSObject.Properties | ForEach-Object {
                Write-Host "  $($_.Name): $($_.Value)"
                Write-WorkflowLog "Job stat - $($_.Name): $($_.Value)" -Level 'Debug'
            }
        } else {
            Write-Host "Job manager not available" -ForegroundColor Yellow
            Write-WorkflowLog "Job manager not available" -Level 'Warning'
        }

        # Show hook handler status
        if (Get-Command Get-HookHandlerStatus -ErrorAction SilentlyContinue) {
            $hookStatus = Get-HookHandlerStatus
            Write-Host "`nHook Handlers:" -ForegroundColor Yellow
            Write-Host "  Total Handlers: $($hookStatus.TotalHandlers)"
            Write-Host "  Hook Directory: $($hookStatus.HookDirectory)"
            Write-WorkflowLog "Hook handlers loaded: $($hookStatus.TotalHandlers)" -Level 'Debug'
        } else {
            Write-Host "`nHook handlers not available" -ForegroundColor Yellow
            Write-WorkflowLog "Hook handlers not available" -Level 'Warning'
        }

        # Show available workflows
        if (Get-Command Get-AvailableWorkflows -ErrorAction SilentlyContinue) {
            $workflows = Get-AvailableWorkflows
            Write-Host "`nAvailable Workflows: $($workflows.Count)" -ForegroundColor Yellow
            foreach ($workflow in $workflows) {
                Write-Host "  - $workflow"
                Write-WorkflowLog "Available workflow: $workflow" -Level 'Debug'
            }
        } else {
            Write-Host "`nWorkflow management not available" -ForegroundColor Yellow
            Write-WorkflowLog "Workflow management not available" -Level 'Warning'
        }

        Write-WorkflowLog "System status check completed" -Level 'Success'

    } catch {
        $errorMsg = "Status check failed: $_"
        Write-WorkflowLog $errorMsg -Level 'Error'
        Write-Warning $errorMsg
    }

    exit 0
}

if ($Cleanup) {
    Write-WorkflowLog "Starting cleanup process" -Level 'Info'
    Write-Host "Cleaning up old workflows and logs..." -ForegroundColor Cyan

    try {
        # Remove old workflow states
        if (Get-Command Get-AvailableWorkflows -ErrorAction SilentlyContinue) {
            $workflows = Get-AvailableWorkflows
            $cleanupCount = 0

            foreach ($workflow in $workflows) {
                $state = Load-WorkflowState -WorkflowId $workflow
                if ($state -and $state.EndTime -and ((Get-Date) - $state.EndTime).TotalDays -gt 7) {
                    Remove-WorkflowState -WorkflowId $workflow
                    $cleanupCount++
                    Write-WorkflowLog "Cleaned up workflow: $workflow" -Level 'Debug'
                }
            }

            Write-Host "Cleaned up $cleanupCount old workflows" -ForegroundColor Green
            Write-WorkflowLog "Cleanup completed: $cleanupCount workflows removed" -Level 'Success'
        } else {
            Write-WorkflowLog "Workflow management not available for cleanup" -Level 'Warning'
        }

        # Rotate logs
        if (Get-Command Invoke-LogRotation -ErrorAction SilentlyContinue) {
            Invoke-LogRotation
            Write-WorkflowLog "Log rotation completed" -Level 'Debug'
        }

        Write-Host "Cleanup completed" -ForegroundColor Green
        Write-WorkflowLog "Cleanup process finished" -Level 'Success'

    } catch {
        $errorMsg = "Cleanup failed: $_"
        Write-WorkflowLog $errorMsg -Level 'Error'
        Write-Warning $errorMsg
    }

    exit 0
}

if ($Test) {
    Write-WorkflowLog "Running system tests" -Level 'Info'
    Write-Host "Running system tests..." -ForegroundColor Cyan

    # Test imported modules
    Write-WorkflowLog "Testing imported modules: $($importedModules.Count)" -Level 'Info'
    foreach ($module in $importedModules) {
        Write-Host "✓ $module module loaded successfully" -ForegroundColor Green
        Write-WorkflowLog "Module test passed: $module" -Level 'Success'
    }

    # Test failed modules
    if ($failedModules.Count -gt 0) {
        foreach ($failedModule in $failedModules) {
            Write-Host "✗ Failed module: $failedModule" -ForegroundColor Red
            Write-WorkflowLog "Module test failed: $failedModule" -Level 'Error'
        }
    }

    # Test configuration file
    if (Test-Path $ConfigPath) {
        Write-Host "✓ Configuration file exists: $ConfigPath" -ForegroundColor Green
        Write-WorkflowLog "Configuration file test passed: $ConfigPath" -Level 'Success'
    } else {
        Write-Host "✗ Configuration file missing: $ConfigPath" -ForegroundColor Red
        Write-WorkflowLog "Configuration file test failed: $ConfigPath" -Level 'Error'
    }

    # Test Claude CLI availability
    $claudeAvailable = Get-Command "claude" -ErrorAction SilentlyContinue
    if ($claudeAvailable) {
        Write-Host "✓ Claude Code CLI found at: $($claudeAvailable.Source)" -ForegroundColor Green
        Write-WorkflowLog "Claude CLI test passed: $($claudeAvailable.Source)" -Level 'Success'
    } else {
        Write-Host "✗ Claude Code CLI not found in PATH" -ForegroundColor Red
        Write-WorkflowLog "Claude CLI test failed: Not in PATH" -Level 'Error'
    }

    # Test log file creation
    if (Test-Path $logFile) {
        Write-Host "✓ Log file created successfully: $logFile" -ForegroundColor Green
        Write-WorkflowLog "Log file test passed: $logFile" -Level 'Success'
    } else {
        Write-Host "✗ Log file creation failed" -ForegroundColor Red
        Write-WorkflowLog "Log file test failed: Could not create log file" -Level 'Error'
    }

    Write-Host "System tests completed" -ForegroundColor Cyan
    Write-WorkflowLog "System tests completed" -Level 'Success'
    exit 0
}

# Run workflow
Write-WorkflowLog "Starting main workflow execution" -Level 'Info'

# Validate StoryPath for main workflow execution
if (-not $StoryPath) {
    $errorMsg = "StoryPath is required for workflow execution. Use -Help for usage information."
    Write-WorkflowLog $errorMsg -Level 'Error'
    Write-Error $errorMsg
    exit 1
}

if (-not (Test-Path $StoryPath)) {
    $errorMsg = "Story file not found: $StoryPath"
    Write-WorkflowLog $errorMsg -Level 'Error'
    Write-Error $errorMsg
    exit 1
}

Write-Host "Starting BMAD workflow for: $StoryPath" -ForegroundColor Cyan
Write-Host "Configuration: $ConfigPath" -ForegroundColor Gray
Write-Host "Log file: $logFile" -ForegroundColor Gray

try {
    Write-WorkflowLog "Initializing workflow environment" -Level 'Info'
    Write-Host "Workflow started at $(Get-Date)" -ForegroundColor Green
    Write-Host "Story Path: $StoryPath" -ForegroundColor Gray
    Write-Host "Config Path: $ConfigPath" -ForegroundColor Gray
    Write-Host "Log File: $logFile" -ForegroundColor Gray
    Write-Host "----------------------------------------" -ForegroundColor Gray

    # Check if main workflow function is available
    if (Get-Command Start-BMADWorkflow -ErrorAction SilentlyContinue) {
        Write-WorkflowLog "Starting BMAD workflow execution" -Level 'Info'
        Write-Host "Starting BMAD workflow execution..." -ForegroundColor Yellow

        $result = Start-BMADWorkflow -StoryPath $StoryPath -ConfigPath $ConfigPath

        Write-Host "----------------------------------------" -ForegroundColor Gray
        Write-Host "Workflow completed at $(Get-Date)" -ForegroundColor Green
        Write-Host "Status: $($result.Status)" -ForegroundColor $(if($result.Status -eq 'Completed'){'Green'}else{'Yellow'})
        Write-Host "Duration: $(($result.EndTime - $result.StartTime).ToString('hh\:mm\:ss'))" -ForegroundColor Cyan
        Write-Host "Iterations: $($result.IterationCount)" -ForegroundColor Cyan
        Write-Host "Jobs Executed: $($result.Jobs.Count)" -ForegroundColor Cyan

        Write-WorkflowLog "Workflow execution completed" -Level 'Info'
        Write-WorkflowLog "Final Status: $($result.Status)" -Level 'Info'
        Write-WorkflowLog "Duration: $(($result.EndTime - $result.StartTime).ToString('hh\:mm\:ss'))" -Level 'Info'
        Write-WorkflowLog "Iterations: $($result.IterationCount)" -Level 'Info'
        Write-WorkflowLog "Jobs Executed: $($result.Jobs.Count)" -Level 'Info'

        # Show summary if available
        if (Get-Command Get-WorkflowSummary -ErrorAction SilentlyContinue) {
            $summary = Get-WorkflowSummary -State $result
            Write-Host "`nWorkflow Summary:" -ForegroundColor Yellow
            Write-Host $summary -ForegroundColor White
            Write-WorkflowLog "Workflow summary generated" -Level 'Debug'
        }

        Write-Host "`nLog file saved to: $logFile" -ForegroundColor Green

        # Exit with appropriate code
        if ($result.Status -eq 'Completed') {
            Write-Host "✓ Workflow completed successfully!" -ForegroundColor Green
            Write-WorkflowLog "Workflow completed successfully" -Level 'Success'
            exit 0
        } else {
            Write-Host "⚠ Workflow completed with issues. Check logs for details." -ForegroundColor Yellow
            Write-WorkflowLog "Workflow completed with issues" -Level 'Warning'
            exit 1
        }
    } else {
        $errorMsg = "Start-BMADWorkflow function not available - modules may not have loaded correctly"
        Write-WorkflowLog $errorMsg -Level 'Error'
        Write-Host "✗ $errorMsg" -ForegroundColor Red
        Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
        Write-Host "1. Check if all module files exist in src/ directory" -ForegroundColor White
        Write-Host "2. Verify PowerShell execution policy allows script execution" -ForegroundColor White
        Write-Host "3. Run '.\BMAD-Workflow.ps1 -Test' for diagnostic information" -ForegroundColor White
        Write-Host "4. Check log file for detailed error information: $logFile" -ForegroundColor White

        exit 1
    }

} catch {
    $errorMsg = "Workflow failed: $_"
    Write-Host "----------------------------------------" -ForegroundColor Gray
    Write-Error $errorMsg
    Write-Host "Log file: $logFile" -ForegroundColor Yellow
    Write-WorkflowLog $errorMsg -Level 'Error'
    Write-WorkflowLog "Stack trace: $($_.ScriptStackTrace)" -Level 'Error'
    exit 1
}