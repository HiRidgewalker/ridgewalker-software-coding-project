# JavaScript 知识点回顾

这个目录用于回顾常见 JavaScript 基础知识点。每个文件都可以直接运行，适合一边看代码一边看控制台输出。

## 文件说明

### 1. `01-array-methods.js`

回顾数组及常用方法，包括：

- 数组的基础访问与修改
- `push`、`pop`、`shift`、`unshift`
- `forEach`
- `map`、`filter`
- `find`、`findIndex`
- `some`、`every`
- `reduce`
- `slice`、`splice`、`concat`
- `join`、`flat`
- `sort`、`reverse`
- 展开运算符与解构

### 2. `02-error-handling.js`

回顾异常捕获与错误处理，包括：

- `try...catch`
- `throw`
- `Error`
- 自定义错误类型
- `finally`
- `async / await` 中的异常捕获

### 3. `03-common-containers.js`

回顾常用容器类型，包括：

- `Object`
- `Array`
- `Set`
- `Map`
- `WeakSet`
- `WeakMap`

### 4. `04-class-and-object.js`

回顾类和对象相关知识点，包括：

- 对象字面量
- 属性访问与动态新增属性
- 工厂函数
- `class`
- `constructor`
- `this`
- `new`
- 实例方法
- `instanceof`
- `extends`
- `super`

## 运行方式

在当前目录下执行：

```bash
node 01-array-methods.js
node 02-error-handling.js
node 03-common-containers.js
node 04-class-and-object.js
```

如果你想更系统地复习，可以按下面顺序看：

1. 先看数组操作，因为这是最常用的数据结构。
2. 再看异常捕获，理解代码出错时如何处理。
3. 再看类和对象，理解 `new`、实例、继承这些概念。
4. 最后看不同容器类型，建立“什么时候该用什么”的意识。

## 复习建议

- 不只看输出，建议自己修改示例数据再运行一遍。
- 可以把每个方法的返回值和是否修改原数组单独总结出来。
- `Map` 和 `Object`、`Set` 和 `Array` 的区别建议重点比较。
