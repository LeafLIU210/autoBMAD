# BMAD.Command.Mapper.ps1
# Converts BMAD star commands to natural language task content
# Solves the CLI invocation issue by expanding commands before passing to Claude CLI

# BMAD Command Mapper - Converts star commands to task file paths
function Get-BMADTaskMapping {
    param([string]$Command)

    $mappings = @{
        # Dev Commands
        "*develop-story" = "./develop-story.md"  # Dev development command

        # QA Commands
        "*review" = "./review-story.md"  # QA review command
        "*review-qa" = "./apply-qa-fixes.md"  # Dev fix mode

        # Documentation Commands
        "*create-doc" = ".claude/commands/BMAD/tasks/create-doc.md"  # Create documentation

        # Additional BMAD Commands
        "*create-next-story" = ".claude/commands/BMAD/tasks/create-next-story.md"  # Create next story
        "*validate-next-story" = ".claude/commands/BMAD/tasks/validate-next-story.md"  # Validate next story
        "*execute-checklist" = ".claude/commands/BMAD/tasks/execute-checklist.md"  # Execute checklist
        "*qa-gate" = ".claude/commands/BMAD/tasks/qa-gate.md"  # QA gate decision
        "*test-design" = ".claude/commands/BMAD/tasks/test-design.md"  # Test design
        "*trace-requirements" = ".claude/commands/BMAD/tasks/trace-requirements.md"  # Requirements traceability
        "*risk-profile" = ".claude/commands/BMAD/tasks/risk-profile.md"  # Risk assessment
        "*nfr-assess" = ".claude/commands/BMAD/tasks/nfr-assess.md"  # NFR assessment
        "*index-docs" = ".claude/commands/BMAD/tasks/index-docs.md"  # Index documentation
        "*shard-doc" = ".claude/commands/BMAD/tasks/shard-doc.md"  # Shard documentation
        "*document-project" = ".claude/commands/BMAD/tasks/document-project.md"  # Document project
        "*brownfield-create-story" = ".claude/commands/BMAD/tasks/brownfield-create-story.md"  # Brownfield create story
        "*brownfield-create-epic" = ".claude/commands/BMAD/tasks/brownfield-create-epic.md"  # Brownfield create epic
        "*correct-course" = ".claude/commands/BMAD/tasks/correct-course.md"  # Correct course
        "*advanced-elicitation" = ".claude/commands/BMAD/tasks/advanced-elicitation.md"  # Advanced elicitation
        "*create-brownfield-story" = ".claude/commands/BMAD/tasks/create-brownfield-story.md"  # Create brownfield story
        "*facilitate-brainstorming-session" = ".claude/commands/BMAD/tasks/facilitate-brainstorming-session.md"  # Brainstorming
        "*kb-mode-interaction" = ".claude/commands/BMAD/tasks/kb-mode-interaction.md"  # KB mode interaction
        "*create-deep-research-prompt" = ".claude/commands/BMAD/tasks/create-deep-research-prompt.md"  # Research prompt
        "*generate-ai-frontend-prompt" = ".claude/commands/BMAD/tasks/generate-ai-frontend-prompt.md"  # Frontend prompt
    }

    return $mappings[$Command]
}

function Expand-BMADCommand {
    <#
    .SYNOPSIS
    Expands a BMAD star command into natural language task content.

    .PARAMETER Command
    The BMAD star command to expand (e.g., "*develop-story", "*review")

    .PARAMETER Parameters
    Hashtable of parameters to substitute in the task content

    .PARAMETER WorkflowDir
    Directory of the workflow (bmad-workflow), used for resolving relative paths

    .RETURNS
    Object with TaskName, TaskContent, and TaskFile properties

    .EXAMPLE
    $result = Expand-BMADCommand -Command "*develop-story" -Parameters @{ StoryPath = "test.md" }
    # Returns: @{ TaskName = "Develop Story"; TaskContent = "..."; TaskFile = "..." }
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Command,

        [Parameter(Mandatory=$false)]
        [hashtable]$Parameters = @{},

        [Parameter(Mandatory=$false)]
        [string]$WorkflowDir = $null
    )

    try {
        # Get script directory if WorkflowDir not provided
        if (-not $WorkflowDir) {
            $WorkflowDir = Split-Path -Parent $MyInvocation.PSCommandPath
        }

        # Get task file mapping
        $taskFile = Get-BMADTaskMapping -Command $Command
        if (-not $taskFile) {
            throw "Unknown BMAD command: $Command"
        }

        # Resolve relative paths to absolute paths based on workflow directory
        if ($taskFile -match '^\.\/') {
            # Path like ./develop-story.md - resolve relative to workflow directory
            $taskFile = Join-Path $WorkflowDir $taskFile.Substring(2)  # Remove './' prefix
        } elseif ($taskFile -match '^\.\.\/') {
            # Path like ../something - resolve relative to workflow directory
            $taskFile = Join-Path $WorkflowDir $taskFile
        } elseif (-not [System.IO.Path]::IsPathRooted($taskFile)) {
            # Relative path without ./ prefix - resolve relative to workflow directory
            $taskFile = Join-Path $WorkflowDir $taskFile
        }

        # Check if the task file exists
        if (-not (Test-Path $taskFile)) {
            throw "Task file not found: $taskFile"
        }

        # Read the task content
        $taskContent = Get-Content $taskFile -Raw

        # Determine task name from command
        $taskName = switch ($Command) {
            "*develop-story" { "Develop Story" }
            "*review" { "Review Story" }
            "*review-qa" { "Review QA Feedback" }
            "*create-doc" { "Create Documentation" }
            "*create-next-story" { "Create Next Story" }
            "*validate-next-story" { "Validate Next Story" }
            "*execute-checklist" { "Execute Checklist" }
            "*qa-gate" { "QA Gate Decision" }
            "*test-design" { "Test Design" }
            "*trace-requirements" { "Requirements Traceability" }
            "*risk-profile" { "Risk Assessment" }
            "*nfr-assess" { "NFR Assessment" }
            "*index-docs" { "Index Documentation" }
            "*shard-doc" { "Shard Documentation" }
            "*document-project" { "Document Project" }
            "*brownfield-create-story" { "Brownfield Create Story" }
            "*brownfield-create-epic" { "Brownfield Create Epic" }
            "*correct-course" { "Correct Course" }
            "*advanced-elicitation" { "Advanced Elicitation" }
            "*create-brownfield-story" { "Create Brownfield Story" }
            "*facilitate-brainstorming-session" { "Facilitate Brainstorming" }
            "*kb-mode-interaction" { "KB Mode Interaction" }
            "*create-deep-research-prompt" { "Create Research Prompt" }
            "*generate-ai-frontend-prompt" { "Generate Frontend Prompt" }
            default { "Unknown Task" }
        }

        # Substitute parameters in the task content
        foreach ($param in $Parameters.GetEnumerator()) {
            $pattern = "\{$($param.Key)\}"
            $taskContent = $taskContent -replace $pattern, $param.Value
        }

        # Return expanded command with substituted content
        $result = @{
            TaskName = $taskName
            TaskContent = $taskContent
            TaskFile = $taskFile
        }

        # CRITICAL: Verify StoryPath was substituted
        if ($Parameters.ContainsKey("StoryPath") -and $taskContent -match "\{StoryPath\}") {
            Write-Warning "⚠️  WARNING: StoryPath parameter '$($Parameters.StoryPath)' was NOT substituted in task content. Check if {StoryPath} placeholder exists in task file."
        }

        return $result

    } catch {
        Write-Error "Failed to expand BMAD command '$Command': $_"
        throw
    }
}

function Get-AvailableBMADCommands {
    <#
    .SYNOPSIS
    Gets a list of all available BMAD commands.

    .RETURNS
    Array of command strings
    #>
    [CmdletBinding()]
    param()

    return @(
        # Dev Commands
        "*develop-story",

        # QA Commands
        "*review",
        "*review-qa",

        # Documentation Commands
        "*create-doc",

        # Additional BMAD Commands
        "*create-next-story",
        "*validate-next-story",
        "*execute-checklist",
        "*qa-gate",
        "*test-design",
        "*trace-requirements",
        "*risk-profile",
        "*nfr-assess",
        "*index-docs",
        "*shard-doc",
        "*document-project",
        "*brownfield-create-story",
        "*brownfield-create-epic",
        "*correct-course",
        "*advanced-elicitation",
        "*create-brownfield-story",
        "*facilitate-brainstorming-session",
        "*kb-mode-interaction",
        "*create-deep-research-prompt",
        "*generate-ai-frontend-prompt"
    )
}

function Build-ClaudePrompt {
    <#
    .SYNOPSIS
    Builds a complete Claude CLI prompt from agent persona and task content.

    .PARAMETER AgentPrompt
    The agent persona prompt (from agent file)

    .PARAMETER ExpandedCommand
    The result of Expand-BMADCommand

    .RETURNS
    Complete prompt string for Claude CLI

    .EXAMPLE
    $expanded = Expand-BMADCommand -Command "*develop-story" -Parameters @{ StoryPath = "test.md" }
    $prompt = Build-ClaudePrompt -AgentPrompt "You are a developer." -ExpandedCommand $expanded
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$AgentPrompt,

        [Parameter(Mandatory = $true)]
        [object]$ExpandedCommand
    )

    try {
        # Build base prompt with agent definition first
        $fullPrompt = $AgentPrompt.Trim()

        # Add task definition at the end
        $fullPrompt = $fullPrompt + "`n`n--- Task: $($ExpandedCommand.TaskName) ---`n`n" + $ExpandedCommand.TaskContent.Trim()

        return $fullPrompt

    } catch {
        Write-Error "Failed to build Claude prompt: $_"
        throw
    }
}

# Function to load phase-specific workflow execution configuration
function Get-PhaseExecutionConfig {
    <#
    .SYNOPSIS
    Loads phase-specific execution configuration for timer-based workflow.

    .DESCRIPTION
    Replaces generic Get-WorkflowExecutionConfig with phase-specific
    configuration loading. Integrates with timer-based workflow system
    where phase transitions are time-based, not completion-based.

    .PARAMETER Phase
    Workflow phase identifier (a, b, c, d)

    .PARAMETER ConfigDir
    Configuration directory (default: ./config)

    .RETURNS
    Hashtable with phase-specific configuration
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("a", "b", "c", "d")]
        [string]$Phase,

        [Parameter(Mandatory=$false)]
        [string]$ConfigDir = "./config"
    )

    try {
        # Phase mapping
        $phaseNames = @{
            "a" = "phase-a"
            "b" = "phase-b"
            "c" = "phase-c"
            "d" = "phase-d"
        }

        $phaseName = $phaseNames[$Phase]
        $configPath = Join-Path $ConfigDir "workflow.execution.$phaseName.yaml"

        if (Test-Path $configPath) {
            $yamlContent = Get-Content -Path $configPath -Raw

            # Parse YAML-like structure
            $config = @{
                Phase = $Phase
                PhaseName = $phaseName
                ConfigPath = $configPath
                AutoExecute = $true
                AutoExecuteCommand = "*develop-story"
                ShowHelp = $false
                Timeout = 3600
                AgentType = "dev"
                InstanceCount = if ($Phase -in @("a", "c")) { 3 } else { 1 }
                Command = "*develop-story"
            }

            # Extract values from YAML content
            if ($yamlContent -match 'schema:\s*(\d+)') {
                $config.Schema = [int]$matches[1]
            }

            if ($yamlContent -match 'phase_name:\s*["'']?([^"'']*)["'']?') {
                $config.PhaseDisplayName = $matches[1].Trim()
            }

            if ($yamlContent -match 'agent_type:\s*["'']?([^"'']*)["'']?') {
                $config.AgentType = $matches[1].Trim()
            }

            if ($yamlContent -match 'instance_count:\s*(\d+)') {
                $config.InstanceCount = [int]$matches[1]
            }

            if ($yamlContent -match 'command:\s*["'']?([^"'']*)["'']?') {
                $config.Command = $matches[1].Trim()
            }

            if ($yamlContent -match 'autoExecuteCommand:\s*["'']?([^"'']*)["'']?') {
                $config.AutoExecuteCommand = $matches[1].Trim()
            }

            if ($yamlContent -match 'timeout:\s*(\d+)') {
                $config.Timeout = [int]$matches[1]
            }

            if ($yamlContent -match 'autoExecute:\s*(true|false|yes|no)') {
                $config.AutoExecute = $matches[1] -match '^(true|yes)$'
            }

            if ($yamlContent -match 'showHelp:\s*(true|false|yes|no)') {
                $config.ShowHelp = $matches[1] -match '^(true|yes)$'
            }

            # CRITICAL FIX: Set correct command for QA phase
            if ($Phase -eq "b") {
                $config.AutoExecuteCommand = "*review"
                $config.Command = "*review"
                $config.AgentType = "qa"
                # Update timeout if not specified in YAML
                if ($yamlContent -notmatch 'timeout:\s*(\d+)') {
                    $config.Timeout = 2700  # 45 minutes default for QA
                }
            }

            Write-Host "✅ Loaded config for Phase $Phase ($phaseName)" -ForegroundColor Green
            Write-Host "   Agent: $($config.AgentType), Command: $($config.AutoExecuteCommand), Instances: $($config.InstanceCount)" -ForegroundColor Gray
            return $config
        }

        # Fallback to deprecated config
        $legacyConfigPath = Join-Path $ConfigDir "workflow.execution.config.yaml"
        if (Test-Path $legacyConfigPath) {
            Write-Warning "⚠️  Using deprecated config file - recommend migrating to phase-specific configs"
            return Get-LegacyExecutionConfig -Phase $Phase -ConfigPath $legacyConfigPath
        }

        # Use defaults with QA fix
        $defaultConfig = @{
            AutoExecute = $true
            AutoExecuteCommand = if ($Phase -eq "b") { "*review" } else { "*develop-story" }
            ShowHelp = $false
            Timeout = 3600
            AgentType = if ($Phase -eq "b") { "qa" } else { "dev" }
            InstanceCount = if ($Phase -in @("a", "c")) { 3 } else { 1 }
            Command = if ($Phase -eq "b") { "*review" } else { "*develop-story" }
            Phase = $Phase
            PhaseName = $phaseNames[$Phase]
            ConfigPath = "Defaults"
        }

        Write-Host "ℹ️  Using default config for Phase $Phase" -ForegroundColor Yellow
        return $defaultConfig

    } catch {
        Write-Error "❌ Failed to load config for Phase $Phase : $_"
        throw
    }
}

function Get-LegacyExecutionConfig {
    <#
    .SYNOPSIS
    Parser for legacy configuration file with QA command fix.

    .PARAMETER Phase
    Workflow phase identifier

    .PARAMETER ConfigPath
    Path to legacy config file

    .RETURNS
    Hashtable with configuration (with QA fix applied)
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Phase,

        [Parameter(Mandatory=$true)]
        [string]$ConfigPath
    )

    try {
        $content = Get-Content $ConfigPath -Raw
        $config = @{}

        # Parse basic YAML structure
        if ($content -match 'autoExecute:\s*(true|false|yes|no)') {
            $config.AutoExecute = $matches[1] -match '^(true|yes)$'
        }

        if ($content -match 'autoExecuteCommand:\s*["'']?([^"'']*)["'']?') {
            $config.AutoExecuteCommand = $matches[1].Trim()
        }

        if ($content -match 'showHelp:\s*(true|false|yes|no)') {
            $config.ShowHelp = $matches[1] -match '^(true|yes)$'
        }

        # CRITICAL FIX: Override QA command regardless of what's in legacy config
        if ($Phase -eq "b") {
            $config.AutoExecuteCommand = "*review"
            Write-Warning "⚠️  Legacy config overridden: Phase B set to *review command"
        }

        # Set additional defaults
        $config.AgentType = if ($Phase -eq "b") { "qa" } else { "dev" }
        $config.InstanceCount = if ($Phase -in @("a", "c")) { 3 } else { 1 }
        $config.Timeout = 3600
        $config.Phase = $Phase

        return $config

    } catch {
        Write-Error "❌ Failed to parse legacy config: $_"
        # Return safe defaults with QA fix
        return @{
            AutoExecute = $true
            AutoExecuteCommand = if ($Phase -eq "b") { "*review" } else { "*develop-story" }
            ShowHelp = $false
            AgentType = if ($Phase -eq "b") { "qa" } else { "dev" }
            InstanceCount = if ($Phase -in @("a", "c")) { 3 } else { 1 }
            Timeout = 3600
            Phase = $Phase
        }
    }
}

# Function to load workflow execution configuration (deprecated - use Get-PhaseExecutionConfig)
function Get-WorkflowExecutionConfig {
    <#
    .SYNOPSIS
    [DEPRECATED] Loads the workflow execution configuration for BMAD-Workflow automation.
    Use Get-PhaseExecutionConfig instead for phase-specific configurations.

    .PARAMETER ConfigPath
    Path to the execution configuration file

    .RETURNS
    Hashtable containing execution configuration
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false)]
        [string]$ConfigPath = "./config/workflow.execution.config.yaml"
    )

    Write-Warning "⚠️  Get-WorkflowExecutionConfig is deprecated. Use Get-PhaseExecutionConfig -Phase <phase> instead."

    try {
        $config = @{
            AutoExecute = $false
            AutoExecuteCommand = ""
            ShowHelp = $true
        }

        if (Test-Path $ConfigPath) {
            $configContent = Get-Content $ConfigPath -Raw

            # Parse simple YAML-like structure (basic implementation)
            if ($configContent -match 'autoExecute:\s*(true|false|yes|no)') {
                $config.AutoExecute = $matches[1] -match '^(true|yes)$'
            }

            if ($configContent -match 'autoExecuteCommand:\s*["'']?([^"'']*)["'']?') {
                $config.AutoExecuteCommand = $matches[1].Trim()
            }

            if ($configContent -match 'showHelp:\s*(true|false|yes|no)') {
                $config.ShowHelp = $matches[1] -match '^(true|yes)$'
            }

            Write-Host "Loaded workflow execution config from: $ConfigPath" -ForegroundColor Green
        } else {
            Write-Host "No workflow execution config found at: $ConfigPath, using defaults" -ForegroundColor Gray
        }

        return $config

    } catch {
        Write-Warning "Failed to load workflow execution config: $_"
        return $config  # Return defaults on error
    }
}

function Get-BMADAgentPath {
    <#
    .SYNOPSIS
    Gets the file path for a BMAD agent.

    .PARAMETER AgentType
    The agent type (dev, qa, architect, etc.)

    .RETURNS
    File path to the agent definition file
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$AgentType
    )

    $agentPath = "command/$AgentType.md"
    return $agentPath
}

function Load-BMADAgent {
    <#
    .SYNOPSIS
    Loads a BMAD agent definition from file.

    .PARAMETER AgentType
    The agent type (dev, qa, architect, etc.)

    .RETURNS
    Agent prompt string or fallback prompt
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$AgentType
    )

    try {
        $agentPath = Get-BMADAgentPath -AgentType $AgentType

        if (Test-Path $agentPath) {
            $agentPrompt = Get-Content $agentPath -Raw
            if ($agentPrompt.Trim()) {
                return $agentPrompt
            }
        }

        # Fallback prompts
        $fallbackPrompts = @{
            "dev" = "You are a software developer working on BMAD tasks. Implement requirements thoroughly with comprehensive testing."
            "qa" = "You are a QA engineer working on BMAD tasks. Review implementations against requirements and provide clear decisions."
            "architect" = "You are a software architect working on BMAD tasks. Design solutions that meet requirements and follow best practices."
        }

        $fallbackPrompt = $fallbackPrompts[$AgentType]
        if ($fallbackPrompt) {
            return $fallbackPrompt
        }

        return "You are working on BMAD tasks. Complete the assigned work thoroughly and professionally."

    } catch {
        Write-Warning "Failed to load agent '$AgentType': $_"
        return "You are working on BMAD tasks. Complete the assigned work thoroughly and professionally."
    }
}

# Utility functions for testing and validation
function Test-BMADCommand {
    <#
    .SYNOPSIS
    Tests if a BMAD command is valid and has a mapping.

    .PARAMETER Command
    The command to test

    .RETURNS
    Boolean indicating if command is valid
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Command
    )

    $mapping = Get-BMADTaskMapping -Command $Command
    return $null -ne $mapping
}

function Get-AvailableBMADCommands {
    <#
    .SYNOPSIS
    Gets a list of all available BMAD commands.

    .RETURNS
    Array of command strings
    #>
    [CmdletBinding()]
    param()

    return @("*develop-story", "*review", "*review-qa", "*create-doc")
}

function Validate-BMADTaskFiles {
    <#
    .SYNOPSIS
    Validates that all required BMAD task files exist.

    .RETURNS
    Object with validation results
    #>
    [CmdletBinding()]
    param()

    $commands = Get-AvailableBMADCommands
    $results = @{
        Valid = $true
        MissingFiles = @()
        PresentFiles = @()
    }

    foreach ($command in $commands) {
        $taskFile = Get-BMADTaskMapping -Command $command
        if (Test-Path $taskFile) {
            $results.PresentFiles += $taskFile
        } else {
            $results.Valid = $false
            $results.MissingFiles += $taskFile
        }
    }

    return $results
}

# Note: Export-ModuleMember only works in module files (.psm1), not script files (.ps1)
# Functions are available through dot-sourcing

Write-Host "BMAD Command Mapper module loaded successfully" -ForegroundColor Green
$availableCommands = Get-AvailableBMADCommands
Write-Host "Available commands: $($availableCommands -join ', ')" -ForegroundColor Gray