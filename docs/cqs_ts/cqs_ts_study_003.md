# 第3章：CQSの基本ルール（初心者版）✅✨

この章は、「**関数（メソッド）がやることを2種類に分けるだけ**」の超基本を、ふんわり→しっかりにしていく回だよ〜🧸🌸
読み終わったら「この関数、Command？Query？」がかなり迷いにくくなるはず！🎯✨

---

## 1. まずは“たった2種類”だけ覚えよ〜🧠💡

## ✅ Command（コマンド）＝状態を変える（副作用あり）🔧💥

* 例：追加する、更新する、削除する、保存する、送信する…
* **大事ポイント：** 何かが“変わる”ならCommand！

## ✅ Query（クエリ）＝状態を読む（副作用なし）📖🍃

* 例：一覧を取得する、件数を数える、検索する、計算して返す…
* **大事ポイント：** “聞くだけ”で、世界が変わらないのが理想！

この考え方は、Command と Query を**混ぜない**のがコツだよ〜✨（「Queryは状態を変えない」「Commandは値を返さない」という説明が有名！） ([martinfowler.com][1])

---

## 2. 超初心者向けCQSルールは「3行」でOK📝✨

## ✅ ルール①：1つの関数は「Command」か「Query」どっちかにする🎯

* “ついでに”を入れない！🙅‍♀️💦

## ✅ ルール②：Queryの中で「保存/更新/送信/ログ出し」はしない📦🚫

* `localStorage` に保存した
* DB/APIに書いた
* `console.log()`した
* カウンタ増やした
  …全部「副作用」扱いだと思ってOKだよ👀💥

## ✅ ルール③：迷ったら「状態が変わる？変わらない？」で決める🔍✨

* 変わる → Command
* 変わらない → Query

---

## 3. ありがち事故：CommandとQueryを混ぜるとこうなる😇→😱

たとえば ToDo でありがちな「混ぜ混ぜ関数」👇

```ts
type Todo = { id: string; title: string; done: boolean };

const todos: Todo[] = [];

export function addTodoAndReturnList(title: string): Todo[] {
  // ✅ 追加（状態変化）＝ Command
  const todo: Todo = { id: crypto.randomUUID(), title, done: false };
  todos.push(todo);

  // ✅ 一覧取得（参照）＝ Query
  // でも…同じ関数の中に入ってる！😱
  return todos;
}
```

これ、呼び出し側はこう思っちゃうの👇
「え？一覧返ってくるなら Queryっぽいよね？」🤔
でも中では `todos.push()` してて **状態が変わってる** 💥

---

## 4. 正しい分け方：Command と Query を分離する✂️✨

```ts
type Todo = { id: string; title: string; done: boolean };
const todos: Todo[] = [];

// ✅ Command：状態を変える（戻り値は基本なし）
export function addTodo(title: string): void {
  const todo: Todo = { id: crypto.randomUUID(), title, done: false };
  todos.push(todo);
}

// ✅ Query：状態を読む（副作用なし）
export function getTodos(): readonly Todo[] {
  // 呼び出し側がうっかり書き換えないようにガード🛡️✨
  return todos;
}
```

ポイントはここだよ👇

* `addTodo()` は「追加だけ」🔧
* `getTodos()` は「見るだけ」📖
* 「追加した結果の一覧が欲しい」なら
  **Command → Query の2ステップ**にするのが基本 🔁✨

---

## 5. 「副作用」ってなに？超ざっくりリスト🧨👀

Queryでやっちゃダメ（やるならCommand側へ！）になりがちなもの👇

* どこかに保存する（DB / ファイル / `localStorage`）💾
* ネットワーク送信する（API呼ぶ、Webhook投げる）🌐
* 状態を更新する（配列にpush、フラグ変更、カウンタ++）🔧
* ログを残す（`console.log` も広い意味で副作用）🪵
* 乱数・時刻に依存する（結果が毎回変わる）⏰🎲

  * ※「状態変更」じゃなくても、**“同じ入力で同じ出力にならない”**のは Query と相性が悪いよ〜💦

---

## 6. どうしても迷う「例外」ゾーン（軽く）🧠⚠️

CQSは基本ルールとして強いけど、例外もあるよ〜（有名なのは “pop” みたいなやつ！） ([martinfowler.com][1])

## 🌀 例外ケースの考え方（初心者向け）

迷ったらこの順で判断するとラク👇

1. **分けられる？**（`pop()` を `peek()` + `removeTop()` にできる？）✂️
2. **分けると使いにくすぎる？**（APIとして不自然？）😵‍💫
3. それでも混ぜるなら、**名前で「Commandっぽさ」を出す**📛

   * 例：`consumeNext()` / `popAndAdvance()` みたいに
     「状態動きますよ⚠️」感を出す✨

---

## 7. ミニ判断フローチャート（脳内用）🧠🗺️

* ① これ呼ぶと、保存されたデータ・メモリ・画面・外部が変わる？

  * YES → **Command** 🔧
  * NO → ②へ
* ② 同じ入力なら、いつ呼んでも同じ結果が返る？（時刻/乱数/グローバル依存してない？）

  * YES → **Query** 📖
  * NO → “Queryっぽいけど危険”⚠️（設計で改善チャンス！）

---

## 8. 仕分けクイズ（12問）🎯💖

次の関数は Command？Query？どっちかな？✨（直感でOK！）

1. `getTodoById(id)`：IDで1件返す
2. `markDone(id)`：完了フラグを立てる
3. `getTodoCount()`：件数を返す（ただし中で `console.log` してる）
4. `saveTodos()`：ローカル保存する
5. `formatTodoTitle(todo)`：表示用に整形して返す
6. `getNow()`：`Date.now()` を返す
7. `loadTodos()`：ローカルから読み込んで `todos` に反映する
8. `searchTodos(keyword)`：検索結果を返す
9. `incrementAccessCount()`：アクセス回数を+1する
10. `getTodosSorted()`：ソートした配列を返す（元配列は変更しない）
11. `popTodo()`：先頭を取り出して、配列からも消す
12. `ensureDefaultTodo()`：なければ1件作って、あればそのまま返す

## ✅ 答え（理由つき）💡

* 1. Query 📖（読むだけ）
* 2. Command 🔧（状態変える）
* 3. Command寄り ⚠️（ログ＝副作用。Queryにしたいならログ外へ！）
* 4. Command 🔧（保存は副作用）
* 5. Query 📖（純粋な変換）
* 6. Queryっぽいけど注意 ⚠️（同じ入力でも結果が変わるタイプ）
* 7. Command 🔧（読み込みで状態を反映＝変化）
* 8. Query 📖（読むだけ）
* 9. Command 🔧（++は状態変化）
* 10. Query 📖（元を変えないならOK✨）
* 11. Command（例外枠）🔧⚠️（取り出し＋削除で状態変化）
* 12. Command ⚠️（「なければ作る」で状態変化し得る）

---

## 9. AI活用コーナー🤖✨（この章にちょうどいい使い方）

## 💬 AIに投げると強いプロンプト例

* 「この関数、Command と Query に分けて。副作用も指摘して」🪄
* 「このQueryに隠れ副作用がないかチェックして」👀
* 「命名案を10個出して。Queryっぽい/Commandっぽい接頭辞も付けて」📛✨

VS Code側のCopilotは、**インライン提案**や**説明/実装の補助**ができるよ〜 ([code.visualstudio.com][2])
あと最近は、Copilot周りが「拡張機能の分割→統合」みたいに整理されてきてて、**従来の Copilot 拡張が段階的に整理される予定**も出てるよ🧹✨ ([code.visualstudio.com][3])

---

## 10. おまけ豆知識： “副作用を遅らせる” って発想もあるよ⏳🌱

TypeScript 5.9 では `import defer` で「モジュール実行（＝副作用が起きうる）を遅らせる」考え方が入ってきたよ〜✨
CQSの「副作用をコントロールする」感覚と相性いいので、頭の片隅に置いとくと得🧠🍯 ([typescriptlang.org][4])

---

## まとめ：この章の持ち帰りチェックリスト✅🎒

* [ ] 「状態が変わるならCommand」って即答できる🔧
* [ ] 「読むだけならQuery」って即答できる📖
* [ ] “ついで”の保存/ログ/更新が混ざってないか疑える👀
* [ ] 迷ったら「分けられる？」→「分ける」方向で考える✂️✨

次の章では、「TypeScriptだと戻り値どうするの？」（`void`？`Promise<void>`？`T`？）を気持ちよく整理していくよ〜🧩💖

* [The Verge](https://www.theverge.com/news/808032/github-ai-agent-hq-coding-openai-anthropic?utm_source=chatgpt.com)
* [TechRadar](https://www.techradar.com/pro/angry-github-users-want-to-ditch-copilot-features-forced-upon-them?utm_source=chatgpt.com)
* [windowscentral.com](https://www.windowscentral.com/artificial-intelligence/microsoft-adds-googles-gemini-2-5-pro-to-github-copilot-but-only-if-you-pay?utm_source=chatgpt.com)

[1]: https://martinfowler.com/bliki/CommandQuerySeparation.html "Command Query Separation"
[2]: https://code.visualstudio.com/docs/copilot/overview "GitHub Copilot in VS Code"
[3]: https://code.visualstudio.com/blogs/2025/11/04/openSourceAIEditorSecondMilestone "Open Source AI Editor: Second Milestone"
[4]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
