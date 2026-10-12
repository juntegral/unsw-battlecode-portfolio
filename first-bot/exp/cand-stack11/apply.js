#!/usr/bin/env node
// cand-stack11 (research/experiments/cand-stack11.md): apply the gh / kx / lwk edits of the endgame king study
// (research/observations/endgame-king.md section 7) to a copy of the base bot (stack10; stack9 for the early dev build). Every edit is an
// exact-string replacement whose anchor must occur exactly once, so a changed base fails loudly.
// usage: node exp/cand-stack11/apply.js <bot dir> [--off] [--only gh,kx,lwk]
//   --off   GH_ON, KX_ON and LWK_ON false (the identity copy)
//   --only  switch on only the named toggles (the others false), for per-mechanism local runs
'use strict';
const fs = require('fs'), path = require('path');
const dir = path.resolve(process.argv[2] || ''), off = process.argv.includes('--off');
const oi = process.argv.indexOf('--only'), only = oi >= 0 ? new Set(process.argv[oi + 1].split(',')) : null;
if (!fs.existsSync(path.join(dir, 'plan.cpp'))) { console.error('usage: apply.js <bot dir> [--off] [--only gh,kx,lwk]'); process.exit(2); }
const on = k => !off && (!only || only.has(k));

const PARAMS = `// --- stack11 (2026-09-30): the three proposals of the endgame king study research/observations/endgame-king.md (section 7; our 21 elite
// sets, 1,469 games, + top-vs-top 500-round games), each with its own toggle and indicator tag (research/experiments/cand-stack11.md).
// With GH_ON, KX_ON and LWK_ON all false the bot plays exactly as stack10 (checked by replay event hashes on two local games).
// On 500-round maps our final king ends 20.4 shorter than top winners' (stack5-7), 17.5 of it in sacrifice pearls. Gathering supplies
// 57-76% of the line's sacrifice pearls but leaks: the team's longest at the start of gathering is the final king in 33%, and other own
// dragons eat 26-35% of the pearls of labelled feeds aimed at the line (merge2 20%). Our king lives next to enemy heads (52% of its
// r300-399 turns have one within Manhattan 6; top winners 32%) and we lose the team's longest to an enemy head after r340 in 13% of games
// (winners 5%); conv is blocked by an enemy head in view in 36-39% of its geometric states (winners 17%).
// gh (proposal 1): gatherers hold back at the king, and fresh drops beside a longer ally's head are left to it.
//   hold: the gathering leaf penalty (dfs) is GATHER_W x max(0, goal distance - GH_HOLD) instead of GATHER_W x goal distance (as F's
//     FG_HOLD). Tag " gh" on a gathering move turn whose goal distance at our head is <= GH_HOLD + 2.
//   drops: from GH_DROP_START, a fresh death drop (freshDrop) within Manhattan GH_DROP_R of the head of an ally seen this turn that is
//     longer than us is worth CONTEST_ALLY_CLOSER times a pearl wherever the planner values a pearl on it: the search's step value, its
//     attraction source (which loses grab's boost and tag for this dragon; the ally-closer discount applies at every distance), and the
//     first-step and sprint values of the candidates (a dragon beside the drop would otherwise take it on its first step). Whether a move
//     eats is unchanged (the body model). Tag " ghd@<x>,<y>" (the nearest such drop) on a move turn with one within 3 steps of our head.
// kx (proposal 2): from KX_START the king keeps away from enemy heads on the recognised fight maps (kxMapOn: Schooltime, Slithery Fight,
//   Trauma, Autarky; World::mapFamIs, off before recognition and on "map=none"). The king = length >= KING_MIN_LEN and no ally longer than
//   us with news (seen, heard or relayed) within KX_KING_FRESH rounds (kingFresh(); not gatherKing_, whose 100-round memory counts dead
//   allies: World::dragons is cleared only at init). kxDist_ = path distance over known edges (bodies ignored, as goalDist_) from the enemy
//   heads seen within KX_STALE rounds, up to KX_DIST; while a known enemy head is within KX_DIST of our head, the search's leaf pays
//   KX_W x (KX_DIST - kxDist_). Unlike stack1 ks and stack3 ks2 (threat weights on tiles inside the sprint reach of enemy heads long enough
//   to strike, r450 / r400 on; the king's position did not change), kx prices plain distance to every enemy head, pieces included (their
//   presence blocks conv and feed), from r300, as a pull over the whole search horizon. Tag " kx<d>" (d = kxDist_ at our head), and
//   " kxm" when the chosen move ends farther than d.
// lwk (proposal 3): the late window (from FEED_FIRST_ROUND) also feeds only the king class (an ally at least kingLen - 2 long, as the
//   gathering window's earlyOnlyKing), with kingLen taken from news of the last LWK_KING_FRESH rounds (not GATHER_KING_MEMORY: a dead
//   king's record would stop feeds to the new one). Tag " lwk" on a move turn whose feed the old late-window rule (any longer ally within
//   FEED_MAX_DIST) would have made.
constexpr bool   GH_ON = ${on('gh') ? 'true' : 'false'};
constexpr int    GH_HOLD = 3;               // the study: no gathering pull within 3 of the goal (feeds reach 5)
constexpr int    GH_DROP_R = 2;             // drops within Manhattan 2 of a longer ally's head are left to it
constexpr int    GH_DROP_START = 300;       // CONV_START: the feeds (conv from r300, feed from r340) whose pearls the rule leaves to the target
constexpr bool   KX_ON = ${on('kx') ? 'true' : 'false'};
constexpr int    KX_START = 300;            // the exposure gap is widest in r300-399 (52% vs 32%)
constexpr int    KX_DIST = 7;               // keep >= 7 from enemy heads (the exposure metric counts <= 6)
constexpr double KX_W = 0.4;                // leaf penalty per tile below KX_DIST (GATHER_W 0.12 moves gatherers 19 steps)
constexpr int    KX_STALE = 3;              // enemy heads seen this recently
constexpr int    KX_KING_FRESH = 20;        // GATHER_STALE: a longer ally with news this recent says we are not the king
constexpr bool   LWK_ON = ${on('lwk') ? 'true' : 'false'};
constexpr int    LWK_KING_FRESH = 20;       // GATHER_STALE: kingLen from news this recent in the late window

// --- search / budget ---`;

const HPP_MEMBERS = `    // stack11 gh / kx / lwk (params.hpp stack11 section)
    std::vector<uint8_t> ghDrop_;               // gh: 1 on a fresh drop left to a longer ally this turn
    std::vector<int> ghdTiles_;                 // gh: those tiles (cleared next turn; the tag names the nearest)
    bool ghOn_ = false;                         // gh: some drop is left to a longer ally this turn
    std::vector<int16_t> kxDist_;               // kx: path distance (<= KX_DIST) from enemy heads seen within KX_STALE rounds; 99 beyond
    std::vector<int> kxQ_;                      // kx: BFS queue
    bool kxOn_ = false;                         // kx: the king-away leaf penalty applies this turn
    bool lwkHeld_ = false;                      // lwk: the king-class rule stopped a late-window feed this turn
    void computeGhDrops();                      // gh: ghDrop_ / ghdTiles_ / ghOn_
    void computeKingAway();                     // kx: kxDist_ / kxOn_
    bool kingFresh() const;                     // kx: no ally longer than us with news within KX_KING_FRESH rounds
    bool kxMapOn() const;                       // kx: a recognised KX map family
    double pearlValue(int t, double p) const;   // gh: p, or p x CONTEST_ALLY_CLOSER on a drop left to a longer ally
};

long long nowPoints();`;

const PLAN_FUNCS = `// stack11 gh (drops): from GH_DROP_START, fresh death drops (freshDrop, a pearl likely there) within Manhattan GH_DROP_R of the head of an
// ally seen this turn that is longer than us (the feed rule's length: a whole chain in view is exact). They are left to that ally.
void Planner::computeGhDrops() {
    for (int t : ghdTiles_) ghDrop_[t] = 0;
    ghdTiles_.clear(); ghOn_ = false;
    if (!P::GH_ON || w_.round < P::GH_DROP_START || w_.allyHeadsNow.empty()) return;
    int n = w_.geo.tiles();
    if ((int)ghDrop_.size() != n) ghDrop_.assign(n, 0);
    for (int id : w_.allyHeadsNow) {
        auto it = w_.dragons.find(id); if (it == w_.dragons.end()) continue;
        const Dragon& a = it->second;
        int la = a.tailSeen && a.lastSeen == w_.round ? a.visLen : std::max(a.minLen, a.estLen);
        if (a.headT < 0 || la <= w_.myLen) continue;
        int ax = a.headT % w_.geo.W, ay = a.headT / w_.geo.W;
        for (int dy = -P::GH_DROP_R; dy <= P::GH_DROP_R; dy++) for (int dx = -P::GH_DROP_R; dx <= P::GH_DROP_R; dx++) {
            if (Geo::abs(dx) + Geo::abs(dy) > P::GH_DROP_R) continue;
            int t = w_.geo.idx(w_.geo.wrapX(ax + dx), w_.geo.wrapY(ay + dy));
            if (ghDrop_[t] || !freshDrop(t) || w_.pearlProb(t, w_.round) < 0.15) continue;
            ghDrop_[t] = 1; ghdTiles_.push_back(t); ghOn_ = true;
        }
    }
}

// stack11 gh: the value of a pearl of probability p on tile t (the ally-closer discount on a drop left to a longer ally)
double Planner::pearlValue(int t, double p) const { return ghOn_ && ghDrop_[t] ? p * P::CONTEST_ALLY_CLOSER : p; }

// stack11 kx: are we the king? Only news from the last KX_KING_FRESH rounds counts. World::dragons keeps every dragon ever seen (it is
// cleared once, at init), so the gathering's 100-round memory (GATHER_KING_MEMORY, gatherKing_) can keep a dead longer ally in our
// belief; a longer ally seen, heard (its message) or relayed (a relay carries the round of its news) within KX_KING_FRESH rounds says no.
bool Planner::kingFresh() const {
    for (auto& [id, d] : w_.dragons) {
        if (id == w_.myId || d.team != w_.myTeam || d.headT < 0 || w_.round - d.headSeen > P::KX_KING_FRESH) continue;
        if (std::max(d.estLen, d.minLen) > w_.myLen) return false;
    }
    return true;
}

// stack11 kx: the fight maps of the study's KX_MAPS (Schooltime and Slithery Fight first, then Trauma and Autarky), as this process
// recognised the family (off before recognition and on "map=none"; Portals and the elimination maps are off)
bool Planner::kxMapOn() const {
    for (const char* f : {"Schooltime", "Slithery_Fight", "Trauma", "Autarky"})
        if (w_.mapFamIs(f)) return true;
    return false;
}

// stack11 kx (endgame king study 7.2): the king (kingFresh, length >= KING_MIN_LEN) from KX_START on a KX map keeps away from enemy
// heads. kxDist_ = path distance over known edges, bodies ignored (as goalDist_), from every enemy head seen within KX_STALE rounds, up
// to KX_DIST (99 beyond). On only while such a head is within KX_DIST of our head (the rule's firing condition; every firing is tagged).
void Planner::computeKingAway() {
    kxOn_ = false;
    if (!P::KX_ON || w_.round < P::KX_START || w_.myLen < P::KING_MIN_LEN || !kxMapOn() || !kingFresh()) return;
    int n = w_.geo.tiles();
    kxDist_.assign(n, 99);
    kxQ_.clear();
    for (auto& [id, d] : w_.dragons) {
        if (d.team == w_.myTeam || d.headT < 0 || w_.round - d.headSeen > P::KX_STALE) continue;
        if (kxDist_[d.headT] > 0) { kxDist_[d.headT] = 0; kxQ_.push_back(d.headT); }
    }
    for (size_t qi = 0; qi < kxQ_.size(); qi++) {
        int t = kxQ_[qi];
        if (kxDist_[t] >= P::KX_DIST) continue;
        for (int dir = 0; dir < 4; dir++) {
            int u = w_.across(t, dir);
            if (u < 0 || kxDist_[u] <= kxDist_[t] + 1) continue;
            kxDist_[u] = (int16_t)(kxDist_[t] + 1); kxQ_.push_back(u);
        }
    }
    kxOn_ = kxDist_[w_.headT] <= P::KX_DIST;
}

int Planner::pickHotspot() const {`;

// ---------------------------------------------------------------------------------------------------------------
const edits = [
  // params.hpp: the stack11 section before the search budget
  ['params.hpp', '\n// --- search / budget ---', '\n' + PARAMS],
  // plan.hpp: members and methods
  ['plan.hpp', '};\n\nlong long nowPoints();', HPP_MEMBERS],
  // plan.cpp computeAttract: a drop left to a longer ally is not a grab target; its source gets the ally-closer discount everywhere
  ['plan.cpp', 'struct Src { int t; double v; int wait; bool grab; bool cov = false; }; // cov: stack5',
               'struct Src { int t; double v; int wait; bool grab; bool cov = false; bool gh = false; }; // cov: stack5; gh: stack11'],
  ['plan.cpp', `        bool grab = grabOn_ && p >= 0.15 && headDist_[t] >= 0 && headDist_[t] <= P::GRAB_REACH && freshDrop(t);
        if (grab) { v = std::max(v, p * P::GRAB_VALUE); grabTiles_.push_back(t); }`,
               `        bool grab = grabOn_ && p >= 0.15 && headDist_[t] >= 0 && headDist_[t] <= P::GRAB_REACH && freshDrop(t);
        const bool ghs = ghOn_ && ghDrop_[t];                 // stack11 gh: left to the longer ally beside it (no grab for us)
        if (ghs) grab = false;
        if (grab) { v = std::max(v, p * P::GRAB_VALUE); grabTiles_.push_back(t); }`],
  ['plan.cpp', '        src.push_back({t, v, wait, grab, cov});', '        src.push_back({t, v, wait, grab, cov, ghs});'],
  ['plan.cpp', '            if (af < dist) contest *= P::CONTEST_ALLY_CLOSER;\n            attract_[t] +=',
               '            if (af < dist || s.gh) contest *= P::CONTEST_ALLY_CLOSER; // stack11 gh: at every distance for a drop left to a longer ally\n            attract_[t] +='],
  // plan.cpp dfs leaf: the gathering hold (gh) and the king-away penalty (kx)
  ['plan.cpp', `        if (goalOn_) v -= fGoal_ ? P::FG_W * std::max(0, std::min(goalDist_[t], 200) - P::FG_HOLD)   // stack5 F: hold the group
                                 : P::GATHER_W * std::min(goalDist_[t], 200);`,
               `        if (goalOn_) v -= fGoal_ ? P::FG_W * std::max(0, std::min(goalDist_[t], 200) - P::FG_HOLD)   // stack5 F: hold the group
                                 : P::GH_ON ? P::GATHER_W * std::max(0, std::min(goalDist_[t], 200) - P::GH_HOLD)   // stack11 gh: hold back at the king
                                 : P::GATHER_W * std::min(goalDist_[t], 200);
        if (kxOn_) v -= P::KX_W * std::max(0, P::KX_DIST - (int)kxDist_[t]);                        // stack11 kx: the king keeps away`],
  // plan.cpp dfs step: the pearl's value (not whether it is eaten)
  ['plan.cpp', '        double v = p * g - threatAt(u) * g - softPenalty_[u] * g - portalPenalty(t, d, u) * g;',
               '        double v = pearlValue(u, p) * g - threatAt(u) * g - softPenalty_[u] * g - portalPenalty(t, d, u) * g; // stack11 gh: pearlValue'],
  // plan.cpp computeKingAway and friends before pickHotspot
  ['plan.cpp', 'int Planner::pickHotspot() const {', PLAN_FUNCS],
  // plan.cpp decide(): the fields
  ['plan.cpp', '    computeSoftPenalty();\n    computeAttract();\n', '    computeSoftPenalty();\n    computeGhDrops();        // stack11 gh (before the attraction field)\n    computeAttract();\n'],
  ['plan.cpp', '    computeFountainGoal();   // stack5 F (only when no gathering goal is on)\n',
               '    computeFountainGoal();   // stack5 F (only when no gathering goal is on)\n    computeKingAway();       // stack11 kx\n'],
  // plan.cpp decide(): the late window's king class (lwk)
  ['plan.cpp', `        int kingLen = 0;
        for (auto& [id, d] : w_.dragons)
            if (id != w_.myId && d.team == w_.myTeam && d.headT >= 0 && w_.round - d.headSeen <= P::GATHER_KING_MEMORY)
                kingLen = std::max(kingLen, std::max(d.estLen, d.minLen));
        bool earlyOnlyKing = w_.round < P::FEED_FIRST_ROUND;`,
               `        // stack11 lwk: the late window feeds the king class too, with kingLen from news of the last LWK_KING_FRESH rounds
        const bool lwk = P::LWK_ON && w_.round >= P::FEED_FIRST_ROUND;
        int oldTo = -1, oldDist = 99;                // stack11 lwk: the nearest longer ally outside the king class (the old rule's choice)
        int kingLen = 0;
        for (auto& [id, d] : w_.dragons)
            if (id != w_.myId && d.team == w_.myTeam && d.headT >= 0 && w_.round - d.headSeen <= (lwk ? P::LWK_KING_FRESH : P::GATHER_KING_MEMORY))
                kingLen = std::max(kingLen, std::max(d.estLen, d.minLen));
        bool earlyOnlyKing = w_.round < P::FEED_FIRST_ROUND;`],
  ['plan.cpp', `            if (earlyOnlyKing && la < kingLen - 2) continue;
            if (w_.round < P::FEED_FIRST_ROUND) { // gathering: not into a king with an enemy head beside it (c10h)`,
               `            if (earlyOnlyKing && la < kingLen - 2) continue;
            const bool lwkOut = lwk && la < kingLen - 2;   // stack11 lwk: not the king class (the old late-window rule fed it)
            if (w_.round < P::FEED_FIRST_ROUND) { // gathering: not into a king with an enemy head beside it (c10h)`],
  ['plan.cpp', `            if (found < feedDist) { feedDist = found; feedTo = id; }
        }
        bool lateWindow = w_.round >= P::FEED_FIRST_ROUND && w_.round >= 500 - (w_.myLen + feedDist + P::FEED_SLACK);
        if (feedTo >= 0 && (lateWindow || (gathering && w_.unitCount >= P::GATHER_FEED_UNITS && w_.myLen >= P::GATHER_FEED_MIN_LEN))) {`,
               `            if (lwkOut) { if (found < oldDist) { oldDist = found; oldTo = id; } continue; } // stack11 lwk
            if (found < feedDist) { feedDist = found; feedTo = id; }
        }
        bool lateWindow = w_.round >= P::FEED_FIRST_ROUND && w_.round >= 500 - (w_.myLen + feedDist + P::FEED_SLACK);
        const bool feedNow = feedTo >= 0 && (lateWindow || (gathering && w_.unitCount >= P::GATHER_FEED_UNITS && w_.myLen >= P::GATHER_FEED_MIN_LEN));
        if (lwk && !feedNow && oldTo >= 0 && oldDist < 99) { // stack11 lwk: would the old rule (the nearest longer ally, any class) have fed?
            const int od = std::min(oldDist, feedDist);
            lwkHeld_ = w_.round >= 500 - (w_.myLen + od + P::FEED_SLACK) || (gathering && w_.unitCount >= P::GATHER_FEED_UNITS && w_.myLen >= P::GATHER_FEED_MIN_LEN);
        }
        if (feedNow) {`],
  // stack10 lnt's ram branch as a sub-toggle (coordinator 23:50, W11 verdict): LNT_RAM_ON guards lntRam() only, i.e. the ram-at-d3 >= +1 trade
  // value and its " lnt<d3>" tag; the veto (lntVeto, " lntv", kint >= 8 and r495 exceptions) is untouched. The identity copy keeps stack10's true.
  ['params.hpp', 'constexpr bool   LNT_ON = true;\n', 'constexpr bool   LNT_ON = true;\n' + `// stack11 (coordinator, W11 verdict): lnt's ram branch only (lntRam: ram an adjacent enemy head when locally ahead, d3 >= LNT_MIN_D3; tag
// " lnt<d3>"). false = those turns fall back to stack9's trade rules; the veto (" lntv", with the kint >= 8 and r495 exceptions) stays. true = stack10.
constexpr bool   LNT_RAM_ON = ${off ? 'true;             // identity copy: stack10\'s value' : 'false;            // W11 (2026-09-30 23:50): ram part off; online 46/52% pearl share, net20 −0.06 per trade; veto kept'}
`],
  ['plan.cpp', '    if (!P::LNT_ON || w_.myLen > P::LNT_MAX_LEN || w_.unitCount < P::LNT_MIN_UNITS) return false;\n', '    if (!P::LNT_ON || !P::LNT_RAM_ON || w_.myLen > P::LNT_MAX_LEN || w_.unitCount < P::LNT_MIN_UNITS) return false; // stack11: LNT_RAM_ON\n'],
  // lwkHeld_ is reset every turn (before the feed block)
  ['plan.cpp', '    bool gathering = w_.round >= P::GATHER_START;\n', '    bool gathering = w_.round >= P::GATHER_START;\n    lwkHeld_ = false;                                                                    // stack11 lwk\n'],
  // plan.cpp decide(): candidate values (first step, sprint, escape sprints)
  ['plan.cpp', '        c.base = p1 - th1 - softPenalty_[u1]', '        c.base = pearlValue(u1, p1) - th1 - softPenalty_[u1]'],
  ['plan.cpp', '                s.base = p1 + p2 - P::SPRINT_COST - th2', '                s.base = pearlValue(u1, p1) + pearlValue(u2, p2) - P::SPRINT_COST - th2'],
  ['plan.cpp', '                        s2.base = p1 + p2 - P::SPRINT_COST', '                        s2.base = pearlValue(u1, p1) + pearlValue(u2, p2) - P::SPRINT_COST'],
  ['plan.cpp', '                        s3.base = p1 + p2 + p3 - 2.0 * P::SPRINT_COST', '                        s3.base = pearlValue(u1, p1) + pearlValue(u2, p2) + pearlValue(u3, p3) - 2.0 * P::SPRINT_COST'],
  // plan.cpp decide(): the tags (move labels), before PROFILE
  ['plan.cpp', '    if (splitTailStop) act.indicator += " sx";    // stack4 split tail\n',
               `    if (splitTailStop) act.indicator += " sx";    // stack4 split tail
    // stack11 gh: " gh" on a gathering turn within GH_HOLD + 2 of the goal (the leaf penalty stops at GH_HOLD); " ghd@x,y" names the
    // nearest drop left to a longer ally within 3 steps of our head (headDist_: known edges, bodies ignored)
    if (P::GH_ON && goalOn_ && !fGoal_ && goalDist_[w_.headT] <= P::GH_HOLD + 2) act.indicator += " gh";
    if (ghOn_) {
        int bt = -1, bd = 4;
        for (int t : ghdTiles_) if (headDist_[t] >= 0 && headDist_[t] < bd) { bd = headDist_[t]; bt = t; }
        if (bt >= 0) { snprintf(buf, sizeof buf, " ghd@%d,%d", bt % w_.geo.W, bt / w_.geo.W); act.indicator += buf; }
    }
    // stack11 kx: " kx<d>" (path distance of the nearest enemy head seen within KX_STALE rounds, at our head); " kxm" when the move ends farther
    if (kxOn_) {
        snprintf(buf, sizeof buf, " kx%d", (int)kxDist_[w_.headT]); act.indicator += buf;
        if (!c.tiles.empty() && kxDist_[c.tiles.back()] > kxDist_[w_.headT]) act.indicator += " kxm";
    }
    if (lwkHeld_) act.indicator += " lwk";                                                      // stack11 lwk
`],
];

// the toggle list in the stack1 comment (stack10's wording if present)
const optional = [
  ['params.hpp', 'stack10: LNT_ON, UTAB_ON. M1 conv', 'stack10: LNT_ON, UTAB_ON; stack11: GH_ON, KX_ON, LWK_ON. M1 conv'],
  ['params.hpp', 'stack9: LSPLIT_ON, FRAG_CAP_CSPLIT_ON (and COV_ON on). M1 conv', 'stack9: LSPLIT_ON, FRAG_CAP_CSPLIT_ON (and COV_ON on); stack11: GH_ON, KX_ON, LWK_ON. M1 conv'],
];

const files = {};
const get = f => files[f] !== undefined ? files[f] : (files[f] = fs.readFileSync(path.join(dir, f), 'utf8'));
let bad = 0;
for (const [f, a, b] of edits) {
  const s = get(f), n = s.split(a).length - 1;
  if (n !== 1) { console.error(`${f}: anchor found ${n} times: ${JSON.stringify(a.slice(0, 90))}`); bad++; continue; }
  files[f] = s.replace(a, () => b);
}
let opt = 0;
for (const [f, a, b] of optional) { const s = get(f); if (s.split(a).length - 1 === 1) { files[f] = s.replace(a, () => b); opt++; break; } }
if (bad) { console.error(`${bad} anchors failed; nothing written`); process.exit(1); }
for (const [f, s] of Object.entries(files)) fs.writeFileSync(path.join(dir, f), s);
console.log(`applied ${edits.length} edits (+${opt} comment) to ${path.relative(process.cwd(), dir)}: GH_ON ${on('gh')}, KX_ON ${on('kx')}, LWK_ON ${on('lwk')}, LNT_RAM_ON ${off}`);
