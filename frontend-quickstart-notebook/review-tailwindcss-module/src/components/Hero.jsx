/**
 * Hero 组件 - 首屏展示区域
 *
 * 样式说明：
 * flex: 使用 Flex 布局
 * flex-col: 子元素垂直排列
 * items-center: 水平居中
 * justify-center: 垂直居中
 * py-20: 上下内边距 80px
 * text-center: 文字居中
 */
function Hero() {
  return (
    <section className="flex flex-col items-center justify-center py-20 text-center">
      {/* text-4xl: 文字大小 36px */}
      {/* font-bold: 粗体 */}
      {/* text-gray-800: 深灰色文字 */}
      {/* mb-4: 下边距 16px */}
      <h1 className="text-4xl font-bold text-gray-800 mb-4">
        你好，我是开发者
      </h1>

      {/* text-xl: 文字大小 20px */}
      {/* text-gray-600: 中灰色文字 */}
      {/* mb-8: 下边距 32px */}
      {/* max-w-lg: 最大宽度 512px */}
      <p className="text-xl text-gray-600 mb-8 max-w-lg">
        我热爱前端开发，专注于 React 和现代 CSS 技术
      </p>

      {/* 按钮样式说明：
          px-6: 水平内边距 24px
          py-3: 垂直内边距 12px
          bg-blue-500: 背景蓝色
          text-white: 文字白色
          rounded-lg: 圆角
          hover:bg-blue-600: 悬停时背景变深
          transition-colors: 颜色过渡动画
      */}
      <button className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
        联系我
      </button>
    </section>
  )
}

export default Hero
