# 第10章：Command設計：返していいもの／ダメなもの🎁⚠️

## この章のゴール🏁✨

* Commandの戻り値で迷ったときの“判断の軸”を持つ🧠💡
* 「返しすぎCommand（＝実質Query混入）」を見抜けるようになる👀💥
* **基本パターン：Command → Queryで再取得🔁** を自然に使えるようになる🙌✨

---

## 1) なんでCommandの戻り値って悩むの？😵‍💫

Commandって「状態を変える係」だよね🔧
でも実務だとついこう言いたくなるの👇

* 「更新した後の一覧も返してよ〜🥺」
* 「画面に出す用に整形して返して〜🖼️」

これ、**“読む”情報が戻り値に混ざる**と、CommandがQueryっぽいことまで背負いがち💥
すると…

* どこで何を読んでるのか分かりにくい😇
* 仕様変更で壊れやすい（UI都合がドメインに侵入）🧨
* テストが一気にダルくなる🥲

---

## 2) Commandが「返してOK」なものはこの3カテゴリ🎁✅

### A. ID（識別子）🪪✨

作成系Commandの王道！
「作ったよ！」の証拠として **新しいIDだけ返す**のは超よくある💖

* ✅ `todoId`
* ✅ `userId`
* ✅ `orderId`

### B. 成否（と、必要最小の理由）✅❌

「できた？できなかった？」は、Commandの責務の範囲だよ🙆‍♀️
例：

* ✅ `ok: true/false`
* ✅ 失敗理由（業務的なものだけ）

  * 例：「すでに完了済みだった」
  * 例：「権限がない」

### C. 最小のメタ情報（再取得の助け）🧾✨

「読み取り」じゃなくて、**再取得・整合性チェックに必要な最小情報**ならOKになりやすいよ！

* ✅ `version`（楽観ロック用の世代）
* ✅ `updatedAt`（更新時刻）
* ✅ `etag` みたいなもの

---

## 3) Commandが「返すと危険」なもの🐘⚠️（返しすぎあるある）

ここがこの章のメイン！🔥

### ❌ 更新後の一覧を返す

* `completeTodo()` が **更新後のToDo一覧** を返す
  → それ、ほぼQueryしてるよね？😇

### ❌ 画面表示用に整形済みのデータを返す

* `displayText: "✅ 完了：牛乳を買う"` とか
  → UI都合がロジック層に入り込む💥

### ❌ でっかいEntity丸ごと返す

* `Todo` を丸ごと返す（しかも内部に他の情報も…）
  → 将来フィールドが増えると依存が増殖🌱🌱🌱

---

## 4) 基本パターン：Command → Queryで再取得🔁✨

いちばん安全で、読みやすくて、育てやすい流れだよ💖

1. Commandで更新する🔧
2. 画面更新に必要なら Queryで読む📖

これができると、CQSがグッと気持ちよくなる😌✨

ちなみにTypeScriptは現時点で **5.9系**が最新メジャーとして案内されてるよ（2026-01時点）。([TypeScript][1])

---

## 5) ToDoミニアプリで「返しすぎCommand」を直してみよ🛠️💖

### 5-1. ダメ寄り例（返しすぎ）😇💥

```ts
type Todo = { id: string; title: string; completed: boolean };

const todos: Todo[] = [];

export function addTodo_bad(title: string): Todo[] {
  // Command（追加）しつつ…
  const id = crypto.randomUUID();
  todos.push({ id, title, completed: false });

  // Query（一覧取得）まで一緒にやっちゃう…😱
  return todos;
}

export function completeTodo_bad(id: string): Todo[] {
  const t = todos.find(x => x.id === id);
  if (t) t.completed = true;

  // 更新後一覧を返す＝“読んでる”混入💥
  return todos;
}
```

**問題ポイント**

* 「追加・完了」っていう更新（Command）をしながら、一覧取得（Query）まで混ぜてる😱
* 将来「一覧の並び順」「フィルタ」「ページング」みたいな要求が来ると、Commandが肥大化🐘

---

### 5-2. 良い例：Commandは最小だけ返す（ID or 成否）🎁✅

```ts
type TodoId = string;
type Todo = { id: TodoId; title: string; completed: boolean };

const todos: Todo[] = [];

type CommandResult =
  | { ok: true }
  | { ok: false; reason: "NOT_FOUND" | "ALREADY_COMPLETED" };

export function addTodo(title: string): TodoId {
  const id: TodoId = crypto.randomUUID();
  todos.push({ id, title, completed: false });
  return id; // ✅ IDだけ返す
}

export function completeTodo(id: TodoId): CommandResult {
  const t = todos.find(x => x.id === id);
  if (!t) return { ok: false, reason: "NOT_FOUND" };
  if (t.completed) return { ok: false, reason: "ALREADY_COMPLETED" };

  t.completed = true;
  return { ok: true }; // ✅ 成否だけ返す
}

// QueryはQueryで分ける✨
export function getTodos(): readonly Todo[] {
  return todos;
}
```

---

### 5-3. UI側はこう使う（Command→Query）🖥️🔁

```ts
const newId = addTodo("牛乳を買う🍼");
const list1 = getTodos(); // 画面更新用に読む📖

const r = completeTodo(newId);
if (r.ok) {
  const list2 = getTodos(); // 更新後の画面反映✨
} else {
  // 失敗理由に応じてメッセージ出せる🙂
}
```

---

## 6) それでも「少し返したい」実務の落とし所🧩✨

たとえば「追加した直後に、その1件だけ画面に出したい」みたいな時あるよね🥺
その場合は **“最小のスナップショット”だけ**返す、が妥協ラインになりやすいよ👇

* ✅ `id`
* ✅ `title`
* ✅ `completed`（初期値）
* ✅ `updatedAt`（あるなら）

でも！

* ❌ 一覧まるごと
* ❌ 表示用整形済み
  は避けよ〜🐘💥

---

## 7) TSで事故を減らす小ワザ🧠✨（CQSにも効く！）

### noImplicitReturns で「返し忘れ」を検出🧯

CommandResultみたいなUnionを返すとき、返し忘れが地味に危ない😇
`noImplicitReturns` をONにすると「全部の分岐でreturnしてる？」をチェックしてくれるよ。([TypeScript][2])

（TypeScript 5.9の `tsc --init` も“今どき向けに更新”されてるので、初期設定の質も上がってるよ🧸✨）([Microsoft for Developers][3])

---

## 8) チェックリスト✅✨（迷ったらここを見る！）

### Commandの戻り値、こう考える🧠

* 「これは**読むための情報**？」

  * YES → Queryへ📖
* 「これは**更新した事実の通知**？」

  * YES → OK（成否・ID・最小メタ）🎁
* 「この戻り値がないとUIが更新できない？」

  * たいていQueryを呼べばOK🔁

### よくある地雷💣

* 「便利だから一覧返しちゃえ」→ その便利、未来にツケ来る🥲
* 「画面文言まで返す」→ UIの変更でドメイン壊れる😱

---

## 9) 演習（手を動かすやつ）✍️💖

### 演習1：返しすぎを分離しよ✂️✨

* `completeTodo_bad()` を

  * `completeTodo()`（Command）
  * `getTodos()`（Query）
    に分けてね！

### 演習2：成否の設計🎯

* `NOT_FOUND` のとき
* `ALREADY_COMPLETED` のとき
  UIが表示する文言は **Commandから返さず**、UI側で作ってね🧁

### 演習3：どこまで返す？クイズ🎲

次の戻り値、OK/NGどっち？理由も✨

1. `TodoId`
2. `ok: boolean`
3. `updatedAt`
4. `Todo[]`（更新後一覧）
5. `displayText`（画面表示用文字列）

---

## 10) AIコーナー🤖🪄（そのままコピペでOK）

* 「この関数、CQSに直して。CommandとQueryを分けて、Commandの戻り値は最小にして」
* 「このCommand、返しすぎてない？返すなら何が最小？理由もつけて」
* 「`CommandResult` をUnion型で設計して。業務的な失敗理由も2〜3個提案して」
* 「`noImplicitReturns` で引っかかる可能性がある箇所を指摘して」

---

## まとめ🌸✨

* Commandは「状態を変える係」🔧
* 戻り値は **ID／成否／最小メタ** までが基本🎁
* 「更新後一覧を返す」はQuery混入の代表例🐘💥
* 困ったら **Command → Queryで再取得🔁** に戻ろう😌💖

次の第11章は、この考え方を **Promise（非同期）でも崩さず**やる回だよ〜🌐⏳

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[2]: https://www.typescriptlang.org/tsconfig/?utm_source=chatgpt.com "TSConfig Reference - Docs on every TSConfig option"
[3]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/?utm_source=chatgpt.com "Announcing TypeScript 5.9"
