// per map from local_report caches (analysis.jsonl): games, wins, natural intake us/them, final longest, trap / rammed+ram / ally head-on deaths, eliminations
const fs = require('fs');
for (const dir of process.argv.slice(2)) {
  const G = fs.readFileSync(dir + '/analysis.jsonl', 'utf8').trim().split('\n').map(JSON.parse);
  const by = {};
  for (const g of G) { const b = by[g.file] || (by[g.file] = []); b.push(g); }
  for (const [m, a] of Object.entries(by).sort()) {
    const s = f => a.reduce((x, g) => x + f(g), 0);
    console.log(`${dir.split('/').pop()} ${m}: n ${a.length}, wins ${s(g => g.won)}, intake ${s(g => g.nat[0])}/${s(g => g.nat[1])}, longest ${(s(g => g.king[0]) / a.length).toFixed(1)}, trap ${s(g => g.dt.trap || 0)}, head-on enemy ${s(g => (g.dt.rammed || 0) + (g.dt.ram || 0))}, ally head-on ${s(g => g.dt.allyHead || 0)}, elim ${s(g => g.elim)}`);
  }
}
