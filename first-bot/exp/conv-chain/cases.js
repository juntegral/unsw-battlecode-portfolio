#!/usr/bin/env node
// Selected-replay reading for research/observations/conversion-chain.md (stage 3 of the user's method).
// Selection rule: our labelled conversions (conv, feed) on 500-round maps in the stacked sets (stack1-5) and merge2's three
// waves, grouped by where most of their pearls went (line = the final king's line; alive = an ally whose family lived to the end
// off the line; dead = an ally whose family all died; enemy). Per class the N events with the most pearls in that class, one per
// game, ties by game key. For each: a timeline of the sacrificer, the target and the line member at that moment.
// usage: node exp/conv-chain/cases.js [--n 2]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { readJsonl, grp, OUR } = require('./report.js');
const n = +(process.argv.includes('--n') ? process.argv[process.argv.indexOf('--n') + 1] : 2);
const CAUSE_KO = ['희생', '갇힘', '박힘', '박음', '적 몸', '아군 머리', '시간 초과', '질주 사망'];

const ev = [];
for (const s of [...OUR.stack, ...OUR.merge2]) for (const g of readJsonl(path.join(ROOT, '.cache', 'conv-chain', 'online-' + s + '.jsonl'))) {
  if (g.kind !== 'r500') continue;
  for (const v of g[g.us].conv || []) {
    if (!v.c) continue;
    const q = grp(v.c), cls = { line: q.K, alive: q.M, dead: q.D + q.S2K, enemy: q.E };
    const top = Object.entries(cls).sort((a, b) => b[1] - a[1])[0];
    if (top[1] === 0) continue;
    ev.push({ set: s, key: g.key, map: g.map, opp: g.opp, us: g.us, v, cls: top[0], amount: top[1] });
  }
}
const pick = [];
for (const c of ['line', 'alive', 'dead', 'enemy']) {
  const xs = ev.filter(e => e.cls === c).sort((a, b) => b.amount - a.amount || (a.key < b.key ? -1 : 1));
  const seen = new Set(); let k = 0;
  for (const e of xs) { if (seen.has(e.key)) continue; seen.add(e.key); pick.push(e); if (++k >= n) break; }
  console.log(`class ${c}: ${xs.length} events`);
}

const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
for (const e of pick) {
  const [set, gid] = e.key.split(':');
  const R = load(path.join(ROOT, 'data', 'online', set, 'M' + gid + '.replay'));
  const v = e.v, watch = new Set([v.id, v.target, v.lineAt]);
  const tl = new Map(); // id -> [[r, len, x, y]]
  const deaths = new Map(), eatsOf = [];
  let kingEnd = null;
  const hooks = {
    turn(d, r, c) { if (watch.has(d.id) && (r % 10 === 0 || Math.abs(r - v.r) <= 2)) { let a = tl.get(d.id); if (!a) tl.set(d.id, a = []); if (!a.length || a[a.length - 1][0] !== r) a.push([r, d.body.length, d.body[0].x, d.body[0].y]); } },
    death(d, rec, idx, other, r, c) { if (watch.has(d.id)) deaths.set(d.id, { r, cause: rec.cause, len: rec.len, other: other ? other.body.length : 0, idx }); },
    eat(d, tile, o, r, c) { if (o >= 0) eatsOf.push([o, d.id, d.team, r]); },
    end(rounds, c) { kingEnd = c.kingOf(e.us); },
  };
  perGame(R, { map: e.map }, hooks);
  const dist = (a, b) => a && b ? Math.abs(a[2] - b[2]) + Math.abs(a[3] - b[3]) : '?';
  const at = (id, r) => { const a = tl.get(id) || []; let best = null; for (const x of a) if (x[0] <= r) best = x; return best; };
  console.log(`\n## [${e.cls}] ${e.key} ${e.map} vs ${e.opp} · r${v.r} ${v.k} #${v.id}(L${v.L}) -> #${v.target}(L${v.tLen}, 팀 순위 ${v.tRank}, 팀 최장 ${v.teamLongest}) · 그 순간 계보 #${v.lineAt} · 진주 ${v.drops}: 계보 ${grp(v.c).K}, 산 아군 ${grp(v.c).M}, 죽은 아군 ${grp(v.c).D + grp(v.c).S2K}, 상대 ${grp(v.c).E}`);
  const pT = at(v.target, v.r), pL = at(v.lineAt, v.r), pS = at(v.id, v.r);
  console.log(`- 그 순간 머리 거리(토러스 무시 맨해튼): 희생→대상 ${dist(pS, pT)}, 희생→계보 ${dist(pS, pL)}, 대상→계보 ${dist(pT, pL)}; 계보 길이 ${pL ? pL[1] : '?'}`);
  for (const id of [v.target, v.lineAt]) {
    const a = (tl.get(id) || []).filter(x => x[0] >= v.r && x[0] % 20 === 0).map(x => `r${x[0]} L${x[1]}`).join(', ');
    const dz = deaths.get(id);
    const fed = dz ? eatsOf.filter(q => q[0] === dz.idx) : [];
    console.log(`- #${id}${id === v.target ? ' (대상)' : ' (계보)'}: ${a}${dz ? ` · r${dz.r} ${CAUSE_KO[dz.cause]} L${dz.len}${dz.other ? ` (상대 길이 ${dz.other})` : ''}, 진주를 먹은 쪽 ${fed.map(q => (q[2] === e.us ? '#' + q[1] : '적')).join(' ') || '없음'}` : ' · 끝까지 삶'}`);
  }
  console.log(`- 끝: 최종 왕 #${kingEnd ? kingEnd.id : '-'} L${kingEnd ? kingEnd.body.length : 0} · 대상 가족 ${v.tFam} (계보로 간 사망 진주 ${v.tFamToLine})`);
}
