## `??`、`||`、`?.` 的区别

在 [src/02-functions-and-objects.ts](/Users/limber/Desktop/review-front-end-project/review-typescript-module/src/02-functions-and-objects.ts) 里有这行代码：

```ts
const displayName = user.nickname ?? user.name;
```

这里用的是空值合并运算符 `??`。

### 1. `??` 空值合并运算符

作用：
当左边的值是 `null` 或 `undefined` 时，才返回右边的值。

```ts
const a = null ?? "default"; // "default"
const b = undefined ?? "default"; // "default"
const c = "" ?? "default"; // ""
const d = 0 ?? 100; // 0
```

适用场景：
当你只想处理“值缺失”的情况时，用 `??` 更准确。

在当前文件里：
`user.nickname ?? user.name` 的意思是：
如果 `nickname` 有值，就用 `nickname`；
如果 `nickname` 是 `undefined` 或 `null`，就退回用 `name`。

### 2. `||` 逻辑或运算符

作用：
只要左边是假值，就返回右边。

JavaScript 里的假值包括：
- `false`
- `0`
- `""`
- `NaN`
- `null`
- `undefined`

```ts
const a = "" || "default"; // "default"
const b = 0 || 100; // 100
const c = null || "default"; // "default"
```

适用场景：
当你希望“所有假值都走默认值”时，可以用 `||`。

注意：
如果 `0`、`""`、`false` 是合法值，`||` 往往会误伤，这时应该优先用 `??`。

### 3. `?.` 可选链运算符

作用：
当左边对象是 `null` 或 `undefined` 时，停止继续访问，并直接返回 `undefined`，不会报错。

```ts
const user = { profile: { nickname: "Ali" } };

const a = user.profile?.nickname; // "Ali"
const b = user.settings?.theme; // undefined
```

它常见的几种写法：

```ts
obj?.prop
obj?.[key]
func?.()
```

适用场景：
当对象层级不确定、属性可能不存在时，用 `?.` 可以避免 `Cannot read properties of undefined` 这类运行时错误。

### 4. 三者对比

```ts
const value = 0;

value || 100; // 100
value ?? 100; // 0
```

结论：
- `||`：处理所有假值
- `??`：只处理 `null` 和 `undefined`
- `?.`：安全访问对象属性、数组项或函数调用

### 5. 我的理解

- `??` 更像“值缺失时给默认值”
- `||` 更像“左边不成立时给默认值”
- `?.` 更像“先安全地往下访问，再决定后续逻辑”

### 6. 常见组合

`?.` 和 `??` 经常一起用：

```ts
const nickname = user.profile?.nickname ?? "Anonymous";
```

含义：
如果 `user.profile?.nickname` 能取到值，就用它；
如果结果是 `undefined` 或 `null`，就用 `"Anonymous"`。
# readonly

`readonly` 的意思是：某个属性在初始化之后，不能再被重新赋值。

## 基本示例

```ts
type User = {
  readonly id: number;
  name: string;
};

const user: User = {
  id: 1,
  name: "Tom"
};

user.name = "Jerry"; // 可以
// user.id = 2; // 报错
```

## 关键点

- `readonly` 限制的是属性重新赋值
- 它常用于对象属性、类属性、数组相关类型
- 它不是深度冻结，只限制当前这一层

## 易混点

```ts
type Config = {
  readonly tags: string[];
};

const config: Config = {
  tags: ["ts", "js"]
};

config.tags.push("react"); // 可以
// config.tags = ["new"]; // 不可以
```

这里 `tags` 这个属性不能重新指向别的数组，但原数组内部的元素仍然可以修改。

---

# 泛型推断与手动指定 `<T>`

核心结论：

- TypeScript 的泛型会尽量自动推断
- 是否需要手动写 `<T>`，取决于 TS 能不能从函数参数里推断出泛型
- 你传入具体类型时，泛型会保留这个具体类型，不会自动变成更宽泛的 `object`

## 1. 自动推断

当泛型可以从函数参数中推断出来时，通常不需要手动写 `<T>`。

```ts
function identity<T>(value: T): T {
  return value;
}

const a = identity(123); // T = number
const b = identity("hello"); // T = string
```

这里的 `T` 是根据参数 `value` 的实际类型自动推断出来的。

## 2. 必须手动写 `<T>` 的情况

### 情况 1：泛型没有出现在参数里

```ts
function createArray<T>(): T[] {
  return [];
}

const arr = createArray<number>();
```

因为函数没有参数，TS 无法知道 `T` 是什么，所以必须手动指定。

### 情况 2：你想覆盖默认推断结果

```ts
function wrap<T>(value: T): T[] {
  return [value];
}

const x = wrap("hello"); // T = string
const y = wrap<string | number>("hello");
```

这里 `y` 是手动把 `T` 指定成 `string | number`，而不是让 TS 自动推成 `string`。

### 情况 3：推断结果过窄或不符合预期

```ts
function fn<T>(value: T): T {
  return value;
}

const v1 = fn(null); // T = null
const v2 = fn<string | null>(null);
```

如果自动推断的结果太窄，可以手动指定一个更合适的联合类型。

## 3. 泛型不会自动变宽成 `object`

这一点很重要。

```ts
type ApiShape<T> = T extends string
  ? { type: "text"; value: T }
  : { type: "json"; value: T };
```

如果你传入：

```ts
type A = ApiShape<{ ok: true }>;
```

那么 `T` 就是 `{ ok: true }`，最终得到：

```ts
{
  type: "json";
  value: { ok: true };
}
```

这时 `value` 不是宽泛的 `object`，而是精确的 `{ ok: true }`。

如果你主动写：

```ts
type B = ApiShape<object>;
```

那 `value` 才会是 `object`。

所以泛型的规则是：

- 传入具体类型，就保留具体类型
- 传入宽泛类型，就得到宽泛类型
- 泛型不会替你自动把具体对象“泛化”为 `object`

## 4. 快速判断规则

### 不用手动写 `<T>`

- 泛型出现在函数参数中
- 参数提供了足够信息让 TS 推断

### 需要手动写 `<T>`

- 泛型没有出现在参数中
- TS 推断不出来
- 你想覆盖默认推断结果

## 5. 一句话总结

是否要手动写 `<T>`，本质上看的是：

`TypeScript 能不能从当前上下文里准确推断出你想要的类型。`

---

# TypeScript 常见类型关键字

可以把 TypeScript 里的类型关键字和常见类型写法分成三类来记：

- 基础值类型
- 特殊类型
- 类型系统相关关键字

## 1. 基础值类型关键字

这些基本对应 JavaScript 的基础值类型：

- `number`
- `string`
- `boolean`
- `null`
- `undefined`
- `bigint`
- `symbol`

示例：

```ts
let age: number = 18;
let userName: string = "Tom";
let done: boolean = false;
```

## 2. 特殊类型关键字

这部分是 TypeScript 里非常重要的一组类型。

### `any`

- 含义：任意类型
- 特点：基本放弃类型检查
- 风险：最宽松，但不安全

```ts
let value: any = 123;
value = "hello";
value = true;
```

### `unknown`

- 含义：未知类型
- 特点：比 `any` 安全，使用前必须先做类型判断

```ts
let input: unknown = "hello";

if (typeof input === "string") {
  console.log(input.toUpperCase());
}
```

### `never`

- 含义：不会出现的类型
- 常见场景：
  - 永远抛错的函数
  - 死循环函数
  - 穷尽检查中不该出现的分支

```ts
function fail(message: string): never {
  throw new Error(message);
}
```

### `void`

- 含义：没有返回值
- 常用于函数返回类型

```ts
function log(): void {
  console.log("hi");
}
```

### `object`

- 含义：非原始类型
- 特点：比具体对象类型宽泛很多

```ts
let data: object = { name: "Tom" };
```

## 3. 常见复合类型写法

这些不一定都是单独的关键字，但它们是 TypeScript 最常见的类型表达方式。

### 数组类型

- `Array<T>`
- `T[]`

```ts
let scores: number[] = [1, 2, 3];
let names: Array<string> = ["a", "b"];
```

### 元组类型

- `[T1, T2]`

```ts
let point: [number, string] = [1, "x"];
```

### 对象类型

```ts
let user: { name: string; age: number } = {
  name: "Tom",
  age: 18
};
```

### 函数类型

```ts
let fn: (a: number) => string;
```

### 联合类型

- `"a" | "b"`
- `string | number`

```ts
let result: string | number = "ok";
```

### 交叉类型

- `A & B`

表示一个值同时满足多个类型要求。

## 4. 类型系统相关关键字

这部分在泛型和高级类型里会频繁出现。

### `type`

- 用于定义类型别名

```ts
type Status = "draft" | "published";
```

### `interface`

- 用于定义接口
- 更适合描述对象结构

```ts
interface User {
  name: string;
}
```

### `keyof`

- 取对象类型的键名联合

```ts
type UserKeys = keyof User;
```

### `extends`

- 在泛型里常表示约束
- 在条件类型里表示“是否满足某种类型条件”

```ts
type Box<T extends string> = {
  value: T;
};
```

### `infer`

- 在条件类型中临时推断一个类型变量

```ts
type ElementType<T> = T extends Array<infer Item> ? Item : T;
```

### `typeof`

- 取某个变量或值的类型

```ts
const user = { name: "Tom" };
type UserType = typeof user;
```

### `in`

- 常用于映射类型中遍历 key

```ts
type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};
```

### `as`

- 类型断言

```ts
const value = "hello" as string;
```

### `is`

- 类型谓词
- 常用于自定义类型守卫

```ts
function isString(value: unknown): value is string {
  return typeof value === "string";
}
```

### `readonly`

- 表示只读属性
- 初始化后不能重新赋值

```ts
type UserInfo = {
  readonly id: number;
};
```

## 5. 当前阶段最值得优先记住的

如果你现在是回顾阶段，优先掌握这几个：

- `number`
- `string`
- `boolean`
- `null`
- `undefined`
- `any`
- `unknown`
- `never`
- `void`
- `object`
- `type`
- `interface`
- `keyof`
- `extends`
- `infer`
- `readonly`

## 6. 一句话总结

TypeScript 常见类型关键字可以分成三类：

- 基础值类型：`number`、`string`、`boolean` 等
- 特殊类型：`any`、`unknown`、`never`、`void`、`object`
- 类型系统关键字：`type`、`interface`、`keyof`、`extends`、`infer`、`readonly` 等

---

# infer 的使用方法

`infer` 是 TypeScript 高级类型里很重要的一个关键字。

核心理解：

- `infer` 只能用在条件类型里
- 它的作用是：从一个已有类型结构中，临时提取出一部分类型
- `infer X` 里的 `X` 不是值变量，而是“临时类型变量”

## 1. 一句话理解

可以把 `infer` 理解成：

`如果某个类型能匹配某种结构，就把结构里的某一部分类型取出来，并临时命名。`

## 2. 最经典的例子：提取数组元素类型

```ts
type ElementType<T> = T extends Array<infer Item> ? Item : T;
```

这段代码的意思是：

- 如果 `T` 是数组类型
- 那就把数组里的元素类型提取出来，命名为 `Item`
- 最后返回 `Item`
- 如果 `T` 不是数组，就返回 `T` 本身

示例：

```ts
type A = ElementType<number[]>; // number
type B = ElementType<string[]>; // string
type C = ElementType<boolean>; // boolean
```

这里的 `infer Item` 不是提前定义好的类型，而是 TypeScript 在匹配 `Array<...>` 这个结构时，自动把里面那部分类型提取出来。

## 3. 它很像“类型解构”

你可以把它类比成 JavaScript 里的解构：

```ts
const [first] = [1, 2, 3];
```

而 `infer` 更像是在类型层面做解构：

```ts
T extends Array<infer Item>
```

它在问：

`T 能不能匹配 Array<某种类型> 这种结构？如果能，就把这个“某种类型”取出来，记作 Item。`

## 4. 常见用法一：提取函数返回值

```ts
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
```

含义：

- 如果 `T` 是函数类型
- 就把它的返回值类型提取出来，命名为 `R`
- 否则返回 `never`

示例：

```ts
type A = MyReturnType<() => string>; // string
type B = MyReturnType<(x: number) => boolean>; // boolean
```

## 5. 常见用法二：提取 Promise 内部类型

```ts
type MyAwaited<T> = T extends Promise<infer U> ? U : T;
```

含义：

- 如果 `T` 是 `Promise<某类型>`
- 就把 Promise 里面的类型提取出来，命名为 `U`
- 否则直接返回 `T`

示例：

```ts
type A = MyAwaited<Promise<number>>; // number
type B = MyAwaited<string>; // string
```

## 6. 常见用法三：提取对象某个属性的类型

```ts
type ValueType<T> = T extends { value: infer V } ? V : never;
```

含义：

- 如果 `T` 的结构里有 `value` 属性
- 就把 `value` 对应的类型提取出来，命名为 `V`

示例：

```ts
type A = ValueType<{ value: string }>; // string
type B = ValueType<{ value: number }>; // number
```

## 7. 一个组合例子

如果你想表达：

- `T` 是数组时，提取数组元素类型
- 否则如果 `T` 有 `value` 属性，就提取 `value` 的类型
- 否则返回 `T`

可以写成：

```ts
type ArrayOrValue<T> =
  T extends Array<infer Item>
    ? Item
    : T extends { value: infer ValueType }
      ? ValueType
      : T;
```

示例：

```ts
type A = ArrayOrValue<number[]>; // number
type B = ArrayOrValue<{ value: string }>; // string
type C = ArrayOrValue<boolean>; // boolean
```

## 8. 使用 `infer` 时要记住的约束

- `infer` 只能写在条件类型里，不能单独乱用
- 它必须依附在某种“匹配结构”里，比如：
  - `Array<infer Item>`
  - `Promise<infer U>`
  - `(...args: any[]) => infer R`
  - `{ value: infer V }`
- `infer` 提取的是“类型的一部分”，不是运行时值

## 9. 最容易混淆的点

- `infer` 不是定义普通变量，而是定义临时类型变量
- `infer` 不是让你随便发明一个类型，而是要从已有结构里“拆”出来
- `infer` 本质上是“匹配 + 提取”，不是“手动指定”

## 10. 一句话总结

`infer` 的本质是：在条件类型中，从一个已有类型结构里提取子类型，并给这个子类型起一个临时名字。

好，这里我帮你整理成一份**可以直接放进笔记的结构化总结（偏工程化）**👇

---

# 📘 TypeScript：`type` vs `interface` 知识总结

---

# 一、基础概念

## 1️⃣ `type`

> **类型别名（Type Alias）**：给任意类型起名字

```ts
type User = {
  name: string
  age: number
}
```

---

## 2️⃣ `interface`

> **接口**：专门用于描述对象结构

```ts
interface User {
  name: string
  age: number
}
```

---

# 二、核心区别

| 对比维度      | type | interface     |
| --------- | ---- | ------------- |
| 本质        | 类型别名 | 对象结构定义        |
| 适用范围      | 任意类型 | 仅对象类型         |
| 是否可定义联合类型 | ✅    | ❌             |
| 是否可定义交叉类型 | ✅    | ❌（只能 extends） |
| 是否支持声明合并  | ❌    | ✅             |
| 扩展方式      | `&`  | `extends`     |

---

# 三、定义能力对比

## 1️⃣ type 能定义的类型

```ts
// 对象
type User = { name: string }

// 联合类型
type Status = "success" | "error"

// 基本类型组合
type ID = number | string

// 函数类型
type Fn = (a: number) => number

// 交叉类型
type A = { a: number } & { b: number }
```

---

## 2️⃣ interface 能定义的类型

```ts
interface User {
  name: string
  age: number
}
```

👉 ❗只能描述对象结构

---

# 四、扩展（继承）方式

## 1️⃣ interface 使用 extends

```ts
interface A {
  a: number
}

interface B extends A {
  b: number
}
```

---

## 2️⃣ type 使用交叉类型 `&`

```ts
type A = { a: number }

type B = A & { b: number }
```

---

## 3️⃣ interface 可以继承 type（前提）

```ts
type A = { a: number }

interface B extends A {
  b: number
}
```

👉 ✅ 前提：type 必须是对象类型

---

# 五、声明合并（重要）

## interface 支持

```ts
interface User {
  name: string
}

interface User {
  age: number
}
```

👉 自动合并：

```ts
{
  name: string
  age: number
}
```

---

## type 不支持

```ts
type User = { name: string }
type User = { age: number } // ❌ 报错
```

---

# 六、使用场景建议（工程实践）

## ✅ 推荐使用 interface

* 定义数据结构（DTO / 实体）
* API 请求 / 响应结构
* 面向对象建模

---

## ✅ 推荐使用 type

* 联合类型（枚举替代）
* 工具类型（泛型、映射类型）
* 复杂类型组合
* 条件类型

---

# 七、等价关系（重要理解）

```ts
interface A {
  a: number
}
```

≈

```ts
type A = {
  a: number
}
```

👉 在“简单对象”场景下基本等价

---

# 八、关键限制

## interface 不能：

```ts
interface A = string | number ❌
```

---

## type 不能：

```ts
type A {}
type A {} ❌（不能重复定义）
```

---

# 九、核心理解（必须掌握）

👉

* `type`：**万能类型工具（更灵活）**
* `interface`：**对象建模工具（更语义化）**

---

# 十、一句话总结（记忆版）

👉

* 能用 `interface` 描述结构 → 优先用 interface
* 需要联合 / 高级类型 → 用 type

---

# 十一、终极理解（进阶）

👉 TypeScript 类型系统本质：

```text
type = 类型表达式（表达能力强）
interface = 对象结构约束（建模清晰）
```

---

如果你下一步要继续进阶（强烈建议）👇

👉 我可以帮你整理：

* TS 类型体系全图（very important）
* 企业项目类型设计规范（非常实用）
* `as const + typeof + satisfies` 组合技（高频）

你现在已经到 TS 类型系统核心阶段了 👍
