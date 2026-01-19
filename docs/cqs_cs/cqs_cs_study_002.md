# 第2章：準備（Windows＋Visual Studio）とミニプロジェクト作成🪟🛠️

この章は「あとでCQSを気持ちよく分離できる土台づくり」だよ〜😊✨
先に“作業場”を整えておくと、後半で**ぐちゃぐちゃになりにくい**の！🧹💕

---

## 0) この章のゴール🎯✨

章末でこうなってたら勝ち〜！🏆😆

* ✅ Console版（または Minimal API版）のプロジェクトが作れて、実行できる
* ✅ テストプロジェクトが一緒に動く（1テストでもOK）🧪
* ✅ Git管理（GitHubに上げなくてもローカルでOK）ができる
* ✅ Copilot/Codexを「事故りにくい設定」にできた🤖🧷
* ✅ フォルダ構成が整ってて、後からCQSで分けやすい🗂️✨

---

## 1) 2026時点の“前提バージョン感”だけ確認👀✨

* **C#の最新は C# 14**、**.NET 10 上でサポート**されてるよ🧡 ([Microsoft Learn][1])
* **Visual Studio 2026** には **.NET 10** が入ってくる前提でOK（公式のリリースノートにも .NET 10 前提の話が出てくるよ）🛠️ ([Microsoft Learn][2])
* もし **Visual Studio 2022** を使う場合でも、**17.14 は長くサポートされる**って明記があるので安心寄り👌 ([Microsoft Learn][3])

---

## 2) まずは「Console」か「Minimal API」どっちで作る？🎮🌐

迷ったらこれでOK〜😊

* **Console版**：最速で始められる／CQSの“分ける感覚”に集中しやすい🎮✨
* **Minimal API版**：実務っぽい／APIのCQS分離にそのまま繋がる🌐✨

この教材は**両対応**にするね！💪😆（章の手順も両方書くよ）

---

## 3) Visual Studioで“ミニプロジェクト”作成（いちばん楽コース）🛠️😊

### 3-1) 新規ソリューションを作る🗂️

1. Visual Studio → **Create a new project**
2. **Console App**（または **ASP.NET Core Web API / Minimal API**）を選ぶ
3. 名前は例：`CqsTodo`
4. フレームワークは **.NET 10** を選べるならそれ（なければ入ってるSDKに合わせてOK）✨ ([Microsoft][4])

---

## 4) VS Code派向け：dotnet CLIで一気に作る（超速）⚡🧑‍💻

PowerShell（Windows TerminalでもOK）で、作業用フォルダへ移動してから👇

```powershell
mkdir CqsTodo
cd CqsTodo

dotnet new sln -n CqsTodo

mkdir src
mkdir tests
```

### 4-1) Console版を作る🎮

```powershell
dotnet new console -n CqsTodo.App -o src/CqsTodo.App
dotnet sln add src/CqsTodo.App/CqsTodo.App.csproj
```

### 4-2) Minimal API版を作る🌐

```powershell
dotnet new web -n CqsTodo.Api -o src/CqsTodo.Api
dotnet sln add src/CqsTodo.Api/CqsTodo.Api.csproj
```

> `web` テンプレは最小構成で作りやすくて、Minimal APIの入口にちょうど良いよ😊✨

---

## 5) テストプロジェクトを“最初から”作る🧪✨（ここ大事〜！）

後で作ると「参照追加し忘れ」「配置迷子」が起きがち😇💥
最初から作っちゃお！

```powershell
dotnet new xunit -n CqsTodo.Tests -o tests/CqsTodo.Tests
dotnet sln add tests/CqsTodo.Tests/CqsTodo.Tests.csproj
```

### 5-1) テストから本体を参照（Console版ならこれ）🔗

```powershell
dotnet add tests/CqsTodo.Tests/CqsTodo.Tests.csproj reference src/CqsTodo.App/CqsTodo.App.csproj
```

（Minimal API版なら `CqsTodo.Api` を参照してもOKだよ👌）

### 5-2) テスト実行して「緑」を見よう🟢😍

```powershell
dotnet test
```

---

## 6) “後でCQSに分けやすい”フォルダ構成にしておく🗂️✨

この時点では難しい設計はしないよ😊
でも、**置き場所だけ**先に作っておくと未来の自分が助かる〜！🛟💕

おすすめ（最小）👇

* `src/`

  * `CqsTodo.App`（または `CqsTodo.Api`）
  * `CqsTodo.Domain`（あとで作る：データやルール置き場）
  * `CqsTodo.Application`（あとで作る：Command/Query置き場）
* `tests/`

  * `CqsTodo.Tests`

> これ、あとで「依存の向き（Dependency Ruleの入口）」を事故らせないための“下ごしらえ”だよ🧭✨
> いきなり難しい話はしないけど、**“内側（Domain）ほど素朴で、外側（UI/DB）ほど都合が多い”**って感覚だけ持てばOK〜😊💕

---

## 7) Gitの準備（ローカルだけでもOK）🐙✨

```powershell
git init
dotnet new gitignore
```

**やっておくと嬉しい**🧡

* 変な変更が入ったらすぐ戻せる😌
* AIにコード生成させた時も差分が見える👀✨

---

## 8) AI拡張を“教材用に安全設定”する🤖🧷（Copilot/Codex）

### 8-1) Copilot：まずここだけは押さえる✅

GitHubの設定で、**公開コードに似すぎる提案をブロック**できるよ🧯✨
さらに、**プロンプトや提案の収集・保持を許可するか**も選べるよ🧷 ([GitHub Docs][5])

やり方（ざっくり）👇

* GitHub → Settings → Copilot

  * **Suggestions matching public code：Block**（まずはBlockがおすすめ）🧱
  * **Prompt & suggestion collection**：必要に応じてON/OFF（教材では“OFF寄り”が安心）🧷 ([GitHub Docs][6])

### 8-2) Codex：安全運用の考え方（超重要）🧷🧯

Codexは「コーディング**エージェント**」として、**サンドボックス**や**許可ルール**で安全に動かす思想が公式に書かれてるよ🔒✨ ([OpenAI Developers][7])

教材ルール（おすすめ）👇

* 🔑 **秘密情報（鍵・接続文字列・個人情報）は貼らない**
* 🧾 AIの提案は“採用前に自分の目でチェック”
* 🧨 「ファイル大量変更」や「依存追加」は、**差分を見てから**採用
* 🌐 ネットワークや外部アクセスが絡む操作は特に慎重に（必要な時だけ）

---

## 9) ここまでのミニ演習🧩✨（5分）

できたらスクショ撮りたくなるやつ📸😆

1. `dotnet --version` でSDKが出る
2. `dotnet test` が通る🟢
3. Consoleなら `dotnet run --project src/CqsTodo.App` が動く🎮
4. Minimal APIなら `dotnet run --project src/CqsTodo.Api` で起動してブラウザ表示できる🌐

---

## 10) AIに頼むときの“指示テンプレ”🤖📝（コピペOK）

### 10-1) 生成（小さく、安全に）

```text
C#/.NET 10 のプロジェクトです。
今回は「新規ファイルを1つだけ追加」して、xUnitの最小テストを1本作ってください。
既存ファイルの変更はしないでください。
追加後、どう実行するか（dotnet test）も書いてください。
```

### 10-2) レビュー（事故防止）

```text
次の差分をレビューして：
- CQS的に混ざりそうなところがない？
- 状態変更（副作用）が入りそうな箇所はどこ？
- テストしづらくなる匂いはある？
できれば改善案も1つだけください。
```

---

## 11) よくある詰まりポイント🧱😵‍💫（先回り！）

* 😭 `.NET 10` が選べない
  → SDKが入ってない可能性。公式の .NET 10 ダウンロード案内から入れ直すのが早いよ🛠️ ([Microsoft][4])
* 😭 `dotnet test` が失敗する
  → まずは「何もいじってないのに失敗」か確認！テンプレ更新や復元で直ることもあるよ🔧
* 😭 Copilotが“公開コードに一致してブロック”系になる
  → ブロック設定が効いてる証拠でもある（安全寄り）🧱✨ ([GitHub Docs][5])

---

## 次の章へ🎯✨（予告）

次は **「CommandとQueryの見分け方」**で、
“混ぜるとヤバい”を体で覚えるよ😇💥→😊✨

必要なら、あなたの好みで👇どっちメインに寄せて書くよ〜！

* 🎮 Consoleメイン（理解しやすさ最優先）
* 🌐 Minimal APIメイン（実務っぽさ最優先）

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes?utm_source=chatgpt.com "Visual Studio 2026 Release Notes"
[3]: https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-history?utm_source=chatgpt.com "Visual Studio 2022 Release History"
[4]: https://dotnet.microsoft.com/en-US/download/dotnet/10.0?utm_source=chatgpt.com "Download .NET 10.0 (Linux, macOS, and Windows) | .NET"
[5]: https://docs.github.com/copilot/configuring-github-copilot/configuring-github-copilot-in-your-environment?tool=visualstudio&utm_source=chatgpt.com "Configuring GitHub Copilot in your environment"
[6]: https://docs.github.com/copilot/how-tos/manage-your-account/managing-copilot-policies-as-an-individual-subscriber?utm_source=chatgpt.com "Managing GitHub Copilot policies as an individual subscriber"
[7]: https://developers.openai.com/codex/security/?utm_source=chatgpt.com "Security"
