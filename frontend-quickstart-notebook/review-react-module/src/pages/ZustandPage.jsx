import { useState } from 'react'
import { SectionCard } from '../components/SectionCard.jsx'
import { useReviewStore } from '../store/useReviewStore.js'

export function ZustandPage() {
  const [inputValue, setInputValue] = useState('')

  // selector 的作用是“只取 store 中我关心的那一部分”。
  // 这样组件代码更清晰，也更符合 zustand 的使用习惯。
  const count = useReviewStore((state) => state.count)
  const todos = useReviewStore((state) => state.todos)
  const topicFilter = useReviewStore((state) => state.topicFilter)

  const increment = useReviewStore((state) => state.increment)
  const decrement = useReviewStore((state) => state.decrement)
  const setTopicFilter = useReviewStore((state) => state.setTopicFilter)
  const addTodo = useReviewStore((state) => state.addTodo)
  const toggleTodo = useReviewStore((state) => state.toggleTodo)
  const removeTodo = useReviewStore((state) => state.removeTodo)

  const visibleTodos =
    topicFilter === 'done'
      ? todos.filter((todo) => todo.done)
      : topicFilter === 'todo'
        ? todos.filter((todo) => !todo.done)
        : todos

  function handleSubmit(event) {
    event.preventDefault()

    if (!inputValue.trim()) {
      return
    }

    addTodo(inputValue.trim())
    setInputValue('')
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="page-kicker">Zustand</p>
        <h2>使用 Zustand 管理全局状态</h2>
        <p>
          这一页把“计数器 + todo 列表”都放到同一个 store 中，演示最常见的 Zustand 写法。
        </p>
      </header>

      <div className="grid-two">
        <SectionCard
          title="全局计数器"
          description="不同页面都能共享这份状态，因为它已经脱离组件局部 state。"
        >
          <p className="stat-line">count in store: {count}</p>
          <div className="button-row">
            <button className="primary-button" onClick={increment}>
              increment
            </button>
            <button className="ghost-button" onClick={decrement}>
              decrement
            </button>
          </div>
        </SectionCard>

        <SectionCard
          title="筛选器"
          description="topicFilter 也是全局状态，因此筛选条件也可以被别的组件复用。"
        >
          <div className="button-row">
            <button className="ghost-button" onClick={() => setTopicFilter('all')}>
              all
            </button>
            <button className="ghost-button" onClick={() => setTopicFilter('todo')}>
              todo
            </button>
            <button className="ghost-button" onClick={() => setTopicFilter('done')}>
              done
            </button>
          </div>
          <p className="inline-note">当前筛选状态: {topicFilter}</p>
        </SectionCard>
      </div>

      <SectionCard
        title="Todo 列表"
        description="状态和修改动作都来自同一个 zustand store。"
      >
        <form className="inline-form" onSubmit={handleSubmit}>
          <input
            value={inputValue}
            placeholder="输入一条新的复习任务"
            onChange={(event) => setInputValue(event.target.value)}
          />
          <button className="primary-button" type="submit">
            添加任务
          </button>
        </form>

        <ul className="todo-list">
          {visibleTodos.map((todo) => (
            <li key={todo.id} className="todo-item">
              <label className="todo-main">
                <input
                  checked={todo.done}
                  type="checkbox"
                  onChange={() => toggleTodo(todo.id)}
                />
                <span className={todo.done ? 'todo-done' : ''}>{todo.text}</span>
              </label>
              <button className="ghost-button" onClick={() => removeTodo(todo.id)}>
                删除
              </button>
            </li>
          ))}
        </ul>
      </SectionCard>
    </div>
  )
}
