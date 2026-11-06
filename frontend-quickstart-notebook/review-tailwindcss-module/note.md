# Tailwind CSS 学习笔记

## 第一阶段：基础布局 ✅ 已完成

### 1.1 导航栏 (Navbar)
```html
<nav className="flex justify-between items-center p-4 bg-white shadow-sm">
  <div className="text-xl font-bold text-gray-800">Logo</div>
  <div className="flex gap-4">
    <a href="#">链接</a>
  </div>
</nav>
```
**关键类名**：
- `flex`: 启用 Flex 布局
- `justify-between`: 子元素两端对齐
- `items-center`: 子元素垂直居中
- `p-4`: 内边距 16px
- `shadow-sm`: 小阴影
- `gap-4`: 元素之间间距

### 1.2 Hero 区域
```html
<section className="flex flex-col items-center justify-center py-20 text-center">
  <h1 className="text-4xl font-bold text-gray-800 mb-4">标题</h1>
  <p className="text-xl text-gray-600 mb-8 max-w-lg">描述</p>
</section>
```
**关键类名**：
- `flex-col`: 垂直排列
- `items-center`: 水平居中
- `justify-center`: 垂直居中
- `py-20`: 上下内边距 80px
- `text-center`: 文字居中
- `mb-4`: 下边距 16px
- `max-w-lg`: 最大宽度 512px

### 1.3 按钮
```html
<button className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
  按钮文字
</button>
```
**关键类名**：
- `px-6`: 水平内边距 24px
- `py-3`: 垂直内边距 12px
- `bg-blue-500`: 背景蓝色
- `text-white`: 文字白色
- `rounded-lg`: 圆角
- `hover:bg-blue-600`: 悬停时背景变深
- `transition-colors`: 颜色过渡动画

### 1.4 常用布局类名速查
| 类名 | 含义 |
|------|------|
| `flex` | Flex 布局容器 |
| `flex-col` | 垂直排列 |
| `justify-center` | 水平居中 |
| `justify-between` | 两端对齐 |
| `justify-end` | 右对齐 |
| `items-center` | 垂直居中 |
| `gap-4` | 元素间距 16px |
| `container` | 限制最大宽度 |
| `mx-auto` | 水平居中 |

### 1.5 文字样式速查
| 类名 | 含义 |
|------|------|
| `text-xs` | 12px |
| `text-sm` | 14px |
| `text-base` | 16px |
| `text-lg` | 18px |
| `text-xl` | 20px |
| `text-2xl` | 24px |
| `text-3xl` | 30px |
| `text-4xl` | 36px |
| `font-bold` | 粗体 |
| `font-semibold` | 中等粗细 |
| `text-gray-600` | 浅灰色文字 |

### 1.6 间距速查
| 类名 | 含义 |
|------|------|
| `p-4` | 内边距 16px |
| `px-4` | 水平内边距 |
| `py-4` | 垂直内边距 |
| `m-4` | 外边距 16px |
| `mt-4` | 上外边距 |
| `mb-4` | 下外边距 |
| `ml-4` | 左外边距 |
| `mr-4` | 右外边距 |
| `gap-4` | 元素间距 |

### 1.7 颜色速查
- `gray`: 灰色系（50-900）
- `blue`: 蓝色系
- `red`: 红色系
- `green`: 绿色系
- `yellow`: 黄色系
- `bg-white` / `bg-gray-50` / `bg-gray-100` 等等

---

## 第二阶段：内容区块 ✅ 已完成

### 2.1 关于我 (About)
```html
<section className="py-16 bg-white">
  <div className="container mx-auto px-4">
    <h2 className="text-3xl font-bold text-center mb-12">关于我</h2>
    <div className="max-w-2xl mx-auto text-lg text-gray-600 leading-relaxed">
      <p className="mb-4">段落内容</p>
    </div>
  </div>
</section>
```
**新学类名**：
- `container`: 限制最大宽度（默认 max-w-screen-xl）
- `mx-auto`: 水平居中（自动左右边距）
- `py-16`: 上下内边距 64px
- `leading-relaxed`: 行高 1.625

### 2.2 技能展示 (Skills) - 药丸/标签样式
```html
<div className="flex flex-wrap gap-4 justify-center">
  <span className="px-4 py-2 bg-white text-gray-700 rounded-full shadow-sm text-sm font-medium hover:shadow-md transition-shadow">
    技能名称
  </span>
</div>
```
**新学类名**：
- `flex-wrap`: 允许子元素换行
- `rounded-full`: 完整圆角（药丸/胶囊形状）
- `shadow-sm`: 小阴影
- `shadow-md`: 中等阴影
- `transition-shadow`: 阴影过渡动画
- `font-medium`: 中等粗细（500）
- `text-sm`: 文字大小 14px

---

## 第三阶段：交互与响应式 ✅ 已完成

### 3.1 项目卡片 (Projects)
```html
<div className="grid grid-cols-1 md:grid-cols-3 gap-8">
  <div className="bg-gray-50 rounded-xl p-6 hover:-translate-y-1 hover:shadow-lg transition-all duration-300">
    <h3>项目标题</h3>
    <p>项目描述</p>
    <div className="flex flex-wrap gap-2">
      <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded text-xs">标签</span>
    </div>
  </div>
</div>
```
**新学类名**：
- `grid`: Grid 布局
- `grid-cols-1`: 默认 1 列
- `md:grid-cols-3`: 中等屏幕 3 列（响应式前缀）
- `gap-8`: 间距 32px
- `rounded-xl`: 较大圆角
- `p-6`: 内边距 24px
- `hover:-translate-y-1`: 悬停时向上移动
- `hover:shadow-lg`: 悬停时大阴影
- `transition-all`: 所有属性过渡
- `duration-300`: 过渡时长 300ms
- `bg-blue-100`: 浅蓝色背景
- `text-blue-700`: 深蓝色文字
- `text-xs`: 12px

### 3.2 联系我区域 (Contact)
```html
<div className="flex justify-center gap-4">
  <button className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
    主要按钮
  </button>
  <button className="px-6 py-3 bg-white text-gray-700 rounded-lg border border-gray-300 hover:bg-gray-100">
    次要按钮
  </button>
</div>
```
**新学类名**：
- `justify-center`: 水平居中
- `border`: 边框
- `border-gray-300`: 边框颜色

### 3.3 页脚 (Footer)
```html
<footer className="py-8 bg-white border-t border-gray-200">
  <p className="text-gray-500 text-sm">版权信息</p>
</footer>
```
**新学类名**：
- `border-t`: 顶部边框
- `border-gray-200`: 边框颜色（比 300 更浅）
- `text-gray-500`: 更浅的灰色文字

### 3.4 响应式前缀速查
| 前缀 | 触发条件 | 典型用途 |
|------|----------|----------|
| `sm:` | ≥640px | 手机横屏 |
| `md:` | ≥768px | 平板 |
| `lg:` | ≥1024px | 笔记本 |
| `xl:` | ≥1280px | 桌面显示器 |
| `2xl:` | ≥1536px | 大屏显示器 |

### 3.5 过渡动画速查
| 类名 | 用途 |
|------|------|
| `transition` | 默认过渡 |
| `transition-colors` | 颜色过渡 |
| `transition-all` | 所有属性过渡 |
| `transition-none` | 无过渡 |
| `duration-75/100/200/300/500` | 过渡时长 |

### 3.6 变换 (Transform)
| 类名 | 用途 |
|------|------|
| `scale-95/100/105` | 缩放 |
| `rotate-1/3/6/12` | 旋转角度 |
| `translate-x-1/2/4` | 水平位移 |
| `translate-y-1/2/4` | 垂直位移 |
| `-translate-y-1` | 向上移动（负值） |

---

## 常用快捷类名速查汇总

### 布局
- `flex` / `flex-col` / `flex-wrap`
- `justify-center` / `justify-between` / `justify-end`
- `items-center` / `items-start` / `items-end`
- `grid` / `grid-cols-3` / `grid-cols-4`
- `gap-2` / `gap-4` / `gap-8`

### 间距
- `p-4` / `px-4` / `py-4` / `pt-4` / `pb-4`
- `m-4` / `mx-auto` / `mt-4` / `mb-4`

### 文字
- `text-xs` ~ `text-6xl`
- `font-light` / `font-normal` / `font-medium` / `font-bold`
- `text-gray-500` 等颜色

### 背景与颜色
- `bg-white` / `bg-gray-50` / `bg-blue-500`
- `rounded` / `rounded-lg` / `rounded-full`

### 阴影
- `shadow-sm` / `shadow` / `shadow-lg`

### 交互
- `hover:bg-xxx` / `hover:text-xxx`
- `hover:-translate-y-1` / `hover:shadow-lg`
- `transition` / `transition-colors`

---

## CSS 动画与过渡学习（额外补充）

### 目录文件
`css-properties/index.html` - 学习目录页

### 文件列表
| 文件 | 内容 |
|------|------|
| `01-transform.html` | Transform 基础变换 |
| `02-transition.html` | Transition 过渡效果 |
| `03-animation.html` | Animation 关键帧动画 |
| `04-comprehensive.html` | 综合实战案例 |
