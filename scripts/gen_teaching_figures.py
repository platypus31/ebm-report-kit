#!/usr/bin/env python3
"""EBM 固定教學圖產生器 —— 程式生成六張全頁 SVG（White Grey 風格，可版控可重生）。

這六張是**跨報告重複使用**的教學圖（證據金字塔／證據等級表／評讀工具對照／評讀流程／VIP 框架）。
坊間流通的版本多半有版權，本 repo 不轉貼；改以「公開學術事實自行重繪」——
分級內容、工具清單、流程步驟本身是公開事實，可以合法重畫，版式則完全自製。

產出：`data/assets/*.svg`，每張都是 1280x720 全頁版面，可直接當一張投影片用
（content.json 走 `{"kind": "asset", "path": "data/assets/<檔名>.svg"}`，見 gen_journal_svg.py）。

風格常數（畫布、底色、波紋、字級、灰階）一律 import 自 `gen_journal_svg.py`，不另立一套。

用法（只用標準庫，系統 python3 即可）：
    python3 scripts/gen_teaching_figures.py [輸出目錄]      # 預設 data/assets
    python3 scripts/gen_teaching_figures.py --list          # 只列出會產生哪些檔

版面契約（與 gen_journal_svg.py 的 asset 頁型對齊，改圖時請守住）：
    y 168-648  圖本體（含圖內註腳）
    y 656-676  caption 帶（由 content.json 的 caption 注入，本檔不得佔用）
    y 690-710  出處註記（本檔畫，靠左小字灰階）
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gen_journal_svg import W, cjk_wrap, dots, head, txt, waves  # noqa: E402

# ── 版面契約 ───────────────────────────────────────────────────────────────
BODY_TOP = 168      # 圖本體上緣（標題橫線下方）
BODY_BOTTOM = 648   # 圖本體下緣；再往下是 caption 帶與出處註記，本檔不得越界
NOTE_Y = 700        # 出處註記末行基線（多行時往上長）
NOTE_TOP_LIMIT = 690  # 出處註記首行基線的上限：再高就會壓到 caption 帶（676 底緣＋字身餘裕）
MARGIN_L, MARGIN_R = 90, 1190

# ── 灰階（沿用 gen_journal_svg 既有色票，不新增色系）───────────────────────
INK = "#1A1D21"        # 內文黑
INK_SOFT = "#2A2A2A"
MUTED = "#8A9099"      # 註記灰（同 caption 色）
LINE = "#B0B6BE"       # 格線
RULE = "#C4C9D0"       # 標題橫線
HEAD_BG = "#3D434B"    # 表頭深灰
PANEL = "#F0F2F5"      # 淺底塊


def frame(title):
    """共用頁框：底色＋右上波紋＋左上圓點＋標題＋橫線（同 content/table 頁）。"""
    s = head()
    s.append(waves(1150, 90, 12, 12, 34, 160, 0.6, -1))
    s.append(dots(70, 70))
    s.append(txt(MARGIN_L, 120, title, 46, ls="1.2"))
    s.append(f'<line x1="{MARGIN_L}" y1="145" x2="{MARGIN_R}" y2="145" stroke="{RULE}" stroke-width="2"/>')
    return s


def source_note(s, name, text, fs=15):
    """底部出處註記（比內文小、灰階）。

    過長會自動折行並**往上**長（末行固定貼齊 NOTE_Y），因為橫向出血 `check_overflow` 看不見——
    ppt-master 的 svg_quality_checker 會把它判成 blocking error（實測：中文版等級表的出處註記
    單行寬 1301px > 畫布 1280）。往上長的代價是會侵入 caption 帶，所以另立 `NOTE_TOP_LIMIT` 守住
    （`check_overflow` 只驗「往下」那一邊，對這裡完全沒有訊號）。
    """
    lines = wrap_fit(text, int((MARGIN_R - MARGIN_L) / (fs * 0.52)))
    y = NOTE_Y - (len(lines) - 1) * (fs + 5)
    if y < NOTE_TOP_LIMIT:
        sys.stderr.write(f"WARN {name}：出處註記 {len(lines)} 行，首行 y={y} 高過 {NOTE_TOP_LIMIT}，"
                         f"會壓到 caption 帶（請縮短文字）\n")
    for ln in lines:
        s.append(txt(MARGIN_L, y, ln, fs, MUTED, "400", ls="0.2"))
        y += fs + 5


def save(outdir, name, body):
    path = os.path.join(outdir, f"{name}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(body + ["</svg>"]))
    return path


def check_overflow(name, y, limit=BODY_BOTTOM):
    """內容底緣越界就示警——生成端零檢查的話沒人會發現。

    `limit` 要跟呼叫端**算版面預算時用的同一條線**：表格的 y_max 通常小於 BODY_BOTTOM
    （下面還要留給 footnotes），寫死 BODY_BOTTOM 的話，表格漲進「y_max 與 BODY_BOTTOM 之間」
    那段就會壓掉 footnotes 卻不出聲。預設 BODY_BOTTOM 給「本體最後一段內容」用。
    """
    if y > limit:
        sys.stderr.write(f"WARN {name}：內容底緣 y={y:.0f} 超過本區上限 {limit}，會壓到下一段（footnotes／caption 帶）\n")


# ── 通用表格繪製（自動縮字以塞進版面）───────────────────────────────────────

# 中文斷行禁則：這兩串字元不得落在行首／行尾（不處理的話會出現孤零零的「）」自成一行）
_NO_LINE_START = "）〕］｝〉》」』】、，。．：；？！%‰°℃)]}>,.?!:;*＊"  # `*` 是等級表的註腳記號，落單一行會被誤讀成星號項目
_NO_LINE_END = "（〔［｛〈《「『【([{<"


KINSOKU_MAX_SHIFT = 2   # wrap() 每行最多把前一行尾端搬幾個字下來（實測六張圖會用到第 2 次）


def text_units(s):
    """全形 2 單位、半形 1 單位——與 cjk_wrap 同一把尺。"""
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in str(s))


def wrap(s, units):
    """cjk_wrap ＋ 禁則處理。

    斷行本身沿用引擎的 `cjk_wrap`（全形 2 單位／半形 1 單位），這裡只做「把違規標點連同前一個字
    一起推到下一行」。⚠️ 推字會讓下一行變長、可能超出 `units`——本函式**不保證**行寬，
    要保證請用 `wrap_fit()`。
    """
    lines = [str(x) for x in cjk_wrap(s, units)]
    for i in range(1, len(lines)):
        for _ in range(KINSOKU_MAX_SHIFT):  # 有上限才不會被連續標點拖成無限迴圈
            prev, cur = lines[i - 1], lines[i]
            bad_start = cur and cur[0] in _NO_LINE_START
            bad_end = prev and prev[-1] in _NO_LINE_END
            if (bad_start or bad_end) and len(prev) > 1:
                lines[i - 1], lines[i] = prev[:-1], prev[-1] + cur
                continue
            break
    return [ln for ln in lines if ln] or [""]


def wrap_fit(s, units):
    """斷行＋禁則，並**保證**每一行都真的塞得進 units。

    禁則推字會讓下一行變寬，天真作法是量測時一律預留餘裕；但餘裕是按最壞情況算的，
    窄欄付不起——實測 OCEBM 英文表的 Step 5 欄（108px）在預留 4 單位後只剩 9 單位，
    連 "Mechanism-based" 都放不下而被逐字硬切，整張表被逼到最小字級還是溢出。
    改成「推完再量，超寬才用更窄的寬度重斷」：不觸發禁則的欄位一次就過、零成本，
    只有真的被推寬的欄位才付出縮一點的代價。
    """
    lines = wrap(s, units)
    for shrink in range(1, 2 * KINSOKU_MAX_SHIFT + 1):
        if all(text_units(ln) <= units for ln in lines):
            return lines
        lines = wrap(s, units - shrink)
        if units - shrink < 4:
            break
    if all(text_units(ln) <= units for ln in lines):
        return lines
    # 欄窄到禁則怎麼縮都塞不下（實測 units<6 的極窄欄）：寧可留下孤標點也不要超寬——
    # 超寬是橫向出血，ppt-master 會判 blocking error；孤標點只是難看。
    return [str(x) for x in cjk_wrap(s, units)]


def _measure(rows_text, widths, fs, lh, pad):
    """回傳 (各列行數清單, 總高)。rows_text = [[cell_str, ...], ...]（含表頭列）。"""
    per_row = []
    for row in rows_text:
        lines = []
        for i, cell in enumerate(row):
            units = max(int((widths[i] - 2 * pad) / (fs * 0.52)), 4)
            lines.append(wrap_fit(cell, units))
        per_row.append(lines)
    total = sum(max(len(c) for c in r) * lh + 2 * pad for r in per_row)
    return per_row, total


def draw_table(s, name, headers, rows, weights, y0, y_max,
               header_rows=None, fs_max=20, fs_min=10, zebra=True):
    """畫表格並自動選字級：從 fs_max 往下試到塞得進 (y0, y_max) 為止。

    headers/rows 的每一列都是字串清單；`header_rows` 可再多一列跨欄的上層表頭
    （list of (label, span, fill, color)），給中文版的「建議等級 A-D」帶用。
    回傳表格底緣 y。
    """
    x0, x1 = MARGIN_L + 5, MARGIN_R - 5
    tw = x1 - x0
    tot = sum(weights)
    widths = [tw * w / tot for w in weights]
    budget = y_max - y0

    if header_rows and sum(span for _l, span, _f, _c in header_rows) != len(headers):
        raise SystemExit(f"{name}：header_rows 的 span 總和須等於欄數 {len(headers)}")

    for fs in range(fs_max, fs_min - 1, -1):
        lh = fs + 3
        pad = max(round(fs * 0.42), 4)
        band_h = (fs + 12) if header_rows else 0
        per_row, total = _measure([headers] + rows, widths, fs, lh, pad)
        if total + band_h <= budget:
            break
    else:
        sys.stderr.write(f"WARN {name}：表格在最小字級 {fs_min} 仍塞不下（需 {total + band_h:.0f} > {budget}）\n")

    y = y0
    if header_rows:
        cx, col = x0, 0
        for label, span, fill, color in header_rows:
            cw = sum(widths[col:col + span])
            s.append(f'<rect x="{cx:.0f}" y="{y:.0f}" width="{cw:.0f}" height="{band_h}" '
                     f'fill="{fill}" stroke="{LINE}" stroke-width="1"/>')
            if label:
                s.append(txt(cx + cw / 2, y + band_h - 8, label, fs, color, "700", "middle", ls="0.3"))
            cx += cw
            col += span
        y += band_h

    def draw_row(cells_lines, fill, color, weight):
        nonlocal y
        rh = max(len(c) for c in cells_lines) * lh + 2 * pad
        cx = x0
        for i, lines in enumerate(cells_lines):
            s.append(f'<rect x="{cx:.0f}" y="{y:.0f}" width="{widths[i]:.0f}" height="{rh:.0f}" '
                     f'fill="{fill}" stroke="{LINE}" stroke-width="1"/>')
            ty = y + pad + lh - round(fs * 0.28)
            for ln in lines:
                s.append(txt(cx + pad, ty, ln, fs, color, weight, ls="0.2"))
                ty += lh
            cx += widths[i]
        y += rh

    draw_row(per_row[0], HEAD_BG, "#FFFFFF", "700")
    for n, cells in enumerate(per_row[1:]):
        fill = "#FFFFFF" if (not zebra or n % 2 == 0) else PANEL
        draw_row(cells, fill, INK, "400")
    check_overflow(name, y, y_max)  # 用算預算的同一條線，不是 BODY_BOTTOM
    return y, fs


def footnotes(s, name, lines, y, fs=13):
    """表格下方的 * / ** 註腳（灰階小字，逐行斷行）。"""
    for ln in lines:
        for seg in wrap_fit(ln, int((MARGIN_R - MARGIN_L) / (fs * 0.52))):
            y += fs + 5
            s.append(txt(MARGIN_L, y, seg, fs, MUTED, "400", ls="0.2"))
    check_overflow(name, y)
    return y


# ── 圖 1：6S 證據金字塔 ────────────────────────────────────────────────────

PYRAMID_6S = [
    ("Systems", "電子病歷整合的臨床決策支援系統", "例：與醫囑系統連動的提示"),
    ("Summaries", "主題式證據摘要／實證臨床指引", "例：UpToDate、DynaMed、指引"),
    ("Synopses of Syntheses", "系統性回顧的結構式摘要", "例：ACP Journal Club 摘要"),
    ("Syntheses", "系統性回顧／統合分析", "例：Cochrane Reviews"),
    ("Synopses of Studies", "單篇原始研究的結構式摘要", "例：實證期刊的評述摘要"),
    ("Studies", "單篇原始研究（未經二次消化）", "例：PubMed 檢索到的 RCT"),
]
# 由上（最消化）到下（最原始）：深→淺
BAND_FILL = ["#3D434B", "#545B64", "#6B7280", "#868D96", "#A6ACB4", "#C9CED4"]
BAND_TEXT = ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", INK, INK]


def fig_pyramid(outdir):
    name = "evidence-pyramid-6s"
    s = frame("6S 證據金字塔")
    apex_x, apex_y = 430, 180
    base_y, half = 636, 235
    top_hw = 52  # 頂端切平：真正的尖頂放不下「Systems」七個字母，字會溢出三角形外
    n = len(PYRAMID_6S)
    bh = (base_y - apex_y) / n

    def hw(y):  # 該高度的半寬
        return top_hw + (y - apex_y) / (base_y - apex_y) * (half - top_hw)

    for i, (en, _zh, _eg) in enumerate(PYRAMID_6S):
        yt, yb = apex_y + i * bh, apex_y + (i + 1) * bh
        wt, wb = hw(yt), hw(yb)
        d = (f"M {apex_x - wt:.1f} {yt:.1f} L {apex_x + wt:.1f} {yt:.1f} "
             f"L {apex_x + wb:.1f} {yb:.1f} L {apex_x - wb:.1f} {yb:.1f} Z")
        s.append(f'<path d="{d}" fill="{BAND_FILL[i]}" stroke="#FFFFFF" stroke-width="1.5"/>')
        s.append(txt(apex_x, yt + bh / 2 + 7, en, 20, BAND_TEXT[i], "700", "middle", ls="0.4"))

    # 第 5/6 層之間的分界：以上是已消化過的二次資源，以下是原始研究
    # 標籤放在金字塔左側的空白帶（該高度的塔身左緣約在 x=206 之後，不會壓到塔）
    dy = apex_y + 5 * bh
    s.append(f'<line x1="30" y1="{dy:.0f}" x2="{apex_x + half + 25:.0f}" y2="{dy:.0f}" '
             f'stroke="{HEAD_BG}" stroke-width="2" stroke-dasharray="9 7"/>')
    s.append(txt(30, dy - 34, "↑ secondary", 15, MUTED, "700", ls="0.2"))
    s.append(txt(30, dy - 14, "已評讀／已消化資源", 15, MUTED, "400", ls="0.2"))
    s.append(txt(30, dy + 28, "↓ primary", 15, MUTED, "700", ls="0.2"))
    s.append(txt(30, dy + 48, "原始研究", 15, MUTED, "400", ls="0.2"))

    # 右側圖例：色塊＋英文層名＋中文說明＋例子
    lx = 700
    ly = 205
    step = (BODY_BOTTOM - 50 - ly) / (n - 1)  # 末項還要放「例：」那行（+46），扣掉才不會壓到 caption 帶
    for i, (en, zh, eg) in enumerate(PYRAMID_6S):
        cy = ly + i * step
        s.append(f'<rect x="{lx}" y="{cy - 13:.0f}" width="15" height="15" '
                 f'fill="{BAND_FILL[i]}" stroke="{LINE}" stroke-width="1"/>')
        s.append(txt(lx + 26, cy, en, 19, INK, "700", ls="0.3"))
        s.append(txt(lx + 26, cy + 24, zh, 17, INK_SOFT, "400", ls="0.2"))
        s.append(txt(lx + 26, cy + 46, eg, 15, MUTED, "400", ls="0.2"))
    check_overflow(name, ly + (n - 1) * step + 46)
    s.append(txt(30, 190, "檢索順序：由上往下", 16, MUTED, "700", ls="0.2"))
    source_note(s, name, "依 Haynes 6S 證據資源模型（DiCenso A, Bayley L, Haynes RB. Evid Based Nurs 2009）內容自繪")
    return save(outdir, name, s)


# ── 圖 2／3：OCEBM 2011 證據等級表 ─────────────────────────────────────────

OCEBM_EN_HEADERS = ["Question", "Step 1 (Level 1*)", "Step 2 (Level 2*)",
                    "Step 3 (Level 3*)", "Step 4 (Level 4*)", "Step 5 (Level 5)"]
OCEBM_EN_ROWS = [
    ["How common is the problem?",
     "Local and current random sample surveys (or censuses)",
     "SR of surveys that allow matching to local circumstances**",
     "Local non-random sample**",
     "Case-series**",
     "n/a"],
    ["Is this diagnostic or monitoring test accurate? (Diagnosis)",
     "SR of cross sectional studies with consistently applied reference standard and blinding",
     "Individual cross sectional studies with consistently applied reference standard and blinding",
     "Non-consecutive studies, or studies without consistently applied reference standards**",
     "Case-control studies, or poor or non-independent reference standard**",
     "Mechanism-based reasoning"],
    ["What will happen if we do not add a therapy? (Prognosis)",
     "SR of inception cohort studies",
     "Inception cohort studies",
     "Cohort study or control arm of randomized trial*",
     "Case-series or case-control studies, or poor quality prognostic cohort study**",
     "n/a"],
    ["Does this intervention help? (Treatment Benefits)",
     "SR of randomized trials or n-of-1 trials",
     "Randomized trial or observational study with dramatic effect",
     "Non-randomized controlled cohort/follow-up study**",
     "Case-series, case-control studies, or historically controlled studies**",
     "Mechanism-based reasoning"],
    ["What are the COMMON harms? (Treatment Harms)",
     "SR of randomized trials, SR of nested case-control studies, n-of-1 trial with the patient you are raising the question about, or observational study with dramatic effect",
     "Individual randomized trial or (exceptionally) observational study with dramatic effect",
     "Non-randomized controlled cohort/follow-up study (post-marketing surveillance) provided there are sufficient numbers to rule out a common harm (for long-term harms the duration of follow-up must be sufficient)**",
     "Case-series, case-control, or historically controlled studies**",
     "Mechanism-based reasoning"],
    ["What are the RARE harms? (Treatment Harms)",
     "SR of randomized trials or n-of-1 trial",
     "Randomized trial or (exceptionally) observational study with dramatic effect",
     "",
     "",
     ""],
    ["Is this (early detection) test worthwhile? (Screening)",
     "SR of randomized trials",
     "Randomized trial",
     "Non-randomized controlled cohort/follow-up study**",
     "Case-series, case-control, or historically controlled studies**",
     "Mechanism-based reasoning"],
]
OCEBM_WEIGHTS = [1.25, 1.08, 1.05, 1.18, 1.05, 0.62]
OCEBM_SOURCE = "依 Oxford CEBM《The Oxford 2011 Levels of Evidence》公開內容自繪"


def fig_ocebm_en(outdir):
    name = "ocebm-2011-levels-en"
    s = frame("OCEBM 2011 Levels of Evidence")
    y, _fs = draw_table(s, name, OCEBM_EN_HEADERS, OCEBM_EN_ROWS, OCEBM_WEIGHTS,
                        BODY_TOP, BODY_BOTTOM - 46, fs_max=14)
    footnotes(s, name, [
        "* Level may be graded down on study quality, imprecision, indirectness (study PICO does not match "
        "question PICO), inconsistency between studies, or very small absolute effect size; "
        "graded up on a large or very large effect size.",
        "** A systematic review (SR) is generally better than an individual study.",
    ], y)
    source_note(s, name, OCEBM_SOURCE)
    return save(outdir, name, s)


OCEBM_ZH_HEADERS = ["臨床問題", "證據等級 1*", "證據等級 2*", "證據等級 3*", "證據等級 4*", "證據等級 5*"]
OCEBM_ZH_ROWS = [
    ["此臨床問題多常見？",
     "區域及當代隨機樣本的（人口）普查",
     "切合當地環境普查的系統性回顧**",
     "區域性非隨機樣本調查**",
     "系列病例報告**",
     "n/a"],
    ["診斷或監測工具正確嗎？（診斷）",
     "使用一致的參考（黃金）標準及盲化的斷代研究的系統性回顧",
     "使用一致的參考（黃金）標準及盲化的斷代研究",
     "非連續性研究，或沒有使用一致的參考（黃金）標準的研究**",
     "病例對照試驗，低品質或無獨立參考標準的研究**",
     "基於基本原理的推斷"],
    ["如果不治療會有什麼後果？（預後）",
     "初期（inception）世代研究的系統性回顧",
     "初期（inception）世代研究",
     "世代研究，或隨機對照研究的控制組**",
     "系列病例報告，病例對照試驗，或低品質的預後型世代研究**",
     "n/a"],
    ["這個介入治療有幫助嗎？（治療益處）",
     "隨機對照試驗（RCT）或隨機序列治療試驗（n-of-1）的系統性回顧",
     "隨機對照試驗，或有顯著療效的觀察型研究",
     "非隨機控制的世代／追蹤研究**",
     "系列病例報告，病例對照試驗，或歷史對照試驗**",
     "基於基本原理的推斷"],
    ["介入治療的常見害處？（治療傷害）",
     "隨機對照試驗（RCT）、巢式病例對照試驗、隨機序列治療試驗（n-of-1）或有顯著療效的觀察型研究的系統性回顧",
     "隨機對照試驗，或有顯著傷害的異常觀察型研究",
     "非隨機控制的世代／追蹤研究（上市後監測），提供足夠樣本數排除常見危害（長期危害需有足夠追蹤時間）**",
     "系列病例報告，病例對照試驗，或歷史對照試驗**",
     "基於基本原理的推斷"],
    ["介入治療的罕見害處？（治療傷害）",
     "隨機對照試驗（RCT）或隨機序列治療試驗（n-of-1）的系統性回顧",
     "隨機對照試驗，或有顯著傷害的異常觀察型研究",
     "",
     "",
     ""],
    ["值得早期診斷嗎？（篩檢）",
     "隨機對照試驗（RCT）的系統性回顧",
     "隨機對照試驗",
     "非隨機控制的世代／追蹤研究**",
     "系列病例報告，病例對照試驗，或歷史對照試驗**",
     "基於基本原理的推斷"],
]
# 建議等級帶：A=Level 1、B=Level 2-3、C=Level 4、D=Level 5（中文教學版慣例，非原表欄位）
OCEBM_ZH_BAND = [
    ("", 1, "#F7F8FA", INK),
    ("建議等級 A", 1, "#545B64", "#FFFFFF"),
    ("建議等級 B", 2, "#6B7280", "#FFFFFF"),
    ("建議等級 C", 1, "#868D96", "#FFFFFF"),
    ("建議等級 D", 1, "#A6ACB4", INK),
]


def fig_ocebm_zh(outdir):
    name = "ocebm-2011-levels-zh"
    s = frame("牛津實證醫學中心 2011 證據等級表")
    y, _fs = draw_table(s, name, OCEBM_ZH_HEADERS, OCEBM_ZH_ROWS, OCEBM_WEIGHTS,
                        BODY_TOP, BODY_BOTTOM - 68, header_rows=OCEBM_ZH_BAND, fs_max=14)
    footnotes(s, name, [
        "* 可因研究品質不佳、不精確、間接性（研究 PICO 與問題 PICO 不符）、研究間不一致或絕對效應量極小而降級；效應量大則可升級。",
        "** 系統性回顧通常優於單一研究。",
        "建議等級 A-D 為中文教學版對應等級 1-5 的慣例標示，非 OCEBM 2011 原表欄位。",
    ], y)
    source_note(s, name, OCEBM_SOURCE + "；中文為本 kit 自行翻譯")
    return save(outdir, name, s)


# ── 圖 4：評讀工具對照表 ───────────────────────────────────────────────────

TOOLS_ROWS = [
    ["Cochrane risk of bias tool（RoB 1.0）", "RCT"],
    ["CASP（Critical Appraisal Skills Programme）\nhttps://casp-uk.net/casp-tools-checklists/",
     "SR, RCT, Cohort, Case Control, Diagnostics, Economics, Qualitative Researches"],
    ["CAT（Critical Appraisal Tools）from Oxford CEBM", "SR, RCTs, Diagnostics, Prognostic"],
    ["Newcastle-Ottawa Scale（NOS）", "Non-RCT"],
    ["A Measurement Tool to Assess Systematic Reviews（AMSTAR）", "SR"],
    ["Appraisal of Guidelines for Research and Evaluation（AGREE）",
     "Guideline development and the quality of reporting"],
]


def fig_tools(outdir):
    name = "appraisal-tool-selection"
    s = frame("評讀工具對照表")
    rows = [[c.replace("\n", " ") for c in r] for r in TOOLS_ROWS]
    y, _fs = draw_table(s, name, ["評讀工具", "適用的研究設計"], rows, [1.35, 1.0],
                        BODY_TOP, BODY_BOTTOM - 40, fs_max=21)
    footnotes(s, name, [
        "選工具的順序：先分型（治療／診斷／預後／SR）再挑對應清單；同一篇只用一套工具，逐題留下 Yes／No／Can't tell。",
    ], y)
    source_note(s, name, "依 Cochrane RoB、CASP、Oxford CEBM CAT、Newcastle-Ottawa Scale、AMSTAR、AGREE 各自公開說明整理自繪")
    return save(outdir, name, s)


# ── 圖 5：評讀流程五步驟 ───────────────────────────────────────────────────

WORKFLOW_STEPS = [
    ("挑選適當文獻", "依 PICO 與研究設計挑最貼近的一篇"),
    ("挑選評讀工具", "按研究型別選對應清單（例：CASP）"),
    ("嚴格評讀", "逐題作答，Can't tell 誠實勾"),
    ("評定證據等級", "對照 OCEBM 2011 標出落點"),
    ("評定推薦等級，給予建議", "回到病人，給可執行的臨床建議"),
]


def _elbow_arrow(x1, y1, x2, y2):
    """直角箭頭：從 (x1,y1) 先橫走到 x2，再直走到 y2。

    箭頭用 path 畫成實心三角（不用 `marker`——marker 在多數 SVG→pptx 轉換器會被丟掉，
    線就變成沒有頭的折線）。"""
    head_w, head_h = 9, 14
    sign = 1 if y2 < y1 else -1  # 往上畫時三角底邊在下
    body = (f'<path d="M {x1:.0f} {y1:.0f} L {x2:.0f} {y1:.0f} L {x2:.0f} {y2 + sign * head_h:.0f}" '
            f'fill="none" stroke="{HEAD_BG}" stroke-width="3.5"/>')
    tri = (f'<path d="M {x2:.0f} {y2:.0f} L {x2 - head_w:.0f} {y2 + sign * head_h:.0f} '
           f'L {x2 + head_w:.0f} {y2 + sign * head_h:.0f} Z" fill="{HEAD_BG}"/>')
    return body + "\n" + tri


def fig_workflow(outdir):
    name = "appraisal-workflow"
    s = frame("評讀流程五步驟")
    n = len(WORKFLOW_STEPS)
    bw, bh = 196, 96
    gap = (MARGIN_R - MARGIN_L - n * bw) / (n - 1)
    top_y, bot_y = 226, 442  # 上排提示小字畫在方塊上方，top_y 要留 2 行（約 46px）給它，才不會頂到標題橫線
    boxes = []
    for i, (label, hint) in enumerate(WORKFLOW_STEPS):
        x = MARGIN_L + i * (bw + gap)
        y = top_y if i % 2 == 0 else bot_y
        boxes.append((x, y))
        s.append(f'<rect x="{x:.0f}" y="{y}" width="{bw}" height="{bh}" fill="#FFFFFF" '
                 f'stroke="{HEAD_BG}" stroke-width="2.5"/>')
        lines = wrap(label, 16)
        ty = y + bh / 2 - (len(lines) - 1) * 15 + 8
        for ln in lines:
            s.append(txt(x + bw / 2, ty, ln, 23, INK, "700", "middle", ls="0.3"))
            ty += 30
        # 步驟編號圓（壓在方塊左上角）
        s.append(f'<circle cx="{x:.0f}" cy="{y}" r="19" fill="{HEAD_BG}"/>')
        s.append(txt(x, y + 8, str(i + 1), 21, "#FFFFFF", "700", "middle", ls="0"))
        # 提示小字：上排畫在方塊「上方」、下排畫在「下方」——中間帶要留給折線箭頭走
        hint_lines = wrap(hint, 20)
        hy = (y - 26 - (len(hint_lines) - 1) * 20) if i % 2 == 0 else (y + bh + 26)
        for hl in hint_lines:
            s.append(txt(x + bw / 2, hy, hl, 15, MUTED, "400", "middle", ls="0.2"))
            hy += 20

    for i in range(n - 1):
        x0, y0 = boxes[i]
        x1, y1 = boxes[i + 1]
        # 從本方塊右緣的垂直中線出發，橫走到下一方塊的中心 x，再直走進它的上／下緣
        s.append(_elbow_arrow(x0 + bw, y0 + bh / 2, x1 + bw / 2,
                              y1 + (bh if y1 < y0 else 0)))

    y = bot_y + bh + 26 + 40
    footnotes(s, name, [
        "第 2 步的工具、第 4 步的等級表都是固定素材：工具見「評讀工具對照表」，等級見「OCEBM 2011 證據等級表」。",
        "第 5 步不是覆述結論，而是把等級換算成對這位病人可執行的建議（含做不到時的替代方案）。",
    ], y)
    source_note(s, name, "依實證醫學嚴格評讀通用教學流程內容自繪")
    return save(outdir, name, s)


# ── 圖 6：VIP 框架 ─────────────────────────────────────────────────────────

# how 欄刻意寫成「已斷好的行」：這幾句的斷點要落在頓號上，交給自動斷行會把「盲化」「可近性」腰斬
VIP = [
    ("V", "alidity", "(Reliability)", "效度／信度", "我們可以相信這個證據嗎？",
     ["看設計與執行：隨機、盲化、", "追蹤完整度、混雜是否控制好"]),
    ("I", "mportance", "(Impact)", "重要性", "相信了，但這個結果重要嗎？",
     ["看效應量與精確度：ARR／NNT、", "95% CI 寬窄，不只看 p 值"]),
    ("P", "ractice", "(Applicability)", "臨床適用性", "結果能用在我的病人身上嗎？",
     ["看族群、劑量、照護環境、", "可近性是否對得上"]),
]


def fig_vip(outdir):
    name = "appraisal-vip"
    s = frame("嚴格評讀 VIP 框架")
    r = 96
    cy = 288
    fills = ["#3D434B", "#6B7280", "#A6ACB4"]
    texts = ["#FFFFFF", "#FFFFFF", INK]
    for i, (initial, rest, alt, zh, q, how) in enumerate(VIP):
        cx = 300 + i * 340
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fills[i]}"/>')
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE}" stroke-width="1.5"/>')
        s.append(txt(cx, cy - 4, initial + rest, 23, texts[i], "700", "middle", ls="0.4"))
        s.append(f'<line x1="{cx - 58}" y1="{cy + 8}" x2="{cx + 58}" y2="{cy + 8}" '
                 f'stroke="{texts[i]}" stroke-width="1.2" opacity="0.7"/>')
        s.append(txt(cx, cy + 32, alt, 19, texts[i], "400", "middle", ls="0.3"))
        s.append(txt(cx, cy + r + 46, zh, 26, INK, "700", "middle", ls="0.5"))
        qy = cy + r + 84
        for ln in wrap(q, 28):
            s.append(txt(cx, qy, ln, 20, INK_SOFT, "400", "middle", ls="0.2"))
            qy += 28
        hy = qy + 12
        for ln in how:
            s.append(txt(cx, hy, ln, 15, MUTED, "400", "middle", ls="0.2"))
            hy += 21
    s.append(f'<line x1="{MARGIN_L}" y1="{BODY_BOTTOM - 44}" x2="{MARGIN_R}" y2="{BODY_BOTTOM - 44}" '
             f'stroke="{RULE}" stroke-width="1.5"/>')
    s.append(txt(W / 2, BODY_BOTTOM - 14, "三關依序過：V 不過就不必談 I，I 不過就不必談 P",
                 19, MUTED, "700", "middle", ls="0.3"))
    check_overflow(name, BODY_BOTTOM - 14)
    source_note(s, name, "依實證醫學 VIP（Validity／Importance／Practice）評讀框架通用教學內容自繪")
    return save(outdir, name, s)


FIGURES = [fig_pyramid, fig_ocebm_en, fig_ocebm_zh, fig_tools, fig_workflow, fig_vip]


def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    paths = [fn(outdir) for fn in FIGURES]
    for p in paths:
        print(f"generated {p}")
    print(f"generated {len(paths)} teaching figures -> {outdir}")
    return paths


def main(argv):
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_out = os.path.join(repo, "data", "assets")
    if "--list" in argv:
        for fn in FIGURES:
            print(fn.__name__)
        return 0
    outdir = argv[1] if len(argv) > 1 else default_out
    build(outdir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
