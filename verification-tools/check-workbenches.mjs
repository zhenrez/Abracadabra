import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import crypto from 'node:crypto';
import {chromium} from 'playwright';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const output = process.argv[2];
assert(output, 'Supply a new output JSON path');
const outputPath = path.resolve(output);
assert(!fs.existsSync(outputPath), 'Existing receipts must not be overwritten');
const targets = [
  ['ARIADNE', 'work/final-day-2026-11-07/dashboard/SUN_ARIADNE_Workbench.html'],
  ['SUNNY_GUIDE', 'web/delivery-2026-11-07/system-guide.html'],
  ['SUNNY_WORKBENCH', 'web/delivery-2026-11-07/index.html']
];
const before = Object.fromEntries(targets.map(([,relative]) => [relative,
  crypto.createHash('sha256').update(fs.readFileSync(path.join(root, relative))).digest('hex')]));
const browser = await chromium.launch({headless: true});
const results = [];
try {
  for (const [name, relative] of targets) {
    for (const [width, height] of [[1440, 1000], [390, 844]]) {
      const page = await browser.newPage({viewport: {width, height}});
      await page.route(/^https?:\/\//, route => route.abort());
      const errors = [];
      page.on('pageerror', error => errors.push(String(error)));
      await page.goto(pathToFileURL(path.join(root, relative)).href);
      await page.waitForLoadState('load');
      if (name === 'ARIADNE') {
        await page.waitForFunction(() => Boolean(window.SUN_WORKBENCH));
      } else {
        await page.waitForFunction(() => Boolean(window.SUNNY_DELIVERY?.graph?.entities?.length), null, {timeout: 120000});
        if (name === 'SUNNY_WORKBENCH') await page.locator('#navigation button').first().waitFor({state: 'visible'});
      }
      assert.equal(await page.locator('body').isVisible(), true, `${name} body not visible`);
      assert((await page.locator('body').innerText()).length > 200, `${name} empty content`);
      assert.deepEqual(errors, [], `${name} browser errors`);
      const state = await page.evaluate(() => ({
        title: document.title,
        horizontalOverflow: document.documentElement.scrollWidth > innerWidth + 4,
        controls: document.querySelectorAll('button,select,input').length,
        ariadneReady: Boolean(window.SUN_WORKBENCH)
      }));
      if (name === 'ARIADNE') assert.equal(state.ariadneReady, true);
      assert(state.controls > 0, `${name} lacks interactive controls`);
      results.push({name, relative, width, height, ...state, javascriptErrors: errors});
      await page.close();
    }
  }
} finally {
  await browser.close();
}
for (const [relative, expected] of Object.entries(before)) {
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root, relative))).digest('hex'), expected);
}
const receipt = {schema: 'abracadabra.portable-browser-smoke.v1', status: 'PASSED',
  checks: results.length, results, inputSha256: before, inputsUnchanged: true,
  scope: 'Fresh page startup at two sizes with HTTP/HTTPS requests blocked, visible content, controls and JavaScript errors. No complete interaction, source-rights, audio, plugin or scientific certification.'};
fs.mkdirSync(path.dirname(outputPath), {recursive: true});
fs.writeFileSync(outputPath, JSON.stringify(receipt, null, 2) + '\n', {flag: 'wx'});
console.log(JSON.stringify({status: receipt.status, checks: receipt.checks, receipt: outputPath}));
