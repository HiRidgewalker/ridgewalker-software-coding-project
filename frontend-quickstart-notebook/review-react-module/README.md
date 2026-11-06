# React Review Project

这个目录是一个基于 `Vite + React + JavaScript` 搭建的复习型项目，目标不是做业务页面，而是把 React 常用方法、常用特性、路由和状态管理放进一个可运行的示例里。

## 启动方式

```bash
npm install
npm run dev
```

构建生产包：

```bash
npm run build
```

## 项目中覆盖的 React 知识点

### 1. 基础语法与组件能力

- JSX
- 函数组件
- `props`
- `children`
- 事件处理，例如 `onClick`、`onChange`
- 条件渲染
- 列表渲染与 `key`
- 受控表单

对应页面：

- `src/pages/BasicsPage.jsx`

### 2. 常用 Hooks

- `useState`
- `useEffect`
- `useRef`
- `useReducer`
- `useId`
- `useContext`
- `useEffectEvent`
- `useTransition`
- `useDeferredValue`

对应页面：

- `src/pages/HooksPage.jsx`
- `src/pages/LifecyclePage.jsx`
- `src/pages/AdvancedPage.jsx`
- `src/context/ThemeContext.jsx`

### 3. React 常用特性

- `StrictMode`
- 路由嵌套渲染
- `Outlet`
- 错误边界 `ErrorBoundary`
- `createPortal`
- `lazy`
- `Suspense`
- Context 跨层级共享数据
- 生命周期观察
- 父子组件更新顺序

对应文件：

- `src/main.jsx`
- `src/App.jsx`
- `src/pages/LifecyclePage.jsx`
- `src/components/ErrorBoundary.jsx`
- `src/components/PortalModal.jsx`
- `src/components/LazyPanel.jsx`

### 4. 生命周期、渲染流程与父子更新顺序

项目里新增了一页专门讲这些内容：

- `src/pages/LifecyclePage.jsx`

这页主要覆盖：

- 挂载 `mount`
- 更新 `update`
- 卸载 `unmount`
- `useEffect` 的执行与清理
- render 阶段和 commit 阶段的区别
- 父组件更新时对子组件的影响
- `StrictMode` 在开发环境下的额外检查行为

## 使用了哪一个路由方案

这个项目使用的是 `react-router-dom`，具体是：

- `createBrowserRouter`
- `RouterProvider`
- `NavLink`
- `Link`
- `Outlet`

核心入口文件：

- `src/router.jsx`
- `src/main.jsx`
- `src/App.jsx`

这套方案的含义是：

- `createBrowserRouter` 负责定义路由表
- `RouterProvider` 负责把路由能力挂到整个应用上
- `NavLink` 适合做导航菜单，因为它能自动识别当前是否激活
- `Link` 适合做普通跳转
- `Outlet` 是子路由的渲染占位符

## Zustand 是什么

`Zustand` 是一个轻量级状态管理库，用来管理“多个组件共享的数据”。

它比 Redux 更轻，学习成本更低，适合你现在这种“先理解状态管理核心思路”的阶段。

这个项目里 Zustand 的核心文件是：

- `src/store/useReviewStore.js`
- `src/pages/ZustandPage.jsx`

## Zustand 在这个项目里怎么使用

### 1. 创建 store

在 `src/store/useReviewStore.js` 里：

```js
import { create } from 'zustand'

export const useReviewStore = create((set) => ({
  count: 1,
  increment: () => set((state) => ({ count: state.count + 1 })),
}))
```

理解方式：

- `create(...)` 会创建一个 store hook
- `count` 是全局状态
- `increment` 是修改状态的方法
- `set(...)` 用来更新 store

### 2. 在组件里读取状态

```js
const count = useReviewStore((state) => state.count)
```

这里的 `(state) => state.count` 叫做 `selector`，也就是“只取我需要的那部分状态”。

### 3. 在组件里调用 action 修改状态

```js
const increment = useReviewStore((state) => state.increment)
increment()
```

也就是说：

- 状态和动作都从同一个 store hook 中取出来
- 组件不需要额外写 Provider
- 使用方式比 Redux 更直接

### 4. 为什么推荐你先学 Zustand

因为它有几个优点：

- API 少，容易记
- 不需要写太多模板代码
- 不强制你拆 action type、reducer、dispatch 那一整套
- 对小到中型 React 项目非常实用

## 阅读建议

推荐顺序：

1. 先看 `src/pages/BasicsPage.jsx`
2. 再看 `src/pages/HooksPage.jsx`
3. 再看 `src/pages/LifecyclePage.jsx`
4. 再看 `src/pages/AdvancedPage.jsx`
5. 最后看 `src/pages/ZustandPage.jsx`

如果你对 `new`、类、对象、实例这些概念还不熟，建议你先配合 `review-javascript-module` 里的类和对象示例一起看，这样更容易理解：

- 为什么 `ErrorBoundary` 要写成类组件
- 为什么 `new Error(...)` 会得到一个错误对象实例
- 为什么 `instanceof` 可以判断实例类型

## 额外说明

- 项目中的注释写得比较细，适合边跑边看。
- 这不是 React API 的“绝对全集”，但覆盖了前端日常开发里最常见、最值得先掌握的一批能力。

## 项目目录与文件说明

下面是这个项目里主要文件和文件夹的职责说明。

### 根目录

- `package.json`
  项目的依赖和脚本配置文件，例如 `npm run dev`、`npm run build` 都定义在这里。
- `vite.config.js`
  Vite 的配置文件。
- `index.html`
  整个 React 应用挂载的 HTML 模板，`src/main.jsx` 会把 React 渲染到这里的 `#root` 节点。
- `README.md`
  当前这份项目说明文档。
- `public/`
  放不会经过打包模块系统处理的静态资源。

### src 目录

- `src/main.jsx`
  React 应用入口。这里负责挂载 React、开启 `StrictMode`、接入路由、接入全局 ThemeProvider。
- `src/App.jsx`
  应用整体布局组件。这里主要放侧边导航和 `Outlet`，相当于整个项目的页面壳子。
- `src/router.jsx`
  路由表配置文件，定义各个页面路径和它们对应的页面组件。
- `src/index.css`
  全局样式文件。

### src/pages

这个目录放的是“页面级组件”。

页面级组件的特点是：

- 通常会直接对应一个路由地址
- 一般内容更完整，包含一整块页面结构
- 经常会组合多个小组件

当前有这些页面文件：

- `src/pages/HomePage.jsx`
  首页，总览项目覆盖的 React 知识点。
- `src/pages/BasicsPage.jsx`
  基础语法页，讲 JSX、props、children、列表渲染、条件渲染、表单等。
- `src/pages/HooksPage.jsx`
  常用 Hooks 页。
- `src/pages/LifecyclePage.jsx`
  生命周期、渲染流程、父子组件更新顺序演示页。
- `src/pages/AdvancedPage.jsx`
  Context、错误边界、Portal、lazy、Suspense 等特性页。
- `src/pages/ZustandPage.jsx`
  Zustand 状态管理演示页。
- `src/pages/RouteErrorPage.jsx`
  路由错误页，当路由渲染异常时会显示这个页面。

### src/components

这个目录放的是“可复用组件”。

可复用组件的特点是：

- 不一定直接对应路由
- 更偏向局部 UI 或局部功能
- 可能被多个页面共同使用

当前有这些组件文件：

- `src/components/SectionCard.jsx`
  用于统一每个知识点板块的卡片结构。
- `src/components/ErrorBoundary.jsx`
  错误边界组件，用来捕获其子树中的渲染错误。
- `src/components/PortalModal.jsx`
  基于 `createPortal` 的弹窗组件。
- `src/components/LazyPanel.jsx`
  用于演示 `React.lazy` 和 `Suspense` 的懒加载组件。

### src/context

- `src/context/ThemeContext.jsx`
  放 Context 相关内容。这里定义了 `ThemeContext`、`ThemeProvider` 和 `useTheme`。

### src/store

- `src/store/useReviewStore.js`
  Zustand store 文件。这里集中定义全局状态和更新动作。

## 为什么有些 JSX 文件放在 components，有些放在 pages

可以用一个很实用的判断标准：

- 如果这个 JSX 文件代表“一个完整页面”，并且通常会对应一个路由地址，就放到 `pages/`
- 如果这个 JSX 文件只是“页面中的一小块可复用 UI 或功能单元”，就放到 `components/`

例如：

- `BasicsPage.jsx` 是一个完整页面，所以放到 `pages/`
- `SectionCard.jsx` 只是一个可复用卡片外壳，所以放到 `components/`
- `ZustandPage.jsx` 是一个完整的教学页，所以放到 `pages/`
- `PortalModal.jsx` 是一个弹窗组件，可能在多个页面复用，所以放到 `components/`

你可以先把它们理解成：

- `pages` 负责“页面组织”
- `components` 负责“局部复用”

这是 React 项目里非常常见的一种目录拆分方式。对于当前这个复习项目，这样拆分已经足够清晰，也方便后续继续扩展新的知识点页面。

## 在真实 React 项目里，`context/`、`store/`、`hooks/`、`utils/` 通常怎么划分

下面这几个目录不是每个项目都必须有，但在中型及以上项目里很常见。

### `context/`

这个目录通常放 React Context 相关内容。

适合放进 `context/` 的内容：

- `ThemeContext`
- `AuthContext`
- `LocaleContext`
- 一些需要跨层级共享、但又不算复杂状态管理的数据

适合用 `context/` 的场景：

- 主题切换
- 语言切换
- 登录用户信息
- 权限信息

不太适合用 `context/` 的场景：

- 更新频繁的大量业务状态
- 结构复杂、联动很多的全局状态

因为 Context 更偏向“共享值传递”，不是专门为复杂状态流设计的。

### `store/`

这个目录通常放全局状态管理相关代码。

如果项目用了 Zustand、Redux、Jotai、MobX，一般都会有类似目录。

适合放进 `store/` 的内容：

- 全局状态定义
- 修改状态的方法
- 状态切片
- store 组合逻辑

例如当前项目中的：

- `src/store/useReviewStore.js`

它就属于很典型的 `store/` 文件，因为它专门负责管理跨组件共享的数据。

你可以把 `store/` 理解成：

- 专门放“全局状态中心”的地方

### `hooks/`

这个目录通常放“自定义 Hook”。

所谓自定义 Hook，就是把一段可复用的状态逻辑提取成函数，并且函数名通常以 `use` 开头。

例如：

- `useTheme`
- `useDebounce`
- `useUserProfile`
- `useTodoFilter`
- `useWindowSize`

适合放进 `hooks/` 的内容：

- 可复用的状态逻辑
- 可复用的副作用逻辑
- 对浏览器 API 的封装
- 对业务逻辑的组合封装

不适合放进 `hooks/` 的内容：

- 单纯的 UI 组件
- 单纯的工具函数
- 没有用到 React Hook 能力的普通函数

一个很好记的判断标准是：

- 如果它内部用到了 `useState`、`useEffect`、`useContext` 等 Hook，并且希望被多个组件复用，就很适合放进 `hooks/`

### `utils/`

这个目录通常放“纯工具函数”。

工具函数的特点是：

- 通常不依赖 React
- 输入固定，输出固定
- 可以单独测试

适合放进 `utils/` 的内容：

- 日期格式化
- 金额格式化
- 数组处理
- 字符串处理
- 请求参数转换
- 通用校验函数

例如这类函数通常会放进 `utils/`：

```js
export function formatPrice(value) {
  return `¥${Number(value).toFixed(2)}`
}
```

因为它和 React 组件无关，本质上只是一个普通 JavaScript 工具函数。

## 一套很实用的目录判断方法

当你写一个新文件时，可以按下面的顺序判断它应该放哪：

1. 它是不是一个完整页面，并且通常对应一个路由？
   是的话，放 `pages/`

2. 它是不是一个可复用的 UI 组件？
   是的话，放 `components/`

3. 它是不是一段可复用的 React 状态逻辑？
   是的话，放 `hooks/`

4. 它是不是全局共享状态的定义中心？
   是的话，放 `store/`

5. 它是不是跨层级共享值的 Context 定义？
   是的话，放 `context/`

6. 它是不是和 React 无关的普通工具函数？
   是的话，放 `utils/`

## 对当前这个项目的延伸建议

如果后面你继续扩展这个复习项目，可以考虑再新增这些目录：

- `src/hooks/`
  用来放自定义 Hook，例如 `usePageTitle.js`、`useToggle.js`
- `src/utils/`
  用来放纯工具函数，例如日志格式化、演示数据转换

当前项目规模还不大，所以暂时没有强行把目录拆得特别细，这是刻意保持简单。等你开始增加更多页面、更多逻辑时，再把 `hooks/` 和 `utils/` 单独抽出来会更合适。
