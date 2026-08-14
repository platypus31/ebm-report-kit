# EBM Report Kit

EBM（實證醫學）報告產生器。**主要用法：丟一篇論文 → 反推整份 6A 報告的可編輯簡報初稿**。
內容結構權威見 `data/report-spec.md`，名詞公式見 `data/glossary.md`。

## Skills

| Command | File | 說明 |
|---------|------|------|
| `/ebm-from-paper` | `skills/ebm-from-paper.md` | **主入口（反向）** — 丟論文（PDF/DOI/PMID）反推整份 6A 報告簡報初稿＋待人工清單 |
| `/ebm` | `skills/ebm.md` | 從臨床問題出發，互動式走完整 6A 流程 |
| `/pico` | `skills/pico.md` | PICO 框架分析 |
| `/classify` | `skills/classify.md` | 臨床問題分類（治療/診斷/預後/傷害/預防五型） |
| `/lit-search` | `skills/lit-search.md` | 檢索（PubMed E-utilities＋Cochrane） |
| `/appraise` | `skills/appraise.md` | 嚴格評讀（CASP / RoB 2 / AMSTAR 2） |
| `/ebm-slides` | `skills/ebm-slides.md` | 產生簡報（White Grey 格式：gen_journal_svg 引擎 → ppt-master 匯出 native 可編輯 pptx） |
| `/save-progress`／`/load-progress` | 對應 md | 儲存／載入報告進度 |

## 使用方式

### 快速開始

```bash
cd ebm-report-kit
claude
> /ebm-from-paper 33693636      # Claude Code：.claude/commands/ 已附
```

其他 AI CLI（Codex / Gemini）沒有斜線指令時，改成直接對 AI 說：
**「請讀 skills/ebm-from-paper.md 並對這篇論文執行：<PMID/DOI/PDF>」**——效果相同。

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
│   └── self_assessment.md     # 五面向自我評估
└── 06_slides/                 # 簡報輸出
    ├── content.json           # 簡報中間格式（餵給 gen_journal_svg）
    └── ebm-report.pptx        # 匯出的 PowerPoint
```

## 實體腳本

| 腳本 | 用途 |
|------|------|
| `scripts/init_project.py` | 初始化專案目錄結構 |
| `scripts/validate_step.py` | 驗證各步驟產出是否完整（檔案層級） |
| `scripts/quality_gate.py` | 品質門檻驗證（跑法：`python3 -m scripts.quality_gate --project <name>`，不可直呼） |
| `scripts/build_search_query.py` | 從 PICO YAML 自動建構 PubMed 搜尋式 |
| `scripts/generate_prisma_flow.py` | 產生 PRISMA 篩選流程圖 |
| `scripts/dedupe_results.py` | 候選文獻去重（依 PMID → DOI → 標題相似度） |
| `scripts/export_appraisal.py` | 將評讀 JSON 匯出為結構化 CSV |
| `scripts/build_slide_outline.py` | 從專案檔案自動組裝 slides.json |
| `scripts/generate_pptx.py` | python-pptx fallback 簡報產生器 |
| `scripts/status.py` | 專案進度儀表板 |

## 品質門檻

每個階段完成時可驗證：

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

`projects/example-sglt2i-ckd/` — SGLT2i 在 CKD 合併糖尿病的完整 EBM 報告範例，展示每個步驟的結構化產出。

## 外部工具（核心零 MCP）

核心流程**不依賴任何 MCP**：
- PubMed 檢索／metadata／摘要：內建 E-utilities（curl，見 `skills/ebm-from-paper.md` 指令模板）
- 論文全文：Europe PMC（PDF＋fullTextXML）
- Cochrane 檢索＋截圖：`scripts/cochrane_search.js`（內建 Playwright）
- 簡報匯出：[ppt-master](https://github.com/hugohe3/ppt-master)（`~/ppt-master`）
- 圖表：`scripts/extract_figures.py`／`clip_evidence.py`（pymupdf）

有 PubMed／Playwright MCP 可加分替代上述內建管道，但非必需。

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
├── skills/                            # 技能指令（所有平台共用）
│   ├── ebm.md                         # 完整 5A 流程
│   ├── brainstorm.md                  # 選題
│   ├── pico.md                        # PICO 分析
│   ├── classify.md                    # 問題分類
│   ├── lit-search.md                  # 文獻搜尋
│   ├── appraise.md                    # 嚴格評讀
│   ├── ebm-slides.md                  # 簡報
│   ├── save-progress.md               # 儲存進度
│   └── load-progress.md               # 載入進度
├── scripts/                           # 實體腳本（所有平台共用）
│   ├── init_project.py                # 初始化專案
│   ├── validate_step.py               # 驗證步驟產出
│   ├── quality_gate.py                # 品質門檻驗證
│   ├── build_search_query.py          # 建構搜尋策略
│   ├── generate_prisma_flow.py        # PRISMA 流程圖
│   ├── dedupe_results.py              # 文獻去重
│   ├── export_appraisal.py            # 匯出評讀 CSV
│   ├── build_slide_outline.py         # 自動組裝簡報大綱
│   ├── generate_pptx.py              # PowerPoint 產生器
│   ├── generate_platform_config.py    # 跨平台設定產生器
│   └── status.py                      # 專案進度儀表板
├── data/                              # 參考資料（所有平台共用）
│   ├── departments.md                 # 科別 MeSH 對照表
│   ├── study-type-hierarchy.md        # 證據層級
│   ├── appraisal-tools.md             # 評讀工具對照表
│   ├── ebm-slide-template.md          # 簡報結構範本
│   ├── progress-schema.md             # 進度 JSON schema
│   ├── references/                    # 結構化模板
│   └── templates/                     # 簡報設計模板
├── projects/                          # 專案目錄
│   └── example-sglt2i-ckd/            # 範例專案
└── tests/                             # 測試
```
