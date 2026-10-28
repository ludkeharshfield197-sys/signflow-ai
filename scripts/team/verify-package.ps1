[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ArchivePath
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$resolvedArchive = (Resolve-Path -LiteralPath $ArchivePath).Path
Add-Type -AssemblyName System.IO.Compression.FileSystem

$archive = [IO.Compression.ZipFile]::OpenRead($resolvedArchive)
try {
    $entries = @($archive.Entries)
    $suspicious = @($entries | Where-Object {
        $name = $_.FullName.Replace([char]92, [char]47)
        ($name -match '(^|/)\.git(/|$)') -or
        ($name -match '(^|/)\.venv(/|$)') -or
        ($name -match '(^|/)node_modules(/|$)') -or
        ($name -match '(^|/)(media|logs|dist|unpackage)(/|$)') -or
        ($name -match '(^|/)\.env$') -or
        ($name -match '(^|/)\.demo-credentials$') -or
        ($name -match '\.(sqlite3|pyc|pyo|log)$')
    })
    if ($suspicious.Count -gt 0) {
        throw "Excluded private or generated entries were found: $($suspicious.FullName -join ', ')"
    }

    $modelEntries = @($entries | Where-Object {
        $_.FullName.Replace([char]92, [char]47) -like 'SignFlow-AI/web_project/model/*.pt'
    })
    if ($modelEntries.Count -lt 2) {
        throw "The archive must contain at least the bundled ASL and CSL model weights."
    }
    Write-Host "ZIP entries       : $($entries.Count)"
    Write-Host "Bundled .pt models: $($modelEntries.Count)"
}
finally {
    $archive.Dispose()
}

$temporaryBase = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd(
    [IO.Path]::DirectorySeparatorChar
) + [IO.Path]::DirectorySeparatorChar
$verificationRoot = Join-Path ([IO.Path]::GetTempPath()) (
    "signflow-verify-" + [guid]::NewGuid().ToString("N")
)
New-Item -ItemType Directory -Path $verificationRoot | Out-Null

try {
    [IO.Compression.ZipFile]::ExtractToDirectory($resolvedArchive, $verificationRoot)
    $packageRoot = Join-Path $verificationRoot "SignFlow-AI"
    $quickStart = Join-Path $packageRoot "TEAM-QUICKSTART.md"
    if (-not (Test-Path -LiteralPath $quickStart -PathType Leaf)) {
        throw "TEAM-QUICKSTART.md is missing from the extracted package."
    }

    foreach ($script in Get-ChildItem -LiteralPath (Join-Path $packageRoot "scripts\team") -Filter "*.ps1" -File) {
        [void][ScriptBlock]::Create((Get-Content -LiteralPath $script.FullName -Raw))
    }

    & powershell.exe `
        -NoProfile `
        -ExecutionPolicy Bypass `
        -File (Join-Path $packageRoot "scripts\team\setup.ps1") `
        -CheckOnly
    if ($LASTEXITCODE -ne 0) {
        throw "The extracted setup preflight failed with exit code $LASTEXITCODE."
    }

    $manifest = Join-Path $packageRoot "PACKAGE-SHA256SUMS.txt"
    $checked = 0
    foreach ($line in Get-Content -LiteralPath $manifest) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }
        if ($line.Length -lt 67) {
            throw "Malformed checksum line: $line"
        }
        $expected = $line.Substring(0, 64)
        $relativePath = $line.Substring(66).Replace(
            [char]47,
            [IO.Path]::DirectorySeparatorChar
        )
        $filePath = Join-Path $packageRoot $relativePath
        if (-not (Test-Path -LiteralPath $filePath -PathType Leaf)) {
            throw "A manifest file is missing: $relativePath"
        }
        $actual = (Get-FileHash -LiteralPath $filePath -Algorithm SHA256).Hash
        if ($actual -ne $expected) {
            throw "Checksum mismatch: $relativePath"
        }
        $checked += 1
    }

    $archiveFile = Get-Item -LiteralPath $resolvedArchive
    if ($archiveFile.Length -ge 200MB) {
        throw "The archive exceeds the 200 MB handoff limit."
    }
    Write-Host "Verified checksums : $checked"
    Write-Host "Archive size       : $([math]::Round($archiveFile.Length / 1MB, 2)) MB"
    Write-Host "Archive SHA256     : $((Get-FileHash -LiteralPath $resolvedArchive -Algorithm SHA256).Hash)"
    Write-Host "Package verification passed." -ForegroundColor Green
}
finally {
    if (Test-Path -LiteralPath $verificationRoot) {
        $resolvedVerificationRoot = [IO.Path]::GetFullPath($verificationRoot)
        if (-not $resolvedVerificationRoot.StartsWith(
            $temporaryBase,
            [StringComparison]::OrdinalIgnoreCase
        )) {
            throw "Refusing to remove a verification path outside the temporary directory."
        }
        Remove-Item -LiteralPath $resolvedVerificationRoot -Recurse -Force
    }
}
