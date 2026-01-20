# 第13章：テスト① Queryはテストが超簡単🧪🥳

この章は「Query（読むだけ・副作用なし）って、テストすると気持ちよすぎる…！」を体験する回だよ〜🌸✨
ToDoミニアプリ題材のまま、`getTodos()` みたいな Query をテストしていくよ📚💖

---

## 1) 今日のゴール🎯✨

* ✅ Queryのテストが「入力→出力の比較だけ」になる理由を体感する
* ✅ 並び替え・絞り込み・検索みたいな Query をテストできる
* ✅ 「隠れ副作用」をテストで炙り出せる🔥👀
* ✅ AIに“テスト雛形”を作らせて、人間がチェックして仕上げる🤖✍️

---

## 2) なんでQueryはテストが簡単なの？🧠💡

Query の理想はこれ👇

* **同じ入力**を渡したら
* **いつも同じ出力**が返ってきて
* **外の世界（保存・通信・ログ・日時・乱数）**に触らない🍃

つまりテストはこうなるよ👇

* ✅ **入力を用意して（Arrange）**
* ✅ **関数を呼んで（Act）**
* ✅ **出力を比べるだけ（Assert）**

副作用がないと「モック地獄」になりにくいのが最高〜🥳🫶

---

## 3) テスト道具はどうする？🧰✨（おすすめ：Vitest）

TypeScriptでサクッと書きやすくて、動作も速くて、今どきの開発と相性いいのが **Vitest** だよ〜⚡️🧪
（2025年秋にVitest 4が出て、npmでも4系が最新として更新されてるよ） ([vitest.dev][1])

> ちなみに Jest も定番で、安定版は Jest 30 が案内されてるよ📌 ([jestjs.io][2])
> ただ今回は “軽く始めて気持ちよく回す” を優先して Vitest でいくね💖

### インストール（例）

```bash
npm i -D vitest
```

`package.json` にテストコマンドを追加（例）

```json
{
  "scripts": {
    "test": "vitest"
  }
}
```

実行✨

```bash
npm test
```

---

## 4) 題材：ToDoの “Queryだけ” をテストしよう📝🧪

ここでは ToDo をこんな感じで扱うよ👇

* `getTodos()`：一覧を返す（そのまま）
* `queryTodos()`：並び替え・絞り込み・検索（表示用に欲しくなるやつ！）

### フォルダの置き方（イメージ）📁✨

* `src/core/`：ドメイン（Query/Commandの中心）
* `src/ui/`：表示やイベント（ここは今回触らない）
* `src/core/__tests__/`：coreのテスト（UIから独立✨）

---

## 5) まずは Query 実装例（テストしやすい形）🧩

### `src/core/todo.ts`

```ts
export type TodoStatus = "active" | "completed";

export type Todo = Readonly<{
  id: string;
  title: string;
  status: TodoStatus;
  createdAt: number; // epoch ms（Dateを持たないのがテスト楽💖）
}>;

export type TodoQuery = Readonly<{
  status?: TodoStatus | "all";
  search?: string;
  sort?: "createdAtAsc" | "createdAtDesc";
}>;

export function getTodos(all: ReadonlyArray<Todo>): ReadonlyArray<Todo> {
  // Query：読むだけ（引数をそのまま返してOKなケース）
  return all;
}

export function queryTodos(
  all: ReadonlyArray<Todo>,
  q: TodoQuery
): ReadonlyArray<Todo> {
  const status = q.status ?? "all";
  const search = (q.search ?? "").trim().toLowerCase();
  const sort = q.sort ?? "createdAtDesc";

  // ✅ “元配列を破壊しない”ためにコピーしてから操作
  let result = [...all];

  if (status !== "all") {
    result = result.filter(t => t.status === status);
  }

  if (search.length > 0) {
    result = result.filter(t => t.title.toLowerCase().includes(search));
  }

  result.sort((a, b) => {
    return sort === "createdAtAsc"
      ? a.createdAt - b.createdAt
      : b.createdAt - a.createdAt;
  });

  return result;
}
```

ポイントだよ〜👇🥰

* `ReadonlyArray` を受け取る → **破壊しない意識**が強制される💖
* `Date` を持たず `createdAt: number` にする → **テストが固定できる**🧊
* `sort()` は破壊的だから、必ず `[...]` でコピーしてから！⚠️

---

## 6) テストは「準備→実行→確認」だけ🧪✨

### `src/core/__tests__/todo.query.test.ts`

```ts
import { describe, it, expect } from "vitest";
import { queryTodos, type Todo } from "../todo";

function t(partial: Partial<Todo> & Pick<Todo, "id" | "title">): Todo {
  return {
    id: partial.id,
    title: partial.title,
    status: partial.status ?? "active",
    createdAt: partial.createdAt ?? 0
  };
}

describe("queryTodos", () => {
  it("completed だけを抽出できる✅", () => {
    // Arrange
    const all = [
      t({ id: "1", title: "buy milk", status: "active", createdAt: 100 }),
      t({ id: "2", title: "write report", status: "completed", createdAt: 200 }),
      t({ id: "3", title: "clean room", status: "completed", createdAt: 150 })
    ] as const;

    // Act
    const result = queryTodos(all, { status: "completed", sort: "createdAtAsc" });

    // Assert
    expect(result.map(x => x.id)).toEqual(["3", "2"]);
  });

  it("検索（大文字小文字関係なし）できる🔎", () => {
    const all = [
      t({ id: "1", title: "Read Book", createdAt: 1 }),
      t({ id: "2", title: "buy milk", createdAt: 2 }),
      t({ id: "3", title: "book hotel", createdAt: 3 })
    ] as const;

    const result = queryTodos(all, { search: "book", sort: "createdAtAsc" });

    expect(result.map(x => x.id)).toEqual(["1", "3"]);
  });

  it("元の配列を破壊しない（超大事）🧯", () => {
    const all = [
      t({ id: "1", title: "a", createdAt: 100 }),
      t({ id: "2", title: "b", createdAt: 200 }),
      t({ id: "3", title: "c", createdAt: 150 })
    ];

    const before = all.map(x => x.id); // 元の順番を保存
    queryTodos(all, { sort: "createdAtAsc" });
    const after = all.map(x => x.id);

    // sort() を直接 all にかけちゃうとここが壊れる💥
    expect(after).toEqual(before);
  });
});
```

この3本だけで、もう「Queryの気持ちよさ」かなり出るよ〜🥳✨

---

## 7) よくある “Queryのつもり副作用” 事故🚨😱（テストで見抜こう）

### 事故①：Queryの中で `Date.now()` を使う🕒💥

* 毎回結果が変わってテストが不安定に…😇
  対策：
* Queryには「今の時刻」を渡す（引数に `now` を入れる）か、Command側で決める✅

### 事故②：Queryの中で `Math.random()` 🎲💥

* 当然テスト不能😇
  対策：
* ランダムが必要なら「乱数生成」を外から渡す（依存を分離）🎁

### 事故③：Queryの中でログ送信・保存・通信📡💥

* Queryじゃなくなってる〜！😱
  対策：
* ログは Command の責務に寄せるか、呼び出し側の境界でやる📍

---

## 8) AIミニコーナー🤖✍️：テスト雛形を作ってもらうコツ

AIに丸投げじゃなくて「人間が設計者」でいこ〜🫶✨
おすすめプロンプト例👇

* 「`queryTodos` のテストケースを **境界値**込みで5つ提案して。期待結果も書いて」
* 「`queryTodos` が **入力配列を破壊しない**ことを検証するテストを書いて」
* 「`search` が空文字・スペースだけ・null相当のときの期待動作を決めてテストにして」
* 「`status=all` のときにフィルタしないことをテストして」

AIの出力チェックはこの3点だけ意識すると強いよ✅👀✨

* ✅ 期待結果が**仕様として筋が通ってる？**
* ✅ テストが**1つの理由でだけ落ちる**形になってる？
* ✅ “破壊的操作” や “時刻/乱数” みたいな**地雷**を踏んでない？

---

## 9) 演習（手を動かすやつ）💪🧪✨

1. `status: "all"` のとき、件数が変わらないテストを書こう📌
2. `search: "   "`（スペースだけ）のとき、検索しない仕様にする？どうする？決めてテストにしよう🤔💖
3. `sort: "createdAtDesc"` がデフォルトになってることをテストしよう⬇️
4. わざと `result = all; result.sort(...)` に書き換えて、**テストが落ちる**のを見よう（安全装置体験）🧯🔥

---

## 10) 今日のまとめ🌸✨

* Queryはテストが簡単＝「入力→出力」だけで済む🧪🥳
* いちばん怖いのは **“元配列を壊す”** 系（`sort()` とか）😱
* Queryが綺麗だと、テストも綺麗で、保守が楽で、将来の自分が助かる🫶💖
* AIは「雛形づくり係」にするとめっちゃ便利🤖✍️

---

補足：この章の内容は、現行のTypeScript安定版（ダウンロードページで “currently 5.9” と案内）と、Vitestの現行ドキュメント/リリース状況を参照して組み立てたよ📌 ([typescriptlang.org][3])

[1]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[2]: https://jestjs.io/versions?utm_source=chatgpt.com "Jest Versions"
[3]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
