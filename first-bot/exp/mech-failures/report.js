#!/usr/bin/env node
// Numbers for research/observations/mech-merge2-failures.md, from the JSON lines written by exp/mech-failures/collect.js.
// usage: node exp/mech-failures/report.js <online.jsonl> [<top.jsonl>] [--select <cases.json>]
//   Stage 1 (population): per set, every firing of each mechanism of our bot (all elite-set online games of our lineage).
//   Stage 2 (classes): every failure of the primary sample (merge2, three waves) sorted into counter-play classes, with
//            class sizes by opponent, map, phase and length class.
//   Stage 3 (selection): the replays to read closely, chosen per class by a fixed rule (below); written to --select.
//   Reference: the same situations over all top-vs-top games, and the independent recount (recount.js) beside the
//            primary numbers.
'use strict';
const fs = require('fs');
const argv = process.argv.slice(2);
const opt = n => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : null; };
const files = argv.filter((a, i) => !a.startsWith('--') && argv[i - 1] !== '--select');
const readL = f => fs.readFileSync(f, 'utf8').split('\n').filter(Boolean).map(l => JSON.parse(l));
const ON = readL(files[0]);
const TOPG = files[1] && fs.existsSync(files[1]) ? readL(files[1]) : [];
const CA = ['sac', 'trap', 'rammed', 'ram', 'enemyBody', 'allyHead', 'fault', 'sprintDeath'];
const PRIMARY = new Set(['cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3']);
const SETS = ['baseline-r1', 'baseline-r1b', 'baseline-r1c', 'cand-avoid6-online', 'cand-portal1-online', 'cand-merge2-online', 'cand-merge2-online-r2', 'cand-merge2-online-r3', 'cand-swarm8-online'];
const SHORT = { 'baseline-r1': 'base-r1', 'baseline-r1b': 'base-r1b', 'baseline-r1c': 'base-r1c', 'cand-avoid6-online': 'avoid6', 'cand-portal1-online': 'portal1',
  'cand-merge2-online': 'merge2-r1', 'cand-merge2-online-r2': 'merge2-r2', 'cand-merge2-online-r3': 'merge2-r3', 'cand-swarm8-online': 'swarm8' };
const nSet = s => ON.filter(g => g.meta.set === s).length;
const P = ON.filter(g => PRIMARY.has(g.meta.set)), NP = P.length;
const pc = (a, b) => b ? (100 * a / b).toFixed(0) + '%' : '–';
const f1 = v => Number.isFinite(v) ? v.toFixed(2) : '–';
const vOf = t => { const m = t && / v(-?[\d.]+)/.exec(t); return m ? +m[1] : null; };
const phase = r => r < 100 ? 'r0-99' : r < 250 ? 'r100-249' : r < 350 ? 'r250-349' : r < 450 ? 'r350-449' : 'r450+';
const lenCls = L => L <= 4 ? 'L2-4' : L <= 7 ? 'L5-7' : L <= 14 ? 'L8-14' : 'L15+';
const out = [];
const say = s => out.push(s);
const H = s => say('\n## ' + s + '\n');
const table = (head, rows) => { say('| ' + head.join(' | ') + ' |'); say('|' + head.map(() => '---').join('|') + '|'); for (const r of rows) say('| ' + r.join(' | ') + ' |'); say(''); };
const cnt = (xs, f) => { const o = new Map(); for (const x of xs) { const k = f(x); if (k === null || k === undefined) continue; o.set(k, (o.get(k) || 0) + 1); } return [...o.entries()].sort((a, b) => b[1] - a[1]); };
const cntStr = (xs, f) => cnt(xs, f).map(([k, v]) => `${k} ${v}`).join(' · ');
const med = a => { const b = a.filter(v => v !== null && v !== undefined && Number.isFinite(v)).sort((x, y) => x - y); return b.length ? b[b.length >> 1] : null; };
const histMed = h => { if (!h) return null; const e = Object.entries(h).filter(([k]) => k !== 'x').map(([k, v]) => [+k, v]).sort((a, b) => a[0] - b[0]); const n = e.reduce((s, x) => s + x[1], 0); let c = 0; for (const [k, v] of e) { c += v; if (c * 2 >= n) return k; } return null; };
const mergeHist = (a, b) => { const o = { ...(a || {}) }; for (const [k, v] of Object.entries(b || {})) o[k] = (o[k] || 0) + v; return o; };
const recs = (games, k) => games.flatMap(g => (g.mech && g.mech[k] || []).map(x => ({ ...x, set: g.meta.set, game: g.meta.game, map: g.meta.map, opp: g.meta.opp, us: g.meta.us, rounds: g.meta.rounds })));
const selections = [];
// Stage 3 rule, applied per class on the primary sample: the extreme case (largest length at stake; ties: lower game id,
// earlier round) and up to two representative cases (length closest to the class median; each from an opponent not yet
// picked in the class, then a map not yet picked; ties: lower game id, earlier round).
// For split children (all L2-3) the measure is the child's age at death instead of a length: the extreme case is the child
// that died soonest, the representative ones are closest to the class median age.
function select(pattern, cls, xs, lenOf, describe, keyOf = lenOf) {
  if (!xs.length) return;
  const byExt = [...xs].sort((a, b) => keyOf(b) - keyOf(a) || a.game - b.game || a.r - b.r);
  const picks = [byExt[0]]; const m = med(xs.map(keyOf));
  const rest = xs.filter(x => x !== byExt[0]).sort((a, b) => Math.abs(keyOf(a) - m) - Math.abs(keyOf(b) - m) || a.game - b.game || a.r - b.r);
  for (const pass of ['opp', 'map', 'any']) for (const x of rest) {
    if (picks.length >= 3 || picks.includes(x)) continue;
    if (pass === 'opp' && picks.some(p => p.opp === x.opp)) continue;
    if (pass === 'map' && picks.some(p => p.map === x.map)) continue;
    picks.push(x);
  }
  picks.forEach((x, i) => selections.push({ pattern, cls, role: i === 0 ? 'extreme' : 'representative', set: x.set, game: x.game, map: x.map, opp: x.opp, r: x.r, id: x.id, L: lenOf(x), note: describe(x) }));
}
const classTable = (xs, clsOf, title) => {
  const classes = cnt(xs, clsOf);
  say(`${title} (N = ${xs.length})`); say('');
  table(['class', 'n', 'by opponent', 'by map', 'by phase', 'by length'], classes.map(([c, n]) => { const ys = xs.filter(x => clsOf(x) === c); return [c, n, cntStr(ys, x => x.opp), cntStr(ys, x => x.map), cntStr(ys, x => phase(x.r)), cntStr(ys, x => lenCls(x.L))]; }));
  return classes;
};

// ---------------------------------------------------------------------------------------------------------------
H('0. Population');
say(`- Our online games against the elite set (Cutlery 306, cheji bt 70, calc 20, 中国必须人能飞😡 801, forgot to mention 264, Sabotage-d 46, DEV 545), our bot lineage only: ${ON.length} games.`);
const subOf = s => { try { const ix = JSON.parse(fs.readFileSync(require('path').resolve(__dirname, '..', '..', 'data', 'online', s, 'index.json'), 'utf8')); return [...new Set((ix.games || ix).map(g => g.ourSubmission))].join(', '); } catch { return '?'; } };
const BOT = { 'baseline-r1': 'g4-r4', 'baseline-r1b': 'g4-r4', 'baseline-r1c': 'g4-r4', 'cand-avoid6-online': 'g4-r4 + esc (avoid6)', 'cand-portal1-online': 'g4-r4 + unexplored portals (portal1)',
  'cand-merge2-online': 'merge2 = avoid6 + portal1 + pocket-eat', 'cand-merge2-online-r2': 'merge2', 'cand-merge2-online-r3': 'merge2', 'cand-swarm8-online': 'merge2 + swarm early game' };
table(['set', 'games', 'submission', 'bot'], SETS.map(s => [SHORT[s], nSet(s), subOf(s), BOT[s]]));
say('- Excluded: px-king-v2, base-px8, base-px9d (other bot families without our labels), r1-online and r1-autoscrim (not the elite set).');
say(`- Primary sample (the bot that has every mechanism studied here): merge2, three waves, N = ${NP} games.`);
say(`- Top-vs-top reference: ${TOPG.length} games (data/top, all games with a replay).`);
say(`- Reconstruction checks nonzero: online ${ON.filter(g => Object.values(g.meta.chk || {}).some(v => v)).length}, top ${TOPG.filter(g => Object.values(g.meta.chk || {}).some(v => v)).length}.`);

// ---------------------------------------------------------------------------------------------------------------
H('1. Escape sprints (esc) and 2-step threat sprints (sprintEsc)');
// executed = 2+ steps and the dragon survived its own move. tools/mech_check.js also drops escapes after which the dragon was
// rammed later in the same round (its ex = 0); here those count as executed and failed (the recount found them).
const ESC = recs(ON, 'esc').filter(x => x.steps >= 2 && !(x.death && x.death.r === x.r && x.death.cause !== 2));
const ESC_MC = recs(ON, 'esc').filter(x => x.ex);
const escCls = x => {
  const z = x.death;
  if (!z) return 'body lost through a descendant';
  if (z.text && /TRADE|last-trade/.test(z.text)) return 'not a loss: our own TRADE';
  if (z.cause !== 2) return 'other death: ' + CA[z.cause];
  if (x.killerBorn > x.r) return 'newborn: child born after the escape';
  const nearest = x.near.filter(q => q.len < x.L).sort((a, b) => a.td - b.td)[0];
  if (nearest && nearest.id === z.killer.id) return 'pursuit: the head we escaped from';
  if (x.killerAtEsc && x.killerAtEsc.cheb <= 3) return 'second head: in view at the escape';
  return 'second head: outside the 7x7 view at the escape';
};
for (const k of ['esc', 'sprintEsc']) {
  say(`### ${k}: per set`); say('');
  table(['set', 'games', 'executed', 'per game', 'body dead within 10', 'rate', 'mass kept +10', 'mass kept +30'], SETS.map(s => {
    const xs = ESC.filter(x => x.k === k && x.set === s), L = xs.reduce((a, x) => a + x.L, 0);
    return [SHORT[s], nSet(s), xs.length, f1(xs.length / nSet(s)), xs.filter(x => !x.alive10).length, pc(xs.filter(x => !x.alive10).length, xs.length), pc(xs.reduce((a, x) => a + x.fam10L, 0), L), pc(xs.reduce((a, x) => a + x.fam30L, 0), L)];
  }).filter(r => r[2] > 0));
  const xs = ESC.filter(x => x.k === k && PRIMARY.has(x.set)), fails = xs.filter(x => !x.alive10);
  const classes = classTable(fails, escCls, `${k}: merge2 failures (body dead within 10 rounds) by counter-play class`);
  const rm = fails.filter(x => x.death && x.death.cause === 2 && x.death.killer);
  say(`- rammed ${rm.length}: killer's final move a sprint ${rm.filter(x => x.death.killer.steps >= 2).length}; killer length ${cntStr(rm, x => 'L' + x.death.killer.len)}; through a portal ${rm.filter(x => x.death.killer.portal).length}.`);
  const shR = x => (x.trace || []).slice(1, -1).filter(d => d !== null && d <= 5).length, grew = x => x.killerLenB > x.killerLenAfterEsc;
  const later = rm.filter(x => x.death.r >= x.r + 2);
  say(`- shadow and grow (rammed at least 2 rounds after the escape: ${later.length}): killer within 5 tiles on >= 2 round starts between the escape and the strike ${later.filter(x => shR(x) >= 2).length}; killer longer at the strike than just after the escape ${later.filter(grew).length}; both ${later.filter(x => shR(x) >= 2 && grew(x)).length}. Rammed in the escape round or the next: ${rm.length - later.length}.`);
  const sh = x => x.near.filter(q => q.len < x.L && q.len <= 4 && q.td <= 5).length;
  say(`- failure rate by shorter enemy heads within 5 at the escape: ${[[0, 1], [2, 2], [3, 99]].map(([a, b]) => { const ys = xs.filter(x => sh(x) >= a && sh(x) <= b); return `${a}${b === 99 ? '+' : b > a ? '-' + b : ''}: ${ys.filter(x => !x.alive10).length}/${ys.length} (${pc(ys.filter(x => !x.alive10).length, ys.length)})`; }).join(' · ')}`);
  say(`- failure rate by tail distance to the nearest enemy head: <=3 ${xs.filter(x => x.tailE <= 3 && !x.alive10).length}/${xs.filter(x => x.tailE <= 3).length} · >=4 ${xs.filter(x => x.tailE >= 4 && !x.alive10).length}/${xs.filter(x => x.tailE >= 4).length}; failures with the tail >= 4 away: ${fails.filter(x => x.tailE >= 4).length}/${fails.length}`);
  say(`- killer distance 5 rounds before the escape (median) ${med(rm.map(x => x.killerHist && x.killerHist[0]))}, at the escape ${med(rm.map(x => x.killerAtEsc && x.killerAtEsc.td))}`);
  say('');
  for (const [c] of classes) if (!c.startsWith('not a loss')) select(`1 ${k}`, c, fails.filter(x => escCls(x) === c), x => x.L, x => `${x.text || ''} -> ${x.death ? `r${x.death.r} ${CA[x.death.cause]}${x.death.killer ? ` by #${x.death.killer.id} L${x.death.killer.len} (${x.death.killer.steps} steps)` : ''}` : 'descendants'}`);
}

H('1b. Every head-on death of our dragons of length >= 6: what the bot could know at its last decision');
const RAMS = ON.flatMap(g => g.rams.filter(r => r.side === 'us' && r.len >= 6).map(r => ({ ...r, set: g.meta.set, game: g.meta.game, map: g.meta.map, opp: g.meta.opp, L: r.len })));
const ramCls = d => {
  const k = d.atDecision;
  if (!d.hasDecision) return 'newborn: no decision before the ram';
  if (d.text && /^(feed|escape-split|no-exit|split|pocket|last-trade)/.test(d.text)) return 'label ' + d.text.split(/[ \d]/)[0];
  if (!k) { const ourR = d.killerId !== undefined && d.id > d.killerId ? d.r - 1 : d.r; return d.killerBorn >= ourR ? 'unseen: killer born after the decision (a split)' : 'unseen: killer farther than 8 at the decision'; }
  if (k.cheb > 3) return 'unseen: killer outside the 7x7 view';
  const inf = k.tailVis ? k.vis - 1 : Math.max(3, k.vis - 1);
  if (d.killerSteps > inf) return d.killerAte ? 'reach gap: pearl eaten on the strike path' : 'reach gap: tail unseen, killer L>=5';
  const v = vOf(d.text);
  if (v !== null && v < 0) return 'priced: in reach, threat in the value (v<0), still hit';
  if (d.newHeadWasOcc || d.pathThroughOcc > 0) return 'blind spot: path through a tile occupied at the decision';
  return 'unpriced: cause not visible in the replay';
};
say('### per set'); say('');
table(['set', 'games', 'rams on L>=6', 'per game', 'killer sprinted', 'blind spot', 'reach gap', 'unseen'], SETS.map(s => { const xs = RAMS.filter(x => x.set === s); return [SHORT[s], nSet(s), xs.length, f1(xs.length / nSet(s)), pc(xs.filter(x => x.killerSteps >= 2).length, xs.length), xs.filter(x => ramCls(x).startsWith('blind')).length, xs.filter(x => ramCls(x).startsWith('reach')).length, xs.filter(x => ramCls(x).startsWith('unseen')).length]; }));
const RP = RAMS.filter(x => PRIMARY.has(x.set));
const rcl = classTable(RP, ramCls, 'merge2: rams on our L>=6 dragons by class');
say(`- killer steps: ${cntStr(RP, x => 'steps ' + x.killerSteps)}; killer length before its move: ${cntStr(RP, x => 'L' + x.killerLenB)}`);
say(`- blind spot detail: our new head on a tile occupied at the decision (own tail) ${RP.filter(x => x.newHeadWasOcc).length}; strike path through such tiles ${RP.filter(x => x.pathThroughOcc > 0).length}; a nearer shorter head (cannot reach) in front of the killer ${RP.filter(x => x.masked).length}`);
say(`- shadow and grow: killer's head within 5 of the victim's on >= 3 of the 10 round starts before the strike ${RP.filter(x => x.shadow >= 3).length}/${RP.length}; killer longer at the strike than 10 rounds before ${RP.filter(x => x.killerLen10 !== null && x.killerLenB > x.killerLen10).length}/${RP.length}; both ${RP.filter(x => x.shadow >= 3 && x.killerLen10 !== null && x.killerLenB > x.killerLen10).length}/${RP.length}`);
say(`- our kings (team's longest, L>=8) rammed from r400: ${RP.filter(x => x.king && x.r >= 400).length}; their label value >= 0: ${RP.filter(x => x.king && x.r >= 400 && (vOf(x.text) ?? 0) >= 0).length}; killer steps ${cntStr(RP.filter(x => x.king && x.r >= 400), x => 'steps ' + x.killerSteps)}`);
say(`- pearls of both bodies: killer's team ${RP.reduce((s, x) => s + x.eatKillerTeam, 0)}, ours ${RP.reduce((s, x) => s + x.eatVictimTeam, 0)}; nearest collector median: theirs ${med(RP.map(x => x.colKillerTeam))}, ours ${med(RP.map(x => x.colVictimTeam))}`);
say('');
for (const [c] of rcl) select('1b rams', c, RP.filter(x => ramCls(x) === c), x => x.L, x => `decision "${x.text || ''}" killer L${x.killerLenB} ${x.killerSteps} steps${x.killerAte ? ', ate on the path' : ''}`);
// top reference
const TR = TOPG.flatMap(g => g.rams.map(r => ({ ...r, map: g.meta.map })));
if (TOPG.length) {
  say(`### top-vs-top reference: head-on deaths of L>=6 dragons (N games = ${TOPG.length})`); say('');
  const inView = TR.filter(x => x.atDecision && x.atDecision.cheb <= 3);
  say(`- ${TR.length} rams (${f1(TR.length / TOPG.length)} per game). Killer steps: ${cntStr(TR, x => 'steps ' + x.killerSteps)}; sprint share ${pc(TR.filter(x => x.killerSteps >= 2).length, TR.length)}.`);
  say(`- killer ate a pearl on the strike path ${TR.filter(x => x.killerAte).length} (${pc(TR.filter(x => x.killerAte).length, TR.length)}); strike longer than the victim could infer from visible segments ${inView.filter(x => x.killerSteps > (x.atDecision.tailVis ? x.atDecision.vis - 1 : Math.max(3, x.atDecision.vis - 1))).length}/${inView.length} in view; path through a tile occupied at the victim's decision ${TR.filter(x => x.pathThroughOcc > 0).length}; victim moved onto its own tail tile ${TR.filter(x => x.newHeadWasOcc).length}; killer outside the victim's 7x7 view or farther ${TR.filter(x => !x.atDecision || x.atDecision.cheb > 3).length}.`);
  say(`- pearls of both bodies: killer's team ${TR.reduce((s, x) => s + x.eatKillerTeam, 0)}, victim's team ${TR.reduce((s, x) => s + x.eatVictimTeam, 0)}`);
  say(`- shadow and grow: killer within 5 on >= 3 of the 10 round starts before the strike ${TR.filter(x => x.shadow >= 3).length}/${TR.length}; killer grew over those 10 rounds ${TR.filter(x => x.killerLen10 !== null && x.killerLenB > x.killerLen10).length}/${TR.length}; both ${TR.filter(x => x.shadow >= 3 && x.killerLen10 !== null && x.killerLenB > x.killerLen10).length}/${TR.length}`);
  say('');
}

H('1c. Long dragons (>=6) with every single step inside a shorter enemy head reach: response and mass kept');
const cornered = (games, sidePred, bucket = 'cornered') => { const o = {}; for (const g of games) for (const [side, a] of Object.entries(g.agg)) { if (!sidePred(side)) continue; for (const [k, q] of Object.entries(a[bucket] || {})) { const t = o[k] || (o[k] = { n: 0, L: 0, f10: 0, f30: 0, d10: 0, fd10: 0 }); for (const f of Object.keys(t)) t[f] += q[f]; } } return o; };
const cornRows = (label, o) => Object.entries(o).sort().map(([k, q]) => [label, k, q.n, (q.L / q.n).toFixed(1), pc(q.f10, q.L), pc(q.f30, q.L), q.d10, q.fd10]);
table(['population', 'response', 'turns', 'mean L', 'mass kept +10', 'mass kept +30', 'dragon dead <=10', 'body dead <=10'], [
  ...cornRows(`us, merge2 (${NP})`, cornered(P, s => s === 'us')),
  ...cornRows(`us, all sets (${ON.length})`, cornered(ON, s => s === 'us')),
  ...cornRows(`them in our games (${ON.length})`, cornered(ON, s => s === 'them')),
  ...(TOPG.length ? cornRows(`top-vs-top (${TOPG.length})`, cornered(TOPG, () => true)) : [])]);
say('Same, only turns where the tail was >= 4 from every enemy head:'); say('');
table(['population', 'response', 'turns', 'mean L', 'mass kept +10', 'mass kept +30', 'dragon dead <=10', 'body dead <=10'], [
  ...cornRows(`us, merge2 (${NP})`, cornered(P, s => s === 'us', 'corneredTail4')),
  ...(TOPG.length ? cornRows(`top-vs-top (${TOPG.length})`, cornered(TOPG, () => true, 'corneredTail4')) : [])]);

H('1d. How often long dragons (>=6) have a shorter enemy head (<=4) within 3, and an ally head within 3 (per long-dragon turn)');
const longT = (games, sidePred) => { const o = {}; for (const g of games) for (const [side, a] of Object.entries(g.agg)) { if (!sidePred(side)) continue; for (const [k, q] of Object.entries(a.longTurns)) { const t = o[k] || (o[k] = { turns: 0, e3: 0, e5: 0, a3any: 0 }); for (const f of Object.keys(t)) t[f] += q[f]; } } return o; };
const ltRows = (label, o) => Object.entries(o).sort().map(([k, q]) => [label, k, q.turns, pc(q.e3, q.turns), pc(q.e5, q.turns), pc(q.a3any, q.turns)]);
table(['population', 'maps | phase', 'turns', 'short enemy head <=3', '<=5', 'ally head <=3'], [
  ...ltRows(`us, merge2 (${NP})`, longT(P, s => s === 'us')), ...ltRows(`them in merge2 games (${NP})`, longT(P, s => s === 'them')),
  ...(TOPG.length ? ltRows(`top-vs-top (${TOPG.length})`, longT(TOPG, () => true)) : [])]);

// ---------------------------------------------------------------------------------------------------------------
H('2. Feed');
const FEED = recs(ON, 'feed');
say('### per set'); say('');
table(['set', 'games', 'feeds', 'per game', 'target alive at the end', 'target body alive at the end', 'drops eaten by us', 'by them'], SETS.map(s => { const xs = FEED.filter(x => x.set === s), d = xs.reduce((a, x) => a + x.drops, 0); return [SHORT[s], nSet(s), xs.length, f1(xs.length / nSet(s)), pc(xs.filter(x => x.tAliveEnd).length, xs.length), pc(xs.filter(x => x.tFamEnd).length, xs.length), pc(xs.reduce((a, x) => a + x.eatOwn, 0), d), pc(xs.reduce((a, x) => a + x.eatEnemy, 0), d)]; }).filter(r => r[2] > 0));
const feedCls = x => {
  const z = x.tDeath; if (!z) return 'target alive at the end';
  const t = z.text || '', lab = t.startsWith('feed') ? 'fed onward (chain)' : t.startsWith('no-exit') ? 'loop stub (no-exit)' : /TRADE/.test(t) ? 'our TRADE' : '';
  if (x.tFamEnd) return 'body lives on: ' + (lab || CA[z.cause]);
  if (z.cause === 2) return (x.map === 'Prisoners Dilemma' ? 'body lost: PD king rammed late' : 'body lost: target rammed');
  if (z.cause === 5) return 'body lost: head-on with our own head';
  return 'body lost: ' + (lab || CA[z.cause]);
};
const FP = FEED.filter(x => PRIMARY.has(x.set)).map(x => ({ ...x, L: x.tLen }));
const fcl = classTable(FP, feedCls, 'merge2: fed target outcome by class (length = target length)');
say(`- targets whose body was lost: killer ${cntStr(FP.filter(x => !x.tFamEnd && x.tDeath), x => x.tDeath.killer ? (x.tDeath.killer.team === x.us ? 'our own L' : 'enemy L') + x.tDeath.killer.len + (x.tKillerIsEnemyKing ? ' (their king)' : '') : 'none')}`);
const nk = FP.filter(x => !x.kingIsTarget);
say(`- target was our longest at the feed ${FP.length - nk.length}/${FP.length}; otherwise the longest was median ${med(nk.map(x => x.kingDistFromFeeder))} tiles away (<=5: ${nk.filter(x => x.kingDistFromFeeder <= 5).length}); body alive at the end: that longest ${nk.filter(x => x.kingFamEnd).length}/${nk.length}, the target ${nk.filter(x => x.tFamEnd).length}/${nk.length}`);
say(`- on the final king's line: the target ${FP.filter(x => x.tIsFinalLine).length}/${FP.length}, the longest at the feed ${FP.filter(x => x.kingIsFinalLine).length}/${FP.length}`);
say('');
for (const [c] of fcl) if (c.startsWith('body lost')) select('2 feed', c, FP.filter(x => feedCls(x) === c), x => x.tLen, x => `#${x.id} L${x.L} feeds #${x.target} L${x.tLen}; target ${x.tDeath ? `r${x.tDeath.r} ${CA[x.tDeath.cause]} "${x.tDeath.text || ''}"` : ''}`);

// ---------------------------------------------------------------------------------------------------------------
H('3. Gathering (g label), dragons outside the corridor loop');
const GA = recs(ON, 'gather').filter(x => !x.loop).map(x => ({ ...x, r: x.r0 }));
const gEnd = x => {
  if (x.fed) return 'ok: fed';
  if (x.dMin <= 3) return 'ok: within 3';
  if (x.death && x.death.r <= x.r1 + 2) return x.death.text && /TRADE/.test(x.death.text) ? 'died: our TRADE' : x.death.cause === 5 ? 'died: head-on with our own head' : x.death.killer && x.death.killer.team === x.us ? 'died: into our own body' : x.death.cause === 2 || x.death.cause === 3 ? 'died: enemy ram' : 'died: ' + CA[x.death.cause];
  if (x.r1 >= x.rounds - 2) return 'stopped: game ended';
  if (x.becameKing) return 'stopped: became the longest';
  if (x.unitsAfter < 4) return 'stopped: units < 4';
  if (x.lenAfter !== null && x.lenAfter < 4) return 'stopped: length < 4';
  return 'stopped: goal lost (news stale or goal changed)';
};
say('### per set'); say('');
table(['set', 'games', 'episodes', 'ok (fed or within 3)', 'died on the way (mech_check def.)', 'of which into our own dragons'], SETS.map(s => { const xs = GA.filter(x => x.set === s); const d = xs.filter(x => x.death); return [SHORT[s], nSet(s), xs.length, pc(xs.filter(x => x.ok).length, xs.length), `${d.length} (${pc(d.length, xs.length)})`, d.filter(x => x.death.cause === 5 || (x.death.killer && x.death.killer.team === x.us)).length]; }).filter(r => r[2] > 0));
const GP = GA.filter(x => PRIMARY.has(x.set));
const gcl = classTable(GP, gEnd, 'merge2: gathering episodes by end reason');
say(`- slack (rounds left - start distance) vs ok: ${[[-99, 9], [10, 49], [50, 99], [100, 999]].map(([a, b]) => { const ys = GP.filter(x => { const s = (500 - x.r0) - x.d0; return s >= a && s <= b; }); return `${a < 0 ? '<10' : a + '-' + b}: ${ys.filter(x => x.ok).length}/${ys.length}`; }).join(' · ')}`);
say(`- all deaths after the start (mech_check definition, ${GP.filter(x => x.death).length}): ${cntStr(GP.filter(x => x.death), x => x.death.text && /TRADE/.test(x.death.text) ? 'our TRADE' : x.death.cause === 5 ? 'head-on with our own head' : x.death.killer && x.death.killer.team === x.us ? 'into our own body' : x.death.cause === 2 || x.death.cause === 3 ? 'enemy ram' : CA[x.death.cause])}`);
say(`- path to the presumed goal (static map): through a portal ${GP.filter(x => x.path && x.path.portals > 0).length}/${GP.length}, >30% in enemy territory ${GP.filter(x => x.path && x.path.enemyFrac > 0.3).length}/${GP.length}; goal (our longest) died during a failed episode ${GP.filter(x => !x.ok && x.goalDiedR !== null && x.goalDiedR <= x.r1 + 1).length}`);
say('');
for (const [c] of gcl) if (!c.startsWith('ok')) select('3 gather', c, GP.filter(x => gEnd(x) === c), x => x.L, x => `d0 ${x.d0} -> min ${x.dMin} in ${x.turns} turns${x.death ? `, died r${x.death.r} "${x.death.text || ''}"` : ''}`);

// ---------------------------------------------------------------------------------------------------------------
H('4. Portal crossings');
const PO = recs(ON, 'portal');
const pCls = x => {
  const z = x.death; if (!z || z.r > x.r + 3) return 'body kept';
  const t = z.text || '', v = vOf(x.text), desperate = v !== null && v <= -20 ? ' (desperate entry)' : '';
  if (t.startsWith('feed')) return 'feed (deliberate)';
  const own = z.killer && z.killer.team === x.us;
  if (x.onStep) return (own ? 'exit held by our own dragon' : z.killer ? 'exit held by an enemy' : 'exit blocked') + desperate;
  if (t.startsWith('no-exit')) return 'dead-end exit (no-exit)';
  if (own || z.cause === 5) return 'our own dragon after the exit';
  if (z.cause === 2 || z.cause === 3 || z.cause === 4) return 'enemy after the exit';
  return 'other: ' + CA[z.cause];
};
say('### per set'); say('');
table(['set', 'games', 'crossings', 'per game', 'unexplored exits', 'dragon alive +3', 'body alive +3', 'died on the portal step', 'held by our own dragon'], SETS.map(s => { const xs = PO.filter(x => x.set === s); return [SHORT[s], nSet(s), xs.length, f1(xs.length / nSet(s)), xs.filter(x => x.blind).length, pc(xs.filter(x => x.self3).length, xs.length), pc(xs.filter(x => x.alive3).length, xs.length), xs.filter(x => x.onStep && x.death && x.death.r === x.r).length, xs.filter(x => x.onStep && x.death && x.death.r === x.r && x.death.killer && x.death.killer.team === x.us).length]; }).filter(r => r[2] > 0));
const POP = PO.filter(x => PRIMARY.has(x.set));
const lostBody = POP.filter(x => !x.alive3);
const pcl = classTable(lostBody, pCls, 'merge2: crossings after which the body was lost within 3 rounds');
const selfDead = POP.filter(x => !x.self3);
say(`- dragon itself dead within 3 (${selfDead.length}): ${cntStr(selfDead, pCls)}`);
say(`- Portals map r450+: ${POP.filter(x => x.map === 'Portals' && x.r >= 450).length} crossings, dragon alive +3 ${pc(POP.filter(x => x.map === 'Portals' && x.r >= 450 && x.self3).length, POP.filter(x => x.map === 'Portals' && x.r >= 450).length)}, body ${pc(POP.filter(x => x.map === 'Portals' && x.r >= 450 && x.alive3).length, POP.filter(x => x.map === 'Portals' && x.r >= 450).length)}; dragon deaths ${cntStr(POP.filter(x => x.map === 'Portals' && x.r >= 450 && !x.self3), pCls)}`);
const onStep = POP.filter(x => x.onStep && x.death && x.death.r === x.r);
say(`- died on the portal step (${onStep.length}): ${cntStr(onStep, pCls)}; with a gathering label ${onStep.filter(x => / g\d+/.test(x.text || '')).length}; by map ${cntStr(onStep, x => x.map)}; by phase ${cntStr(onStep, x => phase(x.r))}`);
say('');
for (const [c] of pcl) select('4 portal', c, lostBody.filter(x => pCls(x) === c), x => x.L, x => `"${x.text || ''}"${x.death ? ` -> r${x.death.r} ${CA[x.death.cause]}${x.death.killer ? ' with L' + x.death.killer.len : ''}` : ''}`);
if (TOPG.length) {
  const pt = {}; for (const g of TOPG) for (const a of Object.values(g.agg)) for (const [lc, q] of Object.entries(a.portal)) { const t = pt[lc] || (pt[lc] = { n: 0, self3: 0, body3: 0, onStep: 0, onStepOwn: 0, onStepEnemy: 0 }); for (const f of Object.keys(t)) t[f] += q[f] || 0; }
  const pu = {}; for (const g of P) { const a = g.agg.us; if (!a) continue; for (const [lc, q] of Object.entries(a.portal)) { const t = pu[lc] || (pu[lc] = { n: 0, self3: 0, body3: 0, onStep: 0, onStepOwn: 0, onStepEnemy: 0 }); for (const f of Object.keys(t)) t[f] += q[f] || 0; } }
  say(`### portal crossings by length: merge2 (${NP}) vs top-vs-top (${TOPG.length})`); say('');
  table(['population', 'length', 'crossings', 'dragon alive +3', 'body alive +3', 'died on the step', 'held by own team', 'held by enemy'], [
    ...Object.entries(pu).sort().map(([k, q]) => ['us, merge2', k, q.n, pc(q.self3, q.n), pc(q.body3, q.n), `${q.onStep} (${pc(q.onStep, q.n)})`, q.onStepOwn, q.onStepEnemy]),
    ...Object.entries(pt).sort().map(([k, q]) => ['top-vs-top', k, q.n, pc(q.self3, q.n), pc(q.body3, q.n), `${q.onStep} (${pc(q.onStep, q.n)})`, q.onStepOwn, q.onStepEnemy])]);
}

// ---------------------------------------------------------------------------------------------------------------
H('5. Trades (TRADE label) and head-on pearl flows');
const TRD = recs(ON, 'trade');
const tCls = x => { if (!x.ex || !x.our) return 'not executed'; const t = x.their || {}; const du = Math.min(x.our.colOwn ? x.our.colOwn.d : 99, t.colEnemy ? t.colEnemy.d : 99), dt = Math.min(x.our.colEnemy ? x.our.colEnemy.d : 99, t.colOwn ? t.colOwn.d : 99); return du === 99 ? 'no head of ours within 14' : du <= dt ? 'our collector nearer or equal' : 'their collector nearer'; };
say('### per set'); say('');
table(['set', 'games', 'trades', 'executed', 'pearls us', 'pearls them', 'our collector nearer/equal: us-them', 'otherwise: us-them'], SETS.map(s => { const xs = TRD.filter(x => x.set === s && x.ex), a = xs.filter(x => tCls(x) === 'our collector nearer or equal'), b = xs.filter(x => tCls(x) !== 'our collector nearer or equal'); return [SHORT[s], nSet(s), TRD.filter(x => x.set === s).length, xs.length, xs.reduce((q, x) => q + x.pUs, 0), xs.reduce((q, x) => q + x.pThem, 0), `${a.reduce((q, x) => q + x.pUs, 0)}-${a.reduce((q, x) => q + x.pThem, 0)} (${a.length})`, `${b.reduce((q, x) => q + x.pUs, 0)}-${b.reduce((q, x) => q + x.pThem, 0)} (${b.length})`]; }).filter(r => r[2] > 0));
const TP = TRD.filter(x => PRIMARY.has(x.set) && x.ex);
const tcl = classTable(TP, tCls, 'merge2: executed trades by collector class');
table(['collector class', 'trades', 'our length', 'their length', 'pearls us', 'pearls them'], tcl.map(([c]) => { const ys = TP.filter(x => tCls(x) === c); return [c, ys.length, ys.reduce((q, x) => q + x.L, 0), ys.reduce((q, x) => q + x.killed, 0), ys.reduce((q, x) => q + x.pUs, 0), ys.reduce((q, x) => q + x.pThem, 0)]; }));
for (const [c] of tcl) select('5 trade', c, TP.filter(x => tCls(x) === c), x => x.killed, x => `our L${x.L} kills L${x.killed}: pearls us ${x.pUs} them ${x.pThem}`);
const headon = (games, sidePred) => { const o = { n: 0, spr: 0, col: {} }; for (const g of games) for (const [side, a] of Object.entries(g.agg)) { if (!sidePred(side)) continue; o.n += a.headon.n; o.spr += a.headon.spr; for (const [k, q] of Object.entries(a.headon.col)) { const t = o.col[k] || (o.col[k] = { n: 0, kEat: 0, vEat: 0, drops: 0 }); for (const f of Object.keys(t)) t[f] += q[f]; } } return o; };
const hoRows = (label, o, gamesN) => Object.entries(o.col).sort().map(([k, q]) => [label, `${o.n} (${f1(o.n / gamesN)}/game), rammer sprint ${pc(o.spr, o.n)}`, k, q.n, q.kEat, q.vEat, pc(q.kEat, q.kEat + q.vEat)]);
table(['head-ons', 'total', 'nearest collector', 'n', "pearls to the rammer's team", "to the victim's team", "rammer's share"], [
  ...hoRows(`merge2: they ram us (${NP})`, headon(P, s => s === 'us'), NP), ...hoRows(`merge2: we ram them (${NP})`, headon(P, s => s === 'them'), NP),
  ...(TOPG.length ? hoRows(`top-vs-top (${TOPG.length})`, headon(TOPG, () => true), TOPG.length) : [])]);

// ---------------------------------------------------------------------------------------------------------------
H('6. Policy split children');
const SP = recs(ON, 'split').map(x => ({ ...x, pL: x.L, L: x.cLen }));
const sCls = x => {
  if (x.alive30) return 'alive 30 rounds';
  if (x.childFam30) return 'child dead, body lives on (its own escape split)';
  const z = x.death; if (!z) return 'dead (unknown)';
  if (z.cause === 1 || (z.text || '').startsWith('no-exit')) return x.blindBefore ? 'trapped after entering an unexplored portal' : x.portalBefore ? 'trapped after a known portal' : 'trapped in a pocket (no portal)';
  if (z.cause === 2) return x.killerAge > 50 ? 'rammed by an old hunter (>50 rounds)' : 'rammed by a young piece (<=50 rounds)';
  if (z.cause === 3) return 'our child rammed (TRADE or forced)';
  return 'other: ' + CA[z.cause];
};
say('### per set'); say('');
table(['set', 'games', 'policy splits', 'child alive 30', 'child body alive 30', 'rammed <=30', 'trapped <=30'], SETS.map(s => { const xs = SP.filter(x => x.set === s); return [SHORT[s], nSet(s), xs.length, pc(xs.filter(x => x.alive30).length, xs.length), pc(xs.filter(x => x.alive30 || x.childFam30).length, xs.length), xs.filter(x => !x.alive30 && x.death && x.death.cause === 2).length, xs.filter(x => !x.alive30 && x.death && x.death.cause === 1).length]; }).filter(r => r[2] > 0));
const SPP = SP.filter(x => PRIMARY.has(x.set));
const scl = classTable(SPP.filter(x => !x.alive30), sCls, 'merge2: policy split children dead within 30 rounds by class (length = child length)');
say(`- death rate by the nearest enemy head at birth: ${[[0, 4], [5, 8], [9, 99]].map(([a, b]) => { const ys = SPP.filter(x => x.eHead >= a && x.eHead <= b); return `${a}-${b === 99 ? '' : b}: ${ys.filter(x => !x.alive30).length}/${ys.length} (${pc(ys.filter(x => !x.alive30).length, ys.length)})`; }).join(' · ')}; by territory at birth: ${cnt(SPP, x => x.terrBirth).map(([k]) => { const ys = SPP.filter(x => x.terrBirth === k); return `${k} ${ys.filter(x => !x.alive30).length}/${ys.length}`; }).join(' · ')}`);
const rmK = SPP.filter(x => !x.alive30 && x.death && x.death.cause === 2);
say(`- rammed children: killer length ${cntStr(rmK, x => 'L' + x.death.killer.len)}, killer sprint ${rmK.filter(x => x.death.killer.steps >= 2).length}/${rmK.length}, territory at death ${cntStr(rmK, x => x.terrDeath)}, child age ${cntStr(rmK, x => x.deathAge <= 5 ? '0-5' : x.deathAge <= 15 ? '6-15' : '16-30')}; pearls of the children us ${rmK.reduce((s, x) => s + (x.eatenOwn || []).filter(t => t === 'us').length, 0)} them ${rmK.reduce((s, x) => s + (x.eatenOwn || []).filter(t => t === 'them').length, 0)}, of their rammers us ${rmK.reduce((s, x) => s + (x.pairEaten || []).filter(t => t === 'us').length, 0)} them ${rmK.reduce((s, x) => s + (x.pairEaten || []).filter(t => t === 'them').length, 0)}`);
const trappedBlind = SPP.filter(x => !x.alive30 && sCls(x) === 'trapped after entering an unexplored portal');
say(`- trapped after an unexplored portal: rounds from the last crossing to death ${cntStr(trappedBlind, x => '+' + (x.death.r - x.lastCross))}`);
say('');
for (const [c] of scl) if (!c.startsWith('child dead, body lives on')) select('6 split', c, SPP.filter(x => sCls(x) === c), x => x.cLen, x => `parent #${x.id} L${x.pL}, child #${x.child} L${x.cLen}, enemy head ${x.eHead} away at birth -> +${x.deathAge} ${x.death ? CA[x.death.cause] : ''}`, x => -(x.deathAge ?? 99));
const children = (games, sidePred) => { const o = { n: 0, dead30: 0, causes: {} }; for (const g of games) for (const [side, a] of Object.entries(g.agg)) { if (!sidePred(side)) continue; o.n += a.children.n; o.dead30 += a.children.dead30; for (const [k, v] of Object.entries(a.children.causes)) o.causes[k] = (o.causes[k] || 0) + v; } return o; };
const chRow = (label, o, gamesN) => [label, o.n, f1(o.n / gamesN), pc(o.dead30, o.n), Object.entries(o.causes).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${CA[k]} ${v}`).join(' · ')];
table(['population (children L<=3, all kinds of split)', 'children', 'per game', 'dead within 30', 'causes'], [chRow(`us, merge2 (${NP})`, children(P, s => s === 'us'), NP), chRow(`them in merge2 games (${NP})`, children(P, s => s === 'them'), NP), ...(TOPG.length ? [chRow(`top-vs-top, per team-game (${TOPG.length})`, children(TOPG, () => true), 2 * TOPG.length)] : [])]);

// ---------------------------------------------------------------------------------------------------------------
H('7. Sacrifices (self-inflicted death with a free neighbour)');
const sacAgg = (games, sidePred, ph) => { const o = { n: 0, len: 0, drops: 0, own: 0, enemy: 0, withE: 0, eAlive: 0, eLine: 0, v23: 0, v47: 0, v8: 0, colD: {}, colL: {} }; for (const g of games) for (const [side, a] of Object.entries(g.agg)) { if (!sidePred(side)) continue; const q = a.sac[ph]; if (!q) continue; for (const f of ['n', 'len', 'drops', 'own', 'enemy', 'withE', 'eAlive', 'eLine', 'v23', 'v47', 'v8']) o[f] += q[f]; o.colD = mergeHist(o.colD, q.colD); o.colL = mergeHist(o.colL, q.colL); } return o; };
const sacRow = (label, o, teamGames) => [label, o.n, f1(o.n / teamGames), f1(o.len / teamGames), pc(o.own, o.drops), pc(o.enemy, o.drops), histMed(o.colD), histMed(o.colL), `${o.eAlive}/${o.withE}`, `${o.eLine}/${o.withE}`, pc(o.v23, o.n)];
table(['population', 'sacrifices', 'per team-game', 'length per team-game', 'drops eaten by own team', 'by enemy', 'nearest own head (median)', 'its length (median)', "an eater's body alive at the end", "an eater on the final king's line", 'L2-3 share'], [
  ...['r0-249', 'r250+'].map(ph => sacRow(`us, merge2 ${ph} (${NP})`, sacAgg(P, s => s === 'us', ph), NP)),
  ...['r0-249', 'r250+'].map(ph => sacRow(`them in merge2 games ${ph} (${NP})`, sacAgg(P, s => s === 'them', ph), NP)),
  ...(TOPG.length ? ['r0-249', 'r250+'].map(ph => sacRow(`top-vs-top ${ph} (${TOPG.length})`, sacAgg(TOPG, () => true, ph), 2 * TOPG.length)) : [])]);

// ---------------------------------------------------------------------------------------------------------------
H('8. Independent recount (exp/mech-failures/recount.js: raw events, no step simulation) beside the primary numbers');
const rc = games => games.map(g => g.recount).filter(Boolean);
const rows = [];
for (const s of [...SETS, 'ALL']) {
  const gs = s === 'ALL' ? ON : ON.filter(g => g.meta.set === s); if (!gs.length) continue;
  const R = rc(gs).map(x => x.mech).filter(Boolean);
  const pe = recs(gs, 'esc');
  const exA = x => x.steps >= 2 && !(x.death && x.death.r === x.r && x.death.cause !== 2);
  const pr = (k) => { const xs = pe.filter(x => x.k === k); return `${xs.length}/${xs.filter(exA).length}/${xs.filter(x => exA(x) && !x.alive10).length} (mech_check ex ${xs.filter(x => x.ex).length}/${xs.filter(x => x.ex && !x.alive10).length})`; };
  const rr = (k) => `${R.reduce((a, x) => a + x[k].n, 0)}/${R.reduce((a, x) => a + x[k].ex, 0)}/${R.reduce((a, x) => a + x[k].fail, 0)}`;
  const ramsP = gs.flatMap(g => g.rams.filter(r => r.side === 'us' && r.len >= 6)).length, ramsR = R.reduce((a, x) => a + x.ramsLong.n, 0);
  const fd = recs(gs, 'feed'), sp = recs(gs, 'split'), tr = recs(gs, 'trade').filter(x => x.ex), po = recs(gs, 'portal').filter(x => x.onStep && x.death && x.death.r === x.r);
  rows.push([s === 'ALL' ? 'ALL' : SHORT[s], `${pr('esc')} ; ${rr('esc')}`, `${pr('sprintEsc')} ; ${rr('sprintEsc')}`, `${ramsP} ; ${ramsR}`,
    `${fd.length}/${fd.filter(x => x.tFamEnd).length} ; ${R.reduce((a, x) => a + x.feed.n, 0)}/${R.reduce((a, x) => a + x.feed.famEnd, 0)}`,
    `${tr.reduce((a, x) => a + x.pUs, 0)}-${tr.reduce((a, x) => a + x.pThem, 0)} ; ${R.reduce((a, x) => a + x.trade.us, 0)}-${R.reduce((a, x) => a + x.trade.them, 0)}`,
    `${sp.filter(x => x.ex !== 0).length}/${sp.filter(x => x.alive30).length} ; ${R.reduce((a, x) => a + x.split.n, 0)}/${R.reduce((a, x) => a + x.split.alive30, 0)}`,
    `${po.length} ; ${R.reduce((a, x) => a + x.portalStepDeaths, 0)}`]);
}
say('Each cell: primary ; recount. esc and sprintEsc: fired/executed/body dead within 10. Feed: feeds/target body alive at the end. Trade: pearls us-them. Split: splits/child alive 30. Portal: our deaths on a portal step (primary: exit held, O/H; recount: any death on a portal step).'); say('');
table(['set', 'esc', 'sprintEsc', 'rams on our L>=6', 'feed', 'trade pearls', 'policy split', 'portal-step deaths'], rows);
const cmp = (games, label, gamesN) => {
  const R = rc(games); let hoP = 0, hoR = 0, hoPk = 0, hoRk = 0, chP = 0, chR = 0, chPd = 0, chRd = 0, snP = 0, snR = 0, snPo = 0, snRo = 0, e3P = 0, e3R = 0, tP = 0, tR = 0;
  for (const g of games) for (const [side, a] of Object.entries(g.agg)) {
    hoP += a.headon.n; hoPk += Object.values(a.headon.col).reduce((s, q) => s + q.kEat, 0); chP += a.children.n; chPd += a.children.dead30;
    if (a.selfNoHit) { snP += a.selfNoHit.n; snPo += a.selfNoHit.own; }
    for (const q of Object.values(a.longTurns)) { e3P += q.e3; tP += q.turns; }
  }
  for (const x of R) { for (const q of Object.values(x.heads)) { hoR += q.n; hoRk += q.kEat; } for (const q of Object.values(x.children)) { chR += q.n; chRd += q.dead30; } for (const q of Object.values(x.selfNoHit)) { snR += q.n; snRo += q.own; } for (const q of Object.values(x.expo)) { e3R += q.e3; tR += q.turns; } }
  return [label, gamesN, `${hoP}/${hoPk} ; ${hoR}/${hoRk}`, `${chP}/${chPd} ; ${chR}/${chRd}`, `${snP}/${snPo} ; ${snR}/${snRo}`, `${tP}/${e3P} ; ${tR}/${e3R}`];
};
say('Population counters (both sides). Head-ons: victims/pearls to the rammer. Children L<=3: n/dead within 30. Self-inflicted deaths hitting no dragon from r250: n/drops eaten by own team. Long-dragon turns: turns/with a shorter enemy head within 3 (primary: path-free torus Manhattan; recount: the same distance on tracked heads).'); say('');
table(['population', 'games', 'head-ons', 'children', 'self deaths r250+', 'long-dragon turns'], [cmp(ON, 'our online sets', ON.length), ...(TOPG.length ? [cmp(TOPG, 'top-vs-top', TOPG.length)] : [])]);

// ---------------------------------------------------------------------------------------------------------------
H('9. Replays selected for close reading (stage 3)');
say('Rule, per class of the primary sample: the extreme case (largest length at stake; for split children the soonest death; ties: lower game id, earlier round) and up to two representative cases (closest to the class median of the same measure; first from opponents not yet picked in the class, then maps not yet picked; ties: lower game id, earlier round).'); say('');
table(['pattern', 'class', 'role', 'set', 'game', 'map', 'opponent', 'round', 'dragon', 'L', 'note'], selections.map(s => [s.pattern, s.cls, s.role, SHORT[s.set], s.game, s.map, s.opp, s.r, '#' + s.id, s.L, s.note.replace(/\|/g, '/')]));
if (opt('--select')) fs.writeFileSync(opt('--select'), JSON.stringify(selections, null, 1));
console.log(out.join('\n'));
