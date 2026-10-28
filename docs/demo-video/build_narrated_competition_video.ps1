[CmdletBinding()]
param(
    [string]$VoiceName = "Microsoft Huihui Desktop",
    [switch]$KeepVoiceClips
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$DemoRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $DemoRoot "..\.."))
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$OriginalVideo = Join-Path $DemoRoot "SignFlow-AI-competition-full-demo-2026-08-25.mp4"
$TimelinePath = Join-Path $DemoRoot "SignFlow-AI-competition-narration-zh-CN.json"
$SrtPath = Join-Path $DemoRoot "SignFlow-AI-competition-full-demo-2026-08-27.zh-CN.srt"
$VttPath = Join-Path $DemoRoot "SignFlow-AI-competition-full-demo-2026-08-27.zh-CN.vtt"
$OutputVideo = Join-Path $DemoRoot "SignFlow-AI-competition-full-demo-2026-08-27-narrated-subtitled.mp4"
$ClipRoot = Join-Path $DemoRoot "narration-zh-CN"

function Assert-LastExitCode {
    param([string]$Action)
    if ($LASTEXITCODE -ne 0) {
        throw "$Action failed with exit code $LASTEXITCODE."
    }
}

function Format-SubtitleTime {
    param([double]$Seconds, [string]$Separator)
    $milliseconds = [math]::Round($Seconds * 1000)
    $hours = [math]::Floor($milliseconds / 3600000)
    $milliseconds -= $hours * 3600000
    $minutes = [math]::Floor($milliseconds / 60000)
    $milliseconds -= $minutes * 60000
    $wholeSeconds = [math]::Floor($milliseconds / 1000)
    $milliseconds -= $wholeSeconds * 1000
    return "{0:00}:{1:00}:{2:00}{3}{4:000}" -f $hours, $minutes, $wholeSeconds, $Separator, $milliseconds
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
    throw "Original competition video not found: $OriginalVideo"
}
if (-not (Test-Path -LiteralPath $TimelinePath -PathType Leaf)) {
    throw "Narration timeline not found: $TimelinePath"
}

$Ffmpeg = (& $Python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())" | Select-Object -Last 1).Trim()
Assert-LastExitCode "FFmpeg discovery"
if (-not (Test-Path -LiteralPath $Ffmpeg -PathType Leaf)) {
    throw "FFmpeg binary was not found. Install imageio-ffmpeg in the project environment."
}

$timeline = Get-Content -LiteralPath $TimelinePath -Raw -Encoding UTF8 | ConvertFrom-Json
$segments = @($timeline.segments)
if ($segments.Count -eq 0) {
    throw "Narration timeline has no segments."
}

$srtLines = New-Object Collections.Generic.List[string]
$vttLines = New-Object Collections.Generic.List[string]
$vttLines.Add("WEBVTT")
$vttLines.Add("")
foreach ($segment in $segments) {
    $srtLines.Add([string]$segment.id)
    $srtLines.Add(
        "$(Format-SubtitleTime ([double]$segment.start) ',') --> $(Format-SubtitleTime ([double]$segment.end) ',')"
    )
    $srtLines.Add([string]$segment.subtitle)
    $srtLines.Add("")

    $vttLines.Add(
        "$(Format-SubtitleTime ([double]$segment.start) '.') --> $(Format-SubtitleTime ([double]$segment.end) '.')"
    )
    $vttLines.Add([string]$segment.subtitle)
    $vttLines.Add("")
}
$srtLines | Set-Content -LiteralPath $SrtPath -Encoding UTF8
$vttLines | Set-Content -LiteralPath $VttPath -Encoding UTF8

Add-Type -AssemblyName System.Speech
$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
$availableVoice = $synthesizer.GetInstalledVoices() |
    Where-Object { $_.VoiceInfo.Name -eq $VoiceName } |
    Select-Object -First 1
if (-not $availableVoice) {
    $voices = $synthesizer.GetInstalledVoices() |
        ForEach-Object { $_.VoiceInfo.Name }
    throw "Voice '$VoiceName' is unavailable. Installed voices: $($voices -join ', ')"
}
$synthesizer.SelectVoice($VoiceName)
$synthesizer.Volume = 100
New-Item -ItemType Directory -Path $ClipRoot -Force | Out-Null

$voiceClips = New-Object Collections.Generic.List[object]
try {
    foreach ($segment in $segments) {
        $clipPath = Join-Path $ClipRoot ("{0:000}.wav" -f [int]$segment.id)
        $availableDuration = [double]$segment.end - [double]$segment.start - 0.12
        $selectedRate = $null
        $duration = 0.0
        foreach ($rate in @(1, 2, 3, 4, 5)) {
            if (Test-Path -LiteralPath $clipPath) {
                Remove-Item -LiteralPath $clipPath -Force
            }
            $synthesizer.Rate = $rate
            $synthesizer.SetOutputToWaveFile($clipPath)
            $synthesizer.Speak([string]$segment.text)
            $synthesizer.SetOutputToNull()
            $duration = Get-WavDurationSeconds $clipPath
            if ($duration -le $availableDuration) {
                $selectedRate = $rate
                break
            }
        }
        if ($null -eq $selectedRate) {
            throw "Narration segment $($segment.id) is too long for its timeline window."
        }
        Write-Host (
            "Voice segment {0:00}: {1:N2}s / {2:N2}s, rate {3}" -f
            [int]$segment.id, $duration, $availableDuration, $selectedRate
        )
        $voiceClips.Add([pscustomobject]@{
            Path = $clipPath
            DelayMilliseconds = [math]::Round([double]$segment.start * 1000)
        })
    }
}
finally {
    $synthesizer.Dispose()
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
$filterParts.Add(
    "$($audioLabels -join '')amix=inputs=$($voiceClips.Count):normalize=0," +
    "alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
)
$escapedSrtPath = $SrtPath.Replace("\", "/").Replace(":", "\:").Replace("'", "\'")
$subtitleStyle = "FontName=Microsoft YaHei,FontSize=22,PrimaryColour=&H00FFFFFF," +
    "BackColour=&H90000000,OutlineColour=&H70000000,BorderStyle=3,Outline=1," +
    "Shadow=0,Alignment=2,MarginV=32"
$filterParts.Add(
    "[0:v]subtitles=filename='$escapedSrtPath':force_style='$subtitleStyle'[vout]"
)

$arguments.Add("-filter_complex")
$arguments.Add($filterParts -join ";")
$arguments.Add("-map")
$arguments.Add("[vout]")
$arguments.Add("-map")
$arguments.Add("[aout]")
$arguments.Add("-c:v")
$arguments.Add("libx264")
$arguments.Add("-preset")
$arguments.Add("medium")
$arguments.Add("-crf")
$arguments.Add("20")
$arguments.Add("-pix_fmt")
$arguments.Add("yuv420p")
$arguments.Add("-r")
$arguments.Add("24")
$arguments.Add("-c:a")
$arguments.Add("aac")
$arguments.Add("-b:a")
$arguments.Add("192k")
$arguments.Add("-ar")
$arguments.Add("48000")
$arguments.Add("-t")
$arguments.Add("273.041625")
$arguments.Add("-movflags")
$arguments.Add("+faststart")
$arguments.Add("-metadata:s:a:0")
$arguments.Add("language=zho")
$arguments.Add("-metadata")
$arguments.Add("comment=AI-generated Chinese voiceover with burned-in subtitles")
$arguments.Add($OutputVideo)

Write-Host "Rendering narrated and subtitled MP4..." -ForegroundColor Cyan
& $Ffmpeg @arguments
Assert-LastExitCode "Narrated video render"

if (-not (Test-Path -LiteralPath $OutputVideo -PathType Leaf)) {
    throw "Narrated video output was not created."
}
$outputFile = Get-Item -LiteralPath $OutputVideo
if ($outputFile.Length -lt 1MB) {
    throw "Narrated video output is unexpectedly small."
}

if (-not $KeepVoiceClips) {
    foreach ($clip in $voiceClips) {
        if (Test-Path -LiteralPath $clip.Path) {
            Remove-Item -LiteralPath $clip.Path -Force
        }
    }
}

Write-Host "Output : $OutputVideo" -ForegroundColor Green
Write-Host "SRT    : $SrtPath"
Write-Host "WebVTT : $VttPath"
Write-Host "Voice  : $VoiceName (synthetic speech)"
Write-Host "Size   : $([math]::Round($outputFile.Length / 1MB, 2)) MB"

