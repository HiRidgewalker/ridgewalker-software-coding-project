import { useEffect, useEffectEvent, useRef, useState } from 'react'
import { SectionCard } from '../components/SectionCard'

type AppendLog = (message: string) => void

function ChildPanel({
  parentCount,
  appendLog,
}: {
  parentCount: number
  appendLog: AppendLog
}) {
  const childRenderCount = useRef(0)
  childRenderCount.current += 1

  // 这条 console.log 用来辅助观察“渲染阶段”的执行顺序。
  // 打开浏览器控制台后，你会看到每次更新时父组件和子组件谁先进入 render。
  console.log('Child render -> parentCount:', parentCount)

  useEffect(() => {
    appendLog(`Child effect 执行，接收到 parentCount = ${parentCount}`)

    // 依赖变化或组件卸载时，React 会先执行上一次 effect 的清理函数。
    return () => {
      appendLog(`Child cleanup 执行，准备离开 parentCount = ${parentCount}`)
    }
  }, [parentCount])

  return (
    <article className="demo-box">
      <h3>ChildPanel</h3>
      <p className="inline-note">child render 次数: {childRenderCount.current}</p>
      <p className="inline-note">当前接收到的父组件 count: {parentCount}</p>
    </article>
  )
}

export function LifecyclePage() {
  const [parentCount, setParentCount] = useState(0)
  const [showChild, setShowChild] = useState(true)
  const [logs, setLogs] = useState<string[]>([])
  const parentRenderCount = useRef(0)

  parentRenderCount.current += 1

  // useEffectEvent 适合这种“我要在 effect 里读取最新逻辑，
  // 但又不想让 effect 因为回调函数引用变化而反复重跑”的场景。
  const appendLog = useEffectEvent((message: string) => {
    setLogs((currentLogs) =>
      [`${new Date().toLocaleTimeString()} | ${message}`, ...currentLogs].slice(
        0,
        30,
      ),
    )
  })

  console.log('Parent render -> parentCount:', parentCount, 'showChild:', showChild)

  useEffect(() => {
    appendLog(
      `Parent effect 执行，parentCount = ${parentCount}，showChild = ${showChild}`,
    )

    return () => {
      appendLog(
        `Parent cleanup 执行，准备离开 parentCount = ${parentCount}，showChild = ${showChild}`,
      )
    }
  }, [parentCount, showChild])

  return (
    <div className="page">
      <header className="page-header">
        <p className="page-kicker">Lifecycle</p>
        <h2>React 生命周期、渲染流程与父子更新顺序</h2>
        <p>
          这页主要讲函数组件世界里的 mount、update、unmount。React 没有再强调传统类组件那套生命周期名词，但本质流程仍然存在。
        </p>
      </header>

      <SectionCard
        title="先记住这三个阶段"
        description="观察 React 时，先把复杂概念压缩成挂载、更新、卸载。"
      >
        <ul className="topic-list">
          <li>挂载 mount: 组件第一次出现在页面上，会先 render，再执行 effect。</li>
          <li>更新 update: state 或 props 变化后重新 render，旧 effect 先 cleanup，再执行新 effect。</li>
          <li>卸载 unmount: 组件从页面移除时，最后一次执行 cleanup。</li>
        </ul>
      </SectionCard>

      <div className="grid-two">
        <SectionCard
          title="父组件控制子组件"
          description="点击按钮后，观察页面日志和浏览器控制台输出。"
        >
          <p className="stat-line">parent render 次数: {parentRenderCount.current}</p>
          <div className="button-row">
            <button
              className="primary-button"
              onClick={() => setParentCount((value) => value + 1)}
            >
              更新父组件 count
            </button>
            <button
              className="ghost-button"
              onClick={() => setShowChild((currentValue) => !currentValue)}
            >
              {showChild ? '卸载子组件' : '重新挂载子组件'}
            </button>
            <button className="ghost-button" onClick={() => setLogs([])}>
              清空日志
            </button>
          </div>
          <p className="inline-note">parentCount 当前值: {parentCount}</p>
          <p className="inline-note">
            一般情况下，父组件更新会先触发父组件重新执行，再触发子组件重新执行。
          </p>
        </SectionCard>

        <SectionCard
          title="子组件区域"
          description="当 showChild 为 false 时，子组件会被真正卸载。"
        >
          {showChild ? (
            <ChildPanel parentCount={parentCount} appendLog={appendLog} />
          ) : (
            <div className="callout">
              <strong>ChildPanel 已卸载。</strong>
              <p>这意味着 React 会执行子组件上一次 effect 的 cleanup。</p>
            </div>
          )}
        </SectionCard>
      </div>

      <div className="grid-two">
        <SectionCard
          title="如何理解渲染流程"
          description="把 React 更新粗略分成两段更容易理解。"
        >
          <ul className="topic-list">
            <li>render 阶段: React 执行组件函数，计算新的 JSX 结果。</li>
            <li>commit 阶段: React 把变化真正同步到 DOM，然后执行 effect。</li>
            <li>如果只是 render 了，但结果没有提交，就不会看到最终 DOM 变化。</li>
          </ul>
        </SectionCard>

        <SectionCard
          title="关于开发环境下的 StrictMode"
          description="如果你看到 effect 日志比预期多，不一定是代码错了。"
        >
          <p className="inline-note">
            当前项目在 <code>src/main.tsx</code> 中开启了 <code>StrictMode</code>。
          </p>
          <p className="inline-note">
            在开发环境下，React 会额外执行一次挂载和清理，帮助你发现不安全副作用。所以你可能看到 mount / cleanup / mount 这种调试行为。
          </p>
        </SectionCard>
      </div>

      <SectionCard
        title="日志面板"
        description="这里记录的是 effect 和 cleanup 的执行顺序。真正的 render 顺序建议同时配合浏览器控制台观察。"
      >
        <ul className="log-list">
          {logs.map((log) => (
            <li key={log} className="log-item">
              {log}
            </li>
          ))}
        </ul>
      </SectionCard>
    </div>
  )
}
