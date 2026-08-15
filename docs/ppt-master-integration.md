# ppt-master 整合說明（簡報匯出引擎）

> 本 kit 的簡報主路線是「程式生成 SVG → 匯出 native 可編輯 pptx」。
> 後半段的匯出由 [ppt-master](https://github.com/hugohe3/ppt-master)（MIT）負責，它是**唯一必裝的外部依賴**。
> 內建的 `scripts/generate_pptx.py` 只是 fallback：用 `Presentation()` 從零硬編碼、無法載入既有範本，版面陽春。

## 1. 它裝在哪、怎麼跑

- **位置**：獨立工具，預設在 `~/ppt-master`（**不放進本 repo**，它的資產庫約 1.2GB）。
  裝在別處就設環境變數 `PPT_MASTER_DIR`；本文件所有指令一律先取值：

  ```bash
  PPT_MASTER="${PPT_MASTER_DIR:-$HOME/ppt-master}"
  PY="$PPT_MASTER/.venv/bin/python"
  ```

- **安裝**：`bash bootstrap.sh` 會自動 clone 並建好 venv。手動安裝見 README「手動安裝」段。
- **依賴**：它有自己的 venv（`$PPT_MASTER/.venv`），內含 python-pptx / skia-pathops / uharfbuzz / PyMuPDF / Pillow。
- **它是「skill」不是 GUI 程式**：主路線用到的兩支腳本（`svg_quality_checker.py`、`svg_to_pptx.py`）可直接命令列呼叫、
  能全自動跑完；但它另外那條「AI 手寫 SVG」的 Generate 路線需要掛在 AI agent 底下、含互動確認關卡（見 §3B）。

## 2. 資料流（本 kit ↔ ppt-master）

本 kit 負責**內容**與**版面 SVG**，ppt-master 負責**把 SVG 變成 native 可編輯 pptx**：

```
本 kit: 6A 各步產出 → 06_slides/content.json（內容）
                              │
                              ▼
        scripts/gen_journal_svg.py → 06_slides/svg_output/*.svg（版面）
                              │
                              ▼
ppt-master: svg_quality_checker.py（品質關卡）→ svg_to_pptx.py（匯出）
                              │
                              ▼
                  06_slides/ebm-report.pptx（native 可編輯）
```

完整的五步指令見 `skills/ebm-slides.md` §3——那裡是可直接複製執行的權威版本，本文件不重複。

⚠️ `content.json` 是**現行主路線格式**。舊的 `slides.json`（由 `scripts/build_slide_outline.py` 產生）
只餵給 fallback 的 `scripts/generate_pptx.py`，不要拿它走主路線。

## 3. 套用自己的 .pptx 範本（備選路線）

主路線產出的 White Grey 版面若不合用，ppt-master 另有兩條範本路線：

### A. Fill Native PPTX — 有自己的 .pptx 範本

把你的範本當「投影片庫」，複製版面、把內容填進 slot（純 OOXML，不走 SVG，保真度最高）：

```bash
PPT_MASTER="${PPT_MASTER_DIR:-$HOME/ppt-master}"
PY="$PPT_MASTER/.venv/bin/python"
cd "$PPT_MASTER"
# 1) 分析範本每頁的可填 slot
$PY skills/ppt-master/scripts/template_fill_pptx.py analyze <你的範本.pptx> -o analysis/lib.json
# 2) 產生填充計畫骨架 → 由 AI 依 content.json 內容規劃哪段填哪頁
$PY skills/ppt-master/scripts/template_fill_pptx.py scaffold ...
# 3) 套用 → 產出 pptx
$PY skills/ppt-master/scripts/template_fill_pptx.py apply ...
```

更省事的做法：在 `$PPT_MASTER` 目錄開一個 AI CLI session，說「用 `<範本>.pptx` 產這份 EBM 簡報，內容在這」，
貼上 `06_slides/content.json`，讓它讀 `skills/ppt-master/SKILL.md` 走 Fill Native PPTX route。

⚠️ 契合度取決於你的範本結構：EBM 報告的頁型（逐題評讀＋佐證截圖＋多欄表格）不一定對得上一般簡報範本的 slot，
硬套可能出現版面不搭。建議先拿幾頁試跑再決定要不要整份走這條。

### B. Generate PPTX — 沒有範本，讓 AI 設計

在 `$PPT_MASTER` 開 agent session，餵內容 + 想要的風格，讀 `SKILL.md` 走 Generate route（AI 一張張手寫 SVG → native pptx）。
設計由 AI 即興決定、每次結果不同，穩定度不如主路線的程式生成，通常只在想要全新視覺時才用。

## 4. Fallback 關係

`gen_journal_svg + ppt-master（主路線）` → `Canva MCP` → `scripts/generate_pptx.py`（陽春 python-pptx） → `Markdown`。

`generate_pptx.py` 只保留為 ppt-master 不可用時的救急選項，因此不為它另加「載入範本」功能——那與 ppt-master 的
template-fill 重複。想套範本請走 §3A。

## 5. 更新 ppt-master

```bash
PPT_MASTER="${PPT_MASTER_DIR:-$HOME/ppt-master}"
cd "$PPT_MASTER" && git pull                      # shallow clone 也能 fetch 最新
"$PPT_MASTER/.venv/bin/pip" install -r requirements.txt   # 補新依賴
```

不打算更新的話，`$PPT_MASTER/.git` 可刪省磁碟空間，但刪後要更新只能重新 clone。
