// g2 r2: map-aware forager. Own protocol reader (protocol 2 input; tolerates ECHOES).
// Known public maps are embedded (mapdb.hpp) and identified from the first 7x7 view;
// unknown maps fall back to learning edges from vision.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <ctime>
#include <vector>
#include <deque>
#include <map>
#include <algorithm>
#include "mapdb.hpp"

#ifndef HUNTED
#define HUNTED 3
#endif
#ifndef HOMEW
#define HOMEW 25.0
#endif
#ifndef CHAMPL
#define CHAMPL 16
#endif
#ifndef NODB
#define NODB 0
#endif
#ifndef SPRINTT
#define SPRINTT 100
#endif
#ifndef UTARGET
#define UTARGET 4
#endif
#ifndef SUICIDE
#define SUICIDE 0
#endif
#ifndef GROWP
#define GROWP 0
#endif
#ifndef OTHREL
#define OTHREL 1
#endif
#ifndef SPLITWHEN
#define SPLITWHEN 0
#endif
#ifndef CORR
#define CORR 2
#endif
#ifndef FARMW
#define FARMW 0.0
#endif
#ifndef G2DBG
#define G2DBG 0
#endif

static int W, H, N, ME = -1, UNIT_LIMIT = 64;
static char TEAM = 'A';
static const int DX[4] = {0, 1, 0, -1}, DY[4] = {-1, 0, 1, 0};
static const char *DC = "NESW";

// edges: kind -1 unknown, 0 open, 1 kelp, 2 portal. H key = north side of tile, V key = west side.
static std::vector<signed char> hKind, vKind;
static std::vector<int> hPid, vPid, hPart, vPart;
static std::map<int, std::vector<int>> pidEdges;
static std::vector<int> nbr;
static bool nbrDirty = true;
static int mapIdx = -1, symT = 0;
static bool mapTried = false;
static std::vector<int> gMin, gMax;             // spawn gap range per tile (-1 unknown)
static std::vector<int> lastSeen, spawnRound, pearlSeen;
static std::vector<char> neverSpawn;
static std::deque<int> hist;

static inline int cellOf(int x, int y) { x %= W; if (x < 0) x += W; y %= H; if (y < 0) y += H; return y * W + x; }

static int rawStep(int c, int d) {
    int x = c % W, y = c / W, type, key;
    if (d == 0) { type = 0; key = c; }
    else if (d == 2) { type = 0; key = cellOf(x, y + 1); }
    else if (d == 3) { type = 1; key = c; }
    else { type = 1; key = cellOf(x + 1, y); }
    int kind = type ? vKind[key] : hKind[key];
    if (kind == 1) return -1;
    if (kind == 2) {
        int other = type ? vPart[key] : hPart[key];
        if (other < 0) return -2;
        int px = other % W, py = other / W;
        if (d == 0) return cellOf(px, py - 1);
        if (d == 3) return cellOf(px - 1, py);
        return other;
    }
    return cellOf(x + DX[d], y + DY[d]);
}
static std::vector<int> deg;
static void rebuildNbr() {
    nbr.assign(N * 4, 0); deg.assign(N, 0);
    for (int c = 0; c < N; c++) for (int d = 0; d < 4; d++) { int n = rawStep(c, d); nbr[c * 4 + d] = n; if (n >= 0) deg[c]++; }
    nbrDirty = false;
}
static inline int step(int c, int d) { return nbr[c * 4 + d]; }

static void pairPortal(int a, int b) {
    int ta = a / N, ka = a % N, tb = b / N, kb = b % N;
    (ta ? vPart : hPart)[ka] = kb;
    (tb ? vPart : hPart)[kb] = ka;
}
static void learnEdge(int type, int key, const char *s) {
    int kind, pid = -1;
    if (s[0] == '.') kind = 0; else if (s[0] == 'w') kind = 1; else { kind = 2; pid = atoi(s); }
    std::vector<signed char> &K = type ? vKind : hKind;
    std::vector<int> &P = type ? vPid : hPid;
    if (K[key] == kind && P[key] == pid) return;
    K[key] = (signed char)kind; P[key] = pid; nbrDirty = true;
    if (kind == 2) {
        std::vector<int> &v = pidEdges[pid];
        int code = type * N + key;
        if (std::find(v.begin(), v.end(), code) == v.end()) v.push_back(code);
        if (v.size() == 2) pairPortal(v[0], v[1]);
    }
}
static void resetKnowledge() {
    hKind.assign(N, -1); vKind.assign(N, -1);
    hPid.assign(N, -1); vPid.assign(N, -1); hPart.assign(N, -1); vPart.assign(N, -1);
    pidEdges.clear(); gMin.assign(N, -1); gMax.assign(N, -1);
    mapIdx = -1; symT = 0; nbrDirty = true;
}
static void loadMap(int m) {
    const MapInfo &M = MAPDB[m];
    for (int i = 0; i < N; i++) {
        char a = M.edges[2 * i], b = M.edges[2 * i + 1];
        hKind[i] = a == '.' ? 0 : a == 'w' ? 1 : 2;
        vKind[i] = b == '.' ? 0 : b == 'w' ? 1 : 2;
        hPart[i] = vPart[i] = hPid[i] = vPid[i] = -1;
    }
    std::map<int, std::vector<int>> byPid;
    const char *p = M.portals;
    while (*p) {
        char *e;
        long t = strtol(p, &e, 10); if (e == p) break; p = e;
        long k = strtol(p, &e, 10); p = e;
        long pid = strtol(p, &e, 10); p = e;
        byPid[(int)pid].push_back((int)(t * N + k));
        while (*p == ' ') p++;
    }
    for (auto &kv : byPid) if (kv.second.size() == 2) pairPortal(kv.second[0], kv.second[1]);
    std::vector<int> cmn, cmx;
    p = M.classes;
    while (*p) {
        char *e;
        long a = strtol(p, &e, 10); if (e == p) break; p = e;
        long b = strtol(p, &e, 10); p = e;
        cmn.push_back((int)a); cmx.push_back((int)b);
        while (*p == ' ') p++;
    }
    for (int i = 0; i < N; i++) {
        char g = M.gap[i];
        if (g == '0') { gMin[i] = gMax[i] = 0; neverSpawn[i] = 1; }
        else { int k = g - 'a'; gMin[i] = cmn[k]; gMax[i] = cmx[k]; }
    }
    mapIdx = m; symT = M.sym; nbrDirty = true;
}
static inline char kindCh(const char *tok) { return tok[0] == '.' ? '.' : tok[0] == 'w' ? 'w' : 'p'; }

static char rdbuf[64];
static bool rd() { return scanf("%63s", rdbuf) == 1; }
static int rdi() { if (!rd()) exit(0); return atoi(rdbuf); }
static int dirOf(char c) { return c == 'N' ? 0 : c == 'E' ? 1 : c == 'S' ? 2 : 3; }

struct Seg { char team; int id, c, dir, head; };

// ---- survival DFS (globals to avoid std::function overhead) ----
static std::vector<int> g_rel, g_orel;
static std::vector<char> g_block, g_onPath, g_avoid, g_pearl;
static int g_growPath;
static int g_grow, g_depth;
static bool g_useAvoid;
static long g_budget, g_turnBudget;
static int g_maxReached;
static int dfs(int c, int t) {
    if (t - 1 > g_maxReached) g_maxReached = t - 1;
    if (t - 1 >= g_depth) return g_depth;
    if (--g_budget < 0 || --g_turnBudget < 0) return g_maxReached;  // out of budget: deepest seen so far
    int best = t - 1;
    for (int k = 0; k < 4; k++) {
        int n = nbr[c * 4 + k];
        if (n < 0 || g_onPath[n] || g_block[n] || (g_useAvoid && g_avoid[n])) continue;
        if (g_rel[n] && t + 1 < g_rel[n] + g_grow + g_growPath) continue;
        if (g_orel[n] && t + 1 < g_orel[n]) continue;
        g_onPath[n] = 1; int ate = g_pearl[n]; g_growPath += ate;
        int r = dfs(n, t + 1);
        g_onPath[n] = 0; g_growPath -= ate;
        if (r > best) best = r;
        if (best >= g_depth) break;
    }
    return best;
}
static long long nowNs() { timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec; }

int main() {
    setvbuf(stdout, NULL, _IOFBF, 1 << 16);
    while (rd()) {
        if (!strcmp(rdbuf, "ID")) { ME = rdi(); continue; }
        if (!strcmp(rdbuf, "TEAM")) { rd(); TEAM = rdbuf[0]; continue; }
        if (!strcmp(rdbuf, "MAP")) {
            W = rdi(); H = rdi(); N = W * H;
            resetKnowledge();
            lastSeen.assign(N, -1000); spawnRound.assign(N, -1); pearlSeen.assign(N, -1); neverSpawn.assign(N, 0);
            g_rel.assign(N, 0); g_orel.assign(N, 0); g_block.assign(N, 0); g_onPath.assign(N, 0); g_avoid.assign(N, 0); g_pearl.assign(N, 0);
            continue;
        }
        if (!strcmp(rdbuf, "UNIT_LIMIT")) { UNIT_LIMIT = rdi(); continue; }
        if (!strcmp(rdbuf, "ENDGAME")) return 0;
        if (strcmp(rdbuf, "ROUND")) continue;
        long long t0 = nowNs();
        static int turnsLived = 0; turnsLived++;
        int R = rdi(), L = 2, U = 1, myDir = 0;
        rd(); rd(); myDir = dirOf(rdbuf[0]);
        rd(); L = rdi(); rd(); U = rdi(); rd(); int nm = rdi();
        std::vector<unsigned long long> msgs;
        for (int i = 0; i < nm; i++) { rd(); msgs.push_back(strtoull(rdbuf, NULL, 10)); }
        rd();
        int firstTile;
        if (!strcmp(rdbuf, "ECHOES")) { for (int i = 0; i < 5; i++) rdi(); firstTile = rdi(); } else firstTile = atoi(rdbuf);
        int tx[49], ty[49], tp[49], tt[49];
        for (int i = 0; i < 49; i++) { tx[i] = i ? rdi() : firstTile; ty[i] = rdi(); tp[i] = rdi(); tt[i] = rdi(); }
        rd(); int nb = rdi();
        std::vector<Seg> segs(nb);
        for (int i = 0; i < nb; i++) {
            rd(); segs[i].team = rdbuf[0]; segs[i].id = rdi(); int x = rdi(), y = rdi();
            segs[i].c = cellOf(x, y); rd(); segs[i].dir = dirOf(rdbuf[0]); segs[i].head = rdi();
        }
        int hx = tx[24], hy = ty[24], head = cellOf(hx, hy);
        static char eh[8][7][12], ev[7][8][12];
        for (int r = 0; r < 8; r++) for (int c = 0; c < 7; c++) { rd(); strncpy(eh[r][c], rdbuf, 11); eh[r][c][11] = 0; }
        for (int r = 0; r < 7; r++) for (int c = 0; c < 8; c++) { rd(); strncpy(ev[r][c], rdbuf, 11); ev[r][c][11] = 0; }
        // ---- map identification / verification ----
        auto viewMatches = [&](const MapInfo &M) {
            if (M.W != W || M.H != H) return false;
            for (int i = 0; i < 49; i++) { int c = cellOf(tx[i], ty[i]); if ((M.gap[c] == '0') != (tt[i] < 0)) return false; }
            for (int r = 0; r < 8; r++) for (int c = 0; c < 7; c++) if (M.edges[2 * cellOf(hx - 3 + c, hy - 3 + r)] != kindCh(eh[r][c])) return false;
            for (int r = 0; r < 7; r++) for (int c = 0; c < 8; c++) if (M.edges[2 * cellOf(hx - 3 + c, hy - 3 + r) + 1] != kindCh(ev[r][c])) return false;
            return true;
        };
        if (!mapTried) {
            mapTried = true;
            for (int m = 0; m < MAPDB_N && !NODB; m++) if (viewMatches(MAPDB[m])) { loadMap(m); break; }
        } else if (mapIdx >= 0 && !viewMatches(MAPDB[mapIdx])) {
            resetKnowledge();
            for (int c = 0; c < N; c++) neverSpawn[c] = 0;
        }
        if (mapIdx < 0) {
            for (int r = 0; r < 8; r++) for (int c = 0; c < 7; c++) learnEdge(0, cellOf(hx - 3 + c, hy - 3 + r), eh[r][c]);
            for (int r = 0; r < 7; r++) for (int c = 0; c < 8; c++) learnEdge(1, cellOf(hx - 3 + c, hy - 3 + r), ev[r][c]);
        }
        if (nbrDirty) rebuildNbr();
        const bool known = mapIdx >= 0;
        static int homeCell = -1;
        if (homeCell < 0) {
            homeCell = head;
            if (known) {
                // circular mean of our team's initial head positions
                double sx = 0, cx = 0, sy = 0, cy = 0; int cnt = 0;
                const char *p = MAPDB[mapIdx].dragons;
                while (*p) {
                    char *e; long tm = strtol(p, &e, 10); if (e == p) break; p = e;
                    long n = strtol(p, &e, 10); p = e;
                    long hx0 = 0, hy0 = 0;
                    for (long j = 0; j < n; j++) { long x = strtol(p, &e, 10); p = e; long y = strtol(p, &e, 10); p = e; if (j == 0) { hx0 = x; hy0 = y; } }
                    while (*p == ';' || *p == ' ') p++;
                    if ((tm == 0) == (TEAM == 'A')) {
                        double ax = 2 * M_PI * hx0 / W, ay = 2 * M_PI * hy0 / H;
                        sx += sin(ax); cx += cos(ax); sy += sin(ay); cy += cos(ay); cnt++;
                    }
                }
                if (cnt) {
                    double ax = atan2(sx, cx), ay = atan2(sy, cy);
                    if (ax < 0) ax += 2 * M_PI; if (ay < 0) ay += 2 * M_PI;
                    homeCell = cellOf((int)lround(ax * W / (2 * M_PI)) % W, (int)lround(ay * H / (2 * M_PI)) % H);
                }
            }
        }
        bool swarmMap = known && !strcmp(MAPDB[mapIdx].name, "Trophy");
        // maps where the champion grows slowly in a safe field and rams are rare: no extra insurance splits
        const bool calmMap = known && !strcmp(MAPDB[mapIdx].name, "Trauma");
        // per-map switches (maps whose starting dragons sit in fountain tubes)
        const bool deadEndMap = known && (!strcmp(MAPDB[mapIdx].name, "Autarky") || !strcmp(MAPDB[mapIdx].name, "Prisoners Dilemma"));
        std::vector<char> vis(N, 0);
        for (int i = 0; i < 49; i++) {
            int c = cellOf(tx[i], ty[i]); vis[c] = 1; lastSeen[c] = R;
            if (tt[i] < 0) neverSpawn[c] = 1; else spawnRound[c] = R + tt[i];
            pearlSeen[c] = tp[i] ? R : -1;
        }
        std::fill(g_pearl.begin(), g_pearl.end(), 0);
        for (int i = 0; i < 49; i++) if (tp[i]) g_pearl[cellOf(tx[i], ty[i])] = 1;
        // ---- occupancy ----
        std::vector<int> occ(N, -1);
        std::map<int, int> lenOf, headOf; std::map<int, char> teamOf;
        for (int i = 0; i < nb; i++) {
            occ[segs[i].c] = i; lenOf[segs[i].id]++; teamOf[segs[i].id] = segs[i].team;
            if (segs[i].head) headOf[segs[i].id] = segs[i].c;
        }
        // ---- own body order (head history) ----
        if (hist.empty() || hist[0] != head) {
            bool cont = false;
            if (!hist.empty()) for (int d = 0; d < 4; d++) if (step(hist[0], d) == head) cont = true;
            if (cont) hist.push_front(head); else hist.clear();
        }
        if (hist.empty() && known && R == 0) {
            // initial bodies are in the map file (head first)
            const char *p = MAPDB[mapIdx].dragons;
            while (*p) {
                char *e; long tm = strtol(p, &e, 10); if (e == p) break; p = e;
                long n = strtol(p, &e, 10); p = e;
                std::vector<int> cells;
                for (long j = 0; j < n; j++) { long x = strtol(p, &e, 10); p = e; long y = strtol(p, &e, 10); p = e; cells.push_back(cellOf((int)x, (int)y)); }
                while (*p == ';' || *p == ' ') p++;
                if ((tm == 0) == (TEAM == 'A') && n == L && !cells.empty() && cells[0] == head) { for (int c : cells) hist.push_back(c); break; }
            }
        }
        if (hist.empty()) {
            for (unsigned long long m : msgs) {
                if ((m >> 28) != 0xAULL || m > 0xFFFFFFFFULL) continue;
                int n = (int)((m >> 24) & 15);
                std::vector<int> cells(1, head); bool ok = n >= 1;
                for (int j = 0; j < n && ok; j++) {
                    int d = (int)((m >> (2 * j)) & 3);
                    int nx = step(cells.back(), d);
                    if (nx < 0) { ok = false; break; }
                    if (vis[nx] && (occ[nx] < 0 || segs[occ[nx]].id != ME)) ok = false;
                    cells.push_back(nx);
                }
                if (ok && (int)cells.size() <= L) { for (int c : cells) hist.push_back(c); if (G2DBG) printf("LOG GOTBODY R%d id%d n%d L%d\n", R, ME, n, L); break; }
            }
        }
        if (hist.empty()) {
            hist.push_back(head);
            std::vector<char> used(nb, 0);
            for (int k = 1; k < L; k++) {
                int prev = hist.back(), found = -1;
                for (int i = 0; i < nb; i++)
                    if (!used[i] && segs[i].id == ME && !segs[i].head && step(segs[i].c, segs[i].dir) == prev) { found = i; break; }
                if (found < 0) break;
                used[found] = 1; hist.push_back(segs[found].c);
            }
        }
        while ((int)hist.size() > L + 2) hist.pop_back();
        if (G2DBG && (int)hist.size() < std::min(L, 6)) {
            printf("LOG REBUILD R%d id%d L%d hist%d head(%d,%d) dir%c own:", R, ME, L, (int)hist.size(), hx, hy, DC[myDir]);
            for (int i = 0; i < nb; i++) if (segs[i].id == ME) printf(" (%d,%d)%c%s", segs[i].c % W, segs[i].c / W, DC[segs[i].dir], segs[i].head ? "H" : "");
            printf("\n");
        }
        std::vector<int> &rel = g_rel;
        std::vector<char> &block = g_block;
        int unresolved = 0;
        auto setBody = [&](int Lp) {
            unresolved = 0;
            std::fill(rel.begin(), rel.end(), 0); std::fill(block.begin(), block.end(), 0);
            for (int i = 0; i < (int)hist.size() && i < L; i++) {
                if (i < Lp) rel[hist[i]] = std::max(rel[hist[i]], Lp - i + 1); else block[hist[i]] = 1;
            }
            for (int i = 0; i < nb; i++) {
                if (segs[i].id == ME) {
                    int c = segs[i].c;
                    if (rel[c] || block[c]) continue;
                    // follow facings toward the head until a segment of known index
                    int cur = i, steps = 0, idx = -1;
                    while (steps < 64) {
                        int nx = step(segs[cur].c, segs[cur].dir);
                        if (nx < 0 || occ[nx] < 0 || segs[occ[nx]].id != ME) break;
                        steps++;
                        int j = -1;
                        for (int t = 0; t < (int)hist.size() && t < L; t++) if (hist[t] == nx) { j = t; break; }
                        if (j >= 0) { idx = j + steps; break; }
                        cur = occ[nx];
                    }
                    if (idx >= 0 && idx < L) { if (idx < Lp) rel[c] = Lp - idx + 1; else block[c] = 1; }
                    else { rel[c] = Lp + 1; unresolved++; }
                }
                else block[segs[i].c] = 1;
            }
            if (OTHREL) {
                std::fill(g_orel.begin(), g_orel.end(), 0);
                for (auto &kv : headOf) {
                    int id = kv.first; if (id == ME) continue;
                    std::vector<int> chain(1, kv.second);
                    while ((int)chain.size() < 200) {
                        int prev = chain.back(), found = -1;
                        for (int k = 0; k < 4 && found < 0; k++) {
                            int nb2 = step(prev, k); if (nb2 < 0 || occ[nb2] < 0) continue;
                            Seg &sg = segs[occ[nb2]];
                            if (sg.id == id && !sg.head && step(nb2, sg.dir) == prev) found = nb2;
                        }
                        if (found < 0) break;
                        chain.push_back(found);
                    }
                    if ((int)chain.size() != lenOf[id]) continue;          // pieces outside the chain
                    int tail = chain.back(); bool proven = true;
                    for (int k = 0; k < 4; k++) { int nb2 = step(tail, k); if (nb2 == -2 || (nb2 >= 0 && !vis[nb2])) proven = false; }
                    if (!proven) continue;
                    int Le = (int)chain.size();
                    for (int i = 1; i < Le; i++) { int c = chain[i]; block[c] = 0; g_orel[c] = Le - i + 2; }
                }
            }
        };
        setBody(L);
        // ---- heads ----
        std::vector<std::pair<int, int>> enemyHeads; std::vector<int> allyHeads;
        for (auto &kv : headOf) {
            if (teamOf[kv.first] != TEAM) enemyHeads.push_back({kv.second, lenOf[kv.first]});
            else if (kv.first != ME) allyHeads.push_back(kv.second);
        }
        // opponent style: several small enemy heads in view at once = ram swarm
        static int huntedUntil = -1;
        {
            int small = 0;
            for (auto &e : enemyHeads) if (e.second <= 5) small++;
            if (HUNTED && small >= HUNTED) huntedUntil = R + 60;
        }
        if (HUNTED && R <= huntedUntil && !deadEndMap && !calmMap) swarmMap = true;
        std::vector<int> threat(N, 0);   // (max enemy len)+1 that can step here next move
        std::vector<char> &avoid = g_avoid;
        std::fill(avoid.begin(), avoid.end(), 0);
        for (int a : allyHeads) for (int d = 0; d < 4; d++) { int t = step(a, d); if (t >= 0) avoid[t] = 1; }
        for (auto &e : enemyHeads) {
            avoid[e.first] = 1;
            for (int d = 0; d < 4; d++) { int t = step(e.first, d); if (t >= 0) { threat[t] = std::max(threat[t], e.second + 1); avoid[t] = 1; } }
        }
        // sprint rams: an enemy of length e can take up to e-1 steps in one turn
        std::vector<signed char> sreach(N, 0);   // min steps (2..4) an enemy head needs to reach a tile
        std::vector<int> sLen(N, 0);
        if (SPRINTT) {
            std::vector<int> dd(N, -1); std::vector<int> qq;
            for (auto &e : enemyHeads) {
                int lim = std::min(4, e.second - 1);
                if (lim < 2) continue;
                qq.clear(); qq.push_back(e.first); dd[e.first] = 0;
                for (size_t qi = 0; qi < qq.size(); qi++) {
                    int c = qq[qi]; if (dd[c] >= lim) continue;
                    for (int k = 0; k < 4; k++) {
                        int n = step(c, k); if (n < 0 || dd[n] >= 0) continue;
                        if (occ[n] >= 0 && !(segs[occ[n]].id == ME && segs[occ[n]].head)) continue;
                        dd[n] = dd[c] + 1; qq.push_back(n);
                        if (dd[n] >= 2 && (!sreach[n] || dd[n] < sreach[n])) { sreach[n] = (signed char)dd[n]; sLen[n] = e.second; }
                    }
                }
                for (int c : qq) dd[c] = -1;
            }
        }
        auto torus = [&](int a, int c) {
            int ax = a % W, ay = a / W, cx = c % W, cy = c / W;
            int dx = abs(ax - cx), dy = abs(ay - cy);
            return std::min(dx, W - dx) + std::min(dy, H - dy);
        };
        // probability-like value of a pearl on tile c when we arrive at round T; eff = extra wait
        auto pearlValue = [&](int c, int T, int &eff) -> double {
            eff = 0;
            if (neverSpawn[c]) return 0;
            if (vis[c]) {
                if (pearlSeen[c] == R) return 1.0;
                if (spawnRound[c] < 0) return 0;
                int w = spawnRound[c] - T;
                if (w > 12) return 0;
                if (w > 0) eff = w;
                return 0.8;
            }
            if (lastSeen[c] >= 0) {
                if (pearlSeen[c] >= 0) return 0.75 * exp(-(T - pearlSeen[c]) / 60.0);
                if (spawnRound[c] < 0) return 0;
                if (spawnRound[c] <= T) return 0.6 * exp(-(T - spawnRound[c]) / 50.0);
                int w = spawnRound[c] - T;
                if (w > 12) return 0;
                eff = w; return 0.55;
            }
            if (known && gMax[c] > 0) {
                double f = (T - gMin[c] + 1.0) / (gMax[c] - gMin[c] + 1.0);
                if (f > 1) f = 1;
                if (f <= 0) return 0;
                return 0.5 * f;
            }
            return 0;
        };
        static double decayTab[64];
        if (decayTab[0] == 0) for (int i = 0; i < 64; i++) decayTab[i] = exp(-i / 15.0);
        std::vector<int> dist(N), q(N);
        double score[4]; bool phys[4]; bool deadEnd[4] = {false, false, false, false};
        g_turnBudget = 250000;
        auto survive = [&](int dest, int Lp, bool useAvoid) {
            int depth = std::min(Lp + 1, 16);
            g_depth = depth; g_budget = 25000; g_useAvoid = useAvoid; g_maxReached = 0; g_growPath = 0;
            if (g_turnBudget < 2000) g_turnBudget = 2000;
            g_onPath[dest] = 1; int got = dfs(dest, 1); g_onPath[dest] = 0;
            if (g_budget < 0 && got < g_maxReached) got = g_maxReached;
            return got - depth;
        };
        auto evalDirs = [&](int Lp, double *score, bool *phys, bool full) {
            for (int d = 0; d < 4; d++) {
                double s = 0; int dest = step(head, d); phys[d] = true;
                if (dest == -1 || (L >= 2 && d == (myDir + 2) % 4)) { score[d] = -1e9; continue; }
                if (dest == -2) { score[d] = -5e5; continue; }
                if (occ[dest] >= 0) {
                    Seg &sg = segs[occ[dest]];
                    if (sg.id == ME) { if (rel[dest] > 1) { score[d] = -1e9; continue; } }
                    else if (sg.head && sg.team != TEAM) {
                        int el = lenOf[sg.id];
                        double v = -2e5 + 1000.0 * (el - Lp);
                        if ((U >= 4 && el >= Lp + 3) || (U >= 2 && el >= 2 * Lp + 4) || (U >= 6 && el > Lp)) v = 5e4 + 100.0 * el;
                        score[d] = v; phys[d] = false; continue;
                    } else if (sg.head) { score[d] = -2e9; continue; }
                    else { score[d] = -1e9; continue; }
                }
                if (block[dest]) { score[d] = -1e9; continue; }
                g_grow = (pearlSeen[dest] == R) ? 1 : 0;
                if (GROWP) {   // assume we will greedily eat nearby visible pearls: tail release is delayed
                    int cnt = 0;
                    for (int i = 0; i < 49; i++) if (tp[i]) { int c = cellOf(tx[i], ty[i]); if (c != dest && torus(c, dest) <= 3) cnt++; }
                    g_grow += (cnt + 1) / 2;
                }
                // 1-wide corridor commitment. A dead end kills the head, but with L>=4 the body escapes by
                // splitting at the end (child = rear, reversed), so a dead end full of pearls is worth entering.
                bool deadEndMove = false;
                if (CORR && deg[dest] <= 2) {
                    int prev = head, cur = dest, len = 1; bool headIn = false;
                    double inside = 0; int eff;
                    inside += pearlSeen[dest] == R ? 1.0 : pearlValue(dest, R + 1, eff);
                    while (deg[cur] == 2 && len < 100) {
                        int nx = -1;
                        for (int k = 0; k < 4; k++) { int n = step(cur, k); if (n >= 0 && n != prev) { nx = n; break; } }
                        if (nx < 0) break;
                        if (occ[nx] >= 0 && segs[occ[nx]].head && segs[occ[nx]].id != ME) headIn = true;
                        prev = cur; cur = nx; len++;
                        inside += pearlValue(cur, R + len, eff);
                    }
                    if (deg[cur] <= 1 && ((CORR & 1) || deadEndMap)) {
                        deadEndMove = true;
                        if (R + len < 499 && full) {
                            if (Lp >= 4 && inside >= 2.0 && !headIn) s -= 600.0 + 60.0 * len;   // enter, eat, split at the end
                            else s -= 40000.0 + 1000.0 * (100 - len);
                        }
                    } else if (deg[cur] > 1 && (CORR & 2)) {
                        double risk = headIn ? 1.0 : 0.0;
                        for (auto &e : enemyHeads) if (torus(e.first, cur) <= len + 1) risk = std::max(risk, 0.6);
                        for (int a : allyHeads) if (torus(a, cur) <= len + 1) risk = std::max(risk, 0.4);
                        if (risk > 0 && full) s -= risk * (3000.0 + 150.0 * Lp);
                    }
                }
                deadEnd[d] = deadEndMove;
                int ps = survive(dest, Lp, false);
                if (ps < 0 && deadEndMove && Lp >= 4) { phys[d] = false; }
                else if (ps < 0) { s -= 40000.0 - 2000.0 * ps; }
                else {
                    phys[d] = false;
                    if (full) { int ds = survive(dest, Lp, true); if (ds < 0) s -= 2500.0 - 250.0 * ds; }
                }
                if (!full) { score[d] = s; g_grow = 0; continue; }
                for (int a : allyHeads) for (int k = 0; k < 4; k++) if (step(a, k) == dest) { s -= 300; break; }
                double vw = U <= 2 ? 3.0 : U <= 4 ? 1.6 : 1.0;
                if (threat[dest]) {
                    int el = threat[dest] - 1;
                    s -= vw * (el <= Lp + 2 ? 3000.0 + 150.0 * Lp : 1500.0);
                } else if (SPRINTT && sreach[dest]) {
                    double f = sreach[dest] == 2 ? 1.0 : sreach[dest] == 3 ? 0.5 : 0.3;
                    s -= vw * f * (sLen[dest] <= Lp + 2 ? 1.0 : 0.5) * (8.0 * SPRINTT + SPRINTT * (double)Lp);
                }
                // BFS from dest at time 1
                std::fill(dist.begin(), dist.end(), -1);
                int qh = 0, qt = 0; dist[dest] = 0; q[qt++] = dest;
                int reach = 0, knownReach = 0; bool tailReach = false;
                double food = 0, foodSum = 0, expl = 0, farm = 0;
                while (qh < qt) {
                    int c = q[qh++]; int D = dist[c]; reach++;
                    if (known || lastSeen[c] >= 0) knownReach++;
                    int eff; double v = pearlValue(c, R + 1 + D, eff);
                    if (v > 0) {
                        int ed = D + eff;
                        for (auto &e : enemyHeads) if (torus(e.first, c) < D) { v *= 0.4; break; }
                        for (int a : allyHeads) if (torus(a, c) < D) { v *= 0.5; break; }
                        double val = v / (1.0 + ed);
                        if (val > food) food = val;
                        foodSum += val / (1.0 + 0.3 * ed);
                    }
                    if (known && gMax[c] > 0 && D < 60) farm += 2.0 / (gMin[c] + gMax[c]) * decayTab[D];
                    if (!known) { int stale = std::min(R - lastSeen[c], 60); if (stale > 3) expl = std::max(expl, stale / (D + 4.0)); }
                    for (int k = 0; k < 4; k++) {
                        int n = step(c, k);
                        if (n < 0 || dist[n] >= 0) continue;
                        if (block[n] || (rel[n] && D + 2 < rel[n] + g_grow) || (g_orel[n] && D + 2 < g_orel[n])) continue;
                        if (rel[n] && rel[n] <= Lp) tailReach = true;
                        dist[n] = D + 1; q[qt++] = n;
                    }
                }
                int need = Lp + 3;
                int r2 = known ? reach : knownReach + (knownReach >= 40 ? 100 : 0);
                if (!tailReach && r2 < need) s -= 20000.0 * (need - r2) / need + (r2 < Lp ? 30000 : 0);
                s += 1000.0 * food + 150.0 * foodSum + FARMW * farm + 8.0 * expl + 0.5 * std::min(reach, 2 * Lp + 20);
                if (pearlSeen[dest] == R) s += 800;
                if (HOMEW > 0 && Lp >= CHAMPL) {   // a champion has little to gain from roaming: stay on our side
                    int hd = torus(dest, homeCell), limit = (W + H) / 6;
                    if (hd > limit) s -= HOMEW * (hd - limit);
                }
                if (d == myDir) s += 1;
                score[d] = s; g_grow = 0;
            }
        };
        evalDirs(L, score, phys, true);
        double best = -1e18; int bestD = -1;
        for (int d = 0; d < 4; d++) if (score[d] > best) { best = score[d]; bestD = d; }
        bool allDoom = phys[0] && phys[1] && phys[2] && phys[3];
        bool stuck = score[0] <= -1e9 && score[1] <= -1e9 && score[2] <= -1e9 && score[3] <= -1e9;
        if (SPLITWHEN == 1 && !stuck) allDoom = false;
        // ---- escape split: only when every move is physically doomed ----
        int splitK = 0;
        bool inDeadEnd = deg[head] <= 2 && known;
        if (allDoom && L >= (inDeadEnd ? 4 : 6) && U < UNIT_LIMIT && (int)hist.size() >= L && unresolved == 0) {
            static const int ks[] = {2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 96, 128};
            for (int k : ks) {
                if (L - k < 2) break;
                if (nowNs() - t0 > 60000000LL) break;
                setBody(L - k);
                double sc2[4]; bool ph2[4];
                evalDirs(L - k, sc2, ph2, false);
                if (!(ph2[0] && ph2[1] && ph2[2] && ph2[3])) { splitK = k; break; }
            }
            if (!splitK) splitK = L - 2;
            setBody(L);
        } else if (stuck && L >= 4 && U < UNIT_LIMIT) {
            bool tailFree = true;   // skip the split if the child would be born stuck as well
            if ((int)hist.size() >= L) {
                tailFree = false;
                int tl = hist[L - 1];
                for (int k = 0; k < 4; k++) { int n = step(tl, k); if (n >= 0 && occ[n] < 0 && !block[n] && !rel[n]) tailFree = true; }
            }
            if (tailFree) splitK = L - 2;   // certain death otherwise: hand the body to a child at our tail
        }
        bool nearEnemy = false;
        for (auto &e : enemyHeads) if (torus(e.first, head) <= 3) nearEnemy = true;
        if (!splitK && U < UNIT_LIMIT && !nearEnemy && !threat[head] && best > -1000) {
            bool eatNow = bestD >= 0 && step(head, bestD) >= 0 && pearlSeen[step(head, bestD)] == R;
            if (!eatNow) {
                if (U == 1 && L >= 6 && R < 450) splitK = std::max(2, std::min(5, L / 3));
                else if (!calmMap && U == 2 && L >= 6 && R < 420) splitK = 3;
                else if (!calmMap && U < UTARGET && L >= 8 && L <= 24 && R < 420) splitK = 3;
                else if (swarmMap && U < 14 && L >= 5 && R < 440) splitK = 2;   // small open map: numbers beat rams
                if (splitK && G2DBG) printf("LOG INSURANCE\n");
            }
        }
        if (SUICIDE && turnsLived == 1 && R > 3 && L <= 3 && U >= SUICIDE && !splitK) {
            // a lizard-split tail fragment: turn it into a pearl instead of clutter
            printf("SPLIT 1\nENDTURN\n"); fflush(stdout); continue;
        }
        if (G2DBG) printf("LOG R%d id%d L%d U%d map%d head(%d,%d) sc %.0f %.0f %.0f %.0f split%d t=%lld\n", R, ME, L, U, mapIdx, hx, hy, score[0], score[1], score[2], score[3], splitK, (nowNs() - t0) / 1000000);
        if (splitK) {
            printf("SPLIT %d\n", splitK);
            if ((int)hist.size() >= L && splitK >= 4 && L - splitK >= 2) {
                // child cells: head = our tail, then toward the split point
                std::vector<int> child;
                for (int j = 0; j < splitK; j++) child.push_back(hist[L - 1 - j]);
                int n = std::min(splitK - 1, 12);
                unsigned long long m = (0xAULL << 28) | ((unsigned long long)n << 24);
                bool ok = true;
                for (int j = 0; j < n && ok; j++) {
                    int dd = -1;
                    for (int k = 0; k < 4; k++) if (step(child[j], k) == child[j + 1]) { dd = k; break; }
                    if (dd < 0) ok = false; else m |= (unsigned long long)dd << (2 * j);
                }
                if (ok) {
                    std::vector<char> isChild(N, 0), isBody(N, 0);
                    for (int c : child) isChild[c] = 1;
                    for (int i = 0; i < L - splitK; i++) isBody[hist[i]] = 1;
                    int newTail = hist[L - splitK - 1], preTail = hist[L - splitK - 2];
                    int tailDir = -1;
                    for (int k = 0; k < 4; k++) if (step(preTail, k) == newTail) tailDir = k;
                    for (int D = 0; D < 4; D++) {
                        int cur, dir = D;
                        if (D == (myDir + 2) % 4) { if (tailDir < 0) continue; cur = newTail; dir = tailDir; } else cur = head;
                        int hit = -1;
                        for (int t = 0; t < W + H; t++) {
                            cur = step(cur, dir);
                            if (cur < 0) break;
                            if (isChild[cur]) { hit = 1; break; }
                            if (isBody[cur] || occ[cur] >= 0) { hit = 0; break; }
                        }
                        if (hit == 1) { printf("SONAR %c %llu\n", DC[D], m); break; }
                    }
                }
            }
            printf("ENDTURN\n");
            while ((int)hist.size() > L - splitK) hist.pop_back();
        } else {
            printf("MOVE %c\nENDTURN\n", DC[bestD < 0 ? myDir : bestD]);
        }
        fflush(stdout);
    }
    return 0;
}
