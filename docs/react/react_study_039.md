# 第39章：複数入力の管理（オブジェクトState）

フォーム項目が増えてきたとき、
`useState` を「名前用」「メアド用」「年齢用」…とたくさん作っていませんか？ 😫

```tsx
// 😫 ちょっとつらいパターン
const [name, setName] = useState("");
const [email, setEmail] = useState("");
const [age, setAge] = useState("");
```

これでも動きますが、項目が10個あったら大変です。
こういうときは **「オブジェクトでまとめてState管理」** するとスッキリします ✨

---

## 1. オブジェクトでStateを作る 📦

まずは型を定義して、初期値をオブジェクトにします。

```tsx
type FormState = {
  name: string;
  email: string;
  age: string;
};

const [form, setForm] = useState<FormState>({
  name: "",
  email: "",
  age: "",
});
```

これで `form.name` や `form.email` で値にアクセスできるようになりました。

---

## 2. 更新関数の書き方（スプレッド構文） 🧈

オブジェクトStateを更新するときは **スプレッド構文 (`...`)** が必須です！
ReactのStateは「前の値を直接書き換えちゃダメ（イミュータブル）」というルールがあるからです。

```tsx
// ❌ ダメな例（直接書き換え）
form.name = "Taro"; // Reactが変更に気づかない！

// ⭕️ 良い例（新しいオブジェクトを作る）
setForm({
  ...form,       // 今の値を全部コピーして展開
  name: "Taro",  // name だけ上書き
});
```

`...form` で全部のプロパティをコピーして、変更したいプロパティだけ後ろに書いて上書きする。
このパターンはReactで死ぬほど使うので、指が覚えるまで練習しましょう 🎹

---

## 3. 汎用ハンドラーでさらにスッキリ ✨

項目ごとに `handleNameChange`, `handleEmailChange`... と作るのも面倒ですよね。
`<input>` に `name` 属性をつけて、**1つの関数で全項目を処理** しちゃいましょう！

```tsx
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const { name, value } = e.target;
  
  setForm((prev) => ({
    ...prev,
    [name]: value, // ✨ Computed Property Name
  }));
};

return (
  <form>
    <input name="name" value={form.name} onChange={handleChange} />
    <input name="email" value={form.email} onChange={handleChange} />
    <input name="age" value={form.age} onChange={handleChange} />
  </form>
);
```

### 🧙‍♂️ 解説

1. `<input name="email" ... />` のように、Stateのキーと同じ名前をつける。
2. `e.target.name` でその名前（"email"など）が取れる。
3. `[name]: value` という書き方（Computed Property Name）で、
   「変数 `name` に入ってる文字列をキーにして、値をセットする」ことができる。

これで項目が100個に増えても、ハンドラー関数はこれ1つでOKです！魔法みたいですね 🪄

---

## 4. ミニ練習：ユーザー登録フォーム 📝

実際に動くコードで試してみましょう。

```tsx
import { useState } from "react";

export const SignupForm = () => {
  const [user, setUser] = useState({
    username: "",
    password: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setUser((prev) => ({ ...prev, [name]: value }));
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px", maxWidth: "300px" }}>
      <label>
        ユーザーID:
        <input name="username" value={user.username} onChange={handleChange} />
      </label>
      <label>
        パスワード:
        <input type="password" name="password" value={user.password} onChange={handleChange} />
      </label>
      
      <p>入力中: {JSON.stringify(user)}</p>
    </div>
  );
};
```

`JSON.stringify(user)` で中身を表示してみると、
両方のフィールドがちゃんと更新されているのがわかります 👀

---

## 5. まとめ 🌟

* フォーム項目が多いときは **オブジェクト型のState** 1つにまとめる。
* 更新時は **スプレッド構文 (`...prev`)** を使って、前の値をコピーしつつ上書きする。
* `<input name="...">` を活用すれば、1つのハンドラー関数で全項目を制御できる（DRY原則！）。

次は、入力したデータを送信するための **`onSubmit`** イベントについて学びます。
これでフォーム機能が完結しますよ！ 🚀