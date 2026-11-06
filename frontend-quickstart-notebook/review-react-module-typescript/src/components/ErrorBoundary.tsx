import { Component, type ErrorInfo, type ReactNode } from 'react'

type ErrorBoundaryProps = {
  children: ReactNode
}

type ErrorBoundaryState = {
  hasError: boolean
  message: string
}

export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props)

    // class 组件的 state 通常写在 constructor 中初始化。
    this.state = {
      hasError: false,
      message: '',
    }
  }

  // 这个静态方法会在子组件抛错后执行。
  // 它的返回值会合并到当前组件 state 中。
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      message: error.message,
    }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // 这里通常可以接日志平台，例如 Sentry。
    console.log('ErrorBoundary 捕获到错误:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="callout callout-warning">
          <strong>错误边界已接管当前区域。</strong>
          <p>{this.state.message}</p>
        </div>
      )
    }

    return this.props.children
  }
}
