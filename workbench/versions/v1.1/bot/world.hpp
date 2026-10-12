// world.hpp — a dragon's private memory of the board, rebuilt from 7x7 observations each turn.
#pragma once
#include <algorithm>
#include <cstdint>
#include <deque>
#include <string>
#include <unordered_map>
#include <vector>

#include "geom.hpp"
#include "params.hpp"
#include "proto.hpp"

namespace seed0 {

constexpr int NEVER = -1;
constexpr int16_t FREE_NEVER = 30000; // "blocked for the whole planning horizon"

struct Tile {
    int16_t seen = -1;          // last round observed (-1 never)
    uint8_t edge[4] = {EDGE_UNKNOWN, EDGE_UNKNOWN, EDGE_UNKNOWN, EDGE_UNKNOWN};
    int16_t portal[4] = {-1, -1, -1, -1};
    int32_t spawnRound = 0;     // absolute round of next spawn attempt as last known; -1 never; 0 unknown
    int16_t pearlSeen = -1;     // last round a pearl was seen here
    int16_t emptySeen = -1;     // last round seen without a pearl
    uint16_t maxGapLB = 0;      // lower bound of max_gap (largest countdown ever shown)
    uint16_t maxSample = 0;     // largest single-reset gap sample
    uint8_t  samples = 0;       // number of gap samples
    int16_t  occSeen = -1;      // last round a dragon segment was seen here
    int16_t  dropSeen = -1;     // stack2 S2: round a death drop (a pearl no spawn attempt can explain) was first seen here
};

struct Dragon {
    int id = -1;
    char team = 'A';
    int lastSeen = -1;          // round of the last observation of any segment
    int headSeen = -1;          // round of the last head observation
    int headT = -1;             // tile of the head when last seen
    int headDir = 0;
    int visLen = 0;             // segments visible at last sight
    int estLen = 0;             // best estimate of full length (>= visLen); inflated when the body leaves the window
    int minLen = 0;             // proven lower bound (exact when the whole dragon was in view)
    bool tailSeen = false;      // the whole chain was visible (tail identified)
    int tailT = -1;             // tail tile when tailSeen
    std::vector<int> chain;     // head first, as reconstructed at lastSeen (only when head visible)
};

struct AllyMsg { int id = -1; int round = -1; int t = -1; int len = 0; int hotT = -1; bool relay = false; };

struct World {
    Geo geo;
    int myId = 0; char myTeam = 'A'; int unitLimit = 64;
    int round = 0, myLen = 3, unitCount = 1, myDir = 0, headT = -1;
    bool parsedOk = false;
    std::vector<Tile> tiles;

    // own body, head first; -1 = unknown placeholder (only for a long starting body beyond vision)
    std::deque<int> body;

    std::unordered_map<int, Dragon> dragons;   // every dragon ever seen, by id
    // v1 belief fix: per id, the round of the length evidence estLen / minLen rest on (a full view, a direct report, a reset). Kept apart
    // from Dragon so that the fix-off build allocates exactly as stack11 (the judge prices malloc's work like any other instruction).
    std::unordered_map<int, int> lenRound;
    int lenRoundOf(int id) const { auto it = lenRound.find(id); return it == lenRound.end() ? -1000 : it->second; }
    std::vector<int> enemyHeadsNow;            // ids of enemy heads visible this turn
    std::vector<int> allyHeadsNow;

    // per-turn occupancy for planning: step index at which the tile becomes free (0 = free now)
    std::vector<int16_t> freeAt;
    std::vector<int16_t> headOf;   // dragon id whose head is on the tile now, -1 otherwise (own head too)
    std::vector<uint8_t> occNow;   // 0 free, 1 own body, 2 ally, 3 enemy (this turn's observation)

    // portals: id -> canonical ends (tile, side in {N,W}); up to two
    struct PortalEnd { int t = -1; int side = 0; };
    std::unordered_map<int, std::vector<PortalEnd>> portals;

    // symmetry: 0 flipY (y'=H-1-y), 1 flipX (x'=W-1-x), 2 rot180; -1 unresolved
    int sym = -1;
    bool symAlive[3] = {true, true, true};
    int symChecks[3] = {0, 0, 0};

    // sonar
    Echoes lastEcho;             // echoes reported this turn (for rays sent last turn)
    int echoRound = -1;
    int enemyEchoDir[4] = {0, 0, 0, 0};   // round when a ray in dir d last echoed an enemy (head or body), 0 none
    int enemyHeadEchoDir[4] = {0, 0, 0, 0};

    // ally messages heard
    std::vector<AllyMsg> allies;   // one entry per ally id (latest)
    int maxAllyLenSeen = 0;        // longest ally length ever seen or heard
    int bestEnemyLen = 0;          // longest enemy length ever established

    // sonar probe: the single ray sent last turn from probeFromT (our head after that move) in probeDir hit no dragon => probeClear
    int prevHeadT = -1;
    int probeDir = -1, probeRound = -1; bool probeClear = false;
    int probeFromT = -1;
    bool probeAlly = false;    // stack8 px2: that ray stopped on a dragon of ours (echo ally or ally_head)

    // cand-portal1: hunger (rounds since our length last grew) and frontiers muted after a dirty probe
    int lastAteRound = -1, prevLen = 0;
    std::vector<int16_t> frontierBlock;   // tile*4+dir -> round until which that unexplored portal is ignored

    // birth (pd10): first round this process saw, length then, and whether the head tile was open to the sides
    int birthRound = -1, birthLen = 0;
    bool bornExposed = false;

    // map-level statistics
    double pearlPriorUnseen = 0.05;
    int tilesObserved = 0, pearlsAtFirstSight = 0;
    int fountainCount = 0;

    // cand-mapid (hypothesis #11): which known map and pearl layout this is (mapdb.hpp, mapid.cpp). Every process keeps the
    // table maps of its size that fit every kelp/portal edge, spawn flag (pearlIn -1 = never spawns) and countdown it has
    // seen in its own windows; a split child starts again from its own first window. The planner reads these only in the
    // layout policy (params.hpp, cand-mapid section).
    int mapCand[16] = {0}; int nMapCand = 0; int mapChecks = 0;
    int mapIdx = -1;          // the one table map left (decided), -1 otherwise
    int mapFam = -1;          // the family (index of its a map) once every map left belongs to one family
    char mapLayout = '?';     // 'a' / 'b' once decided, '?' otherwise
    int mapType = 0;          // 0 unknown, 1 elimination-type family, 2 round-500-type family
    bool mapNone = false;     // no table map fits what we saw (unknown map or layout, or a contradiction after a decision)
    int mapDecidedRound = -1; // round of the decision
    int mapTagState = -2;     // state last written to the indicator (mapStateCode()); -2 = never
    bool mapIs(const char* famName, char layout) const;   // decided on this family (mapdb name) and layout
    bool mapFamIs(const char* famName) const;              // stack7: this family known (layout decided or not), not "none"
    int mapStateCode() const { return mapNone ? -1 : mapIdx >= 0 ? 1000 + mapIdx : mapFam >= 0 ? 100 + mapFam : 0; }
    std::string mapTag() const;                            // "map=<Name>/<a|b|?>", "map=?", "map=none"
    // stack8 F2 (mapid.cpp, terrdb.hpp): the recognised map's own fountain (1/0; spawn gap mean <= 12) and territory at tile t once
    // the family is known and every table map left agrees there, else -1. Territory: 1 = the side of homeT (the server swaps the file's
    // team letters in about half of the online games, so the side comes from a tile we know is ours), 2 = the other, 0 = neutral.
    int mapFountAt(int t) const;
    int mapTerrAt(int t, int homeT) const;
    char mapTerrChar(int t) const;     // v1 sd: terrdb's char at t ('0' neutral, '1', '2') where every table map left agrees, else '?'
    double mapSpawnGap(int t) const;   // v1 sd: the table's mean spawn gap at t (0 never spawns, -1 unknown or the maps left disagree)
    // v1 final (coordinator 03:30, pocket exclusion): the 2-core of the recognised family's passable graph (mapdb kelp edges; a portal edge
    // counts as passable and is never pruned from its unknown far side): tiles left after repeatedly removing tiles with <= 1 passable
    // neighbour. A tile outside it is a dead-end pocket: never a swarm goal target. Built once per family; empty = unknown (all allowed).
    std::vector<uint8_t> core2; int core2Fam = -2;
    void ensureCore2();
    bool inCore2(int t) const { return core2.empty() || core2[t] != 0; }
    // v1.1 frontier allocation (frontdb.hpp): the frontier bin of tile t (0 own-deep .. 4 enemy-deep) seen from terrdb side '1' or '2', where
    // every table map left agrees; -1 unknown (not recognised, the maps left disagree, both starts unreachable, or no side)
    int mapFrontBin(int t, char side) const;

    void init(const InitBlock& ib);
    void ingest(const RoundBlock& rb);  // updates everything for this turn

    // --- queries used by the planner ---
    // Destination across edge d from tile t: >=0 tile, -1 blocked (kelp), -2 unknown portal exit.
    int across(int t, int d) const;
    bool edgeUnknown(int t, int d) const { return tiles[t].edge[d] == EDGE_UNKNOWN; }
    // Probability a pearl sits on tile t when we arrive at absolute round r (r >= round).
    double pearlProb(int t, int r) const;
    bool isFountain(int t) const { const Tile& x = tiles[t]; return x.samples >= 2 ? x.maxSample <= 12 : (x.samples == 1 && x.maxSample <= 3); }
    int mirrorTile(int t, int hyp) const;
    int mirrorDir(int d, int hyp) const;
    int teamLongestKnown() const; // max(myLen, longest ally seen/heard); v1 belief fix: longest ally with fresh news
    // v1 belief fix (params.hpp BELIEF_FIX_ON): the one king class. The longest ally with news (seen, heard or relayed) within
    // BELIEF_FRESH rounds and its last known head are computed after every ingest (computeFreshAllies); with the fix off the lifetime
    // maximum maxAllyLenSeen stands in (stack11, compiled exactly as before).
    int freshAllyLen = 0, freshAllyT = -1;
    int freshAllyId = -1, freshAllyHeadRound = -1;   // v1.1 king beacon (KING_BEACON_ON): that ally's id and the round of its head news
    int allyLongest() const { return P::BELIEF_FIX_ON ? freshAllyLen : maxAllyLenSeen; }
    bool iAmLongest() const { return myLen >= (P::BELIEF_FIX_ON ? freshAllyLen : maxAllyLenSeen); }
    bool allyFresh(const Dragon& d, int maxAge) const { return round - std::max(d.lastSeen, d.headSeen) <= maxAge; }

    // test hook: load an edge as if observed (used by tools/test_world.cpp)
    void testSetEdge(int t, int d, uint8_t kind, int pid) { setEdge(t, d, kind, pid); }

    // encoding of the 64-bit team message
    uint64_t encodeMsg(int hotT) const;
    uint64_t encodeMsg(int hotT, int t, int len) const;                     // v1 belief fix: format 2 with the post-action head and length
    uint64_t encodeKingMsg(int kid, int infoRound, int kt, int klen) const; // relay of the king's last known head (c10d)
    bool decodeMsg(uint64_t v, AllyMsg& out) const;
    int msgIdMask() const;                                                  // 255 (format 1), 2047 (format 2)

  private:
    void setEdge(int t, int d, uint8_t kind, int pid);
    void ingestTiles(const RoundBlock& rb);
    void ingestEdges(const RoundBlock& rb, const int* winTile);
    void ingestDragons(const RoundBlock& rb);
    void updateOwnBody(const RoundBlock& rb);
    void buildOccupancy();
    void updateSymmetry(const int* winTile);
    void applyMirror(const int* winTile);
    void ingestSonar(const RoundBlock& rb);
    void computeFreshAllies();                                    // v1 belief fix
    int canonicalPortalEnd(int t, int d, int& side) const;
    void initMapId();                                              // cand-mapid (mapid.cpp)
    void updateMapId(const RoundBlock& rb, const int* winTile);   // cand-mapid (mapid.cpp)
};

} // namespace seed0
