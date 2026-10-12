#!/usr/bin/env node
// Per-game features of top-team replays (data/top) for heuristic research. Reads replays only; runs no games.
// usage: node tools/top_features.js [--limit N] [--jobs K] [--force]
//   Reads data/top/index.jsonl and appends one JSON line per game to data/top/features.jsonl, skipping games that are
//   already there. --limit N processes at most N of the selected games. --jobs K runs K worker threads (default 6).
//   --force recomputes the selected games and rewrites the file atomically (rows of other games are kept).
//   Schema, definitions and limitations: docs/top_features.md.
// Body reconstruction is adapted from g5's lineages/g5/tools/analyze.js (moves, sprints, portals, splits, deaths):
// each step is simulated and checked against the replay's own dragonUpdate head/tail (meta.simMismatches).
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), vm = require('vm'), cp = require('child_process');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

const ROOT = path.resolve(__dirname, '..'), TOP = path.join(ROOT, 'data', 'top');
const INDEX = path.join(TOP, 'index.jsonl'), OUT = path.join(TOP, 'features.jsonl'), LOCK = OUT + '.lock';
const ROUNDS = 500, TL_STEP = 10, WIN = 50, NWIN = ROUNDS / WIN;
const DX = { N: 0, E: 1, S: 0, W: -1 }, DY = { N: -1, E: 0, S: 1, W: 0 };
const TEAMS = ['A', 'B'];
const zeros = () => new Array(NWIN).fill(0);
const win = r => Math.max(0, Math.min(NWIN - 1, Math.floor(r / WIN)));
const gameKey = row => row.battleId + ':' + row.gameId;
const replayFile = row => path.join(TOP, String(row.battleId), row.gameId + '.replay.gz');

// ---------------------------------------------------------------------------------------------------------------
// Replay loader. Same parse as tools/replay.js (the official viewer's parser, run in a vm), plus the fields that
// its format-1 schema cannot see. Server replays are format 2; the layout below is the one in the unswbc 1.1.0
// viewer's schema (UNSW/.unswbc-110/unswbc/replay-viewer.vsix), which tools/viewer.js does not use:
//  - EventSonarPing grew from 16 to 32 data bytes. The old `value` (UInt32 @8) is always 0 in format 2; the sent
//    64-bit value is `value64` UInt64 @16 (-> e.value64, BigInt) and `hitKind` UInt16 @24 says what the ray stopped
//    on (-> e.hitKind, a HIT_KIND name).
//  - The Replay root grew from 8 to 16 data bytes: union `seed` (UInt16 @4 = 1 when set, UInt64 @8) (-> R.seed, hex).
function viewerSource() {
  const { root } = require('./viewer.js');
  const vsix = path.join(root, '.venv-ppo/lib/python3.13/site-packages/unswbc/replay-viewer.vsix');
  return cp.execFileSync('unzip', ['-p', vsix, 'extension/dist/webview/webview.js'], { maxBuffer: 8 << 20 }).toString();
}
function makeLoader(src) {
  const cut = src.indexOf('var Af=B(');
  if (cut < 0) throw Error('unexpected replay-viewer build (parser cut point not found)');
  const code = src.slice(0, cut).replace('if(n.formatVersion>1)', 'if(n.formatVersion>2)') +
    'globalThis.__tf={Df:Df,bf:bf,Of:Of,cu:$};})();';
  const ctx = { TextEncoder, TextDecoder };
  vm.runInNewContext(code, ctx, { timeout: 5000 });
  const { Df, bf, Of, cu } = ctx.__tf || {};
  if (![Df, bf, Of].every(f => typeof f === 'function') || !cu || typeof cu.getUint64 !== 'function')
    throw Error('unexpected replay-viewer build (parser internals not found)');
  return function load(file) {
    const raw = fs.readFileSync(file);
    const root = Df(file.endsWith('.gz') ? zlib.gunzipSync(raw) : raw);
    const list = root.events, n = list.length, events = new Array(n);
    for (let i = 0; i < n; i++) {
      const ev = list.get(i), o = bf(ev);
      if (o.type === 'sonarPing') {
        const sp = ev.sonarPing;
        if (cu.getSize(sp).dataByteLength >= 32) { o.value64 = cu.getUint64(16, sp); o.hitKind = HIT_KIND[cu.getUint16(24, sp)]; }
        else o.value64 = BigInt(o.value);
      }
      events[i] = o;
    }
    const R = Of(root, events);
    R.formatVersion = root.formatVersion;
    R.seed = cu.getSize(root).dataByteLength >= 16 && cu.getUint16(4, root) === 1 ? cu.getUint64(8, root).toString(16).padStart(16, '0') : null;
    return R;
  };
}
// hitKind names as in the 1.1.0 viewer (0 UNKNOWN, 1 EMPTY = reached nothing, 2 KELP, 3 ALLY, ...), relative to the
// sender; a ray that comes back to the sender counts as ally/allyHead. meta.checks.hitKind counts pings where it
// disagrees with the reconstructed board (0 over 464 games, 2026-09-29; only codes 2..6 occurred).
const HIT_KIND = [undefined, 'empty', 'kelp', 'ally', 'allyHead', 'enemy', 'enemyHead'];

// ---------------------------------------------------------------------------------------------------------------
// Feature extraction for one parsed replay R and its index row.
function extract(R, row) {
  const M = R.match.map, W = M.width, H = M.height;
  const wx = x => ((x % W) + W) % W, wy = y => ((y % H) + H) % H;
  const key = (x, y) => y * W + x;
  // --- map geometry (from analyze.js) ---
  // portal edges: canonical "x,y,N|W" -> partner {x,y,side}
  const canon = e => e.side === 'S' ? { x: e.x, y: wy(e.y + 1), side: 'N' } : e.side === 'E' ? { x: wx(e.x + 1), y: e.y, side: 'W' } : { x: e.x, y: e.y, side: e.side };
  const portal = new Map();
  for (const pr of M.portals || []) { if (pr.length !== 2) continue; const a = canon(pr[0]), b = canon(pr[1]); portal.set(a.x + ',' + a.y + ',' + a.side, b); portal.set(b.x + ',' + b.y + ',' + b.side, a); }
  // kelp: hedges (H+1)*W indexed r*W+c (north edge of row r), vedges H*(W+1) indexed r*(W+1)+c (west edge of col c)
  const hk = (x, y) => M.initialHEdges[wy(y) * W + x] === 1 || (wy(y) === 0 && M.initialHEdges[H * W + x] === 1);
  const vk = (x, y) => M.initialVEdges[y * (W + 1) + wx(x)] === 1 || (wx(x) === 0 && M.initialVEdges[y * (W + 1) + W] === 1);
  function across(x, y, d) {
    let ek, kelp;
    if (d === 'N') { ek = x + ',' + y + ',N'; kelp = hk(x, y); }
    else if (d === 'S') { ek = x + ',' + wy(y + 1) + ',N'; kelp = hk(x, y + 1); }
    else if (d === 'W') { ek = x + ',' + y + ',W'; kelp = vk(x, y); }
    else { ek = wx(x + 1) + ',' + y + ',W'; kelp = vk(x + 1, y); }
    const p = portal.get(ek);
    if (p) {
      if (d === 'N') return { x: p.x, y: wy(p.y - 1) };
      if (d === 'S') return { x: p.x, y: p.y };
      if (d === 'W') return { x: wx(p.x - 1), y: p.y };
      return { x: p.x, y: p.y };
    }
    if (kelp) return null;
    return { x: wx(x + DX[d]), y: wy(y + DY[d]) };
  }

  // --- state ---
  const drag = new Map(); // id -> {id, team, body:[{x,y}] head first, born, fate, expect, act}
  const occ = new Map();  // tile -> id
  const setOcc = d => { for (const s of d.body) occ.set(key(s.x, s.y), d.id); };
  const clrOcc = d => { for (const s of d.body) if (occ.get(key(s.x, s.y)) === d.id) occ.delete(key(s.x, s.y)); };
  const pearls = new Set();
  if (M.initialTiles) for (let i = 0; i < M.initialTiles.length; i++) if (M.initialTiles[i] === 2) pearls.add(i);
  for (const d0 of M.initialDragons) {
    const o = { id: d0.id, team: d0.team, body: d0.body.map(s => ({ x: s.x, y: s.y })), born: 0, fate: null, expect: [], act: null };
    drag.set(o.id, o); setOcc(o);
  }
  const T = {};
  for (const tm of TEAMS) T[tm] = {
    timeline: [], splits: [], deaths: [], eaten: zeros(), sprints: zeros(), longSprints: zeros(),
    sonar: { sent: zeros(), self: zeros(), ally: zeros(), enemy: zeros(), none: zeros(), enemyHead: zeros() },
    values: new Set(), pings: 0, turns: 0, eatEvents: 0,
  };
  // consistency checks (all expected 0): head/tail per step, death cause, split lengths, eaten pearls,
  // pearls dropped at death (= ceil(len/2), checks deaths[].len), sonar hitKind, pings of unknown dragons
  const chk = { updates: 0, deaths: 0, splits: 0, eaten: 0, drops: 0, hitKind: 0, pings: 0 };
  let round = -1, cur = -1, lastSnap = -TL_STEP;
  let drop = null; // pearls expected from the last death: its tileChange events follow the dragonDeath directly
  const closeDrop = () => { if (drop) { if (drop.got !== drop.want) chk.drops++; drop = null; } };
  const snapshot = r => {
    for (const tm of TEAMS) {
      let units = 0, total = 0, longest = 0;
      for (const d of drag.values()) if (d.team === tm) { units++; total += d.body.length; if (d.body.length > longest) longest = d.body.length; }
      T[tm].timeline.push({ r, units, total, longest });
    }
    lastSnap = r;
  };
  const units = tm => { let n = 0; for (const d of drag.values()) if (d.team === tm) n++; return n; };

  for (const e of R.events) {
    if (drop && !(e.type === 'tileChange' && e.hasPearl)) closeDrop();
    switch (e.type) {
      case 'roundStart':
        round = e.round;
        if (round % TL_STEP === 0 && round <= ROUNDS) snapshot(round);
        break;
      case 'turnStart': {
        cur = e.id;
        const d = drag.get(cur);
        if (d) { T[d.team].turns++; d.fate = null; d.expect = []; d.act = null; d.tle = false; }
        break;
      }
      case 'tileChange': {
        const k = key(e.tile.x, e.tile.y);
        if (e.hasPearl) { pearls.add(k); if (drop) drop.got++; }
        else {
          pearls.delete(k);
          const d = drag.get(cur);
          if (d && round >= 0) T[d.team].eatEvents++;
        }
        break;
      }
      case 'dragonAction': {
        const d = drag.get(e.id); if (!d) break;
        const a = e.action;
        d.act = a ? a.kind : null; d.tle = !!e.tle;
        if (!a || a.kind !== 'move') break;
        const t = T[d.team], w = win(round);
        if (a.steps.length >= 2) t.sprints[w]++;
        if (a.steps.length >= 3) t.longSprints[w]++;
        // simulate the steps (execution-order.md): pay, kelp/portal, own body, other dragons, then move and eat
        clrOcc(d);
        const body = d.body.slice();
        let fate = null;
        for (let i = 0; i < a.steps.length; i++) {
          const st = a.steps[i];
          if (i > 0 && body.length <= 2) { fate = { reason: 'A', step: i, why: 'sprint' }; break; }
          const h = body[0], nx = across(h.x, h.y, st);
          if (!nx) { fate = { reason: 'W', step: i }; break; }
          if (body.some(s => s.x === nx.x && s.y === nx.y)) { fate = { reason: 'S', step: i }; break; }
          const o = occ.get(key(nx.x, nx.y));
          if (o !== undefined) {
            const od = drag.get(o), isHead = od.body[0].x === nx.x && od.body[0].y === nx.y;
            fate = { reason: isHead ? 'H' : 'O', step: i, hit: o, hitTeam: od.team, hitLen: od.body.length };
            break;
          }
          body.unshift(nx);
          const k = key(nx.x, nx.y);
          if (pearls.has(k)) { pearls.delete(k); t.eaten[w]++; } else body.pop();
          if (i > 0) body.pop();
          d.expect.push({ h: body[0], t: body[body.length - 1] });
        }
        d.fate = fate;
        d.body = body; // steps already taken stand, also when a later step is fatal
        setOcc(d);
        break;
      }
      case 'dragonUpdate': {
        const d = drag.get(e.id);
        if (!d || round < 0) break;
        const x = d.expect.length ? d.expect.shift() : { h: d.body[0], t: d.body[d.body.length - 1] };
        if (x.h.x !== e.head.x || x.h.y !== e.head.y || x.t.x !== e.tail.x || x.t.y !== e.tail.y) {
          chk.updates++;
          // resync the way the viewer does (new head, drop segments up to the reported tail) so one error does not cascade
          clrOcc(d);
          const b = d.body.slice();
          if (b[0].x !== e.head.x || b[0].y !== e.head.y) b.unshift({ x: e.head.x, y: e.head.y });
          while (b.length > 1 && (b[b.length - 1].x !== e.tail.x || b[b.length - 1].y !== e.tail.y)) b.pop();
          d.body = b; d.expect = [];
          setOcc(d);
        }
        break;
      }
      case 'dragonSplit': {
        const p = drag.get(e.parentId); if (!p) break;
        const lenBefore = p.body.length;
        if (lenBefore !== e.parentBody.length + e.childBody.length) chk.splits++;
        T[p.team].splits.push([round, lenBefore, e.childBody.length, units(p.team)]);
        clrOcc(p);
        p.body = e.parentBody.map(s => ({ x: s.x, y: s.y }));
        setOcc(p);
        const c = { id: e.childId, team: e.team, body: e.childBody.map(s => ({ x: s.x, y: s.y })), born: round, fate: null, expect: [], act: null };
        drag.set(c.id, c); setOcc(c);
        break;
      }
      case 'dragonDeath': {
        const d = drag.get(e.id); if (!d) break;
        const rec = { r: round, id: d.id, reason: e.reason, len: d.body.length, born: d.born, mover: cur === d.id };
        if (rec.mover) {
          const f = d.fate;
          if (f && f.hit !== undefined) { rec.hitTeam = f.hitTeam; rec.hitLen = f.hitLen; }
          if (e.reason === 'A') {
            rec.why = d.tle ? 'tle' : f ? f.why : d.act === 'split' ? 'split' : d.act === 'suicide' ? 'suicide' : d.act === null ? 'none' : 'other';
            if (f && f.reason !== 'A') chk.deaths++;
          } else if (!f || f.reason !== e.reason) chk.deaths++;
        } else {
          const m = drag.get(cur);
          if (m) { rec.byTeam = m.team; rec.byLen = m.body.length; }
          if (e.reason !== 'H' || !m || !m.fate || m.fate.hit !== d.id) chk.deaths++;
        }
        T[d.team].deaths.push(rec);
        clrOcc(d); drag.delete(e.id);
        drop = { want: Math.ceil(rec.len / 2), got: 0 };
        break;
      }
      case 'sonarPing': {
        const s = drag.get(e.senderId);
        if (!s) { chk.pings++; break; }
        const t = T[s.team], w = win(round), sn = t.sonar;
        t.pings++; sn.sent[w]++;
        t.values.add(e.value64 === undefined ? String(e.value) : e.value64.toString());
        let kind;
        if (e.hitId === undefined) { sn.none[w]++; kind = 'none'; }
        else {
          const h = drag.get(e.hitId);
          if (!h) { chk.pings++; break; }
          const onHead = h.body[0].x === e.end.x && h.body[0].y === e.end.y;
          if (e.hitId === e.senderId) { sn.self[w]++; kind = onHead ? 'allyHead' : 'ally'; }
          else if (h.team === s.team) { sn.ally[w]++; kind = onHead ? 'allyHead' : 'ally'; }
          else { sn.enemy[w]++; kind = onHead ? 'enemyHead' : 'enemy'; if (onHead) sn.enemyHead[w]++; }
        }
        if (R.formatVersion >= 2 && (kind === 'none' ? e.hitKind !== 'empty' && e.hitKind !== 'kelp' : e.hitKind !== kind)) chk.hitKind++;
        break;
      }
    }
  }
  closeDrop();
  const rounds = round + 1;
  for (let r = lastSnap + TL_STEP; r <= ROUNDS; r += TL_STEP) snapshot(r); // final state carried to round 500
  for (const tm of TEAMS) {
    let sim = 0; for (const x of T[tm].eaten) sim += x;
    chk.eaten += Math.abs(sim - T[tm].eatEvents);
  }
  const res = R.result, fin = {};
  for (const tm of TEAMS) { const x = res['team' + tm]; fin[tm] = { dragonCount: x.dragonCount, longestDragon: x.longestDragon, totalLength: x.totalLength }; }
  const finalMatch = TEAMS.every(tm => {
    const s = T[tm].timeline[T[tm].timeline.length - 1], x = fin[tm];
    return s.units === x.dragonCount && s.longest === x.longestDragon && s.total === x.totalLength;
  });
  const winner = row.winner ? String(row.winner).toUpperCase() : res.winner;
  const team = tm => {
    const t = T[tm];
    return {
      timeline: t.timeline, splits: t.splits, deaths: t.deaths, eaten: t.eaten, sprints: t.sprints, longSprints: t.longSprints,
      sonar: { ...t.sonar, distinctValues: t.values.size, dragonRounds: t.turns, pingsPerDragonRound: t.turns ? +(t.pings / t.turns).toFixed(4) : 0 },
    };
  };
  return {
    meta: {
      battleId: row.battleId, gameId: row.gameId, map: row.map, width: W, height: H,
      teams: { A: { name: row.teamA, elo: row.eloA, rank: row.rankA }, B: { name: row.teamB, elo: row.eloB, rank: row.rankB } },
      winner, ranked: row.ranked, at: row.at, seed: R.seed, endReason: res.endReason, rounds, final: fin,
      simMismatches: chk.updates,
      checks: { deaths: chk.deaths, splits: chk.splits, eaten: chk.eaten, drops: chk.drops, hitKind: chk.hitKind, pings: chk.pings, finalMatch, winnerMatch: res.winner === winner, format: R.formatVersion },
    },
    A: team('A'), B: team('B'),
  };
}

// ---------------------------------------------------------------------------------------------------------------
// Worker thread: parse and extract one game per message.
if (!isMainThread) {
  const load = makeLoader(workerData.src);
  parentPort.on('message', task => {
    const t0 = Date.now();
    try {
      const f = extract(load(task.file), task.row);
      parentPort.postMessage({ key: task.key, line: JSON.stringify(f), sim: f.meta.simMismatches, checks: f.meta.checks, ms: Date.now() - t0 });
    } catch (err) {
      parentPort.postMessage({ key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 3).join(' | '), ms: Date.now() - t0 });
    }
  });
}

// ---------------------------------------------------------------------------------------------------------------
// Main: select games, run workers, append lines.
function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  const out = [];
  for (const l of fs.readFileSync(file, 'utf8').split('\n')) { if (!l.trim()) continue; try { out.push(JSON.parse(l)); } catch { /* partial line */ } }
  return out;
}
// Game key of a features line without parsing the whole (large) line when it has the usual prefix.
function lineKey(l) {
  const m = /^\{"meta":\{"battleId":(\d+),"gameId":(\d+)[,}]/.exec(l);
  if (m) return m[1] + ':' + m[2];
  try { const f = JSON.parse(l); return f && f.meta ? gameKey(f.meta) : null; } catch { return null; }
}
const featureLines = () => fs.existsSync(OUT) ? fs.readFileSync(OUT, 'utf8').split('\n').filter(l => l.trim()) : [];
// Drop a trailing partial line left by an interrupted run, so the next append starts on a fresh line.
function repairTail(file) {
  if (!fs.existsSync(file)) return;
  const size = fs.statSync(file).size; if (!size) return;
  const fd = fs.openSync(file, 'r+');
  try {
    const last = Buffer.alloc(1); fs.readSync(fd, last, 0, 1, size - 1);
    if (last[0] === 0x0a) return;
    const buf = fs.readFileSync(file), cut = buf.lastIndexOf(0x0a) + 1;
    fs.ftruncateSync(fd, cut);
    console.error(`features.jsonl: dropped a partial last line (${size - cut} bytes)`);
  } finally { fs.closeSync(fd); }
}
function takeLock() {
  for (let attempt = 0; attempt < 2; attempt++) {
    try { fs.writeFileSync(LOCK, String(process.pid), { flag: 'wx' }); return true; }
    catch (err) {
      if (err.code !== 'EEXIST') throw err;
      const pid = +fs.readFileSync(LOCK, 'utf8');
      let alive = false; try { if (pid) { process.kill(pid, 0); alive = true; } } catch (e2) { alive = e2.code === 'EPERM'; }
      if (alive) return false;
      fs.rmSync(LOCK, { force: true }); // stale lock from a dead run
    }
  }
  return false;
}
const stats = xs => {
  if (!xs.length) return 'n=0';
  const s = xs.slice().sort((a, b) => a - b), sum = s.reduce((a, b) => a + b, 0);
  return `n=${s.length} sum=${sum} mean=${(sum / s.length).toFixed(3)} median=${s[s.length >> 1]} max=${s[s.length - 1]} nonzero=${s.filter(x => x).length}`;
};

async function main() {
  const argv = process.argv.slice(2);
  const opt = (k, d) => { const i = argv.indexOf('--' + k); return i >= 0 ? argv[i + 1] : d; };
  const limit = opt('limit', null) === null ? Infinity : +opt('limit'), jobs = +opt('jobs', 6), force = argv.includes('--force');
  if (!(limit >= 0) || !(Number.isInteger(jobs) && jobs >= 1)) { console.error('usage: node tools/top_features.js [--limit N] [--jobs K] [--force]'); process.exit(2); }
  if (!takeLock()) { console.log('another top_features.js run holds ' + path.relative(ROOT, LOCK) + '; exiting'); return; }
  const release = () => fs.rmSync(LOCK, { force: true });
  process.on('exit', release);
  for (const sig of ['SIGINT', 'SIGTERM']) process.on(sig, () => { release(); process.exit(130); });

  const t0 = Date.now();
  repairTail(OUT);
  const index = [], seen = new Set();
  for (const row of readJsonl(INDEX)) { const k = gameKey(row); if (!seen.has(k)) { seen.add(k); index.push(row); } }
  const done = new Set(featureLines().map(lineKey).filter(Boolean));
  let missing = 0;
  const todo = [];
  for (const row of index) {
    if (todo.length >= limit) break;
    if (!force && done.has(gameKey(row))) continue;
    if (!fs.existsSync(replayFile(row))) { missing++; continue; }
    todo.push(row);
  }
  console.log(`index ${index.length} games, already in features ${done.size}, to process ${todo.length}` + (missing ? `, replay missing ${missing}` : '') + (force ? ' (--force)' : ''));
  if (!todo.length) return;

  // Output: append to features.jsonl, or with --force write a fresh file (kept rows first) and rename it at the end.
  let outFile = OUT;
  if (force) {
    outFile = OUT + '.tmp';
    const redo = new Set(todo.map(gameKey));
    const kept = featureLines().filter(l => { const k = lineKey(l); return k && !redo.has(k); });
    fs.writeFileSync(outFile, kept.map(l => l + '\n').join(''));
  }
  const fd = fs.openSync(outFile, 'a');

  const src = viewerSource();
  const queue = todo.slice(), sims = [], errors = [], checkSums = {}, times = [];
  let written = 0;
  const nw = Math.min(jobs, queue.length);
  await new Promise((resolve, reject) => {
    let live = nw;
    for (let i = 0; i < nw; i++) {
      const w = new Worker(__filename, { workerData: { src } });
      let finished = false;
      const next = () => {
        const row = queue.shift();
        if (!row) { finished = true; w.terminate(); if (--live === 0) resolve(); return; }
        w.postMessage({ key: gameKey(row), file: replayFile(row), row });
      };
      w.on('message', m => {
        times.push(m.ms);
        if (m.error) { errors.push(m.key + ' ' + m.error); console.error('error', m.key, m.error); }
        else {
          fs.writeSync(fd, m.line + '\n'); written++; sims.push(m.sim);
          for (const [k, v] of Object.entries(m.checks)) if (typeof v === 'number' && k !== 'format') checkSums[k] = (checkSums[k] || 0) + v; else if (typeof v === 'boolean' && !v) checkSums[k + 'False'] = (checkSums[k + 'False'] || 0) + 1;
          if (written % 50 === 0) console.log(`  ${written}/${todo.length} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
        }
        next();
      });
      w.on('error', reject);
      w.on('exit', code => { if (!finished) reject(Error('worker exited unexpectedly with code ' + code)); });
      next();
    }
  });
  fs.closeSync(fd);
  if (force) fs.renameSync(outFile, OUT);
  const secs = (Date.now() - t0) / 1000;
  console.log(`wrote ${written} games to ${path.relative(ROOT, OUT)}, errors ${errors.length}, ${secs.toFixed(1)}s wall, ${(times.reduce((a, b) => a + b, 0) / Math.max(1, times.length)).toFixed(0)} ms/game per worker`);
  console.log('simMismatches ' + stats(sims));
  console.log('other checks (summed; *False = games failing):', JSON.stringify(checkSums));
  if (errors.length) process.exitCode = 1;
}

module.exports = { makeLoader, viewerSource, extract, HIT_KIND };
if (isMainThread && require.main === module) main().catch(err => { console.error(err); process.exit(1); });
