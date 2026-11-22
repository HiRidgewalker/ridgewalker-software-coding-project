## `??`、`||`、`?.`

### `??`

左边是 `null` 或 `undefined` 时，返回右边的值。

```ts
const displayName = user.nickname ?? user.name;

const a = null ?? "default"; // "default"
const b = undefined ?? "default"; // "default"
const c = "" ?? "default"; // ""
const d = 0 ?? 100; // 0
```

### `||`

左边是假值时，返回右边的值。假值包括 `false`、`0`、`""`、`NaN`、`null`、`undefined`。

```ts
const a = "" || "default"; // "default"
const b = 0 || 100; // 100
const c = null || "default"; // "default"
```

### `?.`

左边是 `null` 或 `undefined` 时，停止继续访问并返回 `undefined`。

```ts
const user = { profile: { nickname: "Ali" } };

const a = user.profile?.nickname; // "Ali"
const b = user.settings?.theme; // undefined
```

```ts
obj?.prop
obj?.[key]
func?.()
```

### `||` 与 `??`

```ts
const value = 0;

value || 100; // 100
value ?? 100; // 0
```

### `?.` 与 `??`

`?.` 的结果是 `null` 或 `undefined` 时，改用 `??` 右边的值。

```ts
const nickname = user.profile?.nickname ?? "Anonymous";
```

## `readonly`

属性初始化之后不能再被重新赋值。

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

只限制当前这一层属性。数组内部的元素仍然可以修改。

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

## 泛型推断与手动指定 `<T>`

### 自动推断

泛型能从函数参数推断出来时，不用手写 `<T>`。

```ts
function identity<T>(value: T): T {
  return value;
}

const a = identity(123); // T = number
const b = identity("hello"); // T = string
```

### 泛型没有出现在参数里

```ts
function createArray<T>(): T[] {
  return [];
}

const arr = createArray<number>();
```

### 覆盖默认推断

```ts
function wrap<T>(value: T): T[] {
  return [value];
}

const x = wrap("hello"); // T = string
const y = wrap<string | number>("hello");
```

### 放宽过窄的推断

```ts
function fn<T>(value: T): T {
  return value;
}

const v1 = fn(null); // T = null
const v2 = fn<string | null>(null);
```

### 保留传入的具体类型

传入什么类型，`value` 就是什么类型。

```ts
type ApiShape<T> = T extends string
  ? { type: "text"; value: T }
  : { type: "json"; value: T };

type A = ApiShape<{ ok: true }>;
// { type: "json"; value: { ok: true } }

type B = ApiShape<object>;
// { type: "json"; value: object }
```

## TypeScript 常见类型关键字

### 基础值类型

`number`、`string`、`boolean`、`null`、`undefined`、`bigint`、`symbol`。

```ts
let age: number = 18;
let userName: string = "Tom";
let done: boolean = false;
```

### `any`

任意类型，放弃类型检查。

```ts
let value: any = 123;
value = "hello";
value = true;
```

### `unknown`

未知类型，使用前先判断类型。

```ts
let input: unknown = "hello";

if (typeof input === "string") {
  console.log(input.toUpperCase());
}
```

### `never`

不会出现的类型。用于永远抛错的函数、死循环，以及穷尽检查中不该出现的分支。

```ts
function fail(message: string): never {
  throw new Error(message);
}
```

### `void`

函数没有返回值。

```ts
function log(): void {
  console.log("hi");
}
```

### `object`

非原始类型。

```ts
let data: object = { name: "Tom" };
```

### 数组

```ts
let scores: number[] = [1, 2, 3];
let names: Array<string> = ["a", "b"];
```

### 元组

```ts
let point: [number, string] = [1, "x"];
```

### 对象

```ts
let user: { name: string; age: number } = {
  name: "Tom",
  age: 18
};
```

### 函数

```ts
let fn: (a: number) => string;
```

### 联合类型

```ts
let result: string | number = "ok";
```

### 交叉类型

一个值同时满足多个类型。

```ts
type A = { a: number } & { b: number };
```

### `type`

给类型起名字。

```ts
type Status = "draft" | "published";
```

### `interface`

描述对象结构。

```ts
interface User {
  name: string;
}
```

### `keyof`

取对象类型的键名联合。

```ts
type UserKeys = keyof User;
```

### `extends`

在泛型里表示约束，在条件类型里表示能否赋值给某个类型。

```ts
type Box<T extends string> = {
  value: T;
};
```

### `infer`

在条件类型里，从匹配到的结构中取出一部分类型。

```ts
type ElementType<T> = T extends Array<infer Item> ? Item : T;
```

### `typeof`

取某个值的类型。

```ts
const user = { name: "Tom" };
type UserType = typeof user;
```

### `in`

在映射类型里遍历键。

```ts
type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};
```

### `as`

类型断言。

```ts
const value = "hello" as string;
```

### `is`

类型谓词，用于自定义类型守卫。

```ts
function isString(value: unknown): value is string {
  return typeof value === "string";
}
```

### `readonly`

属性初始化后不能重新赋值。

```ts
type UserInfo = {
  readonly id: number;
};
```

## `infer`

`infer` 写在条件类型的 `extends` 结构里，从匹配到的类型中取出一部分。

### 提取数组元素类型

```ts
type ElementType<T> = T extends Array<infer Item> ? Item : T;

type A = ElementType<number[]>; // number
type B = ElementType<string[]>; // string
type C = ElementType<boolean>; // boolean
```

### 提取函数返回值

```ts
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

type A = MyReturnType<() => string>; // string
type B = MyReturnType<(x: number) => boolean>; // boolean
```

### 提取 Promise 内部类型

```ts
type MyAwaited<T> = T extends Promise<infer U> ? U : T;

type A = MyAwaited<Promise<number>>; // number
type B = MyAwaited<string>; // string
```

### 提取对象属性类型

```ts
type ValueType<T> = T extends { value: infer V } ? V : never;

type A = ValueType<{ value: string }>; // string
type B = ValueType<{ value: number }>; // number
```

### 数组或 `value` 属性

```ts
type ArrayOrValue<T> =
  T extends Array<infer Item>
    ? Item
    : T extends { value: infer ValueType }
      ? ValueType
      : T;

type A = ArrayOrValue<number[]>; // number
type B = ArrayOrValue<{ value: string }>; // string
type C = ArrayOrValue<boolean>; // boolean
```

## `type` 与 `interface`

### `type`

可以表示对象、联合类型、函数类型和交叉类型。

```ts
type User = { name: string }

type Status = "success" | "error"

type ID = number | string

type Fn = (a: number) => number

type A = { a: number } & { b: number }
```

### `interface`

描述对象结构。

```ts
interface User {
  name: string
  age: number
}
```

### `interface` 使用 `extends`

```ts
interface A {
  a: number
}

interface B extends A {
  b: number
}
```

### `type` 使用 `&`

```ts
type A = { a: number }

type B = A & { b: number }
```

### `interface` 继承 `type`

被继承的 `type` 是对象类型。

```ts
type A = { a: number }

interface B extends A {
  b: number
}
```

### 声明合并

同名 `interface` 会把成员合并到一起。

```ts
interface User {
  name: string
}

interface User {
  age: number
}
```

合并后的结构：

```ts
{
  name: string
  age: number
}
```

同名 `type` 不能重复定义。

```ts
type User = { name: string }
type User = { age: number } // 报错
```

### 简单对象

两种写法描述同一结构。

```ts
interface A {
  a: number
}
```

```ts
type A = {
  a: number
}
```

### 限制

`interface` 不能写成联合类型。

```ts
interface A = string | number // 报错
```

`type` 不能重复定义。

```ts
type A {}
type A {} // 报错
```
