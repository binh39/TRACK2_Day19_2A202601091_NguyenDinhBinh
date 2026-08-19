param([switch]$SkipInstall)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if (-not (Test-Path '.venv\Scripts\python.exe')) { py -3.11 -m venv .venv }
$Py = Join-Path $Root '.venv\Scripts\python.exe'
$env:PATH = "$(Join-Path $Root '.venv\Scripts');$env:PATH"
if (-not $SkipInstall) {
    & $Py -m pip install --upgrade pip
    & $Py -m pip install -r requirements.txt
}
& $Py scripts\seed_corpus.py
& $Py scripts\verify_lite.py
& $Py -m pytest -q
Write-Host 'Windows setup complete.'
