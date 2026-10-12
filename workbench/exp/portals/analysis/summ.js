#!/usr/bin/env node
// Summaries of exp/portals/analysis/ours.js records: node summ.js <a.jsonl> [<b.jsonl> ...] [--seedmin 1] [--kd]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const { FI } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const argv = process.argv.slice(2);
const files = argv.filter(a => a.endsWith('.jsonl'));
const seedMin = (() => { const i = argv.indexOf('--seedmin'); return i >= 0 ? +argv[i + 1] : 1; })();
const q = (xs, p) => { const a = xs.filter(x => x != null && !Number.isNaN(x)).sort((u, v) => u - v); if (!a.length) return null; const i = (a.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return a[lo] + (a[hi] - a[lo]) * (i - lo); };
const mean = xs => { const a = xs.filter(x => x != null && !Number.isNaN(x)); return a.length ? a.reduce((s, x) => s + x, 0) / a.length : null; };
const f1 = x => x == null ? '–' : x.toFixed(1), f2 = x => x == null ? '–' : x.toFixed(2);
const sumB = (arr, a, b) => { let s = 0; for (let i = a; i <= b; i++) s += arr[i] || 0; return s; };
const cols = [];
for (const f of files) {
  const rs = fs.readFileSync(f, 'utf8').trim().split('\n').map(l => JSON.parse(l)).filter(r => r.src !== 'local' || r.seed >= seedMin);
  cols.push({ name: path.basename(f, '.jsonl'), rs });
}
const rows = [];
const add = (label, fn) => rows.push([label, ...cols.map(c => fn(c.rs))]);
add('N', rs => String(rs.length));
add('king500 median [P25-P75] mean', rs => { const k = rs.map(r => r.k500); return `${f1(q(k, .5))} [${f1(q(k, .25))}-${f1(q(k, .75))}] ${f1(mean(k))}`; });
add('king500 P10 / min', rs => { const k = rs.map(r => r.k500); return `${f1(q(k, .1))} / ${Math.min(...k)}`; });
add('conversion k500/total400 (med)', rs => f2(q(rs.map(r => r.total[40] ? r.k500 / r.total[40] : null), .5)));
add('total500 - king500 (med, unconverted)', rs => f1(q(rs.map(r => r.total[50] - r.k500), .5)));
for (const t of [100, 200, 250, 300, 350, 400, 450]) add(`king r${t} med | total mean | units mean`, rs => `${f1(q(rs.map(r => r.king[t / 10]), .5))} | ${f1(mean(rs.map(r => r.total[t / 10])))} | ${f1(mean(rs.map(r => r.units[t / 10])))}`);
add('second r450 / r500 (med)', rs => `${f1(q(rs.map(r => r.second[45]), .5))} / ${f1(q(rs.map(r => r.second[50]), .5))}`);
add('king deaths / game (games with one)', rs => `${f2(mean(rs.map(r => r.kingDeaths.length)))} (${rs.filter(r => r.kingDeaths.length).length})`);
add('king deaths by cause', rs => { const c = {}; for (const r of rs) for (const k of r.kingDeaths) c[k.cause] = (c[k.cause] || 0) + 1; return JSON.stringify(c); });
add('king handoffs / game (after r300)', rs => `${f2(mean(rs.map(r => r.handoffs.length)))} (${f2(mean(rs.map(r => r.handoffs.filter(h => h.r >= 300).length)))})`);
add('handoff tags', rs => { const c = {}; for (const r of rs) for (const h of r.handoffs) { const t = (h.tag.match(/^(\S+)/) || ['', '?'])[1].replace(/\d+/g, ''); c[t] = (c[t] || 0) + 1; } return JSON.stringify(c); });
add('lineage r300: Lt / +nat / +own / -path / transfers', rs => { const C = rs.map(r => r.lin && r.lin.cp && r.lin.cp[300]).filter(Boolean); return `${f1(mean(C.map(c => c.Lt)))} / ${f1(mean(C.map(c => c.eat[0])))} / ${f1(mean(C.map(c => c.eat.slice(1, 6).reduce((a, b) => a + b, 0))))} / ${f1(mean(C.map(c => c.lossPath)))} / ${f1(mean(C.map(c => c.transfers)))}`; });
add('lineage r300: -cost -off', rs => { const C = rs.map(r => r.lin && r.lin.cp && r.lin.cp[300]).filter(Boolean); return `${f1(mean(C.map(c => c.cost)))} ${f1(mean(C.map(c => c.lossOff)))}`; });
for (const [a, b, n] of [[25, 29, 'r250-299'], [30, 34, 'r300-349'], [35, 39, 'r350-399'], [40, 44, 'r400-449'], [45, 49, 'r450-499']]) {
  add(`${n}: sac n/L | trap n/L | king eats nat/own`, rs => `${f1(mean(rs.map(r => sumB(r.fl[FI.dn_sac], a, b))))}/${f1(mean(rs.map(r => sumB(r.fl[FI.dl_sac], a, b))))} | ${f1(mean(rs.map(r => sumB(r.fl[FI.dn_trap], a, b))))}/${f1(mean(rs.map(r => sumB(r.fl[FI.dl_trap], a, b))))} | ${f1(mean(rs.map(r => sumB(r.fl[FI.keat_nat], a, b))))}/${f1(mean(rs.map(r => ['keat_oSac', 'keat_oTrap', 'keat_oRammed', 'keat_oRam', 'keat_oOther'].reduce((s, k) => s + sumB(r.fl[FI[k]], a, b), 0))))}`);
}
add('team nat eats r0-99 / 100-249 / 250-399 / 400-499', rs => [[0, 9], [10, 24], [25, 39], [40, 49]].map(([a, b]) => f1(mean(rs.map(r => sumB(r.fl[FI.eat_nat], a, b))))).join(' / '));
add('splits r0-99 / 100-249 / 250-349 / 350-449 / 450-499', rs => [[0, 9], [10, 24], [25, 34], [35, 44], [45, 49]].map(([a, b]) => f1(mean(rs.map(r => sumB(r.fl[FI.split_n], a, b))))).join(' / '));
add('sprint cost segments (mean)', rs => f1(mean(rs.map(r => ['spr_ram', 'spr_eat', 'spr_esc', 'spr_other'].reduce((s, k) => s + sumB(r.fl[FI[k]], 0, 49), 0)))));
const w = rows.reduce((m, r) => Math.max(m, r[0].length), 0);
for (const r of rows) console.log(r[0].padEnd(w) + ' | ' + r.slice(1).join(' | '));
if (argv.includes('--kd')) for (const c of cols) { console.log(`\n== king deaths ${c.name}`); for (const r of c.rs) for (const k of r.kingDeaths) console.log(`${r.key} r${k.r} ${k.cause} L${k.len} free ${k.free} core ${k.inCore} mech ${k.mech} near ${k.near} blk ${k.blk} other ${k.otherLen}${k.otherTeam || ''} | ${k.tag}`); }
