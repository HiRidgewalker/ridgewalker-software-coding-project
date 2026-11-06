/**
 * Projects 项目作品组件
 *
 * 样式说明：
 * py-16: 上下内边距 64px
 * bg-white: 背景白色
 */
function Projects() {
  // 项目数据
  const projects = [
    {
      title: '电商后台管理系统',
      description: '基于 React + TypeScript 构建的管理后台，包含订单管理、商品管理、用户管理等功能。',
      tags: ['React', 'TypeScript', 'Ant Design']
    },
    {
      title: '个人博客网站',
      description: '使用 Next.js 开发的静态博客，支持 Markdown 文章、SEO 优化和响应式设计。',
      tags: ['Next.js', 'Markdown', 'Tailwind CSS']
    },
    {
      title: '实时聊天应用',
      description: '基于 WebSocket 的实时聊天应用，支持群聊、私聊、消息提醒等功能。',
      tags: ['Vue', 'WebSocket', 'Node.js']
    }
  ]

  return (
    <section id="projects" className="py-16 bg-white">
      <div className="container mx-auto px-4">
        {/* text-3xl: 文字大小 30px */}
        {/* font-bold: 粗体 */}
        {/* text-center: 文字居中 */}
        {/* mb-12: 下边距 48px */}
        <h2 className="text-3xl font-bold text-center mb-12">项目作品</h2>

        {/* grid: 启用 Grid 布局 */}
        {/* grid-cols-1: 默认 1 列（移动端） */}
        {/* md:grid-cols-3: 中等屏幕 3 列 */}
        {/* gap-8: 元素间距 32px */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {projects.map((project, index) => (
            <div
              key={index}
              className="bg-gray-50 rounded-xl p-6 hover:-translate-y-1 hover:shadow-lg transition-all duration-300"
            >
              {/* 卡片样式：
                  bg-gray-50: 背景浅灰色
                  rounded-xl: 较大圆角
                  p-6: 内边距 24px
                  hover:-translate-y-1: 悬停时向上移动 4px
                  hover:shadow-lg: 悬停时大阴影
                  transition-all: 所有属性过渡
                  duration-300: 过渡时长 300ms
              */}

              {/* text-xl: 文字大小 20px */}
              {/* font-bold: 粗体 */}
              {/* text-gray-800: 深灰色文字 */}
              {/* mb-3: 下边距 12px */}
              <h3 className="text-xl font-bold text-gray-800 mb-3">
                {project.title}
              </h3>

              {/* text-gray-600: 中灰色文字 */}
              {/* text-sm: 文字大小 14px */}
              {/* leading-relaxed: 行高 1.625 */}
              {/* mb-4: 下边距 16px */}
              <p className="text-gray-600 text-sm leading-relaxed mb-4">
                {project.description}
              </p>

              {/* flex: 启用 Flex 布局 */}
              {/* flex-wrap: 允许换行 */}
              {/* gap-2: 子元素间距 8px */}
              <div className="flex flex-wrap gap-2">
                {/* 标签样式：
                    px-3: 水平内边距 12px
                    py-1: 垂直内边距 4px
                    bg-blue-100: 浅蓝色背景
                    text-blue-700: 深蓝色文字
                    rounded: 基础圆角
                    text-xs: 文字大小 12px
                */}
                {project.tags.map((tag, tagIndex) => (
                  <span
                    key={tagIndex}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-xs"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Projects
