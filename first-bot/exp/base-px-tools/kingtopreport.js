'use strict';
const fs = require('fs');
const rows = fs.readFileSync(__dirname + '/cache/king-top.jsonl', 'utf8').split('\n').filter(Boolean).map(JSON.parse);
const byKey = new Map(); for (const r of rows) { if (!byKey.has(r.key)) byKey.set(r.key, []); byKey.get(r.key).push(r); }
const S = [];
for (const [k, rs] of byKey) { if (rs.some(r => r.name === 'SSS' && r.splitsSelf < 10)) continue; for (const r of rs) if (r.name !== "SSS") S.push({ ...r.us, name: r.name, map: r.map }); }
const sum = a => a.reduce((x, y) => x + y, 0), mean = a => a.length ? sum(a) / a.length : NaN;
const med = a => { if (!a.length) return NaN; const s = a.slice().sort((x, y) => x - y); const m = (s.length - 1) / 2; return (s[Math.floor(m)] + s[Math.ceil(m)]) / 2; };
const f1 = x => Number.isNaN(x) ? '-' : x.toFixed(2), pc = x => Number.isNaN(x) ? '-' : (100 * x).toFixed(1) + '%';
const curve = (X, r) => med(X.filter(x => x.rounds > r || (r === 500 && x.rounds >= 500)).map(x => x.tl[r / 10][2]));
function line(name, X) {
  const n = X.length;
  const bd = {}; for (const x of X) for (const [k, v] of Object.entries(x.bigDeaths)) bd[k] = (bd[k] || 0) + v;
  const bds = Object.entries(bd).sort((a, b) => b[1] - a[1]).map(([m, v]) => `${m} ${(v / n).toFixed(2)}`).join(', ');
  let dv3 = 0, dv4 = 0, e3 = 0, e4 = 0; for (const x of X) { dv3 += (x.dietBy[3].vol || 0); dv4 += (x.dietBy[4].vol || 0); e3 += sum(x.kingEat[3]); e4 += sum(x.kingEat[4]); }
  const vd = sum(X.map(x => x.volDrop));
  console.log(`| ${name} | ${n} | ${curve(X, 300)} | ${curve(X, 400)} | ${curve(X, 450)} | ${curve(X, 500)} | ${f1(sum(X.map(x => x.kingStubsLate)) / n)} | ${f1(sum(X.map(x => x.bigStubsLate)) / n)} | ${f1(sum(X.map(x => x.kingDeathsLate.length)) / n)} | ${bds} | ${f1((e3 + e4) / n)} | ${pc((dv3 + dv4) / (e3 + e4))} | ${pc(dv4 / e4)} | ${f1(sum(X.map(x => x.vol)) / n)} | ${pc(sum(X.map(x => x.volKing20)) / vd)} | ${pc(sum(X.map(x => x.volL20)) / vd)} | ${pc(sum(X.map(x => x.volOwn20)) / vd)} | ${f1(sum(X.map(x => x.trapN)) / n)} (${f1(sum(X.map(x => x.trapLen)) / n)}) |`);
}
console.log('| group | sides | L300 | L400 | L450 | L500 | king stubs r250+/side | big stubs r250+ | king deaths r250+ | L>=8 deaths/side | king eat r300+ | diet vol r300+ | r400+ | vol r250+ | vol->king@death 20r | ->longest 20r | ->own 20r | trapped/side (len) |');
console.log('|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---|');
line('all top', S);
const full = S.filter(x => x.rounds >= 500);
line('500-round games', full);
line('500-round winners', full.filter(x => x.win === 1));
line('500-round losers', full.filter(x => x.win === 0));
line('K teams', S.filter(x => x.name === 'Kamikaze' || x.name === '中国必须人能飞😡'));
line('K 500-round', full.filter(x => x.name === 'Kamikaze' || x.name === '中国必须人能飞😡'));
line('cheji bt', S.filter(x => x.name === 'cheji bt'));
line('cheji 500-round', full.filter(x => x.name === 'cheji bt'));
for (const m of ['trauma', 'slithery_fight', 'schooltime', 'portals', 'autarky', 'default']) line('500w ' + m, full.filter(x => x.win === 1 && x.map === m));
