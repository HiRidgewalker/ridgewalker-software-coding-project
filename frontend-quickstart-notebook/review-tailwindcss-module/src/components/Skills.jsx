/**
 * Skills 技能展示组件
 *
 * 样式说明：
 * py-16: 上下内边距 64px
 * bg-gray-50: 背景浅灰色
 */
function Skills() {
  // 技能列表数据
  const skills = [
    'React', 'Vue', 'JavaScript', 'TypeScript',
    'Tailwind CSS', 'Node.js', 'Git', 'Webpack'
  ]

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        {/* text-3xl: 文字大小 30px */}
        {/* font-bold: 粗体 */}
        {/* text-center: 文字居中 */}
        {/* mb-12: 下边距 48px */}
        <h2 className="text-3xl font-bold text-center mb-12">技能展示</h2>

        {/* flex: 启用 Flex 布局 */}
        {/* flex-wrap: 允许换行 */}
        {/* gap-4: 子元素间距 16px */}
        {/* justify-center: 水平居中 */}
        <div className="flex flex-wrap gap-4 justify-center">
          {/* 技能标签样式：
              px-4: 水平内边距 16px
              py-2: 垂直内边距 8px
              bg-white: 背景白色
              text-gray-700: 文字深灰色
              rounded-full: 完整圆角（药丸形状）
              shadow-sm: 小阴影
              text-sm: 文字大小 14px
              font-medium: 中等粗细
              hover:shadow-md: 悬停时阴影加深
              transition-shadow: 阴影过渡动画
          */}
          {skills.map((skill, index) => (
            <span
              key={index}
              className="px-4 py-2 bg-white text-gray-700 rounded-full shadow-sm text-sm font-medium hover:shadow-md transition-shadow"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Skills
