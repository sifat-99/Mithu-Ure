$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $scriptDir '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Error 'Virtual environment Python not found at .\.venv\Scripts\python.exe'
    exit 1
}
Set-Location $scriptDir
& $python (Join-Path $scriptDir 'main.py') @args
