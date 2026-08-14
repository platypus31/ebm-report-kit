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

### 需求

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)（或其他相容 AI CLI：repo 內含 AGENTS.md／GEMINI.md 設定）
- Python 3.9+；`pymupdf`（PDF 處理，建議裝在 venv）
- [ppt-master](https://github.com/hugohe3/ppt-master)（SVG → 可編輯 pptx 匯出引擎；裝在 `~/ppt-master`）
- Node.js＋Playwright（`npx playwright install chromium`——Cochrane/PubMed 截圖與圖卡生成）

### 使用

```bash
git clone https://github.com/platypus31/ebm-report-kit.git
cd ebm-report-kit
claude
> /ebm-from-paper 33693636
```

完整範例專案見 `projects/pcv13-covid19/`（PMID 33693636 的全流程實跑產出）。

## 結構

```
skills/          # AI CLI 指令（/ebm-from-paper、/ebm、/pico、/appraise、/ebm-slides…）
scripts/         # 引擎與工具（gen_journal_svg 簡報引擎、clip_evidence 佐證裁圖、
                 #   pubmed_shot/cochrane_search 檢索截圖、html2png 圖卡、PRISMA、品質 gate…）
data/            # 規格與素材（report-spec 內容結構權威、glossary 名詞公式、
                 #   slide-snippets 固定題組、CASP 檢核表 CSV、範例 content）
projects/        # 範例專案（每份報告一個目錄，01_ask → 06_slides 結構化產出）
```

## License

MIT
