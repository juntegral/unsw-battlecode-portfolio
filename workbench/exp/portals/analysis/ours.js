#!/usr/bin/env node
// Portals: our own games, one record per game (exp/portals step 1a/1b). Replays only, through tools/mass_ledger.js perGame hooks.
//   king deaths (the dying dragon was our longest and >= 8 long): cause, round, length, its last indicator (the move tags), its free
//     space at turn start (tiles reachable from its head through tiles no body holds, capped at 256) vs its length, whether the head
//     was on a tile outside the static 2-core, and full-board pictures 10 rounds before and at the start of the fatal turn;
//   king handoffs (a split of the king whose child is longer than what the parent keeps);
//   the king curve, units, mass, sacrifices, where our death drops went, the final-king lineage (perGame's lin).
// usage:
//   node exp/portals/analysis/ours.js local <evalOutDir> [--label L] [--out file.jsonl] [--pics N]
//   node exp/portals/analysis/ours.js online <set> [<set> ...] [--out file.jsonl] [--pics N]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools/top_features.js'));
const { perGame, CAUSE } = require(path.join(ROOT, 'tools/mass_ledger.js'));
const load = makeLoader(viewerSource());
const PTM = JSON.parse(fs.readFileSync(path.join(__dirname, '../gen/ptmap.json'), 'utf8'));   // DEAD / ROOM tables (genptmap.js)
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };

// static 2-core of the movement graph (kelp, portals, wrap): repeatedly drop tiles with fewer than 2 open neighbours
function twoCore(ctx) {
  const { W, H, across, key } = ctx, N = W * H;
  const nb = []; for (let k = 0; k < N; k++) { const x = k % W, y = (k / W) | 0, s = new Set(); for (const d of ['N', 'E', 'S', 'W']) { const u = across(x, y, d); if (u) s.add(key(u.x, u.y)); } s.delete(k); nb.push([...s]); }
  const alive = new Uint8Array(N).fill(1), deg = nb.map(a => a.length), q = [];
  for (let k = 0; k < N; k++) if (deg[k] < 2) q.push(k);
  while (q.length) { const k = q.pop(); if (!alive[k]) continue; alive[k] = 0; for (const u of nb[k]) if (alive[u] && --deg[u] < 2) q.push(u); }
  return { core: alive, nb };
}

function analyse(file, us, meta, nPics) {
  const R = load(file);
  const rec = { ...meta, us, kingDeaths: [], handoffs: [], sacs: [], pics: [] };
  let core = null, nb = null, lastSnapRound = -1;
  const snaps = []; // ring of { r, text }
  const lastInd = new Map();     // dragon id -> indicator text of its latest turn
  const wasKingTurn = new Map(); // dragon id -> it was our king at its turn start
  const freeAtTurn = new Map();  // dragon id -> { free, len, core }
  const picture = (ctx, kingId) => {
    const { W, H, drag, pearls } = ctx;
    const g = Array.from({ length: H }, (_, y) => Array.from({ length: W }, (_, x) => core[y * W + x] ? ' ' : ','));
    for (const [k, v] of pearls) { const x = k % W, y = (k / W) | 0; g[y][x] = v === -1 ? 'o' : '%'; }
    const list = [];
    for (const d of drag.values()) {
      if (d.team !== us) continue;
      const L = d.body.length, isK = d.id === kingId;
      for (let i = 1; i < L; i++) { const s = d.body[i]; g[s.y][s.x] = isK ? '=' : '.'; }
      const h = d.body[0]; g[h.y][h.x] = isK ? 'K' : L >= 10 ? '#' : String(L);
      list.push(L);
    }
    list.sort((a, b) => b - a);
    return `ours ${list.length} [${list.slice(0, 14).join(' ')}${list.length > 14 ? ' …' : ''}] total ${list.reduce((a, b) => a + b, 0)}\n+${'-'.repeat(W)}+\n${g.map(r => '|' + r.join('') + '|').join('\n')}\n+${'-'.repeat(W)}+`;
  };
  const flood = (ctx, d) => { // free tiles reachable from d's head (bodies block, own tail included), capped
    const { W, occ, key, across } = ctx, h = d.body[0], seen = new Set([key(h.x, h.y)]), q = [h];
    let n = 0;
    while (q.length && n < 256) { const t = q.shift(); for (const dd of ['N', 'E', 'S', 'W']) { const u = across(t.x, t.y, dd); if (!u) continue; const k = key(u.x, u.y); if (seen.has(k) || occ.has(k)) continue; seen.add(k); q.push(u); n++; } }
    return n;
  };
  const kingOf = ctx => { let k = null; for (const d of ctx.drag.values()) if (d.team === us && (!k || d.body.length > k.body.length || (d.body.length === k.body.length && d.id < k.id))) k = d; return k; };
  const g = perGame(R, { map: 'Portals' }, {
    turn(d, round, ctx) {
      if (!core) { const c = twoCore(ctx); core = c.core; nb = c.nb; }
      if (round !== lastSnapRound) { lastSnapRound = round; const k = kingOf(ctx); snaps.push({ r: round, text: picture(ctx, k ? k.id : -1) }); if (snaps.length > 12) snaps.shift(); }
      if (d.team !== us) return;
      const isK = ctx.isKingNow(d) && d.body.length >= 8;
      wasKingTurn.set(d.id, isK);
      if (isK) {
        const h = d.body[0], k = ctx.key(h.x, h.y);
        freeAtTurn.set(d.id, { free: flood(ctx, d), len: d.body.length, core: core[k], x: h.x, y: h.y, room: PTM.room[k], dead: PTM.dead[k] });
        if (round >= 250) { rec.kTurns = (rec.kTurns || 0) + 1; if (PTM.room[k]) rec.kRoomTurns = (rec.kRoomTurns || 0) + 1; if (PTM.dead[k]) rec.kDeadTurns = (rec.kDeadTurns || 0) + 1; }
      }
    },
    indicator(e, round, ctx) { const id = e.dragonId ?? e.id; lastInd.set(id, String(e.text || '')); },
    split(p, ch, e, round, ctx) {
      if (p.team !== us) return;
      if (wasKingTurn.get(p.id) && ch.body.length > p.body.length) rec.handoffs.push({ r: round, parentKeeps: p.body.length, child: ch.body.length, tag: lastInd.get(p.id) || '' });
    },
    death(d, drec, idx, other, round, ctx) {
      if (d.team !== us) return;
      if (drec.king) {
        const f = freeAtTurn.get(d.id) || {};
        const before = snaps.find(s => s.r === round - 10) || snaps[0];
        const kd = { r: round, cause: CAUSE[drec.cause], len: drec.len, tag: lastInd.get(d.id) || '', free: f.free, lenAtTurn: f.len, inCore: f.core, x: f.x, y: f.y, room: f.room, dead: f.dead, mech: drec.mech, near: drec.near, blk: drec.blk,
          otherLen: other ? other.body.length : null, otherTeam: other ? other.team : null, otherTag: other ? lastInd.get(other.id) || '' : '', otherId: other ? other.id : null, id: d.id, idx };
        if (rec.pics.length < nPics) rec.pics.push({ r: round, before: before ? `r${before.r}: ` + before.text : '', at: `r${round}: ` + picture(ctx, d.id) });
        rec.kingDeaths.push(kd);
      }
      if (round >= 250) rec.sacs.push({ r: round, cause: CAUSE[drec.cause], len: drec.len, kdist: drec.kdist, near: drec.near, idx });
    },
  });
  // death-drop outcomes (perGame's records are final now): eaten by the king / own / none
  const T = g[us];
  rec.rounds = g.rounds; rec.k500 = T.st.king[50]; rec.total = T.st.total; rec.units = T.st.units; rec.king = T.st.king; rec.second = T.st.second;
  rec.lin = T.lin; rec.fl = T.fl; rec.dt = T.dt; rec.chk = g.chk; rec.result = R.result;
  return rec;
}

(async () => {
  const mode = argv[0], nPics = +opt('pics', 3), out = opt('out', null);
  const jobs = [];
  if (mode === 'local') {
    const dir = path.resolve(argv[1]);
    for (const l of fs.readFileSync(path.join(dir, 'rows.jsonl'), 'utf8').trim().split('\n')) {
      const r = JSON.parse(l); if (r.map !== 'portals' || r.G === undefined) continue;
      const f = path.join(dir, 'games', r.key.replace(/:/g, '_'), 'game.replay'); if (!fs.existsSync(f)) continue;
      jobs.push({ file: f, us: r.side, meta: { src: 'local', label: opt('label', path.basename(dir)), key: r.key, seed: r.seed, opp: r.opp, G: r.G } });
    }
  } else if (mode === 'online') {
    const sets = []; for (let i = 1; i < argv.length; i++) { if (argv[i].startsWith('--')) { i++; continue; } sets.push(argv[i]); }
    for (const set of sets) {
      const idx = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/online', set, 'index.json'), 'utf8'));
      for (const g of idx.games) {
        if (g.mapName !== 'Portals') continue;
        const f = path.join(ROOT, 'data/online', set, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
        jobs.push({ file: f, us: String(g.ourSide).toUpperCase(), meta: { src: 'online', label: set, key: set + ':' + g.gameId, opp: g.opponentTeam, won: g.ourWin } });
      }
    }
  } else { console.error('usage: ours.js local <dir> | online <set>...'); process.exit(2); }
  const lines = [];
  for (const j of jobs) {
    try { const r = analyse(j.file, j.us, j.meta, nPics); lines.push(JSON.stringify(r)); }
    catch (e) { console.error('error', j.meta.key, String(e.stack || e).split('\n').slice(0, 3).join(' | ')); }
  }
  if (out) fs.writeFileSync(out, lines.join('\n') + '\n'); else console.log(lines.join('\n'));
  console.error(`${lines.length} games`);
})();
