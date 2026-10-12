#!/usr/bin/env node
// Stage 2-3: classes and selected cases (pointers for exp/econ-principles/film.js) from .cache/econ-principles.
// usage: node exp/econ-principles/cases.js [--top top-all] [--per 2]
// Selection rule: inside each class, the cases with the smallest FNV hash of "<key>|<round>|<id>" (deterministic, blind to
// the outcome). Classes:
//   E4-top: one-step rams (B3: mover length <= 4, adjacent enemy head) by top winners (W) and losers (L), split by the
//     view difference d3 (>= +1 / 0 / <= -1) and the radius-8 difference d8 (>= +1 / <= -1).
//   E4-ours: every ram4 ram of cand-stack1-online (the primary sample) is listed.
//   E7: kings of length >= 15 killed head-on by an attacker of length <= 4 at r >= 350 on round-500 maps (W or L king).
'use strict';
const fs = require('fs'), path = require('path'), readline = require('readline');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'econ-principles');
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const PER = +opt('per', 2);
const ELIM = new Set(['Devil', 'Trophy', 'Prisoners Dilemma', 'Queen Of Spades', 'Default']);
function hash32(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
const cls = {}; const put = (c, x) => { (cls[c] = cls[c] || []).push(x); };
async function read(f, src) {
  if (!fs.existsSync(f)) return;
  const rl = readline.createInterface({ input: fs.createReadStream(f), crlfDelay: Infinity });
  for await (const line of rl) {
    if (!line.trim()) continue; let g; try { g = JSON.parse(line); } catch { continue; }
    const role = t => src === 'top' ? (!g.winner ? 'D' : (g.winner === 'A' ? 0 : 1) === t ? 'W' : 'L') : (g.us === (t ? 'B' : 'A') ? 'U' : 'X');
    for (const o of g.O) {
      if (o[18] !== 1 || o[2] > 4 || o[24] < 0) continue;
      const c = g.C[o[24]], rl = role(o[1]);
      const d3 = o[8] - o[9], d8 = o[12] - o[13];
      const x = { key: g.key, map: g.map, r: o[0], id: o[22], team: o[1] ? 'B' : 'A', L: o[2], Le: o[3], d3, d8, own20: c[29], opp20: c[32], drops: Math.ceil(o[2] / 2) + Math.ceil(o[3] / 2), tag: o[21], h: hash32(g.key + '|' + o[0] + '|' + o[22]) };
      if (src === 'top' && (rl === 'W' || rl === 'L')) put(`E4-top ${rl} d3${d3 >= 1 ? '≥+1' : d3 === 0 ? '=0' : '≤−1'} d8${d8 >= 1 ? '≥+1' : '≤0'}`, x);
      if (src !== 'top' && g.set === 'cand-stack1-online' && o[21] >= 2 && o[21] <= 4) put('E4-ours stack1 ram4', x);
    }
    if (src === 'top' && !ELIM.has(g.map)) for (const k of g.KD) {
      if (k[2] < 15 || k[0] < 350 || !(k[3] === 2 || k[3] === 3) || k[4] > 4) continue;
      put(`E7 king≥15 head-on by L≤4 r≥350 (${role(k[1])} king)`, { key: g.key, map: g.map, r: k[0], id: 'K' + (k[1] ? 'B' : 'A'), team: k[1] ? 'B' : 'A', L: k[2], Le: k[4], k3: k[6], own20: k[16], opp20: k[19], kd0: k[24], kd20: k[23], h: hash32(g.key + '|' + k[0]) });
    }
  }
}
async function main() {
  await read(path.join(CACHE, opt('top', 'top-all') + '.jsonl'), 'top');
  await read(path.join(CACHE, 'online-cand-stack1-online.jsonl'), 'ours');
  for (const [c, xs] of Object.entries(cls).sort()) {
    const own = xs.reduce((s, x) => s + (x.own20 || 0), 0), opp = xs.reduce((s, x) => s + (x.opp20 || 0), 0), dr = xs.reduce((s, x) => s + (x.drops || 0), 0);
    console.log(`## ${c}: class size ${xs.length}${dr ? `; drops eaten <=20R own ${(100 * own / dr).toFixed(0)}% / enemy ${(100 * opp / dr).toFixed(0)}%` : ''}`);
    const pick = c.startsWith('E4-ours') ? xs : xs.slice().sort((a, b) => a.h - b.h).slice(0, PER);
    for (const x of pick) console.log(`  node exp/econ-principles/film.js ${x.key} ${x.r} ${x.id}   # ${x.map} team ${x.team} L${x.L} vs L${x.Le}${x.d3 !== undefined ? ` d3=${x.d3} d8=${x.d8}` : ''}${x.k3 !== undefined ? ` attacker-team heads within 3: ${x.k3}, kd0 ${x.kd0} kd20 ${x.kd20}` : ''} own20 ${x.own20} opp20 ${x.opp20}`);
  }
}
main().catch(e => { console.error(e); process.exit(1); });
