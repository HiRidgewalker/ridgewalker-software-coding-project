# CLAUDE.md - Tailwind CSS 练习项目

## 项目概述
- **用途**: Tailwind CSS 实战练习
- **技术栈**: Vite + React + JavaScript + Tailwind CSS v4

## 项目结构
```
review-tailwindcss-module/
├── src/
│   ├── components/       # 组件目录
│   │   ├── Navbar.jsx    # 导航栏
│   │   ├── Hero.jsx      # 首屏区域
│   │   ├── About.jsx     # 关于我
│   │   ├── Skills.jsx    # 技能展示
│   │   ├── Projects.jsx  # 项目作品
│   │   ├── Contact.jsx   # 联系我
│   │   └── Footer.jsx    # 页脚
│   ├── pages/            # 页面目录（待用）
│   ├── store/            # 状态管理（待用）
│   ├── App.jsx           # 主应用
│   ├── index.css         # Tailwind 入口
│   └── main.jsx          # 入口文件
├── note.md               # 学习笔记
├── CLAUDE.md             # 项目记忆文件
└── package.json
```

## 启动命令
```bash
npm run dev
```

---

## 练习计划

### 第一阶段：基础布局 ✅ 已完成
- [x] 搭建项目环境（Vite + React + Tailwind v4）
- [x] 创建 note.md 笔记文件
- [x] 导航栏（Navbar）
- [x] Hero 区域
- [x] "联系我" 按钮

**本阶段学到**：
- `flex` 布局、`justify-between`、`items-center`
- `p-4`、`px-4`、`py-2` 内边距
- `text-xl`、`font-bold`、`text-center` 文字样式
- 按钮的 `hover:bg-xxx` 交互效果

---

### 第二阶段：内容区块 ✅ 已完成
- [x] 关于我区块（About）
- [x] 技能展示（Skills）- 药丸/标签样式

**本阶段学到**：
- `container`、`mx-auto` 居中布局
- `flex-wrap` 换行
- `rounded-full` 药丸形状
- `shadow-sm`、`shadow-md` 阴影

---

### 第三阶段：交互与响应式 ✅ 已完成
- [x] 项目作品卡片（Grid 布局）
- [x] 卡片 hover 浮起效果（`hover:-translate-y-1`）
- [x] 联系我区域
- [x] 页脚
- [x] 移动端响应式适配（`md:` 前缀）

**本阶段学到**：
- `grid`、`grid-cols-1`、`md:grid-cols-3` 响应式网格
- `hover:shadow-lg` 悬停阴影
- `transition-all`、`duration-300` 过渡动画
- `border-t` 顶部边框

---

## 常用命令
- `npm run dev` - 启动开发服务器
- `npm run build` - 构建生产版本

---

## CSS 动画与过渡学习（额外补充）

### 学习文件位置
`css-properties/` 目录

### 文件列表
| 文件 | 内容 |
|------|------|
| `css-properties/index.html` | 学习目录页 |
| `css-properties/01-transform.html` | Transform 基础变换 |
| `css-properties/02-transition.html` | Transition 过渡效果 |
| `css-properties/03-animation.html` | Animation 关键帧动画 |
| `css-properties/04-comprehensive.html` | 综合实战案例 |

### 学习顺序建议
1. **01-transform.html** - 先学基础变换
2. **02-transition.html** - 再学过渡效果
3. **03-animation.html** - 然后关键帧动画
4. **04-comprehensive.html** - 最后综合实战
