/**
 * Footer 页脚组件
 *
 * 样式说明：
 * py-8: 上下内边距 32px
 * bg-white: 背景白色
 * border-t: 顶部边框
 * border-gray-200: 边框浅灰色
 */
function Footer() {
  return (
    <footer className="py-8 bg-white border-t border-gray-200">
      <div className="container mx-auto px-4 text-center">
        {/* text-gray-500: 浅灰色文字 */}
        {/* text-sm: 文字大小 14px */}
        <p className="text-gray-500 text-sm">
          © 2024 MyPortfolio. All rights reserved.
        </p>
      </div>
    </footer>
  )
}

export default Footer
