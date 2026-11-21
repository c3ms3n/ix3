'use strict';
/**
 * ambient.js - the colour of the car's ambient light, read from the body controller (BDC, 0x40) over the read-only link.
 *
 * The BDC keeps the ambient light's modules on two LIN buses; 22 DA5F (bus 1) and 22 E3D1 (bus 2) answer with 26 records
 * of 10 bytes each (location, blue, green, red, brightness, white, four fault bytes; an empty record has location FF),
 * as the public BDC_G05 description and robertnisipeanu's Ambient config (G20, car-tested) have it. The BDC asks its LIN
 * modules first, so the reply comes seconds after a "response pending". Only reads leave the head unit.
 *
 *   parse(uds)    the lit modules' colours in one reply: [[r, g, b], ...]
 *   pick(colours) the colour most modules show, as [r, g, b] 0-255 (null when the lights are off)
 *   accent(rgb)   what a shader wants: the colour scaled so its largest channel is 1, plus how much it replaces the blues
 */
const BDC = 0x40;
const DIDS = [0xDA5F, 0xE3D1];       // LIN bus 1, bus 2
const RECORD = 10, RECORDS = 26;

function parse(uds, did) {
    const b = Array.prototype.slice.call(uds || []);
    if (b[0] !== 0x62 || ((b[1] << 8) | b[2]) !== did) return null;
    const out = [];
    for (let i = 0; i < RECORDS; i++) {
        const r = b.slice(3 + i * RECORD, 3 + (i + 1) * RECORD);
        if (r.length < RECORD || r[0] === 0xFF) continue;
        const rgb = [r[3], r[2], r[1]];
        if (r[4] > 0 && Math.max.apply(null, rgb) > 0) out.push(rgb);
    }
    return out;
}

function pick(colours) {
    const count = {};
    let best = null;
    (colours || []).forEach((c) => {
        const k = c.join(',');
        count[k] = (count[k] || 0) + 1;
        if (!best || count[k] > count[best.join(',')]) best = c;
    });
    return best;
}

function accent(rgb) {
    if (!rgb) return [1, 1, 1, 0];
    const m = Math.max(rgb[0], rgb[1], rgb[2]);
    if (!(m > 0)) return [1, 1, 1, 0];
    return [rgb[0] / m, rgb[1] / m, rgb[2] / m, 1];
}

/** Both buses through `link` (a ReadOnlyDiag): [r, g, b] of the ambient light, null when off, undefined when unreadable. */
async function read(link) {
    const all = [];
    let answered = false;
    for (const did of DIDS) {
        const uds = await link.read(BDC, did, 15000);
        const got = uds ? parse(uds, did) : null;
        if (got) { answered = true; got.forEach((c) => all.push(c)); }
    }
    return answered ? pick(all) : undefined;
}

module.exports = { BDC, DIDS, parse, pick, accent, read };
