import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { to: '/', label: '总览' },
  { to: '/basics', label: '基础语法' },
  { to: '/hooks', label: '常用 Hooks' },
  { to: '/lifecycle', label: '生命周期' },
  { to: '/advanced', label: '常用特性' },
  { to: '/zustand', label: 'Zustand' },
]

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <p className="sidebar-eyebrow">Review React Module</p>
        <h1>React 常用方法与特性回顾</h1>
        <p className="sidebar-intro">
          这个项目不是业务 demo，而是一个按知识点组织的复习手册。每个页面都配有详细注释，方便你对照代码理解。
        </p>

        <nav className="nav-list" aria-label="Main navigation">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                isActive ? 'nav-link nav-link-active' : 'nav-link'
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="content-panel">
        {/*
          Outlet 是嵌套路由的占位符。
          当前匹配到的子路由页面会渲染在这里。
        */}
        <Outlet />
      </main>
    </div>
  )
}
