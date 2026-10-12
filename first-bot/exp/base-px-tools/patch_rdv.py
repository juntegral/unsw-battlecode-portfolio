# px6: feeding station. The known map (mapdb.hpp, recognised from the edges we see) gives every dragon the same
# rendezvous tile Z (most open tile on our side of the map, from the initial dragons); from GATHER_START pieces walk to Z
# (true-map distance) unless they see the king, and the king stays within KING_Z_R of Z. Geometry used only for this.
# usage: python3 patch_rdv.py <bot dir>   (bot dir needs mapdb.hpp with initial heads)
import sys
d = sys.argv[1]
p = d + '/pxcore.cpp'
s = open(p).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new)

rep('#include "pxproto.hpp"\n#include "style.hpp"', '#include "mapdb.hpp"\n#include "pxproto.hpp"\n#include "style.hpp"')
rep("""        double g = 1.0; for (int i = 0; i < 128; i++) { gpow[i] = g; g *= style::GAMMA; }
    }""",
"""        double g = 1.0; for (int i = 0; i < 128; i++) { gpow[i] = g; g *= style::GAMMA; }
        nCand = 0;
        if (style::RDV) for (int i = 0; i < mapdb::COUNT && nCand < 16; i++) if (mapdb::MAPS[i].W == W && mapdb::MAPS[i].H == H) cand[nCand++] = i;
    }""")
rep("""    std::vector<int> spawnSeenR;                                          // round at which spawnR was last read""",
"""    std::vector<int> spawnSeenR;                                          // round at which spawnR was last read
    // ---- px6: known map -> feeding station ----
    int cand[16]; int nCand = 0; int mapIdx = -1; int mapChecks = 0;
    std::vector<int> mdest;       // true map: destination across each tile side, -1 kelp (used for the station only)
    std::vector<int> zdist;       // true-map steps to the station Z, -1 unreachable
    int zTile = -1;""")
rep("""    // ---- ingest one round block ----""",
"""    // ---- px6: known map and feeding station ----
    static int hexBit(const char* h, int i) { char c = h[i >> 2]; int v = c <= '9' ? c - '0' : c - 'a' + 10; return (v >> (i & 3)) & 1; }
    uint8_t dbEdge(int m, int t, int side) const {
        const mapdb::MapInfo& M = mapdb::MAPS[m];
        int x = t % W, y = t / W, s1 = side == 0 ? 0 : 1;
        for (int i = 0; i < M.nPortals; i++) for (int e = 0; e < 2; e++) {
            const int* q = M.portals + i * 6 + e * 3;
            if (q[0] == x && q[1] == y && q[2] == s1) return E_PORTAL;
        }
        return hexBit(side == 0 ? M.hk : M.vk, t) ? E_KELP : E_OPEN;
    }
    void checkMap(const int* win) {
        if (mapIdx >= 0 || nCand == 0) return;
        for (int i = 0; i < 49; i++) {
            int t = win[i];
            for (int side : {0, 3}) {
                uint8_t k = ek[t * 4 + side]; if (k == E_UNK) continue;
                for (int c = 0; c < nCand; c++) if (dbEdge(cand[c], t, side) != k) { cand[c] = cand[--nCand]; c--; }
                mapChecks++;
            }
        }
        if (nCand == 1 && mapChecks >= 40) setupStation(cand[0]);
    }
    void trueBfs(const std::vector<int>& src, std::vector<int>& d, int maxd) {
        d.assign(N, -1); std::vector<int> qq; qq.reserve(N);
        for (int t : src) if (d[t] < 0) { d[t] = 0; qq.push_back(t); }
        for (size_t i = 0; i < qq.size(); i++) {
            int t = qq[i]; if (d[t] >= maxd) continue;
            for (int k = 0; k < 4; k++) { int u = mdest[t * 4 + k]; if (u < 0 || d[u] >= 0) continue; d[u] = d[t] + 1; qq.push_back(u); }
        }
    }
    void setupStation(int m) {
        const mapdb::MapInfo& M = mapdb::MAPS[m];
        mapIdx = m;
        mdest.assign(N * 4, -1);
        for (int t = 0; t < N; t++) for (int side : {0, 3}) {
            if (dbEdge(m, t, side) != E_OPEN) continue;
            int u = stepT(t, side); mdest[t * 4 + side] = u; mdest[u * 4 + opp(side)] = t;
        }
        for (int i = 0; i < M.nPortals; i++) for (int e = 0; e < 2; e++) {
            const int* a = M.portals + i * 6 + e * 3; const int* b = M.portals + i * 6 + (1 - e) * 3;
            int ta = a[1] * W + a[0], tb = b[1] * W + b[0];
            if (a[2] == 0) { mdest[ta * 4 + 0] = stepT(tb, 0); mdest[stepT(ta, 0) * 4 + 2] = tb; }
            else { mdest[ta * 4 + 3] = stepT(tb, 3); mdest[stepT(ta, 3) * 4 + 1] = tb; }
        }
        std::vector<int> ours, theirs, dA, dB;
        int me = myTeam == 'B' ? 1 : 0;
        for (int i = 0; i < M.nHeads; i++) { int t = M.heads[i * 3 + 2] * W + M.heads[i * 3 + 1]; (M.heads[i * 3] == me ? ours : theirs).push_back(t); }
        if (ours.empty() || theirs.empty()) return;
        trueBfs(ours, dA, 1 << 20); trueBfs(theirs, dB, 1 << 20);
        // openness: tiles within STATION_R true-map steps; the station is the most open tile on our side
        std::vector<int> stamp(N, -1), qq; qq.reserve(128);
        int best = -1; long long bestScore = -1;
        for (int t = 0; t < N; t++) {
            if (dA[t] < 0 || (dB[t] >= 0 && dA[t] >= dB[t])) continue;
            qq.clear(); qq.push_back(t); stamp[t] = t; std::vector<int>* dummy = nullptr; (void)dummy;
            int cnt = 0; std::vector<int> lvl; lvl.push_back(0);
            for (size_t i = 0; i < qq.size(); i++) {
                int u = qq[i]; cnt++; if (lvl[i] >= style::STATION_R) continue;
                for (int k = 0; k < 4; k++) { int v = mdest[u * 4 + k]; if (v < 0 || stamp[v] == t) continue; stamp[v] = t; qq.push_back(v); lvl.push_back(lvl[i] + 1); }
            }
            long long sc = (long long)cnt * 100000 - dA[t];
            if (sc > bestScore) { bestScore = sc; best = t; }
        }
        if (best < 0) return;
        zTile = best;
        trueBfs(std::vector<int>{zTile}, zdist, 1 << 20);
    }

    // ---- ingest one round block ----""")
rep("""        updateSymmetry(win);
        if (sym >= 0) applyMirror(win);""",
"""        checkMap(win);
        updateSymmetry(win);
        if (sym >= 0) applyMirror(win);""")
# scoring: gather mode chosen in decide(); 0 none, 1 to the king's head (kingT), 2 to the station, 3 king near the station
rep("""        if (late && !amKing && kingT >= 0 && style::GATHER_W > 0) {
            int kd = dist[kingT] >= 0 ? dist[kingT] : manh(s, kingT) + 4;
            sc -= style::GATHER_W * kd;
        }""",
"""        if (gatherMode == 1 && kingT >= 0 && style::GATHER_W > 0) {
            int kd = dist[kingT] >= 0 ? dist[kingT] : manh(s, kingT) + 4;
            sc -= style::GATHER_W * kd;
        } else if (gatherMode == 2 && zTile >= 0 && zdist[s] >= 0) {
            sc -= style::GATHER_W * std::max(0, zdist[s] - style::Z_PIECE_R);
        } else if (gatherMode == 3 && zTile >= 0 && zdist[s] >= 0) {
            sc -= style::KING_Z_W * std::max(0, zdist[s] - style::Z_KING_R);
        }""")
rep("""    double scoreDir(int d, bool late, int kingT, bool amKing) {""",
"""    int gatherMode = 0;
    double scoreDir(int d, bool late, int kingT, bool amKing) {""")
rep("""        bool late = round >= style::SAC_START;
        int kid = myId, klen = L, kt = head, kr = round; bool amKing = true;
        if (style::KING_GATHER && late) {
            kingInfo(kid, klen, kt, kr); amKing = kid == myId;
            if (!amKing) { const Seen* ks = seenById(kid); if (ks && ks->head >= 0) kt = ks->head; }
            if (klen < style::KING_MIN_LEN) { amKing = true; kt = -1; } // no real king yet: no gathering
        }""",
"""        bool late = round >= style::SAC_START;
        int kid = myId, klen = L, kt = head, kr = round; bool amKing = true;
        if (style::KING_GATHER && late) {
            kingInfo(kid, klen, kt, kr); amKing = kid == myId;
            if (!amKing) { const Seen* ks = seenById(kid); if (ks && ks->head >= 0) kt = ks->head; }
            if (klen < style::KING_MIN_LEN) { amKing = true; kt = -1; } // no real king yet: no gathering
        }
        // px6: gathering mode. With a station: a dragon that sees the king walks to it, others walk to the station,
        // the king (or a big dragon that believes it is the king) keeps near the station.
        gatherMode = 0;
        if (style::KING_GATHER && late && !amKing && kt >= 0) gatherMode = 1;
        if (zTile >= 0 && round >= style::STATION_START) {
            bool kingSeen = !amKing && seenById(kid) != nullptr;
            if (amKing && L >= style::KING_MIN_LEN) gatherMode = 3;
            else if (!kingSeen) gatherMode = 2;
            else gatherMode = 1;
            if (gatherMode == 1 && kt < 0) gatherMode = 2;
        }""")
rep("""            double sc = scoreDir(d, late, amKing ? -1 : kt, amKing);""",
"""            double sc = scoreDir(d, late || gatherMode != 0, amKing ? -1 : kt, amKing);""")
open(p, 'w').write(s)
p = d + '/style.hpp'
s = open(p).read()
old = "// --- movement ---"
assert old in s
s = s.replace(old, """// --- px6: feeding station on known maps ---
constexpr bool RDV = true;                  // recognise the map (mapdb.hpp) and gather at a common station
constexpr int STATION_START = 320;          // from here pieces walk to the station (or to the king once they see it)
constexpr int STATION_R = 5;                // openness radius used to choose the station
constexpr int Z_PIECE_R = 3;                // pieces are pulled until this close to the station ...
constexpr int Z_KING_R = 6;                 // ... the king until this close
constexpr double KING_Z_W = 0.20;           // pull per step for the king

// --- movement ---""", 1)
open(p, 'w').write(s)
print('patched', d)
