import {
  startTransition,
  useDeferredValue,
  useEffect,
  useId,
  useReducer,
  useRef,
  useState,
  useTransition,
} from 'react'
import { SectionCard } from '../components/SectionCard.jsx'

const lessons = [
  'useState 负责本地状态',
  'useEffect 负责副作用',
  'useRef 负责跨渲染保存可变值',
  'useReducer 适合复杂状态流转',
  'useId 适合生成可访问性相关 id',
  'useTransition 适合标记非紧急更新',
  'useDeferredValue 适合延后大计算结果',
]

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

export function HooksPage() {
  const [count, setCount] = useState(0)
  const [query, setQuery] = useState('')
  const [reducerState, dispatch] = useReducer(reducer, { total: 2 })
  const [isPending, startListTransition] = useTransition()
  const renderTimesRef = useRef(0)
  const inputRef = useRef(null)
  const searchId = useId()
  const deferredQuery = useDeferredValue(query)

  renderTimesRef.current += 1

  // useEffect 用来处理“渲染之后再做的事”。
  // 例如请求数据、订阅事件、操作标题、手动操作 DOM 等。
  useEffect(() => {
    document.title = `count = ${count}`

    // return 的函数就是清理函数。
    // 当组件卸载，或者依赖变化导致 effect 重新执行前，会先执行清理。
    return () => {
      document.title = 'React Review'
    }
  }, [count])

  const filteredLessons = lessons.filter((lesson) =>
    lesson.toLowerCase().includes(deferredQuery.toLowerCase()),
  )

  return (
    <div className="page">
      <header className="page-header">
        <p className="page-kicker">Hooks</p>
        <h2>React 常用 Hooks</h2>
        <p>这一页集中回顾最常见的状态、副作用、引用、上下文前置能力和并发更新接口。</p>
      </header>

      <div className="grid-two">
        <SectionCard
          title="useState"
          description="useState 会返回当前状态值和修改它的方法。"
        >
          <p className="stat-line">当前 count: {count}</p>
          <div className="button-row">
            <button className="primary-button" onClick={() => setCount((value) => value + 1)}>
              +1
            </button>
            <button className="ghost-button" onClick={() => setCount(0)}>
              重置
            </button>
          </div>
        </SectionCard>

        <SectionCard
          title="useRef"
          description="useRef 保存的是一个 { current } 对象，修改它不会触发重新渲染。"
        >
          <p className="inline-note">当前组件渲染次数: {renderTimesRef.current}</p>
          <div className="button-row">
            <input ref={inputRef} placeholder="点击右侧按钮自动聚焦" />
            <button
              className="ghost-button"
              onClick={() => {
                inputRef.current?.focus();
                console.log(inputRef)
              }}
            >
              聚焦输入框
            </button>
          </div>
        </SectionCard>
      </div>

      <div className="grid-two">
        <SectionCard
          title="useReducer"
          description="当状态更新逻辑比较多、动作比较清晰时，用 reducer 会更易维护。"
        >
          <p className="stat-line">reducer total: {reducerState.total}</p>
          <div className="button-row">
            <button className="primary-button" onClick={() => dispatch({ type: 'increment' })}>
              dispatch increment
            </button>
            <button className="ghost-button" onClick={() => dispatch({ type: 'decrement' })}>
              dispatch decrement
            </button>
            <button className="ghost-button" onClick={() => dispatch({ type: 'reset' })}>
              dispatch reset
            </button>
          </div>
        </SectionCard>

        <SectionCard
          title="useId"
          description="useId 常用于生成 label 和 input 之间的唯一关联 id。"
        >
          <label className="field" htmlFor={searchId}>
            <span>搜索 Hook 知识点</span>
            <input
              id={searchId}
              value={query}
              onChange={(event) => {
                const nextValue = event.target.value

                // startTransition 用来告诉 React:
                // 接下来这次更新不是最紧急的，可以更平滑地安排。
                startTransition(() => {
                  setQuery(nextValue)
                })
              }}
              placeholder="输入 use"
            />
          </label>
          <p className="inline-note">useId 生成的 id: {searchId}</p>
        </SectionCard>
      </div>

      <SectionCard
        title="useTransition + useDeferredValue"
        description="这两个 API 常用于交互流畅度优化。"
      >
        <p className="inline-note">
          输入框更新由 startTransition 包裹，过滤结果读取 deferredQuery，避免重计算过早抢占输入体验。
        </p>
        <p className="inline-note">isPending: {isPending ? '正在调度更新' : '空闲中'}</p>
        <div className="topic-grid">
          {filteredLessons.map((lesson) => (
            <article key={lesson} className="topic-tile">
              {lesson}
            </article>
          ))}
        </div>
      </SectionCard>
    </div>
  )
}
