# Adds known-map geometry (mapdb.hpp) to a base-px pxcore.cpp. usage: python3 patch_map.py <bot dir>
import sys
d = sys.argv[1]
p = d + '/pxcore.cpp'
s = open(p).read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new)

rep('#include "pxproto.hpp"\n#include "style.hpp"', '#include "mapdb.hpp"\n#include "pxproto.hpp"\n#include "style.hpp"')

# init: map candidates
rep("""        double g = 1.0; for (int i = 0; i < 128; i++) { gpow[i] = g; g *= style::GAMMA; }
    }""",
"""        double g = 1.0; for (int i = 0; i < 128; i++) { gpow[i] = g; g *= style::GAMMA; }
        nCand = 0;
        if (style::USE_MAPDB) for (int i = 0; i < mapdb::COUNT && nCand < 16; i++) if (mapdb::MAPS[i].W == W && mapdb::MAPS[i].H == H) cand[nCand++] = i;
    }""")

# members
rep("""    std::vector<int> spawnSeenR;                                          // round at which spawnR was last read""",
"""    std::vector<int> spawnSeenR;                                          // round at which spawnR was last read
    // ---- known maps (mapdb.hpp): candidates of our size, checked against every edge we see; one left -> full geometry ----
    int cand[16]; int nCand = 0; int mapIdx = -1; int mapChecks = 0;
    std::vector<int> mdest;                                               // known map: destination across each tile side, -1 kelp
    std::vector<int8_t> mspawn;                                           // known map: 1 if the tile ever spawns pearls, 0 never""")

# helper functions: DB edge kind and map application
rep("""    // ---- ingest one round block ----""",
"""    // ---- known maps ----
    static int hexBit(const char* h, int i) { char c = h[i >> 2]; int v = c <= '9' ? c - '0' : c - 'a' + 10; return (v >> (i & 3)) & 1; }
    // kind of the north (side 0) or west (side 3) edge of tile t in map m: E_OPEN, E_KELP or E_PORTAL
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
        if (nCand == 1 && mapChecks >= 40) applyMap(cand[0]);
    }
    void applyMap(int m) {
        const mapdb::MapInfo& M = mapdb::MAPS[m];
        mapIdx = m;
        mdest.assign(N * 4, -1); mspawn.assign(N, 0);
        for (int t = 0; t < N; t++) {
            for (int side : {0, 3}) {
                uint8_t k = dbEdge(m, t, side);
                int u = stepT(t, side);
                ek[t * 4 + side] = k; ek[u * 4 + opp(side)] = k;
                if (k == E_OPEN) { mdest[t * 4 + side] = u; mdest[u * 4 + opp(side)] = t; }
            }
            int pi = M.spawn[t] - 48; mspawn[t] = (pi > 0 && pi < M.nPal && M.pal[pi * 2 + 1] > 0) ? 1 : 0;
            if (!mspawn[t] && spawnR[t] == -2) spawnR[t] = -1;
        }
        // portals: crossing north through (x,y,N) emerges north of the partner's tile, crossing south enters the partner's tile
        for (int i = 0; i < M.nPortals; i++) for (int e = 0; e < 2; e++) {
            const int* a = M.portals + i * 6 + e * 3; const int* b = M.portals + i * 6 + (1 - e) * 3;
            int ta = a[1] * W + a[0], tb = b[1] * W + b[0];
            if (a[2] == 0) { mdest[ta * 4 + 0] = stepT(tb, 0); mdest[stepT(ta, 0) * 4 + 2] = tb; }
            else { mdest[ta * 4 + 3] = stepT(tb, 3); mdest[stepT(ta, 3) * 4 + 1] = tb; }
        }
        if (M.sym >= 0) sym = M.sym;
    }

    // ---- ingest one round block ----""")

# across: known map first
rep("""    int across(int t, int d) const {
        uint8_t k = ek[t * 4 + d];""",
"""    int across(int t, int d) const {
        if (mapIdx >= 0) return mdest[t * 4 + d];
        uint8_t k = ek[t * 4 + d];""")

# setEdge: no changes once the map is known
rep("""    void setEdge(int t, int d, int tok) {
        uint8_t k""",
"""    void setEdge(int t, int d, int tok) {
        if (mapIdx >= 0) return;
        uint8_t k""")

# ingest: check after edges
rep("""        updateSymmetry(win);
        if (sym >= 0) applyMirror(win);""",
"""        checkMap(win);
        updateSymmetry(win);
        if (sym >= 0) applyMirror(win);""")

# applyMirror must not write edges once known (edges already complete); keep timers
rep("""            for (int d = 0; d < 4; d++) {
                int md = mirrorD(d, sym);
                if (ek[m * 4 + md] != E_UNK) continue;""",
"""            if (mapIdx >= 0) continue;
            for (int d = 0; d < 4; d++) {
                int md = mirrorD(d, sym);
                if (ek[m * 4 + md] != E_UNK) continue;""")

# exploration: known map -> only tiles that can spawn pearls
rep("""            for (int t : q) if (seenR[t] < 0 || round - seenR[t] > style::STALE_AGE) { best = t; break; }""",
"""            for (int t : q) if ((seenR[t] < 0 || round - seenR[t] > style::STALE_AGE) && (mapIdx < 0 || mspawn[t])) { best = t; break; }""")
open(p, 'w').write(s)

p = d + '/style.hpp'
s = open(p).read()
old = "// --- movement ---"
assert old in s
s = s.replace(old, """// --- px3: known maps ---
constexpr bool USE_MAPDB = true;            // recognise the map among mapdb.hpp (size + every edge seen) and use its full geometry

// --- movement ---""", 1)
open(p, 'w').write(s)
print('patched', d)
