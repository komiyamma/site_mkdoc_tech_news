# 第37章：フォーム入力の基本 (`onChange` と `value`)

Webアプリといえば「フォーム」ですよね！
検索ボックス、お問い合わせ、ログイン…すべてフォームです。
Reactにおけるフォーム操作の基本中の基本、**「入力された値をStateで管理する」** 方法（Controlled Component）をマスターしましょう 🥋

---

## 1. フォームの「値」は State で持つ 🤝

HTMLだけだと `<input>` は自分で勝手に値を持ちますが、Reactでは
**「入力欄の値（value）は State と同期させる」** のが鉄則です。

これを **制御されたコンポーネント (Controlled Component)** と呼びます。

イメージはこんな感じ：
1. ユーザーが文字を打つ ⌨️
2. `onChange` が動いて、State を更新する 🔄
3. 更新された State が `<input>` の `value` に戻ってくる 📺

「入力」→「State更新」→「表示」のサイクルを作ります。

---

## 2. 基本の書き方 ✍️

一番シンプルなテキストボックスを作ってみましょう。

```tsx
import { useState } from "react";

export const TextInput = () => {
  // 1. 入力値を管理する State
  const [text, setText] = useState("");

  // 2. 入力されたら State を更新する関数
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setText(e.target.value);
  };

  return (
    <div style={{ padding: "16px" }}>
      <label>
        名前：
        <input
          type="text"
          value={text}        // 3. State を value に紐付ける
          onChange={handleChange} // 4. 変更を検知する
        />
      </label>
      <p>こんにちは、{text} さん！</p>
    </div>
  );
};
```

### ポイント解説 💡

* **`value={text}`**
  これを書くことで、Reactが入力欄の中身を完全に支配します。
  State が空文字なら、入力欄も必ず空文字になります。

* **`onChange={handleChange}`**
  これがないと、キーボードを叩いても文字が入力されません（Stateが変わらない → valueも変わらないから）。
  `e.target.value` で「今入力された文字」を取得して、`setText` でStateを更新します。

---

## 3. `value` を指定しないとどうなる？ 🤔

もし `value={text}` を書かずに `onChange` だけ書いた場合、これを **非制御コンポーネント (Uncontrolled Component)** と呼びます。
単純なフォームならそれでも動きますが、
「送信ボタンを押したら入力を空にする」とか
「入力文字数に合わせてリアルタイムでエラーを出す」といった操作が難しくなります。

React では基本的に **`value` と `onChange` はセット** で使う、と覚えておけばOKです ✨

---

## 4. ミニ練習：文字数カウンターを作ろう 📏

入力した文字数をリアルタイムで表示する機能を作ってみましょう。
State で管理していれば、`.length` を見るだけで一瞬です！

```tsx
import { useState } from "react";

export const CharacterCounter = () => {
  const [text, setText] = useState("");

  return (
    <div style={{ padding: "16px" }}>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="ここに感想を書いてね"
        rows={4}
        style={{ width: "100%", padding: "8px" }}
      />
      <p style={{ textAlign: "right", color: text.length > 20 ? "red" : "black" }}>
        現在 {text.length} 文字 （20文字以内推奨）
      </p>
    </div>
  );
};
```

JSXの中で `{text.length}` と書くだけ。
DOMを直接操作して「文字数を数えて…」なんてしなくていいんです。これがReactのいいところ！🥳

---

## 5. まとめ 🌟

* 入力フォームの値は **State** で管理する（Controlled Component）。
* `<input>` には必ず **`value`** と **`onChange`** をセットで書く。
* `onChange` の中で `e.target.value` を取得して State を更新する。
* State にデータがあるので、文字数カウントやバリデーション（チェック）が簡単！

次は、この `onChange` で受け取るイベント `e` の型、
**`React.ChangeEvent`** について詳しく見ていきます 🕵️‍♀️