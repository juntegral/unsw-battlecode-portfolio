#!/usr/bin/env node
// cand-stack12 (research/experiments/cand-stack12.md): apply the pf edits (piece-first opening; intake-gap study
// research/observations/intake-gap.md section 13, proposal 1) to a copy of the base bot (stack11; stack10 for the early dev build).
// Every edit is an exact-string replacement whose anchor must occur exactly once, so a changed base fails loudly.
// usage: node exp/cand-stack12/apply.js <bot dir> [--off]
//   --off   PF_ON false (the identity copy: must play exactly as the base)
'use strict';
const fs = require('fs'), path = require('path');
const dir = path.resolve(process.argv[2] || ''), off = process.argv.includes('--off');
if (!fs.existsSync(path.join(dir, 'plan.cpp'))) { console.error('usage: apply.js <bot dir> [--off]'); process.exit(2); }

const PARAMS = `// --- stack12 (2026-10-01): proposal 1 of the intake-gap study research/observations/intake-gap.md (section 13; our 1,540 elite-set
// games + 14,169 top-vs-top games), with its own toggle and indicator tag (research/experiments/cand-stack12.md). With PF_ON false the bot
// plays exactly as stack11 (checked by replay event hashes on two local games).
// On 500-round maps our natural-pearl intake trails the elite opponent's by 514 a game, and 511 of it is head count (view B: head-rounds x
// per-head rate; the rate term is 3). We hold r10 5.9 / r50 8.0 / r100 12.1 / r250 16.2 dragons against 9.4 / 20.1 / 35.1 / 51.3, because
// we split slowly: excluding escape splits, 0.08 / 0.07 new heads per length >= 4 head-round in r0-49 / r50-99 on open 500-round maps
// (elite 0.64 / 0.39), and we keep the long start dragon (Slithery Fight longest 23 at r10 and at r100; elite 7.7 at r10). On elimination
// maps the gap is 193.5 pearls, 190.7 of it head count.
// pf (piece-first opening): in rounds PF_START..PF_END-1 on the recognised pf maps (pfMapOn: Slithery Fight, Schooltime, Trauma, Default,
//   Devil, Queen Of Spades, Trophy; World::mapFamIs, off before recognition and on "map=none"; off on Autarky, Prisoners Dilemma (6 and 10
//   dragons) and Portals, where decision rule E1 is a "keep": early splits were worse there), while the team has fewer units (UNIT_COUNT)
//   than the pf target (pfTarget(): top winners' mean r100 dragon count of the recognised layout, the family's before this process decided
//   the layout, at most unitLimit - PF_HEADROOM), a dragon of length >= PF_MIN_LEN splits off a PF_CHILD child, at most once in PF_GAP
//   rounds per dragon. Neither csplit's king rule (a dragon of length >= KING_MIN_LEN splits only when it knows a longer ally) nor its E1
//   start block (seedMap_: no csplit before r50 on maps that start with a long dragon or many) applies: the Slithery Fight start dragon (L25)
//   is split too. The child's spot is csplit's (csplitChildSafe(CSPLIT_TAIL_DIST, SPLIT_MIN_CHILD_EXITS): a known, open tail seen this or
//   last round, >= 2 exits, no enemy head within 2 of it) plus room (pfRoomOk(): >= PF_ROOM free tiles reachable from our tail, none of them
//   within one step of a known enemy head), and the move gate of every split stays (no pearl on the best first step, the best move
//   unthreatened and safe, no enemy head within 2 of our head).
// Precedence in decide(): policy split -> frag -> bsp -> pf -> csplit -> kcap -> floor -> lsplit. One split per turn and one tag per split.
//   pf supersedes csplit while it owns the turn (pfOwns_: PF_ON, a pf map, the pf window, units < pf target): csplit does not split then,
//   and a pf split restarts csplit's CSPLIT_GAP clock too (lastCsplitRound_), so the two never split one dragon in quick succession. csplit
//   takes over from PF_END, and above the pf target where csplit's is higher (Default, Queen Of Spades, Trauma, Schooltime b). kcap and
//   floor keep their place and gates (the low-unit rescue rules: inside the pf window they act only on turns pf leaves, its 2-round gap or a
//   1-exit child spot, and only while units < 6 / <= 3). frag and lsplit start at r250; bsp (Schooltime b, no enemy head in view) stays first.
// Tag "pf<n> u<units> L<len> t<target>" (+ " f" when the target is the family's (layout not decided yet), + " v" with an enemy head in view,
//   + " k" when we believe we are the longest). On a move turn: " pfx" when pf chose to split but the move gate kept the dragon moving,
//   " pfc" when pf owned the turn and the dragon could split (length, gap) but the child's spot failed.
constexpr bool   PF_ON = ${off ? 'false' : 'true'};
constexpr int    PF_START = 1;              // not in round 0 (csplit's CSPLIT_START: every start dragon sees the team's start count)
constexpr int    PF_END = 100;              // r1-99: the head gap opens in the first 100 rounds and does not close (study 3)
constexpr int    PF_MIN_LEN = 4;            // PF_CHILD + PF_KEEP: 4 -> 2 + 2
constexpr int    PF_CHILD = 2;              // top winners' children are length 2 in 76-77%
constexpr int    PF_KEEP = 2;               // the parent keeps at least this length
constexpr int    PF_GAP = 2;                // rounds between two pf splits of one dragon (elite length >= 4 dragons split every 1.6-2.6 rounds in r0-99)
constexpr int    PF_HEADROOM = 8;           // the target stays <= unitLimit - PF_HEADROOM (56): our escape splits (Slithery Fight 64.7 a game)
                                            // need room under the 64-unit limit (px8: trapped kings at 62-63 units; csplit's clamp keeps 24)
constexpr int    PF_ROOM = 8;               // coordinator 00:05: the child's spot also needs this many free tiles reachable from our tail (not
                                            // within one step of a known enemy head, bounded flood fill); W10 lsplit children died trapped in 49%

// --- search / budget ---`;

const HPP_MEMBERS = `    int lastLsplitRound_ = -1000;      // lsplit: our last late re-split
    // stack12 pf (params.hpp stack12 section)
    int lastPfRound_ = -1000;          // pf: our last piece-first split
    mutable int pfTarget_ = 0;         // pf: this turn's unit target (for the tag)
    mutable bool pfFam_ = false;       // pf: the target is the family's (this process has not decided the layout yet)
    mutable bool pfOwns_ = false;      // pf: this turn is pf's (a pf map, the pf window, units < target), so csplit stands aside
    mutable int pfWhy_ = 0;            // pf: 3 when pf owned the turn and the dragon could split but the child's spot failed (" pfc")
`;
const HPP_DECL = `    bool wantLsplit(int& size) const;           // stack9 lsplit (late re-split of a length 4-6 dragon)
    bool pfMapOn() const;                       // stack12 pf: this process recognised a map family where pf is on
    int pfTarget() const;                       // stack12 pf: the unit target of the recognised layout (the family's before), -1 off
    bool wantPf(int& size) const;               // stack12 pf (piece-first opening)
    bool pfRoomOk() const;                      // stack12 pf: >= PF_ROOM free tiles reachable from our tail (the child's room)
`;

const CPP_FUNCS = `// stack12 pf (intake-gap study 13, proposal 1): the maps where pf is on, as this process recognised the family (off before recognition and on
// "map=none"). Off on Autarky, Prisoners Dilemma (6 and 10 dragons) and Portals: decision rule E1 ("r < 50, length >= 4: split") is a keep there
// (hypotheses-stack6-20260930.md), early splits cost family length, and our corridor structure wins those maps.
bool Planner::pfMapOn() const {
    for (const char* f : {"Slithery_Fight", "Schooltime", "Trauma", "Default", "Devil", "Queen_Of_Spades", "Trophy"})
        if (w_.mapFamIs(f)) return true;
    return false;
}

// stack12 pf: top winners' mean r100 dragon count (intake-gap study 13): the recognised layout's, the family's before this process decided
// the layout (World::mapIs), capped at unitLimit - PF_HEADROOM; -1 when pf is off on this map
struct PfRow { const char* fam; int fam100, a100, b100; };
static const PfRow PF_TAB[] = {
    {"Slithery_Fight", 57, 60, 54}, {"Schooltime", 30, 44, 16}, {"Trauma", 18, 18, 18}, {"Default", 19, 19, 19},
    {"Devil", 26, 29, 23}, {"Queen_Of_Spades", 13, 13, 12}, {"Trophy", 31, 31, 31},
};
int Planner::pfTarget() const {
    pfFam_ = false;
    for (const PfRow& r : PF_TAB) {
        if (!w_.mapFamIs(r.fam)) continue;
        int t = r.fam100;
        if (w_.mapIs(r.fam, 'a')) t = r.a100; else if (w_.mapIs(r.fam, 'b')) t = r.b100; else pfFam_ = true;
        return std::min(t, w_.unitLimit - P::PF_HEADROOM);
    }
    return -1;
}

// stack12 pf (intake-gap study 13, proposal 1): in rounds PF_START..PF_END-1 on the pf maps, while the team has fewer units than the pf target,
// a dragon of length >= PF_MIN_LEN splits off a PF_CHILD piece, at most once in PF_GAP rounds. Our dragons hold a third of the elite's heads
// from r50 on, and we split 0.08 times per length >= 4 head-round in r0-49 (elite 0.64). Neither csplit's king rule nor its E1 start block
// (seedMap_) applies; the child's spot is csplit's. pfOwns_: the map, window and target hold, so the turn is pf's and csplit stands aside.
bool Planner::wantPf(int& size) const {
    pfOwns_ = false; pfWhy_ = 0;
    if (!P::PF_ON || w_.round < P::PF_START || w_.round >= P::PF_END || !pfMapOn()) return false;
    pfTarget_ = pfTarget();
    if (pfTarget_ <= 0 || w_.unitCount >= std::min(w_.unitLimit, pfTarget_)) return false;
    pfOwns_ = true;
    int L = w_.myLen;
    if (L < P::PF_MIN_LEN || w_.round - lastPfRound_ < P::PF_GAP) return false;
    size = P::PF_CHILD;
    if (L - size < P::PF_KEEP) return false;
    if (!csplitChildSafe(P::CSPLIT_TAIL_DIST, P::SPLIT_MIN_CHILD_EXITS) || !pfRoomOk()) { pfWhy_ = 3; return false; }
    return true;
}

// stack12 pf: the child's room. From the child's head (our tail): the tiles free now (no dragon), reached over edges that are not kelp and not an
// unexplored portal, and not within one step of a known enemy head (the child-spot field of csplitChildSafe), counted by a flood fill that
// stops at PF_ROOM. A child born into a smaller pocket is likely to die trapped (W10: 49% of lsplit children).
bool Planner::pfRoomOk() const {
    int L = w_.myLen; if ((int)w_.body.size() < L || L < 2) return false;
    int tail = w_.body[L - 1]; if (tail < 0) return false;
    const std::vector<int16_t>& ed = P::TG_ON ? enemyDistOld_ : enemyDist_;
    int q[P::PF_ROOM + 8]; int qn = 0, found = 0; q[qn++] = tail;
    for (int i = 0; i < qn && found < P::PF_ROOM; i++) {
        for (int d = 0; d < 4 && found < P::PF_ROOM; d++) {
            int u = w_.across(q[i], d);
            if (u < 0 || w_.occNow[u] != 0 || ed[u] <= 1) continue;
            bool dup = false; for (int j = 0; j < qn; j++) if (q[j] == u) { dup = true; break; }
            if (dup) continue;
            q[qn++] = u; found++;
        }
    }
    return found >= P::PF_ROOM;
}

// stack5 F / cov: our side`;

const edits = [
  // params: the stack12 section before the search / budget block
  ['params.hpp', '// --- search / budget ---', PARAMS],
  // plan.hpp: members and declarations
  ['plan.hpp', '    int lastLsplitRound_ = -1000;      // lsplit: our last late re-split\n', HPP_MEMBERS],
  ['plan.hpp', '    bool wantLsplit(int& size) const;           // stack9 lsplit (late re-split of a length 4-6 dragon)\n', HPP_DECL],
  // plan.cpp: the pf functions after wantLsplit (before the F / cov side helpers)
  ['plan.cpp', '// stack5 F / cov: our side', CPP_FUNCS],
  // plan.cpp: per-turn reset
  ['plan.cpp', '    splitTailBlocked_ = false; splitTailDist_ = 99; // stack4 split tail\n',
               '    splitTailBlocked_ = false; splitTailDist_ = 99; // stack4 split tail\n    pfOwns_ = false; pfWhy_ = 0;                    // stack12 pf\n'],
  // plan.cpp: the split chain (pf after bsp, before csplit; csplit stands aside while pf owns the turn)
  ['plan.cpp', 'bool frag = false, csplit = false, bsplit = false, kcap = false, floorSp = false, lsplit = false;',
               'bool frag = false, csplit = false, bsplit = false, kcap = false, floorSp = false, lsplit = false, pf = false, pfGateStop = false; // pf: stack12'],
  ['plan.cpp', '(bsplit = wantBSplit(splitSize)) || (csplit = wantCsplit(splitSize)) ||',
               '(bsplit = wantBSplit(splitSize)) || (pf = wantPf(splitSize)) || (!pfOwns_ && (csplit = wantCsplit(splitSize))) ||'],
  ['plan.cpp', '            if (csplit) lastCsplitRound_ = w_.round;\n',
               '            if (csplit) lastCsplitRound_ = w_.round;\n            if (pf) { lastPfRound_ = w_.round; lastCsplitRound_ = w_.round; }                     // stack12 pf: csplit\'s clock too\n'],
  ['plan.cpp', '            if (lsplit) snprintf(buf, sizeof buf, "lsplit%d u%d L%d t%d", splitSize, w_.unitCount, w_.myLen, lsplitTarget_); // stack9 lsplit\n',
               '            if (lsplit) snprintf(buf, sizeof buf, "lsplit%d u%d L%d t%d", splitSize, w_.unitCount, w_.myLen, lsplitTarget_); // stack9 lsplit\n' +
               '            if (pf) snprintf(buf, sizeof buf, "pf%d u%d L%d t%d%s%s%s", splitSize, w_.unitCount, w_.myLen, pfTarget_, pfFam_ ? " f" : "",\n' +
               '                             w_.enemyHeadsNow.empty() ? "" : " v", w_.iAmLongest() ? " k" : "");                  // stack12 pf\n'],
  // plan.cpp: pf chose to split but the move gate kept the dragon moving
  ['plan.cpp', '            return act;\n        }\n    }\n    // stack4 split tail: " sx" when the tail rule alone stopped a policy split',
               '            return act;\n        }\n        if (pf) pfGateStop = true;                                                                 // stack12 pf: " pfx"\n    }\n    // stack4 split tail: " sx" when the tail rule alone stopped a policy split'],
  // plan.cpp: the move-label tags
  ['plan.cpp', '    if (gxOff_) act.indicator += " gx";',
               '    if (pfGateStop) act.indicator += " pfx"; else if (pfWhy_ == 3) act.indicator += " pfc";      // stack12 pf\n    if (gxOff_) act.indicator += " gx";'],
];

// the toggle list in the stack1 comment
const optional = [
  ['params.hpp', 'stack11: GH_ON, KX_ON, LWK_ON. M1 conv', 'stack11: GH_ON, KX_ON, LWK_ON; stack12: PF_ON. M1 conv'],
  ['params.hpp', 'stack10: LNT_ON, UTAB_ON. M1 conv', 'stack10: LNT_ON, UTAB_ON; stack12: PF_ON. M1 conv'],
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
console.log(`applied ${edits.length} edits (+${opt} comment) to ${path.relative(process.cwd(), dir)}: PF_ON ${!off}`);
