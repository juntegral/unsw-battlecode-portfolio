// world.cpp — per-dragon memory: tiles, edges, portals, pearl calendar, own body, other dragons,
// symmetry inference, sonar echoes and team messages.
#include "world.hpp"

#include <algorithm>
#include <cmath>
#include <cstring>

#include "params.hpp"

namespace seed0 {

static const uint64_t MSG_MAGIC = 0x2D; // 6 bits
static const uint64_t MSG_WHITEN = 0x9E3779B97F4A7C15ull; // fixed team key: casual decoding by others fails

void World::init(const InitBlock& ib) {
    geo.W = ib.W; geo.H = ib.H;
    myId = ib.id; myTeam = ib.team; unitLimit = ib.unitLimit;
    int n = geo.tiles();
    tiles.assign(n, Tile{});
    freeAt.assign(n, 0);
    headOf.assign(n, -1);
    occNow.assign(n, 0);
    body.clear();
    dragons.clear();
    portals.clear();
    pearlPriorUnseen = P::PRIOR_UNSEEN;
}

int World::mirrorTile(int t, int hyp) const {
    int x = t % geo.W, y = t / geo.W;
    switch (hyp) {
    case 0: return geo.idx(x, geo.H - 1 - y);
    case 1: return geo.idx(geo.W - 1 - x, y);
    default: return geo.idx(geo.W - 1 - x, geo.H - 1 - y);
    }
}
int World::mirrorDir(int d, int hyp) const {
    switch (hyp) {
    case 0: return (d == N || d == S) ? opp(d) : d;
    case 1: return (d == E || d == W) ? opp(d) : d;
    default: return opp(d);
    }
}

int World::canonicalPortalEnd(int t, int d, int& side) const {
    if (d == N) { side = N; return t; }
    if (d == W) { side = W; return t; }
    if (d == S) { side = N; return geo.stepIdx(t, S); }
    side = W; return geo.stepIdx(t, E);
}

void World::setEdge(int t, int d, uint8_t kind, int pid) {
    Tile& a = tiles[t];
    a.edge[d] = kind; a.portal[d] = (int16_t)(kind == EDGE_PORTAL ? pid : -1);
    int u = geo.stepIdx(t, d);
    Tile& b = tiles[u];
    b.edge[opp(d)] = kind; b.portal[opp(d)] = (int16_t)(kind == EDGE_PORTAL ? pid : -1);
    if (kind == EDGE_PORTAL && pid >= 0) {
        int side; int ct = canonicalPortalEnd(t, d, side);
        auto& ends = portals[pid];
        for (auto& e : ends) if (e.t == ct && e.side == side) return;
        if (ends.size() < 2) ends.push_back(PortalEnd{ct, side});
    }
}

int World::across(int t, int d) const {
    const Tile& x = tiles[t];
    switch (x.edge[d]) {
    case EDGE_KELP: return -1;
    case EDGE_PORTAL: {
        int pid = x.portal[d];
        if (pid < 0) return -2;
        auto it = portals.find(pid);
        if (it == portals.end() || it->second.size() < 2) return -2;
        int side; int ct = canonicalPortalEnd(t, d, side);
        const PortalEnd* other = nullptr;
        for (auto& e : it->second) if (!(e.t == ct && e.side == side)) other = &e;
        if (!other) return -2;
        if (other->side != d && other->side != opp(d)) return -2;
        return d == other->side ? geo.stepIdx(other->t, other->side) : other->t;
    }
    default: return geo.stepIdx(t, d);
    }
}

// ------------------------------------------------------------------------------------------------
void World::ingest(const RoundBlock& rb) {
    round = rb.round; myLen = rb.length; unitCount = rb.unitCount; myDir = rb.dir; parsedOk = rb.ok;
    if (!rb.ok) return; // keep the old picture; the planner falls back to a cautious move
    prevHeadT = headT;
    int winTile[49];
    for (int i = 0; i < 49; i++) winTile[i] = geo.idx(geo.wrapX(rb.tiles[i].x), geo.wrapY(rb.tiles[i].y));
    headT = winTile[24]; // the window is centred on our head
    for (auto& p : rb.parts) if (p.head && p.id == myId && p.team == myTeam) headT = geo.idx(geo.wrapX(p.x), geo.wrapY(p.y));

    ingestTiles(rb);
    ingestEdges(rb, winTile);
    ingestDragons(rb);
    updateOwnBody(rb);
    updateSymmetry(winTile);
    if (sym >= 0) applyMirror(winTile);
    buildOccupancy();
    ingestSonar(rb);
}

void World::ingestTiles(const RoundBlock& rb) {
    for (int i = 0; i < 49; i++) {
        const TileObs& o = rb.tiles[i];
        int t = geo.idx(geo.wrapX(o.x), geo.wrapY(o.y));
        Tile& x = tiles[t];
        if (x.seen < 0) { tilesObserved++; if (o.pearl) pearlsAtFirstSight++; }
        x.seen = (int16_t)round;
        if (o.pearl) x.pearlSeen = (int16_t)round; else x.emptySeen = (int16_t)round;
        if (o.pearlIn < 0) { x.spawnRound = NEVER; continue; }
        int c = o.pearlIn;
        int newSpawn = round + c;
        if (x.spawnRound > 0 && newSpawn > x.spawnRound) {
            int since = round - x.spawnRound; // rounds since the last predicted reset
            if (since >= 0 && since <= 60) {
                int sample = c + since;
                if (sample > x.maxSample) x.maxSample = (uint16_t)std::min(sample, 65535);
                if (x.samples < 255) x.samples++;
            }
        }
        if (c > (int)x.maxGapLB) x.maxGapLB = (uint16_t)std::min(c, 65535);
        x.spawnRound = newSpawn;
    }
    if (tilesObserved >= 30) {
        double p = (pearlsAtFirstSight + 1.0) / (tilesObserved + 20.0);
        pearlPriorUnseen = std::clamp(p, 0.01, 0.3);
    }
    int fc = 0;
    for (int i = 0; i < 49; i++) if (isFountain(geo.idx(geo.wrapX(rb.tiles[i].x), geo.wrapY(rb.tiles[i].y)))) fc++;
    fountainCount = std::max(fountainCount, fc);
}

static inline uint8_t kindOf(int tok) { return tok == -2 ? EDGE_KELP : (tok == -1 ? EDGE_OPEN : EDGE_PORTAL); }

void World::ingestEdges(const RoundBlock& rb, const int* winTile) {
    for (int r = 0; r < 7; r++) for (int c = 0; c < 7; c++) {
        int t = winTile[r * 7 + c];
        int n = rb.hedge[r][c], s = rb.hedge[r + 1][c], w = rb.vedge[r][c], e = rb.vedge[r][c + 1];
        setEdge(t, N, kindOf(n), n);
        setEdge(t, S, kindOf(s), s);
        setEdge(t, W, kindOf(w), w);
        setEdge(t, E, kindOf(e), e);
    }
}

void World::ingestDragons(const RoundBlock& rb) {
    enemyHeadsNow.clear(); allyHeadsNow.clear();
    // group by id
    std::unordered_map<int, std::vector<const PartObs*>> byId;
    for (auto& p : rb.parts) byId[p.id].push_back(&p);
    for (auto& [id, parts] : byId) {
        Dragon& d = dragons[id];
        d.id = id; d.team = parts[0]->team; d.lastSeen = round; d.visLen = (int)parts.size();
        // position -> part
        std::unordered_map<int, const PartObs*> at;
        for (auto* p : parts) at[geo.idx(geo.wrapX(p->x), geo.wrapY(p->y))] = p;
        const PartObs* head = nullptr;
        for (auto* p : parts) if (p->head) head = p;
        d.chain.clear();
        if (head) {
            d.headSeen = round; d.headT = geo.idx(geo.wrapX(head->x), geo.wrapY(head->y)); d.headDir = head->dir;
            if (d.team == myTeam) { if (id != myId) allyHeadsNow.push_back(id); } else enemyHeadsNow.push_back(id);
            // walk from the head: the next segment is the one whose facing points at the current tile
            std::vector<char> used(parts.size(), 0);
            int cur = d.headT; d.chain.push_back(cur);
            for (;;) {
                const PartObs* next = nullptr; size_t ni = 0;
                for (size_t i = 0; i < parts.size(); i++) {
                    const PartObs* p = parts[i];
                    if (used[i] || p->head) continue;
                    int pt = geo.idx(geo.wrapX(p->x), geo.wrapY(p->y));
                    if (geo.stepIdx(pt, p->dir) == cur) { next = p; ni = i; break; }
                }
                if (!next) break;
                used[ni] = 1; cur = geo.idx(geo.wrapX(next->x), geo.wrapY(next->y)); d.chain.push_back(cur);
            }
        }
        // tail identification: a segment nobody points at, whose "behind" tile is in view and not this dragon
        d.tailSeen = false;
        if (head && (int)d.chain.size() == d.visLen) {
            int last = d.chain.back();
            const PartObs* lp = at[last];
            int behind = geo.stepIdx(last, opp(lp->dir));
            bool inView = false;
            for (int i = 0; i < 49; i++) if (geo.idx(geo.wrapX(rb.tiles[i].x), geo.wrapY(rb.tiles[i].y)) == behind) { inView = true; break; }
            if (d.visLen == 1) inView = false; // a lone head: the body is out of view
            if (inView && !at.count(behind)) d.tailSeen = true;
        }
        d.tailT = (head && d.tailSeen) ? d.chain.back() : -1;
        bool onRing = false;
        for (auto* p : parts) if (geo.cheb(geo.idx(geo.wrapX(p->x), geo.wrapY(p->y)), headT) >= 3) onRing = true;
        if (head && d.tailSeen) { d.estLen = d.visLen; d.minLen = d.visLen; }
        else {
            d.minLen = std::max(d.minLen, d.visLen);
            d.estLen = std::max(d.estLen, d.visLen);
            if (onRing) d.estLen = std::max(d.estLen, 4); // its body continues out of view: assume it can sprint
        }
        if (d.team == myTeam && id != myId) maxAllyLenSeen = std::max(maxAllyLenSeen, d.estLen);
        if (d.team != myTeam) bestEnemyLen = std::max(bestEnemyLen, d.minLen);
        for (auto* p : parts) tiles[geo.idx(geo.wrapX(p->x), geo.wrapY(p->y))].occSeen = (int16_t)round;
    }
}

void World::updateOwnBody(const RoundBlock& rb) {
    auto it = dragons.find(myId);
    std::vector<int> chain;
    if (it != dragons.end() && !it->second.chain.empty()) chain = it->second.chain;
    else chain.push_back(headT);
    std::deque<int> old = body;
    std::deque<int> nb(chain.begin(), chain.end());
    for (int t : old) {
        if (t >= 0 && std::find(chain.begin(), chain.end(), t) != chain.end()) continue;
        nb.push_back(t);
    }
    while ((int)nb.size() > myLen) nb.pop_back();
    // segments we have never seen (a long starting body): assume the body continues straight
    if ((int)nb.size() < myLen && nb.size() >= 2) {
        int a = nb[nb.size() - 2], b = nb[nb.size() - 1];
        int dir = -1;
        if (a >= 0 && b >= 0) for (int d = 0; d < 4; d++) if (geo.stepIdx(a, d) == b) dir = d;
        int cur = b;
        while ((int)nb.size() < myLen) {
            if (dir < 0 || cur < 0) { nb.push_back(-1); continue; }
            int nx = across(cur, dir);
            if (nx < 0 || std::find(nb.begin(), nb.end(), nx) != nb.end()) { dir = -1; nb.push_back(-1); continue; }
            nb.push_back(nx); cur = nx;
        }
    }
    while ((int)nb.size() < myLen) nb.push_back(-1);
    body = nb;
    (void)rb;
}

void World::buildOccupancy() {
    std::fill(freeAt.begin(), freeAt.end(), (int16_t)0);
    std::fill(headOf.begin(), headOf.end(), (int16_t)-1);
    std::fill(occNow.begin(), occNow.end(), (uint8_t)0);
    int L = (int)body.size();
    for (int i = 0; i < L; i++) {
        int t = body[i]; if (t < 0) continue;
        int k = L - 1 - i;                    // distance from tail
        freeAt[t] = (int16_t)std::min(k + 2, (int)FREE_NEVER);
        occNow[t] = 1;
    }
    headOf[headT] = (int16_t)myId;
    for (auto& [id, d] : dragons) {
        if (id == myId || d.lastSeen != round) continue;
        uint8_t kind = d.team == myTeam ? 2 : 3;
        int n = (int)d.chain.size();
        if (d.headSeen == round && d.tailSeen && n > 0) {
            int pad = 3; // k + 2 exact if it never eats, +1 safety
            for (int dd = 0; dd < 4; dd++) { int u = across(d.headT, dd); if (u >= 0 && tiles[u].pearlSeen == round) pad = 4; }
            for (int i = 0; i < n; i++) { int k = n - 1 - i; int t = d.chain[i]; freeAt[t] = std::max(freeAt[t], (int16_t)std::min(k + pad, (int)FREE_NEVER)); occNow[t] = kind; }
        } else {
            for (int t : d.chain) { freeAt[t] = FREE_NEVER; occNow[t] = kind; }
        }
        if (d.headSeen == round) headOf[d.headT] = (int16_t)id;
    }
    // segments visible this turn but not on a reconstructed chain (head out of view): block for the horizon
    for (int t = 0; t < geo.tiles(); t++) if (tiles[t].occSeen == round && occNow[t] == 0) { occNow[t] = 3; freeAt[t] = FREE_NEVER; }
}

void World::updateSymmetry(const int* winTile) {
    if (sym >= 0) return;
    int alive = 0;
    for (int h = 0; h < 3; h++) {
        if (!symAlive[h]) continue;
        for (int i = 0; i < 49 && symAlive[h]; i++) {
            int t = winTile[i], m = mirrorTile(t, h);
            if (m == t) continue;
            const Tile& a = tiles[t]; const Tile& b = tiles[m];
            if (b.seen < 0) continue;
            for (int d = 0; d < 4; d++) {
                uint8_t ka = a.edge[d], kb = b.edge[mirrorDir(d, h)];
                if (ka == EDGE_UNKNOWN || kb == EDGE_UNKNOWN) continue;
                if ((ka == EDGE_KELP) != (kb == EDGE_KELP) || (ka == EDGE_PORTAL) != (kb == EDGE_PORTAL)) { symAlive[h] = false; break; }
                symChecks[h]++;
            }
            if (!symAlive[h]) break;
            if ((a.spawnRound == NEVER) != (b.spawnRound == NEVER) && a.spawnRound != 0 && b.spawnRound != 0) { symAlive[h] = false; break; }
            if (a.spawnRound > 0 && b.spawnRound > 0) {
                int ra = a.seen, rb2 = b.seen;
                if (std::max(ra, rb2) < std::min(a.spawnRound, b.spawnRound) && a.spawnRound != b.spawnRound) { symAlive[h] = false; break; }
                if (ra == rb2 && a.spawnRound != b.spawnRound) { symAlive[h] = false; break; }
                if (ra == rb2) symChecks[h] += 2;
            }
        }
        if (symAlive[h]) alive++;
    }
    if (alive == 1) {
        for (int h = 0; h < 3; h++) if (symAlive[h] && symChecks[h] >= 12) sym = h;
    } else if (alive > 1 && round >= 40) {
        int best = -1;
        for (int h = 0; h < 3; h++) if (symAlive[h] && (best < 0 || symChecks[h] > symChecks[best])) best = h;
        if (best >= 0 && symChecks[best] >= 30) sym = best;
    }
}

void World::applyMirror(const int* winTile) {
    // a known portal pair mirrors onto another connected pair: register it under a synthetic id
    for (auto& [pid, ends] : portals) {
        if (pid >= 1000 || ends.size() < 2) continue;
        int sid = 1000 + pid;
        if (portals.count(sid)) continue;
        std::vector<PortalEnd> mirrored;
        bool self = false;
        for (auto& e : ends) {
            int mt = mirrorTile(e.t, sym), md = mirrorDir(e.side, sym);
            int side; int ct = canonicalPortalEnd(mt, md, side);
            for (auto& o : ends) if (o.t == ct && o.side == side) self = true;
            mirrored.push_back(PortalEnd{ct, side});
        }
        if (self) continue;
        bool ok = true;
        for (auto& m : mirrored) { uint8_t k = tiles[m.t].edge[m.side]; if (k == EDGE_KELP || k == EDGE_OPEN) ok = false; if (k == EDGE_PORTAL && tiles[m.t].portal[m.side] >= 0 && tiles[m.t].portal[m.side] < 1000) ok = false; }
        if (!ok) continue;
        for (auto& m : mirrored) {
            tiles[m.t].edge[m.side] = EDGE_PORTAL; tiles[m.t].portal[m.side] = (int16_t)sid;
            int u = geo.stepIdx(m.t, m.side); tiles[u].edge[opp(m.side)] = EDGE_PORTAL; tiles[u].portal[opp(m.side)] = (int16_t)sid;
        }
        portals[sid] = mirrored;
    }
    for (int i = 0; i < 49; i++) {
        int t = winTile[i], m = mirrorTile(t, sym);
        if (m == t) continue;
        Tile& a = tiles[t]; Tile& b = tiles[m];
        for (int d = 0; d < 4; d++) {
            int md = mirrorDir(d, sym);
            if (b.edge[md] != EDGE_UNKNOWN) continue;
            if (a.edge[d] == EDGE_KELP || a.edge[d] == EDGE_OPEN) {
                b.edge[md] = a.edge[d];
                int u = geo.stepIdx(m, md); tiles[u].edge[opp(md)] = a.edge[d];
            } else if (a.edge[d] == EDGE_PORTAL) {
                b.edge[md] = EDGE_PORTAL; b.portal[md] = -1;  // unknown partner id: treated as an unknown exit
                int u = geo.stepIdx(m, md); tiles[u].edge[opp(md)] = EDGE_PORTAL; tiles[u].portal[opp(md)] = -1;
            }
        }
    }
}

void World::ingestSonar(const RoundBlock& rb) {
    lastEcho = rb.echoes; echoRound = rb.echoes.present ? round : echoRound;
    for (uint64_t v : rb.msgs) {
        AllyMsg m;
        if (!decodeMsg(v, m)) continue;
        if (m.id == myId) continue;
        bool found = false;
        for (auto& a : allies) if (a.id == m.id) { if (m.round >= a.round) a = m; found = true; }
        if (!found) allies.push_back(m);
        auto known = dragons.find(m.id);
        if (known != dragons.end() && known->second.lastSeen >= 0 && known->second.team != myTeam) continue; // seen as an enemy
        Dragon& d = dragons[m.id];
        d.id = m.id; if (d.lastSeen < 0) d.team = myTeam;
        if (m.round >= d.headSeen) { d.headSeen = m.round; d.headT = m.t; d.lastSeen = std::max(d.lastSeen, m.round); }
        d.estLen = std::max(d.estLen, m.len);
        if (m.round >= round - 2) d.estLen = m.len;
        maxAllyLenSeen = std::max(maxAllyLenSeen, m.len);
    }
}

double World::pearlProb(int t, int r) const {
    const Tile* x = &tiles[t];
    double conf = 1.0;
    if (x->seen < 0) {
        if (sym >= 0) {
            int m = mirrorTile(t, sym);
            if (tiles[m].seen >= 0) { x = &tiles[m]; conf = P::MIRROR_CONF; }
            else return pearlPriorUnseen;
        } else return pearlPriorUnseen;
    }
    if (x->spawnRound == NEVER) {
        if (conf < 1.0) return 0.0;
        if (x->pearlSeen > x->emptySeen) return std::pow(P::PEARL_DECAY, r - x->pearlSeen);
        return 0.0;
    }
    double p = 0.0;
    if (conf == 1.0 && x->pearlSeen > x->emptySeen) p = std::pow(P::PEARL_DECAY, r - x->pearlSeen);
    if (x->spawnRound > 0 && x->spawnRound <= r) {
        double q = P::SPAWN_CONF * std::pow(P::PEARL_DECAY, r - x->spawnRound);
        bool fountain = x->samples >= 2 ? x->maxSample <= P::FOUNTAIN_MAX_GAP : (x->samples == 1 && x->maxSample <= 3);
        if (fountain) q = std::max(q, 0.7);
        p = std::max(p, q);
    }
    return p * conf;
}

int World::teamLongestKnown() const { return std::max(myLen, maxAllyLenSeen); }

uint64_t World::encodeMsg(int hotT) const {
    uint64_t id = (uint64_t)(myId & 255), rnd = (uint64_t)(round & 511);
    uint64_t x = (uint64_t)(headT % geo.W) & 63, y = (uint64_t)(headT / geo.W) & 63;
    uint64_t len = (uint64_t)std::min(myLen, 255);
    uint64_t hx = hotT >= 0 ? (uint64_t)(hotT % geo.W) & 63 : 63, hy = hotT >= 0 ? (uint64_t)(hotT / geo.W) & 63 : 63;
    uint64_t team = myTeam == 'B' ? 1 : 0;
    uint64_t chk = (id * 131 + rnd * 7 + x * 17 + y * 31 + len * 3 + hx * 5 + hy * 13 + team * 101 + 0x2A) & 255;
    uint64_t v = (MSG_MAGIC << 58) | (id << 50) | (rnd << 41) | (x << 35) | (y << 29) | (len << 21) | (hx << 15) | (hy << 9) | (team << 8) | chk;
    return v ^ MSG_WHITEN;
}

bool World::decodeMsg(uint64_t v, AllyMsg& out) const {
    v ^= MSG_WHITEN;
    if ((v >> 58) != MSG_MAGIC) return false;
    uint64_t id = (v >> 50) & 255, rnd = (v >> 41) & 511, x = (v >> 35) & 63, y = (v >> 29) & 63;
    uint64_t len = (v >> 21) & 255, hx = (v >> 15) & 63, hy = (v >> 9) & 63, team = (v >> 8) & 1, chk = v & 255;
    uint64_t want = (id * 131 + rnd * 7 + x * 17 + y * 31 + len * 3 + hx * 5 + hy * 13 + team * 101 + 0x2A) & 255;
    if (chk != want) return false;
    if ((team == 1) != (myTeam == 'B')) return false; // an identical bot on the other team
    if ((int)x >= geo.W || (int)y >= geo.H) return false;
    if (len < 2) return false;
    { int rr = (int)rnd, cur = round & 511; int diff = (cur - rr + 512) & 511; if (diff > 3) return false; }
    out.id = (int)id; out.round = (int)rnd; out.t = geo.idx((int)x, (int)y); out.len = (int)len;
    out.hotT = (hx == 63 && hy == 63) ? -1 : ((int)hx < geo.W && (int)hy < geo.H ? geo.idx((int)hx, (int)hy) : -1);
    return true;
}

} // namespace seed0
