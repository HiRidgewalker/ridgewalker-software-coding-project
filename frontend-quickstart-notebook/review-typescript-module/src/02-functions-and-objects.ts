/*
函数和对象建模

JavaScript 里函数和对象很自由，TypeScript 的重点是把这种自由描述清楚：
- 函数接收什么参数，返回什么结果
- 对象有哪些属性，哪些可选，哪些只读
- ts中type只有一种用法，就是类型别名
*/

type User = {
  id: number;
  name: string; // 必需属性
  nickname?: string; // 可选属性
  readonly createdAt: Date; // 只读属性
};

function greetUser(user: User): string {
  const displayName = user.nickname ?? user.name; // a ?? b； 如果 a 是 null 或 undefined，就用 b
  return `Hello, ${displayName}`;
}

function add(a: number, b: number): number {
  return a + b;
}

function logMessage(message: string, prefix = "INFO"): void { // void 表示没有返回值
  console.log(`[${prefix}] ${message}`);
}

function formatUser(
  name: string,
  age?: number,
  city: string = "Unknown"
): string {
  return age === undefined
    ? `${name} from ${city}`
    : `${name} is ${age} years old and lives in ${city}`;
}

type Point = {
  x: number;
  y: number;
};

function distanceFromOrigin({ x, y }: Point): number {
  return Math.sqrt(x * x + y * y);
}

const currentUser: User = {
  id: 1,
  name: "Alice",
  nickname: "Ali",
  createdAt: new Date("2026-03-30")
};

console.log(greetUser(currentUser));
console.log("2 + 3 =", add(2, 3));
logMessage("functions can have typed params and return values");
console.log(formatUser("Bob"));
console.log(formatUser("Carol", 18, "Shanghai"));
console.log("distance:", distanceFromOrigin({ x: 3, y: 4 }));

/*
易混点：
- 可选参数 `age?: number` 的真实含义是“可能是 number，也可能缺失”。
- readonly 限制的是属性重新赋值，不是对象内部所有深层结构都自动冻结。
- 为函数显式写返回值，不只是为了编译器，也是为了让维护者一眼看懂接口。
*/
