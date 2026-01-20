# 第9章：Query設計：副作用ゼロにするコツ🍃✨

この章は「**Queryって、どこまで“読むだけ”にできる？**」を体にしみこませる回だよ〜🧸💡
ゴールはシンプル👇

* Queryを見た瞬間に「何が起きるか」予想できる👀✨
* テストがラクになる🧪🥳
* バグの温床（隠れ副作用）を踏まない💣💥

---

## 0. ちょい最新トピック（今の空気感）📰✨

今の安定版TypeScriptは **5.9.3** が最新（npm上の “Latest”）だよ〜📦✨ ([npm][1])
そしてTypeScriptは **6.0→7.0（ネイティブ移行）** に向けて動いてて、6.0は“橋渡し”の位置づけ、7.0はGo実装のネイティブ版へ…っていう流れが公式から出てるよ🚀 ([Microsoft for Developers][2])

さらに5.9では `import defer` みたいに、**モジュールの実行（=副作用が起きるタイミング）を遅らせられる**仕組みも入ってて、「副作用を制御する」方向性が強まってる感じ✋✨ ([TypeScript][3])

この章の「Queryは副作用ゼロに寄せる」って考え方、まさに今っぽいよ〜🌿

---

## 1. Queryの副作用ってなに？（ふわっと→くっきり）🍃

### ✅ Queryの理想

* **同じ入力なら、いつ呼んでも同じ結果**
* **呼んでも世界が変わらない**（状態更新しない、外に送らない、書き込まない）

### 🙅‍♀️ Queryでやらない代表例

* 保存（DB / ファイル / localStorage）💾
* 更新（配列・オブジェクトをその場で書き換え）🧨
* 外部送信（HTTP / analytics / webhook）🌐
* 時刻や乱数に依存（結果が毎回変わる）⏰🎲
* “ついで”のログ（console出力）📝（※後で「置き場所」教えるよ！）

---

## 2. 隠れ副作用チェックリスト👀🧾✨

Queryって「読んでるだけのつもり」でも、地雷があるの…😇💣
よくあるやつ、これ👇

### 2-1. 時刻：`Date.now()` を呼んでる⏰

`Date.now()` は “今のミリ秒” を返すから、呼ぶたび変わるよ〜😳 ([MDN ウェブドキュメント][4])
つまり Queryの結果がブレやすい！

* 例：`getTodos()` の中で「期限切れ判定」を `Date.now()` でやる
  → テストが不安定になりがち🧪💥

### 2-2. 乱数：`Math.random()` を呼んでる🎲

* 例：Queryの中で「おすすめ3件」をランダム抽出
  → 結果が毎回変わって、デバッグ地獄😵‍💫

### 2-3. 配列の `sort()` が“その場で並べ替える”🧨

`sort()` は配列を **in-place（その場）でソートしてしまう**よ〜⚠️ ([MDN ウェブドキュメント][5])
Queryで `sort()` したつもりが、元データを壊してるパターン超ある…😇

✅ 対策：**コピーしてからソート** or **`toSorted()` を使う**（非破壊）✨ ([MDN ウェブドキュメント][5])

### 2-4. グローバル（外側の変数）を書き換えてる🌍

* `let cache = ...` みたいなのを Query内で更新
* “閲覧回数” を Queryが増やす
  → それ、Commandのお仕事だよ〜🙅‍♀️

### 2-5. 例外：読むだけでも“外部I/O”はブレる🌐

* Queryが `fetch()` で外部APIから取得
  → 「読む」だけでも、相手次第で結果が変わる
  → CQSの意味では“Query”扱いでも、**純粋Query** ではない、って感覚が大事💡

---

## 3. 「副作用ゼロQuery」を作る3つの型🧩✨

ここからが実戦だよ〜🔥

### 型A：Queryは “引数 → 戻り値” に寄せる📦➡️🎁

* 外部に取りに行かない
* グローバルを読まない
* 受け取ったデータを加工して返すだけ

### 型B：加工は “コピーしてから” やる✂️✨

* 破壊的操作（`sort()` など）は避ける
* 新しい配列・新しいオブジェクトを作って返す

### 型C：ブレる要素（時刻・乱数）は “注入” する💉⏰🎲

* Queryの外から「今はこれ」って渡してあげる
* テストでは固定値にできる🧪✨

---

## 4. ToDo題材で「地雷Query」→「いいQuery」へ📝✨

### 4-1. まずは地雷例😇💣（`sort()` で元データ破壊）

```ts
type Todo = {
  id: string;
  title: string;
  done: boolean;
  createdAt: number; // epoch ms
};

export function getTodos_bad(todos: Todo[]): Todo[] {
  // ❌ これ、元の todos をその場で並べ替えちゃう
  todos.sort((a, b) => b.createdAt - a.createdAt);
  return todos;
}
```

* 呼ぶだけで `todos` の順番が変わる🧨
* 「読むだけの関数」の顔して世界を変えるタイプ😇

✅ 改善：**非破壊で返す**（`toSorted()` or コピーしてsort）

```ts
export function getTodos_ok(todos: readonly Todo[]): Todo[] {
  // ✅ toSorted() は元の配列を変えず、新しい配列を返す
  return todos.toSorted((a, b) => b.createdAt - a.createdAt);
}
```

`toSorted()` が使えるのは、まさに「Queryの副作用を減らす」方向の進化だよ〜🍯✨ ([MDN ウェブドキュメント][5])

---

### 4-2. もう一個の地雷：Queryが “時刻” に触る⏰💥

```ts
export function getOverdueTodos_bad(todos: readonly Todo[]): Todo[] {
  const now = Date.now(); // ❌ 呼ぶたび変わる
  return todos.filter(t => !t.done && t.createdAt < now - 7 * 24 * 60 * 60 * 1000);
}
```

`Date.now()` は呼ぶたび“今の値”だから、結果がブレやすいよ〜 ([MDN ウェブドキュメント][4])

✅ 改善：**「今」を外から渡す**（注入💉）

```ts
export function getOverdueTodos_ok(
  todos: readonly Todo[],
  now: number
): Todo[] {
  const weekMs = 7 * 24 * 60 * 60 * 1000;
  return todos.filter(t => !t.done && t.createdAt < now - weekMs);
}
```

* 本番：`getOverdueTodos_ok(todos, Date.now())`
* テスト：`getOverdueTodos_ok(todos, 1700000000000)`（固定）
  → テストが安定する〜🥳🧪✨

---

## 5. 「どうしてもログが欲しい😢」の置き場所📍📝

気持ちはわかる！
でも Queryの中で `console.log()` とか analytics をやると、**“読むだけ”が嘘になる**のね😇

おすすめはこの2択👇

### 5-1. 呼び出し側でログする（いちばん素直）🙆‍♀️

* Queryは純粋に返す
* 呼んだ人がログする

### 5-2. “ラッパー”で包む（Queryは汚さない）🎁✨

```ts
export function withQueryLog<TArgs extends unknown[], TResult>(
  name: string,
  query: (...args: TArgs) => TResult
) {
  return (...args: TArgs) => {
    const result = query(...args);
    console.log(`[query:${name}]`, { args, result }); // ログはここ
    return result;
  };
}
```

Query本体は純粋のまま🍃
ログは“外側”でやるのがコツだよ〜✨

---

## 6. 仕上げ：Query副作用ゼロの「最終チェック」✅👀

Queryを書いたら、これを自分に質問してね🧸✨

* これ、**同じ入力なら同じ出力**？（時間・乱数・外部I/Oでブレない？）⏰🎲
* **何かを書き換えてない**？（配列/オブジェクト/グローバル）🧨
* **保存・送信・ログ**してない？💾🌐📝
* `sort()` してない？（してたら `toSorted()` or コピー）🔁 ([MDN ウェブドキュメント][5])

---

## 7. ミニ演習（5分）🎯✨

### 演習A：副作用ある？判定してみて👀

次のうち「Queryとして危険」なのはどれ？（複数OK）

1. `return todos.filter(...)`
2. `todos.sort(...); return todos;`
3. `return todos.toSorted(...)`
4. `const now = Date.now(); return ...`
5. `console.log("get"); return ...`

答えの方向性：2,4,5 が特に危険〜💣（3はOK寄り）✨

### 演習B：AIに“副作用レビュー係”をやらせる🤖🪄

Copilot / Codex にこう投げてみてね👇

* 「この関数が副作用を持つ可能性を列挙して、修正案を出して」
* 「CQSのQueryとして安全か判定して、危険なら理由付きで直して」
* 「`sort()` や `Date.now()` が混ざってないかチェックして」

---

## まとめ🍃💖

* Queryは **“読むだけ”を信用できる設計**にするのが価値✨
* 隠れ副作用の地雷は **時刻・乱数・in-place操作（`sort()`）・ログ** あたりが多い💣
* コツは **コピーして加工**＋**ブレ要素は注入**＋**ログは外へ** 🧩✨
* その結果、テストが安定して、デバッグがめちゃラクになるよ〜🥳🧪

次の章（第10章）では、「Commandは何を返していいの？」問題をスッキリさせるよ〜🎁⚠️✨

[1]: https://www.npmjs.com/package/typescript?activeTab=versions&utm_source=chatgpt.com "typescript"
[2]: https://devblogs.microsoft.com/typescript/progress-on-typescript-7-december-2025/?utm_source=chatgpt.com "Progress on TypeScript 7 - December 2025"
[3]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html?utm_source=chatgpt.com "Documentation - TypeScript 5.9"
[4]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/now?utm_source=chatgpt.com "Date.now() - JavaScript - MDN Web Docs - Mozilla"
[5]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort?utm_source=chatgpt.com "Array.prototype.sort() - JavaScript - MDN Web Docs"
