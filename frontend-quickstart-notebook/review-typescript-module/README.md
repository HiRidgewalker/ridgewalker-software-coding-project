# TypeScript Review Notes

这是一套从零整理的 TypeScript 回顾材料，目标不是堆概念，而是把常见知识点拆成可以直接阅读、运行和对照的示例文件。

## 学习顺序

1. `src/01-primitives-and-inference.ts`
   - 基础类型、类型标注、类型推断
2. `src/02-functions-and-objects.ts`
   - 函数、对象、可选属性、只读属性
3. `src/03-unions-and-narrowing.ts`
   - 联合类型、字面量类型、控制流收窄
4. `src/04-aliases-interfaces-and-enums.ts`
   - 类型别名、接口、枚举与替代方案
5. `src/05-generics.ts`
   - 泛型、约束、默认类型参数
6. `src/06-advanced-types.ts`
   - `keyof`、索引访问类型、映射类型、条件类型、工具类型
7. `src/07-classes.ts`
   - 类、访问修饰符、抽象类、接口实现
8. `src/08-modules-and-declarations.ts`
   - 模块、类型导入导出、声明文件、`any` / `unknown` / `never`

## 阅读方式

- 每个文件都按“问题 -> 示例 -> 易混点”的思路组织。
- 先运行代码看行为，再结合注释理解类型系统为什么这样限制。
- 示例尽量保持可执行；涉及报错的错误写法会用注释展示，不影响整体编译。

## 运行方式

先安装依赖：

```bash
npm install
```

类型检查：

```bash
npm run check
```

编译到 `dist`：

```bash
npm run build
```

如果你只想看某个文件的运行结果，可以在编译后用 Node 运行对应产物，例如：

```bash
node dist/01-primitives-and-inference.js
```

## 重点提醒

- TypeScript 不是“给 JavaScript 加注释”，它的核心价值是用类型系统描述数据约束和程序意图。
- 你最需要建立的心智图不是“语法列表”，而是“如何给值、函数、对象、模块建模”。
- 学到后半段时，始终回头问自己：这个特性能解决什么真实建模问题？
