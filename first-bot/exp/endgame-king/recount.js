#!/usr/bin/env node
// Independent recount of the endgame-king key numbers from the raw replay events only (no tools/mass_ledger.js, no
// exp/endgame-king/extract.js code). Lengths are counts: initial body, +1 per pearl eaten (a pearl tile cleared during the
// actor's turn), -(steps-1) per multi-step move, split bodies from dragonSplit. Pearl origin: the consecutive pearl tiles right
// after a dragonDeath are its drops (team of the dead dragon), every other pearl tile is natural.
// Compares, per team-game, with .cache/endgame-king/*.jsonl:
//   L300 of the final king line, final king length (also vs the replay result), and the line's r300-499 gains: natural, own
//   drops (sac + other), enemy drops, sprint cost, split losses (off + path);
//   ours: gathering dragons (first g label), labelled deaths among them, their drops eaten by the line;
//   r340 cohort (non-king length >= 4 at the first turn of r340): size, natural spawns within Manhattan 5 of its heads in
//   r340-379 and how many of them the enemy / own team ate.
// usage: node exp/endgame-king/recount.js [--top-every 10] [--jobs 3] [--only-set <set> | --top-only | --keys <file>] [--out recount-<name>.txt]   -> exp/endgame-king/recount.txt
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..'), CACHE = path.join(ROOT, '.cache', 'endgame-king');
const hash32 = s => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; };

function recount(R, us) {
  const M = R.match.map, W = M.width, H = M.height, key = (x, y) => y * W + x;
  const man = (a, b) => { const dx = Math.abs(a.x - b.x), dy = Math.abs(a.y - b.y); return Math.min(dx, W - dx) + Math.min(dy, H - dy); };
  const D = new Map(); // id -> { team, parent, len, head, born(ev), alive, eats: [[ev, round, origin]], costs: [[ev, round, c]], splits: [[ev, round, childId, childLen, kept]], firstG, lbl }
  let ev = 0;
  for (const d0 of M.initialDragons) D.set(d0.id, { id: d0.id, team: d0.team, parent: -1, len: d0.body.length, head: { x: d0.body[0].x, y: d0.body[0].y }, born: -1, alive: true, eats: [], costs: [], splits: [], firstG: -1, lastLbl: null, lblRound: -1 });
  const pearl = new Map(); // tile -> origin: 'n' or { team, id }
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearl.set(i, 'n');
  let round = -1, cur = -1, dropping = null;
  const lenAt = {}; // round -> Map(id -> len) at round start
  const spawns = []; // [round, tile]
  const natEaten = new Map(); // `${tile}:${spawnRound}` -> team
  const spawnRoundOf = new Map(); // tile -> spawn round of the natural pearl on it
  const deathDrops = new Map(); // dead id -> [eaterId, ev]...
  const dropOwner = new Map(); // tile -> dead id (drop pearls)
  const cohort = { A: [], B: [] }; let cohortDone = false;
  const posAt340 = new Map();
  for (const e of R.events) {
    ev++;
    if (dropping && !(e.type === 'tileChange' && e.hasPearl)) dropping = null;
    switch (e.type) {
      case 'roundStart':
        round = e.round;
        if ([300, 350, 400, 450].includes(round)) { const m = new Map(); for (const d of D.values()) if (d.alive) m.set(d.id, d.len); lenAt[round] = m; }
        break;
      case 'turnStart':
        cur = e.id;
        if (round >= 340 && !cohortDone) {
          cohortDone = true;
          for (const tm of ['A', 'B']) {
            let k = null; for (const d of D.values()) if (d.alive && d.team === tm && (!k || d.len > k.len || (d.len === k.len && d.id < k.id))) k = d;
            for (const d of D.values()) if (d.alive && d.team === tm && d !== k && d.len >= 4) cohort[tm].push({ id: d.id, head: { ...d.head }, r0: round });
          }
        }
        break;
      case 'dragonIndicator': {
        const d = D.get(e.id); if (!d || !us || d.team !== us) break;
        const s = (e.text || '').split('|')[0];
        if (/\sg\d+(\s|$)/.test(s) && d.firstG < 0) d.firstG = round;
        d.lastLbl = /^feed #\d+ d\d+ L\d+/.test(s) ? s : null; d.lblRound = round;
        break;
      }
      case 'dragonAction': {
        const d = D.get(e.id); if (!d) break;
        const a = e.action;
        if (a && a.kind === 'move' && a.steps.length >= 2) d.costs.push([ev, round, a.steps.length - 1]), d.len -= a.steps.length - 1;
        break;
      }
      case 'dragonUpdate': { const d = D.get(e.id); if (d) d.head = { x: e.head.x, y: e.head.y }; break; }
      case 'tileChange': {
        const k = key(e.tile.x, e.tile.y);
        if (e.hasPearl) {
          if (dropping) { pearl.set(k, dropping); }
          else { pearl.set(k, 'n'); spawns.push([round, k]); spawnRoundOf.set(k, round); }
        } else if (pearl.has(k)) {
          const o = pearl.get(k); pearl.delete(k);
          const d = D.get(cur); if (!d) break;
          d.len++;
          const origin = o === 'n' ? 0 : o.team === d.team ? 1 : 2;
          d.eats.push([ev, round, origin]);
          if (o === 'n') { if (spawnRoundOf.has(k)) natEaten.set(k + ':' + spawnRoundOf.get(k), d.team); }
          else { let q = deathDrops.get(o.id); if (!q) deathDrops.set(o.id, q = []); q.push([d.id, ev]); }
        }
        break;
      }
      case 'dragonSplit': {
        const p = D.get(e.parentId); if (!p) break;
        p.splits.push([ev, round, e.childId, e.childBody.length, e.parentBody.length]);
        p.len = e.parentBody.length; p.head = { x: e.parentBody[0].x, y: e.parentBody[0].y };
        D.set(e.childId, { id: e.childId, team: e.team, parent: p.id, len: e.childBody.length, head: { x: e.childBody[0].x, y: e.childBody[0].y }, born: ev, alive: true, eats: [], costs: [], splits: [], firstG: -1, lastLbl: null, lblRound: -1 });
        break;
      }
      case 'dragonDeath': {
        const d = D.get(e.id); if (!d) break;
        d.alive = false; d.deathRound = round; d.deathEv = ev; d.drops = Math.ceil(d.len / 2);
        d.lbl = d.lblRound === round && d.lastLbl ? 1 : 0;
        dropping = { team: d.team, id: d.id };
        break;
      }
    }
  }
  const out = {};
  for (const tm of ['A', 'B']) {
    let k = null; for (const d of D.values()) if (d.alive && d.team === tm && (!k || d.len > k.len || (d.len === k.len && d.id < k.id))) k = d;
    const res = R.result['team' + tm];
    const o = { final: k ? k.len : 0, resLongest: res.longestDragon };
    if (k) {
      const line = []; for (let x = k; x; x = x.parent >= 0 ? D.get(x.parent) : null) line.push(x);
      line.reverse();
      const win = new Map(line.map((x, i) => [x.id, [x.born, i + 1 < line.length ? line[i + 1].born : Infinity, i]]));
      const onLine = (id, e) => { const w = win.get(id); return !!w && e > w[0] && e < w[1]; };
      const g = { nat: 0, own: 0, enemy: 0, sprint: 0, split: 0 };
      for (let i = 0; i < line.length; i++) {
        const x = line[i], [w0, w1] = win.get(x.id);
        for (const q of x.eats) if (q[0] > w0 && q[0] < w1 && q[1] >= 300) g[['nat', 'own', 'enemy'][q[2]]]++;
        for (const q of x.costs) if (q[0] > w0 && q[0] < w1 && q[1] >= 300) g.sprint += q[2];
        for (const q of x.splits) if (q[0] > w0 && q[0] <= w1 && q[1] >= 300) g.split += (i + 1 < line.length && q[2] === line[i + 1].id) ? q[4] : q[3];
      }
      o.g = g;
      if (lenAt[300]) { let m = null; for (const x of line) if (x.born < Infinity && lenAt[300].has(x.id)) m = x; if (m) o.L300 = lenAt[300].get(m.id); }
      if (us === tm) {
        const G = [...D.values()].filter(d => d.team === tm && d.firstG >= 0);
        o.gath = G.length; o.gathFed = 0; o.gathFedToLine = 0;
        for (const d of G) if (!d.alive && d.lbl) { o.gathFed++; for (const q of deathDrops.get(d.id) || []) if (onLine(q[0], q[1])) o.gathFedToLine++; }
      }
    }
    // cohort near spawns
    let n = 0, sp = 0, en = 0, own = 0;
    for (const c of cohort[tm]) {
      n++;
      for (const [r, t] of spawns) {
        if (r < c.r0 || r >= c.r0 + 40) continue;
        const x = t % W, y = (t / W) | 0; if (man({ x, y }, c.head) > 5) continue;
        sp++; const who = natEaten.get(t + ':' + r); if (who === undefined) continue; if (who === tm) own++; else en++;
      }
    }
    o.coh = [n, sp, own, en];
    out[tm] = o;
  }
  return out;
}

function workerMain() {
  const { makeLoader, viewerSource } = require(path.join(ROOT, 'tools', 'top_features.js'));
  const load = makeLoader(viewerSource());
  process.on('message', t => { try { process.send({ key: t.key, r: recount(load(t.file), t.us) }); } catch (err) { process.send({ key: t.key, error: String(err && err.stack || err).split('\n').slice(0, 3).join(' | ') }); } });
}
function readJsonl(f) { const out = []; if (!fs.existsSync(f)) return out; for (const l of fs.readFileSync(f, 'utf8').split('\n')) { if (!l.trim()) continue; try { out.push(JSON.parse(l)); } catch { } } return out; }
async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const every = +opt('top-every', 10), jobs = Math.min(3, +opt('jobs', 3)), only = opt('only-set', null), outName = opt('out', 'recount.txt');
  const keysOnly = opt('keys', null) ? new Set(fs.readFileSync(path.resolve(ROOT, opt('keys')), 'utf8').split('\n').map(x => x.trim()).filter(Boolean)) : null;
  // main extraction rows
  const main = new Map();
  for (const f of fs.readdirSync(CACHE).filter(f => f.endsWith('.jsonl'))) {
    const isTop = f.startsWith('top');
    if (only && (isTop || f !== 'online-' + only + '.jsonl')) continue;
    if (argv.includes('--top-only') && !isTop) continue;
    if (keysOnly && !isTop) continue;
    for (const g of readJsonl(path.join(CACHE, f))) { if (isTop && (keysOnly ? !keysOnly.has(g.key) : hash32(g.key) % every !== 0)) continue; main.set(g.key, g); }
  }
  const tasks = [];
  for (const g of main.values()) {
    let file;
    if (g.src === 'top') { const [b, id] = g.key.split(':'); file = path.join(ROOT, 'data', 'top', b, id + '.replay.gz'); }
    else { const [set, id] = g.key.split(':'); file = path.join(ROOT, 'data', 'online', set, 'M' + id + '.replay'); }
    tasks.push({ key: g.key, file, us: g.us });
  }
  console.log('recount tasks', tasks.length);
  const res = new Map(); let errors = 0;
  await new Promise(resolve => {
    const q = tasks.slice(); let live = Math.min(jobs, q.length);
    for (let i = 0, k = live; i < k; i++) {
      const w = cp.fork(__filename, ['--worker'], { serialization: 'advanced', execArgv: ['--max-old-space-size=3072'] });
      const next = () => { const t = q.shift(); if (!t) { w.kill(); if (--live === 0) resolve(); return; } w.send(t); };
      w.on('message', m => { if (m.error) { errors++; console.error(m.key, m.error); } else res.set(m.key, m.r); if (res.size % 500 === 0) console.log('  ', res.size); next(); });
      next();
    }
  });
  // compare
  const mism = { final: 0, result: 0, L300: 0, nat: 0, own: 0, enemy: 0, sprint: 0, split: 0, gath: 0, gathFed: 0, gathFedToLine: 0, cohN: 0, cohSp: 0, cohOwn: 0, cohEn: 0 };
  const tot = { teams: 0, lineTeams: 0, nat: 0, own: 0, enemy: 0, sprint: 0, split: 0, gath: 0, gathFed: 0, gathFedToLine: 0, cohN: 0, cohSp: 0, cohOwn: 0, cohEn: 0 };
  const ex = [];
  for (const [key, r] of res) {
    const g = main.get(key);
    for (const tm of ['A', 'B']) {
      const a = r[tm], b = g[tm]; tot.teams++;
      if (a.final !== b.king) { mism.final++; if (ex.length < 10) ex.push(key + ' ' + tm + ' final ' + a.final + ' vs ' + b.king); }
      if (a.final !== a.resLongest) mism.result++;
      if (a.g && b.kid >= 0) {
        tot.lineTeams++;
        const s = i => [1, 2, 3, 4].reduce((x, bb) => x + b.dec[bb][i], 0);
        const cmp = { nat: s(0), own: s(1) + s(2), enemy: s(3), sprint: s(4), split: s(5) + s(6) };
        for (const k of Object.keys(cmp)) { tot[k] += a.g[k]; if (a.g[k] !== cmp[k]) { mism[k]++; if (ex.length < 10) ex.push(key + ' ' + tm + ' ' + k + ' ' + a.g[k] + ' vs ' + cmp[k]); } }
        if (a.L300 !== undefined && b.Lt[300] !== undefined && a.L300 !== b.Lt[300]) { mism.L300++; if (ex.length < 10) ex.push(key + ' ' + tm + ' L300 ' + a.L300 + ' vs ' + b.Lt[300]); }
      }
      if (g.us === tm && b.gath) {
        const n = b.gath.length, fed = b.gath.filter(q => q[15] === 1).length, fedLine = b.gath.filter(q => q[15] === 1).reduce((s, q) => s + q[18], 0);
        if (a.gath !== undefined) {
          tot.gath += a.gath; tot.gathFed += a.gathFed; tot.gathFedToLine += a.gathFedToLine;
          if (a.gath !== n) mism.gath++; if (a.gathFed !== fed) mism.gathFed++; if (a.gathFedToLine !== fedLine) { mism.gathFedToLine++; if (ex.length < 10) ex.push(key + ' gathFedToLine ' + a.gathFedToLine + ' vs ' + fedLine); }
        }
      }
      const C = b.coh; const cn = C.length, csp = C.reduce((s, c) => s + c[7], 0), cown = C.reduce((s, c) => s + c[8] + c[9], 0), cen = C.reduce((s, c) => s + c[10], 0);
      tot.cohN += a.coh[0]; tot.cohSp += a.coh[1]; tot.cohOwn += a.coh[2]; tot.cohEn += a.coh[3];
      if (a.coh[0] !== cn) mism.cohN++; if (a.coh[1] !== csp) { mism.cohSp++; if (ex.length < 10) ex.push(key + ' ' + tm + ' cohSp ' + a.coh[1] + ' vs ' + csp); } if (a.coh[2] !== cown) mism.cohOwn++; if (a.coh[3] !== cen) mism.cohEn++;
    }
  }
  const txt = [`recount ${new Date().toISOString()}: games ${res.size} (${keysOnly ? 'top keys from ' + opt('keys') : only ? 'set ' + only : argv.includes('--top-only') ? 'top hash % ' + every + ' == 0' : 'online all, top hash % ' + every + ' == 0'}), errors ${errors}`,
    'mismatches (expected 0): ' + JSON.stringify(mism), 'totals: ' + JSON.stringify(tot), ...ex].join('\n');
  fs.writeFileSync(path.join(__dirname, outName), txt + '\n');
  console.log(txt);
}
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
module.exports = { recount };
