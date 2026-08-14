// Cochrane Library 匿名搜尋：拿 Reviews/Trials 計數＋結果頁截圖（畫靶檢索 Cochrane 段用）
// 依賴：npx playwright（chromium headless 需先 npx playwright install chromium）
// 用法：node scripts/cochrane_search.js "<query>" <screenshot.png>
// ⚠️ 結果由 portlet AJAX 載入——必須表單提交（fill+Enter）再等 selector；GET 參數直開只會得到空殼首頁
const { chromium } = require('playwright');

(async () => {
  const [q, shot] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  await page.goto('https://www.cochranelibrary.com/', { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForTimeout(2500);
  // 關 cookie 橫幅（若有）
  try { await page.click('text=/Accept|OK|Close/i', { timeout: 3000 }); } catch (e) {}
  const box = page.locator('input[name="searchText"], input#searchText, .search-bar input[type="text"]').first();
  await box.fill(q);
  await box.press('Enter');
  // 等結果清單或計數出現
  try {
    await page.waitForSelector('.search-results-item, .results-number, .search-results-section', { timeout: 60000 });
  } catch (e) { console.log('WAIT-TIMEOUT'); }
  await page.waitForTimeout(3000);
  const info = await page.evaluate(() => {
    const t = (s) => (document.querySelector(s) ? document.querySelector(s).textContent.replace(/\s+/g, ' ').trim() : null);
    const items = [...document.querySelectorAll('.search-results-item .result-title, .search-results-item h3')]
      .map(e => e.textContent.replace(/\s+/g, ' ').trim()).slice(0, 8);
    const tabs = [...document.querySelectorAll('a,button,li')].map(e => e.textContent.replace(/\s+/g, ' ').trim())
      .filter(x => /^(Cochrane Reviews|Trials|Clinical Answers|Editorials|Protocols)\s*\(?[\d,]+\)?$/.test(x)).slice(0, 12);
    return { resultsNumber: t('.results-number') || t('.search-results-header'), tabs, items };
  });
  console.log(JSON.stringify(info, null, 1));
  if (shot) await page.screenshot({ path: shot, fullPage: false });
  await browser.close();
})();
