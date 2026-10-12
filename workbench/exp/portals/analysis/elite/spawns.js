#!/usr/bin/env node
// Harvest check for elite.js: natural spawns in a team's own territory (mass-ledger gf spawn_A / spawn_B by territory; a spawn succeeds
// only on an empty tile, so a pearl left lying stops its tile) and the team's natural eats, per 50-round window, by band. Same cache,
// bands and stall rule as elite.js. Ours: W0-W12 Portals games.
'use strict';
const fs = require('fs'), path = require('path'), readline = require('readline');
const ROOT = path.resolve(__dirname, '../../../..');
const { FI } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const TH = { p25: 26, p40: 31, p60: 37, p90: 51 };
const WAVES = ['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3', 'cand-stack1-online', 'cand-stack2-online', 'cand-stack3-online', 'cand-stack4-online',
  'cand-stack5-online', 'cand-stack6-online', 'cand-stack6-online-r2', 'cand-stack7-online', 'cand-stack8-online', 'cand-stack9-online', 'cand-stack10-online', 'cand-stack11-online'];
const era = s => { const i = WAVES.indexOf(s); return i <= 6 ? 'ours W0-W4' : i <= 11 ? 'ours W5-W9' : 'ours W10-W12'; };
const sb = (a, x, y) => { let s = 0; for (let i = x; i <= y; i++) s += a[i]; return s; };
const WIN = [[0, 9, 'r0-99'], [10, 19, 'r100-199'], [20, 24, 'r200-249'], [25, 29, 'r250-299'], [30, 34, 'r300-349'], [35, 39, 'r350-399'], [40, 44, 'r400-449'], [45, 49, 'r450-499']];
const acc = {};
const add = (band, g, tm) => {
  const a = acc[band] = acc[band] || { n: 0, sp: WIN.map(() => 0), fsp: WIN.map(() => 0), nat: WIN.map(() => 0) };
  a.n++;
  const own = tm === 'A' ? 0 : 1;
  WIN.forEach(([x, y], i) => { a.sp[i] += sb(g.gf[own], x, y); a.fsp[i] += sb(g.gf[3 + own], x, y); a.nat[i] += sb(g[tm].fl[FI.eat_nat], x, y); });
};
(async () => {
  const rl = readline.createInterface({ input: fs.createReadStream(path.join(ROOT, '.cache/mass-ledger/top-sample.jsonl')), crlfDelay: Infinity });
  for await (const l of rl) {
    if (!l.includes('"map":"Portals"')) continue;
    const g = JSON.parse(l); if (g.map !== 'Portals') continue;
    const st = tm => g.rounds >= 100 && g[tm].sonar === 0 && g[tm].splits <= 3;
    if (st('A') || st('B')) continue;
    for (const tm of ['A', 'B']) {
      const k = g[tm].st.king[50];
      add('all elite', g, tm);
      if (k >= TH.p90) add('top decile', g, tm); else if (k >= TH.p40 && k <= TH.p60) add('median band', g, tm); else if (k <= TH.p25) add('bottom quartile', g, tm);
    }
  }
  for (const s of WAVES) {
    const f = path.join(ROOT, '.cache/mass-ledger/online-' + s + '.jsonl');
    for (const l of fs.readFileSync(f, 'utf8').split('\n')) { if (!l.includes('"map":"Portals"')) continue; const g = JSON.parse(l); if (g.map === 'Portals' && g.us) add(era(s), g, g.us); }
  }
  console.log('own-territory natural spawns / of them on fountain tiles (gap mean <= 12) / team natural eats, per game (mean), by window');
  console.log('band [N] | ' + WIN.map(w => w[2]).join(' | '));
  for (const [b, a] of Object.entries(acc)) console.log(`${b} [${a.n}] | ` + WIN.map((w, i) => `${(a.sp[i] / a.n).toFixed(1)}/${(a.fsp[i] / a.n).toFixed(1)}/${(a.nat[i] / a.n).toFixed(1)}`).join(' | '));
})();
