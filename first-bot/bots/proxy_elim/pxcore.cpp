// pxcore.cpp — shared code of the top-team proxy bots (bots/proxy_*). Identical in every proxy directory; the behaviour
// constants are in each directory's style.hpp. Sync: node tools/proxy_check.js sync (bots/proxy_swarm is the master).
// Design and calibration: research/experiments/proxies.md.
//
// One process per dragon (rules). Each dragon remembers what it has seen: kelp and portal edges, pearls, pearl timers
// (filled in for mirror tiles once the map symmetry is inferred), its own body, visible dragons, and what allies report
// by sonar (all four rays every turn carry team, kind, id, round, head x/y and length). Every turn, in this order:
//   1. rams: a piece of length <= RAM_MAX_LEN steps (adjacent) or sprints (2 or 3 steps) into a visible enemy head with
//      a style probability, much higher when the target is big (>= RAM_BIG_LEN and >= twice our length);
//   2. trapped (no free neighbour): ram an adjacent enemy head, else split off all but STUB_KEEP head segments (the
//      reversed body leaves from the old tail), else die (no action or a blocked step);
//   3. late conversion from SAC_START: short pieces die next to a longer ally head (much more likely beside a big one),
//      mid-size ones beside a clearly longer one (from MERGE_START any longer one); K style: beside the king (known by
//      sonar relay, >= KING_MIN_LEN) or into its body; pearls near a longer ally's head are left for it;
//   4. splitting: 4 -> 2+2 (longer: halves) until GROW_START; then only the local king (longest seen or heard within
//      KING_RADIUS) grows, other mid-size dragons (<= HALVE_MAX_LEN) halve; no split when the tail has no room;
//   5. move: pearl attraction (visible, remembered and soon-spawning pearls, discounted when another head is closer),
//      exploration (stale tiles, portals with an unknown far end), room check (2*L+4 tiles for long dragons, own tail
//      held while eating), survival lookahead (length >= 5: some path of 8 more steps), enemy-head avoidance for
//      length >= 5, ally spacing, gathering to the king (K), hunting reported enemy heads (elim), and a two-step sprint
//      onto a contested pearl for short dragons.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <string>
#include <unordered_map>
#include <vector>

#include "pxproto.hpp"
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
    std::vector<int> chain;  // tiles, head first, following the facing pointers
};
struct News { int round = -1; int t = -1; int len = 0; };
struct Target { int t; double v; int spawn; };

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
        dist.assign(N, -1); distOther.assign(N, -1); tmp.assign(N, -1); eReach.assign(N, 99); eReachLen.assign(N, 0);
        double g = 1.0; for (int i = 0; i < 128; i++) { gpow[i] = g; g *= style::GAMMA; }
    }

    void turn(const RoundBlock& rb, Writer& w) {
        ingest(rb);
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
    // ---- this turn ----
    int round = 0, L = 3, units = 1, dir = 0, head = -1, safeDir = -1; bool ok = false;
    std::vector<int> occId, headId, freeAt, bodyIdx; std::vector<uint8_t> occKind; // occKind: 0 none 1 own 2 ally 3 enemy
    std::vector<uint8_t> nearHead;   // 1 if another dragon's head is next to the tile (it may step there first)
    std::vector<int> gapMin;         // smallest observed gap between two spawn attempts of a tile (fountains), 0 unknown
    std::vector<Seen> vis;
    int nb[4] = {-1, -1, -1, -1}, nbKind[4] = {0, 0, 0, 0}, nbId[4] = {-1, -1, -1, -1};
    bool nbBlind[4] = {false, false, false, false}; // a known portal whose exit tile is out of view (vision does not cross portals)
    // ---- scratch ----
    std::vector<int> dist, distOther, tmp, q, eReach, eReachLen;
    std::vector<Target> targets;
    double gpow[128];

    // ---- geometry ----
    int wx(int x) const { x %= W; return x < 0 ? x + W : x; }
    int wy(int y) const { y %= H; return y < 0 ? y + H : y; }
    int stepT(int t, int d) const { return wy(t / W + DY[d]) * W + wx(t % W + DX[d]); }
    int adx(int a, int b) const { int d = std::abs(a % W - b % W); return std::min(d, W - d); }
    int ady(int a, int b) const { int d = std::abs(a / W - b / W); return std::min(d, H - d); }
    int cheb(int a, int b) const { return std::max(adx(a, b), ady(a, b)); }
    int manh(int a, int b) const { return adx(a, b) + ady(a, b); }
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
                int behind = stepT(cur, opp(lastDir));
                if (inView[behind] == round && occId[behind] != s.id) s.tailSeen = true;
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
                nw.round = round; nw.t = s.head; nw.len = s.nVis;
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
        if (style::SONAR_ENEMY) {
            int best = -1, bd = 99;
            for (auto& s : vis) if (s.team != myTeam && s.head >= 0) { int d0 = manh(s.head, head); if (d0 < bd) { bd = d0; best = s.id; } }
            if (best >= 0) { auto& s = *std::find_if(vis.begin(), vis.end(), [&](const Seen& x) { return x.id == best; }); alt = encode(2, s.id, round, s.head, s.nVis); }
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
    // Survival lookahead for longer dragons: can we make `depth` more single steps after entering tile s? Our body is
    // simulated exactly (tail stays when a visible pearl is eaten); other bodies are static until freeAt; heads block.
    std::vector<int> sb; std::vector<uint8_t> onBody; long long dfsNodes = 0;
    bool survive(int s, int lastDir, int depth) {
        sb.clear();
        for (int t : body) { if (t < 0) break; sb.push_back(t); }
        if ((int)onBody.size() != N) onBody.assign(N, 0);
        for (int t : sb) onBody[t]++;
        dfsNodes = 0;
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
        bool eat = pearlR[u] == round && inView[u] == round;
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
        if (!eat) { sb.push_back(tail); onBody[tail]++; }
        sb.erase(sb.begin()); onBody[u]--;
        return res;
    }

    // path distance (<= 3) from the nearest visible enemy head to every tile, and that enemy's visible length
    void enemyReach() {
        std::fill(eReach.begin(), eReach.end(), 99);
        for (auto& s : vis) {
            if (s.team == myTeam || s.head < 0) continue;
            std::fill(tmp.begin(), tmp.end(), -1);
            q.clear(); q.push_back(s.head); tmp[s.head] = 0;
            for (size_t qi = 0; qi < q.size(); qi++) {
                int t = q[qi], k = tmp[t];
                if (k < eReach[t]) { eReach[t] = k; eReachLen[t] = s.nVis; }
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
    // path distance from other visible heads (bodies ignored), for pearl contention
    void otherHeads() {
        std::fill(distOther.begin(), distOther.end(), -1);
        q.clear();
        for (auto& s : vis) if (s.id != myId && s.head >= 0 && distOther[s.head] < 0) { distOther[s.head] = 0; q.push_back(s.head); }
        for (auto& [id, nw] : allies) if (id != myId && nw.round >= round - 1 && nw.t >= 0 && distOther[nw.t] < 0) { distOther[nw.t] = 0; q.push_back(nw.t); }
        for (size_t qi = 0; qi < q.size(); qi++) {
            int t = q[qi], k = distOther[t];
            if (k >= 12) continue;
            for (int dd = 0; dd < 4; dd++) { int u = across(t, dd); if (u < 0 || distOther[u] >= 0) continue; distOther[u] = k + 1; q.push_back(u); }
        }
    }
    std::vector<uint8_t> leave; // late: pearls next to a clearly longer ally's head are left for it
    void markLeave() {
        if ((int)leave.size() != N) leave.assign(N, 0); else std::fill(leave.begin(), leave.end(), (uint8_t)0);
        if (round < style::SAC_START || !style::LEAVE_PEARLS) return;
        for (auto& v : vis) {
            if (v.id == myId || v.team != myTeam || v.head < 0 || v.nVis < L + 3) continue;
            for (int dy = -2; dy <= 2; dy++) for (int dx = -2; dx <= 2; dx++) {
                if (std::abs(dx) + std::abs(dy) > 2) continue;
                leave[wy(v.head / W + dy) * W + wx(v.head % W + dx)] = 1;
            }
        }
    }
    void buildTargets() {
        targets.clear();
        markLeave();
        for (int t = 0; t < N; t++) {
            double v = 0; int sp = -1;
            if (pearlR[t] >= 0 && pearlR[t] > emptyR[t]) { int age = round - pearlR[t]; v = age == 0 ? 1.0 : 0.8 * std::pow(0.97, age); }
            if (spawnR[t] > round && spawnR[t] - round <= 40 && !(pearlR[t] == round)) { double s = 0.7; if (s > v) { v = s; sp = spawnR[t]; } }
            if (style::FOUNTAIN_V > 0 && gapMin[t] > 0 && gapMin[t] <= 40 && inView[t] != round && round - seenR[t] >= gapMin[t] && style::FOUNTAIN_V > v) { v = style::FOUNTAIN_V; sp = -1; }
            if (v > 0.05 && leave[t]) v *= 0.15;
            if (v > 0.05) targets.push_back({t, v, sp});
        }
    }
    const Seen* seenById(int id) const { for (auto& s : vis) if (s.id == id) return &s; return nullptr; }
    int estLen(const Seen& s) const { return s.nVis; } // visible segments: a lower bound (exact when the tail is seen)

    // ---- decisions ----
    int dieDirV = -1;
    int dieDir() const { return dieDirV >= 0 ? dieDirV : opp(dir); }
    // trapped: a random blocked direction that is not a head (kelp, own or ally body)
    int trappedDir() const {
        int cand[4], n = 0;
        for (int d = 0; d < 4; d++) if (nbKind[d] == NB_KELP || nbKind[d] == NB_OWN || nbKind[d] == NB_ALLY || nbKind[d] == NB_ENEMY) cand[n++] = d;
        if (!n) return opp(dir);
        return cand[std::min(n - 1, (int)(rnd(61) * n))];
    }
    Plan die(int method, char tag) { Plan p; p.kind = Plan::DIE; p.method = method; p.tag = tag; return p; }

    // a target worth any small piece: at least RAM_BIG_LEN long and at least twice our length (visible segments)
    bool isBig(int el) const { return el >= style::RAM_BIG_LEN && el >= 2 * L; }
    bool tryRam(Plan& out) {
        if (L > style::RAM_MAX_LEN || units < style::RAM_MIN_UNITS) return false;
        // one step
        for (int d = 0; d < 4; d++) {
            if (nbKind[d] != NB_ENEMY_HEAD) continue;
            const Seen* e = seenById(nbId[d]); int el = e ? estLen(*e) : 2;
            double p = isBig(el) ? style::RAM_BIG_ADJ : el > L ? style::RAM_ADJ_UP : style::RAM_ADJ;
            if (rnd(11 + d) < p) { out.kind = Plan::MOVE; out.dirs = std::string(1, DIRCH[d]); out.tag = 'R'; return true; }
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
                const Seen* e = seenById(headId[u2]); int el = e ? estLen(*e) : 2;
                double p = isBig(el) ? style::RAM_BIG_S2 : el > L ? style::RAM_S2_UP : style::RAM_S2;
                if (rnd(31 + d1 * 4 + d2) < p) { out.kind = Plan::MOVE; out.dirs = std::string(1, DIRCH[d1]) + DIRCH[d2]; out.tag = 'S'; return true; }
            }
        }
        if (L < 4 || (style::RAM_S3 <= 0 && style::RAM_BIG_S3 <= 0)) return false;
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
                    const Seen* e = seenById(headId[u3]); int el = e ? estLen(*e) : 2;
                    if (rnd(71 + d1 * 16 + d2 * 4 + d3) < (isBig(el) ? style::RAM_BIG_S3 : style::RAM_S3)) {
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

    bool wantSplit(int& c) {
        if (units >= unitLimit || L < 4) return false;
        { int cr = childRoom(style::CHILD_ROOM); if (cr >= 0 && cr < style::CHILD_ROOM) return false; }
        if (round < style::GROW_START) {
            c = L >= style::HALF_MIN_LEN ? L / 2 : 2;
            return rnd(5) < style::SPLIT_P_EARLY;
        }
        // one grower per neighbourhood: the longest dragon we see or hear of within KING_RADIUS keeps growing
        bool localKing = true;
        for (auto& v : vis) if (v.id != myId && v.team == myTeam && v.head >= 0 && (v.nVis > L || (v.nVis == L && v.id < myId))) localKing = false;
        for (auto& [id, nw] : allies) if (id != myId && nw.round >= round - 2 && nw.t >= 0 && (nw.len > L || (nw.len == L && id < myId)) && manh(nw.t, head) <= style::KING_RADIUS) localKing = false;
        if (L >= style::GROWER_LEN) {
            if (L > style::HALVE_MAX_LEN || localKing) return false;
            c = L / 2;                           // a mid-size dragon with a longer ally nearby halves
            return rnd(6) < style::SPLIT_P_MID;
        }
        if (localKing && rnd(7) < style::GROW_P) return false; // a length-4 local king starts growing (gradually)
        c = 2;
        return rnd(5) < (round >= style::SAC_START ? style::SPLIT_P_LATE : style::SPLIT_P_MID);
    }

    bool wantSacrifice() {
        if (round < style::SAC_START || round > 496 || units <= style::SAC_MIN_UNITS) return false;
        bool small = L <= style::SAC_MAX_LEN;
        bool mid = !small && round >= style::SAC2_START && L <= style::SAC2_MAX_LEN;
        if (!small && !mid) return false;
        double ramp = std::min(1.0, (round - style::SAC_START + 1) / (double)style::SAC_RAMP);
        // feed a longer ally whose head is close: directly (big receiver within 2, or the king) or diffusely (any longer
        // ally within SAC_RECV_DIST, the N style's nearby mid-size eaters)
        int kid = -1, klen = 0, kt = -1, kr = -1;
        if (style::KING_GATHER) { kingInfo(kid, klen, kt, kr); if (kid == myId) return false; if (klen < style::KING_MIN_LEN) kid = -1; }
        double best = 0;
        for (auto& s : vis) {
            if (s.id == myId || s.team != myTeam || s.head < 0) continue;
            int al = s.nVis, c = cheb(s.head, head);
            int margin = round >= style::MERGE_START ? 1 : style::SAC2_MARGIN; // late: merge into any longer neighbour
            if (al <= L || (mid && al < L + margin)) continue;
            double q = 0;
            if (c <= 2 && (al >= std::max(style::BIG_RECV_LEN, 2 * L) || (mid && al >= L + margin))) q = small ? style::SAC_NEAR_P : style::SAC2_P;
            else if (c <= style::SAC_RECV_DIST) q = small ? style::SAC_P : 0.0;
            if (style::KING_GATHER && s.id == kid && manh(s.head, head) <= style::KING_SAC_DIST) q = std::max(q, style::SAC_KING_P);
            best = std::max(best, q * ramp);
        }
        return best > 0 && rnd(77) < best;
    }

    double scoreDir(int d, bool late, int kingT, bool amKing) {
        int s = nb[d];
        double sc = 0;
        if (nbKind[d] == NB_PORTAL_UNKNOWN) return style::PORTAL_ENTER + 0.01 * rnd(90 + d); // unknown far side: exploration gamble
        // long dragons need room to turn their whole body: about twice their length
        int need = L >= style::BIG_ROOM_LEN ? 2 * L + style::BIG_ROOM_EXTRA : L + style::ROOM_EXTRA, cap = std::max(need, style::ROOM_MIN);
        int rm = room(s, cap);
        if (nbBlind[d]) sc -= style::PORTAL_BLIND_PEN;
        if (L >= style::SURVIVE_LEN && !survive(s, d, std::min(L, style::SURVIVE_DEPTH))) sc -= 2 * style::ROOM_PEN; // doomed within a few moves
        if (rm < need) sc -= style::ROOM_PEN * (1.0 + (need - rm) / (double)need);
        else if (rm < cap) sc -= style::POCKET_PEN * (cap - rm) / (double)cap; // a small closed pocket: mild
        bfs(s, 60, dist);
        double pv = 0;
        for (auto& T : targets) {
            int dd = dist[T.t]; if (dd < 0) continue;
            int arrive = dd + 1;
            double v = T.v;
            if (T.spawn > round) { int wait = T.spawn - round - arrive; if (wait > 0) v *= std::pow(0.93, wait); }
            int od = distOther[T.t];
            if (od >= 0) { if (od < arrive - 1) v *= 0.15; else if (od <= arrive) v *= 0.55; }
            pv += v * gpow[std::min(arrive, 127)];
        }
        if (round >= style::SAC_START - 20 && L >= style::BIG_RECV_LEN && style::FOOD_W > 0) {
            for (auto& v : vis) if (v.id != myId && v.team == myTeam && v.head >= 0 && v.nVis < L && v.nVis <= style::SAC2_MAX_LEN) {
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
            if (r <= 1) sc -= style::THREAT1;
            else if (r == 2 && eReachLen[s] >= 3) sc -= style::THREAT2;
            else if (r == 3 && eReachLen[s] >= 4) sc -= style::THREAT3;
        }
        for (int dd = 0; dd < 4; dd++) { int u = across(s, dd); if (u >= 0 && headId[u] >= 0 && headId[u] != myId && occKind[u] == 2) sc -= style::ALLY_HEAD_PEN; }
        if (late && !amKing && kingT >= 0 && style::GATHER_W > 0) {
            int kd = dist[kingT] >= 0 ? dist[kingT] : manh(s, kingT) + 4;
            sc -= style::GATHER_W * kd;
        }
        if (style::HUNT && L <= style::RAM_MAX_LEN && units >= style::RAM_MIN_UNITS) {
            int bestD = 99;
            for (auto& [id, nw] : enemies) {
                if (nw.round < round - 3 || nw.t < 0) continue;
                int dd = dist[nw.t] >= 0 ? dist[nw.t] : manh(s, nw.t) + 3;
                bestD = std::min(bestD, dd);
            }
            if (bestD < 99) sc += style::HUNT_W * std::pow(0.85, bestD);
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
            for (int d = 0; d < 4; d++) if (nbKind[d] == NB_ENEMY_HEAD && units >= 2) { p.dirs = std::string(1, DIRCH[d]); p.tag = 'r'; return p; }
            if (L >= 4 && units < unitLimit && L - style::STUB_KEEP >= 2 && childRoom(2) != 0) { p.kind = Plan::SPLIT; p.child = L - style::STUB_KEEP; p.tag = 'X'; return p; }
            if (rnd(62) < style::TRAP_NOACT) return die(0, 't');
            dieDirV = trappedDir();
            return die(2, 't');
        }
        // 3. late sacrifice
        if (wantSacrifice()) {
            dieDirV = opp(dir);
            if (style::SAC_INTO_ALLY) for (int d = 0; d < 4; d++) if (nbKind[d] == NB_ALLY) { const Seen* a = seenById(nbId[d]); if (a && a->nVis > L) { dieDirV = d; break; } }
            return die(rnd(63) < style::SAC_NOACT ? 0 : 2, 'K');
        }
        // 4. split
        int c = 0;
        if (wantSplit(c) && c >= 2 && L - c >= 2) { p.kind = Plan::SPLIT; p.child = c; p.tag = 'D'; return p; }
        eatPad = 0;
        if (L >= style::BIG_ROOM_LEN) { for (int dy = -3; dy <= 3; dy++) for (int dx = -3; dx <= 3; dx++) if (std::abs(dx) + std::abs(dy) <= 4 && pearlR[wy(head / W + dy) * W + wx(head % W + dx)] == round) eatPad++; eatPad = std::min(eatPad, 6); }
        // 5. move (a contested pearl two steps away is worth a sprint)
        if (trySprintEat(p)) return p;
        buildTargets(); otherHeads(); enemyReach();
        bool late = round >= style::SAC_START;
        int kid = myId, klen = L, kt = head, kr = round; bool amKing = true;
        if (style::KING_GATHER && late) {
            kingInfo(kid, klen, kt, kr); amKing = kid == myId;
            if (!amKing) { const Seen* ks = seenById(kid); if (ks && ks->head >= 0) kt = ks->head; }
            if (klen < style::KING_MIN_LEN) { amKing = true; kt = -1; } // no real king yet: no gathering
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
