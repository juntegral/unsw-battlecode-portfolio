// scratch: sprint-bracket games (old rules, 1.1.x): each team's mass concentration. Per game and team: dragons / total / longest share at
// r250..500; drops of the team's own deaths eaten by its longest dragon (at the eat) by round bin; the round its longest first holds >= 50% of
// the team's mass (from r100) and the dragon count then. Grouped by team name.
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = '~/01. Project/개인 프로젝트/unsw-swarm', D = path.join(ROOT, 'data/online/sprint-bracket');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const ML = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const CP = [200, 250, 300, 350, 400, 450, 475], BINS = [[0, 250], [250, 350], [350, 430], [430, 470], [470, 501]];
const byTeam = {};
for (const f of fs.readdirSync(D).filter(f => /^game-\d+\.json$/.test(f))) {
  const g = JSON.parse(fs.readFileSync(path.join(D, f))), id = f.match(/\d+/)[0], rf = path.join(D, 'M' + id + '.replay');
  if (!fs.existsSync(rf)) continue;
  let R; try { R = load(rf); } catch (e) { continue; }
  const names = { A: g.teamAName, B: g.teamBName }, snap = { A: {}, B: {} }, onset = { A: null, B: null }, feed = { A: BINS.map(() => 0), B: BINS.map(() => 0) }, drops = { A: BINS.map(() => 0), B: BINS.map(() => 0) };
  const recs = new Map(); let lastR = -1;
  try {
    ML.perGame(R, { map: g.mapName, variant: '?', rules: '110' }, {
      turn(d, r, c) {
        if (r === lastR) return; lastR = r;
        for (const t of ['A', 'B']) {
          let n = 0, tot = 0, lo = 0; for (const o of c.drag.values()) if (o.team === t) { n++; tot += o.body.length; lo = Math.max(lo, o.body.length); }
          if (CP.includes(r)) snap[t][r] = { n, tot, share: tot ? lo / tot : 0, lo };
          if (r >= 100 && onset[t] === null && n >= 2 && tot && lo / tot >= 0.5) onset[t] = { r, n };
        }
      },
      death(d, rec, idx, other, r) { const b = BINS.findIndex(([a, z]) => r >= a && r < z); recs.set(idx, { team: d.team, b }); drops[d.team][b] += rec.drops; },
      eat(d, tile, idx, r, c) {
        const x = recs.get(idx); if (!x || d.team !== x.team) return;
        let lo = null; for (const o of c.drag.values()) if (o.team === d.team && (!lo || o.body.length > lo.body.length)) lo = o;
        if (lo && lo.id === d.id) feed[x.team][x.b]++;
      },
      end(n, c) { for (const t of ['A', 'B']) { let k = 0, tot = 0, lo = 0; for (const o of c.drag.values()) if (o.team === t) { k++; tot += o.body.length; lo = Math.max(lo, o.body.length); } snap[t].end = { n: k, tot, share: tot ? lo / tot : 0, lo }; } },
    });
  } catch (e) { continue; }
  for (const t of ['A', 'B']) {
    const T = byTeam[names[t]] = byTeam[names[t]] || { games: 0, wins: 0, snaps: [], onsets: [], feed: BINS.map(() => 0), drops: BINS.map(() => 0) };
    T.games++; if (g.winner && g.winner.toUpperCase() === t) T.wins++;
    T.snaps.push(snap[t]); T.onsets.push(onset[t]);
    feed[t].forEach((v, i) => T.feed[i] += v); drops[t].forEach((v, i) => T.drops[i] += v);
  }
}
const med = a => { const s = a.filter(x => x !== undefined && x !== null).sort((x, y) => x - y); return s.length ? s[Math.floor(s.length / 2)] : '-'; };
const rows = Object.entries(byTeam).filter(([, T]) => T.games >= 7).sort((a, b) => b[1].games - a[1].games || b[1].wins - a[1].wins);
console.log('team | games W | longest share r200/250/300/350/400/450/475/end (median) | dragons r300/400/450/end | onset (longest >= 50%) median round, dragons then, never | own-death drops eaten by the longest: <250 / 250-349 / 350-429 / 430-469 / 470+');
for (const [name, T] of rows) {
  const sh = CP.concat(['end']).map(r => { const v = med(T.snaps.map(s => s[r] ? s[r].share : undefined)); return v === '-' ? '-' : (100 * v).toFixed(0); }).join('/');
  const dn = [300, 400, 450, 'end'].map(r => med(T.snaps.map(s => s[r] ? s[r].n : undefined))).join('/');
  const on = T.onsets.filter(Boolean);
  const fd = T.feed.map((v, i) => `${v}/${T.drops[i]}`).join(' ');
  const lo = med(T.snaps.map(s => s.end ? s.end.lo : undefined)), to = med(T.snaps.map(s => s.end ? s.end.tot : undefined));
  console.log(`${name.slice(0, 22).padEnd(22)} | ${T.games} ${T.wins} | ${sh} | ${dn} | end longest ${lo} total ${to} | r${med(on.map(o => o.r))} n${med(on.map(o => o.n))} never ${T.onsets.length - on.length} | ${fd}`);
}
