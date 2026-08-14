// HTML → PNG 圖卡工具：表格頁（PICO/型別表/SDM/MPICOT）與敘事文字卡（臨床情境/臨床回覆）都用它生成，
// 產出的 png 走引擎 figure 頁嵌入（引擎無 table 頁型的正解，見 ebm-from-paper.md 教訓 13）。
// 用法：node scripts/html2png.js <in.html> <out.png> [width=1600] [height=900]
// 依賴：playwright（npx playwright install chromium 一次性）
const { chromium } = require('playwright');
const path = require('path');
const { pathToFileURL } = require('url');

(async () => {
  const [input, out] = process.argv.slice(2);
  if (!input || !out) {
    console.error('用法：node scripts/html2png.js <in.html> <out.png> [width=1600] [height=900]');
    process.exit(1);
  }
  const w = parseInt(process.argv[4] || '1600', 10);
  const h = parseInt(process.argv[5] || '900', 10);
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 2 });
    await page.goto(pathToFileURL(path.resolve(input)).href);
    await page.waitForTimeout(300);
    const el = await page.$('#card');
    if (el) { await el.screenshot({ path: out }); } else { await page.screenshot({ path: out, fullPage: false }); }
    console.log('✅', out);
  } finally {
    await browser.close();
  }
})();
