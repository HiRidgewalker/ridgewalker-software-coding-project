import { Link } from 'react-router-dom'
import { SectionCard } from '../components/SectionCard'

const featureGroups = [
  {
    title: '基础能力',
    items: [
      'JSX',
      '组件拆分',
      'props',
      'children',
      '事件处理',
      '条件渲染',
      '列表渲染',
      '受控表单',
    ],
  },
  {
    title: '常用 Hooks',
    items: [
      'useState',
      'useEffect',
      'useRef',
      'useReducer',
      'useId',
      'useContext',
      'useTransition',
      'useDeferredValue',
    ],
  },
  {
    title: '常用特性',
    items: [
      'StrictMode',
      '嵌套路由',
      'Outlet',
      '错误边界',
      'Portal',
      'lazy',
      'Suspense',
      '全局状态管理',
    ],
  },
  {
    title: '渲染与生命周期',
    items: [
      '首次挂载',
      '重新渲染',
      '副作用清理',
      '组件卸载',
      '父子更新顺序',
      'StrictMode 调试行为',
    ],
  },
] as const

export function HomePage() {
  return (
    <div className="page">
      <section className="hero-panel">
        <p className="hero-kicker">Vite + React + TypeScript</p>
        <h2>把 React 常用知识点放进一个可运行项目里回顾</h2>
        <p className="hero-copy">
          这个项目尽量覆盖日常开发里最常见的 React API 和特性。不是死记概念，而是直接通过页面行为观察状态变化和组件渲染。
        </p>
        <div className="hero-actions">
          <Link className="primary-button" to="/basics">
            从基础语法开始
          </Link>
          <Link className="ghost-button" to="/zustand">
            直接看 Zustand
          </Link>
        </div>
      </section>

      <div className="grid-two">
        {featureGroups.map((group) => (
          <SectionCard
            key={group.title}
            title={group.title}
            description="这些点都可以在对应页面看到实际代码和交互效果。"
          >
            <ul className="chip-list">
              {group.items.map((item) => (
                <li key={item} className="chip">
                  {item}
                </li>
              ))}
            </ul>
          </SectionCard>
        ))}
      </div>
    </div>
  )
}
