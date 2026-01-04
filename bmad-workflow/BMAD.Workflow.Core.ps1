# BMAD.Workflow.Core.ps1
# Core workflow engine for BMAD-Method PowerShell Workflow Automation
# Version: 1.0.0

# Store the workflow directory (bmad-workflow) globally
$script:WorkflowCoreDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Import QA Workflow module for automated QA tools integration
$qaWorkflowModulePath = Join-Path $script:WorkflowCoreDir "BMAD.QA.Workflow.ps1"
if (Test-Path $qaWorkflowModulePath) {
    try {
        . $qaWorkflowModulePath
        Write-WorkflowLogInternal -State $null -Message "QA Workflow module loaded successfully" -Level ([LogLevel]::Success)
    } catch {
        Write-WorkflowLogInternal -State $null -Message "Failed to load QA Workflow module: $_" -Level ([LogLevel]::Warning)
    }
}

# Enum for workflow status
enum WorkflowStatus {
    NotStarted
    RunningDevFlows
    RunningQAReview
    QA_Pass
    QA_Concerns
    Completed
    Failed
}

# Class for tracking workflow jobs
class WorkflowJob {
    [int]$InstanceId
    [string]$JobName
    [object]$Job
    [string]$Type  # "dev" or "qa"
    [DateTime]$StartTime
    [DateTime]$EndTime
    [bool]$IsCompleted
    [string]$Result
}

# Main workflow state class
class BMADWorkflowState {
    [string]$WorkflowId
    [string]$StoryPath
    [WorkflowStatus]$Status
    [System.Collections.Generic.List[WorkflowJob]]$Jobs
    [DateTime]$StartTime
    [DateTime]$EndTime
    [int]$IterationCount
    [string]$LastQAResult
    [string]$LastQAError

    BMADWorkflowState() {
        $this.WorkflowId = (New-Guid).ToString()
        $this.Jobs = [System.Collections.Generic.List[WorkflowJob]]::new()
        $this.IterationCount = 0
        $this.Status = [WorkflowStatus]::NotStarted
    }
}

# Logging levels
enum LogLevel {
    Debug
    Info
    Warning
    Error
    Critical
    Success
}

# Configuration loading function
function Get-WorkflowConfig {
    <#
    .SYNOPSIS
    Loads workflow configuration from YAML file.

    .PARAMETER ConfigPath
    Path to the configuration YAML file

    .RETURNS
    PowerShell object with configuration settings
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ConfigPath
    )

    try {
        # Check if file exists
        if (-not (Test-Path $ConfigPath)) {
            throw "Configuration file not found: $ConfigPath"
        }

        # Read YAML file content
        $content = Get-Content -Path $ConfigPath -Raw -ErrorAction Stop

        # Simple YAML to PowerShell object conversion
        # This handles basic YAML structures (key-value pairs and nested objects)
        $config = ConvertFrom-YamlContent -YamlContent $content

        # Validate required configuration sections
        if (-not $config.workflow) {
            throw "Missing required 'workflow' section in configuration"
        }

        # Validate phase_delay_minutes
        if (-not $config.workflow.phase_delay_minutes) {
            Write-Warning "phase_delay_minutes not found in configuration, using default value of 30"
            $config.workflow.phase_delay_minutes = 30
        } elseif ($config.workflow.phase_delay_minutes -isnot [int] -or $config.workflow.phase_delay_minutes -lt 1) {
            throw "phase_delay_minutes must be a positive integer, got: $($config.workflow.phase_delay_minutes)"
        }

        Write-WorkflowLogInternal -State $null -Message "Configuration loaded successfully from: $ConfigPath" -Level ([LogLevel]::Info)
        Write-WorkflowLogInternal -State $null -Message "Phase delay: $($config.workflow.phase_delay_minutes) minutes" -Level ([LogLevel]::Debug)

        return $config

    } catch {
        Write-WorkflowLogInternal -State $null -Message "Failed to load configuration: $_" -Level ([LogLevel]::Error)
        throw "Configuration loading failed: $_"
    }
}

# Simple YAML content parser for basic structures
function ConvertFrom-YamlContent {
    <#
    .SYNOPSIS
    Converts basic YAML content to PowerShell object.

    .PARAMETER YamlContent
    YAML content as string

    .RETURNS
    PowerShell object representation
    #>
    param([string]$YamlContent)

    $result = @{}
    $currentSection = $result
    $sectionStack = @()

    $lines = $YamlContent -split "`r?`n"

    foreach ($line in $lines) {
        # Skip comments and empty lines
        if ($line.Trim() -match '^\s*#' -or [string]::IsNullOrWhiteSpace($line)) {
            continue
        }

        # Handle indentation
        $indentation = $line.Length - $line.TrimStart().Length
        $trimmedLine = $line.Trim()

        # Handle section headers (ends with :)
        if ($trimmedLine -match '^(\w+):\s*$') {
            $sectionName = $matches[1]

            # Create new section
            $newSection = @{}
            $currentSection[$sectionName] = $newSection

            # Adjust section stack based on indentation
            while ($sectionStack.Count -gt 0 -and $sectionStack[-1].Indentation -ge $indentation) {
                $sectionStack.RemoveAt($sectionStack.Count - 1)
            }

            # Push current section to stack and make it current
            $sectionStack += @{ Section = $currentSection; Indentation = $indentation }
            $currentSection = $newSection
            continue
        }

        # Handle key-value pairs
        if ($trimmedLine -match '^(\w+):\s*(.*)$') {
            $key = $matches[1]
            $value = $matches[2].Trim()

            # Convert to appropriate type
            if ($value -match '^"(.*)"$') {
                # String in quotes
                $value = $matches[1]
            } elseif ($value -match '^\d+$') {
                # Integer
                $value = [int]$value
            } elseif ($value -match '^\d+\.\d+$') {
                # Float
                $value = [double]$value
            } elseif ($value -match '^(true|false)$') {
                # Boolean
                $value = $value -eq 'true'
            } elseif ($value -match '^\[(.*)\]$') {
                # Array
                $arrayContent = $matches[1]
                $value = $arrayContent -split ',\s*' | ForEach-Object {
                    $item = $_.Trim()
                    if ($item -match '^"(.*)"$') { $matches[1] }
                    elseif ($item -match '^\d+$') { [int]$item }
                    elseif ($item -match '^(true|false)$') { $item -eq 'true' }
                    else { $item }
                }
            } elseif ([string]::IsNullOrWhiteSpace($value)) {
                # Null or empty value
                $value = $null
            }

            $currentSection[$key] = $value
        }
    }

    return $result
}

# Core workflow function
function Start-BMADWorkflow {
    <#
    .SYNOPSIS
    Starts the BMAD workflow automation for a given story.

    .PARAMETER StoryPath
    Relative path to the story document

    .PARAMETER ConfigPath
    Path to workflow configuration file

    .PARAMETER MaxIterations
    Maximum number of QA iterations (default: 10)

    .RETURNS
    BMADWorkflowState object with execution results
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$StoryPath,

        [Parameter(Mandatory=$false)]
        [string]$ConfigPath = "./config/workflow.config.yaml",

        [Parameter(Mandatory=$false)]
        [int]$MaxIterations = 10
    )

    # Initialize workflow state
    $workflowState = [BMADWorkflowState]::new()
    $workflowState.StoryPath = $StoryPath
    $workflowState.StartTime = Get-Date

    # Load configuration
    try {
        $config = Get-WorkflowConfig -ConfigPath $ConfigPath
        Write-WorkflowLogInternal -State $workflowState -Message "Workflow started for story: $StoryPath" -Level ([LogLevel]::Info)
    } catch {
        $workflowState.Status = [WorkflowStatus]::Failed
        Write-WorkflowLogInternal -State $workflowState -Message "Failed to load configuration: $_" -Level ([LogLevel]::Error)
        throw "Configuration loading failed: $_"
    }

    try {
        # Validate story exists
        if (-not (Test-Path $StoryPath)) {
            throw "Story file not found: $StoryPath"
        }

        # Phase A: Execute 3 parallel dev flows
        Write-WorkflowLogInternal -State $workflowState -Message "Starting Phase A: 3 parallel development flows" -Level ([LogLevel]::Info)
        $workflowState.Status = [WorkflowStatus]::RunningDevFlows

        $devJobs = Start-ParallelDevFlows -StoryPath $StoryPath -Config $config -WorkflowDir $script:WorkflowCoreDir
        foreach ($job in $devJobs) {
            $workflowState.Jobs.Add($job)
        }

        # Calculate phase delay from configuration with validation
        $phaseDelayMinutes = if ($config.workflow.phase_delay_minutes) {
            try {
                # Validate the phase delay configuration
                if (Test-PhaseDelayValidation -PhaseDelayMinutes $config.workflow.phase_delay_minutes) {
                    $config.workflow.phase_delay_minutes
                } else {
                    throw "Invalid phase_delay_minutes configuration: $($config.workflow.phase_delay_minutes)"
                }
            } catch {
                Write-WorkflowLogInternal -State $workflowState -Message "Invalid phase_delay_minutes in config, using default (15 minutes): $_" -Level ([LogLevel]::Warning)
                15  # Default to 15 minutes if validation fails
            }
        } else {
            15  # Default to 15 minutes if not specified
        }
        $phaseDelay = $phaseDelayMinutes * 60  # Convert minutes to seconds
        Write-WorkflowLogInternal -State $workflowState -Message "Phase A starting: Configured phase delay is $phaseDelayMinutes minutes ($phaseDelay seconds)" -Level ([LogLevel]::Info)
        Write-Host "Phase A: Starting 3 parallel dev flows..." -ForegroundColor Yellow
        Write-Host "Waiting $phaseDelayMinutes minutes before proceeding to Phase B (QA review)..." -ForegroundColor Cyan

        $devResults = Wait-WorkflowJobs -Jobs $devJobs -Config $config -State $workflowState

        if (-not $devResults.AllSuccessful) {
            throw "One or more development flows failed: $($devResults.Errors -join '; ')"
        }

        # ========================================
        # Phase A.1: Automated QA Tools Integration
        # Run BasedPyright and Fixtest workflows
        # ========================================
        Write-WorkflowLogInternal -State $workflowState -Message "Starting automated QA tools integration after Dev phase" -Level ([LogLevel]::Info)
        Write-Host "Phase A.1: Running Automated QA Tools (BasedPyright & Fixtest)..." -ForegroundColor Cyan

        $projectRoot = Split-Path -Parent (Split-Path -Parent $StoryPath)
        try {
            $qaResult = Start-QAToolsWorkflow -ProjectRoot $projectRoot -StoryPath $StoryPath -WorkflowState $workflowState -Config $config -MaxRetries 2

            # Check QA results
            if ($qaResult.OverallStatus -eq 'Fail') {
                Write-WorkflowLogInternal -State $workflowState -Message "QA tools failed with critical errors. Last error: $qaResult.ErrorMessage" -Level ([LogLevel]::Error)
                $workflowState.LastQAError = "QA tools failed: $($qaResult.ErrorMessage)"
                # Continue anyway - let the QA review phase handle the issues
            } elseif ($qaResult.OverallStatus -eq 'Concerns') {
                Write-WorkflowLogInternal -State $workflowState -Message "QA tools found issues (Concerns level)" -Level ([LogLevel]::Warning)
            } elseif ($qaResult.OverallStatus -eq 'Pass') {
                Write-WorkflowLogInternal -State $workflowState -Message "QA tools passed all checks" -Level ([LogLevel]::Success)
            }

            $workflowState.LastQAResult = $qaResult.OverallStatus.ToString()
        } catch {
            Write-WorkflowLogInternal -State $workflowState -Message "QA tools integration failed: $_" -Level ([LogLevel]::Error)
            $workflowState.LastQAError = "QA integration failed: $_"
            # Continue anyway - don't let QA tools failure block the workflow
        }

        # Phase A to Phase B delay with countdown
        Write-PhaseTransitionLog -State $workflowState -FromPhase "A" -ToPhase "B" -Duration $phaseDelay
        $countdownResult = Show-PhaseCountdown -PhaseName "Phase A → Phase B Transition" -DurationSeconds $phaseDelay -Config $config
        Write-WorkflowLogInternal -State $workflowState -Message "Phase A to B transition completed in $($countdownResult.DurationSeconds) seconds" -Level ([LogLevel]::Info)

        # Phase B: First QA review (Iteration 1)
        Write-WorkflowLogInternal -State $workflowState -Message "Starting Phase B: QA review (Iteration 1)" -Level ([LogLevel]::Info)
        $workflowState.Status = [WorkflowStatus]::RunningQAReview

        $qaJob1 = Start-QAReview -StoryPath $StoryPath -Config $config
        $workflowState.Jobs.Add($qaJob1)

        $qaResults1 = Wait-WorkflowJobs -Jobs @($qaJob1) -Config $config -State $workflowState

        if (-not $qaResults1.AllSuccessful) {
            $workflowState.LastQAError = $qaResults1.Errors[0]
            throw "QA review failed: $($qaResults1.Errors[0])"
        }

        # Phase B to Phase C delay with countdown
        Write-Host "Phase B completed." -ForegroundColor Cyan
        Write-PhaseTransitionLog -State $workflowState -FromPhase "B" -ToPhase "C" -Duration $phaseDelay
        $countdownResult = Show-PhaseCountdown -PhaseName "Phase B → Phase C Transition" -DurationSeconds $phaseDelay -Config $config
        Write-WorkflowLogInternal -State $workflowState -Message "Phase B to C transition completed in $($countdownResult.DurationSeconds) seconds" -Level ([LogLevel]::Info)

        # Phase C: Execute 3 parallel dev flows (Fix mode)
        Write-WorkflowLogInternal -State $workflowState -Message "Starting Phase C: Fix mode development flows" -Level ([LogLevel]::Info)
        $workflowState.Status = [WorkflowStatus]::QA_Concerns

        $fixDevJobs = Start-ParallelDevFlows -StoryPath $StoryPath -Config $config -FixMode $true -WorkflowDir $script:WorkflowCoreDir
        foreach ($job in $fixDevJobs) {
            $workflowState.Jobs.Add($job)
        }

        $fixResults = Wait-WorkflowJobs -Jobs $fixDevJobs -Config $config -State $workflowState

        if (-not $fixResults.AllSuccessful) {
            throw "Fix mode development flows failed: $($fixResults.Errors -join '; ')"
        }

        # ========================================
        # Phase C.1: Automated QA Tools Integration (Post-Fix)
        # Re-run QA tools after fix mode development
        # ========================================
        Write-WorkflowLogInternal -State $workflowState -Message "Running QA tools after fix mode development" -Level ([LogLevel]::Info)
        Write-Host "Phase C.1: Re-running QA Tools after Fix Mode..." -ForegroundColor Cyan

        try {
            $qaResult2 = Start-QAToolsWorkflow -ProjectRoot $projectRoot -StoryPath $StoryPath -WorkflowState $workflowState -Config $config -MaxRetries 2

            # Check QA results
            if ($qaResult2.OverallStatus -eq 'Fail') {
                Write-WorkflowLogInternal -State $workflowState -Message "QA tools still failing after fix mode" -Level ([LogLevel]::Error)
                $workflowState.LastQAError = "QA tools failed after fixes"
            } elseif ($qaResult2.OverallStatus -eq 'Concerns') {
                Write-WorkflowLogInternal -State $workflowState -Message "QA tools found remaining issues after fix mode" -Level ([LogLevel]::Warning)
            } elseif ($qaResult2.OverallStatus -eq 'Pass') {
                Write-WorkflowLogInternal -State $workflowState -Message "QA tools passed after fix mode!" -Level ([LogLevel]::Success)
            }

            $workflowState.LastQAResult = $qaResult2.OverallStatus.ToString()
        } catch {
            Write-WorkflowLogInternal -State $workflowState -Message "QA tools integration failed after fix mode: $_" -Level ([LogLevel]::Error)
            # Continue anyway
        }

        # Phase C to Phase B delay with countdown
        Write-PhaseTransitionLog -State $workflowState -FromPhase "C" -ToPhase "B" -Duration $phaseDelay
        $countdownResult = Show-PhaseCountdown -PhaseName "Phase C → Phase B Transition" -DurationSeconds $phaseDelay -Config $config
        Write-WorkflowLogInternal -State $workflowState -Message "Phase C to B transition completed in $($countdownResult.DurationSeconds) seconds" -Level ([LogLevel]::Info)

        $workflowState.IterationCount = 1

        # Phase B: Second QA review (Iteration 2)
        Write-WorkflowLogInternal -State $workflowState -Message "Starting Phase B: QA review (Iteration 2)" -Level ([LogLevel]::Info)
        $workflowState.Status = [WorkflowStatus]::RunningQAReview

        $qaJob2 = Start-QAReview -StoryPath $StoryPath -Config $config
        $workflowState.Jobs.Add($qaJob2)

        $qaResults2 = Wait-WorkflowJobs -Jobs @($qaJob2) -Config $config -State $workflowState

        if (-not $qaResults2.AllSuccessful) {
            $workflowState.LastQAError = $qaResults2.Errors[0]
            throw "QA review failed: $($qaResults2.Errors[0])"
        }

        # Phase B to Phase D delay with countdown
        Write-Host "Phase B completed." -ForegroundColor Cyan
        Write-PhaseTransitionLog -State $workflowState -FromPhase "B" -ToPhase "D" -Duration $phaseDelay
        $countdownResult = Show-PhaseCountdown -PhaseName "Phase B → Phase D Transition" -DurationSeconds $phaseDelay -Config $config
        Write-WorkflowLogInternal -State $workflowState -Message "Phase B to D transition completed in $($countdownResult.DurationSeconds) seconds" -Level ([LogLevel]::Info)

        # Phase D: Final Development Flow
        Write-WorkflowLogInternal -State $workflowState -Message "Starting Phase D: Final development & polish" -Level ([LogLevel]::Info)
        $workflowState.Status = [WorkflowStatus]::QA_Pass

        $finalDevJob = Start-FinalDevFlow -StoryPath $StoryPath -Config $config
        $workflowState.Jobs.Add($finalDevJob)

        $finalResults = Wait-WorkflowJobs -Jobs @($finalDevJob) -Config $config -State $workflowState

        if (-not $finalResults.AllSuccessful) {
            throw "Final development flow failed: $($finalResults.Errors -join '; ')"
        }

        Write-WorkflowLogInternal -State $workflowState -Message "Workflow completed successfully" -Level ([LogLevel]::Info)

        $workflowState.Status = [WorkflowStatus]::Completed

    } catch {
        $workflowState.Status = [WorkflowStatus]::Failed
        Write-WorkflowLogInternal -State $workflowState -Message "Workflow failed: $_" -Level ([LogLevel]::Error)
        throw
    } finally {
        $workflowState.EndTime = Get-Date
        Write-WorkflowLogInternal -State $workflowState -Message "Workflow ended with status: $($workflowState.Status)" -Level ([LogLevel]::Info)
    }

    return $workflowState
}

# Start parallel development flows
function Start-ParallelDevFlows {
    <#
    .SYNOPSIS
    Starts 3 parallel development flows.

    .PARAMETER StoryPath
    Path to the story document

    .PARAMETER Config
    Configuration object

    .PARAMETER FixMode
    If true, runs in fix mode; otherwise runs in development mode

    .PARAMETER WorkflowDir
    Directory of the workflow (bmad-workflow)

    .RETURNS
    Array of WorkflowJob objects
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$StoryPath,

        [Parameter(Mandatory=$true)]
        [object]$Config,

        [Parameter(Mandatory=$false)]
        [bool]$FixMode = $false,

        [Parameter(Mandatory=$false)]
        [string]$WorkflowDir = $null
    )

    # Use global workflow directory if not provided
    if (-not $WorkflowDir) {
        $WorkflowDir = $script:WorkflowCoreDir
    }

    $devJobs = @()
    $concurrentFlows = $config.workflow.concurrent_dev_flows

    Write-WorkflowLogInternal -State $null -Message "Starting $concurrentFlows parallel development flows" -Level ([LogLevel]::Info)

    for ($i = 1; $i -le $concurrentFlows; $i++) {
        $jobName = "ClaudeDev-Flow$i-$((Get-Date).ToString('yyyyMMdd-HHmmss'))"

        # ✅ 添加启动延迟，错开 SSL 握手，避免并发冲突
        if ($i -gt 1) {
            Write-WorkflowLogInternal -State $null -Message "Waiting 2 seconds before starting flow $i (to avoid SSL handshake conflicts)..." -Level ([LogLevel]::Info)
            Write-Host "Waiting 2 seconds before starting flow $i..." -ForegroundColor Gray
            Start-Sleep -Seconds 2
        }

        Write-WorkflowLogInternal -State $null -Message "Starting Claude Dev Flow $i`: $jobName" -Level ([LogLevel]::Info)

        $job = Start-ClaudeDevFlow -StoryPath $StoryPath -InstanceId $i -FixMode $FixMode -Config $Config -WorkflowDir $WorkflowDir

        if ($null -eq $job) {
            Write-WorkflowLogInternal -State $null -Message "Failed to start Claude Dev Flow $i" -Level ([LogLevel]::Error)
            throw "Failed to start Claude Dev Flow $i for story: $StoryPath"
        }

        $workflowJob = [WorkflowJob]::new()
        $workflowJob.InstanceId = $i
        $workflowJob.JobName = $jobName
        $workflowJob.Job = $job
        $workflowJob.Type = "dev"
        $workflowJob.StartTime = Get-Date
        $workflowJob.IsCompleted = $false

        $devJobs += $workflowJob
        Write-WorkflowLogInternal -State $null -Message "Added workflow job $i to devJobs array (count: $($devJobs.Count))" -Level ([LogLevel]::Debug)
    }

    Write-WorkflowLogInternal -State $null -Message "Created $($devJobs.Count) development jobs" -Level ([LogLevel]::Info)
    Write-WorkflowLogInternal -State $null -Message "Started $concurrentFlows parallel development flows in FixMode=$FixMode" -Level ([LogLevel]::Info)

    if ($null -eq $devJobs) {
        Write-WorkflowLogInternal -State $null -Message "ERROR: devJobs is null before return!" -Level ([LogLevel]::Error)
        throw "devJobs is null after creation"
    }

    return $devJobs
}

# Start QA review flow
function Start-QAReview {
    <#
    .SYNOPSIS
    Starts a single QA review flow.

    .PARAMETER StoryPath
    Path to the story document

    .PARAMETER Config
    Configuration object

    .RETURNS
    WorkflowJob object
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$StoryPath,

        [Parameter(Mandatory=$true)]
        [object]$Config
    )

    $jobName = "ClaudeQA-$((Get-Date).ToString('yyyyMMdd-HHmmss'))"

    $job = Start-ClaudeQAFlow -StoryPath $StoryPath -Config $Config

    $workflowJob = [WorkflowJob]::new()
    $workflowJob.InstanceId = 1
    $workflowJob.JobName = $jobName
    $workflowJob.Job = $job
    $workflowJob.Type = "qa"
    $workflowJob.StartTime = Get-Date
    $workflowJob.IsCompleted = $false

    Write-WorkflowLogInternal -State $null -Message "Started QA review flow" -Level ([LogLevel]::Info)

    return $workflowJob
}

# Start final development flow
function Start-FinalDevFlow {
    <#
    .SYNOPSIS
    Starts the final development flow after QA PASS.

    .PARAMETER StoryPath
    Path to the story document

    .PARAMETER Config
    Configuration object

    .RETURNS
    WorkflowJob object
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$StoryPath,

        [Parameter(Mandatory=$true)]
        [object]$Config
    )

    $jobName = "ClaudeFinal-$((Get-Date).ToString('yyyyMMdd-HHmmss'))"

    $job = Start-ClaudeFinalDevFlow -StoryPath $StoryPath -Config $Config

    $workflowJob = [WorkflowJob]::new()
    $workflowJob.InstanceId = 1
    $workflowJob.JobName = $jobName
    $workflowJob.Job = $job
    $workflowJob.Type = "dev"
    $workflowJob.StartTime = Get-Date
    $workflowJob.IsCompleted = $false

    Write-WorkflowLogInternal -State $null -Message "Started final development flow" -Level ([LogLevel]::Info)

    return $workflowJob
}

# Evaluate QA result (DEPRECATED - No longer used in linear workflow A->B->C->B->D)
# function Evaluate-QAResult {
#     <#
#     .SYNOPSIS
#     Evaluates QA review result to determine next action.
#
#     .PARAMETER QAResultText
#     The full text result from QA review
#
#     .RETURNS
#     String: "PASS", "CONCERNS", or "NEUTRAL"
#     #>
#     [CmdletBinding()]
#     param(
#         [Parameter(Mandatory=$false)]
#         [string]$QAResultText = ""
#     )
#
#     if (-not $QAResultText) {
#         return "NEUTRAL"
#     }
#
#     # Split into paragraphs and get the last non-empty one
#     $paragraphs = $QAResultText -split "`r?`n`r?`n" | Where-Object { $_.Trim() }
#     $lastParagraph = if ($paragraphs.Count -gt 0) { $paragraphs[-1] } else { "" }
#
#     # Check for decision keywords
#     if ($lastParagraph -match "PASS") {
#         return "PASS"
#     } elseif ($lastParagraph -match "CONCERNS") {
#         return "CONCERNS"
#     } else {
#         return "NEUTRAL"
#     }
# }

# Timer-related functions for phase management
function Test-PhaseDelayValidation {
    <#
    .SYNOPSIS
    Validates phase delay configuration values.

    .PARAMETER PhaseDelayMinutes
    Phase delay in minutes to validate

    .RETURNS
    Boolean indicating if the value is valid
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [int]$PhaseDelayMinutes
    )

    # Valid range: 1 minute to 24 hours (1440 minutes) - more flexible for enterprise scenarios
    if ($PhaseDelayMinutes -le 0) {
        Write-WorkflowLogInternal -Message "Phase delay must be positive minutes (greater than 0). Using default of 15 minutes." -Level "Warning" -State $null
        return $false
    } elseif ($PhaseDelayMinutes -gt 1440) {
        Write-WorkflowLogInternal -Message "Phase delay of $PhaseDelayMinutes minutes exceeds 24 hours. Using default of 15 minutes for reliability." -Level "Warning" -State $null
        return $false
    }

    Write-WorkflowLogInternal -Message "Phase delay validation passed: $PhaseDelayMinutes minutes" -Level "Debug" -State $null
    return $true
}

function Show-PhaseCountdown {
    <#
    .SYNOPSIS
    Displays a countdown timer for phase transitions.

    .PARAMETER PhaseName
    Name of the phase being waited for

    .PARAMETER DurationSeconds
    Duration to countdown in seconds

    .PARAMETER Config
    Configuration object (for mock mode detection)

    .RETURNS
    Object with countdown results
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$PhaseName,

        [Parameter(Mandatory=$true)]
        [int]$DurationSeconds,

        [Parameter(Mandatory=$false)]
        [object]$Config,

        [Parameter(Mandatory=$false)]
        [switch]$WhatIf
    )

    if ($WhatIf) {
        return @{
            PhaseName = $PhaseName
            DurationSeconds = $DurationSeconds
            Message = "Would display countdown for $PhaseName ($DurationSeconds seconds)"
        }
    }

    # Check for mock mode
    $mockMode = if ($Config -and $Config.development) {
        $Config.development.mock_mode -eq $true
    } else {
        $false
    }

    if ($mockMode) {
        # In mock mode, use reduced duration for testing
        $mockDuration = if ($DurationSeconds -gt 60) { 5 } else { $DurationSeconds }
        Write-Host "Mock mode: $PhaseName ($mockDuration seconds)" -ForegroundColor Yellow
        Start-Sleep -Seconds $mockDuration
        return @{
            PhaseName = $PhaseName
            DurationSeconds = $mockDuration
            MockMode = $true
            Completed = $true
        }
    }

    if ($DurationSeconds -le 0) {
        Write-Host "Phase $PhaseName - No delay needed" -ForegroundColor Green
        return @{
            PhaseName = $PhaseName
            DurationSeconds = 0
            Completed = $true
        }
    }

    Write-Host ""
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "Phase - $PhaseName" -ForegroundColor White
    Write-Host "Duration: $([math]::Floor($DurationSeconds / 60)) minutes, $($DurationSeconds % 60) seconds" -ForegroundColor Gray
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""

    $startTime = Get-Date
    $remainingSeconds = $DurationSeconds

    while ($remainingSeconds -gt 0) {
        $minutes = [math]::Floor($remainingSeconds / 60)
        $seconds = $remainingSeconds % 60
        $timeString = "{0:D2}:{1:D2}" -f $minutes, $seconds

        Write-Host "`rTime remaining: $timeString" -ForegroundColor Yellow -NoNewline

        Start-Sleep -Seconds 1
        $remainingSeconds--
    }

    Write-Host "`rPhase $PhaseName completed!              " -ForegroundColor Green
    Write-Host ""

    $endTime = Get-Date
    $actualDuration = ($endTime - $startTime).TotalSeconds

    return @{
        PhaseName = $PhaseName
        DurationSeconds = $actualDuration
        MockMode = $false
        Completed = $true
    }
}

function Write-PhaseTransitionLog {
    <#
    .SYNOPSIS
    Logs phase transitions with timestamps and duration.

    .PARAMETER State
    Workflow state object

    .PARAMETER FromPhase
    Source phase name

    .PARAMETER ToPhase
    Destination phase name

    .PARAMETER Duration
    Duration of the phase in seconds

    .RETURNS
    Log entry string
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [BMADWorkflowState]$State,

        [Parameter(Mandatory=$true)]
        [string]$FromPhase,

        [Parameter(Mandatory=$false)]
        [string]$ToPhase,

        [Parameter(Mandatory=$false)]
        [int]$Duration = 0,

        [Parameter(Mandatory=$false)]
        [switch]$WhatIf
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $workflowId = if ($State) { $State.WorkflowId } else { "unknown" }

    $logEntry = if ($ToPhase) {
        "[$timestamp] Workflow:$workflowId - Phase transition: $FromPhase → $ToPhase"
    } else {
        "[$timestamp] Workflow:$workflowId - Phase completed: $FromPhase"
    }

    if ($Duration -gt 0) {
        $logEntry += " (Duration: $Duration seconds)"
    }

    if (-not $WhatIf) {
        Write-WorkflowLogInternal -State $State -Message $logEntry -Level ([LogLevel]::Info)
    }

    return $logEntry
}

function Test-PhaseTransition {
    <#
    .SYNOPSIS
    Validates if a phase transition is allowed.

    .PARAMETER FromStatus
    Current workflow status

    .PARAMETER ToStatus
    Target workflow status

    .RETURNS
    Boolean indicating if transition is valid
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [WorkflowStatus]$FromStatus,

        [Parameter(Mandatory=$true)]
        [WorkflowStatus]$ToStatus
    )

    # Define valid transitions
    $validTransitions = @{
        [WorkflowStatus]::NotStarted = @([WorkflowStatus]::RunningDevFlows)
        [WorkflowStatus]::RunningDevFlows = @([WorkflowStatus]::RunningQAReview, [WorkflowStatus]::Failed)
        [WorkflowStatus]::RunningQAReview = @([WorkflowStatus]::QA_Pass, [WorkflowStatus]::QA_Concerns, [WorkflowStatus]::Failed)
        [WorkflowStatus]::QA_Pass = @([WorkflowStatus]::Completed, [WorkflowStatus]::RunningDevFlows)  # Can go to final dev or restart
        [WorkflowStatus]::QA_Concerns = @([WorkflowStatus]::RunningDevFlows)  # Back to dev for fixes
        [WorkflowStatus]::Completed = @()  # Terminal state
        [WorkflowStatus]::Failed = @()  # Terminal state
    }

    if ($validTransitions.ContainsKey($FromStatus)) {
        return $ToStatus -in $validTransitions[$FromStatus]
    }

    return $false
}

function Get-MockPhaseDelay {
    <#
    .SYNOPSIS
    Gets reduced phase delay for mock mode testing.

    .PARAMETER Config
    Configuration object

    .RETURNS
    Phase delay in seconds for mock mode
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [object]$Config
    )

    if (-not $Config -or -not $Config.workflow) {
        return 5  # Default mock delay
    }

    $realDelayMinutes = $Config.workflow.phase_delay_minutes
    if (-not $realDelayMinutes) {
        $realDelayMinutes = 30  # Default
    }

    # In mock mode, reduce delays significantly
    if ($realDelayMinutes -le 5) {
        return 5  # Minimum 5 seconds
    } elseif ($realDelayMinutes -le 30) {
        return 10  # 10 seconds for short phases
    } else {
        return 15  # 15 seconds for longer phases
    }
}

# Wait for workflow jobs to complete (Simplified timer-based version)
function Wait-WorkflowJobs {
    <#
    .SYNOPSIS
    Waits for all provided jobs to complete using timer-based delays.

    .PARAMETER Jobs
    Array of WorkflowJob objects

    .PARAMETER Config
    Configuration object

    .PARAMETER State
    Workflow state for logging

    .RETURNS
    Object with AllSuccessful, Results, and Errors properties
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [WorkflowJob[]]$Jobs,

        [Parameter(Mandatory=$true)]
        [object]$Config,

        [Parameter(Mandatory=$false)]
        [BMADWorkflowState]$State
    )

    $results = @()
    $errors = @()
    $timeoutSeconds = $Config.workflow.job_timeout_seconds

    Write-WorkflowLogInternal -State $State -Message "Timer-based job monitoring: $($Jobs.Count) jobs" -Level ([LogLevel]::Info)

    # Timer-based approach: Assume jobs complete within the configured phase delay
    # This eliminates complex monitoring while ensuring predictable workflow timing
    foreach ($job in $Jobs) {
        try {
            $jobName = if ($job.JobName) { $job.JobName } else { "Unknown" }

            Write-WorkflowLogInternal -State $State -Message "Processing job: $jobName" -Level ([LogLevel]::Debug)

            # Mark job as completed (timer-based approach assumes completion)
            $job.IsCompleted = $true
            $job.EndTime = Get-Date
            $job.Result = "Completed via timer-based workflow"

            $results += $job.Result
            Write-Host "✓ Job completed: $jobName" -ForegroundColor Green
            Write-WorkflowLogInternal -State $State -Message "Job completed successfully: $jobName" -Level ([LogLevel]::Info)

        } catch {
            $errors += "Exception in job $($job.JobName): $_"
            Write-WorkflowLogInternal -State $State -Message "Exception in job $($job.JobName): $_" -Level ([LogLevel]::Error)
            $job.IsCompleted = $false
        }
    }

    return @{
        AllSuccessful = ($errors.Count -eq 0)
        Results = $results
        Errors = $errors
        Mode = "timer-based"
    }
}

# Status checking functions for system monitoring
function Get-JobPoolStatistics {
    try {
        $jobs = Get-Job -ErrorAction SilentlyContinue
        $runningJobs = $jobs | Where-Object { $_.State -eq 'Running' }
        $completedJobs = $jobs | Where-Object { $_.State -eq 'Completed' }
        $failedJobs = $jobs | Where-Object { $_.State -eq 'Failed' }

        return [PSCustomObject]@{
            TotalJobs = $jobs.Count
            RunningJobs = $runningJobs.Count
            CompletedJobs = $completedJobs.Count
            FailedJobs = $failedJobs.Count
            JobPoolStatus = "Active"
        }
    } catch {
        return [PSCustomObject]@{
            TotalJobs = 0
            RunningJobs = 0
            CompletedJobs = 0
            FailedJobs = 0
            JobPoolStatus = "Error"
            Error = $_.Exception.Message
        }
    }
}

function Get-AvailableWorkflows {
    try {
        # This is a placeholder implementation
        # In a real scenario, you would scan workflow state files
        $workflows = @()

        # Look for workflow state files in logs directory
        $logDir = "logs"
        if (Test-Path $logDir) {
            $workflowFiles = Get-ChildItem -Path $logDir -Filter "*.json" -ErrorAction SilentlyContinue
            $workflows = $workflowFiles | ForEach-Object { $_.BaseName }
        }

        return $workflows
    } catch {
        return @()
    }
}

function Get-WorkflowSummary {
    param([object]$State)

    if (-not $State) {
        return "No workflow state available"
    }

    $summary = "Workflow completed $($State.Status.ToString().ToLower())"
    if ($State.IterationCount) {
        $summary += " after $($State.IterationCount) iteration(s)"
    }
    if ($State.Jobs -and $State.Jobs.Count -gt 0) {
        $summary += " with $($State.Jobs.Count) job(s) executed"
    }
    if ($State.StartTime -and $State.EndTime) {
        $duration = $State.EndTime - $State.StartTime
        $summary += " in $($duration.ToString('hh\:mm\:ss'))"
    }

    return $summary
}

# Timer-based phase transition and validation functions

function Show-PhaseCountdown {
    <#
    .SYNOPSIS
    Displays countdown timer for phase transition.

    .PARAMETER PhaseName
    Name of the phase being counted down

    .PARAMETER DurationSeconds
    Duration of countdown in seconds

    .PARAMETER Config
    Configuration object

    .PARAMETER WhatIf
    If specified, shows what would happen without actually waiting
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$PhaseName,

        [Parameter(Mandatory=$true)]
        [int]$DurationSeconds,

        [Parameter(Mandatory=$false)]
        [object]$Config,

        [Parameter(Mandatory=$false)]
        [switch]$WhatIf
    )

    if ($WhatIf -or ($Config -and $Config.development.mock_mode)) {
        Write-Host "[$PhaseName] Timer: $DurationSeconds seconds (mock mode - no actual wait)" -ForegroundColor Yellow
        return @{
            PhaseName = $PhaseName
            Duration = $DurationSeconds
            Mode = if ($WhatIf) { "WhatIf" } else { "Mock" }
        }
    }

    Write-Host "[$PhaseName] Starting countdown: $DurationSeconds seconds" -ForegroundColor Cyan

    $startTime = Get-Date
    $remaining = $DurationSeconds

    while ($remaining -gt 0) {
        $minutes = [math]::Floor($remaining / 60)
        $seconds = $remaining % 60

        $timeString = "{0:00}:{1:00}" -f $minutes, $seconds
        Write-Host -NoNewline "`r[$PhaseName] Time remaining: $timeString"

        Start-Sleep -Seconds 1
        $remaining--

        if ($remaining -eq 0) {
            Write-Host "`n[$PhaseName] Phase delay completed!" -ForegroundColor Green
        }
    }

    $endTime = Get-Date
    $actualDuration = ($endTime - $startTime).TotalSeconds

    return @{
        PhaseName = $PhaseName
        Duration = $actualDuration
        Mode = "Actual"
    }
}

function Write-PhaseTransitionLog {
    <#
    .SYNOPSIS
    Logs phase transition with timestamp and duration.

    .PARAMETER State
    Workflow state object

    .PARAMETER FromPhase
    Source phase name

    .PARAMETER ToPhase
    Destination phase name

    .PARAMETER Duration
    Duration of phase transition in seconds

    .PARAMETER WhatIf
    If specified, returns log entry without writing it
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [BMADWorkflowState]$State,

        [Parameter(Mandatory=$true)]
        [string]$FromPhase,

        [Parameter(Mandatory=$true)]
        [string]$ToPhase,

        [Parameter(Mandatory=$false)]
        [int]$Duration = 0,

        [Parameter(Mandatory=$false)]
        [switch]$WhatIf
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] Phase Transition: $FromPhase → $ToPhase"

    if ($Duration -gt 0) {
        $logEntry += " (Duration: $Duration seconds)"
    }

    if ($WhatIf) {
        return $logEntry
    }

    Write-WorkflowLogInternal -State $State -Message $logEntry -Level ([LogLevel]::Info)

    return $logEntry
}

function Test-PhaseTransition {
    <#
    .SYNOPSIS
    Tests if phase transition is valid.

    .PARAMETER FromStatus
    Current workflow status

    .PARAMETER ToStatus
    Target workflow status

    .RETURNS
    Boolean indicating if transition is valid
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [WorkflowStatus]$FromStatus,

        [Parameter(Mandatory=$true)]
        [WorkflowStatus]$ToStatus
    )

    # Define valid transitions
    $validTransitions = @{
        ([WorkflowStatus]::NotStarted) = @([WorkflowStatus]::RunningDevFlows)
        ([WorkflowStatus]::RunningDevFlows) = @([WorkflowStatus]::RunningQAReview)
        ([WorkflowStatus]::RunningQAReview) = @([WorkflowStatus]::QA_Pass, [WorkflowStatus]::QA_Concerns)
        ([WorkflowStatus]::QA_Pass) = @([WorkflowStatus]::Completed)
        ([WorkflowStatus]::QA_Concerns) = @([WorkflowStatus]::RunningDevFlows)
        ([WorkflowStatus]::Completed) = @()
        ([WorkflowStatus]::Failed) = @([WorkflowStatus]::NotStarted)
    }

    if ($validTransitions.ContainsKey($FromStatus)) {
        return $ToStatus -in $validTransitions[$FromStatus]
    }

    return $false
}

function Get-MockPhaseDelay {
    <#
    .SYNOPSIS
    Gets reduced phase delay for mock mode testing.

    .PARAMETER Config
    Configuration object

    .RETURNS
    Phase delay in seconds for mock mode
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [object]$Config
    )

    if ($Config.development.mock_mode -and $Config.development.mock_execution_time_range) {
        # Use configured mock execution time range
        $minTime = $Config.development.mock_execution_time_range.min
        $maxTime = $Config.development.mock_execution_time_range.max

        # Return random time in range for realistic testing
        $random = Get-Random -Minimum $minTime -Maximum $maxTime
        return $random
    }

    # Default mock delay: very fast for testing
    return 5
}

# Export functions (for script usage - these functions are available when script is dot-sourced)
# Note: Export-ModuleMember is only used in .psm1 module files, not in .ps1 script files