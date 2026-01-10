# https://tech-news.komiyamma.net

[![GitHub release](https://img.shields.io/github/v/release/komiyamma/site_mkdoc_tech_news)](https://github.com/komiyamma/site_mkdoc_tech_news/releases)

Grokが出力したニュース記事を効率的に管理・公開するために構築された、[MkDocs](https://www.mkdocs.org/) ベースのウェブサイトです。
Cloudflare Pages と Functions を活用し、コンテンツの作成からデプロイまでを自動化する実験的な試みを行っています。

## ■ 主な特徴

- **MkDocsベース**: シンプルな Markdown で記事を管理できます。
- **カスタムプラグイン**:
  - ファイル名からページタイトルを自動生成。
  - `.memo` ファイルから `meta description` を自動設定。
  - これらにより、コンテンツ作成の手間を大幅に削減します。
- **自動デプロイ**: `main` ブランチにプッシュするだけで、Cloudflare Pages が自動でビルドとデプロイを行います。

## ■ セットアップと使い方

基本的なセットアップとコンテンツ作成の詳しい手順については、以下のマニュアルを参照してください。

- **[MANUAL.md](MANUAL.md)**

簡単なセットアップコマンドは以下の通りです。

```bash
pip install -r requirements.txt
pip install -e .
```

