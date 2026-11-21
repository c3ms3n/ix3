'use strict';
// shared/ambient.js: the ambient light's colour from the body controller's status reply.
//   node tools/test_ambient.js
const assert = require('assert');
const A = require('../shared/ambient');

// 62 DA 5F, 26 records of 10 bytes (location, blue, green, red, brightness, white, 4 faults); an empty one is FF
const reply = (did, recs) => {
    const b = [0x62, did >> 8, did & 0xFF];
    for (let i = 0; i < 26; i++) b.push.apply(b, recs[i] || [0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 3, 7, 7, 7, 7]);
    return b.concat([2]);
};
const lit = (loc, r, g, bl, bright) => [loc, bl, g, r, bright, 0, 0, 0, 0, 0];

const orange = reply(0xDA5F, [lit(0x0F, 255, 110, 0, 100), lit(0x0E, 255, 110, 0, 100), lit(0x01, 0, 0, 255, 100)]);
assert.deepStrictEqual(A.parse(orange, 0xDA5F), [[255, 110, 0], [255, 110, 0], [0, 0, 255]], 'colours are read red, green, blue');
assert.deepStrictEqual(A.pick(A.parse(orange, 0xDA5F)), [255, 110, 0], 'the colour most modules show');

assert.deepStrictEqual(A.parse(reply(0xDA5F, [lit(0x0F, 255, 0, 0, 0), lit(0x0E, 0, 0, 0, 100)]), 0xDA5F), [], 'off or black is no colour');
assert.strictEqual(A.parse([0x7F, 0x22, 0x31], 0xDA5F), null, 'a refusal is not a status');
assert.strictEqual(A.parse(reply(0xE3D1, [lit(1, 1, 2, 3, 50)]), 0xDA5F), null, 'the other bus\'s reply is not this one\'s');
assert.strictEqual(A.pick([]), null);

assert.deepStrictEqual(A.accent([255, 110, 0]), [1, 110 / 255, 0, 1], 'scaled so the largest channel is 1');
assert.deepStrictEqual(A.accent([40, 20, 10]), [1, 0.5, 0.25, 1]);
assert.strictEqual(A.accent(null)[3], 0, 'no colour: the blues as drawn');

// read() asks both buses and takes the colour of what answered; undefined when neither does
const link = (answers) => ({ read: async (ecu, did) => { assert.strictEqual(ecu, 0x40); return answers[did] || null; } });
(async () => {
    assert.deepStrictEqual(await A.read(link({ 0xE3D1: reply(0xE3D1, [lit(0x15, 10, 200, 30, 100)]) })), [10, 200, 30]);
    assert.strictEqual(await A.read(link({})), undefined, 'the unit gave nothing');
    assert.strictEqual(await A.read(link({ 0xDA5F: reply(0xDA5F, []) })), null, 'answered, lights off');
    console.log('ambient ok');
})().catch((e) => { console.error(e); process.exit(1); });
