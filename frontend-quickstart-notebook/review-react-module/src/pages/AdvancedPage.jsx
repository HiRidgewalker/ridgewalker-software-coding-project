import { lazy, Suspense, useState } from 'react'
import { ErrorBoundary } from '../components/ErrorBoundary.jsx'
import { PortalModal } from '../components/PortalModal.jsx'
import { SectionCard } from '../components/SectionCard.jsx'
import { useTheme } from '../context/ThemeContext.jsx'

const LazyPanel = lazy(() => import('../components/LazyPanel.jsx'))

function CrashButton({ shouldCrash }) {
  if (shouldCrash) {
    throw new Error('这是一个演示用错误，ErrorBoundary 会接住它')
  }

  return <p className="inline-note">点击“触发子组件报错”观察错误边界表现。</p>
}

export function AdvancedPage() {
  const { theme, toggleTheme } = useTheme()
  const [showModal, setShowModal] = useState(false)
  const [shouldCrash, setShouldCrash] = useState(false)
  const [showLazyPanel, setShowLazyPanel] = useState(false)

  return (
    <div className="page">
      <header className="page-header">
        <p className="page-kicker">Advanced</p>
        <h2>React 常用特性</h2>
        <p>这一页演示 Context、错误边界、Portal、lazy 和 Suspense。</p>
      </header>

      <div className="grid-two">
        <SectionCard
          title="Context + useContext"
          description="Context 适合跨层级共享主题、语言、登录态等数据。"
        >
          <p className="inline-note">当前主题: {theme}</p>
          <button className="primary-button" onClick={toggleTheme}>
            切换主题
          </button>
        </SectionCard>

        <SectionCard
          title="Portal"
          description="弹窗通常要脱离父级布局约束，这时会用到 createPortal。"
        >
          <button className="primary-button" onClick={() => setShowModal(true)}>
            打开弹窗
          </button>
        </SectionCard>
      </div>

      <div className="grid-two">
        <SectionCard
          title="Error Boundary"
          description="错误边界只能捕获其子树中的渲染错误。"
        >
          <div className="button-row">
            <button className="primary-button" onClick={() => setShouldCrash(true)}>
              触发子组件报错
            </button>
            <button className="ghost-button" onClick={() => setShouldCrash(false)}>
              还原
            </button>
          </div>

          <ErrorBoundary>
            <CrashButton shouldCrash={shouldCrash} />
          </ErrorBoundary>
        </SectionCard>

        <SectionCard
          title="lazy + Suspense"
          description="按需加载组件，常用于页面级拆包。"
        >
          <button className="primary-button" onClick={() => setShowLazyPanel(true)}>
            加载懒组件
          </button>
          {showLazyPanel ? (
            <Suspense fallback={<p className="inline-note">懒组件加载中...</p>}>
              <LazyPanel />
            </Suspense>
          ) : (
            <p className="inline-note">点击按钮后才会真正请求 LazyPanel 对应的代码块。</p>
          )}
        </SectionCard>
      </div>

      {showModal ? (
        <PortalModal title="Portal 示例" onClose={() => setShowModal(false)}>
          <p>
            这个弹窗虽然写在 AdvancedPage 组件里，但实际会渲染到 document.body
            下，这就是 createPortal 的作用。
          </p>
        </PortalModal>
      ) : null}
    </div>
  )
}
