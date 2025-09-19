# MkDocs再起動スクリプト
# 1. ポート6283に接続中のpython.exeのPIDを取得
# 2. 該当プロセスを強制終了
# 3. MkDocsサーバーを再起動

param(
    [int]$Port = 6283
)

$mkdocsPid = (
    Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty OwningProcess
)

if ($mkdocsPid) {
    Write-Host "Killing python.exe (PID: $mkdocsPid) on port $Port..."
    Stop-Process -Id $mkdocsPid -Force
    Start-Sleep -Seconds 1
}

Write-Host "Starting MkDocs server on port $Port..."
Start-Process -NoNewWindow python -ArgumentList "-m mkdocs serve -a 127.0.0.1:$Port"
