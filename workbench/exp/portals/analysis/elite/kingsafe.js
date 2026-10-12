#!/usr/bin/env node
// King self-safety on Portals from replays (exp/portals step 1c, extra): how often the king (the team's longest living dragon, L >= 8,
// at its turn start) stands on or enters a tile outside the 2-core of the static movement graph (kelp, portals, wrap; a tile outside
// the 2-core lies in a tree-like appendage: a dragon whose head goes in cannot turn back and dies or must split), how cramped it is
// (free tiles reachable from its head through tiles no body holds, vs its length), how often its line hands the body to a child
// (a split by the king whose child is longer than the parent keeps), and the context of king deaths.
// usage: node exp/portals/analysis/elite/kingsafe.js [--per-band 200] > kingsafe.txt   (writes kingsafe.json beside this file)
// Samples: every top-decile elite team-game, and a hash-ordered sample of --per-band median-band and bottom-quartile team-games
// (bands by king500 as in elite.js: P90 51, P40 31, P60 37, P25 26); ours: every W0-W12 Portals game (data/online/<set>/M<id>.replay).
'use strict';
const fs = require('fs'), path = require('path'), readline = require('readline');
const ROOT = path.resolve(__dirname, '../../../..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const PER = +(process.argv.includes('--per-band') ? process.argv[process.argv.indexOf('--per-band') + 1] : 200);
const TH = { p25: 26, p40: 31, p60: 37, p90: 51 };
const WAVES = [['W0', 'cand-merge2-online'], ['W0', 'cand-merge2-online-r2'], ['W0', 'cand-merge2-online-r3'], ['W1', 'cand-stack1-online'], ['W2', 'cand-stack2-online'],
  ['W3', 'cand-stack3-online'], ['W4', 'cand-stack4-online'], ['W5', 'cand-stack5-online'], ['W6', 'cand-stack6-online'], ['W7', 'cand-stack6-online-r2'], ['W8', 'cand-stack7-online'],
  ['W9', 'cand-stack8-online'], ['W10', 'cand-stack9-online'], ['W11', 'cand-stack10-online'], ['W12', 'cand-stack11-online']];
const eraOf = w => { const n = +w.slice(1); return n <= 4 ? 'ours W0-W4' : n <= 9 ? 'ours W5-W9' : 'ours W10-W12'; };
function hash32(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }

function analyse(file, team) {
  const R = load(file), M = R.match.map;
  let core = null, W = 0, H = 0;
  const g = { kingTurns: 0, offCore: 0, entries: 0, entriesAll: 0, cramped: 0, halfCramped: 0, handoff: 0, handoffLen: 0, kingDeaths: [], rounds: 0, k500: R.result['team' + team].longestDragon };
  const hist = []; // recent king-turn records for death context: {r, off, free, L, entry}
  const DIRS = ['N', 'E', 'S', 'W'];
  perGame(R, { map: 'Portals' }, {
    turn(d, round, ctx) {
      if (!core) {
        W = ctx.W; H = ctx.H; const N = W * H;
        const nb = []; for (let k = 0; k < N; k++) { const x = k % W, y = (k / W) | 0, s = new Set(); for (const dd of DIRS) { const n = ctx.across(x, y, dd); if (n) { const nk = n.y * W + n.x; if (nk !== k) s.add(nk); } } nb.push([...s]); }
        const deg = nb.map(a => a.length), alive = new Uint8Array(N).fill(1), q = [];
        for (let k = 0; k < N; k++) if (deg[k] <= 1) { alive[k] = 0; q.push(k); }
        for (let i = 0; i < q.length; i++) for (const u of nb[q[i]]) if (alive[u] && --deg[u] <= 1) { alive[u] = 0; q.push(u); }
        core = alive; g.coreTiles = alive.reduce((s, v) => s + v, 0);
      }
      d._king = false;
      if (d.team !== team || round < 300 || d.body.length < 8 || !ctx.isKingNow(d)) return;
      d._king = true;
      const L = d.body.length, h = d.body[0], hk = h.y * W + h.x;
      // free tiles reachable from the head through tiles no body holds (cap L + 4)
      const seen = new Set([hk]), q = [hk]; let free = 0; const cap = L + 4;
      for (let i = 0; i < q.length && free < cap; i++) { const k = q[i], x = k % W, y = (k / W) | 0; for (const dd of DIRS) { const n = ctx.across(x, y, dd); if (!n) continue; const nk = n.y * W + n.x; if (seen.has(nk) || ctx.occ.has(nk)) continue; seen.add(nk); q.push(nk); free++; } }
      g.kingTurns++;
      const off = !core[hk]; if (off) g.offCore++;
      if (free < L) g.cramped++;
      if (free < L / 2) g.halfCramped++;
      d._rec = { r: round, off, free, L, entry: false };
      hist.push(d._rec); if (hist.length > 40) hist.shift();
    },
    action(d, e, round, ctx, bodyBefore) {
      if (!d._king || !e.action || e.action.kind !== 'move') return;
      let x = bodyBefore[0].x, y = bodyBefore[0].y, wasCore = core[y * W + x];
      for (const st of e.action.steps) {
        const n = ctx.across(x, y, st); if (!n) break;
        x = n.x; y = n.y;
        if (!core[y * W + x]) { g.entriesAll++; if (wasCore) { g.entries++; if (d._rec) d._rec.entry = true; } break; }
      }
    },
    split(p, ch, e, round, ctx) {
      if (p.team !== team || round < 300 || !p._king) return;
      if (ch.body.length > p.body.length) { g.handoff++; g.handoffLen += p.body.length; }
    },
    death(d, rec, i, other, round, ctx) {
      if (d.team !== team || !rec.king) return;
      const recent = hist.filter(h => h.r >= round - 10);
      const last = hist.length ? hist[hist.length - 1] : null;
      g.kingDeaths.push({ r: round, cause: ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'][rec.cause], L: rec.len,
        lastOff: last && last.r >= round - 1 ? last.off : null, lastFree: last && last.r >= round - 1 ? last.free : null,
        entries10: recent.filter(h => h.entry).length, offTurns10: recent.filter(h => h.off).length });
    },
  });
  return g;
}

(async () => {
  // elite samples
  const top = [], med = [], bot = [];
  const rl = readline.createInterface({ input: fs.createReadStream(path.join(ROOT, '.cache/mass-ledger/top-sample.jsonl')), crlfDelay: Infinity });
  for await (const l of rl) {
    if (!l.includes('"map":"Portals"')) continue;
    const g = JSON.parse(l); if (g.map !== 'Portals') continue;
    const st = tm => g.rounds >= 100 && g[tm].sonar === 0 && g[tm].splits <= 3;
    if (st('A') || st('B')) continue;
    for (const tm of ['A', 'B']) {
      const k = g[tm].st.king[50], [bid, gid] = g.key.split(':');
      const t = { key: g.key, team: tm, k500: k, file: path.join(ROOT, 'data/top', bid, gid + '.replay.gz'), name: tm === 'A' ? g.teamA : g.teamB };
      if (k >= TH.p90) top.push(t); else if (k >= TH.p40 && k <= TH.p60) med.push(t); else if (k <= TH.p25) bot.push(t);
    }
  }
  const pick = a => a.sort((u, v) => hash32(u.key + u.team) - hash32(v.key + v.team)).slice(0, PER);
  const jobs = [...top.map(t => ({ ...t, band: 'top decile' })), ...pick(med).map(t => ({ ...t, band: 'median band' })), ...pick(bot).map(t => ({ ...t, band: 'bottom quartile' }))];
  for (const [w, set] of WAVES) {
    const idx = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/online', set, 'index.json'), 'utf8'));
    for (const g of idx.games) if (g.mapName === 'Portals') { const f = path.join(ROOT, 'data/online', set, 'M' + g.gameId + '.replay'); if (fs.existsSync(f)) jobs.push({ key: set + ':' + g.gameId, team: String(g.ourSide).toUpperCase(), file: f, band: eraOf(w) }); }
  }
  const res = {}; let n = 0; const t0 = Date.now();
  const LIM = +(process.env.LIMIT || 0), ONLY = process.env.ONLY, run = ONLY ? jobs.filter(j => j.key.includes(ONLY)) : LIM ? jobs.filter((j, i) => i % Math.ceil(jobs.length / LIM) === 0) : jobs;
  for (const j of run) {
    try { const g = analyse(j.file, j.team); (res[j.band] = res[j.band] || []).push({ key: j.key, team: j.team, ...g }); }
    catch (e) { console.error('error', j.key, String(e).slice(0, 200)); }
    if (++n % 100 === 0) console.error(`${n}/${run.length} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  fs.writeFileSync(path.join(__dirname, 'kingsafe.json'), JSON.stringify(res));
  const mean = a => a.length ? a.reduce((s, x) => s + x, 0) / a.length : null;
  const S = (a, k) => a.reduce((s, g) => s + g[k], 0);
  console.log('band | N | king-turns r300-499 per game | on non-2-core tiles | entries into non-2-core per game | free < L share | free < L/2 share | handoff splits per game (parent kept, mean) | king deaths per game | deaths: cause (on non-core at last turn, free < L at last turn, entry within 10 rounds)');
  for (const [b, gs] of Object.entries(res)) {
    const kt = S(gs, 'kingTurns'), kd = gs.flatMap(g => g.kingDeaths);
    const byCause = {}; for (const x of kd) byCause[x.cause] = (byCause[x.cause] || 0) + 1;
    const off = kd.filter(x => x.lastOff === true).length, cr = kd.filter(x => x.lastFree !== null && x.lastFree < x.L).length, en = kd.filter(x => x.entries10 > 0).length;
    console.log(`${b} | ${gs.length} | ${(kt / gs.length).toFixed(0)} | ${(100 * S(gs, 'offCore') / Math.max(1, kt)).toFixed(1)}% | ${(S(gs, 'entries') / gs.length).toFixed(2)} | ${(100 * S(gs, 'cramped') / Math.max(1, kt)).toFixed(1)}% | ${(100 * S(gs, 'halfCramped') / Math.max(1, kt)).toFixed(1)}% | ${(S(gs, 'handoff') / gs.length).toFixed(2)} (${(S(gs, 'handoffLen') / Math.max(1, S(gs, 'handoff'))).toFixed(1)}) | ${(kd.length / gs.length).toFixed(2)} | ${Object.entries(byCause).map(([c, v]) => c + ' ' + v).join(', ')} (${off}/${kd.length}, ${cr}/${kd.length}, ${en}/${kd.length})`);
  }
  console.log('core tiles (static 2-core of the Portals graph):', Object.values(res)[0][0].coreTiles, 'of 512');
})();
