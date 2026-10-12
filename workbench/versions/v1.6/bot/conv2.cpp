// conv2.cpp — unsw-swarm v1.6: the conversion module CONV2 (params.hpp v1.6 section; versions/v1.6/VERSION.md).
// research/observations/conversion-protocol.md (Codex, 9,382 games): on the 500-round SE maps the elite winners' kings eat 28-38 sacrifice pearls in
// r300-499, ours 3-9. Our declared recipients are the final king's path in 13-23% of the Slithery feeds, k8's floor (recipient >= 8) keeps a short
// king unfed on Trauma and Slithery b, and other dragons of ours eat 29-35% of the packets aimed at the king. The module gives every process one
// recipient, the elected king K (hysteresis, frozen from CV2_FREEZE), pulls the donors that may feed it to its head, lets the first drop fall
// within K's reach (the front), lets bigs merge into it at the end, and makes the others leave its drops and its next tiles to it.
// Only the CONV2 instantiations call these: decideImpl<4> (SWARM rows, dfs<2, true>) and decideImpl<5> (FORTRESS-late, dfs<0, true>; v1.6g G5), on configs
// with conv2 set (policy.hpp makeConfig); every other config runs v1.3's decideImpl<0..3>. cvOn() gates every rule (round >= cfg.cv2Start).
// v1.6b (VERSION.md §6): the switches CV2_RELAY_K .. CV2_PORTAL_SAFE. v1.6g (§8): CV2_ALL_SWARM .. CV2_FORT_ON; no rule reads the map's name.
// v1.6g+H0 (§12): CV2_EVIDENCE_LEN, CV2_LEN_CONFIRM (cvLenOf).
#include <algorithm>
#include <cstdio>

#include "params.hpp"
#include "plan.hpp"

namespace seed0 {

// v1.6g G3: an ally's length as CONV2 reads it. With C2 on (a recognised family) World's estLen / minLen already keep the largest evidence (raise-only
// but for a whole chain in view or the dragon's own report): v1.6's reading. Without C2 (unknown maps, before recognition) a partial sighting may reset
// an old bound, so CONV2 reads its own memory, kept in cv2Pre the same way (CV2_LEN_MEMORY rounds).
int Planner::cvLenOf(int id, const Dragon& d) const {
    const int ev = P::CV2_EVIDENCE_LEN ? d.minLen : std::max(d.estLen, d.minLen);   // v1.6g+H0: no sprint guess
    if constexpr (P::CV2_LEN_CONFIRM > 0) {
        int e = ev;
        if (P::CV2_LEN_MEM && !w_.lenKeepActive) {
            auto it = cvLen_.find(id);
            if (it != cvLen_.end() && w_.round - it->second.second <= P::CV2_LEN_MEMORY) e = it->second.first;   // kept by cv2Pre this turn
        }
        // v1.6g+H0b: a small length not confirmed for CV2_LEN_CONFIRM rounds (the dragon may have split since) gives way to what is in view now
        if (e < P::CV2_KMIN && w_.round - w_.lenRoundOf(id) > P::CV2_LEN_CONFIRM &&
            std::find(w_.allyHeadsNow.begin(), w_.allyHeadsNow.end(), id) != w_.allyHeadsNow.end()) e = std::min(e, d.visLen);
        return e;
    }
    if (!P::CV2_LEN_MEM || w_.lenKeepActive) return ev;
    auto it = cvLen_.find(id);
    if (it == cvLen_.end() || w_.round - it->second.second > P::CV2_LEN_MEMORY) return ev;
    return it->second.first;   // kept by cv2Pre this turn for every fresh ally
}

// v1.6g G2: the bootstrap holds while our team is small (no other way to grow a king when material is scarce; Trauma's median units r250 / r350 are
// 12 / 9), else k8's floor (on Slithery and Schooltime, feeds into kings < 8 reached the final line 5-38% of the time and drained the pieces)
int Planner::cvFloor() const { return w_.unitCount <= P::CV2_BOOT_UNITS ? 0 : P::CV2_KMIN; }

// Before the attraction field (decideImpl<4>, after the gh reset; decideImpl<5>, after computeGhDrops). The election: the candidates are ourselves
// and the allies with news within BELIEF_FRESH rounds at CONV2's length reading (cvLenOf: C2's length memory, without C2 CONV2's own); the
// incumbent K stays until a candidate is longer by the phase's hysteresis or its news is
// stale (ties: the lower id, so that processes with the same news agree). Then, when K is another dragon and its head news is at most a round old:
// its fresh death drops within CV2_YIELD_R are left to it (stack11 gh's discount through ghDrop_: pearlValue and the attraction field), and the
// tiles its head can step to next (free now) cost CV2_FRONT_PEN.
void Planner::cv2Pre() {
    cvAmK_ = false; cvYield_ = 0;
    if (!cvOn()) return;
    const int r = w_.round;
    // v1.6g G3: CONV2's own length memory while C2 is off: a whole chain in view sets it; a newer direct report (the dragon's own post-action length,
    // World::allies) sets it, even shorter; otherwise the largest evidence of the last CV2_LEN_MEMORY rounds
    if (P::CV2_LEN_MEM && !w_.lenKeepActive) {
        for (const AllyMsg& a : w_.allies) {   // direct reports (World::allies holds the latest per id; relays are not kept there)
            if (a.relay || a.len < 2 || a.id == (w_.myId & w_.msgIdMask()) || r - a.round > P::BELIEF_FRESH) continue;
            auto it = cvLen_.find(a.id);
            if (it == cvLen_.end() || a.round > it->second.second) cvLen_[a.id] = {a.len, a.round};
        }
        for (auto& [id, d] : w_.dragons) {     // sightings: a whole chain sets it; a partial one raises it, or renews an expired one
            if (id == w_.myId || d.team != w_.myTeam || d.headT < 0 || !w_.allyFresh(d, P::BELIEF_FRESH)) continue;
            const bool exact = d.lastSeen == r && d.headSeen == r && d.tailSeen;
            const int ev = exact ? d.visLen : P::CV2_EVIDENCE_LEN ? d.minLen : std::max(d.estLen, d.minLen);   // v1.6g+H0
            auto it = cvLen_.find(id);
            if (exact || (ev > 0 && (it == cvLen_.end() || r - it->second.second > P::CV2_LEN_MEMORY || ev >= it->second.first))) cvLen_[id] = {ev, r};
        }
    }
    int bestId = w_.myId, bestLen = w_.myLen;
    for (auto& [id, d] : w_.dragons) {
        if (id == w_.myId || d.team != w_.myTeam || d.headT < 0 || !w_.allyFresh(d, P::BELIEF_FRESH)) continue;
        const int la = cvLenOf(id, d);
        if (la > bestLen || (la == bestLen && id < bestId)) { bestId = id; bestLen = la; }
    }
    int kl = -1;   // the incumbent's length; -1 none or its news is stale
    if (cvK_ == w_.myId) kl = w_.myLen;
    else if (cvK_ >= 0) {
        auto it = w_.dragons.find(cvK_);
        if (it != w_.dragons.end() && it->second.team == w_.myTeam && it->second.headT >= 0 && w_.allyFresh(it->second, P::BELIEF_FRESH))
            kl = cvLenOf(cvK_, it->second);
    }
    if (kl < 0) { cvK_ = bestId; cvKSince_ = r; }
    else if (bestId != cvK_) {
        const int H = r < P::CV2_CAND ? P::CV2_H1 : r < P::CV2_FREEZE ? std::max(P::CV2_H2, kl / P::CV2_H2_DIV) : std::max(P::CV2_H3, kl / P::CV2_H3_DIV);
        if (bestLen >= kl + H) { cvK_ = bestId; cvKSince_ = r; }
    }
    cvAmK_ = cvK_ == w_.myId;
    if (cvAmK_) return;
    auto it = w_.dragons.find(cvK_);
    if (it == w_.dragons.end()) return;
    const Dragon& k = it->second;
    const int n = w_.geo.tiles(), W = w_.geo.W;
    if ((int)ghDrop_.size() != n) ghDrop_.assign(n, 0);
    auto yieldTile = [&](int t) {
        if (ghDrop_[t]) return;
        ghDrop_[t] = 1; ghdTiles_.push_back(t); ghOn_ = true; cvYield_++;
        if (P::CV2_YIELD_ALL) softPenalty_[t] += P::CV2_YIELD_PEN;
    };
    if (P::CV2_YIELD_ALL) {   // v1.6b: the drops reserved for K while the lease lasts and a pearl is still there (whatever K's news now)
        if ((int)cvRes_.size() != n) cvRes_.assign(n, -1);
        size_t m = 0;
        for (int t : cvResTiles_) {
            if (cvRes_[t] >= r && w_.tiles[t].pearlSeen > w_.tiles[t].emptySeen) { cvResTiles_[m++] = t; yieldTile(t); }
            else cvRes_[t] = -1;
        }
        cvResTiles_.resize(m);
    }
    if (k.headT < 0 || r - k.headSeen > 1) return;
    const int kx = k.headT % W, ky = k.headT / W;
    for (int dy = -P::CV2_YIELD_R; dy <= P::CV2_YIELD_R; dy++) for (int dx = -P::CV2_YIELD_R; dx <= P::CV2_YIELD_R; dx++) {
        if (Geo::abs(dx) + Geo::abs(dy) > P::CV2_YIELD_R) continue;
        const int t = w_.geo.idx(w_.geo.wrapX(kx + dx), w_.geo.wrapY(ky + dy));
        if (P::CV2_YIELD_ALL) {   // v1.6b: every pearl beside K's head; a fresh drop seen there is reserved for CV2_LEASE rounds
            if (freshDrop(t) && cvRes_[t] < 0) { cvRes_[t] = (int16_t)(r + P::CV2_LEASE); cvResTiles_.push_back(t); }
            if (w_.pearlProb(t, r) >= 0.5) yieldTile(t);
        } else if (freshDrop(t) && w_.pearlProb(t, r) >= 0.15) yieldTile(t);
    }
    if (k.headSeen == r)
        for (int d = 0; d < 4; d++) {
            const int u = w_.across(k.headT, d);
            if (u >= 0 && w_.occNow[u] == 0) softPenalty_[u] += P::CV2_FRONT_PEN;
        }
    // v1.6b: a portal crossing within the search's reach whose known exit is out of view and near K's head (Slithery's two portals join its far
    // sides: ally head-ons there killed K 6 times in 16 v1.6 games, 3 in v1.3)
    if (P::CV2_PORTAL_SAFE && r - k.headSeen <= 3) {
        const int R = P::DFS_DEPTH_MAX + 1, hx = w_.headT % W, hy = w_.headT / W, near = P::CV2_PORTAL_NEAR + (r - k.headSeen);
        for (int dy = -R; dy <= R; dy++) for (int dx = -R; dx <= R; dx++) {
            if (Geo::abs(dx) + Geo::abs(dy) > R) continue;
            const int t = w_.geo.idx(w_.geo.wrapX(hx + dx), w_.geo.wrapY(hy + dy));
            for (int d = 0; d < 4; d++) {
                if (w_.tiles[t].edge[d] != EDGE_PORTAL) continue;
                const int u = w_.across(t, d);
                if (u >= 0 && w_.tiles[u].seen != r && w_.geo.manhattan(u, k.headT) <= near) softPenalty_[u] += P::CV2_PORTAL_PEN;
            }
        }
    }
}

// After the goals (decideImpl<4>, after harvestPlan; decideImpl<5>, after computeGoal: fortress = true, the conv2 pull then replaces the gathering
// pull). The relay: the every-other-turn relay (setSonar reads goalId_ / goalT_ / goalRound_ / goalLen_ when !gatherKing_) carries K, and K itself
// relays nobody. The pull: a dragon that may feed K (the feed's length gates; mids from CV2_CAND, bigs from CV2_FREEZE), not a young piece, not a
// pocket harvester, with no other goal this turn and news of K's head at most CV2_PULL_FRESH rounds old, within the phase radius (+ the news age) of
// K's head by path over known edges (bodies ignored), with the rounds to arrive (and, for a big, for K to walk its body): the search leaf pays
// CV2_PULL_W (a big CV2_PULL_W_BIG, v1.6g G4) a tile beyond CV2_HOLD of K's head (dfs).
void Planner::cv2Plan(bool fortress) {
    cvPull_ = false;
    if (!cvOn() || cvK_ < 0) return;
    if (cvAmK_) { if (P::CV2_RELAY_K) { goalId_ = -1; gatherKing_ = true; } return; }
    auto it = w_.dragons.find(cvK_);
    if (it == w_.dragons.end()) return;
    const Dragon& k = it->second;
    if (k.headT < 0) return;
    const int kl = cvLenOf(cvK_, k);
    if (P::CV2_RELAY_K) { goalId_ = cvK_; goalT_ = k.headT; goalRound_ = k.headSeen; goalLen_ = kl; gatherKing_ = false; }   // v1.6 (v1.6b: v1.3's relay)
    const int r = w_.round, age = r - k.headSeen, L = w_.myLen;
    // v1.6b: from CV2_FREEZE a pocket harvester still approaching its mouth (outside the pocket) gives way to the pull
    const bool hvApproach = P::CV2_HV_YIELD && r >= P::CV2_FREEZE && hvPocket_ >= 0 && hvPhase_ == 1;
    if ((hvPocket_ >= 0 || (goalOn_ && !fortress)) && !hvApproach) return;   // v1.6g G5: FORTRESS's gathering pull is replaced, not respected
    if (age > P::CV2_PULL_FRESH) return;
    const bool big = L >= P::CV2_BIG;
    if (big ? (r < P::CV2_FREEZE || kl < L || L > P::CV2_MERGE_MAX) : (kl < std::max(L + P::CV2_MARGIN, cvFloor()) || (L > 4 && r < P::CV2_CAND))) return;
    if (P::FRAG_ON && w_.birthRound > 0 && w_.birthLen <= P::FRAG_CHILD && r - w_.birthRound < P::FRAG_FORAGE) return;   // a young piece forages first
    const int R = (r < P::CV2_CAND ? P::CV2_R1 : r < P::CV2_FREEZE ? P::CV2_R2 : P::CV2_R3) + age;
    const int n = w_.geo.tiles(), cap = R + P::DFS_DEPTH_MAX + 4;   // the field covers the search's leaves beyond the radius
    cvDist_.assign(n, 9999);
    queue_.clear(); queue_.push_back(k.headT); cvDist_[k.headT] = 0;
    for (size_t qi = 0; qi < queue_.size(); qi++) {
        const int t = queue_[qi];
        if (cvDist_[t] >= cap) continue;
        for (int dir = 0; dir < 4; dir++) {
            if (P::CV2_PORTAL_SAFE && w_.tiles[t].edge[dir] == EDGE_PORTAL) continue;   // v1.6b: the pull does not lead through portals
            const int u = w_.across(t, dir);
            if (u < 0 || cvDist_[u] <= cvDist_[t] + 1) continue;
            cvDist_[u] = cvDist_[t] + 1; queue_.push_back(u);
        }
    }
    const int dh = cvDist_[w_.headT];
    if (dh > R || r + dh + (big ? L + P::CV2_MERGE_SLACK : 2) > 499) return;
    if (hvApproach) { hvPocket_ = -1; hvPhase_ = 0; goalOn_ = fGoal_ = false; }   // v1.6b: the approach's goal and claim end here
    if (fortress) goalOn_ = false;   // v1.6g G5: no gathering leaf on a turn CONV2 pulls (the relay of the gathering goal stays)
    cvPullW_ = big ? P::CV2_PULL_W_BIG : P::CV2_PULL_W;   // v1.6g G4
    cvPull_ = true;
}

// The feed (decideImpl<4>, in place of sf on conv2 rows). K's head in view; K >= length + CV2_MARGIN for a piece or a mid, K >= length for a big
// from CV2_FREEZE (the merge); sf's conditions (not the escape stub nor a young piece, >= CONV_MIN_UNITS units, our head in the 2-core, no enemy head
// within SF_ENEMY_R of K's head); K's front: the path from K's head to our head through free tiles and our own body (which turns to pearls) is at most
// CONV_MAX_DIST, and no enemy head is nearer to our head than K + 1; the rounds for K to eat (a big: to walk its body); the pickup queue. Then we die
// into our own neck: the body as it stands drops, the head's pearl first, within K's reach.
bool Planner::cv2Feed(Action& act, const std::vector<int>& enemyFar, const std::vector<int>& bodyIndex, const std::vector<double>& pnow, bool youngPiece) {
    if (!cvOn() || cvK_ < 0 || cvAmK_) return false;
    const int L = w_.myLen, r = w_.round;
    if (w_.unitCount < P::CONV_MIN_UNITS || (int)w_.body.size() < 2 || !w_.inCore2(w_.headT) || r - escSplitRound_ <= 3 || youngPiece) return false;
    if (std::find(w_.allyHeadsNow.begin(), w_.allyHeadsNow.end(), cvK_) == w_.allyHeadsNow.end()) return false;
    auto it = w_.dragons.find(cvK_);
    if (it == w_.dragons.end()) return false;
    const Dragon& a = it->second;
    const int la = a.tailSeen && a.lastSeen == r ? a.visLen : cvLenOf(cvK_, a);   // v1.6g G3
    const bool big = L >= P::CV2_BIG;
    if (big ? (r < P::CV2_FREEZE || la < L || L > P::CV2_MERGE_MAX) : la < std::max(L + P::CV2_MARGIN, cvFloor())) return false;   // v1.6b merge cap; v1.6g G2 floor
    if (a.headT < 0 || enemyFar[a.headT] <= P::SF_ENEMY_R) return false;
    std::fill(distBuf_.begin(), distBuf_.end(), -1);
    queue_.clear(); queue_.push_back(a.headT); distBuf_[a.headT] = 0;
    int found = 99;
    for (size_t qi = 0; qi < queue_.size() && found == 99; qi++) {
        const int t = queue_[qi], dd = distBuf_[t];
        if (dd >= P::CONV_MAX_DIST) continue;
        for (int dir = 0; dir < 4; dir++) {
            const int u = w_.across(t, dir);
            if (u < 0 || distBuf_[u] >= 0) continue;
            if (u == w_.headT) { found = dd + 1; break; }
            if (w_.occNow[u] != 0 && bodyIndex[u] < 0) continue;
            distBuf_[u] = dd + 1; queue_.push_back(u);
        }
    }
    if (found > P::CONV_MAX_DIST || enemyFar[w_.headT] <= found + 1) return false;
    if (r + found + (big ? L + P::CV2_MERGE_SLACK : 2) > 499) return false;
    const int ax = a.headT % w_.geo.W, ay = a.headT / w_.geo.W;
    int queued = 0;
    for (int dy = -P::SF_QUEUE_R; dy <= P::SF_QUEUE_R; dy++) for (int dx = -P::SF_QUEUE_R; dx <= P::SF_QUEUE_R; dx++) {
        if (Geo::abs(dx) + Geo::abs(dy) > P::SF_QUEUE_R) continue;
        if (pnow[w_.geo.idx(w_.geo.wrapX(ax + dx), w_.geo.wrapY(ay + dy))] >= 0.5) queued++;
    }
    if (queued >= P::SF_QUEUE_MAX) { sfHeld_ = cvK_; return false; }
    act.dirs = std::string(1, DIRCH[opp(w_.myDir)]);   // into our own neck: death with the body as it stands
    char buf[80];
    snprintf(buf, sizeof buf, "feed #%d d%d L%d cv2 k%d%s", cvK_, found, L, la, big ? " m" : "");
    act.indicator = buf;
    return true;
}

// " ck#<id>" this process's K (" ck=" it is K), " cp<d>" pulled at path distance d to K's head, " cy<n>" drops left to K this turn
std::string Planner::cv2Tag() const {
    if (!cvOn() || cvK_ < 0) return "";
    char buf[48];
    if (cvAmK_) snprintf(buf, sizeof buf, " ck=");
    else snprintf(buf, sizeof buf, " ck#%d", cvK_);
    std::string s = buf;
    if (cvPull_) { snprintf(buf, sizeof buf, " cp%d", cvDist_[w_.headT]); s += buf; }
    if (cvYield_ > 0) { snprintf(buf, sizeof buf, " cy%d", cvYield_); s += buf; }
    return s;
}

} // namespace seed0
