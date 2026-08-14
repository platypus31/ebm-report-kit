// PubMed 搜尋結果頁截圖＋結果數（畫靶檢索 PubMed 段用）
// 用法：node scripts/pubmed_shot.js "<query>" <screenshot.png>；計數驗證另用 E-utilities esearch（見 ebm-from-paper.md）
const { chromium } = require('playwright');
(async () => {
  const [q, shot] = process.argv.slice(2);
  if (!q || !shot) {
    console.error('用法：node scripts/pubmed_shot.js "<query>" <screenshot.png>');
    process.exit(1);
  }
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    await page.goto('https://pubmed.ncbi.nlm.nih.gov/?term=' + encodeURIComponent(q), { waitUntil: 'domcontentloaded', timeout: 90000 });
    await page.waitForTimeout(3500);
    const n = await page.evaluate(() => {
      const el = document.querySelector('.results-amount .value, .results-amount');
      return el ? el.textContent.trim() : null;
    });
    console.log('results:', n);
    await page.screenshot({ path: shot, fullPage: false });
  } finally {
    await browser.close();
  }
})();
