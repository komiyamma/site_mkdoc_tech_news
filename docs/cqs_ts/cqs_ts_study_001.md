# 第1章：CQSってなに？超ざっくりつかむよ〜🧸✨

## 0. 今日のゴール🎯✨

今日のゴールはこれだけです👇
**「CQSの一文ルール」を、口に出して言えるようになること📝💕**

> **Command（命令）**：状態を変える（でも値は返さない）🔧
> **Query（質問）**：値を返す（でも状態は変えない）📖
> この考え方は Martin Fowler の説明が分かりやすいよ〜！ ([martinfowler.com][1])
> （由来は Bertrand Meyer の考え方としてもよく紹介されます🧠） ([ウィキペディア][2])

---

## 1. まず言葉だけ！Command / Queryってなに？🧸💬

### Command（コマンド）🔧💥

「何かをする」「変更する」系だよ〜✨
例👇

* ToDoを追加する ➕📝
* 完了にする ✅
* 保存する 💾
* 削除する 🗑️

👉 ポイント：**“世界（状態）を変える”**感じ🌍✨

### Query（クエリ）🔍📖

「知りたい」「取得したい」系だよ〜✨
例👇

* ToDo一覧を取得する 📋
* 完了済みだけ数える 🔢
* 1件だけ探す 🕵️‍♀️

👉 ポイント：**“見るだけ（副作用なし）”**が理想🍃

---

## 2. 「混ぜると事故る」直感を作ろう💥😇→😱

### 事故のにおい①：読んだだけなのに、何かが変わる👀💦

たとえば「一覧を表示する」つもりで呼んだ関数が…
実は裏で **ログ保存** したり **カウンタ増やしたり** してたら？📈🧨

* 何回呼ぶと何が起きるの？😵
* テストで同じ結果にならない…😱
* 表示の順番変えただけで動きが変わる…🌀

Fowler も「状態を変えない問い合わせ（Query）は安心して差し込める」みたいな話をしてるよ🍃✨ ([martinfowler.com][1])

---

## 3. いちばん大事：CQSの一文ルール📝💖

はい、今日の主役きた〜！！🧸✨

**✅ CQSの一文ルール**

* **Command**：状態を変える。**値を返さない**（基本は `void`）🔧
* **Query**：値を返す。**状態を変えない**（副作用なし）📖

「質問しただけで答えが変わるのは変だよね？」という直感が根っこだよ〜🌱 ([ウィキペディア][2])

---

## 4. ちっちゃいTypeScript例で体感しよ〜🧪✨

### 4-1. 混ぜ混ぜ（事故りやすい）例😱🧨

```ts
let todos: { id: number; title: string; done: boolean }[] = [];
let nextId = 1;
let viewCount = 0;

// 😱 Queryっぽい名前なのに、裏で状態が変わる！
export function getTodos(): { id: number; title: string; done: boolean }[] {
  viewCount++; // ← えっ、見ただけなのに増えた…😇
  return todos;
}
```

これ、呼ぶたびに `viewCount` が増えます📈💦
「一覧を表示するだけ」のはずなのに、**副作用が混ざってる**のがポイント😵‍💫

---

### 4-2. CQSっぽく分けた例🥳🍃

```ts
let todos: { id: number; title: string; done: boolean }[] = [];
let nextId = 1;
let viewCount = 0;

// ✅ Command：追加する（状態を変える）
export function addTodo(title: string): void {
  todos.push({ id: nextId++, title, done: false });
}

// ✅ Query：一覧を返す（状態を変えない）
export function getTodos(): { id: number; title: string; done: boolean }[] {
  return todos;
}

// ✅ Command：閲覧数を増やす（やるなら“増やす専用”に）
export function incrementViewCount(): void {
  viewCount++;
}

// ✅ Query：閲覧数を見る
export function getViewCount(): number {
  return viewCount;
}
```

こうすると…

* 「見るだけ」関数は安心して何回でも呼べる🍃✨
* 「増える」系は増えるって分かる🔧✨
* デバッグがラクになる🧩💖

---

## 5. 今日のミニ演習🎮✨（5〜10分）

### 演習A：これはどっち？仕分けしよう🎯

次の関数名、Command / Queryどっちっぽい？🤔💭

1. `saveUserProfile()` 💾
2. `getUserProfile()` 👀
3. `calculateTotalPrice()` 🧮
4. `markAsRead()` ✅
5. `searchTodos()` 🔍

**答え（目安）👇**

* 1 Command / 2 Query / 3 Query / 4 Command / 5 Query 🥳
  （※ `calculate...` は “計算するだけ” なら Query だよ〜🍃）

---

### 演習B：混ぜ混ぜを分けてみよう✂️✨

次の “混ぜ混ぜ関数” を **2つに分割**してみてね🧸💖

```ts
let todos: { title: string; done: boolean }[] = [];
let lastUpdated: Date | null = null;

// 😇 取得っぽいのに、更新もしちゃう！
export function getTodosAndTouch(): { title: string; done: boolean }[] {
  lastUpdated = new Date(); // ← 状態が変わる
  return todos;
}
```

**ヒント🧠✨**

* `getTodos()`（Query）
* `touchLastUpdated()`（Command）
  に分ければOK〜🙆‍♀️💕

---

## 6. AIに手伝ってもらうコーナー🤖🪄（超おすすめ！）

### そのままコピペ用プロンプト💌✨

* 「この関数、CQS違反してる？理由も教えて。直すならどう分ける？」🧸🔍
* 「このコードを Command と Query に分割して、関数名も提案して」✂️📛
* 「副作用になりそうなところ（Date/乱数/グローバル更新）を指摘して」👀⚠️

AIは“分割案”を出すの得意だけど、**最後の判断はあなたがルールで握る**のがコツだよ〜🎮✨

---

## 7. 今日のまとめ🌸💻✨

* **Command**＝変える🔧（基本、値を返さない）
* **Query**＝読む📖（基本、状態を変えない）
* 混ぜると「え、これ呼んだら何起きるの？」が増えてしんどい😱💦
* 今日の合言葉：**“聞くだけで世界を変えない🍃”**

---

## 8. おまけ：今のTypeScriptの小ネタ🫘✨

いま最新の TypeScript は **5.9 系**として案内されてるよ〜（インストール案内でも “currently 5.9” って書かれてる）📦✨ ([typescriptlang.org][3])
あと、TypeScript の“ネイティブ化”の流れ（TypeScript 7 のプレビュー系）も公式から出てて、ビルド高速化が話題になってるよ🚀 ([Microsoft Developer][4])

---

次の第2章では、わざと「混ぜ混ぜ関数」を作ってから、どんな事故が起きるか体験するよ〜😇→😱🎮✨

[1]: https://martinfowler.com/bliki/CommandQuerySeparation.html?utm_source=chatgpt.com "Command Query Separation"
[2]: https://en.wikipedia.org/wiki/Command%E2%80%93query_separation?utm_source=chatgpt.com "Command–query separation"
[3]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[4]: https://developer.microsoft.com/blog/typescript-7-native-preview-in-visual-studio-2026?utm_source=chatgpt.com "TypeScript 7 native preview in Visual Studio 2026"
