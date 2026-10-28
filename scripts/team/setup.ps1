[CmdletBinding()]
param(
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$VenvRoot = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvRoot "Scripts\python.exe"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Assert-LastExitCode {
    param([string]$Action)
    if ($LASTEXITCODE -ne 0) {
        throw "$Action failed with exit code $LASTEXITCODE."
    }
}

function Resolve-CompatiblePython {
    $candidates = @(
        [pscustomobject]@{ Command = "py"; Arguments = @("-3.11") },
        [pscustomobject]@{ Command = "py"; Arguments = @("-3.12") },
        [pscustomobject]@{ Command = "python"; Arguments = @() }
    )

    foreach ($candidate in $candidates) {
        if (-not (Get-Command $candidate.Command -ErrorAction SilentlyContinue)) {
            continue
        }
        $command = $candidate.Command
        $arguments = @($candidate.Arguments) + @(
            "-c",
            "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        )
        $previousErrorAction = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try {
            $version = (& $command @arguments 2>$null | Select-Object -Last 1)
            $candidateExitCode = $LASTEXITCODE
        }
        finally {
            $ErrorActionPreference = $previousErrorAction
        }
        if ($candidateExitCode -eq 0 -and $version -in @("3.11", "3.12")) {
            return [pscustomobject]@{
                Command = $command
                Arguments = @($candidate.Arguments)
                Version = $version
            }
        }
    }

    throw "Python 3.11 or 3.12 (64-bit) was not found. Install it and rerun setup-windows.cmd."
}

function Invoke-PnpmInstall {
    param([string]$WorkingDirectory)

    Push-Location $WorkingDirectory
    try {
        if (Get-Command corepack -ErrorAction SilentlyContinue) {
            $env:COREPACK_ENABLE_DOWNLOAD_PROMPT = "0"
            & corepack pnpm install --frozen-lockfile
        }
        elseif (Get-Command pnpm -ErrorAction SilentlyContinue) {
            & pnpm install --frozen-lockfile
        }
        else {
            throw "Neither Corepack nor pnpm is available. Install Node.js 20+ and rerun."
        }
        Assert-LastExitCode "pnpm install in $WorkingDirectory"
    }
    finally {
        Pop-Location
    }
}

Write-Host "SignFlow AI teammate setup" -ForegroundColor Green
Write-Host "Project: $ProjectRoot"

$requiredFiles = @(
    "web_project\manage.py",
    "web_project\requirements\dev.txt",
    "web_project\requirements\prod.txt",
    "web_project\model\ASl-v8.pt",
    "web_project\model\csl.pt",
    "sign\package.json",
    "sign\pnpm-lock.yaml",
    "sign-app\package.json",
    "sign-app\pnpm-lock.yaml"
)
foreach ($relativePath in $requiredFiles) {
    $absolutePath = Join-Path $ProjectRoot $relativePath
    if (-not (Test-Path -LiteralPath $absolutePath -PathType Leaf)) {
        throw "Required package file is missing: $relativePath"
    }
}

$pythonLauncher = Resolve-CompatiblePython
$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCommand) {
    throw "Node.js 20 or newer was not found. Install the LTS release and rerun."
}
$nodeMajor = [int]((& node -p "process.versions.node.split('.')[0]").Trim())
Assert-LastExitCode "Node.js version check"
if ($nodeMajor -lt 20) {
    throw "Node.js 20 or newer is required; detected major version $nodeMajor."
}
if (-not (Get-Command corepack -ErrorAction SilentlyContinue) -and
    -not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    throw "Corepack or pnpm was not found. Install a current Node.js release and rerun."
}

Write-Host "Python $($pythonLauncher.Version) and Node.js $(& node --version) are available."
Write-Host "Bundled inference weights: ASL-80 and CSL-37. No training step will be run."

if ($CheckOnly) {
    Write-Host "Package preflight passed." -ForegroundColor Green
    exit 0
}

$drive = Get-Item -LiteralPath $ProjectRoot
if ($drive.PSDrive.Free -lt 6GB) {
    Write-Warning "Less than 6 GB is free. Python AI dependencies can require several GB after installation."
}

if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
    Write-Step "Creating the isolated Python environment"
    $createArguments = @($pythonLauncher.Arguments) + @("-m", "venv", $VenvRoot)
    $pythonCommand = $pythonLauncher.Command
    & $pythonCommand @createArguments
    Assert-LastExitCode "Python virtual environment creation"
}

Write-Step "Installing pinned backend and inference dependencies"
& $VenvPython -m pip install --upgrade pip setuptools wheel
Assert-LastExitCode "pip bootstrap"
& $VenvPython -m pip install `
    -r (Join-Path $ProjectRoot "web_project\requirements\dev.txt") `
    -r (Join-Path $ProjectRoot "web_project\requirements\prod.txt")
Assert-LastExitCode "backend dependency installation"

Write-Step "Installing desktop Web dependencies"
Invoke-PnpmInstall (Join-Path $ProjectRoot "sign")

Write-Step "Installing mobile H5 and mini-program dependencies"
Invoke-PnpmInstall (Join-Path $ProjectRoot "sign-app")

Write-Step "Initializing the local database, administrator, and bilingual models"
$env:DJANGO_SETTINGS_MODULE = "web_project.settings.dev"
$env:YOLO_AUTOINSTALL = "false"
$env:CELERY_TASK_ALWAYS_EAGER = "1"
$env:DETECTION_AUTO_DISPATCH = "1"
$env:ENABLE_CAMERA_WEBSOCKET = "1"
Push-Location (Join-Path $ProjectRoot "web_project")
try {
    & $VenvPython manage.py migrate --noinput
    Assert-LastExitCode "database migration"
    & $VenvPython manage.py bootstrap_demo
    Assert-LastExitCode "administrator and model bootstrap"
    & $VenvPython manage.py sync_model_cards
    Assert-LastExitCode "model card synchronization"
    & $VenvPython manage.py check
    Assert-LastExitCode "Django system check"
}
finally {
    Pop-Location
}

$credentialsPath = Join-Path $ProjectRoot "web_project\.demo-credentials"
Write-Host "`nSetup completed." -ForegroundColor Green
Write-Host "Credentials are stored locally at: $credentialsPath"
Write-Host "Read them with: Get-Content `"$credentialsPath`""
Write-Host "Next: double-click start-windows.cmd or run .\scripts\team\start.ps1 -OpenBrowser"
