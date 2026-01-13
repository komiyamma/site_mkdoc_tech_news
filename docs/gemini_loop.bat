for /L %%i in (1,1,10) do (
  echo [%%i/10] gemini 実行中...
  gemini -y -p "gemini_command.md を実行してください。"
  echo [%%i/10] 終了コード=%errorlevel%
)