# 第41章：配列のState操作（追加・削除・更新）

Reactでアプリを作ると、必ずと言っていいほど「リスト（配列）」を扱います。
TODOリスト、商品一覧、コメント欄…全部配列です。

でも React の State で配列を扱うときには、**「直接書き換えちゃダメ（ミュータブル操作禁止）」** という超重要なルールがあります 🚨
これを守らないと、画面が更新されなかったりバグの原因になります。

---

## 1. 絶対にやってはいけないこと 🙅‍♂️

```tsx
const [items, setItems] = useState(["りんご", "みかん"]);

const handleBadAdd = () => {
  items.push("バナナ"); // ❌ push は配列を直接書き換える！
  setItems(items);      // Reactは「参照」が変わってないから、変更なしとみなす
};
```

`push`, `pop`, `splice`, `sort` などのメソッドは、元の配列を破壊的に変更します。
React は State が更新されたかどうかを「以前のものと違うか（参照等価性）」で判断するので、
中身だけこっそり書き換えても **「変わってないじゃん」と無視されて、再レンダリングされません** 😱

---

## 2. 追加：スプレッド構文でコピーする ➕

配列に要素を追加するときは、**新しい配列を作って** そこに要素を入れます。
ここで **スプレッド構文 (`...`)** が大活躍します。

```tsx
const handleAdd = () => {
  // [...今の配列, 新しい要素]
  setItems([...items, "バナナ"]); 
};
```

1. `[]` で新しい配列を作る。
2. `...items` で今の要素を全部展開して入れる。
3. 最後に `"バナナ"` を足す。

これで「新しい配列」ができるので、React もちゃんと「おっ、変わったな！」と気づいて画面を更新してくれます ✨

---

## 3. 削除：`filter` を使う 🗑️

要素を削除するときは、**「残したいものだけを集めた新しい配列」** を作ります。
これには `filter` メソッドが最適です。

```tsx
const handleDelete = (targetItem: string) => {
  // 条件に合う（削除対象じゃない）ものだけを残す
  setItems(items.filter((item) => item !== targetItem));
};
```

「りんご」を消したいなら、「りんご以外 (`!==`)」をフィルターして残します。
`filter` は新しい配列を返してくれるメソッドなので、React と相性バツグンです 💕

---

## 4. 更新：`map` を使う 🔄

「2番目の要素だけ書き換えたい」みたいなときはどうでしょう？
これも **「書き換えた新しい配列」** を作ります。
`map` メソッドを使います。

```tsx
const handleUpdate = (indexToUpdate: number, newName: string) => {
  setItems(items.map((item, index) => {
    // ターゲットのインデックスなら、新しい値にする
    if (index === indexToUpdate) {
      return newName;
    }
    // それ以外なら、そのままの値を返す（変えない）
    return item;
  }));
};
```

`map` は配列の全要素をなめて、新しい配列を作ります。
「変えたいやつだけ変えて、あとはそのまま」というロジックを書けばOKです 👍

---

## 5. ミニ練習：TODOリストのロジック 📝

これらを組み合わせると、TODOリストの基本機能が作れます。

```tsx
import { useState } from "react";

export const TodoListLogic = () => {
  const [todos, setTodos] = useState(["勉強", "買い物"]);
  const [text, setText] = useState("");

  // 追加
  const add = () => {
    if (!text) return;
    setTodos([...todos, text]);
    setText("");
  };

  // 削除（インデックスで指定）
  const remove = (indexToRemove: number) => {
    setTodos(todos.filter((_, i) => i !== indexToRemove));
  };

  return (
    <div>
      <input value={text} onChange={(e) => setText(e.target.value)} />
      <button onClick={add}>追加</button>
      
      <ul>
        {todos.map((todo, i) => (
          <li key={i}>
            {todo}
            <button onClick={() => remove(i)}>削除</button>
          </li>
        ))}
      </ul>
    </div>
  );
};
```

---

## 6. まとめ 🌟

* React の配列 State は **直接書き換え（ミュータブル操作）禁止**！ `push` は敵。
* **追加** → `[...old, new]` （スプレッド構文）
* **削除** → `filter` （残したいものだけ抽出）
* **更新** → `map` （条件に合うものだけ差し替え）

この「イミュータブル（不変）な操作」の考え方は、React上級者への第一歩です。
最初は面倒に感じるかもしれませんが、慣れると「データが勝手に書き換わらない安心感」が手放せなくなりますよ 🛡️

次は、この考え方をさらに深掘りして、
**「なぜイミュータブルにするの？」** という理由と、便利なテクニックを紹介します 🥪