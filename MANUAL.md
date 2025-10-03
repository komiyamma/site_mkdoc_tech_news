# MANUAL

このサイトの技術的な仕様やコンテンツの作成方法についての詳細なマニュアルです。

## ■ サイトの概要

このサイトは、[MkDocs](https://www.mkdocs.org/) を利用して構築された静的サイトです。
Cloudflare Pages と Functions を利用して、自動でデプロイ・運用されるように設計されています。

主な特徴として、コンテンツ作成を効率化するための独自の `MkDocs` プラグインを導入しています。

## ■ ディレクトリ構成

- `docs/`
  - サイトのコンテンツ（Markdown ファイル）が格納されています。
  - 各サブディレクトリがサイトのセクションに対応します。
- `macros/`
  - `mkdocs-macros-plugin` で使用される Python スクリプトが格納されています。
- `overrides/`
  - MkDocs の Material テーマのテンプレートを上書きするためのファイルが格納されています。
- `plugins/`
  - このプロジェクト独自の MkDocs プラグインが格納されています。
- `mkdocs.yml`
  - MkDocs の設定ファイルです。サイトの構成やプラグインの設定が記述されています。
- `requirements.txt`
  - Python の依存パッケージリストです。
- `setup.py`
  - プロジェクト独自のプラグインをインストールするための設定ファイルです。

## ■ コンテンツ作成フロー

1. **記事ファイルの作成**:
   - `docs/` 以下に、適切なカテゴリのディレクトリを選択し、`.md` ファイルを作成します。
   - ファイル名は、そのまま URL の一部となり、ページのタイトルとしても自動的に使用されます（`title_from_filename` プラグインによる）。
   - **例**: `docs/2025-web-tech/my-new-article.md`

2. **概要（Description）の作成**:
   - `.md` ファイルと同じ階層に、同名の `.memo` ファイルを作成します。
   - この `.memo` ファイルに記述された内容が、ページの `meta description` として自動的に設定されます（`description_from_memo` プラグインによる）。
   - **例**: `docs/2025-web-tech/my-new-article.memo`

3. **コンテンツの記述**:
   - `.md` ファイルに Markdown 形式で記事の本文を記述します。

## ■ ローカルでの開発とプレビュー

1. **セットアップ**:
   - 必要な依存関係をインストールします。
     ```bash
     pip install -r requirements.txt
     pip install -e .
     ```

2. **開発サーバーの起動**:
   - 以下の PowerShell スクリプトを実行すると、仮想環境の有効化から MkDocs の開発サーバー起動までが自動で行われます。
     ```powershell
     .\mkdocs_serve.ps1
     ```
   - サーバーが起動したら、`http://127.0.0.1:8000` にアクセスしてサイトをプレビューできます。
   - ファイルを編集すると、自動的にリロードがかかります。

## ■ デプロイ

1. **変更のコミットとプッシュ**:
   - 作成・編集したコンテンツを `git` でコミットし、GitHub リポジトリにプッシュします。
     ```bash
     git add .
     git commit -m "feat: 新しい記事を追加"
     git push
     ```

2. **自動デプロイ**:
   - GitHub へのプッシュをトリガーとして、Cloudflare Pages が自動的にサイトのビルドとデプロイを実行します。
   - デプロイの状況は、Cloudflare のダッシュボードから確認できます。

## ■ カスタムプラグインについて

このプロジェクトでは、以下のカスタムプラグインを利用しています（`plugins/` ディレクトリ参照）。

- `title_from_filename`:
  - Markdown ファイルのファイル名（拡張子を除く）を、そのページのタイトルとして自動的に設定します。
- `description_from_memo`:
  - `.md` ファイルに対応する `.memo` ファイルの内容を、ページの `meta description` として設定します。
- `exclude_docs`:
  - `mkdocs.yml` の設定に基づき、特定のファイルを MkDocs のビルド対象から除外します。