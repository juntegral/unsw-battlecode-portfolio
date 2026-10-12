// crossing-level 3-round body failure by probe kind of the previous round, exit kind and desperation (label v <= -20)
const fs = require('fs'); const games = [].concat(...process.argv.slice(2).map(f => JSON.parse(fs.readFileSync(f, 'utf8'))));
const m = new Map(); const add = (k, f, own) => { const o = m.get(k) || [0, 0, 0]; o[0]++; o[1] += f; o[2] += own; m.set(k, o); };
for (const g of games) { const ca = new Map(g.X.cross.map(c => [c.id + ':' + c.r, c]));
  for (const x of g.recs.filter(y => y.k === 'portal')) { const c = ca.get(x.id + ':' + x.r); if (!c) continue;
    const fail = x.alive3 ? 0 : 1, own = c.fate && c.fate.hitTeam === 'us' && c.fate.step === c.stepI ? 1 : 0;
    const desp = x.v !== null && x.v <= -20 ? 'desperate' : 'not desperate';
    add(`${x.blind ? 'PORTAL?' : 'known  '} | probe ${(c.probe || '?').padEnd(16)} | ${desp}`, fail, own); } }
console.log('crossings: exit kind | previous-round probe | label v  ->  N, body dead within 3 (rate), own-blocked on the exit tile');
for (const [k, o] of [...m.entries()].sort((a, b) => b[1][0] - a[1][0])) console.log(`  ${k.padEnd(60)} ${String(o[0]).padStart(5)}  ${String(o[1]).padStart(4)} (${(100 * o[1] / o[0]).toFixed(1)}%)  own ${o[2]}`);
