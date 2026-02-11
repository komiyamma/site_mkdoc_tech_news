
@echo off
REM バッチファイルのあるディレクトリに移動
cd /d %~dp0

REM fix_frontmatter_dates.bat を実行し、終了を待つ
call fix_frontmatter_dates.bat

REM 2秒待機
timeout /t 2 /nobreak >nul

gemini -m "gemini-3-flash" -p "@gemini_command.mdの内容を実行して。画面には進捗以外の情報が出す必要はありません。最後にこのリポジトリに対して、適切なコミットメッセージとともに全てコミット＆プッシュしてください。" -y


