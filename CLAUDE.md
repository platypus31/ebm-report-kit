# EBM Report Kit

EBM（實證醫學）報告產生器——丟論文反推整份 6A 報告的可編輯簡報初稿。

## Skills

| Command | File | 說明 |
|---------|------|------|
| `/ebm-from-paper` | `skills/ebm-from-paper.md` | **最常用（反向）**：丟論文(PDF/DOI/PMID)反推整份 6A 報告簡報初稿＋待人工清單 |
| `/ebm` | `skills/ebm.md` | 從臨床問題出發，互動式走完整 6A 流程 |
| `/brainstorm` | `skills/brainstorm.md` | 搜尋 PubMed 近期文獻，激發選題靈感 |
| `/pico` | `skills/pico.md` | PICO 框架分析 |
| `/classify` | `skills/classify.md` | 臨床問題分類（診斷/預後/治療/預防/病因傷害） |
| `/lit-search` | `skills/lit-search.md` | 6S 階層文獻搜尋（PubMed + Cochrane + Embase） |
| `/appraise` | `skills/appraise.md` | 嚴格評讀（CASP / RoB 2 / AMSTAR 2） |
| `/ebm-slides` | `skills/ebm-slides.md` | 產生 EBM 簡報（White Grey→ppt-master 可編輯 pptx） |
| `/save-progress` | `skills/save-progress.md` | 儲存目前 EBM 報告進度 |
| `/load-progress` | `skills/load-progress.md` | 載入已儲存的進度並繼續 |

## 使用方式

### 快速開始

```bash
git clone https://github.com/platypus31/ebm-report-kit.git
cd ebm-report-kit
bash bootstrap.sh        # 一鍵裝依賴 + self-check（冪等；--check-only 只檢查不安裝）
claude
> /ebm-from-paper 33693636    # 最常用：文獻已選好 → 反推整份報告
> /ebm                        # 或從臨床問題出發，互動式走完整 6A
```

`/ebm` 會自動建立專案目錄、引導完成 6A 流程、每個步驟產出結構化檔案。

### 手動建立專案

```bash
python3 scripts/init_project.py --name my-topic --department 腎臟內科
```

### 單獨使用子技能

```
> /brainstorm    # 只做選題
> /pico          # 只做 PICO 分析
> /lit-search    # 只做文獻搜尋
```

## 專案結構

每個 EBM 報告都是一個獨立專案，位於 `projects/<name>/`：

```
projects/<name>/
├── TOPIC.txt                  # 主題描述
├── README.md                  # 專案摘要
├── 01_ask/                    # ASK — PICO、臨床情境、背景、分類
│   ├── pico.yaml              # PICO 結構化資料（YAML）
│   ├── clinical_scenario.md   # 臨床情境
│   ├── introduction.md        # 背景資訊
│   └── classification.md      # 問題分類與證據層級
├── 02_acquire/                # ACQUIRE — 搜尋策略、PRISMA、選文
│   ├── search_strategy.md     # 完整搜尋策略
│   ├── prisma_flow.md         # PRISMA 篩選流程圖
│   ├── candidates.csv         # 候選文獻列表（CSV）
│   └── selected_articles.md   # 選定文獻與理由
├── 03_appraise/               # APPRAISE — 評讀結果
│   ├── tool_selection.md      # 評讀工具選擇理由
│   ├── appraisal.csv          # 逐題評讀結果（CSV）
│   ├── coi_check.md           # 利益衝突檢核
│   ├── results_summary.md     # 研究結果摘要
│   └── grade.md               # GRADE 評定（選擇性）
├── 04_apply/                  # APPLY — 臨床應用
│   ├── evidence_level.md      # OCEBM 證據等級
│   ├── local_considerations.md # 台灣在地化考量
│   └── clinical_reply.md      # 去學術化臨床回覆
├── 05_audit/                  # AUDIT — 自我評估
│   └── self_assessment.md     # 五面向自評＋效率評估
├── assets/                    # 素材
│   ├── paper.pdf              # 論文全文（gitignore）
│   ├── screenshots/           # 檢索/評讀截圖
│   ├── screenshots.json       # 截圖清單
│   └── figs/                  # 抽出的圖表與佐證裁圖（gitignore）
└── 06_slides/                 # 簡報輸出
    ├── content.json           # 簡報內容（現行格式，餵 gen_journal_svg.py）
    ├── slides.json            # 舊格式（build_slide_outline.py → generate_pptx.py fallback 用）
    └── ebm-report.pptx        # PowerPoint 檔案
```

## 實體腳本

| 腳本 | 用途 |
|------|------|
| `scripts/init_project.py` | 初始化專案目錄結構 |
| `scripts/validate_step.py` | 驗證各步驟產出是否完整（檔案層級） |
| `scripts/quality_gate.py` | 品質門檻驗證（內容層級，檢查 PICO 欄位、CSV 品質等） |
| `scripts/build_search_query.py` | 從 PICO YAML 自動建構 PubMed 搜尋式 |
| `scripts/generate_prisma_flow.py` | 產生 PRISMA 篩選流程圖 |
| `scripts/dedupe_results.py` | 候選文獻去重（依 PMID → DOI → 標題相似度） |
| `scripts/export_appraisal.py` | 將評讀 JSON 匯出為結構化 CSV |
| `scripts/gen_journal_svg.py` | **簡報主引擎**：content.json → White Grey SVG deck |
| `scripts/clip_evidence.py` | 評讀佐證裁圖（搜關鍵句→裁該欄→畫紅框） |
| `scripts/extract_figures.py` | 從論文 PDF 抽統計圖表 |
| `scripts/pubmed_shot.js` | PubMed 結果頁截圖＋計數（Playwright） |
| `scripts/cochrane_search.js` | Cochrane 搜尋計數＋截圖（Playwright） |
| `scripts/html2png.js` | HTML 圖卡轉 PNG（示意圖用） |
| `scripts/screenshot.py` | 截圖清單管理與完整性檢查 |
| `scripts/build_slide_outline.py` | 從專案檔案組裝舊格式 slides.json（僅 fallback 用） |
| `scripts/generate_pptx.py` | python-pptx fallback 簡報產生器 |
| `scripts/status.py` | 專案進度儀表板 |

## 品質門檻

以下 5 個產出階段完成時會自動驗證：

| 階段 | 驗證內容 |
|------|---------|
| ASK | pico.yaml 中 P/I/C/O MeSH 不為空 |
| ACQUIRE | 至少選定 1 篇文獻，candidates.csv 不為空 |
| APPRAISE | appraisal.csv 每題有 answer；Can't tell > 2 題則警告 |
| APPLY | evidence_level.md 和 clinical_reply.md 存在 |
| AUDIT | self_assessment.md 存在 |

可隨時用 `python3 scripts/validate_step.py --project <name>` 驗證全部步驟。

## 參考模板

| 模板 | 路徑 | 用途 |
|------|------|------|
| PICO YAML | `data/references/pico-template.yaml` | PICO 結構化模板 |
| CASP RCT | `data/references/casp-rct-template.csv` | RCT 評讀 11 題 |
| CASP SR | `data/references/casp-sr-template.csv` | Systematic Review 評讀 10 題 |
| CASP Cohort | `data/references/casp-cohort-template.csv` | Cohort 評讀 12 題 |
| CASP Case-Control | `data/references/casp-case-control-template.csv` | Case-Control 評讀 11 題 |
| CASP Diagnostic | `data/references/casp-diagnostic-template.csv` | Diagnostic 評讀 11 題 |

## 範例專案

- **`projects/example-pcv13-covid19/`** — `/ebm-from-paper` 反向流程的完整實跑產出（PMID 33693636，預防型問題、CASP Cohort）。
  `06_slides/content.json` 是**現行主路線格式**的權威範例。
- `projects/example-sglt2i-ckd/` — SGLT2i 在 CKD 合併糖尿病的報告範例，展示 01～05 各步的結構化產出。
  ⚠️ 它的 `06_slides/slides.json` 是**舊格式**（僅 fallback 用）。

掃描 `projects/` 列出使用者專案時，兩個範例都要排除。

## 外部工具（核心流程零 MCP）

**主路線 `/ebm-from-paper` 不需要任何 MCP server**——檢索與全文都用 `curl` 直呼公開 API，截圖用 Playwright CLI：

| 用途 | 實作 | 備註 |
|------|------|------|
| PubMed 檢索／書目／鄰居文獻 | NCBI E-utilities（curl 直呼） | 免金鑰 |
| 全文取得 | Europe PMC REST（curl；PMC 直連會被擋） | |
| PubMed／Cochrane 檢索截圖 | `scripts/pubmed_shot.js`、`scripts/cochrane_search.js`（Playwright） | 需 `npx playwright install chromium` |
| PDF 圖表抽取／佐證裁圖 | `scripts/extract_figures.py`、`scripts/clip_evidence.py`（PyMuPDF） | |
| 簡報產出 | `scripts/gen_journal_svg.py` → ppt-master 匯出 native pptx | 見 `docs/ppt-master-integration.md` |

MCP server 一律**選配**：`/lit-search`、`/brainstorm`、`/appraise` 若偵測到 PubMed／Playwright MCP 會優先使用，偵測不到就走上表的內建管道，流程不中斷。

## 語言規則

- 使用者互動：繁體中文
- PubMed / API 搜尋：English
- MeSH terms：English
- 簡報內容：中文標題 + 英文引用

## 完整檔案結構

```
ebm-report-kit/
├── CLAUDE.md                          # Claude Code 設定
├── GEMINI.md                          # Gemini CLI 設定
├── AGENTS.md                          # OpenAI Codex CLI 設定
├── .cursorrules                       # Cursor 設定
├── .github/copilot-instructions.md    # GitHub Copilot 設定
├── README.md
├── bootstrap.sh                       # 一鍵安裝依賴 + self-check
├── skills/                            # 技能指令（所有平台共用）
│   ├── ebm-from-paper.md              # 反向入口（最常用）
│   ├── ebm.md                         # 完整 6A 流程
│   ├── brainstorm.md                  # 選題
│   ├── pico.md                        # PICO 分析
│   ├── classify.md                    # 問題分類
│   ├── lit-search.md                  # 文獻搜尋
│   ├── appraise.md                    # 嚴格評讀
│   ├── ebm-slides.md                  # 簡報
│   ├── save-progress.md               # 儲存進度
│   └── load-progress.md               # 載入進度
├── scripts/                           # 實體腳本（所有平台共用）
│   ├── gen_journal_svg.py             # 簡報主引擎（content.json → SVG）
│   ├── clip_evidence.py               # 評讀佐證裁圖＋紅框
│   ├── extract_figures.py             # 從 PDF 抽統計圖表
│   ├── pubmed_shot.js                 # PubMed 截圖（Playwright）
│   ├── cochrane_search.js             # Cochrane 搜尋＋截圖（Playwright）
│   ├── html2png.js                    # HTML 圖卡轉 PNG
│   ├── init_project.py                # 初始化專案
│   ├── validate_step.py               # 驗證步驟產出
│   ├── quality_gate.py                # 品質門檻驗證
│   ├── build_search_query.py          # 建構搜尋策略
│   ├── generate_prisma_flow.py        # PRISMA 流程圖
│   ├── dedupe_results.py              # 文獻去重
│   ├── export_appraisal.py            # 匯出評讀 CSV
│   ├── screenshot.py                  # 截圖清單管理
│   ├── build_slide_outline.py         # 組裝舊格式 slides.json（fallback 用）
│   ├── generate_pptx.py               # python-pptx fallback 產生器
│   ├── generate_platform_config.py    # 跨平台設定產生器
│   └── status.py                      # 專案進度儀表板
├── data/                              # 參考資料（所有平台共用）
│   ├── report-spec.md                 # 🔴 內容結構權威（6A 骨架/張數/分型/紅線）
│   ├── glossary.md                    # 名詞與公式權威
│   ├── example-content-ebm.json       # content.json 骨架範例
│   ├── slide-snippets.json            # 固定題組（型別權威表、自評題庫）
│   ├── departments.md                 # 科別 MeSH 對照表
│   ├── study-type-hierarchy.md        # 證據層級
│   ├── appraisal-tools.md             # 評讀工具對照表
│   ├── ebm-slide-template.md          # 舊版 5A 快速骨架（衝突時以 report-spec 為準）
│   ├── progress-schema.md             # 進度 JSON schema
│   ├── assets/                        # 自備固定素材（版權圖不隨 repo 附帶）
│   ├── references/                    # CASP 檢核表 CSV、PICO 模板
│   └── templates/                     # style-a~d（僅 fallback generate_pptx.py 用）
├── docs/
│   └── ppt-master-integration.md      # ppt-master 安裝後的接法詳解
├── projects/                          # 專案目錄
│   ├── example-pcv13-covid19/         # 範例：反向流程完整實跑（現行 content.json 格式）
│   └── example-sglt2i-ckd/            # 範例：01～05 結構化產出（舊 slides.json 格式）
└── tests/                             # 測試
```
