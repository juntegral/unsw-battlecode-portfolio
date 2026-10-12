// pxcore.cpp — shared code of the v4 top-team proxy bots (bots/proxy4_*). Identical in every proxy4 directory; the
// behaviour constants are in each directory's style.hpp, the map spawn table in spawndb.hpp. bots/proxy4_swarm is the
// master copy (copy pxcore.cpp, pxproto.*, spawndb.hpp to the others). Design and calibration:
// research/experiments/proxies-v3.md (v3, and its section "v4"). Built from the v2 proxies (bots/proxy_*,
// research/experiments/proxies.md) and the late-game changes of exp/base-px8/bot (research/experiments/base-px.md).
//
// v4 = v3 (bots/proxy3_*) + the server's second pearl layouts (b) of Devil, Queen Of Spades, Schooltime and Slithery
// Fight in the spawn table (exp/proxy4-tools/genspawndb.js). Only map recognition changed (checkSdb): the a and b layouts
// of a map (spawndb fam) are told apart by tiles that never spawn in one of them (as v3 tells maps apart) and by the
// countdowns read (range check, only for these two-layout maps), and while a dragon cannot yet tell a from b it values
// tiles by their mixture. Every other map, Prisoners Dilemma 6 / 10 included, is recognised exactly as in v3. Each
// process logs its recognition once (LOG px4 ...). Styles and random salts are those of v3.
//
// One process per dragon (rules). Each dragon remembers what it has seen: kelp and portal edges, pearls, pearl timers
// (filled in for mirror tiles once the map symmetry is inferred), its own body, visible dragons, and what allies report
// by sonar (all four rays every turn carry team, kind, id, round, head x/y and length). v3 also recognises the known
// maps from what it sees (spawndb.hpp: kelp/portal edges and which tiles can spawn) and then knows every tile's spawn
// gap range, so it values unseen or stale spawn tiles by the chance that a pearl waits there. Every turn, in this order:
//   1. rams (top rule R4): a piece of length <= RAM_MAX_LEN steps or sprints into a visible enemy head. With an ally head
//      in view it trades with an enemy as long or longer; alone it takes only longer enemies; big targets always;
//   2. trapped (no free neighbour): a big dragon splits off a stub first (px8); else ram an adjacent enemy head; else
//      split off all but STUB_KEEP head segments, else die (no action or a blocked step);
//   3. late conversion: small pieces die next to a growing ally (R3: length >= 8 within Chebyshev 3, no enemy head in
//      view), in front of a big receiver's or the king's head (px8), or near any longer ally (v2); mid-size pieces beside
//      a clearly longer one; pearls near a big ally's or the king's head are left for it (px8);
//   4. splitting (R1): 4 -> 2+2 (longer: halves) until GROW_START; then only the local king (longest seen or heard within
//      KING_RADIUS) grows, other mid-size dragons halve; no split when the tail has no room;
//   5. move: pearl value (visible, remembered, soon-spawning and expected pearls; discounted when an ally head is closer,
//      less so for an enemy head), exploration, room check, survival lookahead, enemy-head avoidance for length >= 5,
//      ally spacing, K gathering, elim hunting, and a two-step sprint onto a contested pearl for short dragons.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <string>
#include <unordered_map>
#include <vector>

#include "pxproto.hpp"
#include "spawndb.hpp"
#include "style.hpp"

namespace px {

constexpr int DX[4] = {0, 1, 0, -1}, DY[4] = {-1, 0, 1, 0};
constexpr const char* DIRCH = "NESW";
inline int opp(int d) { return (d + 2) & 3; }
enum : uint8_t { E_UNK = 0, E_OPEN = 1, E_KELP = 2, E_PORTAL = 3 };
constexpr int NEVER_FREE = 1 << 20;
enum NbKind { NB_FREE = 0, NB_KELP, NB_OWN, NB_ALLY, NB_ENEMY, NB_ALLY_HEAD, NB_ENEMY_HEAD, NB_PORTAL_UNKNOWN };
inline bool isOpen(int k) { return k == NB_FREE || k == NB_PORTAL_UNKNOWN; }

static inline uint32_t mix32(uint32_t x) { x ^= x >> 16; x *= 0x7feb352dU; x ^= x >> 15; x *= 0x846ca68bU; x ^= x >> 16; return x; }

struct Seen {
    int id = -1; char team = 'A'; int head = -1; int hdir = 0; int nVis = 0; bool tailSeen = false;
    int len = 0;             // visible segments, raised to a recent sonar/vision length when the tail is out of view (px8)
    std::vector<int> chain;  // tiles, head first, following the facing pointers
};
struct News { int round = -1; int t = -1; int len = 0; };
struct Target { int t; double v; int spawn; bool exp; };  // exp: value from the map spawn table (a flow; gentler step discount)

struct Plan {
    enum Kind { MOVE, SPLIT, DIE } kind = MOVE;
    std::string dirs;   // MOVE: one letter per step
    int child = 0;      // SPLIT: child length
    int method = 0;     // DIE: 0 no action, 1 SPLIT 1, 2 step into the neck / blocked tile
    char tag = 'm';     // indicator
};

class Bot {
  public:
    void init(const InitBlock& ib) {
        W = ib.W; H = ib.H; N = W * H; myId = ib.id; myTeam = ib.team; unitLimit = ib.unitLimit;
        ek.assign(N * 4, E_UNK); ep.assign(N * 4, -1);
        seenR.assign(N, -1); pearlR.assign(N, -1); emptyR.assign(N, -1); spawnR.assign(N, -2); inView.assign(N, -1); spawnSeenR.assign(N, -1);
        occId.assign(N, -1); headId.assign(N, -1); freeAt.assign(N, 0); bodyIdx.assign(N, -1); occKind.assign(N, 0); nearHead.assign(N, 0); gapMin.assign(N, 0);
        dist.assign(N, -1); distAlly.assign(N, -1); distEnemy.assign(N, -1); tmp.assign(N, -1); eReach.assign(N, 99); eReachLen.assign(N, 0);
        double g = 1.0; for (int i = 0; i < 128; i++) { gpow[i] = g; g *= style::GAMMA; }
        g = 1.0; for (int i = 0; i < 128; i++) { gpowE[i] = g; g *= style::GAMMA_EXP; }
        if (style::SPAWN_KNOW) for (int i = 0; i < spawndb::COUNT && nSdb < 16; i++) if (spawndb::MAPS[i].W == W && spawndb::MAPS[i].H == H) sdbCand[nSdb++] = i;
        for (int i = 0; i < spawndb::COUNT; i++) { sdbMulti[i] = false; for (int j = 0; j < spawndb::COUNT; j++) if (j != i && spawndb::MAPS[j].fam == spawndb::MAPS[i].fam) sdbMulti[i] = true; }
    }

    void turn(const RoundBlock& rb, Writer& w) {
        ingest(rb);
        if (!sdbLog.empty()) { w.log(sdbLog); sdbLog.clear(); }
        Plan p = decide();
        // a well-formed fallback line first, unless we mean to die with no action
        bool noAction = p.kind == Plan::DIE && p.method == 0;
        if (!noAction && safeDir >= 0) w.move(std::string(1, DIRCH[safeDir]).c_str());
        if (p.kind == Plan::MOVE && !p.dirs.empty()) w.move(p.dirs.c_str());
        else if (p.kind == Plan::SPLIT) w.split(p.child);
        else if (p.kind == Plan::DIE) {
            if (p.method == 1) w.split(1);
            else if (p.method == 2) w.move(std::string(1, DIRCH[dieDir()]).c_str());
        }
        if (ok && !(p.kind == Plan::DIE)) sendSonar(w);
        if (style::INDICATOR) { char b[24]; snprintf(b, sizeof b, "%c L%d", p.tag, L); w.indicator(b); }
        w.endTurn();
    }

  private:
    // ---- board memory ----
    int W = 1, H = 1, N = 1, myId = 0, unitLimit = 64; char myTeam = 'A';
    std::vector<uint8_t> ek; std::vector<int> ep;                         // edge kind / portal id per tile side
    std::unordered_map<int, std::vector<std::pair<int, int>>> pends;      // portal id -> canonical ends (tile, side N|W)
    std::vector<int> seenR, pearlR, emptyR, spawnR, inView;               // spawnR: next spawn attempt, -1 never, -2 unknown
    std::vector<int> body;                                                // own body, head first, -1 unknown
    std::unordered_map<int, News> allies, enemies;                         // heard or seen, by dragon id
    int sym = -1; bool symAlive[3] = {true, true, true}; int symChecks[3] = {0, 0, 0}; // 0 flip y, 1 flip x, 2 rotate 180
    std::vector<int> spawnSeenR;                                          // round at which spawnR was last read
    // ---- known maps (spawndb.hpp): candidates of our size, checked against every edge, spawn flag and countdown we see ----
    int sdbCand[16]; int nSdb = 0; int sdbIdx = -1; int sdbChecks = 0;
    bool sdbFam = false; int sdbFamN = 0;                                 // v4: a and b of one map left (mixture)
    bool sdbMulti[spawndb::COUNT];                                        // v4: the map has a second layout (range check)
    std::string sdbLog;                                                   // v4: recognition news for this turn's LOG line
    std::vector<int> gapLo, gapHi;                                        // spawn gap range per tile once the map is known
                                                                          // (family: the range all versions agree on, else 0)
    bool elimMap = false;                                                 // a known elimination-type map
    // ---- this turn ----
    int round = 0, L = 3, units = 1, dir = 0, head = -1, safeDir = -1; bool ok = false;
    std::vector<int> occId, headId, freeAt, bodyIdx; std::vector<uint8_t> occKind; // occKind: 0 none 1 own 2 ally 3 enemy
    std::vector<uint8_t> nearHead;   // 1 if another dragon's head is next to the tile (it may step there first)
    std::vector<int> gapMin;         // smallest observed gap between two spawn attempts of a tile (fountains), 0 unknown
    std::vector<Seen> vis;
    int nb[4] = {-1, -1, -1, -1}, nbKind[4] = {0, 0, 0, 0}, nbId[4] = {-1, -1, -1, -1};
    bool nbBlind[4] = {false, false, false, false}; // a known portal whose exit tile is out of view (vision does not cross portals)
    bool allyHeadInView = false; int enemyHeadsInView = 0;
    // ---- scratch ----
    std::vector<int> dist, distAlly, distEnemy, tmp, q, eReach, eReachLen;
    std::vector<Target> targets;
    double gpow[128], gpowE[128];

    // ---- geometry ----
    int wx(int x) const { x %= W; return x < 0 ? x + W : x; }
    int wy(int y) const { y %= H; return y < 0 ? y + H : y; }
    int stepT(int t, int d) const { return wy(t / W + DY[d]) * W + wx(t % W + DX[d]); }
    int adx(int a, int b) const { int d = std::abs(a % W - b % W); return std::min(d, W - d); }
    int ady(int a, int b) const { int d = std::abs(a / W - b / W); return std::min(d, H - d); }
    int cheb(int a, int b) const { return std::max(adx(a, b), ady(a, b)); }
    int manh(int a, int b) const { return adx(a, b) + ady(a, b); }
    int sdx(int a, int b) const { int d = b % W - a % W; if (d > W / 2) d -= W; else if (d < -(W / 2)) d += W; return d; }
    int sdy(int a, int b) const { int d = b / W - a / W; if (d > H / 2) d -= H; else if (d < -(H / 2)) d += H; return d; }
    // tile t lies behind the head of s (against its heading) (px8)
    bool behind(int shead, int shdir, int t) const { return sdx(shead, t) * DX[shdir] + sdy(shead, t) * DY[shdir] < 0; }
    double rnd(unsigned salt) const {
        uint32_t h = mix32((uint32_t)myId * 0x9E3779B1u ^ mix32((uint32_t)round * 0x85EBCA77u + salt * 0xC2B2AE3Du) ^ style::SALT ^ (uint32_t)(W * 131 + H));
        return (h >> 8) / 16777216.0;
    }

    void canonEnd(int t, int d, int& ct, int& side) const {
        if (d == 0) { ct = t; side = 0; } else if (d == 3) { ct = t; side = 3; }
        else if (d == 2) { ct = stepT(t, 2); side = 0; } else { ct = stepT(t, 1); side = 3; }
    }
    void setEdge(int t, int d, int tok) {
        uint8_t k = tok == -2 ? E_KELP : tok == -1 ? E_OPEN : E_PORTAL;
        ek[t * 4 + d] = k; ep[t * 4 + d] = k == E_PORTAL ? tok : -1;
        int u = stepT(t, d);
        ek[u * 4 + opp(d)] = k; ep[u * 4 + opp(d)] = k == E_PORTAL ? tok : -1;
        if (k == E_PORTAL) {
            int ct, side; canonEnd(t, d, ct, side);
            auto& e = pends[tok];
            for (auto& x : e) if (x.first == ct && x.second == side) return;
            if (e.size() < 2) e.push_back({ct, side});
        }
    }
    // destination across side d of tile t: tile, -1 kelp, -2 portal with unknown far end
    int across(int t, int d) const {
        uint8_t k = ek[t * 4 + d];
        if (k == E_KELP) return -1;
        if (k != E_PORTAL) return stepT(t, d);
        auto it = pends.find(ep[t * 4 + d]);
        if (it == pends.end() || it->second.size() < 2) return -2;
        int ct, side; canonEnd(t, d, ct, side);
        const std::pair<int, int>* other = nullptr;
        for (auto& x : it->second) if (!(x.first == ct && x.second == side)) other = &x;
        if (!other) return -2;
        if (d == 0 || d == 2) { if (other->second != 0) return -2; return d == 0 ? stepT(other->first, 0) : other->first; }
        if (other->second != 3) return -2;
        return d == 3 ? stepT(other->first, 3) : other->first;
    }

    // ---- known maps (spawn ranges only; geometry stays learned from vision) ----
    static int hexBit(const char* h, int i) { char c = h[i >> 2]; int v = c <= '9' ? c - '0' : c - 'a' + 10; return (v >> (i & 3)) & 1; }
    uint8_t sdbEdge(int m, int t, int side) const {   // kind of the north (side 0) or west (side 3) edge of tile t in map m
        const spawndb::MapInfo& M = spawndb::MAPS[m];
        if (hexBit(side == 0 ? M.hp : M.vp, t)) return E_PORTAL;
        return hexBit(side == 0 ? M.hk : M.vk, t) ? E_KELP : E_OPEN;
    }
    void sdbRange(int m, int t, int& lo, int& hi) const {
        const spawndb::MapInfo& M = spawndb::MAPS[m];
        int pi = M.spawn[t] - 48;
        if (pi > 0 && pi < M.nPal) { lo = M.pal[pi * 2]; hi = M.pal[pi * 2 + 1]; } else { lo = 0; hi = 0; }
    }
    // does countdown p (pearlIn, -1 = never spawns) read at this round fit map m at tile t? The spawn flag (as v3) and,
    // v4, for a two-layout map the gap range: countdowns tick at the start of every round from round 0 and redraw U[lo, hi]
    // at each attempt (rules/pearls.md), so p <= hi; the first attempt comes at round g0 - 1 >= lo - 1, and before it
    // p = g0 - 1 - round with g0 in [lo, hi] (checked on local replays: round-0 pearlIn = initial countdown - 1). Slack
    // hi/20 + 1 (lo/20 + 1) keeps a slightly re-estimated map file from being rejected; the ranges that tell a from b
    // differ far more (research/experiments/proxies-v3.md v4).
    bool sdbFits(int m, int t, int p) const {
        int lo, hi; sdbRange(m, t, lo, hi);
        if (hi <= 0 || p < 0) return hi <= 0 && p < 0;
        if (!sdbMulti[m]) return true;
        const int sHi = hi / 20 + 1, sLo = lo / 20 + 1;
        if (p > hi + sHi) return false;
        if (round < lo - 1 - sLo) { int g0 = p + round + 1; if (g0 < lo - sLo || g0 > hi + sHi) return false; }
        return true;
    }
    void sdbName(int m, std::string& out) const { out = spawndb::MAPS[m].name; for (char& c : out) if (c == ' ') c = '_'; }
    // maps that usually end by elimination (research/observations/top-summary-2026-09-29.md 2); versions share the type
    bool isElimMap(int m) const {
        const std::string nm = spawndb::MAPS[spawndb::MAPS[m].fam].name;
        return nm == "Default" || nm == "Devil" || nm == "Trophy" || nm == "Queen Of Spades" || nm.rfind("Prisoners Dilemma", 0) == 0;
    }
    void checkSdb(const int* win, const RoundBlock& rb) {
        if (sdbIdx >= 0 || nSdb == 0) return;
        for (int i = 0; i < 49; i++) {
            int t = win[i];
            for (int side : {0, 3}) {
                uint8_t k = ek[t * 4 + side]; if (k == E_UNK) continue;
                for (int c = 0; c < nSdb; c++) if (sdbEdge(sdbCand[c], t, side) != k) { sdbCand[c] = sdbCand[--nSdb]; c--; }
            }
            const int p = rb.tiles[i].pearlIn;   // spawn flag (p >= 0) and countdown range
            for (int c = 0; c < nSdb; c++) if (!sdbFits(sdbCand[c], t, p)) { sdbCand[c] = sdbCand[--nSdb]; c--; }
            sdbChecks++;
        }
        if (sdbChecks < 49) return;
        std::string nm;
        if (nSdb == 1) {
            sdbIdx = sdbCand[0]; sdbFam = false;
            const spawndb::MapInfo& M = spawndb::MAPS[sdbIdx];
            elimMap = isElimMap(sdbIdx);
            gapLo.assign(N, 0); gapHi.assign(N, 0);
            for (int t = 0; t < N; t++) { int pi = M.spawn[t] - 48; if (pi > 0 && pi < M.nPal) { gapLo[t] = M.pal[pi * 2]; gapHi[t] = M.pal[pi * 2 + 1]; } }
            sdbName(sdbIdx, nm); sdbLog = "px4 map " + nm + " r" + std::to_string(round);
            return;
        }
        if (nSdb == 0) {
            if (sdbFam) { sdbFam = false; elimMap = false; }
            sdbLog = "px4 map none r" + std::to_string(round);
            return;
        }
        // 2+ left: if they are the a and b layouts of one map (same geometry), use the ranges they agree on
        const int fam = spawndb::MAPS[sdbCand[0]].fam;
        for (int c = 1; c < nSdb; c++) if (spawndb::MAPS[sdbCand[c]].fam != fam) return;
        if (sdbFam && sdbFamN == nSdb) return;
        sdbFam = true; sdbFamN = nSdb; elimMap = isElimMap(fam);
        gapLo.assign(N, 0); gapHi.assign(N, 0);
        for (int t = 0; t < N; t++) {
            int lo0, hi0; sdbRange(sdbCand[0], t, lo0, hi0);
            bool same = true;
            for (int c = 1; c < nSdb && same; c++) { int lo, hi; sdbRange(sdbCand[c], t, lo, hi); same = lo == lo0 && hi == hi0; }
            if (same) { gapLo[t] = lo0; gapHi[t] = hi0; }
        }
        sdbName(fam, nm); sdbLog = "px4 fam " + nm + " n" + std::to_string(nSdb) + " r" + std::to_string(round);
    }

    // ---- ingest one round block ----
    void ingest(const RoundBlock& rb) {
        round = rb.round; L = rb.length; units = rb.unitCount; dir = rb.dir; ok = rb.ok;
        safeDir = -1;
        if (!ok) return;
        int win[49];
        for (int i = 0; i < 49; i++) win[i] = wy(rb.tiles[i].y) * W + wx(rb.tiles[i].x);
        head = win[24];
        for (int i = 0; i < 49; i++) {
            int t = win[i]; const TileObs& o = rb.tiles[i];
            seenR[t] = round; inView[t] = round;
            if (o.pearl) pearlR[t] = round; else emptyR[t] = round;
            int ns = o.pearlIn < 0 ? -1 : round + o.pearlIn;
            if (ns > 0 && spawnR[t] > 0 && ns > spawnR[t] && spawnSeenR[t] >= spawnR[t] - 1 && spawnR[t] <= round) {
                int gap = ns - spawnR[t]; if (gap > 0 && (gapMin[t] == 0 || gap < gapMin[t])) gapMin[t] = gap;
            }
            spawnR[t] = ns; spawnSeenR[t] = round;
        }
        for (int r = 0; r < 7; r++) for (int c = 0; c < 7; c++) {
            int t = win[r * 7 + c];
            setEdge(t, 0, rb.hedge[r][c]); setEdge(t, 2, rb.hedge[r + 1][c]);
            setEdge(t, 3, rb.vedge[r][c]); setEdge(t, 1, rb.vedge[r][c + 1]);
        }
        checkSdb(win, rb);
        updateSymmetry(win);
        if (sym >= 0) applyMirror(win);
        // dragons in view
        std::fill(occId.begin(), occId.end(), -1); std::fill(headId.begin(), headId.end(), -1);
        std::fill(freeAt.begin(), freeAt.end(), 0); std::fill(occKind.begin(), occKind.end(), (uint8_t)0);
        std::fill(bodyIdx.begin(), bodyIdx.end(), -1); std::fill(nearHead.begin(), nearHead.end(), (uint8_t)0);
        vis.clear();
        for (auto& p : rb.parts) {
            int t = wy(p.y) * W + wx(p.x);
            occId[t] = p.id;
            if (p.head) headId[t] = p.id;
            Seen* s = nullptr; for (auto& v : vis) if (v.id == p.id) s = &v;
            if (!s) { vis.push_back(Seen{}); s = &vis.back(); s->id = p.id; s->team = p.team; }
            s->nVis++;
            if (p.head) { s->head = t; s->hdir = p.dir; }
        }
        for (auto& s : vis) {
            if (s.head < 0) continue;
            // walk from the head: the next segment is the part whose facing points at the current tile
            std::vector<int> segT, segD;
            for (auto& p : rb.parts) if (p.id == s.id && !p.head) { segT.push_back(wy(p.y) * W + wx(p.x)); segD.push_back(p.dir); }
            std::vector<char> used(segT.size(), 0);
            int cur = s.head, lastDir = s.hdir; s.chain.push_back(cur);
            for (;;) {
                int nx = -1;
                for (size_t i = 0; i < segT.size(); i++) if (!used[i] && stepT(segT[i], segD[i]) == cur) { nx = (int)i; break; }
                if (nx < 0) break;
                used[nx] = 1; cur = segT[nx]; lastDir = segD[nx]; s.chain.push_back(cur);
            }
            if ((int)s.chain.size() == s.nVis && s.nVis >= 2) {
                int behindT = stepT(cur, opp(lastDir));
                if (inView[behindT] == round && occId[behindT] != s.id) s.tailSeen = true;
            }
        }
        // own body: visible chain + remembered segments beyond it
        std::vector<int> nbody;
        for (auto& s : vis) if (s.id == myId) nbody = s.chain;
        if (nbody.empty()) nbody.push_back(head);
        for (int t : body) { if (t < 0) break; if (std::find(nbody.begin(), nbody.end(), t) == nbody.end()) nbody.push_back(t); if ((int)nbody.size() >= L) break; }
        while ((int)nbody.size() > L) nbody.pop_back();
        while ((int)nbody.size() < L) nbody.push_back(-1);
        body = nbody;
        for (int i = 0; i < L; i++) if (body[i] >= 0) { bodyIdx[body[i]] = i; occKind[body[i]] = 1; }
        for (auto& pp : rb.parts) if (pp.id == myId) occKind[wy(pp.y) * W + wx(pp.x)] = 1; // own parts off the chain block too
        // other dragons: time until their segments are gone (+1 in case they eat)
        for (auto& s : vis) {
            if (s.id == myId) continue;
            uint8_t kind = s.team == myTeam ? 2 : 3;
            for (auto& p : rb.parts) if (p.id == s.id) { int t = wy(p.y) * W + wx(p.x); occKind[t] = kind; freeAt[t] = NEVER_FREE; }
            if (s.tailSeen) for (int i = 0; i < (int)s.chain.size(); i++) freeAt[s.chain[i]] = s.nVis - i + 1;
            if (s.head >= 0) {
                News& nw = kind == 2 ? allies[s.id] : enemies[s.id];
                int keep = (!s.tailSeen && nw.round >= round - 3) ? std::max(nw.len, s.nVis) : s.nVis;
                nw.round = round; nw.t = s.head; nw.len = keep;
            }
        }
        for (auto& s2 : vis) if (s2.id != myId && s2.head >= 0) for (int d = 0; d < 4; d++) { int u = across(s2.head, d); if (u >= 0) nearHead[u] = 1; }
        // sonar inbox
        for (uint64_t v : rb.msgs) {
            int kind, id, rr, t, len;
            if (!decode(v, kind, id, rr, t, len)) continue;
            if (id == myId && kind != 2) continue;
            News& nw = kind == 2 ? enemies[id] : allies[id];
            if (rr >= nw.round) { nw.round = rr; nw.t = t; nw.len = len; }
        }
        // lengths of visible dragons: raised to a recent report when the tail is out of view (px8)
        allyHeadInView = false; enemyHeadsInView = 0;
        for (auto& s : vis) {
            s.len = s.nVis;
            if (s.id == myId) { s.len = L; continue; }
            if (s.head >= 0) { if (s.team == myTeam) allyHeadInView = true; else enemyHeadsInView++; }
            if (s.tailSeen) continue;
            auto& book = s.team == myTeam ? allies : enemies;
            auto it = book.find(s.id);
            if (it != book.end() && it->second.round >= round - 3) s.len = std::max(s.len, it->second.len);
        }
        // neighbours
        for (int d = 0; d < 4; d++) {
            int u = across(head, d); nb[d] = u; nbId[d] = -1; nbBlind[d] = false;
            if (u == -1) { nbKind[d] = NB_KELP; continue; }
            if (u == -2) { nbKind[d] = NB_PORTAL_UNKNOWN; continue; }
            if (bodyIdx[u] >= 0 || occKind[u] == 1) { nbKind[d] = NB_OWN; continue; }
            if (occKind[u] == 0) {
                nbKind[d] = NB_FREE;
                if (ek[head * 4 + d] == E_PORTAL && inView[u] != round) {
                    nbBlind[d] = true;
                    // an ally heard to be right there a moment ago: treat the exit as taken
                    for (auto& [id, nw] : allies) if (id != myId && nw.round >= round - 1 && nw.t >= 0 && manh(nw.t, u) <= 1) nbKind[d] = NB_ALLY_HEAD;
                }
                continue;
            }
            nbId[d] = occId[u];
            bool hd = headId[u] >= 0;
            nbKind[d] = occKind[u] == 2 ? (hd ? NB_ALLY_HEAD : NB_ALLY) : (hd ? NB_ENEMY_HEAD : NB_ENEMY);
        }
        // the side opposite our facing is always the neck, also when a portal lies between head and neck
        if (L >= 2) { nbKind[opp(dir)] = NB_OWN; nbId[opp(dir)] = -1; }
        for (int k = 0; k < 4; k++) { int d = (dir + (k == 0 ? 0 : k == 1 ? 3 : k == 2 ? 1 : 2)) & 3; if (nbKind[d] == NB_FREE) { safeDir = d; break; } }
    }

    // ---- symmetry: maps are mirrored or rotated, and mirrored tiles share one pearl countdown (rules/pearls.md) ----
    int mirrorT(int t, int h) const {
        int x = t % W, y = t / W;
        if (h == 0) return (H - 1 - y) * W + x;
        if (h == 1) return y * W + (W - 1 - x);
        return (H - 1 - y) * W + (W - 1 - x);
    }
    static int mirrorD(int d, int h) { if (h == 0) return (d == 0 || d == 2) ? opp(d) : d; if (h == 1) return (d == 1 || d == 3) ? opp(d) : d; return opp(d); }
    void updateSymmetry(const int* win) {
        if (sym >= 0) return;
        int alive = 0;
        for (int h = 0; h < 3; h++) {
            if (!symAlive[h]) continue;
            for (int i = 0; i < 49 && symAlive[h]; i++) {
                int t = win[i], m = mirrorT(t, h);
                if (m == t || seenR[m] < 0) continue;
                for (int d = 0; d < 4; d++) {
                    uint8_t a = ek[t * 4 + d], b = ek[m * 4 + mirrorD(d, h)];
                    if (a == E_UNK || b == E_UNK) continue;
                    if ((a == E_KELP) != (b == E_KELP) || (a == E_PORTAL) != (b == E_PORTAL)) { symAlive[h] = false; break; }
                    symChecks[h]++;
                }
                if (!symAlive[h]) break;
                if (spawnR[t] != -2 && spawnR[m] != -2 && (spawnR[t] == -1) != (spawnR[m] == -1)) { symAlive[h] = false; break; }
                if (spawnR[t] > 0 && spawnR[m] > 0) {
                    // one shared countdown: two readings taken before either predicted attempt must agree
                    bool comparable = std::max(spawnSeenR[t], spawnSeenR[m]) < std::min(spawnR[t], spawnR[m]);
                    if (comparable && spawnR[t] != spawnR[m]) { symAlive[h] = false; break; }
                    if (comparable) symChecks[h] += 2;
                }
            }
            if (symAlive[h]) alive++;
        }
        if (alive == 1) { for (int h = 0; h < 3; h++) if (symAlive[h] && symChecks[h] >= 12) sym = h; }
        else if (alive > 1 && round >= 40) {
            int b = -1; for (int h = 0; h < 3; h++) if (symAlive[h] && (b < 0 || symChecks[h] > symChecks[b])) b = h;
            if (b >= 0 && symChecks[b] >= 40) sym = b;
        }
    }
    void applyMirror(const int* win) {
        for (int i = 0; i < 49; i++) {
            int t = win[i], m = mirrorT(t, sym);
            if (m == t) continue;
            if (spawnSeenR[m] < round) { spawnR[m] = spawnR[t]; spawnSeenR[m] = round; }
            for (int d = 0; d < 4; d++) {
                int md = mirrorD(d, sym);
                if (ek[m * 4 + md] != E_UNK) continue;
                uint8_t k = ek[t * 4 + d]; if (k == E_UNK) continue;
                int u = stepT(m, md);
                ek[m * 4 + md] = k; ek[u * 4 + opp(md)] = k;
                ep[m * 4 + md] = -1; ep[u * 4 + opp(md)] = -1; // a mirrored portal: far end unknown until seen
            }
        }
    }

    // ---- sonar ----
    uint64_t encode(int kind, int id, int rr, int t, int len) const {
        uint64_t tag = 0xB5u ^ (style::SALT & 0xFFu);
        uint64_t team = myTeam == 'B' ? 1 : 0;
        uint64_t x = (uint64_t)(t % W) & 127, y = (uint64_t)(t / W) & 127;
        uint64_t v = (tag << 56) | (team << 55) | ((uint64_t)(kind & 3) << 53) | ((uint64_t)(id & 4095) << 41) |
                     ((uint64_t)(rr & 511) << 32) | (x << 25) | (y << 18) | ((uint64_t)std::min(len, 255) << 10);
        uint64_t chk = mix32((uint32_t)(v >> 32) ^ mix32((uint32_t)v)) & 1023;
        return v | chk;
    }
    bool decode(uint64_t v, int& kind, int& id, int& rr, int& t, int& len) const {
        uint64_t tag = 0xB5u ^ (style::SALT & 0xFFu);
        if ((v >> 56) != tag) return false;
        uint64_t body_ = v & ~(uint64_t)1023;
        if ((mix32((uint32_t)(body_ >> 32) ^ mix32((uint32_t)body_)) & 1023) != (v & 1023)) return false;
        if ((int)((v >> 55) & 1) != (myTeam == 'B' ? 1 : 0)) return false;
        kind = (int)((v >> 53) & 3); id = (int)((v >> 41) & 4095); int r9 = (int)((v >> 32) & 511);
        int x = (int)((v >> 25) & 127), y = (int)((v >> 18) & 127); len = (int)((v >> 10) & 255);
        if (x >= W || y >= H || len < 2) return false;
        int back = ((round & 511) - r9 + 512) & 511;
        if (back > 60) return false;
        rr = round - back; t = y * W + x;
        return true;
    }
    void kingInfo(int& kid, int& klen, int& kt, int& kround) const {
        kid = myId; klen = L; kt = head; kround = round;
        for (auto& [id, nw] : allies) {
            if (nw.round < round - 40 || nw.t < 0) continue;
            if (nw.len > klen || (nw.len == klen && id < kid)) { kid = id; klen = nw.len; kt = nw.t; kround = nw.round; }
        }
    }
    void sendSonar(Writer& w) {
        if (!style::SONAR_ALL) return;
        uint64_t own = encode(0, myId, round, head, L);
        uint64_t alt = own;
        if (style::KING_GATHER && round >= style::SAC_START - 60) {
            int kid, klen, kt, kr; kingInfo(kid, klen, kt, kr);
            if (kid != myId) alt = encode(1, kid, kr, kt, klen);
        }
        if (style::SONAR_ENEMY || (elimMap && style::ELIM_MAP_HUNT_W > 0)) {
            int best = -1, bd = 99;
            for (auto& s : vis) if (s.team != myTeam && s.head >= 0) { int d0 = manh(s.head, head); if (d0 < bd) { bd = d0; best = s.id; } }
            if (best >= 0) { auto& s = *std::find_if(vis.begin(), vis.end(), [&](const Seen& x) { return x.id == best; }); alt = encode(2, s.id, round, s.head, s.len); }
        }
        for (int d = 0; d < 4; d++) w.sonar(d, ((round + d) & 1) ? alt : own);
    }

    // ---- search helpers ----
    // own segment i is enterable at step st iff st > L - i; another dragon's segment once st > freeAt
    int eatPad = 0; // long dragons among visible pearls: our tail stays while we eat, so own segments free up later
    bool passable(int u, int st) const {
        int bi = bodyIdx[u];
        if (bi >= 0) return st > L - bi + eatPad;
        if (occKind[u] == 1) return false;
        if (occKind[u] >= 2) return st > freeAt[u];
        return true;
    }
    // distances from s, which is entered at step 1; bfsPortal = steps to the nearest portal with an unknown far end
    int bfsPortal = 99;
    void bfs(int s, int maxd, std::vector<int>& d) {
        std::fill(d.begin(), d.end(), -1);
        q.clear(); q.push_back(s); d[s] = 0; bfsPortal = 99;
        for (size_t qi = 0; qi < q.size(); qi++) {
            int t = q[qi], k = d[t];
            if (k >= maxd) continue;
            for (int dd = 0; dd < 4; dd++) {
                int u = across(t, dd);
                if (u == -2 && k + 1 < bfsPortal) bfsPortal = k + 1;
                if (u < 0 || d[u] >= 0 || !passable(u, k + 2)) continue;
                d[u] = k + 1; q.push_back(u);
            }
        }
    }
    // free tiles reachable from s (entered at step 1), capped; an unknown portal exit counts as open space
    int room(int s, int cap) {
        std::fill(tmp.begin(), tmp.end(), -1);
        q.clear(); q.push_back(s); tmp[s] = 0;
        for (size_t qi = 0; qi < q.size(); qi++) {
            int t = q[qi], k = tmp[t];
            for (int dd = 0; dd < 4; dd++) {
                int u = across(t, dd);
                if (u == -2) return cap;
                if (u < 0 || tmp[u] >= 0 || !passable(u, k + 2)) continue;
                if (style::ROOM_HEADS && k + 2 <= 2 && nearHead[u]) continue; // another head may take it before we arrive
                tmp[u] = k + 1; q.push_back(u);
                if ((int)q.size() >= cap) return cap;
            }
        }
        return (int)q.size();
    }
    // Survival lookahead: can we make `depth` more single steps after entering tile s? Our body is simulated exactly
    // (tail stays when a visible pearl is eaten); other bodies are static until freeAt; heads block.
    // v3: a dead end is survivable when we arrive long enough to split off a stub (the child leaves from the tail) and
    // have eaten on the way (fountain corridors are pearl pumps); a known fountain tile counts as a pearl on arrival.
    std::vector<int> sb; std::vector<uint8_t> onBody; long long dfsNodes = 0; bool stubOk = false;
    bool survive(int s, int lastDir, int depth) {
        sb.clear();
        for (int t : body) { if (t < 0) break; sb.push_back(t); }
        if ((int)onBody.size() != N) onBody.assign(N, 0);
        for (int t : sb) onBody[t]++;
        dfsNodes = 0; stubOk = style::STUB_SURVIVE && units < unitLimit - 1;
        bool ok2 = step(s, lastDir, 1, depth + 1);
        for (int t : sb) onBody[t]--;
        return ok2;
    }
    bool step(int u, int lastDir, int st, int left) {
        if (++dfsNodes > 4000) return true;             // budget: unknown counts as alive
        if (onBody[u] || headId[u] >= 0) return false;  // own body now, or another head
        if (occKind[u] >= 2 && st <= freeAt[u]) return false;
        if (occKind[u] == 1 && bodyIdx[u] < 0) return false;
        if (left <= 1) return true;
        bool eat = (pearlR[u] == round && inView[u] == round) || ((sdbIdx >= 0 || sdbFam) && gapHi[u] > 0 && gapHi[u] <= style::FOUNTAIN_SIM_GAP && st >= 2);
        sb.insert(sb.begin(), u); onBody[u]++;
        int tail = -1;
        if (!eat) { tail = sb.back(); sb.pop_back(); onBody[tail]--; }
        bool res = false;
        for (int d = 0; d < 4 && !res; d++) {
            if (d == opp(lastDir)) continue;
            int v = across(u, d);
            if (v == -2) { res = true; break; }          // an unknown portal: somewhere else, count as open
            if (v < 0) continue;
            res = step(v, d, st + 1, left - 1);
        }
        if (!res && stubOk && (int)sb.size() >= 4 && (int)sb.size() - L >= style::STUB_GAIN) res = true; // stub escape pays
        if (!eat) { sb.push_back(tail); onBody[tail]++; }
        sb.erase(sb.begin()); onBody[u]--;
        return res;
    }

    // path distance (<= 3) from the nearest visible enemy head to every tile, and that enemy's length
    void enemyReach() {
        std::fill(eReach.begin(), eReach.end(), 99);
        for (auto& s : vis) {
            if (s.team == myTeam || s.head < 0) continue;
            std::fill(tmp.begin(), tmp.end(), -1);
            q.clear(); q.push_back(s.head); tmp[s.head] = 0;
            for (size_t qi = 0; qi < q.size(); qi++) {
                int t = q[qi], k = tmp[t];
                if (k < eReach[t]) { eReach[t] = k; eReachLen[t] = s.len; }
                if (k >= 3) continue;
                for (int dd = 0; dd < 4; dd++) {
                    int u = across(t, dd);
                    if (u < 0 || tmp[u] >= 0) continue;
                    if (occKind[u] != 0 && u != head) continue;
                    tmp[u] = k + 1; q.push_back(u);
                }
            }
        }
    }
    // path distance from other visible heads (bodies ignored), for pearl contention: allies and enemies apart
    void multiBfs(std::vector<int>& d, bool allyHeads) {
        std::fill(d.begin(), d.end(), -1);
        q.clear();
        for (auto& s : vis) if (s.id != myId && s.head >= 0 && (s.team == myTeam) == allyHeads && d[s.head] < 0) { d[s.head] = 0; q.push_back(s.head); }
        if (allyHeads) for (auto& [id, nw] : allies) if (id != myId && nw.round >= round - 1 && nw.t >= 0 && d[nw.t] < 0) { d[nw.t] = 0; q.push_back(nw.t); }
        for (size_t qi = 0; qi < q.size(); qi++) {
            int t = q[qi], k = d[t];
            if (k >= 12) continue;
            for (int dd = 0; dd < 4; dd++) { int u = across(t, dd); if (u < 0 || d[u] >= 0) continue; d[u] = k + 1; q.push_back(u); }
        }
    }
    std::vector<uint8_t> leave; // late: pearls next to a clearly longer ally's head are left for it (2: a big ally's or the king's)
    void markLeave() {
        if ((int)leave.size() != N) leave.assign(N, 0); else std::fill(leave.begin(), leave.end(), (uint8_t)0);
        if (!style::LEAVE_PEARLS) return;
        int from = std::min(style::SAC_START, style::R3_START) - 20;
        if (round >= from) {
            for (auto& v : vis) {
                if (v.id == myId || v.team != myTeam || v.head < 0 || v.len < L + 3) continue;
                bool big = v.len >= style::KING_MIN_LEN;             // px8: any visible big ally, known king or not
                if (!big && round < style::SAC_START) continue;
                const int R = big ? style::KING_RESERVE_R : 2; const uint8_t lvl = big ? 2 : 1;
                for (int dy = -R; dy <= R; dy++) for (int dx = -R; dx <= R; dx++) {
                    if (std::abs(dx) + std::abs(dy) > R) continue;
                    uint8_t& c = leave[wy(v.head / W + dy) * W + wx(v.head % W + dx)];
                    if (c < lvl) c = lvl;
                }
            }
        }
        if (style::KING_RESERVE_R > 0 && style::KING_GATHER && round >= style::SAC_START - 20) {
            int kid, klen, kt, kr; kingInfo(kid, klen, kt, kr);
            if (kid != myId && klen >= style::KING_MIN_LEN && klen >= L + 3) {
                const Seen* ks = seenById(kid);
                if (ks && ks->head >= 0) kt = ks->head; else if (kr < round - 1) kt = -1;
                if (kt >= 0) {
                    const int R = style::KING_RESERVE_R;
                    for (int dy = -R; dy <= R; dy++) for (int dx = -R; dx <= R; dx++) {
                        if (std::abs(dx) + std::abs(dy) > R) continue;
                        leave[wy(kt / W + dy) * W + wx(kt % W + dx)] = 2;
                    }
                }
            }
        }
    }
    // expected pearl at a known spawn tile that is out of view (expectedPearlIn). v4: while a and b of the map are both
    // left (sdbFam), the mean over them (equal prior; the server plays each about half)
    double expectedPearl(int t) const {
        if (sdbIdx >= 0) return expectedPearlIn(t, gapLo[t], gapHi[t]);
        if (!sdbFam || nSdb <= 0) return 0.0;
        double s = 0;
        for (int c = 0; c < nSdb; c++) { int lo, hi; sdbRange(sdbCand[c], t, lo, hi); s += expectedPearlIn(t, lo, hi); }
        return s / nSdb;
    }
    // tile t with gap range [lo, hi]: the last countdown we read (or its mirror's) says when the tile tried to spawn; a
    // pearl that appeared then may still wait, or a later one may have appeared after it was eaten
    double expectedPearlIn(int t, int lo, int hi) const {
        if (hi <= 0) return 0.0;
        double g = 0.5 * (lo + hi);
        if (spawnR[t] >= 0 && spawnSeenR[t] >= 0) {
            if (spawnR[t] > round) return 0.0;          // a known future attempt (the spawn target covers it)
            int since = round - spawnR[t];
            double first = style::EXP_FIRST * std::pow(style::EXP_DECAY, since);
            double regen = std::min(1.0, since / g) * style::EXP_REGEN;
            return std::max(first, regen);
        }
        if (spawnR[t] == -1) return 0.0;
        // never read: the first attempt comes at a uniform time in [lo, hi] (assumption)
        return std::min(1.0, (round + 1.0) / hi) * style::EXP_UNSEEN;
    }
    void buildTargets() {
        targets.clear();
        markLeave();
        const bool know = sdbIdx >= 0 || sdbFam;
        for (int t = 0; t < N; t++) {
            double v = 0; int sp = -1; bool ex = false;
            if (pearlR[t] >= 0 && pearlR[t] > emptyR[t]) { int age = round - pearlR[t]; v = age == 0 ? 1.0 : 0.8 * std::pow(0.97, age); }
            if (spawnR[t] > round && spawnR[t] - round <= 40 && !(pearlR[t] == round)) { double s = 0.7; if (s > v) { v = s; sp = spawnR[t]; } }
            if (style::FOUNTAIN_V > 0 && gapMin[t] > 0 && gapMin[t] <= 40 && inView[t] != round && round - seenR[t] >= gapMin[t] && style::FOUNTAIN_V > v) { v = style::FOUNTAIN_V; sp = -1; }
            if (know && inView[t] != round && !(pearlR[t] >= 0 && pearlR[t] > emptyR[t])) {
                double e = style::SPAWN_W * expectedPearl(t);
                if (e > v) { v = e; sp = -1; ex = true; }
            }
            if (v > 0.05 && leave[t]) v *= leave[t] == 2 ? style::RESERVE_MULT : 0.15;
            if (v > 0.05) targets.push_back({t, v, sp, ex});
        }
    }
    const Seen* seenById(int id) const { for (auto& s : vis) if (s.id == id) return &s; return nullptr; }

    // ---- decisions ----
    int dieDirV = -1, feedT = -1;
    int dieDir() const { return dieDirV >= 0 ? dieDirV : opp(dir); }
    // trapped: a random blocked direction that is not a head (kelp, own or ally body)
    int trappedDir() const {
        int cand[4], n = 0;
        for (int d = 0; d < 4; d++) if (nbKind[d] == NB_KELP || nbKind[d] == NB_OWN || nbKind[d] == NB_ALLY || nbKind[d] == NB_ENEMY) cand[n++] = d;
        if (!n) return opp(dir);
        return cand[std::min(n - 1, (int)(rnd(61) * n))];
    }
    Plan die(int method, char tag) { Plan p; p.kind = Plan::DIE; p.method = method; p.tag = tag; return p; }

    // a target worth any small piece: at least RAM_BIG_LEN long and at least twice our length
    bool isBig(int el) const { return el >= style::RAM_BIG_LEN && el >= 2 * L; }
    // top rule R4 (research/observations/top-decisions.md, b1 leaves): with an ally head in view a small piece trades with an
    // enemy as long or longer; alone it rams only longer enemies
    double ramP(int el) const {
        if (isBig(el)) return style::RAM_BIG_ADJ;
        double p;
        if (allyHeadInView) p = el >= L ? style::R4_ALLY_GE : (enemyHeadsInView <= 1 ? style::R4_ALLY_LT1 : style::R4_ALLY_LT);
        else p = el > L ? style::R4_SOLO_GT : el == L ? style::R4_SOLO_EQ : style::R4_SOLO_LT;
        return std::min(0.97, p * style::RAM_SCALE);
    }
    int enemyLen(int id) const { const Seen* e = seenById(id); return e ? e->len : 2; }
    bool tryRam(Plan& out) {
        if (L > style::RAM_MAX_LEN || units < style::RAM_MIN_UNITS) return false;
        // one step
        for (int d = 0; d < 4; d++) {
            if (nbKind[d] != NB_ENEMY_HEAD) continue;
            if (rnd(11 + d) < ramP(enemyLen(nbId[d]))) { out.kind = Plan::MOVE; out.dirs = std::string(1, DIRCH[d]); out.tag = 'R'; return true; }
        }
        if (L < 3) return false;
        // two steps through a free tile (the second step costs one segment)
        for (int d1 = 0; d1 < 4; d1++) {
            if (nbKind[d1] != NB_FREE) continue;
            int u1 = nb[d1];
            for (int d2 = 0; d2 < 4; d2++) {
                if (d2 == opp(d1)) continue;
                int u2 = across(u1, d2);
                if (u2 < 0 || headId[u2] < 0 || occKind[u2] != 3) continue;
                int el = enemyLen(headId[u2]);
                double p = isBig(el) ? style::RAM_BIG_S2 : ramP(el) * style::R4_S2;
                if (rnd(31 + d1 * 4 + d2) < p) { out.kind = Plan::MOVE; out.dirs = std::string(1, DIRCH[d1]) + DIRCH[d2]; out.tag = 'S'; return true; }
            }
        }
        if (L < 4 || (style::R4_S3 <= 0 && style::RAM_BIG_S3 <= 0)) return false;
        for (int d1 = 0; d1 < 4; d1++) {
            if (nbKind[d1] != NB_FREE) continue;
            int u1 = nb[d1];
            for (int d2 = 0; d2 < 4; d2++) {
                if (d2 == opp(d1)) continue;
                int u2 = across(u1, d2);
                if (u2 < 0 || occKind[u2] != 0 || u2 == head) continue;
                for (int d3 = 0; d3 < 4; d3++) {
                    if (d3 == opp(d2)) continue;
                    int u3 = across(u2, d3);
                    if (u3 < 0 || headId[u3] < 0 || occKind[u3] != 3) continue;
                    int el = enemyLen(headId[u3]);
                    if (rnd(71 + d1 * 16 + d2 * 4 + d3) < (isBig(el) ? style::RAM_BIG_S3 : ramP(el) * style::R4_S3)) {
                        out.kind = Plan::MOVE; out.dirs = std::string(1, DIRCH[d1]) + DIRCH[d2] + DIRCH[d3]; out.tag = 'T'; return true;
                    }
                }
            }
        }
        return false;
    }

    // free tiles around our tail, where a split child's head would start (its neck, our second-last segment, excluded);
    // current occupancy is treated as static; -1 when the tail is not known
    int childRoom(int cap) {
        if (L < 2 || body[L - 1] < 0) return -1;
        int tail = body[L - 1];
        std::fill(tmp.begin(), tmp.end(), -1);
        q.clear(); tmp[tail] = 0;
        for (int d = 0; d < 4; d++) {
            int u = across(tail, d);
            if (u == -2) return cap;
            if (u < 0 || tmp[u] >= 0 || occKind[u] != 0 || bodyIdx[u] >= 0) continue;
            tmp[u] = 1; q.push_back(u);
        }
        for (size_t qi = 0; qi < q.size() && (int)q.size() < cap; qi++) {
            int t = q[qi];
            for (int d = 0; d < 4; d++) {
                int u = across(t, d);
                if (u == -2) return cap;
                if (u < 0 || tmp[u] >= 0 || occKind[u] != 0 || bodyIdx[u] >= 0) continue;
                tmp[u] = tmp[t] + 1; q.push_back(u);
                if ((int)q.size() >= cap) break;
            }
        }
        return (int)q.size();
    }

    // two-step sprint onto a visible pearl that another head is also close to, or through two pearls in a row
    bool trySprintEat(Plan& out) {
        if (style::SPRINT_EAT_P <= 0 || L < 4 || L > style::SPRINT_EAT_MAX_LEN) return false;
        for (int d1 = 0; d1 < 4; d1++) {
            if (nbKind[d1] != NB_FREE || nbBlind[d1]) continue;
            int u1 = nb[d1];
            bool p1 = pearlR[u1] == round;
            for (int d2 = 0; d2 < 4; d2++) {
                if (d2 == opp(d1)) continue;
                int u2 = across(u1, d2);
                if (u2 < 0 || u2 == head || occKind[u2] != 0 || inView[u2] != round || pearlR[u2] != round) continue;
                bool contested = p1;
                for (auto& v : vis) if (v.id != myId && v.head >= 0 && manh(v.head, u2) <= 2) contested = true;
                if (!contested) continue;
                if (rnd(41 + d1 * 4 + d2) >= style::SPRINT_EAT_P) continue;
                if (room(u2, L + 3) < L + 3) continue;   // not into a pocket
                out.kind = Plan::MOVE; out.dirs = std::string(1, DIRCH[d1]) + DIRCH[d2]; out.tag = 'E';
                return true;
            }
        }
        return false;
    }

    // top teams split length-4 pieces less once the team is large (top-decisions.md c: 38-43% up to 31 units, 23% from 32)
    double crowdSplit() const { return units >= style::CROWD_UNITS2 ? style::CROWD_MULT2 : units >= style::CROWD_UNITS ? style::CROWD_MULT : 1.0; }
    bool wantSplit(int& c) {
        if (units >= unitLimit - style::UNIT_SLACK || L < 4) return false;
        { int cr = childRoom(style::CHILD_ROOM); if (cr >= 0 && cr < style::CHILD_ROOM) return false; }
        if (round < style::GROW_START) {
            c = L >= style::HALF_MIN_LEN ? L / 2 : 2;
            double p = style::SPLIT_P_EARLY;
            if (enemyHeadsInView > 0) p = std::min(0.95, p * style::SPLIT_ENEMY_MULT);   // top: more splits with enemy heads in view
            return rnd(5) < p * crowdSplit();
        }
        // one grower per neighbourhood: the longest dragon we see or hear of within KING_RADIUS keeps growing
        bool localKing = true;
        for (auto& v : vis) if (v.id != myId && v.team == myTeam && v.head >= 0 && (v.len > L || (v.len == L && v.id < myId))) localKing = false;
        for (auto& [id, nw] : allies) if (id != myId && nw.round >= round - 2 && nw.t >= 0 && (nw.len > L || (nw.len == L && id < myId)) && manh(nw.t, head) <= style::KING_RADIUS) localKing = false;
        if (L >= style::GROWER_LEN) {
            if (L > style::HALVE_MAX_LEN || localKing) return false;
            c = L / 2;                           // a mid-size dragon with a longer ally nearby halves
            return rnd(6) < style::SPLIT_P_MID;
        }
        if (localKing && rnd(7) < style::GROW_P) return false; // a length-4 local king starts growing (gradually)
        c = 2;
        return rnd(5) < (round >= style::SAC_START ? style::SPLIT_P_LATE : style::SPLIT_P_MID) * crowdSplit();
    }

    bool wantSacrifice() {
        const int start = std::min(style::SAC_START, style::R3_START);
        if (round < start || round > 496 || units <= style::SAC_MIN_UNITS) return false;
        bool small = L <= style::SAC_MAX_LEN;
        bool mid = !small && round >= style::SAC2_START && L <= style::SAC2_MAX_LEN;
        if (!small && !mid) return false;
        const bool conv = round >= style::SAC_START;     // the style's own conversion window (v2 rules, px8 front feeding)
        double ramp = conv ? std::min(1.0, (round - style::SAC_START + 1) / (double)style::SAC_RAMP) : 0.0;
        int kid = -1, klen = 0, kt = -1, kr = -1;
        if (style::KING_GATHER) { kingInfo(kid, klen, kt, kr); if (kid == myId) return false; if (klen < style::KING_MIN_LEN) kid = -1; }
        double best = 0;
        for (auto& s : vis) {
            if (s.id == myId || s.team != myTeam || s.head < 0) continue;
            int al = s.len, c = cheb(s.head, head);
            if (al <= L) continue;
            double q = 0;
            if (conv) {
                int margin = round >= style::MERGE_START ? 1 : style::SAC2_MARGIN; // late: merge into any longer neighbour
                if (!(mid && al < L + margin)) {
                    bool bigRecv = al >= std::max(style::BIG_RECV_LEN, 2 * L) || (mid && al >= L + margin);
                    if (c <= 2 && bigRecv) q = small ? style::SAC_NEAR_P : style::SAC2_P;
                    else if (c <= style::SAC_RECV_DIST) q = small ? style::SAC_P : 0.0;
                    if (style::KING_GATHER && s.id == kid && manh(s.head, head) <= style::KING_SAC_DIST) q = std::max(q, style::SAC_KING_P);
                    // px8: feed from the front, where the receiver's head takes the pearls next
                    if ((bigRecv || (style::KING_GATHER && s.id == kid)) && c <= 2 && !behind(s.head, s.hdir, head))
                        q = std::max(q, manh(s.head, head) <= 1 ? style::FEED_ADJ_P : style::FEED_FRONT_P);
                }
                q *= ramp;
            }
            // top rule R3: beside a growing ally (>= R3_LEN within Chebyshev R3_DIST) with no enemy head in view; v3 drops the
            // pearls where the receiver's head can take them (not behind its head)
            if (small && round >= style::R3_START && al >= style::R3_LEN && c <= style::R3_DIST && enemyHeadsInView == 0 &&
                (!style::R3_FRONT || !behind(s.head, s.hdir, head)))
                q = std::max(q, round >= style::R3_LATE ? style::R3_P_LATE : style::R3_P_EARLY);
            best = std::max(best, q);
        }
        return best > 0 && rnd(77) < best;
    }

    double scoreDir(int d, bool late, int kingT, bool amKing) {
        int s = nb[d];
        double sc = 0;
        if (nbKind[d] == NB_PORTAL_UNKNOWN) return (L >= style::BIG_LEN ? style::BIG_PORTAL_UNKNOWN : style::PORTAL_ENTER) + 0.01 * rnd(90 + d); // unknown far side (px8: not for big dragons)
        // long dragons need room to turn their whole body: about twice their length
        int need = L >= style::BIG_ROOM_LEN ? 2 * L + style::BIG_ROOM_EXTRA : L + style::ROOM_EXTRA, cap = std::max(need, style::ROOM_MIN);
        int rm = room(s, cap);
        if (nbBlind[d]) sc -= L >= style::BIG_LEN ? style::BIG_PORTAL_BLIND_PEN : style::PORTAL_BLIND_PEN;
        if (L >= style::SURVIVE_LEN && !survive(s, d, std::max(style::SURVIVE_MIN_DEPTH, std::min(L + style::SURVIVE_EXTRA, style::SURVIVE_DEPTH)))) sc -= 2 * style::ROOM_PEN; // doomed within a few moves (v3: every length; dead-end corridors kill small pieces)
        if (rm < need) sc -= style::ROOM_PEN * (1.0 + (need - rm) / (double)need);
        else if (rm < cap) sc -= style::POCKET_PEN * (cap - rm) / (double)cap; // a small closed pocket: mild
        bfs(s, 60, dist);
        double pv = 0;
        for (auto& T : targets) {
            int dd = dist[T.t]; if (dd < 0) continue;
            int arrive = dd + 1;
            double v = T.v;
            if (T.spawn > round) { int wait = T.spawn - round - arrive; if (wait > 0) v *= std::pow(0.93, wait); }
            int oa = distAlly[T.t];
            if (oa >= 0) { if (oa < arrive - 1) v *= 0.15; else if (oa <= arrive) v *= 0.55; }
            int oe = distEnemy[T.t];
            if (oe >= 0) { if (oe < arrive - 1) v *= style::CONTEST_ENEMY_CLOSER; else if (oe <= arrive) v *= style::CONTEST_ENEMY_EQ; }
            pv += v * (T.exp ? gpowE[std::min(arrive, 127)] : gpow[std::min(arrive, 127)]);
        }
        if (round >= style::SAC_START - 20 && L >= style::BIG_RECV_LEN && style::FOOD_W > 0) {
            for (auto& v : vis) if (v.id != myId && v.team == myTeam && v.head >= 0 && v.len < L && v.len <= style::SAC2_MAX_LEN) {
                int dd = dist[v.head] >= 0 ? dist[v.head] : manh(s, v.head) + 2;
                pv += style::FOOD_W * gpow[std::min(dd + 1, 127)];
            }
        }
        sc += pv;
        { // explore towards stale or unseen tiles, or a portal whose far end we have not seen
            int best = -1;
            for (int t : q) if (seenR[t] < 0 || round - seenR[t] > style::STALE_AGE) { best = t; break; }
            double ex = best >= 0 ? style::EXPLORE_W * std::pow(0.93, dist[best]) : 0.0;
            if (bfsPortal < 99) ex = std::max(ex, style::PORTAL_W * std::pow(0.93, bfsPortal));
            sc += ex * std::max(0.2, 1.0 - pv);
        }
        if (style::SPREAD_W > 0) { // keep some distance from other ally heads (seen or heard this round)
            double crowd = 0;
            for (auto& v : vis) if (v.id != myId && v.team == myTeam && v.head >= 0) { int m = manh(s, v.head); if (m < 3) crowd += (3 - m) / 3.0; }
            for (auto& [id, nw] : allies) if (id != myId && nw.round == round && nw.t >= 0 && !seenById(id)) { int m = manh(s, nw.t); if (m < 3) crowd += (3 - m) / 3.0; }
            sc -= style::SPREAD_W * crowd;
        }
        if (L >= style::THREAT_LEN) {
            int r = eReach[s];
            double k = L >= style::KING_SAFE_LEN ? style::KING_SAFE_MULT : 1.0;
            if (r <= 1) sc -= style::THREAT1 * k;
            else if (r == 2 && eReachLen[s] >= 3) sc -= style::THREAT2 * k;
            else if (r == 3 && eReachLen[s] >= 4) sc -= style::THREAT3 * k;
        }
        for (int dd = 0; dd < 4; dd++) { int u = across(s, dd); if (u >= 0 && headId[u] >= 0 && headId[u] != myId && occKind[u] == 2) sc -= style::ALLY_HEAD_PEN; }
        if (late && !amKing && kingT >= 0 && style::GATHER_W > 0) {
            int kd = dist[kingT] >= 0 ? dist[kingT] : manh(s, kingT) + 4;
            sc -= style::GATHER_W * kd;
        }
        if (feedT >= 0) { // v3 feeder: a small piece late in the game steps towards the tile in front of a visible big ally's head
            int fd = dist[feedT] >= 0 ? dist[feedT] : manh(s, feedT) + 2;
            sc -= style::FEED_W * fd;
        }
        const double huntW = std::max(style::HUNT ? style::HUNT_W : 0.0, elimMap && units >= style::ELIM_MAP_HUNT_UNITS ? style::ELIM_MAP_HUNT_W : 0.0);
        if (huntW > 0 && L <= style::RAM_MAX_LEN && units >= style::RAM_MIN_UNITS) {
            int bestD = 99;
            for (auto& [id, nw] : enemies) {
                if (nw.round < round - 3 || nw.t < 0) continue;
                int dd = dist[nw.t] >= 0 ? dist[nw.t] : manh(s, nw.t) + 3;
                bestD = std::min(bestD, dd);
            }
            if (bestD < 99) sc += huntW * std::pow(0.85, bestD);
        }
        if (d == dir) sc += 0.02;
        sc += 0.01 * rnd(90 + d);
        return sc;
    }

    Plan decide() {
        Plan p; dieDirV = -1;
        if (!ok || head < 0) { p.dirs = std::string(1, DIRCH[dir]); p.tag = '?'; return p; }
        int nFree = 0; for (int d = 0; d < 4; d++) if (nbKind[d] == NB_FREE || nbKind[d] == NB_PORTAL_UNKNOWN) nFree++;
        // 1. rams
        if (tryRam(p)) return p;
        // 2. trapped
        if (nFree == 0) {
            bool canStub = L >= 4 && units < unitLimit && L - style::STUB_KEEP >= 2 && childRoom(2) != 0;
            if (canStub && L > style::RAM_MAX_LEN) { p.kind = Plan::SPLIT; p.child = L - style::STUB_KEEP; p.tag = 'X'; return p; } // px8: keep the mass
            for (int d = 0; d < 4; d++) if (nbKind[d] == NB_ENEMY_HEAD && units >= 2) { p.dirs = std::string(1, DIRCH[d]); p.tag = 'r'; return p; }
            if (canStub) { p.kind = Plan::SPLIT; p.child = L - style::STUB_KEEP; p.tag = 'X'; return p; }
            if (rnd(62) < style::TRAP_NOACT) return die(0, 't');
            dieDirV = trappedDir();
            return die(2, 't');
        }
        // 3. late sacrifice
        if (wantSacrifice()) {
            dieDirV = opp(dir);
            if (style::SAC_INTO_ALLY) for (int d = 0; d < 4; d++) if (nbKind[d] == NB_ALLY) { const Seen* a = seenById(nbId[d]); if (a && a->len > L) { dieDirV = d; break; } }
            return die(rnd(63) < style::SAC_NOACT ? 0 : 2, 'K');
        }
        // 4. split
        int c = 0;
        if (wantSplit(c) && c >= 2 && L - c >= 2) { p.kind = Plan::SPLIT; p.child = c; p.tag = 'D'; return p; }
        eatPad = 0;
        if (L >= style::BIG_ROOM_LEN) { for (int dy = -3; dy <= 3; dy++) for (int dx = -3; dx <= 3; dx++) if (std::abs(dx) + std::abs(dy) <= 4 && pearlR[wy(head / W + dy) * W + wx(head % W + dx)] == round) eatPad++; eatPad = std::min(eatPad, 6); }
        // 5. move (a contested pearl two steps away is worth a sprint)
        if (trySprintEat(p)) return p;
        buildTargets(); multiBfs(distAlly, true); multiBfs(distEnemy, false); enemyReach();
        bool late = round >= style::SAC_START;
        int kid = myId, klen = L, kt = head, kr = round; bool amKing = true;
        if (style::KING_GATHER && late) {
            kingInfo(kid, klen, kt, kr); amKing = kid == myId;
            if (!amKing) { const Seen* ks = seenById(kid); if (ks && ks->head >= 0) kt = ks->head; }
            if (klen < style::KING_MIN_LEN) { amKing = true; kt = -1; } // no real king yet: no gathering
        }
        feedT = -1;
        if (style::FEED_W > 0 && round >= style::FEED_START && L <= style::SAC_MAX_LEN && units > style::SAC_MIN_UNITS && enemyHeadsInView == 0) {
            int bl = 0;
            for (auto& v : vis) if (v.id != myId && v.team == myTeam && v.head >= 0 && v.len >= style::R3_LEN && v.len >= L + 3 && v.len > bl) {
                int f = v.head; for (int k = 0; k < 2; k++) { int u = across(f, v.hdir); if (u < 0) break; f = u; }
                if (f != v.head) { bl = v.len; feedT = f; }
            }
        }
        double best = -1e18; int bd = -1;
        for (int d = 0; d < 4; d++) {
            if (nbKind[d] != NB_FREE && nbKind[d] != NB_PORTAL_UNKNOWN) continue;
            double sc = scoreDir(d, late, amKing ? -1 : kt, amKing);
            if (sc > best) { best = sc; bd = d; }
        }
        if (bd < 0) bd = safeDir >= 0 ? safeDir : dir;
        p.dirs = std::string(1, DIRCH[bd]);
        return p;
    }
};

} // namespace px

int main() {
    static px::Reader reader;
    static px::Writer writer;
    px::InitBlock ib;
    if (!reader.readInit(ib)) return 0;
    static px::Bot bot;
    bot.init(ib);
    static px::RoundBlock rb;
    while (reader.readRound(rb)) bot.turn(rb, writer);
    return 0;
}
