# 第5章：戻り値の基本ルール（Commandは何を返す？）📦✅

## この章のゴール🎯✨

* 「Commandは何を返してOKか／ダメか」を**迷わず決められる**ようになる😊
* “返しすぎてCQSが崩れる事故” を**未然に防ぐ**コツが身につく🧯
* 3つの落とし所パターン（ID／Result／何も返さない）を**手癖にする**💪

---

## 5-1 まず結論：Commandは基本「返さない」✅🙅‍♀️

CQSの一番コアな考え方はこれ👇

* **Query：値を返す／状態を変えない**
* **Command：状態を変える／値を返さない**

…という“分け方”そのものです。([martinfowler.com][1])

なので基本はこう👇

* Commandは **`void` / `Task`**（非同期なら `Task`）
* 成功は「完了した」でOK（結果データはQueryで取りにいく）🔍✨

---

## 5-2 でも現実はこう：例外として「返していいもの」もある👌🪪

「絶対に1バイトも返すな！」だと実務が詰むので、**必要最小限の“メタデータ”**は返してOKにします😊
たとえば「作成した直後に次の画面へ遷移したい」みたいな時ですね📱➡️

よくある“返してOK”はこれ👇

* ✅ **新しく作ったID**（`Guid` / `long` など）
* ✅ **成功/失敗ステータス**（`Result`、または `bool` でも最初はOK）
* ✅ **失敗理由（ユーザー向け）**（バリデーションなど）
* ✅ **更新のメタ情報**（更新日時、バージョン、ETag的なもの）※必要な時だけ

「返すなら **“業務データ本体”じゃなくて、次の操作に必要な最小情報**にしよ〜」って感じです😊
この“現実的な折衷”はCQRS/CQS界隈でもよく語られてます。([event-driven.io][2])

---

## 5-3 逆にダメ：Commandが返しちゃいけないもの🙅‍♀️💥

ここが事故ポイント！⚠️

* ❌ **Entity丸ごと**（`Todo` とか `Order` とか）
* ❌ **画面表示用DTO（Read Model）**
* ❌ **「作成後の一覧」みたいなクエリ結果**
* ❌ **“ついでに計算して返しました”の盛り盛りデータ**🍰💦

理由はシンプルで、**CommandがQueryの仕事（読む・整形する）まで背負い始める**からです👻
すると👇みたいな地獄が始まります…

* 「内部で余計なSELECTが増える」🐢
* 「返す形がUI都合に引っ張られて変更しづらい」🧱
* 「副作用と返却値の因果が追えない」🌀
* 「テストが重くなる」🧪💦

---

## 5-4 迷ったらコレ！3つの落とし所パターン🧩✨

### パターンA：何も返さない（基本形）✅

「完了したらOK」な操作はこれで十分😊

```csharp
public sealed class CompleteTodoHandler
{
    private readonly ITodoRepository _repo;

    public CompleteTodoHandler(ITodoRepository repo) => _repo = repo;

    public async Task HandleAsync(Guid id, CancellationToken ct)
    {
        var todo = await _repo.FindAsync(id, ct);

        if (todo is null)
            throw new InvalidOperationException("Todoが存在しません"); // ここは後の章で整えるよ🧯

        todo.MarkDone();
        await _repo.SaveChangesAsync(ct);
    }
}
```

🎀コツ：

* 「完了後の状態が欲しい」なら、**呼び出し側がQueryで取りに行く**🔍
* Command側は“やる”だけに集中！

---

### パターンB：IDだけ返す（作成系の定番）🪪✨

「作った直後に詳細画面へ行きたい」→ **IDだけ**で十分！

```csharp
public sealed class CreateTodoHandler
{
    private readonly ITodoRepository _repo;

    public CreateTodoHandler(ITodoRepository repo) => _repo = repo;

    public async Task<Guid> HandleAsync(string title, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(title))
            throw new ArgumentException("タイトルは必須です");

        var id = Guid.NewGuid();
        var todo = new Todo(id, title);

        _repo.Add(todo);
        await _repo.SaveChangesAsync(ct);

        return id; // ✅ 返していい最小情報
    }
}
```

---

### パターンC：Resultを返す（失敗を“仕様”として扱いたい時）🎁🧠

「入力ミス」みたいな**予測できる失敗**は `Result` が相性いいです😊
（例外を乱発しない設計にしやすい✨）

#### まずは超ミニResultでOK👌

```csharp
public readonly record struct Result(bool IsSuccess, string? Error)
{
    public static Result Ok() => new(true, null);
    public static Result Fail(string error) => new(false, error);
}

public readonly record struct Result<T>(bool IsSuccess, T? Value, string? Error)
{
    public static Result<T> Ok(T value) => new(true, value, null);
    public static Result<T> Fail(string error) => new(false, default, error);
}
```

#### 作成Command：IDをResultで返す🎁🪪

```csharp
public sealed class CreateTodoHandler
{
    private readonly ITodoRepository _repo;

    public CreateTodoHandler(ITodoRepository repo) => _repo = repo;

    public async Task<Result<Guid>> HandleAsync(string title, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(title))
            return Result<Guid>.Fail("タイトルは必須です😢");

        var id = Guid.NewGuid();
        _repo.Add(new Todo(id, title));
        await _repo.SaveChangesAsync(ct);

        return Result<Guid>.Ok(id);
    }
}
```

🎀ポイント：

* `Result<T>` の `T` は **業務データ本体ではなく“メタ情報”**に寄せる（IDなど）
* “作成後の表示用データ”は **Queryで取得**🔍✨

---

## 5-5 Web APIの「戻り値」とCommandの「戻り値」は別モノにする🌐🔁

API（HTTP）は「ステータスコード」「Locationヘッダー」「レスポンスボディ」など、**外向けの契約**が必要になります📮
Minimal APIだと、`201 Created` と `Location` を返すのが定番！✨

たとえば **`201 Created` の `Location` を相対パスで返す**例が公式ドキュメントにもあります👇（`TypedResults.Created`）([Microsoft Learn][3])

ここでの超大事な考え方は👇

* **Handler（アプリの中核）**：`Result<Guid>` みたいに最小の戻り値
* **Endpoint（外側）**：HTTPに変換して `Created(...)` を返す

つまり「依存の向き」をキレイに保てます🧭✨
（HandlerがHTTPの型を返し始めると、UI都合が中に侵食しやすいんです💦）

---

## 5-6 “返しすぎ”を防ぐチェックリスト✅🧠

Commandの戻り値を決めるとき、これを自問してね😊

1. その情報、**次の操作に本当に必須**？（画面遷移・関連処理など）
2. それって **業務データ本体**じゃない？（本体ならQueryへ！🔍）
3. “とりあえず返しとく” になってない？🍰💦
4. 返すなら **ID / 状態 / メタ情報**に寄せられる？🪪
5. 「失敗」は **仕様（Result）**？それとも **障害（例外）**？🧯

---

## 5-7 ミニ演習📝✨（サクッと！）

### 演習A：どれを返す？🤔

次のCommand、戻り値はどれが良い？（理由も一言で！）

1. `CompleteTodo(id)`

* A: `Task`
* B: `Task<bool>`
* C: `Task<Result>`

2. `CreateTodo(title)`

* A: `Task`
* B: `Task<Guid>`
* C: `Task<Result<Guid>>`

💡目安：

* “失敗が普通に起こる入力” → `Result` が気持ちいい🎁
* “作成したIDが必要” → `Guid`（または `Result<Guid>`）🪪

---

## 5-8 AI（Copilot/Codex）に頼む時の“事故らない”指示テンプレ🤖🧷✨

そのままコピペでOKだよ😊

### テンプレ①：Result型を作らせる🎁

```text
C#で、Command用の最小Result型(Result / Result<T>)を実装して。
要件:
- 例外は使わず、成功/失敗とエラーメッセージを保持
- Result<T>はValueとErrorを持つ
- 追加ライブラリなし、シンプルに
- サンプルでCreateTodoがResult<Guid>を返す例も付けて
注意:
- EntityやDTOは戻り値にしない
```

### テンプレ②：“返しすぎ”をレビューさせる🧠

```text
このCommandの戻り値はCQS的に適切？
「返しすぎ」や「Queryの仕事を混ぜている」可能性があれば、最小の戻り値に直した案を出して。
(例: IDだけ返す / Resultだけ返す / Queryで取り直す など)
```

---

## まとめ🎉

* Commandは基本 **`void/Task`**（“やった”だけでOK）([martinfowler.com][1])
* 例外として返していいのは **IDやステータスなど最小のメタ情報**🪪([event-driven.io][2])
* APIの `201 Created` / `Location` は **外側（Endpoint）で面倒を見る**のが安定🌐([Microsoft Learn][3])
* 迷ったら **「本体は返さない、必要ならQueryへ」**🔍✨

---

次の章（第6章）は「副作用の整理（見えない変更を見える化）👻⚠️」だね！
第5章の流れのまま、**“副作用が混ざると何が壊れるか”**をToDo題材で体験していこう😊✨

[1]: https://martinfowler.com/bliki/CommandQuerySeparation.html "Command Query Separation"
[2]: https://event-driven.io/en/can_command_return_a_value/ "Can command return a value? - Event-Driven.io"
[3]: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/route-handlers?view=aspnetcore-10.0 "Route handlers in Minimal API apps | Microsoft Learn"
