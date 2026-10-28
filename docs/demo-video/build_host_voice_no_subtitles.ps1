[CmdletBinding()]
param(
    [string]$VoiceName = "Microsoft Kangkang",
    [switch]$KeepVoiceClips
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$DemoRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $DemoRoot "..\.."))
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$OriginalVideo = Join-Path $DemoRoot "SignFlow-AI-competition-full-demo-2026-08-25.mp4"
$TimelinePath = Join-Path $DemoRoot "SignFlow-AI-competition-host-narration-zh-CN.json"
$OneCoreHelper = Join-Path $DemoRoot "synthesize_onecore_speech.ps1"
$OutputVideo = Join-Path $DemoRoot "SignFlow-AI-competition-full-demo-2026-08-28-news-anchor-no-disclosure.mp4"
$ClipRoot = Join-Path $DemoRoot "narration-news-anchor-zh-CN"
$VideoDuration = "273.041625"

function Assert-LastExitCode {
    param([string]$Action)
    if ($LASTEXITCODE -ne 0) {
        throw "$Action failed with exit code $LASTEXITCODE."
    }
}

function Get-WavDurationSeconds {
    param([string]$Path)
    $stream = [IO.File]::OpenRead($Path)
    $reader = New-Object IO.BinaryReader($stream)
    try {
        $riff = -join $reader.ReadChars(4)
        [void]$reader.ReadInt32()
        $wave = -join $reader.ReadChars(4)
        if ($riff -ne "RIFF" -or $wave -ne "WAVE") {
            throw "Unsupported WAV file: $Path"
        }
        $byteRate = 0
        $dataSize = 0
        while ($stream.Position -lt $stream.Length) {
            $chunkId = -join $reader.ReadChars(4)
            if ($chunkId.Length -lt 4) {
                break
            }
            $chunkSize = $reader.ReadInt32()
            $chunkStart = $stream.Position
            if ($chunkId -eq "fmt ") {
                [void]$reader.ReadInt16()
                [void]$reader.ReadInt16()
                [void]$reader.ReadInt32()
                $byteRate = $reader.ReadInt32()
            }
            elseif ($chunkId -eq "data") {
                $dataSize = $chunkSize
            }
            $stream.Position = $chunkStart + $chunkSize + ($chunkSize % 2)
        }
        if ($byteRate -le 0 -or $dataSize -le 0) {
            throw "Could not read WAV duration: $Path"
        }
        return [double]$dataSize / [double]$byteRate
    }
    finally {
        $reader.Dispose()
        $stream.Dispose()
    }
}

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Project Python environment not found: $Python"
}
if (-not (Test-Path -LiteralPath $OriginalVideo -PathType Leaf)) {
    throw "Original no-subtitle video not found: $OriginalVideo"
}
if (-not (Test-Path -LiteralPath $TimelinePath -PathType Leaf)) {
    throw "Host narration timeline not found: $TimelinePath"
}
if (-not (Test-Path -LiteralPath $OneCoreHelper -PathType Leaf)) {
    throw "OneCore speech helper not found: $OneCoreHelper"
}

$Ffmpeg = (& $Python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())" | Select-Object -Last 1).Trim()
Assert-LastExitCode "FFmpeg discovery"
if (-not (Test-Path -LiteralPath $Ffmpeg -PathType Leaf)) {
    throw "FFmpeg binary was not found. Install imageio-ffmpeg in the project environment."
}

$timeline = Get-Content -LiteralPath $TimelinePath -Raw -Encoding UTF8 | ConvertFrom-Json
$segments = @($timeline.segments)
if ($segments.Count -eq 0) {
    throw "Host narration timeline has no segments."
}

New-Item -ItemType Directory -Path $ClipRoot -Force | Out-Null

$voiceClips = New-Object Collections.Generic.List[object]
foreach ($segment in $segments) {
    $clipPath = Join-Path $ClipRoot ("{0:000}.wav" -f [int]$segment.id)
    $availableDuration = [double]$segment.end - [double]$segment.start - 0.20
    $selectedRate = $null
    $duration = 0.0
    $encodedText = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes([string]$segment.text))

    # Start below normal speed for a measured news-anchor cadence. Increase only
    # in small increments when a segment must fit the corresponding screen scene.
    foreach ($rate in @(0.90, 0.94, 0.98, 1.02, 1.06, 1.10, 1.14)) {
        if (Test-Path -LiteralPath $clipPath) {
            Remove-Item -LiteralPath $clipPath -Force
        }
        & powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $OneCoreHelper `
            -TextBase64 $encodedText `
            -OutputPath $clipPath `
            -VoiceDisplayName $VoiceName `
            -SpeakingRate $rate `
            -AudioPitch 0.96 `
            -AudioVolume 1.0
        Assert-LastExitCode "OneCore voice segment $($segment.id)"
        $duration = Get-WavDurationSeconds $clipPath
        if ($duration -le $availableDuration) {
            $selectedRate = $rate
            break
        }
    }
    if ($null -eq $selectedRate) {
        throw "News-anchor narration segment $($segment.id) is too long for its timeline window."
    }

    Write-Host (
        "News segment {0:00}: {1:N2}s / {2:N2}s, speaking rate {3:N2}" -f
        [int]$segment.id, $duration, $availableDuration, $selectedRate
    )
    $voiceClips.Add([pscustomobject]@{
        Path = $clipPath
        DelayMilliseconds = [math]::Round([double]$segment.start * 1000)
    })
}

$arguments = New-Object Collections.Generic.List[string]
$arguments.Add("-y")
$arguments.Add("-hide_banner")
$arguments.Add("-i")
$arguments.Add($OriginalVideo)
foreach ($clip in $voiceClips) {
    $arguments.Add("-i")
    $arguments.Add([string]$clip.Path)
}

$filterParts = New-Object Collections.Generic.List[string]
$audioLabels = New-Object Collections.Generic.List[string]
for ($index = 0; $index -lt $voiceClips.Count; $index += 1) {
    $inputIndex = $index + 1
    $label = "voice$index"
    $delay = [int]$voiceClips[$index].DelayMilliseconds
    $filterParts.Add("[$inputIndex`:a]adelay=$delay|$delay[$label]")
    $audioLabels.Add("[$label]")
}

# Broadcast-style post-processing: remove rumble and harsh top end, add body and
# speech presence, control dynamics, then normalize for consistent playback.
$filterParts.Add(
    "$($audioLabels -join '')amix=inputs=$($voiceClips.Count):normalize=0,aresample=48000," +
    "highpass=f=80,lowpass=f=12000," +
    "equalizer=f=180:t=q:w=1.2:g=1.4," +
    "equalizer=f=2900:t=q:w=1.0:g=2.6," +
    "acompressor=threshold=0.125:ratio=3.5:attack=18:release=220:makeup=1.5," +
    "alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=7," +
    "apad=whole_dur=$VideoDuration[aout]"
)

$arguments.Add("-filter_complex")
$arguments.Add($filterParts -join ";")
$arguments.Add("-map")
$arguments.Add("0:v:0")
$arguments.Add("-map")
$arguments.Add("[aout]")
$arguments.Add("-c:v")
$arguments.Add("copy")
$arguments.Add("-c:a")
$arguments.Add("aac")
$arguments.Add("-b:a")
$arguments.Add("192k")
$arguments.Add("-ar")
$arguments.Add("48000")
$arguments.Add("-t")
$arguments.Add($VideoDuration)
$arguments.Add("-movflags")
$arguments.Add("+faststart")
$arguments.Add("-metadata:s:a:0")
$arguments.Add("language=zho")
$arguments.Add("-metadata")
$arguments.Add("title=SignFlow AI news-anchor demonstration")
$arguments.Add("-metadata")
$arguments.Add("comment=Formal Mandarin news-anchor narration; no subtitles")
$arguments.Add($OutputVideo)

Write-Host "Rendering no-subtitle news-anchor MP4..." -ForegroundColor Cyan
& $Ffmpeg @arguments
Assert-LastExitCode "Host-voice video render"

if (-not (Test-Path -LiteralPath $OutputVideo -PathType Leaf)) {
    throw "Host-voice video output was not created."
}
$outputFile = Get-Item -LiteralPath $OutputVideo
if ($outputFile.Length -lt 1MB) {
    throw "Host-voice video output is unexpectedly small."
}

if (-not $KeepVoiceClips) {
    foreach ($clip in $voiceClips) {
        if (Test-Path -LiteralPath $clip.Path) {
            Remove-Item -LiteralPath $clip.Path -Force
        }
    }
}

Write-Host "Output : $OutputVideo" -ForegroundColor Green
Write-Host "Voice  : $VoiceName (formal Mandarin news-anchor processing)"
Write-Host "Visual : original no-subtitle video stream copied without re-encoding"
Write-Host "Size   : $([math]::Round($outputFile.Length / 1MB, 2)) MB"
