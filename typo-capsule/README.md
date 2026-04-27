# 💊 TypoCapsule (排版时间胶囊)

> **“将你的思绪作为数据碎片，封存进深邃的数字虚空。”**

## 📖 项目说明
**TypoCapsule** 是一个带有“赛博考古 (Cyber-Archaeology)”和“极简实体感”风格的文字记录工具。它刻意摒弃了现代 Web 设计中泛滥的平滑圆角、毛玻璃（Glassmorphism）和渐变阴影，采用粗粝的像素噪点、CRT 扫描线和悬浮物理感，创造出一种老旧但又极具未来感的“数据封存”体验。

---

## 🏗️ 开发概要 (Development Summary)

### 1. 技术栈与架构
- **前端框架**: React 18 + Vite
- **样式方案**: 纯原生 CSS (原生 CSS Grid/Flexbox/Animations)
- **设计规范**: 无圆角、1px 极简硬边框、单色系（黑客绿 `#00ff41`）、全大写终端指令。

### 2. 核心逻辑实现
本项目的核心在于 `App.jsx` 和 `App.css` 的高度配合：

- **动态时序系统**:
  - `App.jsx` 中的 `useEffect` 维护了一个每秒更新的时间戳，格式化为类似 `ARCHIVE_2026_04_16_T14:30:00` 的冷酷编号，增强归档感。
- **视觉反馈系统 (Glitch)**:
  - 监听 `textarea` 的输入事件，每敲击一个字符触发一次极短的 `isGlitching` 状态。
  - CSS 中定义 `@keyframes text-glitch`，利用瞬间的色彩错位（品红/青色）和位移，模拟老旧终端接触不良的故障感。
- **悬浮与空间系统 (Floating Physics)**:
  - 容器通过 `@keyframes float` 结合 `rotateX/Y` 赋予容器缓慢的 3D 呼吸感。
  - 背景摒弃纯黑，采用极细的 `linear-gradient` 交叉绘制出坐标网格（Coordinate Grid），营造“深度空间”的错觉。
- **数据封存系统 (Data Fragmentation)**:
  - 点击保存后，锁定输入和按钮。
  - 触发 `sealing` 类名，执行 `@keyframes fragment-seal`：容器瞬间提亮曝光，随后急速沿 Y 轴收缩、翻转并消失在视野外。

---

## 🚀 部署及运行方式

### 环境要求
- **Node.js**: 推荐 v18 或更高版本
- **包管理器**: npm 或 yarn

### 1. 安装依赖
克隆或下载项目后，在终端进入 `typo-capsule` 根目录并执行：
```bash
npm install
```

### 2. 本地开发运行
启动本地 Vite 开发服务器：
```bash
npm run dev
```
运行成功后，在浏览器中访问终端输出的本地地址（通常是 `http://localhost:5173`），即可体验悬浮胶囊的交互效果。

### 3. 构建生产版本
当需要部署到线上环境时，执行构建命令：
```bash
npm run build
```
构建完成后，项目根目录会生成一个 `dist` 文件夹。你可以将 `dist` 文件夹中的所有静态文件直接部署到如 **Vercel**、**Netlify**、**GitHub Pages** 或任何 Nginx/Apache 静态服务器上。
