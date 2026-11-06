/**
 * Navbar 导航栏组件
 *
 * 样式说明：
 * flex: 使用 Flex 布局
 * justify-between: 子元素两端对齐（Logo在左，链接在右）
 * items-center: 子元素垂直居中
 * p-4: 内边距 16px
 * bg-white: 背景白色
 * shadow-sm: 小阴影
 */
function Navbar() {
  return (
    <nav className="flex justify-between items-center p-4 bg-white shadow-md">
      {/* text-xl: 文字大小 20px */}
      {/* font-bold: 粗体 */}
      {/* text-gray-800: 深灰色文字 */}
      <div className="text-xl font-bold text-gray-800">MyPortfolio</div>

      {/* flex: 启用 Flex 布局 */}
      {/* gap-4: 子元素间距 16px */}
      <div className="flex gap-4">
        {/* text-gray-600: 中灰色文字 */}
        {/* hover:text-gray-900: 悬停时变深灰色 */}
        <a href="#about" className="text-gray-600 hover:text-lime-950">About</a>
        <a href="#projects" className="text-gray-600 hover:text-gray-900">Projects</a>
        <a href="#contact" className="text-gray-600 hover:text-gray-900">Contact</a>
      </div>
    </nav>
  )
}

export default Navbar
