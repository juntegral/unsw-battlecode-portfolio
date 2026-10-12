// mapid.cpp — cand-mapid (hypothesis #11, research/experiments/cand-mapid.md): recognise the map and its pearl layout.
// Ported from the proxy4 bots (bots/proxy4_swarm/pxcore.cpp checkSdb; research/experiments/proxies-v3.md "v4"):
//   - candidates: the table maps (mapdb.hpp) of our board size;
//   - every turn, for each of the 49 window tiles: its north and west edges (kelp / portal / open) and its spawn flag
//     (pearlIn -1 = never spawns) must match the candidate; on a map with two layouts also the countdown: pearlIn <= max
//     (+5% + 1 slack), and before the first possible attempt (round < min - 1) the initial countdown pearlIn + round + 1
//     must lie in [min, max] (rules/pearls.md; checked on local replays: round-0 pearlIn = initial countdown - 1);
//   - one candidate left = decided (map, layout a/b, type); several of one family = family known, layout not yet ('?');
//     none left = "none" (an unknown map or layout).
// Unlike the proxies it keeps checking the decided map, so a wrong decision shows up as "none" in the indicator tag, and
// the 10-dragon Prisoners Dilemma is layout b of the Prisoners Dilemma family (its middle tiles: 480-490 in a, 1-100 in b).
// Cost: 49 tiles x (2 edges + 1 countdown) x candidates left (at most 5) per turn.
#include <cstdio>
#include <cstring>

#include "frontdb.hpp"
#include "mapdb.hpp"
#include "mapstart.hpp"
#include "terrdb.hpp"
#include "world.hpp"

namespace seed0 {

static bool mapMulti[mapdb::COUNT];   // the map's family has a second layout (countdown check)
// v1.6.1: the recognition gate needs the map state in the messages, which only format 2 (the v1 belief fix) carries
constexpr bool GATE_ON = P::MAPID2_ON && P::BELIEF_FIX_ON && !P::QUAL_NO_MAPID;   // v1.7: no gate (nor its table) without recognition

static int hexBit(const char* h, int i) { char c = h[i >> 2]; int v = c <= '9' ? c - '0' : c - 'a' + 10; return (v >> (i & 3)) & 1; }
static uint8_t tableEdge(int m, int t, int side) {   // side N or W of tile t in map m
    const mapdb::MapInfo& M = mapdb::MAPS[m];
    if (hexBit(side == N ? M.hp : M.vp, t)) return EDGE_PORTAL;
    return hexBit(side == N ? M.hk : M.vk, t) ? EDGE_KELP : EDGE_OPEN;
}
static void tableRange(int m, int t, int& lo, int& hi) {
    const mapdb::MapInfo& M = mapdb::MAPS[m];
    int pi = M.spawn[t] - 48;
    if (pi > 0 && pi < M.nPal) { lo = M.pal[pi * 2]; hi = M.pal[pi * 2 + 1]; } else { lo = 0; hi = 0; }
}
static bool tableFits(int m, int t, int p, int round) {
    int lo, hi; tableRange(m, t, lo, hi);
    if (hi <= 0 || p < 0) return hi <= 0 && p < 0;
    if (!mapMulti[m]) return true;
    const int sHi = hi / 20 + 1, sLo = lo / 20 + 1;
    if (p > hi + sHi) return false;
    if (round < lo - 1 - sLo) { int g0 = p + round + 1; if (g0 < lo - sLo || g0 > hi + sHi) return false; }
    return true;
}

void World::initMapId() {
    nMapCand = 0; mapChecks = 0; mapIdx = -1; mapFam = -1; mapLayout = '?'; mapType = 0; mapNone = false; mapDecidedRound = -1;
    if (P::CV2_EVAL_MAPID_OFF || P::QUAL_NO_MAPID) { mapNone = true; return; }   // v1.6g evaluation (exp/gen's GEN_MAPID_OFF); v1.7 qualifier line
    for (int i = 0; i < mapdb::COUNT; i++) {
        mapMulti[i] = false;
        for (int j = 0; j < mapdb::COUNT; j++) if (j != i && mapdb::MAPS[j].fam == mapdb::MAPS[i].fam) mapMulti[i] = true;
    }
    for (int i = 0; i < mapdb::COUNT && nMapCand < 16; i++) if (mapdb::MAPS[i].W == geo.W && mapdb::MAPS[i].H == geo.H) mapCand[nMapCand++] = i;
    if (nMapCand == 0) mapNone = true;
    mapHadCand = nMapCand > 0;   // v1.6.1
}

void World::updateMapId(const RoundBlock& rb, const int* winTile) {
    if (mapNone) return;
    if constexpr (GATE_ON) {
        // v1.6.1: our r0 head and length (the start anchor), then this turn's inbox: a sender that had decided opens the gate; a direct
        // "none" from an ally we already know (in view now, or seen or heard before this turn) makes us none
        if (birthRound < 0 && round == 0) { mapStartT = headT; mapStartLen = myLen; }
        for (uint64_t v : rb.msgs) {
            AllyMsg m; int st = 0;
            if (!decodeMsg(v, m, &st) || m.id == (myId & msgIdMask())) continue;
            if (st == 0) { mapHeardDec = true; continue; }
            if (st != 2 || m.relay) continue;
            bool known = false;
            auto it = dragons.find(m.id);
            if (it != dragons.end() && it->second.team == myTeam) known = true;
            for (const PartObs& p : rb.parts) if (!known && p.id == m.id && p.team == myTeam) known = true;
            if (known) { mapToNone(); mapNews |= 4; return; }
        }
    }
    for (int i = 0; i < 49; i++) {
        int t = winTile[i];
        for (int side : {(int)N, (int)W}) {
            uint8_t k = tiles[t].edge[side]; if (k == EDGE_UNKNOWN) continue;
            for (int c = 0; c < nMapCand; c++) if (tableEdge(mapCand[c], t, side) != k) { mapCand[c] = mapCand[--nMapCand]; c--; }
        }
        const int p = rb.tiles[i].pearlIn;
        for (int c = 0; c < nMapCand; c++) if (!tableFits(mapCand[c], t, p, round)) { mapCand[c] = mapCand[--nMapCand]; c--; }
        mapChecks++;
    }
    if (mapChecks < 49) return;
    if (nMapCand == 0) { mapToNone(); return; }
    if constexpr (GATE_ON) {
        // v1.6.1: the gate before the family decision (a process that decided its family decides its layout as v1.6 did)
        if (mapFam < 0) {
            const int fam0 = mapdb::MAPS[mapCand[0]].fam;
            for (int c = 1; c < nMapCand; c++) if (mapdb::MAPS[mapCand[c]].fam != fam0) return;   // several families left
            if (!mapGateOpen()) { if (mapHeldFam < 0) { mapHeldFam = fam0; mapNews |= 1; } return; }
            if (nMapCand == 0) { mapToNone(); return; }   // the start check dropped every candidate left
        }
    }
    if (nMapCand == 1) {
        if (mapIdx == mapCand[0]) return;
        const mapdb::MapInfo& M = mapdb::MAPS[mapCand[0]];
        mapIdx = mapCand[0]; mapFam = M.fam; mapLayout = M.layout; mapType = M.elim ? 1 : 2; mapDecidedRound = round;
        return;
    }
    const int fam = mapdb::MAPS[mapCand[0]].fam;
    for (int c = 1; c < nMapCand; c++) if (mapdb::MAPS[mapCand[c]].fam != fam) return;   // several families left
    mapFam = fam; mapType = mapdb::MAPS[fam].elim ? 1 : 2;
}

// v1.6.1: may this process decide on the one family left? (a) The start anchor: our first turn was round 0 and, among the candidates
// left, one has a start dragon on our r0 head tile with our length (ids follow the file order, so a candidate with more dragons than our
// id would have had us as a start dragon: one without such a start cannot be the map and is dropped here, never earlier, so a known map
// is decided on the same turn as before). The team letter is not compared (the server swaps letters in about half of its games).
// (b) A message from an ally that had decided its family (mapHeardDec).
bool World::mapGateOpen() {
    if constexpr (!GATE_ON) return true;   // (no start table in the build without the gate)
    else {
        if (mapStartT >= 0) {
            bool anchored = false; int drop = 0;
            for (int c = 0; c < nMapCand; c++) {
                const mapstart::MapStarts& S = mapstart::STARTS[mapCand[c]];
                if (myId >= S.n) continue;   // under this map we would be a child born in round 0: no anchor, nothing to drop
                bool ok = false;
                for (int i = 0; i < S.n && !ok; i++) ok = geo.idx(S.d[i].x, S.d[i].y) == mapStartT && S.d[i].len == mapStartLen;
                if (ok) anchored = true;
                else { mapCand[c] = mapCand[--nMapCand]; c--; drop++; }
            }
            if (drop) { mapStartDrop += drop; mapNews |= 2; }
            if (anchored || nMapCand == 0) return true;   // nMapCand 0: the caller makes it none
        }
        if (mapHeardDec) { mapNews |= 8; return true; }
        return false;
    }
}

void World::mapToNone() {
    const bool decided = mapFam >= 0;
    mapNone = true; mapIdx = -1; mapLayout = '?'; mapFam = -1; mapType = 0;
    if constexpr (P::MAPID2_ON) {
        // v1.6.1: leave no table state of the family we had decided (pockets follow mapStateCode in ensurePockets)
        if (decided) { core2.clear(); core2Fam = -2; ptLenActive = false; }
    }
}

int World::mapMsgState() const {
    if (!GATE_ON || !mapHadCand) return 0;
    if (mapNone) return 2;
    return mapFam >= 0 ? 0 : 1;
}

std::string World::takeMapNewsTag() {
    std::string s;
    if constexpr (GATE_ON) {
        if (mapNews & 1) s += std::string(" mg=") + (mapHeldFam >= 0 ? mapdb::MAPS[mapHeldFam].name : "?");
        if (mapNews & 2) s += " ms" + std::to_string(mapStartDrop);
        if (mapNews & 4) s += " mn";
        if (mapNews & 8) s += " mc";
    }
    mapNews = 0;
    return s;
}

bool World::mapIs(const char* famName, char layout) const {
    return !mapNone && mapIdx >= 0 && mapLayout == layout && std::strcmp(mapdb::MAPS[mapdb::MAPS[mapIdx].fam].name, famName) == 0;
}

// stack7 (the floor / kcap map gate): the family is known once every map left belongs to it; the layout does not matter there
bool World::mapFamIs(const char* famName) const {
    return !mapNone && mapFam >= 0 && std::strcmp(mapdb::MAPS[mapFam].name, famName) == 0;
}

// stack8 F2: the table's fountain (the ledger's definition: spawn gap mean (min + max) / 2 <= 12) and territory (terrdb.hpp) at tile t,
// once the family is known (mapFam >= 0: every map left is of one family) and every table map left agrees on t; -1 otherwise
int World::mapFountAt(int t) const {
    if (mapNone || mapFam < 0 || nMapCand <= 0) return -1;
    int v = -1;
    for (int c = 0; c < nMapCand; c++) {
        int lo, hi; tableRange(mapCand[c], t, lo, hi);
        int f = hi > 0 && lo + hi <= 24 ? 1 : 0;
        if (v < 0) v = f; else if (v != f) return -1;
    }
    return v;
}

int World::mapTerrAt(int t, int homeT) const {
    if (mapNone || mapFam < 0 || nMapCand <= 0 || homeT < 0) return -1;
    int v = -1;
    for (int c = 0; c < nMapCand; c++) {
        const char* T = terrdb::TERR[mapCand[c]];
        char h = T[homeT], x = T[t];
        if (h == '0') return -1;                       // a neutral home tile does not tell the side
        int s = x == '0' ? 0 : x == h ? 1 : 2;
        if (v < 0) v = s; else if (v != s) return -1;
    }
    return v;
}

// v1 sd: terrdb's own char at t (the file's team sides; our side is decided by the planner), where every table map left agrees
char World::mapTerrChar(int t) const {
    if (mapNone || mapFam < 0 || nMapCand <= 0 || t < 0) return '?';
    char v = 0;
    for (int c = 0; c < nMapCand; c++) { const char x = terrdb::TERR[mapCand[c]][t]; if (!v) v = x; else if (v != x) return '?'; }
    return v ? v : '?';
}

// v1.1: frontdb's bin at t seen from terrdb side '1' / '2', where every table map left agrees (see world.hpp)
int World::mapFrontBin(int t, char side) const {
    if (mapNone || mapFam < 0 || nMapCand <= 0 || t < 0 || (side != '1' && side != '2')) return -1;
    const int s = side == '1' ? 0 : 1;
    char v = 0;
    for (int c = 0; c < nMapCand; c++) { const char x = frontdb::FRONT[2 * mapCand[c] + s][t]; if (!v) v = x; else if (v != x) return -1; }
    return v >= '0' && v <= '4' ? v - '0' : -1;
}

// v1 final: the 2-core of the family's passable graph (see world.hpp)
void World::ensureCore2() {
    if (mapNone || mapFam < 0) return;
    if (core2Fam == mapFam) return;
    core2Fam = mapFam;
    const int m = mapFam, n = geo.tiles();
    auto kind = [&](int t, int d) -> uint8_t {   // the edge on side d of tile t in table map m
        if (d == N || d == W) return tableEdge(m, t, d);
        return tableEdge(m, geo.stepIdx(t, d), d == S ? N : W);
    };
    std::vector<int> deg(n, 0), q; q.reserve(n);
    std::vector<uint8_t> gone(n, 0);
    for (int t = 0; t < n; t++) {
        for (int d = 0; d < 4; d++) if (kind(t, d) != EDGE_KELP) deg[t]++;
        if (deg[t] <= 1) { gone[t] = 1; q.push_back(t); }
    }
    for (size_t i = 0; i < q.size(); i++) {
        const int t = q[i];
        for (int d = 0; d < 4; d++) {
            if (kind(t, d) != EDGE_OPEN) continue;   // kelp: no neighbour; portal: its far side is not known here
            const int u = geo.stepIdx(t, d);
            if (gone[u]) continue;
            if (--deg[u] <= 1) { gone[u] = 1; q.push_back(u); }
        }
    }
    core2.assign(n, 1);
    for (int t = 0; t < n; t++) if (gone[t]) core2[t] = 0;
}

// v1.3 HV: the dead-end pockets (see world.hpp)
void World::ensurePockets() {
    ensureCore2();
    const int key = mapStateCode();
    if (key == pocketKey) return;
    pocketKey = key;
    pockets.clear(); pocketOf.clear(); pocketDepth.clear();
    if (mapNone || mapFam < 0 || core2.empty()) return;
    const int m = mapFam, n = geo.tiles();
    auto nb = [&](int t, int d) -> int {   // the tile across an open table edge (kelp and portals: none)
        const uint8_t k = (d == N || d == W) ? tableEdge(m, t, d) : tableEdge(m, geo.stepIdx(t, d), d == S ? N : W);
        return k == EDGE_OPEN ? geo.stepIdx(t, d) : -1;
    };
    pocketOf.assign(n, -1); pocketDepth.assign(n, 0);
    for (int t0 = 0; t0 < n; t0++) {
        if (core2[t0] || pocketOf[t0] >= 0) continue;
        Pocket p; const int id = (int)pockets.size();
        std::vector<int> q{t0}; pocketOf[t0] = (int16_t)id;
        for (size_t i = 0; i < q.size(); i++) {
            const int u = q[i]; p.tiles.push_back(u);
            for (int d = 0; d < 4; d++) {
                const int v = nb(u, d); if (v < 0) continue;
                if (core2[v]) { if (p.mouth < 0) { p.mouth = v; p.entrance = u; } continue; }
                if (pocketOf[v] < 0) { pocketOf[v] = (int16_t)id; q.push_back(v); }
            }
        }
        if (p.entrance >= 0) {   // depth: steps from the entrance + 1, inside the pocket
            std::vector<int> bq{p.entrance}; pocketDepth[p.entrance] = 1;
            for (size_t i = 0; i < bq.size(); i++) for (int d = 0; d < 4; d++) {
                const int v = nb(bq[i], d);
                if (v < 0 || pocketOf[v] != id || pocketDepth[v] > 0) continue;
                pocketDepth[v] = (int16_t)(pocketDepth[bq[i]] + 1); bq.push_back(v);
            }
            for (int u : p.tiles) p.depth = std::max(p.depth, (int)pocketDepth[u]);
        }
        for (int u : p.tiles) { const double g = mapSpawnGap(u); if (g > 0.0 && g <= 12.0) p.fountains++; }
        pockets.push_back(p);
    }
}

// v1 sd: the mean spawn gap at t over the table maps left (a tile that never spawns in one of them: 0)
double World::mapSpawnGap(int t) const {
    if (mapNone || mapFam < 0 || nMapCand <= 0 || t < 0) return -1.0;
    double sum = 0.0;
    for (int c = 0; c < nMapCand; c++) { int lo, hi; tableRange(mapCand[c], t, lo, hi); if (hi <= 0) return 0.0; sum += (lo + hi) * 0.5; }
    return sum / nMapCand;
}

std::string World::mapTag() const {
    if (mapNone) return "map=none";
    if (mapIdx >= 0) return std::string("map=") + mapdb::MAPS[mapdb::MAPS[mapIdx].fam].name + "/" + mapLayout;
    if (mapFam >= 0) return std::string("map=") + mapdb::MAPS[mapFam].name + "/?";
    return "map=?";
}

} // namespace seed0
