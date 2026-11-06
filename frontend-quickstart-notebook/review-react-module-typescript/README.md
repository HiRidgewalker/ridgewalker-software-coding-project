# React Review Project

这个目录是一个基于 `Vite + React + TypeScript` 搭建的复习型项目，目标不是做业务页面，而是把 React 常用方法、常用特性、路由和状态管理放进一个可运行的示例里。

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

- `src/pages/BasicsPage.tsx`

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

- `src/pages/HooksPage.tsx`
- `src/pages/LifecyclePage.tsx`
- `src/pages/AdvancedPage.tsx`
- `src/context/ThemeContext.tsx`

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

- `src/main.tsx`
- `src/App.tsx`
- `src/pages/LifecyclePage.tsx`
- `src/components/ErrorBoundary.tsx`
- `src/components/PortalModal.tsx`
- `src/components/LazyPanel.tsx`

### 4. 生命周期、渲染流程与父子更新顺序

项目里新增了一页专门讲这些内容：

- `src/pages/LifecyclePage.tsx`

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

- `src/router.tsx`
- `src/main.tsx`
- `src/App.tsx`

## Zustand 是什么

`Zustand` 是一个轻量级状态管理库，用来管理“多个组件共享的数据”。

它比 Redux 更轻，学习成本更低，适合你现在这种“先理解状态管理核心思路”的阶段。

这个项目里 Zustand 的核心文件是：

- `src/store/useReviewStore.ts`
- `src/pages/ZustandPage.tsx`
