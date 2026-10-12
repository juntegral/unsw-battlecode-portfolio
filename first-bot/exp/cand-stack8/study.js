#!/usr/bin/env node
// exp/cand-stack8/study.js — cand-stack8 pre-study: failure classes of F targets and of portal crossings over whole online
// sets (research/experiments/cand-stack8.md). Every game of the given sets; the records are tools/mech_check.js's own
// (analyse() with extra ledger hooks composed in), so the populations match the wave reports exactly.
//   node exp/cand-stack8/study.js <set>[+<set>...] [--jobs 3] [--json out.json]
// F episode (dragon x chosen fountain, as mech_check): sit = true fountain, our territory, no other head of ours within 3 at
// the first tag; ex = our head came within 3 steps (path, bodies ignored) on a tagged turn.
// Portal crossing failure = body (dragon + descendants) not alive 3 rounds later (mech_check's alive3).
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..'), ONLINE = path.join(ROOT, 'data', 'online');
const DIRS4 = ['N', 'E', 'S', 'W'];

function tasksOf(pool) {
  let names = {}; try { names = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'top', 'leaderboard.json'), 'utf8')).map(t => [t.id, t.name])); } catch {}
  const MAPNAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma',
    queen_of_spades: 'Queen Of Spades', schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
  const out = [];
  for (const part of pool.split('+')) {
    const abs = path.resolve(ROOT, part);
    if (fs.existsSync(path.join(abs, 'rows.jsonl'))) {
      for (const l of fs.readFileSync(path.join(abs, 'rows.jsonl'), 'utf8').split('\n')) {
        if (!l.trim()) continue;
        const row = JSON.parse(l), [opp, map, side, seed] = row.key.split(':');
        const f = path.join(abs, 'games', `${opp}_${map}_${side}_${seed}`, 'game.replay'); if (!fs.existsSync(f)) continue;
        out.push({ key: part + ':' + row.key, file: f, set: part, src: 'local', map: MAPNAME[map.replace(/_(b|10)$/, '')] || map, opp, us: side, layout: /_(b|10)$/.test(map) ? 'b' : 'a' });
      }
    } else {
      const dir = fs.existsSync(path.join(abs, 'index.json')) ? abs : path.join(ONLINE, part);
      const idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
      for (const g of idx.games || idx) {
        if (g.ourWin === null || g.ourWin === undefined) continue;
        const f = path.join(dir, 'M' + g.gameId + '.replay'); if (!fs.existsSync(f)) continue;
        out.push({ key: part + ':' + g.gameId, file: f, set: part, src: 'online', map: g.mapName, opp: names[g.opponentTeam] || String(g.opponentTeam), us: String(g.ourSide).toUpperCase(), gameId: g.gameId });
      }
    }
  }
  return out;
}

// ---- worker: mech_check.analyse with extra hooks
function workerMain() {
  const MC = require(path.join(ROOT, 'tools', 'mech_check.js'));
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const { perGame } = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
  const load = makeLoader(viewerSource());
  process.on('message', task => {
    try {
      const us = task.us, X = { deaths: {}, ftags: [], fFirst: {}, home: {}, cross: [], labels: {}, units: [], kingId: [], W: 0, H: 0 };
      let GW = 0, GH = 0, NB = null, PORT = null;
      const K = p => p.y * GW + p.x, kx = k => k % GW, ky = k => (k / GW) | 0;
      const tdk = (a, b) => { const dx = Math.abs(kx(a) - kx(b)), dy = Math.abs(ky(a) - ky(b)); return Math.min(dx, GW - dx) + Math.min(dy, GH - dy); };
      const chk = (a, b) => { const dx = Math.abs(kx(a) - kx(b)), dy = Math.abs(ky(a) - ky(b)); return Math.max(Math.min(dx, GW - dx), Math.min(dy, GH - dy)); };
      const initGeo = c => {
        GW = c.W; GH = c.H; X.W = GW; X.H = GH; const N = GW * GH; NB = new Int32Array(N * 4).fill(-1); PORT = new Uint8Array(N * 4);
        for (let k = 0; k < N; k++) for (let d = 0; d < 4; d++) {
          const x = kx(k), y = ky(k), nx = c.across(x, y, DIRS4[d]); if (!nx) continue;
          NB[k * 4 + d] = nx.y * GW + nx.x;
          const DX = [0, 1, 0, -1], DY = [-1, 0, 1, 0];
          if (nx.x !== ((x + DX[d]) % GW + GW) % GW || nx.y !== ((y + DY[d]) % GH + GH) % GH) PORT[k * 4 + d] = 1;
        }
      };
      const bfsD = (src, maxD) => { const D = new Map([[src, 0]]), q = [src]; for (let i = 0; i < q.length; i++) { const k = q[i], d = D.get(k); if (d >= maxD) continue; for (let j = 0; j < 4; j++) { const u = NB[k * 4 + j]; if (u < 0 || D.has(u)) continue; D.set(u, d + 1); q.push(u); } } return D; };
      const room = (c, src, maxD, selfId) => { // free tiles reachable from src within maxD (bodies block, tails do not)
        const tails = new Set(); for (const o of c.drag.values()) tails.add(K(o.body[o.body.length - 1]));
        const seen = new Set([src]), q = [[src, 0]]; let n = 0;
        for (let i = 0; i < q.length; i++) { const [k, d] = q[i]; if (d >= maxD) continue; for (let j = 0; j < 4; j++) { const u = NB[k * 4 + j]; if (u < 0 || seen.has(u)) continue; seen.add(u); const o = c.occ.get(u); if (o !== undefined && !tails.has(u)) continue; n++; q.push([u, d + 1]); } }
        return n;
      };
      X.pullPre = {}; X.pull = []; X.natEat = [];
      const mine = {
        turn(d, r, c) {
          if (!NB) initGeo(c);
          if (X.units[r] === undefined) { let u = 0; for (const o of c.drag.values()) if (o.team === us) u++; X.units[r] = u; const kg = c.kingOf(us); X.kingId[r] = kg ? [kg.id, kg.body.length] : null; }
          if (d.team === us && X.home[d.id] === undefined) { const h = K(d.body[0]); X.home[d.id] = [h, c.terr[h], r]; }
        },
        indicator(e, r, c) {
          const d = c.drag.get(e.id); if (!d || d.team !== us) return;
          X.labels[e.id + ':' + r] = e.text;
          const m = /(?:^|\s)F(\d+)@(\d+),(\d+)(?:\s|$)/.exec(e.text || '');
          if (!m) return;
          const a = +m[3] * c.W + +m[2], h = K(d.body[0]);
          X.ftags.push([e.id, r, a, +m[1]]);
          { // coordinator 18:0x: F must not pull a dragon away from a natural pearl it is the unique nearest head to. Candidates: natural
            // pearls within path 7 of our head (bodies ignored), outside the target group (path > 3 from the target), no other head
            // (any team) as near or nearer
            const Dh = bfsD(h, 7), Dg = bfsD(a, 3), cand = [];
            for (const [k, o] of c.pearls) { if (o !== -1 || !Dh.has(k) || Dg.has(k)) continue; const dm = Dh.get(k), Dp = bfsD(k, dm); let uniq = true;
              for (const o2 of c.drag.values()) { if (o2.id === d.id) continue; const oh = K(o2.body[0]); if (Dp.has(oh)) { uniq = false; break; } }
              if (uniq) cand.push([k, dm]); }
            if (cand.length) X.pullPre[e.id] = { r, a, cand };
          }
          const fk = e.id + ':' + a;
          if (!X.fFirst[fk]) { // the first tag of this episode (before the move): who else is near the target
            const Da = bfsD(a, 40), others = [];
            for (const o of c.drag.values()) {
              if (o.team !== us || o.id === d.id) continue;
              const oh = K(o.body[0]), da = Da.has(oh) ? Da.get(oh) : 99;
              if (da <= 6) others.push([o.id, da, o.body.length, chk(oh, h) <= 3 ? 1 : 0]);
            }
            let enemyNear = 99; for (const o of c.drag.values()) if (o.team !== us) { const oh = K(o.body[0]); const da = Da.has(oh) ? Da.get(oh) : 99; if (da < enemyNear) enemyNear = da; }
            X.fFirst[fk] = { mine: Da.has(h) ? Da.get(h) : 99, others, enemyNear, terrA: c.terr[a], len: d.body.length };
          }
        },
        action(d, e, r, c, before) {
          if (d.team === us && X.pullPre[d.id] && X.pullPre[d.id].r === r) {
            const q = X.pullPre[d.id]; delete X.pullPre[d.id];
            const h2 = K(d.body[0]);
            for (const [k, dm] of q.cand) { const ate = !c.pearls.has(k); const D2 = bfsD(k, dm + 2); const d2 = D2.has(h2) ? D2.get(h2) : dm + 3;
              X.pull.push([d.id, r, q.a, k, dm, d2, ate ? 1 : 0, e.action && e.action.kind === 'move' ? 1 : 0]); }
          }
          if (d.team !== us || !(d.portalSteps > 0)) return;
          const a4 = e.action || {}; if (a4.kind !== 'move') return;
          let h = K(before[0]), exitT = -1, stepI = -1; const n = a4.steps.length;
          let fromT = -1, pdir = null;
          for (let i = 0; i < n; i++) { const di = DIRS4.indexOf(a4.steps[i]), u = NB[h * 4 + di]; if (u < 0) break; if (PORT[h * 4 + di] && exitT < 0) { exitT = u; stepI = i; fromT = h; pdir = a4.steps[i]; } h = u; }
          if (exitT < 0) return;
          let eH = 99, eHL = 0, oH = 99, oB = 99;
          for (const o of c.drag.values()) {
            if (o.id === d.id) continue;
            const oh = K(o.body[0]), dd = tdk(oh, exitT);
            if (o.team !== us) { if (dd < eH) { eH = dd; eHL = o.body.length; } }
            else { if (dd < oH) oH = dd; for (const s of o.body) { const x = tdk(K(s), exitT); if (x < oB) oB = x; } }
          }
          const fate = d.fate;
          X.cross.push({ id: d.id, r, exitT, stepI, fromT, dir: pdir, blocker: d.fate && d.fate.hit !== undefined ? d.fate.hit : null, steps: n, L: before.length, eH, eHL, oH, oB, room4: room(c, K(d.body[0]), 4, d.id),
            fate: fate ? { reason: fate.reason, step: fate.step, hitTeam: fate.hitTeam === undefined ? null : fate.hitTeam === us ? 'us' : 'them', hitLen: fate.hitLen || 0 } : null });
        },
        eat(d, tile, o, r) { if (o < 0) X.natEat.push([tile, r, d.team === us ? 1 : 2, d.id]); },
        death(d, rec, idx, other, r, c) {
          if (d.team !== us) return;
          X.deaths[d.id] = { r, cause: rec.cause, oTeam: other ? (other.team === us ? 'us' : 'them') : null, oLen: other ? other.body.length : 0, oId: other ? other.id : null, t: K(d.body[0]), L: rec.len };
        },
      };
      const compose = hooks => { const h2 = {}; for (const k of new Set([...Object.keys(hooks), ...Object.keys(mine)])) h2[k] = (...a) => { if (hooks[k]) hooks[k](...a); if (mine[k]) mine[k](...a); }; return h2; };
      const res = MC.analyse(load(task.file), task, (R, info, hooks) => perGame(R, info, compose(hooks)));
      const recs = res.recs.filter(x => x.k === 'fguard' || x.k === 'portal');
      { // probe status of each crossing: our ping of the previous round from the tile we crossed from, in the crossing direction
        const R2 = load(task.file); let rr = -1; const pings = new Map();
        for (const ev of R2.events) { if (ev.type === 'roundStart') rr = ev.round; else if (ev.type === 'sonarPing' && X.home[ev.senderId] !== undefined) pings.set(ev.senderId + ':' + rr + ':' + (ev.origin.y * X.W + ev.origin.x) + ':' + ev.direction, ev.hitKind || 'none'); }
        for (const cr of X.cross) { const hk = pings.get(cr.id + ':' + (cr.r - 1) + ':' + cr.fromT + ':' + cr.dir); cr.probe = hk === undefined ? 'none' : /ally|enemy/.test(hk) ? 'dirty:' + hk : 'clean'; }
      }
      process.send({ ok: true, res: { key: res.key, set: task.set, map: res.map, opp: res.opp, game: res.game, us, rounds: res.rounds, recs, X } });
    } catch (err) { process.send({ ok: false, key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 5).join(' | ') }); }
  });
}

async function runAll(tasks, jobs) {
  const out = [], errors = [], q = tasks.slice();
  await Promise.all(Array.from({ length: Math.min(jobs, q.length) }, () => new Promise(resolve => {
    const w = cp.fork(__filename, ['--worker'], { stdio: ['ignore', 'inherit', 'inherit', 'ipc'] });
    const next = () => { const t = q.shift(); if (!t) { w.kill(); resolve(); return; } w.send(t); };
    w.on('message', m => { if (m.ok) out.push(m.res); else errors.push(m); next(); });
    next();
  })));
  return { games: out, errors };
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
  const tasks = tasksOf(argv[0]);
  const { games, errors } = await runAll(tasks, +opt('--jobs', 3));
  for (const e of errors) console.error('error', e.key, e.error);
  fs.writeFileSync(path.resolve(opt('--json', path.join(__dirname, 'study.json'))), JSON.stringify(games));
  console.log(`games ${games.length}, errors ${errors.length}`);
}
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
