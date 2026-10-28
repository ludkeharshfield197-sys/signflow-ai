[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
Set-StrictMode -Version Latest

$targets = @(
    [pscustomobject]@{ Name = "Backend readiness"; Url = "http://127.0.0.1:8001/health/ready" },
    [pscustomobject]@{ Name = "Desktop Web"; Url = "http://127.0.0.1:8080/" },
    [pscustomobject]@{ Name = "Mobile H5"; Url = "http://127.0.0.1:5173/" }
)

$failures = 0
foreach ($target in $targets) {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $target.Url -TimeoutSec 8
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
            Write-Host "[OK]   $($target.Name) - HTTP $($response.StatusCode) - $($target.Url)" -ForegroundColor Green
        }
        else {
            $failures += 1
            Write-Host "[FAIL] $($target.Name) - HTTP $($response.StatusCode) - $($target.Url)" -ForegroundColor Red
        }
    }
    catch {
        $failures += 1
        Write-Host "[FAIL] $($target.Name) - $($_.Exception.Message)" -ForegroundColor Red
    }
}

if ($failures -gt 0) {
    Write-Host "`n$failures health check(s) failed. Review .team-runtime logs or rerun start-windows.cmd." -ForegroundColor Red
    exit 1
}

Write-Host "`nAll SignFlow AI endpoints are reachable." -ForegroundColor Green

