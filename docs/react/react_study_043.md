# 第43章：配列と `map` によるリスト表示

データを配列Stateで持てるようになったら、次はそれを画面に表示したいですよね。
Reactでは、JavaScriptの **`map` メソッド** を使って、
「データの配列」を「JSX（コンポーネント）の配列」に変換して表示します 🔄

---

## 1. `map` でJSXを返す 🥞

`for` 文は使いません。JSXの中で `map` を使います。

```tsx
const fruits = ["りんご", "みかん", "バナナ"];

return (
  <ul>
    {fruits.map((fruit) => (
      <li>{fruit}</li>
    ))}
  </ul>
);
```

### 何が起きているの？ 👀

1. `fruits.map(...)` が配列の要素を1つずつ取り出します。
2. それぞれの要素 (`"りんご"`) を、JSX (`<li>りんご</li>`) に変換します。
3. 結果として `[<li>りんご</li>, <li>みかん</li>, ...]` という **JSXの配列** ができます。
4. ReactはJSXの配列を受け取ると、それを順番に展開してレンダリングしてくれます ✨

---

## 2. オブジェクトの配列を表示する 📇

実務でよくあるパターンです。
プロパティにアクセスして表示します。

```tsx
const users = [
  { id: 1, name: "Taro", age: 20 },
  { id: 2, name: "Hanako", age: 25 },
];

return (
  <div>
    {users.map((user) => (
      <div className="user-card" key={user.id}>
        <h3>{user.name}</h3>
        <p>{user.age}歳</p>
      </div>
    ))}
  </div>
);
```

ここで `key={user.id}` というのが出てきましたね。
これは次章で詳しくやりますが、**リスト表示には必ず `key` が必要** ということだけ覚えておいてください 🗝️

---

## 3. コンポーネントをループする 🧩

`<li>` などのHTMLタグだけでなく、自作コンポーネントもループできます。
これができると、一気にアプリっぽくなります！

```tsx
// UserCard コンポーネントがあるとして...
import { UserCard } from "./UserCard";

return (
  <div className="list-container">
    {users.map((user) => (
      <UserCard
        key={user.id}
        name={user.name}
        age={user.age}
      />
    ))}
  </div>
);
```

Propsとしてデータを渡してあげれば、同じコンポーネントをずらっと並べられます。
データの数だけカードが並ぶ、SNSのタイムラインみたいな画面もこれで作れます 📱

---

## 4. 条件付きで map する？ 🕵️‍♀️

「データがあるときだけリスト表示したい」ときは、`&&` を組み合わせます。

```tsx
return (
  <div>
    <h2>ユーザー一覧</h2>
    {users.length > 0 && (
      <ul>
        {users.map((user) => <li key={user.id}>{user.name}</li>)}
      </ul>
    )}
    
    {users.length === 0 && <p>ユーザーがいません 🍃</p>}
  </div>
);
```

配列が空のときに `map` してもエラーにはなりませんが（空の配列が返るだけ）、
「データなし」のメッセージを出したいときなどはこう書きます。

---

## 5. まとめ 🌟

* リスト表示には **`配列.map()`** を使う。
* `map` のコールバック関数の中で、**JSXを `return`** する。
* 自作コンポーネントもループで表示できる。
* リストの各要素には **一意な `key`** が必要（超重要！次章へ続く）。

`for`文や`forEach`ではなく、**「配列をJSXの配列に変換する」** という関数型プログラミング的な考え方に慣れていきましょう 🧠✨