# 组件 CSS 片段库（css-patterns）

供 1:1 还原时直接拼装。所有片段零依赖、纯 CSS（或内联 SVG），不引用任何外部资源。

## 设计令牌（粘贴到 :root）
```css
:root{
  --bg:#F5F6FA; --surface:#FFFFFF;
  --primary:#2F6BFF; --primary-ink:#FFFFFF;
  --text:#1A1A1A; --text-sub:#8A8F99; --text-faint:#B7BCC4;
  --border:#E5E7EB; --border-strong:#D0D5DD;
  --radius-s:6px; --radius-m:10px; --radius-l:16px;
  --shadow-card:0 2px 8px rgba(17,24,39,.06);
  --font-sans:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",
    "Microsoft YaHei","Hiragino Sans GB","Source Han Sans SC","Noto Sans CJK SC",sans-serif;
  --font-mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Courier New",monospace;
}
```

## 画布容器（1:1 基准）
```css
.canvas{ position:relative; width:1440px; height:900px; margin:0 auto;
  background:var(--bg); font-family:var(--font-sans); color:var(--text);
  overflow:hidden; }
```

## 顶部导航栏
```css
.nav{ position:absolute; left:0; top:0; width:1440px; height:56px;
  background:var(--surface); border-bottom:1px solid var(--border);
  display:flex; align-items:center; padding:0 24px; gap:20px; }
.nav .logo{ font-weight:700; font-size:18px; color:var(--primary); }
.nav .item{ font-size:14px; color:var(--text-sub); }
.nav .item.active{ color:var(--text); font-weight:600; }
```

## 主按钮 / 次级按钮
```css
.btn{ position:absolute; display:inline-flex; align-items:center; justify-content:center;
  height:40px; padding:0 20px; border-radius:var(--radius-m);
  background:var(--primary); color:var(--primary-ink); font-size:14px; font-weight:600;
  border:none; cursor:pointer; }
.btn.ghost{ background:transparent; color:var(--primary); border:1px solid var(--primary); }
```

## 输入框
```css
.input{ position:absolute; height:40px; padding:0 12px; border:1px solid var(--border-strong);
  border-radius:var(--radius-s); font-size:14px; color:var(--text); background:var(--surface); }
.input::placeholder{ color:var(--text-faint); }
```

## 卡片
```css
.card{ position:absolute; background:var(--surface); border:1px solid var(--border);
  border-radius:var(--radius-l); box-shadow:var(--shadow-card); padding:20px; }
```

## 数据表格
```css
.table{ position:absolute; width:100%; border-collapse:collapse; font-size:13px; }
.table th{ background:#F0F2F5; color:var(--text-sub); font-weight:600; text-align:left;
  padding:10px 12px; border-bottom:1px solid var(--border); }
.table td{ padding:10px 12px; border-bottom:1px solid var(--border); color:var(--text); }
.table td.num{ text-align:right; font-variant-numeric:tabular-nums; }
```

## 徽标 / Tag 胶囊
```css
.tag{ display:inline-flex; align-items:center; height:22px; padding:0 10px;
  border-radius:999px; background:rgba(47,107,255,.10); color:var(--primary);
  font-size:12px; font-weight:600; }
.tag.green{ background:rgba(22,163,74,.12); color:#16A34A; }
.tag.red{ background:rgba(220,38,38,.12); color:#DC2626; }
```

## 内联 SVG 图标（示例：搜索）
```html
<svg width="18" height="18" viewBox="0 0 24 24" fill="none"
     stroke="currentColor" stroke-width="2" stroke-linecap="round">
  <circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>
</svg>
```

## 照片 / 插画占位块
```css
.ph{ position:absolute; background:
  repeating-linear-gradient(45deg,#EEE,#EEE 10px,#E3E3E3 10px,#E3E3E3 20px);
  display:flex; align-items:center; justify-content:center;
  color:var(--text-faint); font-size:12px; }
```
```html
<!-- 此处替换为真实图：assets/banner.png，建议 1200x400 -->
<div class="ph" style="left:120px;top:120px;width:1200px;height:400px;">图片占位 1200×400</div>
```

## 轻交互（原生 Vanilla JS，不引库）
```html
<script>
  document.querySelectorAll('.nav .item').forEach(function(el){
    el.addEventListener('click', function(){
      document.querySelectorAll('.nav .item').forEach(function(n){n.classList.remove('active');});
      el.classList.add('active');
    });
  });
</script>
```
