import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext.jsx'
import { router } from './router.jsx'
import './index.css'

// createRoot 是 React 18+ 的新挂载方式。
// 它会把 React 应用挂到 index.html 里的 <div id="root"></div> 上。
createRoot(document.getElementById('root')).render(
  <ThemeProvider>
    {/*
      RouterProvider 接收我们配置好的 router 对象。
      整个应用的页面切换都由 react-router-dom 负责。
    */}
    <RouterProvider router={router} />
  </ThemeProvider>,
)
