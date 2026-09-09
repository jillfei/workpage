---
name: image-to-1to1-html
description: 将 UI 设计稿 / 网页·App 截图按 1:1 像素级还原为单文件、零外部依赖的 HTML。严格不使用任何外部 JS/CSS 库、不使用 cdn.tailwindcss.com、不使用 fonts.googleapis.com，所有样式内联在 style 标签、字体用系统字体栈。This skill should be used when the user provides an image (design mockup, Figma/PS export, wireframe, or screenshot of a web page / app) and asks to "按图片 1:1 生成 HTML"、"还原成网页"、"复刻这张图"、"把设计稿做成 HTML" or any request to reproduce a picture as pixel-faithful, self-contained HTML with no external dependencies.
agent_created: true
---

# Image to 1:1 HTML（图片 1:1 还原为单文件零依赖 HTML）

## Overview

把一张图片（UI 设计稿、网页 / App 截图）还原为与之高度一致、可编辑、**零外部依赖**的单文件 HTML。
通过「多模态读图取结构 + 文字 → 脚本量化取精确尺寸与主色板 → 绝对定位结构化还原 → 还原度自检 → 预览迭代」的标准流程，稳定产出 1:1 的 HTML 原型。

适用图片类型：UI / 网页设计稿、现有网页 / App 截图。不适用：纯照片 / 插画创作（应走生图类工具）。

## ⛔ 硬性约束（不可违反）

生成的 HTML **必须**满足以下全部条件，缺一项即视为不合格：

1. **单文件、零外部依赖**：所有 CSS 写在 `<style>` 内；除内联 SVG 外，不引用任何外部资源。
2. **禁用外部 JS / CSS 库**：不得出现 `<script src=...>`、`<link rel="stylesheet" href=...>` 指向任何第三方库。
3. **禁用 `cdn.tailwindcss.com`**：绝不允许 `<script src="https://cdn.tailwindcss.com">` 或 `<link href="https://cdn.tailwindcss.com">`。还原靠手写 CSS，不靠 Tailwind。
4. **禁用 `fonts.googleapis.com`**：绝不允许 `@import url('https://fonts.googleapis.com/...')` 或 `<link href="https://fonts.googleapis.com/...">`。字体一律使用**系统字体栈**（见下文）。
5. **禁用其他 CDN / 图床**：不引用任何 `https://*.cdn`、`https://unpkg.com`、`https://jsdelivr.net` 等资源。
6. 图片 / 图标：优先内联 SVG 或纯 CSS 绘制；照片位用占位块（保持宽高比 + 注释待替换），不引用外链图片。

> 自检时若出现以上任意链接，立即改为内联实现或系统字体 / 占位块。

## When to Use

用户出现以下任意信号时触发：
- 提供图片路径，并要求「生成 HTML / 做成网页 / 还原页面 / 1:1 复刻 / 按图出原型」。
- 说法如：「按这张图出一个页面」「把设计稿转成可编辑 HTML」「照着截图复刻一个网页」。
- 用户贴出截图并询问「这个能做成 HTML 吗」。

未提供图片时，先要求用户给出图片本地路径，不要凭空生成。

## Workflow

### Step 1 — 读取图片（多模态）
用 Read 工具读取用户提供的本地图片路径。读取后：
- **逐字转录**图片上的全部文字（导航、标题、按钮、表单、表格、页脚），1:1 还原要求文字准确、不可臆造。
- 记录整体画布观感、分区顺序、视觉风格（扁平 / 拟物、圆角、阴影、配色基调）。
- 估算各关键元素的包围盒坐标（左上 x,y / 宽高），作为 Step 4 绝对定位的输入。

### Step 2 — 量化分析（scripts/analyze_image.py）
用 default venv 的 Python 运行分析脚本获取客观数据（Pillow 已装）：

```bash
C:/Users/fei/.workbuddy/binaries/python/envs/default/Scripts/python.exe \
  scripts/analyze_image.py <图片路径> --top 12 --grid 12,8
```

关键产出用于后续编码：
- `size.width × size.height` → HTML 画布基准（`.canvas` 的 width/height）。
- `palette` → 定义为 `:root` CSS 变量（背景 / 主色 / 文字 / 边框）。
- `grid` → 核对大区块位置（顶栏色、底栏 footer、分栏）。

辅助用法：
- 定点取色（核对边界 / 渐变起止色）：`--points "120,40;900,60"`
- 区域裁剪（导出局部做参照 / 占位）：`--crop x1,y1,x2,y2 --crop-out out.png`
- 坐标标尺覆盖图（把视觉位置映射为坐标，辅助精确定位）：`--measure --measure-step 100 --measure-out measure_grid.png`，
  生成后用 Read 打开该 PNG，读取网格交点坐标来校正 Step 1 的估算。

> 详细方法见 `references/methodology.md`，组件级 CSS 片段见 `references/css-patterns.md`，起步骨架见 `assets/template.html`。

### Step 3 — 结构拆解
按 methodology.md 的拆解框架，把图片分解为：画布尺寸、分区顺序、栅格列距、间距节奏、字体层级、组件清单（按钮 / 输入框 / 卡片 / 表格 / 图标）、圆角阴影、图片占位。形成组件树后再动手写 HTML。

### Step 4 — 生成单文件 HTML + CSS（绝对定位还原）
基于 `assets/template.html` 结构扩展，核心规则：
- **画布 1:1**：`.canvas{position:relative;width:<img_width>px;height:<img_height>px;margin:0 auto}` 包住整页；超宽图可加 `transform:scale()` 或横向滚动便于查看。需要响应式时以源图为 desktop 基准加 media query。
- **坐标还原**：每个可视元素用 `position:absolute;left:..px;top:..px;width:..px;height:..px;` 精确落位；文字块用 `line-height` 对齐基线。
- **颜色**：全部用脚本 hex，定义为 `:root` 变量；半透明用 `rgba()`。
- **文字**：直接写入转录文本，保留原文标点 / 大小写；交互元素用语义标签 + `aria-label`。
- **字体（仅系统栈，禁用 Google Fonts）**：
  ```css
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
               "Microsoft YaHei", "Hiragino Sans GB", "Source Han Sans SC",
               "Noto Sans CJK SC", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "Courier New", monospace;
  ```
- **图标 / 图片**：图标优先内联 SVG 或 CSS；照片 / 插画用 `.ph` 占位块保持宽高比，并注释 `<!-- 此处替换为真实图：路径/尺寸 -->`。
- 轻交互（hover / 展开 / 切换）如需还原，用**原生 Vanilla JS**（写在页内 `<script>`，不引库）；纯静态展示可省略。

### Step 5 — 还原度自检
对照 methodology.md 的「还原度自检清单」逐项核对：
画布尺寸一致、分区与 color grid 吻合、文字无遗漏、主色板已用、组件形态 / 圆角 / 阴影接近、字体层级正确、
**单文件零依赖、无 cdn.tailwindcss.com / fonts.googleapis.com / 任何外链**可双击渲染。

### Step 6 — 预览与迭代
用 `present_files` 打开生成的 HTML 进入预览面板，告知用户「已按源图 1:1 还原，可对照查看；哪些细节（高度 / 布局 / 字段排列）需要微调」。
按反馈定位具体区块修改，**不整体重写**，改完再次 `present_files`。

## 边界与异常处理
- 渐变 / 阴影：用 `linear-gradient` / `radial-gradient` 与 `box-shadow`，必要时 `--points` 取起止色。
- 图表：用 CSS / SVG 近似还原形状与配色，数据标签按源图转录（静态还原，非动态可视化）。
- 照片区：占位块保持比例，注释待替换，不虚构内容。
- 深色 / 主题：默认还原所见主题；含明暗双态时优先主态并注明另一态待补。
- 字体缺口：若源图用了特殊美术字（非系统字体），用最接近的系统中文字体栈近似，并在注释标注「字体近似：原图用 XX」。
