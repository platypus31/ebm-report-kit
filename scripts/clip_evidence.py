#!/usr/bin/env python3
"""從論文 PDF 裁「評讀佐證圖」：搜關鍵句 → 定位 → 裁該欄上下文 → 關鍵句畫紅框。

範本文體的靈魂是「每個評讀答案配原文截圖＋紅線」（report-spec.md §1-5）——本工具把這步機械化。

用法（用 ppt-master venv 跑，有 pymupdf）：
  PY=~/ppt-master/.venv/bin/python
  $PY scripts/clip_evidence.py paper.pdf --search "doubly-robust inverse propensity" -o out.png
  $PY scripts/clip_evidence.py paper.pdf --search "531 033 individuals" --pad-above 30 --pad-below 60 -o out.png
  $PY scripts/clip_evidence.py paper.pdf --page 8 --rect 0.05,0.33,0.95,0.82 -o fig2.png   # 手動比例裁（抓 Figure 用）

細節：
- 雙欄自動偵測：命中句中心在左半頁 → 只裁左欄（x: 0..0.52），右半 → 右欄（0.48..1）；--full-width 強制整寬。
- --search 可給多個（都畫紅框，裁區涵蓋全部命中）；找不到會 exit 2 並列出頁面文字供除錯。
- 全向量 PDF（JID/BMJ 等）抓 Figure：先用 search 找 caption 定位頁碼與 y，再用 --rect 裁圖區（caption 之上）。
"""
import argparse
import sys

import pymupdf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--search", action="append", default=[], help="關鍵句（可重複給多個）")
    ap.add_argument("--page", type=int, help="手動模式：頁碼(1-based)")
    ap.add_argument("--rect", help="手動模式：x0,y0,x1,y1（0-1 比例或 pt，任一值>1 視為 pt）")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--pad-above", type=float, default=25.0)
    ap.add_argument("--pad-below", type=float, default=25.0)
    ap.add_argument("--zoom", type=float, default=2.5, help="render 倍率（2.5≈180dpi）")
    ap.add_argument("--full-width", action="store_true", help="不做雙欄偵測，裁整頁寬")
    ap.add_argument("--no-box", action="store_true", help="不畫紅框（純裁圖）")
    args = ap.parse_args()

    doc = pymupdf.open(args.pdf)

    if args.rect:
        if args.page is None:
            sys.exit("--rect 需要 --page")
        pg = doc[args.page - 1]
        vals = [float(v) for v in args.rect.split(",")]
        if max(vals) <= 1.0:
            r = pymupdf.Rect(vals[0] * pg.rect.width, vals[1] * pg.rect.height,
                             vals[2] * pg.rect.width, vals[3] * pg.rect.height)
        else:
            r = pymupdf.Rect(*vals)
        pix = pg.get_pixmap(matrix=pymupdf.Matrix(args.zoom, args.zoom), clip=r)
        pix.save(args.out)
        print(f"✅ {args.out}  p{args.page} rect={r}  {pix.width}x{pix.height}")
        return

    if not args.search:
        sys.exit("要嘛 --search，要嘛 --page + --rect")

    # 搜尋模式：所有關鍵句必須在同一頁
    for pno, pg in enumerate(doc, 1):
        hits = []
        for q in args.search:
            r = pg.search_for(q)
            if r:
                hits.append((q, r[0]))
        if len(hits) == len(args.search):
            break
    else:
        print(f"❌ 找不到同時含全部關鍵句的頁面：{args.search}", file=sys.stderr)
        sys.exit(2)

    # 裁切範圍：涵蓋全部命中 + pad；雙欄偵測
    y0 = min(r.y0 for _, r in hits) - args.pad_above
    y1 = max(r.y1 for _, r in hits) + args.pad_below
    if args.full_width:
        x0, x1 = pg.rect.width * 0.03, pg.rect.width * 0.97
    else:
        cx = sum((r.x0 + r.x1) / 2 for _, r in hits) / len(hits)
        if cx < pg.rect.width / 2:
            x0, x1 = pg.rect.width * 0.03, pg.rect.width * 0.52
        else:
            x0, x1 = pg.rect.width * 0.48, pg.rect.width * 0.97
    clip = pymupdf.Rect(x0, max(0, y0), x1, min(pg.rect.height, y1))

    if not args.no_box:
        for _, r in hits:
            pg.draw_rect(pymupdf.Rect(r.x0 - 1.5, r.y0 - 1.5, r.x1 + 1.5, r.y1 + 1.5),
                         color=(0.85, 0, 0), width=1.2)

    pix = pg.get_pixmap(matrix=pymupdf.Matrix(args.zoom, args.zoom), clip=clip)
    pix.save(args.out)
    print(f"✅ {args.out}  p{pno} 命中 {len(hits)} 句  {pix.width}x{pix.height}")
    if args.no_box:
        # 輸出每個命中框在裁圖內的相對比例（引擎 figure `hl` 用：紅框改由 SVG 疊層＝pptx 可編輯形狀）
        for q, r0 in hits:
            rx0 = max((r0.x0 - 2 - clip.x0) / clip.width, 0.0)
            ry0 = max((r0.y0 - 2 - clip.y0) / clip.height, 0.0)
            rx1 = min((r0.x1 + 2 - clip.x0) / clip.width, 1.0)
            ry1 = min((r0.y1 + 2 - clip.y0) / clip.height, 1.0)
            print(f"HL [{rx0:.4f}, {ry0:.4f}, {rx1:.4f}, {ry1:.4f}]  # {q[:30]}")


if __name__ == "__main__":
    main()
