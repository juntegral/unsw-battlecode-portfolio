#!/usr/bin/env node
// W7 mechanism metric (small-map survival, hypothesis (a) "reach avoidance"; research/observations/small-maps.md §5, §9 #2): for every move of the
// measured team's dragons, whether the tile its head ends on can be reached by an enemy head before the mover's next turn, and whether a safe
// alternative existed then. Every enemy acts exactly once before our next turn (higher ids later this round, lower ids next round), so the reach
// is one action: a path of at most L-1 steps (a sprint of x steps costs x-1 segments; L2 has 1 step) over free tiles, from the enemy's head as it
// stands now. Obstacles: every dragon tile now, with our own body as it is after a one-step move (our tail goes first); the destination itself is
// a target (a head there means a head-on: both die). "latent": also a child that a higher-id enemy of length >= 4 may split off this round (its
// head on the enemy's tail, 1 step). Alternatives: our legal 1-step moves (not reverse, not into a body or wall, not into an enemy head) and, for
// L >= 3, 2-step sprints over free tiles. Outcome check: our dragon was rammed (an enemy head moved into it) before its next turn.
// Cohorts: our local sets (rows.jsonl, side = ours), or the small-map study's population (exp/small/population.json: local, online, top, elite).
// usage: node exp/w7/reach.js --sets exp/w2/v16-H,exp/w2/v16-K [--maps arena,Colosseum,default_small,trophy] [--label v16]
//        node exp/w7/reach.js --population [--src online,top] [--limit N] [--out exp/w7/reach-pop.json]
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const load = makeLoader(viewerSource());
const args = process.argv.slice(2), opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const DIRS = ['N', 'E', 'S', 'W'], OPP = { N: 'S', S: 'N', E: 'W', W: 'E' };
const SHOW = +opt('--show', 0); let shown = 0;   // print up to SHOW rammed avoidable exposures as 11x11 pictures

function newStats() { return { games: 0, moves: 0, reach: 0, reachLatent: 0, safeAlt: 0, exposedAvoidable: 0, exposedForced: 0, ramReach: 0, ramAvoid: 0, ramSafe: 0, safeMoves: 0, splits: 0,
  byLen: { 2: [0, 0, 0], 3: [0, 0, 0], 4: [0, 0, 0] }, crowd: [0, 0, 0], uncrowd: [0, 0, 0], avoidKind: { 'd1 notLonger': 0, 'd1 longer': 0, 'd2+ notLonger': 0, 'd2+ longer': 0 }, avoidRa: { 'd1 notLonger': 0, 'd1 longer': 0, 'd2+ notLonger': 0, 'd2+ longer': 0 }, avoidTrade: 0, avoidLowV: 0 }; }
// measure one game for the teams in `teams` (map team -> stats object)
function measure(file, teams, mapHint) {
  const R = load(file);
  const pending = new Map();   // dragon id -> its last move record (until its next turn)
  const lastInd = new Map();   // dragon id -> this turn's indicator text (it precedes the action in the stream)
  perGame(R, { map: mapHint || '?', variant: 'a' }, {
    turn(d) { pending.delete(d.id); lastInd.delete(d.id); },
    indicator(e) { lastInd.set(e.id, e.text || ''); },
    split(p) { const S = teams[p.team]; if (S) S.splits++; },
    action(d, e, round, ctx, hb) {
      const S = teams[d.team]; if (!S) return;
      const a = e.action; if (!a || a.kind !== 'move' || d.fate) return;   // splits, waits and deaths on the way are not counted here
      const { occ, key, across, drag, W, H } = ctx;
      const L = hb.length, head = hb[0];
      // obstacles: every other dragon tile now + our body after a one-step move (our pre-move body without its tail)
      const own = new Set(); for (let i = 0; i < L - 1; i++) own.add(key(hb[i].x, hb[i].y));
      const blocked = k => (occ.has(k) && occ.get(k) !== d.id) || own.has(k);
      // enemy reach (one action) by BFS from each enemy head near us
      const reach = new Set(), latent = new Set(), reachInfo = new Map();   // tile -> {d: min steps, notLonger: some reaching enemy with length <= ours}
      const near = (p, r) => { const dx = Math.abs(p.x - head.x), dy = Math.abs(p.y - head.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy) <= r + 3; };
      const bfs = (src, r, out, len) => {
        const seen = new Map([[key(src.x, src.y), 0]]), q = [src];
        for (let i = 0; i < q.length; i++) {
          const c = q[i], dc = seen.get(key(c.x, c.y)); if (dc >= r) continue;
          for (const dir of DIRS) {
            const u = across(c.x, c.y, dir); if (!u) continue;
            const k = key(u.x, u.y); if (seen.has(k)) continue;
            seen.set(k, dc + 1); out.add(k);   // reachable as the final step even if occupied by our head
            if (len) { const ri = reachInfo.get(k) || { d: 99, notLonger: false }; ri.d = Math.min(ri.d, dc + 1); if (len <= L) ri.notLonger = true; reachInfo.set(k, ri); }
            if (!blocked(k)) q.push(u);         // passable only when free
          }
        }
      };
      for (const o of drag.values()) {
        if (o.team === d.team || !o.body.length) continue;
        const r = Math.max(1, Math.min(o.body.length - 1, 6));
        if (!near(o.body[0], r)) continue;
        bfs(o.body[0], r, reach, o.body.length);
        if (o.id > d.id && o.body.length >= 4) { const tl = o.body[o.body.length - 1]; if (near(tl, 1)) bfs(tl, 1, latent, 0); }
      }
      // our alternatives
      const enemyHead = new Set(); for (const o of drag.values()) if (o.team !== d.team && o.body.length) enemyHead.add(key(o.body[0].x, o.body[0].y));
      const occBefore = k => occ.has(k) && occ.get(k) !== d.id || hb.some(s => key(s.x, s.y) === k);
      const neckDir = L >= 2 ? DIRS.find(dir => { const u = across(head.x, head.y, dir); return u && u.x === hb[1].x && u.y === hb[1].y; }) : null;
      const alts = [];
      for (const d1 of DIRS) {
        if (d1 === neckDir) continue;
        const u1 = across(head.x, head.y, d1); if (!u1) continue;
        const k1 = key(u1.x, u1.y); if (occBefore(k1) || enemyHead.has(k1)) continue;
        alts.push(k1);
        if (L >= 3) for (const d2 of DIRS) {
          if (d2 === OPP[d1]) continue;
          const u2 = across(u1.x, u1.y, d2); if (!u2) continue;
          const k2 = key(u2.x, u2.y); if (occBefore(k2) || enemyHead.has(k2) || k2 === key(head.x, head.y)) continue;
          alts.push(k2);
        }
      }
      const t = d.body[0], kt = key(t.x, t.y);
      const isReach = reach.has(kt), isLatent = !isReach && latent.has(kt);
      const safe = alts.filter(k => k !== kt && !reach.has(k) && !latent.has(k)).length > 0;
      // crowding: heads (both teams, ours included) within the 7x7 window
      let heads = 0; for (const o of drag.values()) { if (!o.body.length) continue; const h = o.body[0], dx = Math.abs(h.x - head.x), dy = Math.abs(h.y - head.y); if (Math.max(Math.min(dx, W - dx), Math.min(dy, H - dy)) <= 3) heads++; }
      S.moves++;
      if (isReach) S.reach++; if (isLatent) S.reachLatent++;
      if (safe) S.safeAlt++;
      if (isReach && safe) { S.exposedAvoidable++; const ri = reachInfo.get(kt); const kind = (ri.d <= 1 ? 'd1' : 'd2+') + (ri.notLonger ? ' notLonger' : ' longer'); S.avoidKind[kind]++;
        const ind = lastInd.get(d.id) || ''; if (/ ra\d/.test(ind)) S.avoidRa[kind]++; if (/ (TRADE|ram4)/.test(ind)) S.avoidTrade++; const v = /^\S+ v(-?[\d.]+)/.exec(ind); if (v && +v[1] < -20) S.avoidLowV++; }
      else if (isReach) S.exposedForced++; else S.safeMoves++;
      const lb = S.byLen[Math.min(L, 4)]; if (lb) { lb[0]++; if (isReach) lb[1]++; if (isReach && safe) lb[2]++; }
      const cb = heads >= 5 ? S.crowd : S.uncrowd; cb[0]++; if (isReach) cb[1]++; if (isReach && safe) cb[2]++;
      let pic = null;
      if (SHOW && isReach && safe && shown < SHOW) {
        const rows = [];
        for (let dy = -5; dy <= 5; dy++) { let row = '';
          for (let dx = -5; dx <= 5; dx++) {
            const x = (head.x + dx + W) % W, y = (head.y + dy + H) % H, k = key(x, y);
            let c = '·';
            if (reach.has(k)) c = ':';
            if (occ.has(k)) { const o = drag.get(occ.get(k)); const isHead = o && o.body[0].x === x && o.body[0].y === y; c = !o ? '?' : o.team === d.team ? (o.id === d.id ? (isHead ? '!' : '=') : (isHead ? 'a' : '-')) : (isHead ? String(Math.min(9, o.body.length)) : 'x'); }
            if (!occ.has(k) && alts.includes(k) && !reach.has(k)) c = 'o';
            if (x === head.x && y === head.y) c = '@';
            row += c; }
          rows.push(row); }
        pic = `r${round} #${d.id} L${L} moved ${a.steps.join('')} to (${t.x},${t.y}): '@' head before, '!' head after, '=' our body, 'a'/'-' ally head/body, digits enemy heads (length), 'x' enemy body, ':' enemy reach, 'o' safe alternatives\n  indicator: ${lastInd.get(d.id) || ''}\n  ` + rows.join('\n  ');
      }
      pending.set(d.id, { S, isReach, avoid: isReach && safe, pic });
    },
    death(d, rec) {
      if (rec.cause !== 2) return;   // rammed: an enemy head moved into this dragon's head
      const p = pending.get(d.id); if (!p) return;
      if (p.isReach) { p.S.ramReach++; if (p.avoid) p.S.ramAvoid++; } else p.S.ramSafe++;
      if (p.pic && shown < SHOW) { shown++; console.log(p.pic + '\n  -> rammed before its next turn\n'); }
      pending.delete(d.id);
    },
  });
}
function report(label, S) {
  const pc = (a, b) => b ? (100 * a / b).toFixed(1) + '%' : '-';
  const lens = [2, 3, 4].map(l => `L${l === 4 ? '4+' : l} ${pc(S.byLen[l][2], S.byLen[l][0])} of ${S.byLen[l][0]}`).join(', ');
  console.log(`${label.padEnd(28)} games ${S.games} moves ${S.moves}: ends in enemy reach ${pc(S.reach, S.moves)} (+latent child ${pc(S.reachLatent, S.moves)}); ` +
    `**into reach with a safe alternative ${pc(S.exposedAvoidable, S.moves)}** (forced ${pc(S.exposedForced, S.moves)}) | by length: ${lens} | crowded (>=5 heads in 7x7) ${pc(S.crowd[2], S.crowd[0])} of ${S.crowd[0]}, uncrowded ${pc(S.uncrowd[2], S.uncrowd[0])} | ` +
    `rammed before the next turn: after a reach move ${pc(S.ramReach, S.reach)} (rams ${S.ramReach}, of them after an avoidable one ${S.ramAvoid}), after a safe move ${pc(S.ramSafe, S.safeMoves)} | splits ${S.splits} | avoidable exposures by nearest reach step and whether a reaching enemy is no longer than us (the bot's threat is not discounted then): ${JSON.stringify(S.avoidKind)}; of them with the ' ra' tag this turn ${JSON.stringify(S.avoidRa)}; trade/ram tag ${S.avoidTrade}; chosen value < -20 ${S.avoidLowV}`);
}
function addInto(T, S) {
  for (const [k, v] of Object.entries(S)) {
    if (typeof v === 'number') T[k] += v;
    else if (Array.isArray(v)) v.forEach((x, i) => { T[k][i] += x; });
    else for (const [kk, vv] of Object.entries(v)) { if (Array.isArray(vv)) vv.forEach((x, i) => { T[k][kk][i] += x; }); else T[k][kk] += vv; }
  }
}
(async () => {
  const cohorts = new Map(); const get = l => { if (!cohorts.has(l)) cohorts.set(l, newStats()); return cohorts.get(l); };
  const run = (file, teamLabels, map) => {   // teamLabels: team -> [cohort labels]
    const teams = {}; for (const tm of Object.keys(teamLabels)) teams[tm] = newStats();
    measure(file, teams, map);
    for (const [tm, labels] of Object.entries(teamLabels)) for (const l of labels) { const C = get(l); C.games++; addInto(C, Object.assign({}, teams[tm], { games: 0 })); }
  };
  if (opt('--sets')) {
    const maps = opt('--maps') ? new Set(opt('--maps').split(',')) : null, label = opt('--label', 'ours');
    for (const set of opt('--sets').split(',')) {
      const rows = fs.readFileSync(path.join(ROOT, set, 'rows.jsonl'), 'utf8').split('\n').filter(Boolean).map(JSON.parse).filter(r => r.G !== undefined && !r.error && (!maps || maps.has(r.map)));
      for (const r of rows) run(path.join(ROOT, set, 'games', r.key.replace(/:/g, '_'), 'game.replay'), { [r.side]: [`${label} ${r.map}`, `${label} ALL`] }, r.map);
    }
  } else if (args.includes('--population')) {
    const P = JSON.parse(fs.readFileSync(path.join(ROOT, 'exp', 'small', 'population.json'), 'utf8'));
    const srcs = new Set((opt('--src', 'local,online,top,elite')).split(',')), limit = +opt('--limit', 1e9);
    let n = 0;
    for (const t of P.tasks) {
      if (!srcs.has(t.src) || n >= limit) continue;
      n++;
      const map = t.map || t.mapName || '?';
      try {
        if (t.src === 'local' || t.src === 'online') run(t.file, { [t.us]: [`${t.src} ${map}`, `${t.src} ${t.set} ${map}`] }, map);
        else { const w = (t.winner || '').toUpperCase(); run(t.file, { [w]: [`${t.src} winner ${map}`], [w === 'A' ? 'B' : 'A']: [`${t.src} loser ${map}`] }, map); }
      } catch (e) { console.error('skip', t.key, String(e).slice(0, 120)); }
      if (n % 100 === 0) console.error('progress', n);
    }
  }
  for (const [l, S] of [...cohorts].sort()) report(l, S);
  if (opt('--out')) fs.writeFileSync(path.join(ROOT, opt('--out')), JSON.stringify(Object.fromEntries(cohorts), null, 1));
})();
