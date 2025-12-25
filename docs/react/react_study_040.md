# 第40章：フォーム送信 (`onSubmit`)

入力フォームを作ったら、最後に「送信」ボタンを押してデータを送りたいですよね。
Reactでは、`<button onClick>` ではなく、**`<form onSubmit>`** を使うのが作法です 🍵

--- 

## 1. なぜ `<form onSubmit>` なのか？ 🤔

`<button onClick={send}>送信</button>` でも動きそうですが、
`<form>` タグで囲って `onSubmit` を使うと、こんなイイことがあります：

1. **Enterキーで送信できる** ⌨️
   いちいちマウスでボタンを押さなくても、入力中にEnterを押せば送信されます。UX（ユーザー体験）的に超重要！
2. **スマホのキーボード対応** 📱
   スマホのソフトウェアキーボードの「実行」や「Go」ボタンが効くようになります。
3. **HTML標準の動作** 🌐
   アクセシビリティ（スクリーンリーダーなど）の観点からも正しい構造になります。

--- 

## 2. `e.preventDefault()` を忘れずに！ 🛑

HTMLの標準動作では、フォームを送信すると **ページがリロード（再読み込み）** されてしまいます。
ReactのようなSPA（シングルページアプリ）では、リロードされるとStateが全部消えてしまうので困ります。

なので、`onSubmit` ハンドラーの **1行目** には必ずこれを書きます：

```tsx
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault(); // 👈 これ！！ デフォルトのリロード動作を止める
  
  // ここから送信処理を書く
  console.log("送信データ:", formData);
};
```

型は **`React.FormEvent<HTMLFormElement>`** です。
これも覚えておきましょう 📝

--- 

## 3. 実践コード：送信機能付きフォーム 📨

前章のオブジェクトStateと組み合わせて、完成形のフォームを作ってみます。

```tsx
import { useState } from "react";

export const LoginForm = () => {
  const [form, setForm] = useState({ email: "", password: "" });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // リロード阻止！
    alert(`送信しました！\nEmail: ${form.email}`);
    // ここでAPIを叩いたりする
  };

  return (
    <form onSubmit={handleSubmit} style={{ padding: "16px", border: "1px solid #ccc" }}>
      <h2>ログイン</h2>
      <div>
        <label>Email: </label>
        <input name="email" value={form.email} onChange={handleChange} />
      </div>
      <div>
        <label>Pass: </label>
        <input type="password" name="password" value={form.password} onChange={handleChange} />
      </div>
      
      {/* type="submit" にするのがポイント */}
      <button type="submit" style={{ marginTop: "12px" }}>ログイン</button>
    </form>
  );
};
```

### ポイント 💡

* **`<form onSubmit={...}>`**: フォーム全体を包むタグにイベントを設定。
* **`<button type="submit">`**: ボタンには `type="submit"` を明示する（省略してもデフォルトはsubmitですが、書く癖をつけると安全）。
* **`e.preventDefault()`**: これがないと一瞬でページがリロードされて、alertも見えないまま終わります 👻

--- 

## 4. 送信中にボタンを無効化する ⏳

よくある「送信中…」ボタンも、Stateを使えば簡単です。

```tsx
const [isSubmitting, setIsSubmitting] = useState(false);

const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  setIsSubmitting(true); // ロックする 🔒

  // 擬似的に2秒待つ
  await new Promise(r => setTimeout(r, 2000));
  
  alert("完了！");
  setIsSubmitting(false); // 解除する 🔓
};

// ...
<button type="submit" disabled={isSubmitting}>
  {isSubmitting ? "送信中..." : "送信"}
</button>
```

これで「連打されて何回も送信されちゃう」事故を防げます 🛡️

--- 

## 5. まとめ 🌟

* 送信処理はボタンのonClickではなく、**`<form>` の `onSubmit`** で扱う。
* ハンドラーの冒頭で必ず **`e.preventDefault()`** を呼んでリロードを防ぐ。
* イベント型は **`React.FormEvent<HTMLFormElement>`**。
* `isSubmitting` などのStateでローディング表示をすると親切 💕

これでフォーム関連の基礎はバッチリです！
次は、TODOリストなどで必須の **「配列のState操作」** に進みます。
データの追加・削除・更新…Reactらしいデータの扱い方を学びましょう 🥪