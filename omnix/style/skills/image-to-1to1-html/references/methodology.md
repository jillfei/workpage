# 像素级 1:1 还原方法（methodology）

本文件是 SKILL.md 的配套细节，给出可复现的还原流程与自检清单。

## 一、拆解框架（动手前先做这步）

把源图拆成 8 个维度，逐项落到笔记，再写 HTML：

| 维度 | 关注点 | 数据来源 |
|------|--------|----------|
| 画布尺寸 | 宽 × 高（px） | `analyze_image.py --size` |
| 分区顺序 | 从上到下 / 从左到右的区块流 | 多模态读图 |
| 栅格 | 列数、列宽、列间距 gutter | 读图 + grid 色块核对 |
| 间距节奏 | 区块内边距、区块间距（8/12/16/24…） | 读图估测 + measure 标尺 |
| 字体层级 | 标题/正文/辅助文字 的字号、字重、颜色、行高 | 读图估测 + `--points` 取色 |
| 组件清单 | 按钮/输入框/卡片/表格/徽标/导航/图标 | 多模态读图 |
| 圆角阴影 | border-radius、box-shadow 参数 | 读图估测 |
| 图片占位 | 照片/插画区域的位置与宽高比 | 多模态读图 |

## 二、坐标定位（最关键、最难）

1:1 还原的核心是把每个元素放到精确坐标。两种辅助手段：
- **读图估测**：直接在脑中给元素标包围盒（left, top, width, height）。
- **标尺覆盖图（推荐用于精确对齐）**：
  ```bash
  python scripts/analyze_image.py <图> --measure --measure-step 100 --measure-out measure_grid.png
  ```
  用 Read 打开 `measure_grid.png`，读取网格交点坐标（红=竖线/x，蓝=横线/y），反推元素四边落在哪个坐标。
- **定点取色**：核对某边界或渐变起止色：
  ```bash
  python scripts/analyze_image.py <图> --points "120,40;900,60"
  ```

落位写法（绝对定位）：
```css
.el { position:absolute; left:120px; top:40px; width:320px; height:48px; }
```
文字基线对齐用 `line-height` 等于容器高度，或 `top` 微调；多行文字块用 `padding` + 固定 `line-height`。

## 三、颜色还原

- 全部颜色来自 `analyze_image.py` 的 `palette` 与 `--points` 取色，定义为 `:root` 变量：
  ```css
  :root{
    --bg:#F5F6FA; --primary:#2F6BFF; --text:#1A1A1A;
    --text-sub:#8A8F99; --border:#E5E7EB;
  }
  ```
- 半透明：`rgba(R,G,B,A)`，用取到的 hex 换算。
- 渐变：`linear-gradient(135deg, #2F6BFF 0%, #1E4FD6 100%)`，起止色用 `--points` 取。

## 四、字体还原（禁用 Google Fonts，仅系统栈）

中文界面默认用系统 UI 字体栈，保证各 OS 一致观感：
```css
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
             "Microsoft YaHei", "Hiragino Sans GB", "Source Han Sans SC",
             "Noto Sans CJK SC", sans-serif;
```
- 字号：`font-size` 按读图估测（标题常见 20–28px、正文 13–15px、辅助 11–12px）。
- 字重：常规 400 / 中粗 500 / 加粗 600–700，用 `font-weight`。
- 字间距：`letter-spacing` 还原源图（标题常见 0.5–1px）。
- 特殊美术字：源图若用非系统字体，用最近系统字体近似，并加注释 `<!-- 字体近似：原图 XX -->`。

## 五、组件还原要点（对应 css-patterns.md）

- 按钮：圆角 + 背景主色 + 居中文字；次级按钮用描边 / 浅底。
- 输入框：1px 边框 + 内边距 + placeholder 颜色用 `--text-sub`。
- 卡片：白底 + 圆角 + 轻阴影 `box-shadow:0 2px 8px rgba(0,0,0,.06)`。
- 表格：表头底色 + 行分隔线 + 单元格对齐（数字右对齐）。
- 徽标 / tag：小圆角胶囊 + 浅色底 + 主色文字。
- 图标：内联 SVG（16–24px，`fill=currentColor`）或纯 CSS 形状。

## 六、还原度自检清单（Step 5 逐项打勾）

- [ ] 画布 `width × height` 与源图 `--size` 完全一致
- [ ] 各分区顺序、位置与 `grid` 色块吻合
- [ ] 转录文字无遗漏、无臆造，标点 / 大小写正确
- [ ] `:root` 主色板已使用，颜色与源图一致（肉眼 + 取色核对）
- [ ] 组件形态（圆角 / 阴影 / 边框）接近源图
- [ ] 字体层级（字号 / 字重 / 行高）正确
- [ ] 图标 / 照片区已用内联 SVG 或占位块，无外链图片
- [ ] **单文件、双击可渲染**
- [ ] **无任何 `<script src>` / `<link href>` 外链**
- [ ] **无 `cdn.tailwindcss.com`**
- [ ] **无 `fonts.googleapis.com` 及任何 Google Fonts 引用**
- [ ] **无其它 CDN / 图床引用**

任何一项不通过，回到 Step 4 局部修正，不要整体重写。
