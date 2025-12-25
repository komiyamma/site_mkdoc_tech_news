# 第36章：イベントオブジェクトの型 (`React.MouseEvent`)

ボタンを押したとき、入力したとき…Reactでは「イベント」が発生します。
このとき、関数の引数として受け取れる `e` (イベントオブジェクト) に、TypeScriptでどうやって型を付けるか？
これがわかると、エディタの補完がバリバリ効くようになって開発が超快適になります ✨

---

## 1. 「イベントオブジェクト」ってなんだっけ？ 🤔

クリック時の関数をこう書くことがありますよね👇

```tsx
const handleClick = (e) => {
  console.log(e); // ← これ！
  console.log(e.clientX, e.clientY); // クリックした座標とかが入ってる
};
```

この `e` には、
「どのボタンが押されたか」「画面のどこをクリックしたか」「Shiftキーは押されていたか」
などの情報が詰まっています。

でも、TypeScriptだと `e` に型がないと
`Parameter 'e' implicitly has an 'any' type.`（`any`型になっちゃってるよ！）
と怒られます 😡

そこで登場するのが **Reactが用意してくれているイベントの型** です。

---

## 2. クリックイベントの型：`React.MouseEvent` 🖱️

ボタンやdivをクリックしたときのイベント型は **`React.MouseEvent<T>`** です。
ジェネリクス `<T>` には、「クリックされた要素の型」を入れます。

### ✅ 基本の書き方

```tsx
import React from "react"; // 型を使うときは import があると安心

const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  console.log("クリック座標:", e.clientX, e.clientY);
  // e.preventDefault(); // これも補完が出るようになる✨
};

return <button onClick={handleClick}>座標を表示</button>;
```

* `React.MouseEvent`
  → 「マウスのイベントですよ」という意味
* `<HTMLButtonElement>`
  → 「`<button>` 要素で発生したイベントですよ」という意味

こう書くと、`e.` と打った瞬間に `clientX` や `preventDefault` などの候補がズラッと出てきます。これが気持ちいい！😍

---

## 3. よく使う要素の型 📝

ジェネリクス `<...>` の中に入れる要素の型は、HTMLタグに対応しています。
VS Codeなら、タグの上にマウスを乗せるとヒントが出ることもありますが、代表的なものを覚えておくと早いです。

| HTMLタグ | TypeScriptの型 |
| :--- | :--- |
| `<button>` | `HTMLButtonElement` |
| `<div>` | `HTMLDivElement` |
| `<a>` | `HTMLAnchorElement` |
| `<input>` | `HTMLInputElement` |
| `<form>` | `HTMLFormElement` |

だいたい **`HTML` + `(タグ名の大文字)` + `Element`** というルールになっています 💡

---

## 4. `input` の変更イベント型は？（予告）

次章以降で詳しくやりますが、入力フォームの `onChange` などでは
**`React.ChangeEvent<HTMLInputElement>`**
を使います。

```tsx
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  console.log(e.target.value); // 入力された文字
};
```

「マウス操作」なら `MouseEvent`、「値の変更」なら `ChangeEvent`。
名前が直感的なので覚えやすいですね ✨

---

## 5. ミニ練習：座標を表示するボックスを作ろう 📦

クリックした位置を表示する、簡単なボックスを作ってみましょう。

```tsx
import { useState } from "react";

export const ClickBox = () => {
  const [coords, setCoords] = useState({ x: 0, y: 0 });

  // 1. ここでしっかり型を定義！
  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // 2. clientX, clientY が補完で出るか確認してみてね👀
    setCoords({
      x: e.clientX,
      y: e.clientY,
    });
  };

  return (
    <div
      onClick={handleClick}
      style={{
        width: "200px",
        height: "200px",
        background: "#e0f7fa",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        cursor: "pointer",
        userSelect: "none"
      }}
    >
      x: {coords.x}, y: {coords.y}
    </div>
  );
};
```

---

## 6. まとめ 🌟

* イベント引数 `e` には型をつけよう。
* クリックイベントなら **`React.MouseEvent<HTMLButtonElement>`** が基本。
* タグに合わせて `<HTMLDivElement>` などを使い分ける。
* 型をつけると、`e.preventDefault()` や `e.currentTarget` などの補完が効いて開発がサクサク進む！🚀

次は、この知識を使って **フォーム入力（`onChange`）** を攻略していきます！
ユーザーからの入力を受け取る、Webアプリ開発の要（かなめ）です 💪