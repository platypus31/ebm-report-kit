# 檢索策略（真跑於 2026-08-14，E-utilities＋Playwright；數字皆可重現）

## PubMed（Primary）
**檢索技巧迭代**（每步真實計數，簡報照此節奏呈現——檢索迭代紀錄文體）：

| 步驟 | 檢索式 | Results |
|---|---|---|
| 1 | `("COVID-19"[Mesh]) AND ("Pneumococcal Vaccines"[Mesh])` | 192 |
| 2 | 步驟1 `AND (conjugate OR PCV13)`（聚焦結合型疫苗——PICO 的 I） | 77 |
| 3 | 步驟2 `AND ("Aged"[Mesh])`（聚焦高齡族群——PICO 的 P） | **36** |

- 最終式：`("COVID-19"[Mesh]) AND ("Pneumococcal Vaccines"[Mesh]) AND (conjugate OR PCV13) AND ("Aged"[Mesh])`
- **Results: 36 / Corresponding results: 4**（依標題摘要篩符合 PICO 者，見 selected_articles.md）
- 截圖：`assets/figs/pubmed-search.png`（36 results 頁面）

## Cochrane Library（Secondary）
- 搜尋詞：`pneumococcal conjugate vaccine AND COVID-19`（Title-Abstract-Keyword）
- **Cochrane Reviews: 0 / Trials: 14 / Corresponding: 0**——14 篇 Trials 全為 COVID 疫苗與肺炎鏈球菌疫苗
  「共同施打免疫原性/安全性」註冊試驗，無一回答本 PICO（0 篇照登，誠實原則）
- 截圖：`assets/figs/cochrane-search.png`

## 未檢索（如實交代）
- UpToDate／DynaMed：無機構帳號，本報告省略（2026-08-14 裁定）。
- Embase／華藝：無帳號，選配未跑。

## PRISMA（見 prisma_flow.md）
Identification 50（PubMed 36＋Cochrane 14）→ 去重 50（無重複）→ 標題摘要篩選 → 全文評估 4 → **納入評讀 1**
