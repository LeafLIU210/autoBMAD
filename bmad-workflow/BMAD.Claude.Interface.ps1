# BMAD.Claude.Interface.Fixed.ps1
# Fixed version of Claude Code CLI integration module
# Solves the long prompt issue by using file-based input

# Load the command mapper module
$mapperPath = Join-Path $PSScriptRoot "BMAD.Command.Mapper.ps1"
if (Test-Path $mapperPath) {
    . $mapperPath
} else {
    Write-Warning "BMAD Command Mapper not found at: $mapperPath"
    throw "Required BMAD.Command.Mapper module is missing"
}

# Stub function for Claude session detection
function Get-ClaudeSessionId {
    <#
    .SYNOPSIS
    Stub function for detecting Claude session ID.

    .DESCRIPTION
    This is a placeholder function for future session tracking functionality.
    Currently returns null as Claude session detection is not implemented.

    .PARAMETER ProcessId
    Process ID of the Claude CLI process

    .PARAMETER MaxAgeSeconds
    Maximum age of the session in seconds (unused in stub)
    #>
    param(
        [Parameter(Mandatory = $true)]
        [int]$ProcessId,

        [Parameter(Mandatory = $false)]
        [int]$MaxAgeSeconds = 30
    )

    # TODO: Implement actual Claude session detection
    # For now, return null to indicate session detection is not available
    return $null
}

# Function to start Claude development flow with phase-specific configuration
function Start-ClaudeDevFlow {
    param(
        [string]$StoryPath = "",
        [string]$InstanceId = "",
        [bool]$FixMode = $false,
        [object]$Config = $null,
        [string]$WorkflowDir = $null
    )

    try {
        Write-Host "Starting Claude Dev Flow for: $StoryPath" -ForegroundColor Cyan

        # Get script directory if WorkflowDir not provided
        if (-not $WorkflowDir) {
            $WorkflowDir = Split-Path -Parent $MyInvocation.PSCommandPath
        }

        # ✅ Load phase-specific configuration
        $phase = if ($FixMode) { "c" } else { "a" }  # Fix mode = Phase C, Normal = Phase A
        $execConfig = Get-PhaseExecutionConfig -Phase $phase

        # Load Dev agent prompt using the command mapper
        $agentPrompt = Load-BMADAgent -AgentType "dev"

        # Determine task command based on mode and expand it
        $starCommand = if ($FixMode) { "*review-qa" } else { "*develop-story" }
        $parameters = @{ StoryPath = $StoryPath }
        $expandedCommand = Expand-BMADCommand -Command $starCommand -Parameters $parameters -WorkflowDir $WorkflowDir

        # Build complete prompt
        $fullPrompt = Build-ClaudePrompt `
            -AgentPrompt $agentPrompt `
            -ExpandedCommand $expandedCommand

        # ✅ SILENT MODE: Add silent mode instruction (ShowHelp=false - forced)
        $silentModeInstruction = @"

--- Silent Mode ---
Working in SILENT MODE. DO NOT display help or greeting messages.
Execute task immediately without waiting for user input.
"@
        $fullPrompt = $silentModeInstruction + "`n`n" + $fullPrompt

        # ✅ Add execution instruction with phase-specific command
        if ($execConfig.AutoExecute -and $execConfig.AutoExecuteCommand) {
            $executionInstruction = @"

--- Execution Directive ---
MANDATORY: Execute command '$($execConfig.AutoExecuteCommand)' IMMEDIATELY.
Begin task execution NOW without further prompts.
"@
            $fullPrompt = $executionInstruction + "`n`n" + $fullPrompt
        }

        # Create temporary prompt file
        $promptDir = Join-Path $PSScriptRoot "prompts"
        if (-not (Test-Path $promptDir)) { New-Item -Path $promptDir -ItemType Directory -Force | Out-Null }
        $promptFile = Join-Path $promptDir "claude-prompt-$($InstanceId)-$((Get-Date).ToString('yyyyMMdd-HHmmss')).txt"
        $fullPrompt | Out-File -FilePath $promptFile -Encoding UTF8 -NoNewline

        Write-Host "Dev Prompt saved to: $promptFile" -ForegroundColor Green
        Write-Host "Phase $phase Command: $($execConfig.AutoExecuteCommand)" -ForegroundColor Cyan
        Write-Host "Instance: $InstanceId" -ForegroundColor Gray
        Write-Host "Silent Mode: FORCED (ShowHelp=false)" -ForegroundColor Yellow

        # Start Claude process
        $claudeCommand = Get-Command "claude.cmd" -ErrorAction SilentlyContinue
        if (-not $claudeCommand) {
            throw "Claude CLI not found in PATH"
        }
        $claudePath = $claudeCommand.Source

        $claudeArgs = @(
            "--dangerously-skip-permissions"
            "@$promptFile"
        )

        $processInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processInfo.FileName = $claudePath
        $processInfo.Arguments = $claudeArgs -join " "
        $processInfo.UseShellExecute = $true
        $processInfo.CreateNoWindow = $false
        $processInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Normal

        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $processInfo

        if ($process.Start()) {
            Write-Host "✅ Claude Dev Flow (Phase $phase) started" -ForegroundColor Green
            Write-Host "   PID: $($process.Id), Instance: $InstanceId" -ForegroundColor Gray
            Write-Host "   Command: $($execConfig.AutoExecuteCommand)" -ForegroundColor Gray
            Write-Host "   Agent: $($execConfig.AgentType)" -ForegroundColor Gray

            # Try to detect Claude session ID for enhanced monitoring
            $sessionId = $null
            try {
                Write-Host "Detecting Claude session ID..." -ForegroundColor Cyan
                $sessionId = Get-ClaudeSessionId -ProcessId $process.Id -MaxAgeSeconds 30

                if ($sessionId) {
                    Write-Host "✓ Session detected: $sessionId" -ForegroundColor Green
                } else {
                    Write-Warning "Could not detect session ID - using process-based monitoring only"
                }
            } catch {
                Write-Warning "Session detection failed: $_"
            }

            # Return process and session information for enhanced monitoring
            $result = [PSCustomObject]@{
                Process = $process
                ProcessId = $process.Id
                SessionId = $sessionId
                PromptFile = $promptFile
                JobName = "ClaudeDev-Flow$InstanceId-$((Get-Date).ToString('yyyyMMdd-HHmmss'))"
                Phase = $phase
                Command = $execConfig.AutoExecuteCommand
            }

            return $result
        } else {
            throw "Failed to start Claude Dev process"
        }
    }
    catch {
        Write-Error "❌ Failed to start Claude Dev Flow: $_"
        throw
    }
}

# Function to start Claude QA flow with phase-specific configuration (CRITICAL BUG FIX)
function Start-ClaudeQAFlow {
    param(
        [string]$StoryPath = "",
        [object]$Config = $null
    )

    try {
        Write-Host "Starting Claude QA Flow for: $StoryPath" -ForegroundColor Cyan

        # ✅ FIX: Load Phase B configuration (QA-specific)
        $execConfig = Get-PhaseExecutionConfig -Phase "b"

        # Load QA agent prompt using the command mapper
        $agentPrompt = Load-BMADAgent -AgentType "qa"

        # ✅ FIX: Use correct QA command
        $starCommand = "*review"
        $parameters = @{ StoryPath = $StoryPath }
        $expandedCommand = Expand-BMADCommand -Command $starCommand -Parameters $parameters

        # Build complete prompt
        $fullPrompt = Build-ClaudePrompt `
            -AgentPrompt $agentPrompt `
            -ExpandedCommand $expandedCommand

        # ✅ SILENT MODE: Add silent mode instruction (ShowHelp=false - forced)
        $silentModeInstruction = @"

--- Silent Mode ---
Working in SILENT MODE. DO NOT display help or greeting messages.
Execute task immediately without waiting for user input.
"@
        $fullPrompt = $silentModeInstruction + "`n`n" + $fullPrompt

        # ✅ Add execution instruction with QA command
        if ($execConfig.AutoExecute -and $execConfig.AutoExecuteCommand) {
            $executionInstruction = @"

--- Execution Directive ---
MANDATORY: Execute command '$($execConfig.AutoExecuteCommand)' IMMEDIATELY.
Begin task execution NOW without further prompts.
"@
            $fullPrompt = $executionInstruction + "`n`n" + $fullPrompt
        }

        # Create temporary prompt file
        $promptDir = Join-Path $PSScriptRoot "prompts"
        if (-not (Test-Path $promptDir)) { New-Item -Path $promptDir -ItemType Directory -Force | Out-Null }
        $promptFile = Join-Path $promptDir "claude-qa-prompt-$((Get-Date).ToString('yyyyMMdd-HHmmss')).txt"
        $fullPrompt | Out-File -FilePath $promptFile -Encoding UTF8 -NoNewline

        Write-Host "QA Prompt saved to: $promptFile" -ForegroundColor Green
        Write-Host "✅ QA Command: $($execConfig.AutoExecuteCommand)" -ForegroundColor Cyan  # Should be *review

        # Start Claude process
        $claudeCommand = Get-Command "claude.cmd" -ErrorAction SilentlyContinue
        if (-not $claudeCommand) {
            throw "Claude CLI not found in PATH"
        }
        $claudePath = $claudeCommand.Source

        $claudeArgs = @(
            "--dangerously-skip-permissions"
            "@$promptFile"
        )

        $processInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processInfo.FileName = $claudePath
        $processInfo.Arguments = $claudeArgs -join " "
        $processInfo.UseShellExecute = $true

        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $processInfo

        if ($process.Start()) {
            Write-Host "✅ Claude QA Flow (Phase B) started successfully" -ForegroundColor Green
            Write-Host "   PID: $($process.Id)" -ForegroundColor Gray
            Write-Host "   Command: $starCommand" -ForegroundColor Gray
            Write-Host "   Phase: B (QA Review)" -ForegroundColor Cyan
            Write-Host "   Agent: $($execConfig.AgentType)" -ForegroundColor Gray

            return $process
        } else {
            throw "Failed to start Claude QA process"
        }
    }
    catch {
        Write-Error "❌ Failed to start Claude QA Flow: $_"
        throw
    }
}

# New function that waits for Claude CLI to initialize
function Wait-ClaudeProcessReady {
    param(
        [Parameter(Mandatory = $true)]
        [System.Diagnostics.Process]$Process,

        [Parameter(Mandatory = $false)]
        [int]$TimeoutSeconds = 30,

        [Parameter(Mandatory = $false)]
        [string]$PromptFile
    )

    Write-Host "Waiting for Claude CLI to initialize..." -ForegroundColor Yellow

    $startTime = Get-Date
    $lastCheck = 0

    do {
        # Check if process is still running
        $Process.Refresh()
        if ($Process.HasExited) {
            Write-Host "✗ Claude process exited with code: $($Process.ExitCode)" -ForegroundColor Red
            if ($PromptFile -and (Test-Path $PromptFile)) {
                Write-Host "Temporary prompt file was: $PromptFile" -ForegroundColor Gray
            }
            return $false
        }

        # Check every 5 seconds
        $elapsed = (Get-Date) - $startTime
        $checkInterval = [Math]::Floor($elapsed.TotalSeconds)

        if ($checkInterval -gt $lastCheck) {
            Write-Host "  Waiting... $($checkInterval)s elapsed" -ForegroundColor Gray
            $lastCheck = $checkInterval
        }

        # Give Claude time to initialize
        Start-Sleep -Milliseconds 500

    } while ($elapsed.TotalSeconds -lt $TimeoutSeconds)

    # After timeout, check if still running
    $Process.Refresh()
    if (-not $Process.HasExited) {
        Write-Host "✓ Claude CLI initialized and running" -ForegroundColor Green
        return $true
    } else {
        Write-Host "✗ Claude process exited during initialization" -ForegroundColor Red
        return $false
    }
}

# Wait for Claude job completion using state file detection
function Wait-ClaudeJobCompletion {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Job,

        [Parameter(Mandatory = $false)]
        [int]$TimeoutSeconds = 7200,

        [Parameter(Mandatory = $false)]
        [int]$PollingInterval = 10,

        [Parameter(Mandatory = $false)]
        [object]$State
    )

    $startTime = Get-Date
    $result = @{
        Success = $false
        Output = "Task not completed"
        Error = ""
    }

    # Setup state file path
    $scriptDir = Split-Path -Parent $PSScriptRoot
    $stateDir = Join-Path $scriptDir ".workflow-state"
    $markerFile = Join-Path $stateDir "completed-$($Job.JobName).txt"

    # Ensure state directory exists
    if (-not (Test-Path $stateDir)) {
        try {
            New-Item -Path $stateDir -ItemType Directory -Force | Out-Null
        } catch {
            Write-WorkflowLogInternal -State $State -Message "Failed to create state directory: $_" -Level "Warning"
        }
    }

    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  Claude Dev Flow Started - Action Required" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor White
    Write-Host "Job: $($Job.JobName)" -ForegroundColor Yellow
    Write-Host "PID: $($Job.Job.Id)" -ForegroundColor Gray
    Write-Host "" -ForegroundColor White
    Write-Host "Instructions:" -ForegroundColor Green
    Write-Host "  1. Complete your work in the Claude CLI window" -ForegroundColor White
    Write-Host "  2. The agent will automatically create completion marker" -ForegroundColor White
    Write-Host "  3. If agent doesn't create marker, close Claude window to continue" -ForegroundColor White
    Write-Host "" -ForegroundColor White
    Write-Host "Status file: $markerFile" -ForegroundColor DarkGray
    Write-Host "" -ForegroundColor White

    Write-WorkflowLogInternal -State $State -Message "Waiting for completion marker: $markerFile (max timeout: $TimeoutSeconds seconds)" -Level "Info"

    $lastProgressTime = Get-Date
    $progressInterval = 60  # Show progress every 60 seconds

    do {
        # Check if completion marker exists
        if (Test-Path $markerFile) {
            try {
                $markerContent = Get-Content $markerFile -Raw
                $result.Success = $true
                $result.Output = $markerContent

                Write-Host "✓ Task completion detected!" -ForegroundColor Green
                Write-WorkflowLogInternal -State $State -Message "Completion marker detected: $markerFile" -Level "Success"

                # Clean up marker file
                try {
                    Remove-Item $markerFile -Force
                } catch {
                    Write-WorkflowLogInternal -State $State -Message "Warning: Could not remove marker file: $_" -Level "Warning"
                }

                # Terminate Claude process
                try {
                    if (-not $Job.Job.HasExited) {
                        $Job.Job.Kill()
                        Start-Sleep -Seconds 2  # Give it time to close
                    }
                } catch {
                    Write-WorkflowLogInternal -State $State -Message "Warning: Could not terminate Claude process: $_" -Level "Warning"
                }

                return $result
            } catch {
                Write-WorkflowLogInternal -State $State -Message "Error reading marker file: $_" -Level "Error"
            }
        }

        # Check if process has exited (manual close)
        $Job.Job.Refresh()
        if ($Job.Job.HasExited) {
            $exitCode = $Job.Job.ExitCode
            Write-WorkflowLogInternal -State $State -Message "Claude process exited manually: $($Job.JobName) (ExitCode: $exitCode)" -Level "Info"

            # Check for marker file one more time after process exits
            Start-Sleep -Seconds 2
            if (Test-Path $markerFile) {
                $markerContent = Get-Content $markerFile -Raw
                $result.Success = $true
                $result.Output = $markerContent
                Write-Host "✓ Task completed (marker found after exit)" -ForegroundColor Green
            } else {
                $result.Success = ($exitCode -eq 0)
                $result.Output = "Process completed manually"
                if ($exitCode -ne 0) {
                    $result.Error = "Process exited with code: $exitCode"
                } else {
                    $result.Error = ""
                }
                if ($result.Success) {
                    Write-Host "Process completed successfully (ExitCode: $exitCode)" -ForegroundColor Green
                } else {
                    Write-Host "Process completed with warning (ExitCode: $exitCode)" -ForegroundColor Yellow
                }
            }

            # Clean up marker file
            try {
                if (Test-Path $markerFile) {
                    Remove-Item $markerFile -Force
                }
            } catch { }

            return $result
        }

        # Check timeout
        $elapsed = (Get-Date) - $startTime
        if ($elapsed.TotalSeconds -gt $TimeoutSeconds) {
            $result.Error = "Timeout waiting for task completion after $TimeoutSeconds seconds"
            Write-WorkflowLogInternal -State $State -Message $result.Error -Level "Error"

            Write-Host "⚠ Timeout reached" -ForegroundColor Yellow
            $action = Read-Host "Timeout reached. Continue waiting? (Y/N)"

            if ($action -eq 'Y' -or $action -eq 'y') {
                $startTime = Get-Date  # Reset timer
                continue
            }

            # Clean up
            try {
                if (-not $Job.Job.HasExited) {
                    $Job.Job.Kill()
                }
            } catch { }

            return $result
        }

        # Show progress every 60 seconds
        $currentTime = Get-Date
        if (($currentTime - $lastProgressTime).TotalSeconds -ge $progressInterval) {
            $elapsedMinutes = [Math]::Floor(($currentTime - $startTime).TotalMinutes)
            Write-Host "[$elapsedMinutes min] Waiting for completion..." -ForegroundColor Gray
            Write-Host "  Claude is still running. Complete your work and let the agent finish." -ForegroundColor DarkGray
            $lastProgressTime = $currentTime
        }

        # Polling interval
        Start-Sleep -Seconds $PollingInterval

    } while ($true)
}

# Create a completion marker file
function New-TaskCompletionMarker {
    param(
        [Parameter(Mandatory = $true)]
        [string]$JobName,

        [Parameter(Mandatory = $false)]
        [string]$Message = "Task completed successfully",

        [Parameter(Mandatory = $false)]
        [string]$Result = "Success"
    )

    $scriptDir = Split-Path -Parent $PSScriptRoot
    $stateDir = Join-Path $scriptDir ".workflow-state"
    $markerFile = Join-Path $stateDir "completed-$JobName.txt"

    # Ensure state directory exists
    if (-not (Test-Path $stateDir)) {
        New-Item -Path $stateDir -ItemType Directory -Force | Out-Null
    }

    # Create marker file with completion details
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $markerContent = @"
Result: $Result
Message: $Message
Timestamp: $timestamp
JobName: $JobName
"@

    try {
        $markerContent | Out-File -FilePath $markerFile -Encoding UTF8 -Force
        Write-Host "✓ Created completion marker: $markerFile" -ForegroundColor Green
        return $true
    } catch {
        Write-Error "Failed to create completion marker: $_"
        return $false
    }
}

# Check if a task is completed
function Test-TaskCompletion {
    param(
        [Parameter(Mandatory = $true)]
        [string]$JobName
    )

    $scriptDir = Split-Path -Parent $PSScriptRoot
    $stateDir = Join-Path $scriptDir ".workflow-state"
    $markerFile = Join-Path $stateDir "completed-$JobName.txt"

    return Test-Path $markerFile
}

# Function to start Claude Final Dev flow for Phase D
function Start-ClaudeFinalDevFlow {
    param(
        [string]$StoryPath = "",
        [object]$Config = $null
    )

    try {
        Write-Host "Starting Claude Final Dev Flow for: $StoryPath" -ForegroundColor Cyan

        # Load Phase D configuration
        $execConfig = Get-PhaseExecutionConfig -Phase "d"

        # Load Dev agent for final polish
        $agentPrompt = Load-BMADAgent -AgentType "dev"

        # Build command for final development
        $starCommand = "*develop-story"
        $parameters = @{ StoryPath = $StoryPath }
        $expandedCommand = Expand-BMADCommand -Command $starCommand -Parameters $parameters

        # Build complete prompt
        $fullPrompt = Build-ClaudePrompt `
            -AgentPrompt $agentPrompt `
            -ExpandedCommand $expandedCommand

        # ✅ SILENT MODE: Add silent mode instruction (ShowHelp=false - forced)
        $silentModeInstruction = @"

--- Silent Mode ---
Working in SILENT MODE. DO NOT display help or greeting messages.
Execute task immediately without waiting for user input.
"@
        $fullPrompt = $silentModeInstruction + "`n`n" + $fullPrompt

        # Add execution instruction
        if ($execConfig.AutoExecute -and $execConfig.AutoExecuteCommand) {
            $executionInstruction = @"

--- Execution Directive ---
MANDATORY: Execute command '$($execConfig.AutoExecuteCommand)' IMMEDIATELY.
Begin task execution NOW without further prompts.
"@
            $fullPrompt = $executionInstruction + "`n`n" + $fullPrompt
        }

        # Create prompt file
        $promptDir = Join-Path $PSScriptRoot "prompts"
        if (-not (Test-Path $promptDir)) { New-Item -Path $promptDir -ItemType Directory -Force | Out-Null }
        $promptFile = Join-Path $promptDir "claude-final-prompt-$((Get-Date).ToString('yyyyMMdd-HHmmss')).txt"
        $fullPrompt | Out-File -FilePath $promptFile -Encoding UTF8 -NoNewline

        Write-Host "Final Dev Prompt saved to: $promptFile" -ForegroundColor Green
        Write-Host "Phase D Command: $($execConfig.AutoExecuteCommand)" -ForegroundColor Cyan

        # Start Claude process
        $claudeCommand = Get-Command "claude.cmd" -ErrorAction SilentlyContinue
        if (-not $claudeCommand) {
            throw "Claude CLI not found in PATH"
        }
        $claudePath = $claudeCommand.Source

        $claudeArgs = @(
            "--dangerously-skip-permissions"
            "@$promptFile"
        )

        $processInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processInfo.FileName = $claudePath
        $processInfo.Arguments = $claudeArgs -join " "
        $processInfo.UseShellExecute = $true
        $processInfo.CreateNoWindow = $false
        $processInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Normal

        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $processInfo

        if ($process.Start()) {
            Write-Host "✅ Claude Final Dev Flow (Phase D) started" -ForegroundColor Green
            Write-Host "   PID: $($process.Id)" -ForegroundColor Gray
            Write-Host "   Command: $starCommand" -ForegroundColor Gray
            Write-Host "   Phase: D (Final Development & Polish)" -ForegroundColor Cyan
            Write-Host "   Agent: $($execConfig.AgentType)" -ForegroundColor Gray

            return $process
        } else {
            throw "Failed to start Claude Final Dev process"
        }
    }
    catch {
        Write-Error "❌ Failed to start Claude Final Dev Flow: $_"
        throw
    }
}

function Build-ClaudePrompt {
    param(
        [string]$AgentPrompt = "",
        [hashtable]$ExpandedCommand = @{}
    )

    # Simple prompt builder - combines agent prompt with task
    $prompt = @"
$AgentPrompt

--- Task ---
$($ExpandedCommand.TaskName)

$($ExpandedCommand.TaskContent)
"@

    return $prompt.Trim()
}

Write-Host "BMAD.Claude.Interface.Fixed loaded successfully" -ForegroundColor Green
Write-Host "This version uses file-based prompt passing to avoid command line length limits" -ForegroundColor Cyan
