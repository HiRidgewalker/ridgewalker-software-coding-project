import { createContext, useContext, useState } from 'react'

// createContext 用来创建一个上下文对象。
// 适合放一些“跨层级共享、但又不想层层 props 传递”的数据。
const ThemeContext = createContext(null)

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('sunrise')

  function toggleTheme() {
    setTheme((currentTheme) =>
      currentTheme === 'sunrise' ? 'ink' : 'sunrise',
    )
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {/*
        这里顺手把 theme 写到 data-theme 上。
        CSS 可以通过 [data-theme="ink"] 这种选择器切换变量。
      */}
      <div data-theme={theme}>{children}</div>
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)

  if (!context) {
    throw new Error('useTheme 必须在 ThemeProvider 内部使用')
  }

  return context
}
