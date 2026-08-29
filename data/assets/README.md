# data/assets — 固定教學素材

放**跨報告重複使用**的固定素材。目前有兩類：

## 1. 本 repo 自繪的六張教學圖（隨 repo 附帶，可直接用）

由 `scripts/gen_teaching_figures.py` 程式生成，全部是 1280×720 的全頁 SVG，
直接就是一張投影片（不是塞進圖框的插圖）：

| 檔案 | 內容 |
|---|---|
| `evidence-pyramid-6s.svg` | 6S 證據金字塔（Systems → Studies，含 secondary／primary 分界） |
| `ocebm-2011-levels-en.svg` | OCEBM 2011 Levels of Evidence（英文原表結構） |
| `ocebm-2011-levels-zh.svg` | 同上中文版（另附建議等級 A–D 對應帶） |
| `appraisal-tool-selection.svg` | 評讀工具 ↔ 適用研究設計對照表（RoB／CASP／CAT／NOS／AMSTAR／AGREE） |
| `appraisal-workflow.svg` | 評讀流程五步驟（挑文獻 → 挑工具 → 評讀 → 定證據等級 → 定推薦等級） |
| `appraisal-vip.svg` | 嚴格評讀 VIP 框架（Validity／Importance／Practice） |

**用法**（content.json 的 `asset` 頁型，`caption` 由引擎疊在圖下方）：

```json
{"kind": "asset", "title": "以 6S 階層取得實證資訊",
 "caption": "本報告：PubMed＋Cochrane（無帳號資料庫如實省略）",
 "path": "data/assets/evidence-pyramid-6s.svg"}
```

**改圖 / 重生**：改 `scripts/gen_teaching_figures.py` 的資料常數後重跑，不要手改 SVG（下次重生會被蓋掉）：

```bash
python3 scripts/gen_teaching_figures.py          # 重生六張到本目錄
python3 scripts/gen_teaching_figures.py /tmp/out # 或輸出到別處試版
```

**為什麼是自繪的**：這些圖的知識內容（分級、工具清單、流程步驟）是公開學術事實，
但坊間流通的圖檔版式多半有版權。本 repo 依公開來源自行重繪版式，每張圖底部都標了出處，
所以可以隨這個公開 repo 一起散布。內容有疑義時以各自的官方公開文件為準。

## 2. 你自己的固定素材（不隨 repo 附帶）

院內教學流程圖之類的自備圖片放這裡，檔名自訂，在 `content.json` 的 `figure` 頁用 `path` 指過去。
**有版權的圖請不要提交進 repo。**

沒有這些圖也能跑完整個流程：簡報引擎遇到缺圖會畫佔位框，不會中斷。
另一個做法是用 `table`／`textcard` 頁型把內容重製成可編輯的原生頁面，效果通常比貼圖更好。
