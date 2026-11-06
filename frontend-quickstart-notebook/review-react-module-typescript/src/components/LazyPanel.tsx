export default function LazyPanel() {
  return (
    <div className="callout">
      <strong>lazy + Suspense 示例已加载。</strong>
      <p>
        React.lazy 会把组件拆成单独的代码块，真正访问到这里时才加载，有利于控制首屏体积。
      </p>
    </div>
  )
}
