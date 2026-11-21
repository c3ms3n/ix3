// shot.js <url> <out.png> [waitMs] - a Chromium (CDP) screenshot of a page with GPU emulation; CLEAN=1 hides the bench outlines. Used by tools/previews_cluster.py.
// usage: node shot.js <url> <out.png> [waitMs]
const { spawn } = require('child_process');
const fs = require('fs');
const [url, out, wait] = [process.argv[2], process.argv[3], +process.argv[4] || 12000];
const port = 9300 + Math.floor(Math.random() * 500);
const ch = spawn('chromium', ['--headless=new', '--no-sandbox', '--user-data-dir=/tmp/chr-cdp-' + port, '--use-gl=angle', '--use-angle=swiftshader',
  '--enable-unsafe-swiftshader', '--window-size=1920,760', '--remote-debugging-port=' + port, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  let targets;
  for (let i = 0; i < 60; i++) { try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); if (targets.length) break; } catch (e) {} await sleep(500); }
  const page = targets.find((t) => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));
  let id = 0; const pend = {};
  ws.addEventListener('message', (m) => { const d = JSON.parse(m.data); if (d.id && pend[d.id]) pend[d.id](d);
    if (d.method === 'Runtime.consoleAPICalled') console.log('console', d.params.type, d.params.args.map((a) => a.value || a.description).join(' ').slice(0, 1500));
    if (d.method === 'Runtime.exceptionThrown') console.log('exception', JSON.stringify(d.params.exceptionDetails).slice(0, 800));
    if (d.method === 'Log.entryAdded') console.log('log', d.params.entry.level, d.params.entry.text.slice(0, 1500)); });
  const send = (method, params) => new Promise((r) => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
  await send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1100, deviceScaleFactor: 1, mobile: false }); await send('Runtime.enable', {}); await send('Log.enable', {});
  await send('Page.navigate', { url });
  await sleep(wait);
  if (process.env.CLEAN) { await send('Runtime.evaluate', { expression: "for (const id of ['outlines','carview']) { const e = document.getElementById(id); if (e && e.checked) e.click(); }" }); await sleep(2500); }
  const r = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(out, Buffer.from(r.result.data, 'base64'));
  ws.close(); ch.kill();
  process.exit(0);
})().catch((e) => { console.error(e); ch.kill(); process.exit(1); });
