// ptmod.cpp — unsw-swarm exp/portals: the Portals module (exp/portals/PLAN.md, params.hpp "exp/portals" section).
// Portals is solitaire (the halves share no tile), so everything here serves one aim: the longest dragon at round 500 on our own half.
// Every rule acts only in a process that recognised the Portals family; other maps never reach this code.
#include <algorithm>

#include "params.hpp"
#include "ptmap.hpp"
#include "world.hpp"

namespace seed0 {

// PT_LEN_ON: after every ingest, fold this round's length evidence of each ally into ptLen: a whole chain in view is exact and replaces
// the memory; otherwise the memory keeps the longest evidence (estLen / minLen: sightings and sonar reports) of the last PT_LEN_MEMORY rounds.
void World::ptUpdateLens() {
    for (auto& [id, d] : dragons) {
        if (id == myId || d.team != myTeam) continue;
        const bool exact = d.lastSeen == round && d.headSeen == round && d.tailSeen;
        const int ev = exact ? d.visLen : std::max(d.estLen, d.minLen);
        if (ev <= 0) continue;
        auto it = ptLen.find(id);
        if (exact || it == ptLen.end() || round - it->second.second > P::PT_LEN_MEMORY || ev >= it->second.first) ptLen[id] = {ev, round};
    }
}

} // namespace seed0

// ================================================================================================
// The planner side (decideImpl<3>, plan.cpp). ptKing_ and ptFire_ are set at the top of each module turn.
// ================================================================================================
#include "plan.hpp"

namespace seed0 {

// the tile across edge d of t on the static board (ptmap.hpp), whatever this process has seen: -1 kelp
int Planner::ptExit(int t, int d) const {
    if (w_.geo.W != ptmap::W || w_.geo.H != ptmap::H) return w_.across(t, d);
    return ptmap::EXIT[t * 4 + d];
}

double Planner::ptKingTilePen(int t) const { return ptmap::DEAD[t] ? P::PT_KING_DEAD_PEN : 0.0; }

// One step of a candidate from `from` across edge d onto `to` (blind: an unexplored portal, `to` unknown to us; the static board gives it).
//   king class (PT_KING_SAFE_ON): PT_KING_DEAD_PEN onto a dead tile (ptmap DEAD: outside the 2-core or in a one-way compartment; the
//     baseline king dived into them and left through an escape split, 16 handoffs a game); PT_KING_BLIND_PEN across a portal whose exit is
//     out of view without a clean probe from this very tile last turn (7 of 32 king head-ons had the other dragon cross blind, 3 the king).
//   a non-king (PT_PIECE_PORTAL_ON): PT_PIECE_NEAR_KING_PEN across a portal whose exit is out of view and within PT_NEAR_KING_DIST (+ the news
//     age) of the king's last known head (fresh news within PT_KING_NEWS rounds).
double Planner::ptStepPenalty(int from, int d, int to, bool blind) {
    double pen = 0.0;
    const bool portal = w_.tiles[from].edge[d] == EDGE_PORTAL || blind;
    const int exitT = blind || to < 0 ? ptExit(from, d) : to;
    if (exitT < 0) return 0.0;
    const bool unseen = w_.tiles[exitT].seen != w_.round;
    pen += ptTilePen2(exitT);                                                    // v2 A1 (every dragon)
    if (P::PT_KING_SAFE_ON && ptKing_) {
        if (ptmap::DEAD[exitT]) { pen += P::PT_KING_DEAD_PEN; ptFire_ |= 1; }
        // not while the king's head is in a room (ptmap ROOM): there every way out is a portal crossing
        if (portal && unseen && !ptmap::ROOM[w_.headT]) {
            const bool probed = from == w_.headT && w_.probeRound == w_.round && w_.probeFromT == w_.headT && w_.probeDir == d && w_.probeClear;
            if (!probed) { pen += P::PT_KING_BLIND_PEN; ptFire_ |= 2; }
        }
    } else if (P::PT_PIECE_PORTAL_ON && !ptKing_ && portal && unseen) {
        int best = 0, kt = -1, age = 99;
        for (auto& [id, a] : w_.dragons) {
            if (id == w_.myId || a.team != w_.myTeam || a.headT < 0) continue;
            const int ag = w_.round - std::max(a.lastSeen, a.headSeen), la = std::max(a.estLen, a.minLen);
            if (ag > P::PT_KING_NEWS || la < P::KING_MIN_LEN || la <= w_.myLen || la <= best) continue;
            best = la; kt = a.headT; age = ag;
        }
        if (kt >= 0 && w_.geo.manhattan(kt, exitT) <= P::PT_NEAR_KING_DIST + age) { pen += P::PT_PIECE_NEAR_KING_PEN; ptFire_ |= 4; }
    }
    return pen;
}


// v2 A1: every dragon's price for standing on t: a pocket (PT2_POCKET_PEN)
double Planner::ptTilePen2(int t) const {
    if (P::PT2_POCKET_ON && ptmap::POCKET[t]) { ptFire_ |= 16; return P::PT2_POCKET_PEN; }
    return 0.0;
}

// computeGoal() with the module's clock and endgame: non-kings follow the king from PT_GATHER_START; from PT_ENDGAME_ROUND every non-king
// does, whatever the unit count and its length (the baseline stopped at < GATHER_FEED_UNITS units or length < GATHER_FEED_MIN_LEN, so the
// second-longest ended the game apart from the king: median second 10 at r500, 60 local games).
void Planner::computeGoalPt() {
    goalOn_ = false; goalT_ = -1; gatherKing_ = true; goalId_ = -1; gxOff_ = false;
    if (w_.round < P::GATHER_BROADCAST) return;
    int n = w_.geo.tiles();
    int goalLen = 0, goalAge = 1 << 20;
    if (P::BELIEF_FIX_ON) gatherKing_ = w_.iAmLongest();
    for (auto& [id, d] : w_.dragons) {
        if (id == w_.myId || d.team != w_.myTeam || d.headT < 0) continue;
        int age = w_.round - d.headSeen;
        int la = std::max(d.estLen, d.minLen);
        if (w_.ptLenActive) la = std::max(la, w_.ptLenOf(id));   // PT_LEN_ON: the length memory
        if (P::BELIEF_FIX_ON) { if (la <= w_.myLen || !w_.allyFresh(d, P::BELIEF_FRESH)) continue; }
        else {
            if (la <= w_.myLen || age > P::GATHER_KING_MEMORY) continue;
            gatherKing_ = false;
        }
        if (age > P::GATHER_STALE) continue;
        if (la > goalLen + 2 || (la + 2 >= goalLen && age < goalAge)) { goalLen = la; goalAge = age; goalT_ = d.headT; goalId_ = id; goalRound_ = d.headSeen; goalLen_ = la; }
    }
    if (gatherKing_ || goalT_ < 0) { goalId_ = -1; return; }
    if (w_.round < P::PT_GATHER_START) return;
    const bool endgame = P::PT_ENDGAME_ON && w_.round >= P::PT_ENDGAME_ROUND;
    if (!endgame && w_.unitCount < P::GATHER_FEED_UNITS) return;
    if (!endgame && w_.myLen < P::GATHER_FEED_MIN_LEN) return;
    goalDist_.assign(n, 9999);
    queue_.clear(); queue_.push_back(goalT_); goalDist_[goalT_] = 0;
    for (size_t qi = 0; qi < queue_.size(); qi++) {
        int t = queue_[qi];
        for (int dir = 0; dir < 4; dir++) {
            int u = w_.across(t, dir);
            if (u < 0 || goalDist_[u] <= goalDist_[t] + 1) continue;
            goalDist_[u] = goalDist_[t] + 1; queue_.push_back(u);
        }
    }
    goalOn_ = goalDist_[w_.headT] < 9999;
    if (P::GX_ON && goalOn_ && goalDist_[w_.headT] + P::GX_SLACK >= 500 - w_.round) { goalOn_ = false; gxOff_ = true; }
}

} // namespace seed0
