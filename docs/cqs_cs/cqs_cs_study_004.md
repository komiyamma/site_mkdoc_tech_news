# 第4章：アンチパターンを体験しよう（混ぜると何が起きる？）😇💥

この章は「CQSって良さそう…」を **「うわ、分けないと事故るわ…😇」** に変える回だよ〜！💡✨
（C# 14 / .NET 10 世代でサンプル書くね。C# 14 は Visual Studio 2026 や .NET 10 SDK で試せるよ🧡）([Microsoft Learn][1])

---

## 1) この章のゴール🎯✨

読み終わったら、これができるようになるよ😊

* ✅ **「Queryっぽいのに更新してる」** を嗅ぎ分けられる👃💥
* ✅ **「Commandなのに値を返しすぎ問題」** が気持ち悪く感じるようになる🤢📦
* ✅ デバッグで「副作用の追跡が地獄」になる理由が腹落ちする🪦🔍
* ✅ “分ける”の第一歩（分割の型）を手で直せる✂️🧠

---

## 2) まず結論：混ぜると何が起きるの？😇💥

混ぜると、だいたいこうなるよ👇

* 😱 **同じ Query を2回呼んだだけ** なのに結果が変わる（または状態が変わる）
* 😵‍💫 画面表示のために呼んだのに **DB更新・イベント発行・外部API** が走る
* 🐛 「どこで変わったの？」が追えず、**ブレークポイント地獄**
* 🧪 テストが書けない／書いても不安定（フレーク）になる
* 🔥 GET なのに更新して、監視やキャッシュで **勝手にデータが増えたり壊れたり**

今日はこれを **わざとやって** 体験するよ！😈🧪✨

---

## 3) アンチパターン①：Queryっぽいのに内部で更新してる👻🩸

### 🎬 シナリオ（よくある）

「詳細画面を表示するだけ」のつもりで `GetTodo()` を呼んだら…

* 👀 閲覧回数（ViewCount）を増やしてた
* 🕒 最終閲覧日時（LastViewedAt）を更新してた
* 💾 ついでに `SaveChanges()` までしてた

**表示しただけで更新される** ＝副作用トラップ👻

### 🚫 悪い例（わざと混ぜる）

```csharp
public sealed class TodoService
{
    private readonly TodoRepository _repo;

    public TodoService(TodoRepository repo) => _repo = repo;

    // ❌ Queryっぽい名前なのに、内部で更新して保存までしてる
    public Todo? GetTodo(int id)
    {
        var todo = _repo.FindById(id);
        if (todo is null) return null;

        // 👻 表示しただけのつもりなのに…
        todo.ViewCount++;
        todo.LastViewedAt = DateTimeOffset.UtcNow;

        _repo.Save(todo); // 💥DB更新（またはファイル書き込み等）
        return todo;
    }
}

public sealed class Todo
{
    public int Id { get; init; }
    public required string Title { get; set; }
    public bool IsDone { get; set; }

    // 表示の副産物（のつもり）
    public int ViewCount { get; set; }
    public DateTimeOffset? LastViewedAt { get; set; }
}
```

### 🧨 何が怖いの？

* 🔁 画面が同じデータを2回読む（描画都合でよくある）だけで **ViewCountが2増える**
* 🧪 テストで `GetTodo()` 呼んだだけなのに **状態が変わって** 期待が崩れる
* 🧵 監視やキャッシュが GET を叩くと、勝手に更新される（最悪の地雷）

---

## 4) アンチパターン②：Commandなのに値を返しまくる📦😵‍💫

### 🎬 シナリオ（ありがち）

「完了にする」＝Command のはずなのに…

* ✅ 完了にした `Todo` を返す
* ✅ ついでに全件一覧も返す
* ✅ ついでに検索条件に合わせた結果も返す

**“便利そう”に見えて、依存が絡まりはじめる** やつ😇💥

### 🚫 悪い例（返しすぎ）

```csharp
public sealed class TodoService
{
    private readonly TodoRepository _repo;
    public TodoService(TodoRepository repo) => _repo = repo;

    // ❌ Commandなのに「画面に必要そうなもの全部」を返しはじめる
    public IReadOnlyList<Todo> CompleteTodo(int id)
    {
        var todo = _repo.FindById(id) ?? throw new InvalidOperationException("Not found");
        todo.IsDone = true;

        _repo.Save(todo);

        // 💥 ここからQueryの仕事（一覧取得）も混ぜてる
        return _repo.GetAllSorted();
    }
}
```

### 🧨 何がモヤモヤ？

* 🧩 「このCommand、どの画面向け？」が混ざって、再利用が死ぬ⚰️
* 🔄 “返すために” 余計な読み取りが増える（性能も設計も汚れる）🐢💦
* 🧪 テストが「更新＋一覧の並び」まで巻き込まれて重くなる😵‍💫

---

## 5) アンチパターン③：副作用が“隠れてる”😇🪤

地味にヤバいやつランキング上位👇

* 🧊 キャッシュ更新（Queryのついでに…）
* 📝 ログ書き込み（これ自体はOKでも、**ビジネス判断が混ざる**と危険）
* 🎲 乱数・時刻（同じ入力でも結果が揺れてテスト困る）
* 📨 イベント発行（Queryから飛ばすと追跡が地獄）

ポイントはこれ👇
**「呼び出し側が“読むだけ”と思ってるのに、裏で世界が変わる」** と事故る💥

---

## 6) デバッグ地獄を“再現”しよう🪦🧯（体験パート）

### ✅ 体験1：ブレークポイントで「GETなのに保存してる」現場を見よう👀

1. `TodoRepository.Save()` にブレークポイント🧷
2. 画面表示（または `GetTodo()` を呼ぶ）
3. **「え、ここ通るの！？😇」** を味わう

### ✅ 体験2：「同じQueryを2回呼ぶ」だけで状態が変わる🌀

```csharp
var s = new TodoService(repo);

var a = s.GetTodo(1);
var b = s.GetTodo(1);

// 😇 何もしてないのに ViewCount が増えてる…
Console.WriteLine(a?.ViewCount);
Console.WriteLine(b?.ViewCount);
```

### ✅ 体験3：テストが不安定になる（超あるある）🧪💥

「読むだけで更新」だと、テストがこういうノリで壊れる👇

```csharp
[Fact]
public void GetTodo_ShouldNotChangeState()
{
    var repo = new TodoRepository();
    repo.Seed(new Todo { Id = 1, Title = "Milk" });

    var s = new TodoService(repo);

    var before = repo.FindById(1)!.ViewCount;
    _ = s.GetTodo(1);
    var after = repo.FindById(1)!.ViewCount;

    Assert.Equal(before, after); // 💥 落ちる（読むだけのつもりなのに）
}
```

---

## 7) じゃあどう直す？：分ける型（最小形）✂️✨

ここでは **いちばん初心者に優しい直し方** にするよ😊🧡

### ✅ 直し方の基本

* 🔍 Query：読むだけ（状態を変えない）
* 🔧 Command：変える（必要なら Result / ID を返す）

---

### ✅ 改善例：閲覧記録を Command に分離する👀➡️🔧

```csharp
public sealed class TodoQueries
{
    private readonly TodoRepository _repo;
    public TodoQueries(TodoRepository repo) => _repo = repo;

    // ✅ ただ読むだけ
    public Todo? GetTodo(int id) => _repo.FindById(id);
}

public sealed class TodoCommands
{
    private readonly TodoRepository _repo;
    public TodoCommands(TodoRepository repo) => _repo = repo;

    // ✅ 変えるのはこっちに寄せる
    public void RecordViewed(int id)
    {
        var todo = _repo.FindById(id);
        if (todo is null) return;

        todo.ViewCount++;
        todo.LastViewedAt = DateTimeOffset.UtcNow;
        _repo.Save(todo);
    }

    public void Complete(int id)
    {
        var todo = _repo.FindById(id) ?? throw new InvalidOperationException("Not found");
        todo.IsDone = true;
        _repo.Save(todo);
    }
}
```

### 🌟 これで何が嬉しい？

* 🧪 Queryのテストが激ラク（入力→出力だけ）
* 🔍 「更新はどこ？」が Commands に集まって追いやすい
* 😇 “読むだけ”で世界が変わらない＝精神安定剤💊✨

---

## 8) Minimal APIでも事故る例（GETで更新しちゃうやつ）🌐💥

### 🚫 ダメな例：GETで閲覧回数増やす

```csharp
app.MapGet("/todos/{id:int}", (int id, TodoService s) =>
{
    var todo = s.GetTodo(id); // 👻 中で更新してたら終わり
    return todo is null ? Results.NotFound() : Results.Ok(todo);
});
```

### ✅ 良い分け方：GETは読むだけ／閲覧はPOSTで別にする

```csharp
app.MapGet("/todos/{id:int}", (int id, TodoQueries q) =>
{
    var todo = q.GetTodo(id);
    return todo is null ? Results.NotFound() : Results.Ok(todo);
});

app.MapPost("/todos/{id:int}/viewed", (int id, TodoCommands c) =>
{
    c.RecordViewed(id);
    return Results.NoContent();
});
```

GET は“安全”という期待があるから、混ぜると被害が広がりやすいよ😇💥

---

## 9) ミニ演習🧩🎮（手を動かすやつ！）

### 演習A：副作用スキャン👀🔍

次の問いに答えてね👇

* 「このメソッド、読むだけ？変える？」
* 「変えるなら、何が変わる？」
* 「呼び出し側はそれを期待してる？」

対象：自分のプロジェクトの `Get〜 / Search〜 / List〜` 系メソッド✨

### 演習B：分割リファクタ✂️🧠

混ざってるメソッドを1つ選んで👇

* Query部分 → `XXXQueries` へ
* Command部分 → `XXXCommands` へ

### 演習C：事故防止テスト🧪🧷

* ✅ Query を2回呼んでも状態が変わらないテスト
* ✅ Command の結果として「何が変わったか」を確認するテスト

---

## 10) AI活用（Copilot/Codex）プロンプト例🤖✨

Visual Studio 側でも Copilot がどんどん統合されてて、エディタからタスクを委任する流れも増えてるよ〜([The GitHub Blog][2])

その上で、こういう聞き方が強い👇

### 🧠 副作用の棚卸し

「このメソッドの副作用を全部列挙して。DB更新、イベント、時刻、乱数、キャッシュ、ログも含めて🙏」

### ✂️ CQSに分割案

「このクラスを CQS に分割して。Queryは状態変更なし、Commandは更新だけ。分割後のクラス名とメソッド名も提案して🙂」

### 🧪 “読むだけ”を保証するテスト

「この Query が状態を変えていないことを検証するテスト（xUnit）を書いて。2回呼んでも状態が変わらない観点で✅」

### 🧵 デバッグ補助

「この処理で“いつ状態が変わるか”追えるように、ブレークポイント候補とログポイント候補を提案して🧷」

---

## 11) まとめチェックリスト✅✨（この章の合格ライン）

* ✅ Query は **読んだだけで状態が変わらない**
* ✅ Command は **更新する責務に集中**（返しすぎない）
* ✅ 「読むだけのつもり」で呼んだら保存が走る、を消した👻
* ✅ “更新はここ！”が見える場所に集まった🔦✨

---

次の章（第5章）では、「じゃあ Command は何を返すのがちょうどいいの？🤔📦」を **気持ちよく整理**していくよ〜😊🎀

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14 "What's new in C# 14 | Microsoft Learn"
[2]: https://github.blog/changelog/2025-12-03-github-copilot-in-visual-studio-november-update/ "GitHub Copilot in Visual Studio — November update - GitHub Changelog"
