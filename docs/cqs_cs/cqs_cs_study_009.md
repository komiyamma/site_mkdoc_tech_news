# 第9章：CQSとエラー設計①（失敗の種類を分ける）😵‍💫🧠✨

この章のテーマはズバリ👇
**「これは“仕様どおりの失敗”なの？ それとも“事故（障害）”なの？」を分けられるようになること**です🚧💡
CQSは「Command と Query を混ぜない」だけじゃなくて、**失敗の扱いも混ぜない**と一気に読みやすくなります😊✨

---

## 学習ゴール🎯

章が終わったら、こんな状態になってます👇✨

* 失敗を **2種類（仕様の失敗 / 障害）** に分けて説明できる📚✨
* 「どこまでが仕様で、どこからが障害？」の境界が決められる🚧
* Command / Query それぞれで **“よくある失敗の型”** が作れる🧩
* 失敗が起きたときに **“どこで吸収して、どこで投げるか”** の感覚がつく🧠⚡

---

## まず結論：失敗はこの2つに分けよう📌✨

### ① 予測できる失敗（＝仕様どおりの失敗）📋✅

ユーザー入力や業務ルールで**起きてもおかしくない失敗**です😊
例👇

* 入力が空、長すぎる（バリデーション）🧾
* 対象が存在しない（NotFound）🔍
* ルール違反（例：未払いなのに発送しようとした）🧠
* 競合（同時更新、すでに完了済み、二重送信など）⚔️
* 権限がない（Forbidden）🔒

👉 ポイント：これは**アプリが“丁寧に返してあげるべき失敗”**です🎁✨

---

### ② 予期しない障害（＝事故）💥🚒

システムの外側・環境・バグなどで起きる、**本来起きてほしくない失敗**😇
例👇

* DBが落ちた、接続できない🗄️💥
* タイムアウト（外部APIが遅い）⏳
* ネットワーク断🌐💔
* NullReferenceException みたいなバグ🐛
* 設定ミス（接続文字列が違う等）⚙️💣

👉 ポイント：これは**例外（exception）として扱ってログ・監視に回す**のが基本です🧯📝

---

## “境界”の考え方：どこまでが仕様？どこからが障害？🚧🧭

初心者向けの固定ルールを置いちゃうのが一番ラクです😊✨
この章では、いったんこれで統一しましょう👇

### ✅ 仕様どおり（予測できる失敗）にするもの

* 入力が変なら失敗（Validation）🧾
* ビジネスルール違反（Domain Rule）📏
* ないものを指定（NotFound）🔎
* 競合・二重操作（Conflict）⚔️
* 権限・認証（Auth/Forbidden）🔒

### 🚒 障害（予期しない）にするもの

* I/O が失敗（DB/HTTP/ファイル/メールなど）📨💥
* タイムアウト、ネットワーク、環境問題⏳🌐
* 想定外の例外、バグ🐛💣

この“線引き”を決めるだけで、コードがスッキリします😍✨

---

## CQSに当てはめると、こうなるよ🧩✨

### Query（参照）🔍

* 仕様どおりの失敗：

  * 「見つからない」→ 仕様として扱う（例：null相当 / “見つからない”扱い）🫥
  * 「検索条件が変」→ Validation で返す🧾
* 障害：

  * DB接続失敗など → 事故なので例外側へ💥

👉 Query は **“データを読むだけ”** だから、仕様失敗も比較的シンプルになりがちです😊

---

### Command（変更）🔧

* 仕様どおりの失敗：

  * Validation / ルール違反 / NotFound / Conflict を返す📋🎁
* 障害：

  * DBが死んだ、外部APIが落ちた → 例外💥

👉 Command は **副作用がある**ので、失敗の種類を分けないと地獄になりやすいです😇🪦

---

## ToDo題材で“失敗の種類”を仕分けしてみよう📝✨

### 例：ToDoを追加する（CreateTodo）

* タイトル空 → 仕様どおり（Validation）🧾
* タイトル長すぎ → 仕様どおり（Validation）📏
* DB保存が失敗 → 障害（事故）💥🗄️

### 例：ToDoを完了にする（CompleteTodo）

* IDが存在しない → 仕様どおり（NotFound）🔎
* すでに完了済み → 仕様どおり（Conflict か “何もしない”）✅
* 更新時に同時更新で失敗 → 仕様どおり（Conflict）⚔️
* DBタイムアウト → 障害（事故）⏳💥

---

## ミニ実装：失敗の“種類だけ”を型にしてみる🧩🎁（第10章の前準備）

※この章は「分類」が主役なので、**Result型の完成形は次章**でやります😊
でも、分類用の型だけは先に持つと超ラクです✨

```csharp
public enum FailureKind
{
    Validation,
    NotFound,
    Conflict,
    Forbidden
}

public sealed record Failure(FailureKind Kind, string Message, string? Field = null);

// Commandの戻り値（超ミニ版）
public sealed record CommandOutcome(bool IsSuccess, IReadOnlyList<Failure> Failures)
{
    public static CommandOutcome Ok() => new(true, Array.Empty<Failure>());
    public static CommandOutcome Ng(params Failure[] failures) => new(false, failures);
}
```

* ✅ 仕様どおりの失敗は Failure に詰める🎁
* 🚒 障害は例外として投げる（Outcome には入れない）💥

この“交通整理”ができると、実務の読みやすさが一段上がります😊✨

---

## ミニ演習①：これは仕様？それとも障害？🧩📝（仕分けゲーム）

次を **「仕様どおり」or「障害」** に分けてみてね😊✨

1. タイトルが空
2. IDが存在しない
3. すでに完了済みをもう一回完了にした
4. DB接続文字列が間違ってた
5. 外部APIが 503 を返してきた
6. ネットワークが一瞬切れた
7. ユーザーが権限なしの操作をした
8. NullReferenceException が出た

### こたえ🎉

* 仕様どおり：1, 2, 3, 7 ✅
* 障害：4, 5, 6, 8 🚒💥

---

## ミニ演習②：境界を決める（“ここから先は障害”線引き）🚧🧠

あなたのToDoアプリで👇を決めてみてね✨

* “見つからない”は仕様（NotFound）？それとも例外？🔍
* “すでに完了済み”は Conflict？それとも何もしない（冪等）？✅
* DBが落ちたらどうする？（これは障害で確定だね）💥🗄️

この「アプリのルール」を固定すると、迷いが消えます😊🌈

---

## AIへの指示例（Copilot / Codex向け）🤖🪄

そのままコピペでOK系です✨

**① 失敗分類のたたき台を作らせる**

* 「ToDoの Create / Complete / Delete に対して、Validation/NotFound/Conflict/Forbidden の失敗パターンを列挙して。各パターンのメッセージ案も出して。」

**② Failure 型を使った戻り値設計を作らせる**

* 「CommandOutcome（成功/失敗＋Failures）を使って CreateTodo の疑似実装を作って。DB例外は Outcome に入れず例外として投げる形で。」

**③ ありがちな“混ぜ事故”を指摘させる**

* 「Queryでキャッシュ更新や最終アクセス時刻更新をしてしまう設計の問題点を、CQSの観点で列挙して。」

---

## よくある詰まりポイント🧱😵‍💫（先に潰す！）

* **「NotFoundって仕様？例外？」問題**
  → まずは仕様に寄せるのがラク（UIに“見つからない”って出せる）😊
* **「障害も Failure に入れたくなる」問題**
  → 障害は“運用で直す対象”なので、ログと監視に回す方が強い💥📝
* **「全部例外でいいじゃん？」問題**
  → 例外だらけだと、ユーザーに返すべき失敗まで“事故扱い”になって、扱いがぐちゃぐちゃになる😇🌀

---

## まとめチェックリスト✅✨（これが言えたら勝ち！）

* 失敗は **仕様どおり** と **障害** に分ける📌
* 仕様どおり：Validation / NotFound / Conflict / Forbidden など📋
* 障害：I/O失敗・タイムアウト・バグなど💥
* Command/Query で **失敗の扱いを混ぜない**🧩✨

---

## ちなみに：2026年の“今の前提”メモ（情報の根拠つき）🪄

* **C# 14 が最新で、.NET 10 上でサポート**されています📌 ([Microsoft Learn][1])
* **.NET 10 は 2025/11/11 リリースの LTS** として案内されています🧠✨ ([Microsoft][2])
* **LTS は3年サポート、STS は2年サポート**のポリシーです📚 ([Microsoft][3])

---

次の第10章で、この章で分けた「仕様どおりの失敗」を **例外じゃなくて Result で返す**型に整えていくよ🎁🧯✨
もし第9章の内容で、ToDo以外（注文・会員・決済など）で例を作りたい題材があれば、それに寄せた“失敗分類表”も作れるよ😊💖

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://dotnet.microsoft.com/ja-jp/platform/support/policy?utm_source=chatgpt.com "公式の .NET サポート ポリシー | .NET"
[3]: https://dotnet.microsoft.com/en-us/platform/support/policy?utm_source=chatgpt.com "The official .NET support policy"
