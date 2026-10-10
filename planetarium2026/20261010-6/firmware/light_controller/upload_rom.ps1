param([Parameter(Mandatory=$true)][string]$Port)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$pioHome = Join-Path $env:USERPROFILE '.platformio'
$python = Join-Path $pioHome 'penv\Scripts\python.exe'
$esptool = Join-Path $pioHome 'packages\tool-esptoolpy\esptool.py'
$bootApp = Join-Path $pioHome 'packages\framework-arduinoespressif32\tools\partitions\boot_app0.bin'
$build = '.pio\build\seeed_xiao_esp32c3'
foreach ($file in @("$build\bootloader.bin", "$build\partitions.bin", "$build\firmware.bin")) {
    if (-not (Test-Path -LiteralPath $file)) { throw "先にPlatformIOでコンパイルしてください: $file" }
}
# Native ROM loader avoids the stub communication failure observed on COM7.
& $python $esptool --chip esp32c3 --port $Port --baud 115200 --no-stub write_flash --flash_mode dio --flash_freq 80m --flash_size 4MB 0x0 "$build\bootloader.bin" 0x8000 "$build\partitions.bin" 0xe000 $bootApp 0x10000 "$build\firmware.bin"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
