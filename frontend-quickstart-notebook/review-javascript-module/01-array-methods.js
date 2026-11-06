// JavaScript 数组与常用方法回顾
// 运行方式: node 01-array-methods.js

function section(title) {
  console.log(`\n=== ${title} ===`);
}

const numbers = [1, 2, 3, 4, 5];

section("基础访问与变更");
console.log("原数组:", numbers);
console.log("长度:", numbers.length);
console.log("第一个元素:", numbers[0]);

const mutable = ["a", "b"];

// push: 在数组末尾添加元素，返回新数组长度，会修改原数组。
mutable.push("c");
console.log("push 后:", mutable);

// pop: 删除数组最后一个元素，返回被删除的元素，会修改原数组。
const lastItem = mutable.pop();
console.log("pop 返回值:", lastItem);
console.log("pop 后:", mutable);

// unshift: 在数组开头添加元素，返回新数组长度，会修改原数组。
mutable.unshift("start");

// 这里再次使用 push，演示从尾部继续追加元素。
mutable.push("end");
console.log("unshift / push 后:", mutable);

// shift: 删除数组第一个元素，返回被删除的元素，会修改原数组。
const firstItem = mutable.shift();
console.log("shift 返回值:", firstItem);
console.log("shift 后:", mutable);

section("遍历");

// forEach: 遍历数组每一项，常用于执行副作用操作；返回值始终是 undefined。
numbers.forEach(function (item, index) {
  console.log(`forEach -> index=${index}, item=${item}`);
});

section("映射、过滤、查找");

// map: 对每一项做映射，返回一个等长新数组，不修改原数组。
const doubled = numbers.map(function (item) {
  return item * 2;
});
console.log("map:", doubled);

// filter: 按条件筛选元素，返回满足条件的新数组，不修改原数组。
const evens = numbers.filter(function (item) {
  return item % 2 === 0;
});
console.log("filter:", evens);

// find: 返回第一个满足条件的元素；如果找不到，返回 undefined。
const firstGreaterThanThree = numbers.find(function (item) {
  return item > 3;
});
console.log("find:", firstGreaterThanThree);

// findIndex: 返回第一个满足条件元素的下标；如果找不到，返回 -1。
const firstIndexGreaterThanThree = numbers.findIndex(function (item) {
  return item > 3;
});
console.log("findIndex:", firstIndexGreaterThanThree);

section("判断");

// some: 只要有一项满足条件就返回 true，常用于“是否存在”判断。
const hasEven = numbers.some(function (item) {
  return item % 2 === 0;
});
console.log("some:", hasEven);

// every: 只有全部满足条件才返回 true，常用于“是否全部符合”判断。
const allPositive = numbers.every(function (item) {
  return item > 0;
});
console.log("every:", allPositive);

section("归并");

// reduce: 将数组归并为一个结果；accumulator 是累计值，0 是初始值。
const sum = numbers.reduce(function (accumulator, item) {
  return accumulator + item;
}, 0);
console.log("reduce 求和:", sum);

section("截取与拼接");

// slice(start, end): 截取指定范围，左闭右开，返回新数组，不修改原数组。
const sliceResult = numbers.slice(1, 4);
console.log("slice(1, 4):", sliceResult);
console.log("slice 不会修改原数组:", numbers);

const spliceSource = [10, 20, 30, 40];

// splice(start, deleteCount, ...items):
// 从指定位置删除/替换/插入元素，返回被删除的元素数组，会修改原数组。
const removed = spliceSource.splice(1, 2, 200, 300);
console.log("splice 删除项:", removed);
console.log("splice 后:", spliceSource);

// concat: 连接多个数组或元素，返回新数组，不修改原数组。
const merged = numbers.concat([6, 7], [8]);
console.log("concat:", merged);

section("转换");

// join(separator): 按指定分隔符把数组拼接成字符串。
console.log("join:", numbers.join(" - "));
console.log("join:", numbers.join(" * "));

const nested = [1, [2, 3], [4, [5]]];

// flat(depth): 按指定深度扁平化数组，返回新数组，不修改原数组。
console.log("flat(1):", nested.flat());
console.log("flat(2):", nested.flat(2));

section("排序与反转");
const names = ["Tom", "Alice", "Bob"];

// sort: 默认按字符串编码顺序排序，会修改原数组。
// 这里先用 slice() 拷贝一份，避免直接改动 names。
console.log("默认 sort:", names.slice().sort());

const unordered = [10, 2, 30, 4];

// sort(compareFn): 数字排序时通常需要比较函数。
// a - b 表示升序，b - a 表示降序。
const sortedNumbers = unordered.slice().sort(function (a, b) {
  return a - b;
});
console.log("数字升序排序:", sortedNumbers);

// reverse: 反转数组顺序，会修改原数组。
// 这里先 slice() 复制后再反转，避免影响 sortedNumbers。
console.log("reverse:", sortedNumbers.slice().reverse());

section("展开运算符与解构");

// ... 可用于展开数组，常见于复制、拼接、传参。
const copied = [...numbers];
const appended = [...numbers, 6, 7];
console.log("拷贝:", copied);
console.log("追加新元素:", appended);

// 解构赋值: 按位置提取数组元素，rest 收集剩余项。
const [first, second, ...rest] = appended;
console.log("解构 first:", first);
console.log("解构 second:", second);
console.log("剩余项 rest:", rest);

section("数组转字符串后再处理");
const sentence = "js,array,practice";

// split: 字符串方法，按分隔符拆分后返回数组。
const parts = sentence.split(",");
console.log("split:", parts);

// toString: 数组转字符串，默认以逗号连接。
console.log("toString:", parts.toString());

section("小结");
console.log("数组常见操作可以概括为: 增删改查、遍历、转换、归并、排序。");
