// first round where a candidate game differs from the paired baseline game (same opp/map/side/seed), per map
// usage: node diverge.js <cand eval dir> <base eval dir> [map filter]
const path = require('path'), fs = require('fs');
const HR = '~/01. Project/개인 프로젝트/unsw-heuristic';
const { load } = require(path.join(HR, 'tools/replay.js'));
const [cdir, bdir, mf] = process.argv.slice(2);
const J = e => JSON.stringify(e, (k, v) => typeof v === 'bigint' ? String(v) : v);
const rows = d => new Map(fs.readFileSync(d + '/rows.jsonl', 'utf8').trim().split('\n').map(l => JSON.parse(l)).map(r => [r.key, r]));
const C = rows(cdir), B = rows(bdir);
const out = [];
for (const g of fs.readdirSync(cdir + '/games').sort()) {
  if (mf && !g.includes(mf)) continue;
  const bf = bdir + '/games/' + g + '/game.replay'; if (!fs.existsSync(bf)) continue;
  const a = load(cdir + '/games/' + g + '/game.replay').events, b = load(bf).events;
  let round = 0, div = null;
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    if (a[i] && a[i].type === 'roundStart') round = a[i].round;
    if (J(a[i]) !== J(b[i])) { div = round; break; }
  }
  const key = g.replace(/_(A|B)_(\d)$/, ':$1:$2').replace(/^(archetype_hunter|archetype_swarm|replay_rules_v8|h2)_/, '$1:');
  const c = [...C.values()].find(r => r.key.replace(/:/g, '_') === g), bb = [...B.values()].find(r => r.key.replace(/:/g, '_') === g);
  out.push(`${g.padEnd(38)} diverge r${div === null ? '-' : div}  G ${bb ? bb.G : '?'} -> ${c ? c.G : '?'}`);
}
console.log(out.join('\n'));
