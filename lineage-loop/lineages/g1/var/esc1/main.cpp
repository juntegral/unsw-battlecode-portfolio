#define ESC_MD 1
// g1: memory + time-aware flood-fill snake bot for UNSW Battlecode (protocol 3).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>
#include <deque>
#include <string>
#include <algorithm>
#include <ctime>
#include "maps_data.hpp"

#ifndef FOODSUM
#define FOODSUM 25.0
#endif
#ifndef FOODMAX
#define FOODMAX 400.0
#endif
#ifndef ESC_MD
#define ESC_MD 100000
#endif
#ifndef MIRROR
#define MIRROR 1
#endif
#ifndef BLIND
#define BLIND 150.0
#endif
#ifndef SLACK
#define SLACK 2
#endif
#ifndef SPLIT_AT
#define SPLIT_AT 40
#endif
#ifndef SPLIT_END
#define SPLIT_END 380
#endif
#ifndef MAX_UNITS
#define MAX_UNITS 12
#endif

static const int DX[4] = {0, 1, 0, -1}; // N E S W
static const int DY[4] = {-1, 0, 1, 0};
static const char DC[4] = {'N', 'E', 'S', 'W'};
static const int INF = 1 << 28;

static int W, H, N, MYID, MYTEAM, ULIMIT = 64;

// ---------- token reader ----------
static char tokbuf[256];
static bool tok() {
    int c = getchar();
    while (c != EOF && (c == ' ' || c == '\n' || c == '\r' || c == '\t')) c = getchar();
    if (c == EOF) { tokbuf[0] = 0; return false; }
    int n = 0;
    while (c != EOF && !(c == ' ' || c == '\n' || c == '\r' || c == '\t')) {
        if (n < 255) tokbuf[n++] = (char)c;
        c = getchar();
    }
    tokbuf[n] = 0;
    return true;
}
static long long tnum() { tok(); return atoll(tokbuf); }
static int dirOf(char c) { return c == 'N' ? 0 : c == 'E' ? 1 : c == 'S' ? 2 : 3; }

// ---------- map memory ----------
// edges: -2 unknown, -1 open, -3 kelp, >=0 portal id
static std::vector<int> hE, vE;           // hE[c]: north edge of c; vE[c]: west edge of c
static std::vector<int> seenR, ptime, pearlSeen, ptSeenR;
static int symType = 0; // 0 unknown, 1 flip x, 2 flip y, 3 rotate
struct PortalRef { int type, cell; };     // type 0 = horizontal (north edge), 1 = vertical (west edge)
static std::vector<std::vector<PortalRef>> portals;

static inline int cid(int x, int y) { x %= W; if (x < 0) x += W; y %= H; if (y < 0) y += H; return y * W + x; }
static inline int cx(int c) { return c % W; }
static inline int cy(int c) { return c / W; }
static inline int nb(int c, int d) { return cid(cx(c) + DX[d], cy(c) + DY[d]); }

static int edgeVal(int c, int d) {
    if (d == 0) return hE[c];
    if (d == 2) return hE[nb(c, 2)];
    if (d == 3) return vE[c];
    return vE[nb(c, 1)];
}
static void addPortal(int id, int type, int cell) {
    if (id < 0 || id > 100000) return;
    if ((int)portals.size() <= id) portals.resize(id + 1);
    for (auto &p : portals[id]) if (p.type == type && p.cell == cell) return;
    portals[id].push_back({type, cell});
}
// destination cell stepping from c in dir d; -1 kelp, -2 unknown portal exit
static int stepTo(int c, int d) {
    int e = edgeVal(c, d);
    if (e == -3) return -1;
    if (e >= 0) {
        int type = (d == 0 || d == 2) ? 0 : 1;
        int self = (d == 0) ? c : (d == 2) ? nb(c, 2) : (d == 3) ? c : nb(c, 1);
        if (e >= (int)portals.size()) return -2;
        for (auto &p : portals[e]) {
            if (p.type != type || p.cell == self) continue;
            // emerge on the far side of the partner edge, still moving d
            if (d == 2 || d == 1) return p.cell;
            return nb(p.cell, d);
        }
        return -2;
    }
    return nb(c, d);
}


// ---------- cheap math + budget ----------
static double POW82[8192], POW90[8192], EXPT[4001];
static void initTables() {
    POW82[0] = POW90[0] = 1;
    for (int i = 1; i < 8192; i++) { POW82[i] = POW82[i - 1] * 0.82; POW90[i] = POW90[i - 1] * 0.9; }
    for (int i = 0; i <= 4000; i++) EXPT[i] = std::exp(-i / 200.0);
}
static inline double expNeg(double x) { // exp(-x), x >= 0
    if (x <= 0) return 1.0;
    int i = (int)(x * 200.0);
    return i >= 4000 ? 0.0 : EXPT[i];
}
static inline double pw82(int d) { return d < 8192 ? POW82[d] : 0.0; }
static inline double pw90(int d) { return d < 8192 ? POW90[d] : 0.0; }
static long long nowNs() { timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec; }
static long long turnStart;
static inline long long spent() { return nowNs() - turnStart; } // ~= CPU points in the judge

// ---------- known public maps ----------
static std::vector<int> kmAlive;       // candidate indices
static int kmApplied = -1;
static std::vector<double> tileRate;   // spawn attempts per round, -1 unknown
static inline int mirrorCell(int c) {
    int x = c % W, y = c / W;
    if (symType == 1) x = W - 1 - x; else if (symType == 2) y = H - 1 - y; else if (symType == 3) { x = W - 1 - x; y = H - 1 - y; } else return -1;
    return y * W + x;
}
static int kmKind(char ch) { return ch == 'w' ? -3 : ch == 'p' ? 0 : -1; }
static void kmInit() {
    tileRate.assign(N, -1);
    for (int i = 0; i < NUM_KNOWN_MAPS; i++) if (KNOWN_MAPS[i].w == W && KNOWN_MAPS[i].h == H) kmAlive.push_back(i);
}
static std::vector<int> obsPortalH, obsPortalV; // observed cells with portals (to compare ids)
static void kmCheck() {
    if (kmApplied >= 0 || kmAlive.empty()) return;
    std::vector<int> keep;
    for (int i : kmAlive) {
        const KnownMap &m = KNOWN_MAPS[i];
        bool ok = true;
        for (int c = 0; c < N && ok; c++) {
            if (hE[c] != -2) { int k = kmKind(m.he[c]); int o = hE[c] >= 0 ? 0 : hE[c]; if (k != o) ok = false; }
            if (vE[c] != -2) { int k = kmKind(m.ve[c]); int o = vE[c] >= 0 ? 0 : vE[c]; if (k != o) ok = false; }
        }
        if (ok) keep.push_back(i);
    }
    kmAlive = keep;
    if (kmAlive.size() != 1) return;
    const KnownMap &m = KNOWN_MAPS[kmAlive[0]];
    // portal ids: file order
    std::vector<int> hid(N, -1), vid(N, -1);
    int a = 0, b = 0;
    for (int c = 0; c < N; c++) { if (m.he[c] == 'p') hid[c] = m.hp[a++]; if (m.ve[c] == 'p') vid[c] = m.vp[b++]; }
    bool idsMatch = true;
    for (int c = 0; c < N; c++) {
        if (hE[c] >= 0 && hE[c] != hid[c]) idsMatch = false;
        if (vE[c] >= 0 && vE[c] != vid[c]) idsMatch = false;
    }
    kmApplied = kmAlive[0];
    symType = !strcmp(m.sym, "y") ? 1 : !strcmp(m.sym, "x") ? 2 : !strcmp(m.sym, "xy") ? 3 : 0;
    for (int c = 0; c < N; c++) {
        if (hE[c] == -2) { int k = kmKind(m.he[c]); if (k == 0) { if (idsMatch) { hE[c] = hid[c]; addPortal(hid[c], 0, c); } } else hE[c] = k; }
        if (vE[c] == -2) { int k = kmKind(m.ve[c]); if (k == 0) { if (idsMatch) { vE[c] = vid[c]; addPortal(vid[c], 1, c); } } else vE[c] = k; }
        char t = m.tiles[c];
        tileRate[c] = (t == '0') ? 0.0 : 1.0 / std::pow(2.0, (t - 'a') / 3.0);
    }
}

// ---------- per-turn state ----------
struct Seg { int team, id, cell, dir, head; };
static int R, MYDIR, LEN, UCOUNT;
static std::vector<Seg> segs;
static std::vector<int> occ;        // segment index occupying cell or -1
static std::vector<int> visible;    // 1 if in window this turn
static std::vector<int> pearlNow;
static std::deque<int> trail;       // my body, head first (may be shorter than LEN)

struct Dragon { int team, id, len; bool full; std::vector<int> chain; };
static std::vector<Dragon> drags;

static void readInit() {
    int got = 0;
    while (got < 4 && tok()) {
        if (!strcmp(tokbuf, "ID")) { MYID = (int)tnum(); got++; }
        else if (!strcmp(tokbuf, "TEAM")) { tok(); MYTEAM = tokbuf[0] == 'A' ? 0 : 1; got++; }
        else if (!strcmp(tokbuf, "MAP")) { W = (int)tnum(); H = (int)tnum(); got++; }
        else if (!strcmp(tokbuf, "UNIT_LIMIT")) { ULIMIT = (int)tnum(); got++; }
    }
    N = W * H;
    hE.assign(N, -2); vE.assign(N, -2);
    seenR.assign(N, -1000); ptime.assign(N, -1); pearlSeen.assign(N, 0); ptSeenR.assign(N, -1000);
    occ.assign(N, -1); visible.assign(N, 0); pearlNow.assign(N, 0);
}

static int parseEdgeTok() {
    tok();
    if (tokbuf[0] == '.') return -1;
    if (tokbuf[0] == 'w') return -3;
    return atoi(tokbuf);
}

static bool readRound() {
    if (!tok()) return false;
    while (strcmp(tokbuf, "ROUND")) { if (!strcmp(tokbuf, "ENDGAME")) return false; if (!tok()) return false; }
    R = (int)tnum();
    tok(); tok(); MYDIR = dirOf(tokbuf[0]);
    tok(); LEN = (int)tnum();
    tok(); UCOUNT = (int)tnum();
    tok(); int nm = (int)tnum();
    for (int i = 0; i < nm; i++) tok();
    tok();
    long long first;
    if (!strcmp(tokbuf, "ECHOES")) { for (int i = 0; i < 5; i++) tnum(); first = tnum(); }
    else first = atoll(tokbuf);
    std::fill(visible.begin(), visible.end(), 0);
    std::fill(occ.begin(), occ.end(), -1);
    std::fill(pearlNow.begin(), pearlNow.end(), 0);
    int wcell[7][7];
    for (int i = 0; i < 49; i++) {
        int x = (i == 0) ? (int)first : (int)tnum();
        int y = (int)tnum();
        int hp = (int)tnum();
        int pt = (int)tnum();
        int c = cid(x, y);
        wcell[i / 7][i % 7] = c;
        visible[c] = 1; seenR[c] = R; ptSeenR[c] = R; ptime[c] = pt; pearlSeen[c] = hp; pearlNow[c] = hp;
    }
    tok(); // DRAGON_BODIES
    int k = (int)tnum();
    segs.clear();
    for (int i = 0; i < k; i++) {
        Seg s; tok(); s.team = tokbuf[0] == 'A' ? 0 : 1;
        s.id = (int)tnum(); int x = (int)tnum(), y = (int)tnum(); tok(); s.dir = dirOf(tokbuf[0]); s.head = (int)tnum();
        s.cell = cid(x, y);
        occ[s.cell] = (int)segs.size();
        segs.push_back(s);
    }
    for (int i = 0; i < 8; i++) for (int j = 0; j < 7; j++) {
        int v = parseEdgeTok();
        int c = (i < 7) ? wcell[i][j] : nb(wcell[6][j], 2);
        hE[c] = v; if (v >= 0) addPortal(v, 0, c);
    }
    for (int i = 0; i < 7; i++) for (int j = 0; j < 8; j++) {
        int v = parseEdgeTok();
        int c = (j < 7) ? wcell[i][j] : nb(wcell[i][6], 1);
        vE[c] = v; if (v >= 0) addPortal(v, 1, c);
    }
    return true;
}

static int myHead = -1;
static int chebToHead(int c) {
    int dx = std::abs(cx(c) - cx(myHead)); dx = std::min(dx, W - dx);
    int dy = std::abs(cy(c) - cy(myHead)); dy = std::min(dy, H - dy);
    return std::max(dx, dy);
}

static void buildDragons() {
    drags.clear();
    myHead = -1;
    for (auto &s : segs) if (s.head && s.id == MYID) myHead = s.cell;
    std::vector<int> used(segs.size(), 0);
    for (size_t i = 0; i < segs.size(); i++) if (segs[i].head) {
        Dragon d; d.team = segs[i].team; d.id = segs[i].id; d.full = false;
        d.chain.push_back(segs[i].cell); used[i] = 1;
        int cur = segs[i].cell;
        while (true) {
            int found = -1;
            for (size_t j = 0; j < segs.size(); j++) {
                if (used[j] || segs[j].id != d.id || segs[j].head) continue;
                if (stepTo(segs[j].cell, segs[j].dir) == cur) { found = (int)j; break; }
            }
            if (found < 0) {
                int cnt = 0, cand = -1;
                for (size_t j = 0; j < segs.size(); j++) {
                    if (used[j] || segs[j].id != d.id || segs[j].head) continue;
                    for (int k = 0; k < 4; k++) if (nb(segs[j].cell, k) == cur) { cnt++; cand = (int)j; break; }
                }
                if (cnt == 1) found = cand;
            }
            if (found < 0) break;
            used[found] = 1; cur = segs[found].cell; d.chain.push_back(cur);
        }
        d.len = (int)d.chain.size();
        if (d.id == MYID) { d.len = LEN; d.full = true; }
        else d.full = myHead >= 0 && chebToHead(d.chain.back()) < 3;
        drags.push_back(d);
    }
    // orphan body segments (chain broken, e.g. via unknown portal) are static obstacles via occ
}

// ---------- evaluation ----------
static std::vector<int> dist, bfsq, enemyDist, fbuf;
struct Threat { int id, len, reach; std::vector<std::pair<int,int>> cells; };
static std::vector<Threat> threats;

// time-aware BFS from head; returns reachable count, fills dist, sets gMaxDist
static int gMaxDist;
static std::vector<int> eatc;
static inline int pearlGuess(int c) { return visible[c] ? pearlNow[c] : pearlSeen[c]; }
// f[t] applies to own-body cells (delayed by pearls eaten on the way) when ownMask[t]
static std::vector<char> ownMask;
static int bfs(int start, const std::vector<int> &f, std::vector<int> &dd, int cap) {
    std::fill(dd.begin(), dd.end(), INF);
    int qh = 0, qt = 0; bfsq[qt++] = start; dd[start] = 0; int cnt = 0; gMaxDist = 0;
    eatc[start] = 0;
    while (qh < qt) {
        int c = bfsq[qh++]; cnt++;
        if (dd[c] > gMaxDist) gMaxDist = dd[c];
        if (cnt >= cap) break;
        int nd = dd[c] + 1;
        for (int d = 0; d < 4; d++) {
            if (nd <= 3 && edgeVal(c, d) == -2) continue; // unknown edges near the head are not trusted
            int t = stepTo(c, d);
            if (t < 0 || dd[t] != INF) continue;
            if (f[t] + (ownMask[t] ? eatc[c] : 0) > nd) continue;
            dd[t] = nd; eatc[t] = eatc[c] + pearlGuess(t); bfsq[qt++] = t;
        }
    }
    return cnt;
}

static double cellValue(int c, int d) {
    double rate = tileRate[c];
    if (seenR[c] < 0) {
        double u = (rate < 0) ? 0.10 : 0.55 * (1.0 - expNeg(rate * (R + d + 20)));
#if MIRROR
        if (ptSeenR[c] >= 0 && ptime[c] >= 0) {
            int sp = ptSeenR[c] + ptime[c];
            if (R + d >= sp) u = std::max(u, 0.6 * expNeg(std::max(0, R - sp) / 200.0));
            else u *= 0.5;
        } else if (ptSeenR[c] >= 0) u = 0;
#endif
        return u;
    }
    double v = 0;
    if (visible[c]) {
        if (pearlNow[c]) v = 1.0;
        else if (ptime[c] >= 0 && ptime[c] <= d) v = 0.7;
    } else {
        int age = R - seenR[c];
        if (pearlSeen[c]) v = 0.85 * expNeg(age / 90.0);
        if (ptime[c] >= 0) {
            int sp = seenR[c] + ptime[c];
            if (R + d >= sp) v = std::max(v, 0.6 * expNeg(std::max(0, R - sp) / 200.0));
            else if (rate < 0 && age > 40) v = std::max(v, 0.2);
        }
    }
    return v;
}

struct Sim { std::deque<int> body; bool dead; int eaten; int killHead; int steps; int len; int blind; };

static Sim simulate(const std::vector<int> &mv) {
    Sim s; s.body = trail; s.dead = false; s.eaten = 0; s.killHead = -1; s.steps = (int)mv.size(); s.blind = 0;
    int len = LEN;
    std::vector<int> ate;
    for (size_t i = 0; i < mv.size(); i++) {
        if (i > 0 && len <= 2) { s.dead = true; break; }
        int h = s.body[0];
        int t = stepTo(h, mv[i]);
        if (t < 0) { s.dead = true; break; }
        bool self = false;
        for (int k = 0; k < (int)s.body.size() && k < len; k++) if (s.body[k] == t) { self = true; break; }
        if (self) { s.dead = true; break; }
        int o = occ[t];
        if (o >= 0 && segs[o].id == MYID && (int)trail.size() < LEN) { s.dead = true; break; } // unknown part of my body
        if (o >= 0 && segs[o].id != MYID) {
            if (segs[o].head && segs[o].team != MYTEAM) s.killHead = segs[o].id;
            s.dead = true; break;
        }
        if (!visible[t]) s.blind++;
        bool eat = pearlNow[t] && std::find(ate.begin(), ate.end(), t) == ate.end();
        s.body.push_front(t);
        if (eat) { s.eaten++; len++; ate.push_back(t); }
        while ((int)s.body.size() > len) s.body.pop_back();
        if (i > 0) { len--; while ((int)s.body.size() > len) s.body.pop_back(); }
    }
    s.len = len;
    return s;
}

static int dragonLen(int id) { for (auto &d : drags) if (d.id == id) return d.len; return 3; }

static int gLastMd, gLastArea, gBestCell, gBestD; static double gBestV; static bool gLastSurv;
static double evaluate(const std::vector<int> &mv, bool &fatal) {
    Sim s = simulate(mv);
    fatal = false;
    if (s.dead) {
        if (s.killHead >= 0) {
            int eL = dragonLen(s.killHead);
            if (UCOUNT <= 2) { fatal = true; return -1e7; }
            bool good = eL >= 2 * LEN + 3 || (R > 460 && eL >= LEN + 6);
            double tv = good ? 40.0 * eL - 30.0 * LEN - 20.0 * (s.steps - 1) : -1.0;
            return tv > 0 ? 3000 + tv : -5e5 + tv;
        }
        fatal = true; return -1e7;
    }
    int myLen = s.len;
    double score = 0;
    int h = s.body[0];
    std::vector<int> &f = fbuf;
    std::fill(f.begin(), f.end(), 0);
    for (auto &d : drags) {
        if (d.id == MYID) continue;
        for (int k = 0; k < (int)d.chain.size(); k++) {
            int c = d.chain[k];
            f[c] = (k == 0 || !d.full) ? INF : (d.len - k + 1);
        }
    }
    for (auto &sg : segs) if (f[sg.cell] == 0) f[sg.cell] = (sg.id != MYID) ? INF : LEN + 1 + SLACK; // orphan / unknown own segments
    std::fill(ownMask.begin(), ownMask.end(), 0);
    for (int k = 1; k < (int)s.body.size(); k++) { f[s.body[k]] = std::max(f[s.body[k]], myLen - k + 1 + SLACK); ownMask[s.body[k]] = 1; }
    f[h] = 0;
    int need = std::min(myLen + 1, 60);
    int area = bfs(h, f, dist, N + 1);
    int md = gMaxDist; gLastMd = md; gLastArea = area;
    bool roomy = area >= 2 * myLen + 30;
    gLastSurv = !(md < need && !roomy);
    if (!gLastSurv) score -= 6000 + 200.0 * (need - md);
    score += 2.0 * std::min(md, need) + 0.5 * std::min(area, 3 * myLen + 30);

    // food (discounted value over reachable cells)
    double food = 0, bestT = 0;
    int nq = std::min(area, N);
    for (int qi = 0; qi < nq; qi++) {
        int c = bfsq[qi];
        int d = dist[c];
        double v = cellValue(c, d);
        if (v <= 0) continue;
        int ed = enemyDist[c];
        if (ed < d) v *= 0.35; else if (ed == d) v *= 0.6;
        food += v * pw82(d);
        double tv = v * pw90(d);
        if (tv > bestT) { bestT = tv; gBestCell = c; gBestV = v; gBestD = d; }
    }
    // if the BFS stopped at the cap, the rest of the map is still reachable; small constant
    score += FOODSUM * food + FOODMAX * bestT + 150.0 * s.eaten;

    // head risk: allies adjacent (mild), enemies that can reach my new head this turn (sprint included)
    for (auto &d : drags) {
        if (d.id == MYID || d.team != MYTEAM) continue;
        for (int k = 0; k < 4; k++) if (stepTo(d.chain[0], k) == h) { score -= 40; break; }
    }
    for (auto &t : threats) {
        int D = INF;
        for (auto &pr : t.cells) if (pr.first == h) { D = pr.second; break; }
        if (D == INF || D == 0) continue;
        double base = (myLen > t.len) ? 1800 + 25.0 * myLen : (myLen == t.len ? 1100 : 600);
        double w = D == 1 ? 1.0 : D == 2 ? 0.7 : D == 3 ? 0.4 : 0.25;
        score -= base * w;
    }
    // squeeze enemies: count their safe moves given my new body
    for (auto &d : drags) {
        if (d.id == MYID) continue;
        int eh = d.chain[0];
        int safe = 0, trade = 0;
        for (int k = 0; k < 4; k++) {
            int t = stepTo(eh, k);
            if (t < 0) continue;
            if (t == h) { trade++; continue; }
            bool blocked = false;
            for (int q = 1; q < (int)s.body.size(); q++) if (s.body[q] == t) { blocked = true; break; }
            if (!blocked && occ[t] >= 0 && segs[occ[t]].id != MYID) blocked = true;
            if (!blocked) safe++;
        }
        if (d.team == MYTEAM) {
            if (safe == 0) score -= 2500 + 30.0 * d.len;
            else if (safe == 1) score -= 80;
            continue;
        }
        if (safe == 0) score += 500 + 40.0 * d.len - (trade ? 150 : 0);
        else if (safe == 1) score += 60 + 3.0 * d.len;
    }
    score -= 1500.0 * (s.steps - 1);
    score -= BLIND * s.blind;
    return score;
}


// survival check for an arbitrary body (head first) of length len, as if it moves next
static bool survives(const std::deque<int> &body, int len, int excludeFrom, int &mdOut) {
    std::vector<int> &f = fbuf;
    std::fill(f.begin(), f.end(), 0);
    for (auto &d : drags) {
        if (d.id == MYID) continue;
        for (int k = 0; k < (int)d.chain.size(); k++) {
            int c = d.chain[k];
            f[c] = (k == 0 || !d.full) ? INF : (d.len - k + 1);
        }
    }
    for (auto &sg : segs) if (sg.id != MYID && f[sg.cell] == 0) f[sg.cell] = INF;
    std::fill(ownMask.begin(), ownMask.end(), 0);
    // cells of my current body not in this body: the other part of the split (static for a while)
    for (int k = 0; k < (int)trail.size(); k++) f[trail[k]] = INF;
    for (int k = 0; k < (int)body.size(); k++) f[body[k]] = 0;
    for (int k = 1; k < (int)body.size(); k++) { f[body[k]] = len - k + 1 + SLACK; ownMask[body[k]] = 1; }
    // the other part frees too, but slowly; approximate as static except its tail region
    (void)excludeFrom;
    int area = bfs(body[0], f, dist, N + 1);
    mdOut = gMaxDist;
    int need = std::min(len + 1, 60);
    return gMaxDist >= need || area >= 2 * len + 30;
}

static void updateTrail() {
    const Dragon *me = nullptr;
    for (auto &d : drags) if (d.id == MYID) me = &d;
    if (!me) return;
    std::deque<int> nt(me->chain.begin(), me->chain.end());
    if (!trail.empty()) {
        int last = me->chain.back();
        int pos = -1;
        for (int i = 0; i < (int)trail.size(); i++) if (trail[i] == last) { pos = i; break; }
        if (pos >= 0) for (int i = pos + 1; i < (int)trail.size() && (int)nt.size() < LEN; i++) nt.push_back(trail[i]);
    }
    while ((int)nt.size() > LEN) nt.pop_back();
    trail = nt;
}

static void applyMirror() {
    if (!symType) return;
    for (int c = 0; c < N; c++) if (visible[c]) {
        int m = mirrorCell(c);
        if (m >= 0 && !visible[m] && seenR[m] < 0) { ptSeenR[m] = R; ptime[m] = ptime[c]; }
    }
}
int main() {
    setvbuf(stdout, nullptr, _IOFBF, 1 << 16);
    readInit();
    kmInit();
    initTables();
    dist.assign(N, INF); bfsq.assign(N + 8, 0); enemyDist.assign(N, INF); fbuf.assign(N, 0); eatc.assign(N, 0); ownMask.assign(N, 0);
    while (readRound()) {
        turnStart = nowNs();
        kmCheck();
        applyMirror();
        buildDragons();
        updateTrail();
        if (myHead < 0 || trail.empty()) { printf("MOVE %c\nPROTOCOL 3\nENDTURN\n", DC[MYDIR]); fflush(stdout); continue; }

        // enemy distance field (multi-source BFS, static obstacles only)
        std::fill(enemyDist.begin(), enemyDist.end(), INF);
        {
            int qh = 0, qt = 0;
            for (auto &d : drags) if (d.team != MYTEAM) { enemyDist[d.chain[0]] = 0; bfsq[qt++] = d.chain[0]; }
            while (qh < qt) {
                int c = bfsq[qh++];
                if (enemyDist[c] > 12) continue;
                for (int k = 0; k < 4; k++) {
                    int t = stepTo(c, k);
                    if (t < 0 || enemyDist[t] != INF) continue;
                    if (occ[t] >= 0 && !segs[occ[t]].head) continue;
                    enemyDist[t] = enemyDist[c] + 1; bfsq[qt++] = t;
                }
            }
        }

        // per-enemy sprint reach (kamikaze heads can move len-1 steps in one turn)
        threats.clear();
        for (auto &d : drags) if (d.team != MYTEAM && chebToHead(d.chain[0]) <= 6) {
            Threat t; t.id = d.id; t.len = d.full ? d.len : std::max(d.len, 6); t.reach = std::min(4, std::max(1, t.len - 1));
            std::vector<std::pair<int,int>> q; q.push_back({d.chain[0], 0});
            for (size_t qi = 0; qi < q.size(); qi++) {
                int c = q[qi].first, dd = q[qi].second;
                if (dd >= t.reach) continue;
                for (int k = 0; k < 4; k++) {
                    int nx = stepTo(c, k);
                    if (nx < 0) continue;
                    bool seen = false;
                    for (auto &pr : q) if (pr.first == nx) { seen = true; break; }
                    if (seen) continue;
                    q.push_back({nx, dd + 1});
                }
            }
            // keep cells; bodies block the path except we allow reaching into my head
            t.cells = q;
            threats.push_back(t);
        }
        std::vector<int> best; double bestS = -1e18;
        std::vector<std::vector<int>> cands;
        for (int a = 0; a < 4; a++) cands.push_back({a});
        bool anySurv = false; int bestMdAll = -1;
        auto runCands = [&](size_t from) {
            for (size_t i = from; i < cands.size(); i++) {
                if (i >= 4 && spent() > 55000000LL) break;
                bool fatal;
                gLastSurv = false;
                double sc = evaluate(cands[i], fatal);
                if (!fatal && gLastSurv) anySurv = true;
                if (!fatal && gLastMd > bestMdAll) bestMdAll = gLastMd;
                if (sc > bestS) { bestS = sc; best = cands[i]; }
            }
        };
        runCands(0);
        // sprints only matter for escapes, threats and head trades
        bool enemyAdj = false;
        for (auto &d : drags) if (d.team != MYTEAM && chebToHead(d.chain[0]) <= 2) enemyAdj = true;
        if (LEN >= 4 && (!anySurv || !threats.empty() || enemyAdj || bestS < 0)) {
            size_t from = cands.size();
            for (int a = 0; a < 4; a++) for (int b = 0; b < 4; b++) if ((a ^ 2) != b) cands.push_back({a, b});
            runCands(from);
        }

        // escape split: when every move looks doomed, shed segments so at least one part survives
        if (!anySurv && bestMdAll <= ESC_MD && spent() < 60000000LL && LEN >= 4 && UCOUNT < ULIMIT && (int)trail.size() < LEN) {
            // tail not visible: keep a minimal parent here, let the rest leave from the tail
            int c = LEN - 2;
            int m1; std::deque<int> par(trail.begin(), trail.begin() + std::min((int)trail.size(), 2));
            bool sp = (int)trail.size() >= 2 && survives(par, 2, 0, m1);
            (void)sp;
            printf("SPLIT %d\nPROTOCOL 3\nENDTURN\n", c);
            fflush(stdout);
            while ((int)trail.size() > 2) trail.pop_back();
            continue;
        }
        if (!anySurv && bestMdAll <= ESC_MD && spent() < 60000000LL && LEN >= 4 && UCOUNT < ULIMIT && (int)trail.size() == LEN) {
            int bestC = -1; double bestV = -1;
            int cs[4] = {2, LEN / 2, LEN - 3, LEN - 2};
            for (int ci = 0; ci < 4; ci++) {
                int c = cs[ci];
                if (spent() > 75000000LL) break;
                if (c < 2 || c > LEN - 2) continue;
                std::deque<int> par(trail.begin(), trail.begin() + (LEN - c));
                std::deque<int> ch(trail.rbegin(), trail.rbegin() + c);
                int m1, m2;
                bool sp = survives(par, LEN - c, 0, m1);
                bool sc2 = survives(ch, c, 0, m2);
#ifdef G1DEBUG
                printf("LOG esc c%d sp%d m1=%d sc%d m2=%d\n", c, sp, m1, sc2, m2);
#endif
                if (!sp && !sc2) continue;
                double v = (sp ? (LEN - c) * 10.0 + 5 : 0) + (sc2 ? c * 10.0 : 0);
                if (v > bestV) { bestV = v; bestC = c; }
            }
            if (bestC > 0 && bestV >= 20) {
                printf("SPLIT %d\nPROTOCOL 3\nENDTURN\n", bestC);
                fflush(stdout);
                while ((int)trail.size() > LEN - bestC) trail.pop_back();
                continue;
            }
        }
        // splitting: parent stays still this turn, child leaves from the tail
        if (R < SPLIT_END && LEN >= SPLIT_AT && UCOUNT < std::min(ULIMIT, MAX_UNITS) && bestS > 0) {
            bool enemyNear = false;
            for (auto &d : drags) if (d.team != MYTEAM && chebToHead(d.chain[0]) <= 3) enemyNear = true;
            int child = LEN / 2;
            bool ok = !enemyNear && child >= 2 && LEN - child >= 2 && (int)trail.size() == LEN;
            if (ok && spent() > 60000000LL) ok = false;
            if (ok) {
                std::deque<int> par(trail.begin(), trail.begin() + (LEN - child));
                std::deque<int> ch(trail.rbegin(), trail.rbegin() + child);
                int m1, m2;
                ok = survives(par, LEN - child, 0, m1) && survives(ch, child, 0, m2);
            }
            if (ok) {
                printf("SPLIT %d\nPROTOCOL 3\nENDTURN\n", child);
                fflush(stdout);
                while ((int)trail.size() > LEN - child) trail.pop_back();
                continue;
            }
        }
        std::string m;
        for (int d : best) m += DC[d];
#ifdef G1DEBUG
        {
            printf("LOG km%d R%d id%d head(%d,%d) dir%c len%d trail%d u%d best=%s sc=%.0f |", kmApplied, R, MYID, cx(myHead), cy(myHead), DC[MYDIR], LEN, (int)trail.size(), UCOUNT, m.c_str(), bestS);
            for (auto &mv : cands) { bool fa; double sc = evaluate(mv, fa); if (mv.size()==1) printf(" %c:%.0f(md%d,a%d,t%d,%d v%.2f d%d)", DC[mv[0]], sc, gLastMd, gLastArea, cx(gBestCell), cy(gBestCell), gBestV, gBestD); }
            printf(" G:");
            for (int yy = -3; yy <= 3; yy++) {
                for (int xx = -3; xx <= 3; xx++) { int c = cid(cx(myHead) + xx, cy(myHead) + yy); int e = hE[c]; printf("+%c", e == -3 ? '-' : e >= 0 ? 'p' : ' '); }
                printf("/");
                for (int xx = -3; xx <= 3; xx++) {
                    int c = cid(cx(myHead) + xx, cy(myHead) + yy); int e = vE[c];
                    char ch = pearlNow[c] ? 'o' : '.';
                    if (occ[c] >= 0) { const Seg &g = segs[occ[c]]; ch = g.id == MYID ? (g.head ? '@' : '#') : g.team == MYTEAM ? (g.head ? 'A' : 'a') : (g.head ? 'E' : 'e'); }
                    printf("%c%c", e == -3 ? '|' : e >= 0 ? 'P' : ' ', ch);
                }
                printf("/");
            }
            printf(" T:");
            for (int c : trail) printf("%d,%d ", cx(c), cy(c));
            printf("\n");
        }
#endif
        printf("MOVE %s\nPROTOCOL 3\nENDTURN\n", m.c_str());
        fflush(stdout);
        Sim s = simulate(best);
        if (!s.dead) trail = s.body;
    }
    return 0;
}
