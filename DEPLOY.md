# DEPLOY (最低限の手順)

このワーキングスペースで記事を更新した際に行う最低限の手順です。

1. ローカル表示確認が必要な場合は、以下のスクリプトだけ実行します（仮想環境の有効化まで自動で行われます）。
   ```powershell
   PS> .\mkdocs_serve.ps1
   ```

2. 変更内容を確認したら、コミットとプッシュを行います（`git add` / `git commit` / `git push`。GUI ツールでも可）。

3. GitHub へ push すると Cloudflare Pages が自動的にビルド・デプロイを行います。結果は Cloudflare Pages のダッシュボードで確認してください。

4. `mkdocs serve` を終了した際には自動的に仮想環境も解除されますが、必要に応じて `deactivate` を実行しても構いません。
