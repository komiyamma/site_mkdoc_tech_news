# 第38章：フォーム入力の型 (`React.ChangeEvent`)

前章で `<input>` の扱い方をやりましたが、TypeScript で書くときに一番つまづくのが
「`onChange` の `e` ってなんて型？」問題です 🤯

ここでは **`React.ChangeEvent`** をしっかり使いこなして、
型安全なフォームマスターになりましょう ✨

---

## 1. 基本の型：`React.ChangeEvent<HTMLInputElement>` 🔒

テキストボックス (`<input type="text" />`) の場合、これが正解です。

```tsx
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  setText(e.target.value);
};
```

* **`ChangeEvent`**: 「値が変わったとき」のイベント型
* **`<HTMLInputElement>`**: 「input要素」で起きたよ、という指定

これを指定しておくと、
`e.target.` と打ったあとに `value` や `checked`、`type` などの候補が正しく表示されます。
逆に `e.target.hoge` みたいな存在しないプロパティにはエラーを出してくれます 🛡️

---

## 2. `<textarea>` や `<select>` の場合は？ 🤔

タグによって、ジェネリクスの中身 `<...>` を少し変えます。

| タグ | TypeScriptの型 |
| :--- | :--- |
| `<input>` | `React.ChangeEvent<HTMLInputElement>` |
| `<textarea>` | `React.ChangeEvent<HTMLTextAreaElement>` |
| `<select>` | `React.ChangeEvent<HTMLSelectElement>` |

覚え方は簡単。**`HTML` + (タグ名の大文字) + `Element`** です！

### 📝 selectボックスの例

```tsx
const handleSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
  setPrefecture(e.target.value);
};

// ...
<select value={prefecture} onChange={handleSelect}>
  <option value="tokyo">東京都</option>
  <option value="osaka">大阪府</option>
</select>
```

---

## 3. 汎用的なハンドラーを作りたいときは？ 🧪

「input も textarea も、同じ関数で処理したいな〜」ってこと、ありますよね。
そういうときは **ユニオン型**（`|`）を使います。

```tsx
const handleAnyChange = (
  e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
) => {
  setInputVal(e.target.value);
};
```

これで、`<input>` でも `<textarea>` でも使える便利なハンドラーになります。
ただし、`input` にしかない属性（例：`checked`）を使おうとすると、「textareaにはないよ！」と怒られることがあるので注意です ⚠️

---

## 4. インラインで書くなら型推論におまかせ 🚀

関数を外に切り出さず、`onChange` の中に直接アロー関数を書く場合、
**TypeScriptが勝手に型を推論してくれる** ので、型を書く必要はありません。

```tsx
<input
  type="text"
  value={text}
  onChange={(e) => setText(e.target.value)} // ← ここで e の型を書かなくてもOK！
/>
```

VS Code で `e` にマウスを乗せてみてください。
ちゃんと `React.ChangeEvent<HTMLInputElement>` と表示されるはずです 👀
小さなコンポーネントなら、これで済ませちゃうのも手です 👍

---

## 5. まとめ 🌟

* フォームの変更イベント型は **`React.ChangeEvent<T>`**。
* `<T>` には **`HTMLInputElement`** や **`HTMLTextAreaElement`** などを入れる。
* インライン関数 (`onChange={(e) => ...}`) なら型推論が効くので書かなくてOK。
* 正しい型をつけると、`e.target.value` の入力補完が効いてミスが減る！

次は、複数の入力欄（名前、メアド、パスワード…）を
**1つのStateオブジェクトでスッキリ管理する方法** に挑戦です！ 💪