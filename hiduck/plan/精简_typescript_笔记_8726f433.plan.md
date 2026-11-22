---
name: 精简 TypeScript 笔记
overview: 把 note.md 收成“一个属性配一段用法示例”的笔记，保留现有知识点与示例，删掉总结、复述和强调标记。
todos:
  - id: trim-note
    content: 按统一密度重写 note.md：保留示例，删掉总结、复述和强调标记
    status: pending
isProject: false
---

# 精简 TypeScript 笔记

只改 [frontend-quickstart-notebook/review-typescript-module/note.md](frontend-quickstart-notebook/review-typescript-module/note.md)。知识点、代码示例和现有六块顺序保持不变，不并入后面的专题，也不补充聊天里讲过、笔记里没有的内容。

每条统一成这个密度：

```md
### `??`

左边是 `null` 或 `undefined` 时，返回右边的值。

```ts
const a = null ?? "default"; // "default"
const c = "" ?? "default"; // ""
```
```

定义只留一句能看懂示例的话。示例里的注释已经说明结果时，后面不再写段落复述。

删掉这些整段：

- 各处的「一句话总结」「核心结论」「我的理解」「适用场景」「关键点」「快速判断规则」「当前阶段最值得优先记住的」
- `infer` 一节的「一句话理解」「类型解构」类比、「最容易混淆的点」
- `type` 与 `interface` 一节末尾的场景建议复述、等价关系旁白，以及「下一步进阶」
- 文首指向另一台机器的绝对路径说明；`user.nickname ?? user.name` 作为 `??` 的示例留在代码里
- 标题和正文里的 emoji、`👉`、成串的 `✅` / `❌`、加粗的「重要」「必须掌握」

各块保留的示例：

- `??`、`||`、`?.`：各自的示例、`0` 的对比、`?.` 的三种写法和与 `??` 的组合
- `readonly`：属性不能重赋值，以及 `tags.push` 仍可修改数组内容
- 泛型：自动推断、三种手动指定 `<T>`、`ApiShape<T>` 保留具体类型
- 类型关键字：基础类型、`any` / `unknown` / `never` / `void` / `object`、数组到交叉类型、`type` 到 `readonly` 的关键字示例
- `infer`：数组元素、函数返回值、`Promise`、对象属性、组合示例；约束收成一句：`infer` 写在条件类型的 `extends` 结构里
- `type` 与 `interface`：两边能定义的类型、`extends` 与 `&`、声明合并、不能做的写法。对照表删掉，这些差别已在后面的代码里
