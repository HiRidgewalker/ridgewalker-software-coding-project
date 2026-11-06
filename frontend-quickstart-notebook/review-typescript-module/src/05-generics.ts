/*
泛型

泛型的目标不是“写得高级”，而是“让类型信息跟着输入一起流动到输出”。
*/

function firstItem<T>(items: T[]): T | undefined {
  return items[0];
}

function wrapValue<T>(value: T): { value: T } {
  return { value };
}

function mergeObjects<T extends object, U extends object>(a: T, b: U): T & U {
  return { ...a, ...b };
}

type ApiResult<TData = string> = { // 默认泛型参数, 如果调用时不指定类型参数，就用 string 作为 TData 的类型。
  success: boolean;
  data: TData;
};

function pickProperty<T, K extends keyof T>(obj: T, key: K): T[K] { // K extends keyof T 表示 K 必须是 T 的一个键。
  return obj[key];
}

const firstNumber = firstItem([10, 20, 30]);
const firstWord = firstItem(["ts", "js"]);
const wrapped = wrapValue({ topic: "generics", hard: true });
const merged = mergeObjects({ id: 1, name: "Ada" }, { role: "admin" });

const defaultResult: ApiResult = {
  success: true,
  data: "done"
};

const userResult: ApiResult<{ id: number; name: string }> = {
  success: true,
  data: { id: 1, name: "Alice" }
};

console.log("first number:", firstNumber);
console.log("first word:", firstWord);
console.log("wrapped topic:", wrapped.value.topic);
console.log("merged role:", merged.role);
console.log("default result:", defaultResult.data);
console.log("user name:", pickProperty(userResult.data, "name"));

/*
易混点：
- 泛型不是 `any`。`any` 会丢失信息，泛型会保留信息。
- `extends` 在泛型里常表示“约束”，不是类继承那种语义。
- 默认泛型参数适合给常见情况一个默认类型，减少调用噪音。
*/

export {};
