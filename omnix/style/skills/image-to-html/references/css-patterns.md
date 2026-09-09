# 常用 UI 组件 CSS 片段库

为「图片 1:1 转 HTML」提供可直接套用的单文件 CSS 片段。所有片段遵循：
- 零外部依赖，纯 CSS / 内联 SVG
- 颜色用 `var(--c-*)`（在 `:root` 定义，取 analyze_image.py 主色板）
- 圆角、阴影、间距尽量贴近源图 px 值

---

## 0. 基础骨架（reset + 变量）

```css
:root{
  --c-bg:#F5F5F7;        /* 页面底色，取自主色板 */
  --c-surface:#FFFFFF;   /* 卡片/面板 */
  --c-primary:#1677FF;   /* 主色 */
  --c-text:#1F2329;      /* 主文字 */
  --c-text-sub:#8A8F99;  /* 辅助文字 */
  --c-border:#E5E6EB;    /* 描边 */
  --radius:8px;
  --shadow:0 2px 8px rgba(0,0,0,.06);
  --font:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",
         "Hiragino Sans GB",Arial,sans-serif;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:var(--font);color:var(--c-text);background:var(--c-bg);-webkit-font-smoothing:antialiased}
.canvas{width:1200px;margin:0 auto;background:var(--c-surface)}  /* 固定宽度 1:1 画布 */
.ph{display:flex;align-items:center;justify-content:center;background:repeating-linear-gradient(45deg,#eee,#eee 10px,#e3e3e3 10px,#e3e3e3 20px);color:#999;font-size:12px}
```

---

## 1. 顶部导航 / Header

```css
.nav{height:64px;background:var(--c-surface);border-bottom:1px solid var(--c-border);
     display:flex;align-items:center;padding:0 24px;gap:24px}
.nav .logo{font-weight:700;font-size:18px;color:var(--c-primary)}
.nav .menu{display:flex;gap:20px;margin-left:auto}
.nav .menu a{color:var(--c-text-sub);text-decoration:none;font-size:14px}
.nav .menu a.active{color:var(--c-text)}
```

## 2. 按钮（主/次/幽灵）

```css
.btn{display:inline-flex;align-items:center;justify-content:center;height:36px;padding:0 16px;
     border-radius:var(--radius);font-size:14px;cursor:pointer;border:1px solid transparent}
.btn-primary{background:var(--c-primary);color:#fff}
.btn-ghost{background:transparent;border-color:var(--c-border);color:var(--c-text)}
.btn-text{background:none;color:var(--c-primary);padding:0 8px}
```

## 3. 卡片

```css
.card{background:var(--c-surface);border:1px solid var(--c-border);border-radius:var(--radius);
       box-shadow:var(--shadow);padding:20px}
```

## 4. 输入框 / 表单

```css
.field{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
.field label{font-size:13px;color:var(--c-text-sub)}
.input{height:36px;border:1px solid var(--c-border);border-radius:var(--radius);
       padding:0 12px;font-size:14px;outline:none}
.input:focus{border-color:var(--c-primary)}
```

## 5. 标签 / 徽标

```css
.tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;
     background:rgba(22,119,255,.1);color:var(--c-primary)}
.tag.gray{background:#F2F3F5;color:var(--c-text-sub)}
```

## 6. 表格

```css
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:12px 16px;text-align:left;border-bottom:1px solid var(--c-border)}
th{color:var(--c-text-sub);font-weight:500;background:#FAFAFB}
tr:hover td{background:#F7F8FA}
```

## 7. 图标（内联 SVG 示例：箭头 / 勾选）

```html
<!-- 右箭头 -->
<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
  <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
<!-- 对勾 -->
<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
  <path d="M3 8.5l3.2 3.2L13 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

## 8. 图片 / 插画占位

```html
<div class="ph" style="width:100%;height:180px;border-radius:var(--radius)">
  <!-- 替换为真实图：assets/hero.png (1200x180) -->
  图片占位 1200×180
</div>
```
