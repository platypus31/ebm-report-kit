---
description: 反向入口——丟一篇論文（PDF/DOI/PMID），直接生出完整 EBM 報告簡報初稿；使用者只改不寫
triggers:
  - /ebm-from-paper
---

# /ebm-from-paper <PDF 路徑 | DOI | PMID>

> 與 `/ebm` 的差別：`/ebm` 從臨床問題出發互動式走 6A；本 skill 假設**文獻已選定**，
> 從論文**反推**整份報告並產出簡報初稿。目標：丟論文 → 拿到可上台八成完成度的初稿＋明確的「待人工」清單。
> 內容結構照 `data/report-spec.md`（§1 骨架、§2 張數、§3 分型、§4 紅線）；術語與公式照 `data/glossary.md`；
> 語言：**中文為主**（評讀題目中英對照，數據／檢索式保持英文原文）。

## 環境變數（本 skill 全部指令共用，先設好）

```bash
PPT_MASTER="${PPT_MASTER_DIR:-$HOME/ppt-master}"
PY="$PPT_MASTER/.venv/bin/python"     # 有 pymupdf；也可用 kit 自己的 .venv/bin/python
PROJECT_DIR="$PWD/projects/<name>"    # 換成你的專案名，須為絕對路徑
```

⚠️ 所有指令都在 **repo 根目錄**執行（`scripts/…` 是相對 repo root 的路徑），
專案內的檔案一律用 `$PROJECT_DIR/…` 絕對路徑指涉，不要 `cd` 進專案目錄。
依賴沒裝好的話先跑 `bash bootstrap.sh`。

## 工具箱（本 skill 用到的腳本）

| 工具 | 用途 | 用法 |
|---|---|---|
| E-utilities（curl 直呼，**不需 MCP**） | metadata／檢索計數／鄰居文獻清單 | 見 §0／§2 指令模板 |
| `scripts/pubmed_shot.js` | PubMed 結果頁截圖＋計數 | `node scripts/pubmed_shot.js "<query>" out.png` |
| `scripts/cochrane_search.js` | Cochrane 匿名搜尋計數（Reviews／Trials）＋截圖 | `node scripts/cochrane_search.js "<query>" out.png` |
| `scripts/clip_evidence.py` | **評讀佐證圖**：搜關鍵句→裁該欄→紅框；`--page --rect` 手動裁 Figure | 見 §3 |
| `scripts/extract_figures.py` | PDF 圖表抽取（全向量刊＝整頁 render，再 clip） | `"$PY" scripts/extract_figures.py "$PROJECT_DIR/assets/paper.pdf" -o "$PROJECT_DIR/assets/figs"` |
| `scripts/generate_prisma_flow.py` | PRISMA 流程 | `--identified N --screened N --eligible N --included 1` |
| `data/assets/`（自備） | 固定素材（6S 金字塔／OCEBM 等級表等；版權考量不隨 repo 附圖，可放自院教材，或用 table／textcard 頁型重製） | figure 頁引 path |

## 執行流程

### 0. 攝取

1. **先建專案**（🔴 一定要先 init 再放任何檔案——目錄已存在時 `init_project.py` 會拒跑）：

   ```bash
   python3 scripts/init_project.py --name <name> --department <科別>
   mkdir -p "$PROJECT_DIR/assets/figs"     # init 會建 01_ask…06_slides 與 assets/screenshots，figs 要自己補
   ```

   各步落檔到 `01_ask`～`06_slides`——與 `/ebm` 產物相容，之後可用任何子 skill 接手。

2. **取全文**（PMC 官網直連 curl 會被擋，走 Europe PMC）：

   ```bash
   # PMID → PMCID／DOI／期刊／標題
   curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<PMID>&retmode=json"
   # PDF（佐證裁圖用）＋ 全文 XML（精讀／引句用，比 PDF 文字乾淨）
   curl -sL -A "Mozilla/5.0" "https://europepmc.org/articles/<PMCID>?pdf=render" -o "$PROJECT_DIR/assets/paper.pdf"
   curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML" -o "$PROJECT_DIR/assets/fulltext.xml"
   # 驗證頁數（file 指令對 linearized PDF 會誤報 0 pages，以 pymupdf 為準）
   "$PY" -c "import pymupdf;print(len(pymupdf.open('$PROJECT_DIR/assets/paper.pdf')))"
   ```

   讀 PDF 全文；**拿不到全文就停下告知，不憑 abstract 硬做**。

3. 抓 metadata：標題／作者／期刊＋IF／年份／PMID／DOI。
4. 判研究設計（RCT／SR-MA／診斷準確性／世代／病例對照）→ 決定評讀工具與結果呈現（`data/report-spec.md` §3）。

### 1. 反推 Ask（→ `01_ask/`）
- 從論文抽 **PICO 三欄表**（內容｜MeSH/Emtree 同義詞群｜中文關鍵字）；問題型別按**五型**勾選（治療/診斷/預後/傷害/預防，glossary 權威表）。
- **擬真臨床場景初稿**：依論文族群生成一位具體病人＋病史＋家屬/病人的原話提問（提問必須是這篇論文能回答的）。🔴 場景頁與交付清單都標 **「⚠️ 擬真案例——請使用者換成真實遇過的病人」**。
- 背景段：從論文 introduction＋現行指引／二次文獻查證組 2-4 頁（現行共識＋knowledge gap），來源標頁尾。

### 2. 畫靶式檢索（→ `02_acquire/`）

> 這類報告的實情：文獻是先選好的，檢索過程是**倒過來補**的。
> 簡報成品呈現為正常的檢索過程；工藝要求是**靶必須真的畫**——
> 檢索式真跑、數字真實、截圖真拍，目標論文**自然出現**在結果裡。
> 這樣指導老師照式子重搜也重現得出來；憑空編數字才會穿幫。

- **PubMed 真搜用 E-utilities**（curl，headless 穩定，不依賴 MCP）：

  ```bash
  # 計數（調式時 retmax=0 最快）
  curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=0&term=<urlencode 檢索式>"
  # 正式跑：加 retmax=40&sort=relevance 拿 idlist，驗目標論文在結果內
  # 鄰居文獻清單（文獻比較表素材）
  curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=<id1,id2,…>"
  curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=abstract&retmode=text&id=<ids>"
  ```

  連續呼叫之間 `sleep 1` 防限流。
- **畫靶調式法**：從 PICO 的 MeSH 交集起手，一次加一個概念收斂，每步記數字。範例軌跡——
  `COVID-19[Mesh] AND Pneumococcal Vaccines[Mesh]`＝192 → `+(conjugate OR PCV13)`＝77 → `+Aged[Mesh]`＝**36，目標在內** ✅。
  收斂目標 **10-40 篇**；每一步就是簡報「檢索技巧迭代」的一行。
  截圖：`node scripts/pubmed_shot.js "<式子>" "$PROJECT_DIR/assets/screenshots/pubmed-search.png"`
- **Cochrane 真搜**：`node scripts/cochrane_search.js "<自然語詞 query>" "$PROJECT_DIR/assets/screenshots/cochrane-search.png"`
  → 報 Reviews／Trials 兩計數；**0 篇照登**（0 篇本身就是誠實的 Cochrane 頁，不要跳過）。
- 資料庫範圍：**PubMed＋Cochrane Library 必備**；UpToDate／DynaMed／Embase／華藝**有機構訂閱才做**，
  沒帳號就整段省略（**不要放 TODO 佔位頁**，也不要假裝搜過）。
- 固定素材（6S 金字塔／OCEBM 2011 表等）放 `data/assets/`（版權考量不隨 repo 附圖：可放自院教材，或用 `table`／`textcard` 頁型重製）。
- `generate_prisma_flow.py` 產 PRISMA；文獻比較頁：目標論文＋真搜出的 2-4 篇近鄰文獻做 **MPICOT＋紅黃綠燈**表，選文理由＝為什麼是這篇（族群/全文/設計/樣本數）——這頁就是「畫靶」的收束：讓目標論文順理成章勝出。

### 3. 評讀初稿（→ `03_appraise/`）
- 按型別走 CASP 對應工具（`data/references/casp-*.csv`），**逐題 AI 預答**：三態勾選＋一~兩句中文評論＋**PDF 頁碼引用**；評論點名對應偏差類型（glossary 偏差地圖）。
- 每題佐證圖用 `scripts/clip_evidence.py`（自動雙欄偵測＋關鍵句紅框）：

  ```bash
  "$PY" scripts/clip_evidence.py "$PROJECT_DIR/assets/paper.pdf" \
      --search "inverse propensity weighting" -o "$PROJECT_DIR/assets/figs/ev-q5.png"
  ```

  🔴 **搜尋句要用短片語（3-6 個字），不要整句**——PDF 內文有換行／連字號，長句必搜不到。
  跨欄長段落改用多個短句 `--search A --search B`。
- 🔴 **信心分級**：證據明確的題直接答；原文找不到依據的題勾 Can't tell 並標 **🟡 待使用者確認**——寧可留給人，不硬答。
- 評讀語氣照 glossary NOT/IS 表：平衡報導，高異質性／limitation 如實下修。

### 4. 結果抽取（→ `03_appraise/results_summary.md`）
- 效應量表格化（outcome｜效應量+95%CI｜白話判讀），**統計＋臨床雙層**：CI 過中線／寬窄＋NNT 口語化（治療／預防）或 LR→post-test probability 計算鏈（診斷）。
- 🔴 數字**只能來自 PDF 原文**（每個數字可回指頁碼）；同頁並列數據互異自檢（反例 N1）。
- forest plot／KM／ROC 抽圖三步（全向量刊專用）：

  ```bash
  # ① 抽圖：全向量刊只會得到整頁 render（manifest type=page_render_vector）
  "$PY" scripts/extract_figures.py "$PROJECT_DIR/assets/paper.pdf" -o "$PROJECT_DIR/assets/figs"
  # ② 定位 caption 的 y 座標
  "$PY" -c "import pymupdf; d=pymupdf.open('$PROJECT_DIR/assets/paper.pdf'); [print(f'p{i+1}',k,r[0].y0) for i,pg in enumerate(d) for k in ['Figure 1.','Figure 2.','Table 1.'] for r in [pg.search_for(k)] if r]"
  # ③ 依 caption y 換算比例裁圖區（caption 之上），裁完目檢無殘字
  "$PY" scripts/clip_evidence.py "$PROJECT_DIR/assets/paper.pdf" \
      --page <N> --rect 0.03,<y_top>,0.97,<caption_y/頁高> -o "$PROJECT_DIR/assets/figs/fig2.png"
  ```

### 5. Apply／Audit 初稿（→ `04_apply/`、`05_audit/`）
- OCEBM 2011 等級＋落點；applicability 逐項核對清單（年齡/性別/種族/病況/時序——**病人欄留空待使用者填真實案例後補**）；在地考量（健保給付／院內可近性，需查證的標 TODO）；SDM 4E（治療型，Expertise 版）或 3E＋Apply 3 題（診斷型）。
- **臨床回覆初稿**：稱謂開場→研究品質一句→數字白話化→誠實講不確定性→「與醫療團隊討論」收尾；**逐一回應場景裡的每個提問**（反例 N2 檢查）。
- Audit 骨架：五面向自評＋效率評估（共六組，題庫在 `data/slide-snippets.json` 的 `audit_questions`）預填、**時數與個人反思留白**。

### 6. 組簡報（→ `06_slides/`）

照 `skills/ebm-slides.md` §3 五步（content.json → gen_journal_svg → 品質關卡 → 匯出）；
大綱按 `data/report-spec.md` §2 張數配比自檢（總數 45-70 張，評讀 35% 上下）。

**引擎頁型（`gen_journal_svg.py` 支援下列五種 kind；寫錯 kind 會直接報錯中止並列出合法值，不會靜默降級）**：

| kind | 用途 | 可編輯性 |
|---|---|---|
| `section` | 6A 導航過場（`ANALYSIS`/`ASK`/…大寫階段名） | — |
| `content` | 條列頁；評讀三態勾選寫成首行 `■ Yes　□ No　□ Can't tell` | 原生文字 |
| `table` | PICO／MPICOT／型別權威表（`headers`/`rows`/`widths`/`note`，cell 中英文感知斷行） | **原生表格** |
| `textcard` | 臨床情境敘事卡、臨床回覆（`paragraphs`/`quote`/`caption`） | **原生文字** |
| `figure` | 圖表／佐證截圖；`hl: [rx0,ry0,rx1,ry1]` 疊一層相對比例紅框 | 紅框是**獨立 shape**，可拉大 |

🔴 表格與敘事卡**一律用 `table`／`textcard`，不要做成圖片**——使用者要能在 PowerPoint 裡改字。
`hl` 座標可由 `clip_evidence.py --no-box` 自動輸出。`html2png.js` 只用於不需編輯的示意圖（衛教機轉圖／圖解卡）。
頁型不夠用時把實感回填 `data/report-spec.md`，不要硬改共用引擎。

### 7. 交付
1. `06_slides/ebm-report.pptx` ＋ 來源 `content.json`。
2. **「待人工」清單**（固定格式，附在回覆末尾）：
   - ⚠️ 擬真場景待換真實案例（換完 applicability 病人欄同步補）
   - 🟡 評讀第 X/Y 題待確認（附我的猶豫點）
   - TODO 截圖待補（哪幾庫）
   - Audit 時數／反思待填
3. 對使用者（不上簡報）一句話交代：檢索數字是哪天真跑的、用什麼式子——他被指導老師問「怎麼搜的」時答得出來。

## 紅線
- 全文拿不到不硬做；數字／引用不可編造（查不到標「原文未提及」）。
- **畫靶的底線＝可重現**：簡報上的每個檢索數字都必須來自真跑的搜尋（照著式子重搜要能得到同量級結果）。憑空編數字是唯一會穿幫的做法。
- 擬真場景必標「⚠️ 待換真實案例」，使用者換成真實病人後才移除標記。

## 實務要點（實跑驗證過的坑）

1. **PMC 官網直連 curl 必被擋**（回 HTML 殼）→ 全文一律走 Europe PMC 兩管道（`?pdf=render` ＋ `fullTextXML`）；
   `file` 指令對 linearized PDF 會誤報「0 pages」，以 pymupdf 開檔頁數為準。
2. **Cochrane 結果是 portlet AJAX**：GET 帶參數直開只得空殼；必須進首頁→填搜尋框→Enter→等結果元素出現。
   計數在 facet 籤（Reviews N／Trials N）。`scripts/cochrane_search.js` 已封裝這套流程。
3. **E-utilities 免 MCP 免金鑰**：計數／清單／摘要三個端點就夠跑完整個檢索段；連續呼叫 `sleep 1` 防限流。
4. **畫靶調式節奏**：MeSH 交集起手→一次加一個概念→每步記數字；目標 10-40 篇且含目標論文。
   調式軌跡本身就是簡報素材，不用另外編。
5. **clip_evidence 搜尋句用 3-6 字短片語**：內文換行／連字號會讓長句 miss。
   Figure 抽取＝extract_figures（整頁）→ `search_for` 定 caption y → `--rect` 比例裁 → 目檢。
6. **`init_project.py` 不容忍既有目錄**：先 init 再放檔（見 §0 第 1 步）。
7. **figure 頁的 title 與 caption 有長度上限**（品質關卡的 viewBox 水平超界檢查會擋）：
   title 一行 ≤ 約 22 個中文字、caption ≤ 約 55 個中文字——超了會報 blocking，縮短重生成即可。
8. **content.json 的 figure `path` 以生成時的 cwd 解析**（`os.path.isfile`）——一律寫絕對路徑最穩。
   缺圖不會中斷，引擎會畫佔位框。
9. **快速目檢法**：SVG 用 Playwright 開 `file://` 截 1280×720 png 再看（品質關卡的 validation 目錄只有 JSON 沒有 render 圖）；
   抽 3-5 張代表頁（場景／評讀／figure）目檢即可。
10. **Playwright 版本**跟著 repo 的 `package.json` 走：`npm install` ＋ `npx playwright install chromium`（一次性，約 95MB，
    落在 `~/Library/Caches/ms-playwright`）。`bash bootstrap.sh` 會一起做掉。
11. **就地改檔不要用 `open(p,"w").write(open(p).read()…)` 單行式**——`"w"` 會先截斷才 read，把檔案清空。
    正確做法：先 `s = read()` 讀完，改完再另行 `write(s)`，寫完 `assert len(s) > 0`。
