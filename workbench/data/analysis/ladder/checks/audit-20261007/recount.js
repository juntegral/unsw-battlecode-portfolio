// Independent recount of one ladder game from the official 1.2.7 viewer's decoded events.
// Shares nothing with tools/ladder_replay.py or battlecode/replay.py (different decoder, different logic).
// usage: node recount.js <replay> <ourSide A|B>   -> one JSON object on stdout
const fs = require('fs');
const { ctx } = require('./viewer2.js');

const MARKS = [50, 100, 150, 200, 300, 400];
const WIN = r => (r <= 100 ? 'r0-100' : r <= 300 ? 'r101-300' : 'r301-500');
const CAUSE = { W: 'wall', S: 'own body', O: 'other dragon body', H: 'head-on', A: 'other' };
const key = c => c.x + ',' + c.y;

function recount(file, ours) {
  const R = ctx.parseReplay(fs.readFileSync(file));
  const lines = R.map.split('\n').map(l => l.trim().split(/\s+/));
  const [W, H] = lines.find(l => l[0] === 'MAP').slice(1, 3).map(Number);
  // edges: N edge of (x,y) = 2y(W+1)+x, W edge of (x,y) = (2y+1)(W+1)+x; east and south border edges are the
  // west / north edges of the wrapped neighbour (the file does not list them twice).
  const edge = new Map();
  for (const l of lines) if (l[0] === 'EDGE') edge.set(Number(l[1]), [Number(l[2]), Number(l[3])]);
  const nId = (x, y) => 2 * y * (W + 1) + x, wId = (x, y) => (2 * y + 1) * (W + 1) + x;
  const portal = new Map();
  for (const [id, [k, p]] of edge) if (k === 2) { if (!portal.has(p)) portal.set(p, []); portal.get(p).push(id); }
  const decode = id => { const row = Math.floor(id / (W + 1)), x = id % (W + 1); return { ns: row % 2 === 0, x, y: Math.floor(row / 2) }; };
  function step(x, y, d) {            // -> {wall:true} or {x,y}
    let id, nx = x, ny = y;
    if (d === 'N') { id = nId(x, y); ny = (y + H - 1) % H; }
    else if (d === 'S') { ny = (y + 1) % H; id = nId(x, ny); }
    else if (d === 'W') { id = wId(x, y); nx = (x + W - 1) % W; }
    else { nx = (x + 1) % W; id = wId(nx, y); }
    const e = edge.get(id) || [0, -1];
    if (e[0] === 1) return { wall: true };
    if (e[0] === 2) {
      const pair = portal.get(e[1]).filter(z => z !== id);
      if (pair.length !== 1) return { wall: true };
      const q = decode(pair[0]);
      if (d === 'N') return { x: q.x, y: (q.y + H - 1) % H };
      if (d === 'S') return { x: q.x, y: q.y };
      if (d === 'W') return { x: (q.x + W - 1) % W, y: q.y };
      return { x: q.x, y: q.y };
    }
    return { x: nx, y: ny };
  }
  const bodies = new Map(), team = new Map();
  for (const l of lines) if (l[0] === 'DRAGON') {
    const id = bodies.size, n = Number(l[2]), b = [];
    for (let k = 0; k < n; k++) b.push(l[3 + 2 * k] + ',' + l[4 + 2 * k]);
    bodies.set(id, b); team.set(id, 'AB'[Number(l[1])]);
  }
  if (team.get(0) === team.get(1)) throw new Error('dragons 0 and 1 on one team');
  const sideOf = id => (team.get(id) === ours ? 'us' : 'them');
  const queen = { us: team.get(0) === ours ? 0 : 1, them: team.get(0) === ours ? 1 : 0 };
  const spawn = { q0: bodies.get(0).slice(), q1: bodies.get(1).slice() };

  let actEvt = null;
  let round = 0, actor = null, action = null, moved = 0, startLen = 0, lastEvt = '';
  const pearls = new Map();           // tile -> {origin, death}
  const eats = [], deaths = [], snaps = {}, drops = [];
  const qEats = { us: 0, them: 0 }, qSplits = { us: 0, them: 0 };
  let dropWindow = null;               // {death, tiles:Set}
  let geoMismatch = 0, splitTeamBad = 0, sawRounds = 0;
  const snap = () => {
    const o = {};
    for (const s of ['us', 'them']) {
      let alive = 0, total = 0, longest = 0;
      for (const [id, b] of bodies) if (sideOf(id) === s) { alive++; total += b.length; longest = Math.max(longest, b.length); }
      const q = bodies.get(queen[s]);
      o[s] = { alive, total, longest, pearls: eats.filter(e => e.side === s).length, queen_alive: !!q, queen_length: q ? q.length : 0 };
    }
    return o;
  };
  for (const e of R.events) {
    if (e.type !== 'tileChange') dropWindow = null;
    switch (e.type) {
      case 'roundStart':
        if (sawRounds) snaps[round] = snap();
        sawRounds++; round = e.round; actor = null; break;
      case 'turnStart': actor = e.id; action = null; actEvt = null; moved = 0; startLen = bodies.get(e.id).length; break;
      case 'dragonAction': if (e.id !== actor) throw new Error('action outside turn'); action = e.action; actEvt = e; break;
      case 'tileChange': {
        const t = key(e.tile);
        if (e.hasPearl) {
          if (pearls.has(t)) throw new Error('pearl on pearl ' + t);
          if (dropWindow && dropWindow.tiles.has(t)) {
            const p = { origin: 'drop', death: dropWindow.death, round, eater: null, eatRound: null };
            dropWindow.tiles.delete(t); dropWindow.death.dropped++; drops.push(p); pearls.set(t, p);
          } else pearls.set(t, { origin: 'spawn', round, inTurn: actor !== null });
        } else {
          const p = pearls.get(t); if (!p) throw new Error('eat without pearl ' + t);
          pearls.delete(t);
          if (actor === null || !bodies.has(actor)) throw new Error('pearl removed outside a living turn');
          const s = sideOf(actor);
          eats.push({ round, side: s, id: actor, tile: t });
          if (actor === queen[s]) qEats[s]++;
          if (p.origin === 'drop') { p.eater = s; p.eatRound = round; }
        }
        break;
      }
      case 'dragonUpdate': {
        const b = bodies.get(e.id); if (!b) throw new Error('update of dead dragon');
        const h = key(e.head), t = key(e.tail);
        if (b[0] !== h) { b.unshift(h); if (e.id === actor) moved++; }
        while (b.length > 1 && b[b.length - 1] !== t) b.pop();
        if (b[b.length - 1] !== t) throw new Error('tail not in body');
        break;
      }
      case 'dragonSplit': {
        if (team.get(e.parentId) !== e.team) splitTeamBad++;
        const s = sideOf(e.parentId); if (e.parentId === queen[s]) qSplits[s]++;
        bodies.set(e.parentId, e.parentBody.map(key)); bodies.set(e.childId, e.childBody.map(key)); team.set(e.childId, e.team);
        break;
      }
      case 'dragonDeath': {
        const b = bodies.get(e.id);
        // geometry: what did the mover's next step run into?
        let geo = null, hitId = null, dest = null;
        if (actor !== null && bodies.has(actor) && action && action.kind === 'move' && moved < action.steps.length) {
          const ab = bodies.get(actor), [hx, hy] = ab[0].split(',').map(Number);
          const free = Math.ceil(startLen / 4);
          if (moved >= free && ab.length <= 2) geo = 'A';
          else {
            const to = step(hx, hy, action.steps[moved]);
            if (to.wall) geo = 'W';
            else {
              dest = to.x + ',' + to.y;
              if (ab.includes(dest)) geo = 'S';
              else for (const [id, ob] of bodies) if (id !== actor) { const k = ob.indexOf(dest); if (k === 0) { geo = 'H'; hitId = id; } else if (k > 0) { geo = 'O'; hitId = id; } }
            }
          }
        } else geo = 'A';
        const prev = deaths[deaths.length - 1];
        const pairedVictim = e.id !== actor;          // the stationary head of a head-on dies first
        let why = null;
        if (e.reason === 'A') {
          if (e.id !== actor || !actEvt) why = 'no action';
          else if (actEvt.tle || (actEvt.instructions && actEvt.instructions.exceeded)) why = 'timeout';
          else if (!action || action.kind === 'suicide') why = 'no action';
          else if (action.kind === 'split') why = 'illegal split';
          else why = 'unpaid sprint';
        }
        const d = { id: e.id, side: sideOf(e.id), round, length: b.length, reason: e.reason, actor, geo, hitId, dropped: 0, victimOfActor: pairedVictim, why };
        if (e.id === actor) {
          if (prev && prev.round === round && prev.actor === actor && prev.victimOfActor && prev.reason === 'H') { if (e.reason !== 'H') geoMismatch++; }
          else if (geo !== e.reason) { geoMismatch++; d.geoBad = geo + '!=' + e.reason; }
        } else if (!(e.reason === 'H' && geo === 'H' && hitId === e.id)) { geoMismatch++; d.geoBad = 'victim ' + geo + ' ' + hitId; }
        deaths.push(d);
        dropWindow = { death: d, tiles: new Set(b.filter((_, k) => k % 2 === 0)) };
        bodies.delete(e.id);
        break;
      }
      default: break;
    }
    lastEvt = e.type;
  }
  snaps[round] = snap();
  const fin = snap();
  // head-on meetings: victim death immediately followed by the mover's death in the same turn
  const meets = [];
  for (let k = 1; k < deaths.length; k++) {
    const a = deaths[k - 1], b = deaths[k];
    if (a.reason === 'H' && b.reason === 'H' && a.victimOfActor && b.id === b.actor && a.actor === b.actor && a.round === b.round) { meets.push([a, b]); a.meet = b.meet = meets.length - 1; a.cross = b.cross = a.side !== b.side; }
  }
  const unpairedH = deaths.filter(d => d.reason === 'H' && d.meet === undefined).length;
  const dropBad = deaths.filter(d => d.dropped !== Math.ceil(d.length / 2)).length;
  const deathTab = {};
  for (const w of ['r0-100', 'r101-300', 'r301-500']) {
    deathTab[w] = {};
    for (const s of ['us', 'them']) { deathTab[w][s] = {}; for (const c of Object.values(CAUSE)) deathTab[w][s][c] = 0; }
  }
  for (const d of deaths) deathTab[WIN(d.round)][d.side][CAUSE[d.reason]]++;
  const otherTab = {};
  for (const w of ['r0-100', 'r101-300', 'r301-500']) { otherTab[w] = {}; for (const s of ['us', 'them']) otherTab[w][s] = { 'unpaid sprint': 0, 'illegal split': 0, 'no action': 0, timeout: 0 }; }
  for (const d of deaths) if (d.reason === 'A') otherTab[WIN(d.round)][d.side][d.why]++;
  const pearlTab = {};
  for (const w of ['r0-100', 'r101-300', 'r301-500']) pearlTab[w] = { us: 0, them: 0 };
  for (const e of eats) pearlTab[WIN(e.round)][e.side]++;
  const dropTab = {};
  for (const s of ['us', 'them']) {
    const ps = drops.filter(p => p.death.cross && p.death.side === s);
    const within = ps.filter(p => p.eater && p.eatRound - p.round <= 15);
    const cens = ps.filter(p => !p.eater && round - p.round < 15).length;
    dropTab[s] = {
      total: ps.length,
      eaten_within_15: { us: within.filter(p => p.eater === 'us').length, them: within.filter(p => p.eater === 'them').length },
      not_eaten_within_15: ps.length - within.length - cens, censored: cens,
      eaten_by_end: { us: ps.filter(p => p.eater === 'us').length, them: ps.filter(p => p.eater === 'them').length, nobody: ps.filter(p => !p.eater).length },
    };
  }
  const q = {};
  for (const s of ['us', 'them']) {
    const d = deaths.find(x => x.id === queen[s]);
    let ram = null;
    if (d && d.reason === 'H') { const m = meets[d.meet]; ram = { attacker: m[1].id, victim: m[0].id, attacker_side: m[1].side }; }
    q[s] = { id: queen[s], death_round: d ? d.round : null, death_cause: d ? CAUSE[d.reason] : 'none', death_length: d ? d.length : null,
      death_hit_id: d && d.reason === 'O' ? d.hitId : null, death_other: d && d.reason === 'A' ? d.why : null, head_on: ram, pearls_eaten: qEats[s], splits: qSplits[s],
      length: Object.fromEntries([100, 200, 300, 400].map(r => [r, snaps[r] ? snaps[r][s].queen_length : null])) };
  }
  const res = R.result, off = { A: res.teamA, B: res.teamB }, them = ours === 'A' ? 'B' : 'A';
  const official = { us: off[ours], them: off[them] };
  let ended;
  if (res.endReason === 'teamEliminated') ended = 'elimination';
  else if (official.us.queenLength !== official.them.queenLength) ended = 'queen rule';
  else if (official.us.longestDragon !== official.them.longestDragon) ended = 'longest dragon';
  else if (official.us.totalLength !== official.them.totalLength) ended = 'total length';
  else ended = 'draw';
  // expected winner from the written rules, to compare with the stored winner
  let ruleWinner = null;
  const cmp = (a, b) => (a > b ? 'us' : a < b ? 'them' : null);
  if (res.endReason === 'teamEliminated') ruleWinner = cmp(official.us.dragonCount > 0 ? 1 : 0, official.them.dragonCount > 0 ? 1 : 0);
  else ruleWinner = cmp(official.us.queenLength, official.them.queenLength) || cmp(official.us.longestDragon, official.them.longestDragon) || cmp(official.us.totalLength, official.them.totalLength);
  return {
    botA: R.teams.A.botId, botB: R.teams.B.botId, W, H,
    winner: res.winner, result: res.winner === null ? 'draw' : res.winner === ours ? 'win' : 'loss', ruleWinner,
    endReason: res.endReason, terminated: res.terminated, ended_by: ended, last_round: round,
    official, final: fin, finalMatchesOfficial: ['us', 'them'].every(s => fin[s].alive === official[s].dragonCount && fin[s].longest === official[s].longestDragon && fin[s].total === official[s].totalLength && fin[s].queen_length === official[s].queenLength),
    curves: Object.fromEntries(MARKS.map(r => [r, snaps[r] || null])),
    queen: q, deaths: deathTab, deaths_other: otherTab, pearls: pearlTab,
    queens_at_end: official.us.queenLength > 0 ? (official.them.queenLength > 0 ? 'both alive' : 'only ours') : (official.them.queenLength > 0 ? 'only theirs' : 'both dead'),
    head_on: { count: meets.filter(m => m[0].side !== m[1].side).length, same_team_count: meets.filter(m => m[0].side === m[1].side).length, drops: dropTab },
    checks: { geoMismatch, geoBad: deaths.filter(d => d.geoBad).map(d => [d.round, d.id, d.geoBad]).slice(0, 5), splitTeamBad, unpairedH, dropBad, deaths: deaths.length, eats: eats.length, pearlsLeft: pearls.size,
      spawnInTurn: [...pearls.values()].filter(p => p.inTurn).length },
    spawn,
  };
}

if (require.main === module) {
  const out = recount(process.argv[2], process.argv[3]);
  process.stdout.write(JSON.stringify(out) + '\n');
}
module.exports = { recount };
