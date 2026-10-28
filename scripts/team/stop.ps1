[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$PidFile = Join-Path $ProjectRoot ".team-runtime\processes.json"

if (-not (Test-Path -LiteralPath $PidFile -PathType Leaf)) {
    Write-Host "No managed SignFlow process record was found. Nothing was stopped."
    exit 0
}

$metadata = Get-Content -LiteralPath $PidFile -Raw | ConvertFrom-Json
$entries = @($metadata.processes)
[array]::Reverse($entries)

foreach ($entry in $entries) {
    $pidValue = [int]$entry.pid
    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $pidValue" -ErrorAction SilentlyContinue
    if (-not $process) {
        Write-Host "[stopped] $($entry.role) was already closed."
        continue
    }
    if ($process.CommandLine -notlike "*$($entry.marker)*") {
        Write-Warning "Skipped PID $pidValue because it no longer matches the recorded $($entry.role) command."
        continue
    }
    & taskkill.exe /PID ([string]$pidValue) /T /F | Out-Null
    Write-Host "[stopped] $($entry.role) (PID $pidValue)"
}

Remove-Item -LiteralPath $PidFile -Force
Write-Host "SignFlow AI managed services are stopped." -ForegroundColor Green

