// opmod.cpp — unsw-swarm v1.4: the opening module (params.hpp v1.4 section, opdb.hpp; versions/v1.4/VERSION.md).
// A SWARM-engine process (decideImpl<2>) that recognised a scripted family finds its role in the script of the recognised layout (layout a while
// the layout is not decided) by its birth: round, head tile and length (a start dragon: its start; a round-0 child: its birth at the old tail).
// While the script steers it, it takes the role's scheduled splits first (the split chain's first rule; the explosion and re-split wait while it
// is pulled to a waypoint) and the search leaf pulls to the role's next waypoint instead of the sd target. It hands back to v1.2's rules for good
// when the script ends, at the last waypoint, or on a deviation (params.hpp: contact, blocked or late, a dragon of ours lost). Maps without a
// script and processes without a role never reach any of this.
#include <algorithm>
#include <cstdio>

#include "opdb.hpp"
#include "plan.hpp"

namespace seed0 {

void Planner::opUpdate() {
    opActive_ = false; opPull_ = false; opWpT_ = -1; opWpR_ = -1; opWpD_ = -1; opEndedNow_ = false;
    const int prevUnits = opPrevUnits_;
    opPrevUnits_ = w_.unitCount;
    if (opDone_) return;
    auto stop = [&](char why) { opDone_ = true; opWhy_ = why; opEndedNow_ = true; };
    // the script and our role, looked up again when the recognition state changes (the layout decided later: the same births)
    const int key = w_.mapStateCode();
    if (key != opKey_) {
        opKey_ = key; opScript_ = nullptr; opRole_ = -1;
        bool fam = false;
        if (!w_.mapNone && w_.mapFam >= 0 && homeT_ >= 0) {
            const char lay = w_.mapIdx >= 0 ? w_.mapLayout : 'a';
            for (int i = 0; i < opdb::COUNT && !opScript_; i++) {
                const opdb::Script& s = opdb::SCRIPTS[i];
                if (!w_.mapFamIs(s.fam)) continue;
                fam = true;
                if (s.layout != lay) continue;
                for (int k = 0; k < s.nRoles; k++) {
                    const opdb::Role& r = s.roles[k];
                    if (r.born == w_.birthRound && r.len == w_.birthLen && w_.geo.idx(r.x, r.y) == homeT_) { opScript_ = &s; opRole_ = k; break; }
                }
            }
        }
        opFam_ = fam;                                      // the hold phase (OP_HOLD_ON) runs on scripted families only
        if (!opScript_) { if (fam) stop('n'); return; }   // a scripted family, but no role for this birth: v1.2 from now on
    }
    if (!opScript_) return;
    const opdb::Script& s = *opScript_;
    const opdb::Role& r = s.roles[opRole_];
    if (w_.round > s.endR) return stop('e');
    if (enemyDist_[w_.headT] <= P::OP_CONTACT) return stop('c');
    if (s.lossStops && prevUnits > 0 && w_.unitCount < prevUnits) return stop('u');
    bool splitsLeft = false;
    for (int i = 0; i < r.nSplit; i++) if (!(opSplitDone_ & (1u << i)) && w_.round <= r.split[i].r + P::OP_SPLIT_LATE) splitsLeft = true;
    // the waypoint: the role's first waypoint at least OP_AHEAD rounds ahead that we have not reached (path distance over known edges, bodies
    // ignored); after the last one's round, the last one. The leaf sits DFS_DEPTH_MIN..DFS_DEPTH_MAX + 1 steps ahead, so a waypoint nearer
    // than that does not tell the first steps apart (every branch reaches it within the search): the pull looks ahead to where the medoid was
    // about OP_AHEAD..OP_AHEAD + 5 rounds from now.
    const int n = w_.geo.tiles();
    int k = -1, dk = 9999;
    for (int i = 0; i < r.nWp; i++) {
        const opdb::Wp& p = r.wp[i];
        if (p.r < w_.round + P::OP_AHEAD && i + 1 < r.nWp) continue;
        if (p.r <= w_.round) continue;
        const int t = w_.geo.idx(p.x, p.y);
        opDist_.assign(n, 9999);
        queue_.clear(); queue_.push_back(t); opDist_[t] = 0;
        for (size_t qi = 0; qi < queue_.size(); qi++) {
            const int u = queue_[qi];
            for (int dir = 0; dir < 4; dir++) {
                const int v = w_.across(u, dir);
                if (v < 0 || opDist_[v] <= opDist_[u] + 1) continue;
                opDist_[v] = opDist_[u] + 1; queue_.push_back(v);
            }
        }
        if (opDist_[w_.headT] <= P::OP_REACHED) continue;   // reached ahead of schedule: the next one pulls
        k = i; dk = opDist_[w_.headT];
        break;
    }
    if (k < 0) {
        if (r.nWp > 0 && !splitsLeft) return stop('a');     // the last waypoint reached (or passed) and no split left: arrived
        if (r.nWp == 0 && !splitsLeft) return stop('e');    // a split-only role with nothing left
    } else {
        opWpT_ = w_.geo.idx(r.wp[k].x, r.wp[k].y); opWpR_ = r.wp[k].r; opWpD_ = dk;
        if (dk >= 9999) return stop('b');
        if (dk > opWpR_ - w_.round + P::OP_LATE) return stop('l');
        opPull_ = s.pull;
    }
    opActive_ = true;
}

// a scheduled split of our role is due: round in [r, r + OP_SPLIT_LATE] (later: dropped), the child length the script's (at most our length - 2,
// at least 2), a free unit, and a free tile beside our tail that is not our neck (the child is born at our tail and moves later this round)
bool Planner::opWantSplit(int& size) {
    if (!opActive_) return false;
    const opdb::Role& r = opScript_->roles[opRole_];
    for (int i = 0; i < r.nSplit; i++) {
        if (opSplitDone_ & (1u << i)) continue;
        const opdb::Split& s = r.split[i];
        if (w_.round < s.r) break;
        if (w_.round > s.r + P::OP_SPLIT_LATE) { opSplitDone_ |= 1u << i; continue; }
        const int L = w_.myLen, c = std::min<int>(s.child, L - 2);
        if (c < 2 || w_.unitCount >= w_.unitLimit || (int)w_.body.size() < L) return false;
        const int tail = w_.body[L - 1], neck = w_.body[L - 2];
        if (tail < 0) return false;
        int exits = 0;
        for (int d = 0; d < 4; d++) { const int u = w_.across(tail, d); if (u >= 0 && u != neck && w_.occNow[u] == 0) exits++; }
        if (exits == 0) return false;
        size = c; opSplitIdx_ = i;
        return true;
    }
    return false;
}

// the explosion (sx) and the re-split (sr) wait while the script pulls this dragon to a waypoint (the elite parents split at the middle)
bool Planner::opHoldSplits() const { return opActive_ && opPull_; }

// " op<role>" on a turn the script steers (+ ">x,y d<dist>" while it pulls), " opx<why>" once on the turn it hands back
std::string Planner::opTag() const {
    char buf[64];
    if (opActive_ && opScript_) {
        const opdb::Role& r = opScript_->roles[opRole_];
        if (opPull_ && opWpT_ >= 0) snprintf(buf, sizeof buf, " op%s>%d,%d d%d", r.label, opWpT_ % w_.geo.W, opWpT_ / w_.geo.W, opWpD_);
        else snprintf(buf, sizeof buf, " op%s", r.label);
        return buf;
    }
    if (opEndedNow_ && opWhy_) { snprintf(buf, sizeof buf, " opx%c", opWhy_); return buf; }
    return "";
}

std::string Planner::opSplitTag() const {
    char buf[40];
    snprintf(buf, sizeof buf, " op%ss", opScript_ ? opScript_->roles[opRole_].label : "?");
    return buf;
}

// ------------------------------------------------------------------------------------------------
// v1.4 §7 the hold phase (params.hpp OP_HOLD_ON / OP_HOLD_ALL): the elite winners keep the middle bin after r25 (Devil a 54% of heads at r25,
// 58% at r50, 42% + 14% beyond at r100; the losers 17% / 8%), while v1.2's sd (the enemy-ETA contest and the veto) pulls our heads back to bins
// 0-1 within a few rounds of the hand-back. On a scripted family, until OP_HOLD_END:
//   who holds: OP_HOLD_ON, a process whose script hands back (any reason but 'n') while its head stands in bin 2; OP_HOLD_ALL also any other
//     process of ours whose head stands in bin 2 (children born there, heads that come later), the script no longer steering it;
//   the target: a bin-2 spawn group (2-core flow, value = yield / (1 + fresh allies within FG_GUARD_DIST + claims) >= SD_MIN_FLOW, within the
//     head BFS reach), the trade veto not firing at the group, whatever an enemy head's ETA; sticky while it stays such a group (else the best
//     one, ties to the nearer); the sd leaf pull (FG_W_FRONT beyond FG_HOLD) to it replaces v1.2's sd target;
//   it ends for good on: the trade veto at our head (local balance d8 <= LNT_D8_VETO; Slithery d3 <= LNT_VETO_D3), doom (plan.cpp), the king
//     class, the round, no such group left ('v', 'd', 'k', 'e', 'x').
// Tags: " oph@x,y d<dist>" on a holding turn, " ophx<why>" once when it ends.
void Planner::opMidHold() {
    opMidOn_ = false; opMidEndedNow_ = 0;
    if (!P::OP_HOLD_ON || opMidState_ == 2 || !opFam_) return;
    auto end = [&](char why) { opMidState_ = 2; opMidEndedNow_ = why; opMidT_ = -1; };
    if (sideChar_ != '1' && sideChar_ != '2') return;
    const int n = w_.geo.tiles(), W = w_.geo.W;
    const int headBin = w_.mapFrontBin(w_.headT, sideChar_);
    if (opMidState_ == 0) {
        if (w_.round > P::OP_HOLD_END || headBin != 2 || kingClass()) return;
        const bool handBack = opEndedNow_ && opWhy_ && opWhy_ != 'n';
        if (!handBack && !(P::OP_HOLD_ALL && !opActive_)) return;
        opMidState_ = 1;
    }
    if (w_.round > P::OP_HOLD_END) return end('e');
    if (kingClass()) return end('k');
    if (w_.unitCount < P::FG_MIN_UNITS) return;   // a team of one or two: v1.2 this turn
    // the trade veto's local balance (computeDisperseGoal's vetoAt): heads with news within 3 rounds, us counted in
    std::vector<std::pair<int, bool>> heads3;
    for (auto& [id, d] : w_.dragons)
        if (id != w_.myId && d.headT >= 0 && w_.round - d.headSeen <= 3) heads3.push_back({d.headT, d.team == w_.myTeam});
    auto vetoAt = [&](int t) {
        int a = 1, e = 0;
        for (auto& [h, ally] : heads3) {
            if (cfg_->d8Veto ? w_.geo.manhattan(h, t) > 8 : w_.geo.cheb(h, t) > 3) continue;
            if (ally) a++; else e++;
        }
        return cfg_->d8Veto ? a - e <= P::LNT_D8_VETO : a - e <= P::LNT_VETO_D3;
    };
    if (vetoAt(w_.headT)) return end('v');
    // the flow table of the recognised family (computeDisperseGoal's): 1 / mean gap on 2-core spawn tiles; -1 where the maps left disagree
    const int key = w_.mapStateCode();
    if (key != opFlowKey_ || (int)opFlow_.size() != n) {
        opFlowKey_ = key; opFlow_.assign(n, 0.0);
        for (int t = 0; t < n; t++) {
            if (!w_.inCore2(t)) continue;
            const double g = w_.mapSpawnGap(t);
            if (g > 0.0) opFlow_[t] = 1.0 / std::max(1.0, g); else if (g < 0.0) opFlow_[t] = -1.0;
        }
    }
    auto fl = [&](int t) { const double v = opFlow_[t]; if (v >= 0.0) return v; return w_.isFountain(t) ? 1.0 / std::max(1.0, (double)w_.tiles[t].maxSample) : 0.0; };
    std::vector<int> fresh;   // ally heads with news within BELIEF_FRESH rounds
    for (auto& [id, d] : w_.dragons)
        if (id != w_.myId && d.team == w_.myTeam && d.headT >= 0 && w_.round - d.headSeen <= P::BELIEF_FRESH) fresh.push_back(d.headT);
    const int myId11 = w_.myId & 2047;
    auto value = [&](int t) {
        const int x = t % W, y = t / W; double yield = 0.0;
        for (int dy = -P::FG_GROUP_DIST; dy <= P::FG_GROUP_DIST; dy++) for (int dx = -P::FG_GROUP_DIST; dx <= P::FG_GROUP_DIST; dx++)
            if (Geo::abs(dx) + Geo::abs(dy) <= P::FG_GROUP_DIST) yield += fl(w_.geo.idx(w_.geo.wrapX(x + dx), w_.geo.wrapY(y + dy)));
        int assigned = 0;
        for (int a : fresh) if (w_.geo.manhattan(a, t) <= P::FG_GUARD_DIST) assigned++;
        for (auto& c : claimsHeard_) if (c.id != myId11 && w_.geo.manhattan(c.anchor, t) <= P::FG_GROUP_DIST) assigned++;
        return yield / (1.0 + assigned);
    };
    auto ok = [&](int t) { return t >= 0 && headDist_[t] >= 0 && fl(t) > 0.0 && w_.mapFrontBin(t, sideChar_) == 2 && value(t) >= P::SD_MIN_FLOW && !vetoAt(t); };
    int target = ok(opMidT_) ? opMidT_ : -1;
    if (target < 0) {
        double bestV = 0.0; int bestD = 1 << 20;
        for (int t = 0; t < n; t++) {
            if (headDist_[t] < 0 || fl(t) <= 0.0 || w_.mapFrontBin(t, sideChar_) != 2) continue;
            const double v = value(t);
            if (v < P::SD_MIN_FLOW || vetoAt(t)) continue;
            if (v > bestV + 1e-9 || (v > bestV - 1e-9 && headDist_[t] < bestD)) { bestV = v; target = t; bestD = headDist_[t]; }
        }
    }
    if (target < 0) return end('x');
    opMidT_ = target; opMidOn_ = true;
    // the sd target and its field (computeDisperseGoal's): the group's spawn tiles within FG_GROUP_DIST are the sources; the leaf pulls FG_W_FRONT
    // a tile beyond FG_HOLD (dfs<2>), and the hotspot field of our sonar carries the target as our claim
    if (target != sdAnchor_) { sdTaken_ = w_.round; sdSince_ = w_.round; }
    sdAnchor_ = target; sdKind_ = 1; sdBin_ = 2; sdContest_ = enemyDist_[target] <= headDist_[target];
    goalDist_.assign(n, 9999);
    queue_.clear();
    const int ax = target % W, ay = target / W;
    for (int dy = -P::FG_GROUP_DIST; dy <= P::FG_GROUP_DIST; dy++) for (int dx = -P::FG_GROUP_DIST; dx <= P::FG_GROUP_DIST; dx++) {
        if (Geo::abs(dx) + Geo::abs(dy) > P::FG_GROUP_DIST) continue;
        const int t = w_.geo.idx(w_.geo.wrapX(ax + dx), w_.geo.wrapY(ay + dy));
        if ((t == target || fl(t) > 0.0) && goalDist_[t] > 0) { goalDist_[t] = 0; queue_.push_back(t); }
    }
    for (size_t qi = 0; qi < queue_.size(); qi++) {
        const int t = queue_[qi];
        for (int dir = 0; dir < 4; dir++) {
            const int u = w_.across(t, dir);
            if (u < 0 || goalDist_[u] <= goalDist_[t] + 1) continue;
            goalDist_[u] = goalDist_[t] + 1; queue_.push_back(u);
        }
    }
    goalOn_ = fGoal_ = goalDist_[w_.headT] < 9999;
}

// doom this turn (plan.cpp's escape test): the hold ends for good
void Planner::opMidDoom() { if (opMidState_ == 1) { opMidState_ = 2; opMidEndedNow_ = 'd'; opMidOn_ = false; opMidT_ = -1; } }

std::string Planner::opMidTag() const {
    char buf[48];
    if (opMidOn_ && opMidT_ >= 0) { snprintf(buf, sizeof buf, " oph@%d,%d d%d", opMidT_ % w_.geo.W, opMidT_ / w_.geo.W, goalDist_[w_.headT]); return buf; }
    if (opMidEndedNow_) { snprintf(buf, sizeof buf, " ophx%c", opMidEndedNow_); return buf; }
    return "";
}

} // namespace seed0
