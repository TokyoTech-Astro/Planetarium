$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here
$python = 'C:\Program Files\Python39\python.exe'
if (-not (Test-Path $python)) { $python = 'python' }
$shared = 'C:\Users\kazu2\Documents\Codex\2026-07-11\new-chat\work\pydeps39'
$env:PYTHONPATH = "$here\vendor;$shared"
if (-not (Test-Path "$here\vendor\pygame")) { & $python -m pip install pygame==2.6.1 --target "$here\vendor" }
if (-not (Test-Path "$here\vendor\appdirs.py")) { & $python -m pip install appdirs==1.4.4 --target "$here\vendor" }
& $python -m PyInstaller --noconfirm --onefile --windowed --name PlaneControl --paths "$here\vendor" --paths $shared --exclude-module pkg_resources --collect-all pygame --collect-all audiostretchy app.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$versionedExe = Join-Path $here 'PlaneControl_v20261010-6.exe'
Copy-Item -LiteralPath (Join-Path $here 'dist\PlaneControl.exe') -Destination $versionedExe -Force
$operatorDir = Join-Path (Split-Path -Parent $here) '操作者用'
if (Test-Path -LiteralPath $operatorDir) {
    Copy-Item -LiteralPath $versionedExe -Destination (Join-Path $operatorDir ('PlaneControl_v20261010-6.exe')) -Force
}
Write-Host "Created: $versionedExe"
