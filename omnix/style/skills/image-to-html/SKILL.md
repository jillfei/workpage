---
name: image-to-html
description: 将 UI/网页设计稿或网页/App 截图按 1:1 还原为单文件 HTML+CSS（零外部依赖、双击即开）。This skill should be used when the user provides an image (design mockup, Figma/PS export, wireframe, or screenshot of a web page / app) and asks to "还原成 HTML"、"按图片生成网页"、"1:1 复刻这张图"、"把设计稿做成网页" or any request to reproduce a picture as pixel-faithful HTML.
agent_created: true
---

# Image to HTML（图片 1:1 还原为单文件 HTML）

## Overview

把一张图片（UI 设计稿、网页/App 截图）还原为与之高度一致、可编辑、零依赖的单文件 HTML。通过「多模态读图取结构+文字 → 脚本量化取精确尺寸与主色板 → 结构化还原 → 还原度自检 → 预览迭代」的标准流程，稳定产出 1:1 的 HTML 原型。

适用图片类型：UI/网页设计稿、现有网页/App 截图。不适用：纯照片/插画创作（应走生图类工具）。

## When to Use

用户出现以下任意信号时触发：
- 提供图片路径，并要求「生成 HTML / 做成网页 / 还原页面 / 1:1 复刻」。
- 说法如：「按这张图出一个页面」「把设计稿转成可编辑 HTML」「照着截图复刻一个网页」。
- 用户贴出截图并询问「这个能做成 HTML 吗」。

未提供图片时，先要求用户给出图片路径，不要凭空生成。

## Workflow

### Step 1 — 读取图片（多模态）
用 Read 工具读取用户提供的本地图片路径。读取后：
- **逐字转录**图片上的全部文字（导航、标题、按钮、表单、表格、页脚），1:1 还原要求文字准确、不可臆造。
- 记录整体画布观感、分区顺序、视觉风格（扁平/拟物、圆角、阴影、配色基调）。

### Step 2 — 量化分析（scripts/analyze_image.py）
运行分析脚本获取客观数据（managed venv 已装 Pillow）：

```bash
<managed_venv>/Scripts/python.exe scripts/analyze_image.py <图片路径> --top 12 --grid 16
```

关键产出用于后续编码：
- `width × height` → HTML 画布基准。
- `palette` → 定义为 `:root` CSS 变量（背景/主色/文字/边框）。
- `color grid` → 核对大区块位置（顶栏色、底部 footer 等）。

辅助用法：
- 定点取色：`--points "120,40;900,60"`
- 区域裁剪：`--crop x1,y1,x2,y2 --crop-out out.png`

> 完整方法见 `references/methodology.md`，组件级 CSS 见 `references/css-patterns.md`，起步骨架见 `assets/template.html`。

### Step 3 — 结构拆解
按 methodology.md 的拆解框架，把图片分解为：画布尺寸、分区顺序、栅格列距、间距节奏、字体层级、组件清单（按钮/输入框/卡片/表格/图标）、圆角阴影、图片占位。形成组件树后再动手写 HTML。

### Step 4 — 生成单文件 HTML+CSS
硬性规则：
- **单文件、零外部依赖**：CSS 写在 `<style>` 内；不引用任何 CDN/外部 CSS/JS/字体文件。
- **画布 1:1**：用 `.canvas{width:<img_width>px;margin:0 auto}` 包住整页；超宽图加缩放或滚动便于查看。需要响应式时以源图为 desktop 基准加 media query。
- **颜色**：全部用脚本 hex，定义为 `:root` 变量；半透明用 `rgba()`。
- **文字**：直接写入转录文本，保留原文标点和大小写；交互元素用语义标签 + `aria-label`。
- **图标/图片**：图标优先内联 SVG 或 CSS；照片/插画用 `.ph` 占位块保持宽高比，并注释「此处替换为真实图：路径/尺寸」。
- 直接基于 `assets/template.html` 结构扩展，或从空白按组件片段（`references/css-patterns.md`）拼装。

### Step 5 — 还原度自检
对照 methodology.md 的「还原度自检清单」逐项核对：画布尺寸、分区与 color grid 吻合、文字无遗漏、主色板已用、组件形态/圆角/阴影接近、字体层级正确、单文件零依赖可双击渲染。

### Step 6 — 预览与迭代
用 `present_files` 打开生成的 HTML 进入预览面板，告知用户「已按源图 1:1 还原，可对照查看；哪些细节（高度/布局/字段排列）需要微调」。按反馈定位具体区块修改，**不整体重写**，改完再次 `present_files`。

## 边界与异常处理
- 渐变/阴影：用 `linear-gradient` 与 `box-shadow`，必要时 `--points` 取起止色。
- 图表：用 CSS/SVG 近似还原形状与配色，数据标签按源图转录（静态还原，非动态可视化）。
- 照片区：占位块保持比例，注释待替换，不虚构内容。
- 深色/主题：默认还原所见主题；含明暗双态时优先主态并注明另一态待补。
