#!/usr/bin/env node
// Independent recount of the key supply-chain numbers (user rule: key numbers are recounted with separate code).
// It does not use tools/mass_ledger.js perGame nor exp/territory-analysis geometry: bodies come from the replay's own
// dragonUpdate (head/tail per step) and dragonSplit bodies, geometry is rebuilt here from the map fields, the conv BFS runs
// forward (from the big ally to the piece, as plan.cpp does; extract.js runs it backward), deaths are classified from the
// replay's death reason and the free neighbours counted here.
// Recounted per game and team, then compared game by game with the cache of extract.js:
//   pieces (children <= 3 at birth), of them: ate >= 1 natural pearl within 30 rounds, alive 30 rounds on (or at the end),
//   ended by sacrifice / trap / rammed (enemy head moved in) / alive at the end; conv-state dragon-turns (cs) and sacrifices at a
//   turn in cs; death drops within 6 steps (static path) of a team head in their first 6 rounds, and of those eaten by that team.
// usage: node exp/supply-chain/recount.js [--top-every 10] [--jobs 3] [--sets a,b,...]
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'supply-chain');

function geo(M) {
  const W = M.width, H = M.height, N = W * H;
  const md = (a, m) => ((a % m) + m) % m;
  // kelp on the north edge of (x, y): horizontal edge row y; on the west edge: vertical edge column x
  const kelpN = (x, y) => M.initialHEdges[md(y, H) * W + x] === 1 || (md(y, H) === 0 && M.initialHEdges[H * W + x] === 1);
  const kelpW = (x, y) => M.initialVEdges[y * (W + 1) + md(x, W)] === 1 || (md(x, W) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  const port = new Map();
  const norm = e => e.side === 'S' ? [e.x, md(e.y + 1, H), 'N'] : e.side === 'E' ? [md(e.x + 1, W), e.y, 'W'] : [e.x, e.y, e.side];
  for (const pr of M.portals || []) if (pr.length === 2) { const a = norm(pr[0]), b = norm(pr[1]); port.set(a.join(), b); port.set(b.join(), a); }
  const nb = new Int32Array(N * 4).fill(-1);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const k = y * W + x;
    // N
    { const p = port.get([x, y, 'N'].join()); if (p) nb[k * 4] = md(p[1] - 1, H) * W + p[0]; else if (!kelpN(x, y)) nb[k * 4] = md(y - 1, H) * W + x; }
    // E (the west edge of x+1)
    { const p = port.get([md(x + 1, W), y, 'W'].join()); if (p) nb[k * 4 + 1] = p[1] * W + p[0]; else if (!kelpW(x + 1, y)) nb[k * 4 + 1] = y * W + md(x + 1, W); }
    // S (the north edge of y+1)
    { const p = port.get([x, md(y + 1, H), 'N'].join()); if (p) nb[k * 4 + 2] = p[1] * W + p[0]; else if (!kelpN(x, y + 1)) nb[k * 4 + 2] = md(y + 1, H) * W + x; }
    // W
    { const p = port.get([x, y, 'W'].join()); if (p) nb[k * 4 + 3] = p[1] * W + md(p[0] - 1, W); else if (!kelpW(x, y)) nb[k * 4 + 3] = y * W + md(x - 1, W); }
  }
  return { W, H, N, nb };
}

function recount(R) {
  const M = R.match.map, { W, H, N, nb } = geo(M);
  const occ = new Int32Array(N).fill(-1); // dragon id + body
  const D = new Map();
  const put = (id, team, body) => { const o = { id, team, body: body.map(s => s.y * W + s.x) }; D.set(id, o); for (const k of o.body) occ[k] = id; return o; };
  const clr = o => { for (const k of o.body) if (occ[k] === o.id) occ[k] = -1; };
  for (const d0 of M.initialDragons) put(d0.id, d0.team, d0.body);
  const tor = (a, b) => { let dx = Math.abs(a % W - b % W), dy = Math.abs(((a / W) | 0) - ((b / W) | 0)); dx = Math.min(dx, W - dx); dy = Math.min(dy, H - dy); return [dx, dy]; };
  const out = [0, 1].map(() => ({ pieces: 0, n30: 0, alive30: 0, endSac: 0, endTrap: 0, endRammed: 0, endAlive: 0, cs: 0, sacCs: 0, w6: 0, w6own: 0 }));
  const TI = t => t === 'A' ? 0 : 1;
  const pc = new Map(); // piece id -> { ti, born, nat30 }
  const pearls = new Map(); // tile -> { nat: bool, r, death: idx }
  const drops = []; let round = -1, cur = -1, afterDeath = false, lastDeath = -1, prevDeathTeam = null;
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.set(i, { nat: true });
  const deathsTeam = []; const csNow = new Map(); const freeAt = new Map();
  const stamp = new Int32Array(N); const dist = new Int16Array(N); const Q = new Int32Array(N); let st = 0;
  const nearest = k => { // nearest head of each team over static paths (bodies ignored), <= 6
    st++; let qh = 0, qt = 0; Q[qt++] = k; stamp[k] = st; dist[k] = 0; const best = [99, 99];
    const heads = new Map(); for (const o of D.values()) heads.set(o.body[0], o.team);
    while (qh < qt) { const t = Q[qh++]; const tm = heads.get(t); if (tm !== undefined) { const i = TI(tm); if (dist[t] < best[i]) best[i] = dist[t]; }
      if (dist[t] >= 6) continue; for (let j = 0; j < 4; j++) { const u = nb[t * 4 + j]; if (u < 0 || stamp[u] === st) continue; stamp[u] = st; dist[u] = dist[t] + 1; Q[qt++] = u; } }
    return best;
  };
  const convState = d => { // forward BFS from each big ally head through free tiles and d's body to d's head, <= 3
    const L = d.body.length; if (L < 2 || L > 4) return false;
    const h = d.body[0];
    for (const o of D.values()) if (o.team !== d.team) { const [dx, dy] = tor(o.body[0], h); if (dx <= 3 && dy <= 3) return false; }
    for (const a of D.values()) {
      if (a.team !== d.team || a === d || a.body.length < 8 || a.body.length < L + 4) continue;
      const [dx, dy] = tor(a.body[0], h); if (dx > 3 || dy > 3) continue;   // in the 7x7 view
      st++; let qh = 0, qt = 0; Q[qt++] = a.body[0]; stamp[a.body[0]] = st; dist[a.body[0]] = 0;
      while (qh < qt) { const t = Q[qh++]; if (dist[t] >= 3) continue;
        for (let j = 0; j < 4; j++) { const u = nb[t * 4 + j]; if (u < 0 || stamp[u] === st) continue; stamp[u] = st;
          if (u === h) return true; if (occ[u] >= 0 && occ[u] !== d.id) continue; dist[u] = dist[t] + 1; Q[qt++] = u; } }
    }
    return false;
  };
  const freeN = d => { let n = 0; const h = d.body[0]; for (let j = 0; j < 4; j++) { const u = nb[h * 4 + j]; if (u >= 0 && occ[u] < 0) n++; } return n; };
  let act = null, stepIdx = 0, jumps = 0; const pending = [];
  const flush = () => { while (pending.length) { const x = pending.shift(); const b = nearest(x.k); for (let i = 0; i < 2; i++) if (b[i] <= 6) x.w6[i] = 1; } };
  const DIR = { N: 0, E: 1, S: 2, W: 3 };
  for (const e of R.events) {
    if (afterDeath && !(e.type === 'tileChange' && e.hasPearl)) afterDeath = false;
    switch (e.type) {
      case 'dragonAction': { act = e.id === cur ? { a: e.action, tle: !!e.tle } : null; stepIdx = 0; break; }
      case 'roundStart': {
        flush();
        round = e.round;
        for (const x of drops) { if (x.eaten !== null || round - x.r > 6) continue; const b = nearest(x.k); for (let i = 0; i < 2; i++) if (b[i] <= 6) x.w6[i] = 1; }
        break;
      }
      case 'turnStart': {
        flush();
        cur = e.id; const d = D.get(cur); if (!d || round < 0) break;
        freeAt.set(cur, freeN(d));
        const c = convState(d); csNow.set(cur, c ? round : -1); if (c) out[TI(d.team)].cs++;
        break;
      }
      case 'dragonUpdate': {
        const d = D.get(e.id); if (!d) break;
        const hk = e.head.y * W + e.head.x, tk = e.tail.y * W + e.tail.x;
        clr(d);
        if (d.body[0] !== hk) { let adj = false; for (let j = 0; j < 4; j++) if (nb[d.body[0] * 4 + j] === hk) adj = true; if (!adj) jumps++; d.body.unshift(hk); }
        if (e.id === cur) stepIdx++;
        while (d.body.length > 1 && d.body[d.body.length - 1] !== tk) d.body.pop();
        for (const k of d.body) occ[k] = d.id;
        break;
      }
      case 'dragonSplit': {
        const p = D.get(e.parentId); if (!p) break;
        clr(p); p.body = e.parentBody.map(s => s.y * W + s.x); for (const k of p.body) occ[k] = p.id;
        const ch = put(e.childId, e.team, e.childBody);
        if (ch.body.length <= 3) { pc.set(ch.id, { ti: TI(e.team), born: round, nat30: 0 }); out[TI(e.team)].pieces++; }
        break;
      }
      case 'tileChange': {
        const k = e.tile.y * W + e.tile.x;
        if (e.hasPearl) {
          if (afterDeath) { const x = { k, r: round, death: lastDeath, w6: [0, 0], eaten: null }; pending.push(x); drops.push(x); pearls.set(k, x); }
          else pearls.set(k, { nat: true });
        } else {
          flush();
          const p = pearls.get(k); pearls.delete(k);
          const d = D.get(cur);
          if (p && d) {
            if (p.nat) { const q = pc.get(d.id); if (q && round <= q.born + 30) q.nat30++; }
            else p.eaten = TI(d.team);
          }
        }
        break;
      }
      case 'dragonDeath': {
        const d = D.get(e.id); if (!d) break;
        const ti = TI(d.team), mover = e.id === cur;
        let cause;
        const free = (freeAt.get(d.id) || 0) > 0;
        if (!mover) { const m = D.get(cur); cause = m && m.team === d.team ? 'allyHead' : 'rammed'; }
        else if (e.reason === 'H') {
          const steps = act && act.a && act.a.kind === 'move' ? act.a.steps : [], dir = DIR[steps[stepIdx]];
          const u = dir !== undefined ? nb[d.body[0] * 4 + dir] : -1, o = u >= 0 && occ[u] >= 0 ? D.get(occ[u]) : null;
          cause = (o && o.team === d.team) || (!o && prevDeathTeam === d.team) ? 'allyHead' : 'ram';
        } else if (e.reason === 'A') {
          if (act && act.tle) cause = 'fault';
          else if (act && act.a && act.a.kind === 'move' && stepIdx > 0) cause = 'sprintDeath';
          else cause = free ? 'sac' : 'trap';
        } else if (e.reason === 'O') {
          const steps = act && act.a && act.a.kind === 'move' ? act.a.steps : [], dir = DIR[steps[stepIdx]];
          const u = dir !== undefined ? nb[d.body[0] * 4 + dir] : -1, o = u >= 0 && occ[u] >= 0 ? D.get(occ[u]) : null;
          cause = o && o.team !== d.team ? (free ? 'enemyBody' : 'trap') : (free ? 'sac' : 'trap');
        } else cause = free ? 'sac' : 'trap';
        if (cause === 'sac' && csNow.get(d.id) === round) out[ti].sacCs++;
        const q = pc.get(d.id);
        if (q) { const o = out[ti]; if (cause === 'sac') o.endSac++; else if (cause === 'trap') o.endTrap++; else if (cause === 'rammed') o.endRammed++; if (round - q.born >= 30) o.alive30++; if (q.nat30 >= 1) o.n30++; pc.delete(d.id); }
        clr(d); D.delete(d.id);
        afterDeath = true; lastDeath = deathsTeam.length; deathsTeam.push(ti); prevDeathTeam = d.team;
        break;
      }
    }
  }
  flush();
  for (const [id, q] of pc) { const o = out[q.ti]; o.endAlive++; o.alive30++; if (q.nat30 >= 1) o.n30++; }
  for (const x of drops) for (let i = 0; i < 2; i++) if (x.w6[i]) { out[i].w6++; if (x.eaten === i) out[i].w6own++; }
  out[0].jumps = jumps; out[1].jumps = 0;
  return out;
}

// the same numbers from the extract.js cache line
function fromCache(g) {
  return ['A', 'B'].map((s, ti) => {
    const T = g[s], o = { pieces: 0, n30: 0, alive30: 0, endSac: 0, endTrap: 0, endRammed: 0, endAlive: 0, cs: 0, sacCs: 0, w6: 0, w6own: 0, jumps: 0 };
    for (const p of g.P) { if (p[0] !== ti) continue; o.pieces++; if (p[27] >= 1) o.n30++; if (p[28]) o.alive30++; if (p[12] === 1) o.endSac++; else if (p[12] === 2) o.endTrap++; else if (p[12] === 3) o.endRammed++; else if (p[12] === 0) o.endAlive++; }
    o.cs = T.b.cs ? T.b.cs.reduce((a, b) => a + b, 0) : 0; o.sacCs = T.b.sacCs ? T.b.sacCs.reduce((a, b) => a + b, 0) : 0;
    for (const [k, v] of Object.entries(T.dr)) if (k.split('|')[3] === '1') { o.w6 += v[0]; o.w6own += v[1]; }
    return o;
  });
}

function workerMain() {
  const tf = require(path.join(ROOT, 'tools', 'top_features.js'));
  const load = tf.makeLoader(tf.viewerSource());
  process.on('message', t => { try { process.send({ key: t.key, res: recount(load(t.file)) }); } catch (err) { process.send({ key: t.key, error: String(err && err.stack || err).slice(0, 300) }); } });
}
function hash32(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const every = +opt('top-every', 10), jobs = Math.min(3, +opt('jobs', 3));
  // cached games (online sets and the top cache), keyed
  const cached = new Map(), readline = require('readline');
  for (const f of fs.readdirSync(CACHE).filter(f => f.endsWith('.jsonl.gz'))) {
    const rl = readline.createInterface({ input: fs.createReadStream(path.join(CACHE, f)).pipe(zlib.createGunzip()), crlfDelay: Infinity });
    for await (const l of rl) {
      if (!l.trim()) continue;
      const g = JSON.parse(l);
      if (g.src === 'top' && hash32(g.key) % every !== 0) continue;
      cached.set(g.key, { g: fromCache(g), file: g.src === 'top' ? path.join(ROOT, 'data', 'top', String(g.battleId), g.gameId + '.replay.gz') : path.join(ROOT, 'data', 'online', g.set, 'M' + g.gameId + '.replay'), src: g.src, set: g.set || 'top' });
    }
  }
  const tasks = [...cached.entries()].map(([key, v]) => ({ key, file: v.file }));
  console.error(`recount: ${tasks.length} games (online all, top 1 in ${every} by key hash)`);
  const res = new Map(), q = tasks.slice(), t0 = Date.now(); let n = 0;
  await Promise.all(Array.from({ length: Math.min(jobs, q.length) }, () => new Promise(resolve => {
    const w = cp.fork(__filename, ['--worker']);
    const next = () => { const t = q.shift(); if (!t) { w.kill(); resolve(); return; } w.send(t); };
    w.on('message', m => { if (m.error) console.error('error', m.key, m.error); else res.set(m.key, m.res); if (++n % 200 === 0) console.error(`  ${n}/${tasks.length} ${((Date.now() - t0) / 1000).toFixed(0)}s`); next(); });
    next();
  })));
  // compare
  const F = ['pieces', 'n30', 'alive30', 'endSac', 'endTrap', 'endRammed', 'endAlive', 'cs', 'sacCs', 'w6', 'w6own', 'jumps'];
  const bySrc = {};
  for (const [key, r] of res) {
    const c = cached.get(key), grp = c.src === 'top' ? 'top' : c.set;
    const s = bySrc[grp] || (bySrc[grp] = { games: 0, eq: Object.fromEntries(F.map(f => [f, 0])), tot: Object.fromEntries(F.map(f => [f, [0, 0]])), ex: [] });
    s.games++;
    for (let ti = 0; ti < 2; ti++) for (const f of F) {
      const a = c.g[ti][f], b = r[ti][f]; s.tot[f][0] += a; s.tot[f][1] += b;
      if (a === b) s.eq[f]++; else if (s.ex.length < 3) s.ex.push(`${key} team${ti} ${f} cache ${a} recount ${b}`);
    }
  }
  const lines = [];
  for (const [grp, s] of Object.entries(bySrc)) {
    lines.push(`${grp}: ${s.games} games (team-games ${2 * s.games})`);
    for (const f of F) lines.push(`  ${f.padEnd(10)} equal ${s.eq[f]}/${2 * s.games}  totals cache ${s.tot[f][0]} recount ${s.tot[f][1]}`);
    for (const x of s.ex) lines.push('    e.g. ' + x);
  }
  const outF = path.join(__dirname, 'recount.txt');
  fs.writeFileSync(outF, lines.join('\n') + '\n');
  console.log(lines.join('\n'));
}
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
