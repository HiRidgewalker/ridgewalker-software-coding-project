/*
高级类型

这一节开始进入 TypeScript 独有的“类型编程”能力。
重点不是记语法，而是理解：类型也可以被计算和转换。
*/

// User 是一个普通对象类型，后面的高级类型示例都会基于它来做“类型计算”。
// 约束：
// - id 必须是 number
// - name 必须是 string
// - active 必须是 boolean
type User = {
  id: number;
  name: string;
  active: boolean;
};

// keyof User 的意思是“取出 User 的所有键名，组成一个联合类型”。
// 所以 UserKeys 等价于: "id" | "name" | "active"
// 约束：
// - 它拿到的是属性名，不是属性值
// - 常用于限制某个参数只能传对象已有的 key
type UserKeys = keyof User;

// User["name"] 是索引访问类型，意思是“取出 User 里 name 这个属性对应的类型”。
// 所以 UserName 等价于 string。
// 约束：
// - 方括号里必须是 User 已有的键
// - 如果写成 User["age"] 会直接报错，因为 User 没有 age
type UserName = User["name"];

// Nullable<T> 是一个映射类型。
// 含义：把传入对象 T 的每一个属性都改造成“原类型 | null”。
// 例如 Nullable<User> 会变成：
// {
//   id: number | null;
//   name: string | null;
//   active: boolean | null;
// }
//
// 使用到的语法：
// - <T>: 泛型参数，表示这个类型工具可以复用在任何对象类型上
// - keyof T: 取出 T 的所有键
// - [K in keyof T]: 遍历 T 的每一个键，逐个生成新属性
// - T[K]: 取出某个键 K 在 T 中对应的值类型
//
// 约束：
// - 这里默认 T 最好是对象类型
// - 如果 T 不是对象，keyof T 的结果会变得不直观，学习阶段先按对象理解
type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};

// ApiShape<T> 是条件类型。
// 含义：根据 T 是否满足某个条件，返回不同的类型结构。
// 这里的规则是：
// - 如果 T 是 string，则返回 { type: "text"; value: T }
// - 否则返回 { type: "json"; value: T }
//
// 使用到的语法：
// - T extends string ? A : B
//   这里的 extends 不是“继承类”，而是“判断 T 是否可以赋值给 string”
//
// 约束：
// - 这是纯类型层面的判断，不是运行时 if
// - T 不同，最终推导出来的对象形状就不同
type ApiShape<T> = T extends string
  ? { type: "text"; value: T }
  : { type: "json"; value: T };

// ElementType<T> 用来提取数组元素类型。
// 含义：
// - 如果 T 是数组类型，就取出数组里单个元素的类型
// - 如果 T 不是数组，就直接返回 T 本身
//
// 使用到的语法：
// - Array<infer Item>
//   infer 的意思是“让我在条件类型里临时推断出一个类型变量”
//   这里推断出的 Item 就是数组元素类型
//
// 例子：
// - ElementType<number[]> -> number
// - ElementType<string[]> -> string
// - ElementType<boolean> -> boolean
type ElementType<T> = T extends Array<infer Item> ? Item : T;

// Pick<User, "id" | "name"> 是 TypeScript 内置工具类型。
// 含义：从 User 中“挑出” id 和 name 两个属性，组成一个新类型。
// 所以 UserPreview 等价于：
// {
//   id: number;
//   name: string;
// }
//
// 约束：
// - 第二个泛型参数必须是 User 已有的键
// - 如果写 Pick<User, "age"> 会报错
type UserPreview = Pick<User, "id" | "name">;

// Partial<User> 也是内置工具类型。
// 含义：把 User 的所有属性都变成可选。
// 所以 UserPatch 等价于：
// {
//   id?: number;
//   name?: string;
//   active?: boolean;
// }
//
// 常见用途：
// - 更新表单
// - patch 请求
// - 局部更新对象
type UserPatch = Partial<User>;

// Required<User> 是内置工具类型。
// 含义：把一个类型里的所有可选属性都变成必填。
// 当前 User 本来就没有可选属性，所以 Required<User> 看起来和 User 一样。
// 如果原类型里有 ? 属性，这个工具就会把它们都变成必须提供。
type RequiredUser = Required<User>;

// Readonly<User> 是内置工具类型。
// 含义：把 User 的所有属性都变成只读，初始化后不能重新赋值。
// 约束：
// - 它限制的是属性重新赋值
// - 不是深层冻结
type ReadonlyUser = Readonly<User>;

// Record<K, V> 也是很常用的内置工具类型。
// 含义：创建一个“键是 K，值是 V”的对象类型。
// 这里表示：对象的每个键都是 string，每个值都必须是 UserPreview。
//
// 常见用途：
// - 做字典表
// - 做 id -> 数据 的映射
// - 做配置对象
type UserDirectory = Record<string, UserPreview>;

const userKeys: UserKeys[] = ["id", "name", "active"];
const userName: UserName = "Alice";

const nullableUser: Nullable<User> = {
  id: 1,
  name: null,
  active: true
};

const textShape: ApiShape<string> = {
  type: "text",
  value: "hello"
};

const jsonShape: ApiShape<{ ok: true }> = {
  type: "json",
  value: { ok: true }
};

const preview: UserPreview = {
  id: 1,
  name: "Preview"
};

const patch: UserPatch = {
  active: false
};

const requiredUser: RequiredUser = {
  id: 1,
  name: "Required",
  active: true
};

const readonlyUser: ReadonlyUser = {
  id: 2,
  name: "Read only",
  active: true
};

const userDirectory: UserDirectory = {
  first: { id: 1, name: "Alice" },
  second: { id: 2, name: "Bob" }
};

const arrayElement: ElementType<number[]> = 123;

console.log("keys:", userKeys.join(", "));
console.log("userName:", userName);
console.log("nullable user:", nullableUser);
console.log("text shape:", textShape);
console.log("json shape:", jsonShape);
console.log("preview:", preview);
console.log("patch:", patch);
console.log("required user:", requiredUser);
console.log("readonly user:", readonlyUser);
console.log("user directory:", userDirectory);
console.log("array element:", arrayElement);

/*
易混点：
- keyof 是“取键名联合”，不是取值。
- T[K] 是“按键取属性类型”，不是取运行时值。
- 映射类型适合做“批量变换”，比如把所有属性变可选、只读、可空。
- 条件类型常用于根据输入类型返回不同的输出类型。
- Pick / Partial / Required / Readonly / Record 都是 TypeScript 内置工具类型，本质上是在帮你复用常见类型变换。
- Record 适合“键值字典”场景；Pick 适合“从已有对象类型里裁剪字段”。
*/

export {};
