# 第11章：非同期のCQS（Promise版の基本だけ）🌐⏳

この章は「非同期になっても、CQSのルールは一切ブレない」って感覚を作る回だよ〜☺️💕

---

## 今日のゴール🎯💡

* `Promise<void>`（Command）と `Promise<T>`（Query）を迷わず書ける✨
* `fetch` の超基本（`ok` チェック → `json()`）が書ける✨ ([MDN ウェブドキュメント][1])
* 「Commandしたら Queryで取り直す🔁」の気持ちよさを体験する✨

---

## 11-1. 非同期って、結局なに？🤔💭

非同期＝「待ち時間がある処理（ネットワーク/DB/ファイルなど）を、Promiseで扱う」ってことだよ〜⏳📦

* `fetch()` は **Promise** を返す（将来の `Response` を約束してる） ([MDN ウェブドキュメント][1])
* `response.json()` も **Promise** を返す（読み取り＆変換が“待ち”だから） ([MDN ウェブドキュメント][2])

つまりこう👇

* `fetch()` → `Promise<Response>`
* `response.json()` → `Promise<any>`（なので型で整えるのがTSの仕事💪）

---

## 11-2. 非同期でもCQSのルールは同じ✅✨

### ✅ Query（読む）📖

* 状態を読む（例：GETで一覧取得）
* 戻り値は **`Promise<T>`**（読む結果があるから）

### ✅ Command（変える）🔧

* 状態を変える（例：POST/PUT/DELETEで更新）
* 戻り値は基本 **`Promise<void>`**
* どうしても必要なら「最小限（IDとか）」だけ返すのはOK🎁（第10章の話）

> 🧠ポイント：**HTTPのメソッド**で考えると最初は超ラクだよ〜
> GET＝Query、POST/PUT/DELETE＝Command（まずはこれでOK🙆‍♀️）

---

## 11-3. `fetch` の最小セット（これだけ覚えよ）🧩✨

`fetch` は「成功っぽく見えても失敗してる」ことがあるので、**`response.ok` を必ず見る**のが基本だよ👀✨ ([MDN ウェブドキュメント][1])

```ts
// どこでも使い回せる “fetchの型付きラッパー” 🧁
export async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);

  // ここ大事！HTTP的に失敗なら例外にする（後の章でResult型に進化させてもOK）
  if (!res.ok) {
    throw new Error(`HTTP Error: ${res.status} ${res.statusText}`);
  }

  // json()はPromiseを返すよ（＝awaitが必要） :contentReference[oaicite:4]{index=4}
  return (await res.json()) as T;
}
```

> 🍬この `as T` は「型チェックをサボる」書き方でもあるから、
> 本気で堅くするのは後の章（入力チェックやエラーモデリング）でやればOKだよ☺️

---

## 11-4. ToDo題材を「非同期CQS」にするよ〜📝🌐✨

今回は、ダミーAPIとして **DummyJSON** を使うね（ToDoが用意されてて便利！）

* 一覧：`GET https://dummyjson.com/todos`
* 追加：`POST https://dummyjson.com/todos/add`
* 更新：`PUT https://dummyjson.com/todos/1`
  （※“サーバーに本当に保存はされないけど、挙動は学べる”って書いてあるよ） ([DummyJSON][3])

### ① 型を作る🧸🧩

```ts
export type Todo = {
  id: number;
  todo: string;
  completed: boolean;
  userId: number;
};

type TodoListResponse = {
  todos: Todo[];
  total: number;
  skip: number;
  limit: number;
};
```

---

### ② Query：一覧を取る（`Promise<Todo[]>`）📖✨

```ts
import { fetchJson } from "./fetchJson";
import type { Todo } from "./types";

type TodoListResponse = {
  todos: Todo[];
  total: number;
  skip: number;
  limit: number;
};

export async function getTodosQuery(): Promise<Todo[]> {
  const data = await fetchJson<TodoListResponse>("https://dummyjson.com/todos");
  return data.todos;
}
```

* **読む**だけだから Query ✅
* **配列が欲しい**から `Promise<Todo[]>` ✅

---

### ③ Command：追加する（基本は `Promise<void>`）➕🔧✨

まずは王道の「返さない」版（シンプル！）👇

```ts
import { fetchJson } from "./fetchJson";
import type { Todo } from "./types";

export async function addTodoCommand(todoText: string): Promise<void> {
  await fetchJson<Todo>("https://dummyjson.com/todos/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      todo: todoText,
      completed: false,
      userId: 1,
    }),
  });
}
```

* **状態を変える（追加）**から Command ✅
* 追加の結果（一覧など）を返したくなるけど…ここは我慢！🙅‍♀️
  → **Commandのあとに Query で取り直す**のがCQSの基本の型だよ🔁✨

---

### ④ 「IDだけ欲しい」なら最小限だけ返す🎁✨（オプション）

```ts
import { fetchJson } from "./fetchJson";
import type { Todo } from "./types";

export async function addTodoCommand_ReturnId(todoText: string): Promise<{ id: number }> {
  const created = await fetchJson<Todo>("https://dummyjson.com/todos/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      todo: todoText,
      completed: false,
      userId: 1,
    }),
  });

  return { id: created.id }; // “最小限” ✅
}
```

---

## 11-5. UIから呼ぶときの「CQS黄金パターン」🏆✨

やりたいことはいつもこれ👇

1. Command（追加/更新）
2. Query（一覧を再取得）
3. 画面に反映

```ts
import { addTodoCommand } from "./commands";
import { getTodosQuery } from "./queries";

let todos: { id: number; todo: string; completed: boolean; userId: number }[] = [];

export async function refreshTodos(): Promise<void> {
  todos = await getTodosQuery();
  render(todos);
}

export async function onClickAdd(todoText: string): Promise<void> {
  try {
    await addTodoCommand(todoText); // Command 🔧
    await refreshTodos();           // Query 📖（再取得）🔁
  } catch (e) {
    alert("失敗しちゃった…🥲 もう一回ためしてみてね！");
  }
}

// 画面表示（例）
function render(list: typeof todos) {
  console.log(list);
}
```

> 🌟ここまでできたら「非同期でもCQSできてる！」って胸張ってOKだよ〜🥳🎉

---

## 11-6. あるある事故集😇→😱（ここだけ先に潰す）

### 😱 事故1：`await` 付け忘れ

* `response.json()` もPromiseだから、`await` 忘れると中身が取れないよ〜 ([MDN ウェブドキュメント][2])

### 😱 事故2：QueryのつもりでPOSTしちゃう

* 関数名が `get...` なのに中で `POST` してたらアウト🙅‍♀️
  → **読むならGET、変えるならPOST/PUT/DELETE**（最初はこれで十分）

### 😱 事故3：Commandが“更新後の一覧”を返す

* 「便利そう」でやりがちだけど、責務が混ざって事故りやすい🐘💥
  → Commandの後は Queryで取り直す🔁

---

## 11-7. ミニ演習✍️✨（手を動かす用）

### 演習A：分類ゲーム🎯

次は Command？Query？理由も一言で書いてみて〜😊

1. `fetch('/todos')` で一覧取得
2. `fetch('/todos/add', { method: 'POST', ... })`
3. `fetch('/todos/1', { method: 'PUT', ... })`
4. 一覧を `completed=true` のものだけに絞る（配列操作だけ）

### 演習B：実装チャレンジ🧪

* `setTodoCompletedCommand(id, completed): Promise<void>` を作る（PUTでOK） ([DummyJSON][3])
* そのあと `refreshTodos()` を呼ぶ（黄金パターン🔁）

---

## 章末：AIコーナー🤖✨（そのままコピペOK）

* 「この関数はCommand？Query？理由も一言で」🧠
* 「`fetch` 周りの例外処理、初心者向けに読みやすくして」🧼
* 「Commandの戻り値が大きすぎないかレビューして」🎁👀
* 「`getTodosQuery` の戻り値型、もっと安全にする方法ある？」🧷✨

---

## おまけメモ（最新動向ちょいだけ）📌✨

現時点の安定版TypeScriptは **5.9.3** が “latest” 扱いだよ（npmもGitHubも同じ） ([npm][4])
あと、TypeScript 6.0/7.0（ネイティブ化の流れ）も進捗が出てるけど、教材としてはまず **今の安定ラインで迷わず書ける**のが最優先でOK！ ([Microsoft for Developers][5])

---

次の章（第12章）は「Queryが安定するとキャッシュしやすい🍯」に行けるよ〜！
この第11章のコードを、あなたのToDoミニアプリの構成（ファイル分け）に合わせて “教材として綺麗な形” に整えたバージョンも作れるよ☺️💖

[1]: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch?utm_source=chatgpt.com "Using the Fetch API - MDN Web Docs"
[2]: https://developer.mozilla.org/en-US/docs/Web/API/Response/json?utm_source=chatgpt.com "Response: json() method - Web APIs | MDN"
[3]: https://dummyjson.com/docs/todos "Todos - DummyJSON - Free Fake REST API for Placeholder JSON Data"
[4]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[5]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
