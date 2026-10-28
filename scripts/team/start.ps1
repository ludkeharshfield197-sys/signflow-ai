[CmdletBinding()]
param(
    [switch]$OpenBrowser,
    [switch]$Lan
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$RuntimeRoot = Join-Path $ProjectRoot ".team-runtime"
$PidFile = Join-Path $RuntimeRoot "processes.json"

function Assert-PortFree {
    param([int]$Port, [string]$Name)
    $listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($listener) {
        throw "$Name cannot start because port $Port is already in use by PID $($listener.OwningProcess)."
    }
}

function Assert-LastExitCode {
    param([string]$Action)
    if ($LASTEXITCODE -ne 0) {
        throw "$Action failed with exit code $LASTEXITCODE."
    }
}

function Wait-Endpoint {
    param([string]$Name, [string]$Url, [int]$TimeoutSeconds = 120)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 5
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
                Write-Host "[ready] $Name -> $Url" -ForegroundColor Green
                return
            }
        }
        catch {
            Start-Sleep -Seconds 1
        }
    } while ((Get-Date) -lt $deadline)
    throw "$Name did not become ready within $TimeoutSeconds seconds. See .team-runtime logs."
}

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "The Python environment is missing. Run setup-windows.cmd first."
}
if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot "sign\node_modules") -PathType Container) -or
    -not (Test-Path -LiteralPath (Join-Path $ProjectRoot "sign-app\node_modules") -PathType Container)) {
    throw "Frontend dependencies are missing. Run setup-windows.cmd first."
}

New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null
if (Test-Path -LiteralPath $PidFile -PathType Leaf) {
    $existing = Get-Content -LiteralPath $PidFile -Raw | ConvertFrom-Json
    $alive = @($existing.processes | Where-Object {
        Get-Process -Id ([int]$_.pid) -ErrorAction SilentlyContinue
    })
    if ($alive.Count -gt 0) {
        throw "Managed SignFlow processes are already running. Run stop-windows.cmd before starting again."
    }
    Remove-Item -LiteralPath $PidFile -Force
}

Assert-PortFree 8001 "Backend"
Assert-PortFree 8080 "Desktop Web"
Assert-PortFree 5173 "Mobile H5"

$lanIp = $null
if ($Lan) {
    $lanIp = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -ne "127.0.0.1" -and
            $_.IPAddress -notlike "169.254.*" -and
            $_.AddressState -eq "Preferred"
        } |
        Sort-Object InterfaceMetric |
        Select-Object -ExpandProperty IPAddress -First 1
    if (-not $lanIp) {
        throw "No active LAN IPv4 address was found. Start without -Lan or connect to a network."
    }
}

$origins = @(
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://localhost:5173"
)
if ($lanIp) {
    $origins += "http://${lanIp}:5173"
}

$env:DJANGO_SETTINGS_MODULE = "web_project.settings.dev"
$env:DJANGO_ALLOWED_HOSTS = (@("localhost", "127.0.0.1") + @($lanIp) | Where-Object { $_ }) -join ","
$env:CORS_ALLOWED_ORIGINS = $origins -join ","
$env:CSRF_TRUSTED_ORIGINS = $env:CORS_ALLOWED_ORIGINS
$env:ENABLE_CAMERA_WEBSOCKET = "1"
$env:CELERY_TASK_ALWAYS_EAGER = "1"
$env:DETECTION_AUTO_DISPATCH = "1"
$env:YOLO_AUTOINSTALL = "false"
$env:PYTHONUTF8 = "1"

Push-Location (Join-Path $ProjectRoot "web_project")
try {
    & $Python manage.py migrate --noinput
    Assert-LastExitCode "database migration"
    & $Python manage.py bootstrap_demo
    Assert-LastExitCode "administrator and model bootstrap"
    & $Python manage.py sync_model_cards
    Assert-LastExitCode "model card synchronization"
}
finally {
    Pop-Location
}

$pnpmCommand = if (Get-Command corepack -ErrorAction SilentlyContinue) {
    "corepack pnpm"
}
elseif (Get-Command pnpm -ErrorAction SilentlyContinue) {
    "pnpm"
}
else {
    throw "Corepack or pnpm is missing. Run setup-windows.cmd again."
}

$runId = Get-Date -Format "yyyyMMdd-HHmmss"
$processes = @()
try {
    $backendHost = if ($Lan) { "0.0.0.0" } else { "127.0.0.1" }
    $backend = Start-Process `
        -FilePath $Python `
        -ArgumentList @(
            "-u", "-m", "uvicorn", "web_project.asgi:application",
            "--host", $backendHost, "--port", "8001"
        ) `
        -WorkingDirectory (Join-Path $ProjectRoot "web_project") `
        -RedirectStandardOutput (Join-Path $RuntimeRoot "backend-$runId.stdout.log") `
        -RedirectStandardError (Join-Path $RuntimeRoot "backend-$runId.stderr.log") `
        -WindowStyle Hidden `
        -PassThru
    $processes += [pscustomobject]@{ role = "backend"; pid = $backend.Id; marker = "uvicorn" }

    $desktop = Start-Process `
        -FilePath "cmd.exe" `
        -ArgumentList @("/d", "/s", "/c", "$pnpmCommand run dev") `
        -WorkingDirectory (Join-Path $ProjectRoot "sign") `
        -RedirectStandardOutput (Join-Path $RuntimeRoot "desktop-$runId.stdout.log") `
        -RedirectStandardError (Join-Path $RuntimeRoot "desktop-$runId.stderr.log") `
        -WindowStyle Hidden `
        -PassThru
    $processes += [pscustomobject]@{ role = "desktop"; pid = $desktop.Id; marker = "pnpm run dev" }

    $mobile = Start-Process `
        -FilePath "cmd.exe" `
        -ArgumentList @("/d", "/s", "/c", "$pnpmCommand run dev:h5") `
        -WorkingDirectory (Join-Path $ProjectRoot "sign-app") `
        -RedirectStandardOutput (Join-Path $RuntimeRoot "mobile-$runId.stdout.log") `
        -RedirectStandardError (Join-Path $RuntimeRoot "mobile-$runId.stderr.log") `
        -WindowStyle Hidden `
        -PassThru
    $processes += [pscustomobject]@{ role = "mobile"; pid = $mobile.Id; marker = "pnpm run dev:h5" }

    [pscustomobject]@{
        startedAt = (Get-Date).ToString("o")
        processes = $processes
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $PidFile -Encoding UTF8

    Wait-Endpoint "Backend" "http://127.0.0.1:8001/health/ready"
    Wait-Endpoint "Desktop Web" "http://127.0.0.1:8080/"
    Wait-Endpoint "Mobile H5" "http://127.0.0.1:5173/"
}
catch {
    foreach ($entry in $processes) {
        if (Get-Process -Id ([int]$entry.pid) -ErrorAction SilentlyContinue) {
            & taskkill.exe /PID ([string]$entry.pid) /T /F | Out-Null
        }
    }
    if (Test-Path -LiteralPath $PidFile) {
        Remove-Item -LiteralPath $PidFile -Force
    }
    throw
}

$credentialsPath = Join-Path $ProjectRoot "web_project\.demo-credentials"
Write-Host "`nSignFlow AI is running." -ForegroundColor Green
Write-Host "Desktop Web : http://127.0.0.1:8080/"
Write-Host "Mobile H5   : http://127.0.0.1:5173/#/"
Write-Host "Backend API : http://127.0.0.1:8001/health/ready"
if ($lanIp) {
    Write-Host "Phone H5    : http://${lanIp}:5173/#/"
    Write-Host "Phone API   : http://${lanIp}:8001"
}
Write-Host "Credentials : $credentialsPath"
Write-Host "Logs        : $RuntimeRoot"

if ($OpenBrowser) {
    Start-Process "http://127.0.0.1:8080/"
    Start-Process "http://127.0.0.1:5173/#/"
}

