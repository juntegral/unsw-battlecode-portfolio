#!/usr/bin/env node
// Mechanism application check (구현 적용 확인), the per-wave online feedback since 2026-09-30 10:10 KST.
// For each mechanism our bot implements: did it fire against these opponents, in the situation it was designed for, and
// did its designed immediate effect happen? Win rate is not a criterion (user rule; see research/OVERNIGHT-2026-09-29.md).
// Our bot labels every turn with INDICATOR text, which the server keeps in replays; the labels are read on top of the
// mass-ledger reconstruction (tools/mass_ledger.js perGame hooks: moves, sprints, portals, splits, deaths by cause,
// every pearl's source and eater).
//
// usage (repository root):
//   node tools/mech_check.js <pool> [--vs <pool>] [--out <file.md>] [--json <file.json>] [--cases 10] [--jobs 4]
//     <pool>: sets joined with '+'. A set is an online set under data/online/ (index.json + M<id>.replay) or a local
//             eval folder such as exp/merge2-a-px4 (rows.jsonl + games/<opp>_<map>_<side>_<seed>/game.replay).
//     --vs:   a second pool shown beside the first in the summary (previous wave, or local proxy games).
//
// Mechanisms (indicator text written in bot/plan.cpp decide(); a new mechanism gets its own tag and a section here):
//   feed      "feed #<ally> d<dist> L<len>": die into our neck so the longer ally eats the pearls (late consolidation).
//             Effect: the dropped pearls are eaten by our team (by the named ally in particular) and the ally lives on.
//   pocket    "pocket-eat ...": eat one pearl in a walled dead end before the forced escape split (pd10e).
//             Effect: a split within 2 turns, and the child lives 20 rounds.
//   escsplit  "escape-split<n> L<len>": no safe move; hand the body to a child born at the tail (corridor fortress loop).
//             Effect: the child lives 10 and 30 rounds.
//   split     "split<n> u<units> L<len>": policy split. Effect: the child lives 30 rounds; family length 30 rounds on.
//   esc       move label with " esc": 2-3 step escape sprint from shorter enemy heads (avoid6).
//             Situation: a shorter enemy head within 4. Effect: alive 5 and 10 rounds later.
//   portal    every portal crossing (label "PORTAL?" = an unseen exit, portal1). Effect: alive 3 and 10 rounds later,
//             pearls eaten in the 10 rounds after.
//   trade     move label with " TRADE": ram an enemy head (adjacent, or a kill path of 3+ steps).
//             Executed: the head-on happened. Effect: killed length >= ours; the pearls of both go to us.
//   sprint    other 2+ step moves (pearl sprints). Effect: a pearl eaten during the move.
//   K/g, T, late: turn counts (gather goal toward the king / any ally; rammer trust: escapes off; endgame mode).
//   health    degraded / no-exit / last-trade labels, timeouts, instruction counts (only our side is in the replay).
//   stack1:   conv "feed #<ally> d<dist> L<len> conv" (M1), " ram4"/" ram4o" + " c1"/" c0" on TRADE (M2), " ks" (M3).
//   frag      "split<n> u<units> L<len> frag" (stack2 S1): a non-king dragon splits off a small piece from r250 to r420.
//             Situation: the parent is not the team's longest and no enemy head is within its 7x7 view (Chebyshev 3).
//             Effect: the piece lives 30 rounds having eaten >= 1 pearl, or it is later fed to an ally (feed/conv).
//   grab      move label with " grab@<x>,<y>" (stack2 S2): the move eats or closes in on a fresh death drop. One record per
//             targeted pearl (tile + the death that dropped it). Situation: the pearl is a death drop in the ledger.
//             Effect: our team eats it (share of the targeted drops; the opponent's share beside it).
//   Hypothesis metrics (tag-independent, any set): B3 ram rate, sacrifice length after r250, king loss after r450,
//             our dragons at r400 and splits in r350-449 (H3), natural pearls of our territory eaten by the opponent (H2),
//             pearls of head-on exchanges and of enemy deaths eaten by us (H5).
//   stack4 (research/experiments/cand-stack4.md; study research/observations/mech-merge2-failures.md):
//   tg        move label " tg" / " tgx": the threat-gap fix saw threat on some candidate's tiles that stack3's model did not;
//             tg = the chosen move avoids it, tgx = the chosen move carries it. Situation: an enemy head within path distance
//             5 (kelp and bodies block, tails do not).
//             Effect: not rammed within 2 rounds.
//   escsplit2 "esc-split<n> L<len>": cornered (every single step inside a shorter head's reach), tail safe: split instead of a
//             sprint. Situation: cornered at that turn. Effect: body (family) length kept +30 (ratio of sums), body alive +10.
//   px        move label " px" / " pxx": a candidate portal crossing got the own-crowding penalty; px = avoided, pxx = crossed.
//             Effect: no death that turn against our own dragon.
//   gx        move label " gx" (one record per dragon): gathering suppressed, too few rounds left. Effect: alive at the end.
//   sx        move label " sx": a policy split blocked by the tail distance rule (counts); policy splits may end " e<d>".
//   stack4 hypothesis metrics (tag-independent, any set; appended section): rams on our L>=6 dragons classified at the last
//             decision exactly as exp/mech-failures/report.js ramCls (blind spot, reach gap, ...), r400 king rams with v >= 0,
//             non-desperate portal-step deaths against our own dragon, gather deaths against our own dragons, cornered
//             turns by response (split / sprint) with body length kept +10/+30.
//   stack5 (research/experiments/cand-stack5.md; study research/observations/top-territory.md section 10):
//   csplit    "csplit<n> u<units> L<len> t<target>[ v][ k]": coverage split before r250 while the team has fewer units than the
//             map-scaled target (v = an enemy head in view, k = the parent believed it was our longest). Situation: the parent
//             is not the team's longest dragon of length >= 8. Effect (the study's two gates, as pass2.js measures top winners):
//             the child eats >= 1 natural pearl within 30 rounds; the child is alive 30 rounds later (or at the end).
//   fguard    move label " F<d>@<x>,<y>" (one record per dragon and chosen fountain): head for an unguarded fountain of our side
//             and hold its group. Situation: a true fountain of the game's layout in our territory with no other head of ours
//             within 3 steps at the first tag. Effect: after the head comes within 3 steps (path, bodies ignored) of it, our
//             team eats >= 85% of the natural pearls spawned in the next 30 rounds on the true fountains within 3 steps of it.
//   cov       move label " cov": a piece's move ends on our side with no ally head within 6. Effect: it eats a natural pearl of
//             our territory within 20 rounds.
//   stack5 hypothesis metrics (tag-independent; section shown with stack5 tags or --territory): our units, own-territory Voronoi
//             share by capacity and own fountains with our head within 3 steps at r100; natural pearls (r >= 0 spawns) of our
//             territory and of its fountains eaten by the opponent (exp/territory-analysis/extract.js definitions).
//   cand-conv2 (research/experiments/cand-conv2.md; study research/observations/conversion-chain.md):
//   kc        conv / feed label ending " kc": the target is the agreed king candidate (the longest ally with fresh news) or an
//             ally at least as long minus 2. Effect: the dropped pearls are eaten by the final king's line (share).
//   kch       move label " kch" (one record per dragon): a conv or feed was held because the eligible ally was not the candidate.
//             Effect: the dragon later fed the candidate (a kc label) or its body lives at the end.
//   k2        "feed #<id> d<dist> L<len> k2": the second stage (mid -> king) from r400. Situation: the target is the team's longest
//             at that moment. Effect: >= half of the dropped pearls are eaten by the final king's line.
//   k2g       move label " k2" (one record per dragon): the stronger pull toward the candidate from r400. Effect: the dragon ends
//             by a labelled feed (k2, feed or conv).
//   Lineage metrics (tag-independent; section shown with conv2 tags or --lineage): the final king's line = the longest dragon at
//             the end followed back through its parents; member i owns the rounds from its birth to the birth of member i+1. Our
//             labelled conversions' pearls eaten by the line, sacrifice pearls from r300 eaten by it, the line's sacrifice pearls
//             after r350, and our non-king dragons of length >= 8 at r400 (their family after r400 alive at the end off the line,
//             or giving pearls to the line).
//   cand-mapid (research/experiments/cand-mapid.md):
//   mapid     " map=<Name>/<a|b|?>" (or " map=?", " map=none") on a process's first turn and on every change of its map
//             recognition. One record per game. Truth: the map name, and the pearl layout from the local map file name
//             (*_b, *_10 = b) or, online, from the replay's natural spawns on tiles that never spawn in the other layout
//             (layoutTruth; Prisoners Dilemma: 10 starting dragons = b). Effect (the gate): at least one process decided and
//             every decided process (its last tag names a layout) names the true map and layout. Games whose layout the
//             replay cannot tell (no discriminating spawn before the end) are left out of the rate.
//   stack7 (research/experiments/cand-stack7.md; study research/observations/our-eliminations.md section 4):
//   floor     "split<n> u<units> L<len> floor": from r30, while the team has <= 3 dragons, a dragon of length >= 4 splits off a
//             2-child (enemy heads in view allowed). Situation: the opponent has >= 8 dragons at the firing (replay count).
//             Effect: the child is alive 30 rounds later (or at the end).
//   kcap      "split<n> u<units> L<len> kcap": before r250, while the team has < 6 dragons, the dragon that believes it is our
//             longest (length >= 7) splits off a 2-child. Situation: the parent is the team's longest at the firing (ledger king,
//             ties to the lowest id) and r < 250. Effect: the child is alive 10 rounds later (the parent's 10 rounds beside it).
//   stack8 (research/experiments/cand-stack8.md; failure classes exp/cand-stack8/study.js):
//   F2        " F2" after the F tag: the F target's fountain and side came from the recognised map (F episodes carry f2 from their
//             first tag; dbl = another of our dragons' F episode on the same fountain overlaps it). Gates on F2 episodes with the F
//             definitions: designed situation, arrival, group pearl share, overlapping chases.
//   fp        " Fp@<x>,<y>" (F2p): the F pull is off this turn for a claimed pearl (the F tag stays). One record per dragon and named
//             pearl (tile + origin). Situation: the pearl is on the board at the label and no other head (either team) is nearer
//             (path, bodies ignored). Effect: this dragon eats it within 10 rounds (the opponent's share beside it).
//   cl / ce   " cl@<x>,<y>" / " ce@<x>,<y>" (supply-chain claims, one record per dragon and named pearl). cl situation: a natural pearl
//             whose unique nearest own head is the labelled piece; effect: the piece eats it (our team, our longer dragons beside it).
//             ce situation: an enemy head within our distance + 1 of the pearl; effect: the opponent does not eat it; rammed within 5.
//   px2       move label " px2" / " px2x": a crossing whose previous-round probe echoed our own dragon paid px2's penalty; px2 = not
//             crossed. Situation: this dragon's previous-round ping from its head tile stopped on a dragon of ours (replay).
//   stack8 metrics (section shown with stack8 tags or --stack8): F's pull-away turns (an F-tagged move that raises our path distance
//             to a natural pearl within 7, outside 3 of the target, that no other head is as near to), and every portal crossing by
//             the previous-round probe from the crossing tile in the crossing direction (clean / ally / enemy / none).
//   stack7 metrics (tag-independent; section shown with floor/kcap tags or --elim), definitions of exp/eliminations (top.js I,
//             lib.js classOf): the low-unit episode = the first r in 50, 55, ... (r + 20 before the end, before our elimination)
//             with our units 1-3 and the opponent's >= 8 at the round's first turn; in [r, r + 20) our splits (non-escape tags,
//             floor alone, all), recovery = >= 4 dragons alive at r + 20, eliminated within 50 rounds. Per game: eliminated, its
//             round and class (E1/E2/E3m/E3l), units at r100, longest at r50, deaths of length >= 8. Map gate: floor/kcap firings
//             by true map and by the firing process's own last " map=" tag.
'use strict';
const fs = require('fs'), path = require('path'), cp = require('child_process');

const ROOT = path.resolve(__dirname, '..'), ONLINE = path.join(ROOT, 'data', 'online');
const MAPNAME = { autarky: 'Autarky', default: 'Default', devil: 'Devil', portals: 'Portals', prisoners_dilemma: 'Prisoners Dilemma',
  queen_of_spades: 'Queen Of Spades', schooltime: 'Schooltime', slithery_fight: 'Slithery Fight', trauma: 'Trauma', trophy: 'Trophy' };
const PHASES = [[0, 100, 'r0-99'], [100, 250, 'r100-249'], [250, 350, 'r250-349'], [350, 450, 'r350-449'], [450, 501, 'r450+']];
const phaseOf = r => PHASES.find(p => r >= p[0] && r < p[1])[2];
// stack7 (cand-stack7.md): the map gate's families (the bot's floorMapOn / kcapMapOn) and the non-escape split tags
const S7_FLOOR_MAPS = new Set(['Trophy', 'Queen Of Spades', 'Devil', 'Default', 'Schooltime', 'Trauma', 'Slithery Fight']);
const S7_KCAP_MAPS = new Set(['Trophy', 'Queen Of Spades', 'Devil', 'Default', 'Schooltime', 'Trauma']);
const S7_SPLITS = new Set(['split', 'frag', 'bsplit', 'csplit', 'kcap', 'floor']);

// ---------------------------------------------------------------------------------------------------------------
// cand-mapid: the true pearl layout of a game from its replay (same rule as exp/mapid/layout.js). A second layout turns some
// mirror groups off (TILE max 0), so one natural spawn (a pearl tileChange after roundStart, before the round's first
// turnStart) on a tile that never spawns in layout X rules X out. 'a' / 'b' / '?' (no discriminating spawn) / 'x' (both).
const LAYOUT_FILES = { 'Devil': ['devil', 'devil_b'], 'Queen Of Spades': ['queen_of_spades', 'queen_of_spades_b'], 'Schooltime': ['schooltime', 'schooltime_b'],
  'Slithery Fight': ['slithery_fight', 'slithery_fight_b'], 'Prisoners Dilemma': ['prisoners_dilemma', 'prisoners_dilemma_10'] };
const layoutTables = new Map();
function spawnTable(file) {
  if (!layoutTables.has(file)) {
    const L = fs.readFileSync(file, 'utf8').split('\n'), m = /^MAP (\d+) (\d+)/.exec(L[0]), W = +m[1], on = new Uint8Array(W * +m[2]);
    for (const l of L) if (l.startsWith('TILE ')) { const [x, y, , mx] = l.trim().split(/\s+/).slice(1).map(Number); on[y * W + x] = mx > 0 ? 1 : 0; }
    layoutTables.set(file, on);
  }
  return layoutTables.get(file);
}
function layoutTruth(R, mapName) {
  const M = R.match.map, f = LAYOUT_FILES[mapName];
  if (!f) return 'a';
  if (mapName === 'Prisoners Dilemma') return M.initialDragons.length === 10 ? 'b' : 'a';
  const a = spawnTable(path.join(ROOT, 'maps', 'online-20260927', f[0] + '.map')), b = spawnTable(path.join(ROOT, 'maps', 'variants', f[1] + '.map'));
  if (a.length !== M.width * M.height) return '?';
  let evA = 0, evB = 0, rs = false;
  for (const e of R.events) {
    if (e.type === 'roundStart') rs = true; else if (e.type === 'turnStart') rs = false;
    else if (rs && e.type === 'tileChange' && e.hasPearl) { const k = e.tile.y * M.width + e.tile.x; if (a[k] && !b[k]) evA++; else if (b[k] && !a[k]) evB++; }
  }
  return evA && !evB ? 'a' : evB && !evA ? 'b' : evA && evB ? 'x' : '?';
}

// ---------------------------------------------------------------------------------------------------------------
// Indicator labels (bot/plan.cpp decide()).
function parseInd(s) {
  if (!s) return { kind: 'none' };
  let m;
  if ((m = /^feed #(\d+) d(\d+) L(\d+)( conv)?/.exec(s))) return { kind: / k2(?:\s|$)/.test(s) ? 'k2' : m[4] ? 'conv' : 'feed', target: +m[1], dist: +m[2], kc: / kc(?:\s|$)/.test(s) ? 1 : 0 }; // cand-conv2 k2, kc
  if ((m = /^pocket-eat L(\d+) b(\d+)(x?)/.exec(s))) return { kind: 'pocket', birthLen: +m[2], exposed: m[3] === 'x' };
  if ((m = /^escape-split(\d+) L(\d+)/.exec(s))) return { kind: 'escsplit', size: +m[1] };
  if ((m = /^esc-split(\d+) L(\d+)/.exec(s))) return { kind: 'escsplit2', size: +m[1] };                                        // stack4 esc-split
  if ((m = /^split(\d+) u(\d+) L(\d+)( frag)?/.exec(s))) { const e = / e(\d+)(?:\s|$)/.exec(s);                                   // frag: stack2 S1
    return { kind: m[4] || / frag(?:\s|$)/.test(s) ? 'frag' : / bsp(?:\s|$)/.test(s) ? 'bsplit' : / kcap(?:\s|$)/.test(s) ? 'kcap' : / floor(?:\s|$)/.test(s) ? 'floor' : 'split', // kcap, floor: stack7
      size: +m[1], units: +m[2], e: e ? +e[1] : null }; } // e: stack4 fix 6; bsp: cand-mapid
  if ((m = /^csplit(\d+) u(\d+) L(\d+) t(\d+)/.exec(s))) return { kind: 'csplit', size: +m[1], units: +m[2], target: +m[4], view: / v(?:\s|$)/.test(s), king: / k(?:\s|$)/.test(s) }; // stack5 csplit
  if (s.startsWith('last-trade')) return { kind: 'lasttrade' };
  if (s.startsWith('no-exit')) return { kind: 'noexit' };
  if (s.startsWith('degraded')) return { kind: 'degraded' };
  if ((m = /^([NESW]+) v(\S+) d(\d+) L(\d+)(.*)$/.exec(s))) {
    const f = { kind: 'move', dirs: m[1], v: +m[2], depth: +m[3], trade: false, blind: false, late: false, esc: false, trust: false, goal: null, goalDist: null, ram4: null, coll: null, ks: false, grab: null, extra: [] };
    for (const t of m[5].split('|')[0].trim().split(/\s+/).filter(Boolean)) {
      let g;
      if (t === 'TRADE') f.trade = true; else if (t === 'PORTAL?') f.blind = true; else if (t === 'late') f.late = true;
      else if (t === 'esc') f.esc = true; else if (t === 'T') f.trust = true;
      else if (/^[Kg]\d+$/.test(t)) { f.goal = t[0]; f.goalDist = +t.slice(1); }
      else if (t === 'ram4' || t === 'ram4o') f.ram4 = t === 'ram4' ? 'new' : 'old'; // stack1 M2
      else if (t === 'c1' || t === 'c0') f.coll = t === 'c1' ? 1 : 0;
      else if (t === 'ks') f.ks = true;                                                // stack1 M3
      else if (t === 'ks2') f.ks2 = true;                                              // stack3 ks2
      else if ((g = /^grab@(\d+),(\d+)$/.exec(t))) f.grab = { x: +g[1], y: +g[2] };   // stack2 S2
      else if (t === 'tg' || t === 'tgx') f.tg = t;                                    // stack4 tg
      else if (t === 'px' || t === 'pxx') f.px = t;                                    // stack4 px
      else if (t === 'gx') f.gx = true;                                                // stack4 gx
      else if (t === 'sx') f.sx = true;                                                // stack4 sx
      else if ((g = /^F(\d+)@(\d+),(\d+)$/.exec(t))) f.fg = { d: +g[1], x: +g[2], y: +g[3] }; // stack5 F
      else if (t === 'cov') f.cov = true;                                              // stack5 cov
      else if (t.startsWith('map=')) {}                                                // cand-mapid (read in the indicator hook)
      else if (t === 'kch') f.kch = true;                                              // cand-conv2 kc hold
      else if (t === 'k2') f.k2g = true;                                               // cand-conv2 k2 pull
      else if (t === 'F2') f.f2 = true;                                                // stack8 F2
      else if ((g = /^Fp@(\d+),(\d+)$/.exec(t))) f.fp = { x: +g[1], y: +g[2] };      // stack8 F2p
      else if (t === 'px2' || t === 'px2x') f.px2 = t;                                 // stack8 px2
      else if ((g = /^c([le])@(\d+),(\d+)$/.exec(t))) f['c' + g[1]] = { x: +g[2], y: +g[3] }; // stack8 cl / ce
      else f.extra.push(t);
    }
    return f;
  }
  return { kind: 'other', word: s.split(/\s+/)[0].replace(/[#\d]+$/, '').slice(0, 24) };
}

// ---------------------------------------------------------------------------------------------------------------
// One game: records of mechanism firings with their context and effects.
function analyse(R, task, perGame) {
  const us = task.us;
  const nInit = R.match.map.initialDragons.length;
  const info = { map: task.map };
  if (task.map === 'Prisoners Dilemma') info.variant = nInit === 10 ? 'PD10' : 'PD6';
  const mapKey = info.variant === 'PD10' ? 'Prisoners Dilemma (10)' : task.map; // the two PD versions play differently
  let truthLay0 = null; const truthLay = () => truthLay0 !== null ? truthLay0 : (truthLay0 = task.layout || layoutTruth(R, task.map)); // cand-mapid
  const life = new Map();      // our dragon id -> { born, parent, lens: [r, len, ...], death, eats: [r...] }
  const deathEat = new Map();  // death index -> [[eaterId, eaterTeam, round], ...]
  const recs = [], pending = new Map(), ind = new Map(), ctxOf = new Map(), lastTrust = new Map(), lastEscSplit = new Map(), gather = new Map();
  const c2Hold = new Map(), c2Pull = new Map();  // cand-conv2: kch / k2 move-tag episodes by dragon id
  const mapTags = new Map();   // cand-mapid: our dragon id -> [{ r, tag }] (" map=..." tags in label order)
  const health = { turns: 0, labelled: 0, degraded: 0, noexit: 0, lasttrade: 0, fault: 0, maxInstr: 0, over80: 0, exceeded: 0, lowDepth: 0, moveTurns: 0 };
  const counts = { K: 0, g: 0, T: 0, late: 0, ks: 0, ks2: 0, trustRammed: 0, extra: {}, other: {} };
  // hypothesis metrics measured from the replay whether or not the bot labels them (comparable with any earlier set):
  //   b3Elig/b3Ram: turns of our piece (length <= 4) with an enemy head one tile away (torus) at least as long / rams on them
  //   sac250: our self-inflicted deaths with a free neighbour (ledger cause 'sac') from r250: count, length, pearls, own-eaten
  //   king450: length of our king deaths (team's longest, >= 8) from r450
  const hyp = { b3Elig: 0, b3Ram: 0, sac250N: 0, sac250Len: 0, sac250Drops: 0, sac250Own: 0, sac250Enemy: 0, king450Len: 0, king450N: 0,
    // (stack3 ks2) late king from r400: turns of our king (>= 8) inside some enemy head's full sprint reach (Manhattan on the
    // torus <= min(length - 1, 7)), and our king deaths by an enemy head-on (rammed) from r400
    kingT400: 0, kingExp400: 0, kingRam400N: 0, kingRam400Len: 0 };
  //   (stack2) g400/u400: games that reached r400 / our living dragons at its start (H3) · split350: our splits in r350-449 (H3)
  //   natOwnUs/Them/Left: natural pearls of our territory eaten by us / by the opponent / still on the board at the end (H2)
  //   xch*: pearls of the two bodies of every head-on between us and the opponent (N, eaten by us, by them); xchR*: the same
  //   when our dragon was rammed (H5) · eDropUs: pearls of enemy deaths eaten by us (H5)
  Object.assign(hyp, { g400: 0, u400: 0, split350: 0, natOwnUs: 0, natOwnThem: 0, natOwnLeft: 0, xchN: 0, xchUs: 0, xchThem: 0, xchRN: 0, xchRUs: 0, xchRThem: 0, eDropUs: 0 });
  const ourTerr = us === 'A' ? 1 : 2;
  let seen400 = false, deathsAll = [];
  const grabPre = new Map(), grabEp = new Map(), eatenBy = new Map(); // stack2 S2: target seen at the label, episodes, pearl eaters
  const sacIdx = [];
  const fin = new Map(); let finKing = -1, rounds = 0;
  const lifeOf = (id, r, parent, len) => { let L = life.get(id); if (!L) { L = { born: r, parent, bornLen: len, lens: [], death: null, eats: [], nat: [], natOwn: [] }; life.set(id, L); } return L; };
  // ---- stack4: decision-moment data, ported from exp/mech-failures/collect.js (study research/observations/mech-merge2-failures.md)
  //   rams:  every head-on death (cause 2) of our L>=6 dragons with what it could know at its last decision (ramCls in report())
  //   corn:  turns of our L>=6 dragons with every single step inside a shorter (<=4) enemy head's reach (collect.js exposure())
  //   pstep: our portal-step deaths (the fatal step crossed a portal), with the blocker's team and the crossing label's value
  const ext = { rams: [], corn: [], pstep: [], gxN: 0, sxN: 0, l6T: 0, l6P4: 0, l6M4: 0, kT: 0, kP4: 0, kP7: 0 };
  const DIRS4 = ['N', 'E', 'S', 'W'], DX4 = [0, 1, 0, -1], DY4 = [-1, 0, 1, 0];
  let GW = 0, GH = 0, NB = null, PORT = null, bStamp = null, bDist = null, bQ = null, bCur = 0;
  const kx = k => k % GW, ky = k => (k / GW) | 0, K = p => p.y * GW + p.x;
  const tdk = (a, b) => { const dx = Math.abs(kx(a) - kx(b)), dy = Math.abs(ky(a) - ky(b)); return Math.min(dx, GW - dx) + Math.min(dy, GH - dy); };
  const chk = (a, b) => { const dx = Math.abs(kx(a) - kx(b)), dy = Math.abs(ky(a) - ky(b)); return Math.max(Math.min(dx, GW - dx), Math.min(dy, GH - dy)); };
  function initGeo(c) {
    GW = c.W; GH = c.H; const N = GW * GH;
    NB = new Int32Array(N * 4).fill(-1); PORT = new Uint8Array(N * 4);
    for (let k = 0; k < N; k++) for (let d = 0; d < 4; d++) {
      const x = kx(k), y = ky(k), nx = c.across(x, y, DIRS4[d]); if (!nx) continue;
      NB[k * 4 + d] = nx.y * GW + nx.x;
      if (nx.x !== ((x + DX4[d]) % GW + GW) % GW || nx.y !== ((y + DY4[d]) % GH + GH) % GH) PORT[k * 4 + d] = 1;
    }
    bStamp = new Int32Array(N); bDist = new Int32Array(N); bQ = new Int32Array(N);
  }
  // BFS from sources over tiles for which pass(k) is true (sources always pass); visit(k, d, blocked) returns true to stop
  function bfs(srcs, maxD, pass, visit) {
    bCur++; let qh = 0, qt = 0;
    for (const s of srcs) { if (s < 0 || bStamp[s] === bCur) continue; bStamp[s] = bCur; bDist[s] = 0; bQ[qt++] = s; }
    while (qh < qt) {
      const k = bQ[qh++], d = bDist[k];
      if (visit && visit(k, d, false)) return;
      if (d >= maxD) continue;
      for (let i = 0; i < 4; i++) {
        const u = NB[k * 4 + i]; if (u < 0 || bStamp[u] === bCur) continue;
        bStamp[u] = bCur; bDist[u] = d + 1;
        if (!pass(u)) { if (visit && visit(u, d + 1, true)) return; continue; }
        bQ[qt++] = u;
      }
    }
  }
  // collect.js exposure(): cornered = every free single step of our long dragon X inside a shorter (<= 4) enemy head's sprint reach
  function cornered(c, X) {
    const LX = X.body.length, hx = K(X.body[0]), thr = [];
    for (const Y of c.drag.values()) { if (Y.team === X.team) continue; const LY = Y.body.length; if (LY > 4 || LY >= LX) continue; if (tdk(K(Y.body[0]), hx) <= 5) thr.push(Y); }
    if (!thr.length) return null;
    const singles = []; for (let i = 0; i < 4; i++) { const u = NB[hx * 4 + i]; if (u >= 0 && !c.occ.has(u)) singles.push(u); }
    const margin = new Map(singles.map(u => [u, 99]));
    for (const Y of thr) { const reach = Y.body.length - 1; bfs([K(Y.body[0])], 5, u => !c.occ.has(u), (u, dd, blocked) => { if (!blocked && margin.has(u)) margin.set(u, Math.min(margin.get(u), dd - reach)); return false; }); }
    const thrd = singles.filter(u => margin.get(u) <= 0).length;
    if (!(singles.length > 0 && thrd === singles.length)) return null;
    const tail = K(X.body[LX - 1]); let tailE = 99;
    for (const Y of c.drag.values()) if (Y.team !== X.team) tailE = Math.min(tailE, tdk(K(Y.body[0]), tail));
    return { tailE };
  }
  const lastAct = new Map();   // any dragon id -> its last action (the killer's move of a ram is recorded before the death event)
  const ourAct = new Map();    // our dragon id -> its last action with the decision-moment view (near enemies, occupied tiles)
  const cornNow = new Map();   // our dragon id -> cornered info of this turn
  const labelAt = new Map();   // our dragon id -> { r, text } of its last label
  const gxEp = new Map();      // our dragon id -> gx episode
  // ---- stack5 (research/experiments/cand-stack5.md; territory study research/observations/top-territory.md): fountains of the
  //   game's pearl layout (mean gap <= 12 in its layout file, exp/territory-analysis/extract.js), every natural spawn from r0 and
  //   its eater (1 us, 2 them, 0 none), the r100 snapshot (our units, own-territory Voronoi share by capacity, own fountains with
  //   our head within 3 steps; heads' static path distances, bodies ignored), and F episodes (one per dragon and chosen fountain)
  const T5 = { fnt: null, wgt: null, terr: null, sp: [], known: new Map(), r: -1, snap: null, fEp: new Map(), cb: new Map() };
  const t5Init = c => {
    const W5 = c.W, H5 = c.H, N5 = W5 * H5; T5.terr = c.terr; T5.fnt = new Uint8Array(N5); T5.wgt = new Float64Array(N5);
    try {
      const X5 = require(path.join(ROOT, 'exp', 'territory-analysis', 'extract.js'));
      const tag = task.map === 'Prisoners Dilemma' ? (nInit === 10 ? '10' : 'a') : (task.layout || X5.variantOf(task.map, task.gameId, R, nInit).tag);
      const f = X5.fileOf(task.map, tag), gg = f && fs.existsSync(f) ? X5.gapsOfFile(f) : null;
      if (gg && gg.w === W5 && gg.h === H5) for (let k = 0; k < N5; k++) { const q = gg.g[k]; if (q && q[1] > 0) { const m = (q[0] + q[1]) / 2; T5.wgt[k] = 1 / Math.max(1, m); if (m <= 12) T5.fnt[k] = 1; } }
      else T5.err = 'no layout file';
      T5.layout = tag;
    } catch (err) { T5.err = String(err).slice(0, 80); }
    const it = R.match.map.initialTiles; if (it) for (let i = 0; i < it.length; i++) if (it[i] === 2) T5.known.set(i, null); // start pearls: not spawns
  };
  const t5Round = (r, c) => {
    if (!T5.terr) t5Init(c);
    for (const [k, o] of c.pearls) { if (o !== -1 || T5.known.has(k)) continue; const q = { k, r, e: 0 }; T5.sp.push(q); T5.known.set(k, q); }
    if (r === 100 && !T5.snap) {
      const N5 = c.W * c.H, hs = [[], []];
      for (const o of c.drag.values()) hs[o.team === us ? 0 : 1].push(K(o.body[0]));
      const distOf = src => { const D = new Int32Array(N5).fill(-1), q = []; for (const x of src) if (D[x] < 0) { D[x] = 0; q.push(x); }
        for (let i = 0; i < q.length; i++) { const k = q[i]; for (let j = 0; j < 4; j++) { const u = NB[k * 4 + j]; if (u < 0 || D[u] >= 0) continue; D[u] = D[k] + 1; q.push(u); } } return D; };
      const dO = distOf(hs[0]), dE = distOf(hs[1]);
      let vn = 0, vd = 0, fh = 0, ft = 0;
      for (let k = 0; k < N5; k++) {
        if (T5.terr[k] !== ourTerr) continue;
        const a = dO[k] < 0 ? 1e9 : dO[k], b = dE[k] < 0 ? 1e9 : dE[k], w = T5.wgt[k];
        if (w > 0) { vd += w; vn += w * (a < b ? 1 : a === b ? 0.5 : 0); }
        if (T5.fnt[k]) { ft++; if (a <= 3) fh++; }
      }
      T5.snap = { u: hs[0].length, vr: vd > 0 ? vn / vd : null, fr: ft > 0 ? fh / ft : null };
    }
  };
  const t5F = (d, fg, r, c, base) => {
    const a = fg.y * c.W + fg.x, k5 = d.id + ':' + a;
    let ep = T5.fEp.get(k5);
    if (!ep) {
      const others = new Set(); for (const o of c.drag.values()) if (o.team === us && o.id !== d.id) others.add(K(o.body[0]));
      let guarded = 0; bfs([a], 3, () => true, u => { if (others.has(u)) { guarded = 1; return true; } return false; });
      ep = { k: 'fguard', ...base, a, ax: fg.x, ay: fg.y, d0: fg.d, turns: 0, rArr: null, guarded0: guarded, fnt: T5.fnt ? T5.fnt[a] : 0, own: T5.terr && T5.terr[a] === ourTerr ? 1 : 0, r1: r };
      T5.fEp.set(k5, ep);
    }
    ep.turns++; ep.r1 = r;
    if (ep.rArr === null) { const h = K(d.body[0]); let hit = false; bfs([h], 3, () => true, u => { if (u === a) { hit = true; return true; } return false; }); if (hit) ep.rArr = r; }
  };
  const snaps = new Map(); let snapR = -1; // round -> our dragon id -> length at the round's first turn (collect.js snapshot, for famLenAt)
  // ---- stack7 (research/experiments/cand-stack7.md; elimination study exp/eliminations): our and the opponent's units, our total and
  //   longest length at the first turn of every round, our deaths of length >= 8 as exp/eliminations/lib.js rows (classOf), our last
  //   death round and the opponent's final units
  const S7 = { r: -1, u: [], eu: [], t: [], k: [], kd: [], lastDeath: -1, d8: 0, euEnd: 0 };
  // ---- stack8 (research/experiments/cand-stack8.md): every sonar ping by sender and round (px2's designed situation; the probe of
  //   every portal crossing is the crossing dragon's ping of the previous round from the tile it crosses from, in that direction),
  //   the pre-move view of the pearl an Fp / cl / ce label names, and F's pull-away turns
  const S8 = { pings: new Map(), pre: new Map(), eps: new Map(), pullPre: new Map(), fT: 0, fCand: 0, fAway: 0 };
  { let rr8 = -1; const W8 = R.match.map.width;
    for (const ev of R.events) { if (ev.type === 'roundStart') rr8 = ev.round; else if (ev.type === 'sonarPing' && ev.origin) { const k8 = ev.senderId + ':' + rr8; let a8 = S8.pings.get(k8); if (!a8) S8.pings.set(k8, a8 = []); a8.push([ev.origin.y * W8 + ev.origin.x, ev.direction, ev.hitKind || 'none']); } } }
  const bfs8 = (src, maxD) => { const D = new Map([[src, 0]]), q = [src]; for (let i = 0; i < q.length; i++) { const k = q[i], dd = D.get(k); if (dd >= maxD) continue; for (let j = 0; j < 4; j++) { const u = NB[k * 4 + j]; if (u < 0 || D.has(u)) continue; D.set(u, dd + 1); q.push(u); } } return D; };

  const hooks = {
    turn(d, r, c) {
      if (!NB) initGeo(c);                                                                     // stack4
      if (r !== T5.r) { T5.r = r; t5Round(r, c); }                                            // stack5
      if (r !== snapR) { snapR = r; const m4 = new Map(); for (const o of c.drag.values()) if (o.team === us) m4.set(o.id, o.body.length); snaps.set(r, m4); }
      if (r !== S7.r) { S7.r = r; let u7 = 0, e7 = 0, t7 = 0, k7 = 0; for (const o of c.drag.values()) { if (o.team === us) { u7++; t7 += o.body.length; if (o.body.length > k7) k7 = o.body.length; } else e7++; }
        S7.u[r] = u7; S7.eu[r] = e7; S7.t[r] = t7; S7.k[r] = k7; }                                  // stack7
      if (r >= 400 && !seen400) { seen400 = true; if (r === 400) { hyp.g400 = 1; for (const o of c.drag.values()) if (o.team === us) hyp.u400++; } } // H3
      if (d.team !== us) return;
      { const cz = d.body.length >= 6 ? cornered(c, d) : null; if (cz) cornNow.set(d.id, { r, L: d.body.length, tailE: cz.tailE }); else cornNow.delete(d.id); } // stack4
      lifeOf(d.id, d.born, d.parent, d.body.length).lens.push(r, d.body.length);
      health.turns++;
      let eD = 99, eL = 0, eSD = 99, aD = 99, aL = 0, eC = 99;
      for (const o of c.drag.values()) {
        if (o === d) continue;
        const x = c.tdist(o.body[0], d.body[0]);
        if (o.team !== us) { if (x < eD || (x === eD && o.body.length < eL)) { eD = x; eL = o.body.length; } if (o.body.length < d.body.length && x < eSD) eSD = x; eC = Math.min(eC, c.cheb(o.body[0], d.body[0])); }
        else if (x < aD || (x === aD && o.body.length > aL)) { aD = x; aL = o.body.length; }
      }
      const k = c.kingOf(us);
      let b3 = 0;
      if (d.body.length <= 4) for (const o of c.drag.values()) if (o.team !== us && o.body.length >= d.body.length && c.tdist(o.body[0], d.body[0]) === 1) { b3 = 1; break; }
      if (b3) hyp.b3Elig++;
      if (r >= 400 && k === d && d.body.length >= 8) { // stack3 ks2 exposure
        hyp.kingT400++;
        for (const o of c.drag.values()) if (o.team !== us && c.tdist(o.body[0], d.body[0]) <= Math.min(o.body.length - 1, 7)) { hyp.kingExp400++; break; }
      }
      // stack4: path distance (<= 5) from our head to the nearest enemy head over the board: kelp and bodies block, tails do not
      // (they are vacated before a head moves); the tg situation
      let eP = 99;
      if (eD <= 5) {
        const tails = new Set(); for (const o of c.drag.values()) tails.add(K(o.body[o.body.length - 1]));
        bfs([K(d.body[0])], 5, u => !c.occ.has(u) || tails.has(u), (u, dd) => { const o = c.occ.get(u); if (o === undefined) return false; const od = c.drag.get(o); if (od && od.team !== us && K(od.body[0]) === u) { eP = dd; return true; } return false; });
      }
      ctxOf.set(d.id, { eD, eL, eSD, aD, aL, king: k === d ? 1 : 0, kingL: k ? k.body.length : 0, free: d.free, b3, eC, eP });
      { // stack4 (W4 king safety): exposure by path distance. BFS from each enemy head (prefilter: torus Manhattan <= reach) over
        // tiles free now (kelp and bodies block), our head the target; reach = min(true length - 1, cap)
        const hk = K(d.body[0]), l6 = d.body.length >= 6, kg = r >= 400 && k === d && d.body.length >= 8;
        const pathIn = (Y, cap) => {
          const reach = Math.min(Y.body.length - 1, cap); if (reach < 1 || c.tdist(Y.body[0], d.body[0]) > reach) return false;
          let hit = false; bfs([K(Y.body[0])], reach, u => !c.occ.has(u), (u) => { if (u === hk) { hit = true; return true; } return false; }); return hit;
        };
        if (l6) { ext.l6T++; let p4 = 0, m4 = 0; for (const Y of c.drag.values()) { if (Y.team === us) continue; if (!m4 && c.tdist(Y.body[0], d.body[0]) <= Math.min(Y.body.length - 1, 4)) m4 = 1; if (!p4 && pathIn(Y, 4)) p4 = 1; if (p4 && m4) break; } ext.l6P4 += p4; ext.l6M4 += m4; }
        if (kg) { ext.kT++; let p4 = 0, p7 = 0; for (const Y of c.drag.values()) { if (Y.team === us) continue; if (!p7 && pathIn(Y, 7)) p7 = 1; if (!p4 && pathIn(Y, 4)) p4 = 1; if (p4 && p7) break; } ext.kP4 += p4; ext.kP7 += p7; }
      }
    },
    indicator(e, r, c) {
      const d = c.drag.get(e.id);
      if (!d || d.team !== us) return;
      ind.set(e.id, e.text);
      labelAt.set(e.id, { r, text: e.text });                                                  // stack4: the death label
      { const mt = /(?:^|\s)map=(\S+)/.exec(e.text || ''); if (mt) { if (!mapTags.has(e.id)) mapTags.set(e.id, []); mapTags.get(e.id).push({ r, tag: mt[1] }); } } // cand-mapid
      // stack2 S2: the pearl a grab label names, as the board holds it before the move (null: no pearl there any more)
      const g = /(?:^|\s)grab@(\d+),(\d+)(?:\s|$)/.exec(e.text || '');
      if (g) {
        const p = { x: +g[1], y: +g[2] }, k = c.key(p.x, p.y);
        let enemyD = 99; for (const o of c.drag.values()) if (o.team !== us) enemyD = Math.min(enemyD, c.tdist(o.body[0], p));
        grabPre.set(e.id, { k, px: p.x, py: p.y, o: c.pearls.has(k) ? c.pearls.get(k) : null, ourD: c.tdist(d.body[0], p), enemyD });
      }
      if (NB) { // stack8: the named pearl of an Fp / cl / ce label as the board holds it before the move, and who is nearer to it
        const h8 = K(d.body[0]); let Dh8 = null;
        for (const m8 of (e.text || '').matchAll(/(?:^|\s)(Fp|cl|ce)@(\d+),(\d+)(?=\s|$)/g)) {
          if (!Dh8) Dh8 = bfs8(h8, 12);
          const k8 = +m8[3] * c.W + +m8[2], o8 = c.pearls.has(k8) ? c.pearls.get(k8) : null, dm = Dh8.has(k8) ? Dh8.get(k8) : 99;
          let nearerAny = 0, nearerOwn = 0, enemyIn = 0;
          if (dm < 99) { const Dp = bfs8(k8, dm + 1); for (const o of c.drag.values()) { if (o.id === d.id) continue; const x8 = Dp.has(K(o.body[0])) ? Dp.get(K(o.body[0])) : 99; if (x8 < dm) nearerAny = 1; if (o.team === us && x8 <= dm) nearerOwn = 1; if (o.team !== us && x8 <= dm + 1) enemyIn = 1; } }
          let q8 = S8.pre.get(e.id); if (!q8 || q8.r !== r) S8.pre.set(e.id, q8 = { r });
          q8[m8[1]] = { k: k8, px: +m8[2], py: +m8[3], o: o8, dm, nearerAny, nearerOwn, enemyIn };
        }
        const fm8 = /(?:^|\s)F\d+@(\d+),(\d+)(?:\s|$)/.exec(e.text || '');
        if (fm8) { // F's pull-away candidates: natural pearls within 7 of our head, outside 3 of the target, no other head as near
          const a8 = +fm8[2] * c.W + +fm8[1], Dh = bfs8(h8, 7), Dg = bfs8(a8, 3), cand = [];
          for (const [k8, o8] of c.pearls) { if (o8 !== -1 || !Dh.has(k8) || Dg.has(k8)) continue; const dm = Dh.get(k8), Dp = bfs8(k8, dm); let uniq = true;
            for (const o of c.drag.values()) { if (o.id === d.id) continue; if (Dp.has(K(o.body[0]))) { uniq = false; break; } }
            if (uniq) cand.push([k8, dm]); }
          S8.fT++; if (cand.length) { S8.fCand++; S8.pullPre.set(e.id, { r, cand }); }
        }
      }
    },
    action(d, e, r, c, before) {
      // stack4: every dragon's action with its executed tiles (collect.js action hook); a ram's killer acts before the death event
      const a4 = e.action || {}, act4 = { r, lenB: before.length, ate: d.ateThisAct, hB: K(before[0]), hA: K(d.body[0]), tiles: null, nExits: 0 };
      if (a4.kind === 'move') {
        let h = before[0]; const tiles = [], n = d.fate ? d.fate.step : a4.steps.length;
        for (let i = 0; i < n; i++) { const di = DIRS4.indexOf(a4.steps[i]), k = K(h), u = NB[k * 4 + di]; if (u < 0) break; tiles.push(u); if (PORT[k * 4 + di]) act4.nExits++; h = { x: kx(u), y: ky(u) }; }
        act4.tiles = tiles;
      }
      lastAct.set(d.id, act4);
      if (d.team !== us) return;
      if (S8.pullPre.has(d.id)) { // stack8: did this F-tagged move raise our distance to a pull-away candidate it did not eat?
        const q8 = S8.pullPre.get(d.id); S8.pullPre.delete(d.id);
        if (q8.r === r) { const h8 = K(d.body[0]); let away = 0; for (const [k8, dm] of q8.cand) { if (!c.pearls.has(k8)) continue; const D2 = bfs8(k8, dm + 2); if ((D2.has(h8) ? D2.get(h8) : dm + 3) > dm) away = 1; } if (away) S8.fAway++; }
      }
      let pFrom8 = -1, pDir8 = null;                                                            // stack8: the first portal step
      if (d.portalSteps > 0 && a4.kind === 'move') { let h8 = K(before[0]); const n8 = Math.min(a4.steps.length, d.fate ? d.fate.step + 1 : a4.steps.length);
        for (let i = 0; i < n8; i++) { const di = DIRS4.indexOf(a4.steps[i]), u = NB[h8 * 4 + di]; if (u < 0) break; if (PORT[h8 * 4 + di]) { pFrom8 = h8; pDir8 = a4.steps[i]; break; } h8 = u; } }
      if (e.instructions) { const n = e.instructions.count || 0; if (n > health.maxInstr) health.maxInstr = n; if (n > 80e6) health.over80++; if (e.instructions.exceeded) health.exceeded++; }
      const text = ind.get(d.id); ind.delete(d.id);
      if (text) health.labelled++;
      const t = parseInd(text), cx = ctxOf.get(d.id) || {};
      if (t.kind === 'noexit' && /^no-exit s(?:\s|$)/.test(text || '')) T5.spare = (T5.spare || 0) + 1;       // stack5 no-exit spare
      const base = { r, id: d.id, L: before.length, act: d.act, steps: d.steps, ate: d.ateThisAct, cx };
      const made = [];
      { // stack4: the decision-moment view (collect.js): enemy heads within 8 with their segments inside our 7x7 view, and the
        // tiles occupied at this decision within 6 of our head (our own body as it stood included)
        const hB = act4.hB, near = [], occ = new Set(), hx = kx(hB), hy = ky(hB);
        for (const o of c.drag.values()) {
          if (o === d || o.team === us) continue;
          const oh = K(o.body[0]), td = tdk(oh, hB);
          if (td <= 8) { let vis = 0, tailVis = 0; o.body.forEach((sg, i) => { if (chk(K(sg), hB) <= 3) { vis++; if (i === o.body.length - 1) tailVis = 1; } }); near.push([o.id, o.team, o.body.length, oh, td, chk(oh, hB), o.born, vis, tailVis]); }
        }
        for (let dy = -6; dy <= 6; dy++) for (let dx = -6; dx <= 6; dx++) { const k = (((hy + dy) % GH + GH) % GH) * GW + (((hx + dx) % GW + GW) % GW); if (c.occ.has(k) && c.occ.get(k) !== d.id) occ.add(k); }
        for (const sg of before) occ.add(K(sg));
        ourAct.set(d.id, { r, hB, hA: act4.hA, near, occ, text: text || null });
      }
      const cz4 = cornNow.get(d.id), corn4 = cz4 && cz4.r === r ? cz4 : null;                  // stack4: cornered this turn
      if (corn4) { ext.corn.push({ r, id: d.id, L: corn4.L, tailE: corn4.tailE, resp: d.act === 'split' ? 'split' : d.steps >= 3 ? 'sprint3' : d.steps === 2 ? 'sprint2' : 'single' }); cornNow.delete(d.id); }
      switch (t.kind) {
        case 'feed': case 'conv': case 'k2': made.push({ k: t.kind, ...base, target: t.target, dist: t.dist, kc: t.kc || 0 }); break; // cand-conv2 k2, kc
        case 'pocket': made.push({ k: 'pocket', ...base, birthLen: t.birthLen }); break;
        case 'escsplit': made.push({ k: 'escsplit', ...base }); lastEscSplit.set(d.id, r); break;
        case 'escsplit2': made.push({ k: 'escsplit2', ...base, corn: corn4 ? 1 : 0, tailE: corn4 ? corn4.tailE : null }); break; // stack4
        case 'split': made.push({ k: 'split', ...base, units: t.units, e: t.e }); break;
        case 'frag': made.push({ k: 'frag', ...base, units: t.units }); break; // stack2 S1
        case 'csplit': made.push({ k: 'csplit', ...base, units: t.units, target: t.target, view: t.view ? 1 : 0, kingTag: t.king ? 1 : 0 }); break; // stack5
        case 'bsplit': made.push({ k: 'bsplit', ...base, units: t.units }); break; // cand-mapid bsplit
        case 'kcap': case 'floor': { // stack7: the opponent's units now (replay count) and this process's last map tag (the map gate)
          let e7 = 0; for (const o of c.drag.values()) if (o.team !== us) e7++;
          const mt7 = mapTags.get(d.id);
          made.push({ k: t.kind, ...base, units: t.units, eu: e7, mt: mt7 && mt7.length ? mt7[mt7.length - 1].tag : null }); break;
        }
        case 'lasttrade': health.lasttrade++; made.push({ k: 'lasttrade', ...base }); break;
        case 'noexit': health.noexit++; made.push({ k: 'noexit', ...base, stub: lastEscSplit.has(d.id) && lastEscSplit.get(d.id) >= r - 3 ? 1 : 0 }); break;
        case 'degraded': health.degraded++; break;
        case 'other': counts.other[t.word] = (counts.other[t.word] || 0) + 1; made.push({ k: 'other:' + t.word, ...base }); break;
        case 'move': {
          health.moveTurns++; if (t.depth < 5) health.lowDepth++;
          if (t.goal) { counts[t.goal]++; let gz = gather.get(d.id); if (!gz) gather.set(d.id, gz = { id: d.id, r0: r, d0: t.goalDist, dMin: t.goalDist, r1: r, L0: before.length }); gz.dMin = Math.min(gz.dMin, t.goalDist); gz.r1 = r; }
          if (t.late) counts.late++;
          if (t.trust) { counts.T++; lastTrust.set(d.id, r); }
          if (t.ks) counts.ks++;
          if (t.ks2) counts.ks2++;
          if (t.tg) made.push({ k: 'tg', ...base, tgx: t.tg === 'tgx' ? 1 : 0 });                  // stack4 tg
          if (t.px) made.push({ k: 'px', ...base, pxx: t.px === 'pxx' ? 1 : 0 });                  // stack4 px
          if (t.gx) { ext.gxN++; let q = gxEp.get(d.id); if (!q) gxEp.set(d.id, q = { r0: r, r1: r, turns: 0, L0: before.length, cx }); q.turns++; q.r1 = r; } // stack4 gx
          if (t.fg) t5F(d, t.fg, r, c, base);                                                     // stack5 F
          if (t.fg) { const ep8 = T5.fEp.get(d.id + ':' + (t.fg.y * c.W + t.fg.x)); if (ep8) { if (ep8.turns === 1) ep8.f2 = t.f2 ? 1 : 0; if (t.fp) ep8.fpT = (ep8.fpT || 0) + 1; } } // stack8 F2
          if (t.px2) made.push({ k: 'px2', ...base, px2x: t.px2 === 'px2x' ? 1 : 0, hB: act4.hB });                            // stack8 px2
          for (const w8 of ['fp', 'cl', 'ce']) { // stack8: one record per dragon and named pearl (tile + origin), with the first label's view
            if (!t[w8]) continue;
            const q8 = S8.pre.get(d.id), v8 = q8 && q8.r === r ? q8[w8 === 'fp' ? 'Fp' : w8] : null; if (!v8) continue;
            const key8 = w8 + ':' + d.id + ':' + v8.k + ':' + v8.o; let ep8 = S8.eps.get(key8);
            if (!ep8) { ep8 = { k: w8, ...base, tile: v8.k, px: v8.px, py: v8.py, o: v8.o, dm: v8.dm, nearerAny: v8.nearerAny, nearerOwn: v8.nearerOwn, enemyIn: v8.enemyIn, turns: 0 }; S8.eps.set(key8, ep8); recs.push(ep8); }
            ep8.turns++;
          }
          if (t.cov) made.push({ k: 'cov', ...base });                                              // stack5 cov
          if (t.kch) { let q = c2Hold.get(d.id); if (!q) c2Hold.set(d.id, q = { r0: r, r1: r, turns: 0, L0: before.length, cx }); q.turns++; q.r1 = r; } // cand-conv2
          if (t.k2g) { let q = c2Pull.get(d.id); if (!q) c2Pull.set(d.id, q = { r0: r, r1: r, turns: 0, L0: before.length, cx }); q.turns++; q.r1 = r; } // cand-conv2
          if (t.sx) ext.sxN++;                                                                     // stack4 sx
          for (const x of t.extra) { counts.extra[x] = (counts.extra[x] || 0) + 1; made.push({ k: 'tag:' + x, ...base }); }
          if (t.esc) made.push({ k: 'esc', ...base });
          else if (t.trade) made.push({ k: 'trade', ...base, path: t.dirs.length, ram4: t.ram4, coll: t.coll });
          else if (t.dirs.length >= 2) made.push({ k: d.ateThisAct > 0 ? 'sprint' : cx.eD <= 4 ? 'sprintEsc' : 'sprintOther', ...base });
          if (t.grab && grabPre.has(d.id)) { // stack2 S2: one episode per targeted pearl (tile + the death that dropped it)
            const pre = grabPre.get(d.id), pk = pre.k + ':' + pre.o;
            let ep = grabEp.get(pk);
            if (!ep) { ep = { k: 'grab', ...base, tile: pre.k, px: pre.px, py: pre.py, o: pre.o, ourD: pre.ourD, enemyD: pre.enemyD, turns: 0, ids: new Set() }; grabEp.set(pk, ep); recs.push(ep); }
            ep.turns++; ep.ids.add(d.id);
          }
          break;
        }
      }
      grabPre.delete(d.id);
      if (d.portalSteps > 0) made.push({ k: 'portal', ...base, blind: t.kind === 'move' && t.blind ? 1 : 0,
        onStep: d.portalSteps > act4.nExits ? 1 : 0, v: t.kind === 'move' ? t.v : null, feedLbl: /^feed/.test(text || '') ? 1 : 0, // stack4: the fatal step crossed a portal
        pFrom: pFrom8, pDir: pDir8 });                                                                   // stack8: the probe's tile and direction
      pending.set(d.id, made);
      for (const x of made) recs.push(x);
    },
    eat(d, tile, o, r, c) {
      if (o < 0 && T5.known.has(tile)) { const q = T5.known.get(tile); if (q) q.e = d.team === us ? 1 : 2; T5.known.delete(tile); } // stack5
      if (d.team === us && o < 0) { const L5 = life.get(d.id); if (L5) { L5.nat.push(r); if (c.terr[tile] === ourTerr) L5.natOwn.push(r); } }
      if (o >= 0) { let a = deathEat.get(o); if (!a) deathEat.set(o, a = []); a.push([d.id, d.team, r]); }
      if (d.team === us) { const L = life.get(d.id); if (L) L.eats.push(r); }
      else if (o < 0 && c.terr[tile] === ourTerr) hyp.natOwnThem++;                            // H2
      if (d.team === us && o < 0 && c.terr[tile] === ourTerr) hyp.natOwnUs++;
      const ek = tile + ':' + o; let a = eatenBy.get(ek); if (!a) eatenBy.set(ek, a = []); a.push({ team: d.team, r, id: d.id }); // S2
    },
    split(p, ch, e, r) {
      if (p.team !== us) return;
      if (GW) T5.cb.set(ch.id, K(ch.body[0]));                                                  // stack5: the child's birth tile
      if (r >= 350 && r < 450) hyp.split350++;                                                  // H3
      lifeOf(ch.id, r, p.id, ch.body.length);
      const m = pending.get(p.id);
      if (m) for (const x of m) if (x.r === r) { x.child = ch.id; x.childLen = ch.body.length; }
    },
    death(d, rec, idx, other, r, c) {
      if (d.team !== us) return;
      if (rec.cause === 1 || rec.cause === 2 || rec.cause === 5) { const q = rec.cause === 1 ? 'dTrap' : rec.cause === 2 ? 'dRam' : 'dAlly'; T5[q] = (T5[q] || 0) + 1; if (r < 250) T5[q + '250'] = (T5[q + '250'] || 0) + 1; } // stack5 side effects
      const pair = rec.pair >= 0 ? c.deaths[rec.pair] : null;
      const dz = { r, cause: rec.cause, idx, len: rec.len, drops: rec.drops, otherLen: other ? other.body.length : 0, otherTeam: other ? other.team : null, pairIdx: rec.pair >= 0 ? rec.pair : -1, pairLen: pair ? pair.len : 0 };
      const L = lifeOf(d.id, d.born, d.parent, d.body.length); L.death = dz;
      if (rec.cause === 6) health.fault++;
      const cz = ctxOf.get(d.id);
      if (rec.cause === 3 && cz && cz.b3) hyp.b3Ram++;
      if (rec.cause === 0 && r >= 250) { hyp.sac250N++; hyp.sac250Len += rec.len; hyp.sac250Drops += rec.drops; sacIdx.push(idx); }
      if (rec.king && r >= 450) { hyp.king450N++; hyp.king450Len += rec.len; }
      if (rec.king && r >= 400 && rec.cause === 2) { hyp.kingRam400N++; hyp.kingRam400Len += rec.len; }
      if (rec.cause === 2 && lastTrust.has(d.id) && lastTrust.get(d.id) >= r - 1) counts.trustRammed++;
      { const lb = labelAt.get(d.id); dz.text = lb && lb.r === r ? lb.text : null; }             // stack4: the label of the death round
      if (rec.cause === 2 && other && rec.len >= 6) {
        // stack4 (collect.js rams): our long dragon rammed. Our last decision is this round if we move before the killer (lower
        // id), else the previous round; the killer's move of this round is already recorded
        const ka0 = lastAct.get(other.id), ka = ka0 && ka0.r === r ? ka0 : {};
        const ourR = d.id < other.id ? r : r - 1, oa0 = ourAct.get(d.id), oa = oa0 && oa0.r === ourR ? oa0 : {};
        const q = (oa.near || []).find(y => y[0] === other.id);
        const x = { r, id: d.id, L: rec.len, len: rec.len, king: rec.king, killerId: other.id, killerLen: other.body.length, killerSteps: other.steps || 0,
          killerAte: ka.ate, killerLenB: ka.lenB, killerBorn: other.born, text: oa.text !== undefined ? oa.text : null, hasDecision: oa.hB !== undefined ? 1 : 0,
          atDecision: q ? { td: q[4], cheb: q[5], vis: q[7], tailVis: q[8], len: q[2] } : null, pathThroughOcc: 0, newHeadWasOcc: 0 };
        if (oa.occ && ka.tiles) { x.pathThroughOcc = ka.tiles.filter(u => oa.occ.has(u)).length; x.newHeadWasOcc = oa.hA !== undefined && oa.occ.has(oa.hA) ? 1 : 0; }
        ext.rams.push(x);
      }
      const m = pending.get(d.id);
      if (m) for (const x of m) if (x.r === r) x.died = dz;
      S7.lastDeath = r; if (rec.len >= 8) { S7.d8++; S7.kd.push([r, rec.len, rec.cause, 0, 0, 0, rec.king ? 1 : 0, 0, 0, 0, 0, rec.blk]); } // stack7 (lib.js row layout)
    },
    end(n, c) {
      rounds = n;
      for (const d of c.drag.values()) if (d.team === us) fin.set(d.id, d.body.length);
      for (const d of c.drag.values()) if (d.team !== us) S7.euEnd++;                              // stack7
      const k = c.kingOf(us); finKing = k ? k.id : -1;
      deathsAll = c.deaths;
      for (const [tk, o] of c.pearls) if (o < 0 && c.terr[tk] === ourTerr) hyp.natOwnLeft++;      // H2
      for (const x of c.deaths) {                                                                 // H5
        if (x.team !== us) hyp.eDropUs += x.eatEnemy;
        if (x.cause !== 3 || x.pair < 0) continue;
        const v = c.deaths[x.pair];                          // x moved into v's head: one of the two is ours
        if (x.team !== us && v.team !== us) continue;
        const mine = y => y.team === us ? y.eatOwn : y.eatEnemy, theirs = y => y.team === us ? y.eatEnemy : y.eatOwn;
        const pu = mine(x) + mine(v), pt = theirs(x) + theirs(v);
        hyp.xchN++; hyp.xchUs += pu; hyp.xchThem += pt;
        if (v.team === us) { hyp.xchRN++; hyp.xchRUs += pu; hyp.xchRThem += pt; }
      }
    },
  };
  const g = perGame(R, info, hooks);

  // ---- cand-conv2: the final king's line (by rounds: member i owns [its birth, the birth of member i+1)), and our lengths per round
  const c2 = (() => {
    const win = new Map(), line = [];
    for (let q = finKing; q !== undefined && q !== -1 && life.has(q); q = life.get(q).parent) line.push(q);
    line.reverse();
    for (let i = 0; i < line.length; i++) win.set(line[i], [life.get(line[i]).born, i + 1 < line.length ? life.get(line[i + 1]).born : Infinity]);
    const inLine = (id, r) => { const w = win.get(id); return w ? r >= w[0] && r < w[1] : false; };
    const rank1 = (id, r) => { const m = snaps.get(r); if (!m || !m.has(id)) return null; const L = m.get(id); for (const [o, l] of m) if (o !== id && (l > L || (l === L && o < id))) return 0; return 1; };
    return { win, line, inLine, rank1 };
  })();

  // ---- effects
  const INF = 1e9;
  const deathR = id => { const L = life.get(id); return L && L.death ? L.death.r : INF; };
  const alive = (id, t) => deathR(id) > t;
  const lenAt = (id, t) => {
    const L = life.get(id); if (!L || !alive(id, t)) return 0;
    if (t >= rounds - 1 && fin.has(id)) return fin.get(id);
    let v = 0; for (let i = 0; i < L.lens.length; i += 2) { if (L.lens[i] > t) break; v = L.lens[i + 1]; }
    return v || (L.born <= t ? L.bornLen : 0);
  };
  const kids = new Map(); for (const [id, L] of life) if (L.parent !== undefined && L.parent >= 0) { if (!kids.has(L.parent)) kids.set(L.parent, []); kids.get(L.parent).push(id); }
  // family = the dragon and every descendant born by round t (the corridor loop keeps a body alive through generations)
  const familyLen = (root, t) => { let s = 0; const st = [root]; while (st.length) { const id = st.pop(); const L = life.get(id); if (!L || L.born > t) continue; s += lenAt(id, t); for (const c of kids.get(id) || []) st.push(c); } return s; };
  const body = (id, t) => familyLen(id, Math.min(t, rounds - 1)) > 0 ? 1 : 0; // the dragon or a descendant is alive
  // stack4: body length at round t as collect.js famLenAt (the study's 1.4 "mass kept"): lengths at the round's first turn, final
  // lengths from the end on; members born after t (and their descendants) do not count
  const famLenAt = (root, t) => {
    const end = t >= rounds, m = end ? null : snaps.get(t); let v = 0; const st = [root];
    while (st.length) { const id = st.pop(); const Lf = life.get(id); if (!Lf || (!end && Lf.born > t)) continue; v += end ? (fin.get(id) || 0) : (m && m.get(id)) || 0; for (const q of kids.get(id) || []) st.push(q); }
    return v;
  };
  const eatsIn = (id, a, b) => { const L = life.get(id); return L ? L.eats.filter(r => r > a && r <= b).length : 0; };
  const eaters = idx => deathEat.get(idx) || [];
  // stack2 S1: dragons that later died feeding an ally (an executed feed or conv label)
  const fedBy = new Map(); for (const x of recs) if ((x.k === 'feed' || x.k === 'conv') && x.died) fedBy.set(x.id, { k: x.k, r: x.r });
  for (const x of recs) {
    x.map = mapKey; x.opp = task.opp; x.game = task.gameId || task.key; x.ph = phaseOf(x.r);
    switch (x.k) {
      case 'frag': { // stack2 S1
        x.ex = x.child !== undefined ? 1 : 0;
        x.sit = x.cx.king === 0 && x.cx.eC > 3 ? 1 : 0; // not the team's longest; no enemy head within its 7x7 view
        if (x.ex) {
          const CL = life.get(x.child); x.childId = x.child;
          x.childAlive30 = alive(x.child, x.r + 30) ? 1 : 0; x.eat30 = eatsIn(x.child, x.r, x.r + 30); x.eatLife = CL.eats.length;
          const f = fedBy.get(x.child); x.fed = f ? f.k : null; x.fedAge = f ? f.r - x.r : null;
          x.aliveEnd = alive(x.child, INF - 1) ? 1 : 0;
          x.childDeath = CL.death && CL.death.r <= x.r + 30 ? { r: CL.death.r, cause: CL.death.cause, otherLen: CL.death.otherLen } : null;
        }
        x.ok = x.ex && ((x.childAlive30 && x.eat30 >= 1) || x.fed) ? 1 : 0; // the piece paid its way: fed itself, or fed an ally
        break;
      }
      case 'bsplit': { // cand-mapid: early split on Schooltime b. Situation: the game really is Schooltime b (truth, not the tag)
        x.ex = x.child !== undefined ? 1 : 0;
        x.sit = task.map === 'Schooltime' && truthLay() === 'b' ? 1 : 0;
        if (x.ex) {
          const CL = life.get(x.child); x.childId = x.child;
          x.childAlive10 = alive(x.child, x.r + 10) ? 1 : 0; x.eat10 = eatsIn(x.child, x.r, x.r + 10);
          x.childAlive30 = alive(x.child, x.r + 30) ? 1 : 0; x.eat30 = eatsIn(x.child, x.r, x.r + 30); x.eatLife = CL.eats.length;
          const f = fedBy.get(x.child); x.fed = f ? f.k : null; x.fedAge = f ? f.r - x.r : null;
          x.parentAlive10 = alive(x.id, x.r + 10) ? 1 : 0; x.parentAlive30 = alive(x.id, x.r + 30) ? 1 : 0;
          x.childDeath = CL.death && CL.death.r <= x.r + 30 ? { r: CL.death.r, cause: CL.death.cause, otherLen: CL.death.otherLen } : null;
          x.fam30 = familyLen(x.id, Math.min(x.r + 30, rounds - 1)) - x.L;   // the parent's family (the child included) 30 rounds on
        }
        x.ok = x.ex && x.childAlive10 ? 1 : 0; // the new unit exists 10 rounds later (elite b 2-children: 92%, exp/mapid/child_ab.js)
        break;
      }
      case 'csplit': { // stack5: the study's two gates on the child (pass2.js: born, alive 30 rounds on or at the end, natural eats)
        x.ex = x.child !== undefined ? 1 : 0;
        x.sit = x.cx.king === 1 && x.L >= 8 ? 0 : 1;                  // the king (our longest, >= 8) keeps its length
        if (x.ex) {
          const CL = life.get(x.child); x.childId = x.child;
          x.childAlive30 = alive(x.child, x.r + 30) ? 1 : 0;
          x.nat30 = CL.nat.filter(q => q >= x.r && q <= x.r + 30).length;
          const bt = T5.cb.get(x.child); x.bornOwn = bt !== undefined && T5.terr && T5.terr[bt] === ourTerr ? 1 : 0;
          x.childDeath = CL.death && CL.death.r <= x.r + 30 ? { r: CL.death.r, cause: CL.death.cause, otherLen: CL.death.otherLen } : null;
        }
        x.ok = x.ex && x.nat30 >= 1 ? 1 : 0;
        break;
      }
      case 'floor': case 'kcap': { // stack7 (cand-stack7.md): the new unit and its parent 10 / 30 rounds on (alive at the end counts)
        x.ex = x.child !== undefined ? 1 : 0;
        x.sit = x.k === 'floor' ? (x.eu >= 8 ? 1 : 0) : (x.cx.king === 1 && x.r < 250 ? 1 : 0); // floor: outnumbered; kcap: the king
        x.view = x.cx.eC <= 3 ? 1 : 0;                                                                // an enemy head in the 7x7 view
        if (x.ex) {
          const CL = life.get(x.child); x.childId = x.child;
          x.childAlive10 = alive(x.child, x.r + 10) ? 1 : 0; x.childAlive30 = alive(x.child, x.r + 30) ? 1 : 0;
          x.parentAlive10 = alive(x.id, x.r + 10) ? 1 : 0; x.parentAlive30 = alive(x.id, x.r + 30) ? 1 : 0;
          x.eat30 = eatsIn(x.child, x.r, x.r + 30); x.nat30 = CL.nat.filter(q => q >= x.r && q <= x.r + 30).length;
          x.childDeath = CL.death && CL.death.r <= x.r + 30 ? { r: CL.death.r, cause: CL.death.cause, otherLen: CL.death.otherLen } : null;
          x.fam30 = familyLen(x.id, Math.min(x.r + 30, rounds - 1)) - x.L;
        }
        x.ok = x.ex && (x.k === 'floor' ? x.childAlive30 : x.childAlive10) ? 1 : 0;
        break;
      }
      case 'cov': { // stack5: a natural pearl of our territory eaten within 20 rounds
        x.ex = 1; const Lc = life.get(x.id); x.ok = Lc && Lc.natOwn.some(q => q > x.r && q <= x.r + 20) ? 1 : 0;
        break;
      }
      case 'grab': { // stack2 S2: one record per targeted pearl
        x.drop = x.o !== null && x.o >= 0 ? 1 : 0; x.gone = x.o === null ? 1 : 0; x.natural = x.o === -1 ? 1 : 0;
        if (x.drop) { const dz = deathsAll[x.o]; x.dropAge = x.r - dz.r; x.dropOurs = dz.team === us ? 1 : 0; x.headon = dz.cause === 2 || dz.cause === 3 ? 1 : 0; }
        const E = (eatenBy.get(x.tile + ':' + x.o) || []).find(q => q.r >= x.r);
        x.side = E ? (E.team === us ? 'us' : 'them') : 'none'; x.delay = E ? E.r - x.r : null;
        x.byTargeter = E && x.ids.has(E.id) ? 1 : 0; x.nIds = x.ids.size; delete x.ids;
        x.contested = x.enemyD <= x.ourD ? 1 : 0; // an enemy head at least as close as ours when we first went for it
        x.ex = x.drop; x.ok = x.drop ? (x.side === 'us' ? 1 : 0) : null;
        break;
      }
      case 'feed': case 'conv': case 'k2': { // cand-conv2: k2 is measured as feed; eatLine / tOnLine added for every one
        x.ex = x.died ? 1 : 0;
        if (x.died) x.eatLine = eaters(x.died.idx).filter(q => q[1] === us && c2.inLine(q[0], q[2])).length;
        x.tOnLine = c2.inLine(x.target, x.r) ? 1 : 0; x.tRank1 = c2.rank1(x.target, x.r);
        if (x.died) {
          const E = eaters(x.died.idx);
          x.drops = x.died.drops; x.eatT = E.filter(q => q[0] === x.target).length; x.eatOwn = E.filter(q => q[1] === us).length; x.eatEnemy = E.filter(q => q[1] !== us).length;
          const own = E.filter(q => q[1] === us).map(q => q[2] - x.r); x.delay = own.length ? own.reduce((a, b) => a + b, 0) / own.length : null;
        }
        x.tLen = lenAt(x.target, x.r); x.tAliveEnd = alive(x.target, INF - 1) ? 1 : 0; x.tFinalKing = x.target === finKing ? 1 : 0;
        x.tBodyEnd = familyLen(x.target, rounds - 1) > 0 ? 1 : 0; // the target or a descendant (corridor-loop generations) lives at the end
        { let fk = false; for (let q = finKing; q !== undefined && q !== -1 && life.has(q); q = life.get(q).parent) if (q === x.target) { fk = true; break; } x.tKingLine = fk ? 1 : 0; } // the final king descends from the target
        const td = life.get(x.target); x.tDeath = td && td.death ? { r: td.death.r, cause: td.death.cause } : null;
        x.ok = x.ex && x.eatOwn * 2 >= x.drops && x.eatEnemy === 0 ? 1 : 0;
        if (x.k === 'k2') { x.sit = x.tRank1; x.ok = x.ex && x.eatLine * 2 >= x.drops ? 1 : 0; } // cand-conv2 k2: half to the final king's line
        break;
      }
      case 'pocket': {
        x.ex = x.ate > 0 && !x.died ? 1 : 0;
        let ch = null; for (const [id, L] of life) if (L.parent === x.id && L.born > x.r && L.born <= x.r + 2) ch = id;
        x.splitNext = ch !== null ? 1 : 0; x.childLen = ch !== null ? life.get(ch).bornLen : 0; x.childAlive20 = ch !== null && alive(ch, life.get(ch).born + 20) ? 1 : 0;
        x.fam30 = familyLen(x.id, Math.min(x.r + 30, rounds - 1)) - x.L;
        x.ok = x.ex && x.splitNext && x.fam30 >= 0 ? 1 : 0; // the loop keeps its length
        break;
      }
      case 'escsplit': case 'escsplit2': case 'split': {
        x.ex = x.child !== undefined ? 1 : 0;
        if (x.ex) {
          x.childAlive10 = alive(x.child, x.r + 10) ? 1 : 0; x.childAlive30 = alive(x.child, x.r + 30) ? 1 : 0;
          x.parentAlive5 = alive(x.id, x.r + 5) ? 1 : 0;
          x.famAlive10 = familyLen(x.id, Math.min(x.r + 10, rounds - 1)) > 0 ? 1 : 0;
          x.fam30 = familyLen(x.id, Math.min(x.r + 30, rounds - 1)) - x.L;
          x.fk10 = famLenAt(x.id, x.r + 10); x.fk30 = famLenAt(x.id, x.r + 30);                  // stack4: body length +10/+30 (study 1.4)
          const cd = life.get(x.child).death; x.childDeath = cd && cd.r <= x.r + 30 ? { r: cd.r, cause: cd.cause, otherLen: cd.otherLen } : null;
        }
        x.ok = x.ex && (x.k === 'escsplit' || x.k === 'escsplit2' ? x.famAlive10 : x.childAlive30) ? 1 : 0; // escape split: the body lives on
        break;
      }
      case 'tg': { // stack4: after a turn where the new threat model saw a gap, is our dragon rammed within 2 rounds?
        x.ex = 1; x.sit = x.cx.eP <= 5 ? 1 : 0;
        const dz = life.get(x.id).death; x.rammed2 = dz && dz.cause === 2 && dz.r <= x.r + 2 ? 1 : 0;
        x.death2 = x.rammed2 ? { r: dz.r, cause: dz.cause, otherLen: dz.otherLen } : null;
        x.ok = x.rammed2 ? 0 : 1;
        break;
      }
      case 'px2': { // stack8: this dragon's previous-round ping from its head tile stopped on a dragon of ours; the body 3 rounds on
        const p8 = (S8.pings.get(x.id + ':' + (x.r - 1)) || []).filter(q => q[0] === x.hB);
        x.ex = 1; x.sit = p8.some(q => q[2] === 'ally' || q[2] === 'allyHead') ? 1 : 0; x.alive3 = body(x.id, x.r + 3); x.ok = x.px2x ? 0 : 1;
        break;
      }
      case 'fp': case 'cl': case 'ce': { // stack8: the named pearl's first eater after the label
        const E8 = (eatenBy.get(x.tile + ':' + x.o) || []).filter(q => q.r >= x.r).sort((a, b) => a.r - b.r)[0] || null;
        x.ex = 1; x.present = x.o !== null ? 1 : 0;
        x.eatSelf = E8 && E8.id === x.id ? 1 : 0; x.eatSelf10 = x.eatSelf && E8.r <= x.r + 10 ? 1 : 0;
        x.eatUs = E8 && E8.team === us ? 1 : 0; x.eatThem = E8 && E8.team !== us ? 1 : 0;
        x.eatLonger = E8 && E8.team === us && E8.id !== x.id && lenAt(E8.id, E8.r) > x.L ? 1 : 0;
        { const dz8 = life.get(x.id) && life.get(x.id).death; x.rammed5 = dz8 && dz8.cause === 2 && dz8.r <= x.r + 5 ? 1 : 0; }
        if (x.k === 'fp') { x.sit = x.present && !x.nearerAny ? 1 : 0; x.ok = x.present ? x.eatSelf10 : null; }
        else if (x.k === 'cl') { x.sit = x.o === -1 && !x.nearerOwn ? 1 : 0; x.ok = x.present ? x.eatSelf : null; }
        else { x.sit = x.enemyIn; x.ok = x.present ? (x.eatThem ? 0 : 1) : null; }
        break;
      }
      case 'px': { // stack4: a portal crossing next to an own-crowded exit was penalised this turn; no death against our own dragon
        x.ex = 1; x.ownDeath = x.died && x.died.otherTeam === us ? 1 : 0; x.alive3 = body(x.id, x.r + 3);
        x.death0 = x.died ? { r: x.died.r, cause: x.died.cause, otherLen: x.died.otherLen } : null;
        x.ok = x.ownDeath ? 0 : 1;
        break;
      }
      case 'esc': {
        x.ex = x.steps >= 2 && !x.died ? 1 : 0; x.sit = x.cx.eSD <= 4 ? 1 : 0;
        x.alive5 = body(x.id, x.r + 5); x.alive10 = body(x.id, x.r + 10); x.self10 = alive(x.id, x.r + 10) ? 1 : 0;
        const dz = life.get(x.id).death; x.death10 = dz && dz.r <= x.r + 10 ? { r: dz.r, cause: dz.cause, otherLen: dz.otherLen } : null;
        x.len10 = lenAt(x.id, Math.min(x.r + 10, rounds - 1)) - x.L;
        x.ok = x.ex && x.alive10 ? 1 : 0;
        break;
      }
      case 'portal': {
        x.ex = 1; x.alive3 = body(x.id, x.r + 3); x.alive10 = body(x.id, x.r + 10); x.self3 = alive(x.id, x.r + 3) ? 1 : 0; x.eat10 = eatsIn(x.id, x.r, x.r + 10);
        const dz = life.get(x.id).death; x.death10 = dz && dz.r <= x.r + 10 ? { r: dz.r, cause: dz.cause, otherLen: dz.otherLen } : null;
        x.ok = x.alive3 ? 1 : 0;
        // stack4 (study 5.2, report.js pCls): died on the crossing step itself; the blocker was ours; desperate entry = label v <= -20
        x.stepDeath = x.onStep && x.died ? 1 : 0;
        x.stepOwn = x.stepDeath && !x.feedLbl && x.died.otherTeam === us ? 1 : 0;
        x.desperate = x.v !== null && x.v !== undefined && x.v <= -20 ? 1 : 0;
        if (x.stepDeath) { hyp.pStepN = (hyp.pStepN || 0) + 1; if (x.stepOwn) { if (x.desperate) hyp.pStepOwnDesp = (hyp.pStepOwnDesp || 0) + 1; else hyp.pStepOwn = (hyp.pStepOwn || 0) + 1; } }
        if (x.stepOwn && !x.desperate) ext.pstep.push({ r: x.r, id: x.id, L: x.L, v: x.v, blind: x.blind, map: mapKey, opp: task.opp, game: task.gameId || task.key, otherLen: x.died.otherLen, cause: x.died.cause });
        { const p8 = (S8.pings.get(x.id + ':' + (x.r - 1)) || []).find(q => q[0] === x.pFrom && q[1] === x.pDir); // stack8: the probe
          x.probe = !p8 ? 'none' : p8[2] === 'ally' || p8[2] === 'allyHead' ? 'ally' : p8[2] === 'enemy' || p8[2] === 'enemyHead' ? 'enemy' : 'clean'; x.probeHead = p8 && /Head$/.test(p8[2]) ? 1 : 0; }
        break;
      }
      case 'trade': {
        x.ex = x.died && x.died.cause === 3 ? 1 : 0;
        if (x.ex) {
          x.killed = x.died.pairLen; x.fair = x.killed >= x.L ? 1 : 0;
          const mine = eaters(x.died.idx), theirs = x.died.pairIdx >= 0 ? eaters(x.died.pairIdx) : [];
          x.pUs = mine.concat(theirs).filter(q => q[1] === us).length; x.pThem = mine.concat(theirs).filter(q => q[1] !== us).length;
        } else { x.alive5 = alive(x.id, x.r + 5) ? 1 : 0; x.otherDeath = x.died ? x.died.cause : null; }
        x.ok = x.ex && x.fair && x.pUs >= x.pThem ? 1 : 0;
        break;
      }
      case 'sprint': x.ex = x.steps >= 2 ? 1 : 0; x.ok = x.ate > 0 ? 1 : 0; break;
      case 'sprintEsc': x.ex = x.steps >= 2 && !x.died ? 1 : 0; x.alive10 = body(x.id, x.r + 10); x.self10 = alive(x.id, x.r + 10) ? 1 : 0;
        { const dz = life.get(x.id).death; x.death10 = dz && dz.r <= x.r + 10 ? { r: dz.r, cause: dz.cause, otherLen: dz.otherLen } : null; }
        x.ok = x.ex && x.alive10 ? 1 : 0; break;
      case 'noexit': x.ex = 1; x.ok = null; break;
      default: {
        x.ex = 1; x.alive10 = alive(x.id, x.r + 10) ? 1 : 0; x.diedNow = x.died ? 1 : 0;
        if (x.died) { const E = eaters(x.died.idx); x.eatOwn = E.filter(q => q[1] === us).length; x.eatEnemy = E.filter(q => q[1] !== us).length; x.drops = x.died.drops; }
        x.ok = null;
      }
    }
    delete x.died; delete x.child;
  }
  // stack5 F: one record per dragon and chosen fountain. The group = true fountains within 3 steps of it; the effect window =
  // the 30 rounds after the head first came within 3 steps; share = natural pearls spawned there eaten by us / spawned
  for (const x of T5.fEp.values()) {
    x.map = mapKey; x.opp = task.opp; x.game = task.gameId || task.key; x.ph = phaseOf(x.r);
    x.sit = x.fnt && x.own && !x.guarded0 ? 1 : 0; x.ex = x.rArr !== null ? 1 : 0; x.ok = null;
    if (x.ex && T5.fnt) {
      const grp = new Set(); bfs([x.a], 3, () => true, u => { if (T5.fnt[u]) grp.add(u); return false; });
      let n5 = 0, u5 = 0, t5 = 0;
      for (const q of T5.sp) if (q.r > x.rArr && q.r <= x.rArr + 30 && grp.has(q.k)) { n5++; if (q.e === 1) u5++; else if (q.e === 2) t5++; }
      x.grp = grp.size; x.spN = n5; x.spUs = u5; x.spThem = t5; x.ok = n5 > 0 ? (u5 >= 0.85 * n5 ? 1 : 0) : null;
    }
    recs.push(x);
  }
  { // stack8: another of our dragons' F episode on the same fountain overlaps this one (two heads chasing one fountain)
    const byA8 = new Map(); for (const x of T5.fEp.values()) { if (!byA8.has(x.a)) byA8.set(x.a, []); byA8.get(x.a).push(x); }
    for (const L8 of byA8.values()) for (const x of L8) x.dbl = L8.some(y => y.id !== x.id && y.r <= x.r1 && y.r1 >= x.r) ? 1 : 0;
  }
  for (const i of sacIdx) for (const q of eaters(i)) { if (q[1] === us) hyp.sac250Own++; else hyp.sac250Enemy++; }
  // gathering toward the king (g label, from GATHER_START): did the dragon reach it, feed it, or die on the way?
  const feeders = new Set(recs.filter(x => x.k === 'feed' && x.ex).map(x => x.id));
  for (const gz of gather.values()) {
    const dz = life.get(gz.id) && life.get(gz.id).death;
    // loop: the dragon handed its body to a child by an escape split during the episode (corridor loop), not a loss
    const loop = lastEscSplit.has(gz.id) && lastEscSplit.get(gz.id) >= gz.r0 ? 1 : 0, fed = feeders.has(gz.id) ? 1 : 0;
    recs.push({ k: 'gather', r: gz.r0, id: gz.id, L: gz.L0, map: mapKey, opp: task.opp, game: task.gameId || task.key, ph: phaseOf(gz.r0), cx: {},
      d0: gz.d0, dMin: gz.dMin, turns: gz.r1 - gz.r0 + 1, fed, loop, aliveEnd: dz ? 0 : 1,
      death: dz && !fed && !loop ? { r: dz.r, cause: dz.cause, otherLen: dz.otherLen } : null, ex: 1,
      ok: fed || gz.dMin <= 3 ? 1 : loop ? null : 0 });
    // stack4 (study 4.2, px criterion 2): deaths after the start outside corridor loops, and those against our own dragons
    if (!loop) { ext.gEp = (ext.gEp || 0) + 1; if (dz && !fed) { ext.gDeath = (ext.gDeath || 0) + 1; if (dz.cause === 5 || dz.otherTeam === us) ext.gOwn = (ext.gOwn || 0) + 1; } }
  }
  // cand-conv2: kch holds and k2 pulls, one record per dragon; the lineage metrics of this game (tag-independent)
  {
    const lab = recs.filter(x => (x.k === 'feed' || x.k === 'conv' || x.k === 'k2') && x.ex);
    for (const [id, q] of c2Hold) {
      const dz = life.get(id) && life.get(id).death, fedKc = lab.some(x => x.id === id && x.kc && x.r >= q.r0) ? 1 : 0;
      recs.push({ k: 'kch', r: q.r0, id, L: q.L0, map: mapKey, opp: task.opp, game: task.gameId || task.key, ph: phaseOf(q.r0), cx: q.cx, turns: q.turns, r1: q.r1,
        fedKc, aliveEnd: dz ? 0 : 1, bodyEnd: familyLen(id, rounds - 1) > 0 ? 1 : 0, death: dz ? { r: dz.r, cause: dz.cause, otherLen: dz.otherLen } : null, ex: 1,
        ok: fedKc || familyLen(id, rounds - 1) > 0 ? 1 : 0 });
    }
    for (const [id, q] of c2Pull) {
      const dz = life.get(id) && life.get(id).death, fed = lab.find(x => x.id === id && x.r >= q.r0);
      recs.push({ k: 'k2g', r: q.r0, id, L: q.L0, map: mapKey, opp: task.opp, game: task.gameId || task.key, ph: phaseOf(q.r0), cx: q.cx, turns: q.turns, r1: q.r1,
        fed: fed ? fed.k : null, fedLine: fed ? fed.eatLine || 0 : 0, onLine: c2.win.has(id) ? 1 : 0, aliveEnd: dz ? 0 : 1, bodyEnd: familyLen(id, rounds - 1) > 0 ? 1 : 0,
        death: dz && !fed ? { r: dz.r, cause: dz.cause, otherLen: dz.otherLen } : null, ex: 1, ok: fed ? 1 : 0 });
    }
  }
  const c2o = { g: 1, r500: ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'].includes(task.map) ? 1 : 0, full: rounds >= 500 ? 1 : 0, king: fin.get(finKing) || 0,
    sac300Drops: 0, sac300Line: 0, sac300Own: 0, lineSac350: 0, mid400: 0, mid400Alive: 0, mid400Fed: 0, mid400AliveLen: 0 };
  {
    const ld = (idx, a, b) => (deathEat.get(idx) || []).filter(q => q[1] === us && c2.inLine(q[0], q[2]) && q[2] >= a && q[2] < b).length;
    for (let i = 0; i < deathsAll.length; i++) {
      const x = deathsAll[i]; if (x.team !== us || x.cause !== 0) continue;
      if (x.r >= 300) { c2o.sac300Drops += x.drops; c2o.sac300Line += ld(i, 0, 1e9); c2o.sac300Own += x.eatOwn; }
      c2o.lineSac350 += ld(i, 350, 1e9);
    }
    const m400 = snaps.get(400);
    if (m400) for (const [id, L4] of m400) {
      if (L4 < 8 || c2.inLine(id, 400)) continue;
      c2o.mid400++;
      // the family after r400: the dragon and its descendants born later
      let alive = 0, aliveLen = 0, toLine = 0; const st = [id];
      while (st.length) { const y = st.pop(); if (fin.has(y)) { alive = 1; aliveLen += fin.get(y); } const Ly = life.get(y); if (Ly && Ly.death) toLine += ld(Ly.death.idx, 400, 1e9);
        for (const [cid, Lc] of life) if (Lc.parent === y && Lc.born >= 400) st.push(cid); } // born in round 400 = after its first-turn snapshot
      if (alive) { c2o.mid400Alive++; c2o.mid400AliveLen += aliveLen; }
      if (toLine > 0) c2o.mid400Fed++;
    }
  }
  // stack4 gx: one record per dragon with a gx turn (gathering suppressed: too few rounds left); effect = its body (the dragon and its
  // descendants born later) alive at the end (user decision 2026-09-30 17:16: survival is judged by the body; the dragon itself = reference)
  for (const [id, q] of gxEp) {
    const dz = life.get(id) && life.get(id).death, bodyEnd = familyLen(id, rounds - 1) > 0 ? 1 : 0;
    recs.push({ k: 'gx', r: q.r0, id, L: q.L0, map: mapKey, opp: task.opp, game: task.gameId || task.key, ph: phaseOf(q.r0), cx: q.cx, turns: q.turns, r1: q.r1,
      aliveEnd: dz ? 0 : 1, bodyEnd, fed: feeders.has(id) ? 1 : 0, death: dz ? { r: dz.r, cause: dz.cause, otherLen: dz.otherLen } : null, ex: 1, ok: bodyEnd });
  }
  // stack4: cornered turns, body length kept 10 and 30 rounds on (collect.js: sums per response; famLen with descendants)
  for (const c4 of ext.corn) {
    c4.f10 = famLenAt(c4.id, c4.r + 10); c4.f30 = famLenAt(c4.id, c4.r + 30);
    const dz = life.get(c4.id) && life.get(c4.id).death; c4.d10 = dz && dz.r <= c4.r + 10 ? 1 : 0; c4.fd10 = body(c4.id, c4.r + 10) ? 0 : 1;
  }
  // cand-mapid: every process's map recognition against the truth; one record per game with any tag. A process's state is
  // its last tag (the bot writes one on the first turn and on every change). Decided = the tag names a layout (a or b).
  if (mapTags.size) {
    const tname = task.map.replace(/ /g, '_'), tl = truthLay(), truth = tname + '/' + tl;
    const p = { procs: 0, untagged: 0, decided: 0, right: 0, wrong: 0, fam: 0, unk: 0, none: 0, init: 0, init0: 0, init0Right: 0, delays: [], bad: [] };
    const isDec = t => /\/[ab]$/.test(t);
    let first = null;
    for (const [id, Lf] of life) {
      const T = mapTags.get(id); p.procs++;
      if (!T) { p.untagged++; continue; }
      const last = T[T.length - 1], born = Lf.born;
      if (born === 0) { p.init++; if (T[0].r === 0 && isDec(T[0].tag)) { p.init0++; if (T[0].tag === truth) p.init0Right++; } }
      const dec = T.find(t => isDec(t.tag));
      if (dec) { p.delays.push(dec.r - born); if (!first || dec.r < first.r) first = { r: dec.r, tag: dec.tag, id }; }
      if (isDec(last.tag)) { p.decided++; if (last.tag === truth) p.right++; else { p.wrong++; p.bad.push({ id, born, r: last.r, tag: last.tag }); } }
      else if (last.tag === 'none') { p.none++; p.bad.push({ id, born, r: last.r, tag: last.tag }); }
      else if (last.tag === '?') p.unk++;
      else if (last.tag === tname + '/?') p.fam++;
      else { p.wrong++; p.bad.push({ id, born, r: last.r, tag: last.tag }); }                // a wrong family
    }
    const known = tl === 'a' || tl === 'b';
    recs.push({ k: 'mapid', r: first ? first.r : 0, id: first ? first.id : -1, L: 0, map: task.map + ' ' + tl, opp: task.opp, game: task.gameId || task.key,
      ph: phaseOf(first ? Math.min(first.r, 499) : 0), truth, call: first ? first.tag : null, spawnTruth: task.layout ? layoutTruth(R, task.map) : null, ...p,
      ex: 1, ok: !known ? null : (p.decided > 0 && p.wrong === 0 && p.none === 0 ? 1 : 0) });
  }
  // cand-mapid bsplit's hypothesis-level indicators, for every Schooltime game (tagged or not, so any set compares): our units
  // at r50 / r100, natural pearls we ate in r0-99, eliminated or not, final longest, and this game's bsplit splits
  let econ = null;
  if (task.map === 'Schooltime') {
    const FI = require('./mass_ledger.js').FI, T = g[us];
    econ = { layout: truthLay(), u50: T.st.units[5], u100: T.st.units[10], nat100: T.fl[FI.eat_nat].slice(0, 10).reduce((s, v) => s + v, 0), elim: T.st.units[50] === 0 ? 1 : 0,
      G: T.st.units[50] === 0 ? 0 : T.st.king[50], bsp: recs.filter(x => x.k === 'bsplit').length };
  }
  const t5o = { g100: T5.snap ? 1 : 0, u100: T5.snap ? T5.snap.u : 0, vr: T5.snap ? T5.snap.vr : null, fr: T5.snap ? T5.snap.fr : null,
    own: 0, ownUs: 0, ownThem: 0, fo: 0, foUs: 0, foThem: 0, layout: T5.layout || null, err: T5.err || null,             // stack5
    dTrap: T5.dTrap || 0, dRam: T5.dRam || 0, dAlly: T5.dAlly || 0, dTrap250: T5.dTrap250 || 0, dRam250: T5.dRam250 || 0, dAlly250: T5.dAlly250 || 0, spare: T5.spare || 0 };
  for (const q of T5.sp) { if (!T5.terr || T5.terr[q.k] !== ourTerr) continue; t5o.own++; if (q.e === 1) t5o.ownUs++; else if (q.e === 2) t5o.ownThem++;
    if (T5.fnt[q.k]) { t5o.fo++; if (q.e === 1) t5o.foUs++; else if (q.e === 2) t5o.foThem++; } }
  // stack7 (cand-stack7.md): the elimination study's per-game numbers for our team (exp/eliminations/top.js I, lib.js classOf), tag-
  // independent so that any set compares, and the map gate (this game's floor / kcap firings, the processes' own last map tags)
  const s7 = (() => {
    const L7 = require(path.join(ROOT, 'exp', 'eliminations', 'lib.js'));
    const nEnd = fin.size, elimR = nEnd === 0 ? S7.lastDeath : -1, end = elimR >= 0 ? elimR : rounds;
    const kEnd = nEnd ? Math.max(...fin.values()) : 0, tEnd = [...fin.values()].reduce((s, v) => s + v, 0);
    const at = (arr, r, v) => r >= rounds || arr[r] === undefined ? v : arr[r];   // lib.js at(): after the end, the final state
    const uAt = r => at(S7.u, r, nEnd), euAt = r => at(S7.eu, r, S7.euEnd), aliveAt = r => !(elimR >= 0 && elimR < r);
    let ep = null;
    for (let r = 50; r + 20 < rounds && r < end; r += 5) {                          // top.js I: the first low-unit state from r50
      const u = uAt(r), eu = euAt(r);
      if (u > 3 || u === 0 || eu < 8) continue;
      const w = recs.filter(x => x.ex && x.r >= r && x.r < r + 20), n = k => w.filter(x => x.k === k).length;
      ep = { r, u, eu, t: at(S7.t, r, tEnd), k: at(S7.k, r, kEnd), rec: uAt(r + 20) >= 4 && aliveAt(r + 20) ? 1 : 0, die50: elimR >= 0 && elimR <= r + 50 ? 1 : 0,
        nonEsc: w.filter(x => S7_SPLITS.has(x.k)).length, floor: n('floor'), kcap: n('kcap'), csplit: n('csplit'),
        all: [...life.values()].filter(q => q.parent !== undefined && q.parent !== null && q.parent >= 0 && q.born >= r && q.born < r + 20).length };
      break;
    }
    const fam = t => t ? t.split('/')[0].replace(/_/g, ' ') : null;
    let procs = 0, recog = 0; for (const id of life.keys()) { procs++; const T = mapTags.get(id); if (T && fam(T[T.length - 1].tag) === task.map) recog++; }
    const fire = recs.filter(x => x.k === 'floor' || x.k === 'kcap');
    return { map: task.map, key: mapKey, lay: LAYOUT_FILES[task.map] && task.map !== 'Prisoners Dilemma' ? truthLay() : null, type: L7.kindOf(task.map),
      on: S7_FLOOR_MAPS.has(task.map) ? 1 : 0, kon: S7_KCAP_MAPS.has(task.map) ? 1 : 0, elim: elimR >= 0 ? 1 : 0, elimR, cls: elimR >= 0 ? L7.classOf(elimR, S7.kd) : null,
      u100: uAt(100), k50: at(S7.k, 50, kEnd), d8: S7.d8, ep, floorN: fire.filter(x => x.k === 'floor').length, kcapN: fire.filter(x => x.k === 'kcap').length,
      offTag: fire.filter(x => !(x.k === 'floor' ? S7_FLOOR_MAPS : S7_KCAP_MAPS).has(fam(x.mt))).length, tagged: mapTags.size, procs, recog };
  })();
  return { t5: t5o, key: task.key, set: task.set, src: task.src, map: mapKey, opp: task.opp, game: task.gameId || task.key, us, rounds, endReason: g.endReason,
    chk: g.chk, health, counts, hyp, recs, ext, econ, c2: c2o, s7,                  // cand-conv2 c2, stack7 s7
    s8: { fT: S8.fT, fCand: S8.fCand, fAway: S8.fAway } };                          // stack8 pull-away counts
}

// ---------------------------------------------------------------------------------------------------------------
// Tasks
function teamNames() { try { return Object.fromEntries(JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'top', 'leaderboard.json'), 'utf8')).map(t => [t.id, t.name])); } catch { return {}; } }
function tasksOf(pool) {
  const names = teamNames(), out = [];
  for (const part of pool.split('+')) {
    const abs = path.resolve(ROOT, part);
    if (fs.existsSync(path.join(abs, 'rows.jsonl'))) {
      for (const l of fs.readFileSync(path.join(abs, 'rows.jsonl'), 'utf8').split('\n')) {
        if (!l.trim()) continue;
        const row = JSON.parse(l), [opp, map, side, seed] = row.key.split(':');
        const f = path.join(abs, 'games', `${opp}_${map}_${side}_${seed}`, 'game.replay'); if (!fs.existsSync(f)) continue;
        out.push({ key: part + ':' + row.key, file: f, set: part, src: 'local', map: MAPNAME[map.replace(/_(b|10)$/, '')] || map, opp, us: side,
          layout: /_(b|10)$/.test(map) ? 'b' : 'a' });                                        // cand-mapid: the file's pearl layout
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

function workerMain() {
  const { makeLoader, viewerSource } = require('./top_features.js');
  const { perGame } = require('./mass_ledger.js');
  const load = makeLoader(viewerSource());
  process.on('message', task => {
    try {
      process.send({ ok: true, res: analyse(load(task.file), task, perGame) });
    } catch (err) { process.send({ ok: false, key: task.key, error: String((err && err.stack) || err).split('\n').slice(0, 4).join(' | ') }); }
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

// ---------------------------------------------------------------------------------------------------------------
// Report
const pct = (a, b) => b ? Math.round(100 * a / b) + '%' : '–';
const avg = (xs) => xs.length ? xs.reduce((s, v) => s + v, 0) / xs.length : null;
const f1 = v => v === null || v === undefined ? '–' : (Math.round(v * 10) / 10).toString();
const CAUSE_KO = ['희생', '갇힘', '박힘(상대 돌진)', '돌진', '적 몸통', '아군 머리', '시간 초과', '질주 불가'];
const LABEL = { gather: '왕에게 모이기 (g, 드래곤 단위)', feed: '희생 먹이기 (feed)', conv: '큰 아군 곁 희생 (conv, stack1 M1)', pocket: '막다른 길 한입 (pocket-eat)', escsplit: '탈출 분열 (escape-split)', split: '정책 분열 (split)',
  esc: '탈출 질주 3칸 (esc)', sprintEsc: '위협 피하기 2칸 질주', portal: '포털 통과 (전체; PORTAL?=미탐색 출구)', trade: '돌진 (TRADE)', sprint: '먹이 질주 (2칸 이상, 먹은 것)',
  sprintOther: '기타 2칸 질주', lasttrade: '마지막 돌진 (last-trade)', noexit: '출구 없음 (no-exit)',
  frag: '조각 떼기 (split frag, stack2 S1)', grab: '새 사망 진주 줍기 (grab, stack2 S2; 진주 단위)',
  tg: '위협 모형 빈틈 (tg, stack4)', escsplit2: '몰렸을 때 분열 (esc-split, stack4)', px: '포털 출구 혼잡 피하기 (px, stack4)', gx: '모이기 시작 제한 (gx, stack4; 드래곤 단위)',
  mapid: '지도·판본 인식 (map=, cand-mapid; 판 단위)', bsplit: 'Schooltime b 초반 분열 (split bsp, cand-mapid)' };
const ORDER = ['mapid', 'bsplit', 'tg', 'escsplit2', 'px', 'gx', 'conv', 'frag', 'grab', 'gather', 'feed', 'pocket', 'escsplit', 'noexit', 'split', 'esc', 'sprintEsc', 'portal', 'trade', 'sprint', 'sprintOther', 'lasttrade'];
Object.assign(LABEL, { csplit: '덮기 분열 (csplit, stack5)', fguard: '샘 지킴 (F, stack5; 드래곤·샘 단위)', cov: '영토 덮기 끌림 (cov, stack5)' }); // stack5
ORDER.splice(ORDER.indexOf('tg') >= 0 ? ORDER.indexOf('tg') : 0, 0, 'csplit', 'fguard', 'cov');
Object.assign(LABEL, { k2: '두 번째 단계 먹이기 (k2, conv2)', k2g: '왕 후보 쪽 끌림 (k2 표식, conv2; 드래곤 단위)', kch: '후보 아닌 아군 희생 보류 (kch, conv2; 드래곤 단위)' }); // cand-conv2
ORDER.splice(0, 0, 'k2', 'k2g', 'kch');                                                                // cand-conv2
Object.assign(LABEL, { floor: '수 바닥 분열 (split floor, stack7)', kcap: '왕 길이 상한 분열 (split kcap, stack7)' });              // stack7
ORDER.splice(0, 0, 'floor', 'kcap');                                                                   // stack7
Object.assign(LABEL, { px2: '아군을 친 탐침 뒤 포털 (px2, stack8)', fp: '몫이 있어 F 끌림 멈춤 (Fp, stack8; 드래곤·진주 단위)',
  cl: '몫을 긴 아군에게 넘기지 않음 (cl, stack8; 드래곤·진주 단위)', ce: '몫을 한 걸음 가까운 적에게 넘기지 않음 (ce, stack8; 드래곤·진주 단위)' }); // stack8
ORDER.splice(0, 0, 'fp', 'cl', 'ce', 'px2');                                                          // stack8
// stack4: rams on our long dragons classified at the last decision, exactly as exp/mech-failures/report.js ramCls (esc-split added)
const vOf = t => { const m = t && / v(-?[\d.]+)/.exec(t); return m ? +m[1] : null; };
const ramCls = d => {
  const k = d.atDecision;
  if (!d.hasDecision) return 'newborn: no decision before the ram';
  if (d.text && /^(feed|escape-split|esc-split|no-exit|split|pocket|last-trade)/.test(d.text)) return 'label ' + d.text.split(/[ \d]/)[0];
  if (!k) { const ourR = d.killerId !== undefined && d.id > d.killerId ? d.r - 1 : d.r; return d.killerBorn >= ourR ? 'unseen: killer born after the decision (a split)' : 'unseen: killer farther than 8 at the decision'; }
  if (k.cheb > 3) return 'unseen: killer outside the 7x7 view';
  const inf = k.tailVis ? k.vis - 1 : Math.max(3, k.vis - 1);
  if (d.killerSteps > inf) return d.killerAte ? 'reach gap: pearl eaten on the strike path' : 'reach gap: tail unseen, killer L>=5';
  const v = vOf(d.text);
  if (v !== null && v < 0) return 'priced: in reach, threat in the value (v<0), still hit';
  if (d.newHeadWasOcc || d.pathThroughOcc > 0) return 'blind spot: path through a tile occupied at the decision';
  return 'unpriced: cause not visible in the replay';
};

function summarise(games) {
  const recs = games.flatMap(g => g.recs), by = {};
  for (const x of recs) (by[x.k] = by[x.k] || []).push(x);
  const S = { games: games.length, by, econ: games.filter(g => g.econ).map(g => g.econ), health: {}, counts: { K: 0, g: 0, T: 0, late: 0, ks: 0, ks2: 0, trustRammed: 0 }, hyp: {}, hypR500: {}, gamesR500: 0 };
  const R500 = new Set(['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']);
  for (const g of games) {
    for (const [k, v] of Object.entries(g.health)) S.health[k] = k === 'maxInstr' ? Math.max(S.health[k] || 0, v) : (S.health[k] || 0) + v;
    for (const k of Object.keys(S.counts)) S.counts[k] += g.counts[k] || 0;
    for (const [k, v] of Object.entries(g.hyp || {})) { S.hyp[k] = (S.hyp[k] || 0) + v; if (R500.has(g.map)) S.hypR500[k] = (S.hypR500[k] || 0) + v; }
    if (R500.has(g.map)) S.gamesR500++;
  }
  // stack4 hypothesis metrics, kept per set (a pool may join several sets)
  S.ext4 = {};
  for (const g of games) {
    const e = g.ext || {}, h = g.hyp || {};
    const s = S.ext4[g.set] || (S.ext4[g.set] = { games: 0, rams: [], corn: [], pstep: [], pStepN: 0, pStepOwn: 0, pStepOwnDesp: 0, gEp: 0, gDeath: 0, gOwn: 0, gxN: 0, sxN: 0,
      l6T: 0, l6P4: 0, l6M4: 0, kT: 0, kP4: 0, kP7: 0, kMT: 0, kM7: 0 });
    s.games++;
    for (const x of e.rams || []) s.rams.push({ ...x, map: g.map, opp: g.opp, game: g.game });
    for (const x of e.corn || []) s.corn.push(x);
    for (const x of e.pstep || []) s.pstep.push(x);
    s.pStepN += h.pStepN || 0; s.pStepOwn += h.pStepOwn || 0; s.pStepOwnDesp += h.pStepOwnDesp || 0;
    s.gEp += e.gEp || 0; s.gDeath += e.gDeath || 0; s.gOwn += e.gOwn || 0; s.gxN += e.gxN || 0; s.sxN += e.sxN || 0;
    for (const f of ['l6T', 'l6P4', 'l6M4', 'kT', 'kP4', 'kP7']) s[f] += e[f] || 0;               // stack4 path-distance exposure
    s.kMT += h.kingT400 || 0; s.kM7 += h.kingExp400 || 0;                                          // the Manhattan twin (stack3 ks2 metric)
  }
  S.t5 = stack5Sum(games);                                                                          // stack5
  S.s7 = games.filter(g => g.s7).map(g => ({ ...g.s7, set: g.set, opp: g.opp, game: g.game }));       // stack7
  S.c2 = {}; for (const g of games) if (g.c2) for (const [k, v] of Object.entries(g.c2)) { if (!S.c2.all) S.c2.all = {}; S.c2.all[k] = (S.c2.all[k] || 0) + v; // cand-conv2
    if (g.c2.r500 && g.c2.full) { if (!S.c2.r500) S.c2.r500 = {}; S.c2.r500[k] = (S.c2.r500[k] || 0) + v; } }
  S.s8 = { fT: 0, fCand: 0, fAway: 0 }; for (const g of games) if (g.s8) for (const k of Object.keys(S.s8)) S.s8[k] += g.s8[k] || 0; // stack8
  return S;
}
// one line of effect numbers per mechanism
function effectLine(k, xs) {
  const ex = xs.filter(x => x.ex);
  switch (k) {
    case 'k2': { const d = ex.reduce((s, x) => s + x.drops, 0); // cand-conv2
      return `실행 ${pct(ex.length, xs.length)} · 설계 상황(지목 아군이 그 순간 팀 최장) ${pct(xs.filter(x => x.sit).length, xs.filter(x => x.sit !== null && x.sit !== undefined).length)} · 떨군 진주 ${d}개 중 최종 왕 계보 ${pct(ex.reduce((s, x) => s + (x.eatLine || 0), 0), d)} · 우리 팀 ${pct(ex.reduce((s, x) => s + x.eatOwn, 0), d)} · 상대 ${pct(ex.reduce((s, x) => s + x.eatEnemy, 0), d)} · 지목 아군이 그 순간 계보 ${pct(xs.filter(x => x.tOnLine).length, xs.length)} · 최종 왕 ${pct(xs.filter(x => x.tFinalKing).length, xs.length)} · 먹인 길이 평균 ${f1(avg(xs.map(x => x.L)))}`; }
    case 'kch': return `드래곤 ${xs.length} (표식 턴 ${xs.reduce((s, x) => s + x.turns, 0)}) · 뒤에 후보에게 희생(kc) ${pct(xs.filter(x => x.fedKc).length, xs.length)} · 몸(자손 포함) 끝까지 ${pct(xs.filter(x => x.bodyEnd).length, xs.length)} · 드래곤 자체 끝까지 ${pct(xs.filter(x => x.aliveEnd).length, xs.length)}`; // cand-conv2
    case 'k2g': return `드래곤 ${xs.length} (표식 턴 ${xs.reduce((s, x) => s + x.turns, 0)}, 시작 길이 평균 ${f1(avg(xs.map(x => x.L)))}) · 표식 희생으로 끝남 ${pct(xs.filter(x => x.fed).length, xs.length)} (k2 ${xs.filter(x => x.fed === 'k2').length}, feed ${xs.filter(x => x.fed === 'feed').length}, conv ${xs.filter(x => x.fed === 'conv').length}; 계보가 먹은 진주 ${xs.reduce((s, x) => s + x.fedLine, 0)}) · 스스로 최종 왕 계보 ${pct(xs.filter(x => x.onLine).length, xs.length)} · 끝까지 생존 ${pct(xs.filter(x => x.aliveEnd).length, xs.length)}`; // cand-conv2
    case 'feed': case 'conv': { const d = ex.reduce((s, x) => s + x.drops, 0), td = {}; for (const x of xs) if (x.tDeath) td[CAUSE_KO[x.tDeath.cause]] = (td[CAUSE_KO[x.tDeath.cause]] || 0) + 1;
      return `실행 ${pct(ex.length, xs.length)} · 떨군 진주 ${d}개 중 우리 팀 ${pct(ex.reduce((s, x) => s + x.eatOwn, 0), d)} (지목한 아군 ${pct(ex.reduce((s, x) => s + x.eatT, 0), d)}) · 상대 ${pct(ex.reduce((s, x) => s + x.eatEnemy, 0), d)} · 지목 아군 끝까지 생존 ${pct(xs.filter(x => x.tAliveEnd).length, xs.length)} (그 뒤 죽은 원인: ${Object.entries(td).map(([k, v]) => k + ' ' + v).join(', ') || '없음'}) · 지목 아군의 몸(자손 포함)이 끝까지 삶 ${pct(xs.filter(x => x.tBodyEnd).length, xs.length)} · 최종 왕 ${pct(xs.filter(x => x.tFinalKing).length, xs.length)} (최종 왕이 지목 아군의 자손 ${pct(xs.filter(x => x.tKingLine).length, xs.length)})`; }
    case 'pocket': return `한입 ${pct(ex.length, xs.length)} · 2턴 안 분열 ${pct(xs.filter(x => x.splitNext).length, xs.length)} · 30라운드 뒤 가족 길이 변화 ${f1(avg(xs.map(x => x.fam30)))} (줄지 않음 ${pct(xs.filter(x => x.fam30 >= 0).length, xs.length)})`;
    case 'escsplit': return `분열 ${pct(ex.length, xs.length)} · 몸(가족)이 10라운드 뒤 살아 있음 ${pct(ex.filter(x => x.famAlive10).length, ex.length)} · 새끼 자체 10라운드 생존 ${pct(ex.filter(x => x.childAlive10).length, ex.length)} · 30라운드 뒤 가족 길이 변화 ${f1(avg(ex.map(x => x.fam30)))}`;
    case 'split': return `분열 ${pct(ex.length, xs.length)} · 새끼 30라운드 생존 ${pct(ex.filter(x => x.childAlive30).length, ex.length)} · 30라운드 뒤 가족 길이 변화 ${f1(avg(ex.map(x => x.fam30)))}`;
    case 'esc': return `질주 ${pct(ex.length, xs.length)} · 짧은 적 머리 4칸 안 ${pct(xs.filter(x => x.sit).length, xs.length)} · 몸 생존 5라운드 ${pct(ex.filter(x => x.alive5).length, ex.length)} · 10라운드 ${pct(ex.filter(x => x.alive10).length, ex.length)} (드래곤 자체 ${pct(ex.filter(x => x.self10).length, ex.length)}) · 10라운드 길이 변화 ${f1(avg(ex.map(x => x.len10)))}`;
    case 'portal': { const b = xs.filter(x => x.blind); return `미탐색 출구 ${b.length}회(몸 3라운드 생존 ${pct(b.filter(x => x.alive3).length, b.length)}) · 전체 몸 생존 3라운드 ${pct(xs.filter(x => x.alive3).length, xs.length)} (드래곤 자체 ${pct(xs.filter(x => x.self3).length, xs.length)}) · 10라운드 ${pct(xs.filter(x => x.alive10).length, xs.length)} · 10라운드 안 먹은 진주 ${f1(avg(xs.map(x => x.eat10)))}`; }
    case 'trade': { const r4 = xs.filter(x => x.ram4 === 'new'), r4x = r4.filter(x => x.ex), c1 = r4x.filter(x => x.coll === 1), c0 = r4x.filter(x => x.coll === 0), sumP = (a, f) => a.reduce((s, x) => s + (x[f] || 0), 0);
      return `충돌 성사 ${pct(ex.length, xs.length)} (인접 ${xs.filter(x => x.path === 1).length}, 경로 ${xs.filter(x => x.path > 1).length}) · 잡은 길이 ≥ 우리 ${pct(ex.filter(x => x.fair).length, ex.length)} · 두 몸의 진주 우리 ${sumP(ex, 'pUs')} 대 상대 ${sumP(ex, 'pThem')}` +
        (r4.length ? ` · 새 작은 조각 박치기(ram4) ${r4.length}회, 성사 ${r4x.length}: 곁에 아군 있음 ${c1.length}회(진주 우리 ${sumP(c1, 'pUs')} 대 ${sumP(c1, 'pThem')}), 없음 ${c0.length}회(${sumP(c0, 'pUs')} 대 ${sumP(c0, 'pThem')})` : ''); }
    case 'sprint': return `먹음 ${pct(xs.filter(x => x.ok).length, xs.length)}`;
    case 'sprintEsc': return `질주 ${pct(ex.length, xs.length)} · 몸 10라운드 생존 ${pct(ex.filter(x => x.alive10).length, ex.length)} (드래곤 자체 ${pct(ex.filter(x => x.self10).length, ex.length)})`;
    case 'noexit': return `탈출 분열 뒤 남은 조각(고리의 일부) ${pct(xs.filter(x => x.stub).length, xs.length)} · 그 밖(진짜로 갇힘) ${xs.filter(x => !x.stub).length}회`;
    case 'gather': { const nl = xs.filter(x => !x.loop); return `모이기 드래곤 ${xs.length} (그중 통로 고리 세대 ${xs.length - nl.length}, 판정에서 뺌) · 고리 밖 ${nl.length}: 처음 거리 평균 ${f1(avg(nl.map(x => x.d0)))} → 최소 ${f1(avg(nl.map(x => x.dMin)))} · 3칸 안까지 감 ${pct(nl.filter(x => x.dMin <= 3).length, nl.length)} · 희생까지 함 ${pct(nl.filter(x => x.fed).length, nl.length)} · 가는 길에 죽음 ${pct(nl.filter(x => x.death).length, nl.length)} · 끝까지 생존 ${pct(nl.filter(x => x.aliveEnd).length, nl.length)}`; }
    case 'frag': { const fed = ex.filter(x => x.fed), td = {}; for (const x of ex) if (x.childDeath) td[CAUSE_KO[x.childDeath.cause]] = (td[CAUSE_KO[x.childDeath.cause]] || 0) + 1;
      return `분열 ${pct(ex.length, xs.length)} · 설계 상황(부모가 팀 최장이 아니고 7×7 시야에 적 머리 없음) ${pct(xs.filter(x => x.sit).length, xs.length)} · 조각 30라운드 생존 ${pct(ex.filter(x => x.childAlive30).length, ex.length)} · 30라운드 안 1개 이상 먹음 ${pct(ex.filter(x => x.eat30 >= 1).length, ex.length)} (살아서 먹음 ${pct(ex.filter(x => x.childAlive30 && x.eat30 >= 1).length, ex.length)}) · 평생 먹은 진주 평균 ${f1(avg(ex.map(x => x.eatLife)))} · 나중에 아군을 먹임 ${pct(fed.length, ex.length)} (conv ${fed.filter(x => x.fed === 'conv').length}, feed ${fed.filter(x => x.fed === 'feed').length}, 분열 뒤 평균 ${f1(avg(fed.map(x => x.fedAge)))}라운드) · 끝까지 생존 ${pct(ex.filter(x => x.aliveEnd).length, ex.length)} · 30라운드 안 죽은 원인: ${Object.entries(td).map(([k, v]) => k + ' ' + v).join(', ') || '없음'}`; }
    case 'grab': { const dr = xs.filter(x => x.drop), side = (a, s) => a.filter(x => x.side === s).length, con = dr.filter(x => x.contested), ho = dr.filter(x => x.headon);
      return `표적 진주 ${xs.length}개 (표식 턴 ${xs.reduce((s, x) => s + x.turns, 0)}, 진주당 드래곤 ${f1(avg(xs.map(x => x.nIds)))}) · 질량 장부의 사망 진주 ${pct(dr.length, xs.length)} (자연 진주 ${xs.filter(x => x.natural).length}, 이미 없음 ${xs.filter(x => x.gone).length}) · 사망 진주 ${dr.length}개 중 우리가 먹음 ${pct(side(dr, 'us'), dr.length)} · 상대 ${pct(side(dr, 'them'), dr.length)} · 아무도 안 먹음 ${pct(side(dr, 'none'), dr.length)} · 표적으로 삼은 드래곤이 먹음 ${pct(dr.filter(x => x.byTargeter).length, dr.length)} · 우리가 먹기까지 평균 ${f1(avg(dr.filter(x => x.side === 'us').map(x => x.delay)))}라운드 · 상대 머리가 같거나 더 가까웠던 ${con.length}개: 우리 ${pct(side(con, 'us'), con.length)} 대 상대 ${pct(side(con, 'them'), con.length)} · 박치기 진주 ${ho.length}개: 우리 ${pct(side(ho, 'us'), ho.length)} 대 상대 ${pct(side(ho, 'them'), ho.length)} · 우리 팀 사망 진주 ${pct(dr.filter(x => x.dropOurs).length, dr.length)} · 사망 뒤 첫 표적까지 평균 ${f1(avg(dr.map(x => x.dropAge)))}라운드`; }
    case 'tg': { const lb = (a, b) => xs.filter(x => x.L >= a && x.L <= b).length; // stack4
      return `피함(tg) ${pct(xs.filter(x => !x.tgx).length, xs.length)} · 위협 칸으로 감(tgx) ${xs.filter(x => x.tgx).length}턴 · 설계 상황(적 머리가 경로 거리 5 안; 해초·몸은 막고 꼬리는 비는 칸) ${pct(xs.filter(x => x.sit).length, xs.length)} · 2라운드 안 박히지 않음 ${pct(xs.filter(x => !x.rammed2).length, xs.length)} (tg ${pct(xs.filter(x => !x.tgx && !x.rammed2).length, xs.filter(x => !x.tgx).length)}, tgx ${pct(xs.filter(x => x.tgx && !x.rammed2).length, xs.filter(x => x.tgx).length)}) · 길이별 L2-5 ${lb(2, 5)} · L6-9 ${lb(6, 9)} · L10+ ${lb(10, 9999)}`; }
    case 'escsplit2': { const sL = ex.reduce((s, x) => s + x.L, 0), s10 = ex.reduce((s, x) => s + x.fk10, 0), s30 = ex.reduce((s, x) => s + x.fk30, 0); // stack4
      return `분열 ${pct(ex.length, xs.length)} · 설계 상황(몰림: 한 걸음이 모두 짧은 적 머리 사정 안) ${pct(xs.filter(x => x.corn).length, xs.length)} · 꼬리가 적 머리에서 4칸 이상 ${pct(xs.filter(x => x.tailE !== null && x.tailE >= 4).length, xs.length)} · 몸 길이 보존 +10 ${pct(s10, sL)} · +30 ${pct(s30, sL)} (기준 ≥85%) · 10라운드 안 몸 잃음 ${pct(ex.filter(x => !x.famAlive10).length, ex.length)} (기준 ≤10%) · 새끼 10라운드 생존 ${pct(ex.filter(x => x.childAlive10).length, ex.length)}`; }
    case 'px': { const po = xs.filter(x => !x.pxx); // stack4
      return `피함(px) ${pct(po.length, xs.length)} · 붐비는 출구로 넘음(pxx) ${xs.filter(x => x.pxx).length}턴 · 그 턴 우리 드래곤과 충돌 사망 ${xs.filter(x => x.ownDeath).length} (px ${po.filter(x => x.ownDeath).length}, pxx ${xs.filter(x => x.pxx && x.ownDeath).length}) · 몸 3라운드 생존 ${pct(xs.filter(x => x.alive3).length, xs.length)} (보호 지표인 포털 통과 판당·통과 뒤 3라운드 몸 생존은 "포털 통과" 행, 넘는 걸음 죽음은 stack4 가설 지표 절)`; }
    case 'gx': return `드래곤 ${xs.length} (표식 턴 ${xs.reduce((s, x) => s + x.turns, 0)}) · 몸(자손 포함) 끝까지 ${pct(xs.filter(x => x.bodyEnd).length, xs.length)} (기준 ≥80%) · 드래곤 자체 끝까지 생존 ${pct(xs.filter(x => x.aliveEnd).length, xs.length)} (참고) · 뒤에 희생 먹이기(feed)로 끝남 ${xs.filter(x => x.fed).length}`; // stack4; body-based since 17:16 (user)
    case 'bsplit': { const td = {}; for (const x of ex) if (x.childDeath) td[CAUSE_KO[x.childDeath.cause]] = (td[CAUSE_KO[x.childDeath.cause]] || 0) + 1; // cand-mapid
      return `분열 ${pct(ex.length, xs.length)} · 설계 상황(그 판이 실제로 Schooltime b) ${pct(xs.filter(x => x.sit).length, xs.length)} · 조각 10라운드 생존 ${pct(ex.filter(x => x.childAlive10).length, ex.length)} (기준 ≥85%; 상위권 b 92%) · 10라운드 안 1개 이상 먹음 ${pct(ex.filter(x => x.eat10 >= 1).length, ex.length)} (상위권 b 20%) · 부모 10라운드 생존 ${pct(ex.filter(x => x.parentAlive10).length, ex.length)} · 조각 30라운드 생존 ${pct(ex.filter(x => x.childAlive30).length, ex.length)}, 30라운드 안 1개 이상 먹음 ${pct(ex.filter(x => x.eat30 >= 1).length, ex.length)} · 30라운드 뒤 가족 길이 변화 ${f1(avg(ex.map(x => x.fam30)))} · 30라운드 안 조각이 죽은 원인: ${Object.entries(td).map(([k, v]) => k + ' ' + v).join(', ') || '없음'}`; }
    case 'mapid': { const kn = xs.filter(x => x.ok !== null), s = f => xs.reduce((a, x) => a + (x[f] || 0), 0), d = xs.flatMap(x => x.delays || []).sort((a, b) => a - b), q = p => d.length ? d[Math.min(d.length - 1, Math.floor(p * d.length))] : '–'; // cand-mapid
      return `판본을 기보로 가릴 수 있는 판 ${kn.length}/${xs.length} · 그중 맞음(결정한 프로세스가 모두 정답, 1개 이상 결정) ${pct(kn.filter(x => x.ok).length, kn.length)} (기준 ≥95%) · 첫 결정이 정답 ${pct(kn.filter(x => x.call === x.truth).length, kn.length)} · 시작 드래곤 0라운드 결정 ${pct(s('init0'), s('init'))}, 그중 정답 ${pct(s('init0Right'), s('init0'))} · 프로세스 ${s('procs')}: 표식 없음 ${s('untagged')}, 결정 ${s('decided')} (정답 ${pct(s('right'), s('decided'))}, 틀림 ${s('wrong')}), 가족만 ${s('fam')}, 모름 ${s('unk')}, none ${s('none')} · 태어나서 결정까지 p50 ${q(0.5)} / p90 ${q(0.9)} / 최대 ${d.length ? d[d.length - 1] : '–'}라운드`; }
    case 'csplit': case 'fguard': case 'cov': return effectLine5(k, xs);                                  // stack5
    case 'floor': case 'kcap': return effectLine7(k, xs);                                                 // stack7
    case 'px2': case 'fp': case 'cl': case 'ce': return effectLine8(k, xs);                              // stack8
    default: return `그 턴 사망 ${pct(xs.filter(x => x.diedNow).length, xs.length)} · 10라운드 생존 ${pct(xs.filter(x => x.alive10).length, xs.length)}`;
  }
}
function okRate(xs) { const d = xs.filter(x => x.ok !== null && x.ok !== undefined); return d.length ? pct(d.filter(x => x.ok).length, d.length) : '–'; }
function caseLine(x) {
  const where = `${x.opp} · ${x.map} · 게임 ${x.game} · r${x.r} · 드래곤 #${x.id} L${x.L}`;
  const dd = z => z ? `r${z.r} ${CAUSE_KO[z.cause] || z.cause}${z.otherLen ? `, 상대 길이 ${z.otherLen}` : ''}` : '';
  switch (x.k) {
    case 'feed': case 'conv': return `${where}: #${x.target}(L${x.tLen})에게 희생 → ${x.ex ? `진주 ${x.drops}개 중 우리 ${x.eatOwn}, 지목 아군 ${x.eatT}, 상대 ${x.eatEnemy}` : '그 턴에 죽지 않음'}${x.tDeath ? `; 지목 아군 ${dd(x.tDeath)}에 사망` : ''}`;
    case 'esc': return `${where}: 질주 ${x.steps}칸 (가장 가까운 짧은 적 머리 ${x.cx.eSD}칸) → ${x.death10 ? `죽음 ${dd(x.death10)}` : '살아남음'}`;
    case 'portal': return `${where}: 포털${x.blind ? '(미탐색 출구)' : ''} → ${x.death10 ? `죽음 ${dd(x.death10)}` : '살아남음'}, 10라운드 안 진주 ${x.eat10}`;
    case 'trade': return `${where}: 돌진 경로 ${x.path}칸 → ${x.ex ? `상대 L${x.killed} 잡음, 진주 우리 ${x.pUs} 대 상대 ${x.pThem}` : x.otherDeath !== null && x.otherDeath !== undefined ? `충돌 못 함(${CAUSE_KO[x.otherDeath]})` : '충돌 못 함(상대가 비킴)'}`;
    case 'escsplit': case 'split': return `${where}: 새끼 L${x.childLen || '?'} → ${x.childDeath ? `새끼 죽음 ${dd(x.childDeath)}` : '새끼 생존'}${x.k === 'escsplit' ? `, 10라운드 뒤 가족 ${x.famAlive10 ? '생존' : '전멸'}` : ''}, 30라운드 뒤 가족 길이 변화 ${x.fam30}`;
    case 'sprintEsc': return `${where}: 2칸 질주 (가장 가까운 적 머리 ${x.cx.eD}칸, 길이 ${x.cx.eL}) → ${x.death10 ? `죽음 ${dd(x.death10)}` : '살아남음'}`;
    case 'gather': return `${where}: 왕까지 거리 ${x.d0} → 최소 ${x.dMin} (${x.turns}턴)${x.death ? `, 가는 길에 죽음 ${dd(x.death)}` : ''}`;
    case 'pocket': return `${where}: ${x.ex ? '한입' : '못 먹음'}, ${x.splitNext ? `분열(새끼 L${x.childLen})` : '분열 없음'}, 30라운드 뒤 가족 길이 변화 ${x.fam30}`;
    case 'tg': return `${where}: ${x.tgx ? '위협 칸으로 감(tgx)' : '피함(tg)'}, 적 머리 경로 ${x.cx.eP < 99 ? x.cx.eP : '>5'}칸 · 맨해튼 ${x.cx.eD}칸(길이 ${x.cx.eL}) → ${x.death2 ? `박힘 ${dd(x.death2)}` : '2라운드 안 박히지 않음'}`; // stack4
    case 'escsplit2': return `${where}: ${x.corn ? '몰림' : '몰림 아님'}, 꼬리-적 머리 ${x.tailE ?? '?'}칸, 새끼 L${x.childLen || '?'} → ${x.childDeath ? `새끼 죽음 ${dd(x.childDeath)}` : '새끼 생존'}, 10라운드 뒤 몸 ${x.famAlive10 ? '생존' : '전멸'}, 30라운드 뒤 몸 길이 변화 ${x.fam30}`; // stack4
    case 'px': return `${where}: ${x.pxx ? '붐비는 출구로 넘음(pxx)' : '피함(px)'} → ${x.death0 ? `그 턴 사망 ${dd(x.death0)}` : '그 턴 생존'}`; // stack4
    case 'gx': return `${where}: gx ${x.turns}턴 (r${x.r}–r${x.r1}) → ${x.death ? `죽음 ${dd(x.death)}` : '끝까지 생존'}`; // stack4
    case 'k2': return `${where}: #${x.target}(L${x.tLen})에게 두 번째 단계 희생 → ${x.ex ? `진주 ${x.drops}개 중 최종 왕 계보 ${x.eatLine || 0}, 우리 ${x.eatOwn}, 상대 ${x.eatEnemy}` : '그 턴에 죽지 않음'}${x.tRank1 === 0 ? '; 지목 아군이 팀 최장 아님' : ''}${x.tDeath ? `; 지목 아군 ${dd(x.tDeath)}에 사망` : ''}`; // cand-conv2
    case 'kch': return `${where}: 보류 ${x.turns}턴 (r${x.r}–r${x.r1}) → ${x.fedKc ? '뒤에 후보에게 희생' : x.death ? `죽음 ${dd(x.death)}` : '끝까지 생존'}`; // cand-conv2
    case 'k2g': return `${where}: 끌림 ${x.turns}턴 (r${x.r}–r${x.r1}) → ${x.fed ? `표식 희생(${x.fed}), 계보가 먹은 진주 ${x.fedLine}` : x.death ? `죽음 ${dd(x.death)}` : x.onLine ? '스스로 최종 왕 계보' : '끝까지 생존(계보 밖)'}`; // cand-conv2
    case 'frag': return `${where}: 조각 L${x.childLen || '?'} → ${x.fed ? `분열 ${x.fedAge}라운드 뒤 아군을 먹임(${x.fed})` : x.childDeath ? `조각 죽음 ${dd(x.childDeath)}, 30라운드 안 먹은 진주 ${x.eat30}` : `30라운드 생존, 먹은 진주 ${x.eat30}`}${x.sit ? '' : ' (설계 밖: 부모가 팀 최장이거나 적 머리가 시야 안)'}`;
    case 'grab': return `${where}: 진주 (${x.px},${x.py}), 우리 머리 ${x.ourD}칸 · 상대 머리 ${x.enemyD}칸, ${x.drop ? `${x.headon ? '박치기' : x.dropOurs ? '우리 팀 사망' : '상대 사망'} ${x.dropAge}라운드 뒤` : x.natural ? '자연 진주(오인)' : '이미 없음'} → ${x.side === 'us' ? '우리가 먹음' : x.side === 'them' ? '상대가 먹음' : '아무도 안 먹음'}${x.delay !== null && x.delay !== undefined ? ` (${x.delay}라운드 뒤)` : ''}, 표식 ${x.turns}턴`;
    case 'bsplit': return `${where}: 조각 L${x.childLen || '?'} → ${x.childDeath ? `조각 죽음 ${dd(x.childDeath)}` : '30라운드 생존'}, 10·30라운드 안 먹은 진주 ${x.eat10 ?? '?'}·${x.eat30 ?? '?'}${x.fed ? `, 분열 ${x.fedAge}라운드 뒤 아군을 먹임(${x.fed})` : ''}${x.sit ? '' : ' (설계 밖: 실제 판본이 Schooltime b가 아님)'}`; // cand-mapid
    case 'mapid': return `${x.opp} · ${x.map} · 게임 ${x.game}: 정답 ${x.truth}, 첫 결정 ${x.call || '없음'} (r${x.r}) · 결정 ${x.decided}/${x.procs}, 틀림 ${x.wrong}, none ${x.none}${(x.bad || []).length ? ' · ' + x.bad.slice(0, 4).map(b => `#${b.id}(태어남 r${b.born}) r${b.r} ${b.tag}`).join(', ') : ''}`; // cand-mapid
    case 'csplit': case 'fguard': case 'cov': return caseLine5(x, where, dd);                              // stack5
    case 'floor': case 'kcap': return caseLine7(x, where, dd);                                             // stack7
    case 'px2': case 'fp': case 'cl': case 'ce': return caseLine8(x, where);                                // stack8
    default: return where;
  }
}

function report(A, B, opts) {
  const L = [];
  const title = opts.title || '구현 적용 확인';
  L.push(`# ${title}`, '');
  L.push(`- 대상: \`${opts.poolA}\` ${A.games}판${B ? ` · 비교: \`${opts.poolB}\` ${B.games}판` : ''}`);
  L.push(`- 기준(사용자 규칙 2026-09-30): 승률이 아니라, 봇에 구현한 기능이 이 상대들에게 실제로 발동하고 의도대로 작동했는지를 본다.`);
  L.push(`- "의도대로"의 정의: 모이기=왕 3칸 안까지 가거나 희생까지 함 · 희생=떨군 진주 절반 이상을 우리 팀이 먹고 상대는 못 먹음 · 한입=2턴 안 분열하고 30라운드 뒤 가족 길이가 줄지 않음 · 탈출 분열=10라운드 뒤 몸이 살아 있음 · 정책 분열=새끼 30라운드 생존 · 탈출 질주·위협 피하기=10라운드 뒤 몸 생존 · 포털=3라운드 뒤 몸 생존 · 돌진=충돌 성사, 잡은 길이 ≥ 우리, 두 몸의 진주를 우리가 더 먹음 · 먹이 질주=진주 먹음.`);
  L.push(`- "몸"은 그 드래곤과 그 뒤 분열로 태어난 자손 전체다. 통로 고리처럼 몸을 새끼에게 넘기며 버티는 경우를 손실로 세지 않기 위해서다.`);
  if (['frag', 'grab'].some(k => (A.by[k] || []).length || (B && (B.by[k] || []).length)))
    L.push(`- stack2의 "의도대로": 조각 떼기=조각이 30라운드 살며 진주를 1개 이상 먹거나, 나중에 희생(feed·conv)으로 아군을 먹임 · 새 사망 진주 줍기=표적이 된 사망 진주(진주 하나가 한 건)를 우리 팀이 먹음(자연 진주로 오인했거나 이미 없던 표적은 판정에서 뺌).`);
  if (['tg', 'escsplit2', 'px', 'gx'].some(k => (A.by[k] || []).length || (B && (B.by[k] || []).length)))
    L.push(`- stack4의 "의도대로": tg=표식 턴 뒤 2라운드 안에 박히지 않음 · 몰렸을 때 분열=10라운드 뒤 몸이 살아 있음(보존율은 효과 줄) · px=그 턴에 우리 드래곤과 부딪혀 죽지 않음 · gx=그 드래곤의 몸(그 드래곤과 뒤에 태어난 자손)이 끝까지 삶(사용자 결정 17:16: 생존은 몸으로 판정, 드래곤 자체 생존은 참고).`);
  if (['mapid', 'bsplit'].some(k => (A.by[k] || []).length || (B && (B.by[k] || []).length)))
    L.push(`- cand-mapid의 "의도대로": Schooltime b 초반 분열(bsp)=떼어 낸 조각(새 유닛)이 10라운드 뒤 살아 있음 · 지도·판본 인식=그 판에서 1개 이상의 프로세스가 판본까지 결정했고, 결정한 프로세스(마지막 표식 기준)가 모두 정답 지도·판본을 댐. 정답 판본은 로컬이면 지도 파일 이름, 온라인이면 기보의 자연 생성(한쪽 판본에서만 생성하는 칸)으로 정하고, 끝까지 가릴 수 없던 판은 뺀다. 지도별 줄의 이름 뒤 a·b·?가 정답 판본이다.`);
  if (['csplit', 'fguard', 'cov'].some(k => (A.by[k] || []).length || (B && (B.by[k] || []).length)))
    L.push(`- stack5의 "의도대로": 덮기 분열=새끼가 30라운드 안에 자연 진주를 1개 이상 먹음(생존은 효과 줄) · 샘 지킴=목표 샘 3걸음 안에 든 뒤 30라운드 동안 그 무리(실제 샘, 목표에서 3걸음 안)에 생긴 자연 진주의 85% 이상을 우리가 먹음(도착하지 않았거나 진주가 생기지 않은 목표는 뺌) · 영토 덮기 끌림=20라운드 안에 우리 영토 자연 진주를 먹음. 게이트와 가설 수준 지표는 맨 뒤 stack5 절.`);
  if (['floor', 'kcap'].some(k => (A.by[k] || []).length || (B && (B.by[k] || []).length)))           // stack7
    L.push(`- stack7의 "의도대로": 수 바닥 분열(floor)=새끼가 30라운드 뒤 살아 있음 · 왕 길이 상한 분열(kcap)=새끼가 10라운드 뒤 살아 있음(부모 생존은 효과 줄). 판이 먼저 끝나면 생존으로 센다. 게이트, 저수 에피소드, 지도 가르기는 맨 뒤 stack7 절.`);
  L.push('');
  L.push('## 요약', '');
  L.push(`| 기능 | 발동(판당) | 의도대로 | ${B ? '비교: 발동(판당) | 비교: 의도대로 |' : ''}`);
  L.push(`|---|---:|---:|${B ? '---:|---:|' : ''}`);
  const kinds = [...new Set([...ORDER, ...Object.keys(A.by), ...(B ? Object.keys(B.by) : [])])].filter(k => (A.by[k] || []).length || (B && (B.by[k] || []).length));
  for (const k of kinds) {
    const a = A.by[k] || [], b = B ? B.by[k] || [] : [];
    L.push(`| ${LABEL[k] || k} | ${a.length} (${f1(a.length / Math.max(1, A.games))}) | ${okRate(a)} | ${B ? `${b.length} (${f1(b.length / Math.max(1, B.games))}) | ${okRate(b)} |` : ''}`);
  }
  const hl = (S) => `턴 ${S.health.turns}, 표식 누락 ${S.health.turns - S.health.labelled}, degraded ${S.health.degraded}, 시간 초과 사망 ${S.health.fault}, 한 턴 최대 명령 수 ${(S.health.maxInstr / 1e6).toFixed(1)}M(한도 100M), 80M 넘은 턴 ${S.health.over80}, 탐색 깊이 5 미만 ${pct(S.health.lowDepth, S.health.moveTurns)}`;
  L.push('', `- 건강: ${hl(A)}${B ? `\n- 비교 건강: ${hl(B)}` : ''}`);
  L.push(`- 표식 턴 수: 왕에게 모이기(g) ${A.counts.g}턴 · 끝판(late) ${A.counts.late}턴 · 돌진 신뢰(T, 탈출 끔) ${A.counts.T}턴, 그 직후 박혀 죽음 ${A.counts.trustRammed}${A.counts.ks ? ` · 후반 왕 보호(ks) ${A.counts.ks}턴` : ''}${A.counts.ks2 ? ` · 끝판 왕 질주 사정 보호(ks2) ${A.counts.ks2}턴` : ''}`, '');
  const hy = (S) => {
    const h = S.hyp, r = S.hypR500, n = Math.max(1, S.games), n5 = Math.max(1, S.gamesR500);
    return [pct(h.b3Ram || 0, h.b3Elig || 0) + ` (${h.b3Ram || 0}/${h.b3Elig || 0}턴)`,
      `${f1((r.sac250Len || 0) / n5)}칸 (${f1((r.sac250N || 0) / n5)}회), 진주 우리 ${pct(r.sac250Own || 0, r.sac250Drops || 0)} · 상대 ${pct(r.sac250Enemy || 0, r.sac250Drops || 0)}`,
      `${f1((r.king450Len || 0) / n5)}칸 (판당 ${((r.king450N || 0) / n5).toFixed(2)}회)`,
      `${pct(h.kingExp400 || 0, h.kingT400 || 0)} (${h.kingExp400 || 0}/${h.kingT400 || 0}턴)`,
      `판당 ${((h.kingRam400N || 0) / n).toFixed(3)}회 (${h.kingRam400N || 0}건, ${h.kingRam400Len || 0}칸)`];
  };
  // (stack2) H3 dragons at r400 and splits in r350-449, H2 territory, H5 exchange and enemy-death pearls; 500-round maps
  const hy2 = (S) => {
    const r = S.hypR500, n5 = Math.max(1, S.gamesR500), v = k => r[k] || 0;
    return [`${f1(v('u400') / Math.max(1, v('g400')))}마리 (${v('g400')}판)`, `${f1(v('split350') / n5)}회`,
      `${pct(v('natOwnThem'), v('natOwnUs') + v('natOwnThem') + v('natOwnLeft'))} (우리 ${pct(v('natOwnUs'), v('natOwnUs') + v('natOwnThem') + v('natOwnLeft'))})`,
      `우리 ${f1(v('xchUs') / n5)} 대 상대 ${f1(v('xchThem') / n5)} (${f1(v('xchN') / n5)}회) · 박힌 교환의 우리 몫 ${pct(v('xchRUs'), v('xchRUs') + v('xchRThem'))} (${v('xchRN')}회)`,
      `${f1(v('eDropUs') / n5)}개`];
  };
  const ha = hy(A), hb = B ? hy(B) : null, ha2 = hy2(A), hb2 = B ? hy2(B) : null;
  L.push('## 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)', '');
  L.push(`| 지표 | 상위권 승자 | 이번 | ${B ? '비교 |' : ''}`, `|---|---|---|${B ? '---|' : ''}`);
  L.push(`| B3: 길이 ≤4 조각이 바로 옆의 같거나 긴 적 머리를 박은 비율 | 43.6% | ${ha[0]} | ${B ? hb[0] + ' |' : ''}`);
  L.push(`| 250라운드 뒤 희생한 길이(500라운드형 지도, 판당), 그 진주를 먹은 쪽 | 214칸, 우리 93% | ${ha[1]} | ${B ? hb[1] + ' |' : ''}`);
  L.push(`| 450라운드 뒤 잃은 왕 길이(500라운드형 지도, 판당) | 0.3–0.7칸 | ${ha[2]} | ${B ? hb[2] + ' |' : ''}`);
  L.push(`| ks2: 400라운드 뒤 우리 왕(≥8)이 적 머리의 질주 사정(맨해튼 ≤ 길이−1, 최대 7) 안에 있던 턴의 비율 | – | ${ha[3]} | ${B ? hb[3] + ' |' : ''}`);
  L.push(`| ks2: 400라운드 뒤 우리 왕이 적 머리에 박혀 죽은 수(모든 지도) | – | ${ha[4]} | ${B ? hb[4] + ' |' : ''}`);
  L.push(`| H3: 400라운드에 살아 있는 우리 드래곤 수(500라운드형 지도, 400라운드까지 간 판) | 27.4마리 | ${ha2[0]} | ${B ? hb2[0] + ' |' : ''}`);
  L.push(`| H3: 350–449라운드 우리 분열 수(500라운드형 지도, 판당; 탈출 분열 포함) | 67.2회 | ${ha2[1]} | ${B ? hb2[1] + ' |' : ''}`);
  L.push(`| H2: 우리 영토 자연 진주를 상대가 먹은 비율(500라운드형 지도) | 11% (우리 85%) | ${ha2[2]} | ${B ? hb2[2] + ' |' : ''}`);
  L.push(`| H5: 박치기 교환 두 몸의 진주(500라운드형 지도, 판당), 박힌 교환의 우리 몫 | 우리 92.8 대 상대 78.1 · 41% | ${ha2[3]} | ${B ? hb2[3] + ' |' : ''}`);
  L.push(`| H5: 우리가 먹은 적 사망 진주(500라운드형 지도, 판당) | 49개 | ${ha2[4]} | ${B ? hb2[4] + ' |' : ''}`);
  L.push('', '상위권 승자 값은 `research/observations/top-decisions-large.md`(B3)와 `top-mass-spending.md`(희생·왕)에서 왔다. 정의가 조금 다르다(여기서 인접은 격자 거리 1, 희생은 빈 이웃이 있는 자해 사망).');
  L.push('H2·H3·H5 행의 상위권 승자 값은 `top-mass-spending.md`(3.1·4.2·5.1·2.1절, 6절 흐름표)에서 왔고, merge2는 4.3마리 · 19.8회 · 59% · 6.8 대 19.9, 22% · 6개다. 영토 비율의 분모는 우리 영토에 나온 자연 진주(시작 진주 포함, 끝에 남은 것 포함)다.', '');
  for (const k of kinds) {
    const a = A.by[k] || []; if (!a.length) continue;
    L.push(`## ${LABEL[k] || k}`, '');
    L.push(`- 이번: ${effectLine(k, a)}`);
    if (B && (B.by[k] || []).length) L.push(`- 비교: ${effectLine(k, B.by[k])}`);
    const group = (field, order) => {
      const m = new Map(); for (const x of a) { const v = x[field]; if (!m.has(v)) m.set(v, []); m.get(v).push(x); }
      const keys = order ? order.filter(v => m.has(v)) : [...m.keys()].sort();
      return keys.map(v => `${v} ${m.get(v).length}회 ${okRate(m.get(v))}`).join(' · ');
    };
    L.push(`- 상대별: ${group('opp')}`);
    L.push(`- 지도별: ${group('map')}`);
    L.push(`- 국면별: ${group('ph', PHASES.map(p => p[2]))}`);
    const fails = a.filter(x => x.ok === 0);
    if (fails.length) {
      L.push('', `실패 사례 (${fails.length}건 중 ${Math.min(opts.cases, fails.length)}건, 기보 확인용):`);
      const pick = []; const seen = new Set();
      for (const x of fails) { const s = x.opp + '|' + x.map; if (!seen.has(s)) { seen.add(s); pick.push(x); } }
      for (const x of fails) if (pick.length < opts.cases && !pick.includes(x)) pick.push(x);
      for (const x of pick.slice(0, opts.cases)) L.push(`- ${caseLine(x)}`);
    }
    L.push('');
  }
  L.push(...stack4Section(A, B, opts));
  L.push(...mapidSection(A, B));
  L.push(...stack5Section(A, B, opts));                                                                  // stack5
  L.push(...conv2Section(A, B, opts));                                                                   // cand-conv2
  L.push(...stack7Section(A, B, opts));                                                                  // stack7
  L.push(...stack8Section(A, B, opts));                                                                  // stack8
  return L.join('\n');
}

// cand-mapid: map and layout recognition by map and true layout (only when a pool carries " map=" tags)
function mapidSection(A, B) {
  const L = [];
  if (!['mapid', 'bsplit'].some(k => (A.by[k] || []).length || (B && (B.by[k] || []).length))) return L;
  L.push('## 지도·판본 인식 상세 (cand-mapid)', '');
  for (const [name, S] of [['이번', A], ['비교', B]]) {
    const xs = S ? S.by.mapid || [] : []; if (!xs.length) continue;
    const by = new Map(); for (const x of xs) { if (!by.has(x.map)) by.set(x.map, []); by.get(x.map).push(x); }
    const s = (a, f) => a.reduce((t, x) => t + (x[f] || 0), 0);
    L.push(`${name} (${xs.length}판):`, '', '| 지도 정답 판본 | 판 | 맞음 | 첫 결정 정답 | 시작 드래곤 0라운드 결정 (정답) | 프로세스 | 결정 (틀림) | 가족만 | 모름 | none | 결정까지 최대 |', '|---|---:|---:|---:|---|---:|---|---:|---:|---:|---:|');
    for (const [m, a] of [...by].sort()) {
      const kn = a.filter(x => x.ok !== null), d = a.flatMap(x => x.delays || []);
      L.push(`| ${m} | ${a.length} | ${okRate(a)} | ${pct(kn.filter(x => x.call === x.truth).length, kn.length)} | ${s(a, 'init0')}/${s(a, 'init')} (${s(a, 'init0Right')}) | ${s(a, 'procs')} | ${s(a, 'decided')} (${s(a, 'wrong')}) | ${s(a, 'fam')} | ${s(a, 'unk')} | ${s(a, 'none')} | ${d.length ? Math.max(...d) : '–'} |`);
    }
    const loc = xs.filter(x => x.spawnTruth !== null && x.spawnTruth !== undefined);
    if (loc.length) {
      const agree = loc.filter(x => x.spawnTruth === x.truth.split('/')[1]).length, undec = loc.filter(x => x.spawnTruth === '?').length;
      L.push('', `- 정답 판본을 정하는 두 방법 대조(로컬 판, 지도 파일 = 정답): 기보의 자연 생성으로 정한 판본이 파일과 같음 ${agree}/${loc.length}, 가릴 수 없음 ${undec}, 다름 ${loc.length - agree - undec}. 온라인 판은 자연 생성 방법만 쓴다.`);
    }
    L.push('');
  }
  // bsplit's hypothesis-level indicators: Schooltime games' economy by true layout, both pools (medians [p25, p75] per game)
  const qq = (a, p) => { const s2 = a.slice().sort((u, v) => u - v); return s2.length ? s2[Math.min(s2.length - 1, Math.floor(p * s2.length))] : '–'; };
  const md = a => `${qq(a, 0.5)} [${qq(a, 0.25)}, ${qq(a, 0.75)}]`;
  const econRows = [];
  for (const [name, S] of [['이번', A], ['비교', B]]) for (const lay of ['a', 'b']) {
    const a = S ? (S.econ || []).filter(x => x.layout === lay) : []; if (!a.length) continue;
    econRows.push(`| ${name} | ${lay} | ${a.length} | ${md(a.map(x => x.u50))} | ${md(a.map(x => x.u100))} | ${md(a.map(x => x.nat100))} | ${pct(a.filter(x => x.elim).length, a.length)} | ${md(a.map(x => x.G))} | ${f1(avg(a.map(x => x.bsp)))} |`);
  }
  if (econRows.length) {
    L.push('### Schooltime 판의 경제 (bsp의 가설 수준 지표, 정답 판본별)', '', '| 묶음 | 판본 | 판 | 드래곤 수 r50 | r100 | r0–99 자연 진주 먹음 | 전멸당함 | 끝 최장(전멸 0) | 판당 bsp 분열 |', '|---|---|---:|---|---|---|---:|---|---:|', ...econRows);
    L.push('', '- 기준값(`research/experiments/cand-mapid.md`, 웨이브 전에 적음): b에서 드래곤 수 r50 중앙 ≥ 6, r0–99 자연 진주 중앙 ≥ 14. 우리 merge2 계열 b 29판은 3 · 9, 떼 계열(swarm8·px) b 14판은 6 · 14, 상위권 b 승자는 8 · 32다. a는 bsp가 켜지지 않는 대조군이다.', '');
  }
  return L;
}

// stack4 hypothesis metrics (tag-independent; any set). Definitions and merge2 baselines: research/observations/mech-merge2-failures.md
// (2.1-2.2 rams on L>=6 by decision-moment class, 1.4 cornered responses, 5.2 portal-step deaths, 4.2 gathering deaths).
function stack4Section(A, B, opts) {
  const L = [], z = () => ({ games: 0, rams: [], corn: [], pstep: [], pStepN: 0, pStepOwn: 0, pStepOwnDesp: 0, gEp: 0, gDeath: 0, gOwn: 0, gxN: 0, sxN: 0,
    l6T: 0, l6P4: 0, l6M4: 0, kT: 0, kP4: 0, kP7: 0, kMT: 0, kM7: 0 });
  const merged = S => { const t = z(); for (const s of Object.values(S.ext4 || {})) { for (const k of Object.keys(t)) t[k] = Array.isArray(t[k]) ? t[k].concat(s[k]) : t[k] + s[k]; } return t; };
  const pools = [[`이번 \`${opts.poolA}\``, A]].concat(B ? [[`비교 \`${opts.poolB}\``, B]] : []);
  const rows = []; // [label, ext]
  for (const [name, S] of pools) {
    rows.push([name, merged(S)]);
    const sets = Object.keys(S.ext4 || {}); if (sets.length > 1) for (const k of sets) rows.push([`· ${k}`, S.ext4[k]]);
  }
  const per = (a, n) => (a / Math.max(1, n)).toFixed(2);
  L.push('## stack4 가설 지표 (표식과 상관없이 기보에서 직접 잰 값; 어느 세트끼리도 비교 가능)', '');
  L.push('정의는 `research/observations/mech-merge2-failures.md`(실패 사례 연구)와 같다. 박힘의 분류는 우리 드래곤의 마지막 결정 순간 기준이고 우선순위대로 매긴다: 막 태어남 → 비이동 표식 → 못 봄(결정 뒤 태어남, 8칸 밖, 7×7 시야 밖) → 도달 오차(가해자 걸음 > 보이는 마디로 추정한 사정: 길에서 진주, 꼬리 안 보이는 L5 이상) → 값 반영(v<0) → 사각(결정 순간 막혀 있던 칸을 지나거나 그 칸에 우리 새 머리) → 원인 미상.', '');
  L.push('| 모집단 | 판 | L≥6 박힘(판당) | 가해자 질주 | 사각(판당) | 도달 오차(판당) | 못 봄 | 값 반영 v<0 | 원인 미상 | 400R 뒤 왕 박힘 중 값 ≥0 (210판당) | 넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외(판당) | 모이기 뒤 우리 드래곤과 부딪힌 죽음 / 모든 죽음 (210판당) |');
  L.push('|---|---:|---|---:|---|---|---:|---:|---:|---|---|---|');
  L.push('| 기준: merge2 3웨이브(연구) | 210 | 248 (1.18) | 71% | 34 (0.16) | 45 (0.21) | 37 | 98 | 24 | 9/11 (9.0) | 55 (0.26; 필사 28) | 30/48 (30.0) |');
  for (const [name, s] of rows) {
    const R = s.rams, cls = R.map(ramCls), n = s.games, c = p => cls.filter(x => x.startsWith(p)).length;
    const k4 = R.filter(x => x.king && x.r >= 400), k4v = k4.filter(x => (vOf(x.text) ?? 0) >= 0);
    L.push(`| ${name} | ${n} | ${R.length} (${per(R.length, n)}) | ${pct(R.filter(x => x.killerSteps >= 2).length, R.length)} | ${c('blind')} (${per(c('blind'), n)}) | ${c('reach')} (${per(c('reach'), n)}) | ${c('unseen')} | ${c('priced')} | ${c('unpriced')} | ${k4v.length}/${k4.length} (${f1(k4v.length * 210 / Math.max(1, n))}) | ${s.pStepOwn} (${per(s.pStepOwn, n)}; 필사 ${s.pStepOwnDesp}) | ${s.gOwn}/${s.gDeath} (${f1(s.gOwn * 210 / Math.max(1, n))}) |`);
  }
  L.push('', '- 사전 등록 기준(stack4, `research/experiments/cand-stack4.md`): 사각 판당 ≤0.05 · 도달 오차 판당 ≤0.10 · L≥6 박힘 판당 ≤1.00 · 400라운드 뒤 값 ≥0 왕 박힘 210판에 ≤3 · 넘는 걸음 우리 드래곤 막힘(필사 제외) 판당 ≤0.10 · 모이기 뒤 우리 드래곤과 부딪힌 죽음 210판에 ≤12.');
  for (const [name, s] of rows) if (s.gxN || s.sxN) L.push(`- ${name}: gx 표식 턴 ${s.gxN} · sx(꼬리 거리 규칙이 막은 정책 분열) 턴 ${s.sxN}`);
  L.push('', '### 적 머리의 질주 사정 안에 있던 턴 (경로 거리)', '');
  L.push('사정 = min(적의 실제 길이 − 1, 한도). 그 턴 시작의 판에서 적 머리부터 빈 칸으로만 걷는다(해초와 몸은 막고, 우리 머리가 목표). 맨해튼은 같은 한도의 토러스 맨해튼 거리(해초·몸 무시)이고, 왕 맨해튼 ≤7은 stack3 ks2의 기존 지표(kingExp400)다. 왕 = 팀 최장이고 길이 ≥8, 400라운드부터.', '');
  L.push('| 모집단 | 판 | L≥6 턴 | L≥6 경로 ≤4 | L≥6 맨해튼 ≤4 | 400R 뒤 왕 턴 | 왕 경로 ≤4 | 왕 경로 ≤7 | 왕 맨해튼 ≤7 (kingExp400) |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|');
  const p1 = (a, b) => b ? (100 * a / b).toFixed(1) + '%' : '–';
  for (const [name, s] of rows) L.push(`| ${name} | ${s.games} | ${s.l6T} | ${p1(s.l6P4, s.l6T)} (${s.l6P4}) | ${p1(s.l6M4, s.l6T)} (${s.l6M4}) | ${s.kT} | ${p1(s.kP4, s.kT)} (${s.kP4}) | ${p1(s.kP7, s.kT)} (${s.kP7}) | ${p1(s.kM7, s.kMT)} (${s.kM7}/${s.kMT}) |`);
  L.push('', '### 몰린 턴(길이 ≥6, 한 걸음이 모두 짧은(≤4) 적 머리의 사정 안)의 대응과 몸 길이 보존율', '');
  L.push('| 모집단 | 꼬리 | 대응 | 턴(몰린 턴 중) | 평균 길이 | 몸 길이 보존 +10 | +30 | 드래곤 10라운드 안 죽음 | 몸 10라운드 안 잃음 |', '|---|---|---|---:|---:|---:|---:|---:|---:|');
  L.push('| 기준: merge2(연구) | 전체 | 분열 · 2칸 · 3칸 · 한 걸음 | 52 (15%) · 150 · 60 · 88 | 11.8 · 10.6 · 11.9 · 11.9 | 86% · 76% · 71% · 29% | 77% · 59% · 49% · 26% | 36 · 50 · 15 · 66 | 8 · 30 · 10 · 58 |');
  for (const [name, s] of rows) for (const [tl, pred] of [['전체', () => true], ['4칸 이상', x => x.tailE >= 4]]) {
    const cs = s.corn.filter(pred), by = {};
    for (const x of cs) { const q = by[x.resp] || (by[x.resp] = { n: 0, L: 0, f10: 0, f30: 0, d10: 0, fd10: 0 }); q.n++; q.L += x.L; q.f10 += x.f10; q.f30 += x.f30; q.d10 += x.d10; q.fd10 += x.fd10; }
    for (const k of ['split', 'sprint2', 'sprint3', 'single']) { const q = by[k]; if (!q) continue;
      L.push(`| ${name} | ${tl} | ${{ split: '분열', sprint2: '2칸 질주', sprint3: '3칸 질주', single: '한 걸음' }[k]} | ${q.n} (${pct(q.n, cs.length)}) | ${f1(q.L / q.n)} | ${pct(q.f10, q.L)} | ${pct(q.f30, q.L)} | ${q.d10} | ${q.fd10} |`); }
  }
  // selected replays of the pool under test: the gap classes and the own-blocked portal steps
  const a = rows[0][1];
  for (const [nm, pre] of [['사각', 'blind'], ['도달 오차', 'reach']]) {
    const xs = a.rams.filter(x => ramCls(x).startsWith(pre)); if (!xs.length) continue;
    L.push('', `${nm} 박힘 (${xs.length}건 중 ${Math.min(opts.cases, xs.length)}건, 기보 확인용):`);
    for (const x of xs.slice(0, opts.cases)) L.push(`- ${x.opp} · ${x.map} · 게임 ${x.game} · r${x.r} · 드래곤 #${x.id} L${x.L}: 결정 "${x.text || ''}" → 가해자 #${x.killerId} L${x.killerLenB ?? '?'} ${x.killerSteps}걸음${x.killerAte ? ', 길에서 진주' : ''} (${ramCls(x).split(': ')[1]})`);
  }
  if (a.pstep.length) {
    L.push('', `넘는 걸음에서 우리 드래곤에 막혀 죽음, 필사 제외 (${a.pstep.length}건 중 ${Math.min(opts.cases, a.pstep.length)}건):`);
    for (const x of a.pstep.slice(0, opts.cases)) L.push(`- ${x.opp} · ${x.map} · 게임 ${x.game} · r${x.r} · 드래곤 #${x.id} L${x.L}: v${x.v}${x.blind ? ' PORTAL?' : ''} → ${CAUSE_KO[x.cause] || x.cause}, 막은 우리 드래곤 L${x.otherLen}`);
  }
  L.push('');
  return L;
}

// ---------------------------------------------------------------------------------------------------------------
// stack5 (research/experiments/cand-stack5.md): csplit / F / cov lines and the territory study's hypothesis-level indicators
// (research/observations/top-territory.md 2.3, 3, 6.4; the same definitions as exp/territory-analysis/extract.js)
const R500_5 = new Set(['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma']);
function stack5Sum(games) {
  const S = { byType: {}, byMap: {} };
  const add = (o, t) => {
    o.games = (o.games || 0) + 1;
    for (const f of ['g100', 'u100', 'own', 'ownUs', 'ownThem', 'fo', 'foUs', 'foThem', 'dTrap', 'dRam', 'dAlly', 'dTrap250', 'dRam250', 'dAlly250', 'spare']) o[f] = (o[f] || 0) + (t[f] || 0);
    if (t.vr !== null && t.vr !== undefined) { o.vrS = (o.vrS || 0) + t.vr; o.vrN = (o.vrN || 0) + 1; }
    if (t.fr !== null && t.fr !== undefined) { o.frS = (o.frS || 0) + t.fr; o.frN = (o.frN || 0) + 1; }
    if (t.err) o.err = (o.err || 0) + 1;
  };
  for (const g of games) { const t = g.t5 || {}, ty = R500_5.has(g.map) ? '500' : 'elim'; add(S.byType[ty] = S.byType[ty] || {}, t); add(S.byMap[g.map] = S.byMap[g.map] || {}, t); }
  return S;
}
function effectLine5(k, xs) {
  const ex = xs.filter(x => x.ex), sum = (a, f) => a.reduce((s, x) => s + (x[f] || 0), 0);
  if (k === 'csplit') {
    const td = {}; for (const x of ex) if (x.childDeath) td[CAUSE_KO[x.childDeath.cause]] = (td[CAUSE_KO[x.childDeath.cause]] || 0) + 1;
    const ty = t => ex.filter(x => (R500_5.has(x.map) ? '500' : 'elim') === t);
    const e5 = ty('500'), ee = ty('elim');
    return `분열 ${pct(ex.length, xs.length)} · 설계 상황(부모가 팀 최장 ≥8이 아님) ${pct(xs.filter(x => x.sit).length, xs.length)} · 적 머리가 시야에 있을 때 ${pct(xs.filter(x => x.view).length, xs.length)} · 부모가 스스로 최장이라 믿음(k) ${pct(xs.filter(x => x.kingTag).length, xs.length)}` +
      ` · 새끼 30라운드 안 자연 진주 ≥1 ${pct(ex.filter(x => x.nat30 >= 1).length, ex.length)} (500형 ${pct(e5.filter(x => x.nat30 >= 1).length, e5.length)} · 전멸형 ${pct(ee.filter(x => x.nat30 >= 1).length, ee.length)}; 기준 ≥45%)` +
      ` · 새끼 30라운드 생존 ${pct(ex.filter(x => x.childAlive30).length, ex.length)} (500형 ${pct(e5.filter(x => x.childAlive30).length, e5.length)} · 전멸형 ${pct(ee.filter(x => x.childAlive30).length, ee.length)}; 기준 ≥30%)` +
      ` · 새끼가 우리 영토에서 태어남 ${pct(ex.filter(x => x.bornOwn).length, ex.length)} · 새끼 30라운드 안 자연 진주 평균 ${f1(avg(ex.map(x => x.nat30)))} · 30라운드 안 죽은 원인: ${Object.entries(td).map(([a, b]) => a + ' ' + b).join(', ') || '없음'}`;
  }
  if (k === 'fguard') {
    const n = sum(ex, 'spN');
    return `목표 ${xs.length}개(표식 턴 ${sum(xs, 'turns')}) · 설계 상황 ${pct(xs.filter(x => x.sit).length, xs.length)} (실제 샘 ${pct(xs.filter(x => x.fnt).length, xs.length)}, 우리 영토 ${pct(xs.filter(x => x.own).length, xs.length)}, 처음에 다른 우리 머리 3걸음 안 없음 ${pct(xs.filter(x => !x.guarded0).length, xs.length)}; 기준 ≥80%)` +
      ` · 3걸음 안 도착 ${pct(ex.length, xs.length)} · 도착 뒤 30라운드 그 무리 자연 진주 ${n}개 중 우리 ${pct(sum(ex, 'spUs'), n)} · 상대 ${pct(sum(ex, 'spThem'), n)} (합산 기준 ≥85%) · 처음 거리 평균 ${f1(avg(xs.map(x => x.d0)))}`;
  }
  return `턴 ${xs.length} · 20라운드 안 우리 영토 자연 진주 먹음 ${okRate(xs)}`;
}
function caseLine5(x, where, dd) {
  if (x.k === 'csplit') return `${where}: 새끼 L${x.childLen || '?'}${x.view ? ', 적 머리 시야 안' : ''} → ${x.childDeath ? `새끼 죽음 ${dd(x.childDeath)}` : '30라운드 생존'}, 30라운드 안 자연 진주 ${x.nat30 ?? 0}${x.sit ? '' : ' (설계 밖: 부모가 팀 최장 ≥8)'}`;
  if (x.k === 'fguard') return `${where}: 샘 (${x.ax},${x.ay}) 처음 거리 ${x.d0}${x.sit ? '' : ` (설계 밖: 실제 샘 ${x.fnt}, 우리 영토 ${x.own}, 다른 머리 ${x.guarded0})`} → ${x.ex ? `r${x.rArr} 도착, 30라운드 무리 진주 ${x.spN}개 중 우리 ${x.spUs} · 상대 ${x.spThem}` : '도착 못 함'}`;
  return where;
}
// cand-conv2: lineage metrics (the final king's line) of our labelled conversions and of the team, with the pre-registered gates
// of research/experiments/cand-conv2.md. Shown when a conv2 tag is present or with --lineage.
function conv2Section(A, B, opts) {
  const L = [];
  const has = S => ['k2', 'k2g', 'kch'].some(k => (S.by[k] || []).length) || ['conv', 'feed'].some(k => (S.by[k] || []).some(x => x.kc));
  if (!has(A) && !(B && has(B)) && !opts.lineage) return L;
  const P = [['이번', A]].concat(B ? [['비교', B]] : []);
  L.push('## cand-conv2: 희생 질량이 최종 왕 계보로 가는가 (kc · k2) 게이트와 가설 수준 지표', '');
  L.push('- 기준값은 `research/experiments/cand-conv2.md`(온라인 전)에서, 상위권·우리 봇 값은 `research/observations/conversion-chain.md`에서 왔다. 최종 왕 계보 = 끝의 최장 드래곤을 부모 쪽으로 따라간 드래곤들이고, 계보 드래곤 i는 태어난 라운드부터 계보 드래곤 i+1이 태어난 라운드 전까지를 맡는다. "계보 몫" = 떨어진 진주 가운데 그 창 안의 계보 드래곤이 먹은 비율.', '');
  const lab = (S, k, f) => (S.by[k] || []).filter(f);
  const line = xs => { const ex = xs.filter(x => x.ex), d = ex.reduce((s, x) => s + x.drops, 0); return `${xs.length}건 · 진주 ${d} → 계보 ${pct(ex.reduce((s, x) => s + (x.eatLine || 0), 0), d)} · 상대 ${pct(ex.reduce((s, x) => s + x.eatEnemy, 0), d)} · 지목이 그 순간 계보 ${pct(xs.filter(x => x.tOnLine).length, xs.length)} · 지목이 그 순간 팀 최장 ${pct(xs.filter(x => x.tRank1 === 1).length, xs.filter(x => x.tRank1 !== null && x.tRank1 !== undefined).length)}`; };
  L.push(`| 항목 | ${P.map(p => p[0]).join(' | ')} |`, `|---|${P.map(() => '---|').join('')}`);
  L.push(`| conv (kc 표식) | ${P.map(p => line(lab(p[1], 'conv', x => x.kc))).join(' | ')} |`);
  L.push(`| conv (kc 없음) | ${P.map(p => line(lab(p[1], 'conv', x => !x.kc))).join(' | ')} |`);
  L.push(`| feed (kc 표식) | ${P.map(p => line(lab(p[1], 'feed', x => x.kc))).join(' | ')} |`);
  L.push(`| feed (kc 없음) | ${P.map(p => line(lab(p[1], 'feed', x => !x.kc))).join(' | ')} |`);
  L.push(`| k2 | ${P.map(p => line(lab(p[1], 'k2', () => true))).join(' | ')} |`);
  const r = (S, f) => { const o = (S.c2 || {}).r500 || {}; return f(o); };
  L.push(`| 500라운드형(500까지 간 판) 판 | ${P.map(p => r(p[1], o => o.g || 0)).join(' | ')} |`);
  L.push(`| k2 발동(판당, 500형 끝까지 간 판) | ${P.map(p => { const n = r(p[1], o => o.g || 0); const k = (p[1].by.k2 || []).filter(x => ['Autarky', 'Portals', 'Schooltime', 'Slithery Fight', 'Trauma'].includes(x.map)).length; return `${k} (${f1(k / Math.max(1, n))})`; }).join(' | ')} |`);
  L.push(`| r300 뒤 우리 희생 진주의 계보 몫 (상위권 승자 24%) | ${P.map(p => r(p[1], o => `${pct(o.sac300Line || 0, o.sac300Drops || 0)} (${o.sac300Line || 0}/${o.sac300Drops || 0})`)).join(' | ')} |`);
  L.push(`| r350 뒤 계보가 먹은 우리 희생 진주(판당; 상위권 승자 21.4, merge2 3.8) | ${P.map(p => r(p[1], o => f1((o.lineSac350 || 0) / Math.max(1, o.g || 0)))).join(' | ')} |`);
  L.push(`| r400 계보 밖 길이 ≥8 드래곤(판당) · 가족이 계보 밖에서 끝까지 삶 · 계보에 진주를 줌 | ${P.map(p => r(p[1], o => `${f1((o.mid400 || 0) / Math.max(1, o.g || 0))} · ${pct(o.mid400Alive || 0, o.mid400 || 0)} (끝 길이 ${f1((o.mid400AliveLen || 0) / Math.max(1, o.mid400Alive || 0))}) · ${pct(o.mid400Fed || 0, o.mid400 || 0)}`)).join(' | ')} |`);
  L.push(`| 끝 왕 길이(500형 끝까지 간 판, 판정에 쓰지 않음) | ${P.map(p => r(p[1], o => f1((o.king || 0) / Math.max(1, o.g || 0)))).join(' | ')} |`);
  L.push('');
  return L;
}

function stack5Section(A, B, opts) {
  const L = [];
  const on = ['csplit', 'fguard', 'cov'].some(k => (A.by[k] || []).length || (B && (B.by[k] || []).length));
  if (!on && !opts.territory) return L;
  const P = [['이번', A]].concat(B ? [['비교', B]] : []);
  L.push('## stack5: 영토 덮기 (csplit · F · cov) 게이트와 가설 수준 지표', '');
  L.push('- 기준값은 `research/experiments/cand-stack5.md`(웨이브 전)에서, 상위권 승자(TW) 값과 merge2 값은 `research/observations/top-territory.md`에서 왔다. 정의는 영토 연구의 `exp/territory-analysis/extract.js`와 같다(영토 = 시작 몸에서 더 가까운 팀의 칸, 샘 = 그 판 판본 파일의 평균 간격 ≤12, 보로노이 = 용량 1/평균 간격 가중, 거리 = 지도 위 이동 거리, 몸은 무시).', '');
  const cs = S => { const xs = S.by.csplit || [], ex = xs.filter(x => x.ex), r5 = xs.filter(x => R500_5.has(x.map) && x.r < 250), g5 = S.t5.byType['500'] ? S.t5.byType['500'].games : 0;
    return { n: xs.length, per5: g5 ? r5.length / g5 : 0, sit: pct(xs.filter(x => x.sit).length, xs.length), eat: pct(ex.filter(x => x.nat30 >= 1).length, ex.length), alive: pct(ex.filter(x => x.childAlive30).length, ex.length), ex: ex.length }; };
  const fg = S => { const xs = S.by.fguard || [], ex = xs.filter(x => x.ex), n = ex.reduce((s, x) => s + (x.spN || 0), 0);
    return { n: xs.length, sit: pct(xs.filter(x => x.sit).length, xs.length), arr: pct(ex.length, xs.length), share: pct(ex.reduce((s, x) => s + (x.spUs || 0), 0), n), them: pct(ex.reduce((s, x) => s + (x.spThem || 0), 0), n), sp: n }; };
  L.push('### 게이트 (기능 적용)', '');
  L.push(`| 지표 | 기준 | ${P.map(p => p[0]).join(' | ')} |`, `|---|---|${P.map(() => '---|').join('')}`);
  const row = (name, crit, f) => L.push(`| ${name} | ${crit} | ${P.map(p => f(p[1])).join(' | ')} |`);
  row('csplit 발동: 500라운드형 지도 r0–249 판당', '≥20', S => f1(cs(S).per5) + ` (전체 ${cs(S).n}회)`);
  row('csplit 설계 상황: 부모가 팀 최장(≥8)이 아님', '≥90%', S => cs(S).sit);
  row('csplit 새끼가 30라운드 안에 자연 진주 ≥1개', '≥45% (TW 47% · 45%)', S => `${cs(S).eat} (${cs(S).ex}마리)`);
  row('csplit 새끼 30라운드 생존', '≥30% (TW 34% · 51%)', S => cs(S).alive);
  row('F 목표(드래곤·샘) 수, 3걸음 안 도착', '–', S => `${fg(S).n}, 도착 ${fg(S).arr}`);
  row('F 설계 상황: 실제 우리 영토 샘, 처음 표식 때 다른 우리 머리 3걸음 안 없음', '≥80%', S => fg(S).sit);
  row('F 도착 뒤 30라운드 그 무리 자연 진주의 우리 몫(합산)', '≥85% (TW 자기 샘 90%)', S => `${fg(S).share} (상대 ${fg(S).them}, ${fg(S).sp}개)`);
  // the same share per map (pooled within a map), averaged over maps with equal weight, Portals left out (its two territories are
  // not connected: no opponent reaches our fountains, study 7.1), so that uncontested maps with many targets do not carry the gate
  const fgMap = S => { const m = new Map(); for (const x of (S.by.fguard || [])) { if (!x.ex || !x.spN || x.map === 'Portals') continue; const o = m.get(x.map) || { u: 0, n: 0 }; o.u += x.spUs; o.n += x.spN; m.set(x.map, o); }
    const v = [...m.entries()]; return v.length ? `${pct(v.reduce((a, [, o]) => a + o.u / o.n, 0), v.length)} (${v.map(([k, o]) => `${k} ${pct(o.u, o.n)}`).join(', ')})` : '–'; };
  row('F 같은 몫의 지도 평균(지도마다 합산, 같은 무게, Portals 제외)', '≥85%', fgMap);
  if (P.some(p => (p[1].by.cov || []).length)) row('cov 턴, 20라운드 안 우리 영토 자연 진주', '–', S => `${(S.by.cov || []).length}, ${okRate(S.by.cov || [])}`);
  L.push('');
  L.push('### 가설 수준 지표 (관찰; 500라운드형 / 전멸형)', '');
  L.push(`| 지표 | 기준 | 상위권 승자 | merge2 | ${P.map(p => p[0]).join(' | ')} |`, `|---|---|---|---|${P.map(() => '---|').join('')}`);
  const ty = (S, f) => ['500', 'elim'].map(t => { const o = S.t5.byType[t]; return o ? f(o) : '–'; }).join(' / ');
  const hrow = (name, crit, tw, m2, f) => L.push(`| ${name} | ${crit} | ${tw} | ${m2} | ${P.map(p => ty(p[1], f)).join(' | ')} |`);
  hrow('r100 우리 드래곤 수(r100까지 간 판)', '≥15 / ≥10', '30 / 21', '4 / 3', o => o.g100 ? f1(o.u100 / o.g100) : '–');
  hrow('r100 우리 영토 보로노이 몫(용량 가중, 판 평균)', '≥80%', '89% / 81%', '66% / 32%', o => o.vrN ? pct(o.vrS, o.vrN) : '–');
  hrow('r100 샘 지킴: 우리 영토 샘 중 우리 머리 3걸음 안(판 평균)', '≥50%', '61% / 55%', '22% / –', o => o.frN ? pct(o.frS, o.frN) : '–');
  hrow('우리 영토 자연 진주(r0부터 생성)를 상대가 먹은 몫(합산)', '≤25%', '11% / 16%', '56% / 55%', o => pct(o.ownThem, o.own));
  hrow('우리 영토 샘 진주를 상대가 먹은 몫(합산)', '≤15%', '7% / 6%', '50% / 33%', o => pct(o.foThem, o.fo));
  L.push('', '- 판 수(500라운드형 / 전멸형): ' + P.map(p => `${p[0]} ${ty(p[1], o => String(o.games))}`).join(' · ') + '. 판본 파일을 못 찾은 판: ' + P.map(p => `${p[0]} ${['500', 'elim'].reduce((s, t) => s + ((p[1].t5.byType[t] || {}).err || 0), 0)}`).join(' · ') + '.');
  L.push('');
  L.push('### 부작용: 우리 드래곤의 죽음 (판당; 전체 / r250 전)', '');
  L.push(`| 원인 | ${P.map(p => p[0]).join(' | ')} |`, `|---|${P.map(() => '---|').join('')}`);
  const dsum = (S, f) => ['500', 'elim'].reduce((a, t) => a + ((S.t5.byType[t] || {})[f] || 0), 0), dgames = S => ['500', 'elim'].reduce((a, t) => a + ((S.t5.byType[t] || {}).games || 0), 0);
  const drow = (name, f) => L.push(`| ${name} | ${P.map(p => `${f1(dsum(p[1], f) / Math.max(1, dgames(p[1])))} / ${f1(dsum(p[1], f + '250') / Math.max(1, dgames(p[1])))}`).join(' | ')} |`);
  drow('갇힘(빈 이웃 없음; 통로 고리의 남은 조각 포함)', 'dTrap');
  drow('적 머리에 박힘', 'dRam');
  drow('우리 드래곤끼리 머리 충돌(둘 다 죽음, 둘 다 셈)', 'dAlly');
  L.push('', `- 막힘에서 아군 머리를 피해 죽은 턴(no-exit s): ${P.map(p => `${p[0]} ${dsum(p[1], 'spare')}`).join(' · ')}`, '');
  L.push('### 지도별 (이번)', '');
  L.push('| 지도 | 판 | csplit 판당 | 새끼 먹음 ≥1 | 새끼 30R 생존 | F 목표 · 도착 · 무리 진주 우리 몫 | r100 드래곤 | 보로노이 | 샘 지킴 | 상대가 먹은 영토 진주 | 상대가 먹은 샘 진주 |', '|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|');
  for (const [m, o] of Object.entries(A.t5.byMap).sort()) {
    const xs = (A.by.csplit || []).filter(x => x.map === m), ex = xs.filter(x => x.ex), fx = (A.by.fguard || []).filter(x => x.map === m);
    L.push(`| ${m} | ${o.games} | ${f1(xs.length / Math.max(1, o.games))} | ${pct(ex.filter(x => x.nat30 >= 1).length, ex.length)} | ${pct(ex.filter(x => x.childAlive30).length, ex.length)} | ${fx.length} · ${pct(fx.filter(x => x.ex).length, fx.length)} · ${pct(fx.reduce((a, x) => a + (x.ex ? x.spUs || 0 : 0), 0), fx.reduce((a, x) => a + (x.ex ? x.spN || 0 : 0), 0))} | ${o.g100 ? f1(o.u100 / o.g100) : '–'} | ${o.vrN ? pct(o.vrS, o.vrN) : '–'} | ${o.frN ? pct(o.frS, o.frN) : '–'} | ${pct(o.ownThem, o.own)} | ${pct(o.foThem, o.fo)} |`);
  }
  L.push('');
  return L;
}

// stack7 (research/experiments/cand-stack7.md; the elimination study research/observations/our-eliminations.md section 4): floor and
// kcap lines, the pre-registered gates, the low-unit episodes (exp/eliminations/top.js I), the hypothesis-level indicators and the
// map gate. Shown when a pool carries floor / kcap tags, or with --elim (any set, for comparison).
function effectLine7(k, xs) {
  const ex = xs.filter(x => x.ex), td = {}; for (const x of ex) if (x.childDeath) td[CAUSE_KO[x.childDeath.cause]] = (td[CAUSE_KO[x.childDeath.cause]] || 0) + 1;
  const sit = k === 'floor' ? `설계 상황(발동 때 상대 ≥8마리) ${pct(xs.filter(x => x.sit).length, xs.length)}` : `설계 상황(부모가 그 순간 팀 최장, r250 전) ${pct(xs.filter(x => x.sit).length, xs.length)}`;
  return `분열 ${pct(ex.length, xs.length)} · ${sit} · 적 머리가 7×7 시야 안 ${pct(xs.filter(x => x.view).length, xs.length)} · 부모 길이 평균 ${f1(avg(xs.map(x => x.L)))} · 우리 수(표식) 평균 ${f1(avg(xs.map(x => x.units)))} · 상대 수 평균 ${f1(avg(xs.map(x => x.eu)))}` +
    ` · 새끼 10라운드 생존 ${pct(ex.filter(x => x.childAlive10).length, ex.length)} · 30라운드 ${pct(ex.filter(x => x.childAlive30).length, ex.length)} · 부모 10라운드 생존 ${pct(ex.filter(x => x.parentAlive10).length, ex.length)} · 30라운드 ${pct(ex.filter(x => x.parentAlive30).length, ex.length)}` +
    ` · 새끼 30라운드 안 1개 이상 먹음 ${pct(ex.filter(x => x.eat30 >= 1).length, ex.length)} · 30라운드 뒤 가족 길이 변화 ${f1(avg(ex.map(x => x.fam30)))} · 30라운드 안 새끼가 죽은 원인: ${Object.entries(td).map(([a, b]) => a + ' ' + b).join(', ') || '없음'}`;
}
function caseLine7(x, where, dd) {
  return `${where}: 우리 ${x.units}마리 · 상대 ${x.eu}마리${x.view ? ' · 적 머리 시야 안' : ''} · 새끼 L${x.childLen || '?'} → ${x.childDeath ? `새끼 죽음 ${dd(x.childDeath)}` : '새끼 30라운드 생존'}, 부모 10라운드 ${x.parentAlive10 ? '생존' : '죽음'}${x.sit ? '' : x.k === 'floor' ? ' (설계 밖: 상대 < 8마리)' : ' (설계 밖: 부모가 팀 최장이 아님)'}${x.mt ? ` · 표식 map=${x.mt}` : ''}`;
}
function stack7Section(A, B, opts) {
  const L = [];
  const has = S => ['floor', 'kcap'].some(k => (S.by[k] || []).length);
  if (!has(A) && !(B && has(B)) && !opts.elim) return L;
  const P = [['이번', A]].concat(B ? [['비교', B]] : []);
  const med7 = xs => { if (!xs.length) return null; const s = xs.slice().sort((a, b) => a - b), i = (s.length - 1) / 2; return (s[Math.floor(i)] + s[Math.ceil(i)]) / 2; };
  L.push('## stack7: 수 바닥 분열(floor)과 왕 길이 상한(kcap) 게이트, 저수 에피소드, 가설 수준 지표, 지도 가르기', '');
  L.push('- 기준값은 `research/experiments/cand-stack7.md`(웨이브 전)에서, 상위권·우리 값은 `research/observations/our-eliminations.md`(2.6절, 1.3절, 2.2절)에서 왔다. 저수 에피소드와 부류의 정의는 전멸 연구(`exp/eliminations/top.js` I, `lib.js` classOf)와 같다: r50부터 5라운드 간격으로 처음 우리 수 1–3·상대 ≥8인 라운드 r(라운드 첫 턴의 수; r+20이 판 안이고 우리 전멸 전), 그 뒤 [r, r+20) 분열, 20라운드 뒤 4마리 이상이면 회복, 50라운드 안 전멸. 연구의 분열 수는 10라운드 칸 두 개의 전체 분열(탈출 분열 포함)이고, 여기서는 [r, r+20)을 그대로 센다.', '');
  const fl = S => S.by.floor || [], kc = S => S.by.kcap || [], exf = xs => xs.filter(x => x.ex);
  const eps = (S, f) => S.s7.filter(g => g.ep && f(g)).map(g => g.ep);
  const onEp = S => eps(S, g => g.on);
  L.push('### 게이트 (기능 적용)', '');
  L.push(`| 기능 | 지표 | 기준 | ${P.map(p => p[0]).join(' | ')} |`, `|---|---|---|${P.map(() => '---|').join('')}`);
  const row = (f, name, crit, fn) => L.push(`| ${f} | ${name} | ${crit} | ${P.map(p => fn(p[1])).join(' | ')} |`);
  row('floor', '발동(판당; floor 지도 판)', '–', S => { const n = S.s7.filter(g => g.on).length; return `${fl(S).length} (${f1(fl(S).length / Math.max(1, n))}; ${n}판)`; });
  row('floor', '1. 설계 상황: 발동 때 상대 ≥8마리', '≥90%', S => pct(fl(S).filter(x => x.sit).length, fl(S).length));
  row('floor', '저수 에피소드가 있는 floor 지도 판 · 그 20라운드 안 floor 발동이 있었던 판', '(관찰)', S => { const e = onEp(S); return `${e.length} · ${pct(e.filter(q => q.floor > 0).length, e.length)}`; });
  row('floor', '2. 즉시 효과 A: 에피소드 20라운드 비탈출 분열(판당; floor 지도)', '≥2.0 (상위 LX·LS 2.0, 우리 0.5)', S => { const e = onEp(S); return e.length ? `${f1(avg(e.map(q => q.nonEsc)))} (floor ${f1(avg(e.map(q => q.floor)))}, kcap ${f1(avg(e.map(q => q.kcap)))}, csplit ${f1(avg(e.map(q => q.csplit)))}; 탈출 포함 전체 ${f1(avg(e.map(q => q.all)))})` : '–'; });
  row('floor', '3. 즉시 효과 B: 에피소드 20라운드 뒤 4마리 이상(floor 지도)', '≥23% (상위 LX 23%, LS 26%, 우리 5%)', S => { const e = onEp(S); return e.length ? `${pct(e.filter(q => q.rec).length, e.length)} (${e.filter(q => q.rec).length}/${e.length})` : '–'; });
  row('floor', '4. 즉시 효과 C: floor 새끼 30라운드 생존', '≥34% (상위 패자 제 영토 새끼 34%, 승자 51%)', S => { const e = exf(fl(S)); return `${pct(e.filter(x => x.childAlive30).length, e.length)} (${e.length}마리)`; });
  row('kcap', '발동(판당; kcap 지도 판)', '–', S => { const n = S.s7.filter(g => g.kon).length; return `${kc(S).length} (${f1(kc(S).length / Math.max(1, n))}; ${n}판)`; });
  row('kcap', '1. 설계 상황: 부모가 그 순간 팀 최장이고 r250 전', '≥90%', S => pct(kc(S).filter(x => x.sit).length, kc(S).length));
  row('kcap', '2. 즉시 효과: 새끼 10라운드 생존', '≥74% (상위권 길이 4 분열 74.2%)', S => { const e = exf(kc(S)); return `${pct(e.filter(x => x.childAlive10).length, e.length)} (${e.length}마리)`; });
  row('kcap', '2. 즉시 효과: 부모 10라운드 생존', '≥55% (상위권 54.5%)', S => { const e = exf(kc(S)); return pct(e.filter(x => x.parentAlive10).length, e.length); });
  L.push('');
  L.push('### 저수 에피소드 (floor 지도 / 모든 지도; 판정은 floor 지도)', '');
  L.push(`| 묶음 | 지도 | 판 | 에피소드 있음 | 처음 라운드(중앙) | 그때 우리 수 · 상대 수 | 그때 총길이 · 최장 | 20라운드 비탈출 분열 | floor · kcap | 탈출 포함 전체 | 20라운드 뒤 4마리 이상 | 50라운드 안 전멸 |`, '|---|---|---:|---:|---:|---|---|---:|---|---:|---:|---:|');
  for (const [name, S] of P) for (const [lab, f] of [['floor 지도', g => g.on], ['floor 지도 중 전멸형', g => g.on && g.type === 'elim'], ['floor 지도 중 500형', g => g.on && g.type === 'r500'], ['끄는 지도(Autarky·PD·Portals)', g => !g.on], ['모든 지도', () => true]]) {
    const G7 = S.s7.filter(f), e = G7.filter(g => g.ep).map(g => g.ep);
    L.push(`| ${name} | ${lab} | ${G7.length} | ${pct(e.length, G7.length)} | ${f1(med7(e.map(q => q.r)))} | ${f1(avg(e.map(q => q.u)))} · ${f1(avg(e.map(q => q.eu)))} | ${f1(avg(e.map(q => q.t)))} · ${f1(avg(e.map(q => q.k)))} | ${f1(avg(e.map(q => q.nonEsc)))} | ${f1(avg(e.map(q => q.floor)))} · ${f1(avg(e.map(q => q.kcap)))} | ${f1(avg(e.map(q => q.all)))} | ${pct(e.filter(q => q.rec).length, e.length)} | ${pct(e.filter(q => q.die50).length, e.length)} |`);
  }
  L.push('', '- 상위권 기준(전멸 연구 2.6절, 전멸형): LX 72%가 그런 때를 겪고(처음 r105) 20라운드에 2.0번 나누며 23%가 회복, 42%가 50라운드 안 전멸. LS 69%, 2.0번, 26%, 0%. 우리 g4 LX 95%(r50), 0.5번, 5%, 15%.', '');
  L.push('### 가설 수준 지표 (관찰)', '');
  L.push(`| 기능 | 지표 | 기준 | 상위권 · 이전 우리 | ${P.map(p => p[0]).join(' | ')} |`, `|---|---|---|---|${P.map(() => '---|').join('')}`);
  const hrow = (f, name, crit, ref, fn) => L.push(`| ${f} | ${name} | ${crit} | ${ref} | ${P.map(p => fn(p[1])).join(' | ')} |`);
  const elimG = (S, onOnly) => S.s7.filter(g => g.type === 'elim' && (!onOnly || g.on));
  const both = (S, fn) => `${fn(elimG(S, false))} / ${fn(elimG(S, true))}`;
  hrow('floor', 'r100 우리 드래곤 수(전멸형; 전멸은 0) — 전멸형 5지도 / PD 뺀 4지도', '≥5.5', '상위 LX 5.5, 우리 g4 LX 2.5', S => both(S, G7 => f1(avg(G7.map(g => g.u100)))));
  hrow('floor', '전멸률(전멸형)', '≤66%', 'swarm8 66%, merge2 78%', S => both(S, G7 => `${pct(G7.filter(g => g.elim).length, G7.length)} (${G7.filter(g => g.elim).length}/${G7.length})`));
  hrow('floor', '전멸 라운드 중앙(전멸형)', '≥r235', 'swarm8 235, merge2 150, stack1–3 163', S => both(S, G7 => f1(med7(G7.filter(g => g.elim).map(g => g.elimR)))));
  hrow('kcap', '우리 전멸 중 E2(왕 사냥) 비율(모든 지도)', '≤8%', '상위 LX 6%, 우리 16%', S => { const X = S.s7.filter(g => g.elim); return `${pct(X.filter(g => g.cls === 'E2').length, X.length)} (E1 ${X.filter(g => g.cls === 'E1').length} · E2 ${X.filter(g => g.cls === 'E2').length} · E3m ${X.filter(g => g.cls === 'E3m').length} · E3l ${X.filter(g => g.cls === 'E3l').length})`; });
  hrow('kcap', 'r50 우리 최장 평균(전멸형; 전멸은 0) — 5지도 / 4지도', '≤4.5', '상위 LS 3.8, 우리 g4 LX 6.8', S => both(S, G7 => f1(avg(G7.map(g => g.k50)))));
  hrow('kcap', '전멸한 판의 길이 ≥8 죽음(판당; 모든 지도)', '≤0.4', '우리 0.75', S => { const X = S.s7.filter(g => g.elim); return X.length ? `${f1(avg(X.map(g => g.d8)))} (${X.length}판)` : '–'; });
  L.push('');
  L.push('### 지도 가르기 (map= 표식으로 확인)', '');
  L.push('- floor는 Trophy, Queen Of Spades, Devil, Default, Schooltime, Trauma, Slithery Fight에서만, kcap은 그중 Slithery Fight를 뺀 여섯에서만 켠다. 봇은 프로세스마다 자기 창으로 지도 가족을 인식하고(`map=` 표식), 인식 전·`none`이면 끈다. "표식이 켜는 가족이 아닌 발동"은 발동한 프로세스의 마지막 `map=` 표식이 그 기능을 켜는 가족을 대지 않은 발동이다(0이어야 한다). "인식한 프로세스"는 마지막 표식이 그 판의 참 지도 가족을 댄 프로세스다.', '');
  L.push(`| 묶음 | 지도(정답 판본) | 판 | floor 발동 | kcap 발동 | 표식이 켜는 가족이 아닌 발동 | 인식한 프로세스 |`, '|---|---|---:|---:|---:|---:|---:|');
  for (const [name, S] of P) {
    const m = new Map(); for (const g of S.s7) { const k = g.key + (g.lay ? ' ' + g.lay : ''); if (!m.has(k)) m.set(k, []); m.get(k).push(g); }
    for (const [k, G7] of [...m.entries()].sort()) {
      const s = f => G7.reduce((a, g) => a + (g[f] || 0), 0);
      L.push(`| ${name} | ${k}${S7_FLOOR_MAPS.has(G7[0].map) ? '' : ' (끔)'}${S7_FLOOR_MAPS.has(G7[0].map) && !S7_KCAP_MAPS.has(G7[0].map) ? ' (kcap 끔)' : ''} | ${G7.length} | ${s('floorN')} | ${s('kcapN')} | ${s('offTag')} | ${s('tagged') ? `${pct(s('recog'), s('procs'))} (${s('recog')}/${s('procs')})` : '표식 없음'} |`);
    }
  }
  L.push('');
  return L;
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv[0] === '--worker') return workerMain();
  const opt = (n, d) => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : d; };
  const flags = new Set(['--vs', '--out', '--json', '--cases', '--jobs', '--title']);
  const pos = argv.filter((a, i) => !a.startsWith('--') && !flags.has(argv[i - 1]));
  if (!pos[0]) { console.error('usage: mech_check.js <pool> [--vs <pool>] [--out f.md] [--json f.json] [--cases 10] [--jobs 4] [--title t]'); process.exit(2); }
  const jobs = +opt('--jobs', 4), cases = +opt('--cases', 10);
  const tA = tasksOf(pos[0]), tB = opt('--vs') ? tasksOf(opt('--vs')) : null;
  const rA = await runAll(tA, jobs), rB = tB ? await runAll(tB, jobs) : null;
  for (const e of [...rA.errors, ...(rB ? rB.errors : [])]) console.error('error', e.key, e.error);
  const bad = [...rA.games, ...(rB ? rB.games : [])].filter(g => Object.values(g.chk).some(v => v));
  if (bad.length) console.error(`reconstruction checks nonzero in ${bad.length} games (e.g. ${bad[0].key} ${JSON.stringify(bad[0].chk)})`);
  const A = summarise(rA.games), B = rB ? summarise(rB.games) : null;
  const md = report(A, B, { poolA: pos[0], poolB: opt('--vs'), cases, title: opt('--title'), territory: argv.includes('--territory'), lineage: argv.includes('--lineage'), // cand-conv2 --lineage
    elim: argv.includes('--elim'),                                                                       // stack7 --elim
    stack8: argv.includes('--stack8') });                                                                // stack8 --stack8
  if (opt('--out')) fs.writeFileSync(path.resolve(ROOT, opt('--out')), md + '\n'); else console.log(md);
  if (opt('--json')) fs.writeFileSync(path.resolve(ROOT, opt('--json')), JSON.stringify({ A: rA.games, B: rB ? rB.games : null }));
  if (opt('--out')) console.log(`wrote ${opt('--out')} (${rA.games.length}${rB ? ' + ' + rB.games.length : ''} games, ${rA.errors.length + (rB ? rB.errors.length : 0)} errors)`);
}
// stack8 (research/experiments/cand-stack8.md): px2 / Fp / cl / ce lines, and the gate section
function effectLine8(k, xs) {
  if (k === 'px2') return `건너지 않음(px2) ${pct(xs.filter(x => !x.px2x).length, xs.length)} · 건넘(px2x) ${xs.filter(x => x.px2x).length}턴 · 설계 상황(전 라운드 그 칸의 음파가 우리 드래곤에 멈춤) ${pct(xs.filter(x => x.sit).length, xs.length)} · 몸 3라운드 생존 ${pct(xs.filter(x => x.alive3).length, xs.length)} (px2 ${pct(xs.filter(x => !x.px2x && x.alive3).length, xs.filter(x => !x.px2x).length)}, px2x ${pct(xs.filter(x => x.px2x && x.alive3).length, xs.filter(x => x.px2x).length)})`;
  const pr = xs.filter(x => x.present);
  const sitDef = k === 'fp' ? '표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음' : k === 'cl' ? '자연 진주이고 우리 머리 가운데 표식한 조각만 가장 가까움' : '적 머리가 진주에서 우리 거리+1 안';
  return `진주 ${xs.length}개 (표식 턴 ${xs.reduce((s, x) => s + x.turns, 0)}; 표식 때 진주 있음 ${pct(pr.length, xs.length)}) · 설계 상황(${sitDef}) ${pct(xs.filter(x => x.sit).length, xs.length)} · 그 드래곤이 먹음 ${pct(pr.filter(x => x.eatSelf).length, pr.length)} (10라운드 안 ${pct(pr.filter(x => x.eatSelf10).length, pr.length)}) · 우리 팀 ${pct(pr.filter(x => x.eatUs).length, pr.length)} · 우리 긴 드래곤 ${pct(pr.filter(x => x.eatLonger).length, pr.length)} · 상대 ${pct(pr.filter(x => x.eatThem).length, pr.length)}${k === 'ce' ? ` · 5라운드 안 박힘 ${pct(xs.filter(x => x.rammed5).length, xs.length)}` : ''}`;
}
function caseLine8(x, where) {
  if (x.k === 'px2') return `${where}: ${x.px2x ? '건넘(px2x)' : '건너지 않음(px2)'}${x.sit ? '' : ' (설계 밖: 전 라운드 음파가 우리 드래곤에 멈추지 않음)'} → 몸 3라운드 ${x.alive3 ? '생존' : '잃음'}`;
  return `${where}: 진주 (${x.px},${x.py}) 우리 거리 ${x.dm}${x.present ? '' : ' (표식 때 진주 없음)'}${x.sit ? '' : ' (설계 밖)'} → ${x.eatSelf ? '그 드래곤이 먹음' : x.eatUs ? '다른 우리 드래곤이 먹음' : x.eatThem ? '상대가 먹음' : '아무도 안 먹음'}`;
}
function stack8Section(A, B, opts) {
  const L = [];
  const has = S => ['px2', 'fp', 'cl', 'ce'].some(k => (S.by[k] || []).length) || (S.by.fguard || []).some(x => x.f2);
  if (!has(A) && !(B && has(B)) && !opts.stack8) return L;
  const P = [['이번', A]].concat(B ? [['비교', B]] : []);
  L.push('## stack8: 샘 목표 고르기(F2·F2p), 포털 출구의 아군(px2), 새끼의 몫(cl·ce)', '');
  L.push('- 기준값은 `research/experiments/cand-stack8.md`(로컬 확인 전, 18:20)에서 왔다. cl·ce의 기준값은 공급망 연구의 값(18:07)이다. F 목표(드래곤·샘 단위)와 포털 통과의 정의는 stack5 절과 "포털 통과" 절과 같다. Fp·cl·ce는 드래곤·진주 단위이고, 설계 상황은 처음 표식 때의 판이다.', '');
  L.push(`| 기능 | 지표 | 기준 | ${P.map(p => p[0]).join(' | ')} |`, `|---|---|---|${P.map(() => '---|').join('')}`);
  const row = (f, name, crit, fn) => L.push(`| ${f} | ${name} | ${crit} | ${P.map(p => fn(p[1])).join(' | ')} |`);
  const fg = S => S.by.fguard || [], f2 = S => fg(S).filter(x => x.f2), prs = xs => xs.filter(x => x.present);
  const share = xs => { let u = 0, n = 0; for (const x of xs) if (x.ex && x.spN) { u += x.spUs; n += x.spN; } return [u, n]; };
  const mapAvg = xs => { const m = new Map(); for (const x of xs) { if (!x.ex || !x.spN || x.map === 'Portals') continue; const o = m.get(x.map) || [0, 0]; o[0] += x.spUs; o[1] += x.spN; m.set(x.map, o); } const v = [...m.values()].map(o => o[0] / o[1]); return v.length ? Math.round(100 * avg(v)) + '%' : '–'; };
  row('F2', '목표 수: F2 표식 / 모든 F(판당)', '–', S => `${f2(S).length} / ${fg(S).length} (${f1(fg(S).length / Math.max(1, S.games))})`);
  row('F2', '1. 설계 상황: F2 표식 목표 (실제 샘 · 우리 영토 · 다른 머리 없음)', '≥90%', S => `${pct(f2(S).filter(x => x.sit).length, f2(S).length)} (${pct(f2(S).filter(x => x.fnt).length, f2(S).length)} · ${pct(f2(S).filter(x => x.own).length, f2(S).length)} · ${pct(f2(S).filter(x => !x.guarded0).length, f2(S).length)})`);
  row('F2', '1. 설계 상황: 모든 F 목표', '≥80%', S => pct(fg(S).filter(x => x.sit).length, fg(S).length));
  row('F2', '2. 도착(3걸음 안): F2 표식 목표 / 모든 F', '≥80%', S => `${pct(f2(S).filter(x => x.ex).length, f2(S).length)} / ${pct(fg(S).filter(x => x.ex).length, fg(S).length)}`);
  row('F2', '3. 도착 뒤 30라운드 무리 자연 진주 우리 몫(F2 표식; 합산 · 지도 평균, Portals 제외)', '≥85% · ≥85%', S => { const [u, n] = share(f2(S)); return `${pct(u, n)} (${n}개) · ${mapAvg(f2(S))}`; });
  row('F2', '4. 겹친 추격: 다른 우리 드래곤의 같은 샘 목표와 겹침(F2 표식 / 모든 F)', '≤10%', S => `${pct(f2(S).filter(x => x.dbl).length, f2(S).length)} / ${pct(fg(S).filter(x => x.dbl).length, fg(S).length)}`);
  const fp = S => S.by.fp || [];
  row('F2p', 'Fp 진주 수(표식 턴)', '–', S => `${fp(S).length} (${fp(S).reduce((s, x) => s + x.turns, 0)}턴)`);
  row('F2p', '1. 설계 상황: 표식 때 진주가 있고 다른 머리(양 팀)가 더 가깝지 않음', '≥80%', S => pct(fp(S).filter(x => x.sit).length, fp(S).length));
  row('F2p', '2. 즉시 효과: 그 드래곤이 10라운드 안에 먹음 · 상대가 먹음', '≥48% · ≤5%', S => `${pct(prs(fp(S)).filter(x => x.eatSelf10).length, prs(fp(S)).length)} · ${pct(prs(fp(S)).filter(x => x.eatThem).length, prs(fp(S)).length)}`);
  row('F2p', '끌어내기: F 표식 턴 가운데 유일하게 가장 가까운 자연 진주(7걸음 안, 무리 밖)에서 멀어진 턴', '≤5% (관찰; W5+W6 15%)', S => `${pct(S.s8.fAway, S.s8.fT)} (후보가 있던 턴 ${pct(S.s8.fCand, S.s8.fT)}; F 표식 턴 ${S.s8.fT})`);
  const px = S => S.by.px2 || [], po = S => S.by.portal || [];
  // v is not a filter here: px2's own penalty moves a px2x crossing's v below -20 (cand-stack8.md, local v1)
  const ownAlly = S => po(S).filter(x => x.stepOwn && !x.blind && x.probe === 'ally').length;
  const ownAll = S => po(S).filter(x => x.stepOwn).length;
  row('px2', '발동(px2 + px2x 턴, 판당)', '–', S => `${px(S).length} (${f1(px(S).length / Math.max(1, S.games))})`);
  row('px2', '1. 설계 상황: 전 라운드 그 칸의 음파가 우리 드래곤에 멈춤', '≥95%', S => pct(px(S).filter(x => x.sit).length, px(S).length));
  row('px2', '2. 즉시 효과 A: 건너지 않음(px2)', '≥80%', S => pct(px(S).filter(x => !x.px2x).length, px(S).length));
  row('px2', '3. 즉시 효과 B: 아군에 멈춘 탐침 뒤 아는 포털을 건너는 걸음에서 아군에 막혀 죽음(판당, v 무관)', '≤0.2 (W5–W7 0.69)', S => `${(ownAlly(S) / Math.max(1, S.games)).toFixed(2)} (${ownAlly(S)}건)`);
  row('px2', '보호: 포털 3라운드 몸 생존', '≥95%', S => pct(po(S).filter(x => x.alive3).length, po(S).length));
  row('px2', '보호: 건너는 걸음 아군 막힘 죽음(판당, 탐침·v 무관)', '≤0.75 (W5–W7 1.41)', S => `${(ownAll(S) / Math.max(1, S.games)).toFixed(2)} (${ownAll(S)}건)`);
  const cl = S => S.by.cl || [], ce = S => S.by.ce || [];
  row('cl', '진주 수(표식 턴)', '–', S => `${cl(S).length} (${cl(S).reduce((s, x) => s + x.turns, 0)}턴)`);
  row('cl', '설계 상황: 자연 진주, 우리 머리 가운데 표식한 조각만 가장 가까움', '≥90%', S => pct(cl(S).filter(x => x.sit).length, cl(S).length));
  row('cl', '즉시 효과: 조각이 먹음 · 우리 팀 · 우리 긴 드래곤', '≥48% · ≥97% · ≤10%', S => { const p = prs(cl(S)); return `${pct(p.filter(x => x.eatSelf).length, p.length)} · ${pct(p.filter(x => x.eatUs).length, p.length)} · ${pct(p.filter(x => x.eatLonger).length, p.length)}`; });
  row('ce', '진주 수(표식 턴)', '–', S => `${ce(S).length} (${ce(S).reduce((s, x) => s + x.turns, 0)}턴)`);
  row('ce', '설계 상황: 적 머리가 진주에서 우리 거리+1 안', '≥80%', S => pct(ce(S).filter(x => x.sit).length, ce(S).length));
  row('ce', '즉시 효과: 상대가 먹음', '≤5%', S => { const p = prs(ce(S)); return pct(p.filter(x => x.eatThem).length, p.length); });
  row('ce', '보호: 표식 뒤 5라운드 안 박힘', '≤19%', S => pct(ce(S).filter(x => x.rammed5).length, ce(S).length));
  L.push('', '- cl·ce의 가설 수준 지표(새끼 30라운드 먹음 ≥45%, 새끼 몫의 상대 몫 ≤3%/≤5%)는 공급망 스크립트 `exp/supply-chain/child_forage.js`로 잰다. 새끼 먹음은 stack5 절의 csplit 줄에도 있다.', '');
  L.push('### 포털 통과: 전 라운드 탐침(같은 칸, 같은 방향의 음파)별', '');
  L.push('| 묶음 | 출구 | 탐침 | 필사(v ≤ −20) | 통과 | 몸 3라운드 실패 | 건너는 걸음 아군 막힘 죽음 |', '|---|---|---|---|---:|---:|---:|');
  for (const [name, S] of P) {
    const m = new Map();
    for (const x of po(S)) { const kk = `${x.blind ? '미탐색' : '아는 포털'} | ${x.probe || '?'}${x.probeHead ? '(머리)' : ''} | ${x.desperate ? '필사' : '아님'}`; const o = m.get(kk) || [0, 0, 0]; o[0]++; if (!x.alive3) o[1]++; if (x.stepOwn) o[2]++; m.set(kk, o); }
    for (const [kk, o] of [...m.entries()].sort((a, b) => b[1][0] - a[1][0])) L.push(`| ${name} | ${kk} | ${o[0]} | ${pct(o[1], o[0])} | ${o[2]} |`);
  }
  L.push('');
  return L;
}
module.exports = { parseInd, analyse, summarise, report };
if (require.main === module) main().catch(e => { console.error(e); process.exit(1); });
