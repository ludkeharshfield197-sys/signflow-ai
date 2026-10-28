[CmdletBinding()]
param(
    [string]$OutputDirectory = "",
    [string]$PackageLabel = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $ProjectRoot "deliverables"
}
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)
if (-not $PackageLabel) {
    $PackageLabel = Get-Date -Format "yyyy-MM-dd-HHmmss"
}

$StageRoot = Join-Path ([IO.Path]::GetTempPath()) ("signflow-package-" + [guid]::NewGuid().ToString("N"))
$PackageRoot = Join-Path $StageRoot "SignFlow-AI"
$ZipPath = Join-Path $OutputDirectory "SignFlow-AI-teammate-project-$PackageLabel.zip"

function Test-ExcludedPath {
    param([string]$RelativePath)

    $normalized = $RelativePath.Replace("\", "/")
    $segments = $normalized.Split("/")
    $excludedSegments = @(
        ".git", ".idea", ".vscode", ".venv", ".ruff_cache", ".pytest_cache",
        "__pycache__", "node_modules", "node_modules-pre-redesign", "dist", "unpackage",
        "test-results", "playwright-report", "logs", "media", "staticfiles",
        ".team-runtime", ".codex-runtime", "legacy-hbuilderx"
    )
    foreach ($segment in $segments) {
        if ($segment -in $excludedSegments) {
            return $true
        }
    }

    $leaf = [IO.Path]::GetFileName($normalized)
    if ($leaf -eq ".env.example") {
        return $false
    }
    if ($leaf -like ".env*") {
        return $true
    }
    if ($leaf -in @(".demo-credentials", ".coverage", "Thumbs.db", ".DS_Store")) {
        return $true
    }
    if ($leaf -like "celerybeat-schedule*") {
        return $true
    }
    if ([IO.Path]::GetExtension($leaf) -in @(".pyc", ".pyo", ".sqlite3", ".log")) {
        return $true
    }
    return $false
}

function Copy-RelativeFile {
    param([string]$RelativePath)

    if (Test-ExcludedPath $RelativePath) {
        return
    }
    $source = Join-Path $ProjectRoot $RelativePath
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
        throw "Package source file is missing: $RelativePath"
    }
    $destination = Join-Path $PackageRoot $RelativePath
    $destinationDirectory = Split-Path -Parent $destination
    New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $destination
}

function Copy-RelativeTree {
    param([string]$RelativeDirectory)

    $sourceRoot = Join-Path $ProjectRoot $RelativeDirectory
    if (-not (Test-Path -LiteralPath $sourceRoot -PathType Container)) {
        throw "Package source directory is missing: $RelativeDirectory"
    }
    Get-ChildItem -LiteralPath $sourceRoot -Recurse -Force -File | ForEach-Object {
        $relativePath = $_.FullName.Substring($ProjectRoot.Length).TrimStart("\")
        Copy-RelativeFile $relativePath
    }
}

New-Item -ItemType Directory -Path $PackageRoot -Force | Out-Null
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

try {
    $rootFiles = @(
        ".dockerignore",
        ".env.example",
        ".gitignore",
        "docker-compose.yml",
        "Dockerfile.backend",
        "Dockerfile.frontend",
        "LICENSE",
        "README.md",
        "TEAM-QUICKSTART.md",
        "setup-windows.cmd",
        "start-windows.cmd",
        "stop-windows.cmd",
        "check-windows.cmd"
    )
    foreach ($relativePath in $rootFiles) {
        Copy-RelativeFile $relativePath
    }

    foreach ($relativeDirectory in @("deploy", "scripts\team", "sign", "sign-app", "web_project")) {
        Copy-RelativeTree $relativeDirectory
    }

    $documentationFiles = @(
        "docs\runbook.md",
        "docs\mobile-mini-program.md",
        "docs\release-checklist.md",
        "docs\competition-script.md",
        "docs\model-evaluation\2026-07-30-model-evaluation.md",
        "docs\design\commercial-redesign\design-system.md"
    )
    foreach ($relativePath in $documentationFiles) {
        Copy-RelativeFile $relativePath
    }
    Copy-RelativeTree "docs\product"
    Get-ChildItem -LiteralPath (Join-Path $ProjectRoot "docs\competition") -File -Filter "*.md" |
        ForEach-Object {
            $relativePath = $_.FullName.Substring($ProjectRoot.Length).TrimStart("\")
            Copy-RelativeFile $relativePath
        }
    Copy-RelativeTree "docs\competition\report-assets-2026-07-30"

    $checksumLines = Get-ChildItem -LiteralPath $PackageRoot -Recurse -Force -File |
        Sort-Object FullName |
        ForEach-Object {
            $relativePath = $_.FullName.Substring($PackageRoot.Length + 1).Replace("\", "/")
            $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
            "$hash  $relativePath"
        }
    $checksumLines | Set-Content -LiteralPath (Join-Path $PackageRoot "PACKAGE-SHA256SUMS.txt") -Encoding UTF8

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    if (Test-Path -LiteralPath $ZipPath) {
        throw "Output archive already exists: $ZipPath"
    }
    [IO.Compression.ZipFile]::CreateFromDirectory(
        $StageRoot,
        $ZipPath,
        [IO.Compression.CompressionLevel]::Optimal,
        $false
    )

    $archive = Get-Item -LiteralPath $ZipPath
    if ($archive.Length -ge 200MB) {
        throw "Archive is $([math]::Round($archive.Length / 1MB, 2)) MB, exceeding the 200 MB limit."
    }
    $zipHash = (Get-FileHash -LiteralPath $ZipPath -Algorithm SHA256).Hash
    Write-Host "Package: $ZipPath" -ForegroundColor Green
    Write-Host "Size   : $([math]::Round($archive.Length / 1MB, 2)) MB"
    Write-Host "SHA256 : $zipHash"
}
finally {
    if (Test-Path -LiteralPath $StageRoot) {
        $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd("\") + "\"
        $resolvedStage = [IO.Path]::GetFullPath($StageRoot)
        if (-not $resolvedStage.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove a staging path outside the system temporary directory: $resolvedStage"
        }
        Remove-Item -LiteralPath $resolvedStage -Recurse -Force
    }
}
