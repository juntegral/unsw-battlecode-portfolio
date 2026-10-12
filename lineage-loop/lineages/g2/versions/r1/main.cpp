// g2: memory-mapped greedy forager with flood-fill safety, head-threat avoidance,
// favourable head trades and bounded splitting. Own protocol reader (protocol 2/3 tolerant).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>
#include <deque>
#include <map>
#include <string>
#include <algorithm>
#include <functional>

#ifndef SPLITMODE
#define SPLITMODE 0
#endif
#ifndef ALLYDISC
#define ALLYDISC 1
#endif
#ifndef STHR
#define STHR 1
#endif
#ifndef G2DBG
#define G2DBG 0
#endif
static int W, H, N, ME = -1, UNIT_LIMIT = 64;
static char TEAM = 'A';
static int DX[4] = {0, 1, 0, -1}, DY[4] = {-1, 0, 1, 0};
static const char *DC = "NESW";

// edges: kind -1 unknown, 0 open, 1 kelp, 2 portal
static std::vector<int> hKind, hPid, vKind, vPid; // H key = north side of tile, V key = west side
static std::map<int, std::vector<int>> portals;   // pid -> list of (type*N + key)
static std::vector<int> lastSeen, spawnRound, pearlSeen; // pearlSeen: round pearl last seen present, -1 none
static std::vector<char> neverSpawn;
static std::deque<int> hist;

static bool rd(char *buf) { return scanf("%63s", buf) == 1; }
static int rdi() { char b[64]; if (!rd(b)) exit(0); return atoi(b); }
static int dirOf(char c) { return c == 'N' ? 0 : c == 'E' ? 1 : c == 'S' ? 2 : 3; }
static inline int cell(int x, int y) { x %= W; if (x < 0) x += W; y %= H; if (y < 0) y += H; return y * W + x; }

static void setEdge(int type, int key, const char *s) {
    int kind, pid = -1;
    if (s[0] == '.') kind = 0; else if (s[0] == 'w') kind = 1; else { kind = 2; pid = atoi(s); }
    std::vector<int> &K = type ? vKind : hKind, &P = type ? vPid : hPid;
    if (K[key] != kind || P[key] != pid) {
        K[key] = kind; P[key] = pid;
        if (kind == 2) {
            auto &v = portals[pid]; int code = type * N + key;
            if (std::find(v.begin(), v.end(), code) == v.end()) v.push_back(code);
        }
    }
}
// returns dest cell, -1 kelp, -2 unknown portal exit
static int step(int c, int d) {
    int x = c % W, y = c / W, type, key;
    if (d == 0) { type = 0; key = cell(x, y); } else if (d == 2) { type = 0; key = cell(x, y + 1); }
    else if (d == 3) { type = 1; key = cell(x, y); } else { type = 1; key = cell(x + 1, y); }
    int kind = type ? vKind[key] : hKind[key];
    if (kind == 1) return -1;
    if (kind == 2) {
        int pid = type ? vPid[key] : hPid[key];
        auto &v = portals[pid]; int me = type * N + key, other = -1;
        for (int e : v) if (e != me) other = e;
        if (other < 0) return -2;
        int ok = other % N, px = ok % W, py = ok / W;
        if (d == 0) return cell(px, py - 1); if (d == 2) return cell(px, py);
        if (d == 3) return cell(px - 1, py); return cell(px, py);
    }
    return cell(x + DX[d], y + DY[d]);
}

struct Seg { char team; int id, c, dir, head; };

int main() {
    setvbuf(stdout, NULL, _IOFBF, 1 << 16);
    char b[64];
    while (rd(b)) {
        if (!strcmp(b, "ID")) { ME = rdi(); continue; }
        if (!strcmp(b, "TEAM")) { rd(b); TEAM = b[0]; continue; }
        if (!strcmp(b, "MAP")) {
            W = rdi(); H = rdi(); N = W * H;
            hKind.assign(N, -1); hPid.assign(N, -1); vKind.assign(N, -1); vPid.assign(N, -1);
            lastSeen.assign(N, -1000); spawnRound.assign(N, -1); pearlSeen.assign(N, -1); neverSpawn.assign(N, 0);
            continue;
        }
        if (!strcmp(b, "UNIT_LIMIT")) { UNIT_LIMIT = rdi(); continue; }
        if (!strcmp(b, "ENDGAME")) return 0;
        if (strcmp(b, "ROUND")) continue;
        int R = rdi(), L = 2, U = 1, myDir = 0;
        rd(b); myDir = dirOf((rd(b), b[0]));
        rd(b); L = rdi(); rd(b); U = rdi(); rd(b); int nm = rdi();
        for (int i = 0; i < nm; i++) rd(b);
        rd(b);
        int firstTile;
        if (!strcmp(b, "ECHOES")) { for (int i = 0; i < 5; i++) rdi(); firstTile = rdi(); } else firstTile = atoi(b);
        int tx[49], ty[49], tp[49], tt[49];
        for (int i = 0; i < 49; i++) {
            tx[i] = i ? rdi() : firstTile; ty[i] = rdi(); tp[i] = rdi(); tt[i] = rdi();
        }
        rd(b); int nb = rdi();
        std::vector<Seg> segs(nb);
        for (int i = 0; i < nb; i++) {
            rd(b); segs[i].team = b[0]; segs[i].id = rdi(); int x = rdi(), y = rdi();
            segs[i].c = cell(x, y); rd(b); segs[i].dir = dirOf(b[0]); segs[i].head = rdi();
        }
        int hx = tx[24], hy = ty[24], head = cell(hx, hy);
        for (int r = 0; r < 8; r++) for (int c = 0; c < 7; c++) { rd(b); setEdge(0, cell(hx - 3 + c, hy - 3 + r), b); }
        for (int r = 0; r < 7; r++) for (int c = 0; c < 8; c++) { rd(b); setEdge(1, cell(hx - 3 + c, hy - 3 + r), b); }
        std::vector<char> vis(N, 0);
        for (int i = 0; i < 49; i++) {
            int c = cell(tx[i], ty[i]); vis[c] = 1; lastSeen[c] = R;
            if (tt[i] < 0) neverSpawn[c] = 1; else spawnRound[c] = R + tt[i];
            pearlSeen[c] = tp[i] ? R : -1;
        }
        // occupancy
        std::vector<int> occ(N, -1);   // index into segs
        std::map<int, int> lenOf; std::map<int, int> headOf; std::map<int, char> teamOf;
        for (int i = 0; i < nb; i++) {
            occ[segs[i].c] = i; lenOf[segs[i].id]++; teamOf[segs[i].id] = segs[i].team;
            if (segs[i].head) headOf[segs[i].id] = segs[i].c;
        }
        // own body order
        if (hist.empty() || hist[0] != head) {
            bool cont = !hist.empty() && [&] { for (int d = 0; d < 4; d++) if (step(hist[0], d) == head) return true; return false; }();
            if (cont) hist.push_front(head); else hist.clear();
        }
        if (hist.empty()) {
            // rebuild from visible chain
            hist.push_back(head);
            std::vector<char> used(nb, 0);
            for (int k = 1; k < L; k++) {
                int prev = hist.back(), found = -1;
                for (int i = 0; i < nb; i++) if (!used[i] && segs[i].id == ME && !segs[i].head && step(segs[i].c, segs[i].dir) == prev) { found = i; break; }
                if (found < 0) break; used[found] = 1; hist.push_back(segs[found].c);
            }
        }
        while ((int)hist.size() > L + 2) hist.pop_back();
        // release time for own body: segment i released for arrival step k >= L - i + 1
        std::vector<int> rel(N, 0);
        std::vector<char> block(N, 0);
        auto setBody = [&](int Lp) {
            std::fill(rel.begin(), rel.end(), 0); std::fill(block.begin(), block.end(), 0);
            for (int i = 0; i < (int)hist.size() && i < L; i++) {
                if (i < Lp) rel[hist[i]] = std::max(rel[hist[i]], Lp - i + 1); else block[hist[i]] = 1;
            }
            for (int i = 0; i < nb; i++) {
                if (segs[i].id == ME) { if (!rel[segs[i].c] && !block[segs[i].c]) rel[segs[i].c] = Lp + 1; }
                else block[segs[i].c] = 1;
            }
        };
        setBody(L);
        // enemy heads
        std::vector<std::pair<int, int>> enemyHeads; // cell, visible length
        for (auto &kv : headOf) if (teamOf[kv.first] != TEAM) enemyHeads.push_back({kv.second, lenOf[kv.first]});
        std::vector<int> allyHeads;
        for (auto &kv : headOf) if (teamOf[kv.first] == TEAM && kv.first != ME) allyHeads.push_back(kv.second);
        std::vector<int> threat(N, 0); // max enemy len that can reach this tile next move (+1)
        for (auto &e : enemyHeads) for (int d = 0; d < 4; d++) {
            int t = step(e.first, d); if (t >= 0) threat[t] = std::max(threat[t], e.second + 1);
        }
        // sprint reach: enemy of length e can take up to e-1 steps in one turn
        std::vector<int> sthreat(N, 0); // min distance (2..4) an enemy head can reach
        {
            std::vector<int> dd(N, -1), qq; qq.reserve(64);
            for (auto &e : enemyHeads) {
                int lim = std::min(STHR, std::max(1, e.second - 1));
                std::vector<int> touched; qq.clear(); dd[e.first] = 0; qq.push_back(e.first); touched.push_back(e.first);
                for (size_t qi = 0; qi < qq.size(); qi++) {
                    int c = qq[qi]; if (dd[c] >= lim) continue;
                    for (int k = 0; k < 4; k++) {
                        int n = step(c, k); if (n < 0 || dd[n] >= 0 || block[n] || rel[n]) continue;
                        dd[n] = dd[c] + 1; qq.push_back(n); touched.push_back(n);
                        if (dd[n] >= 2 && (!sthreat[n] || dd[n] < sthreat[n])) sthreat[n] = dd[n];
                    }
                }
                for (int c : touched) dd[c] = -1;
            }
        }
        int grow = 0;
        std::vector<char> ehead(N, 0);
        for (auto &e : enemyHeads) ehead[e.first] = 1;
        auto passable = [&](int c, int t) { return !block[c] && (rel[c] == 0 || t >= rel[c] + grow); };
        auto torus = [&](int a, int c) {
            int ax = a % W, ay = a / W, cx = c % W, cy = c / W;
            int dx = abs(ax - cx), dy = abs(ay - cy); return std::min(dx, W - dx) + std::min(dy, H - dy);
        };
        auto pearlValue = [&](int c, int arrive, int &eff) -> double {
            eff = 0;
            if (vis[c]) {
                if (pearlSeen[c] == R) return 1.0;
                if (neverSpawn[c] || spawnRound[c] < 0) return 0;
                int w = spawnRound[c] - arrive; if (w > 0) eff = w; if (w > 12) return 0; return 0.8;
            }
            if (pearlSeen[c] >= 0) return 0.75 * exp(-(R - pearlSeen[c]) / 50.0);
            if (neverSpawn[c] || spawnRound[c] < 0) return 0;
            if (spawnRound[c] <= R) return 0.5 * exp(-(R - spawnRound[c]) / 40.0);
            int w = spawnRound[c] - arrive; if (w > 0) eff = w; if (w > 12) return 0; return 0.55;
        };
        std::vector<int> dist(N), q(N);
        double best = -1e18; int bestD = -1;
        double score[4];
        auto evalDirs = [&](int Lp, double *score) {
        for (int d = 0; d < 4; d++) {
            double s = 0; int dest = step(head, d);
            if (dest == -1) { score[d] = -1e9; continue; }
            if (dest == -2) { score[d] = -5e5; continue; }
            if (d == (myDir + 2) % 4 && Lp > 1 && hist.size() > 1 && dest == hist[1]) { score[d] = -1e9; continue; }
            if (occ[dest] >= 0) {
                Seg &sg = segs[occ[dest]];
                if (sg.id == ME) { if (rel[dest] > 1) { score[d] = -1e9; continue; } }
                else if (sg.head && sg.team != TEAM) {
                    int el = lenOf[sg.id];
                    double v = -2e5 + 1000.0 * (el - Lp);
                    if (el >= Lp + 3 || (U >= 3 && el > Lp)) v = 5e4 + 100.0 * el;
                    score[d] = v; continue;
                } else { score[d] = -1e9; continue; }
            }
            grow = (pearlSeen[dest] == R) ? 1 : 0;
            // threat penalty
            if (threat[dest]) {
                int el = threat[dest] - 1;
                s -= (el <= Lp ? 3000 : 1500);
            } else if (sthreat[dest]) {
                s -= sthreat[dest] == 2 ? 500 : 150;
            }
            // BFS from dest at time 1
            std::fill(dist.begin(), dist.end(), -1);
            int qh = 0, qt = 0; dist[dest] = 0; q[qt++] = dest; int reach = 0, cap = 2 * Lp + 20;
            double food = 0, foodSum = 0, expl = 0;
            while (qh < qt) {
                int c = q[qh++]; int D = dist[c]; reach++;
                int eff; double v = pearlValue(c, R + 1 + D, eff);
                if (c == dest && pearlSeen[c] == R) v = 1.0;
                if (v > 0) {
                    int ed = D + eff;
                    for (auto &e : enemyHeads) if (torus(e.first, c) < D) { v *= 0.4; break; }
                    if (ALLYDISC) for (int a : allyHeads) if (torus(a, c) < D) { v *= 0.5; break; }
                    double val = v / (1.0 + ed);
                    food = std::max(food, val); foodSum += val / (1.0 + 0.3 * ed);
                }
                int stale = std::min(R - lastSeen[c], 60);
                if (stale > 3) expl = std::max(expl, stale / (D + 4.0));
                for (int k = 0; k < 4; k++) {
                    int n = step(c, k); if (n < 0 || dist[n] >= 0) continue;
                    if (!passable(n, D + 2)) continue;
                    if (D == 0 && threat[n] && reach < 0) continue;
                    dist[n] = D + 1; q[qt++] = n;
                }
            }
            // safety flood through known tiles only
            {
                std::fill(dist.begin(), dist.end(), -1);
                int h2 = 0, t2 = 0; dist[dest] = 0; q[t2++] = dest; int kr = 0;
                while (h2 < t2 && kr < 200) {
                    int c = q[h2++]; int D = dist[c]; kr++;
                    for (int k = 0; k < 4; k++) {
                        int n = step(c, k); if (n < 0 || dist[n] >= 0 || lastSeen[n] < 0) continue;
                        if (!passable(n, D + 2)) continue;
                        dist[n] = D + 1; q[t2++] = n;
                    }
                }
                reach = std::min(reach, kr + (kr >= 40 ? 100 : 0));
            }
            int need = std::min(Lp + 3, 40);
            // exact-ish survival: can the snake keep moving for 'depth' more steps?
            {
                int depth = std::min(Lp + 1, 16);
                std::vector<char> onPath(N, 0);
                long budget = 60000;
                std::function<int(int, int)> dfs = [&](int c, int t) -> int {
                    if (t - 1 >= depth) return depth;
                    if (--budget < 0) return depth; // give up: assume fine
                    int bestLen = t - 1;
                    for (int k = 0; k < 4; k++) {
                        int n = step(c, k); if (n < 0 || onPath[n]) continue;
                        if (!passable(n, t + 1) || threat[n] || ehead[n]) continue;
                        onPath[n] = 1; int r2 = dfs(n, t + 1); onPath[n] = 0;
                        if (r2 > bestLen) bestLen = r2;
                        if (bestLen >= depth) break;
                    }
                    return bestLen;
                };
                onPath[dest] = 1;
                int got = dfs(dest, 1);
                if (got < depth) s -= 40000.0 + 2000.0 * (depth - got);
            }
            grow = 0;
            if (reach < need) s -= 20000.0 * (need - reach) / need + (reach < Lp ? 30000 : 0);
            s += 1000.0 * food + 150.0 * foodSum + 8.0 * expl + 0.5 * std::min(reach, cap);
            if (occ[dest] < 0 && pearlSeen[dest] == R) s += 800;
            if (d == myDir) s += 1;
            score[d] = s;
        }
        };
        evalDirs(L, score);
        for (int d = 0; d < 4; d++) if (score[d] > best) { best = score[d]; bestD = d; }
        // split decision
        bool nearEnemy = false;
        for (auto &e : enemyHeads) if (torus(e.first, head) <= 3) nearEnemy = true;
        bool wantSplit = false;
        if (U < UNIT_LIMIT && !nearEnemy && !threat[head]) {
            if (SPLITMODE == 1 && R < 300 && L >= 12 && U < 24) wantSplit = true;
            if (SPLITMODE == 1 && R < 450 && U <= 2 && L >= 8) wantSplit = true;
            if (SPLITMODE == 0 && R < 400 && U == 1 && L >= 10) wantSplit = true;
        }
        // do not split if staying still is unsafe (someone could hit our head) or best move is a pearl
        int escapeK = 0;
        if (best < -30000 && L >= 4 && U < UNIT_LIMIT) {
            int cands[8] = {2, 3, 4, L / 4, L / 2, (3 * L) / 4, L - 3, L - 2};
            double bestEsc = best;
            for (int ci = 0; ci < 8; ci++) {
                int k = cands[ci]; if (k < 2 || L - k < 2) continue;
                setBody(L - k); double sc2[4]; evalDirs(L - k, sc2);
                double m = std::max(std::max(sc2[0], sc2[1]), std::max(sc2[2], sc2[3]));
                if (m > -30000) { escapeK = k; break; }
                if (m > bestEsc + 1) { bestEsc = m; escapeK = k; }
            }
            if (!escapeK) escapeK = L - 2;
            setBody(L);
        }
        if (escapeK) {
            printf("SPLIT %d\nENDTURN\n", escapeK);
            for (int i = 0; i < escapeK && !hist.empty(); i++) hist.pop_back();
            while ((int)hist.size() > L - escapeK) hist.pop_back();
        } else if (wantSplit && best > -1000 && !(bestD >= 0 && pearlSeen[step(head, bestD) >= 0 ? step(head, bestD) : 0] == R)) {
            int k = L / 2;
            printf("SPLIT %d\nENDTURN\n", k);
            for (int i = 0; i < k && !hist.empty(); i++) hist.pop_back();
        } else {
            if (G2DBG) printf("LOG R%d id%d L%d head(%d,%d) sc %.0f %.0f %.0f %.0f -> %c\n", R, ME, L, hx, hy, score[0], score[1], score[2], score[3], DC[bestD<0?myDir:bestD]);
            printf("MOVE %c\nENDTURN\n", DC[bestD < 0 ? myDir : bestD]);
        }
        fflush(stdout);
    }
    return 0;
}
