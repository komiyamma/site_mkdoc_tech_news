# 第14章：テスト② Commandは“副作用”を分離してテストする🧩🧪

この章は「**Commandってテストしにくい…😵‍💫**」を、ちゃんと攻略する回だよ〜！✨
（2026年1月時点だと TypeScript の最新は **5.9 系**だよ🧡 ([TypeScript][1]) / テストは **Vitest 4 系**が今どき感強め🧪 ([vitest.dev][2])）

---

## 1) この章のゴール🎯✨

できるようになることはこの3つ！💪💖

* Commandのテストが難しい理由を「副作用」で説明できる😇➡️😱
* **副作用を外に出す（分離）**＋**依存を外から渡す（DI）**ができる📦✨
* Vitestで「Commandの本体ロジック」を**軽く・速く・安定して**テストできる🧪⚡

---

## 2) Commandのテストが難しい理由😵‍💫（副作用のせい）

Commandってだいたいこういうのを触るよね👇

* DB/ファイル/localStorage を更新する💾
* API叩く🌐
* いまの時刻を見る🕒
* ランダムID作る🎲
* ログ送る📡

これ、テストでそのままやると…

* テストが遅い🐢
* 環境でコケる（PC/ネット/時間）💥
* 「たまに落ちる」最悪のやつが出る😇

だから作戦はこれ👇

> ✅ **副作用を「外」に追い出して、Commandの“判断”をテストする**🧠✨

---

## 3) 作戦：副作用を外へ追い出す3ステップ🚚✨

### ステップA：依存（DB/時計/ID生成）を「インターフェース化」する🧩

* **Commandは“どうしたいか”だけ知る**
* “どうやって保存するか”は知らなくてOK🙆‍♀️

### ステップB：依存を「引数で受け取る」＝DI📦✨

* `completeTodo(id, deps)` みたいにする
* テストでは `deps` をニセモノにできる🪄

### ステップC：テストは「ニセモノ依存」で回す🧪

* Fake（それっぽく動く）か
* Mock（呼ばれたか監視）を使う👀

---

## 4) 例題：ToDoの `completeTodo`（Command）をテスタブルにする📝💖

### 4.1 ドメイン（ToDoの型）🧸

```ts
// src/domain/todo.ts
export type TodoId = string;

export type Todo = {
  id: TodoId;
  title: string;
  completedAt: Date | null;
};
```

---

### 4.2 依存の“口”（Port）を作る🧩✨

```ts
// src/app/ports.ts
import type { Todo, TodoId } from "../domain/todo";

export interface TodoRepo {
  findById(id: TodoId): Promise<Todo | null>;
  save(todo: Todo): Promise<void>;
}

export interface Clock {
  now(): Date;
}
```

ここ大事〜！💡
Commandは **TodoRepo を「使う」だけ**で、DBとかlocalStorageの存在を知らない✌️✨
（これが “依存関係ルール” の入口になるよ🚪🧠）

---

### 4.3 Command本体（判断ロジック）🔧✨

「Commandは返していいもの／ダメなもの」ルールに合わせて、ここでは **最小の結果だけ**返すよ🎁（成功/失敗）

```ts
// src/app/commands/completeTodo.ts
import type { TodoId } from "../../domain/todo";
import type { Clock, TodoRepo } from "../ports";

export type CompleteTodoResult =
  | { ok: true }
  | { ok: false; reason: "NOT_FOUND" | "ALREADY_DONE" };

export async function completeTodo(
  id: TodoId,
  deps: { repo: TodoRepo; clock: Clock }
): Promise<CompleteTodoResult> {
  const todo = await deps.repo.findById(id);
  if (!todo) return { ok: false, reason: "NOT_FOUND" };
  if (todo.completedAt) return { ok: false, reason: "ALREADY_DONE" };

  const updated = { ...todo, completedAt: deps.clock.now() };
  await deps.repo.save(updated);

  return { ok: true };
}
```

ポイントはここ👇😍

* `Date()` 直呼びしない（clockに任せる）🕒
* 保存先を知らない（repoに任せる）💾
* 判断はこの関数で完結する🧠✨

---

### 4.4 本番側の“組み立て”（Composition Root）🧱✨

本番では「本物の repo と clock」を渡すだけ！

```ts
// src/main.ts (例)
import { completeTodo } from "./app/commands/completeTodo";
import type { Clock, TodoRepo } from "./app/ports";

const clock: Clock = { now: () => new Date() };

const repo: TodoRepo = {
  async findById(id) {
    // 本当はDB/localStorage/HTTPなど
    return null;
  },
  async save(todo) {
    // 本当はDB/localStorage/HTTPなど
  },
};

await completeTodo("todo-1", { repo, clock });
```

---

## 5) VitestでCommandをテストする🧪⚡

Vitestは “Viteベース”で速くて、Viteじゃなくても使えるよ〜って公式が言ってるやつ🧡 ([vitest.dev][3])
そして今は Vitest 4 が現行の大きな節目📌 ([vitest.dev][2])

### 5.1 インストール（最小）📦

```bash
npm i -D vitest
```

package.json はこんな感じ👇

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:run": "vitest run"
  }
}
```

---

### 5.2 テスト：Fake repo + 固定時計で安定化🕒🧪

```ts
// src/app/commands/completeTodo.spec.ts
import { describe, it, expect, vi } from "vitest";
import { completeTodo } from "./completeTodo";
import type { Todo } from "../../domain/todo";
import type { Clock, TodoRepo } from "../ports";

function makeFakeRepo(initial: Todo[]): {
  repo: TodoRepo;
  saved: Todo[];
} {
  const saved: Todo[] = [];
  const map = new Map(initial.map(t => [t.id, t]));

  return {
    saved,
    repo: {
      async findById(id) {
        return map.get(id) ?? null;
      },
      async save(todo) {
        map.set(todo.id, todo);
        saved.push(todo);
      },
    },
  };
}

describe("completeTodo (Command)", () => {
  it("未完了ToDoを完了にして保存する✅", async () => {
    const todo: Todo = { id: "1", title: "milk", completedAt: null };
    const fake = makeFakeRepo([todo]);

    const fixed = new Date("2026-01-20T12:00:00.000Z");
    const clock: Clock = { now: () => fixed };

    const result = await completeTodo("1", { repo: fake.repo, clock });

    expect(result).toEqual({ ok: true });
    expect(fake.saved).toHaveLength(1);
    expect(fake.saved[0].completedAt?.toISOString()).toBe(fixed.toISOString());
  });

  it("存在しないToDoは NOT_FOUND 😢", async () => {
    const fake = makeFakeRepo([]);

    const clock: Clock = { now: () => new Date("2026-01-20T12:00:00.000Z") };

    const result = await completeTodo("nope", { repo: fake.repo, clock });
    expect(result).toEqual({ ok: false, reason: "NOT_FOUND" });
    expect(fake.saved).toHaveLength(0);
  });

  it("すでに完了済みは ALREADY_DONE 🙅‍♀️", async () => {
    const todo: Todo = { id: "1", title: "milk", completedAt: new Date("2026-01-01T00:00:00.000Z") };
    const fake = makeFakeRepo([todo]);

    const clock: Clock = { now: () => new Date("2026-01-20T12:00:00.000Z") };

    const result = await completeTodo("1", { repo: fake.repo, clock });
    expect(result).toEqual({ ok: false, reason: "ALREADY_DONE" });
    expect(fake.saved).toHaveLength(0);
  });

  it("Mockで『saveが呼ばれた』だけ見る👀（例）", async () => {
    const todo: Todo = { id: "1", title: "milk", completedAt: null };

    const repo: TodoRepo = {
      findById: vi.fn(async () => todo),
      save: vi.fn(async () => {}),
    };

    const clock: Clock = { now: () => new Date("2026-01-20T12:00:00.000Z") };

    await completeTodo("1", { repo, clock });

    expect(repo.save).toHaveBeenCalledTimes(1);
  });
});
```

コツはこれだよ〜💡💖

* **固定時刻**にする（clock）→ “たまに落ちる”が消える🕒✨
* Fake repo で “保存された内容”までチェックできる💾👀
* Mock は「呼ばれたか」だけ見たいときに使う（使いすぎ注意）⚠️

---

## 6) 依存関係ルール（Dependency Rule）を超ざっくり🍩✨

ここでのルールはめちゃシンプルに言うと👇

* **内側（アプリのルール）は外側（DB/HTTP/UI）を知らない**🙅‍♀️
* だから内側は **インターフェース（Port）**だけを見る👀
* 外側がそれを実装して差し込む（DI）📦✨

これができると…

* テストで外側を丸ごと差し替えられる🪄
* Commandテストが「速い」「安定」「読みやすい」になる🥳🧪⚡

---

## 7) AIミニコーナー🤖🪄（Copilot/Codex向け）

そのまま投げてOKなやつ置いとくね💖

* 「`TodoRepo` の **Fake実装**を作って。保存履歴を配列で残して」🧸💾
* 「`completeTodo` の **境界値テスト**を追加して（NOT_FOUND / ALREADY_DONE / 正常系）」🎯🧪
* 「Mock と Fake の使い分けを、このテスト例で説明して」👀📚
* 「Commandで `Date()` を直呼びしない設計に直して。Clockを導入して」🕒✨

---

## 8) 演習（手を動かすやつ）🎮✨

### 演習A：`addTodo` を同じ流れで作ろう📝

* 依存：`IdGenerator` を追加（`nextId(): string`）🎲
* テスト：固定IDを返すFakeで安定化✨

### 演習B：副作用が増えた版（イベント通知）📣

* `EventBus`（`publish(event)`）を Port に追加
* テスト：publishが呼ばれたかをMockで確認👀

---

## 9) まとめチェックリスト✅💖

Commandテスト、これができてたら勝ち！🥳

* [ ] 時刻・乱数・外部IOを **直呼びしてない**（Clock/Id/Repoに寄せた）🕒🎲💾
* [ ] Commandは **判断が中心**で、依存は引数で受け取る（DI）📦
* [ ] テストは Fake/Mock で副作用を差し替えて **速い＆安定**🧪⚡
* [ ] Commandの戻り値は **最小の結果**（成功/失敗/IDくらい）🎁

---

次の章（第15章）は「実務の落とし所」まとめだよ〜🚀💖
もしよかったら、いまのToDo題材に **`addTodo` / `deleteTodo` / `renameTodo`** も同じ型で増やして、テストも一緒に整えていこっか？😆🧪✨

[1]: https://www.typescriptlang.org/download/?utm_source=chatgpt.com "How to set up TypeScript"
[2]: https://vitest.dev/blog/vitest-4?utm_source=chatgpt.com "Vitest 4.0 is out!"
[3]: https://vitest.dev/?utm_source=chatgpt.com "Vitest | Next Generation testing framework"
