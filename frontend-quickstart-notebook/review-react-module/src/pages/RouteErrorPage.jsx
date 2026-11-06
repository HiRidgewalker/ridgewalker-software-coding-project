import { isRouteErrorResponse, Link, useRouteError } from 'react-router-dom'

export function RouteErrorPage() {
  const error = useRouteError()

  let title = '页面渲染失败'
  let description = '发生了一个未预期的路由错误。'

  if (isRouteErrorResponse(error)) {
    title = `${error.status} ${error.statusText}`
    description = error.data?.message || description
  } else if (error instanceof Error) {
    description = error.message
  }

  return (
    <div className="page error-page">
      <h2>{title}</h2>
      <p>{description}</p>
      <Link className="primary-button" to="/">
        返回首页
      </Link>
    </div>
  )
}
