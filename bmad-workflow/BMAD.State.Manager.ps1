# BMAD.State.Manager.ps1 (Clean Version)
# Simplified workflow state management and logging module

# Simple logging function (replaces the complex class-based version)
function Write-WorkflowLogInternal {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,

        [Parameter(Mandatory=$true)]
        [object]$Level,

        [Parameter(Mandatory=$false)]
        [object]$State = $null
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"

    # Extract workflow ID from state object if provided
    $workflowId = ""
    if ($State -and $State.WorkflowId) {
        $workflowId = $State.WorkflowId
    }

    $logEntry = "[$timestamp] [$Level] Workflow:$workflowId - $Message"

    # Output to console
    switch ($Level) {
        "Error" { Write-Host $logEntry -ForegroundColor Red }
        "Warning" { Write-Host $logEntry -ForegroundColor Yellow }
        "Success" { Write-Host $logEntry -ForegroundColor Green }
        default { Write-Host $logEntry -ForegroundColor White }
    }

    # Output to log file if it exists
    try {
        $logFile = $env:BMAD_LOG_FILE
        if ($logFile -and (Test-Path $logFile)) {
            $logEntry | Out-File -FilePath $logFile -Append -Encoding UTF8
        }
    } catch {
        # Fail silently if logging fails
    }
}

# Simple state management (replaces complex class-based version)
function Save-WorkflowState {
    param(
        [object]$state,
        [string]$workflowId = ""
    )

    try {
        $stateDir = "./logs/workflow"
        if (-not (Test-Path $stateDir)) {
            New-Item -Path $stateDir -ItemType Directory -Force | Out-Null
        }

        $stateFile = Join-Path $stateDir "$workflowId.json"
        $state | ConvertTo-Json -Depth 10 | Out-File -FilePath $stateFile -Encoding UTF8

        Write-WorkflowLogInternal -Message "Workflow state saved for: $workflowId" -Level "Success" -State @{WorkflowId = $workflowId}
    } catch {
        Write-WorkflowLogInternal -Message "Failed to save workflow state: $_" -Level "Error" -State @{WorkflowId = $workflowId}
    }
}

function Load-WorkflowState {
    param([string]$workflowId = "")

    try {
        $stateFile = "./logs/workflow/$workflowId.json"

        if (-not (Test-Path $stateFile)) {
            return $null
        }

        $stateData = Get-Content $stateFile | ConvertFrom-Json
        return $stateData
    } catch {
        Write-WorkflowLogInternal -Message "Failed to load workflow state: $_" -Level "Error" -State @{WorkflowId = $workflowId}
        return $null
    }
}

function Get-AvailableWorkflows {
    try {
        $stateDir = "./logs/workflow"
        if (-not (Test-Path $stateDir)) {
            return @()
        }

        $stateFiles = Get-ChildItem (Join-Path $stateDir "*.json") -ErrorAction SilentlyContinue
        return $stateFiles | ForEach-Object { $_.BaseName }
    } catch {
        Write-WorkflowLogInternal -Message "Failed to get available workflows: $_" -Level "Error" -State $null
        return @()
    }
}

function Remove-WorkflowState {
    param([string]$workflowId = "")

    try {
        $stateFile = "./logs/workflow/$workflowId.json"
        if (Test-Path $stateFile) {
            Remove-Item $stateFile -Force
            Write-WorkflowLogInternal -Message "Workflow state removed for: $workflowId" -Level "Success" -State @{WorkflowId = $workflowId}
        }
    } catch {
        Write-WorkflowLogInternal -Message "Failed to remove workflow state: $_" -Level "Error" -State @{WorkflowId = $workflowId}
    }
}

# Simple rotation function
function Invoke-LogRotation {
    try {
        $logDir = "./logs"
        if (Test-Path $logDir) {
            $oldLogs = Get-ChildItem (Join-Path $logDir "bmad-workflow-*.log") -ErrorAction SilentlyContinue
            $cutoffDate = (Get-Date).AddDays(-30)

            $oldLogs | Where-Object { $_.LastWriteTime -lt $cutoffDate } | Remove-Item -Force
        }
    } catch {
        Write-WorkflowLogInternal -Message "Failed to rotate logs: $_" -Level "Error" -State $null
    }
}

# Configuration loading function
function Get-WorkflowConfig {
    param([string]$ConfigPath = "./config/workflow.config.yaml")

    try {
        if (Test-Path $ConfigPath) {
            # Try to load YAML config first
            try {
                # Check if ConvertFrom-Yaml is available
                if (Get-Command ConvertFrom-Yaml -ErrorAction SilentlyContinue) {
                    $configData = Get-Content $ConfigPath -Raw | ConvertFrom-Yaml
                    Write-WorkflowLogInternal -Message "Loaded configuration from YAML: $ConfigPath" -Level "Success" -State $null
                    return $configData
                } else {
                    # Fallback: Simple YAML parsing for our specific structure
                    $configData = @{
                        workflow = @{
                            max_iterations = 10
                            job_timeout_seconds = 3600
                            concurrent_dev_flows = 3
                            enable_persistence = $true
                            auto_cleanup = $true
                            phase_delay_minutes = 30  # Default value
                        }
                        development = @{
                            mock_mode = $false
                            mock_execution_time_range = @{
                                min = 2
                                max = 5
                            }
                        }
                        claude = @{
                            timeout_minutes = 60
                            retry_attempts = 3
                            cli_path = "claude"
                            dangerous_skip_permissions = $true
                        }
                    }

                    # Read the YAML file manually to extract key values
                    $content = Get-Content $ConfigPath -Raw

                    # Extract phase_delay_minutes
                    if ($content -match 'phase_delay_minutes:\s*(\d+)') {
                        $phaseDelay = [int]$matches[1]
                        $configData.workflow.phase_delay_minutes = $phaseDelay
                        Write-WorkflowLogInternal -Message "Extracted phase_delay_minutes: $phaseDelay using simple parsing" -Level "Success" -State $null
                    }

                    # Extract mock_mode
                    if ($content -match 'mock_mode:\s*(true|false)') {
                        $mockMode = [bool]::Parse($matches[1])
                        $configData.development.mock_mode = $mockMode
                        Write-WorkflowLogInternal -Message "Extracted mock_mode: $mockMode using simple parsing" -Level "Debug" -State $null
                    }

                    # Extract mock execution time range
                    if ($content -match 'mock_execution_time_range:\s*\n\s*min:\s*(\d+).*max:\s*(\d+)') {
                        $minTime = [int]$matches[1]
                        $maxTime = [int]$matches[2]
                        $configData.development.mock_execution_time_range.min = $minTime
                        $configData.development.mock_execution_time_range.max = $maxTime
                        Write-WorkflowLogInternal -Message "Extracted mock execution range: $minTime-$maxTime using simple parsing" -Level "Debug" -State $null
                    }

                    return $configData
                }
            } catch {
                Write-WorkflowLogInternal -Message "Failed to parse YAML config, using defaults: $_" -Level "Warning" -State $null
            }

            # Create default config structure with updated phase_delay_minutes
            $config = @{
                workflow = @{
                    max_iterations = 10
                    job_timeout_seconds = 3600
                    concurrent_dev_flows = 3
                    enable_persistence = $true
                    auto_cleanup = $true
                    phase_delay_minutes = 30  # Updated to use minutes instead of seconds
                }
                claude = @{
                    cli_path = "claude"
                    skip_permissions = $true
                    command_delay_seconds = 2
                    initialization_timeout_seconds = 30
                    window_style = "Normal"
                    enable_hooks = $true
                }
                logging = @{
                    level = "Info"
                    base_log_directory = "./logs"
                    console_output = $true
                    structured_logging = $true
                }
            }

            return $config
        } else {
            # Return default config with updated phase_delay_minutes
            return @{
                workflow = @{
                    max_iterations = 10
                    job_timeout_seconds = 3600
                    concurrent_dev_flows = 3
                    enable_persistence = $true
                    auto_cleanup = $true
                    phase_delay_minutes = 30  # Updated to use minutes instead of seconds
                }
                claude = @{
                    cli_path = "claude"
                    skip_permissions = $true
                    command_delay_seconds = 2
                    initialization_timeout_seconds = 30
                    window_style = "Normal"
                    enable_hooks = $true
                }
                logging = @{
                    level = "Info"
                    base_log_directory = "./logs"
                    console_output = $true
                    structured_logging = $true
                }
            }
        }
    } catch {
        Write-WorkflowLogInternal -Message "Failed to load config from $ConfigPath`: $_" -Level "Error" -State $null
        # Return default config on error
        return @{
            "max_iterations" = "10"
            "claude_timeout" = "300"
            "dev_agents" = "3"
            "qa_agents" = "1"
        }
    }
}

Write-Host "BMAD.State.Manager (Simplified) loaded successfully" -ForegroundColor Green