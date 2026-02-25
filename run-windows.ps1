[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArgs
)

$ErrorActionPreference = "Stop"

function Fail {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

function Show-Banner {
    $line = "=" * 72
    Write-Host $line -ForegroundColor Cyan
    Write-Host "TTG AI QUANT TOOLS" -ForegroundColor Cyan
    Write-Host "LEARN FASTER. TRADE SMARTER. PROFIT SOONER." -ForegroundColor Green
    Write-Host "TrueTradingGroup.com" -ForegroundColor Cyan
    Write-Host "Provided by TTG AI LLC | Tested and used by True Trading Group" -ForegroundColor DarkGray
    Write-Host $line -ForegroundColor Cyan
    Write-Host ""
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Show-Banner

if (-not (Test-Path ".\.env")) {
    Fail "Missing .env. Copy .env.example to .env and set your values first."
}

if (-not (Test-Path ".\requirements.txt")) {
    Fail "Missing requirements.txt."
}

if (-not (Test-Path ".\.venv")) {
    Write-Host "Creating virtual environment..."
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -3 -m venv .venv
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        python -m venv .venv
    } else {
        Fail "Python 3 is not installed or not on PATH."
    }
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

$activateScript = ".\.venv\Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Fail "Could not find venv activation script at $activateScript"
}

. $activateScript

Write-Host "Loading env vars from .env..."
$envLines = Get-Content ".\.env"
foreach ($lineRaw in $envLines) {
    $line = $lineRaw.Trim()
    if (-not $line -or $line.StartsWith("#")) {
        continue
    }

    if ($line.StartsWith("export ")) {
        $line = $line.Substring(7).Trim()
    }

    $separatorIndex = $line.IndexOf("=")
    if ($separatorIndex -lt 1) {
        continue
    }

    $key = $line.Substring(0, $separatorIndex).Trim()
    $value = $line.Substring($separatorIndex + 1).Trim()

    if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
        $value = $value.Substring(1, $value.Length - 2)
    }

    Set-Item -Path "Env:$key" -Value $value
}

python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Launching TTG CLI..."
python ".\ttg-cli.py" @CliArgs
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
