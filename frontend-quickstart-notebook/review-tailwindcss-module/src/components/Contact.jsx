/**
 * Contact 联系区域组件
 *
 * 样式说明：
 * py-16: 上下内边距 64px
 * bg-gray-50: 背景浅灰色
 */
function Contact() {
  return (
    <section id="contact" className="py-16 bg-gray-50">
      <div className="container mx-auto px-4 text-center">
        {/* text-3xl: 文字大小 30px */}
        {/* font-bold: 粗体 */}
        {/* mb-4: 下边距 16px */}
        <h2 className="text-3xl font-bold mb-4">联系我</h2>

        {/* text-gray-600: 中灰色文字 */}
        {/* mb-8: 下边距 32px */}
        <p className="text-gray-600 mb-8">
          如果您对我的项目感兴趣，欢迎联系我！
        </p>

        {/* flex: 启用 Flex 布局 */}
        {/* justify-center: 水平居中 */}
        {/* gap-4: 子元素间距 16px */}
        <div className="flex justify-center gap-4">
          {/* 按钮样式：
              px-6: 水平内边距 24px
              py-3: 垂直内边距 12px
              bg-blue-500: 背景蓝色
              text-white: 文字白色
              rounded-lg: 圆角
              font-medium: 中等粗细
              hover:bg-blue-600: 悬停时背景变深
              transition-colors: 颜色过渡
          */}
          <button className="px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors">
            发送邮件
          </button>

          {/* 另一种按钮样式：
              px-6: 水平内边距 24px
              py-3: 垂直内边距 12px
              bg-white: 背景白色
              text-gray-700: 文字深灰色
              rounded-lg: 圆角
              font-medium: 中等粗细
              border: 边框
              border-gray-300: 边框浅灰色
              hover:bg-gray-100: 悬停时背景变浅灰
              transition-colors: 颜色过渡
          */}
          <button className="px-6 py-3 bg-white text-gray-700 rounded-lg font-medium border border-gray-300 hover:bg-gray-100 transition-colors">
            GitHub
          </button>
        </div>
      </div>
    </section>
  )
}

export default Contact
