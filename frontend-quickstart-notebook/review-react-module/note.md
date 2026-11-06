# React 笔记

## 1. `map` + JSX 为什么能直接渲染列表

示例代码：

```jsx
{filteredTopics.map((topic) => (
  <li key={topic}>{topic}</li>
))}
```

### 核心原理

- `filteredTopics` 是一个数组
- `map` 会遍历数组中的每一项
- 每遍历一项，就执行一次回调函数
- 回调函数返回什么，`map` 就会把这些返回值收集成一个新数组

所以这段代码本质上会得到一个“由多个 JSX 元素组成的数组”。

可以粗略理解成：

```jsx
[
  <li key="a">a</li>,
  <li key="b">b</li>,
  <li key="c">c</li>
]
```

而 React 支持直接渲染 JSX 数组，所以这些 `<li>` 会被依次渲染到页面中。

### 为什么这里没有看到 `return`

因为这里用的是箭头函数的“简写返回”。

当前写法：

```jsx
(topic) => (
  <li key={topic}>{topic}</li>
)
```

只要箭头函数后面不是用 `{}` 包裹函数体，而是直接跟一个表达式，就会自动返回这个表达式。

它等价于：

```jsx
(topic) => {
  return <li key={topic}>{topic}</li>
}
```

### 什么时候必须写 `return`

如果你把箭头函数写成这样：

```jsx
filteredTopics.map((topic) => {
  <li key={topic}>{topic}</li>
})
```

那就不会自动返回，因为 `{}` 表示函数体。

这种情况下必须显式写 `return`：

```jsx
filteredTopics.map((topic) => {
  return <li key={topic}>{topic}</li>
})
```

### 一句话记忆

- 箭头函数后面直接跟表达式：自动返回
- 箭头函数后面是 `{}`：通常需要手动写 `return`
- `map` 返回的是一个新数组
- React 可以直接渲染 JSX 数组

## 2. React 事件回调函数和 `event` 是什么

示例代码：

```jsx
<button onClick={() => setShowTips((currentValue) => !currentValue)}>
  切换提示显示状态
</button>
```

### 核心原理

- `onClick`、`onChange`、`onSubmit` 这类写法，本质上是在给 JSX 元素绑定事件处理函数
- `onClick={...}` 里面放的必须是一个函数
- React 不会在渲染时直接执行它，而是等事件真正发生时再调用

例如：

```jsx
<button onClick={handleClick}>点击</button>
```

这里表示：

- 把 `handleClick` 作为点击事件处理函数传给 React
- 当按钮被点击时，React 再调用这个函数

### 为什么常看到箭头函数

很多时候你会看到这种写法：

```jsx
<button onClick={() => console.log('clicked')}>点击</button>
```

这是因为箭头函数本身也是函数，可以直接作为事件回调。

它的好处是：

- 可以在事件触发时再执行逻辑
- 可以顺手传额外参数
- 可以把一些简单逻辑直接写在 JSX 里

### `event` 是什么

如果事件回调函数声明了参数，React 会把“事件对象”传进来。

例如：

```jsx
<button onClick={(event) => console.log(event)}>点击</button>
```

这里的 `event` 表示这次点击事件对应的信息对象。

你可以把它理解成：

- React 在事件触发时，自动帮你创建并传入一个事件对象
- 这个对象里包含当前事件的各种信息

常用属性和方法有：

- `event.type`
  事件类型，例如 `click`、`change`
- `event.target`
  真正触发事件的元素
- `event.currentTarget`
  当前绑定事件的元素
- `event.preventDefault()`
  阻止默认行为
- `event.stopPropagation()`
  阻止事件冒泡

例如输入框中很常见：

```jsx
<input onChange={(event) => setKeyword(event.target.value)} />
```

这里的 `event.target.value` 就是输入框当前值。

### 是否还有其他参数可以自动接收

默认情况下，React 自动传给事件处理函数的核心参数就是 `event`。

也就是说，像这样：

```jsx
<button onClick={(event) => console.log(event)}>点击</button>
```

这里自动得到的是事件对象。

React 不会自动再给你传第二个、第三个业务参数。

### 如果我想传额外参数怎么办

如果你想传自己的参数，需要手动包一层箭头函数。

例如：

```jsx
<button onClick={(event) => handleClick('React', event)}>点击</button>
```

然后：

```jsx
function handleClick(name, event) {
  console.log(name)
  console.log(event)
}
```

这里：

- `'React'` 是你手动传入的参数
- `event` 是 React 自动传入的事件对象

### 常见误区

错误写法：

```jsx
<button onClick={handleClick()}>点击</button>
```

这会导致组件渲染时就立即执行 `handleClick()`，而不是点击时执行。

正确写法通常是：

```jsx
<button onClick={handleClick}>点击</button>
```

或者：

```jsx
<button onClick={(event) => handleClick(event)}>点击</button>
```

### 一句话记忆

- `onClick` 后面接的是函数
- React 会在事件发生时调用这个函数
- React 默认会传入一个 `event` 对象
- 想传额外参数，需要自己再包一层箭头函数

## 3. 不传参数可以直接写函数名，传参数时为什么要包一层函数

### 不传参数时

如果你不需要自己传参数，可以直接把函数名交给 React：

```jsx
<button onClick={handleClick}>点击</button>
```

这里的意思不是“现在执行 `handleClick`”，而是：

- 把 `handleClick` 这个函数本身传给 React
- 等点击真正发生时，React 再调用它

### 为什么不能写成 `handleClick()`

例如这段通常是错误的：

```jsx
<button onClick={handleClick()}>点击</button>
```

因为 `handleClick()` 表示“立即执行函数”。

也就是说：

- 组件一渲染，这个函数就已经执行了
- `onClick` 拿到的就不是你想要的那个事件回调函数

React 需要的是“一个函数”，不是“函数执行后的结果”。

### 传参数时为什么要包一层

如果你想自己传参数，例如：

```jsx
handleClick('React')
```

这本身就是一次“函数调用”，会立刻执行。

但 React 事件绑定需要的是“先把函数交过去，等点击发生时再执行”。

所以必须包一层函数：

```jsx
<button onClick={() => handleClick('React')}>点击</button>
```

这里的执行顺序是：

- 先把 `() => handleClick('React')` 这个新函数交给 React
- 点击发生时，React 调用这个新函数
- 这个新函数内部再去执行 `handleClick('React')`

### 不一定必须是箭头函数

箭头函数只是最常见写法，本质要求是“包一层函数”。

所以普通函数也可以：

```jsx
<button
  onClick={function () {
    handleClick('React')
  }}
>
  点击
</button>
```

只是箭头函数更简洁，所以开发中通常更常见。

### 如果还要拿 `event`

可以把事件对象也一起接进来：

```jsx
<button onClick={(event) => handleClick('React', event)}>点击</button>
```

这里：

- `'React'` 是你自己传的参数
- `event` 是 React 自动传进来的事件对象

### 一句话记忆

- 不传参数时：`onClick={handleClick}`
- 传参数时：`onClick={() => handleClick('xxx')}`
- 核心不是“要不要括号”，而是“传给 React 的必须是函数，而不是函数执行结果”

## 4. `<aside>` 是什么标签

`<aside>` 是 HTML 的语义化标签，不是 React 专属标签。

它通常表示：

- 侧边内容区域
- 补充说明区域
- 与主内容相关，但不是主线主体的内容

在当前项目的 `src/App.jsx` 中：

```jsx
<aside className="sidebar">
  ...
</aside>
```

它被用来表示左侧导航栏，这种用法很常见，也很合适。

因为页面结构里：

- 左边是辅助导航内容
- 右边才是页面主要内容

所以使用 `<aside>` 比单纯写 `<div>` 更有语义。

### 为什么不用普通 `div`

`<div>` 是没有明确语义的通用容器。

而 `<aside>` 会明确告诉人和浏览器：

- 这是一个侧边区域
- 它通常不是页面最核心的主内容

这样做的好处是：

- 代码可读性更强
- 页面结构更清晰
- 对搜索引擎更友好
- 对屏幕阅读器和无障碍工具更友好

### 常见 HTML 语义化标签

在 React 里写 JSX 时，经常会直接使用这些 HTML 标签：

- `<main>`
  表示页面主要内容区域
- `<section>`
  表示内容分区
- `<article>`
  表示一块可以独立存在的内容
- `<nav>`
  表示导航区域
- `<aside>`
  表示侧边栏或补充区域
- `<header>`
  表示头部区域
- `<footer>`
  表示底部区域

### 当前项目里的结构理解

例如这类结构：

```jsx
<div className="app-shell">
  <aside className="sidebar">...</aside>
  <main className="content-panel">...</main>
</div>
```

可以理解成：

- `aside` 是侧边栏
- `main` 是主内容区域

### 一句话记忆

- `<aside>` 是 HTML 语义化标签
- 常用于侧边栏、补充信息区
- 它和 `div` 最大区别不在样式，而在语义

## 5. `<aside>` 是内联标签还是块标签

`<aside>` 默认是块级元素。

也就是说，它通常会：

- 独占一行
- 可以设置宽高
- 可以作为页面中的一整块区域来布局

所以在当前项目中把它作为左侧侧边栏来使用是合理的。

例如：

```jsx
<aside className="sidebar">
  ...
</aside>
```

这里的 `<aside>` 本身就表示一整块侧边区域。

### 什么是块级元素

块级元素通常有这些特点：

- 默认会从新的一行开始
- 通常会占据父容器一整行的可用宽度
- 可以包含其他块级元素和内联元素

常见块级元素有：

- `<div>`
- `<section>`
- `<article>`
- `<main>`
- `<nav>`
- `<aside>`
- `<p>`

### 什么是内联元素

内联元素通常有这些特点：

- 不会默认换行
- 通常只占自身内容需要的宽度
- 更适合放在一段文本内部

常见内联元素有：

- `<span>`
- `<a>`
- `<strong>`
- `<em>`

### 什么是语义化标签

语义化标签关注的是“这个标签代表什么含义”，不只是“它长什么样”。

例如：

- `<nav>` 表示导航区
- `<main>` 表示主内容区
- `<aside>` 表示侧边补充区
- `<article>` 表示一块独立内容

所以：

- “块级 / 内联” 更偏向默认布局行为
- “语义化标签” 更偏向标签含义

一个标签可以同时具备这两层属性。

例如：

- `<aside>` 是语义化标签
- 同时它默认也是块级元素

### 需要注意的一点

在现代前端开发中，元素最终怎么显示，很多时候由 CSS 的 `display` 决定。

例如即使一个标签默认是块级元素，你也可以通过 CSS 把它改成：

```css
display: inline;
```

或者：

```css
display: flex;
```

所以更准确地说：

- `<aside>` 默认是块级元素
- 但最终显示方式仍然可以被 CSS 改变

### 一句话记忆

- `<aside>` 默认是块级元素
- 它也是语义化标签
- 块级 / 内联 说的是默认布局行为
- 语义化标签说的是标签含义

## 6. `useReducer` 的使用方法和注意点

### `useReducer` 是干什么的

`useReducer` 用来管理“状态变化规则比较明确、更新逻辑比较多”的状态。

你可以先简单理解成：

- `useState` 适合简单状态
- `useReducer` 适合复杂状态

例如：

- 有多个按钮会修改同一份状态
- 一个状态有多种变化方式
- 想把“状态如何变化”集中写在一个地方

这时 `useReducer` 往往比多个 `useState` 更清晰。

### 基本写法

先定义一个 `reducer` 函数：

```jsx
function reducer(state, action) {
  switch (action.type) {
    case 'increment':
      return { total: state.total + 1 }
    case 'decrement':
      return { total: state.total - 1 }
    case 'reset':
      return { total: 0 }
    default:
      return state
  }
}
```

然后在组件中使用：

```jsx
const [reducerState, dispatch] = useReducer(reducer, { total: 2 })
```

这里的含义是：

- `reducer`
  状态变化规则函数
- `{ total: 2 }`
  初始状态
- `reducerState`
  当前状态
- `dispatch`
  用来发出动作，触发状态更新

### `dispatch` 是怎么工作的

例如：

```jsx
dispatch({ type: 'increment' })
```

这表示：

- 发送一个 action
- action 里通常至少有一个 `type`
- React 会把“当前状态 + action”交给 reducer

也就是会执行类似：

```jsx
reducer(currentState, { type: 'increment' })
```

然后 reducer 返回新状态，组件再重新渲染。

### 使用流程

可以按下面顺序理解：

1. 定义 reducer
   reducer 接收 `state` 和 `action`

2. 调用 `useReducer(reducer, initialState)`
   得到当前状态和更新函数

3. 通过 `dispatch(action)` 触发更新

4. reducer 根据 action 类型返回新的 state

5. React 使用新 state 重新渲染组件

### 一个完整的小例子

```jsx
import { useReducer } from 'react'

function reducer(state, action) {
  switch (action.type) {
    case 'add':
      return { count: state.count + 1 }
    case 'minus':
      return { count: state.count - 1 }
    default:
      return state
  }
}

function Demo() {
  const [state, dispatch] = useReducer(reducer, { count: 0 })

  return (
    <div>
      <p>{state.count}</p>
      <button onClick={() => dispatch({ type: 'add' })}>+1</button>
      <button onClick={() => dispatch({ type: 'minus' })}>-1</button>
    </div>
  )
}
```

### `dispatch` 这个名字必须吗

不是。

名字只是你自己取的变量名，不是语法关键字。

例如下面也可以：

```jsx
const [state, send] = useReducer(reducer, { count: 0 })
```

或者：

```jsx
const [state, updateState] = useReducer(reducer, { count: 0 })
```

只是社区里最常见、最推荐的写法是：

```jsx
const [state, dispatch] = useReducer(...)
```

因为可读性最好。

### `useReducer` 和 `useState` 的区别

`useState` 更像：

```jsx
const [count, setCount] = useState(0)
setCount((value) => value + 1)
```

`useReducer` 更像：

```jsx
const [state, dispatch] = useReducer(reducer, { total: 0 })
dispatch({ type: 'increment' })
```

区别可以简单记成：

- `useState`：直接改值
- `useReducer`：通过 action 描述“要怎么改”

### 注意点 1：reducer 必须返回新状态

例如：

```jsx
return { total: state.total + 1 }
```

而不是只写逻辑但不返回。

如果不返回新状态，React 就拿不到更新后的值。

### 注意点 2：不要直接修改原 state

不要写这种：

```jsx
state.total += 1
return state
```

更推荐返回一个新对象：

```jsx
return { total: state.total + 1 }
```

因为 React 更适合通过“新对象”判断状态变化。

### 注意点 3：`action` 通常至少有一个 `type`

最常见写法是：

```jsx
dispatch({ type: 'increment' })
```

如果需要额外数据，也可以继续加：

```jsx
dispatch({ type: 'addBy', payload: 5 })
```

然后在 reducer 中读取：

```jsx
case 'addBy':
  return { total: state.total + action.payload }
```

### 注意点 4：适合复杂状态，不必滥用

如果状态非常简单，例如只有一个数字开关：

```jsx
const [count, setCount] = useState(0)
```

那通常没必要强行换成 `useReducer`。

因为 `useReducer` 会多出：

- reducer 函数
- action 对象
- switch / case 逻辑

如果只是简单值，`useState` 反而更直观。

### 注意点 5：任意 state 变化都会导致组件重新执行

`useReducer` 状态变化后，也会触发组件重新渲染。

这和 `useState` 一样。

所以：

- `dispatch(...)` 会触发更新
- 组件函数会重新执行
- 页面根据新的 state 重新渲染

### 一句话记忆

- `useReducer` = 状态值 + dispatch + reducer 规则
- `dispatch` 负责发动作
- `reducer` 负责根据 action 返回新状态
- 状态复杂时优先考虑 `useReducer`
- 状态简单时通常 `useState` 就够了

## 7. 原生 HTML 的 `for` 属性 和 React 的 `htmlFor`

### 原生 HTML 的 `for` 属性是什么

原生 HTML 里，`for` 最常见是写在 `<label>` 标签上。

例如：

```html
<label for="username">用户名</label>
<input id="username" />
```

这里表示：

- 这个 `label` 是给 `id="username"` 的输入框使用的
- `label` 和 `input` 建立了关联关系

只要：

- `label` 的 `for`
- 和表单元素的 `id`

两边值相同，就会绑定成功。

### 绑定后有什么作用

绑定成功后，通常会有这些效果：

- 点击 label 文字时，对应输入框会自动获得焦点
- 表单结构更清晰
- 对屏幕阅读器更友好
- 无障碍支持更好

例如：

```html
<label for="email">邮箱</label>
<input id="email" />
```

点击“邮箱”这两个字时，输入框会被选中。

### React 中为什么不是 `for`

在 React 的 JSX 中，不写：

```jsx
<label for="username">用户名</label>
```

而是写：

```jsx
<label htmlFor="username">用户名</label>
```

因为在 JSX 中，React 对一些 HTML 属性做了特殊命名处理。

就像：

- `class` 在 JSX 中写成 `className`
- `for` 在 JSX 中写成 `htmlFor`

所以：

- 原生 HTML 写 `for`
- React JSX 写 `htmlFor`

本质上表达的是同一个意思。

### React 中怎么使用

例如：

```jsx
<label htmlFor="username">用户名</label>
<input id="username" />
```

这和原生 HTML 中：

```html
<label for="username">用户名</label>
<input id="username" />
```

是对应关系。

### 在当前项目中的例子

在 `HooksPage.jsx` 中有类似写法：

```jsx
<label className="field" htmlFor={searchId}>
  <span>搜索 Hook 知识点</span>
  <input id={searchId} value={query} />
</label>
```

这里的含义是：

- `htmlFor={searchId}` 让 label 指向某个输入框
- `id={searchId}` 让 input 拥有同样的标识
- 两者值相同，所以建立关联

这样用户点击 label 里的文字时，输入框就会聚焦。

### 为什么这里配合 `useId`

因为 `useId()` 可以生成稳定且唯一的 id。

例如：

```jsx
const searchId = useId()
```

然后：

```jsx
<label htmlFor={searchId}>搜索</label>
<input id={searchId} />
```

这可以避免你手动写死 id，也更适合组件化场景。

### 一句话记忆

- 原生 HTML 用 `<label for="xxx">`
- React JSX 用 `<label htmlFor="xxx">`
- `for` / `htmlFor` 要和表单元素的 `id` 对应起来
- 作用是让 label 和输入控件建立关联

## 8. Zustand 中的常见术语：`state` 和 `actions`

在 Zustand 里，一份 store 通常可以拆成两部分：

- `state`
- `actions`

### 什么是 `state`

`state` 指的是“存起来的数据本身”。

例如当前项目的 `src/store/useReviewStore.js` 中：

```js
count: 1,
topicFilter: 'all',
todos: [
  { id: 1, text: '理解 useState 如何触发重新渲染', done: true },
]
```

这些都属于 store 里的 `state`。

你可以把它理解成：

- 当前全局状态数据
- 当前 store 里保存的值

### 什么是 `actions`

`actions` 指的是“修改 state 的函数”。

例如：

```js
increment
decrement
setTopicFilter
addTodo
toggleTodo
removeTodo
```

这些函数都属于 store 的 `actions`。

它们的作用就是：

- 修改已有 state
- 触发状态更新

所以最常见的说法就是：

- store 里有一份 `state`
- store 里也有一组 `actions`

### 在其他页面怎么用

其他页面只要：

```js
import { useReviewStore } from '../store/useReviewStore.js'
```

就可以直接接入这份全局 store。

例如读取状态：

```js
const count = useReviewStore((state) => state.count)
```

例如读取 action：

```js
const increment = useReviewStore((state) => state.increment)
```

然后调用：

```js
increment()
```

### 一句话记忆

- 数据本身叫 `state`
- 修改数据的函数通常叫 `actions`
- Zustand store 一般就是“state + actions”
- 其他组件只要 `import useReviewStore` 就能读取和调用

## 9. 什么是回调函数，以及参数为什么会“自动传进来”

### 什么是回调函数

回调函数可以简单理解成：

- 你把一个函数传给另一个函数
- 由对方在后续某个时机再调用它

这时这个被传进去的函数，就叫回调函数。

例如：

```js
function run(callback) {
  callback('hello')
}

run(function (value) {
  console.log(value)
})
```

这里传进去的：

```js
function (value) {
  console.log(value)
}
```

就是回调函数。

### 为什么回调函数里的参数会有值

不是“凭空自动注入”，而是：

- 调用这个回调函数的那一方
- 在执行它的时候主动传了参数

例如上面的例子里：

```js
callback('hello')
```

这句就是在调用回调函数时，把 `'hello'` 传进去。

所以回调里的 `value` 才会有值。

### 放到 React 里理解

例如：

```jsx
<button onClick={(event) => console.log(event)}>点击</button>
```

这里 `(event) => console.log(event)` 是回调函数。

点击发生时，React 会在内部调用它，并把事件对象传进去。

所以 `event` 才会有值。

### 放到 `map` 里理解

例如：

```js
arr.map((item, index) => {
  console.log(item, index)
})
```

这里 `(item, index) => ...` 也是回调函数。

`map` 在遍历数组时，会反复调用这个回调，并传入：

- 当前项 `item`
- 当前下标 `index`

### 放到 Zustand 里理解

例如：

```js
create((set) => ({
  count: 1,
}))
```

这里 `(set) => ({ ... })` 也是回调函数。

是 Zustand 在内部调用这个函数时，把 `set` 这个参数传进来的。

### 一句话记忆

- 回调函数就是“传给别人，等别人来调用的函数”
- 回调函数的参数来自调用者
- 不是自动凭空生成，而是调用时传进来的

## 10. 回调函数参数个数不匹配会不会报错

通常不会。

JavaScript 的函数参数机制是比较宽松的：

- 传少了，不报错
- 传多了，也不报错

### 情况 1：调用者传得比你定义的少

例如：

```js
function test(a, b) {
  console.log(a, b)
}

test(1)
```

结果：

```js
1 undefined
```

这里：

- `a = 1`
- `b = undefined`

不会报错。

### 情况 2：调用者传得比你定义的多

例如：

```js
function test(a) {
  console.log(a)
}

test(1, 2, 3)
```

结果：

```js
1
```

这里：

- `a` 接到第一个参数
- 多余的参数被忽略

也不会报错。

### 放到回调函数里理解

例如 `map` 在内部可能会传多个参数：

```js
arr.map((item, index, array) => ...)
```

但你只写一个也没问题：

```js
arr.map((item) => item * 2)
```

因为：

- `map` 传了多个参数
- 你只接了第一个
- 其余参数会被忽略

React 事件也是一样：

```jsx
<button onClick={() => console.log('clicked')}>点击</button>
```

即使 React 调用时传了事件对象，你没接也不会报错。

### 一句话记忆

- 参数传少了：缺少的参数是 `undefined`
- 参数传多了：多余的参数会被忽略
- JavaScript 不会因为参数个数不完全一致就报错
