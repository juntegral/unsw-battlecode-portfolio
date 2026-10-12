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

// penalty for stepping through a known portal into a region we cannot currently see
double Planner::portalPenalty(int from, int d, int to) const {
    if (w_.tiles[from].edge[d] != EDGE_PORTAL) return 0.0;
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
    int freeN = 0;
    for (int dd = 0; dd < 4; dd++) { if (dd == opp(d)) continue; int u = w_.across(to, dd); if (u >= 0 && w_.occNow[u] == 0) freeN++; }
    if (freeN <= 1) pen += P::PORTAL_TIGHT_PENALTY;
    return pen;
}

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
        int freeN = 0;
        for (int d = 0; d < 4; d++) { if (d == opp(lastDir)) continue; int u = w_.across(t, d); if (u >= 0 && tileEnterable(u, stepBase + 1, removed, path)) freeN++; }
        v += freeN * 0.15;
        if (freeN == 0) v += DEATH * 0.5 * GPOW[std::min(63, turns)];
        return v;
    }
    double best = -1e18; bool any = false;
    for (int d = 0; d < 4; d++) {
        if (d == opp(lastDir)) continue;
        int u = w_.across(t, d);
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

int Planner::pickSonarDir() const {
    // probe an unknown-exit portal straight ahead (within 3 tiles) so we may enter it next turn
    for (int d = 0; d < 4; d++) {
        if (d == opp(w_.myDir)) continue;
        int t = w_.headT;
        for (int k = 0; k < 3; k++) {
            if (w_.tiles[t].edge[d] == EDGE_KELP) break;
            int u = w_.across(t, d);
            if (u == -2) return d;
            if (u < 0) break;
            t = u;
        }
    }
    int d = (turnCounter_ + w_.myId) & 3;
    if (d == opp(w_.myDir)) d = w_.myDir;
    return d;
}

int Planner::pickHotspot() const {
    int best = -1; double bv = 0.3;
    for (int t = 0; t < w_.geo.tiles(); t++) if (attract_[t] > bv) { bv = attract_[t]; best = t; }
    return best;
}

// ------------------------------------------------------------------------------------------------
Action Planner::decide() {
    initGpow();
    turnCounter_++;
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
    computeSoftPenalty();
    computeAttract();
    long long tp2 = nowPoints();

    // ---- candidates: first action = 1 step, a justified 2-step sprint, or a probed unknown portal
    struct Cand { std::vector<int> dirs; std::vector<int> tiles; int removed; int pearls; double base; bool legal; bool trade; bool blind; };
    std::vector<Cand> cands;
    std::vector<int> path;
    bool probeOk = w_.probeRound == w_.round && w_.probeClear && w_.prevHeadT >= 0 && w_.probeDir >= 0 &&
                   w_.across(w_.prevHeadT, w_.probeDir) == w_.headT; // we stepped along the probed line
    for (int d1 = 0; d1 < 4; d1++) {
        if (d1 == opp(w_.myDir) && w_.myLen >= 2) continue; // into our own neck
        int u1 = w_.across(w_.headT, d1);
        Cand c; c.dirs = {d1}; c.removed = 0; c.pearls = 0; c.base = 0; c.legal = false; c.trade = false; c.blind = false;
        if (u1 == -1) { cands.push_back(c); continue; }
        if (u1 == -2) { // unknown portal exit: only after a clean probe along this direction
            c.blind = true;
            if (probeOk && w_.probeDir == d1 && !late_) { c.legal = true; c.base = P::PORTAL_GAMBLE_VALUE; }
            cands.push_back(c); continue;
        }
        int hid = w_.headOf[u1];
        if (hid >= 0 && hid != w_.myId && w_.dragons[hid].team != w_.myTeam) {
            double tv = tradeValue(hid);
            c.tiles = {u1}; c.legal = tv > 0.0; c.trade = true; c.base = tv > 0.0 ? tv : DEATH;
            cands.push_back(c); continue;
        }
        path.assign(1, w_.headT);
        if (!tileEnterable(u1, 1, 0, path)) { cands.push_back(c); continue; }
        c.legal = true; c.tiles = {u1};
        double p1 = SC.pnow[u1];
        c.pearls = p1 >= 0.5 ? 1 : 0; c.removed = c.pearls ? 0 : 1;
        double th1 = threatAt(u1);
        c.base = p1 - th1 - softPenalty_[u1] - portalPenalty(w_.headT, d1, u1) - (w_.edgeUnknown(w_.headT, d1) ? P::UNKNOWN_EDGE_PENALTY : 0.0);
        if (w_.tiles[u1].spawnRound == w_.round + 1 && p1 < 0.5) c.base -= P::BLOCK_SPAWN_PENALTY;
        cands.push_back(c);
        // 2-step sprints cost a segment: only when they grab a pearl, escape a threat, or trade
        if (w_.myLen + c.pearls >= 3 && !late_) {
            for (int d2 = 0; d2 < 4; d2++) {
                if (d2 == opp(d1)) continue;
                int u2 = w_.across(u1, d2);
                if (u2 < 0) continue;
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
                         - (w_.edgeUnknown(u1, d2) ? P::UNKNOWN_EDGE_PENALTY : 0.0);
                cands.push_back(s);
            }
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
            if (c.trade || c.blind) { v2[i] = c.base; continue; }
            path.assign(1, w_.headT); for (int t : c.tiles) path.push_back(t);
            double cont = dfs(c.tiles.back(), c.dirs.back(), 0, depth, c.removed, w_.myLen + c.pearls - ((int)c.dirs.size() - 1), path, hard);
            v2[i] = c.base + safety[i] + cont;
            if (nodes_ > P::DFS_NODE_BUDGET || nowPoints() > hard) { aborted = true; break; }
        }
        if (aborted) break;
        value = v2; depthDone = depth;
    }
    long long tp4 = nowPoints();

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
    bool doomed = best < 0 || value[best] < P::DOOM_VALUE;
    if (doomed && w_.myLen >= 4 && w_.unitCount < w_.unitLimit && (int)w_.body.size() == w_.myLen) {
        int tail = w_.body[w_.myLen - 1], neck = w_.body[w_.myLen - 2];
        bool childCanMove = true; // unknown tail surroundings: any chance beats certain death
        if (tail >= 0 && neck >= 0 && w_.tiles[tail].seen >= 0) {
            int exits = 0;
            for (int d = 0; d < 4; d++) { int u = w_.across(tail, d); if (u < 0 || u == neck) continue; if (w_.occNow[u] == 0 || u == w_.body[w_.myLen - 3 < 0 ? 0 : w_.myLen - 3]) exits++; }
            childCanMove = exits > 0;
        }
        if (childCanMove) {
            act.kind = Action::SPLIT; act.splitSize = w_.myLen - 2;
            act.sonarDir = pickSonarDir(); act.hotT = pickHotspot();
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
            act.sonarDir = pickSonarDir(); act.hotT = pickHotspot();
            char buf[64]; snprintf(buf, sizeof buf, "split%d u%d L%d", splitSize, w_.unitCount, w_.myLen);
            act.indicator = buf;
            return act;
        }
    }

    Cand& c = cands[best];
    act.kind = Action::MOVE; act.dirs.clear();
    for (int d : c.dirs) act.dirs += DIRCH[d];
    act.path = c.tiles; act.score = value[best];
    act.sonarDir = pickSonarDir(); act.hotT = pickHotspot();
    char buf[160];
    snprintf(buf, sizeof buf, "%s v%.1f d%d L%d%s%s%s", act.dirs.c_str(), value[best], depthDone, w_.myLen, c.trade ? " TRADE" : "", c.blind ? " PORTAL?" : "", late_ ? " late" : "");
    act.indicator = buf;
    if (P::PROFILE) {
        long long tp5 = nowPoints();
        snprintf(buf, sizeof buf, " | enemy %.2fM field %.2fM cand %.2fM dfs %.2fM rest %.2fM total %.2fM nodes %lld",
                 (tp1 - tp0) / 1e6, (tp2 - tp1) / 1e6, (tp3 - tp2) / 1e6, (tp4 - tp3) / 1e6, (tp5 - tp4) / 1e6, (tp5 - start) / 1e6, nodes_);
        act.indicator += buf;
    }
    return act;
}

} // namespace seed0
