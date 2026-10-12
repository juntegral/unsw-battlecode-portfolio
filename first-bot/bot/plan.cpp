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
    SC.enemyFar.assign(n, 9999); SC.allyFar.assign(n, 9999);
    distBuf_.assign(n, -1);
    auto spread = [&](int src, int radius, int le, int age, bool pseudo) {
        std::fill(distBuf_.begin(), distBuf_.end(), -1);
        queue_.clear(); queue_.push_back(src); distBuf_[src] = 0;
        for (size_t qi = 0; qi < queue_.size(); qi++) {
            int t = queue_[qi]; int dist = distBuf_[t];
            int eff = dist + age; // stale sighting: the head may already be closer
            if (eff <= 4 && eff < enemyDist_[t]) { enemyDist_[t] = (int16_t)eff; enemyNearLen_[t] = (int16_t)le; enemyPseudo_[t] = pseudo ? 1 : 0; }
            if (dist >= radius) continue;
            for (int dir = 0; dir < 4; dir++) {
                int u = w_.across(t, dir);
                if (u < 0 || distBuf_[u] >= 0) continue;
                if (w_.occNow[u] != 0 && u != w_.headT) continue; // heads cannot pass bodies; our head tile is a legal (fatal) target
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
        spread(d.headT, std::max(1, reach), le, age, false);
        // a higher-id enemy may split this round: its tail becomes a child head that moves before our next turn
        if (age == 0 && id > w_.myId && d.tailSeen && d.tailT >= 0 && le >= 4) spread(d.tailT, 1, 2, 0, true);
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
    if (d > 4) return 0.0;
    int le = enemyNearLen_[t], lm = w_.myLen;
    // the trade is decided by the opponent: favourable for them when we are at least as long, when we are the
    // team's last dragon (elimination), or late when we hold the longest and they can flip it
    bool favForThem = le <= lm || w_.unitCount == 1 || (late_ && w_.iAmLongest() && le <= lm + 4);
    double T;
    if (d <= 1) T = P::T1 * (favForThem ? 1.0 : P::TRADE_BAD_FOR_THEM);
    else if (d == 2) T = le >= 3 ? P::T2 * (favForThem ? 1.0 : P::T_FAR_BAD_FOR_THEM) : 0.0;
    else if (d == 3) T = le >= 4 ? P::T3 * (favForThem ? 1.0 : P::T_FAR_BAD_FOR_THEM) : 0.0;
    else T = le >= 5 ? P::T4 * (favForThem ? 1.0 : P::T_FAR_BAD_FOR_THEM) : 0.0;
    if (enemyPseudo_[t]) T *= P::PSEUDO_HEAD_MULT;
    if (w_.iAmLongest() && lm >= P::KING_MIN_LEN) T *= P::KING_THREAT_MULT;
    if (late_ && ahead_ && w_.iAmLongest()) T *= P::ENDGAME_THREAT_MULT;
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
    }
    return pen;
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
void Planner::computeAttract() {
    int n = w_.geo.tiles();
    attract_.assign(n, 0.0);
    SC.pnow.assign(n, 0.0);
    struct Src { int t; double v; int wait; };
    std::vector<Src> src; src.reserve(256);
    int hx = w_.headT % w_.geo.W, hy = w_.headT / w_.geo.W;
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
        src.push_back({t, v, wait});
    }
    // hunting: short dragons value a much longer enemy head; any dragon values an enemy shadowing a longer teammate
    if (w_.unitCount >= 2) {
        for (int id : w_.enemyHeadsNow) {
            const Dragon& d = w_.dragons[id];
            double tv = tradeValue(id);
            if (tv > 0.0 && w_.myLen <= P::HUNT_MAX_LEN) src.push_back({d.headT, std::min(tv * 0.15, 3.0), 0});
        }
    }
    for (auto& a : w_.allies) if (a.hotT >= 0 && w_.round - a.round <= 30) src.push_back({a.hotT, 0.4, 0});
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
        for (size_t qi = 0; qi < queue_.size(); qi++) {
            int t = queue_[qi]; int dist = distBuf_[t];
            // race outcomes from turn order: equal distance is ours; one closer needs their sprint
            double contest = 1.0;
            if (ef < dist - 1) contest = P::CONTEST_ENEMY_CLOSER;
            else if (ef == dist - 1) contest = P::CONTEST_ENEMY_ONE_CLOSER;
            else if (ef == dist) contest = P::CONTEST_EQUAL;
            if (af < dist) contest *= P::CONTEST_ALLY_CLOSER;
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
        if (cycles == 0 && (500 - w_.round) > count) v -= P::AREA_DEADEND_PENALTY; // we will hit the end before the game ends
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
double Planner::dfs(int t, int lastDir, int depth, int maxDepth, int removed, int lenNow, std::vector<int>& path, long long deadline) {
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
        if (goalOn_) v -= P::GATHER_W * std::min(goalDist_[t], 200);
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
        double v = p * g - threatAt(u) * g - softPenalty_[u] * g - portalPenalty(t, d, u) * g;
        if (w_.edgeUnknown(t, d)) v -= P::UNKNOWN_EDGE_PENALTY * g;
        if (x.spawnRound == arrive + 1 && p < 0.5) v -= P::BLOCK_SPAWN_PENALTY * g; // our head would block the spawn tick
        path.push_back(u);
        bool eat = p >= 0.5;
        v += dfs(u, d, depth + 1, maxDepth, removed + (eat ? 0 : 1), lenNow + (eat ? 1 : 0), path, deadline);
        path.pop_back();
        if (v > best) best = v;
    }
    if (!any) return DEATH * GPOW[std::min(63, turns)];
    return best;
}

// value of trading heads with this enemy this turn (0 = not allowed)
double Planner::tradeValue(int enemyId) const {
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
        if (w_.iAmLongest() && w_.maxAllyLenSeen > 0) return false; // the king only splits for insurance
        size = P::SPLIT_CHILD;
    }
    if (L - size < 2 || size < 2) return false;
    if (!w_.enemyHeadsNow.empty()) return false;
    // the child's head is our tail: its surroundings must be known and open, with no enemy in reach
    if (w_.body.empty() || (int)w_.body.size() < L) return false;
    int tail = w_.body[L - 1], neck = w_.body[L - 2];
    if (tail < 0 || neck < 0) return false;
    const Tile& tt = w_.tiles[tail];
    if (tt.seen < w_.round - 1) return false;
    for (int d = 0; d < 4; d++) if (tt.edge[d] == EDGE_UNKNOWN) return false;
    if (enemyDist_[tail] <= 2) return false;
    int exits = 0;
    for (int d = 0; d < 4; d++) {
        int u = w_.across(tail, d);
        if (u < 0 || u == neck) continue;
        if (w_.occNow[u] != 0 || enemyDist_[u] <= 1) continue;
        exits++;
    }
    return exits >= P::SPLIT_MIN_CHILD_EXITS;
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
    act.sonarDir = pickSonarDir(fromT, facing, &probe); act.hotT = pickHotspot();
    act.sonarFromT = fromT;
    act.sonarAll = !probe && w_.round >= P::GATHER_BROADCAST;
    // every other turn a non-king passes on the king's last known head, so news of it spreads beyond its own rays
    if (act.sonarAll && !gatherKing_ && goalId_ >= 0 && ((w_.round + w_.myId) & 1)) {
        act.relayId = goalId_; act.relayRound = goalRound_; act.relayT = goalT_; act.relayLen = goalLen_;
    }
}

// Gathering goal (c10): a non-king heads for the longest ally it has recent news of (seen, heard or relayed); the king
// keeps feeding itself. goalDist_ = path distance over known edges (bodies ignored).
void Planner::computeGoal() {
    goalOn_ = false; goalT_ = -1; gatherKing_ = true; goalId_ = -1;
    if (w_.round < P::GATHER_BROADCAST) return;
    int n = w_.geo.tiles();
    // are we the king? any ally heard to be longer recently says no; the goal is the freshest such ally's head
    int goalLen = 0, goalAge = 1 << 20;
    for (auto& [id, d] : w_.dragons) {
        if (id == w_.myId || d.team != w_.myTeam || d.headT < 0) continue;
        int age = w_.round - d.headSeen;
        int la = std::max(d.estLen, d.minLen);
        if (la <= w_.myLen || age > P::GATHER_KING_MEMORY) continue;
        gatherKing_ = false;
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
Action Planner::decide() {
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

    if (!w_.parsedOk || w_.headT < 0 || w_.tiles.empty()) {
        int order[4] = {w_.myDir, leftOf(w_.myDir), rightOf(w_.myDir), opp(w_.myDir)};
        act.dirs = std::string(1, DIRCH[w_.myDir]);
        if (w_.headT >= 0 && !w_.occNow.empty()) {
            for (int i = 0; i < 3; i++) { int u = w_.across(w_.headT, order[i]); if (u >= 0 && w_.occNow[u] == 0) { act.dirs = std::string(1, DIRCH[order[i]]); break; } }
        }
        act.indicator = "degraded";
        return act;
    }

    SC.bodyIndex.assign(n, -1);
    for (size_t i = 0; i < w_.body.size(); i++) if (w_.body[i] >= 0) SC.bodyIndex[w_.body[i]] = (int)i;
    if ((int)exploreStamp_.size() != n) { exploreStamp_.assign(n, -1); exploreVal_.assign(n, 0.0); }
    long long tp0 = nowPoints();
    computeEnemyDistance();
    long long tp1 = nowPoints();
    computeFrontier();
    computeSoftPenalty();
    computeAttract();
    computeGoal();
    long long tp2 = nowPoints();

    // ---- late consolidation: only the longest dragon counts at the end. A shorter dragon beside a longer teammate
    // dies in place so its ceil(L/2) dropped pearls lie where the teammate can eat them before round 500.
    bool gathering = w_.round >= P::GATHER_START;
    if ((w_.round >= P::FEED_FIRST_ROUND || gathering) && w_.unitCount >= 3 && enemyDist_[w_.headT] > 4 && (int)w_.body.size() >= 2) {
        int feedTo = -1, feedDist = 99;
        // the longest ally we know of (recently): before the late window only it is fed, not every longer ally (c10m)
        int kingLen = 0;
        for (auto& [id, d] : w_.dragons)
            if (id != w_.myId && d.team == w_.myTeam && d.headT >= 0 && w_.round - d.headSeen <= P::GATHER_KING_MEMORY)
                kingLen = std::max(kingLen, std::max(d.estLen, d.minLen));
        bool earlyOnlyKing = w_.round < P::FEED_FIRST_ROUND;
        for (int id : w_.allyHeadsNow) {
            const Dragon& a = w_.dragons[id];
            // a whole chain in view is exact; a sonar length can predate a split made this round
            int la = a.tailSeen && a.lastSeen == w_.round ? a.visLen : std::max(a.minLen, a.estLen);
            if (a.headT < 0 || la <= w_.myLen) continue;
            if (earlyOnlyKing && la < kingLen - 2) continue;
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
            if (found < feedDist) { feedDist = found; feedTo = id; }
        }
        bool lateWindow = w_.round >= P::FEED_FIRST_ROUND && w_.round >= 500 - (w_.myLen + feedDist + P::FEED_SLACK);
        if (feedTo >= 0 && (lateWindow || (gathering && w_.unitCount >= P::GATHER_FEED_UNITS && w_.myLen >= P::GATHER_FEED_MIN_LEN))) {
            act.dirs = std::string(1, DIRCH[opp(w_.myDir)]); // into our own neck: death with the body as it stands
            char buf[64]; snprintf(buf, sizeof buf, "feed #%d d%d L%d", feedTo, feedDist, w_.myLen);
            act.indicator = buf;
            return act;
        }
    }

    // ---- candidates: first action = 1 step, a justified 2-step sprint, or a probed unknown portal
    struct Cand { std::vector<int> dirs; std::vector<int> tiles; int removed; int pearls; double base; bool legal; bool trade; bool blind; bool esc = false; bool voluntary = false; };  // esc: cand-avoid6, voluntary: cand-portal1
    std::vector<Cand> cands;
    std::vector<int> path;
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
            c.voluntary = clean && !late_ && fv > 0.0;
            if (!c.voluntary) c.base -= P::BLIND_DESPERATE_PENALTY; // only when all else is doomed
            cands.push_back(c); continue;
        }
        int hid = w_.headOf[u1];
        if (hid >= 0 && hid != w_.myId && w_.dragons[hid].team != w_.myTeam) {
            double tv = tradeValue(hid);
            c.tiles = {u1}; c.legal = tv > 0.0; c.trade = true; c.base = tv > 0.0 ? tv : DEATH;
            cands.push_back(c); continue;
        }
        // cand-portal1: a known portal whose exit we cannot see: free right after a clean probe from here, dearer without
        // one, dearest when that probe hit a dragon (it may stand on the exit)
        double portalExtra = 0.0;
        if (w_.tiles[w_.headT].edge[d1] == EDGE_PORTAL && w_.tiles[u1].seen != w_.round) {
            bool probedHere = w_.probeRound == w_.round && w_.probeFromT == w_.headT && w_.probeDir == d1;
            portalExtra = !probedHere ? P::PORTAL_UNPROBED_PENALTY : (w_.probeClear ? 0.0 : P::PORTAL_DIRTY_PENALTY);
        }
        path.assign(1, w_.headT);
        if (!tileEnterable(u1, 1, 0, path)) { cands.push_back(c); continue; }
        c.legal = true; c.tiles = {u1};
        double p1 = SC.pnow[u1];
        c.pearls = p1 >= 0.5 ? 1 : 0; c.removed = c.pearls ? 0 : 1;
        double th1 = threatAt(u1);
        c.base = p1 - th1 - softPenalty_[u1] - portalPenalty(w_.headT, d1, u1) - portalExtra - (w_.edgeUnknown(w_.headT, d1) ? P::UNKNOWN_EDGE_PENALTY : 0.0);
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
                s.base = p1 + p2 - P::SPRINT_COST - th2 - softPenalty_[u2] - portalPenalty(u1, d2, u2)
                         - (w_.edgeUnknown(u1, d2) ? P::UNKNOWN_EDGE_PENALTY : 0.0)
                         - portalPenalty(w_.headT, d1, u1) - portalExtra; // cand-portal1: the first step's portal too
                cands.push_back(s);
            }
        }
    }

    // ---- cand-avoid2: ram escape. Every single step is threatened by a shorter head and no 2-step sprint reaches an
    // unthreatened tile: add 2-step (also late) and 3-step sprints that end on an unthreatened tile.
    bool escapeOn = w_.myLen >= P::ESCAPE_MIN_LEN && survivedExposures_ < P::RAMMER_TRUST && enemyDist_[w_.headT] <= 4;
    if (escapeOn) {
        bool allSinglesThreatened = true, anySingle = false, cleanSprint = false;
        for (const Cand& c : cands) {
            if (!c.legal || c.trade || c.blind || c.tiles.empty()) continue;
            if (c.dirs.size() == 1) { anySingle = true; if (threatAt(c.tiles[0]) <= 0.0) allSinglesThreatened = false; }
            else if (threatAt(c.tiles.back()) <= 0.0) cleanSprint = true;
        }
        if (anySingle && allSinglesThreatened && !cleanSprint) {
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
                        s2.base = p1 + p2 - P::SPRINT_COST - softPenalty_[u2] - portalPenalty(u1, d2, u2) - (w_.edgeUnknown(u1, d2) ? P::UNKNOWN_EDGE_PENALTY : 0.0);
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
                        s3.base = p1 + p2 + p3 - 2.0 * P::SPRINT_COST - softPenalty_[u3] - portalPenalty(u2, d3, u3) - (w_.edgeUnknown(u2, d3) ? P::UNKNOWN_EDGE_PENALTY : 0.0);
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
            if (tv <= 0.0) continue;
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
                Cand c; c.dirs = dirs; c.tiles = tiles; c.legal = true; c.trade = true; c.blind = false;
                c.base = tv - ((int)dirs.size() - 1) * P::SPRINT_COST; c.removed = 0; c.pearls = 0;
                cands.push_back(c);
            }
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
            double cont = dfs(c.tiles.back(), c.dirs.back(), 0, depth, c.removed, w_.myLen + c.pearls - ((int)c.dirs.size() - 1), path, hard);
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
    int best = -1, bestSingle = -1;
    for (size_t i = 0; i < cands.size(); i++) {
        if (!cands[i].legal) continue;
        if (best < 0 || value[i] > value[best]) best = (int)i;
        if (cands[i].dirs.size() == 1 && !cands[i].trade && !cands[i].blind && (bestSingle < 0 || value[i] > value[bestSingle])) bestSingle = (int)i;
    }
    if (bestSingle >= 0) act.safeDir = cands[bestSingle].dirs[0];

    // ---- escape split: when every move dies within the horizon, hand the body to a child born at the tail
    // Only when death is imminent or an enemy head is near: a far-off "doom" is often a body we assume never
    // moves (tail out of view).
    // Waiting keeps the whole length; if the block is real, next turn has no open step and we split then.
    bool doomed = best < 0;
    bool deadEnd = false; // a legal step exists but none of them has a further step (the board, not an enemy)
    if (!doomed && value[best] < P::DOOM_VALUE) {
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
        act.dirs = std::string(1, DIRCH[w_.myDir]); act.indicator = "no-exit";
        return act;
    }

    // ---- split instead of moving when the policy says so and this move is not urgent
    int splitSize = 0;
    if (!cands[best].trade && !cands[best].blind && wantSplit(splitSize)) {
        double immediate = cands[best].tiles.empty() ? 0.0 : SC.pnow[cands[best].tiles[0]];
        bool threatened = false; for (int t : cands[best].tiles) if (threatAt(t) > 0.0) threatened = true;
        if (immediate < 0.5 && !threatened && safety[best] > -1.0 && enemyDist_[w_.headT] > 2) {
            act.kind = Action::SPLIT; act.splitSize = splitSize;
            setSonar(act);
            char buf[64]; snprintf(buf, sizeof buf, "split%d u%d L%d", splitSize, w_.unitCount, w_.myLen);
            act.indicator = buf;
            return act;
        }
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
    if (goalOn_) { snprintf(buf, sizeof buf, " %s%d", gatherKing_ ? "K" : "g", goalDist_[w_.headT]); act.indicator += buf; }
    if (c.esc) act.indicator += " esc";                                                              // cand-avoid2
    if (w_.myLen >= P::ESCAPE_MIN_LEN && survivedExposures_ >= P::RAMMER_TRUST) act.indicator += " T"; // cand-avoid2: escapes off
    if (P::PROFILE) {
        long long tp5 = nowPoints();
        snprintf(buf, sizeof buf, " | enemy %.2fM field %.2fM cand %.2fM dfs %.2fM rest %.2fM total %.2fM nodes %lld",
                 (tp1 - tp0) / 1e6, (tp2 - tp1) / 1e6, (tp3 - tp2) / 1e6, (tp4 - tp3) / 1e6, (tp5 - tp4) / 1e6, (tp5 - start) / 1e6, nodes_);
        act.indicator += buf;
    }
    return act;
}

} // namespace seed0
