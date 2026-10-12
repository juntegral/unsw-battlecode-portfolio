#!/usr/bin/env node
// cand-stack10 (research/experiments/cand-stack10.md): apply the lnt / utab edits to a copy of the base bot (stack9; stack8 for the early
// dev build). Every edit is an exact-string replacement whose anchor must occur exactly once, so a changed base fails loudly.
// usage: node exp/cand-stack10/apply.js <bot dir> [--off]     (--off: LNT_ON and UTAB_ON false, the identity copy)
'use strict';
const fs = require('fs'), path = require('path');
const dir = path.resolve(process.argv[2] || ''), off = process.argv.includes('--off');
if (!fs.existsSync(path.join(dir, 'plan.cpp'))) { console.error('usage: apply.js <bot dir> [--off]'); process.exit(2); }

const PARAMS = `// --- stack10 (2026-09-30): proposals 1 and 2 of the economy-principles study research/observations/economy-principles.md (section 14;
// 12,566 top-vs-top games + our 1,259 elite-set games), each with its own toggle and indicator tag (research/experiments/cand-stack10.md).
// With LNT_ON and UTAB_ON both false the bot plays exactly as stack9 (checked by replay event hashes on two local games).
// lnt (proposal 1: E4 + decision rule B3; ram4 redesigned): trade by local numbers. d3 = ally heads in view - (enemy heads in view - 1)
// (the 7x7 view, Chebyshev 3 of our head; a trade target is always in view). Top-vs-top, the rammer's team eats 41% of the two bodies'
// pearls within 20 rounds at d8 <= -3 and 77% at >= +3 (net20 -0.12 -> +2.20). In B3 situations (length <= 4, an enemy head adjacent)
// top winners ram 14% of the time at d3 <= -2, 65% at +1 and 73% at >= +2 (30 of 31 big teams alike), and those rams keep 24% -> 80% of
// the pearls. We trade 38% of the time at d8 <= -3 (winners 11%) and keep 38% of our trade pearls; ram4 (W1) rammed 17 times, 14 of them
// locally outnumbered, and kept 6 of 35 pearls (its collector rule only checked "not alone").
//   ram branch: our length <= LNT_MAX_LEN, an enemy head seen this round one step away across an open edge (portals included), team units
//     >= LNT_MIN_UNITS, not the king, d3 >= LNT_MIN_D3: the trade value is max(old rules, RAM_SMALL_VALUE + W_KILL x (its proven length -
//     ours)). It takes ram4's place: RAM_SMALL_ON stays false and ram4's collector rule is not used. Tag " lnt<d3>" on the TRADE label
//     (" lnt<d3>o" when the old rules would have traded too).
//   veto: d3 <= LNT_VETO_D3 zeroes the value of any trade (every length; one step, sprint, kill path, and the hunting pull of short
//     dragons), except when the target's proven length is >= LNT_KINT_MIN_LEN and longer than our longest known (the enemy's likely
//     longest: the study's kint exception; top winners' rams of the opponent's longest (>= 8) net +9.47 even when outnumbered), and from
//     ENDGAME_ANY_TRADE_ROUND. Tags: " lntv<d3>" on a move turn whose best trade the veto removed (its value without the veto beat the
//     chosen move's), " kint" on a TRADE the veto would have removed but for the kint exception.
constexpr bool   LNT_ON = ${off ? 'false' : 'true'};
constexpr int    LNT_MAX_LEN = 4;           // B3: length <= 4
constexpr int    LNT_MIN_D3 = 1;            // winners ram 65-73% from d3 = +1 (29% at 0)
constexpr int    LNT_VETO_D3 = -1;          // winners ram 14-16% at d3 <= -1, and such rams keep 24-35% of the pearls
constexpr int    LNT_MIN_UNITS = 3;         // keep two others alive
constexpr int    LNT_KINT_MIN_LEN = 8;      // the veto's exception: a target this long (proven) and longer than our longest known
constexpr bool   LNT_KINT_NEED_LONGEST = false; // W11 (coordinator 22:29): the exception covers any target of proven length >= LNT_KINT_MIN_LEN.
                                            // true = the study's rule (also longer than our longest known). Evidence, the primary sample: W5-W8
                                            // online (280 games), our TRADE kills at d3 <= -1 of targets >= 8 netted +4.93 each (30 trades),
                                            // of targets < 8 -0.18 (28); top winners' rams of the opponent's longest (>= 8) net +9.47 outnumbered
// utab (proposal 2, E3): csplit's unit target from a table of top winners' median dragon counts per recognised layout instead of map
// tiles / 45 (R^2 of winners' r100 count over 15 layouts: area 0.14, fountain tiles 0.42, natural spawn flow 0.85; the area target is off
// by >= 1.5x on 8 of 15 layouts). Before UTAB_EARLY_END the winners' r50 median, then their r100 median (plan.cpp UTAB); before this
// process decided the map and layout (World::mapIs) or on "map=none", the area formula. The table values are not clamped to the area
// formula's 8-40 (the 64-unit limit still applies). Only csplit's target changes: lsplit and fc (stack9) keep the area formula in their
// own code, so UTAB_ON and LSPLIT_ON / FRAG_CAP_CSPLIT_ON switch independently; they interact only through the units present at r250.
// Tag: the csplit label's "t<target>" is followed by " tab".
constexpr bool   UTAB_ON = false;          // W11 (coordinator 22:50): off. Primary sample W5-W8: outside Portals the table changes csplit's
                                            // permission in <= 13% of r1-249 rounds; units are limited by length and survival, not by the target
constexpr int    UTAB_EARLY_END = 50;       // winners' r50 median before this round, their r100 median from it
constexpr bool   UTAB_PORTALS = false;      // W11 (coordinator 22:29): Portals keeps the area target (11), as in stack9. true = the study's
                                            // table (26). Evidence (stack8-based dev build, 120 local games): on Portals the table doubled our
                                            // r100 units and portal 3-round body survival fell from 94% to 90% (protection floor 95%)

// --- search / budget ---`;

const PLAN_FUNCS = `// value of trading heads with this enemy this turn (0 = not allowed)
double Planner::tradeValue(int enemyId) const {
    double v = tradeValueBase(enemyId);
    if (smallRam(enemyId)) { // stack1 M2 (B3)
        int le = std::max(w_.dragons.at(enemyId).minLen, 2);
        v = std::max(v, P::RAM_SMALL_VALUE + P::W_KILL * (le - w_.myLen));
    }
    if (P::LNT_ON) { // stack10 lnt: ram when locally ahead, no trade when locally behind (params.hpp)
        if (lntRam(enemyId)) {
            int le = std::max(w_.dragons.at(enemyId).minLen, 2);
            v = std::max(v, P::RAM_SMALL_VALUE + P::W_KILL * (le - w_.myLen));
        } else if (v > 0.0 && lntVeto(enemyId)) v = 0.0;
    }
    return v;
}

// stack10 lnt: the trade value without the veto (tradeValue() as in stack9), for the " lntv" tag
double Planner::tradeValuePreVeto(int enemyId) const {
    double v = tradeValueBase(enemyId);
    if (smallRam(enemyId)) {
        int le = std::max(w_.dragons.at(enemyId).minLen, 2);
        v = std::max(v, P::RAM_SMALL_VALUE + P::W_KILL * (le - w_.myLen));
    }
    return v;
}

// stack10 lnt: local numbers in our 7x7 view (Chebyshev 3 of our head), the two dragons of the pair excluded: ally heads seen now (we
// are not in the list) minus enemy heads seen now other than the target. The study's d3 (economy-principles.md 2, extract.js v3).
int Planner::lntD3(int enemyId) const {
    int e = (int)w_.enemyHeadsNow.size();
    for (int id : w_.enemyHeadsNow) if (id == enemyId) { e--; break; }
    return (int)w_.allyHeadsNow.size() - e;
}

// stack10 lnt ram branch: a piece (length <= LNT_MAX_LEN, team units >= LNT_MIN_UNITS, not the king) with an enemy head seen this round
// one step away across an open edge (portals included), locally ahead (d3 >= LNT_MIN_D3). The study's "proven length >= 2" holds for
// every dragon (max(minLen, 2)); the king rule (KING_MIN_LEN and our longest) cannot bind at LNT_MAX_LEN 4 and guards a later raise.
bool Planner::lntRam(int enemyId) const {
    if (!P::LNT_ON || w_.myLen > P::LNT_MAX_LEN || w_.unitCount < P::LNT_MIN_UNITS) return false;
    if (w_.iAmLongest() && w_.myLen >= P::KING_MIN_LEN) return false;
    auto it = w_.dragons.find(enemyId);
    if (it == w_.dragons.end()) return false;
    const Dragon& d = it->second;
    if (d.team == w_.myTeam || d.headT < 0 || d.headSeen != w_.round) return false;
    bool adjacent = false;
    for (int dir = 0; dir < 4; dir++) if (w_.across(w_.headT, dir) == d.headT) adjacent = true;
    return adjacent && lntD3(enemyId) >= P::LNT_MIN_D3;
}

// stack10 lnt veto's exception (the study's kint): the target's proven length is >= LNT_KINT_MIN_LEN and longer than our longest known
bool Planner::lntKint(int enemyId) const {
    auto it = w_.dragons.find(enemyId);
    if (it == w_.dragons.end()) return false;
    int le = std::max(it->second.minLen, 2);
    return le >= P::LNT_KINT_MIN_LEN && (!P::LNT_KINT_NEED_LONGEST || le > w_.teamLongestKnown());
}

// stack10 lnt veto: locally behind (d3 <= LNT_VETO_D3), before ENDGAME_ANY_TRADE_ROUND, and not the kint exception
bool Planner::lntVeto(int enemyId) const {
    if (!P::LNT_ON || w_.round >= P::ENDGAME_ANY_TRADE_ROUND) return false;
    return lntD3(enemyId) <= P::LNT_VETO_D3 && !lntKint(enemyId);
}

// stack10 lnt: a trade candidate the veto removed, worth pre - cost without the veto (pre <= 0: it was no trade anyway)
void Planner::lntVetoNote(double pre, double cost, int enemyId) {
    if (pre <= 0.0) return;
    if (pre - cost > lntVetoBest_) { lntVetoBest_ = pre - cost; lntVetoD3_ = lntD3(enemyId); }
}`;

const OLD_TRADEVALUE = `// value of trading heads with this enemy this turn (0 = not allowed)
double Planner::tradeValue(int enemyId) const {
    double v = tradeValueBase(enemyId);
    if (smallRam(enemyId)) { // stack1 M2 (B3)
        int le = std::max(w_.dragons.at(enemyId).minLen, 2);
        v = std::max(v, P::RAM_SMALL_VALUE + P::W_KILL * (le - w_.myLen));
    }
    return v;
}`;

const UTAB_FUNC = `// stack10 utab (economy-principles study 7 and 14, proposal 2): top winners' median dragon count per recognised layout (mapdb family name,
// layout) at r50 and at r100, csplit's target instead of map tiles / 45 once this process decided the map and its layout
struct UTabRow { const char* fam; char lay; int r50, r100; };
static const UTabRow UTAB[] = {
    {"Autarky", 'a', 17, 23}, {"Default", 'a', 11, 19}, {"Devil", 'a', 16, 30}, {"Devil", 'b', 12, 24}, {"Portals", 'a', 14, 26},
    {"Prisoners_Dilemma", 'a', 9, 13}, {"Prisoners_Dilemma", 'b', 9, 15}, {"Queen_Of_Spades", 'a', 7, 13}, {"Queen_Of_Spades", 'b', 7, 12},
    {"Schooltime", 'a', 13, 44}, {"Schooltime", 'b', 8, 16}, {"Slithery_Fight", 'a', 47, 62}, {"Slithery_Fight", 'b', 43, 55},
    {"Trauma", 'a', 7, 16}, {"Trophy", 'a', 15, 31},
};
int Planner::utabTarget() const {
    if (!P::UTAB_PORTALS && w_.mapFamIs("Portals")) return -1;
    for (const UTabRow& u : UTAB) if (w_.mapIs(u.fam, u.lay)) return w_.round < P::UTAB_EARLY_END ? u.r50 : u.r100;
    return -1;
}

// stack5 csplit: childSafe() without its "no enemy head in view" rule.`;

const EDITS = [
  ['params.hpp', '// --- search / budget ---', PARAMS],
  ['params.hpp', '. M1 conv (R3/K1, mass ledger H1)', '; stack10: LNT_ON, UTAB_ON. M1 conv (R3/K1, mass ledger H1)'],
  ['plan.hpp', '    int pickHotspot() const;\n};', `    int pickHotspot() const;
    // stack10 lnt / utab
    double lntVetoBest_ = -1e18;                // lnt: this turn's best trade candidate value the veto removed (for the " lntv" tag)
    int lntVetoD3_ = 0;                         // lnt: its d3
    mutable bool csplitTab_ = false;            // utab: this turn's csplit target came from the layout table
    int lntD3(int enemyId) const;               // ally heads in view - (enemy heads in view other than the target)
    bool lntRam(int enemyId) const;             // the ram branch applies to this adjacent enemy head
    bool lntKint(int enemyId) const;            // the veto's exception: the target may be the enemy's longest
    bool lntVeto(int enemyId) const;            // the veto applies to a trade with this enemy
    double tradeValuePreVeto(int enemyId) const;// the trade value without the veto (the " lntv" tag)
    void lntVetoNote(double pre, double cost, int enemyId); // a vetoed trade candidate worth pre - cost without the veto
    int utabTarget() const;                     // utab: the table target for this round, -1 if the layout is not decided
};`],
  ['plan.cpp', OLD_TRADEVALUE, PLAN_FUNCS],
  ['plan.cpp', `    csplitTarget_ = std::clamp(w_.geo.tiles() / P::CSPLIT_TILES_PER_UNIT, P::CSPLIT_TARGET_MIN, P::CSPLIT_TARGET_MAX);
    if (w_.unitCount >= std::min(w_.unitLimit, csplitTarget_)) return false;`,
   `    csplitTarget_ = std::clamp(w_.geo.tiles() / P::CSPLIT_TILES_PER_UNIT, P::CSPLIT_TARGET_MIN, P::CSPLIT_TARGET_MAX);
    csplitTab_ = false;
    if (P::UTAB_ON) { int tt = utabTarget(); if (tt > 0) { csplitTarget_ = tt; csplitTab_ = true; } } // stack10 utab: the layout table
    if (w_.unitCount >= std::min(w_.unitLimit, csplitTarget_)) return false;`],
  ['plan.cpp', '// stack5 csplit: childSafe() without its "no enemy head in view" rule.', UTAB_FUNC],
  ['plan.cpp', `    std::vector<Cand> cands;
    std::vector<int> path;
    for (int d1 = 0; d1 < 4; d1++) {`, `    std::vector<Cand> cands;
    std::vector<int> path;
    lntVetoBest_ = -1e18; lntVetoD3_ = 0;                                                  // stack10 lnt
    for (int d1 = 0; d1 < 4; d1++) {`],
  ['plan.cpp', `            double tv = tradeValue(hid);
            c.tiles = {u1}; c.legal = tv > 0.0; c.trade = true; c.base = tv > 0.0 ? tv : DEATH;
            cands.push_back(c); continue;`, `            double tv = tradeValue(hid);
            c.tiles = {u1}; c.legal = tv > 0.0; c.trade = true; c.base = tv > 0.0 ? tv : DEATH;
            if (P::LNT_ON && tv <= 0.0) lntVetoNote(tradeValuePreVeto(hid), 0.0, hid);         // stack10 lnt
            cands.push_back(c); continue;`],
  ['plan.cpp', `                    if (tv > 0.0) { s.tiles = {u1, u2}; s.legal = true; s.trade = true; s.base = tv - P::SPRINT_COST; cands.push_back(s); }
                    continue;`, `                    if (tv > 0.0) { s.tiles = {u1, u2}; s.legal = true; s.trade = true; s.base = tv - P::SPRINT_COST; cands.push_back(s); }
                    else if (P::LNT_ON) lntVetoNote(tradeValuePreVeto(hid2), P::SPRINT_COST, hid2);    // stack10 lnt
                    continue;`],
  ['plan.cpp', `        for (int id : w_.enemyHeadsNow) {
            double tv = tradeValue(id);
            if (tv <= 0.0) continue;`, `        for (int id : w_.enemyHeadsNow) {
            double tv = tradeValue(id);
            double tvPre = P::LNT_ON && tv <= 0.0 ? tradeValuePreVeto(id) : tv; // stack10 lnt: a vetoed target's path is searched for the " lntv" tag
            if (tvPre <= 0.0) continue;`],
  ['plan.cpp', `                std::reverse(dirs.begin(), dirs.end()); std::reverse(tiles.begin(), tiles.end());
                Cand c; c.dirs = dirs; c.tiles = tiles; c.legal = true; c.trade = true; c.blind = false;`,
   `                std::reverse(dirs.begin(), dirs.end()); std::reverse(tiles.begin(), tiles.end());
                if (tv <= 0.0) { lntVetoNote(tvPre, ((int)dirs.size() - 1) * P::SPRINT_COST, id); continue; } // stack10 lnt: vetoed
                Cand c; c.dirs = dirs; c.tiles = tiles; c.legal = true; c.trade = true; c.blind = false;`],
  ['plan.cpp', `"csplit%d u%d L%d t%d%s%s", splitSize, w_.unitCount, w_.myLen, csplitTarget_,`,
   `"csplit%d u%d L%d t%d%s%s%s", splitSize, w_.unitCount, w_.myLen, csplitTarget_, csplitTab_ ? " tab" : "",`],
  ['plan.cpp', `            act.indicator += coll ? " c1" : " c0";
        }
    }`, `            act.indicator += coll ? " c1" : " c0";
        }
    }
    // stack10 lnt: " lnt<d3>" (+ "o" when the old rules would have traded too) on a one-step TRADE the ram branch allowed; " kint" on a
    // TRADE the veto would have removed but for its exception; " lntv<d3>" on a move turn whose best trade candidate the veto removed
    if (P::LNT_ON) {
        if (c.trade && !c.tiles.empty()) {
            int hid = w_.headOf[c.tiles.back()];
            if (hid >= 0 && c.dirs.size() == 1 && lntRam(hid)) {
                snprintf(buf, sizeof buf, " lnt%+d%s", lntD3(hid), tradeValuePreVeto(hid) > 0.0 ? "o" : ""); act.indicator += buf;
            } else if (hid >= 0 && w_.round < P::ENDGAME_ANY_TRADE_ROUND && lntD3(hid) <= P::LNT_VETO_D3 && lntKint(hid)) act.indicator += " kint";
        } else if (!c.trade && lntVetoBest_ > value[best]) { snprintf(buf, sizeof buf, " lntv%+d", lntVetoD3_); act.indicator += buf; }
    }`],
];

const text = {};
for (const [f, anchor, repl] of EDITS) {
  if (!(f in text)) text[f] = fs.readFileSync(path.join(dir, f), 'utf8');
  const n = text[f].split(anchor).length - 1;
  if (n !== 1) { console.error(`${f}: anchor found ${n} times (need 1): ${anchor.slice(0, 80).replace(/\n/g, '\\n')}`); process.exit(1); }
  text[f] = text[f].replace(anchor, () => repl);
}
for (const [f, t] of Object.entries(text)) fs.writeFileSync(path.join(dir, f), t);
console.log(`applied ${EDITS.length} edits to ${path.relative(process.cwd(), dir)}${off ? ' (LNT_ON, UTAB_ON false)' : ''}`);
