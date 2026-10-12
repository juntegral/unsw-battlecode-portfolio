// world.hpp — a dragon's private memory of the board, rebuilt from 7x7 observations each turn.
#pragma once
#include <cstdint>
#include <deque>
#include <unordered_map>
#include <vector>

#include "geom.hpp"
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

struct AllyMsg { int id = -1; int round = -1; int t = -1; int len = 0; int hotT = -1; };

struct World {
    Geo geo;
    int myId = 0; char myTeam = 'A'; int unitLimit = 64;
    int round = 0, myLen = 3, unitCount = 1, myDir = 0, headT = -1;
    bool parsedOk = false;
    std::vector<Tile> tiles;

    // own body, head first; -1 = unknown placeholder (only for a long starting body beyond vision)
    std::deque<int> body;

    std::unordered_map<int, Dragon> dragons;   // every dragon ever seen, by id
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

    // sonar probe: the ray sent last turn (from prevHeadT in probeDir) hit no dragon => probeClear
    int prevHeadT = -1;
    int probeDir = -1, probeRound = -1; bool probeClear = false;

    // map-level statistics
    double pearlPriorUnseen = 0.05;
    int tilesObserved = 0, pearlsAtFirstSight = 0;
    int fountainCount = 0;

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
    int teamLongestKnown() const; // max(myLen, longest ally seen/heard)
    bool iAmLongest() const { return myLen >= maxAllyLenSeen; }

    // test hook: load an edge as if observed (used by tools/test_world.cpp)
    void testSetEdge(int t, int d, uint8_t kind, int pid) { setEdge(t, d, kind, pid); }

    // encoding of the 64-bit team message
    uint64_t encodeMsg(int hotT) const;
    bool decodeMsg(uint64_t v, AllyMsg& out) const;

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
    int canonicalPortalEnd(int t, int d, int& side) const;
};

} // namespace seed0
