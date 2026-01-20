# 第6章：分類ゲーム！これはCommand？Query？🎯✨

## この章でできるようになること💪🌸

* 「これ、Command？Query？」を**自分の言葉で理由付き**で言えるようになる🗣️✨
* “更新っぽいけど参照っぽい”の**ひっかけ問題**に強くなる🧠🧨
* 迷った時に使える**ミニ基準（マイルール）**が手に入る🧭💡

---

## まずは超ショート復習🧸📌

* **Command**：状態を変える／外に影響を出す（保存・送信・ログ・UI更新など）🔧💥
* **Query**：状態を読む／基本は“読むだけ”（できれば副作用ゼロ）📖🍃

ここで大事なのは、**「他の人から見て“何か起きた”って観測できる？」** という視点だよ👀✨
（DBが変わる／ファイルが書き換わる／ログが増える／画面が変わる…などなど）

---

## 迷わないためのミニ基準（3秒チェック）⏱️🧠

次の質問に **1つでもYES** があったら、だいたい **Command寄り** だよ✅

1. **保存・更新・削除**してる？（DB / ファイル / localStorage / メモリ状態）💾🗑️
2. **外部へ送ってる**？（HTTP POST/PUT、通知、分析イベント、メール）📡📨
3. **ログ・メトリクス**増やしてる？（console、analytics、監視）📊📝
4. **画面/UI**を変えてる？（DOM更新、トースト表示）🖥️✨
5. **キャッシュを温める/更新する**？🍯🔁

逆に、**同じ入力なら同じ出力**で、どこにも書き込まないなら **Query** が濃厚📖🍃

---

## ありがちな“ひっかけポイント”3つ🧨😵‍💫

### ① 「読むだけ…のはずが、ログ書いてた」📝

Queryのつもりで `console.log` や analytics を入れると、もう“外に影響”が出るよね👀
➡️ **それはCommand要素**。分けるのがスッキリ✨

### ② 「GETだからQueryでしょ？」問題🌐

GET自体は“読み”だけど、**取得結果を保存してキャッシュ更新**したら Command 混入🍯💥
➡️ `fetchTodos()`（Query）と `refreshTodosCache()`（Command）みたいに分けると勝ち🏆

### ③ 「ID生成・時刻・乱数」🎲⏰

状態は変えないけど、**毎回結果が変わる**から“純粋なQuery”としては扱いづらい子たち🐣
➡️ “境界”に寄せて、必要なら注入（DI）で扱うと後がラク✨

※ちなみに最新のTypeScriptは **5.9系**で、モジュール実行タイミングに関係する `import defer` のような“副作用と実行”に触れる話題も増えてるよ（モジュール読み込み＝実行＝副作用、に敏感になれる）📦⚡️ ([Microsoft for Developers][1])

---

## 🎯分類ゲーム：問題編（15問）🎮✨

まずは直感でOK！「どっち寄り？」って考えてみてね😊🌸
（※この章のコツ：**迷ったら“観測できる変化があるか”**👀）

1. `addTodo(text)`：ToDoを1件追加して保存する📝💾
2. `getTodos()`：ToDo一覧を返す📋
3. `completeTodo(id)`：完了にする✅
4. `completeTodoAndReturnList(id)`：完了にして、更新後一覧も返す🔁📋
5. `getTodos()` の中で `console.log("loaded")` してる📝
6. `getTodoCount()`：件数だけ返す🔢
7. `renderTodos(todos)`：DOMに描画して画面を更新する🖥️✨
8. `validateTodoText(text)`：入力がOKかチェックして true/false を返す✅❌
9. `fetchTodos()`：サーバーからGETして一覧を返す🌐📋
10. `fetchTodosAndCache()`：GETして、結果をキャッシュに保存する🍯💾
11. `trackEvent("todo_completed")`：分析イベントを送る📊📡
12. `generateId()`：UUIDなどで新しいIDを作って返す🆔🎲
13. `getNow()`：現在時刻を返す⏰
14. `loadFromLocalStorage()`：localStorageから読み出して返す📦
15. `import "./initAnalytics"`：importしたら初期化が走ってイベント登録される⚡️📦

---

## ✅解答＆解説編（理由が言えたら優勝🏆💖）

## 1. `addTodo(text)` → **Command** 🔧💾

保存で状態が変わる！観測可能な変化があるよね👀✨

## 2. `getTodos()` → **Query** 📖📋

読むだけで返すならQueryの王道！

## 3. `completeTodo(id)` → **Command** ✅🔧

完了状態に更新＝状態変化！

## 4. `completeTodoAndReturnList(id)` → **Command（混ぜ混ぜ注意）** 🧨

“更新（Command）”しつつ“一覧取得（Query）”もやってる💥
➡️ ベストはこう👇

* `completeTodo(id)`（Command）
* `getTodos()`（Query）
  で2段にするのがCQSの気持ちよさ✨

## 5. `getTodos()` がログ書いてる → **Command要素が混入** 📝💥

読むだけのつもりでも、ログが増える＝外に影響が出る👀
➡️ 対策：ログは“外側”に寄せる（呼び出し側でログ）か、専用Commandへ分離✨

## 6. `getTodoCount()` → **Query** 🔢📖

数を返すだけ。状態変えないならQuery！

## 7. `renderTodos(todos)` → **Command** 🖥️✨

画面が変わる＝観測可能！UI更新は立派な副作用だよ🌸

## 8. `validateTodoText(text)` → **Query** ✅❑

入力→判定（true/false）。理想的な純粋Query！

## 9. `fetchTodos()`（GETして返すだけ） → **Query寄り** 🌐📖

“読む”目的ならQueryとして扱うことが多いよ（実務の落とし所）✨
ただしネットワークは不安定なので、失敗設計は別章で強くなる💪

## 10. `fetchTodosAndCache()` → **Command** 🍯💾

キャッシュ保存＝状態変化！
➡️ 分けるとスッキリ：

* `fetchTodos()`（Query）
* `saveTodosCache(todos)`（Command）
  みたいにね😊

## 11. `trackEvent(...)` → **Command** 📊📡

外部へ送ってる＝影響大。Command！

## 12. `generateId()` → **グレー：Queryっぽいけど“純粋じゃない”** 🧠🎲

状態は変えないからQueryっぽい。だけど乱数で結果が変わる！
➡️ コツ：**ID生成を“境界”扱い**にして、必要なら注入できる形にすると後で困らない✨

## 13. `getNow()` → **グレー：Queryっぽいけど“純粋じゃない”** ⏰🧠

毎回変わる＝テストがやりづらい子。
➡️ `Clock` を外から渡す（DI）にすると、テストで時間固定できて最高💖

## 14. `loadFromLocalStorage()` → **Query寄り（条件つき）** 📦📖

“読むだけで返す”ならQuery扱いでOKなことが多いよ✨
でも「読み出してついでにアプリ状態へ反映」までやるとCommand混入になる🧨

## 15. `import "./initAnalytics"` → **Command寄り（副作用が走るなら）** ⚡️📦

importで初期化・登録・送信が走るなら、観測可能な変化あり👀
最近のTS 5.9 では `import defer` のように“実行 Remember”がより意識される話もあるから、副作用の場所は丁寧に扱うと気持ちいいよ✨ ([Microsoft for Developers][1])

---

## 💡あなた専用「迷ったらこれ」マイルール案🧭✨

この章のゴールは“完璧”じゃなくて、**迷子にならない軸**を持つこと😊

* ✅ **書く（save/set/update/delete/log/track/render/cache）**が入ったら Command
* ✅ **読む（get/find/list/calc/validate）**だけなら Query
* ✅ “両方やってる”と気づいたら **分割**（Command→Queryの2段）🔁✨
* ✅ 乱数・時刻は「境界」へ寄せる（後でテストが超ラク）🧪💖

---

## 🤖AIミニコーナー：分類ゲームを強化する使い方✨

Copilot Chat などに、こう投げるとすごく練習になるよ👇（IDE内チャットが前提の機能として案内されてるよ）([GitHub Docs][2])

**プロンプト例①（理由付き分類）**
「次の関数一覧をCommand/Queryに分類して、理由を1行ずつ書いて。グレーは“グレー”って言ってOK：…」

**プロンプト例②（混ざってるのを分割提案）**
「この関数がCQS違反っぽいなら、分割案（関数名と責務）を出して：…」

**プロンプト例③（命名改善）**
「命名がCommand/Queryどっちか伝わるように、関数名を提案して：…」

AIの答えは便利だけど、最後はあなたの“観測できる変化ある？”チェックで判定すると最強だよ👀✅

---

## ✍️ミニ課題（10分）🧁✨

ToDoミニアプリの操作を想像して、次を紙でもメモでもOKでやってみてね📝💖

1. 「混ぜ混ぜ関数」を1つ作ってしまう（例：追加して一覧返す、みたいな）😇
2. それを **Command / Query に分割**して関数名を付け直す✂️✨
3. それぞれの関数に「なぜこっち？」を1行で書く🧠

---

必要なら、この章の「15問」をもう少し増やして、**“実務あるある（キャッシュ／監査ログ／トランザクション／UI通知）”版**の追加問題も作れるよ🎯💖

[1]: https://devblogs.microsoft.com/typescript/announcing-typescript-5-9/?utm_source=chatgpt.com "Announcing TypeScript 5.9"
[2]: https://docs.github.com/en/copilot/get-started/features?utm_source=chatgpt.com "GitHub Copilot features"
