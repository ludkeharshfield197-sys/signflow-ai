[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TextBase64,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [string]$VoiceDisplayName = "Microsoft Kangkang",
    [double]$SpeakingRate = 0.96,
    [double]$AudioPitch = 1.0,
    [double]$AudioVolume = 1.0
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.SpeechSynthesis.SpeechSynthesizer, Windows.Media.SpeechSynthesis, ContentType = WindowsRuntime]

function Await-WinRtOperation {
    param(
        [Parameter(Mandatory = $true)]
        $Operation,

        [Parameter(Mandatory = $true)]
        [Type]$ResultType
    )

    $asTaskMethod = [System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object {
            $_.Name -eq "AsTask" -and
            $_.IsGenericMethodDefinition -and
            $_.GetParameters().Count -eq 1 -and
            $_.GetParameters()[0].ParameterType.Name -eq "IAsyncOperation``1"
        } |
        Select-Object -First 1

    if (-not $asTaskMethod) {
        throw "Could not locate the WinRT AsTask adapter."
    }

    $task = $asTaskMethod.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    $task.Wait()
    return $task.Result
}

if ($SpeakingRate -lt 0.5 -or $SpeakingRate -gt 2.0) {
    throw "SpeakingRate must be between 0.5 and 2.0 for this build helper."
}
if ($AudioPitch -lt 0.5 -or $AudioPitch -gt 2.0) {
    throw "AudioPitch must be between 0.5 and 2.0."
}
if ($AudioVolume -lt 0.0 -or $AudioVolume -gt 1.0) {
    throw "AudioVolume must be between 0.0 and 1.0."
}

$text = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($TextBase64))
if ([string]::IsNullOrWhiteSpace($text)) {
    throw "Speech text is empty."
}

$voices = [Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices
$voice = $voices |
    Where-Object { $_.DisplayName -eq $VoiceDisplayName -and $_.Language -eq "zh-CN" } |
    Select-Object -First 1
if (-not $voice) {
    $available = $voices |
        Where-Object { $_.Language -eq "zh-CN" } |
        ForEach-Object { $_.DisplayName }
    throw "Voice '$VoiceDisplayName' is unavailable. Chinese voices: $($available -join ', ')"
}

$resolvedOutput = [IO.Path]::GetFullPath($OutputPath)
$outputDirectory = [IO.Path]::GetDirectoryName($resolvedOutput)
if (-not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
    New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
}

$synthesizer = New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer
$speechStream = $null
$readStream = $null
$fileStream = $null
try {
    $synthesizer.Voice = $voice
    $synthesizer.Options.SpeakingRate = $SpeakingRate
    $synthesizer.Options.AudioPitch = $AudioPitch
    $synthesizer.Options.AudioVolume = $AudioVolume

    $operation = $synthesizer.SynthesizeTextToStreamAsync($text)
    $speechStream = Await-WinRtOperation $operation ([Windows.Media.SpeechSynthesis.SpeechSynthesisStream])
    $readStream = [IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($speechStream)
    $fileStream = [IO.File]::Create($resolvedOutput)
    $readStream.CopyTo($fileStream)
}
finally {
    if ($fileStream) { $fileStream.Dispose() }
    if ($readStream) { $readStream.Dispose() }
    if ($speechStream) { $speechStream.Dispose() }
    if ($synthesizer) { $synthesizer.Dispose() }
}

if (-not (Test-Path -LiteralPath $resolvedOutput -PathType Leaf)) {
    throw "Speech output was not created: $resolvedOutput"
}
