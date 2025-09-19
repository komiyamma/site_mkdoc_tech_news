param(
    [string]$Addr = '127.0.0.1:8000'
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$venvActivate = Join-Path $root '.venv\Scripts\Activate.ps1'
if (-not (Test-Path $venvActivate)) {
    Write-Error 'Virtual environment .venv not found. Run python -m venv .venv first.'
    exit 1
}

. $venvActivate

try {
    Write-Host "mkdocs serve --dev-addr $Addr"
    mkdocs serve --dev-addr $Addr
}
finally {
    if (Get-Command 'deactivate' -ErrorAction SilentlyContinue) {
        deactivate
    }
}
