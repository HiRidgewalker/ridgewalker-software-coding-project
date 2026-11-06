/**
 * About 关于我组件
 *
 * 样式说明：
 * py-16: 上下内边距 64px
 * bg-white: 背景白色
 */
function About() {
  return (
    <section id="about" className="py-16 bg-white">
      {/* container: 限制最大宽度并居中 */}
      {/* mx-auto: 水平居中 */}
      <div className="container mx-auto px-4">
        {/* text-3xl: 文字大小 30px */}
        {/* font-bold: 粗体 */}
        {/* text-center: 文字居中 */}
        {/* mb-12: 下边距 48px */}
        <h2 className="text-3xl font-bold text-center mb-12">关于我</h2>

        {/* max-w-2xl: 最大宽度 576px */}
        {/* mx-auto: 水平居中 */}
        {/* text-lg: 文字大小 18px */}
        {/* text-gray-600: 中灰色文字 */}
        {/* leading-relaxed: 行高 1.625，更宽松 */}
        <div className="max-w-2xl mx-auto text-lg text-gray-600 leading-relaxed">
          <p className="mb-4">
            我是一名专注前端开发的工程师，热爱创造优美的用户界面和流畅的用户体验。
          </p>
          <p>
            擅长 React、Vue 等现代前端框架，对 Tailwind CSS 有深入研究。
          </p>
        </div>
      </div>
    </section>
  )
}

export default About
