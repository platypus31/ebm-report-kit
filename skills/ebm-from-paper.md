---
description: 反向入口——丟一篇論文（PDF/DOI/PMID），直接生出完整 EBM 報告簡報初稿；使用者只改不寫
triggers:
  - /ebm-from-paper
---

# /ebm-from-paper <PDF 路徑 | DOI | PMID>

> 與 `/ebm` 的差別：`/ebm` 從臨床問題出發互動式走 6A；本 skill 假設**文獻已選定**，
> 從論文**反推**整份報告並產出簡報初稿。目標：丟論文 → 拿到可上台八成完成度的初稿＋明確的「待人工」清單。
> 內容結構照 `data/report-spec.md` §4（6A 骨架）；術語與公式照 `data/glossary.md`；語言：**中文為主**（題目中英對照、數據/檢索式英文）。

## 工具箱（本 skill 用到的腳本；⚙️＝2026-08-14 首跑實戰驗證過）

| 工具 | 用途 | 用法 |
|---|---|---|
| ⚙️ E-utilities（curl 直呼，**不需 MCP**） | metadata／畫靶檢索計數／鄰居文獻清單 | 見 §0/§2 指令模板 |
| ⚙️ `scripts/pubmed_shot.js` | PubMed 結果頁截圖＋計數 | `node scripts/pubmed_shot.js "<query>" out.png` |
| ⚙️ `scripts/cochrane_search.js` | Cochrane 匿名搜尋計數（Reviews/Trials）＋截圖 | `node scripts/cochrane_search.js "<query>" out.png` |
| ⚙️ `scripts/clip_evidence.py` | **評讀佐證圖**：搜關鍵句→裁該欄→紅框；`--page --rect` 手動裁 Figure | 見 §3 |
| ⚙️ `scripts/extract_figures.py` | PDF 圖表抽取（全向量刊＝整頁 render，再 clip） | `$PY extract_figures.py paper.pdf -o assets/figs` |
| ⚙️ `scripts/generate_prisma_flow.py` | PRISMA 流程 | `--identified N --screened N --eligible N --included 1` |
| `data/assets/`（自備） | 固定素材（6S 金字塔/OCEBM 等級表等，版權考量不隨 repo 附圖，可自院內教材放入或以 table/textcard 頁型重製） | figure 頁引 path |
| 環境 | `PY=~/ppt-master/.venv/bin/python`（有 pymupdf）；Playwright：`npx playwright install chromium`（一次性，裝在 `~/Library/Caches/ms-playwright`） | |

## 執行流程

### 0. 攝取
- 讀 PDF 全文（DOI/PMID 則先取全文；拿不到全文就停下告知，**不憑 abstract 硬做**）。
- ⚙️ **全文取得管道（PMC 直連 curl 會被擋，走 Europe PMC）**：
  ```bash
  # PMID → PMCID/DOI/期刊/標題
  curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<PMID>&retmode=json"
  # PDF（佐證裁圖用）＋ 全文 XML（精讀/引句用，比 PDF 文字乾淨）
  curl -sL -A "Mozilla/5.0" "https://europepmc.org/articles/<PMCID>?pdf=render" -o assets/paper.pdf
  curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML" -o assets/fulltext.xml
  # 驗證：$PY -c "import pymupdf;print(len(pymupdf.open('assets/paper.pdf')))"  # file 指令可能誤報 0 pages
  ```
- 抓 metadata：標題/作者/期刊＋IF/年份/PMID/DOI。
- 判研究設計（RCT/SR-MA/診斷準確性/世代/病例對照）→ 決定評讀工具與結果呈現（report-spec §3）。
- 建專案：🔴 **先跑 `init_project.py` 再放任何檔案**（目錄已存在它會拒跑；已放了就手動 `mkdir 01_ask 02_acquire 03_appraise 04_apply 05_audit 06_slides assets/figs`）。各步落檔到 01-06——與 `/ebm` 產物相容，之後可用任何子 skill 接手。

### 1. 反推 Ask（→ `01_ask/`）
- 從論文抽 **PICO 三欄表**（內容｜MeSH/Emtree 同義詞群｜中文關鍵字）；問題型別按**五型**勾選（治療/診斷/預後/傷害/預防，glossary 權威表）。
- **擬真臨床場景初稿**：依論文族群生成一位具體病人＋病史＋家屬/病人的原話提問（提問必須是這篇論文能回答的）。🔴 場景頁與交付清單都標 **「⚠️ 擬真案例——請使用者換成真實遇過的病人」**。
- 背景段：從論文 introduction＋UpToDate/DynaMed 共識查證組 2-4 頁（現行共識＋knowledge gap），來源標頁尾。

### 2. 畫靶式檢索（→ `02_acquire/`；本文體的默契：先射箭再畫靶，靶要畫得經得起重射）
> 報告文體的實情（2026-08-14 定調）：文獻是先選好的，檢索過程是**倒過來補**的。
> 簡報成品呈現為**正常的檢索過程**（不標「重建」）；工藝要求是**靶必須真的畫**——
> 檢索式真跑、數字真實、截圖真拍，目標論文**自然出現**在結果裡。這樣指導老師重搜也重現得出來；憑空編數字才會穿幫。
- ⚙️ **PubMed 真搜用 E-utilities（curl，headless 穩定，不依賴 MCP）**：
  ```bash
  # 計數（調式時 retmax=0 快測）；正式跑加 retmax=40&sort=relevance 拿 idlist 驗目標在內
  curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=0&term=<urlencode 檢索式>"
  # 鄰居文獻清單（文獻比較表素材）
  curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=<id1,id2,…>"
  curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=abstract&retmode=text&id=<ids>"
  ```
- **畫靶調式法（首跑實錄示範）**：從 PICO 的 MeSH 交集起手，一次加一個概念收斂，每步記數字——
  `COVID-19[Mesh] AND Pneumococcal Vaccines[Mesh]`＝192 → `+(conjugate OR PCV13)`＝77 → `+Aged[Mesh]`＝**36，目標在內** ✅。
  收斂目標 **10-40 篇**；每一步就是簡報「檢索技巧迭代」的一行。截圖：`node scripts/pubmed_shot.js "<式子>" 02_acquire 對應圖`。
- ⚙️ **Cochrane 真搜**：`node scripts/cochrane_search.js "<自然語詞 query>" <截圖>` → 報 Reviews/Trials 兩計數；**0 篇照登**（首跑實例：Reviews 0／Trials 14 全是共同施打免疫原性試驗，Corresponding 0——這就是誠實的 Cochrane 頁）。
- 資料庫範圍（2026-08-14 定案）：**PubMed＋Cochrane Library 必備**；**UpToDate/DynaMed 沒帳號，整段省略**（不放 TODO 佔位頁）；Embase/華藝選配，無權限就不出現。
- 固定素材（6S 金字塔/OCEBM 2011 表等）放 `data/assets/`（版權考量不隨 repo 附圖：可自院內教材放入，或用 `table`/`textcard` 頁型重製後重複使用）。
- `generate_prisma_flow.py` 產 PRISMA；文獻比較頁：目標論文＋真搜出的 2-4 篇近鄰文獻做 **MPICOT＋紅黃綠燈**表，選文理由＝為什麼是這篇（族群/全文/設計/樣本數）——這頁就是「畫靶」的收束：讓目標論文順理成章勝出。

### 3. 評讀初稿（→ `03_appraise/`）
- 按型別走 CASP 對應工具（`data/references/casp-*.csv`），**逐題 AI 預答**：三態勾選＋一~兩句中文評論＋**PDF 頁碼引用**；評論點名對應偏差類型（glossary 偏差地圖）。
- ⚙️ 每題佐證圖用 `scripts/clip_evidence.py`（自動雙欄偵測＋關鍵句紅框）：
  ```bash
  $PY scripts/clip_evidence.py assets/paper.pdf --search "inverse propensity weighting" -o assets/figs/ev-q5.png
  ```
  🔴 **搜尋句要用短片語（3-6 個字），不要整句**——PDF 內文有換行/連字號，長句必搜不到（首跑實證：加上 doubly-robust 前綴就 miss）。跨欄長段落改多個短句 `--search A --search B`。
- 🔴 **信心分級**：證據明確的題直接答；原文找不到依據的題勾 Can't tell 並標 **🟡 待使用者確認**——寧可留給人，不硬答。
- 評讀語氣照 glossary NOT/IS 表：平衡報導，高異質性/limitation 如實下修。

### 4. 結果抽取（→ `03_appraise/results_summary.md`）
- 效應量表格化（outcome｜效應量+95%CI｜白話判讀），**統計＋臨床雙層**：CI 過中線/寬窄＋NNT 口語化（治療/預防）或 LR→post-test probability 計算鏈（診斷）。
- 🔴 數字**只能來自 PDF 原文**（每個數字可回指頁碼）；同頁並列數據互異自檢（反例 N1）。
- ⚙️ forest plot/KM/ROC 抽圖三步（全向量刊如 JID/BMJ 專用）：
  ① `$PY scripts/extract_figures.py assets/paper.pdf -o assets/figs`——全向量刊只會得到整頁 render（manifest type=`page_render_vector`）；
  ② 定位：`$PY -c "import pymupdf; d=pymupdf.open('assets/paper.pdf'); [print(f'p{i+1}',k,r[0].y0) for i,pg in enumerate(d) for k in ['Figure 1.','Figure 2.','Table 1.'] for r in [pg.search_for(k)] if r]"`；
  ③ 依 caption y 座標換算比例裁圖區：`$PY scripts/clip_evidence.py assets/paper.pdf --page <N> --rect 0.03,<y_top>,0.97,<caption_y/頁高> -o assets/figs/fig2.png`，裁完 Read 目檢無殘字。

### 5. Apply／Audit 初稿（→ `04_apply/`、`05_audit/`）
- OCEBM 2011 等級＋落點；applicability 逐項核對清單（年齡/性別/種族/病況/時序——**病人欄留空待使用者填真實案例後補**）；台灣在地考量（健保/可近性，需查證的標 TODO）；SDM 4E（治療型，Expertise 版）或 3E＋Apply 3 題（診斷型）。
- **臨床回覆初稿**：稱謂開場→研究品質一句→數字白話化→誠實講不確定性→「與醫療團隊討論」收尾；**逐一回應場景裡的每個提問**（反例 N2 檢查）。
- Audit 骨架：五面向併 2-3 頁預填、**時數與個人反思留白**。

### 6. 組簡報（→ `06_slides/`）
照 `skills/ebm-slides.md` §3 五步（content.json → gen_journal_svg → gate → export）；大綱按 report-spec §2 張數配比自檢（評讀 35% 上下）。
- **引擎頁型現實**：`gen_journal_svg.py` 只有 `cover/section/content/figure` 四型（未知 kind 靜默 fallback 成 content）。EBM 特殊頁型的權宜寫法——
  評讀三態勾選＝content bullets 首行 `■ Yes　□ No　□ Can't tell`；PICO/MPICOT/SDM 表＝條列模擬或做成圖片走 figure 頁；6A 導航過場＝section 頁大寫階段名（`ANALYSIS`/`ASK`/…）。頁型不夠用的實感回填 report-spec，不硬改共用引擎。

### 7. 交付
1. `ebm-report.pptx`＋來源 content.json。
2. **「待人工」清單**（固定格式，附在回覆末尾）：
   - ⚠️ 擬真場景待換真實案例（換完 applicability 病人欄同步補）
   - 🟡 評讀第 X/Y 題待確認（附我的猶豫點）
   - TODO 截圖待補（哪幾庫）
   - Audit 時數/反思待填
3. 對使用者（不上簡報）一句話交代：檢索數字是哪天真跑的、用什麼式子——他被指導老師問「怎麼搜的」時答得出來。

## 紅線
- 全文拿不到不硬做；數字/引用不可編造（查不到標「原文未提及」）。
- **畫靶的底線＝可重現**：簡報上的每個檢索數字都必須來自真跑的搜尋（老師照著式子重搜要能得到同量級結果）；憑空編數字是唯一會穿幫的做法。內外分際：簡報成品呈現正常流程，「這是反推的」只存在於對使用者的交付說明。
- 擬真場景必標「⚠️ 待換真實案例」（內部標記，換完即除）。
- 品質敏感（正式上台）用 Fable/Opus 跑；夜班 headless 卡 gate 不降級硬闖（同 ebm-slides 模型建議）。

## 實跑教訓（首跑 2026-08-14 PCV13×COVID／PMID 33693636；之後每次實跑 append，不刪舊條）

1. **PMC 官網直連 curl 必被擋**（回 HTML 殼）→ 全文一律走 Europe PMC 兩管道（`?pdf=render` ＋ `fullTextXML`）；`file` 對 linearized PDF 會誤報「0 pages」，以 pymupdf 開檔頁數為準。
2. **Cochrane 結果是 portlet AJAX**：GET 帶參數直開只得空殼；必須進首頁→填搜尋框→Enter→`waitForSelector('.search-results-item…')`。計數在 facet 籤（Reviews N／Trials N）。
3. **E-utilities 免 MCP 免金鑰**，計數/清單/摘要三個端點就夠跑完檢索段；連續呼叫 sleep 1 防限流。
4. **畫靶調式節奏**：MeSH 交集起手→一次加一個概念→每步記數字；目標 10-40 篇含目標論文。調式軌跡本身就是簡報素材，不用另外編。
5. **clip_evidence 搜尋句用 3-6 字短片語**：內文換行/連字號會讓長句 miss；Figure 抽取＝extract_figures（整頁）→ search_for 定 caption y → `--rect` 比例裁 → Read 目檢。
6. **init_project.py 不容忍既有目錄**：先 init 再放檔。
7. **引擎四頁型**（cover/section/content/figure），未知 kind 靜默變 content——別發明新 kind 以為會生效。
8. Playwright：`npx playwright@1.62 install chromium` 一次性（~95MB），headless shell 落在 `~/Library/Caches/ms-playwright`；scratchpad 跑 node 腳本要先在該目錄 `npm i playwright`（或直接在 repo 內跑）。
9. **figure 頁的 title 與 caption 有長度上限**（gate 的 viewBox 水平超界檢查會擋）：title 一行 ≤ 約 22 中文字、caption ≤ 約 55 中文字——超了 gate 報 blocking，縮短重生成即可（首跑 3 條 blocking 全是這型）。
10. **快速目檢法**：SVG 用 Playwright 開 `file://` 截 1280×720 png 再 Read（gate 的 validation 目錄只有 JSON 沒有 render 圖）；抽 3-5 張代表頁（場景/評讀/figure）目檢即可。
11. content.json 的 figure `path` 以**生成時 cwd** 解析（`os.path.isfile`）——一律寫絕對路徑最穩。
15. 🔴 **python 就地改檔禁用 `open(p,"w").write(open(p).read()...)` 單行式**——`"w"` 先截斷才 read，會把檔案自我清空（2026-08-14 實踩：本 skill 被清空成 0 bytes 且 commit 進 v3 tag，靠 git 歷史救回）。正確：先 `s=read()` 完、改完再另行 `write(s)`；寫完 `assert len(s)>0`。
12. **`git add -A` 零報錯 ≠ 檔案被 track**：repo 的 `.gitignore` 有 `projects/*/`，新專案會被**靜默跳過**（首跑實證：宣稱「專案已上遠端」實際 0 檔進 commit）。要保存專案先在 .gitignore 加 `!projects/<slug>/`；宣稱「已入庫」前用 `git show <hash> --stat | grep <路徑>` 驗證。
13. **可編輯性正解（v3 定案，取代 v2 的 html2png 路線）**：使用者要能在 PowerPoint 後續編輯 → 表格/敘事卡/紅框必須是 **SVG 原生物件**（ppt-master 轉成 native 可編輯 text/shape）。引擎已支援三 kind：`table`（headers/rows/widths/note，cell 中英文感知斷行）、`textcard`（paragraphs/quote/caption）、figure 的 `hl: [rx0,ry0,rx1,ry1]`（相對圖比例紅框疊層＝獨立 shape 可拉大）。HL 座標由 `clip_evidence.py --no-box` 自動輸出。**html2png 降級用途**：只用於不需編輯的示意圖（衛教機轉圖/圖解卡）。
14. **v2→v3 版式定案（使用者 2026-08-14 兩輪驗收）**：v3 新增——臨床情境/臨床回覆＝textcard（可編輯）；型別表（權威表純表版）與 PICO 表＝table（可編輯，snippet 見 `data/slide-snippets.json`）；衛教配圖 1-2 頁（html2png 示意卡）；文獻比較後附選定文獻刊頭頁（p1 上半裁圖）；檢索目標不寫執行日期；佐證紅框＝hl 疊層；自評＝六面向題組六頁（題庫在 slide-snippets.json）。v2 舊規格：臨床情境＝敘事段落卡（擬真編造即可，條列為 fallback）；背景做成初步衛教（4 頁）；臨床問題後貼型別權威表；PICO 用三欄表格卡；檢索目標頁後重貼 PICO 表；評讀工具頁不貼對照表（直接宣告 CASP 對應工具）；**評讀每題固定兩頁＝題目 content 頁＋原文截圖 figure 頁**；臨床回覆＝一段對病人講述的文字卡。
