# Instala o VozLocal em %LOCALAPPDATA%\VozLocal (venv próprio + cópia do código).
# Uso: powershell -ExecutionPolicy Bypass -File install.ps1 [-NoAutostart] [-NoLaunch]
param([switch]$NoAutostart, [switch]$NoLaunch)
$ErrorActionPreference = "Stop"

$Root   = Join-Path $env:LOCALAPPDATA "VozLocal"
$AppDir = Join-Path $Root "app"
$Venv   = Join-Path $Root "venv"
$Py     = Join-Path $Venv "Scripts\python.exe"
$PyW    = Join-Path $Venv "Scripts\pythonw.exe"

Write-Host "==> Encerrando instância anterior (se houver)"
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
  Where-Object { $_.CommandLine -like "*VozLocal.pyw*" } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

New-Item -ItemType Directory -Force -Path $AppDir | Out-Null

if (-not (Test-Path $Py)) {
  Write-Host "==> Criando ambiente Python"
  & py -3.11 -m venv $Venv
  if ($LASTEXITCODE -ne 0) { & py -3 -m venv $Venv }
}

Write-Host "==> Instalando dependências (inclui CUDA/cuDNN via pip; pode demorar na 1a vez)"
& $Py -m pip install --upgrade pip --quiet
& $Py -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Falha no pip install" }

Write-Host "==> Copiando aplicativo"
Remove-Item -Recurse -Force (Join-Path $AppDir "vozlocal") -ErrorAction SilentlyContinue
Copy-Item -Recurse -Force (Join-Path $PSScriptRoot "vozlocal") $AppDir
Copy-Item -Force (Join-Path $PSScriptRoot "VozLocal.pyw") $AppDir
Get-ChildItem -Recurse -Directory -Filter "__pycache__" $AppDir | Remove-Item -Recurse -Force

Write-Host "==> Baixando e testando o modelo de transcrição (1a vez: ~1,6 GB)"
& $Py -c "import sys; sys.path.insert(0, r'$AppDir'); from vozlocal import config; from vozlocal.transcriber import Transcriber; t=Transcriber(config.load()); t.load(); print('OK:', t.device_desc)"
if ($LASTEXITCODE -ne 0) { throw "Falha ao carregar o modelo" }

$Script = Join-Path $AppDir "VozLocal.pyw"
$Cmd = "`"$PyW`" `"$Script`""

Write-Host "==> Criando atalho no Menu Iniciar"
$Lnk = Join-Path ([Environment]::GetFolderPath("Programs")) "VozLocal.lnk"
$Shell = New-Object -ComObject WScript.Shell
$S = $Shell.CreateShortcut($Lnk)
$S.TargetPath = $PyW
$S.Arguments = "`"$Script`""
$S.WorkingDirectory = $AppDir
$S.Description = "Ditado por voz local"
$S.Save()

if (-not $NoAutostart) {
  Write-Host "==> Ativando início automático com o Windows"
  Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "VozLocal" -Value $Cmd
}

if (-not $NoLaunch) {
  Write-Host "==> Iniciando VozLocal"
  Start-Process -FilePath $PyW -ArgumentList "`"$Script`"" -WorkingDirectory $AppDir
}

Write-Host ""
Write-Host "Pronto. Atalho padrão: Ctrl+Alt+Espaço (inicia/para). Ctrl+Alt+Backspace descarta."
Write-Host "Configuração: $env:APPDATA\VozLocal\config.json"
