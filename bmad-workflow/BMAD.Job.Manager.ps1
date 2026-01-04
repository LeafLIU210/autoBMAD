# BMAD.Job.Manager.ps1
# PowerShell job management module for BMAD Workflow Automation
# Version: 1.0.0

# Simple logging function (fallback if Write-WorkflowLogInternal not available)
function Write-WorkflowLogInternal {
    param(
        [object]$State,
        [string]$Message,
        [object]$Level
    )
    # Use Write-Host as fallback
    Write-Host "JobManager: $Message" -ForegroundColor Gray
}

# Log levels for job management logging
enum LogLevel {
    Debug
    Info
    Warning
    Error
}

# Job tracking class
class JobTracker {
    [string]$JobId
    [string]$WorkflowId
    [object]$PowerShellJob
    [string]$Type
    [DateTime]$StartTime
    [DateTime]$EndTime
    [string]$Status
    [string]$Result
    [string]$Error
    [int]$InstanceId
    [string]$TempFile

    JobTracker([string]$jobId, [string]$workflowId, [object]$powerShellJob, [string]$type, [int]$instanceId) {
        $this.JobId = $jobId
        $this.WorkflowId = $workflowId
        $this.PowerShellJob = $powerShellJob
        $this.Type = $type
        $this.InstanceId = $instanceId
        $this.StartTime = Get-Date
        $this.Status = "Running"
    }

    [void] MarkCompleted([string]$result) {
        $this.Status = "Completed"
        $this.EndTime = Get-Date
        $this.Result = $result
    }

    [void] MarkFailed([string]$error) {
        $this.Status = "Failed"
        $this.EndTime = Get-Date
        $this.Error = $error
    }

    [timespan] GetDuration() {
        if ($this.EndTime -eq $null) {
            return (Get-Date) - $this.StartTime
        } else {
            return $this.EndTime - $this.StartTime
        }
    }
}

# Job pool for managing multiple concurrent jobs
class JobPool {
    $Jobs
    [hashtable]$JobLookup
    [object]$Lock

    JobPool() {
        $this.Jobs = @()
        $this.JobLookup = @{}
        $this.Lock = [System.Object]::new()
    }

    [void] AddJob([JobTracker]$job) {
        try {
            $this.Jobs.Add($job)
            $this.JobLookup[$job.JobId] = $job
        } catch {
            Write-WorkflowLogInternal -State $null -Message "Error adding job: $_" -Level ([LogLevel]::Error)
        }
    }

    [object] GetJob([string]$jobId) {
        try {
            return $this.JobLookup[$jobId]
        } catch {
            Write-WorkflowLogInternal -State $null -Message "Error getting job: $_" -Level ([LogLevel]::Error)
            return $null
        }
    }

    [array] GetJobsByStatus([string]$status) {
        try {
            $result = $this.Jobs.Where({ $_.Status -eq $status })
            return ,@($result)  # Ensure array return
        } catch {
            Write-WorkflowLogInternal -State $null -Message "Error getting jobs by status: $_" -Level ([LogLevel]::Error)
            return @()
        }
    }

    [array] GetJobsByType([string]$type) {
        try {
            $result = $this.Jobs.Where({ $_.Type -eq $type })
            return ,@($result)  # Ensure array return
        } catch {
            Write-WorkflowLogInternal -State $null -Message "Error getting jobs by type: $_" -Level ([LogLevel]::Error)
            return @()
        }
    }

    [array] GetJobsByWorkflow([string]$workflowId) {
        try {
            $result = $this.Jobs.Where({ $_.WorkflowId -eq $workflowId })
            return ,@($result)  # Ensure array return
        } catch {
            Write-WorkflowLogInternal -State $null -Message "Error getting jobs by workflow: $_" -Level ([LogLevel]::Error)
            return @()
        }
    }

    [void] RemoveJob([string]$jobId) {
        try {
            $job = $this.JobLookup[$jobId]
            if ($job) {
                $this.Jobs.Remove($job)
                $this.JobLookup.Remove($jobId)

                # Clean up PowerShell job if still exists
                if ($job.PowerShellJob -and (Get-Job -Id $job.PowerShellJob.Id -ErrorAction SilentlyContinue)) {
                    Remove-Job -Job $job.PowerShellJob -Force
                }

                # Clean up temp file if exists
                if ($job.TempFile -and (Test-Path $job.TempFile)) {
                    Remove-Item $job.TempFile -Force
                }
            }
        } catch {
            Write-WorkflowLogInternal -State $null -Message "Error removing job: $_" -Level ([LogLevel]::Error)
        }
    }

    [int] GetActiveJobCount() {
        try {
            $count = $this.Jobs.Where({ $_.Status -eq "Running" }).Count
            return $count
        } catch {
            Write-WorkflowLogInternal -State $null -Message "Error getting active job count: $_" -Level ([LogLevel]::Error)
            return 0
        }
    }

    [hashtable] GetJobStatistics() {
        try {
            $stats = @{
                Total = $this.Jobs.Count
                Running = $this.Jobs.Where({ $_.Status -eq "Running" }).Count
                Completed = $this.Jobs.Where({ $_.Status -eq "Completed" }).Count
                Failed = $this.Jobs.Where({ $_.Status -eq "Failed" }).Count
                ByType = @{}
                AverageDuration = [timespan]::Zero
            }

            # Count by type
            foreach ($job in $this.Jobs) {
                if (-not $stats.ByType.ContainsKey($job.Type)) {
                    $stats.ByType[$job.Type] = 0
                }
                $stats.ByType[$job.Type]++
            }

            # Calculate average duration for completed jobs
            $completedJobs = $this.Jobs.Where({ $_.Status -eq "Completed" -and $_.EndTime })
            if ($completedJobs.Count -gt 0) {
                $totalDuration = [timespan]::Zero
                foreach ($job in $completedJobs) {
                    $totalDuration = $totalDuration + $job.GetDuration()
                }
                $stats.AverageDuration = [timespan]::FromTicks($totalDuration.Ticks / $completedJobs.Count)
            }

            return $stats
        } catch {
            Write-WorkflowLogInternal -State $null -Message "Error getting job statistics: $_" -Level ([LogLevel]::Error)
            return @{
                Total = 0
                Running = 0
                Completed = 0
                Failed = 0
                ByType = @{}
                AverageDuration = [timespan]::Zero
                Error = $_.Exception.Message
            }
        }
    }
}

# Global job pool instance
$script:GlobalJobPool = [JobPool]::new()

# Function to create a new job tracker
function New-JobTracker {
    <#
    .SYNOPSIS
    Creates a new job tracker for monitoring a PowerShell job.

    .PARAMETER WorkflowId
    The workflow ID this job belongs to

    .PARAMETER PowerShellJob
    The PowerShell job object

    .PARAMETER Type
    Type of job (dev, qa, etc.)

    .PARAMETER InstanceId
    Instance ID for this job

    .PARAMETER TempFile
    Temporary file path for job communication

    .RETURNS
    JobTracker object
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$WorkflowId,

        [Parameter(Mandatory=$true)]
        [object]$PowerShellJob,

        [Parameter(Mandatory=$true)]
        [string]$Type,

        [Parameter(Mandatory=$false)]
        [int]$InstanceId = 1,

        [Parameter(Mandatory=$false)]
        [string]$TempFile = ""
    )

    $jobId = [Guid]::NewGuid().ToString()
    $jobTracker = [JobTracker]::new($jobId, $WorkflowId, $PowerShellJob, $Type, $InstanceId)
    $jobTracker.TempFile = $TempFile

    # Add to global job pool
    $script:GlobalJobPool.AddJob($jobTracker)

    return $jobTracker
}

# Function to wait for job completion with monitoring
function Wait-JobWithMonitoring {
    <#
    .SYNOPSIS
    Waits for a job to complete with detailed monitoring and logging.

    .PARAMETER JobTracker
    JobTracker object to monitor

    .PARAMETER TimeoutSeconds
    Maximum time to wait

    .PARAMETER PollingInterval
    How often to check status (seconds)

    .PARAMETER WorkflowState
    Current workflow state for logging

    .RETURNS
    Object with completion results
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [JobTracker]$JobTracker,

        [Parameter(Mandatory=$false)]
        [int]$TimeoutSeconds = 3600,

        [Parameter(Mandatory=$false)]
        [int]$PollingInterval = 5,

        [Parameter(Mandatory=$false)]
        [BMADWorkflowState]$WorkflowState
    )

    $startTime = Get-Date
    $result = @{
        Success = $false
        Output = ""
        Error = ""
        Duration = [timespan]::Zero
    }

    try {
        Write-WorkflowLogInternal -State $WorkflowState -Message "Monitoring job $($JobTracker.JobId) of type $($JobTracker.Type)" -Level ([LogLevel]::Debug)

        do {
            # Check PowerShell job state
            $jobState = $JobTracker.PowerShellJob.State

            if ($jobState -eq "Completed") {
                # Get job results
                try {
                    $jobOutput = Receive-Job -Job $JobTracker.PowerShellJob -Wait
                    $jobErrors = $JobTracker.PowerShellJob.ChildJobs[0].Error

                    if ($jobErrors -and $jobErrors.Count -gt 0) {
                        $errorString = $jobErrors -join "; "
                        $JobTracker.MarkFailed($errorString)
                        $result.Error = $errorString
                        Write-WorkflowLogInternal -State $WorkflowState -Message "Job $($JobTracker.JobId) completed with errors: $errorString" -Level ([LogLevel]::Error)
                    } else {
                        $outputString = $jobOutput -join "`n"
                        $JobTracker.MarkCompleted($outputString)
                        $result.Success = $true
                        $result.Output = $outputString
                        Write-WorkflowLogInternal -State $WorkflowState -Message "Job $($JobTracker.JobId) completed successfully" -Level ([LogLevel]::Info)
                    }
                } catch {
                    $errorString = "Error receiving job output: $_"
                    $JobTracker.MarkFailed($errorString)
                    $result.Error = $errorString
                    Write-WorkflowLogInternal -State $WorkflowState -Message "Error receiving job output for $($JobTracker.JobId): $_" -Level ([LogLevel]::Error)
                }
                break

            } elseif ($jobState -eq "Failed") {
                $errorString = "Job failed: $($JobTracker.PowerShellJob.ChildJobs[0].Exception.Message)"
                $JobTracker.MarkFailed($errorString)
                $result.Error = $errorString
                Write-WorkflowLogInternal -State $WorkflowState -Message "Job $($JobTracker.JobId) failed: $errorString" -Level ([LogLevel]::Error)
                break

            } elseif ($jobState -eq "Stopped") {
                $errorString = "Job was stopped"
                $JobTracker.MarkFailed($errorString)
                $result.Error = $errorString
                Write-WorkflowLogInternal -State $WorkflowState -Message "Job $($JobTracker.JobId) was stopped" -Level ([LogLevel]::Warning)
                break
            }

            # Check timeout
            $elapsed = (Get-Date) - $startTime
            if ($elapsed.TotalSeconds -gt $TimeoutSeconds) {
                $errorString = "Job timed out after $TimeoutSeconds seconds"
                $JobTracker.MarkFailed($errorString)
                $result.Error = $errorString
                Write-WorkflowLogInternal -State $WorkflowState -Message "Job $($JobTracker.JobId) timed out" -Level ([LogLevel]::Error)

                # Force stop the job
                try {
                    Stop-Job -Job $JobTracker.PowerShellJob -Force
                } catch {
                    Write-Warning "Failed to stop job $($JobTracker.JobId): $_"
                }
                break
            }

            # Periodic status logging
            if ($elapsed.TotalSeconds % 60 -eq 0) {
                Write-WorkflowLogInternal -State $WorkflowState -Message "Job $($JobTracker.JobId) still running, elapsed: $($elapsed.ToString('hh\:mm\:ss'))" -Level ([LogLevel]::Debug)
            }

            Start-Sleep -Seconds $PollingInterval

        } while ($true)

    } catch {
        $errorString = "Exception monitoring job: $_"
        $JobTracker.MarkFailed($errorString)
        $result.Error = $errorString
        Write-WorkflowLogInternal -State $WorkflowState -Message "Exception monitoring job $($JobTracker.JobId): $_" -Level ([LogLevel]::Error)
    } finally {
        $result.Duration = $JobTracker.GetDuration()

        # Clean up the PowerShell job
        try {
            if (Get-Job -Id $JobTracker.PowerShellJob.Id -ErrorAction SilentlyContinue) {
                Remove-Job -Job $JobTracker.PowerShellJob -Force
            }
        } catch {
            Write-Warning "Failed to cleanup job $($JobTracker.JobId): $_"
        }
    }

    return $result
}

# Function to wait for multiple jobs
function Wait-MultipleJobs {
    <#
    .SYNOPSIS
    Waits for multiple jobs to complete concurrently.

    .PARAMETER JobTrackers
    Array of JobTracker objects

    .PARAMETER TimeoutSeconds
    Maximum time to wait for all jobs

    .PARAMETER PollingInterval
    How often to check status (seconds)

    .PARAMETER WorkflowState
    Current workflow state for logging

    .RETURNS
    Object with all job results
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [JobTracker[]]$JobTrackers,

        [Parameter(Mandatory=$false)]
        [int]$TimeoutSeconds = 3600,

        [Parameter(Mandatory=$false)]
        [int]$PollingInterval = 5,

        [Parameter(Mandatory=$false)]
        [BMADWorkflowState]$WorkflowState
    )

    $startTime = Get-Date
    $results = @{}
    $completedJobs = @()

    Write-WorkflowLogInternal -State $WorkflowState -Message "Waiting for $($JobTrackers.Count) jobs to complete" -Level ([LogLevel]::Info)

    do {
        $allCompleted = $true
        $anyFailed = $false

        foreach ($jobTracker in $JobTrackers) {
            if ($jobTracker.JobId -notin $completedJobs) {
                $jobState = $jobTracker.PowerShellJob.State

                if ($jobState -eq "Completed") {
                    # Process completed job
                    try {
                        $jobOutput = Receive-Job -Job $jobTracker.PowerShellJob -Wait
                        $jobErrors = $jobTracker.PowerShellJob.ChildJobs[0].Error

                        if ($jobErrors -and $jobErrors.Count -gt 0) {
                            $errorString = $jobErrors -join "; "
                            $jobTracker.MarkFailed($errorString)
                            $results[$jobTracker.JobId] = @{
                                Success = $false
                                Error = $errorString
                                Duration = $jobTracker.GetDuration()
                            }
                            Write-WorkflowLogInternal -State $WorkflowState -Message "Job $($jobTracker.JobId) completed with errors: $errorString" -Level ([LogLevel]::Error)
                            $anyFailed = $true
                        } else {
                            $outputString = $jobOutput -join "`n"
                            $jobTracker.MarkCompleted($outputString)
                            $results[$jobTracker.JobId] = @{
                                Success = $true
                                Output = $outputString
                                Duration = $jobTracker.GetDuration()
                            }
                            Write-WorkflowLogInternal -State $WorkflowState -Message "Job $($jobTracker.JobId) completed successfully" -Level ([LogLevel]::Info)
                        }
                        $completedJobs += $jobTracker.JobId

                        # Clean up
                        Remove-Job -Job $jobTracker.PowerShellJob -Force

                    } catch {
                        $errorString = "Error processing completed job: $_"
                        $jobTracker.MarkFailed($errorString)
                        $results[$jobTracker.JobId] = @{
                            Success = $false
                            Error = $errorString
                            Duration = $jobTracker.GetDuration()
                        }
                        Write-WorkflowLogInternal -State $WorkflowState -Message "Error processing job $($jobTracker.JobId): $_" -Level ([LogLevel]::Error)
                        $anyFailed = $true
                        $completedJobs += $jobTracker.JobId
                    }

                } elseif ($jobState -eq "Failed") {
                    $errorString = "Job failed: $($jobTracker.PowerShellJob.ChildJobs[0].Exception.Message)"
                    $jobTracker.MarkFailed($errorString)
                    $results[$jobTracker.JobId] = @{
                        Success = $false
                        Error = $errorString
                        Duration = $jobTracker.GetDuration()
                    }
                    Write-WorkflowLogInternal -State $WorkflowState -Message "Job $($jobTracker.JobId) failed: $errorString" -Level ([LogLevel]::Error)
                    $completedJobs += $jobTracker.JobId
                    $anyFailed = $true

                    # Clean up
                    Remove-Job -Job $jobTracker.PowerShellJob -Force

                } elseif ($jobState -eq "Stopped") {
                    $errorString = "Job was stopped"
                    $jobTracker.MarkFailed($errorString)
                    $results[$jobTracker.JobId] = @{
                        Success = $false
                        Error = $errorString
                        Duration = $jobTracker.GetDuration()
                    }
                    Write-WorkflowLogInternal -State $WorkflowState -Message "Job $($jobTracker.JobId) was stopped" -Level ([LogLevel]::Warning)
                    $completedJobs += $jobTracker.JobId

                    # Clean up
                    Remove-Job -Job $jobTracker.PowerShellJob -Force

                } else {
                    # Job is still running
                    $allCompleted = $false
                }
            }
        }

        if ($allCompleted) {
            break
        }

        # Check timeout
        $elapsed = (Get-Date) - $startTime
        if ($elapsed.TotalSeconds -gt $TimeoutSeconds) {
            Write-WorkflowLogInternal -State $WorkflowState -Message "Job pool timed out after $TimeoutSeconds seconds" -Level ([LogLevel]::Error)

            # Force stop remaining jobs
            foreach ($jobTracker in $JobTrackers) {
                if ($jobTracker.JobId -notin $completedJobs) {
                    try {
                        Stop-Job -Job $jobTracker.PowerShellJob -Force
                        $jobTracker.MarkFailed("Timed out")
                        $results[$jobTracker.JobId] = @{
                            Success = $false
                            Error = "Job timed out"
                            Duration = $jobTracker.GetDuration()
                        }
                        Remove-Job -Job $jobTracker.PowerShellJob -Force
                    } catch {
                        Write-Warning "Failed to stop job $($jobTracker.JobId): $_"
                    }
                }
            }
            break
        }

        # Periodic status logging
        $runningCount = ($JobTrackers | Where-Object { $_.JobId -notin $completedJobs }).Count
        if ($elapsed.TotalSeconds % 30 -eq 0) {
            Write-WorkflowLogInternal -State $WorkflowState -Message "$runningCount jobs still running, elapsed: $($elapsed.ToString('hh\:mm\:ss'))" -Level ([LogLevel]::Debug)
        }

        Start-Sleep -Seconds $PollingInterval

    } while ($true)

    # Compile final results
    $allResults = $results.Values
    $successCount = ($allResults | Where-Object { $_.Success }).Count
    $totalJobs = $JobTrackers.Count

    Write-WorkflowLogInternal -State $WorkflowState -Message "All jobs completed: $successCount/$totalJobs successful" -Level ([LogLevel]::Info)

    return @{
        AllSuccessful = ($successCount -eq $totalJobs)
        SuccessCount = $successCount
        TotalCount = $totalJobs
        Results = $results
        TotalDuration = (Get-Date) - $startTime
    }
}

# Function to get job pool statistics
function Get-JobPoolStatistics {
    <#
    .SYNOPSIS
    Gets statistics from the global job pool.

    .RETURNS
    Hashtable with job statistics
    #>
    [CmdletBinding()]
    param()

    return $script:GlobalJobPool.GetJobStatistics()
}

# Function to cleanup jobs for a workflow
function Remove-WorkflowJobs {
    <#
    .SYNOPSIS
    Removes all jobs associated with a specific workflow.

    .PARAMETER WorkflowId
    The workflow ID to cleanup jobs for

    .RETURNS
    Number of jobs cleaned up
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$WorkflowId
    )

    $workflowJobs = $script:GlobalJobPool.GetJobsByWorkflow($WorkflowId)
    $cleanupCount = 0

    foreach ($job in $workflowJobs) {
        try {
            # Stop job if still running
            if ($job.PowerShellJob.State -eq "Running") {
                Stop-Job -Job $job.PowerShellJob -Force
            }

            # Remove from job pool (this also cleans up PowerShell job and temp file)
            $script:GlobalJobPool.RemoveJob($job.JobId)
            $cleanupCount++
        } catch {
            Write-Warning "Failed to cleanup job $($job.JobId): $_"
        }
    }

    return $cleanupCount
}

# Note: Export-ModuleMember is only used in .psm1 module files, not in .ps1 script files
# These functions are available when the script is dot-sourced
# Global variable $GlobalJobPool is available when script is dot-sourced