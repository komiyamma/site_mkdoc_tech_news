# 第3章：CommandとQueryの見分け方（判断の軸）🎯🧩

この章は **「これってCommand？Query？」** を迷わず判定できるようになる回だよ〜😊✨
（ここがフワッとしてると、後の章がぜんぶグラグラするので超大事！）

---

## 1) まず超シンプル定義いくよ📌

* **Command（コマンド）**：状態を変える（Create / Update / Delete など）🔧
* **Query（クエリ）**：状態を読む（Get / List / Search など）🔍

CQSの合言葉はこれ👇
**「変えるなら返しすぎない／返すなら変えない」**✨

※ちなみに今の最新は **C# 14 + .NET 10** が基準になってるよ（2025年11月公開）💡 ([Microsoft Learn][1])
Visual Studio も **Visual Studio 2026** が最新ラインにいるよ〜🛠️ ([Microsoft Learn][2])

---

## 2) 判断のいちばん強い軸：「観測できる状態が変わった？」👀

ここでいう「状態」は、だいたいこういうやつ👇

* DBのデータ 🗄️
* 画面に出る/APIが返す“業務データ” 📦
* ドメインのルール上の状態（例：注文=支払い済み、ToDo=完了）✅

**これが変わったら Command！**
変わってないなら **Query** の可能性が高いよ😊

---

## 3) 3ステップ判定フロー（迷ったらこれ）🧭✨

### ✅ Step 1：目的はどっち？

* 「登録したい／更新したい／削除したい」→ Command
* 「見たい／探したい／一覧がほしい」→ Query

### ✅ Step 2：実際に何か書き換えてる？

* DBにINSERT/UPDATE/DELETEしてる？ → Command
* コレクションにAdd/Removeしてる？ → Command
* 外部へ「作成」「送信」「確定」してる？（メール送信、決済、在庫引当など）→ Command

### ✅ Step 3：名前が紛らわしいときは「副作用」を疑う

名前が **Get** でも、裏で更新してたら Command だよ😇💥

---

## 4) ひっかけポイント集（ここが一番おいしい🍰）

### 4-1) 「Getなのに更新」タイプ 👻（←ほぼ事故）

例：既読を付ける、回数を増やす、最後に見た日時を更新する、など。

```csharp
// ❌ 名前はGetだけど、既読にしてるなら Command
public Message GetMessageAndMarkAsRead(Guid id)
{
    var msg = _repo.Get(id);
    msg.IsRead = true;          // ← 状態変更！
    _repo.Save(msg);            // ← 状態変更！
    return msg;                 // ← 値も返してる
}
```

👉 これは分けるのが正解✨

* `GetMessage(id)` … Query 🔍
* `MarkAsRead(id)` … Command ✅

---

### 4-2) ログ・メトリクスって状態変更じゃないの？🤔📈

ログ出力やメトリクス加算は「書き込み」だけど、**業務状態（ドメイン状態）じゃない**ことが多いよね。

* ✅ **ログ出力だけ**：多くの現場では Query に入れてOK扱いにすることが多い（観測のため）📝
* ⚠️ でも「検索回数をDBに保存」みたいに業務データとして使い始めたら、それは **Command寄り** になるよ💥

迷ったらこの基準👇
**「その変更は“ユーザーのデータ”として意味がある？」**
YESなら Command っぽい！👀

---

### 4-3) キャッシュ更新はどうする？🧊

これも超よく出る！

* ✅ **読むための最適化**（メモリキャッシュを温める等）→ Query扱いにすることが多い
* ❌ **キャッシュのせいで業務状態が変わる**（ポイント付与とか、在庫引当とか）→ Command

つまり👇
**「キャッシュは“性能の都合”ならQuery寄り、”業務の都合”ならCommand」**✨

---

### 4-4) “時刻取得”は？⏰

`GetCurrentTime()` みたいなやつは普通に Query でOK〜😊
（時刻が変わるのは世界の状態であって、アプリが書き換えたわけじゃないからね）

---

## 5) 命名で8割ラクになる（でも信用しすぎない）✍️💡

### ✅ Commandっぽい動詞

* Create / Add / Register / Update / Change / Delete / Remove
* Complete / Cancel / Approve / Reject / Pay など

### ✅ Queryっぽい動詞

* Get / Find / Search / List / Query / Read
* Calculate / Estimate（※計算だけなら）など

でもね…名前だけで決めると事故る😇
**「何をするつもりか」より「実際に何が変わったか」** が最強だよ🧠✨

---

## 6) 3分ミニ演習🧩⏱️（Command？Query？）

次のメソッド、どっち？（直感でOK😊）

1. `GetTodoList()`
2. `AddTodo(string title)`
3. `SearchUsers(string keyword)`
4. `GetUserAndUpdateLastLogin(Guid id)`
5. `CalculateShippingFee(int weight)`
6. `ReserveStock(Guid itemId, int qty)`
7. `GetOrCreateCustomerByEmail(string email)`
8. `DeleteTodo(Guid id)`
9. `GetMonthlyReportAndSaveCache(int year, int month)`
10. `MarkOrderAsPaid(Guid orderId)`

---

## 7) 演習の答え合わせ✅🎉（理由もセットで）

1. Query 🔍（読むだけ）
2. Command 🔧（追加＝状態変更）
3. Query 🔍（読むだけなら）
4. Command 😇💥（LastLogin更新してるなら状態変更）
5. Query 🔍（計算のみなら）
6. Command 🔧（引当＝状態変更）
7. だいたい Command 寄り⚠️（Createがあり得る＝状態変更の可能性）
8. Command 🗑️（削除＝状態変更）
9. Query寄りにすることは多い🧊（キャッシュ温めが目的なら）※ただし混ぜると混乱しやすいので要注意
10. Command ✅（支払い済みにする＝状態変更）

---

## 8) AI（Copilot/Codex）に手伝わせる“良い聞き方”🤖✨

AIに丸投げすると、たまに「それっぽい嘘」で突っ走るので😇
**判定＋理由＋副作用チェック**までセットで聞くのがコツ！

**コピペ用プロンプト👇**（そのまま使ってOK）

```text
次のメソッドはCQS観点で Command / Query のどちらですか？
1) 判断理由を「状態変更の有無」で説明して
2) 紛らわしい副作用（ログ/キャッシュ/時刻/通知/イベント）がある場合の注意点も書いて
3) もし混ざってるなら、分割後のメソッド名案も出して
```

---

## 9) この章のまとめ（ここだけ覚えれば勝ち🥇）

* **最強の判断軸は「観測できる状態が変わった？」**👀
* 名前がGetでも更新してたら **Command** 😇💥
* ログ/キャッシュは「業務状態かどうか」で扱いが変わる🧊📝
* 迷ったら **分割** がいちばん安全✨

---

次の章（第4章）では、わざと混ぜて **「地獄〜😂🪦」** を体験して、CQSの価値を腹落ちさせるよ！

[1]: https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14?utm_source=chatgpt.com "What's new in C# 14"
[2]: https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-history?utm_source=chatgpt.com "Visual Studio Release History"
