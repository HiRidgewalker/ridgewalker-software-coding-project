import { createPortal } from 'react-dom'

export function PortalModal({ title, children, onClose }) {
  // createPortal 的作用是:
  // 把这段 JSX 渲染到“当前组件层级之外”的 DOM 节点中。
  // 常见用途就是弹窗、抽屉、全局提示。
  return createPortal(
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="modal-card"
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="ghost-button" onClick={onClose}>
            关闭
          </button>
        </div>
        <div className="modal-content">{children}</div>
      </div>
    </div>,
    document.body,
  )
}
