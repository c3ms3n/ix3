'use strict';
/**
 * page_preview.js - draws the app's centre-screen page (shared/page.js) to PNG files without a car or the bench, so it can be looked at in a browser:
 *   node tools/preview/page_preview.js          -> tools/preview/out/page-<tab>.png and index.html
 * The hud and the head unit are stubs (a Proxy that answers harmlessly); only the drawing is real.
 */
const fs = require('fs');
const path = require('path');
// the app's JavaScript expects shared/*.js and the kit runtime side by side (as the build lays them out): copy them to a temporary folder
const root = path.join(__dirname, '..', '..');
const stage = path.join(require('os').tmpdir(), 'ix3-page-preview');
fs.rmSync(stage, { recursive: true, force: true });
fs.mkdirSync(stage, { recursive: true });
fs.readdirSync(path.join(root, 'shared')).filter((n) => n.endsWith('.js')).forEach((n) => fs.copyFileSync(path.join(root, 'shared', n), path.join(stage, n)));
fs.cpSync(path.join(root, 'kit', 'runtime'), path.join(stage, 'kit'), { recursive: true });
// the theme pictures: previews.js reads them from the packed hud data on the car; here straight from the json files
const zlib = require('zlib');
const pics = [];
fs.writeFileSync(path.join(stage, 'previews.js'), `'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib');
const dir = ${JSON.stringify(path.join(root, 'apps', 'ix3_themes', 'hud', 'previews'))};
const cache = {};
module.exports = { get(name, size) {
    const k = name + ':' + size;
    if (k in cache) return cache[k];
    let out = null;
    try {
        const p = JSON.parse(fs.readFileSync(path.join(dir, name + '.json'), 'utf8'))[size];
        const px = zlib.inflateSync(Buffer.from(p.z, 'base64'));
        global.__pics = global.__pics || [];
        global.__pics.push({ w: p.w, h: p.h, px });
        out = { id: global.__pics.length - 1, w: p.w, h: p.h };
    } catch (e) { out = null; }
    cache[k] = out; return out;
} };
`);
const { Canvas } = require(path.join(stage, 'kit', 'canvas'));
const themes = require(path.join(stage, 'kit', 'themes'));
const Page = require(path.join(stage, 'page'));

const spec = JSON.parse(fs.readFileSync(path.join(root, 'apps', 'ix3_themes', 'app.json'), 'utf8'));
const store = {};
spec.settings.forEach((s) => { store[s.key] = s.default; });
store.hudLayout = 'apex'; store.units = 'metric'; store.mapInTheme = true;
const quiet = (target) => new Proxy(target, {
    get(t, k) {
        if (k in t) return t[k];
        if (k === 'then') return undefined;
        return typeof k === 'symbol' ? undefined : (() => quiet(function () {}));
    },
    apply() { return quiet(function () {}); },
});
let last = null;
const seen = new Set();
const ctx = {
    spec,
    canvas: (w, h) => { const c = new Canvas(w, h); if (process.env.COLLECT) { const t0 = c.text.bind(c); c.text = (str, ...a) => { seen.add(String(str)); return t0(str, ...a); }; } c.target = function () { return c; }; c.pointer = null; c.image = (id, x, y, w, h) => { const p = global.__pics[id]; if (p) c.drawImage(p.px, p.w, p.h, x, y, w, h); }; return c; },
    theme: () => themes.THEMES.m_tricolour,
    loop: () => ({ stop() {} }),
    ui: { image: (id, cv) => { last = cv; return null; } },
    settings: { get: (k) => store[k], set: (k, v) => { store[k] = v; }, item: (k) => spec.settings.find((s) => s.key === k) || null, onChange() {} },
    log: { info() {}, warn() {}, error() {} },
};
const hud = quiet({
    activeName: 'apex', playDemo() {}, demoPlaying: () => false, demoBlocked: () => null, mapLayout: true,
    setting: (k) => store[k], car: { data: () => ({ demo: false }) },
    waze: { info: () => ({ text: 'Map showing in the theme', up: true, ok: true }) },
    // the real logo lookup on the bench's data folder (put test PNGs in bench/.data/ix3_themes/logos/)
    logos: new (require(path.join(stage, 'logos.js')).Logos)(path.join(root, 'bench', '.data', 'ix3_themes'), { info() {}, warn() {} }),
});
const outDir = path.join(__dirname, 'out');
fs.mkdirSync(outDir, { recursive: true });
const tabs = ['look', 'readouts', 'badge', 'map', 'alerts', 'gmeter', 'settings', 'about'];
const langs = process.env.COLLECT ? ['en'] : ['en', 'ckb'];
const shots = [];
langs.forEach((lang) => tabs.forEach((tab) => {
    store.language = lang;
    if (process.env.PREVIEW_BADGE) store.badge = process.env.PREVIEW_BADGE;     // e.g. M340i, to see a logo from the bench's logos folder
    try {
        const p = new Page(ctx, hud, { title: spec.title, what: 'cluster', look: { name: 'Themes', style: 'hero', tags: {} }, tabs, settings: ['units', 'clock', 'timeZone', 'tankLitres', 'redline', 'nightDim'] });
        p.tab = tab;
        // PREVIEW_PICKER=inHybrid[:offset] draws that list open over the Themes tab (and scrolled by offset px)
        if (process.env.PREVIEW_PICKER && tab === 'look') { const [k, off] = process.env.PREVIEW_PICKER.split(':'); p.picker = { key: k, title: k, fmt: (v) => p.layoutName(v) }; if (off) p.picker.off = Number(off); }
        p.render();
        fs.writeFileSync(path.join(outDir, 'page-' + tab + (lang === 'en' ? '' : '-' + lang) + '.png'), last.png(9));
        shots.push(tab + (lang === 'en' ? '' : '-' + lang));
    } catch (e) { console.log('tab ' + tab + ': ' + (e && e.message)); }
}));
fs.writeFileSync(path.join(outDir, 'index.html'), '<!doctype html><meta charset="utf-8"><title>iX3 Themes pages</title><body style="background:#111;color:#ddd;font:14px sans-serif;margin:16px">' +
    '<h2>iX3 Themes: the app\'s centre-screen pages</h2>' + shots.map((t) => '<h3>' + t + '</h3><img src="page-' + t + '.png" style="max-width:100%;border:1px solid #333">').join('') + '</body>');
console.log('drew', shots.join(', '), '->', outDir);
if (process.env.COLLECT) {
    // the strings of the settings and their options too (the page shows them as values and rows)
    spec.settings.forEach((st) => { if (st.label) seen.add(st.label); (st.options || []).forEach((o) => seen.add(o[1])); });
    fs.writeFileSync(path.join(__dirname, 'ckb_strings.json'), JSON.stringify(Array.from(seen).sort(), null, 1));
    console.log('collected', seen.size, 'strings');
}
