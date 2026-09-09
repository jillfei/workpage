#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
analyze_image.py - 图片量化分析辅助脚本（图片 → 1:1 HTML 专用）

提供客观数据，辅助 WorkBuddy 把一张图片 1:1 还原为单文件 HTML：
  - 画布尺寸 (width × height)         → HTML 画布基准
  - 主色板 (palette)                  → 定义为 :root CSS 变量
  - 色块网格 (color grid)             → 核对大区块位置（顶栏/底栏/分栏）
  - 定点取色 (--points)               → 精确核对某像素颜色
  - 区域裁剪 (--crop)                 → 导出局部做参照 / 占位图
  - 坐标标尺覆盖图 (--measure)        → 叠加网格与坐标，辅助模型定位元素坐标

仅依赖 Pillow。用法见各子命令 / -h。
"""
import argparse
import json
import sys
from PIL import Image


def hex_of(rgb):
    return "#%02X%02X%02X" % (rgb[0], rgb[1], rgb[2])


def get_size(img):
    return img.size  # (width, height)


def get_palette(img, top=12):
    """返回出现频率最高的若干主色（量化后统计）。"""
    small = img.convert("RGB").resize((160, 160))  # 缩小提速，颜色分布近似
    q = small.quantize(colors=top, method=Image.Quantize.MAXCOVERAGE)
    palette = q.getpalette()  # 768 长度
    counts = q.getcolors()    # [(count, index), ...]
    out = []
    for count, idx in sorted(counts, reverse=True)[:top]:
        r, g, b = palette[idx * 3: idx * 3 + 3]
        out.append({"hex": hex_of((r, g, b)), "count": count})
    return out


def get_grid(img, cols=12, rows=8):
    """把画布切成 cols×rows 网格，返回每格平均色 hex（左上→右下）。"""
    w, h = img.size
    cw, ch = w / cols, h / rows
    grid = []
    for ry in range(rows):
        row = []
        for cx in range(cols):
            box = (int(cx * cw), int(ry * ch), int((cx + 1) * cw), int((ry + 1) * ch))
            crop = img.crop(box).resize((1, 1)).convert("RGB")
            row.append(hex_of(crop.getpixel((0, 0))))
        grid.append(row)
    return grid


def sample_points(img, points):
    """points: list of (x, y)，返回每个点的 hex。"""
    out = []
    for (x, y) in points:
        x = min(max(x, 0), img.size[0] - 1)
        y = min(max(y, 0), img.size[1] - 1)
        out.append({"x": x, "y": y, "hex": hex_of(img.convert("RGB").getpixel((x, y)))})
    return out


def crop_region(img, box, out_path):
    x1, y1, x2, y2 = box
    x1, x2 = max(0, min(x1, x2)), min(img.size[0], max(x1, x2))
    y1, y2 = max(0, min(y1, y2)), min(img.size[1], max(y1, y2))
    img.crop((x1, y1, x2, y2)).save(out_path)
    return out_path


def make_measure_grid(img, step=100, out_path="measure_grid.png"):
    """在副本上叠加网格线与坐标标签，输出 PNG，辅助模型把视觉位置映射为坐标。"""
    from PIL import ImageDraw, ImageFont
    base = img.convert("RGB").copy()
    d = ImageDraw.Draw(base)
    w, h = base.size
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    # 竖线 + x 坐标
    for x in range(0, w + 1, step):
        d.line([(x, 0), (x, h)], fill=(255, 0, 0), width=1)
        if x < w:
            d.text((x + 2, 2), str(x), fill=(255, 0, 0), font=font)
    # 横线 + y 坐标
    for y in range(0, h + 1, step):
        d.line([(0, y), (w, y)], fill=(0, 0, 255), width=1)
        if y < h:
            d.text((2, y + 2), str(y), fill=(0, 0, 255), font=font)
    base.save(out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="图片量化分析（1:1 还原 HTML 辅助）")
    ap.add_argument("image", help="图片路径")
    ap.add_argument("--size", action="store_true", help="输出画布尺寸")
    ap.add_argument("--top", type=int, default=12, help="主色数量 (默认 12)")
    ap.add_argument("--grid", type=str, default=None,
                    help="色块网格列数,行数，如 --grid 12,8")
    ap.add_argument("--points", type=str, default=None,
                    help="定点取色，分号分隔 x,y，如 --points \"120,40;900,60\"")
    ap.add_argument("--crop", type=str, default=None,
                    help="区域裁剪 x1,y1,x2,y2")
    ap.add_argument("--crop-out", type=str, default="crop.png", help="裁剪输出路径")
    ap.add_argument("--measure", action="store_true", help="生成坐标标尺覆盖图")
    ap.add_argument("--measure-step", type=int, default=100, help="标尺步长 px")
    ap.add_argument("--measure-out", type=str, default="measure_grid.png")
    args = ap.parse_args()

    try:
        img = Image.open(args.image)
    except Exception as e:
        print(json.dumps({"error": "无法打开图片: %s" % e}, ensure_ascii=False))
        sys.exit(1)

    result = {}
    w, h = get_size(img)
    result["size"] = {"width": w, "height": h}

    if args.size:
        print("width=%d height=%d" % (w, h))
    else:
        if args.grid:
            cols, rows = (int(v) for v in args.grid.split(","))
            result["grid"] = get_grid(img, cols, rows)
        if args.points:
            pts = [tuple(int(v) for v in p.split(",")) for p in args.points.split(";") if p]
            result["points"] = sample_points(img, pts)
        if args.crop:
            box = tuple(int(v) for v in args.crop.split(","))
            result["crop"] = crop_region(img, box, args.crop_out)
        if args.measure:
            result["measure"] = make_measure_grid(img, args.measure_step, args.measure_out)
        if not args.grid and not args.points and not args.crop and not args.measure:
            result["palette"] = get_palette(img, args.top)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
