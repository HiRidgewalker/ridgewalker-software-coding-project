import { create } from 'zustand'

// create(...) 会创建一个 store hook。
// 后续在组件里直接调用 useReviewStore(...) 就能读写全局状态。
export const useReviewStore = create((set) => ({
  count: 1,
  topicFilter: 'all',
  todos: [
    { id: 1, text: '理解 useState 如何触发重新渲染', done: true },
    { id: 2, text: '理解 useEffect 的依赖数组', done: false },
    { id: 3, text: '理解 zustand 的 selector 写法', done: false },
  ],

  increment: () =>
    set((state) => ({
      count: state.count + 1,
    })),

  decrement: () =>
    set((state) => ({
      count: state.count - 1,
    })),

  setTopicFilter: (nextFilter) =>
    set({
      topicFilter: nextFilter,
    }),

  addTodo: (text) =>
    set((state) => ({
      todos: [
        ...state.todos,
        {
          id: Date.now(),
          text,
          done: false,
        },
      ],
    })),

  toggleTodo: (id) =>
    set((state) => ({
      todos: state.todos.map((todo) =>
        todo.id === id ? { ...todo, done: !todo.done } : todo,
      ),
    })),

  removeTodo: (id) =>
    set((state) => ({
      todos: state.todos.filter((todo) => todo.id !== id),
    })),
}))
