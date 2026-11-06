import { createBrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import { RouteErrorPage } from './pages/RouteErrorPage.jsx'
import { AdvancedPage } from './pages/AdvancedPage.jsx'
import { BasicsPage } from './pages/BasicsPage.jsx'
import { HomePage } from './pages/HomePage.jsx'
import { HooksPage } from './pages/HooksPage.jsx'
import { LifecyclePage } from './pages/LifecyclePage.jsx'
import { ZustandPage } from './pages/ZustandPage.jsx'

// createBrowserRouter 使用浏览器的 History API。
// 这意味着 URL 看起来会比较自然，例如 /hooks、/zustand。
export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    errorElement: <RouteErrorPage />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'basics', element: <BasicsPage /> },
      { path: 'hooks', element: <HooksPage /> },
      { path: 'lifecycle', element: <LifecyclePage /> },
      { path: 'advanced', element: <AdvancedPage /> },
      { path: 'zustand', element: <ZustandPage /> },
    ],
  },
])
