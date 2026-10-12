#!/usr/bin/env node
// Aggregate kingstat caches. usage: node kingreport.js --labels a,b [--side us|them] [--maps m1,m2] [--by map]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = require('path').resolve(__dirname, '..', '..');
const SCR = require('path').join(__dirname, 'cache');
const cacheFile = L => L.startsWith('base-px') ? path.join(ROOT, 'exp', L, 'king.jsonl') : path.join(SCR, 'king-' + L + '.jsonl');
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const labels = String(arg('labels', '')).split(',').filter(Boolean);
const sideKey = arg('side', 'us');
const mapsF = arg('maps') ? new Set(arg('maps').split(',')) : null;
const oppsF = arg('opps') ? new Set(arg('opps').split(',')) : null;
const by = arg('by', 'opp');
const readJsonl = f => fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(Boolean).map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean) : [];
const sum = a => a.reduce((x, y) => x + y, 0), mean = a => a.length ? sum(a) / a.length : NaN;
const med = a => { if (!a.length) return NaN; const s = a.slice().sort((x, y) => x - y); const m = (s.length - 1) / 2; return (s[Math.floor(m)] + s[Math.ceil(m)]) / 2; };
const f1 = x => Number.isNaN(x) || x === null || x === undefined ? '-' : Math.abs(x) >= 100 ? x.toFixed(0) : x.toFixed(1);
const pc = x => Number.isNaN(x) || x === null ? '-' : (100 * x).toFixed(1) + '%';
const curve = (S, r) => med(S.filter(x => x.rounds > r || (r === 500 && x.rounds >= 500)).map(x => x.tl[r / 10][2]));
function stats(rows) {
  const S = rows.map(r => r[sideKey]);
  const n = S.length;
  const o = { n, win: mean(S.map(x => x.win === 1 ? 1 : 0)), G: mean(S.map(x => x.final[0] > 0 ? x.final[1] : 0)) };
  o.L300 = curve(S, 300); o.L400 = curve(S, 400); o.L450 = curve(S, 450); o.L500 = curve(S, 500);
  const full = S.filter(x => x.rounds >= 500);
  o.full = full.length; o.finalL500 = med(full.map(x => x.final[1]));
  o.kingStubsLate = sum(S.map(x => x.kingStubsLate)) / n; o.bigStubsLate = sum(S.map(x => x.bigStubsLate)) / n;
  const bd = {}; for (const x of S) for (const [k, v] of Object.entries(x.bigDeaths)) bd[k] = (bd[k] || 0) + v;
  o.bigDeaths = Object.fromEntries(Object.entries(bd).map(([k, v]) => [k, v / n]));
  o.kingDeathsLate = sum(S.map(x => x.kingDeathsLate.length)) / n;
  // king diet r300+: windows 3 and 4
  let kn = 0, ks = 0, kall = 0; for (const x of S) for (const w of [3, 4]) { const e = x.kingEat[w]; kn += e[0]; ks += e[1]; kall += e[0] + e[1] + e[2] + e[3]; }
  o.kingEat300 = kall / n; o.kingSacShare = kall ? ks / kall : NaN;
  let k4 = 0, k4s = 0; for (const x of S) { const e = x.kingEat[4]; k4 += e[0] + e[1] + e[2] + e[3]; k4s += e[1]; }
  o.kingEat400 = k4 / n; o.kingSacShare400 = k4 ? k4s / k4 : NaN;
  const sacDrop = sum(S.map(x => x.sacDrop));
  o.sac = sum(S.map(x => x.sac)) / n; o.sacKing20 = sacDrop ? sum(S.map(x => x.sacKing20)) / sacDrop : NaN; o.sacOwn20 = sacDrop ? sum(S.map(x => x.sacOwn20)) / sacDrop : NaN;
  o.sacKingAny = sacDrop ? sum(S.map(x => x.sacKingAny)) / sacDrop : NaN;
  // diet from voluntary own deaths (self-kill, kelp/own body with a free exit, into an ally with a free exit)
  let dv3 = 0, dv4 = 0, e3 = 0, e4 = 0; for (const x of S) { dv3 += (x.dietBy[3].vol || 0); dv4 += (x.dietBy[4].vol || 0); e3 += sum(x.kingEat[3]); e4 += sum(x.kingEat[4]); }
  o.dietVol300 = (e3 + e4) ? (dv3 + dv4) / (e3 + e4) : NaN; o.dietVol400 = e4 ? dv4 / e4 : NaN;
  const vd = sum(S.map(x => x.volDrop)); o.vol = sum(S.map(x => x.vol)) / n; o.volKing20 = vd ? sum(S.map(x => x.volKing20)) / vd : NaN; o.volL20 = vd ? sum(S.map(x => x.volL20)) / vd : NaN; o.volOwn20 = vd ? sum(S.map(x => x.volOwn20)) / vd : NaN;
  o.trapN = sum(S.map(x => x.trapN)) / n; o.trapLen = sum(S.map(x => x.trapLen)) / n;
  o.units300 = med(S.filter(x => x.rounds > 300).map(x => x.tl[30][0])); o.units400 = med(S.filter(x => x.rounds > 400).map(x => x.tl[40][0]));
  o.total500 = med(full.map(x => x.final[2]));
  return o;
}
const rows = []; for (const L of labels) for (const r of readJsonl(cacheFile(L))) if ((!mapsF || mapsF.has(r.map)) && (!oppsF || oppsF.has(r.opp))) rows.push({ ...r, label: L });
const groups = new Map();
for (const r of rows) { const k = r.label + ' | ' + (by === 'map' ? r.map : by === 'oppmap' ? r.opp + ' ' + r.map : r.opp); if (!groups.has(k)) groups.set(k, []); groups.get(k).push(r); }
for (const L of labels) { const k = L + ' | (all)'; groups.set(k, rows.filter(r => r.label === L)); }
console.log(`side: ${sideKey}`);
console.log('| label | group | n | win | G | L300 | L400 | L450 | L500 | final L (500g) | u300 | u400 | king stubs r250+/g | big stubs r250+/g | king deaths r250+/g | L>=8 deaths/g (mode) | king eat r300+/g | diet vol r300+ | r400+ | vol r250+/g | vol pearls->king@death 20r | ->longest 20r | ->own 20r | trapped deaths/g (len) |');
console.log('|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|');
for (const [k, rs] of [...groups.entries()].sort()) {
  if (!rs.length) continue;
  const o = stats(rs); const [L, g] = k.split(' | ');
  const bd = Object.entries(o.bigDeaths).sort((a, b) => b[1] - a[1]).map(([m, v]) => `${m} ${v.toFixed(2)}`).join(', ');
  console.log(`| ${L} | ${g} | ${o.n} | ${pc(o.win)} | ${f1(o.G)} | ${f1(o.L300)} | ${f1(o.L400)} | ${f1(o.L450)} | ${f1(o.L500)} | ${f1(o.finalL500)} (${o.full}) | ${f1(o.units300)} | ${f1(o.units400)} | ${o.kingStubsLate.toFixed(2)} | ${o.bigStubsLate.toFixed(2)} | ${o.kingDeathsLate.toFixed(2)} | ${bd} | ${f1(o.kingEat300)} | ${pc(o.dietVol300)} | ${pc(o.dietVol400)} | ${f1(o.vol)} | ${pc(o.volKing20)} | ${pc(o.volL20)} | ${pc(o.volOwn20)} | ${f1(o.trapN)} (${f1(o.trapLen)}) |`);
}
