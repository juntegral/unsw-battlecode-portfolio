#!/usr/bin/env node
// Q2 (queen rules, engine 1.2.3): per game, both queens (id 0 = team A's, id 1 = team B's): length at r50 / 100 / 200 / 300 / 400 / end,
// death round and cause (mass_ledger causes: rammed = an enemy head moved into ours, ram = ours moved into an enemy head, enemyBody,
// trap = wall / own body / no valid action, sac / allyHead = into our own team), and the other dragon (its team, length, whether a queen).
// usage: node exp/q2/queenstat.js <runq set dir>... [--games]   (the set's rows.jsonl gives side and result)
'use strict';
process.env.UNSW_RULES = process.env.UNSW_RULES || '123';   // 1.2.3 replays (tools/mass_ledger.js step simulation)
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const SHOW = process.argv.includes('--games');
const CP = [50, 100, 250];
const TAGS = [['qs', /(^| )qs( |$)/], ['qd', /(^| )qd\d+( |$)/], ['qk', /(^| )qk( |$)/], ['escape-split', /^escape-split/], ['esc-split', /^esc-split/]];
for (const set of process.argv.slice(2).filter(a => !a.startsWith('--'))) {
  const rows = fs.readFileSync(path.join(set, 'rows.jsonl'), 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
  const T = { games: 0, won: 0, our: { alive: 0, deaths: {}, rounds: [], len: Object.fromEntries(CP.map(c => [c, []])), end: [] }, their: { alive: 0, deaths: {}, rounds: [], len: Object.fromEntries(CP.map(c => [c, []])), end: [] }, killedTheirs: {}, tags: {} };
  const skip = process.argv.includes('--nopocket') ? /autarky|dilemma|slithery/i : null;   // start-pocket maps: both queens die by geometry
  for (const r of rows) {
    if (skip && skip.test(r.map)) continue;
    const f = path.join(set, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
    let R; try { R = load(f); } catch (e) { console.error('skip', f, e.message); continue; }
    const us = r.side, ourQ = us === 'A' ? 0 : 1, theirQ = 1 - ourQ;
    const Q = { [ourQ]: { len: {}, death: null }, [theirQ]: { len: {}, death: null } };
    const ourIds = new Set(R.match.map.initialDragons.filter(d => d.team === us).map(d => d.id));
    for (const e of R.events) if (e.type === 'dragonSplit' && e.team === us) ourIds.add(e.childId);
    for (const e of R.events) if (e.type === 'dragonIndicator' && ourIds.has(e.id) && e.text) for (const [k, re] of TAGS) if (re.test(e.text)) T.tags[k] = (T.tags[k] || 0) + 1;
    let last = -1, lastRound = 0;
    perGame(R, { map: r.map, variant: 'a' }, {
      turn(d, round, ctx) {
        lastRound = round;
        if (round === last) return; last = round;
        for (const q of [ourQ, theirQ]) { const dq = ctx.drag.get(q); if (CP.includes(round)) Q[q].len[round] = dq ? dq.body.length : 0; }
      },
      death(d, rec, idx, other, round) {
        if (d.id !== ourQ && d.id !== theirQ) return;
        Q[d.id].death = { round, cause: CAUSE[rec.cause], other: other ? `${other.team === (d.id === ourQ ? us : (us === 'A' ? 'B' : 'A')) ? 'own' : 'enemy'} #${other.id} L${other.body.length}${other.id <= 1 ? ' QUEEN' : ''}` : '-', len: d.body.length };
      },
      end(rounds, ctx) { for (const q of [ourQ, theirQ]) { const dq = ctx.drag.get(q); Q[q].end = dq ? dq.body.length : 0; } },
    });
    T.games++; if (r.won) T.won++;
    for (const [q, side] of [[ourQ, 'our'], [theirQ, 'their']]) {
      const S = T[side], x = Q[q];
      if (!x.death) S.alive++; else { S.deaths[x.death.cause] = (S.deaths[x.death.cause] || 0) + 1; S.rounds.push(x.death.round); }
      for (const c of CP) S.len[c].push(x.len[c] ?? 0); S.end.push(x.end ?? 0);
    }
    if (Q[theirQ].death) { const k = Q[theirQ].death.cause + ' by ' + (Q[theirQ].death.other.startsWith('enemy') ? 'us' : 'them'); T.killedTheirs[k] = (T.killedTheirs[k] || 0) + 1; }
    if (SHOW) console.log(`${r.key.padEnd(34)} ${r.won ? 'W' : 'L'} our queen #${ourQ}: ${Q[ourQ].death ? `died r${Q[ourQ].death.round} ${Q[ourQ].death.cause} L${Q[ourQ].death.len} (${Q[ourQ].death.other})` : `alive L${Q[ourQ].end}`} | their queen #${theirQ}: ${Q[theirQ].death ? `died r${Q[theirQ].death.round} ${Q[theirQ].death.cause} L${Q[theirQ].death.len} (${Q[theirQ].death.other})` : `alive L${Q[theirQ].end}`}`);
  }
  const med = a => { const s = a.slice().sort((x, y) => x - y); return s.length ? s[s.length >> 1] : '-'; };
  const fmt = S => `alive at the end ${S.alive}/${T.games}; deaths ${Object.entries(S.deaths).map(([k, v]) => k + ' ' + v).join(', ') || '-'} (median round ${med(S.rounds)}); median length r50/100/250/end ${CP.map(c => med(S.len[c])).join('/')}/${med(S.end)}`;
  console.log(`== ${set}: games ${T.games}, won ${T.won}`);
  console.log(`   our queen:   ${fmt(T.our)}`);
  console.log(`   their queen: ${fmt(T.their)}; killed: ${Object.entries(T.killedTheirs).map(([k, v]) => k + ' ' + v).join(', ') || '-'}`);
  console.log(`   our tags (turns): ${Object.entries(T.tags).map(([k, v]) => k + ' ' + v).join(', ') || '-'}`);
}
