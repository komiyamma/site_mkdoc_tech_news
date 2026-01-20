# 第8章：リファクタ② “境界”を作る（UIとロジックを分ける）🚪🧱

## この章でできるようになること 🎯💖

* **UI（入力・表示）** と **ロジック（判断・処理）** を「線引き」できるようになる✂️✨
* Query を **副作用ゼロ** に近づけて、**テストしやすい形**にできる🧪🥳
* “やりすぎ設計” にならない **ちょうどいい分け方**がわかる🧯🙂

---

## 2026年1月時点のメモ（最新リサーチ）🗓️🔎

* TypeScript の npm latest は **5.9.3**（2025-09-30 公開）だよ〜📦 ([npm][1])
* TypeScript **6.0 は 5.9 → 7.0 への“橋渡し”**として **2026年初頭リリース予定**、という位置づけ（Microsoft 公式）🌉 ([Microsoft for Developers][2])
* Vite は GitHub リリース表示上 **v7.3.1 が Latest**（2026-01 中旬確認）⚡ ([GitHub][3])
* VS Code は 2026年1月の更新ページで **1.108 が available** と表示されてるよ🧰 ([Visual Studio Code][4])

この章の内容は **TypeScript 5.9.x 前提でもそのままOK** 👍✨（6.0/7.0 になっても “境界” の考え方は変わらないよ〜）

---

## 1) “境界”ってなに？🚪✨（超かんたん）

**境界**＝「ここから先は UI の担当、こっちはロジックの担当ね！」って決める **境目**のことだよ〜🙂💡

* **UI（外側）**：入力を受け取る、ボタン押下、DOM描画、アラート表示、フォーム操作…など 🎨🖱️
* **ロジック（内側）**：追加していい？どんなTodo作る？完了にしたらどうなる？並び順どうする？…など 🧠🧩

この境界を作ると、CQSが一気に守りやすくなるの！
UI は副作用まみれでもOK。でも **Query は副作用ゼロでいたい**から、Query を **UI から隔離**しよ〜って話だよ🍃✨

---

## 2) なぜ UI とロジックを分けるの？🤔💥

UI とロジックが混ざってると、ありがちな事故が起きるよ〜😱

### 事故①：Query なのに副作用が混ざる 🧨

* `getTodos()` の中で DOM を触ったり
* ついでに localStorage 書いたり
* ついでにログ送ったり
  → 「読むだけのはずが、何か起きてる」状態に…😇

### 事故②：テストが地獄 👿🧪

* DOM が必要
* ブラウザ環境が必要
* 依存が多くて “入力→出力” の比較ができない
  → Query の良さ（テスト簡単）が消える〜😭

### 事故③：UI変更がロジックに波及して壊れる 🧟‍♀️

* 見た目を少し変えただけで、ロジックが動かなくなる
  → “触ったら壊れる” アプリになる🥶

---

## 3) どこまで分ければOK？やりすぎ防止ライン🧯✨

この章は、まず **レベル2** を目標にするのがちょうどいいよ〜🙂💖

### 境界レベル（おすすめ順）📈

* **レベル1：同ファイルで区切る**（コメントの壁でもOK）🧱
* **レベル2：ファイル/フォルダを分ける（おすすめ）** 📁✨
* **レベル3：外部依存（保存/通信）を“差し替え可能”にする** 🔌（次以降の章で強くなる）

この章は **レベル2中心＋レベル3をチラ見**くらいでいくね👀✨

---

## 4) “境界”の合言葉：依存の向きは一方通行➡️🧭

超ざっくりでOKなルール👇

* **外側（UI）は内側（ロジック）を呼んでOK**
* **内側（ロジック）は外側（UI）を知らない**（importしない）🙅‍♀️

イメージ👇

* UI → ロジック ✅
* ロジック → UI ❌

これが（初見でも大丈夫な）**Dependency Rule の入口**だよ〜🚪✨

---

## 5) ToDoミニアプリ：境界を作るリファクタ実演📝💖

ここからは「第7章までに分けた Command/Query」が **まだUIと混ざってる**想定で、境界を作るよ〜✂️✨

### ゴールの構成（おすすめ）📁✨

```
src/
  core/
    todo.ts            // 型・純粋関数（副作用なし）
    todoStore.ts       // 状態を持つ（Command側の“器”）
  ui/
    main.ts            // DOM・イベント・描画（副作用だらけOK）
```

* `core/`：**ロジック担当（内側）** 🧠
* `ui/`：**UI担当（外側）** 🎨

---

## 6) core/todo.ts：まず “純粋ロジック” を作る🍃✨

ここはできるだけ **副作用なし**でいくよ〜🧪🥳

```ts
// src/core/todo.ts
export type TodoId = string;

export type Todo = Readonly<{
  id: TodoId;
  title: string;
  done: boolean;
  createdAt: number; // epoch ms
}>;

// ✅ Query向け：表示用に整えるだけ（副作用なし）
export function sortTodosByCreatedAtDesc(todos: readonly Todo[]): Todo[] {
  return [...todos].sort((a, b) => b.createdAt - a.createdAt);
}

// ✅ Commandの“中身”：配列をどう更新するか（副作用なし）
export function addTodo(
  todos: readonly Todo[],
  input: { id: TodoId; title: string; createdAt: number }
): Todo[] {
  const title = input.title.trim();
  if (title.length === 0) return [...todos]; // 空は無視（例）
  const next: Todo = { id: input.id, title, done: false, createdAt: input.createdAt };
  return [...todos, next];
}

export function completeTodo(todos: readonly Todo[], id: TodoId): Todo[] {
  return todos.map(t => (t.id === id ? { ...t, done: true } : t));
}
```

ポイントだよ〜👇✨

* `core/todo.ts` は **DOMもlocalStorageも触らない**🙅‍♀️
* `todos` を直接変更しないで、**新しい配列**を返す（地味に超大事）🧼✨
* これだけでテストは “入力→出力” で終わるようになる🧪💕

---

## 7) core/todoStore.ts：状態（副作用）を “器” に閉じ込める📦🧩

UI が配列を直接いじり出すとまた混ざるから、**状態は Store に持たせる**のが楽だよ〜🙂✨

```ts
// src/core/todoStore.ts
import { addTodo, completeTodo, sortTodosByCreatedAtDesc, type Todo, type TodoId } from "./todo";

export class TodoStore {
  private todos: Todo[] = [];

  // Command ✅：状態を変える
  add(title: string): void {
    // “外部っぽいもの”はここで作って core/todo.ts に渡す
    const id = crypto.randomUUID();      // ブラウザの副作用寄りAPI
    const createdAt = Date.now();        // 時間も“揺れる”値
    this.todos = addTodo(this.todos, { id, title, createdAt });
  }

  // Command ✅
  complete(id: TodoId): void {
    this.todos = completeTodo(this.todos, id);
  }

  // Query ✅：読むだけ（副作用なしの形で返す）
  getAllSorted(): Todo[] {
    return sortTodosByCreatedAtDesc(this.todos);
  }
}
```

ここが “境界のコツ”💡

* `Date.now()` と `crypto.randomUUID()` は **ロジックの純度を落とす要素**だから、**Store側に寄せた**よ〜🧠➡️📦
* `core/todo.ts` の純度が上がって、テストしやすいまま保てる🧪✨

---

## 8) ui/main.ts：UIは “呼ぶだけ＆描くだけ” にする🎨🖱️✨

UIは副作用の塊でOK！その代わり **判断を持ち込まない**のが大事🙂💖

```ts
// src/ui/main.ts
import { TodoStore } from "../core/todoStore";
import type { Todo } from "../core/todo";

const store = new TodoStore();

const form = document.querySelector<HTMLFormElement>("#todo-form")!;
const input = document.querySelector<HTMLInputElement>("#todo-input")!;
const list = document.querySelector<HTMLUListElement>("#todo-list")!;

function render(todos: readonly Todo[]): void {
  list.innerHTML = "";
  for (const t of todos) {
    const li = document.createElement("li");
    li.dataset.id = t.id;

    const label = document.createElement("span");
    label.textContent = t.done ? `✅ ${t.title}` : `⬜ ${t.title}`;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = t.done ? "完了済み💤" : "完了にする✅";
    btn.disabled = t.done;

    btn.addEventListener("click", () => {
      store.complete(t.id);          // ✅ Commandを呼ぶだけ
      render(store.getAllSorted());  // ✅ Queryで取り直して描画
    });

    li.append(label, " ", btn);
    list.append(li);
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  store.add(input.value);           // ✅ Command
  input.value = "";
  render(store.getAllSorted());     // ✅ Query → 描画
});

// 初期描画
render(store.getAllSorted());
```

この形になると最高ポイント👇🥳✨

* UI は **store に命令するだけ**（Command）
* 表示は **store から読むだけ**（Query）
* “更新後の一覧を返す” みたいな **混ぜ混ぜが自然に減る**🔁💖

---

## 9) “境界”ができたかチェックするコツ👀✅

### チェック①：core/ に DOM が出てきたら赤信号🚨

* `document`, `window`, `alert` が `core/` に出てきたら混ざってる！

### チェック②：Query が何か保存/送信してたらアウト🙅‍♀️

* `localStorage.setItem`
* `fetch` でログ送信
* DB更新（サーバー呼び出し）
  → それは Query じゃなくて Command 側へ！

### チェック③：import の向きが逆になってない？➡️

* `core/` が `ui/` を import してたら依存逆流😱
* UI → core の一方通行を守ろ〜✨

---

## 10) やりすぎ防止🧯🙂「今日はここまででOK」ライン

境界を作るとき、こうなったら一旦ストップでOK👇

* ファイル数が増えすぎて迷子📁😵‍💫
* まだ機能が少ないのに DI/抽象化を盛りすぎた🌀
* “綺麗” だけど、追加が遅くなった🐢

この章のゴールは **「UIとロジックが別れてて、CQSが守りやすい」** ことだよ〜💖
アーキテクチャ職人になるのは、もうちょい後でOK😌✨

---

## 11) ミニ演習（15〜30分）🧪⏰✨

### 演習A：フィルタ Query を core に追加してみよ〜🔎

* `getActiveTodos()`（未完了だけ）
* `getDoneTodos()`（完了だけ）

UI はボタンで切り替えて、**Queryで取って render** にする🎨✨

### 演習B：入力バリデーションをどこに置く？🧠

* 空文字は無視
* 50文字以上は禁止
  これ、UIで弾く？ coreで弾く？
  おすすめ：**core側（addTodoの中）に寄せる**と、入口が増えても安全🙂💖

### 演習C：完了を “トグル” にしたい🔁

* `toggleTodo()` を core に追加して、Store と UI を更新してみよ〜😆✨

---

## 12) AI活用コーナー🤖💡（そのまま投げてOK）

* 「この `ui/main.ts` を、UIとロジックの境界が明確になるように分割して。`core/` はDOM禁止で！」
* 「この関数、Queryなのに副作用ありそう？怪しいところを指摘して、直して」
* 「`core/todo.ts` のテストケースを3つ作って（入力→出力で）」🧪
* 「依存の向き（UI→core）を壊してるimportがないかチェックして」👀

---

## まとめ🌸✨

* **境界＝UIとロジックの担当分け**🚪🧱
* **core は純度高め**にすると、CQSが守りやすくてテストも楽🧪🥳
* **依存の向きは UI → core の一方通行**➡️✨
* やりすぎず、まずは **フォルダを分ける（レベル2）** がちょうどいい📁💖

次の章（第9章）では、いよいよ **Queryを副作用ゼロにする“チェック術”** を、もっと具体的にやっていくよ〜🍃👀✨

[1]: https://www.npmjs.com/package/typescript?utm_source=chatgpt.com "TypeScript"
[2]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[3]: https://github.com/vitejs/vite/releases?utm_source=chatgpt.com "Releases · vitejs/vite"
[4]: https://code.visualstudio.com/updates/v1_109?utm_source=chatgpt.com "January 2026 Insiders (version 1.109)"
