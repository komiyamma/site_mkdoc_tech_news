# 第12章：発展おまけ：キャッシュしやすいQuery🍯

〜「CQSを守ると、キャッシュが超ラクになる」って話だよ〜🥳💛

---

## この章のゴール🎯

* 「キャッシュって何が嬉しいの？」を**CQS目線**でつかむ🤝✨
* 「キャッシュしていいQuery」の条件を、**チェックリスト**で言えるようになる✅
* ToDo題材で「**安全なキャッシュ**」を小さく実装できるようになる🧩

---

## 12-1. キャッシュってなに？🍯（ふわっとでOK）

キャッシュはざっくり言うと👇
**「前に計算（取得）した結果を、とっておいて再利用する」**ことだよ〜💡

たとえば ToDo アプリで…

* フィルタ付き一覧（未完了だけ表示）を毎回ガチャガチャ計算する
* サーバーから毎回同じ一覧を取りにいく

みたいなの、地味に重い😵‍💫💦
そこでキャッシュが効くと👇

* 体感がキビキビ⚡
* 通信回数が減る📡
* バッテリーにもやさしい（スマホ想定なら）🔋✨

---

## 12-2. なんでCQSだとキャッシュしやすいの？💖

ここが今日のメイン🥰

**Query は「読むだけ」**だから、理想は👇

* 同じ入力 → 同じ結果（安定）🧊
* 余計な副作用なし（安全）🍃

つまり…
**「Query の結果は保存して再利用しても壊れにくい」**んだよね🍯✨
（逆に Command は状態を変えるから、キャッシュと相性が悪いことが多い⚠️）

---

## 12-3. キャッシュの種類（イメージだけでOK）🧠💡

## A) メモ化（関数キャッシュ）🧩

同じ引数で呼ばれたら、前回結果を返すやつ！

## B) データ取得キャッシュ（API結果キャッシュ）🌐

「todos 一覧」みたいな取得結果を保存して、しばらく再利用する！

## C) HTTPキャッシュ（ブラウザ/CDNのキャッシュ）🛰️

サーバーが `Cache-Control` などで「どれくらいキャッシュしていいよ」を指示できるよ〜📦✨ ([MDN ウェブドキュメント][1])
さらに更新確認のために「条件付きリクエスト（ETagなど）」で **変更なければ 304 Not Modified** を返す仕組みもあるよ🧾✨ ([MDN ウェブドキュメント][2])

---

## 12-4. 「キャッシュしていいQuery」チェックリスト✅🍯

Queryがこの条件を満たすほど、キャッシュして事故りにくいよ〜🥳

## ✅ チェック1：副作用ゼロ？

* DB保存しない🙅‍♀️
* ログ送信しない🙅‍♀️（ログは別の場所へ📍）
* グローバル状態をこっそり変えない🙅‍♀️

## ✅ チェック2：結果が安定してる？

* `Date.now()` で時間を混ぜない⏰❌
* `Math.random()` で運ゲーしない🎲❌
* 「現在のログインユーザー」みたいな**隠れ入力**がない👤❌

## ✅ チェック3：同じ入力なら同じ出力？

* 引数と明示的な入力だけで決まる🧊✨
  （＝テストもしやすい🥳）

## ✅ チェック4：返すデータが “うっかり改変” されない？

* 返した配列やオブジェクトを呼び出し側が `push()` とかしちゃうと事故る😱
* 対策：**コピーして返す**／**読み取り専用として扱う**📌

---

## 12-5. ToDo題材：キャッシュしやすいQueryの作り方📝✨

## 例：フィルタ済み一覧を返す Query

ポイントは👇

* **元データ（todos）**と**条件（filter）**が入力
* Query内で更新はしない
* 出力は「表示用の結果」だけ

```typescript
type Todo = { id: string; title: string; done: boolean };
type Filter = "all" | "active" | "done";

export function getVisibleTodos(todos: readonly Todo[], filter: Filter): Todo[] {
  switch (filter) {
    case "active":
      return todos.filter(t => !t.done);
    case "done":
      return todos.filter(t => t.done);
    default:
      return [...todos];
  }
}
```

これ、めちゃキャッシュ向き🍯✨
同じ `todos` と `filter` なら結果は同じになりやすいからね〜🥰

---

## 12-6. “メモ化”を超ミニでやってみよ🧩🍯

「同じ入力なら同じ出力」な Query は、メモ化の王道👑

## 超ミニ memoize（Mapで保存）

```typescript
export function memoize2<A, B, R>(fn: (a: A, b: B) => R) {
  const cache = new Map<string, R>();

  return (a: A, b: B) => {
    const key = JSON.stringify([a, b]);
    const hit = cache.get(key);
    if (hit !== undefined) return hit;

    const result = fn(a, b);
    cache.set(key, result);
    return result;
  };
}
```

## 使うとこう🎀

```typescript
const getVisibleTodosMemo = memoize2(getVisibleTodos);

// 何回呼んでも、同じ入力なら速い（ことが多い）
const v1 = getVisibleTodosMemo(todos, "active");
const v2 = getVisibleTodosMemo(todos, "active");
```

💡注意：`JSON.stringify` は「雑にやると落とし穴」もあるよ（順序・循環参照など）😵‍💫
でもこの章は“発想を掴む”がゴールだからOK〜🙆‍♀️✨

---

## 12-7. Command が走ったら、キャッシュはどうするの？🔁⚠️

ここが超大事！🥺✨
Command は状態を変えるから、**今までのQuery結果が古くなる**ことがあるよね？

そこで基本はこれ👇

## ✅ Command → キャッシュ無効化 → Queryで再取得

* `addTodo()`（Command）したら

  * `getTodos()` のキャッシュは古いかも
  * だから「無効化」して、次の Query を新しくする✨

“キャッシュの無効化”の戦略は大きく2つ👇

* **イベント型（Commandが起きたら消す）**🧯
* **時間型（TTLで期限切れ）**⏳

---

## 12-8. API取得のキャッシュ：考え方だけ先取り🌐🍯

フロントで「サーバーから取るデータ」をキャッシュする世界では、専用ライブラリが超強いよ💪✨
たとえば👇

* **TanStack Query**：取得・キャッシュ・更新・再取得などをまとめて面倒みる系📦✨ ([tanstack.com][3])
* **SWR**：キャッシュを返してから裏で再取得（stale-while-revalidate）をしやすい設計🌀✨ ([swr.vercel.app][4])

この章では深入りしないけど、言いたいのは👇
**CQSで Query を安定させるほど、こういう仕組みの恩恵を最大化できるよ〜🥳🍯**

（ちなみに TypeScript は 5.9.3 が最新扱いになってるよ📌） ([GitHub][5])

---

## 12-9. キャッシュの“やりすぎ注意”ポイント⚠️😇

キャッシュは正義っぽいけど、雑にやると事故るよ〜😱💦

* **古いデータをいつまでも見せちゃう**（期限や無効化が必要）⏳
* **メモリ食いすぎ**（キャッシュしすぎ）🍔
* **個人データをlocalStorageに入れて危ない**（取り扱い注意）🔐
* **「速くなった？」が体感できない場所に入れて複雑化**🌀

✅おすすめは
**「重い・頻繁・同じ結果になりやすいQuery」**から小さく🍯✨

---

## 12-10. ミニ演習（ToDoでやろう）🧪✨

## 演習A：キャッシュ向きQueryを増やす🧩

次の Query を作って、メモ化もしてみてね👇

* `getTodoStats(todos)` → `{ total, done, active }`

ヒント：入力は `todos` だけで、出力は統計だけ📊✨

## 演習B：Command後の無効化を入れる🔁

* `addTodo()` を実行したら

  * `getTodoStats` のキャッシュをクリアする🧯
  * 次の表示で再計算されるようにする

---

## 12-11. AIミニコーナー🤖✨（そのまま投げてOK）

* 「この Query はキャッシュして安全？危険ポイントも教えて」🕵️‍♀️
* 「この関数を“副作用ゼロのQuery”に直して、入力と出力が分かる形にして」🧼✨
* 「ToDoアプリの `getVisibleTodos` をメモ化したい。落とし穴と改善案を3つ」🧠💡
* 「Command実行後に無効化すべきキャッシュ一覧を提案して」🧯

---

## 12-12. 今日のまとめ🍯💖

* **CQSでQueryが安定**すると → **キャッシュがしやすい**🥳
* キャッシュしていいQueryは「副作用なし・同じ入力→同じ出力」🧊✨
* Commandが走ったら「無効化→Queryで再取得」が基本🔁✅

次の章はテストだよ〜🧪🥳
Queryが“入力→出力”になってると、ほんとに気持ちいいくらい簡単になるから楽しみにしててね〜💖✨

[1]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control?utm_source=chatgpt.com "Cache-Control header - HTTP - MDN Web Docs"
[2]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Conditional_requests?utm_source=chatgpt.com "HTTP conditional requests - MDN Web Docs"
[3]: https://tanstack.com/query?utm_source=chatgpt.com "TanStack Query"
[4]: https://swr.vercel.app/?utm_source=chatgpt.com "SWR"
[5]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
