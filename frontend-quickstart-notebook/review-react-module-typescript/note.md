## `??`、`||`、`?.` 的区别

在 `src` 目录的 TypeScript 版本示例里，这几个操作符的行为和 JavaScript 一样，但 TypeScript 会额外帮助你表达“值可能为空”的边界。

### 1. `??` 空值合并运算符

作用：
当左边的值是 `null` 或 `undefined` 时，才返回右边的值。

```ts
const a = null ?? "default"; // "default"
const b = undefined ?? "default"; // "default"
const c = "" ?? "default"; // ""
const d = 0 ?? 100; // 0
```

### 2. `||` 逻辑或运算符

作用：
只要左边是假值，就返回右边。

```ts
const a = "" || "default"; // "default"
const b = 0 || 100; // 100
const c = null || "default"; // "default"
```

### 3. `?.` 可选链运算符

作用：
当左边对象是 `null` 或 `undefined` 时，停止继续访问，并直接返回 `undefined`，不会报错。

```ts
const user = { profile: { nickname: "Ali" } };

const a = user.profile?.nickname; // "Ali"
const b = user.settings?.theme; // undefined
```

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
