// JavaScript 常用容器类型回顾
// 运行方式: node 03-common-containers.js

function section(title) {
  console.log(`\n=== ${title} ===`);
}

section("Object");
const user = {
  name: "Alice",
  age: 20,
  city: "Shanghai",
};

console.log("对象:", user);
console.log("读取属性:", user.name);
user.job = "Developer";
console.log("新增属性后:", user);
console.log("keys:", Object.keys(user));
console.log("values:", Object.values(user));
console.log("entries:", Object.entries(user));

section("Array");
const fruits = ["apple", "banana", "orange"];
console.log("数组:", fruits);
console.log("通过下标访问:", fruits[1]);
console.log("包含 banana:", fruits.includes("banana"));

section("Set");
const numbers = new Set([1, 2, 2, 3, 3, 4]);
console.log("Set 自动去重:", numbers);
numbers.add(5);
numbers.delete(2);
console.log("修改后:", numbers);
console.log("has(3):", numbers.has(3));
console.log("size:", numbers.size);
console.log("转数组:", Array.from(numbers));

section("Map");
const scoreMap = new Map();
scoreMap.set("Tom", 90);
scoreMap.set("Lucy", 95);
scoreMap.set("Tom", 99);

console.log("Map:", scoreMap);
console.log("get('Tom'):", scoreMap.get("Tom"));
console.log("has('Lucy'):", scoreMap.has("Lucy"));
console.log("size:", scoreMap.size);

for (const [key, value] of scoreMap) {
  console.log(`Map 遍历 -> ${key}: ${value}`);
}

section("WeakSet / WeakMap");
const obj1 = { id: 1 };
const obj2 = { id: 2 };

const weakSet = new WeakSet([obj1]);
weakSet.add(obj2);
console.log("weakSet.has(obj1):", weakSet.has(obj1));

const weakMap = new WeakMap();
weakMap.set(obj1, { cached: true });
console.log("weakMap.get(obj1):", weakMap.get(obj1));

console.log("WeakSet / WeakMap 的键必须是对象，且不可枚举，常用于缓存或私有数据关联。");

section("容器选择建议");
console.log("Object: 适合简单键值对，键通常是字符串或 Symbol。");
console.log("Array: 适合有序数据集合。");
console.log("Set: 适合去重、成员判断。");
console.log("Map: 适合任意类型键的键值对。");
console.log("WeakMap / WeakSet: 适合对象引用相关的临时关联。");
