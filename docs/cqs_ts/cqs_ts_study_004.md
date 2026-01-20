# 第4章：TypeScriptでCQSを書く時の型（戻り値の決め方）🧩

この章はね、**「戻り値の型をどう決めると、CQSがブレなくなるか」**を、TypeScriptで“手触り”が出るように練習する回だよ〜🥰💡
（戻り値って、実は**設計の意思表示**そのものなんだよね…！🫶）

---

## 1) まず結論：戻り値はこう決める！🎯✨

### ✅ Query（読む）📖

* 同期なら：**`T`**
* 非同期なら：**`Promise<T>`**

### ✅ Command（変える）🔧

* 同期なら：**`void`**
* 非同期なら：**`Promise<void>`**

この「4つ」に揃えるだけで、コードが急にスッキリして事故りにくくなるよ〜😇✨

> TypeScriptでも「戻り値の型」は関数型の一部で、`(a: string) => void` は「戻り値がない」って意味だよ〜🧠✨ ([TypeScript][1])
> Promiseは「非同期処理の結果（成功/失敗）を表すオブジェクト」なので、非同期Queryは `Promise<T>` になるよ〜⏳✨ ([MDN ウェブドキュメント][2])

---

## 2) Queryの戻り値：**“ほしいデータそのもの”**を返す📦✨

Queryは「読む」だけだから、戻り値は素直でOK🙆‍♀️💕

### よくあるQuery例🧸

```ts
export type Todo = {
  id: string;
  title: string;
  completed: boolean;
};

export function getTodos(): Todo[] {
  // 読むだけ（副作用なしのつもり！）
  return [
    { id: "1", title: "レポート", completed: false },
    { id: "2", title: "買い物", completed: true },
  ];
}

export function findTodoById(id: string): Todo | undefined {
  return getTodos().find(t => t.id === id);
}
```

* `Todo[]` みたいに **欲しい形をそのまま返す**のが基本だよ🥳✨
* 「見つからない」があり得るなら `T | undefined` が自然だよ〜🫧

### 非同期Queryは `Promise<T>` 🌐✨

```ts
export async function fetchTodos(): Promise<Todo[]> {
  const res = await fetch("/api/todos");
  const data = (await res.json()) as Todo[];
  return data;
}
```

---

## 3) Commandの戻り値：基本は **`void`**（＝返さない）🧹✨

Commandは「変える」側。
戻り値を盛り始めると、だんだん **Queryっぽい責務**が混ざってくるのが落とし穴😱💥

### 典型Command例🧯

```ts
const store: Todo[] = [];

export function addTodo(title: string): void {
  store.push({
    id: crypto.randomUUID(),
    title,
    completed: false,
  });
}

export function completeTodo(id: string): void {
  const t = store.find(x => x.id === id);
  if (!t) return;
  t.completed = true;
}
```

### 非同期Commandは `Promise<void>` 🧵✨

```ts
export async function saveTodo(title: string): Promise<void> {
  await fetch("/api/todos", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ title }),
  });
}
```

---

## 4) 超だいじ：`void` の“挙動”の落とし穴👀💣

TypeScriptではちょっと不思議なことが起きるよ〜😳

### ⚠️ `() => void` って「何も返せない」じゃない！？

**“文脈（contextual typing）で `void` を期待されてる関数”**は、実装側が値を返してもOKになっちゃうことがあるの！
（返した値は **呼び出し側が無視する**って扱い） ([TypeScript][1])

たとえば `forEach` のコールバックがまさにそれ👇
`forEach` は戻り値 `void` を期待してるけど、実際には `push` が number を返してもOK、みたいな現象が起きるよ〜😇 ([TypeScript][1])

**つまり**：

* 「`( ) => void` と書いたから、絶対にreturnできない」ではない
* “戻り値を使わない”という意味が強い

> 公式ドキュメントでも「`void` は文脈次第で、返しても無視される」って説明されてるよ📚 ([TypeScript][1])

### ✅ 対策の気持ち🛡️✨

* **Command関数そのもの**は `function x(): void { ... }` / `async function x(): Promise<void> { ... }` みたいに、**関数宣言側でハッキリさせる**のが気持ちいい🙆‍♀️✨
* コールバック（引数で渡す関数）の `void` は「戻り値を使わないよ」くらいで捉えると混乱しにくいよ〜🫶

---

## 5) 「Commandは何を返してもいい？」の答え🎁✨（最小限だけOK）

基本は **返さない**が一番キレイ💎
でも現実には「ちょっとだけ返したい」があるよね🥺

ここでの合言葉は👇

### ✅ Commandが返していいのは **“レシート”** 🧾✨

* **ID**（作ったものの識別子）
* **成否**（OK/NG）
* **バージョン**（楽観ロックとかの）
* **最小限のメタ情報**（作成日時など）

逆に、これはやりがちだけど避けたい👇

### ❌ Commandが返しがちなダメ例🐘💥

* 「更新後の一覧を返す」
* 「画面表示用に整形したデータを返す」
* 「ついでに検索結果も返す」

それ、Queryの仕事まで混ざりやすいの〜😱💦
（Commandが太ると、テストもデバッグも地獄になりがち😇）

### レシートOK例🧾✨

```ts
export type CreateTodoReceipt = { id: string };

export function createTodo(title: string): CreateTodoReceipt {
  const id = crypto.randomUUID();
  store.push({ id, title, completed: false });
  return { id };
}
```

**ポイント**：返してるのは “中身” じゃなくて “控え” だけ☺️🧾✨
中身が欲しければ **Queryで取りに行く**のがCQSっぽいよ🔁💕

---

## 6) 非同期Commandのもう1個の落とし穴：「await付け忘れ」😱⚡

`Promise<void>` のCommandを呼ぶとき、うっかり `await` を忘れると、**失敗がどこかに飛んでいく**ことがあるよ〜🥲

そこで登場するのが、よく使われるlintルール：`no-floating-promises` 🧹✨
このルールは「Promiseを放置しないで！」って怒ってくれるやつ！

* `void somePromise()` って書くと「意図的にawaitしない」意思表示になるよ🙋‍♀️
* でも `void` は **エラー処理をしてくれるわけじゃない**ので、拒否（reject）されたら普通に問題は起きるよ⚠️ ([typescript-eslint.io][3])

---

## 7) ミニ演習：戻り値の型を選んでみよ〜🎯💗

次の関数、戻り値はどれが自然？
**A: `void` / B: `T` / C: `Promise<void>` / D: `Promise<T>`** で考えてね🧠✨

1. `getTodoList()`（一覧を返す）
2. `addTodo(title)`（追加する）
3. `loadTodoListFromServer()`（サーバから一覧を取る）
4. `saveTodoToServer(todo)`（サーバへ保存する）
5. `isCompleted(id)`（完了してるか調べる）
6. `completeTodo(id)`（完了にする）

👉 解答イメージ：

* 読む＝B/D、変える＝A/C、同期/非同期で分岐だよ〜🥳✨

---

## 8) AIに頼るコーナー🤖✨（コピペで使ってOK）

* 「このファイルの関数をCQS観点で見て、Command/Queryを分類して。戻り値の型が変なら指摘して📝」
* 「Commandが“返しすぎ”になってる箇所を見つけて、レシート型に直す案を出して🧾✨」
* 「`Promise<void>` の呼び出しで `await` 付け忘れが起きそうな箇所を洗って⚡」
* 「Queryに副作用（保存/更新/ログ送信など）が混ざってないかチェックして👀🍃」

---

## まとめ🎀✨

* Queryは **`T` / `Promise<T>`**（欲しいデータを返す📦）
* Commandは **`void` / `Promise<void>`**（基本は返さない🧹）
* 例外で返すなら **レシート（ID/成否など最小限）** 🧾
* `void` は文脈で「返しても無視される」ことがあるから、そこだけ注意ね👀💥 ([TypeScript][1])
* 非同期Commandは `await` 忘れがちなので、lintや運用で守るのが安心🛡️✨ ([typescript-eslint.io][3])

次の章で、わざと“混ぜ混ぜToDo”を作ってから直すから、ここで覚えた戻り値ルールがめっちゃ効いてくるよ〜😎💖

[1]: https://www.typescriptlang.org/docs/handbook/2/functions.html "TypeScript: Documentation - More on Functions"
[2]: https://developer.mozilla.org/ja/docs/Web/JavaScript/Guide/Using_promises?utm_source=chatgpt.com "プロミスの使用 - JavaScript - MDN Web Docs"
[3]: https://typescript-eslint.io/rules/no-floating-promises?utm_source=chatgpt.com "no-floating-promises"
