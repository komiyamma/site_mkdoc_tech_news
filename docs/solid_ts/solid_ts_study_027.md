# 第27章：卒業制作② 実装＆テスト（SOLIDを当てながら作る）🛠️✅✨

この章は「作りながらSOLIDを体に入れる回」だよ〜☺️🧡
第26章で作った “土台” に、機能を足していきます🌱


![Construction Site](./picture/solid_ts_study_027_impl_construction.png)

---

## この章のゴール 🎯✨

* **注文→合計→保存→通知** が一通り動く📦➡️💰➡️💾➡️🔔
* 追加機能（例：学割、PayPay、通知追加）を入れても、コードが崩れにくい🧱✨
* テストが “守り神” になって、リファクタが怖くなくなる🛡️✅

---

## 2026/01/10時点の「最新ど真ん中」メモ 🧠📌✨

* TypeScript は **5.9 系**（公式リリースノートが 2026/01/07 更新） ([TypeScript][1])
* Node.js の Latest LTS は **v24.12.0**（公式トップに表示） ([Node.js][2])
* テストは **Vitest 4 系**（公式ブログで 4.0 公開、ページ上部に 4.0.16 など表示） ([vitest.dev][3])

> バージョンは日々進むけど、「この章の設計と考え方」はそのまま使い回せるよ😊💪

---

## 今日の題材（例）☕️📦

「Campus Café 注文アプリ（超ミニ）」として、

* 商品をカートに入れる🛒
* 割引（学割など）を適用する🎟️
* 支払い方法を選ぶ💳📱
* 注文を保存する💾
* 通知する🔔

…を作るよ〜！

---

# 1) まず “完成の形” を置こう 🏁✨（先にゴールを見せる）

### 章末でこういう `main.ts` が書けるのが理想👇😊

```ts
// src/main.ts
import { PlaceOrderUseCase } from "./app/usecases/PlaceOrderUseCase.js";
import { InMemoryOrderRepository } from "./infra/repositories/InMemoryOrderRepository.js";
import { ConsoleNotifier } from "./infra/notifiers/ConsoleNotifier.js";
import { StudentDiscountPolicy } from "./domain/discount/StudentDiscountPolicy.js";
import { CashPayment } from "./domain/payment/CashPayment.js";
import { Money } from "./domain/value/Money.js";
import { OrderRequest } from "./app/dto/OrderRequest.js";

const orderRepo = new InMemoryOrderRepository();
const notifier = new ConsoleNotifier();

const useCase = new PlaceOrderUseCase({
  orderRepository: orderRepo,
  notifier,
});

const req: OrderRequest = {
  customerId: "u-001",
  items: [
    { productId: "coffee", name: "カフェラテ", unitPriceYen: 480, quantity: 2 },
    { productId: "sandwich", name: "サンド", unitPriceYen: 550, quantity: 1 },
  ],
  discountPolicy: new StudentDiscountPolicy(),
  paymentMethod: new CashPayment(),
};

const result = await useCase.execute(req);

console.log("注文できた？", result.ok);
if (result.ok) {
  console.log("合計:", result.value.total.toString());
} else {
  console.error("失敗:", result.error.message);
}
```

この “呼び出し側がスッキリしてる感じ” が、SOLIDが効いてるサインだよ🌈✨

---

# 2) ドメイン：まず Money（お金）を最強にする 💴🛡️

お金は **浮動小数点で事故りやすい** から、Value Object にしちゃうのが鉄板！😇

```ts
// src/domain/value/Money.ts
export class Money {
  private constructor(private readonly yen: number) {
    if (!Number.isInteger(yen)) throw new Error("Moneyは整数（円）で持ってね🥺");
    if (yen < 0) throw new Error("Moneyがマイナスはダメだよ🥺");
  }

  static yen(value: number): Money {
    return new Money(value);
  }

  add(other: Money): Money {
    return new Money(this.yen + other.yen);
  }

  multiply(n: number): Money {
    if (!Number.isInteger(n)) throw new Error("multiplyは整数でね🥺");
    if (n < 0) throw new Error("multiplyでマイナスはダメだよ🥺");
    return new Money(this.yen * n);
  }

  min(other: Money): Money {
    return this.yen <= other.yen ? this : other;
  }

  toNumber(): number {
    return this.yen;
  }

  toString(): string {
    return `${this.yen}円`;
  }
}
```

🎀 **SOLID的にどこが良い？**

* どこでも `number` で金額を持たない → **バグの入口を封鎖** 🔒✨
* 計算ルールがここに集まる → SRP的にもスッキリ✂️

---

# 3) ドメイン：注文モデルを作る 📦✨

```ts
// src/domain/order/LineItem.ts
import { Money } from "../value/Money.js";

export type LineItem = {
  productId: string;
  name: string;
  unitPrice: Money;
  quantity: number;
};
```

```ts
// src/domain/order/Order.ts
import { Money } from "../value/Money.js";
import { LineItem } from "./LineItem.js";

export class Order {
  constructor(
    public readonly id: string,
    public readonly customerId: string,
    public readonly items: LineItem[],
    public readonly total: Money
  ) {}
}
```

---

# 4) OCP：割引を Strategy で “追加し放題” にする 🎟️🧠✨

## 4-1. まず差し替え口（interface）を作る 🚪✨

```ts
// src/domain/discount/DiscountPolicy.ts
import { Money } from "../value/Money.js";

export interface DiscountPolicy {
  readonly name: string;
  apply(subtotal: Money): Money; // 返すのは「割引後の金額」だよ😊
}
```

## 4-2. 何もしない割引（デフォルト）🌿

```ts
// src/domain/discount/NoDiscountPolicy.ts
import { DiscountPolicy } from "./DiscountPolicy.js";
import { Money } from "../value/Money.js";

export class NoDiscountPolicy implements DiscountPolicy {
  readonly name = "割引なし";
  apply(subtotal: Money): Money {
    return subtotal;
  }
}
```

## 4-3. 学割（例：10%OFF）🎓✨

```ts
// src/domain/discount/StudentDiscountPolicy.ts
import { DiscountPolicy } from "./DiscountPolicy.js";
import { Money } from "../value/Money.js";

export class StudentDiscountPolicy implements DiscountPolicy {
  readonly name = "学割10%";

  apply(subtotal: Money): Money {
    const discounted = Math.floor(subtotal.toNumber() * 0.9);
    return Money.yen(discounted);
  }
}
```

🎯 **OCPポイント**
割引を追加したい？ → `DiscountPolicy` を実装したクラスを **増やすだけ** 🎉
既存の計算ロジックは **なるべく触らない** ✨

---

# 5) SRP：合計計算は “計算だけ” にする 💰🧾✨

```ts
// src/domain/pricing/PriceCalculator.ts
import { Money } from "../value/Money.js";
import { LineItem } from "../order/LineItem.js";
import { DiscountPolicy } from "../discount/DiscountPolicy.js";

export class PriceCalculator {
  calcSubtotal(items: LineItem[]): Money {
    return items.reduce((sum, item) => {
      const line = item.unitPrice.multiply(item.quantity);
      return sum.add(line);
    }, Money.yen(0));
  }

  calcTotal(items: LineItem[], discountPolicy: DiscountPolicy): Money {
    const subtotal = this.calcSubtotal(items);
    const discounted = discountPolicy.apply(subtotal);
    return discounted;
  }
}
```

💡ここで **保存** とか **通知** を混ぜないのが SRP のコツだよ✂️✨

---

# 6) OCP：支払いも差し替え可能にする 💳📱✨

```ts
// src/domain/payment/PaymentMethod.ts
import { Money } from "../value/Money.js";

export type PaymentResult =
  | { ok: true; transactionId: string }
  | { ok: false; reason: string };

export interface PaymentMethod {
  readonly name: string;
  pay(amount: Money): Promise<PaymentResult>;
}
```

```ts
// src/domain/payment/CashPayment.ts
import { Money } from "../value/Money.js";
import { PaymentMethod, PaymentResult } from "./PaymentMethod.js";

export class CashPayment implements PaymentMethod {
  readonly name = "現金";

  async pay(amount: Money): Promise<PaymentResult> {
    // 現金は外部連携なし想定で即OKにしちゃう😌
    return { ok: true, transactionId: `cash-${Date.now()}` };
  }
}
```

> 追加：PayPay でもクレカでも、ここに “実装を足すだけ” で済む形にしておくと楽ちん🎉

---

# 7) ISP：Repository と Notifier を “薄く” する 🧻✨

## 7-1. 注文保存（Repository）💾

```ts
// src/app/ports/OrderRepository.ts
import { Order } from "../../domain/order/Order.js";

export interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: string): Promise<Order | null>;
}
```

```ts
// src/infra/repositories/InMemoryOrderRepository.ts
import { OrderRepository } from "../../app/ports/OrderRepository.js";
import { Order } from "../../domain/order/Order.js";

export class InMemoryOrderRepository implements OrderRepository {
  private readonly store = new Map<string, Order>();

  async save(order: Order): Promise<void> {
    this.store.set(order.id, order);
  }

  async findById(id: string): Promise<Order | null> {
    return this.store.get(id) ?? null;
  }
}
```

## 7-2. 通知（Notifier）🔔

```ts
// src/app/ports/Notifier.ts
import { Order } from "../../domain/order/Order.js";

export interface Notifier {
  notifyOrderPlaced(order: Order): Promise<void>;
}
```

```ts
// src/infra/notifiers/ConsoleNotifier.ts
import { Notifier } from "../../app/ports/Notifier.js";
import { Order } from "../../domain/order/Order.js";

export class ConsoleNotifier implements Notifier {
  async notifyOrderPlaced(order: Order): Promise<void> {
    console.log(`🔔 注文完了！ id=${order.id} total=${order.total.toString()}`);
  }
}
```

---

# 8) DIP/DI：ユースケース（アプリ層）が “詳細” に依存しないようにする 💉🤖✨

ユースケースは **重要ロジックの中心** だから、
DB や通知サービスみたいな詳細に振り回されないようにするよ🙅‍♀️✨

## 8-1. DTO（入力）📩

```ts
// src/app/dto/OrderRequest.ts
import { DiscountPolicy } from "../../domain/discount/DiscountPolicy.js";
import { PaymentMethod } from "../../domain/payment/PaymentMethod.js";

export type OrderRequest = {
  customerId: string;
  items: Array<{
    productId: string;
    name: string;
    unitPriceYen: number;
    quantity: number;
  }>;
  discountPolicy: DiscountPolicy;
  paymentMethod: PaymentMethod;
};
```

## 8-2. 結果型（成功/失敗）🎭

```ts
// src/app/shared/Result.ts
export type Result<T> = { ok: true; value: T } | { ok: false; error: Error };

export const ok = <T>(value: T): Result<T> => ({ ok: true, value });
export const fail = (error: Error): Result<never> => ({ ok: false, error });
```

## 8-3. UseCase 本体 💪

```ts
// src/app/usecases/PlaceOrderUseCase.ts
import { OrderRepository } from "../ports/OrderRepository.js";
import { Notifier } from "../ports/Notifier.js";
import { OrderRequest } from "../dto/OrderRequest.js";
import { Result, ok, fail } from "../shared/Result.js";
import { Money } from "../../domain/value/Money.js";
import { LineItem } from "../../domain/order/LineItem.js";
import { PriceCalculator } from "../../domain/pricing/PriceCalculator.js";
import { Order } from "../../domain/order/Order.js";

type Deps = {
  orderRepository: OrderRepository;
  notifier: Notifier;
};

export class PlaceOrderUseCase {
  private readonly priceCalc = new PriceCalculator();

  constructor(private readonly deps: Deps) {}

  async execute(req: OrderRequest): Promise<Result<Order>> {
    try {
      const items: LineItem[] = req.items.map((i) => ({
        productId: i.productId,
        name: i.name,
        unitPrice: Money.yen(i.unitPriceYen),
        quantity: i.quantity,
      }));

      const total = this.priceCalc.calcTotal(items, req.discountPolicy);

      const payResult = await req.paymentMethod.pay(total);
      if (!payResult.ok) {
        return fail(new Error(`支払い失敗: ${payResult.reason}`));
      }

      const order = new Order(
        `ord-${Date.now()}`,
        req.customerId,
        items,
        total
      );

      await this.deps.orderRepository.save(order);
      await this.deps.notifier.notifyOrderPlaced(order);

      return ok(order);
    } catch (e) {
      return fail(e instanceof Error ? e : new Error("未知のエラー🥺"));
    }
  }
}
```

✨ここが超大事：

* `PlaceOrderUseCase` は **InMemory** とか **Console** を知らない🙈
* 知ってるのは `OrderRepository` と `Notifier` だけ（＝抽象）🧠
  → DIP できてる〜！🎉

---

# 9) テスト：Vitest で “壊れない成長” を作る ✅🧪✨

## 9-1. まずテストの狙いを決める 🎯

この章でのテストは主に3種類だよ😊

1. **割引のテスト**（OCPで増える場所）🎟️✅
2. **ユースケースのテスト**（依存差し替えでDIP確認）💉✅
3. **契約（Contract）テスト**（LSPっぽく「差し替えても同じ約束」）🧩✅

---

## 9-2. 割引の単体テスト 🎟️🧪

```ts
// test/discount/StudentDiscountPolicy.test.ts
import { describe, it, expect } from "vitest";
import { Money } from "../../src/domain/value/Money.js";
import { StudentDiscountPolicy } from "../../src/domain/discount/StudentDiscountPolicy.js";

describe("StudentDiscountPolicy", () => {
  it("10%引きになる", () => {
    const p = new StudentDiscountPolicy();
    const subtotal = Money.yen(1000);

    const total = p.apply(subtotal);

    expect(total.toNumber()).toBe(900);
  });
});
```

---

## 9-3. LSPっぽい！割引の “共通テスト（契約テスト）” 🧩🛡️✨

「DiscountPolicy はこう振る舞うべし」っていう約束を、全部の割引に適用するよ😊

```ts
// test/discount/discountPolicy.contract.ts
import { describe, it, expect } from "vitest";
import { Money } from "../../src/domain/value/Money.js";
import { DiscountPolicy } from "../../src/domain/discount/DiscountPolicy.js";

export const discountPolicyContract = (factory: () => DiscountPolicy) => {
  describe(`DiscountPolicy contract: ${factory().name}`, () => {
    it("0円を入れたら0円のまま", () => {
      const p = factory();
      expect(p.apply(Money.yen(0)).toNumber()).toBe(0);
    });

    it("割引後の金額はマイナスにならない", () => {
      const p = factory();
      expect(p.apply(Money.yen(100)).toNumber()).toBeGreaterThanOrEqual(0);
    });

    it("割引後の金額は小計を超えない（無料化はOKだけど増額はNG）", () => {
      const p = factory();
      expect(p.apply(Money.yen(1000)).toNumber()).toBeLessThanOrEqual(1000);
    });
  });
};
```

```ts
// test/discount/DiscountPolicies.contract.test.ts
import { discountPolicyContract } from "./discountPolicy.contract.js";
import { NoDiscountPolicy } from "../../src/domain/discount/NoDiscountPolicy.js";
import { StudentDiscountPolicy } from "../../src/domain/discount/StudentDiscountPolicy.js";

discountPolicyContract(() => new NoDiscountPolicy());
discountPolicyContract(() => new StudentDiscountPolicy());
```

✅ これで「新しい割引を追加したのに、挙動がヤバい😵」がすぐ見つかる！

---

## 9-4. ユースケースのテスト（DIの強さを体験）💉✨

`OrderRepository` と `Notifier` を **偽物（Fake/Spy）** にして、
“ユースケースだけ” を検査するよ🧪🔍

```ts
// test/usecases/PlaceOrderUseCase.test.ts
import { describe, it, expect } from "vitest";
import { PlaceOrderUseCase } from "../../src/app/usecases/PlaceOrderUseCase.js";
import { OrderRepository } from "../../src/app/ports/OrderRepository.js";
import { Notifier } from "../../src/app/ports/Notifier.js";
import { NoDiscountPolicy } from "../../src/domain/discount/NoDiscountPolicy.js";
import { CashPayment } from "../../src/domain/payment/CashPayment.js";

class RepoSpy implements OrderRepository {
  savedCount = 0;
  lastId: string | null = null;

  async save(order: any): Promise<void> {
    this.savedCount++;
    this.lastId = order.id;
  }
  async findById(): Promise<any> {
    return null;
  }
}

class NotifierSpy implements Notifier {
  notifiedCount = 0;
  async notifyOrderPlaced(): Promise<void> {
    this.notifiedCount++;
  }
}

describe("PlaceOrderUseCase", () => {
  it("注文できたら保存と通知が走る", async () => {
    const repo = new RepoSpy();
    const notifier = new NotifierSpy();
    const uc = new PlaceOrderUseCase({ orderRepository: repo, notifier });

    const res = await uc.execute({
      customerId: "u-001",
      items: [{ productId: "coffee", name: "カフェラテ", unitPriceYen: 500, quantity: 1 }],
      discountPolicy: new NoDiscountPolicy(),
      paymentMethod: new CashPayment(),
    });

    expect(res.ok).toBe(true);
    expect(repo.savedCount).toBe(1);
    expect(notifier.notifiedCount).toBe(1);
  });
});
```

ここ、超気持ちいいポイント🥹🧡

* DBも外部通知も使ってないのに、ユースケースの正しさが確認できる✨
* つまり **テストが速い** → 速いテストは正義👑

---

# 10) “追加機能” を1個入れよう 🎉✨（OCPの成果を味わう）

例：**雨の日割（-50円）☔️** を追加してみよう！

```ts
// src/domain/discount/RainyDayDiscountPolicy.ts
import { DiscountPolicy } from "./DiscountPolicy.js";
import { Money } from "../value/Money.js";

export class RainyDayDiscountPolicy implements DiscountPolicy {
  readonly name = "雨の日割-50円";

  apply(subtotal: Money): Money {
    const after = Math.max(0, subtotal.toNumber() - 50);
    return Money.yen(after);
  }
}
```

追加したら、契約テストに1行足すだけ！

```ts
// test/discount/DiscountPolicies.contract.test.ts
import { RainyDayDiscountPolicy } from "../../src/domain/discount/RainyDayDiscountPolicy.js";
// ...
discountPolicyContract(() => new RainyDayDiscountPolicy());
```

🎉 これだけで「割引が増えても地獄にならない」世界に近づくよ〜！

---

# 11) よくある “崩れポイント” と対処 💥🩹

* **ユースケースが太る**（計算・保存・通知・ログ・例外…全部入り）
  → 「それ、別クラスに出せない？」で SRP に戻す✂️✨

* **interface が巨大化**（Notifierに10メソッドとか）
  → “用途別に薄く” で ISP✂️🧻✨

* **割引を追加するたびに if/switch が増える**
  → Strategy に逃がす（OCP）🎟️🔁✨

* **テストが書きにくい**
  → 依存が注入できてないサインかも（DIP/DI）💉🥺

---

# 12) AI活用（Copilot/Codex）で爆速にするコツ 🤖⚡️

## 使えるお願いの型（そのままコピペOK）📝✨

* 「この interface を満たす実装を作って」
  👉 *“`DiscountPolicy` を満たす `RainyDayDiscountPolicy` を作って。金額は `Money` を使って。0未満禁止。”*

* 「契約テストを書いて」
  👉 *“`DiscountPolicy` 実装に共通で守らせたいテストを Vitest で書いて。0円、マイナス禁止、増額禁止。”*

* 「差分レビューして」
  👉 *“この変更でSOLIDが崩れてない？SRP/OCP/ISP/DIPの観点で危ない所だけ指摘して。”* 🔍✨

---

# 章末チェックリスト ✅🌸

* [ ] 注文→合計→保存→通知 が動く 📦💰💾🔔
* [ ] 割引を1つ追加しても、既存コードの修正が最小 🎟️✨
* [ ] 割引の契約テストがあり、新割引を追加したら同じテストが走る 🧩✅
* [ ] ユースケースのテストで Repo/Notifier を差し替えできる 💉✅
* [ ] “責務が混ざりそう” になったら分ける癖がついた ✂️😊

---

## 提出物（この章で残すもの）🎁✨

* 動く `main.ts`（注文が通る）🛠️
* テスト数本（割引、ユースケース、契約テスト）🧪
* 追加機能1つ（学割/雨割/PayPay/通知追加…どれでもOK）🎉

---

必要なら、ここから先は「あなたの卒業制作の仕様（第26章で作ったユーザーストーリー）」に合わせて、**クラス構成とテスト設計を完全カスタム**して一緒に組み直せるよ😊🧡
（例：通知を Email/SMS/アプリに分ける、Repository をファイル保存にする、支払いをAPIっぽくする…とかも楽しい✨）

[1]: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html "TypeScript: Documentation - TypeScript 5.9"
[2]: https://nodejs.org/en "Node.js — Run JavaScript Everywhere"
[3]: https://vitest.dev/blog/vitest-4 "Vitest 4.0 is out! | Vitest"
