# ppt-master 整合說明（簡報產生主路線）

> 目的：解決「EBM 產出的 PowerPoint 跟我的模板差很遠」。
> 內建的 `scripts/generate_pptx.py` 是 `Presentation()` 從零硬編碼、無法載入既有範本，這是落差的技術根源。
> [ppt-master](https://github.com/hugohe3/ppt-master)（MIT）能**載入你的 .pptx 範本當母片、產出 native 可編輯 pptx**，故設為簡報產生的**主路線**。

## 1. 它裝在哪、怎麼跑

- **位置**：獨立工具，裝在 `~/ppt-master`（**不在本 repo 內**，避免把 1.3G 資產庫塞進對外 GitHub）。
- **依賴**：獨立 venv `~/ppt-master/.venv`（python 3.12，已裝 python-pptx / skia-pathops / uharfbuzz / PyMuPDF / Pillow 等完整依賴）。
- 🔴 **認知：ppt-master 不是雙擊就開的 GUI 軟體，是一個「skill」** —— 要掛在某個 AI agent（Claude Code / Cursor / GPT）底下、由 AI 讀它的指令執行（Generate 路線是 AI 一張張手寫 SVG）。它有**互動確認關卡**，不能全自動無人跑。「獨立於 Claude」只在「也能被別的 AI agent 用」這意義上成立。

## 2. 資料流（EBM ↔ ppt-master）

EBM 負責**內容**（5A / PICO / 評讀 → `PROJECT_DIR/06_slides/slides.json`），ppt-master 負責**把內容變漂亮 pptx**：

```
EBM: build_slide_outline.py → 06_slides/slides.json（內容）
                                   │
                                   ▼
ppt-master（在 ~/ppt-master 跑）：讀內容 + 你的 .pptx 範本 → native pptx
                                   │
                                   ▼
產出的 .pptx 放回 EBM: PROJECT_DIR/06_slides/ebm-report.pptx
```

## 3. 兩條路線（依你有沒有 .pptx 範本二選一）

### A. 有設計範本（推薦，最貼合你的設計）— Fill Native PPTX 路線
把你的 .pptx 範本當「投影片庫」，複製版面、直接把 EBM 內容填進 slot（純 OOXML，不走 SVG，最保真）：

```bash
cd ~/ppt-master
PY=~/ppt-master/.venv/bin/python
# 1) 分析範本每頁的可填 slot
$PY skills/ppt-master/scripts/template_fill_pptx.py analyze <你的範本.pptx> -o analysis/lib.json
# 2) 產生填充計畫骨架 → 由 AI 依 EBM slides.json 內容規劃哪段填哪頁
$PY skills/ppt-master/scripts/template_fill_pptx.py scaffold ...
# 3) 套用 → 產出 pptx
$PY skills/ppt-master/scripts/template_fill_pptx.py apply ...
```
更簡單：在 `~/ppt-master` 開一個 Claude Code session，說「用 `<範本>.pptx` 產這份 EBM 簡報，內容在這」，貼上 EBM `slides.json` / markdown，讓 AI 讀 `skills/ppt-master/SKILL.md` 走 Fill Native PPTX route。

### B. 沒有範本 — Generate PPTX 路線（AI 設計）
在 `~/ppt-master` 開 agent session，餵 EBM 內容 + 選定風格，讀 `SKILL.md` 走 Generate route（AI 手寫 SVG → native pptx）。設計由 AI 決定，不一定完全合你意，所以**有範本時優先走 A**。

## 4. Fallback 關係

`ppt-master（主路線）` → `Canva MCP` → `scripts/generate_pptx.py`（陽春 python-pptx） → `Markdown`。
`generate_pptx.py` 保留為 ppt-master 不可用時的 fallback，不再是主要產出方式，故不為它另加載入範本功能（與 ppt-master template-fill 重複）。

## 5. 更新 ppt-master

`cd ~/ppt-master && git pull`（shallow clone，會 fetch 最新）。之後 `~/ppt-master/.venv/bin/pip install -r requirements.txt` 補新依賴。
不更新的話 `~/ppt-master/.git`（約 611M）可刪省空間，但刪後要更新只能重新 clone。
