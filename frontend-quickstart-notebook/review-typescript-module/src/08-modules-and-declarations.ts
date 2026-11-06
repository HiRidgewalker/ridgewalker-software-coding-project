/*
模块与声明文件

这部分关注 TypeScript 如何和文件、库、未知输入协作。
*/

import { sum } from "./math-utils";
import type { MathResult } from "./math-utils";

const result: MathResult = {
  label: "sum result",
  value: sum(4, 5)
};

function parseExternalValue(value: unknown): string {
  if (typeof value === "string") {
    return value.toUpperCase();
  }

  if (typeof value === "number") {
    return `number:${value}`;
  }

  return "unsupported";
}

function fail(message: string): never {
  throw new Error(message);
}

function readConfig(source: unknown): { mode: string } {
  if (
    typeof source === "object" &&
    source !== null &&
    "mode" in source &&
    typeof source.mode === "string"
  ) {
    return { mode: source.mode };
  }

  return fail("invalid config");
}

let flexibleValue: any = { topic: "typescript" };
flexibleValue = 123;

console.log(result.label, result.value);
console.log(parseExternalValue("hello"));
console.log(parseExternalValue(42));
console.log("config:", readConfig({ mode: "strict" }));
console.log("any value:", flexibleValue);

/*
易混点：
- import type 只导入类型，不会参与运行时代码。
- unknown 比 any 更安全，因为你必须先判断再使用。
- never 通常表示“不会正常返回”的函数，或在穷尽检查里表示不该出现的分支。
- .d.ts 不提供实现，只提供类型描述，用来告诉 TypeScript 某个外部模块长什么样。
*/

export {};
