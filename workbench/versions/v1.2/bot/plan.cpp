// plan.cpp — action selection.
//   candidates: 4 single steps, justified 2-step sprints, probed unknown-portal entries, kill paths
//   exact own-body timeline, time-aware occupancy of others, depth-limited search with iterative
//   deepening under a deterministic node budget (clock as backstop), pearl attraction field with
//   future spawns, threat model, escape split, split policy, sonar probing.
#include "plan.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>

#include "params.hpp"
#include "ptmap.hpp"   // exp/portals: dfsPt

namespace seed0 {

long long nowPoints() {
    // In the judge, steady_clock advances one nanosecond per CPU point spent.
    return (long long)std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
}

static const double DEATH = -1000.0;
static double GPOW[64], GWAIT[512];
static bool gpowInit = false;
static void initGpow() {
    if (gpowInit) return;
    double g = 1.0; for (int i = 0; i < 64; i++) { GPOW[i] = g; g *= P::GAMMA; }
    g = 1.0; for (int i = 0; i < 512; i++) { GWAIT[i] = g; g *= P::GAMMA_WAIT; }
    gpowInit = true;
}
static inline uint32_t mix32(uint32_t x) { x ^= x >> 16; x *= 0x7feb352dU; x ^= x >> 15; x *= 0x846ca68bU; x ^= x >> 16; return x; }

struct Scratch {
    std::vector<int> bodyIndex;   // tile -> index in own body (0 = head), -1 none
    std::vector<double> pnow;     // P(pearl on tile now)
    std::vector<int> enemyFar, allyFar; // multi-source BFS distance from enemy / ally heads
};
static Scratch SC;

// ------------------------------------------------------------------------------------------------
void Planner::computeEnemyDistance() {
    int n = w_.geo.tiles();
    enemyDist_.assign(n, 99); enemyNearLen_.assign(n, 0); enemyPseudo_.assign(n, 0);
    if (P::TG_ON) { enemyTradeLen_.assign(n, 0); enemyDistOld_.assign(n, 99); enemyNearLenOld_.assign(n, 0); enemyPseudoOld_.assign(n, 0); }
    SC.enemyFar.assign(n, 9999); SC.allyFar.assign(n, 9999);
    distBuf_.assign(n, -1);
    // stack4 tg: tiles empty by the time a given enemy head moves. Our tail goes with our move, which comes before every
    // enemy's next move; a seen tail of another dragon goes when that dragon moves between us and the enemy (turns run in id
    // order). (World pads other dragons' freeAt by >= 3, so stack3's "freeAt <= 1" freed only our own tail.)
    std::vector<std::pair<int, int>> tails; // (tail tile, dragon id)
    int ourTail = w_.body.empty() ? -1 : w_.body.back();
    if (P::TG_ON)
        for (auto& [id, d] : w_.dragons)
            if (id != w_.myId && d.lastSeen == w_.round && d.headSeen == w_.round && d.tailSeen && d.tailT >= 0) tails.push_back({d.tailT, id});
    auto vacated = [&](int t, int enemyId) {
        if (t == ourTail) return true;
        int m = w_.myId;
        for (auto& [tt, o] : tails)
            if (tt == t && o != enemyId && (enemyId > m ? (o > m && o < enemyId) : (o > m || o < enemyId))) return true;
        return false;
    };
    // tg = false: stack3's field exactly. tg = true (stack4): an occupied tile gets a distance (a step onto a tile that empties
    // has a threat; failure study: 22 of 34 blind-spot rams were our new head on a tile our body held) but passes the head on
    // only when vacated() before this enemy moves (killer paths through such tiles: 22 of the 34)
    auto spread = [&](int src, int radius, int le, int leTrade, int age, bool pseudo, bool tg, int enemyId,
                      std::vector<int16_t>& dOut, std::vector<int16_t>& lOut, std::vector<uint8_t>& pOut, std::vector<int16_t>* tOut) {
        std::fill(distBuf_.begin(), distBuf_.end(), -1);
        queue_.clear(); queue_.push_back(src); distBuf_[src] = 0;
        for (size_t qi = 0; qi < queue_.size(); qi++) {
            int t = queue_[qi]; int dist = distBuf_[t];
            int eff = dist + age; // stale sighting: the head may already be closer
            if (eff <= 4 && eff < dOut[t]) { dOut[t] = (int16_t)eff; lOut[t] = (int16_t)le; pOut[t] = pseudo ? 1 : 0; if (tOut) (*tOut)[t] = (int16_t)leTrade; }
            if (dist >= radius) continue;
            if (tg && dist > 0 && w_.occNow[t] != 0 && t != w_.headT && !vacated(t, enemyId)) continue; // stack4 tg: a target, not a passage
            for (int dir = 0; dir < 4; dir++) {
                int u = w_.across(t, dir);
                if (u < 0 || distBuf_[u] >= 0) continue;
                if (!tg && w_.occNow[u] != 0 && u != w_.headT) continue; // heads cannot pass bodies; our head tile is a legal (fatal) target
                distBuf_[u] = dist + 1; queue_.push_back(u);
            }
        }
    };
    for (auto& [id, d] : w_.dragons) {
        if (d.team == w_.myTeam || d.headT < 0) continue;
        int age = w_.round - d.headSeen;
        if (age > P::ENEMY_MEMORY_ROUNDS) continue;
        int le = std::max(d.estLen, 2);
        int reach = std::min(le - 1, 4);
        // a higher-id enemy may split this round: its tail becomes a child head that moves before our next turn
        bool latent = age == 0 && id > w_.myId && d.tailSeen && d.tailT >= 0 && le >= 4;
        if (!P::TG_ON) {
            spread(d.headT, std::max(1, reach), le, le, age, false, false, id, enemyDist_, enemyNearLen_, enemyPseudo_, nullptr);
            if (latent) spread(d.tailT, 1, 2, 2, 0, true, false, id, enemyDist_, enemyNearLen_, enemyPseudo_, nullptr);
            continue;
        }
        // stack4 tg: stack3's field for the tag, then the new one. Reach length: an unseen tail is long enough for the capped
        // reach (failure study: 21 rams by L>=5 heads with the tail out of view, estimated L4), and a pearl beside the head adds
        // a step (24 rams ate on the strike path; as ks2). The trade side keeps the estimated length.
        spread(d.headT, std::max(1, reach), le, le, age, false, false, id, enemyDistOld_, enemyNearLenOld_, enemyPseudoOld_, nullptr);
        if (latent) spread(d.tailT, 1, 2, 2, 0, true, false, id, enemyDistOld_, enemyNearLenOld_, enemyPseudoOld_, nullptr);
        int leR = d.tailSeen ? le : std::max(le, P::TG_UNSEEN_LEN);
        for (int dir = 0; dir < 4; dir++) { int u = w_.across(d.headT, dir); if (u >= 0 && w_.pearlProb(u, w_.round) >= 0.5) { leR++; break; } }
        spread(d.headT, std::max(1, std::min(leR - 1, 4)), leR, le, age, false, true, id, enemyDist_, enemyNearLen_, enemyPseudo_, &enemyTradeLen_);
        if (latent) spread(d.tailT, 1, 2, 2, 0, true, true, id, enemyDist_, enemyNearLen_, enemyPseudo_, &enemyTradeLen_);
    }
    // stack3 ks2: for the late king, the full sprint reach (length - 1 up to KS2_REACH; an unseen tail may be long)
    if (kingSafe2_) {
        enemyDist2_.assign(n, 99); enemyNearLen2_.assign(n, 0);
        for (auto& [id, d] : w_.dragons) {
            if (d.team == w_.myTeam || d.headT < 0) continue;
            int age = w_.round - d.headSeen;
            if (age > P::ENEMY_MEMORY_ROUNDS) continue;
            int le2 = d.tailSeen ? std::max(d.estLen, 2) : 99;
            // a pearl beside its head makes it one longer before it strikes (failure study: 24 of 45 reach-gap rams)
            if (le2 < 99) for (int dir = 0; dir < 4; dir++) { int u = w_.across(d.headT, dir); if (u >= 0 && w_.pearlProb(u, w_.round) >= 0.5) { le2++; break; } }
            int reach2 = std::min(le2 - 1, P::KS2_REACH);
            if (reach2 < 5) continue; // the ordinary field covers distances up to 4
            std::fill(distBuf_.begin(), distBuf_.end(), -1);
            queue_.clear(); queue_.push_back(d.headT); distBuf_[d.headT] = 0;
            for (size_t qi = 0; qi < queue_.size(); qi++) {
                int t = queue_[qi]; int dist = distBuf_[t];
                int eff = dist + age;
                if (eff <= P::KS2_REACH && eff < enemyDist2_[t]) { enemyDist2_[t] = (int16_t)eff; enemyNearLen2_[t] = (int16_t)le2; }
                if (dist >= reach2) continue;
                for (int dir = 0; dir < 4; dir++) {
                    int u = w_.across(t, dir);
                    if (u < 0 || distBuf_[u] >= 0) continue;
                    // a tile vacated before it moves (a tail, ours included) does not stop its sprint (failure study: 34
                    // rams through tiles that were occupied at decision time)
                    bool ourTail = !w_.body.empty() && u == w_.body.back();
                    if (w_.occNow[u] != 0 && u != w_.headT && !ourTail && w_.freeAt[u] > 1) continue;
                    distBuf_[u] = dist + 1; queue_.push_back(u);
                }
            }
        }
    }
    auto multi = [&](bool enemy, std::vector<int>& out) {
        queue_.clear();
        for (auto& [id, d] : w_.dragons) {
            if (id == w_.myId || d.headT < 0 || w_.round - d.headSeen > 3) continue;
            if ((d.team != w_.myTeam) != enemy) continue;
            if (out[d.headT] > 0) { out[d.headT] = 0; queue_.push_back(d.headT); }
        }
        for (size_t qi = 0; qi < queue_.size(); qi++) {
            int t = queue_[qi]; int dist = out[t];
            if (dist >= P::ATTRACT_RADIUS + 4) continue;
            for (int dir = 0; dir < 4; dir++) {
                int u = w_.across(t, dir);
                if (u < 0 || out[u] <= dist + 1) continue;
                if (w_.occNow[u] != 0 && w_.freeAt[u] > dist + 1) continue;
                out[u] = dist + 1; queue_.push_back(u);
            }
        }
    };
    multi(true, SC.enemyFar);
    multi(false, SC.allyFar);
}

void Planner::computeSoftPenalty() {
    int n = w_.geo.tiles();
    softPenalty_.assign(n, 0.0);
    // other dragons' heads tend to keep going: soft-penalise the tiles straight ahead of them
    for (auto& [id, d] : w_.dragons) {
        if (id == w_.myId || d.headSeen != w_.round || d.headT < 0) continue;
        int t = d.headT;
        for (int k = 1; k <= 3; k++) {
            int u = w_.across(t, d.headDir);
            if (u < 0 || w_.occNow[u] != 0) break;
            softPenalty_[u] = std::max(softPenalty_[u], P::HEAD_PATH_PENALTY * (k == 1 ? 1.0 : k == 2 ? 0.6 : 0.3));
            t = u;
        }
    }
    // an enemy head echoed along the ray we sent last turn: avoid running down that line
    for (int d = 0; d < 4; d++) {
        int r = w_.enemyHeadEchoDir[d];
        if (r <= 0 || w_.round - r > 3) continue;
        double wgt = P::ECHO_LINE_PENALTY * (w_.round - r == 0 ? 1.0 : 0.6);
        int t = w_.headT;
        for (int k = 1; k <= P::ECHO_LINE_RANGE; k++) {
            int u = w_.across(t, d);
            if (u < 0) break;
            softPenalty_[u] = std::max(softPenalty_[u], wgt * (1.0 - 0.1 * k));
            t = u;
        }
    }
}

double Planner::threatAt(int t) const {
    int d = enemyDist_[t];
    if (d > 4) return ks2Threat(t);
    int le = enemyNearLen_[t];
    return threatCore(d, le, P::TG_ON ? (int)enemyTradeLen_[t] : le, enemyPseudo_[t] != 0);
}

// stack3 ks2: a sprint of 5..KS2_REACH steps into the late king (a trade they always win)
double Planner::ks2Threat(int t) const {
    if (!kingSafe2_) return 0.0;
    int d2 = enemyDist2_[t];
    if (d2 < 5 || d2 > P::KS2_REACH || enemyNearLen2_[t] < d2 + 1) return 0.0;
    double T2 = d2 == 5 ? P::KS2_T5 : d2 == 6 ? P::KS2_T6 : P::KS2_T7;
    if (w_.iAmLongest() && w_.myLen >= P::KING_MIN_LEN) T2 *= P::KING_THREAT_MULT;
    return T2;
}

// stack4 tg: the threat stack3's field gives at t (only for the " tg" tag)
double Planner::threatAtOld(int t) const {
    int d = enemyDistOld_[t];
    if (d > 4) return ks2Threat(t);
    int le = enemyNearLenOld_[t];
    return threatCore(d, le, le, enemyPseudoOld_[t] != 0);
}

// d = path distance, le = length for the reach (needs le >= d + 1), leTrade = length for whom the head-on favours
double Planner::threatCore(int d, int le, int leTrade, bool pseudo) const {
    int lm = w_.myLen;
    // the trade is decided by the opponent: favourable for them when we are at least as long, when we are the
    // team's last dragon (elimination), or late when we hold the longest and they can flip it
    bool favForThem = leTrade <= lm || w_.unitCount == 1 || (late_ && w_.iAmLongest() && leTrade <= lm + 4);
    double T;
    if (d <= 1) T = P::T1 * (favForThem ? 1.0 : P::TRADE_BAD_FOR_THEM);
    else if (d == 2) T = le >= 3 ? P::T2 * (favForThem ? 1.0 : P::T_FAR_BAD_FOR_THEM) : 0.0;
    else if (d == 3) T = le >= 4 ? P::T3 * (favForThem ? 1.0 : P::T_FAR_BAD_FOR_THEM) : 0.0;
    else T = le >= 5 ? P::T4 * (favForThem ? 1.0 : P::T_FAR_BAD_FOR_THEM) : 0.0;
    if (pseudo) T *= P::PSEUDO_HEAD_MULT;
    if (w_.iAmLongest() && lm >= P::KING_MIN_LEN) T *= P::KING_THREAT_MULT;
    if (late_ && ahead_ && w_.iAmLongest()) T *= P::ENDGAME_THREAT_MULT;
    else if (kingSafe_) T *= P::ENDGAME_THREAT_MULT; // stack1 M3: the king in the last rounds, ahead or not
    return T;
}

// information value of standing on t: unseen or stale tiles the 7x7 window would reveal
double Planner::exploreValue(int t) {
    if (exploreStamp_[t] == w_.round) return exploreVal_[t];
    int x = t % w_.geo.W, y = t / w_.geo.W;
    double v = 0.0;
    for (int dy = -3; dy <= 3; dy++) for (int dx = -3; dx <= 3; dx++) {
        int u = w_.geo.idx(w_.geo.wrapX(x + dx), w_.geo.wrapY(y + dy));
        int seen = w_.tiles[u].seen;
        if (seen < 0) v += 1.0;
        else if (w_.round - seen > 60) v += std::min(1.0, (w_.round - seen - 60) / 200.0);
    }
    v *= P::EXPLORE_W * w_.pearlPriorUnseen * 4.0; // ~49 tiles * prior ≈ expected pearls revealed
    exploreStamp_[t] = w_.round; exploreVal_[t] = v;
    return v;
}

// penalty for stepping through a known portal into a region we cannot currently see. cand-portal1: only the risk that
// something unseen stands on or beside the exit; a tight or dead-end exit is seen by the search and the flood fill.
double Planner::portalPenalty(int from, int d, int to) const {
    if (w_.tiles[from].edge[d] != EDGE_PORTAL) return 0.0;
    if (from == w_.headT && probeOk_ && w_.probeDir == d) return 0.0; // a ray through it just now hit no dragon
    double pen = 0.0;
    int seen = w_.tiles[to].seen;
    if (seen != w_.round) {
        pen += P::PORTAL_BLIND_PENALTY + P::PORTAL_STALE_PENALTY * std::min(1.0, (seen < 0 ? 20.0 : (double)(w_.round - seen)) / 20.0);
        // vision does not cross portals: a head (ours or theirs) seen near the exit recently may now stand on it
        for (auto& [id, dg] : w_.dragons) {
            if (id == w_.myId || dg.headT < 0 || w_.round - dg.headSeen > 2) continue;
            if (w_.geo.manhattan(dg.headT, to) <= 2) { pen += P::PORTAL_HEAD_NEAR_PENALTY; break; }
        }
        if (P::PX_ON) pen += pxPenalty(from, d, to);
    }
    return pen;
}

// stack4 px: crossing a known portal (exit out of view, no clean probe from our head) toward our own crowd. Failure study
// (merge2, 210 games): 83 of the 103 deaths on the crossing step had our own body or head at the exit, 55 of them not
// desperate; the exit is out of view and the ally heard near it long ago. An ally head seen or heard within PX_ALLY_ROUNDS
// rounds within PX_ALLY_DIST of the exit costs what a head seen beside it just now costs (not both).
double Planner::pxPenalty(int from, int d, int to) const {
    if (w_.tiles[from].edge[d] != EDGE_PORTAL || w_.tiles[to].seen == w_.round) return 0.0;
    if (from == w_.headT && probeOk_ && w_.probeDir == d) return 0.0;
    bool near = false, crowd = false;
    for (auto& [id, dg] : w_.dragons) {
        if (id == w_.myId || dg.headT < 0) continue;
        int age = w_.round - dg.headSeen, md = w_.geo.manhattan(dg.headT, to);
        if (age <= 2 && md <= 2) near = true; // portalPenalty() already charges this one
        if (dg.team == w_.myTeam && age <= P::PX_ALLY_ROUNDS && md <= P::PX_ALLY_DIST) crowd = true;
    }
    return crowd && !near ? P::PORTAL_HEAD_NEAR_PENALTY : 0.0;
}

// ---- unexplored portals (cand-portal1) ----
// The value of trying an unexplored portal grows with hunger (rounds since we last grew), with the share of the map we
// have never seen, and fades before the end. A probe that hit a dragon mutes that one edge for a few rounds.
void Planner::computeFrontier() {
    int left = 500 - w_.round;
    double timeF = std::clamp((left - P::ENDGAME_ROUNDS) / (double)P::FRONTIER_FADE_ROUNDS, 0.0, 1.0);
    double hunger = std::clamp((w_.round - w_.lastAteRound) / (double)P::HUNGER_ROUNDS, 0.0, 1.0);
    double unseen = 1.0 - (double)w_.tilesObserved / std::max(1, w_.geo.tiles());
    double unseenF = std::clamp(P::FRONTIER_UNSEEN_GAIN * unseen, 0.0, 1.0);
    frontierBase_ = P::FRONTIER_VALUE * (P::FRONTIER_FED_FRAC + (1.0 - P::FRONTIER_FED_FRAC) * hunger) * timeF * unseenF;
    probeOk_ = w_.probeRound == w_.round && w_.probeClear && w_.probeDir >= 0 && w_.probeFromT == w_.headT;
    if (w_.probeRound == w_.round && !w_.probeClear && w_.probeDir >= 0 && w_.probeFromT >= 0 &&
        w_.across(w_.probeFromT, w_.probeDir) == -2)
        w_.frontierBlock[(size_t)w_.probeFromT * 4 + w_.probeDir] = (int16_t)std::min(30000, w_.round + P::FRONTIER_BLOCK_ROUNDS);
    // path distance from our head over known edges, bodies ignored (ranking of attraction sources through portals)
    int n = w_.geo.tiles();
    headDist_.assign(n, -1);
    queue_.clear(); queue_.push_back(w_.headT); headDist_[w_.headT] = 0;
    for (size_t qi = 0; qi < queue_.size(); qi++) {
        int t = queue_[qi];
        if (headDist_[t] >= P::ATTRACT_RADIUS + 6) continue;
        for (int dir = 0; dir < 4; dir++) {
            int u = w_.across(t, dir);
            if (u < 0 || headDist_[u] >= 0) continue;
            headDist_[u] = headDist_[t] + 1; queue_.push_back(u);
        }
    }
}

double Planner::frontierValue(int t, int d) const {
    if (frontierBase_ <= 0.0) return 0.0;
    const Tile& x = w_.tiles[t];
    if (x.seen < 0 || x.edge[d] != EDGE_PORTAL || w_.across(t, d) != -2) return 0.0;
    if (w_.frontierBlock[(size_t)t * 4 + d] > w_.round) return 0.0;
    return frontierBase_;
}

double Planner::blindRisk(int len) const { return P::BLIND_RISK + P::BLIND_RISK_PER_LEN * len; }

// Pearl attraction field: sum over sources of v * gamma^dist * gammaWait^(wait-dist) with contention factors.
// v1: the swarm instantiation (SW) keeps its goal-like boosts off dead-end pockets (World::inCore2): grab, cov and the piece claims (cl); its cov
// side is the swarm's side vote (sideOf). The FORTRESS instantiation is stack11's computeAttract().
template <int MODE> void Planner::computeAttractT() {
    constexpr bool SW = MODE == 2, W4 = MODE == 1;
    int n = w_.geo.tiles();
    attract_.assign(n, 0.0);
    SC.pnow.assign(n, 0.0);
    struct Src { int t; double v; int wait; bool grab; bool cov = false; bool gh = false; }; // cov: stack5; gh: stack11
    std::vector<Src> src; src.reserve(256);
    int hx = w_.headT % w_.geo.W, hy = w_.headT / w_.geo.W;
    grabTiles_.clear();
    for (int t = 0; t < n; t++) {
        double p = w_.pearlProb(t, w_.round);
        SC.pnow[t] = p;
        const Tile& x = w_.tiles[t];
        double v = 0.0; int wait = 0;
        if (p >= 0.15) v = p;
        else if (x.seen >= 0 && x.spawnRound > w_.round && x.spawnRound - w_.round <= P::FUTURE_SPAWN_HORIZON) { v = P::SPAWN_CONF * 0.9; wait = x.spawnRound - w_.round; }
        if (w_.isFountain(t) && w_.occNow[t] == 0) v = std::max(v, P::FOUNTAIN_VALUE);
        if (v <= 0.0) continue;
        int md = Geo::abs(w_.geo.dx(hx, t % w_.geo.W)) + Geo::abs(w_.geo.dy(hy, t / w_.geo.W));
        if (headDist_[t] >= 0) md = std::min(md, headDist_[t]); // a remembered tile behind a known portal is near
        if (md > P::ATTRACT_RADIUS + 6) continue;
        // stack2 S2 (H5): a fresh death drop within reach is worth more, and the enemy contest below does not discount it
        bool grab = grabOn_ && p >= 0.15 && headDist_[t] >= 0 && headDist_[t] <= P::GRAB_REACH && freshDrop(t);
        if constexpr (SW) grab = grab && w_.inCore2(t);
        const bool ghs = ghOn_ && ghDrop_[t];                 // stack11 gh: left to the longer ally beside it (no grab for us)
        if (ghs) grab = false;
        if (grab) { v = std::max(v, p * P::GRAB_VALUE); grabTiles_.push_back(t); }
        // stack5 cov: for a piece, a coming spawn or a fountain of our side is contested, not ceded, when an enemy head is nearer
        // (stack9: our side by the recognised map's territory, covSide)
        bool cov = !W4 && P::COV_ON && w_.myLen <= P::COV_MAX_LEN && p < 0.15 && (SW ? sideOf(t) == 1 && w_.inCore2(t) : covSide(t));   // 5b: no cov
        src.push_back({t, v, wait, grab, cov, ghs});
    }
    // stack8 claims (supply-chain proposal, params.hpp): a pearl within CLAIM_REACH that no ally or enemy head is nearer to is ours
    // for CLAIM_ROUNDS while it stays, even if others come nearer later (hysteresis). F2p reads them for any length, cl / ce for a piece.
    clTiles_.clear(); ceTiles_.clear();
    if (!W4 && (P::F2P_ON || P::CLAIM_ALLY_ON || P::CLAIM_ENEMY_ON)) {   // 5b: no claims (cl / ce) on Autarky and PD6
        size_t k = 0;
        for (auto& c : claims_) if (w_.round - c.second <= P::CLAIM_ROUNDS && SC.pnow[c.first] >= 0.15) claims_[k++] = c;
        claims_.resize(k);
        for (int t = 0; t < n; t++) {
            if (SC.pnow[t] < 0.15 || headDist_[t] < 0 || headDist_[t] > P::CLAIM_REACH || freshDrop(t)) continue;
            if constexpr (SW) { if (!w_.inCore2(t)) continue; }
            // a pearl we have seen, not a predicted spawn (local check v1, 18:38: half the claimed tiles held no pearl)
            if (!(w_.tiles[t].pearlSeen > w_.tiles[t].emptySeen && w_.round - w_.tiles[t].pearlSeen <= P::CLAIM_SEEN)) continue;
            if (headDist_[t] > SC.allyFar[t] || headDist_[t] > SC.enemyFar[t]) continue;
            bool have = false;
            for (auto& c : claims_) if (c.first == t) { have = true; break; }
            if (!have) claims_.push_back({t, w_.round});
        }
    }
    const bool claimPiece = !W4 && (P::CLAIM_ALLY_ON || P::CLAIM_ENEMY_ON) && w_.myLen <= P::CLAIM_MAX_LEN;
    // hunting: short dragons value a much longer enemy head; any dragon values an enemy shadowing a longer teammate
    if (w_.unitCount >= 2) {
        for (int id : w_.enemyHeadsNow) {
            const Dragon& d = w_.dragons[id];
            double tv = tradeValue(id);
            if (tv > 0.0 && w_.myLen <= P::HUNT_MAX_LEN) src.push_back({d.headT, std::min(tv * 0.15, 3.0), 0, false});
        }
    }
    for (auto& a : w_.allies) if (a.hotT >= 0 && w_.round - a.round <= 30) src.push_back({a.hotT, 0.4, 0, false});
    if (src.size() > (size_t)P::MAX_SOURCES) {
        std::partial_sort(src.begin(), src.begin() + P::MAX_SOURCES, src.end(), [&](const Src& a, const Src& b) {
            int da = w_.geo.manhattan(w_.headT, a.t), db = w_.geo.manhattan(w_.headT, b.t);
            if (headDist_[a.t] >= 0) da = std::min(da, headDist_[a.t]);
            if (headDist_[b.t] >= 0) db = std::min(db, headDist_[b.t]);
            return a.v * GPOW[std::min(63, da)] * GWAIT[std::min(511, std::max(0, a.wait - da))] >
                   b.v * GPOW[std::min(63, db)] * GWAIT[std::min(511, std::max(0, b.wait - db))];
        });
        src.resize(P::MAX_SOURCES);
    }
    distBuf_.assign(n, -1);
    for (auto& s : src) {
        std::fill(distBuf_.begin(), distBuf_.end(), -1);
        queue_.clear(); queue_.push_back(s.t); distBuf_[s.t] = 0;
        int ef = SC.enemyFar[s.t], af = SC.allyFar[s.t];
        // stack8 cl / ce: a piece's claimed pearl. cl: worth p * CLAIM_VALUE and ceded only to a nearer sibling (a known head of length
        // <= CLAIM_MAX_LEN, Manhattan), not to a longer ally; ce: at least CONTEST_EQUAL while the enemy is at most one step nearer
        bool ce = false;
        if (claimPiece && !s.grab && headDist_[s.t] >= 0) {
            bool claimed = false;
            for (auto& c : claims_) if (c.first == s.t) { claimed = true; break; }
            if (claimed && P::CLAIM_ALLY_ON) {
                s.v = std::max(s.v, SC.pnow[s.t] * P::CLAIM_VALUE);
                int sib = 9999;
                for (auto& [id, d] : w_.dragons)
                    if (id != w_.myId && d.team == w_.myTeam && d.headT >= 0 && w_.round - d.headSeen <= 3 && d.estLen <= P::CLAIM_MAX_LEN) sib = std::min(sib, w_.geo.manhattan(d.headT, s.t));
                af = sib; clTiles_.push_back(s.t);
            }
            if (claimed && P::CLAIM_ENEMY_ON && ef >= headDist_[s.t] - 1) { ce = true; if (ef <= headDist_[s.t] + 1) ceTiles_.push_back(s.t); }
        }
        for (size_t qi = 0; qi < queue_.size(); qi++) {
            int t = queue_[qi]; int dist = distBuf_[t];
            // race outcomes from turn order: equal distance is ours; one closer needs their sprint
            double contest = 1.0;
            if (s.grab) {}                                  // stack2 S2: a fresh drop beside us is raced for, not ceded
            else if (ef < dist - 1) contest = P::CONTEST_ENEMY_CLOSER;
            else if (ef == dist - 1) contest = P::CONTEST_ENEMY_ONE_CLOSER;
            else if (ef == dist) contest = P::CONTEST_EQUAL;
            if (s.cov) contest = std::max(contest, P::COV_CONTEST); // stack5 cov
            if (ce) contest = std::max(contest, P::CONTEST_EQUAL);  // stack8 ce
            if (af < dist || s.gh) contest *= P::CONTEST_ALLY_CLOSER; // stack11 gh: at every distance for a drop left to a longer ally
            attract_[t] += s.v * GPOW[std::min(63, dist)] * GWAIT[std::min(511, std::max(0, s.wait - dist))] * contest;
            if (dist >= P::ATTRACT_RADIUS) continue;
            for (int dir = 0; dir < 4; dir++) {
                int u = w_.across(t, dir);
                if (u < 0 || distBuf_[u] >= 0) continue;
                if (w_.occNow[u] != 0 && w_.freeAt[u] > dist + 2) continue;
                distBuf_[u] = dist + 1; queue_.push_back(u);
            }
        }
    }
    // cand-portal1: the nearest unexplored portals pull like a few pearls when we are hungry. One frontier is entered at
    // a time, so their pulls do not add up: the field is the best single frontier (an ally nearer to it takes it).
    frontierField_.assign(n, 0.0);
    if (frontierBase_ > 0.0) {
        std::vector<std::pair<int, int>> fr; // (path distance, entry tile)
        for (int t = 0; t < n; t++) {
            if (headDist_[t] < 0 || w_.tiles[t].seen < 0) continue;
            for (int d = 0; d < 4; d++) if (frontierValue(t, d) > 0.0) { fr.push_back({headDist_[t], t}); break; }
        }
        std::sort(fr.begin(), fr.end());
        if (fr.size() > (size_t)P::FRONTIER_MAX_SOURCES) fr.resize(P::FRONTIER_MAX_SOURCES);
        for (auto& f : fr) {
            std::fill(distBuf_.begin(), distBuf_.end(), -1);
            queue_.clear(); queue_.push_back(f.second); distBuf_[f.second] = 0;
            int af = SC.allyFar[f.second];
            for (size_t qi = 0; qi < queue_.size(); qi++) {
                int t = queue_[qi]; int dist = distBuf_[t];
                double v = frontierBase_ * GPOW[std::min(63, dist)] * (af < dist ? P::CONTEST_ALLY_CLOSER : 1.0);
                if (v > frontierField_[t]) frontierField_[t] = v;
                if (dist >= P::ATTRACT_RADIUS) continue;
                for (int dir = 0; dir < 4; dir++) {
                    int u = w_.across(t, dir);
                    if (u < 0 || distBuf_[u] >= 0) continue;
                    if (w_.occNow[u] != 0 && w_.freeAt[u] > dist + 2) continue;
                    distBuf_[u] = dist + 1; queue_.push_back(u);
                }
            }
        }
    }
}

// ------------------------------------------------------------------------------------------------
// Own-body rule: at a step where `removed` tail segments have already been removed, the body segment
// with tail-distance k is blocked iff k >= removed. Tiles already in the new path are always blocked.
bool Planner::tileEnterable(int t, int step, int removed, const std::vector<int>& path) const {
    for (int p : path) if (p == t) return false;
    int bi = SC.bodyIndex[t];
    if (bi >= 0) { int k = (int)w_.body.size() - 1 - bi; return k < removed; }
    if (w_.occNow[t] != 0) return w_.freeAt[t] <= step;
    return true;
}

// Flood fill from the first step's tile: how much room is there if we go this way, and is it a dead end?
double Planner::areaSafety(int startT, int startRemoved, const std::vector<int>& pathTiles) {
    int L = w_.myLen;
    int cap = std::max(2 * L + P::AREA_CAP_EXTRA, P::AREA_CAP_MIN);
    std::vector<int>& dist = distBuf_; std::vector<int>& q = queue_; std::vector<int>& par = parBuf_;
    std::fill(dist.begin(), dist.end(), -1);
    par.assign(dist.size(), -1);
    q.clear(); q.push_back(startT); dist[startT] = 0;
    int count = 1; bool tailReached = false; int cycles = 0;
    int tailT = w_.body.empty() ? -1 : w_.body.back();
    for (size_t qi = 0; qi < q.size() && count < cap; qi++) {
        int t = q[qi]; int dd = dist[t];
        int step = 1 + dd + 1;           // arrival step of a neighbour
        int removed = startRemoved + dd; // tail segments gone by then (no eating assumed)
        for (int dir = 0; dir < 4; dir++) {
            int u = w_.across(t, dir);
            if (u < 0) continue;
            if (dist[u] >= 0) { if (u != par[t] && dist[u] >= dd) cycles++; continue; } // non-tree edge: a cycle
            bool ok;
            int bi = SC.bodyIndex[u];
            bool inPath = false; for (int p : pathTiles) if (p == u) { inPath = true; break; }
            if (inPath) ok = false;
            else if (bi >= 0) { int k = (int)w_.body.size() - 1 - bi; ok = k < removed; }
            else if (w_.occNow[u] != 0) ok = w_.freeAt[u] <= step;
            else ok = enemyDist_[u] > 1 || enemyPseudo_[u]; // an enemy head can seal a tile it stands next to
            if (!ok) continue;
            if (u == tailT) tailReached = true;
            dist[u] = dd + 1; par[u] = t; q.push_back(u); count++;
            if (count >= cap) break;
        }
    }
    double v = 0.0;
    if (count < L + P::AREA_MARGIN) v -= P::AREA_TRAP_PENALTY * (1.0 + (L + P::AREA_MARGIN - count) * 0.1);
    if (count < cap) {
        if (cycles == 0 && (500 - w_.round) > count) v -= P::AREA_DEADEND_PENALTY * (kingSafe_ ? P::KS_DEADEND_MULT : 1.0); // we will hit the end before the game ends (stack1 M3: dearer for the late king)
        else v -= P::AREA_ROOM_PENALTY;
        int over = (int)(P::AREA_FILL_RATIO * L) + P::AREA_FILL_MARGIN - count;
        if (over > 0) v -= P::AREA_FILL_PENALTY * over;
    }
    v += std::min(count, cap) * P::AREA_BONUS_PER_TILE;
    if (tailReached) v += P::TAIL_REACH_BONUS;
    return v;
}

// Depth-limited search over own moves after this turn's action. `depth` = turns after this one so far,
// path holds tiles visited (path[0] = original head).
template <int MODE> double Planner::dfs(int t, int lastDir, int depth, int maxDepth, int removed, int lenNow, std::vector<int>& path, long long deadline) {
    int turns = depth;
    int stepBase = (int)path.size() - 1;
    nodes_++;
    bool over = nodes_ > P::DFS_NODE_BUDGET || (((nodes_ & 63) == 0) && nowPoints() > deadline);
    if (depth >= maxDepth || over) {
        double v = attract_[t] * GPOW[std::min(63, turns + 1)] + exploreValue(t) * GPOW[std::min(63, turns + 1)];
        if (frontierField_[t] > 0.0) v += frontierField_[t] * GPOW[std::min(63, turns + 1)]; // cand-portal1
        int freeN = 0;
        for (int d = 0; d < 4; d++) { if (d == opp(lastDir)) continue; int u = w_.across(t, d); if (u >= 0 && tileEnterable(u, stepBase + 1, removed, path)) freeN++; }
        v += freeN * 0.15;
        if (goalOn_) v -= fGoal_ ? (MODE == 2 ? P::FG_W_FRONT : P::FG_W) * std::max(0, std::min(goalDist_[t], 200) - P::FG_HOLD)   // stack5 F: hold the group (v1.1b: the swarm sd pull FG_W_FRONT)
                                 : P::GH_ON ? P::GATHER_W * std::max(0, std::min(goalDist_[t], 200) - P::GH_HOLD)   // stack11 gh: hold back at the king
                                 : P::GATHER_W * std::min(goalDist_[t], 200);
        if (kxOn_) v -= P::KX_W * std::max(0, P::KX_DIST - (int)kxDist_[t]);                        // stack11 kx: the king keeps away
        if (freeN == 0) v += DEATH * 0.5 * GPOW[std::min(63, turns)];
        return v;
    }
    double best = -1e18; bool any = false;
    for (int d = 0; d < 4; d++) {
        if (d == opp(lastDir)) continue;
        int u = w_.across(t, d);
        if (u == -2) { // cand-portal1: an unexplored portal is a leaf worth the frontier minus the blind risk
            double fv = lenNow >= P::BLIND_MIN_LEN ? frontierValue(t, d) : 0.0;
            if (fv > 0.0) {
                any = true;
                double v = (fv - blindRisk(lenNow)) * GPOW[std::min(63, turns + 1)];
                if (v > best) best = v;
            }
            continue;
        }
        if (u < 0) continue;
        if (!tileEnterable(u, stepBase + 1, removed, path)) continue;
        any = true;
        int arrive = w_.round + turns + 1;
        double p = SC.pnow[u];
        const Tile& x = w_.tiles[u];
        if (p < 0.05 && x.seen >= 0 && x.spawnRound > w_.round && x.spawnRound <= arrive) p = P::SPAWN_CONF;
        double g = GPOW[std::min(63, turns + 1)];
        double v = pearlValue(u, p) * g - threatAt(u) * g - softPenalty_[u] * g - portalPenalty(t, d, u) * g; // stack11 gh: pearlValue
        if (w_.edgeUnknown(t, d)) v -= P::UNKNOWN_EDGE_PENALTY * g;
        if (x.spawnRound == arrive + 1 && p < 0.5) v -= P::BLOCK_SPAWN_PENALTY * g; // our head would block the spawn tick
        path.push_back(u);
        bool eat = p >= 0.5;
        v += dfs<MODE>(u, d, depth + 1, maxDepth, removed + (eat ? 0 : 1), lenNow + (eat ? 1 : 0), path, deadline);
        path.pop_back();
        if (v > best) best = v;
    }
    if (!any) return DEATH * GPOW[std::min(63, turns)];
    return best;
}

// exp/portals (ptmod.cpp): dfs() with the Portals king's dead-end price on every step it looks ahead (ptmap.hpp DEAD)
double Planner::dfsPt(int t, int lastDir, int depth, int maxDepth, int removed, int lenNow, std::vector<int>& path, long long deadline) {
    int turns = depth;
    int stepBase = (int)path.size() - 1;
    nodes_++;
    bool over = nodes_ > P::DFS_NODE_BUDGET || (((nodes_ & 63) == 0) && nowPoints() > deadline);
    if (depth >= maxDepth || over) {
        const double g1 = GPOW[std::min(63, turns + 1)];
        double v = attract_[t] * g1 + exploreValue(t) * g1;
        if (frontierField_[t] > 0.0) v += frontierField_[t] * g1;
        int freeN = 0;
        for (int d = 0; d < 4; d++) { if (d == opp(lastDir)) continue; int u = w_.across(t, d); if (u >= 0 && tileEnterable(u, stepBase + 1, removed, path)) freeN++; }
        v += freeN * 0.15;
        if (goalOn_) v -= fGoal_ ? P::FG_W * std::max(0, std::min(goalDist_[t], 200) - P::FG_HOLD)
                                 : P::GH_ON ? (w_.round >= P::PT_ENDGAME_ROUND ? P::PT_END_GATHER_W : P::GATHER_W) * std::max(0, std::min(goalDist_[t], 200) - P::GH_HOLD)
                                 : P::GATHER_W * std::min(goalDist_[t], 200);
        if (kxOn_) v -= P::KX_W * std::max(0, P::KX_DIST - (int)kxDist_[t]);
        if (freeN == 0) v += DEATH * 0.5 * GPOW[std::min(63, turns)];
        return v;
    }
    double best = -1e18; bool any = false;
    for (int d = 0; d < 4; d++) {
        if (d == opp(lastDir)) continue;
        int u = w_.across(t, d);
        if (u == -2) {
            double fv = lenNow >= P::BLIND_MIN_LEN ? frontierValue(t, d) : 0.0;
            if (fv > 0.0) {
                any = true;
                double v = (fv - blindRisk(lenNow)) * GPOW[std::min(63, turns + 1)];
                if (ptKing_ && P::PT_KING_SAFE_ON) { int e = ptExit(t, d); if (e >= 0) v -= ptKingTilePen(e) * GPOW[std::min(63, turns + 1)]; }
                if (v > best) best = v;
            }
            continue;
        }
        if (u < 0) continue;
        if (!tileEnterable(u, stepBase + 1, removed, path)) continue;
        any = true;
        int arrive = w_.round + turns + 1;
        double p = SC.pnow[u];
        const Tile& x = w_.tiles[u];
        if (p < 0.05 && x.seen >= 0 && x.spawnRound > w_.round && x.spawnRound <= arrive) p = P::SPAWN_CONF;
        double g = GPOW[std::min(63, turns + 1)];
        double v = pearlValue(u, p) * g - threatAt(u) * g - softPenalty_[u] * g - portalPenalty(t, d, u) * g;
        if (w_.edgeUnknown(t, d)) v -= P::UNKNOWN_EDGE_PENALTY * g;
        if (x.spawnRound == arrive + 1 && p < 0.5) v -= P::BLOCK_SPAWN_PENALTY * g;
        if (ptKing_ && P::PT_KING_SAFE_ON) v -= ptKingTilePen(u) * g;   // the module's price
        path.push_back(u);
        bool eat = p >= 0.5;
        v += dfsPt(u, d, depth + 1, maxDepth, removed + (eat ? 0 : 1), lenNow + (eat ? 1 : 0), path, deadline);
        path.pop_back();
        if (v > best) best = v;
    }
    if (!any) return DEATH * GPOW[std::min(63, turns)];
    return best;
}

// value of trading heads with this enemy this turn (0 = not allowed)
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
    if (!P::LNT_ON || !P::LNT_RAM_ON || w_.myLen > P::LNT_MAX_LEN || w_.unitCount < P::LNT_MIN_UNITS) return false; // stack11: LNT_RAM_ON
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
    if (cfg_->d8Veto) return lntD8(enemyId) <= P::LNT_D8_VETO && !lntKint(enemyId);   // v1 final: swarm rows but Slithery Fight
    return lntD3(enemyId) <= P::LNT_VETO_D3 && !lntKint(enemyId);
}

// v1 final (map atlas interim §2, elite head-ons by d8): our heads minus enemy heads with news within 3 rounds within Manhattan 8 of our head,
// the two parties excluded
int Planner::lntD8(int enemyId) const {
    int a = 0, e = 0;
    for (auto& [id, d] : w_.dragons) {
        if (id == w_.myId || id == enemyId || d.headT < 0 || w_.round - d.headSeen > 3) continue;
        if (w_.geo.manhattan(d.headT, w_.headT) > 8) continue;
        if (d.team == w_.myTeam) a++; else e++;
    }
    return a - e;
}

// stack10 lnt: a trade candidate the veto removed, worth pre - cost without the veto (pre <= 0: it was no trade anyway)
void Planner::lntVetoNote(double pre, double cost, int enemyId) {
    if (pre <= 0.0) return;
    if (pre - cost > lntVetoBest_) { lntVetoBest_ = pre - cost; lntVetoD3_ = lntD3(enemyId); }
}

// stack1 M2 (B3): a small piece with a visible enemy head one step away that is at least as long (proven length)
bool Planner::smallRam(int enemyId) const {
    if (!P::RAM_SMALL_ON || w_.myLen > P::RAM_SMALL_MAX_LEN || w_.unitCount < 2) return false; // never risk elimination
    auto it = w_.dragons.find(enemyId);
    if (it == w_.dragons.end()) return false;
    const Dragon& d = it->second;
    if (d.team == w_.myTeam || d.headT < 0 || d.headSeen != w_.round || std::max(d.minLen, 2) < w_.myLen) return false;
    bool adjacent = false;
    for (int dir = 0; dir < 4; dir++) if (w_.across(w_.headT, dir) == d.headT) adjacent = true;
    if (!adjacent) return false;
    if (!P::RAM_SMALL_NEED_COLLECTOR) return true;
    for (int aid : w_.allyHeadsNow) {  // a collector for the pearls of both bodies
        auto ai = w_.dragons.find(aid);
        if (ai != w_.dragons.end() && ai->second.headT >= 0 && w_.geo.manhattan(ai->second.headT, d.headT) <= P::RAM_COLLECTOR_DIST) return true;
    }
    return false;
}

double Planner::tradeValueBase(int enemyId) const {
    auto it = w_.dragons.find(enemyId);
    if (it == w_.dragons.end()) return 0.0;
    const Dragon& d = it->second;
    if (w_.unitCount < 2) return 0.0;                // never risk elimination
    int le = std::max(d.minLen, 2), lm = w_.myLen;   // proven length only: never kamikaze on a guess
    bool king = w_.iAmLongest() && w_.unitCount >= 2 && lm >= 6;
    if (king) return 0.0;                            // the longest dragon never trades
    double v = 0.0;
    if (le >= lm + P::KILL_MIN_DIFF && le >= (int)(P::KILL_MIN_RATIO * lm)) v = P::W_KILL * (le - lm);
    if (le > w_.teamLongestKnown()) v = std::max(v, P::W_KILL * (le - lm + 2)); // removes the tiebreak leader
    if (w_.round >= P::ENDGAME_ANY_TRADE_ROUND && le > lm) v = std::max(v, P::W_KILL * (le - lm));
    // escort: a neutral trade is worth it when this enemy shadows a much longer teammate
    if (v <= 0.0 && le >= lm - 1 && w_.unitCount >= 3) {
        for (auto& [aid, a] : w_.dragons) {
            if (aid == w_.myId || a.team != w_.myTeam || a.headT < 0 || w_.round - a.headSeen > 3) continue;
            if (a.estLen >= 2 * lm + 4 && w_.geo.manhattan(a.headT, d.headT) <= 4) v = std::max(v, P::W_ESCORT * a.estLen);
        }
    }
    return v;
}

// ------------------------------------------------------------------------------------------------
bool Planner::wantSplit(int& size) const {
    if (w_.round > P::SPLIT_LAST_ROUND) return false;
    if (w_.round >= P::GATHER_START && w_.unitCount >= 2) return false; // gathering: only the lone dragon's insurance split
    int L = w_.myLen;
    int tiles = w_.geo.tiles();
    int cap = std::min(P::SPLIT_CAP_BASE, std::max(2, tiles / 60));
    int pearlsInView = 0; for (int t = 0; t < tiles; t++) if (w_.tiles[t].seen == w_.round && w_.tiles[t].pearlSeen == w_.round) pearlsInView++;
    if (w_.fountainCount >= 4 || pearlsInView >= 3) cap = std::min(P::SPLIT_CAP_RICH, std::max(cap, tiles / 50));
    if (w_.unitCount >= std::min(w_.unitLimit, cap)) return false;
    if (w_.unitCount == 1) {
        if (tiles < P::SPLIT_SMALL_MAP_TILES && L < P::SPLIT_LEN) return false;
        if (L < P::SPLIT_FIRST_LEN) return false;
        size = P::SPLIT_FIRST_CHILD;
    } else {
        if (L < P::SPLIT_LEN) return false;
        if (w_.iAmLongest() && (P::BELIEF_FIX_ON ? w_.freshAllyLen : w_.maxAllyLenSeen) > 0) return false; // the king only splits for insurance
        size = P::SPLIT_CHILD;
    }
    if (L - size < 2 || size < 2) return false;
    if (!P::SPLIT_TAIL_ON) return childSafe();
    if (!childSafe()) return false;
    // stack4 split tail: the child's head (our tail) far from every enemy head seen within 3 rounds. Failure study: a child
    // born with an enemy head within 4 died within 30 rounds 43% of the time (5-8: 29%, 9+: 12%); the check above
    // (enemyDist_[tail] <= 2) never saw our tail, an occupied tile, in stack3's field. Long parents' tails are out of view.
    int far = SC.enemyFar[w_.body[L - 1]];   // childSafe() checked the tail tile
    splitTailDist_ = std::min(far, 99);
    if (far <= P::SPLIT_TAIL_DIST) { splitTailBlocked_ = true; return false; }
    return true;
}

// No enemy head in view, and the child's head (our tail) has known, open surroundings with no enemy in reach.
bool Planner::childSafe() const {
    int L = w_.myLen;
    if (!w_.enemyHeadsNow.empty()) return false;
    // the child's head is our tail: its surroundings must be known and open, with no enemy in reach
    if (w_.body.empty() || (int)w_.body.size() < L) return false;
    int tail = w_.body[L - 1], neck = w_.body[L - 2];
    if (tail < 0 || neck < 0) return false;
    const Tile& tt = w_.tiles[tail];
    if (tt.seen < w_.round - 1) return false;
    for (int d = 0; d < 4; d++) if (tt.edge[d] == EDGE_UNKNOWN) return false;
    // stack4 tg: this check keeps stack3's field, so fragment and policy splits do not change with TG_ON (the split tail
    // rule, SPLIT_TAIL_ON, is the separate fix for the child's safety)
    const std::vector<int16_t>& ed = P::TG_ON ? enemyDistOld_ : enemyDist_;
    if (ed[tail] <= 2) return false;
    int exits = 0;
    for (int d = 0; d < 4; d++) {
        int u = w_.across(tail, d);
        if (u < 0 || u == neck) continue;
        if (w_.occNow[u] != 0 || ed[u] <= 1) continue;
        exits++;
    }
    return exits >= P::SPLIT_MIN_CHILD_EXITS;
}

// stack2 S1 (mass ledger H3, coverage for H2): from FRAG_START to FRAG_END a non-king dragon of length >= FRAG_MIN_LEN splits
// off a FRAG_CHILD-segment piece that forages and can later be converted into a big ally (stack1 conv). Top winners hold
// 27.4 dragons at r400 (merge2 4.3); the policy split above stops at GATHER_START and caps units at 3-5.
bool Planner::wantFrag(int& size, bool fc) const {
    fragWide_ = false;                                                                         // stack9 fc
    if (!P::FRAG_ON || w_.round < P::FRAG_START || w_.round > P::FRAG_END) return false;
    if (w_.myLen < P::FRAG_MIN_LEN || w_.round - lastFragRound_ < P::FRAG_GAP) return false;
    int cap = std::clamp(w_.geo.tiles() / P::FRAG_TILES_PER_UNIT, P::FRAG_CAP_MIN, P::FRAG_CAP_MAX);
    // stack9 fc (supply-chain proposal 4): the cap widened to csplit's target; " fc" when the old cap alone would have stopped us
    if (P::FRAG_CAP_CSPLIT_ON && fc) {                                                          // v1 5b: fc off on Autarky and PD6
        fragWide_ = w_.unitCount >= std::min(w_.unitLimit, cap);
        cap = std::max(cap, std::clamp(w_.geo.tiles() / P::CSPLIT_TILES_PER_UNIT, P::CSPLIT_TARGET_MIN, P::CSPLIT_TARGET_MAX));
    }
    if (w_.unitCount >= std::min(w_.unitLimit, cap)) return false;
    if (!longerAllyKnown(P::FRAG_KING_MEMORY)) return false;   // never the king: its length is the score
    size = P::FRAG_CHILD;
    if (w_.myLen - size < 2) return false;
    return childSafe();
}

// cand-mapid bsplit (hypothesis #14, research/experiments/cand-mapid.md): on Schooltime layout b, recognised by this process,
// a dragon of BSPLIT_MIN_LEN..BSPLIT_MAX_LEN splits off a BSPLIT_CHILD child in rounds <= BSPLIT_END while the team has fewer
// than BSPLIT_CAP units. Elite b teams split early dragons into 2-pieces (R2 22.4% on b vs 6.5% on a); our bot held 3.
bool Planner::wantBSplit(int& size) const {
    if (!P::BSPLIT_ON || !w_.mapIs("Schooltime", 'b')) return false;
    if (w_.round > P::BSPLIT_END || w_.myLen < P::BSPLIT_MIN_LEN || w_.myLen > P::BSPLIT_MAX_LEN) return false;
    if (w_.unitCount >= std::min(w_.unitLimit, P::BSPLIT_CAP)) return false;
    size = P::BSPLIT_CHILD;
    if (w_.myLen - size < 2) return false;
    return childSafe();
}

// stack2 S1: an ally seen or heard within maxAge rounds is longer than us (then we are not the king). Allies die out of
// sight (late feeding kills many): in the local check (v0) 15 of 137 fragment splits came from the real king; all 12
// inspected in three such games believed in a longer ally that was dead (10) or shorter (2). UNIT_COUNT tells how many
// allies live, so at least (believed - (unitCount - 1)) of the believed ones are dead; trust "not the king" only when
// more longer allies are believed than that (then at least one of them is alive).
bool Planner::longerAllyKnown(int maxAge) const {
    if (P::BELIEF_FIX_ON) return !w_.iAmLongest();   // v1 belief fix: the one king class (fresh news), not a 40-round memory
    int believed = 0, longer = 0;
    for (auto& [id, d] : w_.dragons) {
        if (id == w_.myId || d.team != w_.myTeam || d.headT < 0 || w_.round - d.headSeen > maxAge) continue;
        believed++;
        if (std::max(d.estLen, d.minLen) > w_.myLen) longer++;
    }
    return longer > std::max(0, believed - (w_.unitCount - 1));
}

// stack5 csplit (territory study 10, proposal 1): before CSPLIT_END, while the team has fewer units than the map-scaled
// target, a dragon of length >= CSPLIT_MIN_LEN splits off a CSPLIT_CHILD-segment piece that covers our territory. merge2's
// policy split (wantSplit) stays first and unchanged; its cap, king and length rules blocked 56% / 18% / 18% of merge2's
// dragon-turns on 500-round maps (study 7.4). An enemy head in view does not stop it (top winners: 40% of splits on 500-round
// maps, 23% on elimination maps); the child's spot does (csplitChildSafe).
bool Planner::wantCsplit(int& size) const {
    if (!P::CSPLIT_ON || w_.round < P::CSPLIT_START || w_.round >= P::CSPLIT_END) return false;
    int L = w_.myLen;
    if (L < P::CSPLIT_MIN_LEN || w_.round - lastCsplitRound_ < P::CSPLIT_GAP) return false;
    if (seedMap_ && w_.round < P::CSPLIT_SEED_START) return false;          // E1: long or many start dragons, not before r50
    csplitTarget_ = std::clamp(w_.geo.tiles() / P::CSPLIT_TILES_PER_UNIT, P::CSPLIT_TARGET_MIN, P::CSPLIT_TARGET_MAX);
    csplitTab_ = false;
    if (P::UTAB_ON) { int tt = utabTarget(); if (tt > 0) { csplitTarget_ = tt; csplitTab_ = true; } } // stack10 utab: the layout table
    if (w_.unitCount >= std::min(w_.unitLimit, csplitTarget_)) return false;
    // the king (length >= KING_MIN_LEN) keeps its length: only a dragon that knows a longer ally splits at that length
    if (L >= P::KING_MIN_LEN && !longerAllyKnown(P::FRAG_KING_MEMORY)) return false;
    size = P::CSPLIT_CHILD;
    if (L - size < 2) return false;
    return csplitChildSafe(P::CSPLIT_TAIL_DIST, P::SPLIT_MIN_CHILD_EXITS);
}

// stack10 utab (economy-principles study 7 and 14, proposal 2): top winners' median dragon count per recognised layout (mapdb family name,
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

// stack5 csplit: childSafe() without its "no enemy head in view" rule. The child's head (our tail) must be known and open,
// with >= minExits exits (csplit: SPLIT_MIN_CHILD_EXITS), and no enemy head within tailDist steps of it (csplit: CSPLIT_TAIL_DIST).
// childSafe()'s near-tail rule (enemyDist_[tail] <= 2) never fired: the enemy field gives no distance to an occupied tile such as our tail (failure study,
// stack4 cand-stack4.md). SC.enemyFar (heads seen within 3 rounds) passes tiles once they are vacated; an enemy head beside the
// tail is seen through the neighbour it stands on. stack7 floor and kcap use it with FLOOR_TAIL_DIST and FLOOR_MIN_EXITS.
bool Planner::csplitChildSafe(int tailDist, int minExits) const {
    int L = w_.myLen;
    if (w_.body.empty() || (int)w_.body.size() < L) return false;
    int tail = w_.body[L - 1], neck = w_.body[L - 2];
    if (tail < 0 || neck < 0) return false;
    const Tile& tt = w_.tiles[tail];
    if (tt.seen < w_.round - 1) return false;
    for (int d = 0; d < 4; d++) if (tt.edge[d] == EDGE_UNKNOWN) return false;
    int near = SC.enemyFar[tail];
    for (int d = 0; d < 4; d++) { int u = w_.across(tail, d); if (u >= 0 && u != neck) near = std::min(near, SC.enemyFar[u] + 1); }
    if (near <= tailDist) return false;
    const std::vector<int16_t>& ed = P::TG_ON ? enemyDistOld_ : enemyDist_;  // as childSafe()
    int exits = 0;
    for (int d = 0; d < 4; d++) {
        int u = w_.across(tail, d);
        if (u < 0 || u == neck) continue;
        if (w_.occNow[u] != 0 || ed[u] <= 1) continue;
        exits++;
    }
    return exits >= minExits;
}

// stack7 map gate (elimination study 4, "지도 가르기"): floor and kcap only on the map families we lose (Trophy, Queen Of Spades,
// Devil, Default, Schooltime, Trauma, Slithery Fight), as this process recognised them. Off on Autarky, Prisoners Dilemma (both
// versions) and Portals, where our structure wins and early splits cost the elite family length too (E1: -0.83, -0.96, -0.35), and
// off before the family is known or after a contradiction ("map=none"). kcap: not on Slithery Fight either (start L25; the study
// keeps kcap to maps whose start dragons are all of length <= 4).
bool Planner::floorMapOn() const {
    for (const char* f : {"Trophy", "Queen_Of_Spades", "Devil", "Default", "Schooltime", "Trauma", "Slithery_Fight"})
        if (w_.mapFamIs(f)) return true;
    return false;
}
bool Planner::kcapMapOn() const { return floorMapOn() && !w_.mapFamIs("Slithery_Fight"); }

// stack7 kcap (elimination study 4, proposal 2): before KCAP_END, while the team has fewer than KCAP_UNITS dragons, the dragon
// that believes it is our longest and is >= KCAP_LEN long splits off a KCAP_CHILD child. King kills end 16% of our eliminations
// (top eliminated losers 6%): our lost kings were L12.3 on average, rammed by 4.7-long sprinters with 1.7 of our dragons left.
// csplit (tried first) keeps a king of length >= KING_MIN_LEN whole; kcap cuts it, and an L7 king in csplit's gap.
bool Planner::wantKcap(int& size) const {
    if (!P::KCAP_ON || w_.round >= P::KCAP_END) return false;
    int L = w_.myLen;
    if (L < P::KCAP_LEN || !w_.iAmLongest() || w_.unitCount >= std::min(w_.unitLimit, P::KCAP_UNITS)) return false;
    if (!kcapMapOn()) return false;
    size = P::KCAP_CHILD;
    if (L - size < 2) return false;
    return csplitChildSafe(P::FLOOR_TAIL_DIST, P::FLOOR_MIN_EXITS);
}

// stack7 floor (elimination study 4, proposal 1): from FLOOR_START, while the team has <= FLOOR_UNITS dragons, a dragon of length
// >= FLOOR_MIN_LEN splits off a FLOOR_CHILD child even with enemy heads in view (the child's spot is checked). Top losers that
// survive split 2.0 times in the 20 rounds after falling to <= 3 dragons and 23-26% recover to >= 4; our eliminated games 0.5 and
// 5%, with the length to split (total 13.2, longest 7.1). The king is included before GATHER_START; from then the late gathering
// concentrates length on the king, so only a dragon that knows a longer ally splits, and a lone dragon keeps the insurance split's
// length rule (SPLIT_FIRST_LEN; the study leaves it to that split, now without the "no enemy head in view" rule).
bool Planner::wantFloor(int& size) const {
    if (!P::FLOOR_ON || w_.round < P::FLOOR_START || w_.round > P::SPLIT_LAST_ROUND) return false;
    int L = w_.myLen;
    if (L < P::FLOOR_MIN_LEN || w_.unitCount > P::FLOOR_UNITS || w_.unitCount >= w_.unitLimit) return false;
    if (w_.round >= P::GATHER_START && (w_.unitCount == 1 ? L < P::SPLIT_FIRST_LEN : !longerAllyKnown(P::FRAG_KING_MEMORY))) return false;
    if (!floorMapOn()) return false;
    size = P::FLOOR_CHILD;
    if (L - size < 2) return false;
    return csplitChildSafe(P::FLOOR_TAIL_DIST, P::FLOOR_MIN_EXITS);
}

// stack9 lsplit (supply-chain study 6-7, proposal 1): from LSPLIT_START to LSPLIT_END, while the team has fewer units than csplit's
// target, a dragon of length LSPLIT_MIN_LEN..LSPLIT_MAX_LEN splits off an LSPLIT_CHILD piece, at most once in LSPLIT_GAP rounds. Top
// winners give birth to 156 pieces a game in r250-499 on 500-round maps (120 of them by 4 -> 2 + 2), stack5 / stack6 8.7 / 7.1 (nearly
// all escape splits); the late pieces carry field pearls to the big allies (conv, piece-to-piece sacrifices). decide() tries it after
// every other split rule, so it only takes turns they leave; the child's spot and the king rule are csplit's.
bool Planner::wantLsplit(int& size) const {
    if (!P::LSPLIT_ON || w_.round < P::LSPLIT_START || w_.round >= P::LSPLIT_END) return false;
    int L = w_.myLen;
    if (L < P::LSPLIT_MIN_LEN || L > P::LSPLIT_MAX_LEN || w_.round - lastLsplitRound_ < P::LSPLIT_GAP) return false;
    lsplitTarget_ = std::clamp(w_.geo.tiles() / P::CSPLIT_TILES_PER_UNIT, P::CSPLIT_TARGET_MIN, P::CSPLIT_TARGET_MAX);
    if (w_.unitCount >= std::min(w_.unitLimit, lsplitTarget_)) return false;
    if (L >= P::KING_MIN_LEN && !longerAllyKnown(P::FRAG_KING_MEMORY)) return false;   // csplit's king rule (never binds at L <= 6)
    size = P::LSPLIT_CHILD;
    if (L - size < 2) return false;
    return csplitChildSafe(P::CSPLIT_TAIL_DIST, P::SPLIT_MIN_CHILD_EXITS);
}

// stack5 F / cov: our side = tiles nearer (torus Manhattan) to our first head tile than their mirror image is. The enemy starts
// on the mirror of our start, so near our start this is the study's territory (a tile belongs to the team whose starting
// bodies are nearer). Unknown until the symmetry is resolved.
bool Planner::ourSide(int t) const {
    if (w_.sym < 0 || homeT_ < 0) return false;
    int m = w_.mirrorTile(t, w_.sym);
    return m != t && w_.geo.manhattan(homeT_, t) < w_.geo.manhattan(homeT_, m);
}

// stack9 cov: our side by the recognised map's territory (the table side of our first head tile, World::mapTerrAt, F2's rule: the
// server swaps the file's team letters in about half of the online games, and the mirror rule missed the territory on 13% of W5-W6
// F targets), else ourSide() (before recognition, where the table maps left disagree, or from a neutral first head tile).
bool Planner::covSide(int t) const {
    int v = w_.mapTerrAt(t, homeT_);
    if (v >= 0) return v == 1;
    return ourSide(t);
}

// stack5 F (territory study 10, proposal 2): before GATHER_START, when no gathering goal is on, a dragon that is not the king
// heads for the nearest known fountain of our side (a mirrored fountain counts: mirrored tiles share one countdown) that no
// ally head guards (seen or heard within FG_ALLY_STALE rounds, within FG_GUARD_DIST; an ally nearer to it than we are, or
// as near with a lower id). The goal field (goalDist_) is the path distance to its group (our side's known fountains within
// FG_GROUP_DIST of it) and the leaf penalty spares FG_HOLD steps around it, so the dragon holds the group and eats there.
void Planner::computeFountainGoal() {
    fGoal_ = false; fTable_ = false; fPause_ = -1;                                       // stack8
    if (!P::FGUARD_ON || goalOn_ || w_.round >= P::GATHER_START || w_.unitCount < P::FG_MIN_UNITS) { fTarget_ = -1; return; }
    if (w_.iAmLongest() && w_.myLen >= P::KING_MIN_LEN) { fTarget_ = -1; return; } // the king feeds itself
    if (w_.sym < 0 || homeT_ < 0) return;
    int n = w_.geo.tiles();
    auto fountOld = [&](int t) { if (w_.isFountain(t)) return true; if (w_.tiles[t].seen >= 0) return false; int m = w_.mirrorTile(t, w_.sym); return m != t && w_.isFountain(m); };
    // stack8 F2: the recognised map's own fountains and territory (where the table maps left agree), else the old rules
    auto fount = [&](int t) { if (P::F2_ON) { int f = w_.mapFountAt(t); if (f >= 0) return f == 1; } return fountOld(t); };
    auto side = [&](int t) { if (P::F2_ON) { int v = w_.mapTerrAt(t, homeT_); if (v >= 0) return v == 1; } return ourSide(t); };
    std::vector<std::pair<int, int>> allyHeads; // (tile, id)
    for (auto& [id, d] : w_.dragons)
        if (id != w_.myId && d.team == w_.myTeam && d.headT >= 0 && w_.round - d.headSeen <= P::FG_ALLY_STALE) allyHeads.push_back({d.headT, id});
    auto guardedByOther = [&](int t) {
        int mine = w_.geo.manhattan(w_.headT, t);
        for (auto& [a, id] : allyHeads) {
            int da = w_.geo.manhattan(a, t);
            if (da <= P::FG_GUARD_DIST && (da < mine || (da == mine && id < w_.myId))) return true;
        }
        return false;
    };
    auto usable = [&](int t) { return t >= 0 && fount(t) && side(t) && headDist_[t] >= 0 && headDist_[t] <= P::FG_MAX_DIST && !guardedByOther(t); };
    int target = -1;
    if (P::F2_ON) {
        // stack8 F2: a new target is within FG2_MAX_DIST, no fresh ally head is within FG_GUARD_DIST of it (it is covered already),
        // and no ally head of a non-king length seen or heard within FG2_CLAIM_STALE rounds is nearer to it (Manhattan; ties to the
        // lower id), so two heads do not chase one fountain. The held target is kept within FG2_KEEP_DIST under the old guard rule.
        auto takenByAlly = [&](int t) {
            int mine = w_.geo.manhattan(w_.headT, t);
            for (auto& [a, id] : allyHeads) {
                int da = w_.geo.manhattan(a, t);
                if (da <= P::FG_GUARD_DIST) return true;
                const Dragon& o = w_.dragons.at(id);
                if (w_.round - o.headSeen <= P::FG2_CLAIM_STALE && o.estLen < P::KING_MIN_LEN && (da < mine || (da == mine && id < w_.myId))) return true;
            }
            return false;
        };
        if (fTarget_ >= 0 && headDist_[fTarget_] >= 0 && headDist_[fTarget_] <= P::FG2_KEEP_DIST && fount(fTarget_) && side(fTarget_) && !guardedByOther(fTarget_)) target = fTarget_;
        if (target < 0) {
            int bd = 1 << 20;
            for (int t = 0; t < n; t++)
                if (headDist_[t] >= 0 && headDist_[t] <= P::FG2_MAX_DIST && headDist_[t] < bd && fount(t) && side(t) && !takenByAlly(t)) { bd = headDist_[t]; target = t; }
        }
        fTable_ = target >= 0 && w_.mapFountAt(target) >= 0 && w_.mapTerrAt(target, homeT_) >= 0;
    } else {
        target = usable(fTarget_) ? fTarget_ : -1;   // keep the fountain we hold or head for
        if (target < 0) {
            int bd = 1 << 20;
            for (int t = 0; t < n; t++) if (headDist_[t] >= 0 && headDist_[t] < bd && usable(t)) { bd = headDist_[t]; target = t; }
        }
    }
    fTarget_ = target;
    if (target < 0) return;
    goalDist_.assign(n, 9999);
    queue_.clear();
    for (int t = 0; t < n; t++)
        if (w_.geo.manhattan(t, target) <= P::FG_GROUP_DIST && (t == target || (fount(t) && side(t)))) { goalDist_[t] = 0; queue_.push_back(t); }
    for (size_t qi = 0; qi < queue_.size(); qi++) {
        int t = queue_[qi];
        for (int dir = 0; dir < 4; dir++) {
            int u = w_.across(t, dir);
            if (u < 0 || goalDist_[u] <= goalDist_[t] + 1) continue;
            goalDist_[u] = goalDist_[t] + 1; queue_.push_back(u);
        }
    }
    goalOn_ = fGoal_ = goalDist_[w_.headT] < 9999;
    // stack8 F2p: no pull while we hold a live claim outside the hold zone (the nearest one is named in the tag); the target stays
    if (P::F2P_ON && fGoal_) {
        int bd = 1 << 20;
        // only while the claim is still ours now (no known head nearer, as when it was made): F2p's own gate is "no nearer head"
        for (auto& c : claims_) { int t = c.first; if (goalDist_[t] > P::FG_HOLD && headDist_[t] >= 0 && headDist_[t] < bd && headDist_[t] <= SC.allyFar[t] && headDist_[t] <= SC.enemyFar[t]) { bd = headDist_[t]; fPause_ = t; } }
        if (fPause_ >= 0) goalOn_ = fGoal_ = false;
    }
}

// stack2 S2: tile t holds a death drop (World::ingestTiles) first seen within GRAB_ROUNDS, still there at our last sight
bool Planner::freshDrop(int t) const {
    const Tile& x = w_.tiles[t];
    return x.dropSeen >= 0 && w_.round - x.dropSeen <= P::GRAB_ROUNDS && x.pearlSeen > x.emptySeen;
}

// cand-portal1: the ray leaves our head as it stands AFTER this turn's action (fromT, facing). Probe a portal on an edge of
// that tile: an unexplored one first (so we may enter it next turn), else a known one whose exit we cannot see.
// A ray opposite to our facing would leave from the tail, so that direction is never a probe.
int Planner::pickSonarDir(int fromT, int facing, bool* probe) const {
    if (probe) *probe = false;
    if (fromT >= 0) {
        int bestD = -1; double bestV = 0.0;
        for (int d = 0; d < 4; d++) {
            if (d == opp(facing) || w_.tiles[fromT].edge[d] != EDGE_PORTAL) continue;
            int u = w_.across(fromT, d);
            double v = 0.0;
            if (u == -2) v = 2.0 + frontierValue(fromT, d);
            else if (u >= 0 && w_.tiles[u].seen != w_.round) v = 1.0;
            if (v > bestV) { bestV = v; bestD = d; }
        }
        if (bestD >= 0) { if (probe) *probe = true; return bestD; }
    }
    int d = (turnCounter_ + w_.myId) & 3;     // not a probe: the rotation as before (relative to the facing we started with)
    if (d == opp(w_.myDir)) d = w_.myDir;
    return d;
}

// late game: every ray carries our message so the team learns where the king and the feeders are (c10)
void Planner::setSonar(Action& act) const {
    bool probe = false;
    int fromT = w_.headT, facing = w_.myDir;
    if (act.kind == Action::MOVE) {
        if (act.path.empty()) fromT = -1; // blind portal entry: we do not know where the head comes out
        else { fromT = act.path.back(); facing = dirFromChar(act.dirs.empty() ? 'N' : act.dirs.back()); if (facing < 0) facing = w_.myDir; }
    }
    act.sonarDir = pickSonarDir(fromT, facing, &probe);
    // unsw-swarm v1: in the swarm engine the hotspot field carries our sd claim (research transfer 1, 7); every ray from broadcastRound
    act.hotT = cfg_->claimSonar ? (fGoal_ && sdAnchor_ >= 0 ? sdAnchor_ : -1) : pickHotspot();
    act.sonarFromT = fromT;
    act.sonarAll = !probe && w_.round >= cfg_->broadcastRound;
    // every other turn a non-king passes on the king's last known head, so news of it spreads beyond its own rays
    if (act.sonarAll && !gatherKing_ && goalId_ >= 0 && ((w_.round + w_.myId) & 1)) {
        act.relayId = goalId_; act.relayRound = goalRound_; act.relayT = goalT_; act.relayLen = goalLen_;
    }
    // v1.1 C king beacon (params.hpp KING_BEACON_ON): the believed king reports on all four rays every KING_BEACON_EVERY rounds (the swarm king
    // already does every turn); before GATHER_BROADCAST a FORTRESS non-king passes fresh news of a longer ally on once per KING_BEACON_EVERY
    // rounds (no relays run there yet). Never on a portal probe; the relay keeps the news round, so a dead king's news does not stay fresh.
    if (P::KING_BEACON_ON) {
        beaconTag_ = 0;
        if (probe) return;
        if (w_.iAmLongest() && w_.myLen >= P::KING_MIN_LEN) {
            if (w_.round % P::KING_BEACON_EVERY == 0) { if (!act.sonarAll) beaconTag_ = 1; act.sonarAll = true; act.relayId = -1; }
        } else if (!cfg_->swarm && !act.sonarAll && w_.round < P::GATHER_BROADCAST && w_.freshAllyId >= 0 && w_.freshAllyLen > w_.myLen &&
                   w_.freshAllyT >= 0 && w_.round - w_.freshAllyHeadRound <= P::BEACON_RELAY_AGE && w_.round - beaconRelayRound_ >= P::KING_BEACON_EVERY) {
            act.sonarAll = true; beaconTag_ = 2; beaconRelayRound_ = w_.round;
            act.relayId = w_.freshAllyId; act.relayRound = w_.freshAllyHeadRound; act.relayT = w_.freshAllyT; act.relayLen = w_.freshAllyLen;
        }
    }
}

// Gathering goal (c10): a non-king heads for the longest ally it has recent news of (seen, heard or relayed); the king
// keeps feeding itself. goalDist_ = path distance over known edges (bodies ignored).
void Planner::computeGoal() {
    goalOn_ = false; goalT_ = -1; gatherKing_ = true; goalId_ = -1; gxOff_ = false;
    if (w_.round < P::GATHER_BROADCAST) return;
    int n = w_.geo.tiles();
    // are we the king? any ally heard to be longer recently says no; the goal is the freshest such ally's head
    int goalLen = 0, goalAge = 1 << 20;
    if (P::BELIEF_FIX_ON) gatherKing_ = w_.iAmLongest();   // v1 belief fix: the one king class (fresh news)
    for (auto& [id, d] : w_.dragons) {
        if (id == w_.myId || d.team != w_.myTeam || d.headT < 0) continue;
        int age = w_.round - d.headSeen;
        int la = std::max(d.estLen, d.minLen);
        if (P::BELIEF_FIX_ON) { if (la <= w_.myLen || !w_.allyFresh(d, P::BELIEF_FRESH)) continue; }
        else {
            if (la <= w_.myLen || age > P::GATHER_KING_MEMORY) continue;
            gatherKing_ = false;
        }
        if (age > P::GATHER_STALE) continue;
        // prefer the longest; among similar lengths the fresher sighting
        if (la > goalLen + 2 || (la + 2 >= goalLen && age < goalAge)) { goalLen = la; goalAge = age; goalT_ = d.headT; goalId_ = id; goalRound_ = d.headSeen; goalLen_ = la; }
    }
    if (gatherKing_ || goalT_ < 0) { goalId_ = -1; return; }   // the king keeps feeding itself; the others come to it
    if (w_.round < P::GATHER_START) return;                      // news only: relayed, not yet followed
    if (w_.unitCount < P::GATHER_FEED_UNITS) return;             // few units: stay apart, one of us must survive (c10l)
    if (w_.myLen < P::GATHER_FEED_MIN_LEN) return;               // a one-pearl dragon is not worth the trip (c10n)
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
    // stack4 gx: not without the rounds to get there (failure study: gathering started with < 10 rounds of slack succeeded
    // 4 of 31 times; 24 of 85 failures were the game ending on the way)
    if (P::GX_ON && goalOn_ && goalDist_[w_.headT] + P::GX_SLACK >= 500 - w_.round) { goalOn_ = false; gxOff_ = true; }
}

// stack11 gh (drops): from GH_DROP_START, fresh death drops (freshDrop, a pearl likely there) within Manhattan GH_DROP_R of the head of an
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
    if (P::BELIEF_FIX_ON) return w_.iAmLongest();    // v1 belief fix: the one king class
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

int Planner::pickHotspot() const {
    int best = -1; double bv = 0.3;
    for (int t = 0; t < w_.geo.tiles(); t++) if (attract_[t] > bv) { bv = attract_[t]; best = t; }
    return best;
}

// cand-avoid2/3: is tile t (our head after this move) certainly within the reach of a visible enemy head that is
// (believed) shorter than us? Certain reach = visible segments now - 1 (it is at least that long). Path through tiles
// free now; bodies block (our current head tile becomes our neck).
bool Planner::exactlyExposed(int t) const {
    for (int id : w_.enemyHeadsNow) {
        auto it = w_.dragons.find(id); if (it == w_.dragons.end()) continue;
        const Dragon& d = it->second;
        int believed = d.tailSeen ? d.visLen : std::max(d.estLen, d.visLen);
        if (believed >= w_.myLen) continue;               // a longer enemy declines for its own reasons
        int reach = std::max(1, d.visLen - 1);
        if (w_.geo.manhattan(d.headT, t) > reach) continue;
        // small BFS (reach <= a few steps)
        std::vector<int> frontier{d.headT}, seen{d.headT};
        for (int step = 1; step <= reach; step++) {
            std::vector<int> nx;
            for (int a : frontier) for (int dir = 0; dir < 4; dir++) {
                int u = w_.across(a, dir);
                if (u < 0) continue;
                if (u == t) return true;
                if (w_.occNow[u] != 0 || std::find(seen.begin(), seen.end(), u) != seen.end()) continue;
                seen.push_back(u); nx.push_back(u);
            }
            frontier.swap(nx);
        }
    }
    return false;
}

// ------------------------------------------------------------------------------------------------
// unsw-swarm v1: the engine dispatch (before this turn's point clock starts in decideImpl)
Action Planner::decide() { return cfg_->swarm ? decideImpl<2>() : cfg_->econW4 ? decideImpl<1>() : cfg_->portals ? decideImpl<3>() : decideImpl<0>(); }

// MODE 0 = FORTRESS (stack11's decide()), 1 = FORTRESS with the W4-era economy (Autarky, PD6; v1 final item 5b), 2 = SWARM,
// 3 = FORTRESS with the Portals module (exp/portals, ptmod.cpp)
template <int MODE> Action Planner::decideImpl() {
    constexpr bool SW = MODE == 2, W4 = MODE == 1, PT = MODE == 3;
    initGpow();
    turnCounter_++;
    if (exposedPending_) { survivedExposures_++; exposedPending_ = false; } // we are alive: the shorter head declined
    nodes_ = 0;
    Action act;
    long long start = nowPoints();
    long long soft = start + P::POINTS_SOFT, hard = start + P::POINTS_HARD;
    int n = w_.geo.tiles();
    late_ = (500 - w_.round) <= P::ENDGAME_ROUNDS;
    ahead_ = w_.teamLongestKnown() > w_.bestEnemyLen + 1;
    kingSafe_ = P::KS_ON && (500 - w_.round) <= P::KS_ROUNDS && w_.iAmLongest() && w_.myLen >= P::KING_MIN_LEN; // stack1 M3
    kingSafe2_ = P::KS2_ON && (500 - w_.round) <= P::KS2_ROUNDS && w_.iAmLongest() && w_.myLen >= P::KING_MIN_LEN; // stack3 ks2
    // stack2 S2: not for the late king, computed here so that it does not depend on KS_ON (M3)
    grabOn_ = P::GRAB_ON && !((500 - w_.round) <= P::GRAB_KING_ROUNDS && w_.iAmLongest() && w_.myLen >= P::KING_MIN_LEN);
    splitTailBlocked_ = false; splitTailDist_ = 99; // stack4 split tail
    if constexpr (PT) {   // exp/portals
        ptKing_ = w_.iAmLongest() && w_.myLen >= P::KING_MIN_LEN; ptFire_ = 0;
        if (P::PT_KING_GRAB_ON) grabOn_ = P::GRAB_ON;   // the late king also races for fresh drops (no enemy reaches our half)
    }

    if (!w_.parsedOk || w_.headT < 0 || w_.tiles.empty()) {
        int order[4] = {w_.myDir, leftOf(w_.myDir), rightOf(w_.myDir), opp(w_.myDir)};
        act.dirs = std::string(1, DIRCH[w_.myDir]);
        if (w_.headT >= 0 && !w_.occNow.empty()) {
            for (int i = 0; i < 3; i++) { int u = w_.across(w_.headT, order[i]); if (u >= 0 && w_.occNow[u] == 0) { act.dirs = std::string(1, DIRCH[order[i]]); break; } }
        }
        act.indicator = "degraded";
        return act;
    }
    // stack5: our first head tile (F / cov: our side) and the E1 start check (csplit): a start dragon that sees many start
    // units or a long start dragon (its own length, or an ally's seen or heard by round 2)
    if (homeT_ < 0) {
        homeT_ = w_.headT;
        seedMap_ = w_.birthRound == 0 && (w_.unitCount >= P::CSPLIT_SEED_UNITS || w_.myLen >= P::KING_MIN_LEN);
    }
    if (w_.birthRound == 0 && w_.round <= 2 && w_.maxAllyLenSeen >= P::KING_MIN_LEN) seedMap_ = true;
    // a child cannot see the start: before CSPLIT_SEED_START any dragon that is, or has seen or heard, a dragon of ours of length
    // >= KING_MIN_LEN takes the map for one that starts with a long dragon (local check, 60 games: our dragons reached 8 before
    // r50 from round 1 on Autarky, PD and Slithery Fight, and in 3 of the 42 other games only from r28; children born at r2 and
    // r35 on Slithery Fight made 37 csplits before r50 under the start-only check)
    if (w_.round < P::CSPLIT_SEED_START && (w_.myLen >= P::KING_MIN_LEN || w_.maxAllyLenSeen >= P::KING_MIN_LEN)) seedMap_ = true;

    SC.bodyIndex.assign(n, -1);
    for (size_t i = 0; i < w_.body.size(); i++) if (w_.body[i] >= 0) SC.bodyIndex[w_.body[i]] = (int)i;
    if ((int)exploreStamp_.size() != n) { exploreStamp_.assign(n, -1); exploreVal_.assign(n, 0.0); }
    long long tp0 = nowPoints();
    computeEnemyDistance();
    long long tp1 = nowPoints();
    computeFrontier();
    computeSoftPenalty();
    if constexpr (SW) {      // unsw-swarm v1 swarm engine (versions/v1/VERSION.md "SWARM rule table"): one target rule (sd), no F / F2,
                             // no central gathering, no gh / kx; claims instead of hotspot pulls; spawn clearance
        sfHeld_ = -1;
        w_.ensureCore2();
        updateSide();
        if (cfg_->spawnClear) addSpawnClear();
        for (int t : ghdTiles_) ghDrop_[t] = 0;
        ghdTiles_.clear(); ghOn_ = false; kxOn_ = false;
        if (cfg_->claimSonar) takeClaims();
        computeAttractT<2>();
        computeGoalSwarm();
        if (cfg_->disperse) computeDisperseGoal(); else { fGoal_ = false; fTarget_ = -1; fPause_ = -1; }
        computeKingFloor();   // v1.1 B
    } else {
    computeGhDrops();        // stack11 gh (before the attraction field)
    computeAttractT<MODE>();
    if constexpr (PT) computeGoalPt(); else          // exp/portals: the module's gathering clock and endgame
    computeGoal();
    if constexpr (W4) { fGoal_ = false; fTarget_ = -1; fPause_ = -1; fTable_ = false; }   // 5b: no F / F2 / F2p on Autarky and PD6
    else computeFountainGoal();   // stack5 F (only when no gathering goal is on)
    computeKingAway();       // stack11 kx
    }
    long long tp2 = nowPoints();

    // ---- stack1 M1 conv (R3/K1, mass ledger H1): from CONV_START a small piece beside a big visible ally dies into its
    // neck so that ally eats the pearls. Top winners: 79% of sacrifices are length 2-3, 88% have an ally within 3 tiles,
    // 93% of the dropped pearls go to their own team, 47% to dragons of length >= 8 (the king gets only 22%).
    // Not with an enemy head in view, and not the stub an escape split just left behind (it dies in its dead end anyway).
    // stack2 S1: not a fragment-sized newborn either (born within FRAG_FORAGE rounds): it was split off to forage, and a
    // coiled parent next to it would otherwise eat it back at once (two segments for one pearl).
    bool youngPiece = P::FRAG_ON && w_.birthRound > 0 && w_.birthLen <= P::FRAG_CHILD && w_.round - w_.birthRound < P::FRAG_FORAGE;
    // ---- unsw-swarm v1 sf (ENGINE.md §3 C; params.hpp): the swarm engine's one conversion rule (it replaces stack1 conv, the gathering
    // feeds and the late-window feed there). Never the king class (the fresh World::iAmLongest). Two branches:
    //   main (from the map's clock): a piece (<= 4) dies beside the longest longer ally head in view, a dragon of 5-7 beside one >= max(length
    //     + 4, 8), within CONV_MAX_DIST path steps; not a newborn piece (FRAG_FORAGE) nor an escape split's stub;
    //   late (from FEED_FIRST_ROUND, the old late window's timing): any length, beside the longest longer ally head in view within
    //     FEED_MAX_DIST once round >= 500 - (length + distance + FEED_SLACK), so the ally can still eat the drops.
    // Both: no enemy head within SF_ENEMY_R of the ally's head, none nearer to our head than the ally + 1, the ally has rounds left; pickup
    // queue (research transfer 3): held while SF_QUEUE_MAX pearls already wait within SF_QUEUE_R of the ally's head (" sq#<id>").
    if constexpr (SW) {
        const bool lateWin = w_.round >= P::FEED_FIRST_ROUND;
        const bool mainOn = w_.round >= cfg_->convStart && w_.myLen <= P::SF_MID_MAX && w_.round - escSplitRound_ > 3 && !youngPiece;
        if ((mainOn || lateWin) && w_.unitCount >= P::CONV_MIN_UNITS && (int)w_.body.size() >= 2 && !w_.iAmLongest() && w_.inCore2(w_.headT)) {
            const bool mid = w_.myLen >= P::SF_MID_MIN;
            int feedTo = -1, feedDist = 99, feedLen = 0; bool feedLate = false;
            for (int id : w_.allyHeadsNow) {
                const Dragon& a = w_.dragons[id];
                int la = a.tailSeen && a.lastSeen == w_.round ? a.visLen : std::max(a.minLen, a.estLen);
                if (a.headT < 0 || la <= w_.myLen) continue;
                const bool mainOk = mainOn && ((!mid && !P::SF_PIECE_BIG_ONLY) || la >= std::max(w_.myLen + P::SF_MID_MARGIN, P::SF_MID_ALLY_MIN));
                if (!mainOk && !lateWin) continue;
                if (SC.enemyFar[a.headT] <= P::SF_ENEMY_R) continue;
                const int reach = lateWin ? std::max(P::CONV_MAX_DIST, P::FEED_MAX_DIST) : P::CONV_MAX_DIST;
                std::fill(distBuf_.begin(), distBuf_.end(), -1);
                queue_.clear(); queue_.push_back(a.headT); distBuf_[a.headT] = 0;
                int found = 99;
                for (size_t qi = 0; qi < queue_.size() && found == 99; qi++) {
                    int t = queue_[qi]; int dd = distBuf_[t];
                    if (dd >= reach) continue;
                    for (int dir = 0; dir < 4; dir++) {
                        int u = w_.across(t, dir);
                        if (u < 0 || distBuf_[u] >= 0) continue;
                        if (u == w_.headT) { found = dd + 1; break; }
                        if (w_.occNow[u] != 0 && SC.bodyIndex[u] < 0) continue;
                        distBuf_[u] = dd + 1; queue_.push_back(u);
                    }
                }
                if (found > reach || SC.enemyFar[w_.headT] <= found + 1 || w_.round + found > 499) continue;
                const bool viaMain = mainOk && found <= P::CONV_MAX_DIST;
                if (!viaMain && w_.round < 500 - (w_.myLen + found + P::FEED_SLACK)) continue;   // the late branch waits for its timing
                if (la > feedLen || (la == feedLen && found < feedDist)) { feedTo = id; feedDist = found; feedLen = la; feedLate = !viaMain; }
            }
            if (feedTo >= 0) {
                const int at = w_.dragons[feedTo].headT, ax = at % w_.geo.W, ay = at / w_.geo.W;
                int queued = 0;
                for (int dy = -P::SF_QUEUE_R; dy <= P::SF_QUEUE_R; dy++) for (int dx = -P::SF_QUEUE_R; dx <= P::SF_QUEUE_R; dx++) {
                    if (Geo::abs(dx) + Geo::abs(dy) > P::SF_QUEUE_R) continue;
                    if (SC.pnow[w_.geo.idx(w_.geo.wrapX(ax + dx), w_.geo.wrapY(ay + dy))] >= 0.5) queued++;
                }
                if (queued >= P::SF_QUEUE_MAX) sfHeld_ = feedTo;
                else {
                    act.dirs = std::string(1, DIRCH[opp(w_.myDir)]); // into our own neck: death with the body as it stands
                    char buf[80];
                    if (feedLate) snprintf(buf, sizeof buf, "feed #%d d%d L%d sf#%d a%d late", feedTo, feedDist, w_.myLen, feedTo, feedLen);
                    else snprintf(buf, sizeof buf, "feed #%d d%d L%d conv sf#%d a%d", feedTo, feedDist, w_.myLen, feedTo, feedLen);
                    act.indicator = buf;
                    return act;
                }
            }
        }
    }
    if (!SW && P::CONV_ON && w_.round >= (PT ? P::PT_CONV_START : P::CONV_START) && w_.myLen <= P::CONV_MAX_LEN && w_.unitCount >= P::CONV_MIN_UNITS &&   // stack1 conv: FORTRESS (sf replaces it); exp/portals: its clock
        w_.enemyHeadsNow.empty() && (int)w_.body.size() >= 2 && w_.round - escSplitRound_ > 3 && !youngPiece) {
        int feedTo = -1, feedDist = 99, feedLen = 0;
        for (int id : w_.allyHeadsNow) {
            const Dragon& a = w_.dragons[id];
            int la = a.tailSeen && a.lastSeen == w_.round ? a.visLen : std::max(a.minLen, a.estLen);
            if (a.headT < 0 || la < P::CONV_ALLY_MIN || la < w_.myLen + P::CONV_ALLY_MARGIN) continue;
            // path distance from its head to ours through free tiles and our own body (which turns to pearls)
            std::fill(distBuf_.begin(), distBuf_.end(), -1);
            queue_.clear(); queue_.push_back(a.headT); distBuf_[a.headT] = 0;
            int found = 99;
            for (size_t qi = 0; qi < queue_.size() && found == 99; qi++) {
                int t = queue_[qi]; int dd = distBuf_[t];
                if (dd >= P::CONV_MAX_DIST) continue;
                for (int dir = 0; dir < 4; dir++) {
                    int u = w_.across(t, dir);
                    if (u < 0 || distBuf_[u] >= 0) continue;
                    if (u == w_.headT) { found = dd + 1; break; }
                    if (w_.occNow[u] != 0 && SC.bodyIndex[u] < 0) continue;
                    distBuf_[u] = dd + 1; queue_.push_back(u);
                }
            }
            if (found <= P::CONV_MAX_DIST && (found < feedDist || (found == feedDist && la > feedLen))) { feedDist = found; feedTo = id; feedLen = la; }
        }
        if (feedTo >= 0) {
            act.dirs = std::string(1, DIRCH[opp(w_.myDir)]); // into our own neck: death with the body as it stands
            char buf[64]; snprintf(buf, sizeof buf, "feed #%d d%d L%d conv", feedTo, feedDist, w_.myLen);
            act.indicator = buf;
            return act;
        }
    }

    // ---- late consolidation: only the longest dragon counts at the end. A shorter dragon beside a longer teammate
    // dies in place so its ceil(L/2) dropped pearls lie where the teammate can eat them before round 500.
    bool gathering = !SW && w_.round >= (PT ? P::PT_GATHER_START : P::GATHER_START);   // unsw-swarm v1: no central gathering in the swarm engine (the late window stays); exp/portals: its clock
    lwkHeld_ = false;                                                                    // stack11 lwk
    // exp/portals: from PT_ENDGAME_ROUND the late feed runs down to PT_FEED_MIN_UNITS units (nothing on our half can reach the last dragon)
    const int feedMinUnits = PT && w_.round >= P::PT_ENDGAME_ROUND ? P::PT_FEED_MIN_UNITS : 3;
    if (!SW && (w_.round >= P::FEED_FIRST_ROUND || gathering) && w_.unitCount >= feedMinUnits && enemyDist_[w_.headT] > 4 && (int)w_.body.size() >= 2) {   // v1: sf's late branch in SWARM
        int feedTo = -1, feedDist = 99;
        [[maybe_unused]] int ptFeedLen = 0;          // exp/portals: the length of the ally chosen to be fed
        // the longest ally we know of (recently): before the late window only it is fed, not every longer ally (c10m)
        // stack11 lwk: the late window feeds the king class too, with kingLen from news of the last LWK_KING_FRESH rounds
        const bool lwk = P::LWK_ON && w_.round >= P::FEED_FIRST_ROUND;
        int oldTo = -1, oldDist = 99;                // stack11 lwk: the nearest longer ally outside the king class (the old rule's choice)
        int kingLen = 0;
        if (P::BELIEF_FIX_ON) kingLen = w_.freshAllyLen;   // v1 belief fix: the fresh king class, not a 100-round memory
        else
        for (auto& [id, d] : w_.dragons)
            if (id != w_.myId && d.team == w_.myTeam && d.headT >= 0 && w_.round - d.headSeen <= (lwk ? P::LWK_KING_FRESH : P::GATHER_KING_MEMORY))
                kingLen = std::max(kingLen, std::max(d.estLen, d.minLen));
        bool earlyOnlyKing = w_.round < P::FEED_FIRST_ROUND;
        for (int id : w_.allyHeadsNow) {
            const Dragon& a = w_.dragons[id];
            // a whole chain in view is exact; a sonar length can predate a split made this round
            int la = a.tailSeen && a.lastSeen == w_.round ? a.visLen : std::max(a.minLen, a.estLen);
            if constexpr (PT) { if (!(a.tailSeen && a.lastSeen == w_.round) && w_.ptLenActive) la = std::max(la, w_.ptLenOf(id)); }   // exp/portals: the length memory
            if (a.headT < 0 || la <= w_.myLen) continue;
            if (earlyOnlyKing && la < kingLen - 2) continue;
            const bool lwkOut = lwk && la < kingLen - 2;   // stack11 lwk: not the king class (the old late-window rule fed it)
            if (w_.round < P::FEED_FIRST_ROUND) { // gathering: not into a king with an enemy head beside it (c10h)
                bool contested = false;
                for (int eid : w_.enemyHeadsNow) if (w_.geo.manhattan(w_.dragons[eid].headT, a.headT) <= 3) contested = true;
                if (contested) continue;
            }
            // path distance from its head to our head through free tiles and our own body (which turns to pearls)
            std::fill(distBuf_.begin(), distBuf_.end(), -1);
            queue_.clear(); queue_.push_back(a.headT); distBuf_[a.headT] = 0;
            int found = 99;
            for (size_t qi = 0; qi < queue_.size() && found == 99; qi++) {
                int t = queue_[qi]; int dd = distBuf_[t];
                if (dd >= P::FEED_MAX_DIST) continue;
                for (int dir = 0; dir < 4; dir++) {
                    int u = w_.across(t, dir);
                    if (u < 0 || distBuf_[u] >= 0) continue;
                    if (u == w_.headT) { found = dd + 1; break; }
                    if (w_.occNow[u] != 0 && SC.bodyIndex[u] < 0) continue;
                    distBuf_[u] = dd + 1; queue_.push_back(u);
                }
            }
            if (lwkOut) { if (found < oldDist) { oldDist = found; oldTo = id; } continue; } // stack11 lwk
            if (found < feedDist) { feedDist = found; feedTo = id; if constexpr (PT) ptFeedLen = la; }
        }
        bool lateWindow = w_.round >= P::FEED_FIRST_ROUND && w_.round >= 500 - (w_.myLen + feedDist + (PT ? P::PT_FEED_SLACK : P::FEED_SLACK));
        // exp/portals PT_ENDFEED_ON: from PT_ENDGAME_ROUND a non-king feeds the king class on sight (within FEED_MAX_DIST), without waiting
        // for the late window: nothing on our half threatens the last dragons, and every round of waiting is a round the king cannot eat
        bool ptEndFeed = false;
        if constexpr (PT) ptEndFeed = P::PT_ENDFEED_ON && w_.round >= P::PT_ENDGAME_ROUND && feedTo >= 0 && ptFeedLen >= kingLen - 2;
        const bool feedNow = feedTo >= 0 && (lateWindow || ptEndFeed || (gathering && w_.unitCount >= P::GATHER_FEED_UNITS && w_.myLen >= P::GATHER_FEED_MIN_LEN));
        if (lwk && !feedNow && oldTo >= 0 && oldDist < 99) { // stack11 lwk: would the old rule (the nearest longer ally, any class) have fed?
            const int od = std::min(oldDist, feedDist);
            lwkHeld_ = w_.round >= 500 - (w_.myLen + od + P::FEED_SLACK) || (gathering && w_.unitCount >= P::GATHER_FEED_UNITS && w_.myLen >= P::GATHER_FEED_MIN_LEN);
        }
        if (feedNow) {
            act.dirs = std::string(1, DIRCH[opp(w_.myDir)]); // into our own neck: death with the body as it stands
            char buf[64]; snprintf(buf, sizeof buf, "feed #%d d%d L%d", feedTo, feedDist, w_.myLen);
            act.indicator = buf;
            return act;
        }
    }

    // ---- candidates: first action = 1 step, a justified 2-step sprint, or a probed unknown portal
    struct Cand { std::vector<int> dirs; std::vector<int> tiles; int removed; int pearls; double base; bool legal; bool trade; bool blind; bool esc = false; bool voluntary = false; bool px = false; bool px2 = false; };  // esc: cand-avoid6, voluntary: cand-portal1, px: stack4 (a crossing that pays a px penalty), px2: stack8
    std::vector<Cand> cands;
    std::vector<int> path;
    lntVetoBest_ = -1e18; lntVetoD3_ = 0;                                                  // stack10 lnt
    for (int d1 = 0; d1 < 4; d1++) {
        if (d1 == opp(w_.myDir) && w_.myLen >= 2) continue; // into our own neck
        int u1 = w_.across(w_.headT, d1);
        Cand c; c.dirs = {d1}; c.removed = 0; c.pearls = 0; c.base = 0; c.legal = false; c.trade = false; c.blind = false;
        if (u1 == -1) { cands.push_back(c); continue; }
        if (u1 == -2) { // unexplored portal: worth trying after a clean probe cast from this very tile in this direction
            c.blind = true; c.legal = true;
            double fv = w_.myLen >= P::BLIND_MIN_LEN ? frontierValue(w_.headT, d1) : 0.0;
            bool clean = probeOk_ && w_.probeDir == d1;
            c.base = fv - blindRisk(w_.myLen); // + the best ordinary safety, added below
            c.voluntary = clean && !late_ && !kingSafe_ && fv > 0.0; // stack1 M3: never for the late king
            if (!c.voluntary) c.base -= P::BLIND_DESPERATE_PENALTY; // only when all else is doomed
            cands.push_back(c); continue;
        }
        int hid = w_.headOf[u1];
        if (hid >= 0 && hid != w_.myId && w_.dragons[hid].team != w_.myTeam) {
            double tv = tradeValue(hid);
            c.tiles = {u1}; c.legal = tv > 0.0; c.trade = true; c.base = tv > 0.0 ? tv : DEATH;
            if (P::LNT_ON && tv <= 0.0) lntVetoNote(tradeValuePreVeto(hid), 0.0, hid);         // stack10 lnt
            cands.push_back(c); continue;
        }
        // cand-portal1: a known portal whose exit we cannot see: free right after a clean probe from here, dearer without
        // one, dearest when that probe hit a dragon (it may stand on the exit)
        double portalExtra = 0.0; bool pxHere = false, px2Here = false;
        if (w_.tiles[w_.headT].edge[d1] == EDGE_PORTAL && w_.tiles[u1].seen != w_.round) {
            bool probedHere = w_.probeRound == w_.round && w_.probeFromT == w_.headT && w_.probeDir == d1;
            portalExtra = !probedHere ? P::PORTAL_UNPROBED_PENALTY : (w_.probeClear ? 0.0 : P::PORTAL_DIRTY_PENALTY);
            // stack4 px: from GATHER_BROADCAST (our dragons crowd the king and its exits) or at length >= PX_LONG_LEN, an unprobed
            // crossing costs what a dirty probe costs (failure study: a L74 king crossed a known portal unprobed onto a body)
            if (P::PX_ON && !probedHere && (w_.round >= P::GATHER_BROADCAST || w_.myLen >= P::PX_LONG_LEN)) { portalExtra = P::PORTAL_DIRTY_PENALTY; pxHere = true; }
            if (P::PX_ON && pxPenalty(w_.headT, d1, u1) > 0.0) pxHere = true;
            // stack8 px2: last turn's probe from here through this portal stopped on a dragon of ours (it may stand on the exit)
            if (P::PX2_ON && probedHere && !w_.probeClear && w_.probeAlly) { portalExtra = std::max(portalExtra, P::PX2_ALLY_PENALTY); px2Here = true; }
        }
        path.assign(1, w_.headT);
        if (!tileEnterable(u1, 1, 0, path)) { cands.push_back(c); continue; }
        c.legal = true; c.tiles = {u1}; c.px = pxHere; c.px2 = px2Here;
        double p1 = SC.pnow[u1];
        c.pearls = p1 >= 0.5 ? 1 : 0; c.removed = c.pearls ? 0 : 1;
        double th1 = threatAt(u1);
        c.base = pearlValue(u1, p1) - th1 - softPenalty_[u1] - portalPenalty(w_.headT, d1, u1) - portalExtra - (w_.edgeUnknown(w_.headT, d1) ? P::UNKNOWN_EDGE_PENALTY : 0.0);
        if (w_.tiles[u1].spawnRound == w_.round + 1 && p1 < 0.5) c.base -= P::BLOCK_SPAWN_PENALTY;
        cands.push_back(c);
        // 2-step sprints cost a segment: only when they grab a pearl, escape a threat, or trade
        if (w_.myLen + c.pearls >= 3 && !late_) {
            for (int d2 = 0; d2 < 4; d2++) {
                if (d2 == opp(d1)) continue;
                int u2 = w_.across(u1, d2);
                if (u2 < 0) continue;
                if (w_.tiles[u1].edge[d2] == EDGE_PORTAL && w_.tiles[u2].seen != w_.round) continue; // no unprobed portal
                Cand s = c; s.dirs = {d1, d2}; s.legal = false; s.trade = false;
                int hid2 = w_.headOf[u2];
                if (hid2 >= 0 && hid2 != w_.myId && w_.dragons[hid2].team != w_.myTeam) {
                    double tv = tradeValue(hid2);
                    if (tv > 0.0) { s.tiles = {u1, u2}; s.legal = true; s.trade = true; s.base = tv - P::SPRINT_COST; cands.push_back(s); }
                    else if (P::LNT_ON) lntVetoNote(tradeValuePreVeto(hid2), P::SPRINT_COST, hid2);    // stack10 lnt
                    continue;
                }
                double p2 = SC.pnow[u2];
                double th2 = threatAt(u2);
                if (!(p2 >= 0.5 || (th1 > 0.0 && th2 <= 0.0))) continue;
                path.assign(1, w_.headT); path.push_back(u1);
                if (!tileEnterable(u2, 1, c.removed, path)) continue;
                s.legal = true; s.tiles = {u1, u2};
                s.pearls = c.pearls + (p2 >= 0.5 ? 1 : 0);
                s.removed = c.removed + (p2 >= 0.5 ? 0 : 1) + 1; // +1: sprint payment
                s.base = pearlValue(u1, p1) + pearlValue(u2, p2) - P::SPRINT_COST - th2 - softPenalty_[u2] - portalPenalty(u1, d2, u2)
                         - (w_.edgeUnknown(u1, d2) ? P::UNKNOWN_EDGE_PENALTY : 0.0)
                         - portalPenalty(w_.headT, d1, u1) - portalExtra; // cand-portal1: the first step's portal too
                cands.push_back(s);
            }
        }
    }

    // ---- cand-avoid2: ram escape. Every single step is threatened by a shorter head and no 2-step sprint reaches an
    // unthreatened tile: add 2-step (also late) and 3-step sprints that end on an unthreatened tile.
    bool escapeOn = w_.myLen >= P::ESCAPE_MIN_LEN && (survivedExposures_ < P::RAMMER_TRUST || kingSafe2_) && enemyDist_[w_.headT] <= 4; // stack3 ks2: no trust for the late king
    if (escapeOn) {
        bool allSinglesThreatened = true, anySingle = false, cleanSprint = false;
        for (const Cand& c : cands) {
            if (!c.legal || c.trade || c.blind || c.tiles.empty()) continue;
            if (c.dirs.size() == 1) { anySingle = true; if (threatAt(c.tiles[0]) <= 0.0) allSinglesThreatened = false; }
            else if (threatAt(c.tiles.back()) <= 0.0) cleanSprint = true;
        }
        if (anySingle && allSinglesThreatened && !cleanSprint) {
            // stack4 esc-split: cornered by shorter heads with a safe tail, hand the body to a child born at the tail instead of
            // sprinting. Failure study (merge2 cornered turns): body length kept after 30 rounds 77% after a split, 59% / 49%
            // after a 2 / 3-step sprint; tail >= 4 from every enemy head: 102% vs 76% / 48%. The stub (L2) stays in front.
            // Cornered = every single step inside the sprint reach of a short head (length <= 4 and shorter than us: the
            // study's definition), with the reach we are sure of: a head in view now, reach = its visible segments - 1, a path
            // over tiles free now (as exactlyExposed()). Estimated reaches (an unseen tail taken as 4 or 5, a pearl, a stale
            // sighting) fired it outside the studied situation in the local check (cornered: 16% of firings on tg's field,
            // 25% on stack3's). The trigger does not depend on TG_ON; ks2's long-range threats alone do not count.
            // The child's exits: the check of the escape split below.
            if (P::ESC_SPLIT_ON && w_.unitCount < w_.unitLimit && (int)w_.body.size() == w_.myLen) {
                auto surelyShort = [&](int t) {
                    for (int id : w_.enemyHeadsNow) {
                        auto it = w_.dragons.find(id); if (it == w_.dragons.end()) continue;
                        const Dragon& d = it->second;
                        int believed = d.tailSeen ? d.visLen : std::max(d.estLen, d.visLen);
                        if (believed > 4 || believed >= w_.myLen) continue;
                        int reach = std::max(1, d.visLen - 1);
                        if (w_.geo.manhattan(d.headT, t) > reach) continue;
                        std::vector<int> frontier{d.headT}, seen{d.headT};
                        for (int step = 1; step <= reach; step++) {
                            std::vector<int> nx;
                            for (int a : frontier) for (int dir = 0; dir < 4; dir++) {
                                int u = w_.across(a, dir);
                                if (u < 0) continue;
                                if (u == t) return true;
                                if (w_.occNow[u] != 0 || std::find(seen.begin(), seen.end(), u) != seen.end()) continue;
                                seen.push_back(u); nx.push_back(u);
                            }
                            frontier.swap(nx);
                        }
                    }
                    return false;
                };
                bool shorterAll = true;
                for (const Cand& c : cands) {
                    if (!c.legal || c.trade || c.blind || c.dirs.size() != 1) continue;
                    if (!surelyShort(c.tiles[0])) { shorterAll = false; break; }
                }
                int tail = w_.body[w_.myLen - 1], neck = w_.body[w_.myLen - 2];
                if (shorterAll && tail >= 0 && neck >= 0 && w_.tiles[tail].seen >= 0 && SC.enemyFar[tail] >= P::ESC_SPLIT_TAIL_DIST) {
                    int exits = 0;
                    for (int d = 0; d < 4; d++) { int u = w_.across(tail, d); if (u < 0 || u == neck) continue; if (w_.occNow[u] == 0 || u == w_.body[w_.myLen - 3 < 0 ? 0 : w_.myLen - 3]) exits++; }
                    if (exits > 0) {
                        act.kind = Action::SPLIT; act.splitSize = w_.myLen - 2;
                        escSplitRound_ = w_.round; // stack1: the stub left behind is not a conversion feeder
                        setSonar(act);
                        char buf[64]; snprintf(buf, sizeof buf, "esc-split%d L%d", act.splitSize, w_.myLen);
                        act.indicator = buf;
                        return act;
                    }
                }
            }
            std::vector<Cand> extra;
            for (const Cand& c : cands) {
                if (!c.legal || c.trade || c.blind || c.dirs.size() != 1) continue;
                int d1 = c.dirs[0], u1 = c.tiles[0];
                double p1 = SC.pnow[u1];
                for (int d2 = 0; d2 < 4; d2++) {
                    if (d2 == opp(d1)) continue;
                    int u2 = w_.across(u1, d2);
                    if (u2 < 0 || w_.headOf[u2] >= 0) continue;
                    path.assign(1, w_.headT); path.push_back(u1);
                    if (w_.myLen + c.pearls < 3 || !tileEnterable(u2, 1, c.removed, path)) continue;
                    double p2 = SC.pnow[u2];
                    int rem2 = c.removed + (p2 >= 0.5 ? 0 : 1) + 1, pe2 = c.pearls + (p2 >= 0.5 ? 1 : 0);
                    if (late_ && threatAt(u2) <= 0.0) { // 2-step sprints are otherwise off in the last rounds
                        Cand s2 = c; s2.esc = true; s2.dirs = {d1, d2}; s2.tiles = {u1, u2}; s2.pearls = pe2; s2.removed = rem2;
                        s2.base = pearlValue(u1, p1) + pearlValue(u2, p2) - P::SPRINT_COST - softPenalty_[u2] - portalPenalty(u1, d2, u2) - (w_.edgeUnknown(u1, d2) ? P::UNKNOWN_EDGE_PENALTY : 0.0);
                        s2.px = P::PX_ON && pxPenalty(u1, d2, u2) > 0.0; // stack4 px: the crossings this candidate pays for
                        extra.push_back(s2);
                    }
                    if (w_.myLen + pe2 - 1 < 3) continue; // the third step must be payable
                    for (int d3 = 0; d3 < 4; d3++) {
                        if (d3 == opp(d2)) continue;
                        int u3 = w_.across(u2, d3);
                        if (u3 < 0 || u3 == u1 || w_.headOf[u3] >= 0 || threatAt(u3) > 0.0) continue;
                        path.assign(1, w_.headT); path.push_back(u1); path.push_back(u2);
                        if (!tileEnterable(u3, 1, rem2, path)) continue;
                        double p3 = SC.pnow[u3];
                        Cand s3 = c; s3.esc = true; s3.dirs = {d1, d2, d3}; s3.tiles = {u1, u2, u3};
                        s3.pearls = pe2 + (p3 >= 0.5 ? 1 : 0); s3.removed = rem2 + (p3 >= 0.5 ? 0 : 1) + 1;
                        s3.base = pearlValue(u1, p1) + pearlValue(u2, p2) + pearlValue(u3, p3) - 2.0 * P::SPRINT_COST - softPenalty_[u3] - portalPenalty(u2, d3, u3) - (w_.edgeUnknown(u2, d3) ? P::UNKNOWN_EDGE_PENALTY : 0.0);
                        s3.px = P::PX_ON && pxPenalty(u2, d3, u3) > 0.0; // stack4 px
                        extra.push_back(s3);
                    }
                }
            }
            for (auto& x : extra) cands.push_back(x);
        }
    }

    // ---- kill paths: shortest open path of 3..STRIKE_MAX_STEPS steps into a tradeable enemy head
    if (w_.myLen >= 4 && w_.unitCount >= 2 && !late_) {
        int maxSteps = std::min(P::STRIKE_MAX_STEPS, w_.myLen - 1);
        for (int id : w_.enemyHeadsNow) {
            double tv = tradeValue(id);
            double tvPre = P::LNT_ON && tv <= 0.0 ? tradeValuePreVeto(id) : tv; // stack10 lnt: a vetoed target's path is searched for the " lntv" tag
            if (tvPre <= 0.0) continue;
            int target = w_.dragons[id].headT;
            std::fill(distBuf_.begin(), distBuf_.end(), -1);
            parBuf_.assign(n, -1);
            std::vector<int> pdir(n, -1);
            queue_.clear(); queue_.push_back(w_.headT); distBuf_[w_.headT] = 0;
            int found = -1;
            for (size_t qi = 0; qi < queue_.size() && found < 0; qi++) {
                int t = queue_[qi]; int dd = distBuf_[t];
                if (dd >= maxSteps) continue;
                for (int d = 0; d < 4; d++) {
                    if (t == w_.headT && d == opp(w_.myDir)) continue;
                    int u = w_.across(t, d);
                    if (u < 0 || distBuf_[u] >= 0) continue;
                    if (w_.tiles[t].edge[d] == EDGE_PORTAL && w_.tiles[u].seen != w_.round) continue; // cand-portal1
                    if (u == target) { if (dd + 1 >= 3) { parBuf_[u] = t; pdir[u] = d; distBuf_[u] = dd + 1; found = u; } continue; }
                    if (w_.occNow[u] != 0 || w_.headOf[u] >= 0) continue;
                    distBuf_[u] = dd + 1; parBuf_[u] = t; pdir[u] = d; queue_.push_back(u);
                }
            }
            if (found >= 0) {
                std::vector<int> dirs, tiles; int t = found;
                while (t != w_.headT) { dirs.push_back(pdir[t]); tiles.push_back(t); t = parBuf_[t]; }
                std::reverse(dirs.begin(), dirs.end()); std::reverse(tiles.begin(), tiles.end());
                if (tv <= 0.0) { lntVetoNote(tvPre, ((int)dirs.size() - 1) * P::SPRINT_COST, id); continue; } // stack10 lnt: vetoed
                Cand c; c.dirs = dirs; c.tiles = tiles; c.legal = true; c.trade = true; c.blind = false;
                c.base = tv - ((int)dirs.size() - 1) * P::SPRINT_COST; c.removed = 0; c.pearls = 0;
                cands.push_back(c);
            }
        }
    }

    // exp/portals: the module's penalties on every step of every legal non-trade candidate (ptStepPenalty, ptmod.cpp)
    if constexpr (PT) {
        for (Cand& c : cands) {
            if (!c.legal || c.trade) continue;
            if (c.blind) { c.base -= ptStepPenalty(w_.headT, c.dirs[0], -2, true); continue; }
            int from = w_.headT;
            for (size_t k = 0; k < c.tiles.size(); k++) { c.base -= ptStepPenalty(from, c.dirs[k], c.tiles[k], false); from = c.tiles[k]; }
        }
    }

    // ---- first-step safety (flood fill) once per legal candidate
    std::vector<double> safety(cands.size(), 0.0);
    for (size_t i = 0; i < cands.size(); i++) {
        Cand& c = cands[i];
        if (!c.legal || c.trade || c.blind) continue;
        path.assign(1, w_.headT); for (int t : c.tiles) path.push_back(t);
        safety[i] = areaSafety(c.tiles.back(), c.removed, path);
    }
    // cand-portal1: we cannot flood-fill an unseen exit; assume it is as roomy as our best ordinary step, so the blind
    // step competes on the frontier value minus the blind risk
    {
        bool anySafe = false; double safetyRef = 0.0;
        for (size_t i = 0; i < cands.size(); i++) {
            const Cand& c = cands[i];
            if (!c.legal || c.trade || c.blind) continue;
            if (!anySafe || safety[i] > safetyRef) safetyRef = safety[i];
            anySafe = true;
        }
        for (size_t i = 0; i < cands.size(); i++) if (cands[i].legal && cands[i].blind) safety[i] = safetyRef;
    }
    long long tp3 = nowPoints();

    // ---- iterative deepening search from each legal non-trade candidate
    std::vector<double> value(cands.size(), DEATH * 2);
    for (size_t i = 0; i < cands.size(); i++) if (cands[i].legal) value[i] = cands[i].base + safety[i];
    int depthDone = 0;
    for (int depth = P::DFS_DEPTH_MIN; depth <= P::DFS_DEPTH_MAX; depth++) {
        if (nowPoints() > soft || nodes_ > P::DFS_NODE_BUDGET / 3) break;
        std::vector<double> v2(cands.size(), DEATH * 2);
        bool aborted = false;
        for (size_t i = 0; i < cands.size(); i++) {
            Cand& c = cands[i];
            if (!c.legal) continue;
            if (c.trade || c.blind) { v2[i] = c.base + safety[i]; continue; } // safety: 0 for trades, the reference for blind
            path.assign(1, w_.headT); for (int t : c.tiles) path.push_back(t);
            double cont;
            if constexpr (PT) cont = dfsPt(c.tiles.back(), c.dirs.back(), 0, depth, c.removed, w_.myLen + c.pearls - ((int)c.dirs.size() - 1), path, hard);   // exp/portals
            else cont = dfs<MODE>(c.tiles.back(), c.dirs.back(), 0, depth, c.removed, w_.myLen + c.pearls - ((int)c.dirs.size() - 1), path, hard);
            v2[i] = c.base + safety[i] + cont;
            if (nodes_ > P::DFS_NODE_BUDGET || nowPoints() > hard) { aborted = true; break; }
        }
        if (aborted) break;
        value = v2; depthDone = depth;
    }
    long long tp4 = nowPoints();

    // cand-portal1: at an unexplored portal with a clean probe, staying keeps only the option to enter later (the ordinary
    // values already hold the frontier's pull), so entering is worth the best ordinary value plus what the frontier
    // promises beyond its risk, minus a margin
    {
        double bestOrd = -1e18;
        for (size_t i = 0; i < cands.size(); i++) if (cands[i].legal && !cands[i].blind && value[i] > bestOrd) bestOrd = value[i];
        for (size_t i = 0; i < cands.size(); i++)
            if (cands[i].legal && cands[i].voluntary && bestOrd > -1e17)
                value[i] = std::max(value[i], bestOrd + cands[i].base - P::FRONTIER_COMMIT_MARGIN);
    }

    // deterministic per-dragon jitter so mirrored dragons do not make identical choices on ties
    for (size_t i = 0; i < cands.size(); i++) if (cands[i].legal) {
        uint32_t h = mix32((uint32_t)(w_.myId * 7919 + w_.round * 131 + (int)i * 17 + 3));
        value[i] += P::JITTER * ((h & 1023) / 1023.0);
    }

    // ---- choose
    int best = -1, bestSingle = -1, bestRaw = -1;
    if constexpr (SW) {   // v1.1 B: the king class chooses on value - kingFloorCost(end tile); bestRaw (v1's choice) keeps the doom test v1's
        std::vector<double> cv(value);
        if (kfOn_) for (size_t i = 0; i < cands.size(); i++) if (cands[i].legal && !cands[i].blind && !cands[i].tiles.empty()) cv[i] -= kingFloorCost(cands[i].tiles.back());
        for (size_t i = 0; i < cands.size(); i++) {
            if (!cands[i].legal) continue;
            if (best < 0 || cv[i] > cv[best]) best = (int)i;
            if (bestRaw < 0 || value[i] > value[bestRaw]) bestRaw = (int)i;
            if (cands[i].dirs.size() == 1 && !cands[i].trade && !cands[i].blind && (bestSingle < 0 || cv[i] > cv[bestSingle])) bestSingle = (int)i;
        }
    } else {
    for (size_t i = 0; i < cands.size(); i++) {
        if (!cands[i].legal) continue;
        if (best < 0 || value[i] > value[best]) best = (int)i;
        if (cands[i].dirs.size() == 1 && !cands[i].trade && !cands[i].blind && (bestSingle < 0 || value[i] > value[bestSingle])) bestSingle = (int)i;
    }
    bestRaw = best;
    }
    if (bestSingle >= 0) act.safeDir = cands[bestSingle].dirs[0];

    // ---- escape split: when every move dies within the horizon, hand the body to a child born at the tail
    // Only when death is imminent or an enemy head is near: a far-off "doom" is often a body we assume never
    // moves (tail out of view).
    // Waiting keeps the whole length; if the block is real, next turn has no open step and we split then.
    bool doomed = best < 0;
    bool deadEnd = false; // a legal step exists but none of them has a further step (the board, not an enemy)
    if (!doomed && value[bestRaw] < P::DOOM_VALUE) {   // v1.1: bestRaw == best but for the swarm king floor's choice
        bool open = false;
        for (size_t i = 0; i < cands.size() && !open; i++) {
            const Cand& c = cands[i];
            if (!c.legal || c.trade || c.blind || c.tiles.empty()) continue;
            path.assign(1, w_.headT); for (int t : c.tiles) path.push_back(t);
            int last = c.tiles.back(), ld = c.dirs.back(), stepBase = (int)path.size() - 1;
            for (int d = 0; d < 4 && !open; d++) {
                if (d == opp(ld)) continue;
                int u = w_.across(last, d);
                if (u >= 0 && tileEnterable(u, stepBase + 1, c.removed, path)) open = true;
            }
        }
        // an enemy head close by makes the doom real (a trade we cannot avoid): keep the early insurance split
        doomed = !open || enemyDist_[w_.headT] <= 3;
        deadEnd = !open;
    }
    if (doomed && w_.myLen >= 4 && w_.unitCount < w_.unitLimit && (int)w_.body.size() == w_.myLen) {
        int tail = w_.body[w_.myLen - 1], neck = w_.body[w_.myLen - 2];
        bool childCanMove = true; // unknown tail surroundings: any chance beats certain death
        if (tail >= 0 && neck >= 0 && w_.tiles[tail].seen >= 0) {
            int exits = 0;
            for (int d = 0; d < 4; d++) { int u = w_.across(tail, d); if (u < 0 || u == neck) continue; if (w_.occNow[u] == 0 || u == w_.body[w_.myLen - 3 < 0 ? 0 : w_.myLen - 3]) exits++; }
            childCanMove = exits > 0;
        }
        // pocket eat (pd10): the child is born at our tail whatever its size, so a split now or after one more pearl
        // puts it in the same place; eating first only makes it one longer. Do that when the child would otherwise be
        // shorter than we were born (+1 if we were born on a tile open to the sides): a loop between two dead-end
        // pockets keeps its length, and its births move from the mouth of the corridor into the walled part.
        // Only at a board dead end with no enemy head near, and only onto a pearl, so next turn the split is forced.
        // walk our body from the head while each tile is a walled lane (kelp on both sides across the body): the pocket.
        // Count its tiles and those that can spawn (countdown seen, not "never").
        int lane = 0, laneYield = 0;
        if (deadEnd) {
            for (int i = 0; i + 1 < (int)w_.body.size(); i++) {
                int t = w_.body[i], nx = w_.body[i + 1];
                if (t < 0 || nx < 0) break;
                int along = -1; for (int d = 0; d < 4; d++) if (w_.geo.stepIdx(t, d) == nx) along = d;
                if (along < 0) break;
                const Tile& x = w_.tiles[t];
                if (x.edge[leftOf(along)] != EDGE_KELP || x.edge[rightOf(along)] != EDGE_KELP) break;
                lane++;
                if (x.seen >= 0 && x.spawnRound != NEVER) laneYield++;
            }
        }
        // (pd10e) only in a pocket: our head and the tiles behind it form a walled lane at least POCKET_MIN_LANE long
        bool inPocket = lane >= P::POCKET_MIN_LANE;
        // (pd10d) a map-given dragon also uses the rule when its pocket is poor (fewer than POCKET_LANE_YIELD spawning tiles)
        bool mapLowYield = P::POCKET_MAP_LOW_YIELD && w_.birthRound == 0 && laneYield < P::POCKET_LANE_YIELD;
        bool pocketOk = P::POCKET_EAT && childCanMove && deadEnd && inPocket && best >= 0 && enemyDist_[w_.headT] > P::POCKET_ENEMY_DIST &&
                        (w_.birthRound > 0 || P::POCKET_EAT_MAP_DRAGONS || mapLowYield) && w_.myLen + 1 - 2 >= 2;
        if (pocketOk) {
            int cap = w_.birthLen + (w_.bornExposed ? P::POCKET_EXPOSED_BONUS : 0);
            int eatStep = -1;
            if (w_.myLen + 1 - 2 <= cap) {
                for (size_t i = 0; i < cands.size(); i++) {
                    const Cand& c = cands[i];
                    if (!c.legal || c.trade || c.blind || c.dirs.size() != 1 || c.tiles.empty()) continue;
                    int u = c.tiles[0];
                    if (SC.pnow[u] < 0.5 || threatAt(u) > 0.0) continue;
                    if (eatStep < 0 || value[i] > value[eatStep]) eatStep = (int)i;
                }
            }
            if (eatStep >= 0) {
                const Cand& c = cands[eatStep];
                act.kind = Action::MOVE; act.dirs = std::string(1, DIRCH[c.dirs[0]]); act.path = c.tiles; act.score = value[eatStep];
                setSonar(act);
                char buf[64]; snprintf(buf, sizeof buf, "pocket-eat L%d b%d%s", w_.myLen, w_.birthLen, w_.bornExposed ? "x" : "");
                act.indicator = buf;
                return act;
            }
        }
        if (childCanMove) {
            act.kind = Action::SPLIT; act.splitSize = w_.myLen - 2;
            escSplitRound_ = w_.round; // stack1: the stub left behind is not a conversion feeder
            setSonar(act);
            char buf[64]; snprintf(buf, sizeof buf, "escape-split%d L%d", act.splitSize, w_.myLen);
            act.indicator = buf;
            return act;
        }
    }
    if (best < 0) {
        // everything dies. Take an enemy with us if one is adjacent; otherwise die going forward.
        for (int d = 0; d < 4; d++) {
            int u = w_.across(w_.headT, d);
            if (u >= 0) { int hid = w_.headOf[u]; if (hid >= 0 && w_.dragons[hid].team != w_.myTeam) { act.dirs = std::string(1, DIRCH[d]); act.indicator = "last-trade"; act.path = {u}; return act; } }
        }
        // stack5 no-exit spare (cand-swarm3 T0): not into an ally's head, which dies with us (a head to head)
        int dieDir = w_.myDir; bool spare = false;
        if (P::NOEXIT_SPARE_ON) {
            auto allyHeadAt = [&](int d) { int u = w_.across(w_.headT, d); return u >= 0 && w_.headOf[u] >= 0 && w_.headOf[u] != w_.myId; };
            if (allyHeadAt(w_.myDir)) {
                spare = true; dieDir = -1;
                for (int d = 0; d < 4 && dieDir < 0; d++) if (d != opp(w_.myDir) && w_.across(w_.headT, d) == -2) dieDir = d;
                const int side[2] = {leftOf(w_.myDir), rightOf(w_.myDir)};
                for (int i = 0; i < 2 && dieDir < 0; i++) if (!allyHeadAt(side[i])) dieDir = side[i];
                if (dieDir < 0) dieDir = opp(w_.myDir); // into our own neck: harms nobody
            }
        }
        act.dirs = std::string(1, DIRCH[dieDir]); act.indicator = spare ? "no-exit s" : "no-exit";
        return act;
    }

    // ---- split instead of moving when the policy says so and this move is not urgent
    // (stack2 S1: or a fragment split when the policy says no, tagged " frag")
    // (stack5 csplit: or a coverage split when neither says so, tagged "csplit<n> u<units> L<len> t<target>")
    // (cand-mapid: or an early split on a recognised Schooltime b, tagged " bsp"; it is tried before csplit)
    // (stack7: or, when none of those says so, the king length cap " kcap", then the unit floor " floor")
    // (stack9: or, when none of those says so, the late re-split "lsplit<n> u<units> L<len> t<target>"; frag's label ends " fc" when
    //  the split needed the wider cap)
    // (unsw-swarm v1: the swarm engine has one split policy instead of this chain: the explosion " sx" (A, r1-99), then the re-split " sr" (B,
    //  r100-429, with its service-deficit rule and its survival clause); the escape split below the search stays in both engines)
    int splitSize = 0; bool frag = false, csplit = false, bsplit = false, kcap = false, floorSp = false, lsplit = false, sx = false, sr = false, swGate = false;
    sxWhy_ = 0; srWhy_ = 0;
    if (!cands[best].trade && !cands[best].blind &&
        (SW ? ((sx = wantExplode(splitSize)) || (sr = wantResplit(splitSize)))
            : (wantSplit(splitSize) || (frag = wantFrag(splitSize, !W4)) || (bsplit = wantBSplit(splitSize)) || (csplit = !W4 && wantCsplit(splitSize)) ||
               (kcap = !W4 && wantKcap(splitSize)) || (floorSp = !W4 && wantFloor(splitSize)) || (lsplit = !W4 && wantLsplit(splitSize))))) {   // 5b: W4-era economy
        double immediate = cands[best].tiles.empty() ? 0.0 : SC.pnow[cands[best].tiles[0]];
        bool threatened = false; for (int t : cands[best].tiles) if (threatAt(t) > 0.0) threatened = true;
        if (immediate < 0.5 && !threatened && safety[best] > -1.0 && enemyDist_[w_.headT] > 2) {
            act.kind = Action::SPLIT; act.splitSize = splitSize;
            if (frag) lastFragRound_ = w_.round;
            if (csplit) lastCsplitRound_ = w_.round;
            if (lsplit) lastLsplitRound_ = w_.round;                                              // stack9 lsplit
            if (sx) lastSxRound_ = w_.round;                                                      // v1 sx
            if (sr) lastSrRound_ = w_.round;                                                      // v1 sr
            setSonar(act);
            char buf[64]; snprintf(buf, sizeof buf, "split%d u%d L%d%s%s", splitSize, w_.unitCount, w_.myLen, frag ? " frag" : bsplit ? " bsp" : kcap ? " kcap" : floorSp ? " floor" : "",
                                   frag && fragWide_ ? " fc" : "");                               // stack9 fc
            if (csplit) snprintf(buf, sizeof buf, "csplit%d u%d L%d t%d%s%s%s", splitSize, w_.unitCount, w_.myLen, csplitTarget_, csplitTab_ ? " tab" : "",
                                 w_.enemyHeadsNow.empty() ? "" : " v", w_.iAmLongest() ? " k" : ""); // stack5 csplit
            if (lsplit) snprintf(buf, sizeof buf, "lsplit%d u%d L%d t%d", splitSize, w_.unitCount, w_.myLen, lsplitTarget_); // stack9 lsplit
            if (sx) snprintf(buf, sizeof buf, "split%d u%d L%d sx t%d%s%s", splitSize, w_.unitCount, w_.myLen, sxTarget_,
                             w_.enemyHeadsNow.empty() ? "" : " v", w_.iAmLongest() ? " k" : "");                   // v1 sx
            if (sr) snprintf(buf, sizeof buf, "split%d u%d L%d sr t%d%s%s", splitSize, w_.unitCount, w_.myLen, srTarget_, sdFree_ > 0 ? " d" : "",
                             w_.unitCount <= P::SR_SURVIVE_UNITS ? " s" : "");                                  // v1 sr (" s": survival clause)
            act.indicator = buf;
            if (P::SPLIT_TAIL_ON && !frag) { snprintf(buf, sizeof buf, " e%d", splitTailDist_); act.indicator += buf; } // stack4 split tail
            return act;
        }
        if (sx || sr) swGate = true;                                                               // v1: " sxx" / " srx"
    }
    // stack4 split tail: " sx" when the tail rule alone stopped a policy split (the other conditions above held)
    bool splitTailStop = false;
    if (splitTailBlocked_ && !cands[best].trade && !cands[best].blind) {
        double immediate = cands[best].tiles.empty() ? 0.0 : SC.pnow[cands[best].tiles[0]];
        bool threatened = false; for (int t : cands[best].tiles) if (threatAt(t) > 0.0) threatened = true;
        splitTailStop = immediate < 0.5 && !threatened && safety[best] > -1.0 && enemyDist_[w_.headT] > 2;
    }

    Cand& c = cands[best];
    if (w_.myLen >= P::ESCAPE_MIN_LEN && !c.trade && !c.tiles.empty() && exactlyExposed(c.tiles.back())) exposedPending_ = true; // cand-avoid2
    act.kind = Action::MOVE; act.dirs.clear();
    for (int d : c.dirs) act.dirs += DIRCH[d];
    act.path = c.tiles; act.score = value[best];
    setSonar(act);
    char buf[160];
    snprintf(buf, sizeof buf, "%s v%.1f d%d L%d%s%s%s", act.dirs.c_str(), value[best], depthDone, w_.myLen, c.trade ? " TRADE" : "", c.blind ? " PORTAL?" : "", late_ ? " late" : "");
    act.indicator = buf;
    if (goalOn_ && !fGoal_) { snprintf(buf, sizeof buf, " %s%d", gatherKing_ ? "K" : "g", goalDist_[w_.headT]); act.indicator += buf; }
    // stack5 F; stack8: the F tag stays on a paused turn (the target is held) and " Fp@x,y" names the claim that paused the pull
    if (!SW && (fGoal_ || fPause_ >= 0)) { snprintf(buf, sizeof buf, " F%d@%d,%d", goalDist_[w_.headT], fTarget_ % w_.geo.W, fTarget_ / w_.geo.W); act.indicator += buf; }
    if (!SW && (fGoal_ || fPause_ >= 0) && P::F2_ON && fTable_) act.indicator += " F2";                                     // stack8 F2
    if (fPause_ >= 0) { snprintf(buf, sizeof buf, " Fp@%d,%d", fPause_ % w_.geo.W, fPause_ / w_.geo.W); act.indicator += buf; } // stack8 F2p
    // stack5 cov: the move ends on our side with no other ally head (seen within 3 rounds) within 6 of its last tile (stack9: covSide)
    if (!W4 && P::COV_ON && w_.myLen <= P::COV_MAX_LEN && !c.trade && !c.tiles.empty() && covSide(c.tiles.back())) {
        bool ally6 = false;
        for (auto& [id, d] : w_.dragons)
            if (id != w_.myId && d.team == w_.myTeam && d.headT >= 0 && w_.round - d.headSeen <= 3 && w_.geo.manhattan(d.headT, c.tiles.back()) <= 6) { ally6 = true; break; }
        if (!ally6) act.indicator += " cov";
    }
    if (c.esc) act.indicator += " esc";                                                            // cand-avoid2
    if (w_.myLen >= P::ESCAPE_MIN_LEN && survivedExposures_ >= P::RAMMER_TRUST) act.indicator += " T"; // cand-avoid2: escapes off
    // stack1 M2: " ram4" when the small-piece rule allows this one-step ram (" ram4o": merge2's rule would have too),
    // then " c1" if an ally head is within 3 of the enemy head (a collector for the pearls), else " c0"
    if (c.trade && c.dirs.size() == 1 && !c.tiles.empty()) {
        int hid = w_.headOf[c.tiles[0]];
        if (hid >= 0 && smallRam(hid)) {
            act.indicator += tradeValueBase(hid) > 0.0 ? " ram4o" : " ram4";
            bool coll = false;
            for (int aid : w_.allyHeadsNow) if (w_.geo.manhattan(w_.dragons[aid].headT, c.tiles[0]) <= 3) coll = true;
            act.indicator += coll ? " c1" : " c0";
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
    }
    // stack2 S2: " grab@x,y" when this move eats a fresh death drop within reach or closes in on one (path distance over
    // known edges, bodies ignored, as headDist_); the pearl named is the one eaten, else the nearest one we close in on
    if (!grabTiles_.empty() && !c.trade && !c.tiles.empty()) {
        int tgt = -1;
        for (int t : c.tiles) for (int g : grabTiles_) if (t == g && tgt < 0) tgt = g;
        if (tgt < 0) {
            std::fill(distBuf_.begin(), distBuf_.end(), -1);
            queue_.clear(); queue_.push_back(c.tiles.back()); distBuf_[c.tiles.back()] = 0;
            for (size_t qi = 0; qi < queue_.size(); qi++) {
                int t = queue_[qi];
                if (distBuf_[t] >= P::GRAB_REACH) continue;
                for (int dir = 0; dir < 4; dir++) { int u = w_.across(t, dir); if (u >= 0 && distBuf_[u] < 0) { distBuf_[u] = distBuf_[t] + 1; queue_.push_back(u); } }
            }
            int bd = 1 << 20;
            for (int g : grabTiles_) if (distBuf_[g] >= 0 && distBuf_[g] < headDist_[g] && distBuf_[g] < bd) { bd = distBuf_[g]; tgt = g; }
        }
        if (tgt >= 0) { snprintf(buf, sizeof buf, " grab@%d,%d", tgt % w_.geo.W, tgt / w_.geo.W); act.indicator += buf; }
    }
    // stack8 cl / ce: " cl@x,y" / " ce@x,y" when this move eats a claimed pearl or closes in on one (path distance over known
    // edges, bodies ignored, as headDist_); the pearl named is the one eaten, else the nearest one we close in on (as grab)
    auto claimTag = [&](const std::vector<int>& tiles, const char* word) {
        if (tiles.empty() || c.trade || c.tiles.empty()) return;
        int tgt = -1;
        for (int t : c.tiles) for (int g : tiles) if (t == g && tgt < 0) tgt = g;
        if (tgt < 0) {
            std::fill(distBuf_.begin(), distBuf_.end(), -1);
            queue_.clear(); queue_.push_back(c.tiles.back()); distBuf_[c.tiles.back()] = 0;
            for (size_t qi = 0; qi < queue_.size(); qi++) {
                int t = queue_[qi];
                if (distBuf_[t] >= P::CLAIM_REACH) continue;
                for (int dir = 0; dir < 4; dir++) { int u = w_.across(t, dir); if (u >= 0 && distBuf_[u] < 0) { distBuf_[u] = distBuf_[t] + 1; queue_.push_back(u); } }
            }
            int bd = 1 << 20;
            for (int g : tiles) if (distBuf_[g] >= 0 && distBuf_[g] < headDist_[g] && distBuf_[g] < bd) { bd = distBuf_[g]; tgt = g; }
        }
        if (tgt >= 0) { snprintf(buf, sizeof buf, " %s@%d,%d", word, tgt % w_.geo.W, tgt / w_.geo.W); act.indicator += buf; }
    };
    if (!W4 && P::CLAIM_ALLY_ON) claimTag(clTiles_, "cl");
    if (!W4 && P::CLAIM_ENEMY_ON) claimTag(ceTiles_, "ce");
    if (kingSafe_) act.indicator += " ks"; // stack1 M3
    if (kingSafe2_) act.indicator += " ks2"; // stack3 ks2
    // stack4 tg: " tg" when some legal candidate's final tile (our head after the move, where a strike lands) carries threat
    // only the new field sees (stack3's gives less) and the chosen move's does not; " tgx" when the chosen move's does
    if (P::TG_ON) {
        auto gap = [&](const Cand& k) { if (k.tiles.empty()) return false; int t = k.tiles.back(); return threatAt(t) > threatAtOld(t) + 1e-9; };
        bool inPlay = false;
        for (const Cand& k : cands) if (k.legal && !k.trade && !k.blind && gap(k)) { inPlay = true; break; }
        if (inPlay) act.indicator += !c.trade && !c.blind && gap(c) ? " tgx" : " tg";
    }
    // stack4 px: " px" when some legal candidate's crossing pays a px penalty and the chosen move crosses none; " pxx" when it does
    if (P::PX_ON) {
        bool inPlay = false;
        for (const Cand& k : cands) if (k.legal && k.px) { inPlay = true; break; }
        if (inPlay) act.indicator += c.px ? " pxx" : " px";
    }
    // stack8 px2: " px2" when some legal candidate's crossing paid the px2 penalty and the chosen move crosses none; " px2x" when it does
    if (P::PX2_ON) {
        bool inPlay = false;
        for (const Cand& k : cands) if (k.legal && k.px2) { inPlay = true; break; }
        if (inPlay) act.indicator += c.px2 ? " px2x" : " px2";
    }
    if (gxOff_) act.indicator += " gx";           // stack4 gx: the gathering goal is off for lack of rounds
    if (splitTailStop) act.indicator += " sx";    // stack4 split tail
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
    if constexpr (SW) {   // unsw-swarm v1 swarm tags
        if (swGate) act.indicator += w_.round < P::SX_END ? " sxx" : " srx";
        else if (sxWhy_ == 3) act.indicator += " sxc";
        else if (srWhy_ == 3) act.indicator += " src";
        else if (srWhy_ == 4) act.indicator += " srn";
        if (fGoal_ && sdAnchor_ >= 0) { snprintf(buf, sizeof buf, " sd%d@%d,%d%s", goalDist_[w_.headT], sdAnchor_ % w_.geo.W, sdAnchor_ / w_.geo.W, sdKind_ == 1 ? "o" : "u"); act.indicator += buf; }
        if (fGoal_ && sdAnchor_ >= 0 && sdBin_ >= 0) { snprintf(buf, sizeof buf, " f%d%s", sdBin_, sdContest_ ? "c" : ""); act.indicator += buf; }   // v1.1 A: the target's bin
        if (sdRedir_ >= 0) { snprintf(buf, sizeof buf, " fr%d%c", sdRedir_, sdRedirWhy_); act.indicator += buf; }                             // v1.1 A guard (diagnostic)
        if (kfOn_ && !c.tiles.empty() && !c.blind) {   // v1.1 B: " kf<d>" the chosen end tile's distance (below KF_TARGET), " kfx" when it breaks the floor
            const int d = kfDist_[c.tiles.back()];
            if (d < P::KF_TARGET) { snprintf(buf, sizeof buf, " kf%d%s", d, d <= P::KF_FLOOR_DIST ? "x" : ""); act.indicator += buf; }
        }
        if (sfHeld_ >= 0) { snprintf(buf, sizeof buf, " sq#%d", sfHeld_); act.indicator += buf; }
        if (!scTiles_.empty() && !c.trade && !c.blind) {
            bool inPlay = false;
            for (const Cand& k : cands) if (k.legal && !k.trade && !k.blind && !k.tiles.empty() && scMark_[k.tiles[0]]) { inPlay = true; break; }
            if (inPlay) act.indicator += !c.tiles.empty() && scMark_[c.tiles[0]] ? " scx" : " sc";
        }
        if (kingClass()) act.indicator += " sk";
    }
    if (P::KING_BEACON_ON && beaconTag_) act.indicator += beaconTag_ == 1 ? " kb" : " kbr";   // v1.1 C
    if constexpr (PT) {   // exp/portals: " pt" on every module turn; " ptd" / " ptb" / " ptq" when a rule priced a candidate (king dead end, king blind crossing, crossing near the king)
        act.indicator += " pt";
        if (ptFire_ & 1) act.indicator += " ptd";
        if (ptFire_ & 2) act.indicator += " ptb";
        if (ptFire_ & 4) act.indicator += " ptq";
    }
    if (P::BELIEF_TAG && w_.round % P::BELIEF_TAG_EVERY == 0) act.indicator += beliefTag();   // v1 belief tag
    if (P::PROFILE) {
        long long tp5 = nowPoints();
        snprintf(buf, sizeof buf, " | enemy %.2fM field %.2fM cand %.2fM dfs %.2fM rest %.2fM total %.2fM nodes %lld",
                 (tp1 - tp0) / 1e6, (tp2 - tp1) / 1e6, (tp3 - tp2) / 1e6, (tp4 - tp3) / 1e6, (tp5 - tp4) / 1e6, (tp5 - start) / 1e6, nodes_);
        act.indicator += buf;
    }
    return act;
}

// ================================================================================================
// unsw-swarm v1: the swarm engine's own rules (params.hpp v1 section; engcfg.hpp; ENGINE.md §3; versions/v1/VERSION.md)

// our side's territory char in terrdb ('1' / '2'): a start dragon's own start tile; a child votes with its birth tile and the heads of the
// allies it has fresh news of (the server swaps the file's team letters in about half of the games, so the letter does not tell the side)
void Planner::updateSide() {
    const char c = w_.mapTerrChar(homeT_);
    if (w_.birthRound == 0 && (c == '1' || c == '2')) { sideChar_ = c; return; }
    int v1 = c == '1' ? 1 : 0, v2 = c == '2' ? 1 : 0;
    for (auto& [id, d] : w_.dragons) {
        if (id == w_.myId || d.team != w_.myTeam || d.headT < 0 || !w_.allyFresh(d, P::BELIEF_FRESH)) continue;
        const char e = w_.mapTerrChar(d.headT);
        if (e == '1') v1++; else if (e == '2') v2++;
    }
    sideChar_ = v1 > v2 ? '1' : v2 > v1 ? '2' : (c == '1' || c == '2' ? c : sideChar_);
}

// 1 our side, 2 theirs, 0 neutral, -1 unknown
int Planner::sideOf(int t) const {
    const char x = w_.mapTerrChar(t);
    if (x == '?' || sideChar_ == '?') return -1;
    if (x == '0') return 0;
    return x == sideChar_ ? 1 : 2;
}

// sd claims: allies' hotspot fields (the latest message per id) become claims kept SD_TTL rounds from their issue; a newer message with no
// claim releases that ally's claim. The fields are cleared in World::allies so that computeAttract does not pull us to them.
void Planner::takeClaims() {
    size_t k = 0;
    for (auto& c : claimsHeard_) if (w_.round - c.round <= P::SD_TTL) claimsHeard_[k++] = c;
    claimsHeard_.resize(k);
    for (auto& a : w_.allies) {
        if (w_.round - a.round <= P::SD_TTL) {
            bool have = false;
            for (size_t i = 0; i < claimsHeard_.size(); i++) {
                ClaimHeard& c = claimsHeard_[i];
                if (c.id != a.id) continue;
                have = true;
                if (a.round > c.round && a.hotT < 0) { claimsHeard_.erase(claimsHeard_.begin() + (long)i); break; }   // released
                if (a.hotT >= 0 && a.round >= c.round) c = {a.hotT, a.t, a.id, a.round};
                break;
            }
            if (!have && a.hotT >= 0) claimsHeard_.push_back({a.hotT, a.t, a.id, a.round});
        }
        a.hotT = -1;
    }
}

// sd (v1 final, coordinator 03:30; research "the nearer side eats the pearl"; transfer 1, 5, 7): the dispersal target over the whole map.
//   Candidates: spawn groups (every spawn tile of the recognised map's table weighs by its flow, 1 / mean gap; where the table maps left
//   disagree, an observed fountain) whose anchor lies in the 2-core (World::inCore2; no dead-end pocket), within the head BFS reach
//   (headDist_), group value >= SD_MIN_FLOW. (Fountain groups only, 03:40-04:05: sd idle on Schooltime a.) Ours = our head is the
//   nearest known head by path distance: ally heads seen or heard within 3 rounds (SC.allyFar; equal: no lower-id ally at that Manhattan
//   distance) and enemy heads seen within 3 rounds (SC.enemyFar; equal = not ours), and no ally with news within BELIEF_FRESH rounds nearer
//   by Manhattan (equal: the lower id), and no heard claim that arrives first. Value = group yield (pearls a round, 2-core fountain tiles
//   within FG_GROUP_DIST) / (1 + our heads already there: fresh ally heads within FG_GUARD_DIST, claims on it); ties to the nearer. No
//   fallback: a dragon that owns nothing follows the attraction field. The held target stays SD_LEASE rounds unless another head is SD_HYST
//   nearer. The pull runs before the conversion clock; sdFree_ (another owned group away from ours: the re-split's deficit) until SR_END.
// v1.1 A (FRONTIER_ON and a FRONT_POLICY row, versions/v1.1/VERSION.md): enemy heads no longer cede every tie. A group is takeable when our ETA
//   (headDist_) <= the nearest enemy head's (SC.enemyFar) + SD_ENEMY_MARGIN (the held target: + SD_HYST_ENEMY more) and the trade veto would not
//   apply there (vetoAt). Among the groups we may take, the one in the frontier bin (frontdb.hpp, from our side) with the largest positive
//   deficit wins: deficit = the elite share of the bin x (allies counted + 1) - allies counted in the bin, where the allies counted are those with
//   news within BELIEF_FRESH rounds, each in the bin of its live claim (a lease) or else of its last known head, and we leave ourselves out (the
//   marginal choice). Inside that bin, and when no bin we may take is short, v1's value decides. The allies' part of ownership is v1's.
void Planner::computeDisperseGoal() {
    fGoal_ = false; fTable_ = false; fPause_ = -1; fTarget_ = -1; sdFree_ = 0; sdBin_ = -1; sdContest_ = false; sdRedir_ = -1; sdRedirWhy_ = 0;
    if (goalOn_ || w_.round >= std::max(cfg_->convStart, P::SR_END) || w_.unitCount < P::FG_MIN_UNITS || homeT_ < 0 || w_.mapFam < 0 ||
        (w_.iAmLongest() && w_.myLen >= P::KING_MIN_LEN)) { sdAnchor_ = -1; sdKind_ = 0; return; }
    const int n = w_.geo.tiles(), W = w_.geo.W, myId11 = w_.myId & 2047;
    // fountain flow per tile (table, else observed), 2-core only; recomputed when the recognition state changes (observed part each turn)
    const int key = w_.mapStateCode();
    if (key != flowKey_) {
        flowKey_ = key;
        flow_.assign(n, 0.0);
        for (int t = 0; t < n; t++) {
            if (!w_.inCore2(t)) continue;
            // v1 final (04:05): every spawn tile of the table weighs by its flow (1 / mean gap), not fountains only. The fountain-only
            // candidates left sd nearly idle on Schooltime a (416 sd turns in 2 games vs 17,592 before; intake 141 vs 623), where the food
            // comes from slow spawn tiles
            const double g = w_.mapSpawnGap(t);
            if (g > 0.0) flow_[t] = 1.0 / std::max(1.0, g);
            else if (g < 0.0) flow_[t] = -1.0;   // the table maps left disagree: the observed rule decides each turn
        }
    }
    auto fl = [&](int t) { const double v = flow_[t]; if (v >= 0.0) return v; return w_.isFountain(t) ? 1.0 / std::max(1.0, (double)w_.tiles[t].maxSample) : 0.0; };
    std::vector<std::pair<int, int>> fresh;   // (tile, id): ally heads with news within BELIEF_FRESH rounds
    std::vector<int> freshAge;
    for (auto& [id, d] : w_.dragons)
        if (id != w_.myId && d.team == w_.myTeam && d.headT >= 0 && w_.round - d.headSeen <= P::BELIEF_FRESH) { fresh.push_back({d.headT, id}); freshAge.push_back(w_.round - d.headSeen); }
    // contest ties (coordinator 04:00, SD_CONTEST_TIES): a group as near to our head as to the nearest enemy head is ours unless the trade veto
    // would apply there: local balance around the group (heads with news within 3 rounds, us counted in) d8 <= LNT_D8_VETO, or on Slithery
    // Fight (no d8 veto) stack10's d3 <= LNT_VETO_D3 within Chebyshev 3
    std::vector<std::pair<int, bool>> heads3;   // (tile, ally): other heads with news within 3 rounds (the veto's local balance)
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
    // v1.1 A: the frontier deficits (see above); front = a FRONT_POLICY row and our side known
    const bool front = cfg_->front != nullptr && (sideChar_ == '1' || sideChar_ == '2');
    double deficit[5] = {0.0, 0.0, 0.0, 0.0, 0.0};
    if (front) {
        int have[5] = {0, 0, 0, 0, 0}, known = 0;
        for (auto& [t0, id] : fresh) {
            int t = t0;
            for (auto& c : claimsHeard_) if (c.id == (id & 2047)) { t = c.anchor; break; }   // a live claim: that ally is on its way there
            const int b = w_.mapFrontBin(t, sideChar_);
            if (b >= 0) { have[b]++; known++; }
        }
        for (int b = 0; b < 5; b++) deficit[b] = cfg_->frontShare(w_.round, b) * 0.01 * (known + 1) - have[b];
    }
    auto ours = [&](int t, int hyst) {        // our head is the nearest known head to t (hyst: the held target yields only to a clear lead)
        const int mine = headDist_[t];
        if (front) {                          // v1.1 A: contest an enemy head at most SD_ENEMY_MARGIN nearer (the veto: last, below)
            if (SC.enemyFar[t] + P::SD_ENEMY_MARGIN + (hyst > 0 ? P::SD_HYST_ENEMY : 0) < mine) return false;
        }
        else if (hyst > 0 || !P::SD_CONTEST_TIES) { if (SC.enemyFar[t] + hyst <= mine) return false; }
        else if (SC.enemyFar[t] < mine || (SC.enemyFar[t] == mine && vetoAt(t))) return false;
        if (SC.allyFar[t] + hyst < mine) return false;
        const int mm = w_.geo.manhattan(w_.headT, t);
        for (size_t i = 0; i < fresh.size(); i++) {   // older news (4..BELIEF_FRESH rounds): not in SC.allyFar, Manhattan for both sides
            if (freshAge[i] <= 3) continue;
            const int da = w_.geo.manhattan(fresh[i].first, t);
            if (da + hyst < mm || (hyst == 0 && da == mm && fresh[i].second < w_.myId)) return false;
        }
        if (hyst == 0 && SC.allyFar[t] == mine)       // a path tie: the lower id among the recent heads at that distance
            for (size_t i = 0; i < fresh.size(); i++) if (freshAge[i] <= 3 && fresh[i].second < w_.myId && w_.geo.manhattan(fresh[i].first, t) <= mm) return false;
        for (auto& c : claimsHeard_) {
            if (c.id == myId11 || w_.geo.manhattan(c.anchor, t) > P::FG_GROUP_DIST) continue;
            const int eta = std::max(0, w_.geo.manhattan(c.from, c.anchor) - (w_.round - c.round));
            if (eta + hyst < mm || (hyst == 0 && eta == mm && c.id < myId11)) return false;
        }
        return !(front && vetoAt(t));          // v1.1 A: not where the trade veto would apply
    };
    auto groupValue = [&](int t) {
        const int x = t % W, y = t / W; double yield = 0.0;
        for (int dy = -P::FG_GROUP_DIST; dy <= P::FG_GROUP_DIST; dy++) for (int dx = -P::FG_GROUP_DIST; dx <= P::FG_GROUP_DIST; dx++)
            if (Geo::abs(dx) + Geo::abs(dy) <= P::FG_GROUP_DIST) yield += fl(w_.geo.idx(w_.geo.wrapX(x + dx), w_.geo.wrapY(y + dy)));
        int assigned = 0;
        for (auto& [a, id] : fresh) if (w_.geo.manhattan(a, t) <= P::FG_GUARD_DIST) assigned++;
        for (auto& c : claimsHeard_) if (c.id != myId11 && w_.geo.manhattan(c.anchor, t) <= P::FG_GROUP_DIST) assigned++;
        return yield / (1.0 + assigned);
    };
    int target = -1;
    // v1.1b commitment: a frontier target is held until we arrive (within FG_HOLD of it) or for SD_COMMIT_MAX rounds, while it stays ours (the
    // local check: v1.1's targets were held 3.4 turns and middle-bin targets, 7.3 steps away on average, reached 42%)
    const bool commit = front && sdAnchor_ >= 0 && headDist_[sdAnchor_] > P::FG_HOLD && w_.round - sdTaken_ < P::SD_COMMIT_MAX;
    if (sdAnchor_ >= 0 && fl(sdAnchor_) > 0.0 && headDist_[sdAnchor_] >= 0 && (w_.round - sdSince_ < P::SD_LEASE || commit) && ours(sdAnchor_, P::SD_HYST)) target = sdAnchor_;
    int best = -1; double bestV = 0.0, bestK = 0.0; int bestD = 1 << 20;
    std::vector<int> owned;
    for (int t = 0; t < n; t++) {
        const int hd = headDist_[t];
        if (hd < 0 || fl(t) <= 0.0 || !ours(t, 0)) continue;
        const double v = groupValue(t);
        if (v < P::SD_MIN_FLOW) continue;          // groups poorer than one pearl in 250 rounds (after sharing) are not targets
        owned.push_back(t);
        double k = 0.0;                            // v1.1 A: the bin first (its positive deficit), then v1's value, then the nearer
        if (front) { const int b = w_.mapFrontBin(t, sideChar_); if (b >= 0) k = std::max(0.0, deficit[b]); }
        if (k > bestK + 1e-9 || (k > bestK - 1e-9 && (v > bestV + 1e-9 || (v > bestV - 1e-9 && hd < bestD)))) { bestK = k; bestV = v; best = t; bestD = hd; }
    }
    // v1.1 guard (lead 06:00; research/observations/spatial-occupancy.md: the elite own-deep share on Slithery is partly pocket harvesting): the
    // bin is chosen among the bins that hold a group we may take (2-core, value >= SD_MIN_FLOW, the contest rule), so a bin whose only food is
    // in pockets never pulls a head; it goes to the next deficit. Diagnostic only: when the top-deficit bin held no such group for us, " fr<b>"
    // + why: o = it has 2-core food in reach (owned by an ally, contested, vetoed or too poor), p = only pocket food in reach, n = no food in reach
    if (front) {
        int top = -1; double topD = 1e-9;
        for (int b = 0; b < 5; b++) if (deficit[b] > topD) { topD = deficit[b]; top = b; }
        if (top >= 0 && (best < 0 || w_.mapFrontBin(best, sideChar_) != top)) {
            bool core = false, pocket = false;
            for (int t = 0; t < n && !core; t++) {
                if (headDist_[t] < 0 || w_.mapFrontBin(t, sideChar_) != top) continue;
                const double g = w_.mapSpawnGap(t);
                if (g > 0.0 || (g < 0.0 && w_.isFountain(t))) { if (w_.inCore2(t)) core = true; else pocket = true; }
            }
            sdRedir_ = top; sdRedirWhy_ = core ? 'o' : pocket ? 'p' : 'n';
        }
    }
    if (target < 0) target = best;
    if (target != sdAnchor_) sdTaken_ = w_.round;                                   // v1.1b
    if (target != sdAnchor_ || w_.round - sdSince_ >= P::SD_LEASE) sdSince_ = w_.round;
    sdAnchor_ = target; sdKind_ = target >= 0 ? 1 : 0;
    if (front && target >= 0) { sdBin_ = w_.mapFrontBin(target, sideChar_); sdContest_ = SC.enemyFar[target] <= headDist_[target]; }
    for (int t : owned) if (target < 0 || w_.geo.manhattan(t, target) > 2 * P::FG_GROUP_DIST) { sdFree_ = 1; break; }
    if (target < 0 || w_.round >= cfg_->convStart) return;
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

// v1.1: the swarm engine's king class (the " sk" tag of v1): the fresh World::iAmLongest at length >= KING_MIN_LEN, or at any length from the
// conversion clock
bool Planner::kingClass() const { return w_.iAmLongest() && (w_.myLen >= P::KING_MIN_LEN || w_.round >= cfg_->convStart); }

// v1.1 B king floor (map atlas: kings die at a median path distance 3 from the enemy head, to rammers of median length 3; elite kings spend
// 0.3-4% of rounds within 3, ours 24-38% within 6): path distance over known edges (bodies ignored, the atlas's and kx's distance) from the enemy
// heads seen within KF_STALE rounds, up to KF_TARGET (99 beyond). On for the king class while some such head is known.
void Planner::computeKingFloor() {
    kfOn_ = false;
    if (!cfg_->kingFloor || !kingClass()) return;
    const int n = w_.geo.tiles();
    kfDist_.assign(n, 99);
    kfQ_.clear();
    for (auto& [id, d] : w_.dragons) {
        if (d.team == w_.myTeam || d.headT < 0 || w_.round - d.headSeen > P::KF_STALE) continue;
        if (kfDist_[d.headT] > 0) { kfDist_[d.headT] = 0; kfQ_.push_back(d.headT); }
    }
    for (size_t qi = 0; qi < kfQ_.size(); qi++) {
        const int t = kfQ_[qi];
        if (kfDist_[t] >= P::KF_TARGET) continue;
        for (int dir = 0; dir < 4; dir++) {
            const int u = w_.across(t, dir);
            if (u < 0 || kfDist_[u] <= kfDist_[t] + 1) continue;
            kfDist_[u] = (int16_t)(kfDist_[t] + 1); kfQ_.push_back(u);
        }
    }
    kfOn_ = !kfQ_.empty();
}

// v1.1 B: the choice cost of a move that ends on t: KF_FLOOR + KF_STEP per step inside the floor (so with every move inside, the farthest wins),
// KF_SOFT per step short of KF_TARGET outside it
double Planner::kingFloorCost(int t) const {
    const int d = kfDist_[t];
    if (d <= P::KF_FLOOR_DIST) return P::KF_FLOOR + P::KF_STEP * (P::KF_FLOOR_DIST - d);
    if (d < P::KF_TARGET) return P::KF_SOFT * (P::KF_TARGET - d);
    return 0.0;
}

// no central gathering: only the relay of the longest ally with fresh news (the king class's reference), its last known head and the round
void Planner::computeGoalSwarm() {
    goalOn_ = false; goalT_ = -1; gatherKing_ = w_.iAmLongest(); goalId_ = -1; gxOff_ = false;
    if (w_.round < cfg_->broadcastRound || gatherKing_) return;
    int bestLen = w_.myLen, bestSeen = -1;
    for (auto& [id, d] : w_.dragons) {
        if (id == w_.myId || d.team != w_.myTeam || d.headT < 0 || !w_.allyFresh(d, P::BELIEF_FRESH)) continue;
        const int la = std::max(d.estLen, d.minLen);
        if (la > bestLen || (la == bestLen && goalId_ >= 0 && d.headSeen > bestSeen)) {
            bestLen = la; bestSeen = d.headSeen; goalId_ = id; goalT_ = d.headT; goalRound_ = d.headSeen; goalLen_ = la;
        }
    }
}

// sc (research transfer 12): our side's (or a neutral) spawn tile within the search's reach whose next attempt comes while our body would
// still cover it after a step onto it (round + 2 .. round + min(length, SC_WIN); round + 1 is the head rule of dfs and the candidates)
void Planner::addSpawnClear() {
    for (int t : scTiles_) scMark_[t] = 0;
    scTiles_.clear();
    const int n = w_.geo.tiles();
    if ((int)scMark_.size() != n) scMark_.assign(n, 0);
    updateSide();
    const int L = std::min(w_.myLen, P::SC_WIN);
    if (L < 2) return;
    const int R = P::DFS_DEPTH_MAX + 2, hx = w_.headT % w_.geo.W, hy = w_.headT / w_.geo.W;
    for (int dy = -R; dy <= R; dy++) for (int dx = -R; dx <= R; dx++) {
        if (Geo::abs(dx) + Geo::abs(dy) > R) continue;
        const int t = w_.geo.idx(w_.geo.wrapX(hx + dx), w_.geo.wrapY(hy + dy));
        if (scMark_[t]) continue;
        const Tile& x = w_.tiles[t];
        if (x.seen < 0 || x.spawnRound <= w_.round + 1 || x.spawnRound > w_.round + L) continue;
        if (sideOf(t) == 2) continue;   // the enemy's spawn: not our loss
        softPenalty_[t] += P::BLOCK_SPAWN_PENALTY;
        scMark_[t] = 1; scTiles_.push_back(t);
    }
}

// sx (ENGINE.md §3 A; pf, legacy/exp/cand-stack12): r1-99, units < the map's r100 target, length >= 4 splits off a 2-child every SX_GAP
// rounds; no king rule and no E1 start block; the child's spot is csplit's plus room
bool Planner::wantExplode(int& size) const {
    if (!cfg_->explode || w_.round < P::CSPLIT_START || w_.round >= P::SX_END) return false;
    sxTarget_ = std::min(cfg_->headsAt(w_.round), w_.unitLimit - P::SX_HEADROOM);   // v1 final: the atlas head curve
    if (sxTarget_ <= 0 || w_.unitCount >= sxTarget_) return false;
    const int L = w_.myLen;
    if (L < 4 || w_.round - lastSxRound_ < P::SX_GAP) return false;
    size = 2;
    if (L - size < 2) return false;
    if (!csplitChildSafe(P::CSPLIT_TAIL_DIST, P::SPLIT_MIN_CHILD_EXITS) || !roomOk()) { sxWhy_ = 3; return false; }
    return true;
}

// sr (ENGINE.md §3 B): r100-SR_END, length 4 -> 2 + 2 and 5-7 -> a 2-child every SR_GAP rounds while units < the phase-B target and a service
// deficit exists (research transfer 17; sdFree_), or units < SR_FLOOR_UNITS; the child's spot as sx (no re-split into a dead end)
bool Planner::wantResplit(int& size) const {
    if (!cfg_->resplit || w_.round < P::SR_START || w_.round >= P::SR_END) return false;
    const int L = w_.myLen;
    // survival clause (replaces stack7 floor and the lone dragon's insurance split in the swarm engine): with <= SR_SURVIVE_UNITS units any
    // dragon of length >= 4 may split; the king class only before the conversion clock or when it is our last dragon
    const bool survive = w_.unitCount <= P::SR_SURVIVE_UNITS && L >= 4 && (w_.round < cfg_->convStart || !w_.iAmLongest() || w_.unitCount == 1);
    if ((!survive && (L < P::SR_MIN_LEN || L > P::SR_MAX_LEN)) || w_.round - lastSrRound_ < P::SR_GAP) return false;
    srTarget_ = std::min(cfg_->headsAt(w_.round), w_.unitLimit - P::SX_HEADROOM);    // v1 final: the atlas head curve (held after r250)
    if (w_.unitCount >= srTarget_) return false;
    if (!survive && cfg_->resplitNeedDeficit && sdFree_ <= 0 && w_.unitCount >= P::SR_FLOOR_UNITS) { srWhy_ = 4; return false; }
    size = 2;
    if (L - size < 2) return false;
    if (!csplitChildSafe(P::CSPLIT_TAIL_DIST, P::SPLIT_MIN_CHILD_EXITS) || !roomOk()) { srWhy_ = 3; return false; }
    return true;
}

// sx / sr: the child's room (pf's pfRoomOk): >= SX_ROOM tiles free now reachable from our tail over edges that are not kelp and not an
// unexplored portal, none within one step of a known enemy head
bool Planner::roomOk() const {
    const int L = w_.myLen;
    if ((int)w_.body.size() < L || L < 2) return false;
    const int tail = w_.body[L - 1];
    if (tail < 0) return false;
    const std::vector<int16_t>& ed = P::TG_ON ? enemyDistOld_ : enemyDist_;
    int q[P::SX_ROOM + 8]; int qn = 0, found = 0; q[qn++] = tail;
    for (int i = 0; i < qn && found < P::SX_ROOM; i++) {
        for (int d = 0; d < 4 && found < P::SX_ROOM; d++) {
            const int u = w_.across(q[i], d);
            if (u < 0 || w_.occNow[u] != 0 || ed[u] <= 1) continue;
            bool dup = false; for (int j = 0; j < qn; j++) if (q[j] == u) { dup = true; break; }
            if (dup) continue;
            q[qn++] = u; found++;
        }
    }
    return found >= P::SX_ROOM;
}

// v1 belief tag: the believed longest ally (length, last known head) and our own king verdict under the active belief model
std::string Planner::beliefTag() const {
    int bl = 0, bt = -1;
    if (P::BELIEF_FIX_ON) { bl = w_.freshAllyLen; bt = w_.freshAllyT; }
    else {
        bl = w_.maxAllyLenSeen;
        int best = -1, bestSeen = -1;
        for (auto& [id, d] : w_.dragons) {
            if (id == w_.myId || d.team != w_.myTeam || d.headT < 0) continue;
            const int la = std::max(d.estLen, d.minLen);
            if (la > best || (la == best && d.headSeen > bestSeen)) { best = la; bestSeen = d.headSeen; bt = d.headT; }
        }
    }
    char buf[48];
    if (bt >= 0) snprintf(buf, sizeof buf, " bl%d@%d,%d k%d", bl, bt % w_.geo.W, bt / w_.geo.W, w_.iAmLongest() ? 1 : 0);
    else snprintf(buf, sizeof buf, " bl%d@- k%d", bl, w_.iAmLongest() ? 1 : 0);
    return buf;
}

} // namespace seed0
