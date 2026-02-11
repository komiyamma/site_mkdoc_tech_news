for /L %%i in (1,1,2) do (
  echo [%%i/2] gemini 実行中...
  gemini -m "gemini-3-flash" -y -p "gemini_command.md を実行してください。"
  echo [%%i/2] 終了コード=%errorlevel%
)