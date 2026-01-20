for /L %%i in (1,1,3) do (
  echo [%%i/3] gemini 実行中...
  gemini -y -p "gemini_command.md を実行してください。"
  echo [%%i/3] 終了コード=%errorlevel%
)