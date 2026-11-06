import {
  createContext,
  useContext,
  useState,
  type ReactNode,
  type Dispatch,
  type SetStateAction,
} from 'react'

type Theme = 'sunrise' | 'ink'

type ThemeContextValue = {
  theme: Theme
  toggleTheme: () => void
  setTheme: Dispatch<SetStateAction<Theme>>
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

type ThemeProviderProps = {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>('sunrise')

  function toggleTheme() {
    setTheme((currentTheme) =>
      currentTheme === 'sunrise' ? 'ink' : 'sunrise',
    )
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
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
