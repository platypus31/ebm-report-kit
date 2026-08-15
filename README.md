# EBM Report Kit

臺灣醫院 **EBM（實證醫學）報告產生器**——給 AI CLI（Claude Code / Codex / Gemini CLI）使用的 skill 工具箱。
丟一篇論文，自動反推出完整的 6A 報告簡報初稿（**native 可編輯 .pptx**），你只需要修改，不需要從零做。

> 本工具與姊妹作 [journal-reading-kit](https://github.com/platypus31/journal-reading-kit)（Journal Reading 三格式產生器）**各自獨立、互不依賴**，可單獨安裝使用。

## 兩種用法

| 指令 | 情境 | 流程 |
|---|---|---|
| **`/ebm-from-paper <PDF/DOI/PMID>`** | **文獻已選好**（最常見） | 反推 PICO/臨床情境 → 重建檢索過程（真跑 PubMed/Cochrane 拿真實數字）→ CASP 逐題預答＋原文佐證裁圖 → 組簡報 → 交付初稿＋「待人工」清單 |
| `/ebm` | 從臨床問題出發 | 互動式走完整 6A（Analysis→Ask→Acquire→Appraise→Apply→Audit），每步落結構化檔案 |

## 產出特色

- **6A 完整結構**：臨床情境敘事卡 → 背景衛教 → PICO 表 → 檢索過程（含 PRISMA）→ CASP 逐題評讀（每題附原文截圖＋紅框）→ OCEBM 等級 → SDM → 白話臨床回覆 → 自我評估
- **可編輯**：表格、文字卡、紅框都是 PowerPoint 原生物件，匯出後可直接改字、拉框
- **誠實原則**：檢索數字全部真跑可重現；評讀不確定的題留給人確認；查不到的數字明標不編造
- 內容結構規格見 `data/report-spec.md`；名詞與公式權威見 `data/glossary.md`

## 快速開始

```bash
git clone https://github.com/platypus31/ebm-report-kit.git
cd ebm-report-kit
bash bootstrap.sh          # 一鍵裝依賴 + 自我驗證（冪等，可重複執行）
```

裝完後在同一個目錄啟動 AI CLI：

```bash
claude
> /ebm-from-paper 33693636
```

`bootstrap.sh` 會依序檢查與安裝：基本工具（git／python3 3.9+／Node.js）→ kit 專用 venv（`.venv/`，裝
pymupdf、python-pptx、pyyaml、pytest）→ Node 依賴（`npm install` ＋ `npx playwright install chromium`）
→ ppt-master 匯出引擎（自動 `git clone --depth 1`，約 1.2GB）→ self-check（跑單元測試＋用範例專案實跑簡報引擎）。

只想檢查現況、不要它動手安裝：

```bash
bash bootstrap.sh --check-only
```

完整範例專案見 `projects/example-pcv13-covid19/`（PMID 33693636 的全流程實跑產出）。

### 手動安裝

不想用 bootstrap 的話，以下是它做的事：

- **AI CLI**：[Claude Code](https://docs.anthropic.com/en/docs/claude-code)，或其他相容 CLI
  （repo 內含 `AGENTS.md`／`GEMINI.md`／`.cursorrules`／`.github/copilot-instructions.md`，與 `CLAUDE.md` 同內容）
- **Python 3.9+ 依賴**（建議裝在 repo 內的 venv）：

  ```bash
  python3 -m venv .venv
  .venv/bin/pip install pymupdf python-pptx pyyaml pytest
  ```

- **Node.js**（檢索截圖 `pubmed_shot.js`／`cochrane_search.js` 與圖卡 `html2png.js` 用，**非選配**）：

  ```bash
  npm install
  npx playwright install chromium
  ```

- **[ppt-master](https://github.com/hugohe3/ppt-master)**（SVG → native 可編輯 pptx 的匯出引擎）：

  ```bash
  git clone --depth 1 https://github.com/hugohe3/ppt-master.git ~/ppt-master
  cd ~/ppt-master && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
  ```

  ⚠️ 資產庫約 1.2GB，建議照上面加 `--depth 1` 只抓最新一版。裝在 `~/ppt-master` 以外的位置時，
  設環境變數 `PPT_MASTER_DIR` 指過去即可——本 repo 文件裡的指令一律以
  `PPT_MASTER="${PPT_MASTER_DIR:-$HOME/ppt-master}"` 取值：

  ```bash
  export PPT_MASTER_DIR=/your/path/to/ppt-master
  ```

- **固定素材（選配）**：6S 金字塔、OCEBM 2011 等級表等圖片因版權不隨 repo 附帶。
  需要時自行放進 `data/assets/`（`mkdir -p data/assets`），或用 `table`／`textcard` 頁型重製成可編輯頁面。
  缺圖不會中斷流程，簡報引擎會畫佔位框。

## 自訂風格與模板

常見問題：「可以換成我們科的版型嗎？」三條路，由簡到繁：

1. **直接在 PowerPoint 改（推薦）**——產出是 native 可編輯 pptx，文字、表格、紅框都是原生物件。
   套用自家佈景主題、改字型配色、換 logo 都在 PowerPoint 裡做，不必碰程式碼。
2. **用 ppt-master 的 Fill Native PPTX 硬套自有範本**（備選）——把你的 .pptx 當母片填內容，
   接法見 `docs/ppt-master-integration.md`。版面契合度取決於範本結構，請自行評估效果。
3. **改簡報引擎本身**——「White Grey」版面（白底＋灰流線裝飾＋serif 大寫標題）全部寫在
   `scripts/gen_journal_svg.py`（MIT，歡迎改）。注意它**沒有參數化的模板系統**，換風格＝直接改該檔的繪圖函式。
   `data/templates/style-*` 只供 fallback 的 `scripts/generate_pptx.py` 使用，不影響主路線。

## 結構

```
bootstrap.sh     # 一鍵安裝 + self-check
skills/          # AI CLI 指令（/ebm-from-paper、/ebm、/pico、/appraise、/ebm-slides…）
scripts/         # 引擎與工具（gen_journal_svg 簡報引擎、clip_evidence 佐證裁圖、
                 #   pubmed_shot/cochrane_search 檢索截圖、html2png 圖卡、PRISMA、品質 gate…）
data/            # 規格與素材（report-spec 內容結構權威、glossary 名詞公式、
                 #   slide-snippets 固定題組、CASP 檢核表 CSV、範例 content）
docs/            # ppt-master 接法詳解
projects/        # 範例專案（每份報告一個目錄，01_ask → 06_slides 結構化產出）
```

## License

MIT
