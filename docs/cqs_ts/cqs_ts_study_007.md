# 第7章：リファクタ① まず関数を分ける（CQSの第一歩）✂️✨

この章はね、「混ぜ混ぜ関数」を **Command と Query にスパッと分離**して、読める＆直せるコードにする回だよ〜🥳💕

---

## 1) 今日のゴール🎯✨

* 「状態を変える処理」＝ **Command** 🔧
* 「状態を読む処理」＝ **Query** 📖
* それを **別の関数に分ける**（最初の一歩）✂️

そして最終的に👇こうする！

* `addTodo()`（Command）➕📝
* `completeTodo()`（Command）✅
* `getTodos()`（Query）📋

---

## 2) まず“混ぜ混ぜ関数”を見て、事故ポイントを発見する👀💥

たとえば、こういうの…よくある！🥹（※わざとダメ寄せ）

```ts
type Todo = { id: string; title: string; done: boolean };

let todos: Todo[] = [];

function addTodoAndReturnHtml(title: string): string {
  // ✅ 状態を変える（Commandっぽい）
  todos.push({ id: crypto.randomUUID(), title, done: false });

  // ✅ 状態を読む（Queryっぽい）
  const visibleTodos = todos.filter(t => !t.done);

  // ✅ さらに表示用に整形（UIっぽい）
  return visibleTodos.map(t => `<li>${t.title}</li>`).join("");
}
```

## これ、何がツラいの？😱

* 関数名が「追加」なのに、**HTMLまで返してくる**🎭
* 「追加したいだけ」なのに、**表示ルールが一緒に入ってて直しづらい**🧩
* テストも「追加」なのか「表示」なのか、**何を検証すべきか分からない**🧪💦

---

## 3) 分け方のコツは“3色ペン”🖍️✨

コードを見たら、心の中でこう分けるのがコツだよ〜☺️

* 🔧 **Command**：配列に追加する／完了にする／保存する（とにかく“変える”）
* 📖 **Query**：一覧を返す／絞り込み結果を返す（“読むだけ”）
* 🖥️ **UI**：HTMLを作る／DOMを触る／表示する（“見せる”）

この章はまず **Command と Query の分離**が主役！👑
（UIとの境界は次章で“本格的に”やるよ🚪✨）

---

## 4) リファクタ手順（超安全ルート）🛟✨

## 手順A：まず“状態”をひとつに集める📦

```ts
type Todo = { id: string; title: string; done: boolean };

let todos: Todo[] = [];
```

## 手順B：Commandを切り出す🔧✨（状態を変えるだけ！）

```ts
export function addTodo(title: string): void {
  todos.push({ id: crypto.randomUUID(), title, done: false });
}

export function completeTodo(id: string): void {
  const t = todos.find(x => x.id === id);
  if (!t) return; // ここは今は軽くでOK（エラー設計は後でね🧸）
  t.done = true;
}
```

## 手順C：Queryを切り出す📖✨（読むだけ！）

ここが超重要ポイント👇
**外に配列をそのまま渡すと、外側で書き換えられて事故る**😇💥
だから「コピー」を返すクセをつけよ〜！

```ts
export function getTodos(): readonly Todo[] {
  // shallow copy（配列のコピー）で「外側からpush/sortされる事故」を防ぎやすくするよ🛡️
  return todos.slice();
}
```

---

## 5) UI側は「CommandしてからQueryする」だけにする🔁💕

UIの流れは基本これでOK👇

1. ボタン押した
2. `addTodo()`（Command）
3. `getTodos()`（Query）
4. 描画する

```ts
import { addTodo, completeTodo, getTodos } from "./todo";

function render(): void {
  const list = document.querySelector("#list")!;
  const items = getTodos()
    .filter(t => !t.done)
    .map(t => `<li data-id="${t.id}">${t.title} <button class="done">完了</button></li>`)
    .join("");
  list.innerHTML = items;
}

document.querySelector("#add")!.addEventListener("click", () => {
  const input = document.querySelector<HTMLInputElement>("#title")!;
  addTodo(input.value);
  input.value = "";
  render();
});

document.querySelector("#list")!.addEventListener("click", (e) => {
  const btn = (e.target as HTMLElement).closest("button.done");
  if (!btn) return;
  const li = (e.target as HTMLElement).closest("li");
  const id = li?.getAttribute("data-id");
  if (!id) return;

  completeTodo(id);
  render();
});

render();
```

これで **Command / Query / UI の役割がスッキリ**するよ〜🥰✨
（UIがちょい混ざっててもOK！この章はまず“関数分離”が勝ち🏆）

---

## 6) 命名ルール📛✨（迷ったらコレ！）

## Commandの名前（やること＝動詞）🔧

* `addTodo`
* `completeTodo`
* `deleteTodo`
* `saveTodos`

👉 **状態を変えそうな動詞**（add / set / update / delete / mark / save）を使うと迷子にならないよ🧭💕

## Queryの名前（欲しいもの＝取得・判定）📖

* `getTodos`
* `findTodoById`
* `countCompletedTodos`
* `isAllDone`

👉 `get / find / list / count / calc / is / has` あたりが鉄板🎯

---

## 7) よくあるミス集😇→😱（ここ超大事！）

## ❌ Queryのつもりで配列を並び替えちゃう

```ts
export function getTodosSortedBad(): readonly Todo[] {
  return todos.sort((a, b) => a.title.localeCompare(b.title)); // 😱 sortは破壊的！
}
```

✅ 対策：`slice().sort()` みたいに「コピーしてから」やる✨

## ❌ Queryがログ送信や保存をしちゃう📡

Queryは「読むだけ」だから、送信・保存・更新は置かない🙅‍♀️
（どうしても必要なら“別の場所”へ。ここは第9章あたりで気持ちよく整理できるよ🍃）

---

## 8) ミニ演習🎮✨（手を動かすと一気に身につく！）

## 問1：`deleteTodo(id)` をCommandとして追加🗑️✨

* やること：指定IDのTodoを消す
* ルール：戻り値は `void` でOK（まずはね😉）

## 問2：`getActiveTodos()` をQueryで追加📖✨

* やること：`done === false` だけ返す
* ルール：破壊的操作なし（`filter`はOK！）

## 問3：UI側を「Command → Query → render」に統一🔁✨

* どのイベントでも、この流れにそろえる💕

---

## 9) AIミニコーナー🤖💡（Copilot/Codexに投げると強い！）

そのままコピペで使えるプロンプト例だよ〜✨

* 「この関数の中で Command と Query が混ざってる場所を指摘して、分離案を出して」🧠✂️
* 「`addTodoAndReturnHtml` を `addTodo`（Command）と `getTodos`（Query）と `render`（UI）に分割して」🪄
* 「Queryに副作用が混ざってないかチェックして。怪しい行にコメントして」👀📝
* 「命名が紛らわしい関数名を、CQS的に分かりやすくリネーム案10個ちょうだい」📛✨

※GitHub Copilotは VS Code だと「Copilot本体＋Copilot Chat」の2拡張で動くよ〜🤝✨（最近は agent mode みたいな“複数ステップ実行”も強化されてる） ([Visual Studio Marketplace][1])
※CodexのVS Code拡張もあって、IDE内で作業を任せたりできるよ🤖（Windowsは“実験的”扱いの案内もあるから、環境次第でWSLワークスペース運用が安定寄り） ([OpenAI Developers][2])

---

## 10) 最新情報メモ（この教材の土台）🗞️✨

* TypeScriptのリリースノートは **5.9** が現行ラインとして参照でき、ページ更新も **2026-01-19** になってるよ📌 ([TypeScript][3])
* さらに「TypeScript 7（ネイティブ移植）」のプレビューや高速化（大規模で10x級の話）も公式側で継続発信されてるよ🚀 ([Microsoft Developer][4])
* VS Codeも **2025年12月版（1.108）** のリリース日が **2026-01-08** として公開されてるよ🧩 ([Visual Studio Code][5])

---

次章（第8章）は、いよいよ **「UIとロジックの境界」** を作って、さらに読みやすくするよ〜🚪🧱✨

[1]: https://marketplace.visualstudio.com/items?itemName=GitHub.copilot "
        GitHub Copilot - Visual Studio Marketplace
    "
[2]: https://developers.openai.com/codex/ide/ "Codex IDE extension"
[3]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
[4]: https://developer.microsoft.com/blog/typescript-7-native-preview-in-visual-studio-2026 "TypeScript 7 native preview in Visual Studio 2026 - Microsoft for Developers"
[5]: https://code.visualstudio.com/updates "December 2025 (version 1.108)"
