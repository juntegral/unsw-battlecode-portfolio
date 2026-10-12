'use strict';
const fs = require('fs');
const file = process.argv[2]; const rows = fs.readFileSync(file, 'utf8').trim().split('\n').map(JSON.parse);
const M500 = ['trauma', 'slithery_fight', 'schooltime', 'portals', 'autarky'];
const sum = a => a.reduce((x, y) => x + y, 0);
const med = a => { if (!a.length) return NaN; const s = a.slice().sort((x, y) => x - y); const m = (s.length - 1) / 2; return (s[Math.floor(m)] + s[Math.ceil(m)]) / 2; };
const curve = (S, r) => med(S.filter(x => x.rounds > r || (r === 500 && x.rounds >= 500)).map(x => x.tl[r / 10][2]));
const ucurve = (S, r) => med(S.filter(x => x.rounds > r || (r === 500 && x.rounds >= 500)).map(x => x.tl[r / 10][0]));
const pc = x => Number.isNaN(x) ? '-' : (100 * x).toFixed(1) + '%';
function line(name, R, key) {
  const S = R.map(r => r[key]); const n = S.length; if (!n) return;
  let dv = 0, e = 0; for (const x of S) { dv += (x.dietBy[3].vol || 0) + (x.dietBy[4].vol || 0); e += sum(x.kingEat[3]) + sum(x.kingEat[4]); }
  const bd = {}; for (const x of S) for (const [k, v] of Object.entries(x.bigDeaths)) bd[k] = (bd[k] || 0) + v;
  const vd = sum(S.map(x => x.volDrop));
  console.log(`| ${name} | ${n} | ${S.filter(x => x.win === 1).length} | ${curve(S, 300)} | ${curve(S, 350)} | ${curve(S, 400)} | ${curve(S, 450)} | ${curve(S, 500)} | ${ucurve(S, 300)} | ${ucurve(S, 400)} | ${(e / n).toFixed(1)} | ${pc(dv / e)} | ${(sum(S.map(x => x.kingStubsLate)) / n).toFixed(2)} | ${(sum(S.map(x => x.kingDeathsLate.length)) / n).toFixed(2)} | ${Object.entries(bd).sort((a, b) => b[1] - a[1]).map(([k, v]) => k + ' ' + (v / n).toFixed(2)).join(', ')} | ${(sum(S.map(x => x.vol)) / n).toFixed(1)} | ${pc(sum(S.map(x => x.volKing20)) / vd)} |`);
}
console.log('| group | games | wins | L300 | L350 | L400 | L450 | L500 | u300 | u400 | king eat r300+ | diet vol r300+ | king stubs r250+ | king deaths r250+ | L>=8 deaths/g | vol r250+/g | vol->king 20r |');
console.log('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|');
const R5 = rows.filter(r => M500.includes(r.map));
line('us, 500-round maps', R5, 'us'); line('them, 500-round maps', R5, 'them');
for (const m of M500) { const X = R5.filter(r => r.map === m); line('us ' + m, X, 'us'); line('them ' + m, X, 'them'); }
