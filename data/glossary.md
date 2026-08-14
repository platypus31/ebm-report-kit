# EBM 名詞解釋與公式（生成評讀/結果頁時的術語權威）

> 整理自公開 EBM 教學資源（Oxford CEBM、CASP、通行教科書定義）與臺灣醫院教學慣例。
> 用途：投影片上的術語**中英對照與定義以本檔為準**；公式頁直接引用本檔算式。

## 5A（官方定義）

| 步驟 | 英文 | 定義 |
|---|---|---|
| Asking 問問題 | Asking | 把臨床不確定性轉成**可回答的問題**（涵蓋預防/診斷/預後/治療/傷害五型） |
| Accessing 找資料 | Accessing（範本多寫 Acquire，兩者同義） | 搜尋資料庫、追蹤現有最佳證據 |
| Appraising 分析判斷 | Appraising | 嚴格評讀：正確性（validity）＋影響力（效果大小）＋臨床適用性 |
| Applying 臨床應用 | Applying | 評讀結果 × 臨床專業 × 病人獨特生物特性/價值觀/情境 |
| Auditing 評估成果 | Auditing | 評估步驟 1-4 的成效並尋求下次改善 |

## 問題分型 → 最佳研究設計（權威表；classify 依此）

| 問題類型 | 最佳研究設計 |
|---|---|
| 診斷型 Diagnosis | 前瞻性、有盲法、與黃金標準比較之**橫斷性研究** |
| 預後型 Prognosis | Cohort > Case-control > Case series |
| 病因/傷害 Etiology/Harm | Cohort > Case-control > Case series |
| 治療型 Therapy | RCT |
| **預防型 Prevention** | RCT |
| 經濟效益 Cost-effectiveness | Economic analysis |

> ⚠️ 問題型別勾選列是**五型**（治療/診斷/預後/傷害＋**預防**）——常見錯誤是只印四型漏掉預防型。

## 背景問題 vs 前景問題（Ask 的前置分流）

- **背景問題**：5W1H 型知識問題（這病是什麼/機轉/流行病學）→ 查**教科書/UpToDate 等 summary** 直接回答，**不開 PICO 流程**。
- **前景問題**：**比較性**問題（A vs B 對某族群某結局）→ 形成 PICO、進資料庫、走完整 5A。
- 報告裡的「背景資訊」段＝把背景問題答掉，讓前景問題浮出（knowledge gap）。

## 評讀三軸 VIP

Validity 可信度（用檢核表）／Importance 臨床重要性（效果多大）／Practice 類推應用性（能否用在我的病人）。

## 評讀是什麼、不是什麼（NOT/IS 表；評讀語氣紅線）

| ✗ 評讀不是 | ✓ 評讀是 |
|---|---|
| 全面否定、嫌到一文不值 | 平衡報導：強弱點與結果好壞同時分析 |
| 只看結果是否合用 | 同時評估研究**過程**與結果 |
| 只看統計數字細節 | 質性過程與量性結果並重 |
| 統計學家才做的事 | 所有醫療人員的日常工作 |

## RCT 偏差地圖（六型偏差 ↔ 解法；評讀方法題的檢核底稿）

| 偏差 | 中文 | 對應解法 |
|---|---|---|
| Selection bias | 選擇性偏差 | 樣本具代表性（外部效度） |
| Allocation bias | 分派性偏差 | Randomization 隨機分派 |
| Performance bias | 執行性偏差 | Blinding 盲化（單盲/雙盲） |
| Attrition bias | 耗損性偏差 | Intention-to-treat 治療意向分析 |
| Detection bias | 檢出性偏差 | Outcome assessor blind 結果評估者盲化 |
| Reporting bias | 報告偏差 | Registration protocol 試驗註冊對照 |

## 統計意義 vs 臨床意義（結果頁必須**雙層**呈現）

**統計意義**：p 值（<0.05 有差異）；95% CI——看**過不過中線**（OR/RR 過 1、MD 過 0）＋**寬還是窄**（樣本數愈大愈窄愈可信；`2/100 ≠ 20/1000`）。
**臨床意義**：效果對病人到底多大——RR/RRR/ARR/NNT（類別變項）或直接解釋數值的臨床意涵（連續變項）。
🔴 只報 p 值不報 CI 寬窄、或只報統計顯著不換算 NNT，都是反例。

## 公式（2×2 起手）

```
              Outcome+   Outcome-
Experimental      a          b        EER = a/(a+b)
Control           c          d        CER = c/(c+d)
```
- RR = EER/CER；RRR = |EER−CER|/CER
- **ARR = |EER − CER|**；**NNT = 1/ARR**（益一需治數；口語化「每 N 人有 1 人受益」）；NNH 同理
- 診斷型：Sensitivity＝a/(a+c)（欄位改為疾病±）、Specificity＝d/(b+d)
  **LR+ = Sn/(1−Sp)**；**LR− = (1−Sn)/Sp**
  pre-test odds = prevalence/(1−prevalence) → post-test odds = pre-test odds × LR → **post-test probability = odds/(odds+1)**
- SR/MA：I² 異質性——<50% 低（fixed effect 合理）；≥50% 中高（random effect）；高異質性要**降低結論信心**

## Apply 的 4E（用詞校準）

通行定義：Evidence／Expectation／**Expertise**（臨床專業）／Environment。
部分報告把第三個 E 寫作 Experience（臨床經驗）——語意相近，**投影片建議採 Expertise**，兩者皆通行。
Apply 口訣：**比、想、說、尊、決**——比證據、想病人、說人話、尊重價值觀、共同決定；金句「**用病患聽得懂的話，說他們不懂的事情**」（臨床回覆頁的靈魂）。

## 評讀工具選擇

初學者建議 **CASP**（通行建議）；RCT 深評可用 RoB 2；SR 可加 AMSTAR 2；對照見 `data/appraisal-tools.md`。

## EBM 三要素（開場理念頁可用）

研究證據 × 臨床專業 × 病人期待（Sackett 三合一）；歷史錨點：Cochrane 1972 → Sackett 1980 → Guyatt 1992「EBM」一詞正式出現。
