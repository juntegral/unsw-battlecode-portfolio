// Evasive long-queen bot. Every dragon runs this program in its own process.
// Idea under test: the opponent trades length-2 dragons head-to-head and keeps
// nothing long, so a dragon that never ends a turn inside an enemy head's
// reach and stays long wins on the round-500 queen / longest-dragon rule.
#include "helper.hpp"

#include <algorithm>
#include <cstdlib>
#include <deque>
#include <vector>

using namespace unswbc;

#ifndef LCAP
#define LCAP 12 // stop seeking pearls at this length
#endif
#ifndef SPLIT_AT
#define SPLIT_AT 0 // 0: never split
#endif
#ifndef HUNT
#define HUNT 1 // non-queens kamikaze into the enemy queen when in reach
#endif
#ifndef QSW
#define QSW 3 // the queen splits like a swarm unit while the team has fewer dragons than this
#endif
#ifndef SWARM
#define SWARM 1
#endif
#ifndef HUNT_MIN
#define HUNT_MIN 4 // swarm units seek trades once the team has this many dragons
#endif
#ifndef SMALL_AREA
#define SMALL_AREA 600 // below this many cells the queen stays short
#endif
#ifndef LCAP_SMALL
#define LCAP_SMALL 6
#endif
#ifndef FEARLESS
#define FEARLESS 1 // swarm-mode dragons ignore enemy reach when moving
#endif
#ifndef LOCAL
#define LOCAL 1 // avoid trades where more enemy heads than friendly heads are in view
#endif
#ifndef SMALL_QUEEN_FIGHTS
#define SMALL_QUEEN_FIGHTS 1 // on small maps the queen is an ordinary swarm unit
#endif
#ifndef MATERIAL
#define MATERIAL 0 // prefer trades that cost us no more length than them
#endif
#ifndef DANGER3
#define DANGER3 80.0
#endif
#ifndef RING
#define RING 1 // the queen grows to 23 and walks a sealed 24-cell cycle
#endif
#ifndef RING_MIN
#define RING_MIN 12 // shortest length at which the queen may start a cycle that has pearls on it
#endif
#ifndef RING_QUIET
#define RING_QUIET 20
#endif
#ifndef RING_WAIT
#define RING_WAIT 40 // rounds at ring length before tiles that merely look quiet are accepted
#endif
#ifndef RING_LEN
#define RING_LEN 23
#endif
#ifndef MAXFREE
#define MAXFREE 3
#endif

static int W, H;
static const int DX[4] = {0, 1, 0, -1}, DY[4] = {-1, 0, 1, 0};
static const char DC[4] = {'N', 'E', 'S', 'W'};

struct Cell {
    unsigned char e[4] = {0, 0, 0, 0}; // 0 unknown, 1 open, 2 kelp, 3 portal
    int seen = 0;
    bool pearl = false;
    int due = -1;   // round of the next spawn attempt, whether or not a pearl lies here now
    int spawn = -1; // round the next pearl is due, -1 unknown or never
    bool fount = false; // a pearl lies here and the next one is already due: spawns nearly every round
};
static std::vector<Cell> mem;
static inline int id_of(int x, int y) { return ((y % H + H) % H) * W + ((x % W + W) % W); }
static inline int step(int c, int d) { return id_of(c % W + DX[d], c / W + DY[d]); }
static inline bool open_edge(int c, int d) { return mem[c].e[d] <= 1; }

struct Enemy { int pos, id, len, reach; };

// A Hamiltonian cycle on a 6x4 block. A dragon of length 23 on it leaves one free cell, the one ahead of the
// head. At indices 5, 11, 17 and 23 the head and that free cell are both interior cells, so every other
// neighbour of either is the dragon's own body and no enemy head can get next to the head. Six steps a turn
// (the free allowance at length 21..24) go from one such stop to the next.
static const int RN = 24;
static const int RX[RN] = {3, 3, 4, 5, 5, 4, 4, 5, 5, 4, 3, 3, 2, 2, 1, 0, 0, 1, 1, 0, 0, 1, 2, 2};
static const int RY[RN] = {1, 0, 0, 0, 1, 1, 2, 2, 3, 3, 3, 2, 2, 3, 3, 3, 2, 2, 1, 1, 0, 0, 0, 1};
static inline bool ring_stop(int i) { return i % 6 == 5; }
static bool in_ring = false;
static int ring_cell[RN], ring_idx = 0, ready_round = -1;

static std::vector<int> occ;      // 0 free, 1 own, 2 other body, 3 enemy head
static std::vector<int> dangerN;  // enemies able to enter the cell this round
static std::vector<int> edist;    // steps from nearest enemy head (99 = far)
static std::vector<int> tdist;    // steps to nearest target (pearl / unexplored)
static std::vector<Enemy> enemies;
static std::vector<int> body;     // own cells, tail first, head last
static bool body_ordered = false;
static bool is_queen = false, want_grow = true, evader = false, hunting = false, fearless = false;
static std::vector<std::vector<int>> ally_exits; // free cells next to each visible ally head
static std::vector<char> queen_adj;               // cells next to our queen's head
static int my_len = 3;

struct Best { double score = -1e18; std::vector<int> dirs; std::vector<int> cells; };
static Best best;

static int flood(int from, const std::vector<int>& sim, int cap) {
    static std::vector<int> mark; static int stamp = 0;
    if ((int)mark.size() != W * H) mark.assign(W * H, 0);
    ++stamp;
    for (int c : sim) mark[c] = stamp;
    std::vector<int> q{from}; mark[from] = stamp; int n = 0;
    for (size_t i = 0; i < q.size() && n < cap; i++) {
        int c = q[i]; n++;
        for (int d = 0; d < 4; d++) {
            if (!open_edge(c, d)) continue;
            int v = step(c, d);
            if (mark[v] == stamp || occ[v] >= 2) continue;
            mark[v] = stamp; q.push_back(v);
        }
    }
    return n;
}

static double evaluate(const std::vector<int>& sim, int pearls, int steps, int paid) {
    int c = sim.back();
    double s = 0;
    if (dangerN[c] && !fearless) s -= 1e6 * dangerN[c];
    if (dangerN[c] && fearless && my_len >= 3) s -= DANGER3 * dangerN[c]; // a longer body is a worse trade
    for (auto const& ex : ally_exits) { // do not box in a teammate
        int left = 0;
        for (int v : ex) if (std::find(sim.begin(), sim.end(), v) == sim.end()) left++;
        if (left == 0) s -= 5000; else if (left == 1) s -= 150;
    }
    int need = std::min((int)sim.size() + 3, 24);
    int space = flood(c, sim, need + 8);
    if (space < need) s -= 4000.0 * (need - space);
    s += 2.0 * space;
    int exits = 0;
    for (int d = 0; d < 4; d++) {
        if (!open_edge(c, d)) continue;
        int v = step(c, d);
        if (occ[v] >= 2 || (dangerN[v] && !fearless)) continue;
        if (std::find(sim.begin(), sim.end(), v) != sim.end()) continue;
        exits++;
    }
    s += 25.0 * exits;
    if (exits == 0) s -= 3000;
    if (evader && exits == 1) s -= 1500; // one teammate stepping there would box the queen in
    if (!is_queen && queen_adj[c]) s -= 3000; // keep clear of our queen's head
    if (evader) { if (edist[c] < 7) s -= 60.0 * (7 - edist[c]); }
    else if (!fearless && edist[c] < 3) s -= 15.0 * (3 - edist[c]);
    if (want_grow) {
        s += 40.0 * pearls;
        if (tdist[c] < 9999) s -= 4.0 * tdist[c];
    } else {
        s -= 500.0 * pearls;
        if (tdist[c] < 9999) s -= 6.0 * tdist[c];
    }
    s -= 0.5 * steps + 300.0 * paid;
    if (evader && enemies.empty()) s -= 25.0 * (steps - 1); // do not rush into cells we cannot see around
    return s;
}

static void search(std::vector<int>& sim, std::vector<int>& dirs, std::vector<int>& eaten, int free_left,
                   int paid_left, int paid) {
    if (!dirs.empty()) {
        double s = evaluate(sim, (int)eaten.size(), (int)dirs.size(), paid);
        if (s > best.score) {
            best.score = s; best.dirs = dirs;
            best.cells.assign(sim.end() - std::min(sim.size(), dirs.size()), sim.end());
        }
    }
    if (free_left + paid_left <= 0) return;
    int c = sim.back();
    for (int d = 0; d < 4; d++) {
        if (mem[c].e[d] >= 2) continue; // kelp or portal
        int v = step(c, d);
        if (occ[v] >= 2) continue;
        if (std::find(sim.begin(), sim.end(), v) != sim.end()) continue;
        bool pearl = mem[v].pearl && std::find(eaten.begin(), eaten.end(), v) == eaten.end();
        bool pay = free_left <= 0;
        if (pay && (int)sim.size() <= 2) continue;
        std::vector<int> saved = sim;
        sim.push_back(v);
        if (pearl) eaten.push_back(v);
        dirs.push_back(d);
        search(sim, dirs, eaten, pay ? 0 : free_left - 1, pay ? paid_left - 1 : paid_left, paid + (pay ? 1 : 0));
        dirs.pop_back();
        if (pearl) eaten.pop_back();
        sim = saved;
    }
}

// Shortest path of free cells from our head into an enemy head, within max_steps.
static bool path_to(int target, int max_steps, std::vector<int>& out) {
    int from = body.back();
    std::vector<int> prev(W * H, -2), pd(W * H, -1), dist(W * H, 99), q{from};
    prev[from] = -1; dist[from] = 0;
    for (size_t i = 0; i < q.size(); i++) {
        int c = q[i];
        if (dist[c] >= max_steps) continue;
        for (int d = 0; d < 4; d++) {
            if (mem[c].e[d] >= 2) continue;
            int v = step(c, d);
            if (prev[v] != -2) continue;
            if (v != target && occ[v] != 0) continue;
            prev[v] = c; pd[v] = d; dist[v] = dist[c] + 1; q.push_back(v);
            if (v == target) {
                for (int x = v; x != from; x = prev[x]) out.push_back(pd[x]);
                std::reverse(out.begin(), out.end());
                return true;
            }
        }
    }
    return false;
}

int main() {
    auto [ct, game] = init();
    auto [w, h] = game.get_map_size();
    W = w; H = h;
    mem.assign(W * H, Cell{});
    std::deque<int> trail;
    Team const mine = ct.get_team();

    while (update(ct, game)) {
        int const round = game.get_round_num();
        int const me = id_of(ct.get_position().x, ct.get_position().y);
        my_len = ct.get_length();
        is_queen = ct.get_id() < 2 && (W * H >= SMALL_AREA || !SMALL_QUEEN_FIGHTS);
        evader = is_queen && (!SWARM || ct.get_unit_count() >= QSW);
        want_grow = true;

        occ.assign(W * H, 0);
        enemies.clear();
        std::vector<std::pair<int, int>> own_parts; // cell, dir index
        std::vector<int> enemy_ids, enemy_cells, ally_heads;
        int queen_head = -1;
        for (auto const& t : ct.get_tiles()) {
            int c = id_of(t.position.x, t.position.y);
            for (int d = 0; d < 4; d++) {
                auto const& e = t.edges[d];
                mem[c].e[d] = e.edge_type == EdgeType::KELP ? 2 : e.edge_type == EdgeType::PORTAL ? 3 : 1;
            }
            mem[c].seen = round;
            mem[c].pearl = t.has_pearl();
            mem[c].due = t.get_pearl_time() >= 1 ? round + t.get_pearl_time() : -1;
            { int pt = t.get_pearl_time();
              if (t.has_pearl()) mem[c].fount = pt >= 1 && pt <= 2;
              else if (pt < 1 || pt > 2) mem[c].fount = false; }
            mem[c].spawn = (!t.has_pearl() && t.get_pearl_time() >= 1) ? round + t.get_pearl_time() : -1;
            if (auto const* p = t.get_dragon()) {
                if (p->dragon_id == ct.get_id()) {
                    occ[c] = 1;
                    int di = p->dir.value == 'N' ? 0 : p->dir.value == 'E' ? 1 : p->dir.value == 'S' ? 2 : 3;
                    own_parts.push_back({c, di});
                } else {
                    occ[c] = 2;
                    if (p->team == mine && p->is_head()) ally_heads.push_back(c);
                    if (p->team == mine && p->is_head() && p->dragon_id < 2) queen_head = c;
                    if (!(p->team == mine)) {
                        enemy_ids.push_back(p->dragon_id); enemy_cells.push_back(c);
                        if (p->is_head()) { occ[c] = 3; enemies.push_back({c, p->dragon_id, 0, 0}); }
                    }
                }
            }
        }
        int const mx = me % W, my = me / W;
        for (auto& e : enemies) {
            bool border = false;
            for (size_t i = 0; i < enemy_ids.size(); i++) {
                if (enemy_ids[i] != e.id) continue;
                e.len++;
                int dx = std::abs(enemy_cells[i] % W - mx), dy = std::abs(enemy_cells[i] / W - my);
                dx = std::min(dx, W - dx); dy = std::min(dy, H - dy);
                if (std::max(dx, dy) >= 3 && enemy_cells[i] != e.pos) border = true;
            }
            if (border) e.len++;
            e.len = std::max(e.len, 2);
            e.reach = std::min((e.len + 3) / 4 + (e.len - 2), 4);
        }

        // Own body, tail first. Rebuilt from the vision on the first turn, then tracked.
        if (trail.empty() || trail.back() != me) {
            trail.clear();
            std::vector<int> chain{me};
            for (int guard = 0; guard < my_len; guard++) {
                bool found = false;
                for (auto const& [c, d] : own_parts) {
                    if (c == chain.back() || step(c, d) != chain.back()) continue;
                    if (std::find(chain.begin(), chain.end(), c) != chain.end()) continue;
                    chain.push_back(c); found = true; break;
                }
                if (!found) break;
            }
            for (auto it = chain.rbegin(); it != chain.rend(); ++it) trail.push_back(*it);
        }
        while ((int)trail.size() > my_len) trail.pop_front();
        body.assign(trail.begin(), trail.end());
        body_ordered = (int)body.size() >= my_len;
        for (int c : body) occ[c] = 1;
        for (auto const& [c, d] : own_parts)
            if (std::find(body.begin(), body.end(), c) == body.end()) { body.insert(body.begin(), c); body_ordered = false; }

        queen_adj.assign(W * H, 0);
        if (queen_head >= 0)
            for (int d = 0; d < 4; d++) if (mem[queen_head].e[d] != 2) queen_adj[step(queen_head, d)] = 1;
        ally_exits.clear();
        for (int a : ally_heads) {
            std::vector<int> ex;
            for (int d = 0; d < 4; d++) {
                if (mem[a].e[d] >= 2) continue;
                int v = step(a, d);
                if (occ[v] == 0) ex.push_back(v);
            }
            if (!ex.empty()) ally_exits.push_back(ex);
        }
        int const lcap = RING ? RING_LEN : (W * H < SMALL_AREA ? LCAP_SMALL : LCAP);
        // Outnumbered in view: trading here feeds the dropped pearls to them, so keep out of reach instead.
        bool const outnumbered = (LOCAL && (int)enemies.size() > (int)ally_heads.size() + 1) || ct.get_unit_count() <= 2;
        hunting = SWARM && !is_queen && ct.get_unit_count() >= HUNT_MIN && !outnumbered && (my_len <= 2 || !MATERIAL);
        fearless = SWARM && !is_queen && FEARLESS && !outnumbered; // a queen that still counts as queen never walks into reach

        // Enemy reach this round and distance field from enemy heads.
        dangerN.assign(W * H, 0);
        edist.assign(W * H, 99);
        for (auto const& e : enemies) {
            std::vector<int> dist(W * H, -1), q{e.pos};
            dist[e.pos] = 0;
            for (size_t i = 0; i < q.size(); i++) {
                int c = q[i];
                edist[c] = std::min(edist[c], dist[c]);
                if (dist[c] > 0 && dist[c] <= e.reach) dangerN[c]++;
                if (dist[c] >= 7) continue;
                for (int d = 0; d < 4; d++) {
                    if (mem[c].e[d] == 2) continue;
                    int v = step(c, d);
                    if (dist[v] >= 0 || occ[v] >= 2) continue;
                    dist[v] = dist[c] + 1; q.push_back(v);
                }
            }
        }

        if (is_queen) { // a long enemy can split and its tail becomes a head that moves this same round
            for (auto const& e : enemies) {
                if (e.len < 4) continue;
                for (size_t i = 0; i < enemy_ids.size(); i++) {
                    if (enemy_ids[i] != e.id || enemy_cells[i] == e.pos) continue;
                    for (int d = 0; d < 4; d++)
                        if (mem[enemy_cells[i]].e[d] != 2) { int v = step(enemy_cells[i], d); if (occ[v] < 2) dangerN[v]++; }
                }
            }
        }

        // Targets: pearls we can reach, and tiles whose pearl is due by the time we arrive.
        tdist.assign(W * H, 9999);
        {
            std::vector<int> dm(W * H, 9999), q{me};
            dm[me] = 0;
            for (size_t i = 0; i < q.size(); i++) {
                int c = q[i];
                for (int d = 0; d < 4; d++) {
                    if (mem[c].e[d] >= 2) continue;
                    int v = step(c, d);
                    if (dm[v] < 9999 || occ[v] >= 2) continue;
                    dm[v] = dm[c] + 1; q.push_back(v);
                }
            }
            std::vector<std::pair<int, int>> cand; // eta, cell
            int best_eta = 9999;
            for (int c : q) {
                if (c == me || (dangerN[c] && !fearless)) continue;
                int eta;
                if (mem[c].pearl) eta = dm[c];
                else if (mem[c].spawn >= 0) eta = mem[c].spawn >= round ? std::max(dm[c], mem[c].spawn - round) : dm[c] + 1;
                else continue;
                cand.push_back({eta, c});
                best_eta = std::min(best_eta, eta);
            }
            auto yield = [&](int c) {
                double y = (mem[c].pearl || (mem[c].spawn >= 0 && mem[c].spawn - round <= 20)) ? 1.0 : 0.0;
                if (mem[c].fount) y += 5.0;
                return y;
            };
            std::vector<double> val(cand.size(), 0.0);
            double best_val = 0;
            for (size_t i = 0; i < cand.size(); i++) {
                int c = cand[i].second, cx = c % W, cy = c / W;
                double v = 0;
                for (int dy = -3; dy <= 3; dy++)
                    for (int dx = -3 + std::abs(dy); dx <= 3 - std::abs(dy); dx++) v += yield(id_of(cx + dx, cy + dy));
                val[i] = (1.0 + 0.3 * v) / (cand[i].first + 4.0);
                best_val = std::max(best_val, val[i]);
            }
            std::vector<int> src;
            for (size_t i = 0; i < cand.size(); i++)
                if (val[i] >= 0.85 * best_val) { tdist[cand[i].second] = cand[i].first - dm[cand[i].second]; src.push_back(cand[i].second); }
            if (hunting)
                for (auto const& e : enemies) { tdist[e.pos] = 0; src.push_back(e.pos); }
            if (RING && is_queen && my_len >= RING_LEN) { // look for a 6x4 block of tiles that never spawn
                src.clear();
                tdist.assign(W * H, 9999);
                for (int c = 0; c < W * H; c++) {
                    if (dm[c] >= 9999) continue;
                    for (int tr = 0; tr < 2; tr++) {
                        bool ok = true;
                        for (int a = -2; a <= 3 && ok; a++)
                            for (int b = -1; b <= 2 && ok; b++) {
                                int v = tr ? id_of(c % W + b, c / W + a) : id_of(c % W + a, c / W + b);
                                if (mem[v].seen == 0 || mem[v].due >= 0 || mem[v].pearl) ok = false;
                            }
                        if (ok) { tdist[c] = 0; src.push_back(c); break; }
                    }
                }
            }
            if (src.empty())
                for (int c = 0; c < W * H; c++) if (mem[c].seen == 0 || round - mem[c].seen > 60) { tdist[c] = 0; src.push_back(c); }
            for (size_t i = 0; i < src.size(); i++) {
                int c = src[i];
                for (int d = 0; d < 4; d++) {
                    if (mem[c].e[d] >= 2) continue;
                    int v = step(c, d);
                    if (tdist[v] <= tdist[c] + 1 || occ[v] >= 2) continue;
                    tdist[v] = tdist[c] + 1; src.push_back(v);
                }
            }
        }


        // ---- sealed ring (queen only) ----
        if (RING && is_queen && in_ring && (ring_cell[ring_idx] != me || !body_ordered)) in_ring = false;
        if (RING && is_queen && my_len >= RING_LEN && ready_round < 0) ready_round = round;
        bool const relaxed = ready_round >= 0 && round - ready_round > RING_WAIT;
        if (RING && is_queen && !in_ring && body_ordered && my_len >= RING_LEN - 1 && my_len <= RING_LEN) {
            int best_score = -1, best_cells[RN], best_j = 0;
            for (int t = 0; t < 8; t++) {
                for (int j = 0; j < RN; j++) {
                    int cells[RN];
                    bool ok = true;
                    for (int k = 0; k < RN && ok; k++) {
                        int dx = RX[k] - RX[j], dy = RY[k] - RY[j];
                        if (t & 4) std::swap(dx, dy);
                        if (t & 1) dx = -dx;
                        if (t & 2) dy = -dy;
                        if (std::abs(dx) > 3 || std::abs(dy) > 3) { ok = false; break; }
                        int c = id_of(me % W + dx, me / W + dy);
                        cells[k] = c;
                        if (mem[c].seen != round || occ[c] >= 2) ok = false;
                        if (mem[c].due >= 0 && (!relaxed || mem[c].due - round <= RING_QUIET)) ok = false; // tiles that never spawn
                    }
                    for (int k = 0; k < RN && ok; k++) { // every edge of the cycle must be open water
                        bool edge = false;
                        for (int d = 0; d < 4; d++)
                            if (mem[cells[k]].e[d] == 1 && step(cells[k], d) == cells[(k + 1) % RN]) edge = true;
                        if (!edge) ok = false;
                    }
                    if (!ok) continue;
                    std::deque<int> sim(body.begin(), body.end()); // walk one full lap; our trailing body must be gone in time
                    int lap_len = my_len;
                    for (int n = 1; n <= RN && ok; n++) {
                        int c = cells[(j + n) % RN];
                        if (std::find(sim.begin(), sim.end(), c) != sim.end()) ok = false;
                        if (n <= 6 && dangerN[c]) ok = false; // nobody may reach the first leg this round
                        sim.push_back(c);
                        if (mem[c].pearl && n < RN) lap_len++; else sim.pop_front();
                    }
                    if (!ok || lap_len < RING_LEN - 1 || lap_len > RING_LEN) continue; // pearls on the cycle must bring us to ring length
                    int score = 0;
                    for (int k = 0; k < RN; k += 6) { int c = cells[k]; if (mem[c].spawn < 0 || mem[c].spawn - round > 80) score += 2; }
                    for (int k = 0; k < RN; k++) if (mem[cells[k]].spawn < 0 || mem[cells[k]].spawn - round > 30) score++;
                    if (score > best_score) { best_score = score; best_j = j; for (int k = 0; k < RN; k++) best_cells[k] = cells[k]; }
                }
            }
            if (best_score >= 0) { in_ring = true; ring_idx = best_j; for (int k = 0; k < RN; k++) ring_cell[k] = best_cells[k]; }
        }
        if (is_queen && my_len >= RING_LEN - 1) { FILE* f = fopen("dbg.txt", "a"); fprintf(f, "  r%d queen L%d in_ring%d idx%d ord%d enemies%zu at %d,%d\n", round, my_len, (int)in_ring, ring_idx, (int)body_ordered, enemies.size(), me % W, me / W); fclose(f); }
        if (RING && is_queen && in_ring) {
            std::deque<int> sim(body.begin(), body.end());
            int len = my_len, feasible = 0, pick = 0;
            int const allowed = std::min((my_len + 3) / 4, 6);
            for (int n = 1; n <= allowed; n++) {
                int c = ring_cell[(ring_idx + n) % RN];
                if (occ[c] >= 2) break;
                if (std::find(sim.begin(), sim.end(), c) != sim.end()) break;
                sim.push_back(c);
                if (mem[c].pearl) len++; else sim.pop_front();
                feasible = n;
                if (ring_stop((ring_idx + n) % RN)) pick = n;
                if (len >= RN) break; // the cycle is full: stop here, fully enclosed
            }
            if (my_len >= RN && ct.can_split(2)) { // full cycle: shed two segments
                ct.do_split(2);
                end_turn();
                continue;
            }
            std::vector<Direction> moves;
            if (feasible > 0) {
                if (pick == 0 || len >= RN) pick = feasible;
                int c = me;
                for (int n = 1; n <= pick; n++) {
                    int v = ring_cell[(ring_idx + n) % RN];
                    bool found = false;
                    for (int d = 0; d < 4; d++) if (mem[c].e[d] == 1 && step(c, d) == v) { moves.push_back(Direction(DC[d])); found = true; break; }
                    if (!found) break;
                    c = v;
                }
                if ((int)moves.size() != pick) moves.clear();
            }
            if (!moves.empty()) {
                for (int n = 1; n <= pick; n++) trail.push_back(ring_cell[(ring_idx + n) % RN]);
                ring_idx = (ring_idx + pick) % RN;
                ct.make_moves(moves);
                end_turn();
                continue;
            }
            in_ring = false; // something sits on our cycle: fall back to running
        }
        bool const avoid_pearls = RING && is_queen && my_len >= RING_LEN; // stay at ring length until the ring is found
        want_grow = !avoid_pearls;
        if (avoid_pearls && my_len >= RING_LEN + 1 && ct.can_split(2) && !dangerN[me]) { ct.do_split(2); end_turn(); continue; }

        int const free_steps = std::min((my_len + 3) / 4, is_queen ? 4 : MAXFREE);
        std::vector<int> out_dirs;
        bool attack = false;

        // Non-queens trade themselves for the enemy queen when it is in reach.
        if (HUNT && !is_queen && ct.get_unit_count() >= 2) {
            for (auto const& e : enemies) {
                if (e.id >= 2) continue;
                std::vector<int> p;
                if (path_to(e.pos, (my_len + 3) / 4 + std::max(0, my_len - 2), p)) { out_dirs = p; attack = true; break; }
            }
        }

        // Split first when long enough: the child's head is our tail.
        if (SWARM && !attack && (fearless || !dangerN[me])) {
            bool split = false;
            if (is_queen) split = (!evader && my_len >= 4) || my_len >= lcap + 2;
            else split = my_len >= 4 && ct.get_unit_count() < ct.unit_limit - 4; // keep two slots for the queen
            if (split && !body_ordered) split = false;
            if (split) { // the child needs a way out that is not a pocket
                int t = body.front(), ways = 0;
                for (int d = 0; d < 4; d++) {
                    if (mem[t].e[d] >= 2) continue;
                    int v = step(t, d);
                    if (occ[v] || mem[v].seen != round) continue;
                    for (int d2 = 0; d2 < 4; d2++) {
                        if (mem[v].e[d2] >= 2) continue;
                        int v2 = step(v, d2);
                        if (v2 != t && !occ[v2]) { ways++; break; }
                    }
                }
                if (!ways) split = false;
            }
            if (split && ct.can_split(2)) {
                ct.do_split(2);
                end_turn();
                continue;
            }
        }
        // Swarm units strike first at any enemy head in reach (hunters also pay segments to lunge).
        if (SWARM && !is_queen && !attack && !outnumbered) {
            int reach = (my_len + 3) / 4 + (hunting ? std::max(0, my_len - 2) : 0);
            int best_len = 0;
            for (auto const& e : enemies) { // strike the longest head in reach, and only at even or better material
                std::vector<int> p;
                if (MATERIAL && e.len < my_len && e.id >= 2) continue;
                if (e.len > best_len && path_to(e.pos, reach, p)) { out_dirs = p; attack = true; best_len = e.len; }
            }
        }

        if (!attack) {
            best = Best{};
            std::vector<int> sim = body, dirs, eaten;
            search(sim, dirs, eaten, free_steps, 0, 0);
            if (best.score < -1e5 && my_len > 2) { // nothing safe for free: pay segments to get away
                std::vector<int> sim2 = body, dirs2, eaten2;
                search(sim2, dirs2, eaten2, free_steps, std::min(my_len - 2, 2), 0);
            }
            if (best.score < -1e5 && !is_queen && !enemies.empty()) { // doomed non-queen: take one with us
                std::vector<int> p;
                for (auto const& e : enemies)
                    if (path_to(e.pos, (my_len + 3) / 4 + std::max(0, my_len - 2), p)) { attack = true; break; }
                if (attack) out_dirs = p;
            }
            if (!attack) out_dirs = best.dirs;
        }

        if (out_dirs.empty()) { // boxed in: any edge that is not kelp
            for (int d = 0; d < 4; d++) if (mem[me].e[d] < 2 && occ[step(me, d)] == 0) { out_dirs = {d}; break; }
            if (out_dirs.empty()) out_dirs = {0};
        }
        std::vector<Direction> moves;
        int c = me;
        for (int d : out_dirs) { moves.push_back(Direction(DC[d])); c = step(c, d); trail.push_back(c); }
#ifdef DBG
        if (ct.get_id() < 2) { FILE* f = fopen("dbg.txt", "a"); fprintf(f, "r%d id%d L%d at %d,%d attack%d score%.0f dirs", round, ct.get_id(), my_len, me % W, me / W, (int)attack, best.score);
          for (int d : out_dirs) fputc(DC[d], f); fprintf(f, " body%zu ord%d enemies%zu danger%d pt%d\n", body.size(), (int)body_ordered, enemies.size(), dangerN[me], ct.get_tile(ct.get_position())->get_pearl_time()); fclose(f); }
#endif
        ct.make_moves(moves);
        end_turn();
    }
    return 0;
}
