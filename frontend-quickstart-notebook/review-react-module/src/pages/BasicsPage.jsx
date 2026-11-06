import { useState } from 'react'
import { SectionCard } from '../components/SectionCard.jsx'

function WelcomeCard({ name, role, children }) {
  return (
    <article className="demo-box">
      {/*
        props 是父组件传给子组件的数据。
        这里的 name、role、children 都来自 WelcomeCard 的使用方。
      */}
      <h3>
        {name} / {role}
      </h3>
      <div className="inline-note">{children}</div>
    </article>
  )
}

const reactTopics = [
  '组件是 UI 的最小复用单位',
  'JSX 看起来像 HTML，本质上是 JavaScript',
  '列表渲染时需要稳定的 key',
]

export function BasicsPage() {
  const [keyword, setKeyword] = useState('')
  const [showTips, setShowTips] = useState(true)

  const filteredTopics = reactTopics.filter((topic) =>
    topic.toLowerCase().includes(keyword.toLowerCase()),
  )

  const sayHelloWorld = () => {
    console.log('Hello, world!')
  }

  return (
    <div className="page">
      <header className="page-header">
        <p className="page-kicker">Basics</p>
        <h2>React 基础语法与组件通信</h2>
        <p>
          这一页覆盖 JSX、组件、props、children、事件处理、条件渲染、列表渲染和受控表单。
        </p>
      </header>

      <div className="grid-two">
        <SectionCard
          title="JSX、组件、props、children"
          description="React 组件本质上就是返回 JSX 的函数。"
        >
          <WelcomeCard name="React" role="UI Library">
            children 是一个特殊的 prop，表示组件标签内部包着的内容。
          </WelcomeCard>
        </SectionCard>

        <SectionCard
          title="事件处理"
          description="React 事件名通常采用驼峰写法，例如 onClick、onChange。"
        >
          <button
            className="primary-button"
            onClick={() => setShowTips((currentValue) => !currentValue)}
          >
            切换提示显示状态
          </button>
          <button className="primary-button" onClick={sayHelloWorld}>
            打印 Hello, world!
          </button>

          {/*
            条件渲染最常见的写法有:
            1. 三元表达式 condition ? A : B
            2. 短路写法 condition && A
          */}
          {showTips ? (
            <p className="inline-note">当前展示的是条件渲染出来的提示内容。</p>
          ) : (
            <p className="inline-note">提示内容已隐藏，这里显示备用内容。</p>
          )}
        </SectionCard>
      </div>

      <div className="grid-two">
        <SectionCard
          title="受控表单"
          description="受控组件指的是 input 的值由 React state 驱动。"
        >
          <label className="field">
            <span>输入关键词筛选知识点</span>
            <input
              value={keyword}
              placeholder="例如: JSX"
              onChange={(event) => setKeyword(event.target.value)}
            />
          </label>
          <p className="inline-note">当前输入值: {keyword || '空字符串'}</p>
        </SectionCard>

        <SectionCard
          title="列表渲染"
          description="渲染数组时建议使用 map，并给每一项设置稳定的 key。"
        >
          <ul className="topic-list">
            {filteredTopics.map((topic) => (
              <li key={topic}>{topic}</li>
            ))}
          </ul>

          {filteredTopics.length === 0 ? (
            <p className="inline-note">没有匹配项，说明当前筛选条件没有命中任何 topic。</p>
          ) : null}
        </SectionCard>
      </div>
    </div>
  )
}
