/*
基础类型与类型推断

这部分回答两个最基础的问题：
1. TypeScript 能给哪些值标类型？
2. 如果我不写类型，TypeScript 会帮我推断到什么程度？
*/

const courseName: string = "TypeScript review";
const lessonCount: number = 8;
const isUseful: boolean = true;

const tags: string[] = ["types", "generics", "narrowing"];
const scores: Array<number> = [90, 95, 100];

const point: [number, number] = [120, 240];

// 不显式标注时，TypeScript 会根据初始化值进行推断。
const author = "Limber";
let progress = 0;

progress += 1;

// const 推断通常更窄，let 推断通常更宽。
const fixedStatus = "draft";
let mutableStatus = "draft";

type Status = "draft" | "published";

const articleStatus: Status = fixedStatus;
mutableStatus = "published";

const user = {
  id: 1,
  name: "Ada",
  active: true
};

// 如果需要更精确的字面量约束，可以使用 as const。
const requestConfig = {
  method: "GET",
  retry: 3
} as const;

function summarizeReview() {
  const summary = [
    `course: ${courseName}`,
    `lessons: ${lessonCount}`,
    `useful: ${isUseful}`,
    `author: ${author}`,
    `progress: ${progress}`,
    `status: ${articleStatus}`,
    `user: ${user.name}`,
    `request method: ${requestConfig.method}`,
    `point: ${point[0]}, ${point[1]}`
  ];

  console.log(summary.join(" | "));
  console.log("tags:", tags.join(", "));
  console.log("scores:", scores.join(", "));
}

summarizeReview();

/*
易混点：
- tuple 不是“随便放几个值的数组”，而是“每个位置都有约束”的数组。
- as const 会把值推断得更窄，并把对象属性和数组内容变成只读。
- TypeScript 的推断很强，但复杂场景下仍要主动写类型，让意图更清晰。
*/

/*
TypeScript 原生常见类型速查：
- number: 数字，包含整数、浮点数、NaN、Infinity
- string: 字符串
- boolean: 布尔值
- null: 空值
- undefined: 未定义
- bigint: 大整数
- symbol: 唯一标识
- object: 非原始类型对象
- Array<T> / T[]: 数组，例如 Array<number>、string[]
- [T1, T2]: 元组，例如 [number, string]
- { name: string; age: number }: 对象类型
- (a: number, b: number) => number: 函数类型
- "a" | "b": 联合类型
- type Status = "draft" | "published": 类型别名
- interface User { name: string }: 接口
- unknown: 安全的未知类型，使用前必须先收窄
- any: 任意类型，会放弃类型检查
- never: 不会出现的类型，常用于抛错函数或穷尽检查
- void: 没有返回值，常用于函数返回类型
- literal type: 字面量类型，例如 "GET"、200、true
*/

export {};
