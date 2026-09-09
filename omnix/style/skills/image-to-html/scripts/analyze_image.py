#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_image.py - 图片转 HTML 的像素级分析工具

为 "image-to-html" skill 提供精确的图片量化数据，支撑 1:1 还原：
  - 输出图片精确尺寸（宽 x 高，像素）与 DPI
  - 提取主色板（Top-N  dominant colors，带 hex 与占比）
  - 生成空间色彩分布网格（coarse color map），帮助理解版面分区
  - 支持定点取色（--points）与区域裁剪（--crop），用于精确还原特定元素

依赖：Pillow（已装入 managed venv）。
用法示例：
  python analyze_image.py design.png
  python analyze_image.py design.png --top 16 --grid 20 0
  python analyze_image.py design.png --points "120,40;900,60"
  python analyze_image.py design.png --crop 100,100,400,300 out/cropped.png
  python analyze_image.py design.png --json
"""

import argparse
import json
import os
import sys
from collections import Counter

try:
    from PIL import Image
except ImportError:
    sys.stderr.write(
        "ERROR: Pillow 未安装。请先在 managed venv 中执行：\n"
        "  <managed_python> -m venv <managed_venv> && "
        "<managed_venv>/Scripts/pip install Pillow\n"
    )
    sys.exit(2)


def hex_of(rgb):
    return "#{:02X}{:02X}{:02X}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def analyze(path, top_n=12, grid_cols=16, grid_rows=0, points=None, crop=None, as_json=False):
    if not os.path.isfile(path):
        sys.stderr.write("ERROR: 文件不存在: %s\n" % path)
        sys.exit(1)

    img = Image.open(path)
    img = img.convert("RGB")
    w, h = img.size
    dpi = img.info.get("dpi", None)

    result = {
        "file": os.path.abspath(path),
        "width": w,
        "height": h,
        "aspect_ratio": round(w / h, 4) if h else 0,
        "dpi": (list(dpi) if dpi else None),
    }

    # 主色板：自适应量化为 top_n*2 色，统计占比
    quant = img.convert("P", palette=Image.ADAPTIVE, colors=max(top_n * 2, 16))
    pal = quant.getpalette()
    try:
        _flat = quant.get_flattened_data()  # Pillow >= 12
    except AttributeError:
        _flat = quant.getdata()
    cols, counts = zip(*Counter(_flat).most_common(top_n * 2))
    palette = []
    total = sum(counts)
    for idx, cnt in zip(cols, counts):
        r, g, b = pal[idx * 3: idx * 3 + 3]
        palette.append({
            "hex": hex_of((r, g, b)),
            "rgb": [r, g, b],
            "percent": round(100.0 * cnt / total, 2),
        })
    # 只保留占比 > 0.3% 的，最多 top_n 个
    palette = [p for p in palette if p["percent"] >= 0.3][:top_n]
    result["palette"] = palette

    # 空间色彩分布网格
    if grid_rows <= 0:
        grid_rows = max(1, int(round(grid_cols * h / w / 2)))  # 控制总行数，避免过长
        grid_rows = min(grid_rows, 40)
    small = img.resize((grid_cols, grid_rows), Image.BILINEAR)
    pixels = small.load()
    grid = []
    for y in range(grid_rows):
        row = []
        for x in range(grid_cols):
            row.append(hex_of(pixels[x, y]))
        grid.append(row)
    result["grid"] = {"cols": grid_cols, "rows": grid_rows, "cells": grid}

    # 定点取色
    if points:
        sampled = []
        for pt in points:
            try:
                x, y = (int(v) for v in pt.split(","))
                if 0 <= x < w and 0 <= y < h:
                    sampled.append({"x": x, "y": y, "hex": hex_of(img.getpixel((x, y)))})
                else:
                    sampled.append({"x": x, "y": y, "error": "out of bounds"})
            except Exception as e:
                sampled.append({"point": pt, "error": str(e)})
        result["points"] = sampled

    # 区域裁剪
    if crop:
        try:
            x1, y1, x2, y2 = (int(v) for v in crop.split(","))
            box = (max(0, x1), max(0, y1), min(w, x2), min(h, y2))
            region = img.crop(box)
            out_dir = os.path.dirname(crop_out) if False else None
            # crop_out 在 main 中解析后传入
        except Exception as e:
            result["crop_error"] = str(e)

    return result


def main():
    ap = argparse.ArgumentParser(description="图片像素级分析（image-to-html skill 配套）")
    ap.add_argument("image", help="图片路径")
    ap.add_argument("--top", type=int, default=12, help="主色板数量（默认 12）")
    ap.add_argument("--grid", type=int, default=16, help="色彩网格列数（默认 16）")
    ap.add_argument("--rows", type=int, default=0, help="色彩网格行数（默认按宽高比自动）")
    ap.add_argument("--points", type=str, default="", help="定点取色，格式 'x,y;x,y'")
    ap.add_argument("--crop", type=str, default="", help="区域裁剪，格式 'x1,y1,x2,y2'，需配合 --crop-out")
    ap.add_argument("--crop-out", type=str, default="", help="裁剪输出文件路径")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出（便于程序解析）")
    args = ap.parse_args()

    points = [p for p in args.points.split(";") if p.strip()] if args.points else None

    crop_file = None
    if args.crop:
        if not args.crop_out:
            sys.stderr.write("ERROR: 使用 --crop 时必须提供 --crop-out 输出路径\n")
            sys.exit(1)
        crop_file = args.crop_out

    result = analyze(
        args.image,
        top_n=args.top,
        grid_cols=args.grid,
        grid_rows=args.rows,
        points=points,
    )

    # 执行裁剪（在 analyze 后单独处理，避免噪音进入 result）
    if args.crop and crop_file:
        try:
            from PIL import Image as _I
            img = _I.open(args.image).convert("RGB")
            w, h = img.size
            x1, y1, x2, y2 = (int(v) for v in args.crop.split(","))
            box = (max(0, x1), max(0, y1), min(w, x2), min(h, y2))
            region = img.crop(box)
            os.makedirs(os.path.dirname(os.path.abspath(crop_file)), exist_ok=True)
            region.save(crop_file)
            result["crop"] = {
                "box": list(box),
                "size": list(region.size),
                "saved_to": os.path.abspath(crop_file),
            }
        except Exception as e:
            result["crop_error"] = str(e)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # 人类可读输出
    out = []
    out.append("=" * 60)
    out.append("图片分析: %s" % result["file"])
    out.append("-" * 60)
    out.append("尺寸: %dx%d px  | 宽高比: %s" % (result["width"], result["height"], result["aspect_ratio"]))
    if result["dpi"]:
        out.append("DPI : %s" % result["dpi"])
    out.append("")
    out.append("主色板 (Top %d):" % len(result["palette"]))
    for i, p in enumerate(result["palette"], 1):
        out.append("  %2d. %s  rgb(%s)  %s%%" % (i, p["hex"], ",".join(map(str, p["rgb"])), p["percent"]))
    out.append("")
    out.append("空间色彩分布网格 (%dx%d，左上为原点):" % (result["grid"]["cols"], result["grid"]["rows"]))
    for row in result["grid"]["cells"]:
        out.append("  " + " ".join(row))
    out.append("")
    if "points" in result:
        out.append("定点取色:")
        for s in result["points"]:
            if "error" in s:
                out.append("  %s -> ERROR: %s" % (s.get("point", ""), s["error"]))
            else:
                out.append("  (%d,%d) -> %s" % (s["x"], s["y"], s["hex"]))
        out.append("")
    if "crop" in result:
        out.append("裁剪: box=%s size=%s -> %s" % (result["crop"]["box"], result["crop"]["size"], result["crop"]["saved_to"]))
    if "crop_error" in result:
        out.append("裁剪错误: %s" % result["crop_error"])
    out.append("=" * 60)
    print("\n".join(out))


if __name__ == "__main__":
    main()
