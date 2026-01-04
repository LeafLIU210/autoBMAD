# BMAD.Hooks.Handler.ps1
# Claude Code hooks handler module for BMAD Workflow Automation
# Version: 1.0.0

# Note: System.Collections.Generic is available by default in PowerShell

# Simple logging function (fallback if Write-WorkflowLogInternal not available)
function Write-WorkflowLogInternal {
    param(
        [object]$State,
        [string]$Message,
        [object]$Level
    )
    # Use Write-Host as fallback
    Write-Host "Hook: $Message" -ForegroundColor Gray
}

# Log levels for hook logging
enum LogLevel {
    Debug
    Info
    Warning
    Error
}

# Hook event types
enum HookEventType {
    ToolUse
    Message
    SessionComplete
    ToolStart
    ToolEnd
    Error
    Custom
}

# Hook event data
class HookEventData {
    [string]$EventType
    [string]$EventId
    [DateTime]$Timestamp
    [string]$WorkflowId
    [hashtable]$Data
    [string]$RawData

    HookEventData([string]$eventType, [hashtable]$data, [string]$rawData = "") {
        $this.EventType = $eventType
        $this.EventId = [Guid]::NewGuid().ToString()
        $this.Timestamp = Get-Date
        $this.Data = $data
        $this.RawData = $rawData
    }
}

# Hook handler for processing Claude Code events
class HookHandler {
    [string]$HookDirectory
    [hashtable]$RegisteredHandlers
    [object]$Lock
    [scriptblock]$DefaultHandler

    HookHandler() {
        $this.HookDirectory = "./hooks"
        $this.RegisteredHandlers = @{}
        $this.Lock = [System.Object]::new()

        # Ensure hook directory exists
        if (-not (Test-Path $this.HookDirectory)) {
            New-Item -Path $this.HookDirectory -ItemType Directory -Force | Out-Null
        }

        # Initialize default handler
        $this.DefaultHandler = {
            param($eventData)
            Write-WorkflowLogInternal -State $null -Message "Hook event received: $($eventData.EventType) - $($eventData.Data | ConvertTo-Json -Compress)" -Level ([LogLevel]::Debug)
        }
    }

    HookHandler([string]$hookDirectory) {
        $this.HookDirectory = $hookDirectory
        $this.RegisteredHandlers = @{}
        $this.Lock = [System.Object]::new()

        # Ensure hook directory exists
        if (-not (Test-Path $this.HookDirectory)) {
            New-Item -Path $this.HookDirectory -ItemType Directory -Force | Out-Null
        }

        # Initialize default handler
        $this.DefaultHandler = {
            param($eventData)
            Write-WorkflowLogInternal -State $null -Message "Hook event received: $($eventData.EventType) - $($eventData.Data | ConvertTo-Json -Compress)" -Level ([LogLevel]::Debug)
        }
    }

    [void] RegisterHandler([string]$eventType, [string]$scriptPath) {
        try {
            $this.RegisteredHandlers[$eventType] = $scriptPath
            Write-WorkflowLogInternal -State $null -Message "Registered hook handler: $eventType -> $scriptPath" -Level ([LogLevel]::Info)
        } catch {
            Write-WorkflowLogInternal -State $null -Message "Failed to register handler: $_" -Level ([LogLevel]::Error)
        }
    }

    [void] UnregisterHandler([string]$eventType) {
        try {
            if ($this.RegisteredHandlers.ContainsKey($eventType)) {
                $this.RegisteredHandlers.Remove($eventType)
                Write-WorkflowLogInternal -State $null -Message "Unregistered hook handler: $eventType" -Level ([LogLevel]::Info)
            }
        } catch {
            Write-WorkflowLogInternal -State $null -Message "Failed to unregister handler: $_" -Level ([LogLevel]::Error)
        }
    }

    [bool] ProcessEvent([HookEventData]$eventData) {
        try {
            $eventType = $eventData.EventType

            # Find handler for this event type
            $handlerScript = $null
            if ($this.RegisteredHandlers.ContainsKey($eventType)) {
                $handlerScript = $this.RegisteredHandlers[$eventType]
            }

            if ($handlerScript -and (Test-Path $handlerScript)) {
                # Execute custom handler
                Write-WorkflowLogInternal -State $null -Message "Processing hook event: $eventType with custom handler" -Level ([LogLevel]::Debug)

                $result = & $handlerScript -EventData $eventData
                return ($result -eq $true)
            } else {
                # Use default handler
                & $this.DefaultHandler $eventData
                return $true
            }

        } catch {
            Write-WorkflowLogInternal -State $null -Message "Error processing hook event: $_" -Level ([LogLevel]::Error)
            return $false
        }
    }

    [hashtable] GetRegisteredHandlers() {
        try {
            return $this.RegisteredHandlers.Clone()
        } catch {
            return @{}
        }
    }

    [void] LoadHooksFromConfig([string]$configPath) {
        try {
            if (Test-Path $configPath) {
                Write-WorkflowLogInternal -State $null -Message "Loading hooks from: $configPath" -Level ([LogLevel]::Debug)

                # Read JSON with proper encoding handling
                $rawContent = Get-Content $configPath -Raw -Encoding UTF8
                Write-WorkflowLogInternal -State $null -Message "Config file content length: $($rawContent.Length)" -Level ([LogLevel]::Debug)

                # Check if content is empty or contains invalid characters
                if ([string]::IsNullOrWhiteSpace($rawContent)) {
                    throw "Configuration file is empty or contains only whitespace"
                }

                # Convert from JSON with better error handling
                try {
                    $config = $rawContent | ConvertFrom-Json
                } catch {
                    Write-WorkflowLogInternal -State $null -Message "JSON parsing failed. Content preview: $($rawContent.Substring(0, [Math]::Min(200, $rawContent.Length)))" -Level ([LogLevel]::Error)
                    throw "JSON parsing error: $_"
                }

                if (-not $config.hooks) {
                    throw "Configuration file missing 'hooks' section"
                }

                $loadedCount = 0
                foreach ($hook in $config.hooks.PSObject.Properties) {
                    if ($hook.Value.enabled) {
                        $this.RegisterHandler($hook.Name, $hook.Value.command)
                        $loadedCount++
                    }
                }

                Write-WorkflowLogInternal -State $null -Message "Loaded $loadedCount hooks from configuration (total: $($config.hooks.PSObject.Properties.Count))" -Level ([LogLevel]::Info)
            } else {
                Write-WorkflowLogInternal -State $null -Message "Hooks configuration file not found: $configPath" -Level ([LogLevel]::Warning)
            }
        } catch {
            Write-WorkflowLogInternal -State $null -Message "Failed to load hooks configuration from '$configPath': $_" -Level ([LogLevel]::Error)
            Write-WorkflowLogInternal -State $null -Message "Stack trace: $($_.ScriptStackTrace)" -Level ([LogLevel]::Error)
        }
    }
}

# Global hook handler instance
$script:GlobalHookHandler = [HookHandler]::new()

# Function to register Claude Code hooks
function Register-ClaudeHooks {
    <#
    .SYNOPSIS
    Registers Claude Code CLI hooks for workflow monitoring.

    .PARAMETER ConfigPath
    Path to hooks configuration file

    .PARAMETER HookDirectory
    Directory containing hook scripts

    .RETURNS
    True if successful, false otherwise
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$ConfigPath = "./config/claude.hooks.json",

        [Parameter(Mandatory=$false)]
        [string]$HookDirectory = "./hooks"
    )

    try {
        # Create hook directory if it doesn't exist
        if (-not (Test-Path $HookDirectory)) {
            New-Item -Path $HookDirectory -ItemType Directory -Force | Out-Null
        }

        # Load hooks from configuration
        $script:GlobalHookHandler.LoadHooksFromConfig($ConfigPath)

        # Register default hooks
        Register-DefaultHooks -HookDirectory $HookDirectory

        Write-WorkflowLogInternal -State $null -Message "Claude hooks registered successfully" -Level ([LogLevel]::Info)
        return $true

    } catch {
        Write-WorkflowLogInternal -State $null -Message "Failed to register Claude hooks: $_" -Level ([LogLevel]::Error)
        return $false
    }
}

# Function to register default hooks
function Register-DefaultHooks {
    <#
    .SYNOPSIS
    Registers default hook handlers for common events.

    .PARAMETER HookDirectory
    Directory containing hook scripts
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$HookDirectory = "./hooks"
    )

    # Tool use hook
    $toolUseScript = Join-Path $HookDirectory "ToolUseHandler.ps1"
    if (-not (Test-Path $toolUseScript)) {
        Create-ToolUseHandler -Path $toolUseScript
    }
    $script:GlobalHookHandler.RegisterHandler("tool_use", $toolUseScript)

    # Message hook
    $messageScript = Join-Path $HookDirectory "MessageHandler.ps1"
    if (-not (Test-Path $messageScript)) {
        Create-MessageHandler -Path $messageScript
    }
    $script:GlobalHookHandler.RegisterHandler("message", $messageScript)

    # Session complete hook
    $sessionCompleteScript = Join-Path $HookDirectory "SessionCompleteHandler.ps1"
    if (-not (Test-Path $sessionCompleteScript)) {
        Create-SessionCompleteHandler -Path $sessionCompleteScript
    }
    $script:GlobalHookHandler.RegisterHandler("session_complete", $sessionCompleteScript)
}

# Function to create tool use handler
function Create-ToolUseHandler {
    <#
    .SYNOPSIS
    Creates a default tool use hook handler script.

    .PARAMETER Path
    Path where to create the handler script
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )

    $handlerContent = @'
# Tool Use Hook Handler
# This script is called when Claude Code CLI uses a tool

param(
    [Parameter(Mandatory=$true)]
    [object]$EventData
)

try {
    # Extract tool information
    $toolName = $EventData.Data.tool_name
    $workflowId = $EventData.Data.workflow_id
    $timestamp = $EventData.Timestamp

    Write-Host "[$timestamp] Tool Used: $toolName (Workflow: $workflowId)"

    # Log tool usage
    if ($workflowId) {
        $state = Load-WorkflowState -WorkflowId $workflowId
        if ($state) {
            Write-WorkflowLogInternal -State $state -Message "Tool used: $toolName" -Level ([LogLevel]::Debug)
        }
    }

    # Custom logic based on tool type
    switch ($toolName) {
        "bash" {
            # Monitor bash command execution
            Write-Host "Executing bash command: $($EventData.Data.command)"
        }
        "read" {
            # Monitor file reading
            Write-Host "Reading file: $($EventData.Data.file_path)"
        }
        "write" {
            # Monitor file writing
            Write-Host "Writing file: $($EventData.Data.file_path)"
        }
        default {
            Write-Host "Unknown tool: $toolName"
        }
    }

    return $true

} catch {
    Write-Error "Error in tool use handler: $_"
    return $false
}
'@

    $handlerContent | Out-File -FilePath $Path -Encoding UTF8
    Write-WorkflowLogInternal -State $null -Message "Created tool use handler: $Path" -Level ([LogLevel]::Info)
}

# Function to create message handler
function Create-MessageHandler {
    <#
    .SYNOPSIS
    Creates a default message hook handler script.

    .PARAMETER Path
    Path where to create the handler script
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )

    $handlerContent = @'
# Message Hook Handler
# This script is called when Claude Code CLI sends/receives messages

param(
    [Parameter(Mandatory=$true)]
    [object]$EventData
)

try {
    # Extract message information
    $messageType = $EventData.Data.message_type
    $workflowId = $EventData.Data.workflow_id
    $timestamp = $EventData.Timestamp
    $content = $EventData.Data.content

    Write-Host "[$timestamp] Message: $messageType (Workflow: $workflowId)"

    # Log message
    if ($workflowId) {
        $state = Load-WorkflowState -WorkflowId $workflowId
        if ($state) {
            # Truncate long messages for logging
            $logContent = if ($content.Length -gt 200) {
                $content.Substring(0, 197) + "..."
            } else {
                $content
            }
            Write-WorkflowLogInternal -State $state -Message "Message ($messageType): $logContent" -Level ([LogLevel]::Debug)
        }
    }

    # Custom logic based on message type
    switch ($messageType) {
        "user_input" {
            Write-Host "User input received"
        }
        "assistant_response" {
            Write-Host "Assistant response generated"
        }
        "error" {
            Write-Host "Error message received: $content"
        }
        default {
            Write-Host "Unknown message type: $messageType"
        }
    }

    return $true

} catch {
    Write-Error "Error in message handler: $_"
    return $false
}
'@

    $handlerContent | Out-File -FilePath $Path -Encoding UTF8
    Write-WorkflowLogInternal -State $null -Message "Created message handler: $Path" -Level ([LogLevel]::Info)
}

# Function to create session complete handler
function Create-SessionCompleteHandler {
    <#
    .SYNOPSIS
    Creates a default session complete hook handler script.

    .PARAMETER Path
    Path where to create the handler script
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )

    $handlerContent = @'
# Session Complete Hook Handler
# This script is called when Claude Code CLI session completes

param(
    [Parameter(Mandatory=$true)]
    [object]$EventData
)

try {
    # Extract session information
    $workflowId = $EventData.Data.workflow_id
    $timestamp = $EventData.Timestamp
    $sessionId = $EventData.Data.session_id
    $result = $EventData.Data.result
    $duration = $EventData.Data.duration

    Write-Host "[$timestamp] Session Complete: $sessionId (Workflow: $workflowId)"
    Write-Host "Result: $result"
    Write-Host "Duration: $duration"

    # Update workflow state
    if ($workflowId) {
        $state = Load-WorkflowState -WorkflowId $workflowId
        if ($state) {
            Write-WorkflowLogInternal -State $state -Message "Session completed: $sessionId - Result: $result - Duration: $duration" -Level ([LogLevel]::Info)

            # Update relevant jobs in the workflow state
            $sessionJobs = $state.Jobs | Where-Object { $_.JobName -match $sessionId }
            foreach ($job in $sessionJobs) {
                $job.IsCompleted = $true
                $job.EndTime = Get-Date
                $job.Result = $result
            }

            # Save updated state
            Save-WorkflowState -State $state
        }
    }

    # Create session completion report
    $reportPath = "./logs/session-$sessionId-complete.log"
    $report = @"
Session Completion Report
=========================
Session ID: $sessionId
Workflow ID: $workflowId
Timestamp: $timestamp
Result: $result
Duration: $duration
Raw Data: $($EventData.RawData)
"@
    $report | Out-File -FilePath $reportPath -Encoding UTF8

    return $true

} catch {
    Write-Error "Error in session complete handler: $_"
    return $false
}
'@

    $handlerContent | Out-File -FilePath $Path -Encoding UTF8
    Write-WorkflowLogInternal -State $null -Message "Created session complete handler: $Path" -Level ([LogLevel]::Info)
}

# Function to trigger hook event
function Invoke-HookEvent {
    <#
    .SYNOPSIS
    Triggers a hook event for processing by registered handlers.

    .PARAMETER EventType
    Type of hook event

    .PARAMETER Data
    Event data as hashtable

    .PARAMETER RawData
    Raw event data string

    .PARAMETER WorkflowId
    Associated workflow ID

    .RETURNS
    True if event was processed successfully, false otherwise
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$EventType,

        [Parameter(Mandatory=$false)]
        [hashtable]$Data = @{},

        [Parameter(Mandatory=$false)]
        [string]$RawData = "",

        [Parameter(Mandatory=$false)]
        [string]$WorkflowId = ""
    )

    try {
        # Create event data object
        $eventData = [HookEventData]::new($EventType, $Data, $RawData)
        $eventData.WorkflowId = $WorkflowId

        # Process the event
        $result = $script:GlobalHookHandler.ProcessEvent($eventData)

        Write-WorkflowLogInternal -State $null -Message "Hook event triggered: $EventType - Result: $result" -Level ([LogLevel]::Debug)

        return $result

    } catch {
        Write-WorkflowLogInternal -State $null -Message "Failed to trigger hook event: $_" -Level ([LogLevel]::Error)
        return $false
    }
}

# Function to get hook handler status
function Get-HookHandlerStatus {
    <#
    .SYNOPSIS
    Gets the current status of hook handlers.

    .RETURNS
    Hashtable with handler status information
    #>
    [CmdletBinding()]
    param()

    try {
        $handlers = $script:GlobalHookHandler.GetRegisteredHandlers()
        $status = @{
            TotalHandlers = $handlers.Count
            Handlers = @{}
            HookDirectory = $script:GlobalHookHandler.HookDirectory
        }

        foreach ($handler in $handlers.GetEnumerator()) {
            $status.Handlers[$handler.Key] = @{
                ScriptPath = $handler.Value
                Exists = Test-Path $handler.Value
                LastModified = if (Test-Path $handler.Value) { (Get-Item $handler.Value).LastWriteTime } else { $null }
            }
        }

        return $status

    } catch {
        Write-WorkflowLogInternal -State $null -Message "Failed to get hook handler status: $_" -Level ([LogLevel]::Error)
        return @{}
    }
}

# Function to unregister all hooks
function Unregister-AllHooks {
    <#
    .SYNOPSIS
    Unregisters all hook handlers.

    .RETURNS
    True if successful, false otherwise
    #>
    [CmdletBinding()]
    param()

    try {
        $handlers = $script:GlobalHookHandler.GetRegisteredHandlers()
        $count = $handlers.Count

        foreach ($eventType in $handlers.Keys) {
            $script:GlobalHookHandler.UnregisterHandler($eventType)
        }

        Write-WorkflowLogInternal -State $null -Message "Unregistered $count hook handlers" -Level ([LogLevel]::Info)
        return $true

    } catch {
        Write-WorkflowLogInternal -State $null -Message "Failed to unregister hooks: $_" -Level ([LogLevel]::Error)
        return $false
    }
}

# Note: Export-ModuleMember is only used in .psm1 module files, not in .ps1 script files
# These functions are available when the script is dot-sourced
# Global variable $GlobalHookHandler is available when script is dot-sourced