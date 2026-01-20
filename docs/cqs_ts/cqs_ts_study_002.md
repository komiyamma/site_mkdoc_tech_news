# 第2章：混ぜ混ぜ関数が起こす“あるある事故”集😇→😱

まず、いまの最新ツール感だけサクッと共有しとくね🧡

* TypeScript の最新安定版は **5.9.2（Stable）** まで出てるよ📌 ([GitHub][1])
* VS Code は **1.108（2025年12月版の更新が2026-01-08公開）**、Insiders は **1.109（2026-01-18更新）** が出てるよ🪟✨ ([code.visualstudio.com][2])
* VS Code で使える **Codex IDE 拡張**の案内も公式に出てるよ🤖🧰 ([OpenAI Developers][3])

---

## この章のゴール🎯✨

この章は「CQSのルール暗記」じゃなくて、**“混ぜると何がヤバいか”を体験して直感を作る回**だよ〜🧸💣

読み終わったら、こうなればOK👇

* 「この関数、何してるか説明しにくい…😵‍💫」が **危険信号**って分かる
* 「副作用（ふくさよう）ってこういうことか〜😱」が肌感で分かる
* 次章で CQS を学ぶモチベが爆上がりする🔥💖

---

## まずは“混ぜ混ぜ関数”を見てみよ😇🌀

ToDoアプリあるあるで、こういう「全部入り関数」を作っちゃいがち👇（事故の香りがぷんぷん😇）

```ts
type Todo = { id: string; title: string; done: boolean; createdAt: number };

const STORAGE_KEY = "todos";

function loadTodos(): Todo[] {
  return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]") as Todo[];
}

function saveTodos(todos: Todo[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
}

function escapeHtml(s: string) {
  return s.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

/**
 * 😇 混ぜ混ぜ関数：追加・保存・ログ・表示用整形まで全部やる
 */
export function addTodoAndRenderHtml(title: string): string {
  const todos = loadTodos();                       // 取得（読む）
  const todo: Todo = {
    id: crypto.randomUUID(),                       // ランダム（外部要因）
    title: title.trim(),                           // 整形（表示寄りの都合が混入しがち）
    done: false,
    createdAt: Date.now(),                         // 時刻（外部要因）
  };

  todos.push(todo);                                // 更新（書く）
  saveTodos(todos);                                // 保存（副作用）
  console.log("added:", todo.id);                  // ログ（副作用）

  // ⚠️ sort は配列をその場で並べ替える（= “見た目”のつもりが状態を変える）
  todos.sort((a, b) => b.createdAt - a.createdAt);

  return todos
    .map(t => `<li data-id="${t.id}">${t.done ? "✅" : "⬜"} ${escapeHtml(t.title)}</li>`)
    .join("");
}
```

この時点で「うわ…」ポイントが4つあるよ😱💥

* 追加（Command）してる
* 保存（副作用）してる
* ログ出してる（副作用）
* 表示用HTMLまで作ってる（UI都合）
  さらに `.sort()` が **“読むだけの顔して状態を書き換える”** のも地味にイヤ〜〜😇🧨

---

## 事故①：表示したいだけなのに…増える😱🪄

ありがちなのがこれ👇

* 画面初期表示で「一覧HTMLほしいな〜」って呼ぶ
* でもその関数、**“追加”も入ってる**
* 結果：ページ開いただけでToDoが増える😱💥

```ts
// 画面読み込み時
todoList.innerHTML = addTodoAndRenderHtml(""); // 😱 追加のつもりゼロなのに…
```

### なにが怖い？😨

「表示（Queryっぽい）」のはずの呼び出しで「保存（Command）」が走るから、
**“呼ぶだけで世界が変わる”** 関数になっちゃうの😭🌍💣

---

## 事故②：デバッグが地獄👹🔍「何が起きたの？」が説明できない

混ぜ混ぜ関数だと、バグが出た時にこうなる👇😇

* 追加が悪い？
* 保存が悪い？
* HTML整形が悪い？
* `.sort()` が順番変えた？
* `Date.now()` のせいで順序が揺れた？
* `randomUUID()` のせいで再現できない？

結果：**説明できない＝直せない** になりやすい😱🧯

---

## 事故③：“見た目だけ”の操作が、データを壊す😇→😱

たとえば「表示のためにタイトルを整える」って、ついこうしがち👇

```ts
// ありがち：表示用に整形したつもりが…
todo.title = todo.title.trim();   // 😱 “表示”の都合が “保存データ” に混入
```

これが進むと…

* 「入力そのまま保存したかったのに、勝手に変換される」
* 「過去データの意味が変わる」
  みたいな **静かな破壊** が起きるよ😱🫥💥

---

## 事故④：テストできない（＝安心して変更できない）😵‍💫🧪

混ぜ混ぜ関数は、だいたいテストが難しくなるよ〜😇

* `localStorage` が必要（環境依存）
* `Date.now()` が揺れる（毎回違う）
* `randomUUID()` が揺れる（毎回違う）
* `console.log` がうるさい（テストノイズ）
* HTMLまで生成（テスト対象がデカい）

つまり、**1個の関数に「不安定要素」が詰め込まれる**んだよね😱📦💥

---

## 事故⑤：二重実行・多重クリックで増殖する🐛🐛🐛

UIイベントって、意外と二重で走ることがあるの🥲（Enter＋Click、二重バインド、連打…）

混ぜ混ぜ関数だと、**二回呼ばれた＝二回保存される＝二個増える** 😱

```ts
button.addEventListener("click", () => {
  todoList.innerHTML = addTodoAndRenderHtml(input.value);
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    todoList.innerHTML = addTodoAndRenderHtml(input.value);
  }
});
// Enter押したら「keydown + click」みたいな事故で2回走ることも😱💥（状況次第）
```

---

## 事故⑥：エラーの“責任者”が不明になる🫠🧨

この関数、失敗ポイントが多すぎるよね😇

* JSON壊れてたら `JSON.parse` で落ちる
* localStorage が使えない環境だと落ちる
* HTML生成で想定外文字が混ざる
* 追加は成功したけど表示で落ちる、みたいな「中途半端」も起きる

でも戻り値は `string` だけ。
**「成功したの？失敗したの？どこまで進んだの？」が分からない**😱📉

---

## まとめ：混ぜると何が本当にヤバいの？🧠💥

いちばんヤバいのはこれ👇

## ✅ “呼ぶ前と後で、世界がどう変わるか”が読めない😱🌍

* Queryっぽく見える呼び出しで、保存が走る
* 表示のための処理が、データを変える
* 一回呼んだつもりが二回呼ばれて、増殖する
* どこで失敗したか説明できない

この状態をひとことで言うと…

## 「何が起きた？」を説明できない関数は、将来の自分を泣かせる😭💔

（未来のあなた：ｳｯ…たしかに…ってなるやつ🥹）

---

## ミニ演習🎮✨（超だいじ！）

## Q1：この関数の“副作用”を全部書き出してみて📝👀

ヒント：**外の世界に影響するもの**全部！

* 保存
* ログ
* 時刻
* ランダム
* 並び替え（地味に状態変化！）

## Q2：この関数を「表示のためだけ」に呼ぶと、何が起きうる？😱

「初期表示」「再描画」「フィルタ切り替え」みたいな場面を想像してみてね🪄

---

## AI活用コーナー🤖💡（Copilot / Codex向け）

そのままコピって投げてOKだよ〜✨（VS Code内で使う想定🧡） ([OpenAI Developers][3])

* 「この関数の副作用を“箇条書き”で列挙して。UI/保存/ログ/時間/乱数/配列破壊的操作も含めて」
* 「この関数が“説明できない”理由を、初心者向けに3つに分けて説明して」
* 「この関数を“データ更新”と“表示生成”に分けるなら、関数名案を10個出して」
* 「`.sort()` が危険な理由を、ミュータブル/イミュータブルの観点でやさしく教えて」

---

## 次章の予告📚✨

次は、いよいよ初心者版のCQSルールに入るよ✅💖

* Command：状態を変える🔧
* Query：状態を読む📖
  この章で見た事故たちが、「あ〜〜だから分けるのね！」ってスッキリ繋がるはず☺️✨

[1]: https://github.com/microsoft/typescript/releases "Releases · microsoft/TypeScript · GitHub"
[2]: https://code.visualstudio.com/updates?utm_source=chatgpt.com "December 2025 (version 1.108)"
[3]: https://developers.openai.com/codex/ide/?utm_source=chatgpt.com "Codex IDE extension"
