#!/usr/bin/env node
// Contest losses, stage 2 and 3 (research/observations/intake-gap.md): natural pearls that spawned nearer to one of our heads
// (static path distance, bodies ignored, at the round start) but were eaten by the opponent. For every such pearl of our online
// games (all our elite sets), what was our nearest head doing? Replays only.
//
// usage: node exp/intake-gap/contest.js [--sets a,b,...] [--jobs 3] [--out .cache/intake-gap/contest.jsonl]
//   then: node exp/intake-gap/contest.js --report [--in .cache/intake-gap/contest.jsonl] [--md exp/intake-gap/contest.md]
//
// Per pearl with race U (our nearest head strictly nearer than theirs at its spawn): the designated head = our nearest head at spawn.
// Every round start while the pearl lives: path distance from the designated head (local BFS from the pearl, radius 20), its label
// kind (its last INDICATOR), and our / their nearest distances. At the pearl's end, a class:
//   died     the designated head died before the pearl was eaten
//   away     the designated head ended farther from the pearl than at spawn (it went elsewhere), by its label majority over the life
//   stalled  neither nearer nor farther (circling, blocked)
//   raced    it came nearer but the opponent ate first: 'sprint' if the eater's move had >= 2 steps, else 'walk'
// and 'view' = the pearl was inside the designated head's 7x7 view at spawn. Pearls we ate get the same record (outcome us / ally).
// The same is recorded from the opponent's side (race O pearls, their designated head) for the comparison.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..', '..');
const ML = require(path.join(ROOT, 'tools', 'mass_ledger.js'));
const X = require(path.join(ROOT, 'exp', 'territory-analysis', 'extract.js'));
const E = require('./extract.js');
const argv = process.argv.slice(2), opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
const SETS_DEFAULT = ['cand-stack5-online', 'cand-stack6-online', 'cand-stack6-online-r2', 'cand-stack7-online', 'cand-stack8-online', 'cand-stack9-online',
  'cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3', 'cand-stack1-online', 'cand-stack2-online', 'cand-stack3-online', 'cand-stack4-online'];
const INF = 999;

function analyse(R, info) {
  const M = R.match.map, W = M.width, H = M.height, nInit = M.initialDragons.length;
  const linfo = { map: info.map }; if (info.map === 'Prisoners Dilemma') linfo.variant = nInit === 10 ? 'PD10' : 'PD6';
  const G = X.geometry(R), N = G.N, nb = G.nb, terr = G.terr;
  const us = info.us === 'B' ? 1 : 0, TI = tm => tm === 'A' ? 0 : 1;
  const dist = [new Int16Array(N), new Int16Array(N)], src = [new Int32Array(N), new Int32Array(N)], Q = new Int32Array(N + 8);
  const bfs = (ti, heads) => { const d = dist[ti], s = src[ti]; d.fill(-1); let qh = 0, qt = 0; for (const h of heads) if (d[h.k] < 0) { d[h.k] = 0; s[h.k] = h.id; Q[qt++] = h.k; } while (qh < qt) { const k = Q[qh++]; for (let j = 0; j < 4; j++) { const u = nb[k * 4 + j]; if (u < 0 || d[u] >= 0) continue; d[u] = d[k] + 1; s[u] = s[k]; Q[qt++] = u; } } };
  const lbD = new Int16Array(N), lbS = new Int32Array(N); let stamp = 0;
  const localBfs = (from, r) => { stamp++; let qh = 0, qt = 0; lbS[from] = stamp; lbD[from] = 0; Q[qt++] = from; while (qh < qt) { const k = Q[qh++]; if (lbD[k] >= r) continue; for (let j = 0; j < 4; j++) { const u = nb[k * 4 + j]; if (u < 0 || lbS[u] === stamp) continue; lbS[u] = stamp; lbD[u] = lbD[k] + 1; Q[qt++] = u; } } };
  const lget = k => lbS[k] === stamp ? lbD[k] : INF;
  const label = new Map(), lastKind = new Map();
  const live = new Map(); // tile -> record
  const out = []; let lastRound = -99;
  const cheb = (a, b) => { const ax = a % W, ay = (a / W) | 0, bx = b % W, by = (b / W) | 0; let dx = Math.abs(ax - bx), dy = Math.abs(ay - by); dx = Math.min(dx, W - dx); dy = Math.min(dy, H - dy); return Math.max(dx, dy); };
  let steps = new Map();
  function roundStart(round, ctx) {
    const heads = [[], []]; const headOf = new Map();
    for (const d of ctx.drag.values()) { const h = d.body[0], k = h.y * W + h.x; heads[TI(d.team)].push({ k, id: d.id, len: d.body.length }); headOf.set(d.id, { k, len: d.body.length, team: TI(d.team) }); }
    bfs(0, heads[0]); bfs(1, heads[1]);
    // follow live tracked pearls
    for (const p of live.values()) {
      const h = headOf.get(p.hid);
      if (!h) { if (p.diedR < 0) p.diedR = round; continue; }
      localBfs(p.k, 20); const dd = lget(h.k);
      p.dLast = dd; if (dd < p.dMin) p.dMin = dd;
      const kind = lastKind.get(p.hid) || 'plain'; p.kinds[kind] = (p.kinds[kind] || 0) + 1;
      p.rounds++;
    }
    // new natural pearls
    for (const [k, o] of ctx.pearls) {
      if (o !== -1 || live.has(k)) continue;
      const dU = dist[us][k] < 0 ? INF : dist[us][k], dO = dist[1 - us][k] < 0 ? INF : dist[1 - us][k];
      let side = -1; if (dU < dO) side = us; else if (dO < dU) side = 1 - us;
      const rec = { k, r0: round, init: round === 0 ? 1 : 0, side: side === us ? 'U' : side >= 0 ? 'O' : 'T', dU, dO, terr: terr[k] === 0 ? 'n' : terr[k] === us + 1 ? 'mine' : 'theirs', hid: -1, hlen: 0, view: 0, kinds: {}, dLast: -1, dMin: INF, diedR: -1, rounds: 0, fate: 'none', eatR: -1, eaterLen: 0, eaterSprint: 0, eaterDes: 0, hk0: 'plain' };
      if (side >= 0) {
        const hid = src[side][k]; const h = headOf.get(hid);
        rec.hid = hid; rec.hlen = h ? h.len : 0; rec.view = h && cheb(h.k, k) <= 3 ? 1 : 0; rec.dLast = side === us ? dU : dO; rec.dMin = rec.dLast; rec.hk0 = lastKind.get(hid) || 'plain';
      }
      live.set(k, rec);
    }
  }
  const hooks = {
    turn(d, round, ctx) { if (round !== lastRound) { lastRound = round; roundStart(round, ctx); } label.set(d.id, null); },
    indicator(e) { label.set(e.id, e.text); },
    action(d, e, round) { const ti = TI(d.team); lastKind.set(d.id, ti === us ? E.labelKind(label.get(d.id)) : (e.action && e.action.kind === 'move' && e.action.steps.length >= 2 ? 'sprint' : 'plain')); steps.set(d.id, e.action && e.action.kind === 'move' ? e.action.steps.length : 0); },
    eat(d, k, o, round) {
      if (o >= 0) return; const p = live.get(k); if (!p) return; live.delete(k);
      const ti = TI(d.team);
      p.fate = ti === us ? 'us' : 'them'; p.eatR = round; p.eaterLen = d.body.length; p.eaterSprint = (steps.get(d.id) || 0) >= 2 ? 1 : 0; p.eaterDes = d.id === p.hid ? 1 : 0;
      finish(p);
    },
    end(rounds) { for (const p of live.values()) { p.eatR = rounds - 1; finish(p); } live.clear(); },
  };
  function finish(p) {
    if (p.side === 'T') return;
    const d0 = p.side === 'U' ? p.dU : p.dO;
    let cls;
    if (p.diedR >= 0 && (p.eatR < 0 || p.diedR <= p.eatR)) cls = 'died';
    else if (p.dLast > d0) cls = 'away';
    else if (p.dLast === d0 && p.rounds > 0) cls = 'stalled';
    else cls = 'raced';
    let top = 'plain', tn = -1; for (const [k2, v] of Object.entries(p.kinds)) if (v > tn) { tn = v; top = k2; }
    out.push([p.side, p.r0, p.k, p.terr, p.dU, p.dO, p.hid, p.hlen, p.view, p.fate, p.eatR, p.eaterLen, p.eaterSprint, p.eaterDes, cls, top, p.hk0, p.init]);
  }
  const g = ML.perGame(R, linfo, hooks);
  return { rounds: g.rounds, chk: g.chk, P: out };
}

function tasks(sets) {
  const out = [];
  for (const set of sets) {
    const dir = path.join(ROOT, 'data', 'online', set); if (!fs.existsSync(path.join(dir, 'index.json'))) continue;
    const idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
    for (const gm of idx.games || idx) { const f = path.join(dir, 'M' + gm.gameId + '.replay'); if (fs.existsSync(f)) out.push({ key: set + ':' + gm.gameId, file: f, info: { set, map: gm.mapName, us: String(gm.ourSide).toUpperCase(), gameId: gm.gameId, opp: gm.opponentTeam } }); }
  }
  return out;
}
function worker() {
  const RL = require('./rawload.js');
  process.on('message', t => { try { const R = RL.load(t.file); const r = analyse(R, t.info); process.send({ line: JSON.stringify({ key: t.key, ...t.info, kind: ML.R500.includes(t.info.map) ? 'r500' : 'elim', ...r }) }); } catch (e) { process.send({ error: t.key + ' ' + String(e.stack || e).split('\n').slice(0, 4).join(' | ') }); } });
}
async function run() {
  const sets = (opt('sets', '') || '').split(',').filter(Boolean); const T = tasks(sets.length ? sets : SETS_DEFAULT);
  const outF = path.resolve(ROOT, opt('out', '.cache/intake-gap/contest.jsonl'));
  const done = new Set(); if (fs.existsSync(outF)) for (const l of fs.readFileSync(outF, 'utf8').split('\n')) { const m = /^\{"key":"([^"]+)"/.exec(l); if (m) done.add(m[1]); }
  const todo = T.filter(t => !done.has(t.key)); const jobs = Math.min(3, +opt('jobs', 3));
  console.log(`contest: ${T.length} games, cached ${done.size}, to do ${todo.length}`);
  const fd = fs.openSync(outF, 'a'); let n = 0;
  await new Promise(res => { let live = Math.min(jobs, todo.length); if (!live) return res(); for (let i = 0, k = live; i < k; i++) { const w = cp.fork(__filename, ['--worker']); const next = () => { const t = todo.shift(); if (!t) { w.kill(); if (--live === 0) res(); return; } w.send(t); }; w.on('message', m => { if (m.error) console.error(m.error); else fs.writeSync(fd, m.line + '\n'); if (++n % 50 === 0) console.log('  ' + n); next(); }); next(); } });
  fs.closeSync(fd); console.log('done', n);
}
// report: classes with sizes, by era and family; examples for the film (selection rule in the doc)
function report() {
  const inF = path.resolve(ROOT, opt('in', '.cache/intake-gap/contest.jsonl')), md = path.resolve(ROOT, opt('md', 'exp/intake-gap/contest.md'));
  const era = s => /stack[5-8]/.test(s) ? 'stack5-8' : /stack9/.test(s) ? 'stack9' : /stack[1-4]/.test(s) ? 'stack1-4' : /merge2/.test(s) ? 'merge2' : 'other';
  const acc = {}, ex = []; let games = 0, chk = 0;
  const A = k => acc[k] || (acc[k] = { games: 0, n: 0, fate: {}, cls: {}, clsView: {}, top: {}, hk0: {}, dist: {}, eaterSprint: 0, lostN: 0, lostDes: 0, lostD: {}, lostLen: {}, lostTerr: {}, lostPh: {} });
  for (const l of fs.readFileSync(inF, 'utf8').split('\n')) {
    if (!l.trim()) continue; const g = JSON.parse(l); games++; for (const v of Object.values(g.chk)) chk += v;
    const keys = [era(g.set) + '|' + g.kind, era(g.set) + '|all'];
    for (const k of keys) A(k).games++;
    for (const p of g.P) {
      const [side, r0, k, terr, dU, dO, hid, hlen, view, fate, eatR, eLen, eSpr, eDes, cls, top, hk0, init] = p;
      const lost = side === 'U' ? fate === 'them' : fate === 'us';   // the designated side lost it to the other team
      const sideKey = side === 'U' ? 'U' : 'O';
      for (const kk of keys) {
        const a = A(kk + '|' + sideKey); a.n++; a.fate[fate] = (a.fate[fate] || 0) + 1;
        if (lost) {
          a.lostN++; a.cls[cls] = (a.cls[cls] || 0) + 1; a.clsView[cls + '/' + view] = (a.clsView[cls + '/' + view] || 0) + 1;
          a.top[cls + ':' + top] = (a.top[cls + ':' + top] || 0) + 1; a.hk0[hk0] = (a.hk0[hk0] || 0) + 1; a.eaterSprint += eSpr;
          const dd = side === 'U' ? dU : dO, gap = (side === 'U' ? dO - dU : dU - dO);
          const db = dd <= 1 ? '<=1' : dd <= 3 ? '2-3' : dd <= 6 ? '4-6' : '7+'; a.lostD[db] = (a.lostD[db] || 0) + 1;
          const gb = gap <= 1 ? 'lead1' : gap <= 3 ? 'lead2-3' : 'lead4+'; a.lostD[gb] = (a.lostD[gb] || 0) + 1;
          const lb = hlen <= 2 ? '2' : hlen <= 4 ? '3-4' : hlen <= 7 ? '5-7' : '8+'; a.lostLen[lb] = (a.lostLen[lb] || 0) + 1;
          a.lostTerr[terr] = (a.lostTerr[terr] || 0) + 1;
          const ph = r0 < 50 ? 'r0-49' : r0 < 100 ? 'r50-99' : r0 < 250 ? 'r100-249' : r0 < 350 ? 'r250-349' : 'r350+'; a.lostPh[ph] = (a.lostPh[ph] || 0) + 1;
        }
      }
      if (side === 'U' && fate === 'them' && /stack[5-8]/.test(g.set)) ex.push({ key: g.key, map: g.map, r0, eatR, k, x: k % 1000, hid, hlen, dU, dO, cls, top, view, eSpr });
    }
  }
  const L = ['# contest losses (machine tables)', '', `games ${games}, ledger checks summed ${chk}`, ''];
  const pc = (a, b) => b ? Math.round(100 * a / b) + '%' : '–';
  for (const k of Object.keys(acc).filter(k => k.split('|').length === 3).sort()) {
    const a = acc[k], g = acc[k.split('|').slice(0, 2).join('|')].games;
    L.push(`## ${k} (games ${g}; designated-side pearls ${a.n}, ${(a.n / g).toFixed(1)}/game; lost to the other team ${a.lostN} = ${(a.lostN / g).toFixed(1)}/game, ${pc(a.lostN, a.n)})`, '');
    L.push('fate: ' + Object.entries(a.fate).map(([x, v]) => `${x} ${pc(v, a.n)}`).join(', '));
    L.push('lost by class: ' + Object.entries(a.cls).sort((x, y) => y[1] - x[1]).map(([x, v]) => `${x} ${v} (${pc(v, a.lostN)})`).join(', '));
    L.push('lost by class/view at spawn: ' + Object.entries(a.clsView).sort((x, y) => y[1] - x[1]).map(([x, v]) => `${x} ${pc(v, a.lostN)}`).join(', '));
    L.push('lost by class:label majority: ' + Object.entries(a.top).sort((x, y) => y[1] - x[1]).slice(0, 14).map(([x, v]) => `${x} ${pc(v, a.lostN)}`).join(', '));
    L.push('lost by designated head label at spawn: ' + Object.entries(a.hk0).sort((x, y) => y[1] - x[1]).map(([x, v]) => `${x} ${pc(v, a.lostN)}`).join(', '));
    L.push('lost: eater sprinted ' + pc(a.eaterSprint, a.lostN) + '; distance/lead at spawn: ' + Object.entries(a.lostD).map(([x, v]) => `${x} ${pc(v, a.lostN)}`).join(', '));
    L.push('lost by designated head length: ' + Object.entries(a.lostLen).map(([x, v]) => `${x} ${pc(v, a.lostN)}`).join(', ') + '; by territory: ' + Object.entries(a.lostTerr).map(([x, v]) => `${x} ${pc(v, a.lostN)}`).join(', ') + '; by phase: ' + Object.entries(a.lostPh).map(([x, v]) => `${x} ${(v / g).toFixed(1)}/game`).join(', '), '');
  }
  fs.writeFileSync(md, L.join('\n'));
  fs.writeFileSync(md.replace(/\.md$/, '-examples.json'), JSON.stringify(ex));
  console.log('-> ' + path.relative(ROOT, md));
}
if (argv[0] === '--worker') worker();
else if (argv.includes('--report')) report();
else run();
